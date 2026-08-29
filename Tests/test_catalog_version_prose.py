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
RELEASE_VERSION = json.loads(
    (ROOT / "catalog/release-manifest.json").read_text(encoding="utf-8")
)["releaseVersion"]
SPEC = importlib.util.spec_from_file_location("check_content", ROOT / "Scripts/check-content.py")
CHECK_CONTENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CONTENT)


class CatalogVersionProseTests(unittest.TestCase):
    def test_every_catalog_uses_version_neutral_implementation_prose(self) -> None:
        for path in sorted((ROOT / "catalog").glob("*.json")):
            catalog = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(catalog=path.name):
                version = catalog.get("version", catalog.get("releaseVersion"))
                self.assertIsInstance(version, str)
                self.assertEqual(
                    CHECK_CONTENT.stale_version_prose(path.name, catalog, version),
                    [],
                )

    def test_a_grove_release_number_in_prose_is_reported(self) -> None:
        self.assertEqual(
            CHECK_CONTENT.stale_version_prose(
                "providers-adapter.json",
                {"sourceEvidence": {"tokenBinding": "the 1.2.3 adapter source surface"}},
                RELEASE_VERSION,
            ),
            [
                "catalog/providers-adapter.json field sourceEvidence.tokenBinding names "
                "Grove release version 1.2.3; use version-neutral implementation wording"
            ],
        )

    def test_a_pinned_third_party_version_is_not_a_grove_version(self) -> None:
        self.assertEqual(
            CHECK_CONTENT.stale_version_prose(
                "package-graph.json",
                {"packages": [{"dependencies": ["hl7.fhir.uv.extensions#7.3.0"]}]},
                RELEASE_VERSION,
            ),
            [],
        )

    def test_a_machine_grove_dependency_pin_is_not_prose(self) -> None:
        self.assertEqual(
            CHECK_CONTENT.stale_version_prose(
                "package-graph.json",
                {
                    "packages": [
                        {
                            "dependencies": [
                                f"org.grovealliance.fhir.mobile#{RELEASE_VERSION}"
                            ]
                        }
                    ]
                },
                RELEASE_VERSION,
            ),
            [],
        )

    def test_the_manifest_schema_pins_the_release_the_graph_states(self) -> None:
        # The producer-manifest schema states the machine release metadata as a JSON Schema const,
        # so it must remain aligned with the package graph.
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
