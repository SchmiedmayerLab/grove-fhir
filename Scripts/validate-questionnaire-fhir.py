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
from pathlib import Path
from typing import Any, Sequence

from questionnaire_fixture_corpus import apply_mutation, load_json, write_json


ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "questionnaire/fixtures/validator"
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


def error_issues(outcome: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        issue
        for issue in outcome.get("issue", [])
        if issue.get("severity") in {"error", "fatal"}
    ]


def issue_text(issues: list[dict[str, Any]]) -> str:
    return json.dumps(issues, sort_keys=True)


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
    with tempfile.TemporaryDirectory(prefix="grove-questionnaire-validator-") as temporary:
        temporary_path = Path(temporary)
        if arguments.resource:
            resources = [(path.resolve(), True, None) for path in arguments.resource]
            allow_example_urls = arguments.allow_example_urls
        else:
            manifest = load_json(CORPUS / "cases.json")
            resources: list[tuple[Path, bool, str | None]] = [
                (CORPUS / relative, True, None) for relative in manifest["valid"]
            ]
            invalid_directory = temporary_path / "invalid"
            invalid_directory.mkdir()
            allow_example_urls = True
            for case in manifest["invalid"]:
                if case.get("fhirValidator") is False:
                    continue
                expected_rule = case.get("expectedValidatorRule")
                if not isinstance(expected_rule, str) or not expected_rule:
                    parser.error(
                        f"official Validator case {case.get('id')!r} has no "
                        "expectedValidatorRule"
                    )
                base = load_json(CORPUS / case["base"])
                resource = apply_mutation(base, case["mutation"])
                path = invalid_directory / f"{case['id']}.json"
                write_json(path, resource)
                resources.append((path, False, expected_rule))

        for index, (resource_path, expected_valid, expected_rule) in enumerate(resources):
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
            if expected_rule and expected_rule not in issue_text(errors):
                failures.append(
                    f"{resource_path}: expected {expected_rule!r}, found {issue_text(errors)}"
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
