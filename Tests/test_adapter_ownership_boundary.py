"""Keep normative adapter contracts independent of consumer implementations."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from collections.abc import Iterator
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATHS = (
    ROOT / "catalog/healthkit-adapter.json",
    ROOT / "catalog/sensorkit-adapter.json",
    ROOT / "catalog/connected-health-adapter.json",
)
FORBIDDEN_KEYS = {
    "groveRepository",
    "groveRevision",
    "swiftProducer",
    "swiftImplementationStatus",
    "groveSensor",
    "sourceReference",
}
FORBIDDEN_TEXT = (
    re.compile(r"github\.com/SchmiedmayerLab/Grove(?!-fhir)", re.IGNORECASE),
    re.compile(r"github\.com/SchmiedmayerLab/MyHeartCounts", re.IGNORECASE),
    re.compile(r"\bbf7e25d1a59bc3afc20476f856ad54d2649edee4\b"),
    re.compile(r"\b09d8a5ed490b344b5523d036910a48b97220bad1\b"),
    re.compile(r"\bc16f5bbd18aac8d16b393a0cb64e9816c04930e3\b"),
    re.compile(r"\bGrove SampleType\b"),
    re.compile(r"\bcurrent Grove source adapter\b", re.IGNORECASE),
    re.compile(r"\bSwift adapter\b", re.IGNORECASE),
    re.compile(r"\bSwift status\b", re.IGNORECASE),
    re.compile(r"\bGrove source case\b", re.IGNORECASE),
    re.compile(r"\bplatform/Grove scope\b", re.IGNORECASE),
)


def nested_keys(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from nested_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_keys(child)


def owned_text_paths() -> list[Path]:
    paths = [
        *CATALOG_PATHS,
        ROOT / "Scripts/render-status-matrices.py",
        ROOT / "Scripts/render-adapter-source-terminology.py",
    ]
    for source in ("healthkit", "sensorkit", "connected-health"):
        paths.extend(sorted((ROOT / source / "input/pagecontent").glob("*.md")))
    return paths


class AdapterOwnershipBoundaryTests(unittest.TestCase):
    def test_normative_catalogs_have_no_consumer_owned_fields(self) -> None:
        for path in CATALOG_PATHS:
            with self.subTest(path=path.relative_to(ROOT)):
                catalog = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(FORBIDDEN_KEYS & set(nested_keys(catalog)), set())

    def test_catalogs_renderers_and_published_prose_have_no_consumer_pins(self) -> None:
        for path in owned_text_paths():
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_TEXT:
                with self.subTest(path=path.relative_to(ROOT), pattern=pattern.pattern):
                    self.assertIsNone(pattern.search(text))

    def test_platform_and_provider_evidence_is_authoritative_and_https(self) -> None:
        healthkit = json.loads(CATALOG_PATHS[0].read_text(encoding="utf-8"))
        self.assertEqual(healthkit["source"]["platform"], "Apple HealthKit")
        self.assertTrue(
            any(
                evidence.get("url", "").startswith(
                    "https://developer.apple.com/documentation/healthkit/"
                )
                for evidence in healthkit["source"]["evidence"]
            )
        )

        sensorkit = json.loads(CATALOG_PATHS[1].read_text(encoding="utf-8"))
        self.assertEqual(sensorkit["sourceEvidence"]["platform"], "Apple SensorKit")
        self.assertTrue(
            sensorkit["sourceEvidence"]["appleSensorInventory"].startswith(
                "https://developer.apple.com/documentation/sensorkit/"
            )
        )

        connected = json.loads(CATALOG_PATHS[2].read_text(encoding="utf-8"))
        evidence = connected["sourceEvidence"]["providers"]
        self.assertEqual(
            {provider["id"]: provider["version"] for provider in evidence},
            {"google-health-api": "v4", "oura": "2.0", "withings": "2.0"},
        )
        self.assertTrue(
            all(
                url.startswith("https://")
                for provider in evidence
                for url in provider["documentation"]
            )
        )


if __name__ == "__main__":
    unittest.main()
