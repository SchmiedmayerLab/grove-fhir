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
from typing import Any, Callable, Iterator, Sequence

from producer_validation.diagnostics import ProducerValidationError
from producer_validation.external_validator import validator_outcomes
from questionnaire_fixture_corpus import apply_mutation, load_json, write_json


ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "questionnaire/fixtures/validator"
# The guide build populates this home. Validating against it rather than the ambient
# one keeps the run reproducible on a machine whose own FHIR cache is empty.
FHIR_HOME = ROOT / ".build/fhir-home"
EXPECTATIONS = CORPUS / "validator-expectations.json"
MESSAGE_ID_URL = "http://hl7.org/fhir/StructureDefinition/operationoutcome-message-id"
PROFILES = {
    "Questionnaire": (
        "https://grovealliance.org/fhir/questionnaire/"
        "StructureDefinition/grove-questionnaire"
    ),
    "QuestionnaireResponse": (
        "https://grovealliance.org/fhir/questionnaire/"
        "StructureDefinition/grove-questionnaire-response"
    ),
}
VALIDATOR_ATTEMPTS = 2
VALIDATOR_LOG_LIMIT = 4_000
VALIDATOR_TIMEOUT_SECONDS = 180
# A batch of 29 takes as long as one resource: the package load is the cost, not the validation.
VALIDATOR_TIMEOUT_SECONDS_PER_RESOURCE = 5


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


def operation_outcome_issues(
    outcome: Any, resource_path: Path
) -> list[dict[str, Any]]:
    """Require the official Validator's populated R4 OperationOutcome shape."""

    if not isinstance(outcome, dict) or outcome.get("resourceType") != "OperationOutcome":
        raise ValueError(
            f"FHIR Validator output for {resource_path} is not an OperationOutcome"
        )
    issues = outcome.get("issue")
    if not isinstance(issues, list) or not issues:
        raise ValueError(
            f"FHIR Validator OperationOutcome for {resource_path} has no populated issue array"
        )
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ValueError(
                f"FHIR Validator OperationOutcome.issue[{index}] for {resource_path} "
                "is not an object"
            )
        severity = issue.get("severity")
        if severity not in {"fatal", "error", "warning", "information"}:
            raise ValueError(
                f"FHIR Validator OperationOutcome.issue[{index}] for {resource_path} "
                f"has invalid severity {severity!r}"
            )
        code = issue.get("code")
        if not isinstance(code, str) or not code:
            raise ValueError(
                f"FHIR Validator OperationOutcome.issue[{index}] for {resource_path} "
                "has no code"
            )
        for field in ("expression", "location"):
            values = issue.get(field)
            if values is not None and (
                not isinstance(values, list)
                or not all(isinstance(value, str) and value for value in values)
            ):
                raise ValueError(
                    f"FHIR Validator OperationOutcome.issue[{index}].{field} for "
                    f"{resource_path} is invalid"
                )
        extensions = issue.get("extension")
        if extensions is not None and (
            not isinstance(extensions, list)
            or not all(isinstance(extension, dict) for extension in extensions)
        ):
            raise ValueError(
                f"FHIR Validator OperationOutcome.issue[{index}].extension for "
                f"{resource_path} is invalid"
            )
    return issues


def error_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        issue
        for issue in issues
        if issue.get("severity") in {"error", "fatal"}
    ]


def truncated_validator_log(
    stdout: str | bytes | None, stderr: str | bytes | None
) -> str:
    def text(value: str | bytes | None) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value or ""

    value = f"{text(stdout)}\n{text(stderr)}".strip()
    if not value:
        return "<empty>"
    value = value.replace("\x00", "\\0")
    if len(value) <= VALIDATOR_LOG_LIMIT:
        return value
    return "…" + value[-VALIDATOR_LOG_LIMIT:]


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
    if value.get("schemaVersion") != 0 or set(value) != {"schemaVersion", "cases"}:
        raise ValueError("Questionnaire Validator expectations must use schemaVersion 0")
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


