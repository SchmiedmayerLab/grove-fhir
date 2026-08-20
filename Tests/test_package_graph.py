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
        self.assertEqual(graph["version"], "0.2.0")
        self.assertEqual(graph["canonicalRoot"], "https://grovealliance.org/fhir")
        sources = [package["source"] for package in graph["packages"]]
        self.assertEqual(
            sources,
            ["mobile", "questionnaire", "sensor", "healthkit", "health-connect", "connected-health"],
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


if __name__ == "__main__":
    unittest.main()
