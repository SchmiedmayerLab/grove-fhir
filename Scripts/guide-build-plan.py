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
PINNED = re.compile(
    r"^  org\.grovealliance\.fhir\.([a-z-]+):\s*\n\s+version:\s*(\S+)", re.MULTILINE
)


def guides() -> list[str]:
    """Every published guide, in the order the publication declares them."""
    publication = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    return [package["source"] for package in publication["packages"]]


def dependencies(guide: str) -> set[str]:
    """The Grove guides this guide reads, as its own SUSHI configuration states them."""
    configuration = (ROOT / guide / "sushi-config.yaml").read_text(encoding="utf-8")
    return set(DEPENDENCY.findall(configuration)) - {guide}


def pinned(guide: str) -> list[tuple[str, str]]:
    """Each Grove guide this guide depends on, with the version it pins."""
    configuration = (ROOT / guide / "sushi-config.yaml").read_text(encoding="utf-8")
    return [pin for pin in PINNED.findall(configuration) if pin[0] != guide]


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


def ci_outputs(levels: int) -> dict[str, list[str]]:
    """The guides for each CI wave job, split into the trunk that gates the next wave and leaves.

    A guide belongs to the trunk when another guide depends on it. Every dependency of a guide in
    wave N is therefore a trunk guide of an earlier wave, so wave N needs only the trunk of wave
    N-1 to have finished, and a leaf, however slow, gates nothing but the final aggregate.
    `builtN` is the trunk of waves 1 to N: what the jobs of wave N+1 restore before building.
    The last level has no trunk job, because nothing can depend on its guides.
    """
    plan = waves()
    if len(plan) > levels:
        raise SystemExit(
            f"::error::the guide graph now has {len(plan)} waves but CI provides {levels}; "
            "add a trunk and a leaf job and raise --ci-outputs"
        )
    trunk = set().union(*(dependencies(guide) for guide in guides()))
    outputs: dict[str, list[str]] = {}
    built: list[str] = []
    for level in range(1, levels + 1):
        wave = plan[level - 1] if level <= len(plan) else []
        outputs[f"leaf{level}"] = [guide for guide in wave if guide not in trunk]
        if level < levels:
            outputs[f"trunk{level}"] = [guide for guide in wave if guide in trunk]
            built.extend(outputs[f"trunk{level}"])
            outputs[f"built{level}"] = sorted(built)
        elif any(guide in trunk for guide in wave):
            raise SystemExit(f"::error::wave {level} has dependents but no later wave job")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("lines", "json"),
        default="lines",
        help="lines prints one wave per line for a shell; json emits the waves for a CI matrix",
    )
    parser.add_argument(
        "--dependencies",
        metavar="GUIDE",
        help="print each Grove guide this guide depends on, as 'name version', one per line",
    )
    parser.add_argument(
        "--wave",
        type=int,
        help="print only this wave, counted from 1; prints nothing when the plan has no such wave",
    )
    parser.add_argument(
        "--ci-outputs",
        type=int,
        metavar="LEVELS",
        help="print the trunk, leaf, and built guides of each CI wave job as GITHUB_OUTPUT lines",
    )
    arguments = parser.parse_args()
    if arguments.ci_outputs is not None:
        for name, value in ci_outputs(arguments.ci_outputs).items():
            print(f"{name}={json.dumps(value)}")
        return 0
    if arguments.dependencies:
        for name, version in pinned(arguments.dependencies):
            print(f"{name} {version}")
        return 0
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
