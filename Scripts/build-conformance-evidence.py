#!/usr/bin/env python3
"""Build deterministic conformance evidence and inject it into GitHub Pages."""

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
    build_evidence,
    inject_pages,
    parse_external_evidence,
    parse_package_overrides,
    parse_validation_reports,
    update_semantic_baseline,
    verify_evidence,
)


REPOSITORY = Path(__file__).resolve().parent.parent


def _common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    parser.add_argument(
        "--manifest", type=Path, default=REPOSITORY / "Conformance/evidence.json"
    )
    parser.add_argument(
        "--schema", type=Path, default=REPOSITORY / "Conformance/evidence.schema.json"
    )
    parser.add_argument(
        "--evidence", type=Path, default=REPOSITORY / ".build/conformance-evidence"
    )
    parser.add_argument(
        "--archive", type=Path, default=REPOSITORY / ".build" / ARCHIVE_FILENAME
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="build and immediately verify the evidence")
    _common_paths(build)
    build.add_argument(
        "--package",
        action="append",
        default=[],
        metavar="GUIDE=PATH",
        help="replace one declared sanitized package input; the lock records override mode",
    )
    build.add_argument(
        "--external-evidence",
        action="append",
        default=[],
        metavar="EVIDENCE_SET_ID=PATH",
        help="location of one exact manifest-declared external evidence set",
    )
    build.add_argument(
        "--semantic-base",
        help="exact event base commit; an all-zero SHA denotes the first baseline",
    )
    build.add_argument(
        "--validation-report",
        action="append",
        default=[],
        metavar="REPORT_ID=PATH",
        help="location of one exact manifest-declared generated validation report",
    )
    inject = commands.add_parser(
        "inject-pages", help="verify evidence and inject it into an assembled Pages site"
    )
    _common_paths(inject)
    inject.add_argument("--site", type=Path, default=REPOSITORY / ".build/pages")
    baseline = commands.add_parser(
        "update-semantic-baseline",
        help="deliberately update the reviewed baseline from sanitized package bytes",
    )
    _common_paths(baseline)
    baseline.add_argument(
        "--package",
        action="append",
        default=[],
        metavar="GUIDE=PATH",
        help="replace one declared sanitized package input for this explicit update",
    )
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "build":
            build_evidence(
                repository=arguments.repository,
                manifest_path=arguments.manifest,
                schema_path=arguments.schema,
                output=arguments.evidence,
                archive=arguments.archive,
                overrides=parse_package_overrides(arguments.package),
                semantic_base_revision=arguments.semantic_base,
                external_locations=parse_external_evidence(
                    arguments.external_evidence
                ),
                validation_report_locations=parse_validation_reports(
                    arguments.validation_report
                ),
            )
            failures = verify_evidence(
                arguments.repository,
                arguments.manifest,
                arguments.schema,
                arguments.evidence,
                arguments.archive,
            )
            if failures:
                raise EvidenceError("built evidence failed verification:\n" + "\n".join(failures))
            print(f"Built and verified {arguments.archive}")
            return 0
        if arguments.command == "update-semantic-baseline":
            update_semantic_baseline(
                repository=arguments.repository,
                manifest_path=arguments.manifest,
                schema_path=arguments.schema,
                overrides=parse_package_overrides(arguments.package),
            )
            print("Updated Conformance/semantic-baseline.json for review")
            return 0
        failures = verify_evidence(
            arguments.repository,
            arguments.manifest,
            arguments.schema,
            arguments.evidence,
            arguments.archive,
        )
        if failures:
            raise EvidenceError("refusing to inject invalid evidence:\n" + "\n".join(failures))
        inject_pages(arguments.evidence, arguments.archive, arguments.site)
        print(f"Injected conformance evidence into {arguments.site}")
        return 0
    except (EvidenceError, OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
