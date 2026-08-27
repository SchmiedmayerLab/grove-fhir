#!/usr/bin/env python3
"""Build deterministic FHIR fixture corpora from one RFC 6902 mutation per case.

The module deliberately does not know any profile-specific validation rules. A domain
checker supplies diagnostics after validating the materialized resources, and
``validate_results`` proves that every invalid fixture failed for its declared reason.
This keeps fixture mechanics reusable across implementation guides while preserving
reason-specific evidence.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Sequence


IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RULE_CODE = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
RELEASE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
PATCH_OPERATIONS = frozenset({"add", "remove", "replace", "move", "copy"})
SEVERITIES = frozenset({"fatal", "error", "warning", "information"})


class CorpusError(ValueError):
    """Report an invalid corpus, patch operation, or validation result."""


def canonical_json_bytes(value: Any) -> bytes:
    """Encode JSON deterministically for hashing and byte-for-byte fixtures."""
    return (_canonical_json(value) + "\n").encode("utf-8")


def _canonical_json(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("JSON numbers must be finite")
        return str(value)
    if isinstance(value, float):
        return json.dumps(value, allow_nan=False)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(_canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("JSON object keys must be strings")
        return "{" + ",".join(
            f"{_canonical_json(key)}:{_canonical_json(value[key])}"
            for key in sorted(value)
        ) + "}"
    raise TypeError(f"value is not JSON-compatible: {type(value).__name__}")


def strict_json_loads(value: str) -> Any:
    """Decode JSON without duplicate keys, non-finite values, or decimal precision loss."""
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise CorpusError(f"duplicate JSON object key: {key!r}")
            result[key] = item
        return result

    def invalid_constant(constant: str) -> Any:
        raise CorpusError(f"invalid non-finite JSON number: {constant}")

    return json.loads(
        value,
        object_pairs_hook=object_pairs,
        parse_float=Decimal,
        parse_constant=invalid_constant,
    )


def sha256_bytes(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""
    return hashlib.sha256(value).hexdigest()


def _safe_relative_path(value: Any, label: str) -> Path:
    if not isinstance(value, str):
        raise CorpusError(f"{label} must be a relative POSIX path")
    path = PurePosixPath(value)
    if (
        not value
        or "\0" in value
        or "\\" in value
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != value
    ):
        raise CorpusError(f"{label} must be a safe relative POSIX path")
    return Path(*path.parts)


def _decode_pointer(pointer: Any, label: str) -> list[str]:
    if not isinstance(pointer, str):
        raise CorpusError(f"{label} must be a JSON Pointer string")
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise CorpusError(f"{label} must be empty or start with '/'")
    tokens: list[str] = []
    for encoded in pointer[1:].split("/"):
        index = 0
        decoded: list[str] = []
        while index < len(encoded):
            if encoded[index] != "~":
                decoded.append(encoded[index])
                index += 1
                continue
            if index + 1 >= len(encoded) or encoded[index + 1] not in {"0", "1"}:
                raise CorpusError(f"{label} contains an invalid JSON Pointer escape")
            decoded.append("~" if encoded[index + 1] == "0" else "/")
            index += 2
        tokens.append("".join(decoded))
    return tokens


def _array_index(token: str, length: int, label: str, allow_end: bool) -> int:
    if token == "-":
        if allow_end:
            return length
        raise CorpusError(f"{label} may use '-' only for an add destination")
    if not re.fullmatch(r"0|[1-9][0-9]*", token):
        raise CorpusError(f"{label} contains an invalid array index: {token!r}")
    index = int(token)
    maximum = length if allow_end else length - 1
    if index > maximum:
        raise CorpusError(f"{label} array index is out of bounds: {index}")
    return index


def _resolve(document: Any, tokens: Sequence[str], label: str) -> Any:
    current = document
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                raise CorpusError(f"{label} does not exist")
            current = current[token]
        elif isinstance(current, list):
            current = current[_array_index(token, len(current), label, False)]
        else:
            raise CorpusError(f"{label} traverses a scalar value")
    return current


def _parent(document: Any, tokens: Sequence[str], label: str) -> tuple[Any, str]:
    if not tokens:
        raise CorpusError(f"{label} addresses the document root")
    return _resolve(document, tokens[:-1], label), tokens[-1]


def _remove(document: Any, tokens: Sequence[str], label: str) -> Any:
    if not tokens:
        return None
    parent, token = _parent(document, tokens, label)
    if isinstance(parent, dict):
        if token not in parent:
            raise CorpusError(f"{label} does not exist")
        return parent.pop(token)
    if isinstance(parent, list):
        return parent.pop(_array_index(token, len(parent), label, False))
    raise CorpusError(f"{label} parent is not a container")


def _add(document: Any, tokens: Sequence[str], value: Any, label: str) -> Any:
    if not tokens:
        return copy.deepcopy(value)
    parent, token = _parent(document, tokens, label)
    if isinstance(parent, dict):
        parent[token] = copy.deepcopy(value)
        return document
    if isinstance(parent, list):
        index = _array_index(token, len(parent), label, True)
        parent.insert(index, copy.deepcopy(value))
        return document
    raise CorpusError(f"{label} parent is not a container")


def validate_patch_operation(operation: Any, label: str = "patch") -> list[str]:
    """Return structural failures for one mutating RFC 6902 operation."""
    failures: list[str] = []
    if not isinstance(operation, dict):
        return [f"{label} must contain one JSON Patch object"]
    name = operation.get("op")
    if name == "test":
        failures.append(f"{label} op 'test' is not a mutation")
    elif not isinstance(name, str) or name not in PATCH_OPERATIONS:
        failures.append(f"{label} op must be add, remove, replace, move, or copy")

    required = {"op", "path"}
    if isinstance(name, str) and name in {"add", "replace"}:
        required.add("value")
    if isinstance(name, str) and name in {"move", "copy"}:
        required.add("from")
    missing = sorted(required - operation.keys())
    if missing:
        failures.append(f"{label} is missing: {', '.join(missing)}")
    unknown = sorted(set(operation) - required)
    if unknown:
        failures.append(f"{label} contains unsupported fields: {', '.join(unknown)}")
    for field in ("path", "from"):
        if field not in operation:
            continue
        try:
            _decode_pointer(operation[field], f"{label} {field}")
        except CorpusError as error:
            failures.append(str(error))
    return failures


def apply_patch_operation(document: Any, operation: Mapping[str, Any]) -> Any:
    """Apply one mutating RFC 6902 operation to a deep copy of ``document``."""
    failures = validate_patch_operation(operation)
    if failures:
        raise CorpusError("; ".join(failures))
    result = copy.deepcopy(document)
    name = str(operation["op"])
    path = _decode_pointer(operation["path"], "patch path")

    if name == "add":
        result = _add(result, path, operation["value"], "patch path")
    elif name == "remove":
        if not path:
            result = None
        else:
            _remove(result, path, "patch path")
    elif name == "replace":
        if not path:
            result = copy.deepcopy(operation["value"])
        else:
            _resolve(result, path, "patch path")
            _remove(result, path, "patch path")
            result = _add(result, path, operation["value"], "patch path")
    else:
        source = _decode_pointer(operation["from"], "patch from")
        if name == "move" and path[: len(source)] == source and len(path) > len(source):
            raise CorpusError("patch path may not be a child of patch from for move")
        value = copy.deepcopy(_resolve(result, source, "patch from"))
        if name == "move":
            if source == path:
                raise CorpusError("move must change the document")
            if not source:
                result = None
            else:
                _remove(result, source, "patch from")
        result = _add(result, path, value, "patch path")

    if canonical_json_bytes(result) == canonical_json_bytes(document):
        raise CorpusError("patch operation must change the base resource")
    return result


def _validate_expected_rule(value: Any, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label} expectedRule must be an object"]
    failures: list[str] = []
    allowed = {"code", "reason", "location", "severity"}
    unknown = sorted(set(value) - allowed)
    if unknown:
        failures.append(
            f"{label} expectedRule contains unsupported fields: {', '.join(unknown)}"
        )
    code = value.get("code")
    if not isinstance(code, str) or not RULE_CODE.fullmatch(code):
        failures.append(f"{label} expectedRule code must be a stable lowercase rule code")
    reason = value.get("reason")
    if not isinstance(reason, str) or not reason.strip() or reason != reason.strip():
        failures.append(f"{label} expectedRule reason must be a nonempty exact string")
    location = value.get("location")
    if location is not None and (
        not isinstance(location, str)
        or not location.strip()
        or location != location.strip()
    ):
        failures.append(f"{label} expectedRule location must be a nonempty exact string")
    severity = value.get("severity")
    if severity is not None and (
        not isinstance(severity, str) or severity not in SEVERITIES
    ):
        failures.append(
            f"{label} expectedRule severity must be fatal, error, warning, or information"
        )
    return failures


def validate_manifest(manifest: Any) -> list[str]:
    """Return all schema failures that do not require loading base files."""
    if not isinstance(manifest, dict):
        return ["fixture corpus manifest must be a JSON object"]
    failures: list[str] = []
    unknown = sorted(set(manifest) - {"schemaVersion", "version", "bases", "cases"})
    if unknown:
        failures.append(
            "fixture corpus manifest contains unsupported fields: " + ", ".join(unknown)
        )
    if manifest.get("schemaVersion") != 1:
        failures.append("fixture corpus schemaVersion must be 1")
    version = manifest.get("version")
    if not isinstance(version, str) or RELEASE_VERSION.fullmatch(version) is None:
        failures.append("fixture corpus version must be a semantic release version")

    bases = manifest.get("bases")
    base_ids: set[str] = set()
    base_paths: set[str] = set()
    if not isinstance(bases, list) or not bases:
        failures.append("fixture corpus must contain a nonempty bases list")
        bases = []
    for index, base in enumerate(bases):
        label = f"base {index + 1}"
        if not isinstance(base, dict):
            failures.append(f"{label} must be an object")
            continue
        unknown_base = sorted(set(base) - {"id", "path"})
        if unknown_base:
            failures.append(f"{label} contains unsupported fields: {', '.join(unknown_base)}")
        identifier = base.get("id")
        if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
            failures.append(f"{label} id must be a lowercase hyphenated identifier")
        elif identifier in base_ids:
            failures.append(f"duplicate base id: {identifier}")
        else:
            base_ids.add(identifier)
        try:
            path = _safe_relative_path(base.get("path"), f"{label} path").as_posix()
            if path in base_paths:
                failures.append(f"duplicate base path: {path}")
            base_paths.add(path)
        except CorpusError as error:
            failures.append(str(error))

    cases = manifest.get("cases")
    case_ids: set[str] = set()
    if not isinstance(cases, list) or not cases:
        failures.append("fixture corpus must contain a nonempty cases list")
        cases = []
    for index, case in enumerate(cases):
        label = f"case {index + 1}"
        if not isinstance(case, dict):
            failures.append(f"{label} must be an object")
            continue
        unknown_case = sorted(set(case) - {"id", "base", "patch", "expectedRule"})
        if unknown_case:
            failures.append(f"{label} contains unsupported fields: {', '.join(unknown_case)}")
        identifier = case.get("id")
        if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
            failures.append(f"{label} id must be a lowercase hyphenated identifier")
        elif identifier in case_ids:
            failures.append(f"duplicate case id: {identifier}")
        else:
            case_ids.add(identifier)
        base = case.get("base")
        if not isinstance(base, str) or base not in base_ids:
            failures.append(f"{label} references an unknown base: {base!r}")
        patch = case.get("patch")
        if not isinstance(patch, list) or len(patch) != 1:
            failures.append(f"{label} patch must contain exactly one operation")
        else:
            failures.extend(validate_patch_operation(patch[0], f"{label} patch"))
        failures.extend(_validate_expected_rule(case.get("expectedRule"), label))
    return failures


def load_manifest(path: Path) -> dict[str, Any]:
    """Load and structurally validate a corpus manifest."""
    if path.is_symlink():
        raise CorpusError(f"fixture corpus manifest may not be a symlink: {path}")
    try:
        manifest = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CorpusError(f"unable to read fixture corpus manifest {path}: {error}") from error
    failures = validate_manifest(manifest)
    if failures:
        raise CorpusError("\n".join(failures))
    return manifest


def load_bases(manifest: Mapping[str, Any], manifest_path: Path) -> dict[str, Any]:
    """Load canonical FHIR JSON base resources relative to a manifest."""
    loaded: dict[str, Any] = {}
    corpus_root = manifest_path.parent.resolve()
    for base in manifest["bases"]:
        relative = _safe_relative_path(base["path"], f"base {base['id']} path")
        path = manifest_path.parent / relative
        current = manifest_path.parent
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise CorpusError(f"base {base['id']} path may not contain symlinks")
        try:
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(corpus_root):
                raise CorpusError(f"base {base['id']} escapes the corpus directory")
            resource = strict_json_loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise CorpusError(f"unable to read base {base['id']} at {path}: {error}") from error
        if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
            raise CorpusError(f"base {base['id']} must be a FHIR JSON resource object")
        loaded[base["id"]] = resource
    return loaded


def build_cases(
    manifest: Mapping[str, Any], bases: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply every independent case mutation and return case resources by id."""
    resources: dict[str, Any] = {}
    for case in manifest["cases"]:
        try:
            resource = apply_patch_operation(bases[case["base"]], case["patch"][0])
        except CorpusError as error:
            raise CorpusError(f"case {case['id']}: {error}") from error
        if not isinstance(resource, dict):
            raise CorpusError(f"case {case['id']} must materialize a FHIR JSON object")
        resources[case["id"]] = resource
    return resources


