"""Preview notices and standard Publisher staging boundaries."""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Tests.test_prepare_pages import PREPARE_PAGES as PREVIEW


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("stage_publication", ROOT / "Scripts/stage-publication.py")
assert SPEC and SPEC.loader
STAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STAGE)


def package(path: Path, metadata: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz") as archive:
        payload = json.dumps(metadata).encode()
        member = tarfile.TarInfo("package/package.json")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))


class DevelopmentBannerTests(unittest.TestCase):
    def test_replaces_native_box_once_and_links_to_publications(self):
        original = '<body><!--ReleaseHeader--><p id="publish-box">Local build</p><!--EndReleaseHeader--><h1>Guide</h1></body>'
        source = "https://github.com/example/repo/tree/abcdef123456789"
        canonical = "https://example.org/fhir/mobile"
        result = PREVIEW.development_banner(original, source, canonical)
        self.assertEqual(result.count('id="publish-box"'), 1)
        self.assertIn("Development build — not a published release.", result)
        self.assertIn('href="https://example.org/fhir/mobile/history.html"', result)
        self.assertIn("abcdef123456", result)
        self.assertNotIn("Local build", result)
        self.assertEqual(PREVIEW.development_banner(result, source, canonical), result)

    def test_custom_pages_receive_banner_but_fragments_do_not(self):
        self.assertIn('data-publication-status="ci-build"', PREVIEW.development_banner(
            '<html><BODY class="qa">QA</BODY></html>', 'https://example.org/a', 'https://example.org/fhir'))
        self.assertEqual(PREVIEW.development_banner('<div>fragment</div>', '', ''), '<div>fragment</div>')

    def test_incomplete_publish_box_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "complete FHIR publish box"):
            PREVIEW.development_banner('<body><!--ReleaseHeader-->broken</body>', '', '')

    def test_source_url_is_escaped(self):
        result = PREVIEW.development_banner('<body></body>', 'https://example.org/"<bad>', 'https://example.org')
        self.assertNotIn('<bad>', result)
        self.assertIn('&quot;', result)


