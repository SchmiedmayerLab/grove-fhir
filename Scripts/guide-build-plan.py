#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#

"""Orders the guides into waves that may each be built concurrently.

A guide reads the built package of every guide it depends on, so it cannot start until those have
finished. Everything within one wave is independent and may run at once.

The order is derived from each guide's own `sushi-config.yaml` rather than written down anywhere,
so adding a guide, or changing what one depends on, changes the plan without editing a script or a
workflow. Both the local parallel build and CI read this, so neither can drift from the other.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLICATION = ROOT / "publication/artifact-allowlist.json"
DEPENDENCY = re.compile(r"^  org\.grovealliance\.fhir\.([a-z-]+):", re.MULTILINE)


def guides() -> list[str]:
    """Every published guide, in the order the publication declares them."""
    publication = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    return [package["source"] for package in publication["packages"]]


def dependencies(guide: str) -> set[str]:
    """The Grove guides this guide reads, as its own SUSHI configuration states them."""
    configuration = (ROOT / guide / "sushi-config.yaml").read_text(encoding="utf-8")
    return set(DEPENDENCY.findall(configuration)) - {guide}


def waves() -> list[list[str]]:
    """The guides grouped so that every dependency lands in an earlier wave than its dependents."""
    remaining = {guide: dependencies(guide) for guide in guides()}
    ordered: list[list[str]] = []
    settled: set[str] = set()
    while remaining:
        wave = sorted(
            guide for guide, needs in remaining.items() if needs <= settled
        )
        if not wave:
            raise SystemExit(
                "guide dependencies form a cycle: " + ", ".join(sorted(remaining))
            )
        ordered.append(wave)
        settled.update(wave)
        for guide in wave:
            del remaining[guide]
    return ordered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("lines", "json"),
        default="lines",
        help="lines prints one wave per line for a shell; json emits the waves for a CI matrix",
    )
    parser.add_argument(
        "--wave",
        type=int,
        help="print only this wave, counted from 1; prints nothing when the plan has no such wave",
    )
    arguments = parser.parse_args()
    plan = waves()
    if arguments.wave is not None:
        wave = plan[arguments.wave - 1] if arguments.wave <= len(plan) else []
        print(json.dumps(wave) if arguments.format == "json" else " ".join(wave))
        return 0
    if arguments.format == "json":
        print(json.dumps(plan))
    else:
        for wave in plan:
            print(" ".join(wave))
    return 0


if __name__ == "__main__":
    sys.exit(main())
