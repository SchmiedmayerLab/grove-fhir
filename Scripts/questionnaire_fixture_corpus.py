"""Compatibility imports for the reusable one-mutation fixture corpus."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from fhir_fixture_corpus import (
        canonical_json_bytes,
        CorpusError,
        apply_patch_operation,
        strict_json_loads,
    )
except ModuleNotFoundError:  # Imported as Scripts.questionnaire_fixture_corpus in tests.
    from Scripts.fhir_fixture_corpus import (
        canonical_json_bytes,
        CorpusError,
        apply_patch_operation,
        strict_json_loads,
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load one strict JSON object for legacy Questionnaire callers."""
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise ValueError(f"unable to read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    """Write one canonical JSON object without losing decimal precision."""
    try:
        path.write_bytes(canonical_json_bytes(value))
    except (OSError, TypeError, ValueError) as error:
        raise ValueError(f"unable to write {path}: {error}") from error


def apply_mutation(resource: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    """Apply one RFC 6902 mutation through the reusable corpus implementation."""
    try:
        value = apply_patch_operation(resource, mutation)
    except CorpusError as error:
        raise ValueError(str(error)) from error
    if not isinstance(value, dict):
        raise ValueError("Questionnaire fixture mutation must produce a JSON object")
    return value
