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
