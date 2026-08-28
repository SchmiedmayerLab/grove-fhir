"""Strict filesystem and JSON primitives for untrusted producer inputs."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import stat
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any

from .diagnostics import ProducerValidationError


def unlinked_path(path: Path, label: str) -> Path:
    """Return one lexical path after rejecting every supplied symlink component."""
    if not isinstance(path, Path) or not path.parts:
        raise ProducerValidationError(f"{label} path is invalid")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ProducerValidationError(f"{label} path must not contain traversal components")
    if path.is_absolute():
        current = Path(path.anchor)
        components = path.parts[1:]
    else:
        current = Path.cwd()
        components = path.parts
    for component in components:
        current = current / component
        if current.is_symlink():
            raise ProducerValidationError(
                f"{label} path contains a symlink component: {path}"
            )
    return current

def resolve_unlinked_regular_file(path: Path, label: str) -> Path:
    candidate = unlinked_path(path, label)
    try:
        mode = candidate.stat().st_mode
    except OSError as error:
        raise ProducerValidationError(f"{label} file is absent: {path}") from error
    if not stat.S_ISREG(mode):
        raise ProducerValidationError(f"{label} path is not a regular file: {path}")
    try:
        return candidate.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(f"{label} file cannot be resolved: {path}") from error


def resolve_unlinked_directory(path: Path, label: str) -> Path:
    candidate = unlinked_path(path, label)
    try:
        mode = candidate.stat().st_mode
    except OSError as error:
        raise ProducerValidationError(f"{label} directory is absent: {path}") from error
    if not stat.S_ISDIR(mode):
        raise ProducerValidationError(f"{label} path is not a directory: {path}")
    try:
        return candidate.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(
            f"{label} directory cannot be resolved: {path}"
        ) from error


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProducerValidationError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_float=Decimal,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read JSON {path}: {error}") from error


def require_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = set(value) - expected
    if unknown:
        raise ProducerValidationError(
            f"{label} has unsupported fields: {', '.join(sorted(unknown))}"
        )


def safe_resource_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.endswith(".json"):
        raise ProducerValidationError("resource path must be a relative JSON file")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or not candidate.parts or any(
        part in {"", ".", ".."} for part in candidate.parts
    ):
        raise ProducerValidationError(f"unsafe resource path: {value!r}")
    if root.is_symlink():
        raise ProducerValidationError("manifest resource directory must not be a symlink")
    path = root
    for part in candidate.parts:
        path = path / part
        if path.is_symlink():
            raise ProducerValidationError(
                f"resource path contains a symlink component: {value}"
            )
    try:
        resolved_root = root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(f"resource is absent: {value}") from error
    if not path.is_file() or (
        resolved_path.parent != resolved_root and resolved_root not in resolved_path.parents
    ):
        raise ProducerValidationError(
            f"resource is absent, linked, or outside the manifest directory: {value}"
        )
    return path


def json_pointer(value: Any, pointer: Any, label: str) -> Any:
    """Resolve one strict RFC 6901 pointer without ambiguous array indexes."""
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise ProducerValidationError(f"{label} must be an RFC 6901 JSON Pointer")
    current = value
    if not pointer:
        return current
    for raw_token in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw_token):
            raise ProducerValidationError(
                f"{label} contains an invalid JSON Pointer escape"
            )
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise ProducerValidationError(f"{label} does not resolve")
            current = current[token]
        elif isinstance(current, list):
            if re.fullmatch(r"0|[1-9][0-9]*", token) is None:
                raise ProducerValidationError(f"{label} has an invalid array index")
            index = int(token)
            if index >= len(current):
                raise ProducerValidationError(f"{label} does not resolve")
            current = current[index]
        else:
            raise ProducerValidationError(f"{label} traverses a scalar value")
    return current
