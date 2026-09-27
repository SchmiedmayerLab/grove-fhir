#!/usr/bin/env python3
"""Run the official FHIR Validator over every committed Grove FHIR fixture."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from Scripts.producer_validation.diagnostics import ProducerValidationError
    from Scripts.producer_validation.external_validator import (
        collect_validator_outcomes, reject_validator_errors, run_validator,
        validator_error_messages,
    )
    from Scripts.producer_validation.io import read_json, resolve_unlinked_regular_file
    from Scripts.producer_validation.manifest import parse_package_arguments
except ModuleNotFoundError:  # Direct `python Scripts/validate-fixtures.py` execution.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from producer_validation.diagnostics import ProducerValidationError  # type: ignore[no-redef]
    from producer_validation.external_validator import (  # type: ignore[no-redef]
        collect_validator_outcomes, reject_validator_errors, run_validator,
        validator_error_messages,
    )
    from producer_validation.io import (  # type: ignore[no-redef]
        read_json, resolve_unlinked_regular_file,
    )
    from producer_validation.manifest import parse_package_arguments  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "Conformance/fixture-validator-manifest.json"
GROVE_CANONICAL_PREFIX = "https://grovealliance.org/fhir/"
NEGATIVE_CORPUS_KEYS = {"schemaVersion", "purpose", "profile", "control", "cases"}
NEGATIVE_CASE_EXPECTATIONS = {"expectedInvariant", "expectedBinding"}
REQUIRED_BINDING_FAILURE = "a coding from this value set is required"


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json(path)
    required = {
        "schemaVersion", "fhirVersion", "purpose", "roots", "packages",
        "resources", "negativeCorpora", "excluded",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ProducerValidationError(
            "fixture validator manifest must declare exactly "
            + ", ".join(sorted(required))
        )
    if manifest["schemaVersion"] != 0 or manifest["fhirVersion"] != "4.0.1":
        raise ProducerValidationError(
            "fixture validator manifest must use schemaVersion 0 and FHIR 4.0.1"
        )
    return manifest


def relative_path(
    value: Any, label: str, base: PurePosixPath = PurePosixPath()
) -> PurePosixPath:
    """Resolve one manifest path without escaping the repository or traversing links."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ProducerValidationError(f"{label} must be a safe relative POSIX path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != value:
        raise ProducerValidationError(f"{label} must be a safe relative POSIX path")
    relative = base / relative
    path = ROOT
    for part in relative.parts:
        path /= part
        if path.is_symlink():
            raise ProducerValidationError(f"{label} may not traverse a symlink: {value}")
    return relative


def committed_json_files(manifest: dict[str, Any]) -> set[str]:
    """Every JSON file the declared fixture roots contain, whatever its shape."""
    found: set[str] = set()
    for index, root in enumerate(manifest["roots"]):
        relative = relative_path(root, f"roots[{index}]")
        directory = ROOT / relative
        if not directory.is_dir():
            raise ProducerValidationError(f"fixture root {root} is not a directory")
        for path in directory.rglob("*.json"):
            if path.is_symlink() or not path.is_file():
                raise ProducerValidationError(f"{path} is not a regular file")
            found.add(path.relative_to(ROOT).as_posix())
    return found


def declared_resources(manifest: dict[str, Any]) -> list[tuple[Path, list[str]]]:
    """Bind each declared fixture to the exact Grove profile set it must satisfy."""
    resources: list[tuple[Path, list[str]]] = []
    for index, entry in enumerate(manifest["resources"]):
        label = f"resources[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"path", "profiles"}:
            raise ProducerValidationError(f"{label} must declare exactly path and profiles")
        relative = relative_path(entry["path"], f"{label}.path")
        path = ROOT / relative
        if not path.is_file():
            raise ProducerValidationError(f"{label}.path is not a regular file")
        profiles = entry["profiles"]
        if not isinstance(profiles, list) or any(
            not isinstance(profile, str) or not profile.startswith(GROVE_CANONICAL_PREFIX)
            for profile in profiles
        ):
            raise ProducerValidationError(f"{label}.profiles must be Grove canonical URLs")
        resource = read_json(path)
        if not isinstance(resource, dict) or not isinstance(
            resource.get("resourceType"), str
        ):
            raise ProducerValidationError(f"{label} is not a FHIR resource")
        claimed = resource.get("meta", {}).get("profile", [])
        if not isinstance(claimed, list):
            claimed = []
        # The Validator only checks what a resource itself claims, so the manifest and the
        # fixture have to agree or the lane would silently validate nothing.
        if [
            profile for profile in claimed if profile.startswith(GROVE_CANONICAL_PREFIX)
        ] != profiles:
            raise ProducerValidationError(
                f"{label} declares {profiles} but the fixture claims {claimed}"
            )
        resources.append((path, profiles))
    return resources


