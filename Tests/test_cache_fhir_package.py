"""Tests for deterministic local FHIR package caching."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "Scripts" / "cache-fhir-package.cjs"
DOWNLOAD_SCRIPT = ROOT / "Scripts" / "download-fhir-tools.sh"


class CacheFHIRPackageTests(unittest.TestCase):
    @staticmethod
    def write_archive(
        path: Path,
        package_id: str,
        version: str,
        marker: str,
        *,
        package_type: str | None = None,
    ) -> None:
        with tarfile.open(path, "w:gz") as archive:
            metadata = {"name": package_id, "version": version}
            if package_type is not None:
                metadata["type"] = package_type
            files = {
                "package/package.json": json.dumps(metadata).encode(),
                "package/marker.txt": marker.encode(),
            }
            if package_type == "fhir.template":
                files = {
                    "package/package.json": json.dumps(metadata).encode(),
                    "config.json": json.dumps({"marker": marker}).encode(),
                    "includes/fragment.html": marker.encode(),
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

    def test_default_cache_is_scoped_to_the_explicit_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_home = root / "validator-home"
            archive = root / "package.tgz"
            package_id = "org.example.fhir.private"
            version = "0.1.0"
            self.write_archive(archive, package_id, version, "private")

            result = subprocess.run(
                ["node", str(SCRIPT), str(archive)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                env={**os.environ, "HOME": str(private_home)},
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            installed = (
                private_home
                / ".fhir"
                / "packages"
                / f"{package_id}#{version}"
                / "package"
                / "marker.txt"
            )
            self.assertEqual(installed.read_text(), "private")

    def test_rejects_invalid_archive_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "package.tgz"
            self.write_archive(archive, "Not A Package", "0.1.0", "x")

            result = self.run_cache(root / "cache", archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid package id", result.stderr)

    def test_publisher_template_preserves_root_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "cache"
            archive = root / "template.tgz"
            self.write_archive(
                archive,
                "fhir2.base.template",
                "0.1.0",
                "first",
                package_type="fhir.template",
            )
            first = self.run_cache(cache, archive)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed = cache / "fhir2.base.template#0.1.0"
            self.assertTrue((installed / "config.json").is_file())
            self.assertEqual(
                (installed / "includes/fragment.html").read_text(), "first"
            )
            self.assertTrue((installed / "package/package.json").is_file())
            self.assertFalse((installed / "package/config.json").exists())

            self.write_archive(
                archive,
                "fhir2.base.template",
                "0.1.0",
                "second",
                package_type="fhir.template",
            )
            second = self.run_cache(cache, archive)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                (installed / "includes/fragment.html").read_text(), "second"
            )

    def test_publisher_template_rejects_link_members(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "template.tgz"
            metadata = json.dumps(
                {
                    "name": "fhir2.base.template",
                    "version": "0.1.0",
                    "type": "fhir.template",
                }
            ).encode()
            with tarfile.open(archive, "w:gz") as package:
                for name, contents in {
                    "package/package.json": metadata,
                    "config.json": b"{}\n",
                }.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(contents)
                    package.addfile(member, io.BytesIO(contents))
                link = tarfile.TarInfo("includes/link.html")
                link.type = tarfile.SYMTYPE
                link.linkname = "../config.json"
                package.addfile(link)
            result = self.run_cache(root / "cache", archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported type", result.stderr)

    def test_offline_tool_cache_never_fetches_a_missing_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = root / "tools"
            fake_bin = root / "bin"
            fake_bin.mkdir()
            curl_marker = root / "curl-was-invoked"
            fake_curl = fake_bin / "curl"
            fake_curl.write_text(
                f"#!/usr/bin/env bash\ntouch {curl_marker}\nexit 99\n",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)

            result = subprocess.run(
                [str(DOWNLOAD_SCRIPT), "--offline", str(tools)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "HOME": str(root / "home"),
                    "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
                },
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Offline FHIR tool cache is missing or invalid", result.stderr)
            self.assertFalse(curl_marker.exists())


if __name__ == "__main__":
    unittest.main()
