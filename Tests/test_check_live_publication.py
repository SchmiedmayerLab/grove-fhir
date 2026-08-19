"""Tests for deployed publication smoke checks."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "Scripts/check-live-publication.py"
SPECIFICATION = importlib.util.spec_from_file_location("check_live_publication", SCRIPT)
assert SPECIFICATION and SPECIFICATION.loader
CHECK = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(CHECK)


class LivePublicationTests(unittest.TestCase):
    def test_verifies_aliases_metadata_checksum_and_canonical_resource(self) -> None:
        package = b"package"
        canonical = "https://grovealliance.org/fhir/core"
        configuration = {
            "guides": [
                {
                    "canonicalPath": "fhir/core",
                    "aliases": [""],
                    "representativeResource": "StructureDefinition/example",
                }
            ],
            "retiredPreviewPaths": ["archive/legacy/"],
        }
        calls: list[tuple[str, int]] = []

        def response(url: str, expected: int) -> bytes:
            calls.append((url, expected))
            if url.endswith("package-list.json"):
                return json.dumps(
                    {"canonical": canonical, "list": [{"status": "ci-build"}]}
                ).encode()
            if url.endswith("package.tgz"):
                return package
            if url.endswith("package.tgz.sha256"):
                return f"{hashlib.sha256(package).hexdigest()}  package.tgz\n".encode()
            if url.endswith("StructureDefinition/example.json"):
                return json.dumps(
                    {"url": f"{canonical}/StructureDefinition/example"}
                ).encode()
            return b""

        with mock.patch.object(CHECK, "expect_status", side_effect=response):
            CHECK.verify(
                "https://pages.example/repository/",
                configuration,
                canonical_only=False,
            )

        self.assertIn(("https://pages.example/repository/", 200), calls)
        self.assertIn(("https://pages.example/repository/archive/legacy/", 404), calls)
        self.assertIn(
            (
                "https://pages.example/repository/fhir/core/StructureDefinition/example.json",
                200,
            ),
            calls,
        )


if __name__ == "__main__":
    unittest.main()
