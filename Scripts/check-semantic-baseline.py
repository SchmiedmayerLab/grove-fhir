#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Diff the built mobile package against the committed semantic baseline.

Every semantic delta to the shared Mobile profiles must land as an explicit
reviewed change to publication/mobile-semantic-baseline.json, never as a
silent side effect of generator or tooling changes.

Usage:
  Scripts/check-semantic-baseline.py            # verify the built package
  Scripts/check-semantic-baseline.py --update   # rewrite the baseline
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "publication/mobile-semantic-baseline.json"
PACKAGE = ROOT / "mobile/output/package.tgz"
SNAPSHOT = ROOT / "Scripts/fhir_package_semantic_snapshot.py"
DIFF = ROOT / "Scripts/fhir_package_semantic_diff.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true")
    arguments = parser.parse_args()

    if not PACKAGE.is_file():
        print(f"{PACKAGE} is missing; build the mobile guide first")
        return 1

    if arguments.update:
        subprocess.run(
            [sys.executable, str(SNAPSHOT), str(PACKAGE), "--output", str(BASELINE)],
            check=True,
        )
        print(f"updated {BASELINE}")
        return 0

    if not BASELINE.is_file():
        print(f"{BASELINE} is missing; run Scripts/check-semantic-baseline.py --update")
        return 1

    with tempfile.TemporaryDirectory() as directory:
        current = Path(directory) / "current.json"
        subprocess.run(
            [sys.executable, str(SNAPSHOT), str(PACKAGE), "--output", str(current)],
            check=True,
        )
        report = Path(directory) / "report.json"
        result = subprocess.run(
            [
                sys.executable,
                str(DIFF),
                str(BASELINE),
                str(current),
                "--output",
                str(report),
                "--fail-on-change",
            ]
        )
        if result.returncode:
            if report.is_file():
                print(report.read_text(encoding="utf-8")[:4000])
            print(
                "mobile package drifted from the semantic baseline; review the "
                "change and run Scripts/check-semantic-baseline.py --update"
            )
            return 1
    print("mobile package matches the semantic baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
