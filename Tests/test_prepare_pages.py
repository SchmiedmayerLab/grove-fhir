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

from Scripts import fhir_package_semantic_snapshot as SNAPSHOT


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
    def test_configuration_rejects_alias_and_canonical_path_collisions(self) -> None:
        configuration = {
            "schemaVersion": 0,
            "releaseMode": "ci-build-only",
            "guides": [
                {
                    "source": "sensor",
                    "canonicalPath": "sensor",
                    "aliases": ["sensor"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(configuration), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "collides with canonicalPath"):
                PREPARE_PAGES.load_configuration(path)

    def test_rewrites_build_locations(self) -> None:
        repository = Path("/private/tmp/grove-fhir")
        text = (
            "file:///private/tmp/grove-fhir/healthkit/output/CodeSystem-example.html "
            "/private/tmp/grove-fhir/mobile/output/index.html"
        )

        result = PREPARE_PAGES.replace_build_locations(
            text,
            repository,
            {
                "healthkit": "https://example.org/grove-fhir/fhir/healthkit/ci-build",
                "mobile": "https://example.org/grove-fhir/fhir/mobile/ci-build",
            },
            "https://github.com/example/repository/tree/revision",
        )

        self.assertEqual(
            result,
            "https://example.org/grove-fhir/fhir/healthkit/ci-build/CodeSystem-example.html "
            "https://example.org/grove-fhir/fhir/mobile/ci-build/index.html",
        )

    def test_rewrites_authored_canonical_links(self) -> None:
        mapping = {
            "https://canonical.example/fhir/mobile": "https://pages.example/repo/mobile/ci-build",
            "https://canonical.example/fhir/mobile/history.html": (
                "https://pages.example/repo/mobile/history.html"
            ),
            "https://canonical.example/fhir/sensorkit": "https://pages.example/repo/sensorkit/ci-build",
            "https://canonical.example/fhir/sensor": "https://pages.example/repo/sensor/ci-build",
            "https://canonical.example/fhir/catalog/": "https://pages.example/repo/catalog/",
        }
        text = (
            '<a href="https://canonical.example/fhir/mobile/study.html">study</a>'
            " <a href='https://canonical.example/fhir/mobile/history.html'>history</a>"
            ' <a href="https://canonical.example/fhir/sensorkit/mapping.html">adapter</a>'
            ' <a href="https://canonical.example/fhir/sensor/waveforms.html">sensor</a>'
            ' <a href="https://canonical.example/fhir/catalog/measurement-catalog.json">catalog</a>'
            ' "url": "https://canonical.example/fhir/mobile/StructureDefinition/profile"'
        )
        result = PREPARE_PAGES.rewrite_authored_canonical_links(text, mapping)
        self.assertIn('href="https://pages.example/repo/mobile/ci-build/study.html"', result)
        self.assertIn("href='https://pages.example/repo/mobile/history.html'", result)
        self.assertIn('href="https://pages.example/repo/sensorkit/ci-build/mapping.html"', result)
        self.assertIn('href="https://pages.example/repo/sensor/ci-build/waveforms.html"', result)
        self.assertIn('href="https://pages.example/repo/catalog/measurement-catalog.json"', result)
        # Resource identity is never a link target and stays canonical.
        self.assertIn('"url": "https://canonical.example/fhir/mobile/StructureDefinition/profile"', result)

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
                {
                    "package/example/Observation-example.json": json.dumps(
                        {
                            "resourceType": "Observation",
                            "id": "example",
                            "text": {
                                "status": "generated",
                                "div": (
                                    '<div xmlns="http://www.w3.org/1999/xhtml">'
                                    '<a href="file:///private/tmp/grove-fhir/mobile/output/'
                                    'StructureDefinition-example.html">profile</a></div>'
                                ),
                            },
                        }
                    ).encode(),
                },
            )
            shutil.copy2(original, first)
            shutil.copy2(original, second)

            for archive in (first, second):
                PREPARE_PAGES.rewrite_package_archive(
                    archive,
                    "https://example.org/fhir/example",
                    1_700_000_000,
                    repository_root=Path("/private/tmp/grove-fhir"),
                    public_urls={
                        "mobile": "https://example.org/grove-fhir/fhir/mobile/ci-build"
                    },
                    source_url="https://github.com/example/repository/tree/revision",
                )

            self.assertEqual(first.read_bytes(), second.read_bytes())
            header = first.read_bytes()[:10]
            self.assertEqual(
                header,
                b"\x1f\x8b\x08\x00"
                + (1_700_000_000).to_bytes(4, "little")
                + b"\x02\xff",
            )
            metadata = PREPARE_PAGES.read_package_metadata(first)
            self.assertEqual(metadata["url"], metadata["canonical"])
            self.assertEqual(metadata["date"], "20231114221320")
            self.assertEqual(metadata["description"], "Example package")
            with tarfile.open(first, "r:gz") as package:
                names = [member.name for member in package.getmembers()]
                self.assertEqual(names, sorted(names))
                self.assertEqual(len(names), len(set(names)))
                for member in package.getmembers():
                    self.assertEqual(member.mtime, 1_700_000_000)
                    self.assertEqual(member.uid, 0)
                    self.assertEqual(member.gid, 0)
                    self.assertEqual(member.uname, "")
                    self.assertEqual(member.gname, "")
                    self.assertEqual(member.pax_headers, {})
                    self.assertEqual(member.linkname, "")
                    self.assertEqual(member.devmajor, 0)
                    self.assertEqual(member.devminor, 0)
                    self.assertEqual(member.mode, 0o755 if member.isdir() else 0o644)
                example_file = package.extractfile(
                    "package/example/Observation-example.json"
                )
                self.assertIsNotNone(example_file)
                example = json.load(example_file)
            self.assertEqual(
                example["text"]["div"],
                '<div xmlns="http://www.w3.org/1999/xhtml">'
                '<a href="https://example.org/grove-fhir/fhir/mobile/ci-build/'
                'StructureDefinition-example.html">profile</a></div>',
            )

    def test_publisher_dates_do_not_change_the_sanitized_semantic_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archives: list[Path] = []
            for name, package_date, resource_date in (
                (
                    "first",
                    "20260819110517",
                    "2026-08-19T11:05:17-07:00",
                ),
                (
                    "second",
                    "20260820200618",
                    "2026-08-20T20:06:18+02:00",
                ),
            ):
                archive = root / f"{name}.tgz"
                generated = {
                    "resourceType": "CodeSystem",
                    "id": "generated",
                    "url": "https://example.org/fhir/CodeSystem/generated",
                    "status": "active",
                    "content": "complete",
                    "date": resource_date,
                }
                authored = {
                    "resourceType": "PlanDefinition",
                    "id": "authored",
                    "url": "https://example.org/fhir/PlanDefinition/authored",
                    "status": "active",
                    "date": "2025-01-02T03:04:05Z",
                }
                index = {
                    "index-version": 2,
                    "files": [
                        {
                            "filename": "CodeSystem-generated.json",
                            "resourceType": "CodeSystem",
                            "id": "generated",
                            "url": generated["url"],
                        },
                        {
                            "filename": "PlanDefinition-authored.json",
                            "resourceType": "PlanDefinition",
                            "id": "authored",
                            "url": authored["url"],
                        },
                    ],
                }
                internals = {
                    "npm-name": "org.example.fhir",
                    "date": (
                        f"{package_date[:4]}-{package_date[4:6]}-{package_date[6:8]}"
                    ),
                    "date-time": (
                        f"{package_date[:8]}"
                        f"{int(package_date[8:10]) % 12 or 12:02d}"
                        f"{package_date[10:]}-0700"
                    ),
                }
                self._write_package(
                    archive,
                    {
                        "name": "org.example.fhir",
                        "version": "0.1.0",
                        "canonical": "https://example.org/fhir",
                        "url": "file:///tmp/output",
                        "date": package_date,
                        "description": "Example package (built today)",
                        "fhirVersions": ["4.0.1"],
                        "dependencies": {},
                    },
                    {
                        "package/.index.json": json.dumps(index).encode(),
                        "package/CodeSystem-generated.json": json.dumps(
                            generated
                        ).encode(),
                        "package/PlanDefinition-authored.json": json.dumps(
                            authored
                        ).encode(),
                        "package/other/spec.internals": json.dumps(
                            internals
                        ).encode(),
                    },
                )
                PREPARE_PAGES.rewrite_package_archive(
                    archive,
                    "https://example.org/fhir",
                    1_700_000_000,
                    repository_root=root,
                    public_urls={},
                    source_url="https://github.com/example/repository/tree/revision",
                )
                archives.append(archive)

            self.assertEqual(archives[0].read_bytes(), archives[1].read_bytes())
            first = SNAPSHOT.create_snapshot(archives[0])
            second = SNAPSHOT.create_snapshot(archives[1])
            self.assertEqual(first, second)
            generated_resource = first["codeSystems"][
                "https://example.org/fhir/CodeSystem/generated"
            ]["resource"]
            authored_resource = first["otherConformance"][
                "https://example.org/fhir/PlanDefinition/authored"
            ]["resource"]
            self.assertNotIn("date", generated_resource)
            self.assertEqual(authored_resource["date"], "2025-01-02T03:04:05Z")
            with tarfile.open(archives[0], "r:gz") as package:
                internals_file = package.extractfile("package/other/spec.internals")
                self.assertIsNotNone(internals_file)
                normalized_internals = json.load(internals_file)
            self.assertEqual(normalized_internals["date"], "2023-11-14")
            self.assertEqual(
                normalized_internals["date-time"], "20231114221320+0000"
            )

    def test_publisher_internals_rejects_an_unrelated_clock(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "spec.internals build timestamp is inconsistent"
        ):
            PREPARE_PAGES.normalize_publisher_internals(
                json.dumps(
                    {
                        "date": "2026-08-19",
                        "date-time": "20260819081640+0000",
                    }
                ),
                "20260819201639",
                1_700_000_000,
            )

    def test_publisher_internals_rejects_invalid_clock_data(self) -> None:
        cases = (
            (
                "20269919201639",
                {
                    "date": "2026-99-19",
                    "date-time": "20269919081639+0000",
                },
            ),
            (
                "20260819201639",
                {
                    "date": "2026-08-19",
                    "date-time": "20260819081639+9999",
                },
            ),
        )
        for package_date, internals in cases:
            with self.subTest(package_date=package_date, internals=internals):
                with self.assertRaisesRegex(
                    ValueError, "spec.internals build timestamp is inconsistent"
                ):
                    PREPARE_PAGES.normalize_publisher_internals(
                        json.dumps(internals), package_date, 1_700_000_000
                    )

    def test_package_sanitization_rejects_escaped_ansi_without_url_false_positive(self) -> None:
        PREPARE_PAGES.validate_portable_text(
            json.dumps({"url": "https://example.org/home/runner/reference"}),
            "safe URL",
            ".json",
        )
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "ansi.tgz"
            self._write_package(
                archive,
                {
                    "name": "example",
                    "version": "0.1.0",
                    "canonical": "https://example.org/fhir/example",
                    "url": "https://example.org/fhir/example",
                    "date": "volatile",
                    "description": "Example package",
                    "title": "Example",
                    "fhirVersions": ["4.0.1"],
                },
                {
                    "package/example/Observation-example.json": json.dumps(
                        {
                            "resourceType": "Observation",
                            "note": [{"text": "\x1b[31mvalidator output\x1b[0m"}],
                        }
                    ).encode("utf-8")
                },
            )
            with self.assertRaisesRegex(ValueError, "ANSI"):
                PREPARE_PAGES.rewrite_package_archive(
                    archive,
                    "https://example.org/fhir/example",
                    1_700_000_000,
                    repository_root=Path(directory),
                    public_urls={},
                    source_url="https://github.com/example/repository/tree/revision",
                )

    def test_site_output_symlink_is_rejected_before_recursive_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            (repository / ".build").mkdir(parents=True)
            victim = repository / "guide-source"
            victim.mkdir()
            sentinel = victim / "sentinel.txt"
            sentinel.write_text("do not delete\n", encoding="utf-8")
            site = repository / ".build/pages"
            site.symlink_to(victim, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "symlink"):
                PREPARE_PAGES.assemble_site(
                    site,
                    repository,
                    {},
                    "https://example.org/grove-fhir",
                    "1" * 40,
                    1_700_000_000,
                )
            self.assertEqual(
                sentinel.read_text(encoding="utf-8"), "do not delete\n"
            )

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
                    "mobile",
                    "org.example.mobile",
                    "https://pages.example/repository/fhir/mobile",
                    "StructureDefinition",
                    "example-profile",
                ),
                self._write_guide(
                    repository,
                    "healthkit",
                    "org.example.healthkit",
                    "https://pages.example/repository/fhir/healthkit",
                    "CodeSystem",
                    "example-codes",
                ),
            )
            configuration = {
                "schemaVersion": 0,
                "previewBaseUrl": "https://pages.example/repository",
                "canonicalBaseUrl": "https://pages.example/repository",
                "sourceRepository": "https://github.com/example/repository",
                "releaseMode": "ci-build-only",
                "guides": [
                    {
                        "source": guides[0][0],
                        "canonicalPath": "fhir/mobile",
                        "aliases": [""],
                        "representativeResource": "StructureDefinition/example-profile",
                    },
                    {
                        "source": guides[1][0],
                        "canonicalPath": "fhir/healthkit",
                        "aliases": ["healthkit"],
                        "representativeResource": "CodeSystem/example-codes",
                    },
                ],
                "retiredPreviewPaths": ["fhir/core/", "fhir/platforms/", "platforms/"],
            }
            (repository / "catalog").mkdir()
            (repository / "catalog/example-catalog.json").write_text(
                "{}", encoding="utf-8"
            )
            site = repository / ".build/pages"
            published = Path(directory) / "published"
            (published / "fhir/core/0.5.0").mkdir(parents=True)
            (published / "fhir/core/0.5.0/index.html").write_text(
                "retired release", encoding="utf-8"
            )
            (published / "fhir/platforms/0.1.0").mkdir(parents=True)
            (published / "fhir/platforms/0.1.0/index.html").write_text(
                "retired release", encoding="utf-8"
            )
            (published / "fhir/mobile/0.0.1").mkdir(parents=True)
            (published / "fhir/mobile/0.0.1/index.html").write_text(
                "unreleased pre-1.0 build", encoding="utf-8"
            )

            PREPARE_PAGES.assemble_site(
                site,
                repository,
                configuration,
                "https://pages.example/repository",
                "abc123",
                1_700_000_000,
                published,
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

            mobile = site / "fhir/mobile"
            self.assertTrue((site / ".nojekyll").is_file())
            self.assertTrue((site / "catalog/example-catalog.json").is_file())
            self.assertTrue((site / "index.html").is_file())
            self.assertTrue((site / "healthkit/index.html").is_file())
            self.assertTrue((mobile / "ci-build/index.html").is_file())
            self.assertTrue((mobile / "ci-build/package.tgz.sha256").is_file())
            preview_manifest = json.loads(
                (mobile / "ci-build/publication-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(preview_manifest["sourceRevision"], "abc123")
            self.assertEqual(
                preview_manifest["canonical"],
                "https://pages.example/repository/fhir/mobile",
            )
            self.assertIn("ci-build/", (mobile / "index.html").read_text(encoding="utf-8"))
            history = json.loads((mobile / "package-list.json").read_text(encoding="utf-8"))
            self.assertEqual(history["package-id"], "org.example.mobile")
            self.assertEqual(history["list"], [
                {
                    "version": "current",
                    "desc": "Current build from the default branch.",
                    "path": "https://pages.example/repository/fhir/mobile/ci-build",
                    "status": "ci-build",
                    "fhirversion": "4.0.1",
                }
            ])
            self.assertIn(
                "The current entry tracks the latest build",
                (mobile / "history.html").read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (mobile / "StructureDefinition/example-profile/index.html").is_file()
            )
            self.assertTrue((mobile / "StructureDefinition/example-profile.json").is_file())
            self.assertFalse(
                (mobile / "StructureDefinition/example-profile/example-profile.json").exists()
            )
            checksum = (mobile / "package.tgz.sha256").read_text(encoding="utf-8").split()[0]
            self.assertEqual(
                checksum,
                hashlib.sha256((mobile / "package.tgz").read_bytes()).hexdigest(),
            )
            metadata = PREPARE_PAGES.read_package_metadata(mobile / "package.tgz")
            self.assertEqual(metadata["url"], metadata["canonical"])
            self.assertFalse((site / "fhir/core").exists())
            self.assertFalse((site / "fhir/platforms").exists())
            self.assertFalse((site / "fhir/mobile/0.0.1").exists())
            self.assertNotIn(
                "Local Development build",
                (mobile / "ci-build/index.html").read_text(encoding="utf-8"),
            )
            self.assertFalse((mobile / "ci-build/package.db").exists())
            icon = (mobile / "ci-build/assets/images/001.svg").read_text(
                encoding="utf-8"
            )
            self.assertIn('inkscape:export-filename="Globe Flag.png"', icon)
            self.assertNotIn(r"C:\Users", icon)
            self.assertIn(
                "https://pages.example/repository/fhir/mobile/history.html",
                (mobile / "ci-build/index.html").read_text(encoding="utf-8"),
            )

    def test_local_validation_rejects_canonical_origin_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            repository.mkdir()
            (repository / "tools").mkdir()
            shutil.copy2(
                ROOT / "tools/make-canonical-redirects.py",
                repository / "tools/make-canonical-redirects.py",
            )
            self._write_guide(
                repository,
                "mobile",
                "org.example.mobile",
                "https://other.example/fhir/mobile",
                "StructureDefinition",
                "example-profile",
            )
            configuration = {
                "schemaVersion": 0,
                "previewBaseUrl": "https://pages.example/repository",
                "canonicalBaseUrl": "https://pages.example/repository",
                "sourceRepository": "https://github.com/example/repository",
                "releaseMode": "ci-build-only",
                "guides": [
                    {
                        "source": "mobile",
                        "canonicalPath": "fhir/mobile",
                        "aliases": [""],
                        "representativeResource": "StructureDefinition/example-profile",
                    }
                ],
            }
            site = repository / ".build/pages"
            with self.assertRaisesRegex(ValueError, "does not match configured canonical"):
                PREPARE_PAGES.assemble_site(
                    site,
                    repository,
                    configuration,
                    "https://pages.example/repository",
                    "abc123",
                    1_700_000_000,
                )

    def test_local_validation_rejects_non_https_canonical_origin(self) -> None:
        failures = CHECK_PUBLICATION.check_site(
            Path("/unused"),
            Path("/unused"),
            {
                "canonicalBaseUrl": "http://example.org",
                "releaseMode": "ci-build-only",
                "guides": [{"source": "mobile", "canonicalPath": "fhir/mobile"}],
            },
            "https://pages.example/repository",
        )

        self.assertEqual(
            failures,
            [
                "invalid publication configuration: canonicalBaseUrl must be an HTTPS URL "
                "without credentials, an unsafe path, query, or fragment"
            ],
        )

    def test_canonical_base_accepts_a_safe_github_pages_path(self) -> None:
        self.assertEqual(
            CHECK_PUBLICATION.canonical_for_guide(
                {"canonicalBaseUrl": "https://pages.example/grove-fhir/"},
                {"canonicalPath": "fhir/mobile"},
            ),
            "https://pages.example/grove-fhir/fhir/mobile",
        )

    def test_canonical_base_rejects_unsafe_urls(self) -> None:
        unsafe = (
            "http://pages.example/grove-fhir",
            "https://user@pages.example/grove-fhir",
            "https://pages.example/grove-fhir//nested",
            "https://pages.example/grove-fhir/../other",
            "https://pages.example/grove%2Dfhir",
            "https://pages.example/grove-fhir?preview=true",
            "https://pages.example/grove-fhir#preview",
        )
        for base_url in unsafe:
            with self.subTest(base_url=base_url):
                with self.assertRaises(ValueError):
                    CHECK_PUBLICATION.canonical_for_guide(
                        {"canonicalBaseUrl": base_url},
                        {"canonicalPath": "fhir/mobile"},
                    )

    @staticmethod
    def _write_package(
        path: Path,
        metadata: dict[str, object],
        extra_files: dict[str, bytes] | None = None,
    ) -> None:
        with tarfile.open(path, "w:gz") as package:
            payload = (json.dumps(metadata) + "\n").encode()
            info = tarfile.TarInfo("package/package.json")
            info.size = len(payload)
            info.mtime = 99
            package.addfile(info, io.BytesIO(payload))
            for name, contents in sorted((extra_files or {}).items()):
                info = tarfile.TarInfo(name)
                info.size = len(contents)
                info.mtime = 99
                package.addfile(info, io.BytesIO(contents))

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
        (output / "package.db").write_text(
            f"file://{output}/package-cache", encoding="utf-8"
        )
        icon = output / "assets/images/001.svg"
        icon.parent.mkdir(parents=True)
        icon.write_text(
            '<svg inkscape:export-filename="C:\\Users\\Philip\\Desktop\\Globe Flag.png" />',
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
