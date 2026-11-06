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

try:
    from Scripts.canonical_json import (
        CanonicalJSONError, JSONNumber, canonical_bytes, loads_lossless,
    )
except ModuleNotFoundError:  # Direct `python Scripts/validate-producer.py` execution.
    from canonical_json import (  # type: ignore[no-redef]
        CanonicalJSONError, JSONNumber, canonical_bytes, loads_lossless,
    )


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
        raise ProducerValidationError(
            f"{label} directory is absent: {path}; run Scripts/download-fhir-tools.sh first"
        ) from error
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


def read_lossless_json(path: Path) -> Any:
    """Read one JSON text as a grove-canonical-json-v0 lossless tree.

    read_json parses decimals as Decimal, which keeps their value but not always their lexeme
    (1e2 and 100 compare equal), so every digest recompute reads the bytes again through this.
    """
    try:
        return loads_lossless(path.read_bytes())
    except OSError as error:
        raise ProducerValidationError(f"cannot read JSON {path}: {error}") from error


def decimal_lexeme(value: Decimal) -> str:
    """Return the lexeme a JSON reader most plausibly parsed into this Decimal."""
    if not value.is_finite():
        raise CanonicalJSONError("non-json-constant", f"{value} is not a JSON number")
    if value.as_tuple().exponent <= 0:
        return format(value, "f")
    return str(value)


def lossless_tree(value: Any) -> Any:
    """Convert a parsed JSON tree into the lossless tree of grove-canonical-json-v0.

    A tree read through read_lossless_json is returned unchanged. A tree parsed with int, Decimal
    or float numbers keeps only what its parser kept: 1e2 reads back as 1E+2 and -0 as 0. A key
    recomputed over such a tree can refuse a valid Bundle whose lexemes the parser normalized, so
    a validator that holds the bytes passes read_lossless_json's tree instead.
    """
    if isinstance(value, (JSONNumber, str)) or value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return JSONNumber(str(value))
    if isinstance(value, Decimal):
        return JSONNumber(decimal_lexeme(value))
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CanonicalJSONError("non-json-constant", f"{value} is not a JSON number")
        return JSONNumber(repr(value))
    if isinstance(value, dict):
        return {name: lossless_tree(child) for name, child in value.items()}
    if isinstance(value, list):
        return [lossless_tree(child) for child in value]
    raise CanonicalJSONError("not-lossless", f"{type(value).__name__} is not a JSON value")


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
