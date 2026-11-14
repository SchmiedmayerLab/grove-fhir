"""Dependency refresh uses stable releases and keeps checksum validation."""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import importlib.util
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("update_dependencies", Path(__file__).parents[1] / "Scripts/update-dependencies.py")
UPDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATE)


class DependencyUpdateTests(unittest.TestCase):
    def test_update_rejects_changed_tool_or_template_before_running_package_managers(self):
        for changed in ('tool', 'template'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'catalog').mkdir()
                payload = b'original template'
                binary = {'version': '3.0.3', 'sha256': 'a' * 64}
                template = {'packageId': 'fhir2.base.template', 'version': '0.1.0',
                            'sha256': hashlib.sha256(payload).hexdigest()}
                manifest = root / 'catalog/release-manifest.json'
                original = json.dumps({'toolchain': {
                    'igPublisher': binary, 'fhirValidator': binary, 'template': template}})
                manifest.write_text(original)
                candidate = dict(binary, sha256='b' * 64) if changed == 'tool' else binary
                with patch.object(UPDATE, 'ROOT', root), \
                     patch.object(UPDATE, 'latest_binary', return_value=candidate), \
                     patch.object(UPDATE.urllib.request, 'urlopen', side_effect=[
                         io.BytesIO(b'{"dist-tags":{"latest":"0.1.0"}}'), io.BytesIO(b'changed template')]), \
                     patch.object(UPDATE.subprocess, 'run') as run:
                    with self.assertRaisesRegex(ValueError, 'released asset changed upstream'):
                        UPDATE.main()
                    run.assert_not_called()
                self.assertEqual(manifest.read_text(), original)

    def test_latest_binary_requires_stable_tag_and_upstream_digest(self):
        for version, digest in [('3.0.4-rc1', 'sha256:' + 'a'*64), ('3.0.4', None)]:
            with self.subTest(version=version, digest=digest), patch.object(UPDATE, 'github', return_value={
                'tag_name': version, 'assets': [{'name': 'publisher.jar', 'digest': digest}],
            }):
                with self.assertRaises((ValueError, TypeError)):
                    UPDATE.latest_binary('HL7/fhir-ig-publisher', 'publisher.jar')
        with patch.object(UPDATE, 'github', return_value={
            'tag_name': 'v3.0.4', 'assets': [{'name': 'publisher.jar', 'digest': 'sha256:' + 'a'*64}],
        }):
            self.assertEqual(UPDATE.latest_binary('HL7/fhir-ig-publisher', 'publisher.jar'),
                             {'version': '3.0.4', 'sha256': 'a'*64})

    def test_constant_update_rejects_missing_or_ambiguous_declarations(self):
        for text in ('unrelated', 'VERSION = "old"\nVERSION = "other"'):
            with self.assertRaisesRegex(ValueError, 'expected one'):
                UPDATE.replace_constant(text, 'VERSION', '3.0.4')
        self.assertEqual(UPDATE.replace_constant('readonly VERSION="3.0.3"\n', 'VERSION', '3.0.4', shell=True),
                         'readonly VERSION="3.0.4"\n')

    def test_refresh_synchronizes_external_dependencies_without_changing_local_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'guide'
            (source / 'input/fsh').mkdir(parents=True)
            (root / 'catalog').mkdir()
            (source / 'sushi-config.yaml').write_text(
                'dependencies:\n  hl7.fhir.uv.extensions.r4: 5.3.0\n  org.grovealliance.fhir.mobile: 0.8.0\n')
            alias = source / 'input/fsh/aliases.fsh'
            alias.write_text('Alias: $timezone = http://hl7.org/fhir/StructureDefinition/timezone|5.3.0\n')
            expectations = source / 'fixtures/validator/validator-expectations.json'
            expectations.parent.mkdir(parents=True)
            expectations.write_text('{"message":"from targetConstraint|5.3.0); extension v5.3.0 is not allowed"}')
            graph = root / 'catalog/package-graph.json'
            graph.write_text(json.dumps({'packages': [{'source': 'guide', 'dependencies': []}]}))
            guide = {'source': 'guide', 'directDependencies': [
                'hl7.fhir.uv.extensions.r4#5.3.0', 'org.grovealliance.fhir.mobile#0.8.0']}
            with patch.object(UPDATE, 'ROOT', root), patch.object(UPDATE.urllib.request, 'urlopen',
                    return_value=io.BytesIO(b'{"dist-tags":{"latest":"5.4.0"}}')):
                UPDATE.refresh_guide_dependencies({'guides': [guide]})
            self.assertEqual(guide['directDependencies'], [
                'hl7.fhir.uv.extensions.r4#5.4.0', 'org.grovealliance.fhir.mobile#0.8.0'])
            self.assertEqual(json.loads(graph.read_text())['packages'][0]['dependencies'], guide['directDependencies'])
            self.assertIn('|5.4.0', alias.read_text())
            self.assertEqual(json.loads(expectations.read_text())['message'],
                             'from targetConstraint|5.4.0); extension v5.4.0 is not allowed')
            self.assertIn('hl7.fhir.uv.extensions.r4: 5.4.0', (source / 'sushi-config.yaml').read_text())


if __name__ == '__main__':
    unittest.main()
