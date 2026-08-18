#!/usr/bin/env python3
"""Report IG Publisher QA counts and fail on errors or warnings."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true", help="append a table to the GitHub job summary")
    parser.add_argument("guides", nargs="+", type=Path)
    arguments = parser.parse_args()

    rows: list[tuple[str, int, int, int]] = []
    failed = False
    for guide in arguments.guides:
        qa_path = guide / "output" / "qa.json"
        if not qa_path.is_file():
            print(f"{guide}: missing {qa_path}")
            rows.append((str(guide), -1, -1, -1))
            failed = True
            continue
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        errors = int(qa.get("errs", 0))
        warnings = int(qa.get("warnings", 0))
        hints = int(qa.get("hints", 0))
        rows.append((str(guide), errors, warnings, hints))
        print(f"{guide}: errors={errors} warnings={warnings} hints={hints}")
        failed |= errors > 0 or warnings > 0

    if arguments.summary and (summary_path := os.environ.get("GITHUB_STEP_SUMMARY")):
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write("## FHIR implementation-guide QA\n\n")
            summary.write("| Guide | Errors | Warnings | Hints |\n|---|---:|---:|---:|\n")
            for guide, errors, warnings, hints in rows:
                summary.write(f"| `{guide}` | {errors} | {warnings} | {hints} |\n")

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
