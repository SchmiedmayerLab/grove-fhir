#!/usr/bin/env python3
"""Run the official FHIR Validator with the exact Grove Questionnaire package."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from questionnaire_fixture_corpus import apply_mutation, load_json, write_json


ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "questionnaire/fixtures/validator"
EXPECTATIONS = CORPUS / "validator-expectations.json"
MESSAGE_ID_URL = "http://hl7.org/fhir/StructureDefinition/operationoutcome-message-id"
PROFILES = {
    "Questionnaire": (
        "https://schmiedmayerlab.github.io/grove-fhir/fhir/questionnaire/"
        "StructureDefinition/grove-questionnaire"
    ),
    "QuestionnaireResponse": (
        "https://schmiedmayerlab.github.io/grove-fhir/fhir/questionnaire/"
        "StructureDefinition/grove-questionnaire-response"
    ),
}


def resolve_corpus_file(root: Path, value: Any, label: str) -> Path:
    """Resolve one manifest path without escaping or traversing links."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{label} must be a safe relative POSIX path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != value:
        raise ValueError(f"{label} must be a safe relative POSIX path")
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"{label} root must be a regular directory")
    path = root
    for part in relative.parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"{label} may not traverse a symlink: {path}")
    if not path.is_file():
        raise ValueError(f"{label} must be a regular file beneath its corpus root")
    return path


def error_issues(outcome: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        issue
        for issue in outcome.get("issue", [])
        if issue.get("severity") in {"error", "fatal"}
    ]


def issue_text(issues: list[dict[str, Any]]) -> str:
    return json.dumps(issues, sort_keys=True)


def issue_message_id(issue: dict[str, Any]) -> str | None:
    values = [
        extension.get("valueCode") or extension.get("valueString")
        for extension in issue.get("extension", [])
        if isinstance(extension, dict) and extension.get("url") == MESSAGE_ID_URL
    ]
    values = [value for value in values if isinstance(value, str)]
    if len(values) > 1:
        raise ValueError("Validator issue has duplicate message-id extensions")
    return values[0] if values else None


def issue_matches(issue: dict[str, Any], matcher: dict[str, str]) -> bool:
    if "messageId" in matcher and issue_message_id(issue) != matcher["messageId"]:
        return False
    if "code" in matcher and issue.get("code") != matcher["code"]:
        return False
    expressions = issue.get("expression", [])
    if "expression" in matcher and matcher["expression"] not in expressions:
        return False
    details = issue.get("details")
    text = details.get("text", "") if isinstance(details, dict) else ""
    return "detailsContains" not in matcher or matcher["detailsContains"] in text


def load_expectations(case_ids: set[str]) -> dict[str, list[dict[str, str]]]:
    value = load_json(EXPECTATIONS)
    if value.get("schemaVersion") != 1 or set(value) != {"schemaVersion", "cases"}:
        raise ValueError("Questionnaire Validator expectations must use schemaVersion 1")
    cases = value.get("cases")
    if not isinstance(cases, dict) or set(cases) != case_ids:
        raise ValueError(
            "Questionnaire Validator expectations must exactly cover official cases"
        )
    allowed_fields = {"messageId", "expression", "detailsContains", "code"}
    for identifier, matchers in cases.items():
        if not isinstance(matchers, list) or not matchers:
            raise ValueError(f"Validator case {identifier} needs exact error matchers")
        for matcher in matchers:
            if (
                not isinstance(matcher, dict)
                or not matcher
                or not set(matcher) <= allowed_fields
                or not all(isinstance(item, str) and item for item in matcher.values())
            ):
                raise ValueError(f"Validator case {identifier} has an invalid matcher")
    return cases


def exact_error_failure(
    errors: list[dict[str, Any]], matchers: list[dict[str, str]]
) -> str | None:
    error_matches = [
        [index for index, matcher in enumerate(matchers) if issue_matches(error, matcher)]
        for error in errors
    ]
    matcher_matches = [
        [index for index, error in enumerate(errors) if issue_matches(error, matcher)]
        for matcher in matchers
    ]
    if (
        len(errors) != len(matchers)
        or any(len(matches) != 1 for matches in error_matches)
        or any(len(matches) != 1 for matches in matcher_matches)
    ):
        return (
            "errors did not match the declared exact one-to-one set "
            f"{json.dumps(matchers, sort_keys=True)}; found {issue_text(errors)}"
        )
    return None


