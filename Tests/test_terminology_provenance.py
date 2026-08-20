"""Verify the bounded HealthKit terminology allowlist and its provenance record."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "healthkit/input/data/terminology-provenance.json"
TERMINOLOGY = ROOT / "healthkit/input/fsh/terminology.fsh"
CONFIGURATION = ROOT / "healthkit/sushi-config.yaml"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def configuration_value(name: str) -> str:
    match = re.search(
        rf"^{re.escape(name)}:\s+(.+?)\s*$",
        CONFIGURATION.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"missing {name} in {CONFIGURATION.relative_to(ROOT)}")
    return match.group(1).strip('"')


def code_system_concepts(source: str, name: str) -> set[str]:
    block = re.search(
        rf"^CodeSystem:\s+{re.escape(name)}\s*$"
        rf"(?P<body>.*?)(?=^(?:CodeSystem|ValueSet|Profile|Extension|Instance):|\Z)",
        source,
        re.MULTILINE | re.DOTALL,
    )
    if block is None:
        raise AssertionError(f"missing CodeSystem {name}")
    return set(re.findall(r"^\* #([^\s]+)", block.group("body"), re.MULTILINE))


class TerminologyProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.terminology = TERMINOLOGY.read_text(encoding="utf-8")

    def test_manifest_identifies_the_exact_package_and_source_baseline(self) -> None:
        self.assertEqual(self.manifest["schemaVersion"], 1)
        self.assertEqual(
            self.manifest["package"],
            f"{configuration_value('id')}#{configuration_value('version')}",
        )
        source = self.manifest["source"]
        self.assertEqual(source["framework"], "Apple HealthKit")
        self.assertRegex(source["sdk"], r"^iPhoneOS \d+\.\d+$")
        self.assertRegex(source["xcode"]["version"], r"^\d+\.\d+$")
        self.assertTrue(source["xcode"]["build"])
        self.assertIsNone(source["sourceCommit"])
        self.assertTrue(source["sourceCommitReason"])

        files = source["files"]
        self.assertEqual(len({entry["path"] for entry in files}), len(files))
        self.assertGreaterEqual(len(files), 2)
        for entry in files:
            self.assertRegex(entry["sha256"], SHA256)
            self.assertTrue(entry["path"].startswith("HealthKit.framework/Headers/"))
        self.assertEqual(len(source["documentation"]), 3)
        for url in source["documentation"]:
            self.assertTrue(url.startswith("https://developer.apple.com/documentation/healthkit/"))

    def test_manifest_covers_exactly_the_published_terminology_allowlist(self) -> None:
        artifacts = self.manifest["terminology"]["artifacts"]
        self.assertEqual(
            set(artifacts),
            {"healthkit-metadata-key", "healthkit-heart-rate-motion-context"},
        )
        self.assertTrue(self.manifest["terminology"]["caseSensitive"])
        self.assertIn("Id: healthkit-metadata-key", self.terminology)
        self.assertIn("Id: healthkit-heart-rate-motion-context", self.terminology)
        for artifact in artifacts.values():
            self.assertEqual(artifact["content"], "complete")
            self.assertTrue(artifact["rationale"])
        self.assertEqual(
            code_system_concepts(self.terminology, "HealthKitMetadataKeyCS"),
            {"HKMetadataKeyHeartRateMotionContext"},
        )

    def test_motion_context_raw_values_match_the_fsh_codes(self) -> None:
        motion = self.manifest["terminology"]["artifacts"][
            "healthkit-heart-rate-motion-context"
        ]
        mapping = motion["rawNSNumberMapping"]
        self.assertEqual(
            mapping,
            {
                "0": {"sourceCase": "notSet", "adapterCode": "not-set"},
                "1": {"sourceCase": "sedentary", "adapterCode": "sedentary"},
                "2": {"sourceCase": "active", "adapterCode": "active"},
            },
        )
        self.assertEqual(motion["unknownValuePolicy"], "reject-or-omit-never-default")
        self.assertEqual(
            code_system_concepts(self.terminology, "HealthKitHeartRateMotionContextCS"),
            {entry["adapterCode"] for entry in mapping.values()},
        )
        for entry in mapping.values():
            self.assertRegex(
                self.terminology,
                re.compile(
                    rf"^\* #{re.escape(entry['adapterCode'])}(?:\s|$)",
                    re.MULTILINE,
                ),
            )

    def test_manifest_distinguishes_third_party_terms_from_repository_license(self) -> None:
        third_party = self.manifest["thirdParty"]
        self.assertEqual(third_party["owner"], "Apple Inc.")
        for key in (
            "attribution",
            "retainedTerminology",
            "descriptiveApiReferences",
            "redistributionBasis",
            "excludedMaterial",
            "repositoryLicense",
        ):
            self.assertTrue(third_party[key])
        self.assertIn("MIT", third_party["repositoryLicense"])
        self.assertIn("Apple", third_party["attribution"])

    def test_obsolete_yaml_manifest_is_absent(self) -> None:
        self.assertFalse(MANIFEST.with_suffix(".yaml").exists())


if __name__ == "__main__":
    unittest.main()
