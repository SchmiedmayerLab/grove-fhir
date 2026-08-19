#!/usr/bin/env python3
"""Classify changed repository paths for path-gated conformance jobs."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    from fhir_fixture_corpus import strict_json_loads
except ModuleNotFoundError:  # Imported as Scripts.conformance_path_matrix in tests.
    from Scripts.fhir_fixture_corpus import strict_json_loads


COMMIT = re.compile(r"^[0-9a-f]{40}$")
ZERO_COMMIT = "0" * 40


class PathMatrixError(ValueError):
    """Raised when changed paths or matrix definitions are unsafe."""


def _safe_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PathMatrixError(f"{label} must be a nonempty repository-relative path")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
        raise PathMatrixError(f"{label} escapes the repository: {value!r}")
    return candidate.as_posix()


def _glob_expression(pattern: str) -> re.Pattern[str]:
    pattern = _safe_path(pattern, "path matrix pattern")
    expression = ""
    index = 0
    while index < len(pattern):
        character = pattern[index]
        if character == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                expression += ".*"
                index += 2
            else:
                expression += "[^/]*"
                index += 1
        elif character == "?":
            expression += "[^/]"
            index += 1
        else:
            expression += re.escape(character)
            index += 1
    return re.compile(f"^{expression}$")


def classify_paths(
    path_matrix: Mapping[str, Sequence[str]],
    changed_paths: Sequence[str],
    ignored_patterns: Sequence[str] = (),
) -> dict[str, bool]:
    """Return one deterministic boolean for every declared path-matrix group."""
    normalized = sorted({_safe_path(value, "changed path") for value in changed_paths})
    compiled: dict[str, list[re.Pattern[str]]] = {}
    result: dict[str, bool] = {}
    for group in sorted(path_matrix):
        patterns = path_matrix[group]
        if not isinstance(group, str) or not isinstance(patterns, list) or not patterns:
            raise PathMatrixError("path matrix groups require a name and nonempty pattern list")
        expressions = [_glob_expression(pattern) for pattern in patterns]
        compiled[group] = expressions
        result[group] = any(
            expression.fullmatch(changed)
            for changed in normalized
            for expression in expressions
        )
    ignored = [_glob_expression(pattern) for pattern in ignored_patterns]
    unknown = any(
        not any(expression.fullmatch(changed) for values in compiled.values() for expression in values)
        and not any(expression.fullmatch(changed) for expression in ignored)
        for changed in normalized
    )
    if result.get("evidence_common", False) or unknown:
        return {group: True for group in sorted(result)}
    return result


def load_path_matrix(manifest_path: Path) -> dict[str, list[str]]:
    try:
        manifest = strict_json_loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise PathMatrixError(f"unable to read evidence manifest: {error}") from error
    matrix = manifest.get("pathMatrix") if isinstance(manifest, dict) else None
    if not isinstance(matrix, dict):
        raise PathMatrixError("evidence manifest pathMatrix must be an object")
    for group, patterns in matrix.items():
        if not isinstance(group, str) or not isinstance(patterns, list):
            raise PathMatrixError("evidence pathMatrix has an invalid group")
        if any(not isinstance(pattern, str) for pattern in patterns):
            raise PathMatrixError(f"path matrix group {group} contains a non-string pattern")
    return matrix


def load_ignored_paths(manifest_path: Path) -> list[str]:
    try:
        manifest = strict_json_loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise PathMatrixError(f"unable to read evidence manifest: {error}") from error
    ignored = manifest.get("pathMatrixIgnored") if isinstance(manifest, dict) else None
    if (
        not isinstance(ignored, list)
        or not ignored
        or any(not isinstance(pattern, str) for pattern in ignored)
    ):
        raise PathMatrixError("evidence manifest pathMatrixIgnored must be nonempty strings")
    return ignored


def event_range(event_name: str, event: Mapping[str, Any]) -> tuple[str, str, bool]:
    """Return exact base/head revisions and whether the event must run every group."""
    if event_name == "pull_request":
        pull_request = event.get("pull_request")
        base = pull_request.get("base", {}).get("sha") if isinstance(pull_request, dict) else None
        head = pull_request.get("head", {}).get("sha") if isinstance(pull_request, dict) else None
    elif event_name == "push":
        base = event.get("before")
        head = event.get("after")
    elif event_name == "workflow_dispatch":
        return ZERO_COMMIT, ZERO_COMMIT, True
    else:
        return ZERO_COMMIT, ZERO_COMMIT, True
    if not isinstance(base, str) or not COMMIT.fullmatch(base):
        raise PathMatrixError(f"{event_name} event has no exact base SHA")
    if not isinstance(head, str) or not COMMIT.fullmatch(head):
        raise PathMatrixError(f"{event_name} event has no exact head SHA")
    return base, head, base == ZERO_COMMIT


def changed_paths_from_git(repository: Path, base: str, head: str) -> list[str]:
    if not COMMIT.fullmatch(base) or not COMMIT.fullmatch(head):
        raise PathMatrixError("base and head must be full lowercase commit SHAs")
    for revision, label in ((base, "base"), (head, "head")):
        try:
            subprocess.run(
                ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
                cwd=repository,
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise PathMatrixError(
                f"exact {label} commit is unavailable: {revision}"
            ) from error
    command = [
        "git",
        "diff",
        "--no-renames",
        "--name-only",
        "--diff-filter=ACDMRTUXB",
        "-z",
        base,
        head,
        "--",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=repository,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise PathMatrixError(f"unable to determine changed paths: {error}") from error
    try:
        values = result.stdout.decode("utf-8").split("\0")
    except UnicodeDecodeError as error:
        raise PathMatrixError("git returned a non-UTF-8 repository path") from error
    return [_safe_path(value, "git changed path") for value in values if value]


def write_github_output(
    output: Path,
    result: Mapping[str, bool],
    *,
    base: str | None = None,
    head: str | None = None,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8", newline="\n") as stream:
        for group in sorted(result):
            stream.write(f"{group}={'true' if result[group] else 'false'}\n")
        stream.write(f"any_active={'true' if any(result.values()) else 'false'}\n")
        if base is not None:
            stream.write(f"base={base}\n")
        if head is not None:
            stream.write(f"head={head}\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=Path("Conformance/evidence.json")
    )
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--event-name")
    parser.add_argument("--event-json", type=Path)
    parser.add_argument("--event-head")
    parser.add_argument("--github-output", type=Path)
    arguments = parser.parse_args(argv)
    try:
        matrix = load_path_matrix(arguments.manifest)
        ignored = load_ignored_paths(arguments.manifest)
        event_mode = bool(arguments.event_name or arguments.event_json)
        if event_mode:
            if not arguments.event_name or not arguments.event_json:
                raise PathMatrixError("--event-name and --event-json must be provided together")
            if arguments.all or arguments.base or arguments.head or arguments.changed_path:
                raise PathMatrixError("event mode cannot be combined with manual revisions")
            try:
                event = strict_json_loads(arguments.event_json.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, ValueError) as error:
                raise PathMatrixError(f"unable to read event JSON: {error}") from error
            if not isinstance(event, dict):
                raise PathMatrixError("event JSON must be an object")
            base, head, run_all = event_range(arguments.event_name, event)
            if run_all and head == ZERO_COMMIT:
                if not isinstance(arguments.event_head, str) or not COMMIT.fullmatch(
                    arguments.event_head
                ):
                    raise PathMatrixError("dispatch/unknown events require --event-head")
                base = arguments.event_head
                head = arguments.event_head
            if run_all:
                result = {group: True for group in sorted(matrix)}
            else:
                changed = changed_paths_from_git(
                    arguments.repository.resolve(), base, head
                )
                result = classify_paths(matrix, changed, ignored)
        elif arguments.all:
            if arguments.changed_path:
                raise PathMatrixError("--all cannot be combined with changed paths")
            if bool(arguments.base) != bool(arguments.head):
                raise PathMatrixError("--all base and head must be provided together")
            base = arguments.base
            head = arguments.head
            result = {group: True for group in sorted(matrix)}
        else:
            if bool(arguments.base) != bool(arguments.head):
                raise PathMatrixError("--base and --head must be provided together")
            changed = list(arguments.changed_path)
            if arguments.base and arguments.head:
                changed.extend(
                    changed_paths_from_git(
                        arguments.repository.resolve(), arguments.base, arguments.head
                    )
                )
            base = arguments.base
            head = arguments.head
            result = classify_paths(matrix, changed, ignored)
        if arguments.github_output:
            write_github_output(
                arguments.github_output, result, base=base, head=head
            )
        for group in sorted(result):
            print(f"{group}={'true' if result[group] else 'false'}")
        return 0
    except PathMatrixError as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
