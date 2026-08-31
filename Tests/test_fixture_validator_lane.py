"""Keep every committed fixture inside the official-Validator lane."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Conformance/fixture-validator-manifest.json"

sys.path.insert(0, str(ROOT / "Scripts"))
_spec = importlib.util.spec_from_file_location(
    "validate_fixtures", ROOT / "Scripts/validate-fixtures.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("Cannot load the fixture validator lane")
lane = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lane
_spec.loader.exec_module(lane)


class FixtureValidatorLaneTests(unittest.TestCase):
    def test_every_committed_fixture_is_validated_or_excluded_with_a_reason(self) -> None:
        """A worked example nothing validates is how the step-count defect shipped.

        The lane only closes that hole while it covers everything: each JSON file beneath the
        declared roots is either sent to the official Validator or excluded on the record.
        """
        self.assertEqual(lane.main(["--coverage-only"]), 0)

    def test_the_lane_refuses_a_fixture_nobody_classified(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(
            dir=ROOT / "questionnaire/fixtures", prefix="unclassified-"
        ) as directory:
            stray = Path(directory) / "stray.json"
            stray.write_text('{"resourceType":"Basic"}\n', encoding="utf-8")
            with self.assertRaisesRegex(
                lane.ProducerValidationError, "validated or excluded with a reason"
            ):
                lane.validate_coverage(manifest)

    def test_the_lane_refuses_a_manifest_that_misstates_a_claimed_profile(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["resources"][0]["profiles"] = [
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
        ]
        with self.assertRaisesRegex(lane.ProducerValidationError, "but the fixture claims"):
            lane.validate_coverage(manifest)

    def test_every_declared_package_is_a_published_grove_release_package(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        graph = json.loads(
            (ROOT / "catalog/package-graph.json").read_text(encoding="utf-8")
        )
        published = {package["packageId"] for package in graph["packages"]}
        release = json.loads(
            (ROOT / "catalog/release-manifest.json").read_text(encoding="utf-8")
        )["releaseVersion"]
        for package in manifest["packages"]:
            with self.subTest(package=package["packageId"]):
                self.assertIn(package["packageId"], published)
                self.assertEqual(package["version"], release)

    def test_every_grove_profile_a_fixture_claims_is_covered_by_a_declared_package(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        graph = json.loads(
            (ROOT / "catalog/package-graph.json").read_text(encoding="utf-8")
        )
        declared = {package["alias"] for package in manifest["packages"]}
        available = {
            f"https://grovealliance.org/fhir/{package['source']}/StructureDefinition/{profile}"
            for package in graph["packages"]
            if package["source"] in declared
            for profile in package["profiles"]
        }
        for entry in manifest["resources"]:
            for profile in entry["profiles"]:
                with self.subTest(path=entry["path"], profile=profile):
                    self.assertIn(profile, available)


class FixtureValidatorLaneToolingTests(unittest.TestCase):
    def test_a_symlinked_fixture_root_member_is_refused(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(
            dir=ROOT / "questionnaire/fixtures", prefix="linked-"
        ) as directory:
            target = Path(directory) / "target.json"
            target.write_text("{}\n", encoding="utf-8")
            link = Path(directory) / "linked.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(
                lane.ProducerValidationError, "is not a regular file"
            ):
                lane.committed_json_files(manifest)
            shutil.rmtree(directory, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