def materialize_corpus(manifest_path: Path, output: Path) -> dict[str, Any]:
    """Materialize canonical valid/invalid fixtures and return their deterministic index."""
    manifest = load_manifest(manifest_path)
    bases = load_bases(manifest, manifest_path)
    cases = build_cases(manifest, bases)
    expected_paths = {
        "corpus-index.json",
        *(f"valid/{base['id']}.json" for base in manifest["bases"]),
        *(f"invalid/{case['id']}.json" for case in manifest["cases"]),
    }
    if output.is_symlink():
        raise CorpusError(f"fixture corpus output may not be a symlink: {output}")
    if output.exists() and not output.is_dir():
        raise CorpusError(f"fixture corpus output must be a directory: {output}")
    if output.exists():
        existing: set[str] = set()
        for path in output.rglob("*"):
            if path.is_symlink():
                raise CorpusError(f"fixture corpus output contains a symlink: {path}")
            if path.is_file():
                existing.add(path.relative_to(output).as_posix())
        stale = sorted(existing - expected_paths)
        if stale:
            raise CorpusError("fixture corpus output contains stale files: " + ", ".join(stale))
    (output / "valid").mkdir(parents=True, exist_ok=True)
    (output / "invalid").mkdir(parents=True, exist_ok=True)

    base_index: list[dict[str, Any]] = []
    for base in sorted(manifest["bases"], key=lambda item: item["id"]):
        data = canonical_json_bytes(bases[base["id"]])
        relative = f"valid/{base['id']}.json"
        (output / relative).write_bytes(data)
        base_index.append({"id": base["id"], "path": relative, "sha256": sha256_bytes(data)})

    case_index: list[dict[str, Any]] = []
    case_by_id = {case["id"]: case for case in manifest["cases"]}
    for identifier in sorted(cases):
        case = case_by_id[identifier]
        data = canonical_json_bytes(cases[identifier])
        relative = f"invalid/{identifier}.json"
        (output / relative).write_bytes(data)
        case_index.append(
            {
                "id": identifier,
                "base": case["base"],
                "path": relative,
                "sha256": sha256_bytes(data),
                "patch": copy.deepcopy(case["patch"]),
                "expectedRule": copy.deepcopy(case["expectedRule"]),
            }
        )
    index = {"schemaVersion": 1, "bases": base_index, "cases": case_index}
    (output / "corpus-index.json").write_bytes(canonical_json_bytes(index))
    return index


