# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_content", ROOT / "Scripts/check-content.py")
CHECK_CONTENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CONTENT)


class CatalogVersionProseTests(unittest.TestCase):
    def test_every_catalog_states_only_its_own_version(self) -> None:
        for path in sorted((ROOT / "catalog").glob("*.json")):
            catalog = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(catalog=path.name):
                self.assertEqual(
                    CHECK_CONTENT.stale_version_prose(path.name, catalog, catalog["version"]),
                    [],
                )

    def test_a_stale_version_is_reported(self) -> None:
        self.assertEqual(
            CHECK_CONTENT.stale_version_prose(
                "providers-adapter.json",
                {"sourceEvidence": {"tokenBinding": "the exact v0.3.0 consumed source surface"}},
                "0.5.0",
            ),
            [
                "catalog/providers-adapter.json field sourceEvidence.tokenBinding "
                "names version 0.3.0, but the catalog is 0.5.0"
            ],
        )

    def test_a_pinned_third_party_version_is_not_a_grove_version(self) -> None:
        self.assertEqual(
            CHECK_CONTENT.stale_version_prose(
                "package-graph.json",
                {"packages": [{"dependencies": ["hl7.fhir.uv.extensions#7.3.0"]}]},
                "0.5.0",
            ),
            [],
        )

    def test_a_field_declared_historical_may_name_an_earlier_release(self) -> None:
        self.assertEqual(
            CHECK_CONTENT.stale_version_prose(
                "sensorkit-adapter.json",
                {"inventoryScopes": {"catalog-baseline": "the initial closed v0.3.0 catalog baseline"}},
                "0.5.0",
            ),
            [],
        )

    def test_the_manifest_schema_pins_the_release_the_graph_states(self) -> None:
        # The producer-manifest schema states the release as a JSON Schema const, which nothing
        # else derives. A literal that has to be remembered is how validate-producer.py sat at
        # 0.4.0 through the 0.5.0 bump.
        schema = json.loads(
            (ROOT / "Conformance/producer-manifest.schema.json").read_text(encoding="utf-8")
        )
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        found = []

        def walk(node: object) -> None:
            if isinstance(node, dict):
                if set(node) == {"const"} and isinstance(node["const"], str):
                    found.append(node["const"])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(schema.get("$defs", schema))
        # 4.0.1 is the FHIR release the schema also pins; it does not move with Grove.
        versions = [
            value for value in found if value.count(".") == 2 and value != "4.0.1"
        ]
        self.assertTrue(versions, "the manifest schema pins no release version")
        for version in versions:
            self.assertEqual(version, graph["version"])
