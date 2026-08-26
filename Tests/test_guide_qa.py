"""Tests for exact, exercised IG Publisher warning suppressions."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_guide_qa", ROOT / "Scripts/check-guide-qa.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)



def registered_media_types() -> set[str]:
    """Every media type the format registry admits, read from the registry itself."""
    registry = json.loads(
        (ROOT / "catalog/format-registry.json").read_text(encoding="utf-8")
    )
    return {fmt["contentType"] for fmt in registry["formats"].values()}


class GuideQATests(unittest.TestCase):
    def test_no_generated_terminology_transaction_is_tracked(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files", "*/input-cache/*"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(
            [path for path in tracked if (ROOT / path).is_file()],
            [],
        )
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("**/input-cache/", ignore)
        self.assertNotRegex(ignore, r"(?m)^!.*input-cache")
        workflow = (ROOT / ".github/workflows/build-and-test.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("*/input-cache", workflow)

    def test_offline_mime_diagnostics_are_exact_and_example_scoped(self) -> None:
        for guide in (
            "mobile",
            "sensor",
            "sensorkit",
            "healthkit",
            "health-connect",
            "providers",
            "questionnaire",
        ):
            configured = CHECK.configured_suppressions(
                ROOT / guide / "input/ignoreWarnings.txt"
            )
            self.assertFalse(
                any(
                    message.startswith("ERROR: ")
                    and "ValueSet/mimetypes|4.0.1" in message
                    for message in configured
                ),
                f"{guide} must not suppress the Publisher MIME defect",
            )

        source_content_types: dict[str, set[str]] = {}
        for guide in ("sensor", "sensorkit", "providers"):
            source = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted((ROOT / guide / "input/fsh").glob("*.fsh"))
            )
            source_content_types[guide] = set(
                re.findall(r"contentType\s*=\s*#([^\s]+)", source)
            )
        self.assertEqual(
            source_content_types,
            {
                "sensor": {"application/vnd.grovealliance.native+json"},
                "sensorkit": {"application/vnd.grovealliance.native+json", "text/csv"},
                "providers": {"application/vnd.grovealliance.provider+json"},
            },
        )

        terminology = (ROOT / "sensor/input/fsh/generated-recording-mime-types.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn("ValueSet: GroveNativeRecordingMimeTypeVS", terminology)
        self.assertNotIn("InstanceOf: CodeSystem", terminology)
        self.assertNotIn("* url = \"urn:ietf:bcp:13\"", terminology)
        self.assertEqual(
            set(
                re.findall(
                    r"^\* urn:ietf:bcp:13#([^\s]+)", terminology, re.MULTILINE
                )
            ),
            registered_media_types(),
        )
        self.assertEqual(
            set(
                re.findall(
                    r'^\* \^expansion\.contains\[[^]]+\]\.code = #([^\s]+)',
                    terminology,
                    re.MULTILINE,
                )
            ),
            registered_media_types(),
        )
        self.assertIn(
            '* ^expansion.parameter[=].valueUri = "urn:ietf:bcp:13"',
            terminology,
        )
        self.assertIn(
            '* ^expansion.parameter[=].valueBoolean = false', terminology
        )
        allowlist = json.loads(
            (ROOT / "publication/artifact-allowlist.json").read_text(encoding="utf-8")
        )
        sensor_artifacts = next(
            package["artifacts"]
            for package in allowlist["packages"]
            if package["source"] == "sensor"
        )
        self.assertFalse(
            any(
                artifact["resourceType"] == "CodeSystem"
                and artifact["id"] == "GroveNativeRecordingMimeTypeFragment"
                for artifact in sensor_artifacts
            )
        )

    def test_publisher_232_finding_counts_are_fail_closed_and_transparent(self) -> None:
        counts = CHECK.finding_counts(
            {"errs": 3, "warnings": 2},
            {
                "ERROR: DocumentReference/A: exact offline defect": 1,
                "ERROR: DocumentReference/B: exact offline defect": 1,
                "WARNING: Observation/C: reviewed warning": 1,
            },
        )
        self.assertEqual(counts.raw_errors, 3)
        self.assertEqual(counts.exact_suppressed_errors, 2)
        self.assertEqual(counts.unsuppressed_errors, 1)
        self.assertEqual(counts.raw_warnings, 3)
        self.assertEqual(counts.exact_suppressed_warnings, 1)
        self.assertEqual(counts.unsuppressed_warnings, 2)
        with self.assertRaisesRegex(ValueError, "smaller"):
            CHECK.finding_counts(
                {"errs": 0, "warnings": 0},
                {"ERROR: DocumentReference/A: impossible": 1},
            )
        link_counts = CHECK.finding_counts(
            {"errs": 0, "warnings": 0},
            {
                "ERROR: en/StructureDefinition-a.html#/html/body/a at Line 1, "
                "column 1: frozen generated link": 1
            },
        )
        self.assertEqual(link_counts.raw_errors, 1)
        self.assertEqual(link_counts.exact_suppressed_errors, 1)
        self.assertEqual(link_counts.unsuppressed_errors, 0)

    def test_no_error_suppressions_are_configured(self) -> None:
        for guide in (
            "mobile",
            "sensor",
            "sensorkit",
            "healthkit",
            "health-connect",
            "providers",
            "questionnaire",
        ):
            errors = {
                message
                for message in CHECK.configured_suppressions(
                    ROOT / guide / "input/ignoreWarnings.txt"
                )
                if message.startswith("ERROR: ")
            }
            self.assertEqual(errors, set(), f"{guide} configures error suppressions")

    def test_nonzero_publisher_exit_reuses_the_audited_qa_gate(self) -> None:
        script = (ROOT / "Scripts/build-guides.sh").read_text(encoding="utf-8")
        fallback = script.split(") || {", maxsplit=1)[1].split("done", maxsplit=1)[0]
        self.assertIn('Scripts/check-guide-qa.py" "$REPOSITORY_ROOT/$guide"', fallback)
        self.assertNotIn('qa.get("errs"', fallback)

    def test_exact_suppression_must_be_exercised_once(self) -> None:
        message = "WARNING: Observation/Example: Observation: reviewed warning"
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve()
            (guide / "input").mkdir()
            (guide / "output").mkdir()
            (guide / "input/ignoreWarnings.txt").write_text(
                f"== Suppressed Messages ==\n# reviewed\n{message}\n",
                encoding="utf-8",
            )
            (guide / "output/qa.html").write_text(
                '<a name="suppressed"> </a><ul><li>'
                f'{message} <span style="color: navy">(1 uses)</span></li></ul>'
                '<a name="sorted"> </a>',
                encoding="utf-8",
            )
            self.assertEqual(CHECK.validate_suppressions(guide), [])

            (guide / "output/qa.html").write_text(
                '<a name="suppressed"> </a><a name="sorted"> </a>',
                encoding="utf-8",
            )
            self.assertIn(
                "not exercised exactly", CHECK.validate_suppressions(guide)[0]
            )

    def test_broad_substring_suppression_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve() / "ignoreWarnings.txt"
            path.write_text(
                "== Suppressed Messages ==\nThe Implementation Guide contains no examples\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "broad suppression"):
                CHECK.configured_suppressions(path)

    def test_offline_mime_suppression_cannot_match_another_resource_or_code(self) -> None:
        message = (
            "ERROR: DocumentReference/SensorKitECGDocumentExample: "
            "DocumentReference.content[0].attachment.contentType: The value provided "
            "('application/json') was not found in the value set 'MimeType' "
            "(http://hl7.org/fhir/ValueSet/mimetypes|4.0.1), and a code is required "
            "from this value set (error message = Cannot invoke "
            '"org.hl7.fhir.r5.terminologies.client.TerminologyClientContext.getAddress()" '
            'because "tc" is null)'
        )
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve()
            (guide / "input").mkdir()
            (guide / "output").mkdir()
            (guide / "input/ignoreWarnings.txt").write_text(
                f"== Suppressed Messages ==\n{message}\n", encoding="utf-8"
            )

            different = message.replace("application/json", "text/plain")
            (guide / "output/qa.html").write_text(
                '<a name="suppressed"> </a><ul><li>'
                f'{different} <span style="color: navy">(1 uses)</span></li></ul>'
                '<a name="sorted"> </a>',
                encoding="utf-8",
            )
            problems = CHECK.validate_suppressions(guide)
            self.assertTrue(any("not exercised exactly" in item for item in problems))
            self.assertTrue(any("unconfigured suppression" in item for item in problems))


if __name__ == "__main__":
    unittest.main()