def validate_results(manifest: Mapping[str, Any], results: Any) -> list[str]:
    """Check base success and exact expected-rule evidence for every invalid case."""
    failures: list[str] = []
    if not isinstance(results, dict):
        return ["fixture validation results must be a JSON object"]
    unknown = sorted(
        set(results) - {"schemaVersion", "baseDiagnostics", "caseDiagnostics"}
    )
    if unknown:
        failures.append(
            "fixture validation results contain unsupported fields: " + ", ".join(unknown)
        )
    if results.get("schemaVersion") != 1:
        failures.append("fixture validation results schemaVersion must be 1")

    expected_bases = {base["id"] for base in manifest["bases"]}
    base_diagnostics = results.get("baseDiagnostics")
    if not isinstance(base_diagnostics, dict):
        failures.append("baseDiagnostics must be an object keyed by base id")
        base_diagnostics = {}
    else:
        missing = sorted(expected_bases - base_diagnostics.keys())
        extra = sorted(base_diagnostics.keys() - expected_bases)
        if missing:
            failures.append("baseDiagnostics is missing: " + ", ".join(missing))
        if extra:
            failures.append("baseDiagnostics contains unknown bases: " + ", ".join(extra))
    for identifier in sorted(expected_bases):
        diagnostics = base_diagnostics.get(identifier)
        if diagnostics != []:
            failures.append(f"base {identifier} must have no diagnostics")

    expected_cases = {case["id"]: case for case in manifest["cases"]}
    case_diagnostics = results.get("caseDiagnostics")
    if not isinstance(case_diagnostics, dict):
        failures.append("caseDiagnostics must be an object keyed by case id")
        case_diagnostics = {}
    else:
        missing = sorted(expected_cases.keys() - case_diagnostics.keys())
        extra = sorted(case_diagnostics.keys() - expected_cases.keys())
        if missing:
            failures.append("caseDiagnostics is missing: " + ", ".join(missing))
        if extra:
            failures.append("caseDiagnostics contains unknown cases: " + ", ".join(extra))
    for identifier, case in sorted(expected_cases.items()):
        diagnostics = case_diagnostics.get(identifier)
        if not isinstance(diagnostics, list):
            failures.append(f"case {identifier} diagnostics must be a list")
            continue
        if diagnostics != [case["expectedRule"]]:
            failures.append(
                f"case {identifier} must report exactly one diagnostic equal to expectedRule: "
                + json.dumps(case["expectedRule"], sort_keys=True)
            )
    return failures


