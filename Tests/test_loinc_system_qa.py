"""LOINC lookup collisions require exact diagnostics and pinned concept evidence."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
import tempfile
import unittest

from Tests.test_guide_qa import CHECK


class LoincSystemQATests(unittest.TestCase):
    def test_only_the_proven_loinc_include_is_accounted(self):
        for case in ("valid", "unknown-code", "wrong-system", "filter", "empty", "wrong-path",
                     "wrong-diagnostic", "wrong-message", "wrong-resource"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output = root / "output"
                output.mkdir()
                include = {"system": CHECK.LOINC, "concept": [{"code": "8302-2"}]}
                if case == "unknown-code": include["concept"][0]["code"] = "unknown"
                if case == "wrong-system": include["system"] = "https://example.org/codes"
                if case == "filter": include["filter"] = [{"property": "STATUS", "op": "=", "value": "ACTIVE"}]
                if case == "empty": include["concept"] = []
                resource = {"resourceType": "ValueSet", "compose": {"include": [include]}}
                if case == "wrong-resource": resource["resourceType"] = "CodeSystem"
                (output / "ValueSet-example.json").write_text(json.dumps(resource))
                path = "ValueSet.compose.include[0] (l1/c1)"
                if case == "wrong-path": path = "ValueSet.compose.include[1] (l1/c1)"
                diagnostic = "OTHER" if case == "wrong-diagnostic" else "VALUESET_INCLUDE_WRONG_VS_HINT"
                message = ("The system 'http://loinc.org' is actually a value set, which itself refers "
                           "to the system 'http://loinc.org' so that may be what is intended here")
                if case == "wrong-message": message += " changed"
                (output / "qa.html").write_text(
                    '<h2><a href="example.html">fsh-generated/resources/ValueSet-example.json</a></h2>'
                    f'<table><tr><td><b>{path}</b></td><td><b>error</b></td><td><b>{message}</b>'
                    f'<span>{diagnostic}</span></td><td>profile</td></tr></table>')
                count = CHECK.verified_loinc_system_error_count(root)
                self.assertEqual(count, 1 if case == "valid" else 0)
                counts = CHECK.finding_counts({"errs": 1, "warnings": 0}, {}, verified_terminology_errors=count)
                self.assertEqual(counts.unsuppressed_errors, 1 - count)
                self.assertEqual(counts.offline_terminology_errors, 0)

    def test_verified_error_cannot_exceed_reported_errors(self):
        with self.assertRaisesRegex(ValueError, "smaller"):
            CHECK.finding_counts({"errs": 0, "warnings": 0}, {}, verified_terminology_errors=1)