def validator_command(
    validator: Path,
    package: Path,
    resource_paths: Sequence[Path],
    outcome_path: Path,
    allow_example_urls: bool,
    fhir_home: Path,
    profile: str | None,
) -> list[str]:
    command = [
        "java",
        f"-Duser.home={fhir_home}",
        "-jar",
        str(validator),
        *(str(path) for path in resource_paths),
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
    if profile:
        command.extend(["-profile", profile])
    return command


def run_validator(
    command: list[str],
    outcome_path: Path,
    label: str,
    timeout: int,
    read_errors: Callable[[Any], list[tuple[Path, list[dict[str, Any]]]]],
) -> tuple[list[tuple[Path, list[dict[str, Any]]]], str]:
    """Run one Validator process and return each input's errors, or raise on infrastructure failure."""
    last_failure = ""
    for attempt in range(1, VALIDATOR_ATTEMPTS + 1):
        if outcome_path.exists() or outcome_path.is_symlink():
            outcome_path.unlink()
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as error:
            logs = truncated_validator_log(error.stdout, error.stderr)
            last_failure = (
                f"FHIR Validator timed out after {timeout} seconds "
                f"for {label}; log: {logs}"
            )
            if attempt < VALIDATOR_ATTEMPTS:
                continue
            raise RuntimeError(last_failure) from error
        logs = truncated_validator_log(result.stdout, result.stderr)
        if not outcome_path.is_file() or outcome_path.is_symlink():
            last_failure = (
                f"FHIR Validator produced no trustworthy OperationOutcome for "
                f"{label} (exit {result.returncode}); log: {logs}"
            )
            if attempt < VALIDATOR_ATTEMPTS:
                continue
            raise RuntimeError(last_failure)
        try:
            results = read_errors(load_json(outcome_path))
        except (ValueError, OSError) as error:
            last_failure = (
                f"untrustworthy FHIR Validator output for {label}: {error} "
                f"(exit {result.returncode}); log: {logs}"
            )
            if attempt < VALIDATOR_ATTEMPTS:
                continue
            raise RuntimeError(last_failure) from error

        errors = sum(len(errors) for _, errors in results)
        # The pinned Validator uses exit 1 for genuine validation errors. A populated,
        # well-formed error outcome from exit 0/1 is authoritative and the caller compares
        # it to the exact negative-corpus expectation. Every other exit is infrastructure
        # failure, even when a stale or partial outcome file happens to exist.
        if (errors and result.returncode in {0, 1}) or (
            not errors and result.returncode == 0
        ):
            return results, logs
        last_failure = (
            f"FHIR Validator process failed for {label} with an unexpected "
            f"exit code after producing a trustworthy outcome (exit "
            f"{result.returncode}, errors={errors}); log: {logs}"
        )
        if attempt == VALIDATOR_ATTEMPTS:
            raise RuntimeError(last_failure)
    raise RuntimeError(last_failure)


def validate_one(
    validator: Path,
    package: Path,
    resource_path: Path,
    outcome_path: Path,
    allow_example_urls: bool,
    fhir_home: Path,
) -> tuple[list[dict[str, Any]], str]:
    resource = load_json(resource_path)
    command = validator_command(
        validator,
        package,
        [resource_path],
        outcome_path,
        allow_example_urls,
        fhir_home,
        PROFILES.get(resource.get("resourceType")),
    )
    results, logs = run_validator(
        command,
        outcome_path,
        str(resource_path),
        VALIDATOR_TIMEOUT_SECONDS,
        lambda value: [
            (resource_path, error_issues(operation_outcome_issues(value, resource_path)))
        ],
    )
    return results[0][1], logs


def strings_in(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings_in(item)


def sibling_references(resources: dict[Path, Any]) -> set[Path]:
    """The inputs that name the canonical URL of another input in the same set.

    The Validator loads every input of a run into one context before it validates any of them, so
    within a batch such a name could resolve against the sibling, which a run of its own never sees.
    A resource's own top-level `url` is its identity, not a reference, and is not counted.
    """
    owners: dict[str, set[Path]] = {}
    for path, resource in resources.items():
        url = resource.get("url") if isinstance(resource, dict) else None
        if isinstance(url, str) and url:
            owners.setdefault(url, set()).add(path)
    referencing: set[Path] = set()
    for path, resource in resources.items():
        body = (
            {key: value for key, value in resource.items() if key != "url"}
            if isinstance(resource, dict)
            else resource
        )
        for text in strings_in(body):
            canonical = text.split("#", 1)[0].split("|", 1)[0]
            if owners.get(canonical, set()) - {path}:
                referencing.add(path)
                break
    return referencing


def validate_batch(
    validator: Path,
    package: Path,
    resource_paths: Sequence[Path],
    outcome_path: Path,
    allow_example_urls: bool,
    fhir_home: Path,
    profile: str | None,
) -> dict[Path, tuple[list[dict[str, Any]], str]]:
    """Validate several resources against one profile, sharing one Validator process.

    Each Validator process spends most of its time loading the FHIR packages, so one process per
    resource costs that load every time. A batch pays it once. The Validator then reports one
    OperationOutcome per input, which must be attributed to exactly that input, in order. An input
    that names a sibling's canonical URL is validated on its own, so that no input's verdict can
    depend on which other inputs share its process.
    """
    paths = sorted(dict.fromkeys(resource_paths), key=lambda path: path.as_posix())
    alone = sibling_references({path: load_json(path) for path in paths})
    shared = [path for path in paths if path not in alone]
    results: dict[Path, tuple[list[dict[str, Any]], str]] = {}
    for path in [path for path in paths if path in alone] + (shared if len(shared) == 1 else []):
        results[path] = validate_one(
            validator, package, path, outcome_path, allow_example_urls, fhir_home
        )
    if len(shared) < 2:
        return results

    def read_errors(value: Any) -> list[tuple[Path, list[dict[str, Any]]]]:
        try:
            outcomes = validator_outcomes(value, shared)
        except ProducerValidationError as error:
            raise ValueError(str(error)) from error
        return [
            (path, error_issues(operation_outcome_issues(outcome, path)))
            for path, outcome in outcomes
        ]

    batch, logs = run_validator(
        validator_command(
            validator, package, shared, outcome_path, allow_example_urls, fhir_home, profile
        ),
        outcome_path,
        f"{len(shared)} resources validated against {profile or 'their base types'}",
        VALIDATOR_TIMEOUT_SECONDS + VALIDATOR_TIMEOUT_SECONDS_PER_RESOURCE * len(shared),
        read_errors,
    )
    results.update((path, (errors, logs)) for path, errors in batch)
    return results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fhir-home",
        type=Path,
        default=FHIR_HOME,
        help="FHIR home holding the packages the Validator resolves against",
    )
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
        # Resolved, because the Validator attributes each outcome to the input path as written
        # and a batch is matched to its inputs by that path.
        temporary_path = Path(temporary).resolve()
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

        # One Validator process per profile rather than per resource: the process start, not the
        # validation, is what each run costs.
        batches: dict[str | None, list[Path]] = {}
        for resource_path, _, _ in resources:
            try:
                resource_type = load_json(resource_path).get("resourceType")
            except (OSError, ValueError) as error:
                failures.append(f"{resource_path}: {error}")
                continue
            batches.setdefault(PROFILES.get(resource_type), []).append(resource_path)
        outcomes: dict[Path, tuple[list[dict[str, Any]], str]] = {}
        for index, (profile, paths) in enumerate(batches.items()):
            try:
                outcomes.update(
                    validate_batch(
                        validator,
                        package,
                        paths,
                        temporary_path / f"outcome-{index}.json",
                        allow_example_urls,
                        arguments.fhir_home.resolve(),
                        profile,
                    )
                )
            except (OSError, RuntimeError, ValueError) as error:
                failures.append(str(error))
                continue

        for resource_path, expected_valid, case_id in resources:
            if resource_path not in outcomes:
                # Its batch failed, and that failure is already reported.
                continue
            errors, logs = outcomes[resource_path]
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
