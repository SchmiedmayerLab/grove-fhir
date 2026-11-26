"""Admission and rejection cases for source-neutral Clinical Records documents and attachments."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

from Scripts.producer_validation import clinical_records, context, exchange_bundle
from Scripts.producer_validation.diagnostics import ProducerValidationError


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "Conformance/corpora/clinical-records"
DOCUMENT = context.CLINICAL_RECORD_DOCUMENT_PROFILE
ATTACHMENT = context.CLINICAL_RECORD_ATTACHMENT_PROFILE
PAYLOAD_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-payload-format"
ROLE_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
DOCUMENT_URL = "urn:uuid:00000000-0000-5000-8000-000000000401"
ATTACHMENT_URL = "urn:uuid:00000000-0000-5000-8000-000000000402"
OTHER_DOCUMENT_URL = "urn:uuid:00000000-0000-5000-8000-000000000403"
REGISTRY = json.loads((ROOT / "catalog/format-registry.json").read_text(encoding="utf-8"))


def load(name: str) -> dict[str, Any]:
    return json.loads((CORPUS / f"{name}.json").read_text(encoding="utf-8"))


def admit(resource: dict[str, Any]) -> None:
    exchange_bundle.validate_resource_profile_claims(resource, "Clinical", set())


def with_payload(document: dict[str, Any], payload: bytes, content_type: str) -> dict[str, Any]:
    attachment = document["content"][0]["attachment"]
    attachment["contentType"] = content_type
    attachment["data"] = base64.b64encode(payload).decode()
    attachment["size"] = len(payload)
    attachment["hash"] = base64.b64encode(
        hashlib.sha1(payload).digest()  # noqa: S324 -- FHIR R4 Attachment.hash
    ).decode()
    return document


def role(resource: dict[str, Any], code: str) -> dict[str, Any]:
    return next(
        item for item in resource["identifier"]
        if item["type"]["coding"][0] == {"system": ROLE_SYSTEM, "code": code}
    )


class ClinicalRecordDocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load("document")

    def test_the_corpus_document_and_attachment_are_admitted(self) -> None:
        admit(self.document)
        admit(load("attachment"))

    def test_any_declared_fhir_release_is_admitted_under_one_format(self) -> None:
        payloads = {
            "DSTU2": (b'{"resourceType":"AllergyIntolerance","status":"confirmed"}', "1.0"),
            "R4": (b'{"resourceType":"AllergyIntolerance","clinicalStatus":{}}', "4.0"),
            "R5": (b'{"resourceType":"AllergyIntolerance","type":{}}', "5.0"),
        }
        for release, (payload, version) in payloads.items():
            with self.subTest(release=release):
                document = with_payload(
                    copy.deepcopy(self.document),
                    payload,
                    f"application/fhir+json; fhirVersion={version}",
                )
                self.assertEqual(
                    document["content"][0]["format"],
                    {"system": PAYLOAD_SYSTEM, "code": "provider-issued-fhir-json",
                     "display": "Provider-Issued FHIR JSON"},
                )
                admit(document)

    def test_a_missing_or_malformed_fhir_version_is_rejected(self) -> None:
        payload = b'{"resourceType":"AllergyIntolerance"}'
        for content_type in (
            "application/fhir+json",
            "application/fhir+json; fhirVersion=4",
            "application/fhir+json; fhirversion=4.0",
            "application/fhir+json;fhirVersion=4.0",
            "application/json; fhirVersion=4.0",
        ):
            with self.subTest(content_type=content_type), self.assertRaisesRegex(
                ProducerValidationError, "declaring its FHIR release in the fhirVersion parameter"
            ):
                admit(with_payload(copy.deepcopy(self.document), payload, content_type))

    def test_the_release_pattern_is_the_registry_pattern(self) -> None:
        entry = REGISTRY["formats"]["provider-issued-fhir-json"]
        self.assertEqual(entry["owner"], "clinical-records")
        self.assertEqual(entry["contentTypeRule"], "declared-fhir-release")
        profiles = (ROOT / "clinical-records/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        # The FHIRPath invariant spells the same grammar without backslash escapes.
        self.assertIn(
            "'^application/fhir[+]json; fhirVersion=[0-9]+[.][0-9]+$'", profiles
        )

    def test_a_cda_document_is_cda_r2_xml(self) -> None:
        payload = b'<?xml version="1.0"?><ClinicalDocument xmlns="urn:hl7-org:v3"/>'
        document = with_payload(copy.deepcopy(self.document), payload, "application/hl7-cda+xml")
        document["content"][0]["format"] = {"system": PAYLOAD_SYSTEM, "code": "cda-document"}
        admit(document)
        document["content"][0]["attachment"]["contentType"] = "text/xml"
        with self.assertRaisesRegex(ProducerValidationError, "does not match registry format"):
            admit(document)

    def test_a_clinical_record_document_admits_only_clinical_formats(self) -> None:
        for code, owner in (("native-recording-json", "sensor"), ("source-file", "mobile")):
            document = copy.deepcopy(self.document)
            document["content"][0]["format"] = {"system": PAYLOAD_SYSTEM, "code": code}
            with self.subTest(code=code), self.assertRaisesRegex(
                ProducerValidationError, f"belongs to the {owner} guide"
            ):
                admit(document)

    def test_the_retired_sensor_format_system_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["content"][0]["format"] = {
            "system": REGISTRY["previousCodings"]["system"],
            "code": "fhir-resource",
        }
        with self.assertRaisesRegex(ProducerValidationError, "payload-format registry"):
            admit(document)


class ClinicalRecordAttachmentGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load("document")
        self.attachment = load("attachment")

    def graph(self, *documents: tuple[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        resources = dict(documents)
        resources[ATTACHMENT_URL] = self.attachment
        return resources

    def validate(self, resources: dict[str, dict[str, Any]]) -> None:
        clinical_records.validate_clinical_record_attachment_graph(
            list(resources.values()), resources, "Bundle"
        )

    def test_an_attachment_appends_to_its_own_records_document(self) -> None:
        self.attachment["relatesTo"][0]["target"]["reference"] = DOCUMENT_URL
        self.validate(self.graph((DOCUMENT_URL, self.document)))

    def test_a_companion_linked_to_another_records_document_is_rejected(self) -> None:
        other = copy.deepcopy(self.document)
        role(other, "source-record")["value"] = "v0:test-key:1:" + "B" * 43
        role(other, "source-output")["value"] = "v0:test-key:1:" + "C" * 43
        self.attachment["relatesTo"][0]["target"]["reference"] = OTHER_DOCUMENT_URL
        with self.assertRaises(ProducerValidationError) as raised:
            self.validate(self.graph((DOCUMENT_URL, self.document), (OTHER_DOCUMENT_URL, other)))
        self.assertEqual(raised.exception.diagnostic["code"], "clinical-record.attachment-graph")
        self.assertIn("share the source-record identity", str(raised.exception))

    def test_an_attachment_must_point_at_a_clinical_record_document(self) -> None:
        for target in ("missing", "attachment", "recording"):
            with self.subTest(target=target):
                attachment = copy.deepcopy(self.attachment)
                resources = {DOCUMENT_URL: self.document, ATTACHMENT_URL: attachment}
                if target == "attachment":
                    attachment["relatesTo"][0]["target"]["reference"] = ATTACHMENT_URL
                elif target == "recording":
                    recording = copy.deepcopy(self.document)
                    recording["meta"]["profile"] = [context.SENSOR_RECORDING_PROFILE]
                    resources[OTHER_DOCUMENT_URL] = recording
                    attachment["relatesTo"][0]["target"]["reference"] = OTHER_DOCUMENT_URL
                else:
                    attachment["relatesTo"][0]["target"]["reference"] = OTHER_DOCUMENT_URL
                with self.assertRaises(ProducerValidationError) as raised:
                    clinical_records.validate_clinical_record_attachment_graph(
                        list(resources.values()), resources, "Bundle"
                    )
                self.assertIn("in the same Bundle", str(raised.exception))

    def test_an_adapter_attachment_appends_only_to_its_adapters_document(self) -> None:
        healthkit = context.HEALTHKIT_CLINICAL_ATTACHMENT_PROFILE
        self.attachment["meta"]["profile"].append(healthkit)
        self.attachment["relatesTo"][0]["target"]["reference"] = DOCUMENT_URL
        with self.assertRaisesRegex(ProducerValidationError, "of its own adapter"):
            self.validate(self.graph((DOCUMENT_URL, self.document)))

    def test_a_source_neutral_attachment_carries_no_adapter_source_type(self) -> None:
        self.attachment["extension"] = [{
            "url": "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-source-type",
            "valueCode": "HKClinicalTypeIdentifierClinicalNoteRecord",
        }]
        self.attachment["relatesTo"][0]["target"]["reference"] = DOCUMENT_URL
        with self.assertRaisesRegex(ProducerValidationError, "source type of its clinical"):
            self.validate(self.graph((DOCUMENT_URL, self.document)))

    def test_the_example_attachment_names_its_file_by_archive_path(self) -> None:
        url = self.attachment["content"][0]["attachment"]["url"]
        self.assertRegex(url, r"^documents/[0-9a-f]{64}\.pdf$")
        self.assertEqual(self.attachment["content"][0]["format"]["code"], "source-file")
        self.assertEqual(self.attachment["relatesTo"][0]["code"], "appends")


if __name__ == "__main__":
    unittest.main()
