"""Tests for immutable FHIR version promotion."""

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
from unittest import mock


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "Scripts/publish-version.py"
SPECIFICATION = importlib.util.spec_from_file_location("publish_version", SCRIPT)
assert SPECIFICATION and SPECIFICATION.loader
PUBLISH = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(PUBLISH)


class PublishVersionTests(unittest.TestCase):
    canonical = "https://example.org/fhir/core"
    configuration = {
        "canonicalBaseUrl": "https://example.org",
        "guides": [
            {
                "source": "ig",
                "canonicalPath": "fhir/core",
                "aliases": [""],
                "representativeResource": "StructureDefinition/example",
            }
        ]
    }

    def test_publishes_once_and_updates_current_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            site = root / "published"
            self._write_output(source)

            version = PUBLISH.publish_version(
                site=site,
                source=source,
                configuration=self.configuration,
                guide_source="ig",
                status="preview",
                sequence="0.x Preview",
                publication_date="2026-08-18",
                description="First reviewed preview.",
                current=True,
                revision="abc123",
                repository_root=ROOT,
            )

            self.assertEqual(version, "0.1.0-preview.1")
            publication = site / "fhir/core"
            immutable = publication / version
            self.assertTrue((immutable / "index.html").is_file())
            self.assertTrue((immutable / "package.tgz.sha256").is_file())
            self.assertTrue((publication / "StructureDefinition/example.json").is_file())
            self.assertIn(version, (publication / "index.html").read_text(encoding="utf-8"))
            history = json.loads((publication / "package-list.json").read_text(encoding="utf-8"))
            self.assertEqual(history["list"][0]["version"], version)
            self.assertTrue(history["list"][0]["current"])
            self.assertEqual(
                history["list"][0]["path"], f"{self.canonical}/{version}"
            )
            before = (immutable / "package.tgz").read_bytes()

            with self.assertRaises(FileExistsError):
                PUBLISH.publish_version(
                    site=site,
                    source=source,
                    configuration=self.configuration,
                    guide_source="ig",
                    status="preview",
                    sequence="0.x Preview",
                    publication_date="2026-08-18",
                    description="Attempted overwrite.",
                    current=True,
                    revision="def456",
                    repository_root=ROOT,
                )
            self.assertEqual(before, (immutable / "package.tgz").read_bytes())

    def test_rejects_non_publication_build_without_mutating_site(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            site = root / "published"
            self._write_output(source, not_for_publication=True)

            with self.assertRaisesRegex(ValueError, "publication mode"):
                PUBLISH.publish_version(
                    site=site,
                    source=source,
                    configuration=self.configuration,
                    guide_source="ig",
                    status="preview",
                    sequence="0.x Preview",
                    publication_date="2026-08-18",
                    description="Not publishable.",
                    current=True,
                    revision="abc123",
                    repository_root=ROOT,
                )
            self.assertFalse((site / "fhir/core/0.1.0-preview.1").exists())

    def test_rejects_a_package_from_another_canonical_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            site = root / "published"
            self._write_output(
                source,
                canonical="https://other.example/fhir/core",
            )

            with self.assertRaisesRegex(ValueError, "configured canonical"):
                PUBLISH.publish_version(
                    site=site,
                    source=source,
                    configuration=self.configuration,
                    guide_source="ig",
                    status="preview",
                    sequence="0.x Preview",
                    publication_date="2026-08-18",
                    description="Wrong canonical origin.",
                    current=True,
                    revision="abc123",
                    repository_root=ROOT,
                )
            self.assertFalse(site.exists())

    def test_failure_after_staging_leaves_existing_publication_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_source = root / "first-source"
            second_source = root / "second-source"
            site = root / "published"
            self._write_output(first_source)
            PUBLISH.publish_version(
                site=site,
                source=first_source,
                configuration=self.configuration,
                guide_source="ig",
                status="preview",
                sequence="0.x Preview",
                publication_date="2026-08-18",
                description="First reviewed preview.",
                current=True,
                revision="abc123",
                repository_root=ROOT,
            )
            publication = site / "fhir/core"
            before = {
                str(path.relative_to(publication)): path.read_bytes()
                for path in publication.rglob("*")
                if path.is_file()
            }
            self._write_output(second_source, version="0.1.0-preview.2")

            with mock.patch.object(
                PUBLISH, "release_redirect", side_effect=RuntimeError("injected failure")
            ):
                with self.assertRaisesRegex(RuntimeError, "injected failure"):
                    PUBLISH.publish_version(
                        site=site,
                        source=second_source,
                        configuration=self.configuration,
                        guide_source="ig",
                        status="preview",
                        sequence="0.x Preview",
                        publication_date="2026-08-19",
                        description="Second reviewed preview.",
                        current=True,
                        revision="def456",
                        repository_root=ROOT,
                    )

            after = {
                str(path.relative_to(publication)): path.read_bytes()
                for path in publication.rglob("*")
                if path.is_file()
            }
            self.assertEqual(after, before)
            self.assertFalse((publication / "0.1.0-preview.2").exists())
            self.assertEqual(
                list((site / "fhir").glob(".core.*.tmp")),
                [],
            )

    def _write_output(
        self,
        output: Path,
        *,
        not_for_publication: bool = False,
        version: str = "0.1.0-preview.1",
        canonical: str | None = None,
    ) -> None:
        output.mkdir()
        canonical = canonical or self.canonical
        metadata = {
            "name": "org.example.core",
            "version": version,
            "canonical": canonical,
            "url": f"{canonical}/{version}",
            "notForPublication": not_for_publication,
            "title": "Example Core",
            "description": "Example release",
            "fhirVersions": ["4.0.1"],
        }
        with tarfile.open(output / "package.tgz", "w:gz") as package:
            payload = (json.dumps(metadata) + "\n").encode()
            info = tarfile.TarInfo("package/package.json")
            info.size = len(payload)
            package.addfile(info, io.BytesIO(payload))
        (output / "index.html").write_text("release", encoding="utf-8")
        resource = {
            "resourceType": "StructureDefinition",
            "id": "example",
            "url": f"{canonical}/StructureDefinition/example",
        }
        prefix = "StructureDefinition-example"
        (output / f"{prefix}.json").write_text(json.dumps(resource), encoding="utf-8")
        (output / f"{prefix}.xml").write_text("<StructureDefinition/>", encoding="utf-8")
        (output / f"{prefix}.ttl").write_text("# definition", encoding="utf-8")
        (output / f"{prefix}.html").write_text("definition", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
