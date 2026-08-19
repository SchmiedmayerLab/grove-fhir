"""Load the Questionnaire fixture corpus and apply one-operation mutations."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"JSON pointer must start with '/': {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def _parent(document: Any, pointer: str) -> tuple[Any, str]:
    tokens = _tokens(pointer)
    if not tokens:
        raise ValueError("A fixture mutation cannot replace the whole resource")
    node = document
    for token in tokens[:-1]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node, tokens[-1]


def _read(document: Any, pointer: str) -> Any:
    node = document
    for token in _tokens(pointer):
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def _remove(document: Any, pointer: str) -> Any:
    parent, token = _parent(document, pointer)
    return parent.pop(int(token)) if isinstance(parent, list) else parent.pop(token)


def _add(document: Any, pointer: str, value: Any) -> None:
    parent, token = _parent(document, pointer)
    if isinstance(parent, list):
        if token == "-":
            parent.append(value)
        else:
            parent.insert(int(token), value)
    else:
        parent[token] = value


def apply_mutation(resource: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied resource after exactly one RFC 6902-style operation."""

    document = copy.deepcopy(resource)
    operation = mutation.get("op")
    path = mutation.get("path")
    if not isinstance(path, str) or operation not in {"add", "copy", "move", "remove", "replace"}:
        raise ValueError(f"Unsupported fixture mutation: {mutation!r}")
    if operation == "remove":
        _remove(document, path)
    elif operation == "replace":
        _remove(document, path)
        _add(document, path, copy.deepcopy(mutation.get("value")))
    elif operation == "add":
        _add(document, path, copy.deepcopy(mutation.get("value")))
    else:
        source = mutation.get("from")
        if not isinstance(source, str):
            raise ValueError(f"{operation} mutation requires 'from'")
        value = copy.deepcopy(_read(document, source))
        if operation == "move":
            _remove(document, source)
        _add(document, path, value)
    return document
