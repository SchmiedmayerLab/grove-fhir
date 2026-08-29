#!/usr/bin/env python3
"""Produce a deterministic, identity-aware diff of two FHIR semantic snapshots."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import difflib
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from fhir_package_semantic_snapshot import (
        SnapshotError,
        canonical_json_bytes,
        load_snapshot,
    )
except ModuleNotFoundError:  # Imported as Scripts.fhir_package_semantic_diff in tests.
    from Scripts.fhir_package_semantic_snapshot import (  # type: ignore[no-redef]
        SnapshotError,
        canonical_json_bytes,
        load_snapshot,
    )


def _token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _item_identity(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    if set(item) >= {"source", "kind", "target", "path"}:
        return "edge=" + "|".join(
            str(item[field]) for field in ("source", "kind", "target", "path")
        )
    if set(item) >= {"type", "path"} and isinstance(item.get("path"), str):
        return f"discriminator={item['type']}|{item['path']}"
    reference = item.get("reference")
    if isinstance(reference, dict) and isinstance(reference.get("reference"), str):
        return f"reference={reference['reference']}"
    system = item.get("system")
    code = item.get("code")
    if isinstance(system, str) and isinstance(code, str) and system and code:
        return f"code={system}|{code}"
    if isinstance(system, str) and system:
        return f"system={system}"
    for field in ("id", "key", "code", "linkId", "url", "property"):
        value = item.get(field)
        if isinstance(value, str) and value:
            return f"{field}={value}"
    return None


def _keyed_items(values: list[Any]) -> tuple[list[str], dict[str, Any]] | None:
    identities = [_item_identity(item) for item in values]
    if any(identity is None for identity in identities):
        return None
    keys = [identity for identity in identities if identity is not None]
    if len(keys) != len(set(keys)):
        return None
    return keys, dict(zip(keys, values, strict=True))


def _changes(before: Any, after: Any, path: str) -> list[dict[str, Any]]:
    if type(before) is not type(after):
        return [{"kind": "changed", "path": path, "before": before, "after": after}]
    if isinstance(before, dict):
        changes: list[dict[str, Any]] = []
        before_keys = set(before)
        after_keys = set(after)
        for key in sorted(before_keys - after_keys):
            changes.append(
                {"kind": "removed", "path": f"{path}/{_token(key)}", "before": before[key]}
            )
        for key in sorted(after_keys - before_keys):
            changes.append(
                {"kind": "added", "path": f"{path}/{_token(key)}", "after": after[key]}
            )
        shared_keys = before_keys & after_keys
        if "resource" in shared_keys and "sha256" in shared_keys:
            # Hashes and example profile lists are derived indexes. Report the authored
            # resource field once; added/removed entries still carry their indexes.
            shared_keys.remove("sha256")
            shared_keys.discard("profiles")
        for key in sorted(shared_keys):
            changes.extend(_changes(before[key], after[key], f"{path}/{_token(key)}"))
        return changes
    if isinstance(before, list):
        before_keyed = _keyed_items(before)
        after_keyed = _keyed_items(after)
        if before_keyed is not None and after_keyed is not None:
            before_keys, before_items = before_keyed
            after_keys, after_items = after_keyed
            before_set = set(before_keys)
            after_set = set(after_keys)
            changes: list[dict[str, Any]] = []
            for key in sorted(before_set - after_set):
                changes.append(
                    {
                        "kind": "removed",
                        "path": f"{path}/@{_token(key)}",
                        "before": before_items[key],
                    }
                )
            for key in sorted(after_set - before_set):
                changes.append(
                    {
                        "kind": "added",
                        "path": f"{path}/@{_token(key)}",
                        "after": after_items[key],
                    }
                )
            shared_before = [key for key in before_keys if key in after_set]
            shared_after = [key for key in after_keys if key in before_set]
            if shared_before != shared_after:
                changes.append(
                    {
                        "kind": "changed",
                        "path": f"{path}/@order",
                        "before": shared_before,
                        "after": shared_after,
                    }
                )
            for key in sorted(before_set & after_set):
                changes.extend(
                    _changes(
                        before_items[key],
                        after_items[key],
                        f"{path}/@{_token(key)}",
                    )
                )
            return changes
        before_tokens = [canonical_json_bytes(item) for item in before]
        after_tokens = [canonical_json_bytes(item) for item in after]
        matcher = difflib.SequenceMatcher(
            None, before_tokens, after_tokens, autojunk=False
        )
        changes = []
        for operation, before_start, before_end, after_start, after_end in matcher.get_opcodes():
            if operation == "equal":
                continue
            before_count = before_end - before_start
            after_count = after_end - after_start
            if operation == "replace" and before_count == after_count:
                for offset in range(before_count):
                    changes.extend(
                        _changes(
                            before[before_start + offset],
                            after[after_start + offset],
                            f"{path}/{after_start + offset}",
                        )
                    )
                continue
            if operation in {"delete", "replace"}:
                for index in range(before_start, before_end):
                    changes.append(
                        {
                            "kind": "removed",
                            "path": f"{path}/{index}",
                            "before": before[index],
                        }
                    )
            if operation in {"insert", "replace"}:
                for index in range(after_start, after_end):
                    changes.append(
                        {
                            "kind": "added",
                            "path": f"{path}/{index}",
                            "after": after[index],
                        }
                    )
        return changes
    if canonical_json_bytes(before) != canonical_json_bytes(after):
        return [{"kind": "changed", "path": path, "before": before, "after": after}]
    return []


def semantic_diff(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    """Return stable semantic paths without timestamps or environment data."""
    changes = _changes(before, after, "")
    counts = {"added": 0, "removed": 0, "changed": 0}
    for change in changes:
        counts[change["kind"]] += 1
    return {
        "schemaVersion": 0,
        "before": {
            "name": before.get("package", {}).get("name"),
            "version": before.get("package", {}).get("version"),
        },
        "after": {
            "name": after.get("package", {}).get("name"),
            "version": after.get("package", {}).get("version"),
        },
        "summary": {**counts, "total": len(changes)},
        "changes": changes,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--output", type=Path, help="diff path; defaults to stdout")
    parser.add_argument(
        "--fail-on-change",
        action="store_true",
        help="return status 1 when the snapshots differ",
    )
    arguments = parser.parse_args(argv)
    try:
        before = load_snapshot(arguments.before)
        after = load_snapshot(arguments.after)
        report = semantic_diff(before, after)
        data = canonical_json_bytes(report)
        if arguments.output is None:
            import sys

            sys.stdout.buffer.write(data)
        else:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_bytes(data)
        return int(arguments.fail_on_change and report["summary"]["total"] > 0)
    except SnapshotError as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