def validate_with(
    manifest: Mapping[str, Any],
    bases: Mapping[str, Any],
    cases: Mapping[str, Any],
    validator: Callable[[Any], Iterable[Mapping[str, Any]]],
) -> list[str]:
    """Run an in-process domain validator and check reason-specific results."""
    results = {
        "schemaVersion": 1,
        "baseDiagnostics": {
            identifier: list(validator(resource))
            for identifier, resource in sorted(bases.items())
        },
        "caseDiagnostics": {
            identifier: list(validator(resource))
            for identifier, resource in sorted(cases.items())
        },
    }
    return validate_results(manifest, results)


def _validated_inputs(path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = load_manifest(path)
    bases = load_bases(manifest, path)
    cases = build_cases(manifest, bases)
    return manifest, bases, cases


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate a corpus and all mutations")
    validate.add_argument("manifest", type=Path)
    materialize = commands.add_parser(
        "materialize", help="write canonical valid and invalid fixtures"
    )
    materialize.add_argument("manifest", type=Path)
    materialize.add_argument("output", type=Path)
    check = commands.add_parser(
        "check-results", help="verify reason-specific checker diagnostics"
    )
    check.add_argument("manifest", type=Path)
    check.add_argument("results", type=Path)
    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "validate":
            manifest, bases, cases = _validated_inputs(arguments.manifest)
            print(
                f"Validated {len(bases)} bases and {len(cases)} one-mutation cases "
                f"(schema {manifest['schemaVersion']})"
            )
            return 0
        if arguments.command == "materialize":
            index = materialize_corpus(arguments.manifest, arguments.output)
            print(
                f"Materialized {len(index['bases'])} bases and {len(index['cases'])} "
                f"cases in {arguments.output}"
            )
            return 0
        manifest = load_manifest(arguments.manifest)
        try:
            results = strict_json_loads(arguments.results.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise CorpusError(f"unable to read validation results: {error}") from error
        failures = validate_results(manifest, results)
        if failures:
            raise CorpusError("\n".join(failures))
        print(f"Verified reason-specific diagnostics for {len(manifest['cases'])} cases")
        return 0
    except CorpusError as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
