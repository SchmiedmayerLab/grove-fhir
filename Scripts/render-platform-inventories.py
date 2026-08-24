#!/usr/bin/env python3
"""Record each platform's source inventory as committed evidence.

The generated files are the offline ground truth the adapter catalogs are checked
against. Regenerating them needs network access, and the Apple headers oracle
additionally needs an installed Xcode; the checks that consume them need neither.

Run with --check to verify the committed evidence still matches the platforms.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from platform_inventory import (  # noqa: E402
    ROOT,
    PlatformUnavailable,
    header_hashes,
    health_connect_inventory,
    healthkit_inventory,
    sdk_baseline,
    sensorkit_inventory,
)


def _apple_oracle(framework: str, retrieved: str) -> dict[str, Any]:
    return {
        "kind": "apple-runtime-identifiers",
        "method": (
            f"Every {framework} identifier constant declared by the SDK baseline, resolved "
            "inside an iOS simulator on that baseline, plus the sample types Apple exposes "
            "only through a class accessor. Documentation pages come from Apple's published "
            "symbol index."
        ),
        "sdkBaseline": sdk_baseline(),
        "headers": header_hashes(framework),
        "retrieved": retrieved,
    }


def healthkit_evidence(retrieved: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "oracle": _apple_oracle("HealthKit", retrieved),
        "sourceTypes": healthkit_inventory(refresh=True),
    }


def sensorkit_evidence(retrieved: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "oracle": _apple_oracle("SensorKit", retrieved),
        "sensors": sensorkit_inventory(refresh=True),
    }


def health_connect_evidence(retrieved: str) -> dict[str, Any]:
    # The pinned artifact version lives in the catalog, so a bump is one edit.
    catalog = json.loads(
        (ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8")
    )
    inventory = health_connect_inventory(catalog["source"]["version"])
    return {
        "schemaVersion": 1,
        "oracle": {
            "kind": "androidx-published-artifact",
            "artifact": inventory["artifact"],
            "sha256": inventory["sha256"],
            "filter": (
                "Top-level classes in androidx.health.connect.client.records whose name "
                "ends in Record, excluding the abstract supertypes Record, "
                "InstantaneousRecord, IntervalRecord, and SeriesRecord."
            ),
            "retrieved": retrieved,
        },
        "records": inventory["records"],
    }


EVIDENCE = {
    "healthkit/input/data/healthkit-inventory.json": healthkit_evidence,
    "sensorkit/input/data/sensorkit-inventory.json": sensorkit_evidence,
    "health-connect/input/data/health-connect-inventory.json": health_connect_evidence,
}


def serialize(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when the committed evidence is stale",
    )
    parser.add_argument(
        "--retrieved",
        default=datetime.date.today().isoformat(),
        help="retrieval date recorded in the evidence, for reproducible regeneration",
    )
    arguments = parser.parse_args()

    # A toolchain on a different SDK cannot speak to whether the vendor changed anything,
    # so say that plainly rather than reporting it as drift.
    recorded = json.loads(
        (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
    )["source"]["sdkBaseline"]
    try:
        installed = sdk_baseline()
    except PlatformUnavailable:
        installed = None
    if installed is not None and installed != recorded:
        print(
            f"This toolchain is {installed['platform']} {installed['version']} "
            f"(Xcode {installed['xcodeVersion']}, build {installed['xcodeBuild']}), but the "
            f"catalogs are frozen on {recorded['platform']} {recorded['version']} "
            f"(Xcode {recorded['xcodeVersion']}, build {recorded['xcodeBuild']}). Select the "
            "recorded Xcode before checking or regenerating the inventories.",
            file=sys.stderr,
        )
        return 2

    stale: list[str] = []
    unreachable: list[str] = []
    for relative, build in EVIDENCE.items():
        destination = ROOT / relative
        try:
            rendered = serialize(build(arguments.retrieved))
        except PlatformUnavailable as error:
            print(f"{relative}: platform unavailable ({error})", file=sys.stderr)
            unreachable.append(relative)
            continue
        if arguments.check:
            current = destination.read_text(encoding="utf-8") if destination.is_file() else ""
            # The retrieval date moves on every run, and documentation URLs follow Apple's live
            # site organization rather than the SDK; neither is part of the drift claim. Write
            # mode still refreshes both.
            if _sdk_facts(current) != _sdk_facts(rendered):
                stale.append(relative)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        print(f"wrote {relative}")

    if stale:
        for relative in stale:
            print(f"{relative} no longer matches its platform", file=sys.stderr)
        return 1
    return 2 if unreachable else 0


def _sdk_facts(text: str) -> str:
    if not text:
        return text
    payload = json.loads(text)

    def strip(node: object) -> object:
        if isinstance(node, dict):
            return {
                key: strip(value)
                for key, value in node.items()
                if key not in ("retrieved", "documentation")
            }
        if isinstance(node, list):
            return [strip(item) for item in node]
        return node

    return json.dumps(strip(payload), sort_keys=True)


if __name__ == "__main__":
    raise SystemExit(main())
