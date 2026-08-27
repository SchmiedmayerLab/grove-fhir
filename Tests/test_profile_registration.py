# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vp", ROOT / "Scripts/validate-producer.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

GUIDES = (
    "mobile",
    "sensor",
    "sensorkit",
    "healthkit",
    "health-connect",
    "providers",
    "withings",
    "oura",
    "google-health",
    "questionnaire",
)


def declared_profiles(guide: str) -> set[str]:
    """Every profile a guide's own FSH declares, by id."""
    ids: set[str] = set()
    for path in sorted((ROOT / guide / "input/fsh").glob("*.fsh")):
        text = path.read_text(encoding="utf-8")
        for block in re.split(r"^(?=Profile:)", text, flags=re.MULTILINE)[1:]:
            match = re.search(r"^Id:\s*(\S+)$", block, re.MULTILINE)
            if match:
                ids.add(match.group(1))
    return ids


class ProfileRegistrationTests(unittest.TestCase):
    """A profile a guide declares must be registered everywhere the toolchain looks for it.

    A profile registered in only some of these is worse than one that does not exist: the guide
    publishes it, a producer emits it, and the conversion Provenance is then rejected for
    targeting a resource outside the adapter's output contract. Nothing else checks this.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        cls.claims = json.loads((ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8"))

    def test_every_declared_profile_is_in_the_package_graph(self) -> None:
        graph_ids = set()
        for package in self.graph["packages"]:
            graph_ids.update(package.get("profiles", []))
        for guide in GUIDES:
            for profile in declared_profiles(guide):
                with self.subTest(guide=guide, profile=profile):
                    self.assertIn(profile, graph_ids)

    def test_every_adapter_observation_profile_is_known_to_the_validator(self) -> None:
        known = {
            profile
            for profiles in VALIDATOR.ADAPTER_PACKAGE_PROFILES.values()
            for profile in profiles
        }
        for guide in (
            "sensorkit",
            "healthkit",
            "health-connect",
            "providers",
            "withings",
            "oura",
            "google-health",
        ):
            canonical_root = f"https://grovealliance.org/fhir/{guide}/StructureDefinition/"
            for profile in declared_profiles(guide):
                if not profile.endswith("-observation"):
                    continue
                with self.subTest(guide=guide, profile=profile):
                    self.assertIn(canonical_root + profile, known)

    def test_platform_exclusive_profiles_are_claimed_and_targetable(self) -> None:
        claimed = set(self.claims["sensorKitPlatformExclusiveClaims"]["profiles"])
        targets = {
            target
            for claim in self.claims["adapterConversionProvenanceClaims"]
            if claim.get("adapter") == "sensorkit"
            for target in claim["targetAdapterProfiles"]
        }
        catalog = json.loads((ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8"))
        for entry in catalog["entries"]:
            structured = entry.get("structured", {})
            if structured.get("status") != "platform-exclusive":
                continue
            profile = structured["profile"]
            with self.subTest(source=entry["sourceTypeCode"]):
                self.assertIn(profile, claimed)
                self.assertIn(profile, targets)
