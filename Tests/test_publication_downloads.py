"""Ensure packaging changes preserve resources, bundle bytes, and historical releases."""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import hashlib
import tempfile
import unittest
from pathlib import Path

from Scripts.publication_downloads import offload_downloads, redirect_page


class PublicationDownloadsTests(unittest.TestCase):
    def test_preview_download_links_and_resource_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            (site / "en").mkdir(parents=True)
            bundles = {"full-ig.zip": b"offline guide", "validator.pack": b"validator bytes"}
            resources = {"package.tgz": b"package", "example.json": b'{"value":"full-ig.zip"}',
                         "example.xml": b"<resource/>", "example.ttl": b"rdf",
                         "example.xlsx": b"xlsx", "example.csv": b"csv"}
            for name, data in (bundles | resources).items():
                (site / name).write_bytes(data)
            (site / "en/index.html").write_text('''<html><body>
                <a href="../full-ig.zip" download="full-ig.zip">Offline guide</a>
                <a href='https://example.org/mobile/ci-build/validator.pack'>Validator</a>
                <a href="https://other.example/full-ig.zip">External</a>
                <a href="../package.tgz">FHIR</a></body></html>''')
            rows = offload_downloads(site, root / "downloads/mobile",
                                     public_url="https://example.org/mobile/ci-build",
                                     run_url="https://github.com/example/ig/actions/runs/123")
            for name, data in resources.items():
                self.assertEqual((site / name).read_bytes(), data)
            for row in rows:
                data = bundles[row["path"]]
                self.assertFalse((site / row["path"]).exists())
                self.assertEqual((root / "downloads/mobile" / row["asset"]).read_bytes(), data)
                self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(row["bytes"], len(data))
            page = (site / "en/index.html").read_text()
            self.assertIn('href="../bulk-downloads.html#full-ig.zip"', page)
            self.assertNotIn('download="full-ig.zip"', page)
            self.assertIn("href='../bulk-downloads.html#validator.pack'", page)
            self.assertIn('href="https://other.example/full-ig.zip"', page)
            self.assertIn('href="../package.tgz"', page)
            landing = (site / "bulk-downloads.html").read_text()
            self.assertIn("/runs/123#artifacts", landing)
            self.assertIn("expire after 14 days", landing)
            self.assertIn("GitHub sign-in", landing)

    def test_release_downloads_are_versioned_and_old_history_is_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            web, assets = root / "web", root / "assets"
            for version in ("0.8.0", "0.9.0", ""):
                path = web / version
                path.mkdir(parents=True, exist_ok=True)
                (path / "index.html").write_text('<html><body><a href="full-ig.zip">Download</a></body></html>')
                (path / "full-ig.zip").write_bytes(version.encode() or b"current")
            old = {p.name: p.read_bytes() for p in (web / "0.8.0").iterdir()}
            url = "https://github.com/example/ig/releases/download/0.9.0"
            offload_downloads(web / "0.9.0", assets, public_url="https://example.org/mobile/0.9.0",
                              asset_prefix="mobile-0.9.0-", release_url=url)
            sealed = {p.name: p.read_bytes() for p in (web / "0.9.0").iterdir()}
            offload_downloads(web, assets, public_url="https://example.org/mobile",
                              asset_prefix="mobile-0.9.0-current-", release_url=url,
                              excluded_directories={"0.8.0", "0.9.0"})
            self.assertEqual(old, {p.name: p.read_bytes() for p in (web / "0.8.0").iterdir()})
            self.assertEqual(sealed, {p.name: p.read_bytes() for p in (web / "0.9.0").iterdir()})
            self.assertEqual((assets / "mobile-0.9.0-full-ig.zip").read_bytes(), b"0.9.0")
            self.assertEqual((assets / "mobile-0.9.0-current-full-ig.zip").read_bytes(), b"current")
            self.assertIn(f'{url}/mobile-0.9.0-full-ig.zip', (web / "0.9.0/index.html").read_text())
            self.assertIn(f'{url}/mobile-0.9.0-current-full-ig.zip', (web / "index.html").read_text())

    def test_redirect_preserves_browser_query_and_fragment_and_escapes_target(self):
        page = redirect_page('https://example.org/guide/en/index.html')
        self.assertIn('location.search + location.hash', page)
        self.assertIn('http-equiv="refresh"', page)
        self.assertIn('rel="canonical"', page)
        self.assertIn('href="https://example.org/guide/en/index.html"', page)
        self.assertNotIn('</script><script>alert', redirect_page('</script><script>alert(1)</script>'))

    def test_refuses_to_overwrite_an_existing_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "site").mkdir()
            (root / "assets").mkdir()
            (root / "site/full-ig.zip").write_bytes(b"new")
            (root / "assets/full-ig.zip").write_bytes(b"old")
            with self.assertRaisesRegex(ValueError, "already exists"):
                offload_downloads(root / "site", root / "assets", public_url="https://example.org")
            self.assertEqual((root / "site/full-ig.zip").read_bytes(), b"new")
            self.assertEqual((root / "assets/full-ig.zip").read_bytes(), b"old")
