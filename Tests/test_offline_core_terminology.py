"""Required bindings remain checked when Publisher has no terminology server."""

# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from Tests.test_guide_qa import CHECK


class OfflineCoreTerminologyTests(unittest.TestCase):
    def test_missing_language_system_requires_generated_english_ig(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'output').mkdir()
            for language, diagnostic, expected in (
                ('en', 'UNABLE_TO_INFER_CODESYSTEM_UNKNOWN_SYSTEM', 1),
                ('fr', 'UNABLE_TO_INFER_CODESYSTEM_UNKNOWN_SYSTEM', 0),
                ('en', 'UNKNOWN_CODESYSTEM', 0),
            ):
                (root / 'output/ImplementationGuide-example.json').write_text(json.dumps(
                    {'resourceType': 'ImplementationGuide', 'language': language}))
                (root / 'output/qa.html').write_text(
                    '<h2><a href="index.html">fsh-generated/resources/ImplementationGuide-example.json</a></h2>'
                    '<table><tr><td><b>ImplementationGuide.language (l1/c1)</b></td><td><b>warning</b></td>'
                    f'<td><b>{CHECK.OFFLINE_BCP47_MISSING_SYSTEM_WARNING}</b><span>{diagnostic}</span></td>'
                    '<td>profile</td></tr></table>')
                self.assertEqual(CHECK.offline_unknown_code_system_warning_count(root), expected)

    def test_ucum_membership_requires_the_bound_value_set_and_actual_resource_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'output').mkdir()
            (root / 'fsh-generated/resources').mkdir(parents=True)
            core = root / 'core.tgz'
            value_set = {'resourceType': 'ValueSet', 'url': 'http://hl7.org/fhir/ValueSet/ucum-bodylength',
                         'version': '4.0.1', 'compose': {'include': [
                             {'system': CHECK.UCUM, 'concept': [{'code': 'cm'}]}]}}
            with tarfile.open(core, 'w:gz') as archive:
                payload = json.dumps(value_set).encode()
                member = tarfile.TarInfo('package/ValueSet-ucum-bodylength.json')
                member.size = len(payload)
                archive.addfile(member, io.BytesIO(payload))
            for code, actual, value_set_url, diagnostic, expected in (
                ('cm', 'cm', value_set['url'], 'UNABLE_TO_INFER_CODESYSTEM_UNKNOWN_SYSTEM', 1),
                ('kg', 'kg', value_set['url'], 'UNABLE_TO_INFER_CODESYSTEM_UNKNOWN_SYSTEM', 0),
                ('cm', 'kg', value_set['url'], 'UNABLE_TO_INFER_CODESYSTEM_UNKNOWN_SYSTEM', 0),
                ('cm', 'cm', 'https://example.org/unknown', 'UNABLE_TO_INFER_CODESYSTEM_UNKNOWN_SYSTEM', 0),
                ('cm', 'cm', value_set['url'], 'UNEXPECTED_DIAGNOSTIC', 0),
            ):
                with self.subTest(code=code, actual=actual, value_set=value_set_url, diagnostic=diagnostic):
                    resource = {'resourceType': 'Observation', 'valueQuantity': {'system': CHECK.UCUM, 'code': actual}}
                    (root / 'fsh-generated/resources/Observation-example.json').write_text(json.dumps(resource))
                    message = (f"The System URI could not be determined for the code '{code}' in the ValueSet "
                               f"'{value_set_url}|4.0.1': a definition for the CodeSystem '{CHECK.UCUM}' it includes could not be found")
                    self.write_qa(root, 'Observation.value.ofType(Quantity).code (l1/c1)', message, diagnostic)
                    self.assertEqual(CHECK.offline_missing_core_system_error_count(root, core), expected)

    @staticmethod
    def write_qa(root, path, message, diagnostic):
        (root / 'output/qa.html').write_text(
            '<p>IG Publisher Version: v3.0.3</p>'
            '<h2><a href="example.html">fsh-generated/resources/Observation-example.json</a></h2>'
            f'<table><tr><td><b>{path}</b></td><td><b>error</b></td><td><b>{message}</b>'
            f'<span>{diagnostic}</span></td><td>profile</td></tr></table>')

    def test_period_timezone_error_requires_an_actual_valid_zone(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'output').mkdir()
            (root / 'fsh-generated/resources').mkdir(parents=True)
            core = root / 'core.tgz'
            with tarfile.open(core, 'w:gz'):
                pass
            for zone, expected in [('America/Los_Angeles', 1), ('America/Not_A_Zone', 0)]:
                resource = {'resourceType': 'Observation', 'effectivePeriod': {
                    '_start': {'extension': [{'url': CHECK.TIMEZONE_EXTENSION, 'valueCode': zone}]}}}
                (root / 'fsh-generated/resources/Observation-example.json').write_text(json.dumps(resource))
                missing = (f"The System URI could not be determined for the code '{zone}' in the ValueSet "
                           "'http://hl7.org/fhir/ValueSet/timezones|4.0.1': a definition for the CodeSystem "
                           "'https://www.iana.org/time-zones' it includes could not be found")
                message = (f"The value provided ('{zone}') was not found in the value set 'I a n a timezones' "
                           "(http://hl7.org/fhir/ValueSet/timezones|4.0.1), and a code is required from this value set "
                           f"(error message = {missing})")
                self.write_qa(root, 'Observation.effective.ofType(Period).start.extension[0].value.ofType(code) (l1/c1)',
                              message, 'Terminology_TX_NoValid_16')
                self.assertEqual(CHECK.offline_missing_core_system_error_count(root, core), expected)


if __name__ == '__main__':
    unittest.main()
