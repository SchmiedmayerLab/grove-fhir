#!/usr/bin/env python3
"""Report IG Publisher QA counts and fail on errors or warnings."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
from collections import namedtuple
import html
import json
import os
import re
from pathlib import Path


SUPPRESSED_MESSAGE = re.compile(
    r"<li>((?:WARNING|ERROR):.*?)\s*"
    r"<span[^>]*>\(([0-9]+) uses\)</span></li>",
    re.DOTALL,
)


FindingCounts = namedtuple(
    "FindingCounts",
    (
        "raw_errors",
        "exact_suppressed_errors",
        "unsuppressed_errors",
        "raw_warnings",
        "exact_suppressed_warnings",
        "unsuppressed_warnings",
    ),
)


def finding_counts(
    qa: dict[str, object], exact_suppressions: dict[str, int]
) -> FindingCounts:
    """Normalize Publisher's asymmetric treatment of ignored errors/warnings.

    Publisher 2.3.2 removes ignored warnings and HTML-link errors from the JSON
    totals, but keeps ignored resource-validation errors in ``qa.json.errs``. The
    HTML suppressed section is therefore the authoritative exact count for both
    severities. ``validate_suppressions`` separately requires each configured
    message to appear exactly once, and repository tests close the admitted error
    families.
    """

    publisher_errors = int(qa.get("errs", qa.get("errors", 0)))
    publisher_unsuppressed_warnings = int(qa.get("warnings", 0))
    suppressed_link_errors = sum(
        count
        for message, count in exact_suppressions.items()
        if message.startswith("ERROR: en/")
    )
    suppressed_validation_errors = sum(
        count
        for message, count in exact_suppressions.items()
        if message.startswith("ERROR: ") and not message.startswith("ERROR: en/")
    )
    suppressed_errors = suppressed_link_errors + suppressed_validation_errors
    suppressed_warnings = sum(
        count
        for message, count in exact_suppressions.items()
        if message.startswith("WARNING: ")
    )
    if publisher_errors < suppressed_validation_errors:
        raise ValueError(
            "Publisher error count is smaller than its exact suppressed "
            "resource-validation error count"
        )
    return FindingCounts(
        raw_errors=publisher_errors + suppressed_link_errors,
        exact_suppressed_errors=suppressed_errors,
        unsuppressed_errors=publisher_errors - suppressed_validation_errors,
        raw_warnings=publisher_unsuppressed_warnings + suppressed_warnings,
        exact_suppressed_warnings=suppressed_warnings,
        unsuppressed_warnings=publisher_unsuppressed_warnings,
    )


def configured_suppressions(path: Path) -> list[str]:
    """Read only exact, resource-scoped Publisher suppression messages."""
    messages: list[str] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "== Suppressed Messages ==":
            continue
        if not line.startswith(("WARNING: ", "ERROR: ")):
            raise ValueError(
                f"{path}:{line_number} is a broad suppression; exact messages must "
                "start with WARNING: or ERROR:"
            )
        messages.append(" ".join(line.split()))
    if len(messages) != len(set(messages)):
        raise ValueError(f"{path} repeats an exact suppression")
    return messages


def exercised_suppressions(path: Path) -> dict[str, int]:
    """Extract exact suppressed messages and their Publisher use counts."""
    qa = path.read_text(encoding="utf-8")
    _, marker, suppressed = qa.partition('<a name="suppressed">')
    if not marker:
        return {}
    suppressed = suppressed.partition('<a name="sorted">')[0]
    result: dict[str, int] = {}
    for raw_message, raw_count in SUPPRESSED_MESSAGE.findall(suppressed):
        message = " ".join(html.unescape(re.sub(r"<[^>]+>", "", raw_message)).split())
        if message in result:
            raise ValueError(f"{path} repeats suppressed message {message!r}")
        result[message] = int(raw_count)
    return result


BROKEN_LINK = re.compile(r"The link '([^']+)'")


def broken_link_targets(qa_path: Path) -> set[str]:
    """Every distinct target the Publisher could not resolve.

    Counted separately from warnings: the Publisher reports broken links in its own tally, so a
    guide can carry them while reporting zero warnings, which is how they stayed invisible.
    """
    qa = qa_path.read_text(encoding="utf-8")
    _, marker, internal = qa.partition('<a name="internal">')
    if not marker:
        return set()
    plain = html.unescape(re.sub(r"<[^>]+>", " ", internal)).replace("\u200b", "")
    return set(BROKEN_LINK.findall(plain))


def configured_broken_links(path: Path) -> set[str]:
    """Targets a guide declares unresolvable, each with a reason in the file."""
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def validate_broken_links(guide: Path) -> list[str]:
    declared = configured_broken_links(guide / "input" / "expectedBrokenLinks.txt")
    found = broken_link_targets(guide / "output" / "qa.html")
    problems = [f"undeclared broken link: {target}" for target in sorted(found - declared)]
    problems.extend(
        f"declared broken link no longer occurs: {target}" for target in sorted(declared - found)
    )
    return problems


def validate_suppressions(guide: Path) -> list[str]:
    """Return exact configuration/execution mismatches for one built guide."""
    configured_path = guide / "input" / "ignoreWarnings.txt"
    qa_path = guide / "output" / "qa.html"
    if not configured_path.is_file():
        return [f"missing {configured_path}"]
    if not qa_path.is_file():
        return [f"missing {qa_path}"]
    try:
        configured = configured_suppressions(configured_path)
        exercised = exercised_suppressions(qa_path)
    except ValueError as error:
        return [str(error)]
    problems = [
        f"configured suppression was not exercised exactly: {message}"
        for message in configured
        if exercised.get(message) != 1
    ]
    problems.extend(
        f"Publisher exercised an unconfigured suppression: {message}"
        for message in sorted(set(exercised) - set(configured))
    )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true", help="append a table to the GitHub job summary")
    parser.add_argument("guides", nargs="+", type=Path)
    arguments = parser.parse_args()

    rows: list[tuple[str, FindingCounts | None, int]] = []
    failed = False
    for guide in arguments.guides:
        qa_path = guide / "output" / "qa.json"
        if not qa_path.is_file():
            print(f"{guide}: missing {qa_path}")
            rows.append((str(guide), None, -1))
            failed = True
            continue
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        hints = int(qa.get("hints", 0))
        suppression_problems = validate_suppressions(guide)
        suppression_problems.extend(validate_broken_links(guide))
        try:
            exact_suppressions = exercised_suppressions(guide / "output" / "qa.html")
            counts = finding_counts(qa, exact_suppressions)
        except ValueError as error:
            suppression_problems.append(str(error))
            counts = FindingCounts(-1, -1, -1, -1, -1, -1)
        rows.append((str(guide), counts, hints))
        print(
            f"{guide}: raw-errors={counts.raw_errors} "
            f"exact-suppressed-errors={counts.exact_suppressed_errors} "
            f"unsuppressed-errors={counts.unsuppressed_errors} "
            f"raw-warnings={counts.raw_warnings} "
            f"exact-suppressed-warnings={counts.exact_suppressed_warnings} "
            f"unsuppressed-warnings={counts.unsuppressed_warnings} hints={hints} "
            f"broken-links={len(broken_link_targets(guide / 'output' / 'qa.html'))}"
        )
        failed |= counts.unsuppressed_errors != 0 or counts.unsuppressed_warnings != 0
        for problem in suppression_problems:
            print(f"{guide}: {problem}")
        failed |= bool(suppression_problems)

    if arguments.summary and (summary_path := os.environ.get("GITHUB_STEP_SUMMARY")):
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write("## FHIR implementation-guide QA\n\n")
            summary.write(
                "| Guide | Raw errors | Exact-suppressed errors | Unsuppressed errors | "
                "Raw warnings | Exact-suppressed warnings | Unsuppressed warnings | Hints |\n"
                "|---|---:|---:|---:|---:|---:|---:|---:|\n"
            )
            for guide, counts, hints in rows:
                if counts is None:
                    summary.write(f"| `{guide}` | - | - | - | - | - | - | {hints} |\n")
                    continue
                summary.write(
                    f"| `{guide}` | {counts.raw_errors} | "
                    f"{counts.exact_suppressed_errors} | {counts.unsuppressed_errors} | "
                    f"{counts.raw_warnings} | {counts.exact_suppressed_warnings} | "
                    f"{counts.unsuppressed_warnings} | {hints} |\n"
                )

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
