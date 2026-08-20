#!/usr/bin/env python3
"""Validate domain corpora with the locked FHIR Validator in an isolated cache."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    from fhir_fixture_corpus import (
        canonical_json_bytes,
        apply_patch_operation,
        load_manifest,
        materialize_corpus,
        strict_json_loads,
    )
except ModuleNotFoundError:  # Imported as Scripts.validate_domain_fhir in tests.
    from Scripts.fhir_fixture_corpus import (  # type: ignore[no-redef]
        canonical_json_bytes,
        apply_patch_operation,
        load_manifest,
        materialize_corpus,
        strict_json_loads,
    )


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE = ROOT / "Conformance/evidence.json"
DEFAULT_TOOLCHAIN = ROOT / "Conformance/toolchain.json"
DEFAULT_INDEX = ROOT / "Conformance/corpora/index.json"
DEFAULT_TOOLS = ROOT / ".build/fhir-tools"
DEFAULT_LOCK = ROOT / ".build/conformance/evidence-lock.json"
MESSAGE_ID_URL = "http://hl7.org/fhir/StructureDefinition/operationoutcome-message-id"
FILE_URL = "http://hl7.org/fhir/StructureDefinition/operationoutcome-file"
EXTENSION_VALUE_FIELD = re.compile(r"^(?:extension|value[A-Z][A-Za-z0-9]*)$")


class DomainValidationError(ValueError):
    """Report untrusted tooling, malformed evidence, or a validation mismatch."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        raise DomainValidationError(f"unable to hash {path}: {error}") from error
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink():
        raise DomainValidationError(f"{label} may not be a symlink: {path}")
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise DomainValidationError(f"unable to read {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise DomainValidationError(f"{label} must be a JSON object: {path}")
    return value


def resolve_repository_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise DomainValidationError(f"{label} must be a repository-relative POSIX path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise DomainValidationError(f"{label} must not escape the repository")
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise DomainValidationError(f"{label} escapes the repository")
    return path


FSH_DEFINITION = re.compile(r"^(Profile|Extension|RuleSet|Invariant):\s*(\S+)")
FSH_CARDINALITY = re.compile(r"(?:^|\s)[0-9]+\.\.(?:[0-9]+|\*)(?:\s|$)")


def fsh_inventory(paths: Sequence[Path]) -> tuple[dict[str, str], set[str], set[str]]:
    """Extract active StructureDefinitions, invariants, and computable FSH rules."""
    definitions: dict[str, str] = {}
    invariants: set[str] = set()
    rules: set[str] = set()
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise DomainValidationError(f"coverage FSH source must be a regular file: {path}")
        current_kind: str | None = None
        current_name: str | None = None
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as error:
            raise DomainValidationError(f"unable to read FSH coverage source {path}: {error}") from error
        for line_number, line in enumerate(lines, 1):
            stripped = line.strip()
            header = FSH_DEFINITION.match(stripped)
            if header:
                current_kind, current_name = header.groups()
                if current_kind == "Invariant":
                    if current_name in invariants:
                        raise DomainValidationError(f"duplicate FSH invariant {current_name}")
                    invariants.add(current_name)
                continue
            if current_kind in {"Profile", "Extension"} and stripped.startswith("Id:"):
                identifier = stripped.removeprefix("Id:").strip()
                if not identifier or current_name in definitions:
                    raise DomainValidationError(
                        f"invalid or duplicate Id for {current_kind} {current_name} at {path}:{line_number}"
                    )
                definitions[str(current_name)] = identifier
                continue
            if current_kind not in {"Profile", "Extension", "RuleSet"} or not current_name:
                continue
            continuation = line.startswith("    ") and (
                " named " in stripped or FSH_CARDINALITY.search(stripped)
            )
            if not (stripped.startswith("* ") or continuation):
                continue
            if stripped.startswith("* insert") or " obeys " in f" {stripped} " or "^" in stripped:
                continue
            computable = bool(
                FSH_CARDINALITY.search(stripped)
                or " only " in f" {stripped} "
                or " = " in stripped
                or (" from " in stripped and "(required)" in stripped)
            )
            if computable:
                key = f"{current_kind}:{current_name}|{stripped}"
                if key in rules:
                    raise DomainValidationError(f"duplicate computable FSH rule: {key}")
                rules.add(key)
    missing_ids = sorted(
        name
        for name in definitions
        if not definitions[name]
    )
    if missing_ids:
        raise DomainValidationError("StructureDefinitions missing Id: " + ", ".join(missing_ids))
    return definitions, invariants, rules


def mobile_effective_choice_failure(resource: Mapping[str, Any]) -> str | None:
    allowed = {"effectiveDateTime", "effectivePeriod"}
    r4_choices = {"effectiveDateTime", "effectivePeriod", "effectiveTiming", "effectiveInstant"}
    present = sorted(r4_choices & resource.keys())
    if len(present) != 1 or present[0] not in allowed:
        return "mobile-effective-choice"
    return None


def validate_domain_coverage(
    coverage_path: Path,
    corpora: Mapping[str, Mapping[str, Any]],
    validator_version: str,
) -> list[dict[str, Any]]:
    coverage = load_json(coverage_path, "domain coverage inventory")
    if coverage.get("schemaVersion") != 2 or set(coverage) != {"schemaVersion", "guides"}:
        raise DomainValidationError("domain coverage inventory must use schemaVersion 2")
    declarations = coverage.get("guides")
    if not isinstance(declarations, dict) or set(declarations) != set(corpora):
        raise DomainValidationError("domain coverage guides must exactly match domain corpora")
    reports: list[dict[str, Any]] = []
    for guide_id in sorted(corpora):
        declaration = declarations[guide_id]
        if not isinstance(declaration, dict):
            raise DomainValidationError(f"coverage guide {guide_id} must be an object")
        expected_fields = {
            "fsh",
            "manifest",
            "structureDefinitions",
            "invariants",
            "sourceRules",
            "caseBoundaries",
            "supplementalBoundaries",
            "nonInvalidBoundaries",
            "validatorLimitations",
        }
        if set(declaration) != expected_fields:
            raise DomainValidationError(f"coverage guide {guide_id} has unsupported or missing fields")
        fsh_values = declaration["fsh"]
        if not isinstance(fsh_values, list) or not fsh_values:
            raise DomainValidationError(f"coverage guide {guide_id} needs FSH source files")
        fsh_paths = [
            resolve_repository_path(value, f"coverage guide {guide_id} FSH source")
            for value in fsh_values
        ]
        actual_definitions, actual_invariants, actual_rules = fsh_inventory(fsh_paths)
        if declaration["structureDefinitions"] != actual_definitions:
            raise DomainValidationError(
                f"coverage guide {guide_id} StructureDefinition inventory has drifted"
            )
        invariant_coverage = declaration["invariants"]
        if not isinstance(invariant_coverage, dict) or set(invariant_coverage) != actual_invariants:
            raise DomainValidationError(f"coverage guide {guide_id} invariant inventory has drifted")
        source_rules = declaration["sourceRules"]
        if not isinstance(source_rules, dict) or set(source_rules) != actual_rules:
            missing = sorted(actual_rules - set(source_rules) if isinstance(source_rules, dict) else actual_rules)
            extra = sorted(set(source_rules) - actual_rules if isinstance(source_rules, dict) else set())
            raise DomainValidationError(
                f"coverage guide {guide_id} computable FSH rules have drifted; "
                f"missing={missing}, extra={extra}"
            )
        manifest_path = resolve_repository_path(
            declaration["manifest"], f"coverage guide {guide_id} manifest"
        )
        indexed_manifest = resolve_repository_path(
            corpora[guide_id].get("manifest"), f"corpus {guide_id} manifest"
        )
        if manifest_path != indexed_manifest:
            raise DomainValidationError(f"coverage guide {guide_id} manifest differs from corpus index")
        manifest = load_manifest(manifest_path)
        case_ids = {case["id"] for case in manifest["cases"]}
        invariant_cases: list[str] = []
        for invariant_id, values in invariant_coverage.items():
            if not isinstance(values, list) or not values or not all(
                isinstance(value, str) for value in values
            ):
                raise DomainValidationError(
                    f"coverage invariant {guide_id}/{invariant_id} needs case ids"
                )
            invariant_cases.extend(values)
        case_boundaries = declaration["caseBoundaries"]
        if not isinstance(case_boundaries, dict) or not all(
            isinstance(case, str) and isinstance(boundary, str) and boundary
            for case, boundary in case_boundaries.items()
        ):
            raise DomainValidationError(f"coverage guide {guide_id} has invalid case boundaries")
        covered_cases = invariant_cases + list(case_boundaries)
        if len(covered_cases) != len(set(covered_cases)) or set(covered_cases) != case_ids:
            missing = sorted(case_ids - set(covered_cases))
            extra = sorted(set(covered_cases) - case_ids)
            raise DomainValidationError(
                f"coverage guide {guide_id} cases are not covered exactly once; "
                f"missing={missing}, extra={extra}"
            )
        if not all(case in case_ids for case in invariant_cases):
            raise DomainValidationError(f"coverage guide {guide_id} invariant references unknown case")
        supplemental = declaration["supplementalBoundaries"]
        non_invalid = declaration["nonInvalidBoundaries"]
        limitations = declaration["validatorLimitations"]
        if (
            not isinstance(supplemental, list)
            or len(supplemental) != len(set(supplemental))
            or not all(isinstance(value, str) and value for value in supplemental)
            or not isinstance(non_invalid, dict)
            or not isinstance(limitations, dict)
        ):
            raise DomainValidationError(f"coverage guide {guide_id} boundary declarations are invalid")
        source_boundaries = set(source_rules.values())
        invalid_boundaries = set(case_boundaries.values())
        non_invalid_boundaries = set(non_invalid)
        if invalid_boundaries & non_invalid_boundaries:
            raise DomainValidationError(f"coverage guide {guide_id} classifies a boundary twice")
        declared_boundaries = source_boundaries | set(supplemental)
        if invalid_boundaries | non_invalid_boundaries != declared_boundaries:
            missing = sorted(declared_boundaries - invalid_boundaries - non_invalid_boundaries)
            extra = sorted((invalid_boundaries | non_invalid_boundaries) - declared_boundaries)
            raise DomainValidationError(
                f"coverage guide {guide_id} boundary classification drift; "
                f"missing={missing}, extra={extra}"
            )
        if set(supplemental) & source_boundaries:
            raise DomainValidationError(f"coverage guide {guide_id} supplemental boundary has a source rule")
        used_limitations: set[str] = set()
        allowed_classifications = {
            "base-equivalent",
            "parent-equivalent",
            "valid-only-open-slice",
            "validator-limitation",
        }
        base_ids = {base["id"] for base in manifest["bases"]}
        additional_ids = {"accepted-study-graph"} if guide_id == "mobile" else set()
        for boundary, evidence in non_invalid.items():
            if not isinstance(evidence, dict) or evidence.get("classification") not in allowed_classifications:
                raise DomainValidationError(f"coverage boundary {guide_id}/{boundary} has invalid classification")
            valid_bases = evidence.get("validBases")
            if (
                not isinstance(valid_bases, list)
                or not valid_bases
                or not all(isinstance(value, str) for value in valid_bases)
                or not set(valid_bases) <= base_ids | additional_ids
            ):
                raise DomainValidationError(f"coverage boundary {guide_id}/{boundary} has invalid validBases")
            limitation_id = evidence.get("limitation")
            if evidence["classification"] == "validator-limitation":
                if not isinstance(limitation_id, str) or limitation_id not in limitations:
                    raise DomainValidationError(f"coverage boundary {guide_id}/{boundary} lacks limitation")
                used_limitations.add(limitation_id)
            elif limitation_id is not None:
                raise DomainValidationError(f"coverage boundary {guide_id}/{boundary} has spurious limitation")
        if used_limitations != set(limitations):
            raise DomainValidationError(f"coverage guide {guide_id} has stale validator limitations")
        for limitation_id, limitation in limitations.items():
            if not isinstance(limitation, dict) or set(limitation) != {
                "tool", "version", "base", "patch", "customCheck"
            }:
                raise DomainValidationError(f"coverage limitation {guide_id}/{limitation_id} is malformed")
            if limitation["tool"] != "fhir-validator" or limitation["version"] != validator_version:
                raise DomainValidationError(f"coverage limitation {guide_id}/{limitation_id} tool version drift")
            if limitation["customCheck"] != "mobile-effective-choice":
                raise DomainValidationError(f"unsupported coverage custom check: {limitation['customCheck']}")
            base = next((item for item in manifest["bases"] if item["id"] == limitation["base"]), None)
            if base is None or not isinstance(limitation["patch"], list) or len(limitation["patch"]) != 1:
                raise DomainValidationError(f"coverage limitation {guide_id}/{limitation_id} has invalid witness")
            base_resource = load_json(
                (manifest_path.parent / base["path"]).resolve(),
                f"coverage limitation {guide_id}/{limitation_id} base",
            )
            witness = apply_patch_operation(base_resource, limitation["patch"][0])
            if not isinstance(witness, dict) or mobile_effective_choice_failure(witness) != "mobile-effective-choice":
                raise DomainValidationError(f"coverage limitation {guide_id}/{limitation_id} witness is ineffective")
        reports.append(
            {
                "id": guide_id,
                "structureDefinitionCount": len(actual_definitions),
                "invariantCount": len(actual_invariants),
                "computableRuleCount": len(actual_rules),
                "invalidBoundaryCount": len(invalid_boundaries),
                "nonInvalidBoundaryCount": len(non_invalid_boundaries),
                "validatorLimitationCount": len(limitations),
            }
        )
    return reports


def unique_by_id(values: Any, label: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(values, list):
        raise DomainValidationError(f"{label} must be a list")
    result: dict[str, Mapping[str, Any]] = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get("id"), str):
            raise DomainValidationError(f"{label} entries must be objects with string ids")
        identifier = value["id"]
        if identifier in result:
            raise DomainValidationError(f"duplicate {label} id: {identifier}")
        result[identifier] = value
    return result


def tool_artifacts(toolchain: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    if toolchain.get("kind") != "grove-fhir-toolchain" or toolchain.get("schemaVersion") != 1:
        raise DomainValidationError("toolchain kind/schemaVersion is unsupported")
    artifacts = toolchain.get("artifacts")
    if not isinstance(artifacts, list):
        raise DomainValidationError("toolchain artifacts must be a list")
    seen: set[tuple[str, str]] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise DomainValidationError("toolchain artifacts must be objects")
        identity = (artifact.get("id"), artifact.get("version"))
        if not all(isinstance(item, str) and item for item in identity):
            raise DomainValidationError("toolchain artifacts need nonempty id and version")
        if identity in seen:
            raise DomainValidationError(
                f"duplicate toolchain artifact: {identity[0]}#{identity[1]}"
            )
        seen.add(identity)
        sha256 = artifact.get("sha256")
        if not isinstance(sha256, str) or len(sha256) != 64:
            raise DomainValidationError(
                f"toolchain artifact {identity[0]}#{identity[1]} has invalid SHA-256"
            )
    return artifacts


def verify_regular_file(path: Path, expected_sha256: str, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise DomainValidationError(f"{label} must be a regular file: {path}")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise DomainValidationError(
            f"{label} SHA-256 is {actual}, expected {expected_sha256}"
        )


def package_metadata(path: Path) -> dict[str, Any]:
    try:
        with tarfile.open(path, "r:gz") as archive:
            members = [member for member in archive.getmembers() if member.name == "package/package.json"]
            if len(members) != 1:
                raise DomainValidationError(
                    f"FHIR package {path} must contain one package/package.json"
                )
            extracted = archive.extractfile(members[0])
            if extracted is None:
                raise DomainValidationError(f"unable to read package metadata from {path}")
            metadata = strict_json_loads(extracted.read().decode("utf-8"))
    except (OSError, tarfile.TarError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DomainValidationError(f"unable to inspect FHIR package {path}: {error}") from error
    if not isinstance(metadata, dict):
        raise DomainValidationError(f"FHIR package metadata must be an object: {path}")
    return metadata


def parse_overrides(values: Sequence[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for value in values:
        identifier, separator, raw_path = value.partition("=")
        if not separator or not identifier or not raw_path:
            raise DomainValidationError("--package must use GUIDE=PATH")
        if identifier in overrides:
            raise DomainValidationError(f"duplicate --package override: {identifier}")
        overrides[identifier] = absolute_without_symlinks(
            Path(raw_path), f"package override {identifier}"
        )
    return overrides


def absolute_without_symlinks(path: Path, label: str) -> Path:
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts[1:]
    current = Path(absolute.anchor)
    if parts and (current / parts[0]).is_symlink():
        current = (current / parts[0]).resolve()
        parts = parts[1:]
    for part in parts:
        current /= part
        if current.is_symlink():
            raise DomainValidationError(f"{label} may not traverse a symlink: {current}")
    return current


def safe_manifest_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise DomainValidationError(f"{label} must be a safe relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise DomainValidationError(f"{label} must be a safe relative POSIX path")
    return Path(*path.parts)


def parse_external_evidence(values: Sequence[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        identifier, separator, raw_path = value.partition("=")
        if not separator or not identifier or not raw_path:
            raise DomainValidationError(
                "--external-evidence must use EVIDENCE_SET_ID=PATH"
            )
        if identifier in result:
            raise DomainValidationError(f"duplicate external evidence set: {identifier}")
        result[identifier] = absolute_without_symlinks(
            Path(raw_path), f"external evidence set {identifier}"
        )
    return result


def resolve_external_evidence(
    evidence: Mapping[str, Any],
    supplied: Mapping[str, Path],
    required: bool,
) -> tuple[
    list[dict[str, Any]],
    list[tuple[str, str, Path]],
    dict[tuple[str, str], list[Mapping[str, str]]],
]:
    declarations = unique_by_id(evidence.get("externalEvidence"), "external evidence")
    if not supplied and not required:
        return [], [], {}
    if set(supplied) != set(declarations):
        missing = sorted(set(declarations) - set(supplied))
        unknown = sorted(set(supplied) - set(declarations))
        raise DomainValidationError(
            f"external evidence arguments do not match manifest; missing={missing}, unknown={unknown}"
        )
    reports: list[dict[str, Any]] = []
    fhir_files: list[tuple[str, str, Path]] = []
    expected_unknown_extensions: dict[
        tuple[str, str], list[Mapping[str, str]]
    ] = {}
    for identifier, declaration in sorted(declarations.items()):
        kind = declaration.get("kind")
        classification = declaration.get("classification")
        files = declaration.get("files")
        if (
            kind not in {"directory", "file"}
            or classification
            not in {"accepted-contract", "historical-writer", "legacy-candidate"}
            or not isinstance(files, list)
            or not files
        ):
            raise DomainValidationError(f"external evidence {identifier} declaration is invalid")
        declared: dict[str, Mapping[str, Any]] = {}
        for item in files:
            if not isinstance(item, dict):
                raise DomainValidationError(f"external evidence {identifier} files must be objects")
            relative = safe_manifest_path(item.get("path"), f"external evidence {identifier} path")
            name = relative.as_posix()
            if name in declared:
                raise DomainValidationError(f"external evidence {identifier} repeats {name}")
            declared[name] = item
        fhir_names = {
            name for name, item in declared.items() if item.get("format") == "fhir-json"
        }
        raw_expectations = declaration.get("expectedUnknownExtensions")
        legacy = classification in {"historical-writer", "legacy-candidate"}
        if legacy:
            if not isinstance(raw_expectations, list) or not raw_expectations:
                raise DomainValidationError(
                    f"external evidence {identifier} needs expectedUnknownExtensions"
                )
            by_path: dict[str, list[Mapping[str, str]]] = {}
            allowed_fields = {"path", "expression", "url", "valueField"}
            for expectation in raw_expectations:
                if (
                    not isinstance(expectation, dict)
                    or set(expectation) != allowed_fields
                    or not all(
                        isinstance(value, str) and value
                        for value in expectation.values()
                    )
                    or not expectation["url"].startswith("https://")
                    or (
                        EXTENSION_VALUE_FIELD.fullmatch(expectation["valueField"])
                        is None
                    )
                ):
                    raise DomainValidationError(
                        f"external evidence {identifier} has an invalid unknown-extension contract"
                    )
                name = safe_manifest_path(
                    expectation["path"],
                    f"external evidence {identifier} expected unknown-extension path",
                ).as_posix()
                if name not in fhir_names:
                    raise DomainValidationError(
                        f"external evidence {identifier} unknown-extension contract "
                        f"references non-FHIR file {name}"
                    )
                normalized = {
                    "path": name,
                    "expression": expectation["expression"],
                    "url": expectation["url"],
                    "valueField": expectation["valueField"],
                }
                by_path.setdefault(name, []).append(normalized)
            if set(by_path) != fhir_names:
                raise DomainValidationError(
                    f"external evidence {identifier} unknown-extension contract must "
                    "cover every FHIR file"
                )
            for name, expectations in by_path.items():
                if len(expectations) != len(
                    {
                        (
                            item["expression"],
                            item["url"],
                            item["valueField"],
                        )
                        for item in expectations
                    }
                ):
                    raise DomainValidationError(
                        f"external evidence {identifier}/{name} repeats an "
                        "unknown-extension contract entry"
                    )
                expected_unknown_extensions[(identifier, name)] = expectations
        elif raw_expectations is not None:
            raise DomainValidationError(
                f"accepted external evidence {identifier} may not expect Validator errors"
            )
        location = supplied[identifier]
        resolved: dict[str, Path] = {}
        if kind == "file":
            if len(declared) != 1 or not location.is_file():
                raise DomainValidationError(
                    f"external evidence {identifier} must be its one declared regular file"
                )
            name = next(iter(declared))
            if "/" in name or location.name != name:
                raise DomainValidationError(
                    f"external evidence {identifier} filename differs from manifest"
                )
            resolved[name] = location
        else:
            if not location.is_dir():
                raise DomainValidationError(
                    f"external evidence {identifier} must be a regular directory"
                )
            actual_files: set[str] = set()
            actual_directories: set[str] = set()
            for current_raw, directory_names, file_names in os.walk(location, followlinks=False):
                current = Path(current_raw)
                for name in directory_names:
                    candidate = current / name
                    if candidate.is_symlink():
                        raise DomainValidationError(
                            f"external evidence {identifier} contains symlink {candidate}"
                        )
                    actual_directories.add(candidate.relative_to(location).as_posix())
                for name in file_names:
                    candidate = current / name
                    if candidate.is_symlink() or not candidate.is_file():
                        raise DomainValidationError(
                            f"external evidence {identifier} contains non-regular file {candidate}"
                        )
                    actual_files.add(candidate.relative_to(location).as_posix())
            expected_directories = {
                parent.as_posix()
                for name in declared
                for parent in PurePosixPath(name).parents
                if parent.as_posix() != "."
            }
            if actual_files != set(declared) or actual_directories != expected_directories:
                raise DomainValidationError(
                    f"external evidence {identifier} does not match its exact file tree"
                )
            for name in declared:
                resolved[name] = absolute_without_symlinks(
                    location / Path(*PurePosixPath(name).parts),
                    f"external evidence {identifier}/{name}",
                )
        file_reports: list[dict[str, Any]] = []
        for name, path in sorted(resolved.items()):
            item = declared[name]
            digest = sha256_file(path)
            size = path.stat().st_size
            file_reports.append({"path": name, "sha256": digest, "size": size})
            if item.get("format") == "fhir-json":
                file_reports[-1]["expectedErrorCount"] = len(
                    expected_unknown_extensions.get((identifier, name), [])
                )
                fhir_files.append((identifier, name, path))
        validation_scope = (
            "none"
            if not fhir_names
            else "r4-core"
            if legacy
            else "accepted-package-closure"
        )
        reports.append(
            {
                "id": identifier,
                "validationScope": validation_scope,
                "expectedErrorCount": sum(
                    len(expected_unknown_extensions.get((identifier, name), []))
                    for name in fhir_names
                ),
                "files": file_reports,
            }
        )
    return reports, fhir_files, expected_unknown_extensions


def locked_package_hashes(lock_path: Path | None) -> dict[str, str]:
    if lock_path is None:
        return {}
    lock = load_json(lock_path, "evidence lock")
    if (
        lock.get("kind") != "grove-fhir-conformance-evidence-lock"
        or lock.get("schemaVersion") != 1
    ):
        raise DomainValidationError("evidence lock kind/schemaVersion is unsupported")
    packages = unique_by_id(lock.get("packages"), "evidence lock packages")
    result: dict[str, str] = {}
    for identifier, package in packages.items():
        digest = package.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise DomainValidationError(
                f"evidence lock package {identifier} has invalid SHA-256"
            )
        result[identifier] = digest
    return result


def resolve_guide_packages(
    evidence: Mapping[str, Any],
    guide_ids: set[str],
    overrides: Mapping[str, Path],
    lock_hashes: Mapping[str, str],
) -> tuple[dict[str, Path], dict[str, Mapping[str, Any]], dict[str, str]]:
    guides = unique_by_id(evidence.get("guides"), "evidence guides")
    unknown = sorted(guide_ids - guides.keys())
    if unknown:
        raise DomainValidationError("corpora reference unknown guides: " + ", ".join(unknown))
    unknown_overrides = sorted(overrides.keys() - guide_ids)
    if unknown_overrides:
        raise DomainValidationError(
            "package overrides reference unused guides: " + ", ".join(unknown_overrides)
        )
    paths: dict[str, Path] = {}
    hashes: dict[str, str] = {}
    selected: dict[str, Mapping[str, Any]] = {}
    for identifier in sorted(guide_ids):
        guide = guides[identifier]
        path = overrides.get(identifier)
        if path is None:
            path = resolve_repository_path(guide.get("package"), f"guide {identifier} package")
        if path.is_symlink() or not path.is_file():
            raise DomainValidationError(f"guide {identifier} package is not a regular file: {path}")
        metadata = package_metadata(path)
        expected = {
            "name": guide.get("packageId"),
            "version": guide.get("version"),
            "canonical": guide.get("canonical"),
            "fhirVersions": [guide.get("fhirVersion")],
        }
        for field, value in expected.items():
            if metadata.get(field) != value:
                raise DomainValidationError(
                    f"guide {identifier} package {field} is {metadata.get(field)!r}, expected {value!r}"
                )
        dependencies = guide.get("dependencies")
        if not isinstance(dependencies, list):
            raise DomainValidationError(f"guide {identifier} dependencies must be a list")
        expected_dependencies = {
            dependency["packageId"]: dependency["version"] for dependency in dependencies
        }
        if metadata.get("dependencies") != expected_dependencies:
            raise DomainValidationError(f"guide {identifier} package dependencies have drifted")
        digest = sha256_file(path)
        if lock_hashes and lock_hashes.get(identifier) != digest:
            raise DomainValidationError(
                f"guide {identifier} package SHA-256 does not match evidence lock"
            )
        paths[identifier] = path
        hashes[identifier] = digest
        selected[identifier] = guide
    return paths, selected, hashes


def cache_package(cache_root: Path, archive: Path) -> None:
    command = [
        "node",
        str(ROOT / "Scripts/cache-fhir-package.cjs"),
        "--cache-root",
        str(cache_root),
        str(archive),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise DomainValidationError(
            f"unable to cache exact FHIR package {archive.name}:\n{result.stdout}\n{result.stderr}"
        )


def issue_message_id(issue: Mapping[str, Any]) -> str | None:
    values = [
        extension.get("valueCode") or extension.get("valueString")
        for extension in issue.get("extension", [])
        if isinstance(extension, dict) and extension.get("url") == MESSAGE_ID_URL
    ]
    values = [value for value in values if isinstance(value, str)]
    if len(values) > 1:
        raise DomainValidationError("Validator issue has duplicate message-id extensions")
    return values[0] if values else None


def outcome_file(outcome: Mapping[str, Any]) -> Path:
    values = [
        extension.get("valueString")
        for extension in outcome.get("extension", [])
        if isinstance(extension, dict) and extension.get("url") == FILE_URL
    ]
    values = [value for value in values if isinstance(value, str)]
    if len(values) != 1:
        raise DomainValidationError("Validator OperationOutcome must identify exactly one input file")
    return Path(values[0]).resolve()


def operation_outcomes(path: Path) -> dict[Path, Mapping[str, Any]]:
    value = load_json(path, "FHIR Validator outcome")
    if value.get("resourceType") == "OperationOutcome":
        outcomes = [value]
    elif value.get("resourceType") == "Bundle" and isinstance(value.get("entry"), list):
        if any(
            not isinstance(entry, dict)
            or not isinstance(entry.get("resource"), dict)
            for entry in value["entry"]
        ):
            raise DomainValidationError(
                "FHIR Validator output Bundle contains a malformed entry"
            )
        outcomes = [entry["resource"] for entry in value["entry"]]
    else:
        raise DomainValidationError("FHIR Validator output is not an OperationOutcome Bundle")
    indexed: dict[Path, Mapping[str, Any]] = {}
    for outcome in outcomes:
        if outcome.get("resourceType") != "OperationOutcome":
            raise DomainValidationError("FHIR Validator output Bundle contains a non-OperationOutcome")
        source = outcome_file(outcome)
        if source in indexed:
            raise DomainValidationError(f"duplicate Validator outcome for {source}")
        indexed[source] = outcome
    return indexed


def validate_expectations(value: Any, case_ids: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise DomainValidationError("validator expectations must use schemaVersion 1")
    if set(value) != {"schemaVersion", "warningAllowlist", "cases"}:
        raise DomainValidationError("validator expectations contain unsupported fields")
    allowlist = value.get("warningAllowlist")
    cases = value.get("cases")
    if not isinstance(allowlist, list) or not all(isinstance(item, dict) for item in allowlist):
        raise DomainValidationError("warningAllowlist must be a list of matcher objects")
    if not isinstance(cases, dict) or set(cases) != case_ids:
        raise DomainValidationError("validator expectations must exactly cover corpus cases")
    allowed_fields = {"messageId", "expression", "detailsContains", "code"}
    normalized_cases: dict[str, list[Mapping[str, str]]] = {}
    labeled_matchers: list[tuple[str, Any]] = [
        ("warning allowlist", item) for item in allowlist
    ]
    for identifier, declared in cases.items():
        matchers = declared if isinstance(declared, list) else [declared]
        if not matchers:
            raise DomainValidationError(
                f"case {identifier} must declare at least one exact error matcher"
            )
        normalized_cases[identifier] = matchers
        labeled_matchers.extend(
            (f"case {identifier}", matcher) for matcher in matchers
        )
    for label, matcher in labeled_matchers:
        if not isinstance(matcher, dict) or not matcher or not set(matcher) <= allowed_fields:
            raise DomainValidationError(f"{label} contains an invalid issue matcher")
        if not all(isinstance(item, str) and item for item in matcher.values()):
            raise DomainValidationError(f"{label} matcher values must be nonempty strings")
    return {
        "schemaVersion": 1,
        "warningAllowlist": allowlist,
        "cases": normalized_cases,
    }


def issue_matches(issue: Mapping[str, Any], matcher: Mapping[str, str]) -> bool:
    if "messageId" in matcher and issue_message_id(issue) != matcher["messageId"]:
        return False
    if "code" in matcher and issue.get("code") != matcher["code"]:
        return False
    expressions = issue.get("expression", [])
    if "expression" in matcher and matcher["expression"] not in expressions:
        return False
    details = issue.get("details")
    text = details.get("text", "") if isinstance(details, dict) else ""
    if "detailsContains" in matcher and matcher["detailsContains"] not in text:
        return False
    return True


def validate_outcomes(
    outcomes: Mapping[Path, Mapping[str, Any]],
    valid_paths: set[Path],
    case_paths: Mapping[str, Path],
    expectations: Mapping[str, Any],
) -> tuple[int, list[str]]:
    expected_paths = valid_paths | set(case_paths.values())
    failures: list[str] = []
    if set(outcomes) != expected_paths:
        missing = sorted(str(path) for path in expected_paths - outcomes.keys())
        extra = sorted(str(path) for path in outcomes.keys() - expected_paths)
        if missing:
            failures.append("Validator outcomes missing inputs: " + ", ".join(missing))
        if extra:
            failures.append("Validator outcomes contain extra inputs: " + ", ".join(extra))

    warning_count = 0
    warning_allowlist = expectations["warningAllowlist"]
    warning_match_counts = [0] * len(warning_allowlist)
    for path, outcome in outcomes.items():
        issues = outcome.get("issue", [])
        if not isinstance(issues, list):
            failures.append(f"{path.name}: OperationOutcome.issue must be a list")
            continue
        errors = [
            issue
            for issue in issues
            if isinstance(issue, dict) and issue.get("severity") in {"fatal", "error"}
        ]
        warnings = [
            issue
            for issue in issues
            if isinstance(issue, dict) and issue.get("severity") == "warning"
        ]
        warning_count += len(warnings)
        for warning in warnings:
            matches = [
                index
                for index, matcher in enumerate(warning_allowlist)
                if issue_matches(warning, matcher)
            ]
            if len(matches) != 1:
                failures.append(
                    f"{path.name}: warning matched {len(matches)} allowlist entries; "
                    f"expected exactly one: {json.dumps(warning, sort_keys=True)}"
                )
            else:
                warning_match_counts[matches[0]] += 1
        if path in valid_paths:
            if errors:
                failures.append(
                    f"{path.name}: expected valid, found {json.dumps(errors, sort_keys=True)}"
                )
            continue
        case_id = next(identifier for identifier, candidate in case_paths.items() if candidate == path)
        matchers = expectations["cases"][case_id]
        error_matches = [
            [
                index
                for index, matcher in enumerate(matchers)
                if issue_matches(error, matcher)
            ]
            for error in errors
        ]
        matcher_matches = [
            [
                index
                for index, error in enumerate(errors)
                if issue_matches(error, matcher)
            ]
            for matcher in matchers
        ]
        if (
            len(errors) != len(matchers)
            or any(len(matches) != 1 for matches in error_matches)
            or any(len(matches) != 1 for matches in matcher_matches)
        ):
            failures.append(
                f"{path.name}: errors did not match the declared exact one-to-one set "
                f"{json.dumps(matchers, sort_keys=True)}; found "
                f"{json.dumps(errors, sort_keys=True)}"
            )
    for index, count in enumerate(warning_match_counts):
        if count == 0:
            failures.append(
                "warning allowlist entry matched no warning: "
                + json.dumps(warning_allowlist[index], sort_keys=True)
            )
    return warning_count, failures


def validate_guide(
    identifier: str,
    corpus: Mapping[str, Any],
    package: Path,
    validator: Path,
    java_home: Path,
    cache_root: Path,
    temporary: Path,
) -> tuple[dict[str, Any], list[str]]:
    manifest_path = resolve_repository_path(corpus.get("manifest"), f"corpus {identifier} manifest")
    expectation_path = resolve_repository_path(
        corpus.get("validatorExpectations"), f"corpus {identifier} expectations"
    )
    manifest = load_manifest(manifest_path)
    expectations = validate_expectations(
        load_json(expectation_path, f"corpus {identifier} validator expectations"),
        {case["id"] for case in manifest["cases"]},
    )
    materialized = temporary / identifier
    index = materialize_corpus(manifest_path, materialized)
    valid_paths = {
        (materialized / base["path"]).resolve() for base in index["bases"]
    }
    additional = corpus.get("additionalValidResources", [])
    if not isinstance(additional, list):
        raise DomainValidationError(f"corpus {identifier} additionalValidResources must be a list")
    for item in additional:
        valid_paths.add(resolve_repository_path(item, f"corpus {identifier} additional valid resource"))
    case_paths = {
        case["id"]: (materialized / case["path"]).resolve() for case in index["cases"]
    }
    output = temporary / f"{identifier}-validator-outcome.json"
    command = [
        "java",
        f"-Duser.home={java_home}",
        "-jar",
        str(validator),
        str((materialized / "valid").resolve()),
        str((materialized / "invalid").resolve()),
        *(str(path) for path in sorted(valid_paths) if path.parent != (materialized / "valid").resolve()),
        "-recurse",
        "-version",
        "4.0.1",
        "-ig",
        str(package),
        "-tx",
        "n/a",
        "-txCache",
        str(temporary / "tx-cache"),
        "-no-http-access",
        "-allow-example-urls",
        "true",
        "-level",
        "warnings",
        "-output-style",
        "json",
        "-output",
        str(output),
    ]
    environment = os.environ.copy()
    environment["FHIR_TX_CACHE"] = str(temporary / "tx-cache")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, env=environment)
    if not output.is_file():
        raise DomainValidationError(
            f"FHIR Validator wrote no outcome for {identifier} (exit {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    outcomes = operation_outcomes(output)
    warning_count, failures = validate_outcomes(
        outcomes, valid_paths, case_paths, expectations
    )
    return (
        {
            "id": identifier,
            "baseCount": len(index["bases"]),
            "caseCount": len(index["cases"]),
            "additionalValidCount": len(additional),
            "warningCount": warning_count,
        },
        failures,
    )


def fhir_resource_count(resource: Any) -> int:
    if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
        raise DomainValidationError("external FHIR JSON must contain a FHIR resource object")
    count = 1
    contained = resource.get("contained", [])
    if contained is not None:
        if not isinstance(contained, list):
            raise DomainValidationError("FHIR contained must be a list")
        count += sum(fhir_resource_count(item) for item in contained)
    if resource.get("resourceType") == "Bundle":
        entries = resource.get("entry", [])
        if not isinstance(entries, list):
            raise DomainValidationError("FHIR Bundle.entry must be a list")
        count += sum(
            fhir_resource_count(entry.get("resource"))
            for entry in entries
            if isinstance(entry, dict) and entry.get("resource") is not None
        )
    return count


def unknown_extension_shape(
    resource: Mapping[str, Any],
    filename: str,
) -> list[dict[str, str]]:
    """Return the exact ordered extension tree for a legacy FHIR witness."""
    resource_type = resource.get("resourceType")
    if not isinstance(resource_type, str) or not resource_type:
        raise DomainValidationError("legacy extension witness must have a resourceType")
    result: list[dict[str, str]] = []

    def walk(value: Any, expression: str) -> None:
        if isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{expression}[{index}]")
            return
        if not isinstance(value, dict):
            return
        for extension_field in ("extension", "modifierExtension"):
            if extension_field not in value:
                continue
            extensions = value[extension_field]
            if not isinstance(extensions, list) or not extensions:
                raise DomainValidationError(
                    f"legacy extension field {expression}.{extension_field} must be a nonempty list"
                )
            for index, extension in enumerate(extensions):
                extension_expression = f"{expression}.{extension_field}[{index}]"
                if not isinstance(extension, dict):
                    raise DomainValidationError(
                        f"legacy extension {extension_expression} must be an object"
                    )
                url = extension.get("url")
                payload_fields = [
                    key
                    for key in extension
                    if key == "extension" or key.startswith("value")
                ]
                if (
                    not isinstance(url, str)
                    or not url
                    or len(payload_fields) != 1
                    or set(extension) != {"url", payload_fields[0]}
                ):
                    raise DomainValidationError(
                        f"legacy extension {extension_expression} does not have an exact "
                        "url-plus-one-value shape"
                    )
                result.append(
                    {
                        "path": filename,
                        "expression": extension_expression,
                        "url": url,
                        "valueField": payload_fields[0],
                    }
                )
                walk(extension, extension_expression)
        for key, child in value.items():
            if key not in {"extension", "modifierExtension"}:
                walk(child, f"{expression}.{key}")

    walk(resource, resource_type)
    return result


def expected_unknown_extension_issue_matches(
    issue: Mapping[str, Any], expectation: Mapping[str, str]
) -> bool:
    details = issue.get("details")
    expected_text = (
        f"The extension {expectation['url']} could not be found so is not allowed here"
    )
    return (
        issue.get("severity") == "error"
        and issue.get("code") == "structure"
        and issue_message_id(issue) == "Extension_EXT_Unknown_NotHere"
        and issue.get("expression") == [expectation["expression"]]
        and isinstance(details, dict)
        and details.get("text") == expected_text
    )


def validate_external_fhir(
    files: Sequence[tuple[str, str, Path]],
    set_reports: list[dict[str, Any]],
    expected_unknown_extensions: Mapping[
        tuple[str, str], Sequence[Mapping[str, str]]
    ],
    package_paths: Mapping[str, Path],
    validator: Path,
    java_home: Path,
    temporary: Path,
) -> tuple[dict[str, Any], list[str]]:
    if not files:
        return {
            "setCount": len(set_reports),
            "fhirInputCount": 0,
            "resourceCount": 0,
            "warningCount": 0,
            "expectedErrorCount": 0,
            "sets": set_reports,
        }, []
    reports_by_file = {
        (item["id"], file_report["path"]): file_report
        for item in set_reports
        for file_report in item["files"]
    }
    resource_count = 0
    for set_id, name, path in files:
        resource = load_json(path, f"external FHIR {set_id}/{name}")
        count = fhir_resource_count(resource)
        reports_by_file[(set_id, name)]["resourceCount"] = count
        resource_count += count
    failures: list[str] = []
    for set_id, name, path in files:
        expectations = list(expected_unknown_extensions.get((set_id, name), []))
        if expectations:
            actual_shape = unknown_extension_shape(
                load_json(path, f"legacy external FHIR {set_id}/{name}"), name
            )
            if actual_shape != expectations:
                failures.append(
                    f"external FHIR {set_id}/{name} legacy extension shape differs from "
                    f"its exact contract; expected {json.dumps(expectations, sort_keys=True)}, "
                    f"found {json.dumps(actual_shape, sort_keys=True)}"
                )

    accepted_files = [
        item for item in files if (item[0], item[1]) not in expected_unknown_extensions
    ]
    legacy_files = [
        item for item in files if (item[0], item[1]) in expected_unknown_extensions
    ]
    outcomes: dict[Path, Mapping[str, Any]] = {}
    for scope, scoped_files, include_packages in (
        ("accepted-package-closure", accepted_files, True),
        ("r4-core", legacy_files, False),
    ):
        if not scoped_files:
            continue
        output = temporary / f"external-fhir-{scope}-validator-outcome.json"
        command = [
            "java",
            f"-Duser.home={java_home}",
            "-jar",
            str(validator),
            *(str(path) for _set_id, _name, path in scoped_files),
            "-version",
            "4.0.1",
        ]
        if include_packages:
            for package in (
                package_paths[identifier] for identifier in sorted(package_paths)
            ):
                command.extend(("-ig", str(package)))
        command.extend(
            (
                "-tx",
                "n/a",
                "-txCache",
                str(temporary / "tx-cache"),
                "-no-http-access",
                "-allow-example-urls",
                "true",
                "-level",
                "errors",
                "-output-style",
                "json",
                "-output",
                str(output),
            )
        )
        environment = os.environ.copy()
        environment["FHIR_TX_CACHE"] = str(temporary / "tx-cache")
        result = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, env=environment
        )
        if not output.is_file():
            raise DomainValidationError(
                f"FHIR Validator wrote no {scope} external evidence outcome "
                f"(exit {result.returncode}):\n{result.stdout}\n{result.stderr}"
            )
        scoped_outcomes = operation_outcomes(output)
        scoped_paths = {path.resolve() for _set_id, _name, path in scoped_files}
        if set(scoped_outcomes) != scoped_paths:
            failures.append(
                f"external FHIR Validator {scope} outcomes do not exactly match declared inputs"
            )
        if set(outcomes) & set(scoped_outcomes):
            failures.append("external FHIR Validator returned a file in multiple scopes")
        outcomes.update(scoped_outcomes)
        allowed_returncodes = {0, 1} if scope == "r4-core" else {0}
        if result.returncode not in allowed_returncodes:
            failures.append(
                f"external FHIR Validator {scope} exited {result.returncode}; "
                f"expected one of {sorted(allowed_returncodes)}"
            )

    warning_count = 0
    reverse = {path.resolve(): (set_id, name) for set_id, name, path in files}
    for path, outcome in outcomes.items():
        issues = outcome.get("issue", [])
        if not isinstance(issues, list):
            failures.append(f"external FHIR {reverse.get(path, ('unknown', path.name))} has malformed issues")
            continue
        if any(
            not isinstance(issue, dict)
            or issue.get("severity")
            not in {"fatal", "error", "warning", "information"}
            for issue in issues
        ):
            failures.append(
                f"external FHIR {reverse.get(path, ('unknown', path.name))} "
                "has a malformed issue"
            )
            continue
        errors = [
            issue
            for issue in issues
            if issue.get("severity") in {"fatal", "error"}
        ]
        warning_count += sum(
            1
            for issue in issues
            if issue.get("severity") == "warning"
        )
        set_id, name = reverse.get(path, ("unknown", path.name))
        expectations = list(expected_unknown_extensions.get((set_id, name), []))
        if expectations:
            error_matches = [
                [
                    index
                    for index, expectation in enumerate(expectations)
                    if expected_unknown_extension_issue_matches(error, expectation)
                ]
                for error in errors
            ]
            expectation_matches = [
                [
                    index
                    for index, error in enumerate(errors)
                    if expected_unknown_extension_issue_matches(error, expectation)
                ]
                for expectation in expectations
            ]
            if (
                len(errors) != len(expectations)
                or any(len(matches) != 1 for matches in error_matches)
                or any(len(matches) != 1 for matches in expectation_matches)
            ):
                failures.append(
                    f"external FHIR {set_id}/{name} errors did not match its exact "
                    f"unknown-extension contract: {json.dumps(errors, sort_keys=True)}"
                )
        elif errors:
            failures.append(
                f"external FHIR {set_id}/{name} has error diagnostics: "
                + json.dumps(errors, sort_keys=True)
            )
    return (
        {
            "setCount": len(set_reports),
            "fhirInputCount": len(files),
            "resourceCount": resource_count,
            "warningCount": warning_count,
            "expectedErrorCount": sum(
                len(expectations)
                for expectations in expected_unknown_extensions.values()
            ),
            "sets": set_reports,
        },
        failures,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--toolchain", type=Path, default=DEFAULT_TOOLCHAIN)
    parser.add_argument("--corpus-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--tools-directory", type=Path, default=DEFAULT_TOOLS)
    parser.add_argument("--validator", type=Path)
    parser.add_argument("--evidence-lock", type=Path)
    parser.add_argument("--require-evidence-lock", action="store_true")
    parser.add_argument("--package", action="append", default=[], metavar="GUIDE=PATH")
    parser.add_argument(
        "--external-evidence",
        action="append",
        default=[],
        metavar="EVIDENCE_SET_ID=PATH",
    )
    parser.add_argument("--require-external-evidence", action="store_true")
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args(argv)

    try:
        evidence = load_json(arguments.evidence.resolve(), "evidence manifest")
        toolchain = load_json(arguments.toolchain.resolve(), "toolchain")
        corpus_index = load_json(arguments.corpus_index.resolve(), "corpus index")
        if corpus_index.get("schemaVersion") != 1:
            raise DomainValidationError("corpus index schemaVersion must be 1")
        corpora = unique_by_id(corpus_index.get("domainCorpora"), "domain corpora")
        coverage_path = resolve_repository_path(
            corpus_index.get("coverage"), "domain corpus coverage inventory"
        )
        external_supplied = parse_external_evidence(arguments.external_evidence)
        (
            external_reports,
            external_files,
            expected_unknown_extensions,
        ) = resolve_external_evidence(
            evidence, external_supplied, arguments.require_external_evidence
        )
        guide_ids = set(corpora)
        if external_files:
            guide_ids = set(unique_by_id(evidence.get("guides"), "evidence guides"))
        overrides = parse_overrides(arguments.package)
        lock_path = arguments.evidence_lock.resolve() if arguments.evidence_lock else None
        if lock_path is None and DEFAULT_LOCK.is_file():
            lock_path = DEFAULT_LOCK.resolve()
        if arguments.require_evidence_lock and lock_path is None:
            raise DomainValidationError("--require-evidence-lock needs an evidence lock")
        lock_hashes = locked_package_hashes(lock_path)
        package_paths, guides, package_hashes = resolve_guide_packages(
            evidence, guide_ids, overrides, lock_hashes
        )

        artifacts = tool_artifacts(toolchain)
        validators = [
            artifact
            for artifact in artifacts
            if artifact.get("id") == "fhir-validator" and artifact.get("kind") == "jar"
        ]
        if len(validators) != 1:
            raise DomainValidationError("toolchain must declare exactly one fhir-validator JAR")
        validator_artifact = validators[0]
        coverage_reports = validate_domain_coverage(
            coverage_path, corpora, validator_artifact["version"]
        )
        validator = (
            arguments.validator.resolve()
            if arguments.validator
            else (arguments.tools_directory.resolve() / "validator_cli.jar")
        )
        verify_regular_file(
            validator, validator_artifact["sha256"], "FHIR Validator JAR"
        )

        package_artifacts = sorted(
            (
                artifact
                for artifact in artifacts
                if artifact.get("kind") == "fhir-package"
            ),
            key=lambda artifact: (artifact["id"], artifact["version"]),
        )
        tools_directory = arguments.tools_directory.resolve()
        archive_paths: list[tuple[Mapping[str, Any], Path]] = []
        for artifact in package_artifacts:
            archive = tools_directory / f"{artifact['id']}-{artifact['version']}.tgz"
            verify_regular_file(
                archive,
                artifact["sha256"],
                f"FHIR package {artifact['id']}#{artifact['version']}",
            )
            metadata = package_metadata(archive)
            if metadata.get("name") != artifact["id"] or metadata.get("version") != artifact["version"]:
                raise DomainValidationError(
                    f"FHIR package archive identity mismatch: {artifact['id']}#{artifact['version']}"
                )
            archive_paths.append((artifact, archive))

        failures: list[str] = []
        guide_reports: list[dict[str, Any]] = []
        external_report: dict[str, Any] | None = None
        with tempfile.TemporaryDirectory(prefix="grove-domain-validator-") as directory:
            temporary = Path(directory)
            java_home = temporary / "home"
            cache_root = java_home / ".fhir/packages"
            cache_root.mkdir(parents=True)
            for _artifact, archive in archive_paths:
                cache_package(cache_root, archive)
            for identifier in sorted(package_paths):
                cache_package(cache_root, package_paths[identifier])
            for identifier, corpus in sorted(corpora.items()):
                report, corpus_failures = validate_guide(
                    identifier,
                    corpus,
                    package_paths[identifier],
                    validator,
                    java_home,
                    cache_root,
                    temporary,
                )
                guide = guides[identifier]
                report.update(
                    {
                        "packageId": guide["packageId"],
                        "version": guide["version"],
                        "sha256": package_hashes[identifier],
                    }
                )
                guide_reports.append(report)
                failures.extend(f"{identifier}: {failure}" for failure in corpus_failures)
            if external_supplied or arguments.require_external_evidence:
                external_report, external_failures = validate_external_fhir(
                    external_files,
                    external_reports,
                    expected_unknown_extensions,
                    package_paths,
                    validator,
                    java_home,
                    temporary,
                )
                failures.extend(external_failures)

        if failures:
            print("Domain FHIR validation failed:", file=sys.stderr)
            for failure in failures:
                print(f"- {failure}", file=sys.stderr)
            return 1
        report = {
            "kind": "grove-domain-fhir-validation",
            "schemaVersion": 1,
            "validator": {
                "id": validator_artifact["id"],
                "version": validator_artifact["version"],
                "sha256": validator_artifact["sha256"],
            },
            "fhirPackageClosure": [
                {
                    "id": artifact["id"],
                    "version": artifact["version"],
                    "sha256": artifact["sha256"],
                }
                for artifact, _path in archive_paths
            ],
            "guides": guide_reports,
            "coverage": coverage_reports,
        }
        if external_report is not None:
            report["externalEvidence"] = external_report
        if arguments.report:
            arguments.report.parent.mkdir(parents=True, exist_ok=True)
            arguments.report.write_bytes(canonical_json_bytes(report))
        print(
            f"Validated {sum(item['baseCount'] for item in guide_reports)} bases, "
            f"{sum(item['caseCount'] for item in guide_reports)} one-mutation cases, and "
            f"{sum(item['additionalValidCount'] for item in guide_reports)} additional valid "
            f"resources with FHIR Validator {validator_artifact['version']}"
            + (
                f"; independently validated {external_report['fhirInputCount']} external FHIR files"
                if external_report is not None
                else ""
            )
        )
        return 0
    except (DomainValidationError, OSError, ValueError) as error:
        print(f"Domain FHIR validation could not run: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
