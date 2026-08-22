"""Validate the machine-readable Grove FHIR package graph."""

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


ROOT = Path(__file__).parents[1]


class PackageGraphTests(unittest.TestCase):
    def test_graph_has_exact_r4_version_and_safe_canonicals(self) -> None:
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        self.assertEqual(set(graph), {"schemaVersion", "fhirVersion", "version", "canonicalRoot", "packages"})
        self.assertEqual(graph["schemaVersion"], 1)
        self.assertEqual(graph["fhirVersion"], "4.0.1")
        self.assertEqual(graph["version"], "0.3.0")
        self.assertEqual(graph["canonicalRoot"], "https://grovealliance.org/fhir")
        sources = [package["source"] for package in graph["packages"]]
        self.assertEqual(
            sources,
            ["mobile", "questionnaire", "sensor", "sensorkit", "healthkit", "health-connect", "providers"],
        )
        self.assertEqual(len(sources), len(set(sources)))
        for package in graph["packages"]:
            self.assertEqual(
                set(package), {"source", "packageId", "canonical", "dependencies", "profiles"}
            )
            self.assertEqual(package["canonical"], f"{graph['canonicalRoot']}/{package['source']}")
            self.assertRegex(package["packageId"], r"^org[.]grovealliance[.]fhir[.][a-z-]+$")
            self.assertEqual(package["profiles"], sorted(set(package["profiles"])))
            for profile in package["profiles"]:
                self.assertRegex(profile, r"^[a-z][a-z0-9-]{0,63}$")

    def test_readme_and_publication_list_the_complete_graph(self) -> None:
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        publication = json.loads((ROOT / "publication/config.json").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        publication_doc = (ROOT / "PUBLICATION.md").read_text(encoding="utf-8")
        configured = {guide["source"] for guide in publication["guides"]}
        expected = {package["source"] for package in graph["packages"]}
        self.assertEqual(configured, expected)
        for package in graph["packages"]:
            self.assertIn(f"`{package['packageId']}`", readme)
            self.assertIn(f"`{package['packageId']}`", publication_doc)
            self.assertIn(f"/{package['source']}/", publication_doc)

    def test_conformance_documentation_names_every_closed_claim_mode(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        conformance = (ROOT / "Conformance/README.md").read_text(encoding="utf-8")
        self.assertIn("catalog/profile-claims.json", conformance)
        self.assertIn("authoritative R4 BMI profile", conformance)
        self.assertIn("specimen-specific glucose", conformance)
        self.assertIn("SensorKit-only", conformance)
        self.assertIn("SensorKit ECG hybrid", conformance)
        self.assertIn("raw SensorKit or Provider DocumentReference", conformance)
        self.assertIn("Adapter conversion Provenance", conformance)
        self.assertIn("requiredProfiles", conformance)
        self.assertEqual(
            claims["sensorKitHybridObservationClaims"]["cardinality"], 2
        )
        self.assertEqual(
            claims["healthConnectPlatformExclusiveClaims"]["cardinality"], 1
        )
        self.assertEqual(
            claims["sensorKitPlatformExclusiveClaims"]["cardinality"], 1
        )
        self.assertEqual(
            claims["sensorKitRecordingDocumentClaim"]["cardinality"], 2
        )
        self.assertEqual(
            claims["providerRecordingDocumentClaim"]["cardinality"], 2
        )

    def test_sensorkit_conversion_claim_covers_every_registered_output(self) -> None:
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        claims = json.loads((ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8"))
        package = next(
            entry for entry in graph["packages"] if entry["source"] == "sensorkit"
        )
        claim = next(
            entry
            for entry in claims["adapterConversionProvenanceClaims"]
            if entry["adapter"] == "sensorkit"
        )
        # Every SensorKit output profile derives from sensorkit-observation or is the
        # recording document, so the conversion Provenance targets all of them.
        base = f"{package['canonical']}/StructureDefinition/"
        expected = sorted(
            base + name
            for name in package["profiles"]
            if base + name != claim["profile"]
        )
        self.assertEqual(claim["targetAdapterProfiles"], expected)


if __name__ == "__main__":
    unittest.main()
