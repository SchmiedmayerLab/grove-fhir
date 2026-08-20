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
                "name": "org.example.core",
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
            "canonicalBaseUrl": "https://grovealliance.org",
            "guides": [
                {
                    "canonicalPath": "fhir/core",
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
        manifest_canonical: str = "https://grovealliance.org/fhir/core",
    ) -> tuple[list[tuple[str, int]], Callable[[str, int], bytes]]:
        canonical = "https://grovealliance.org/fhir/core"
        package = self.package(canonical)
        package_digest = hashlib.sha256(package).hexdigest()
        calls: list[tuple[str, int]] = []

        def response(url: str, expected: int) -> bytes:
            calls.append((url, expected))
            if url.endswith("package-list.json"):
                return json.dumps(
                    {
                        "package-id": "org.example.core",
                        "canonical": canonical,
                        "list": [
                            {
                                "version": "current",
                                "status": "ci-build",
                                "path": "https://pages.example/repository/fhir/core/ci-build",
                            }
                        ],
                    }
                ).encode()
            if url.endswith("publication-manifest.json"):
                revision = source_revision if "/ci-build/" in url else "released123"
                return json.dumps(
                    {
                        "packageId": "org.example.core",
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
                "https://pages.example/repository/fhir/core/StructureDefinition/example.json",
                200,
            ),
            calls,
        )
        self.assertIn(
            (
                "https://pages.example/repository/fhir/core/ci-build/"
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
        _, response = self.responses(manifest_canonical="https://example.org/fhir/core")

        with mock.patch.object(CHECK, "expect_status", side_effect=response):
            with self.assertRaisesRegex(RuntimeError, "canonical=.*example.org"):
                CHECK.verify(
                    "https://pages.example/repository/",
                    self.configuration(),
                    canonical_only=True,
                    expected_revision="abc123",
                )


if __name__ == "__main__":
    unittest.main()