class PublicationStagingTests(unittest.TestCase):
    def test_archive_rejects_traversal_and_symlinks(self):
        for kind in ("traversal", "symlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                archive = root / "bad.tar.gz"
                with tarfile.open(archive, "w:gz") as tar:
                    member = tarfile.TarInfo('../escape' if kind == 'traversal' else 'link')
                    if kind == 'symlink':
                        member.type, member.linkname = tarfile.SYMTYPE, '/tmp'
                    tar.addfile(member)
                with self.assertRaisesRegex(ValueError, "unsafe publication archive"):
                    STAGE.checked_extract(archive, root / "target")
                self.assertFalse((root / "escape").exists())

    def test_archive_is_deterministic_and_preserves_hidden_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            web = root / "web"
            web.mkdir()
            (web / '.nojekyll').touch()
            (web / 'index.html').write_text('publication')
            STAGE.archive_site(web, root / 'one.tgz')
            STAGE.archive_site(web, root / 'two.tgz')
            self.assertEqual((root / 'one.tgz').read_bytes(), (root / 'two.tgz').read_bytes())
            STAGE.checked_extract(root / 'one.tgz', root / 'restored')
            self.assertTrue((root / 'restored/.nojekyll').exists())

    def test_first_and_subsequent_requests_use_standard_publication_fields(self):
        guide = {'canonicalPath': 'mobile'}
        metadata = {'name': 'org.grovealliance.fhir.mobile', 'version': '0.9.0', 'title': 'Mobile'}
        config = {'canonicalBaseUrl': 'https://example.org/fhir', 'previewBaseUrl': 'https://example.org/dev'}
        release = {'status': 'draft', 'sequence': 'Releases', 'description': 'Example'}
        first = STAGE.publication_request(guide, metadata, config, release, True)
        self.assertEqual(first['path'], 'https://example.org/fhir/mobile/0.9.0')
        self.assertEqual(first['mode'], 'milestone')
        self.assertEqual(first['ci-build'], 'https://example.org/dev/mobile/ci-build')
        later = STAGE.publication_request(guide, metadata, config, release, False)
        self.assertFalse(later['first'])
        self.assertNotIn('category', later)
        self.assertNotIn('ci-build', later)

    def test_previous_publication_cannot_drop_existing_history(self):
        releases = [{'tag_name': '0.8.0', 'assets': [{'name': 'grove-fhir-publication-0.8.0.tar.gz'}]}]
        with self.assertRaisesRegex(ValueError, 'latest published'):
            STAGE.check_previous_publication(None, releases)
        with self.assertRaisesRegex(ValueError, 'latest published'):
            STAGE.check_previous_publication({'tag': '0.7.0'}, releases)
        STAGE.check_previous_publication({'tag': '0.8.0'}, releases)
        STAGE.check_previous_publication(None, [])

    def test_history_restores_exact_sealed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / 'old'
            web = root / 'web'
            STAGE.write_json(old / 'mobile/package-list.json', {'list': [
                {'version': 'current'}, {'version': '0.8.0'}]})
            (old / 'mobile/0.8.0').mkdir()
            (old / 'mobile/0.8.0/index.html').write_bytes(b'original sealed banner\r\n')
            (web / 'mobile/0.8.0').mkdir(parents=True)
            (web / 'mobile/0.8.0/index.html').write_text('changed by Publisher')
            (web / 'mobile/0.8.0/extra.html').touch()
            STAGE.restore_history(web, old, [{'canonicalPath': 'mobile'}])
            self.assertEqual((web / 'mobile/0.8.0/index.html').read_bytes(), b'original sealed banner\r\n')
            self.assertFalse((web / 'mobile/0.8.0/extra.html').exists())

    def test_tampered_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'evidence.json').write_text('changed')
            (root / 'SHA256SUMS').write_text('0' * 64 + '  evidence.json\n')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                STAGE.verify_evidence(root)

    def test_evidence_requires_exact_checksum_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'evidence.json').write_bytes(b'{}')
            line = hashlib.sha256(b'{}').hexdigest() + '  evidence.json\n'
            (root / 'SHA256SUMS').write_text(line)
            STAGE.verify_evidence(root)
            (root / 'unlisted.json').write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'not covered'):
                STAGE.verify_evidence(root)
            (root / 'unlisted.json').unlink()
            (root / 'SHA256SUMS').write_text(line + line)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                STAGE.verify_evidence(root)

    def test_partial_or_stale_current_publication_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            web = Path(directory)
            root = web / 'mobile'
            canonical = 'https://example.org/fhir/mobile'
            metadata = {'name': 'org.example.mobile', 'version': '0.9.0',
                        'canonical': canonical, 'url': canonical + '/0.9.0'}
            for destination in (root, root / '0.9.0'):
                package(destination / 'package.tgz', metadata)
                (destination / 'index.html').write_text('<p id="publish-box">Published</p>')
                (destination / 'qa.json').write_text('{}')
            (root / 'history.html').write_text('history')
            STAGE.write_json(root / 'package-list.json', {'list': [
                {'version': '0.9.0', 'path': metadata['url'], 'current': True}]})

            def check():
                return STAGE.check_published_guide(web, {'canonicalPath': 'mobile'},
                    {'canonicalBaseUrl': 'https://example.org/fhir'}, '0.9.0')

            self.assertEqual(check(), root / '0.9.0')
            for name in ('index.html', 'package.tgz', 'qa.json'):
                path = root / name
                original = path.read_bytes()
                path.unlink()
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'did not produce'):
                    check()
                path.write_bytes(original)
            package(root / 'package.tgz', dict(metadata, version='0.8.0'))
            with self.assertRaisesRegex(ValueError, 'current package identity'):
                check()

    def test_published_package_rejects_local_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'package.tgz'
            package(path, {'url': 'file:///Users/example/output'})
            with self.assertRaisesRegex(ValueError, 'local filesystem'):
                STAGE.check_package_portability(path)

    def fixture(self, root: Path):
        guides = [{'source': name, 'canonicalPath': name, 'aliases': []}
                  for name in ('mobile', 'questionnaire', 'sensor', 'healthkit')]
        config = {'schemaVersion': 0, 'releaseMode': 'ci-build-only', 'guides': guides,
                  'canonicalBaseUrl': 'https://example.org/fhir',
                  'previewBaseUrl': 'https://example.org/dev', 'sourceRepository': 'https://github.com/example/repo'}
        STAGE.write_json(root / 'publication/config.json', config)
        STAGE.write_json(root / 'publication/release.json', {'status': 'draft', 'sequence': 'Releases',
                         'description': 'Example', 'previousPublication': None})
        STAGE.write_json(root / 'publication/publish-setup.json', {'website': {'url': config['canonicalBaseUrl']}})
        STAGE.write_json(root / 'catalog/release-manifest.json', {'releaseVersion': '0.9.0', 'toolchain': {'igPublisher': {'version': '3.0.3'}}})
        history = root / f'.build/publication-tools/history-{STAGE.HISTORY_REVISION}.tar.gz'
        history.parent.mkdir(parents=True)
        with tarfile.open(history, 'w:gz') as tar:
            item = tarfile.TarInfo('upstream/history.template')
            item.size = 4
            tar.addfile(item, io.BytesIO(b'test'))
        for guide in guides:
            name = guide['source']
            (root / name / 'input/fsh').mkdir(parents=True)
            (root / name / 'input/fsh/example.fsh').write_text('Profile: Example')
            (root / name / 'sushi-config.yaml').write_text('releaseLabel: ci-build\n')
            package(root / name / 'output/package.tgz', {'name': f'org.grovealliance.fhir.{name}',
                    'version': '0.9.0', 'title': name, 'canonical': f'https://example.org/fhir/{name}'})
        output = root / '.build/release'
        output.mkdir()
        names = ('grove-fhir-machine-contracts-0.9.0.tar.gz', 'machine-contract-index-0.9.0.json',
                 'release-manifest-0.9.0.json', 'mobile-semantic-snapshot-0.9.0.json')
        for name in names:
            (output / name).write_text('{}')
        STAGE.write_json(output / 'build-provenance-0.9.0.json', {
            'sourceRevision': 'a'*40, 'releaseVersion': '0.9.0',
            'releaseManifestSha256': STAGE.CHECK.digest(root / 'catalog/release-manifest.json')})
        names += ('build-provenance-0.9.0.json',)
        (output / 'SHA256SUMS').write_text(''.join(
            f"{STAGE.CHECK.digest(output / name)}  {name}\n" for name in names))
        return guides, config, history, output

    def test_staging_invokes_standard_publisher_and_packages_validated_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            guides, config, history, output = self.fixture(root)
            calls = []

            def run(command, **kwargs):
                calls.append(command)
                if 'Scripts/fhir_package_semantic_snapshot.py' in command:
                    Path(command[command.index('--output') + 1]).write_text('{"published":true}')
                if '-go-publish' in command:
                    source = Path(command[command.index('-source') + 1])
                    web = Path(command[command.index('-web') + 1])
                    request = json.loads((source / 'publication-request.json').read_text())
                    self.assertEqual(request['mode'], 'milestone')
                    self.assertTrue((source / 'input/fsh/example.fsh').is_file())
                    self.assertIn('releaseLabel: draft', (source / 'sushi-config.yaml').read_text())
                    self.assertNotIn('-no-network', command)
                    name = source.name
                    build = Path(command[command.index('-temp') + 1]) / 'ig-builds' / f'org.grovealliance.fhir.{name}#0.9.0'
                    (build / 'fsh-generated').mkdir(parents=True)
                    published = web / name / '0.9.0'
                    metadata = STAGE.CHECK.package_metadata(source / 'output/package.tgz')
                    metadata['url'] = request['path']
                    package(published / 'package.tgz', metadata)
                    package(web / name / 'package.tgz', metadata)
                    (web / name / 'index.html').write_text('<html><body>Current publication</body></html>')
                    (web / name / 'qa.json').write_text('{}')
                    (published / 'index.html').write_text('<html><body><!--ReleaseHeader--><p id="publish-box">Published</p><!--EndReleaseHeader--></body></html>')
                    (published / 'qa.json').write_text('{}')
                    (published / 'qa.html').write_text('QA')
                    (published / 'full-ig.zip').write_bytes(b'versioned offline guide')
                    (web / name / 'full-ig.zip').write_bytes(b'current offline guide')
                    (web / name / 'history.html').write_text('history')
                    STAGE.write_json(web / name / 'package-list.json', {'list': [{
                        'version': '0.9.0', 'path': request['path'], 'current': True}]})
                return subprocess.CompletedProcess(command, 0)

            with mock.patch.object(STAGE, 'ROOT', root), \
                 mock.patch.object(STAGE, 'HISTORY_SHA256', hashlib.sha256(history.read_bytes()).hexdigest()), \
                 mock.patch.object(STAGE.PLAN, 'waves', return_value=[[g['source'] for g in guides]]), \
                 mock.patch.object(STAGE.subprocess, 'check_output', side_effect=lambda cmd, **kw: 'a'*40 if 'rev-parse' in cmd else '[[]]' if cmd[0] == 'gh' else ''), \
                 mock.patch.object(STAGE.subprocess, 'run', side_effect=run):
                archive = STAGE.stage(output=root / '.build/publication-release', evidence=output, publication_date='2026-11-13')
            self.assertEqual(len([c for c in calls if '-go-publish' in c]), 4)
            self.assertEqual(json.loads((archive.parent / 'mobile-semantic-snapshot-0.9.0.json').read_text()),
                             {"published": True})
            self.assertTrue(any('Scripts/validate-questionnaire-fhir.py' in c for c in calls))
            self.assertIn(archive.name, (archive.parent / 'SHA256SUMS').read_text())
            self.assertEqual((archive.parent / 'machine-contract-index-0.9.0.json').read_bytes(),
                             (output / 'machine-contract-index-0.9.0.json').read_bytes())
            STAGE.checked_extract(archive, root / 'result')
            manifest = json.loads((root / 'result/publication-manifest.json').read_text())
            self.assertEqual(len(manifest['packages']), 4)
            for guide in guides:
                name = guide['source']
                for suffix, payload in [('', b'versioned offline guide'), ('current-', b'current offline guide')]:
                    asset = f'grove-{name}-0.9.0-{suffix}full-ig.zip'
                    self.assertEqual((archive.parent / asset).read_bytes(), payload)
                    self.assertIn(asset, (archive.parent / 'SHA256SUMS').read_text())
                self.assertFalse((root / f'result/{name}/full-ig.zip').exists())
                self.assertFalse((root / f'result/{name}/0.9.0/full-ig.zip').exists())
                downloads = json.loads((root / f'result/{name}/0.9.0/bulk-downloads.json').read_text())
                self.assertTrue(downloads['files'][0]['url'].endswith(f'/releases/download/0.9.0/grove-{name}-0.9.0-full-ig.zip'))
            self.assertEqual(
                (archive.parent / 'org.grovealliance.fhir.mobile-0.9.0.tgz').read_bytes(),
                (root / 'result/mobile/0.9.0/package.tgz').read_bytes(),
            )
            self.assertIn('Published version 0.9.0', (root / 'result/mobile/0.9.0/index.html').read_text())
            self.assertEqual((root / 'mobile/sushi-config.yaml').read_text(), 'releaseLabel: ci-build\n')
            self.assertTrue((root / 'mobile/input/fsh/example.fsh').is_file())

    def test_successful_process_without_publication_outputs_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'did not produce'):
                STAGE.check_published_guide(Path(directory), {'canonicalPath': 'mobile'},
                                           {'canonicalBaseUrl': 'https://example.org/fhir'}, '0.9.0')


if __name__ == '__main__':
    unittest.main()
