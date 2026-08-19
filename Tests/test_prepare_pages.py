"""Tests for the GitHub Pages publication cleanup."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "Scripts" / "prepare-pages.py"
SPECIFICATION = importlib.util.spec_from_file_location("prepare_pages", SCRIPT_PATH)
assert SPECIFICATION and SPECIFICATION.loader
PREPARE_PAGES = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(PREPARE_PAGES)


class PreparePagesTests(unittest.TestCase):
    def test_rewrites_build_locations(self) -> None:
        repository = Path("/private/tmp/grove-fhir")
        text = (
            "file:///private/tmp/grove-fhir/platforms/output/CodeSystem-example.html "
            "/private/tmp/grove-fhir/ig/output/index.html"
        )

        result = PREPARE_PAGES.replace_build_locations(
            text,
            repository,
            "https://example.org/grove-fhir",
        )

        self.assertEqual(
            result,
            "https://example.org/grove-fhir/platforms/CodeSystem-example.html "
            "https://example.org/grove-fhir/index.html",
        )

    def test_rewrites_package_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "package.tgz"
            with tarfile.open(archive, "w:gz") as package:
                payload = json.dumps({"name": "example", "url": "file:///tmp/output"}).encode()
                info = tarfile.TarInfo("package/package.json")
                info.size = len(payload)
                package.addfile(info, io.BytesIO(payload))

            PREPARE_PAGES.rewrite_package_archive(archive, "https://example.org/guide")

            with tarfile.open(archive, "r:gz") as package:
                package_file = package.extractfile("package/package.json")
                assert package_file is not None
                metadata = json.load(package_file)
            self.assertEqual(metadata["url"], "https://example.org/guide")

    def test_rewrites_provisional_publication_links(self) -> None:
        repository = Path("/private/tmp/grove-fhir")
        text = (
            "Local Development build; "
            "https://grovealliance.org/fhir/core/history.html; "
            "https://grovealliance.org/fhir/platforms/history.html"
        )

        result = PREPARE_PAGES.replace_build_locations(
            text,
            repository,
            "https://example.org/grove-fhir",
        )

        self.assertEqual(
            result,
            "Continuous preview build; "
            "https://github.com/SchmiedmayerLab/grove-fhir/releases; "
            "https://github.com/SchmiedmayerLab/grove-fhir/releases",
        )


if __name__ == "__main__":
    unittest.main()
