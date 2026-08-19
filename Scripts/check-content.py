#!/usr/bin/env python3
"""Run fast, deterministic repository checks before the expensive guide builds."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import py_compile
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
GUIDES = (ROOT / "platforms", ROOT / "ig")
REQUIRED_CONFIGURATION_KEYS = {"id", "canonical", "version", "fhirVersion", "license"}


def scalar_configuration(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s+(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"')
    return values


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> int:
    failures: list[str] = []
    configurations: dict[Path, dict[str, str]] = {}
    for guide in GUIDES:
        configuration_path = guide / "sushi-config.yaml"
        configuration = scalar_configuration(configuration_path)
        configurations[guide] = configuration
        missing = REQUIRED_CONFIGURATION_KEYS - configuration.keys()
        if missing:
            failures.append(f"{configuration_path.relative_to(ROOT)} is missing: {', '.join(sorted(missing))}")
        if configuration.get("license") != "MIT":
            failures.append(f"{configuration_path.relative_to(ROOT)} must declare the MIT license")

    platform_configuration = configurations[ROOT / "platforms"]
    core_configuration_text = (ROOT / "ig" / "sushi-config.yaml").read_text(encoding="utf-8")
    expected_dependency = (
        "org.grovealliance.fhir.platforms:\n"
        f"    version: {platform_configuration.get('version', '<missing>')}"
    )
    if expected_dependency not in core_configuration_text:
        failures.append("ig/sushi-config.yaml does not pin the current platform-guide version")

    for path in tracked_files():
        relative = path.relative_to(ROOT)
        if any(part in {"output", "temp", "input-cache", "node_modules", ".build"} for part in relative.parts):
            failures.append(f"generated file is tracked: {relative}")
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                failures.append(f"invalid JSON in {relative}: {error}")
        if path.suffix == ".py":
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as error:
                failures.append(f"invalid Python in {relative}: {error.msg}")

    if failures:
        print("Repository content checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Checked {len(GUIDES)} guides and {len(tracked_files())} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
