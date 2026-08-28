"""Offline official FHIR Validator process and OperationOutcome handling."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .context import (
    FHIR_TOOL_HOME, VALIDATOR_ATTEMPTS, VALIDATOR_FILE_EXTENSION,
    VALIDATOR_LOG_LIMIT, VALIDATOR_TIMEOUT_SECONDS,
)
from .diagnostics import ProducerValidationError
from .io import (
    read_json, resolve_unlinked_directory, resolve_unlinked_regular_file,
)


def validator_outcomes(
    value: Any, resources: list[Path]
) -> list[tuple[Path, dict[str, Any]]]:
    """Require Validator's exact one-input or ordered multi-input output shape."""
    if not isinstance(value, dict):
        raise ProducerValidationError("FHIR Validator output must be a JSON resource")
    if len(resources) == 1:
        if value.get("resourceType") != "OperationOutcome":
            raise ProducerValidationError(
                "one-input FHIR Validator output must be one OperationOutcome"
            )
        outcomes = [value]
    else:
        if value.get("resourceType") != "Bundle" or value.get("type") != "collection":
            raise ProducerValidationError(
                "multi-input FHIR Validator output must be a collection Bundle"
            )
        entries = value.get("entry")
        if not isinstance(entries, list) or len(entries) != len(resources):
            actual = len(entries) if isinstance(entries, list) else "invalid"
            raise ProducerValidationError(
                "FHIR Validator output count does not match inputs: "
                f"{actual} != {len(resources)}"
            )
        outcomes = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or set(entry) != {"resource"}:
                raise ProducerValidationError(
                    f"FHIR Validator output Bundle entry[{index}] must contain only resource"
                )
            outcome = entry["resource"]
            if not isinstance(outcome, dict) or outcome.get("resourceType") != "OperationOutcome":
                raise ProducerValidationError(
                    f"FHIR Validator output Bundle entry[{index}] is not one OperationOutcome"
                )
            outcomes.append(outcome)

    result: list[tuple[Path, dict[str, Any]]] = []
    for index, (resource, outcome) in enumerate(zip(resources, outcomes, strict=True)):
        extensions = outcome.get("extension", [])
        matches = [
            extension.get("valueString")
            for extension in extensions
            if isinstance(extension, dict)
            and extension.get("url") == VALIDATOR_FILE_EXTENSION
        ] if isinstance(extensions, list) else []
        if matches != [str(resource)]:
            raise ProducerValidationError(
                f"FHIR Validator output[{index}] file attribution does not match input "
                f"{resource}"
            )
        result.append((resource, outcome))
    return result

def reject_validator_errors(outcome: dict[str, Any], label: str) -> None:
    errors: list[str] = []
    issues = outcome.get("issue")
    if not isinstance(issues, list) or not issues:
        raise ProducerValidationError(
            f"FHIR Validator OperationOutcome has no populated issue array for {label}"
        )
    for issue_index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ProducerValidationError(
                f"FHIR Validator OperationOutcome.issue[{issue_index}] is invalid for {label}"
            )
        severity = issue.get("severity")
        if severity not in {"fatal", "error", "warning", "information"}:
            raise ProducerValidationError(
                f"FHIR Validator issue has invalid severity for {label}: {severity!r}"
            )
        if severity in {"fatal", "error"}:
            diagnostics = issue.get("diagnostics")
            if not isinstance(diagnostics, str) or not diagnostics:
                details = issue.get("details")
                diagnostics = details.get("text") if isinstance(details, dict) else None
            errors.append(
                diagnostics
                if isinstance(diagnostics, str) and diagnostics
                else "unspecified validation error"
            )
    if errors:
        raise ProducerValidationError(
            f"FHIR Validator rejected {label}: " + " | ".join(errors)
        )

def truncated_validator_log(value: str | bytes | None) -> str:
    """Return a bounded, printable process log for a terminal infrastructure failure."""
    if not value:
        return "<empty>"
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    normalized = value.replace("\x00", "\\0").strip()
    if len(normalized) <= VALIDATOR_LOG_LIMIT:
        return normalized
    return "…" + normalized[-VALIDATOR_LOG_LIMIT:]

def run_validator(
    validator: Path,
    packages: list[Path],
    resources: list[Path],
    *,
    allow_example_urls: bool = False,
    fhir_tool_home: Path = FHIR_TOOL_HOME,
) -> None:
    validator = resolve_unlinked_regular_file(validator, "Validator JAR")
    packages = [
        resolve_unlinked_regular_file(package, "FHIR package")
        for package in packages
    ]
    fhir_tool_home = resolve_unlinked_directory(fhir_tool_home, "private FHIR home")
    resolve_unlinked_directory(
        fhir_tool_home / ".fhir" / "packages", "private FHIR package cache"
    )
    ordered_resources = sorted(resources, key=lambda path: path.as_posix())
    with tempfile.TemporaryDirectory(prefix="grove-fhir-producer-") as directory:
        output = Path(directory) / "operation-outcomes.json"
        command = [
            "java", f"-Duser.home={fhir_tool_home}", "-jar", str(validator),
            "-version", "4.0.1",
            "-tx", "n/a",
            "-no-http-access",
            "-level", "errors",
        ]
        for package in packages:
            command.extend(("-ig", str(package)))
        if allow_example_urls:
            command.extend(("-allow-example-urls", "true"))
        command.extend(("-output", str(output)))
        command.extend(str(resource) for resource in ordered_resources)

        last_failure = ""
        for attempt in range(1, VALIDATOR_ATTEMPTS + 1):
            if output.exists() or output.is_symlink():
                output.unlink()
            try:
                result = subprocess.run(
                    command,
                    check=False,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=VALIDATOR_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired as error:
                process_log = truncated_validator_log(error.stdout)
                last_failure = (
                    "FHIR Validator timed out after "
                    f"{VALIDATOR_TIMEOUT_SECONDS} seconds; log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure) from error
            process_log = truncated_validator_log(result.stdout)
            if not output.is_file() or output.is_symlink():
                last_failure = (
                    "FHIR Validator produced no trustworthy OperationOutcome output "
                    f"(exit {result.returncode}); log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure)
            try:
                parsed = read_json(output)
                outcomes = validator_outcomes(parsed, ordered_resources)
            except ProducerValidationError as error:
                last_failure = (
                    f"untrustworthy FHIR Validator output: {error} "
                    f"(exit {result.returncode}); log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure) from error

            # A real FHIR fatal/error is final and is never retried or ignored.
            for resource, outcome in outcomes:
                reject_validator_errors(outcome, resource.name)
            if result.returncode == 0:
                return
            last_failure = (
                "FHIR Validator process failed after producing only error-free, correctly "
                f"attributed OperationOutcomes (exit {result.returncode}); log: {process_log}"
            )
            if attempt == VALIDATOR_ATTEMPTS:
                raise ProducerValidationError(last_failure)
