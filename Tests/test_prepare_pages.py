"""Tests for deterministic GitHub Pages publication assembly."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "Scripts/prepare-pages.py"
SPECIFICATION = importlib.util.spec_from_file_location("prepare_pages", SCRIPT_PATH)
assert SPECIFICATION and SPECIFICATION.loader
PREPARE_PAGES = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(PREPARE_PAGES)
CHECK_SPECIFICATION = importlib.util.spec_from_file_location(
    "check_publication", ROOT / "Scripts/check-publication.py"
)
assert CHECK_SPECIFICATION and CHECK_SPECIFICATION.loader
CHECK_PUBLICATION = importlib.util.module_from_spec(CHECK_SPECIFICATION)
CHECK_SPECIFICATION.loader.exec_module(CHECK_PUBLICATION)


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
            {
                "platforms": "https://example.org/fhir/platforms/ci-build",
                "ig": "https://example.org/fhir/core/ci-build",
            },
            "https://github.com/example/repository/tree/revision",
        )

        self.assertEqual(
            result,
            "https://example.org/fhir/platforms/ci-build/CodeSystem-example.html "
            "https://example.org/fhir/core/ci-build/index.html",
        )

    def test_rewrites_package_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.tgz"
            first = Path(directory) / "first.tgz"
            second = Path(directory) / "second.tgz"
            self._write_package(
                original,
                {
                    "name": "example",
                    "version": "0.1.0",
                    "canonical": "https://example.org/fhir/example",
                    "url": "file:///tmp/output",
                    "date": "volatile",
                    "description": "Example package (built today)",
                    "title": "Example",
                    "fhirVersions": ["4.0.1"],
                },
            )
            shutil.copy2(original, first)
            shutil.copy2(original, second)

            for archive in (first, second):
                PREPARE_PAGES.rewrite_package_archive(
                    archive, "https://example.org/fhir/example", 1_700_000_000
                )

            self.assertEqual(first.read_bytes(), second.read_bytes())
            metadata = PREPARE_PAGES.read_package_metadata(first)
            self.assertEqual(metadata["url"], metadata["canonical"])
            self.assertEqual(metadata["date"], "20231114221320")
            self.assertEqual(metadata["description"], "Example package")

    def test_assembles_ci_only_publication_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            repository.mkdir()
            (repository / "tools").mkdir()
            shutil.copy2(
                ROOT / "tools/make-canonical-redirects.py",
                repository / "tools/make-canonical-redirects.py",
            )
            guides = (
                self._write_guide(
                    repository,
                    "ig",
                    "org.example.core",
                    "https://example.org/fhir/core",
                    "StructureDefinition",
                    "example-profile",
                ),
                self._write_guide(
                    repository,
                    "platforms",
                    "org.example.platforms",
                    "https://example.org/fhir/platforms",
                    "CodeSystem",
                    "example-codes",
                ),
            )
            configuration = {
                "schemaVersion": 1,
                "previewBaseUrl": "https://pages.example/repository",
                "sourceRepository": "https://github.com/example/repository",
                "guides": [
                    {
                        "source": guides[0][0],
                        "canonicalPath": "fhir/core",
                        "aliases": [""],
                        "representativeResource": "StructureDefinition/example-profile",
                    },
                    {
                        "source": guides[1][0],
                        "canonicalPath": "fhir/platforms",
                        "aliases": ["platforms"],
                        "representativeResource": "CodeSystem/example-codes",
                    },
                ],
                "retiredPreviewPaths": ["archive/legacy/"],
            }
            site = repository / ".build/pages"

            PREPARE_PAGES.assemble_site(
                site,
                repository,
                configuration,
                "https://pages.example/repository",
                "abc123",
                1_700_000_000,
            )

            self.assertEqual(
                CHECK_PUBLICATION.check_site(
                    site,
                    repository,
                    configuration,
                    "https://pages.example/repository",
                ),
                [],
            )

            core = site / "fhir/core"
            self.assertTrue((site / "index.html").is_file())
            self.assertTrue((site / "platforms/index.html").is_file())
            self.assertTrue((core / "ci-build/index.html").is_file())
            self.assertIn("ci-build/", (core / "index.html").read_text(encoding="utf-8"))
            history = json.loads((core / "package-list.json").read_text(encoding="utf-8"))
            self.assertEqual(history["package-id"], "org.example.core")
            self.assertEqual(history["list"], [
                {
                    "version": "current",
                    "desc": "Current build from the default branch.",
                    "path": "https://pages.example/repository/fhir/core/ci-build",
                    "status": "ci-build",
                    "fhirversion": "4.0.1",
                }
            ])
            self.assertIn(
                "The current entry tracks the latest build",
                (core / "history.html").read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (core / "StructureDefinition/example-profile/index.html").is_file()
            )
            self.assertTrue((core / "StructureDefinition/example-profile.json").is_file())
            self.assertFalse(
                (core / "StructureDefinition/example-profile/example-profile.json").exists()
            )
            checksum = (core / "package.tgz.sha256").read_text(encoding="utf-8").split()[0]
            self.assertEqual(checksum, hashlib.sha256((core / "package.tgz").read_bytes()).hexdigest())
            metadata = PREPARE_PAGES.read_package_metadata(core / "package.tgz")
            self.assertEqual(metadata["url"], metadata["canonical"])
            self.assertFalse((site / "archive/legacy").exists())
            self.assertNotIn(
                "Local Development build",
                (core / "ci-build/index.html").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "https://pages.example/repository/fhir/core/history.html",
                (core / "ci-build/index.html").read_text(encoding="utf-8"),
            )

    @staticmethod
    def _write_package(path: Path, metadata: dict[str, object]) -> None:
        with tarfile.open(path, "w:gz") as package:
            payload = (json.dumps(metadata) + "\n").encode()
            info = tarfile.TarInfo("package/package.json")
            info.size = len(payload)
            info.mtime = 99
            package.addfile(info, io.BytesIO(payload))

    def _write_guide(
        self,
        repository: Path,
        source: str,
        package_id: str,
        canonical: str,
        resource_type: str,
        resource_id: str,
    ) -> tuple[str, str]:
        output = repository / source / "output"
        output.mkdir(parents=True)
        (repository / source / "sushi-config.yaml").write_text(
            f"id: {package_id}\n"
            f"canonical: {canonical}\n"
            "version: 0.1.0\n"
            "fhirVersion: 4.0.1\n",
            encoding="utf-8",
        )
        history = f"{canonical}/history.html"
        local = output.resolve().as_uri()
        (output / "index.html").write_text(
            f"Local Development build <a href='{history}'>history</a> {local}",
            encoding="utf-8",
        )
        metadata = {
            "name": package_id,
            "version": "0.1.0",
            "canonical": canonical,
            "url": local,
            "date": "volatile",
            "description": f"{package_id} (built today)",
            "title": package_id,
            "fhirVersions": ["4.0.1"],
        }
        self._write_package(output / "package.tgz", metadata)
        resource = {
            "resourceType": resource_type,
            "id": resource_id,
            "url": f"{canonical}/{resource_type}/{resource_id}",
        }
        prefix = f"{resource_type}-{resource_id}"
        (output / f"{prefix}.json").write_text(json.dumps(resource), encoding="utf-8")
        (output / f"{prefix}.xml").write_text("<resource />", encoding="utf-8")
        (output / f"{prefix}.ttl").write_text("# resource", encoding="utf-8")
        (output / f"{prefix}.html").write_text("resource", encoding="utf-8")
        (output / "qa.json").write_bytes(
            b"\xef\xbb\xbf" + json.dumps({"url": f"{canonical}/ImplementationGuide/{package_id}"}).encode("utf-8")
        )
        return source, canonical


if __name__ == "__main__":
    unittest.main()
