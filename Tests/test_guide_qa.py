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
    return {
        content_type
        for fmt in registry["formats"].values()
        for content_type in fmt.get("contentTypes", [fmt.get("contentType")])
    }


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
                "sensor": {"application/json"},
                "sensorkit": {
                    "application/json",
                    "application/octet-stream",
                    "text/csv",
                },
                "providers": {"application/json"},
            },
        )

        terminology = (ROOT / "sensor/input/fsh/generated-recording-mime-types.fsh").read_text(
            encoding="utf-8"
        )
        self.assertIn("ValueSet: GroveRecordingMimeTypeVS", terminology)
        self.assertNotIn("InstanceOf: CodeSystem", terminology)
        self.assertNotIn("* url = \"urn:ietf:bcp:13\"", terminology)

        def fsh_codes(pattern: str) -> set[str]:
            return {
                quoted or bare
                for quoted, bare in re.findall(pattern, terminology, re.MULTILINE)
            }

        self.assertEqual(
            fsh_codes(
                r'^\* urn:ietf:bcp:13#(?:"([^"]+)"|([^\s]+))'
            ),
            registered_media_types(),
        )
        self.assertEqual(
            fsh_codes(
                r'^\* \^expansion\.contains\[[^]]+\]\.code = #(?:"([^"]+)"|([^\s]+))'
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
        self.assertEqual(counts.offline_terminology_errors, 0)
        self.assertEqual(counts.unsuppressed_errors, 1)
        self.assertEqual(counts.raw_warnings, 3)
        self.assertEqual(counts.exact_suppressed_warnings, 1)
        self.assertEqual(counts.offline_terminology_warnings, 0)
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
        self.assertEqual(link_counts.offline_terminology_errors, 0)
        self.assertEqual(link_counts.offline_terminology_warnings, 0)
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
        self.assertIn('check_guide_qa "$REPOSITORY_ROOT/$guide"', fallback)
        self.assertNotIn("qa_arguments", script)
        self.assertNotIn('qa.get("errs"', fallback)

    def test_offline_mime_exception_is_exact_registry_backed_and_fail_closed(self) -> None:
        message = (
            "The value provided ('application/json') was not found in the value set "
            "'MimeType' (http://hl7.org/fhir/ValueSet/mimetypes|4.0.1), and a code "
            "is required from this value set (error message = Cannot invoke "
            '"org.hl7.fhir.r5.terminologies.client.TerminologyClientContext.getAddress()" '
            'because "tc" is null)'
        )

        def qa_html(
            *,
            filename: str = "DocumentReference-Example",
            path: str = "DocumentReference.content[0].attachment.contentType (l1/c1)",
            finding: str = message,
            diagnostic: str = "Terminology_TX_NoValid_16",
            publisher: str = "2.3.3",
        ) -> str:
            return (
                f"<p>IG Publisher Version: v{publisher}</p>"
                f'<h2><a href="{filename}.html">fsh-generated/resources/'
                f"{filename}.json</a></h2><table>"
                '<tr style="background-color: #ffcccc">'
                f"<td><b>{path}</b></td><td><b>error</b></td>"
                f'<td><b>{finding}</b> <span class="code-value">{diagnostic}</span></td>'
                "<td>profile</td></tr></table>"
            )

        document = {
            "resourceType": "DocumentReference",
            "content": [{
                "attachment": {"contentType": "application/json"},
                "format": {
                    "system": (
                        "https://grovealliance.org/fhir/sensor/CodeSystem/"
                        "grove-recording-format"
                    ),
                    "code": "native-recording",
                },
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve() / "guide"
            resources = guide / "fsh-generated/resources"
            output = guide / "output"
            resources.mkdir(parents=True)
            output.mkdir()

            def write_case(
                html_text: str,
                resource: dict[str, object] = document,
                filename: str = "DocumentReference-Example",
            ) -> int:
                (output / "qa.html").write_text(html_text, encoding="utf-8")
                (resources / f"{filename}.json").write_text(
                    json.dumps(resource), encoding="utf-8"
                )
                return CHECK.offline_mime_error_count(guide)

            self.assertEqual(write_case(qa_html()), 1)
            versioned_content_type = "application/fhir+json; fhirVersion=1.0"
            versioned_document = json.loads(json.dumps(document))
            versioned_document["content"][0]["attachment"]["contentType"] = (
                versioned_content_type
            )
            versioned_document["content"][0]["format"]["code"] = "fhir-resource"
            self.assertEqual(
                write_case(
                    qa_html(
                        finding=message.replace(
                            "application/json", versioned_content_type
                        )
                    ),
                    versioned_document,
                ),
                1,
            )
            accounted = CHECK.finding_counts(
                {"errs": 1, "warnings": 0}, {}, offline_terminology_errors=1
            )
            self.assertEqual(accounted.raw_errors, 1)
            self.assertEqual(accounted.offline_terminology_errors, 1)
            self.assertEqual(accounted.unsuppressed_errors, 0)

            near_misses = [
                qa_html(finding=message.replace("mimetypes|4.0.1", "other|4.0.1")),
                qa_html(finding=message.replace('because "tc" is null', "different failure")),
                qa_html(diagnostic="Terminology_TX_NoValid_3_CC"),
                qa_html(path="Observation.valueString (l1/c1)"),
                qa_html(publisher="2.3.4"),
            ]
            for html_text in near_misses:
                with self.subTest(html_text=html_text):
                    matched = write_case(html_text)
                    self.assertEqual(matched, 0)
                    self.assertEqual(
                        CHECK.finding_counts(
                            {"errs": 1, "warnings": 0}, {}, matched
                        ).unsuppressed_errors,
                        1,
                    )

            unregistered = json.loads(json.dumps(document))
            unregistered["content"][0]["attachment"]["contentType"] = "text/plain"
            unregistered_count = write_case(
                qa_html(finding=message.replace("application/json", "text/plain")),
                unregistered,
            )
            self.assertEqual(unregistered_count, 0)
            self.assertEqual(
                CHECK.finding_counts(
                    {"errs": 1, "warnings": 0}, {}, unregistered_count
                ).unsuppressed_errors,
                1,
            )

            observation_name = "Observation-Example"
            observation_count = write_case(
                qa_html(filename=observation_name),
                {"resourceType": "Observation"},
                observation_name,
            )
            self.assertEqual(observation_count, 0)
            self.assertEqual(
                CHECK.finding_counts(
                    {"errs": 1, "warnings": 0}, {}, observation_count
                ).unsuppressed_errors,
                1,
            )

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

    def test_exact_package_age_suppression_may_be_absent_online(self) -> None:
        message = (
            "WARNING: ImplementationGuide/org.example.fhir.guide: "
            "ImplementationGuide.dependsOn[2]: The ImplementationGuide uses package "
            "hl7.fhir.uv.extensions.r4#5.3.0 released on 2026-05-16, but the "
            "most recent appropriate version is 5.3.0-ballot-tc1. This reference "
            "is getting old and the more recent version should be considered"
        )
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve()
            (guide / "input").mkdir()
            (guide / "output").mkdir()
            (guide / "output/ImplementationGuide-org.example.fhir.guide.json").write_text(
                json.dumps(
                    {
                        "resourceType": "ImplementationGuide",
                        "id": "org.example.fhir.guide",
                        "dependsOn": [
                            {
                                "packageId": "hl7.terminology.r4",
                                "version": "7.3.0",
                            },
                            {"packageId": "hl7.fhir.uv.sdc", "version": "4.0.0"},
                            {
                                "packageId": "hl7.fhir.uv.extensions.r4",
                                "version": "5.3.0",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (guide / "input/ignoreWarnings.txt").write_text(
                f"== Suppressed Messages ==\n{message}\n", encoding="utf-8"
            )
            (guide / "output/qa.html").write_text(
                '<p>IG Publisher Version: v2.3.3</p>'
                '<a name="suppressed"> </a><ul><li>'
                f'{message} <span style="color: navy">(0 uses)</span></li></ul>'
                '<a name="sorted"> </a>',
                encoding="utf-8",
            )
            self.assertEqual(CHECK.validate_suppressions(guide), [])
            self.assertIn(
                "not exercised exactly",
                CHECK.validate_suppressions(
                    guide, offline_terminology=True
                )[0],
            )

            for changed in (
                message.replace("org.example.fhir.guide", "org.example.fhir.other"),
                message.replace("dependsOn[2]", "dependsOn[1]"),
                message.replace("hl7.fhir.uv.extensions.r4", "hl7.fhir.uv.extensions.r5"),
                message.replace("#5.3.0", "#5.2.0"),
                message.replace("2026-05-16", "2026-05-17"),
                message.replace("5.3.0-ballot-tc1", "5.3.0-ballot-tc"),
            ):
                with self.subTest(changed=changed):
                    (guide / "input/ignoreWarnings.txt").write_text(
                        f"== Suppressed Messages ==\n{changed}\n", encoding="utf-8"
                    )
                    self.assertIn(
                        "not exercised exactly",
                        CHECK.validate_suppressions(guide)[0],
                    )

    def test_rendered_liquid_failures_are_not_hidden_by_green_publisher_qa(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve() / "questionnaire"
            output = guide / "output/en"
            output.mkdir(parents=True)
            page = output / "measurements.html"
            page.write_text(
                "<html><body><p>Script /private/tmp/extraction-bundle.liquid: "
                "Unknown flow control statement 'unless forloop.last'</p></body></html>",
                encoding="utf-8",
            )
            problems = CHECK.validate_rendered_pages(guide)
            self.assertEqual(len(problems), 1)
            self.assertIn("output/en/measurements.html", problems[0])
            self.assertIn("Unknown flow control statement", problems[0])

            page.write_text(
                "<html><body><p>The rendered Bundle contains eight resources.</p>"
                "</body></html>",
                encoding="utf-8",
            )
            self.assertEqual(CHECK.validate_rendered_pages(guide), [])

    def test_offline_no_service_warnings_require_pinned_resource_codings(self) -> None:
        def qa_html(
            system: str,
            code: str,
            *,
            diagnostic: str = (
                "Error_validating_code_running_without_terminology_services"
            ),
            publisher: str = "2.3.3",
            message_suffix: str = "",
        ) -> str:
            message = (
                f"Unable to validate code '{code}' in system '{system}' because the "
                f"validator is running without terminology services{message_suffix}"
            )
            return (
                f"<p>IG Publisher Version: v{publisher}</p>"
                '<h2><a href="Observation-Example.html">fsh-generated/resources/'
                "Observation-Example.json</a></h2><table>"
                '<tr style="background-color: #fff4c2">'
                "<td><b>Observation.value.ofType(Quantity) (l1/c1)</b></td>"
                "<td><b>warning</b></td>"
                f'<td><b>{message}</b> <span class="code-value">{diagnostic}</span></td>'
                "<td>profile</td></tr></table>"
            )

        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve() / "guide"
            resources = guide / "fsh-generated/resources"
            output = guide / "output"
            resources.mkdir(parents=True)
            output.mkdir()

            def write_case(
                system: str,
                code: str,
                *,
                html_text: str | None = None,
                resource_code: str | None = None,
            ) -> int:
                resource = {
                    "resourceType": "Observation",
                    "valueQuantity": {
                        "system": system,
                        "code": resource_code if resource_code is not None else code,
                    },
                }
                (resources / "Observation-Example.json").write_text(
                    json.dumps(resource), encoding="utf-8"
                )
                (output / "qa.html").write_text(
                    html_text if html_text is not None else qa_html(system, code),
                    encoding="utf-8",
                )
                return CHECK.offline_no_service_warning_count(guide)

            valid = (
                ("http://unitsofmeasure.org", "kg"),
                ("http://loinc.org", "8867-4"),
                ("http://snomed.info/sct", "24484000"),
            )
            for system, code in valid:
                with self.subTest(system=system, code=code):
                    matched = write_case(system, code)
                    self.assertEqual(matched, 1)
                    counts = CHECK.finding_counts(
                        {"errs": 0, "warnings": 1},
                        {},
                        offline_terminology_warnings=matched,
                    )
                    self.assertEqual(counts.offline_terminology_warnings, 1)
                    self.assertEqual(counts.unsuppressed_warnings, 0)

            near_misses = (
                (
                    "http://loinc.org",
                    "999999-9",
                    qa_html("http://loinc.org", "999999-9"),
                    None,
                ),
                (
                    "http://unitsofmeasure.org",
                    "{private}",
                    qa_html("http://unitsofmeasure.org", "{private}"),
                    None,
                ),
                (
                    "https://example.org/system",
                    "kg",
                    qa_html("https://example.org/system", "kg"),
                    None,
                ),
                (
                    "http://unitsofmeasure.org",
                    "kg",
                    qa_html(
                        "http://unitsofmeasure.org",
                        "kg",
                        diagnostic="Terminology_TX_NoValid_16",
                    ),
                    None,
                ),
                (
                    "http://unitsofmeasure.org",
                    "kg",
                    qa_html(
                        "http://unitsofmeasure.org",
                        "kg",
                        publisher="2.3.4",
                    ),
                    None,
                ),
                (
                    "http://unitsofmeasure.org",
                    "kg",
                    qa_html(
                        "http://unitsofmeasure.org",
                        "kg",
                        message_suffix=" unexpectedly",
                    ),
                    None,
                ),
                (
                    "http://unitsofmeasure.org",
                    "kg",
                    qa_html("http://unitsofmeasure.org", "kg"),
                    "g",
                ),
            )
            for system, code, html_text, resource_code in near_misses:
                with self.subTest(system=system, code=code, html_text=html_text):
                    matched = write_case(
                        system,
                        code,
                        html_text=html_text,
                        resource_code=resource_code,
                    )
                    self.assertEqual(matched, 0)
                    self.assertEqual(
                        CHECK.finding_counts(
                            {"errs": 0, "warnings": 1},
                            {},
                            offline_terminology_warnings=matched,
                        ).unsuppressed_warnings,
                        1,
                    )

    def test_unknown_system_warnings_are_exact_and_resource_backed(self) -> None:
        message = (
            "A definition for CodeSystem '{system}' could not be found, so the "
            "code cannot be validated"
        )

        def qa_html(
            filename: str,
            path: str,
            system: str,
            diagnostic: str,
            *,
            publisher: str = "2.3.3",
        ) -> str:
            return (
                f"<p>IG Publisher Version: v{publisher}</p>"
                f'<h2><a href="{filename}.html">fsh-generated/resources/'
                f"{filename}.json</a></h2><table>"
                '<tr style="background-color: #fff4c2">'
                f"<td><b>{path}</b></td><td><b>warning</b></td>"
                f"<td><b>{message.format(system=system)}</b> "
                f'<span class="code-value">{diagnostic}</span></td>'
                "<td>profile</td></tr></table>"
            )

        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve() / "guide"
            output = guide / "output"
            output.mkdir(parents=True)

            def write_case(
                filename: str,
                resource: dict[str, object],
                html_text: str,
            ) -> int:
                (output / f"{filename}.json").write_text(
                    json.dumps(resource), encoding="utf-8"
                )
                (output / "qa.html").write_text(html_text, encoding="utf-8")
                return CHECK.offline_unknown_code_system_warning_count(guide)

            implementation_guide = "ImplementationGuide-example"
            language_html = qa_html(
                implementation_guide,
                "ImplementationGuide.language.system (l1/c1)",
                "urn:ietf:bcp:47",
                "UNKNOWN_CODESYSTEM",
            )
            self.assertEqual(
                write_case(
                    implementation_guide,
                    {"resourceType": "ImplementationGuide", "language": "en"},
                    language_html,
                ),
                1,
            )
            primitive_language_html = qa_html(
                implementation_guide,
                "ImplementationGuide.language (l1/c1)",
                "urn:ietf:bcp:47",
                "",
            )
            self.assertEqual(
                write_case(
                    implementation_guide,
                    {"resourceType": "ImplementationGuide", "language": "en"},
                    primitive_language_html,
                ),
                1,
            )

            observation = "Observation-example"
            iso_html = qa_html(
                observation,
                "Observation.component[0].code.coding[0].system (l1/c1)",
                "urn:iso:std:iso:11073:10101",
                "UNKNOWN_CODESYSTEM",
            )
            iso_resource = {
                "resourceType": "Observation",
                "component": [{
                    "code": {"coding": [{
                        "system": "urn:iso:std:iso:11073:10101",
                        "code": "131329",
                    }]},
                }],
            }
            self.assertEqual(write_case(observation, iso_resource, iso_html), 1)
            self.assertEqual(
                set(CHECK.iso_11073_evidence()),
                {"131329", "150452", "531975", "531976"},
            )

            bundle = "Bundle-example"
            bundle_resource = {
                "resourceType": "Bundle",
                "entry": [{
                    "resource": {
                        "resourceType": "Device",
                        "id": "device-example",
                        "version": [{
                            "type": {"coding": [{
                                "system": "urn:iso:std:iso:11073:10101",
                                "code": "531976",
                                "display": "MDC_ID_PROD_SPEC_FW",
                            }]},
                        }],
                    },
                }],
            }
            bundle_html = qa_html(
                bundle,
                "Bundle.entry[0].resource/*Device/device-example*/.version[0]."
                "type.coding[0].system (l1/c1)",
                "urn:iso:std:iso:11073:10101",
                "UNKNOWN_CODESYSTEM",
            )
            self.assertEqual(write_case(bundle, bundle_resource, bundle_html), 1)

            structure = "StructureDefinition-example"
            structure_resource = {
                "resourceType": "StructureDefinition",
                "snapshot": {"element": [{
                    "patternCodeableConcept": {"coding": [{
                        "system": "urn:iso:std:iso:11073:10101",
                        "code": "131329",
                    }]},
                }]},
            }
            structure_html = qa_html(
                structure,
                "StructureDefinition.snapshot.element[0].pattern."
                "ofType(CodeableConcept).coding[0].system (l1/c1)",
                "urn:iso:std:iso:11073:10101",
                "UNKNOWN_CODESYSTEM",
            )
            self.assertEqual(
                write_case(structure, structure_resource, structure_html), 1
            )

            ucum_resource = {
                "resourceType": "Observation",
                "valueQuantity": {
                    "value": 70,
                    "system": "http://unitsofmeasure.org",
                    "code": "kg",
                },
            }
            ucum_system_html = qa_html(
                observation,
                "Observation.value.ofType(Quantity).code.system (l1/c1)",
                "http://unitsofmeasure.org",
                "UNKNOWN_CODESYSTEM",
            )
            self.assertEqual(
                write_case(observation, ucum_resource, ucum_system_html), 1
            )
            ucum_code_html = qa_html(
                observation,
                "Observation.value.ofType(Quantity).code (l1/c1)",
                "http://unitsofmeasure.org",
                "",
            )
            self.assertEqual(write_case(observation, ucum_resource, ucum_code_html), 1)

            near_misses = (
                (
                    implementation_guide,
                    {"resourceType": "ImplementationGuide", "language": "fr"},
                    language_html,
                ),
                (
                    implementation_guide,
                    {"resourceType": "ImplementationGuide", "language": "en"},
                    qa_html(
                        implementation_guide,
                        "ImplementationGuide.language.system (l1/c1)",
                        "urn:ietf:bcp:47",
                        "different-diagnostic",
                    ),
                ),
                (
                    observation,
                    {"resourceType": "Observation"},
                    iso_html,
                ),
                (
                    observation,
                    {
                        "resourceType": "Observation",
                        "component": [{
                            "code": {"coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "8867-4",
                                },
                                {
                                    "system": "urn:iso:std:iso:11073:10101",
                                    "code": "131329",
                                },
                            ]},
                        }],
                    },
                    iso_html,
                ),
                (
                    observation,
                    {
                        "resourceType": "Observation",
                        "component": [{
                            "code": {"coding": [{
                                "system": "urn:iso:std:iso:11073:10101",
                                "code": "131330",
                            }]},
                        }],
                    },
                    iso_html,
                ),
                (
                    observation,
                    iso_resource,
                    qa_html(
                        observation,
                        "Observation.component[0].code.coding[0].code (l1/c1)",
                        "urn:iso:std:iso:11073:10101",
                        "UNKNOWN_CODESYSTEM",
                    ),
                ),
                (
                    observation,
                    iso_resource,
                    qa_html(
                        observation,
                        "Observation.component[0].code.coding[0].system (l1/c1)",
                        "https://example.org/unknown",
                        "UNKNOWN_CODESYSTEM",
                    ),
                ),
                (
                    observation,
                    iso_resource,
                    qa_html(
                        observation,
                        "Observation.component[0].code.coding[0].system (l1/c1)",
                        "urn:iso:std:iso:11073:10101",
                        "UNKNOWN_CODESYSTEM",
                        publisher="2.3.4",
                    ),
                ),
                (
                    bundle,
                    bundle_resource,
                    qa_html(
                        bundle,
                        "Bundle.entry[0].resource/*Device/wrong-id*/.version[0]."
                        "type.coding[0].system (l1/c1)",
                        "urn:iso:std:iso:11073:10101",
                        "UNKNOWN_CODESYSTEM",
                    ),
                ),
                (
                    observation,
                    {
                        "resourceType": "Observation",
                        "valueQuantity": {
                            "system": "http://unitsofmeasure.org",
                            "code": "{private}",
                        },
                    },
                    ucum_system_html,
                ),
                (
                    observation,
                    ucum_resource,
                    qa_html(
                        observation,
                        "Observation.value.ofType(Quantity).code (l1/c1)",
                        "http://unitsofmeasure.org",
                        "UNKNOWN_CODESYSTEM",
                    ),
                ),
            )
            for filename, resource, html_text in near_misses:
                with self.subTest(filename=filename, html_text=html_text):
                    self.assertEqual(write_case(filename, resource, html_text), 0)

    def test_codeable_concept_warnings_require_exact_paths_and_pinned_codes(self) -> None:
        message = (
            'Error Cannot invoke &quot;org.hl7.fhir.r5.terminologies.client.'
            'TerminologyClientContext.getAddress()&quot; because &quot;tc&quot; is null '
            "validating CodeableConcept"
        )

        def qa_html(
            filename: str,
            path: str,
            *,
            diagnostic: str = "Terminology_TX_Error_CodeableConcept",
            finding: str = message,
            publisher: str = "2.3.3",
        ) -> str:
            return (
                f"<p>IG Publisher Version: v{publisher}</p>"
                f'<h2><a href="{filename}.html">fsh-generated/resources/'
                f"{filename}.json</a></h2><table>"
                '<tr style="background-color: #fff4c2">'
                f"<td><b>{path}</b></td><td><b>warning</b></td>"
                f'<td><b>{finding}</b> <span class="code-value">{diagnostic}</span></td>'
                "<td>profile</td></tr></table>"
            )

        with tempfile.TemporaryDirectory() as directory:
            guide = Path(directory).resolve() / "guide"
            resources = guide / "fsh-generated/resources"
            output = guide / "output"
            resources.mkdir(parents=True)
            output.mkdir()

            def write_case(
                filename: str,
                source: dict[str, object],
                publisher: dict[str, object],
                html_text: str,
            ) -> int:
                (resources / f"{filename}.json").write_text(
                    json.dumps(source), encoding="utf-8"
                )
                (output / f"{filename}.json").write_text(
                    json.dumps(publisher), encoding="utf-8"
                )
                (output / "qa.html").write_text(html_text, encoding="utf-8")
                return CHECK.offline_codeable_concept_warning_count(guide)

            observation = "Observation-example"
            observation_resource = {
                "resourceType": "Observation",
                "code": {"coding": [{
                    "system": "http://loinc.org",
                    "code": "8867-4",
                }]},
            }
            observation_html = qa_html(
                observation, "Observation.code (l1/c1)"
            )
            self.assertEqual(
                write_case(
                    observation,
                    observation_resource,
                    observation_resource,
                    observation_html,
                ),
                1,
            )

            structure = "StructureDefinition-example"
            source_structure = {
                "resourceType": "StructureDefinition",
                "differential": {"element": []},
            }
            publisher_structure = {
                "resourceType": "StructureDefinition",
                "snapshot": {"element": [{
                    "patternCodeableConcept": {"coding": [{
                        "system": "http://loinc.org",
                        "code": "8867-4",
                    }]},
                }]},
                "differential": {"element": []},
            }
            structure_html = qa_html(
                structure,
                "StructureDefinition.snapshot.element[0].pattern."
                "ofType(CodeableConcept) (l1/c1)",
            )
            self.assertEqual(
                write_case(
                    structure, source_structure, publisher_structure, structure_html
                ),
                1,
            )

            invalid_code = json.loads(json.dumps(observation_resource))
            invalid_code["code"]["coding"][0]["code"] = "999999-9"
            near_misses = (
                (
                    observation,
                    invalid_code,
                    invalid_code,
                    observation_html,
                ),
                (
                    observation,
                    observation_resource,
                    observation_resource,
                    qa_html(
                        observation,
                        "Observation.valueCodeableConcept (l1/c1)",
                    ),
                ),
                (
                    observation,
                    observation_resource,
                    observation_resource,
                    qa_html(
                        observation,
                        "Observation.code (l1/c1)",
                        diagnostic="different-diagnostic",
                    ),
                ),
                (
                    observation,
                    observation_resource,
                    observation_resource,
                    qa_html(
                        observation,
                        "Observation.code (l1/c1)",
                        finding=message.replace("tc", "client"),
                    ),
                ),
                (
                    structure,
                    source_structure,
                    publisher_structure,
                    qa_html(
                        structure,
                        "StructureDefinition.snapshot.element[1].pattern."
                        "ofType(CodeableConcept) (l1/c1)",
                    ),
                ),
                (
                    observation,
                    observation_resource,
                    observation_resource,
                    qa_html(
                        observation,
                        "Observation.code (l1/c1)",
                        publisher="2.3.4",
                    ),
                ),
            )
            for filename, source, publisher, html_text in near_misses:
                with self.subTest(filename=filename, html_text=html_text):
                    self.assertEqual(
                        write_case(filename, source, publisher, html_text), 0
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
