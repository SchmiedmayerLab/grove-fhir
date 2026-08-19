#!/usr/bin/env python3
"""Fail closed when conformance evidence, its lock, or its source revision drifts."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from conformance_evidence import (
    ARCHIVE_FILENAME,
    EvidenceError,
    verify_evidence,
    verify_site_evidence,
)


REPOSITORY = Path(__file__).resolve().parent.parent


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    full = commands.add_parser("full", help="verify source inputs and the complete evidence")
    full.add_argument("--repository", type=Path, default=REPOSITORY)
    full.add_argument(
        "--manifest", type=Path, default=REPOSITORY / "Conformance/evidence.json"
    )
    full.add_argument(
        "--schema", type=Path, default=REPOSITORY / "Conformance/evidence.schema.json"
    )
    full.add_argument(
        "--evidence", type=Path, default=REPOSITORY / ".build/conformance-evidence"
    )
    full.add_argument(
        "--archive", type=Path, default=REPOSITORY / ".build" / ARCHIVE_FILENAME
    )
    full.add_argument("--expected-revision")
    site = commands.add_parser(
        "site", help="verify a downloaded Pages artifact and its bundled source revision"
    )
    site.add_argument("--site", type=Path, required=True)
    site.add_argument("--expected-revision", required=True)
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "full":
            failures = verify_evidence(
                arguments.repository,
                arguments.manifest,
                arguments.schema,
                arguments.evidence,
                arguments.archive,
                arguments.expected_revision,
            )
        else:
            failures = verify_site_evidence(arguments.site, arguments.expected_revision)
        if failures:
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("Conformance evidence lock is current and internally consistent")
        return 0
    except (EvidenceError, OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
