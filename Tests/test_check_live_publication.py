"""Tests for deployed publication smoke checks."""

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
import tarfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "Scripts/check-live-publication.py"
SPECIFICATION = importlib.util.spec_from_file_location("check_live_publication", SCRIPT)
assert SPECIFICATION and SPECIFICATION.loader
CHECK = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(CHECK)


class LivePublicationTests(unittest.TestCase):
    @staticmethod
    def package(canonical: str) -> bytes:
        payload = json.dumps(
            {
                "name": "org.example.mobile",
                "version": "0.1.0",
                "canonical": canonical,
            }
        ).encode()
        package = io.BytesIO()
        with tarfile.open(fileobj=package, mode="w:gz") as archive:
            entry = tarfile.TarInfo("package/package.json")
            entry.size = len(payload)
            archive.addfile(entry, io.BytesIO(payload))
        return package.getvalue()

    @staticmethod
    def configuration() -> dict[str, object]:
        return {
            "canonicalBaseUrl": "https://pages.example/repository",
            "releaseMode": "ci-build-only",
            "guides": [
                {
                    "canonicalPath": "fhir/mobile",
                    "aliases": [""],
                    "representativeResource": "StructureDefinition/example",
                }
            ],
            "retiredPreviewPaths": ["archive/legacy/"],
        }

    def responses(
        self,
        *,
        source_revision: str = "abc123",
        manifest_canonical: str = "https://pages.example/repository/fhir/mobile",
        retain_release: bool = False,
    ) -> tuple[list[tuple[str, int]], Callable[[str, int], bytes]]:
        canonical = "https://pages.example/repository/fhir/mobile"
        package = self.package(canonical)
        package_digest = hashlib.sha256(package).hexdigest()
        calls: list[tuple[str, int]] = []

        def response(url: str, expected: int) -> bytes:
            calls.append((url, expected))
            if url.endswith("package-list.json"):
                entries = [
                    {
                        "version": "current",
                        "status": "ci-build",
                        "path": "https://pages.example/repository/fhir/mobile/ci-build",
                    }
                ]
                if retain_release:
                    entries.append(
                        {
                            "version": "0.0.1",
                            "status": "draft",
                            "path": "https://pages.example/repository/fhir/mobile/0.0.1",
                        }
                    )
                return json.dumps(
                    {
                        "package-id": "org.example.mobile",
                        "canonical": canonical,
                        "list": entries,
                    }
                ).encode()
            if url.endswith("publication-manifest.json"):
                revision = source_revision if "/ci-build/" in url else "released123"
                return json.dumps(
                    {
                        "packageId": "org.example.mobile",
                        "packageVersion": "0.1.0",
                        "canonical": manifest_canonical,
                        "sourceRevision": revision,
                        "packageSha256": package_digest,
                    }
                ).encode()
            if url.endswith("package.tgz"):
                return package
            if url.endswith("package.tgz.sha256"):
                return f"{package_digest}  package.tgz\n".encode()
            if url.endswith("StructureDefinition/example.json"):
                return json.dumps(
                    {"url": f"{canonical}/StructureDefinition/example"}
                ).encode()
            return b""

        return calls, response

    def test_verifies_aliases_metadata_checksum_and_canonical_resource(self) -> None:
        calls, response = self.responses()

        with mock.patch.object(CHECK, "expect_status", side_effect=response):
            CHECK.verify(
                "https://pages.example/repository/",
                self.configuration(),
                canonical_only=False,
                expected_revision="abc123",
            )

        self.assertIn(("https://pages.example/repository/", 200), calls)
        self.assertIn(("https://pages.example/repository/archive/legacy/", 404), calls)
        self.assertIn(
            (
                "https://pages.example/repository/fhir/mobile/StructureDefinition/example.json",
                200,
            ),
            calls,
        )
        self.assertIn(
            (
                "https://pages.example/repository/fhir/mobile/ci-build/"
                "publication-manifest.json",
                200,
            ),
            calls,
        )

    def test_rejects_a_stale_ci_build_revision(self) -> None:
        _, response = self.responses(source_revision="previous")

        with mock.patch.object(CHECK, "expect_status", side_effect=response):
            with self.assertRaisesRegex(RuntimeError, "sourceRevision='previous'"):
                CHECK.verify(
                    "https://pages.example/repository/",
                    self.configuration(),
                    canonical_only=True,
                    expected_revision="abc123",
                )

    def test_rejects_manifest_canonical_host_drift(self) -> None:
        _, response = self.responses(manifest_canonical="https://example.org/fhir/mobile")

        with mock.patch.object(CHECK, "expect_status", side_effect=response):
            with self.assertRaisesRegex(RuntimeError, "canonical=.*example.org"):
                CHECK.verify(
                    "https://pages.example/repository/",
                    self.configuration(),
                    canonical_only=True,
                    expected_revision="abc123",
                )

    def test_rejects_retained_releases_in_ci_build_only_mode(self) -> None:
        _, response = self.responses(retain_release=True)

        with mock.patch.object(CHECK, "expect_status", side_effect=response):
            with self.assertRaisesRegex(RuntimeError, "does not describe a CI build"):
                CHECK.verify(
                    "https://pages.example/repository/",
                    self.configuration(),
                    canonical_only=True,
                    expected_revision="abc123",
                )

    def test_canonical_base_accepts_a_safe_github_pages_path(self) -> None:
        self.assertEqual(
            CHECK.canonical_for_guide(
                {"canonicalBaseUrl": "https://pages.example/repository/"},
                {"canonicalPath": "fhir/mobile"},
            ),
            "https://pages.example/repository/fhir/mobile",
        )

    def test_canonical_base_rejects_unsafe_urls(self) -> None:
        unsafe = (
            "http://pages.example/repository",
            "https://user@pages.example/repository",
            "https://pages.example/repository//nested",
            "https://pages.example/repository/../other",
            "https://pages.example/repository%2Fnested",
            "https://pages.example/repository?preview=true",
            "https://pages.example/repository#preview",
        )
        for base_url in unsafe:
            with self.subTest(base_url=base_url):
                with self.assertRaises(RuntimeError):
                    CHECK.canonical_for_guide(
                        {"canonicalBaseUrl": base_url},
                        {"canonicalPath": "fhir/mobile"},
                    )


if __name__ == "__main__":
    unittest.main()