def corpus_member(directory: PurePosixPath, value: Any, label: str, profile: str) -> Path:
    """One Observation of a negative corpus, claiming exactly the corpus profile."""
    path = ROOT / relative_path(value, label, directory)
    if not path.is_file():
        raise ProducerValidationError(f"{label} is not a regular file")
    resource = read_json(path)
    if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
        raise ProducerValidationError(f"{label} is not a FHIR resource")
    if resource.get("meta", {}).get("profile") != [profile]:
        raise ProducerValidationError(f"{label} must claim exactly {profile}")
    return path


def declared_negative_corpora(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Bind each negative corpus to the control it must pass and the cases it must reject."""
    corpora: list[dict[str, Any]] = []
    for index, value in enumerate(manifest["negativeCorpora"]):
        label = f"negativeCorpora[{index}]"
        relative = relative_path(value, label)
        path = ROOT / relative
        if not path.is_file():
            raise ProducerValidationError(f"{label} is not a regular file")
        corpus = read_json(path)
        if (
            not isinstance(corpus, dict)
            or set(corpus) != NEGATIVE_CORPUS_KEYS
            or corpus["schemaVersion"] != 0
        ):
            raise ProducerValidationError(
                f"{label} must declare exactly "
                + ", ".join(sorted(NEGATIVE_CORPUS_KEYS))
                + " at schemaVersion 0"
            )
        profile = corpus["profile"]
        if not isinstance(profile, str) or not profile.startswith(GROVE_CANONICAL_PREFIX):
            raise ProducerValidationError(f"{label}.profile must be a Grove canonical URL")
        control = corpus_member(relative.parent, corpus["control"], f"{label}.control", profile)
        cases: list[dict[str, Any]] = []
        if not isinstance(corpus["cases"], list) or not corpus["cases"]:
            raise ProducerValidationError(f"{label}.cases must name at least one case")
        for case_index, case in enumerate(corpus["cases"]):
            case_label = f"{label}.cases[{case_index}]"
            if (
                not isinstance(case, dict)
                or "path" not in case
                or len(set(case) & NEGATIVE_CASE_EXPECTATIONS) != 1
                or set(case) - NEGATIVE_CASE_EXPECTATIONS - {"path", "alsoRejected"}
            ):
                raise ProducerValidationError(
                    f"{case_label} must declare path, exactly one of expectedInvariant or "
                    "expectedBinding, and at most alsoRejected"
                )
            also_rejected = case.get("alsoRejected", [])
            expectation = next(iter(set(case) & NEGATIVE_CASE_EXPECTATIONS))
            if (
                not isinstance(case[expectation], str)
                or not case[expectation]
                or not isinstance(also_rejected, list)
                or any(not isinstance(item, str) or not item for item in also_rejected)
            ):
                raise ProducerValidationError(
                    f"{case_label} expectations must be nonempty strings"
                )
            case_path = corpus_member(relative.parent, case["path"], f"{case_label}.path", profile)
            if case_path == control or any(case_path == other["path"] for other in cases):
                raise ProducerValidationError(f"{case_label}.path repeats a corpus member")
            cases.append({**case, "path": case_path})
        corpora.append({"manifest": path, "control": control, "cases": cases})
    return corpora


def expected_rejections(case: dict[str, Any]) -> list[tuple[str, ...]]:
    """The Validator phrases one case must be rejected with, as fragments one message carries."""
    if "expectedInvariant" in case:
        expected = [(f"Constraint failed: {case['expectedInvariant']}:",)]
    else:
        expected = [(case["expectedBinding"], REQUIRED_BINDING_FAILURE)]
    expected.extend((fragment,) for fragment in case.get("alsoRejected", []))
    return expected


def reject_negative_case(case: dict[str, Any], outcome: dict[str, Any]) -> None:
    """Require every declared rejection and refuse any the case does not declare."""
    label = case["path"].name
    errors = validator_error_messages(outcome, label)
    for fragments in expected_rejections(case):
        if not any(all(fragment in error for fragment in fragments) for error in errors):
            raise ProducerValidationError(
                f"FHIR Validator did not reject {label} for {' and '.join(fragments)!r}: "
                + (" | ".join(errors) or "no errors")
            )
    for error in errors:
        if not any(
            all(fragment in error for fragment in fragments)
            for fragments in expected_rejections(case)
        ):
            raise ProducerValidationError(
                f"FHIR Validator rejected {label} for an undeclared reason: {error}"
            )


def reject_negative_corpus(
    validator: Path, packages: list[Path], corpus: dict[str, Any]
) -> None:
    outcomes = dict(
        collect_validator_outcomes(
            validator,
            packages,
            [corpus["control"], *(case["path"] for case in corpus["cases"])],
            allow_example_urls=True,
        )
    )
    reject_validator_errors(outcomes[corpus["control"]], corpus["control"].name)
    for case in corpus["cases"]:
        reject_negative_case(case, outcomes[case["path"]])


def validate_coverage(
    manifest: dict[str, Any],
) -> tuple[list[tuple[Path, list[str]]], list[dict[str, Any]]]:
    """Refuse a committed fixture that is neither validated, rejected on record nor excluded."""
    resources = declared_resources(manifest)
    corpora = declared_negative_corpora(manifest)
    validated = {path.relative_to(ROOT).as_posix() for path, _ in resources}
    rejected = {
        member.relative_to(ROOT).as_posix()
        for corpus in corpora
        for member in (
            corpus["manifest"], corpus["control"], *(case["path"] for case in corpus["cases"]),
        )
    }
    excluded: dict[str, str] = {}
    for index, entry in enumerate(manifest["excluded"]):
        label = f"excluded[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"path", "reason"}:
            raise ProducerValidationError(f"{label} must declare exactly path and reason")
        relative = relative_path(entry["path"], f"{label}.path")
        if not (ROOT / relative).is_file():
            raise ProducerValidationError(f"{label}.path is not a regular file")
        if not isinstance(entry["reason"], str) or not entry["reason"]:
            raise ProducerValidationError(f"{label} must state why it is not validated")
        excluded[relative.as_posix()] = entry["reason"]
    overlap = (validated & set(excluded)) | (rejected & (validated | set(excluded)))
    if overlap:
        raise ProducerValidationError(
            "a fixture is classified twice: " + ", ".join(sorted(overlap))
        )
    present = committed_json_files(manifest)
    unlisted = present - validated - rejected - set(excluded)
    if unlisted:
        raise ProducerValidationError(
            "every committed fixture must be validated, rejected by a negative corpus "
            "or excluded with a reason: " + ", ".join(sorted(unlisted))
        )
    missing = (validated | rejected | set(excluded)) - present
    if missing:
        raise ProducerValidationError(
            "the manifest names files the fixture roots do not contain: "
            + ", ".join(sorted(missing))
        )
    return resources, corpora


def resolve_packages(manifest: dict[str, Any], supplied: dict[str, Path]) -> list[Path]:
    aliases = {package["alias"] for package in manifest["packages"]}
    if set(supplied) != aliases:
        raise ProducerValidationError(
            "package arguments do not match the manifest: expected "
            + ", ".join(sorted(aliases))
        )
    return [
        resolve_unlinked_regular_file(supplied[package["alias"]], "FHIR package")
        for package in manifest["packages"]
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--validator", type=Path)
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="check that every committed fixture is classified, without running the Validator",
    )
    arguments = parser.parse_args(argv)
    try:
        manifest = load_manifest(
            resolve_unlinked_regular_file(arguments.manifest, "manifest")
        )
        resources, corpora = validate_coverage(manifest)
        cases = sum(len(corpus["cases"]) for corpus in corpora)
        if arguments.coverage_only:
            if arguments.package or arguments.validator is not None:
                raise ProducerValidationError(
                    "--coverage-only cannot be combined with package or Validator arguments"
                )
            print(
                f"Classified {len(resources)} validated, {cases} rejected and "
                f"{len(manifest['excluded'])} excluded committed fixture(s)"
            )
            return 0
        if arguments.validator is None:
            raise ProducerValidationError(
                "--validator is required unless --coverage-only is used"
            )
        packages = resolve_packages(manifest, parse_package_arguments(arguments.package))
        run_validator(
            arguments.validator,
            packages,
            [path for path, _ in resources],
            allow_example_urls=True,
        )
        for corpus in corpora:
            reject_negative_corpus(arguments.validator, packages, corpus)
    except ProducerValidationError as error:
        print(f"Fixture validation failed: {error}", file=sys.stderr)
        return 1
    print(
        f"Validated {len(resources)} committed fixture(s) and rejected {cases} negative "
        "case(s) for their declared reasons with the official FHIR Validator"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
