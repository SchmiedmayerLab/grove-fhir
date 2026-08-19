"""Tests for deterministic local FHIR package caching."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "Scripts" / "cache-fhir-package.cjs"


class CacheFHIRPackageTests(unittest.TestCase):
    @staticmethod
    def write_archive(
        path: Path, package_id: str, version: str, marker: str
    ) -> None:
        with tarfile.open(path, "w:gz") as archive:
            files = {
                "package/package.json": json.dumps(
                    {"name": package_id, "version": version}
                ).encode(),
                "package/marker.txt": marker.encode(),
            }
            for name, contents in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(contents)
                archive.addfile(info, io.BytesIO(contents))

    def run_cache(
        self, cache: Path, archive: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "node",
                str(SCRIPT),
                "--cache-root",
                str(cache),
                str(archive),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_installs_and_replaces_one_exact_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "cache"
            archive = root / "package.tgz"
            package_id = "org.example.fhir.mobile"
            version = "0.1.0"

            self.write_archive(archive, package_id, version, "first")
            first = self.run_cache(cache, archive)
            self.assertEqual(first.returncode, 0, first.stderr)

            self.write_archive(archive, package_id, version, "second")
            second = self.run_cache(cache, archive)
            self.assertEqual(second.returncode, 0, second.stderr)
            marker = cache / f"{package_id}#{version}" / "package" / "marker.txt"
            self.assertEqual(marker.read_text(), "second")

    def test_rejects_invalid_archive_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "package.tgz"
            self.write_archive(archive, "Not A Package", "0.1.0", "x")

            result = self.run_cache(root / "cache", archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid package id", result.stderr)


if __name__ == "__main__":
    unittest.main()