def validate_one(
    validator: Path,
    package: Path,
    resource_path: Path,
    outcome_path: Path,
    allow_example_urls: bool,
) -> tuple[list[dict[str, Any]], str]:
    resource = load_json(resource_path)
    command = [
        "java",
        "-jar",
        str(validator),
        str(resource_path),
        "-version",
        "4.0.1",
        "-ig",
        str(package),
        "-tx",
        "n/a",
        "-no-http-access",
        "-level",
        "errors",
        "-output-style",
        "json",
        "-output",
        str(outcome_path),
    ]
    if allow_example_urls:
        command.extend(["-allow-example-urls", "true"])
    profile = PROFILES.get(resource.get("resourceType"))
    if profile:
        command.extend(["-profile", profile])
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    logs = f"{result.stdout}\n{result.stderr}".strip()
    if not outcome_path.is_file():
        raise RuntimeError(
            f"FHIR Validator did not write {outcome_path} for {resource_path}\n{logs}"
        )
    outcome = load_json(outcome_path)
    return error_issues(outcome), logs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validator",
        type=Path,
        default=Path(
            os.environ.get(
                "FHIR_VALIDATOR", ROOT / ".build/fhir-tools/validator_cli.jar"
            )
        ),
    )
    parser.add_argument(
        "--package",
        type=Path,
        default=Path(
            os.environ.get(
                "GROVE_IG_QUESTIONNAIRE", ROOT / "questionnaire/output/package.tgz"
            )
        ),
    )
    parser.add_argument(
        "--resource",
        action="append",
        default=[],
        type=Path,
        help="validate a resource instead of the repository corpus; repeat as needed",
    )
    parser.add_argument(
        "--allow-example-urls",
        action="store_true",
        help="allow example.org identifiers when validating explicit --resource files",
    )
    arguments = parser.parse_args(argv)
    validator = arguments.validator.resolve()
    package = arguments.package.resolve()
    if not validator.is_file():
        parser.error(f"FHIR Validator JAR not found: {validator}")
    if not package.is_file():
        parser.error(f"Questionnaire package not found: {package}")

    failures: list[str] = []
    passed = 0
    expectations: dict[str, list[dict[str, str]]] = {}
    with tempfile.TemporaryDirectory(prefix="grove-questionnaire-validator-") as temporary:
        temporary_path = Path(temporary)
        if arguments.resource:
            resources = [(path.resolve(), True, None) for path in arguments.resource]
            allow_example_urls = arguments.allow_example_urls
        else:
            manifest = load_json(CORPUS / "cases.json")
            resources: list[tuple[Path, bool, str | None]] = [
                (
                    resolve_corpus_file(
                        CORPUS, relative, "Questionnaire valid corpus resource"
                    ),
                    True,
                    None,
                )
                for relative in manifest["valid"]
            ]
            official_cases = {
                case["id"]
                for case in manifest["invalid"]
                if case.get("fhirValidator") is not False
            }
            expectations = load_expectations(official_cases)
            invalid_directory = temporary_path / "invalid"
            invalid_directory.mkdir()
            allow_example_urls = True
            for case in manifest["invalid"]:
                if case.get("fhirValidator") is False:
                    continue
                base = load_json(
                    resolve_corpus_file(
                        CORPUS,
                        case.get("base"),
                        f"Questionnaire case {case.get('id')} base",
                    )
                )
                resource = apply_mutation(base, case["mutation"])
                path = invalid_directory / f"{case['id']}.json"
                write_json(path, resource)
                resources.append((path, False, case["id"]))

        for index, (resource_path, expected_valid, case_id) in enumerate(resources):
            outcome_path = temporary_path / f"outcome-{index}.json"
            try:
                errors, logs = validate_one(
                    validator,
                    package,
                    resource_path,
                    outcome_path,
                    allow_example_urls,
                )
            except (OSError, RuntimeError, ValueError) as error:
                failures.append(str(error))
                continue
            if expected_valid and errors:
                failures.append(
                    f"{resource_path}: expected valid, found {issue_text(errors)}"
                )
                continue
            if not expected_valid and not errors:
                failures.append(
                    f"{resource_path}: invalid fixture was accepted\n{logs}"
                )
                continue
            if case_id is not None:
                mismatch = exact_error_failure(errors, expectations[case_id])
            else:
                mismatch = None
            if mismatch:
                failures.append(
                    f"{resource_path}: {mismatch}"
                )
                continue
            passed += 1
            print(
                f"PASS {resource_path.name}: "
                f"{'valid' if expected_valid else 'rejected as expected'}"
            )

    if failures:
        print("Questionnaire FHIR validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Validated {passed} Questionnaire corpus resources with {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
