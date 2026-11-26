"""Admission and rejection cases for HealthKit clinical-record attachment documents."""

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

from Scripts.producer_validation import clinical_records, context, exchange_bundle, identity
from Scripts.producer_validation.diagnostics import ProducerValidationError


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "Conformance/corpora/healthkit-clinical-attachment"
CLINICAL = context.HEALTHKIT_CLINICAL_RECORD_PROFILE
ATTACHMENT = context.HEALTHKIT_CLINICAL_ATTACHMENT_PROFILE
ROLE_SYSTEM = "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
DOCUMENT_URL = "urn:uuid:00000000-0000-5000-8000-000000000301"
ATTACHMENT_URL = "urn:uuid:00000000-0000-5000-8000-000000000302"
SECOND_ATTACHMENT_URL = "urn:uuid:00000000-0000-5000-8000-000000000303"


def load(name: str) -> dict[str, Any]:
    return json.loads((CORPUS / f"{name}.json").read_text(encoding="utf-8"))


def role(resource: dict[str, Any], code: str) -> dict[str, Any]:
    return next(
        item for item in resource["identifier"]
        if (item.get("type") or {"coding": [{}]})["coding"][0]
        == {"system": ROLE_SYSTEM, "code": code}
    )


def bundled(document: dict[str, Any], *attachments: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The documents under Bundle fullUrls, each attachment appending to the document."""
    resources = {DOCUMENT_URL: document}
    for url, attachment in zip((ATTACHMENT_URL, SECOND_ATTACHMENT_URL), attachments, strict=False):
        attachment["relatesTo"][0]["target"]["reference"] = DOCUMENT_URL
        resources[url] = attachment
    return resources


def validate_graph(resources: dict[str, dict[str, Any]]) -> None:
    clinical_records.validate_clinical_record_attachment_graph(
        list(resources.values()), resources, "Bundle"
    )


class HealthKitClinicalAttachmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load("document")
        self.attachment = load("attachment")
        self.catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )

    def admit(self, resource: dict[str, Any]) -> None:
        exchange_bundle.validate_resource_profile_claims(
            resource, "Attachment", {CLINICAL, ATTACHMENT}
        )

    def test_corpus_documents_are_admitted(self) -> None:
        self.admit(self.document)
        self.admit(self.attachment)

    def test_contract_names_the_profile_format_role_and_relationship(self) -> None:
        contract = self.catalog["clinicalRecordAdmission"]["attachments"]
        self.assertEqual(contract["profile"], ATTACHMENT)
        self.assertEqual(contract["payloadFormat"], "source-file")
        self.assertEqual(contract["outputRole"], "clinical-record-attachment")
        self.assertEqual(contract["relationship"]["code"], "appends")
        self.assertEqual(
            contract["relationship"]["direction"], "attachment-to-clinical-record-only"
        )
        self.assertIn("Never skip a file for its size", contract["rule"])
        for row in self.catalog["rows"]:
            if row["sourceTypeIdentifier"].startswith("HKClinicalTypeIdentifier"):
                with self.subTest(row=row["sourceTypeIdentifier"]):
                    self.assertEqual(row["profiles"], [CLINICAL, ATTACHMENT])

    def test_inline_file_bytes_are_admitted_and_integrity_checked(self) -> None:
        payload = b"%PDF-1.7\n%%EOF\n"
        inline = copy.deepcopy(self.attachment)
        attachment = inline["content"][0]["attachment"]
        del attachment["url"]
        attachment["data"] = base64.b64encode(payload).decode()
        attachment["size"] = len(payload)
        attachment["hash"] = base64.b64encode(
            hashlib.sha1(payload).digest()  # noqa: S324 -- FHIR R4 Attachment.hash
        ).decode()
        self.admit(inline)

        tampered = copy.deepcopy(inline)
        tampered["content"][0]["attachment"]["size"] = len(payload) + 1
        with self.assertRaisesRegex(ProducerValidationError, "size does not match"):
            self.admit(tampered)

        both = copy.deepcopy(inline)
        both["content"][0]["attachment"]["url"] = self.attachment["content"][0]["attachment"]["url"]
        with self.assertRaisesRegex(ProducerValidationError, "exactly one of data or url"):
            self.admit(both)

    def test_any_lowercase_media_type_is_admitted_and_nothing_else(self) -> None:
        for content_type in (
            "image/jpeg",
            "text/rtf",
            "application/octet-stream",
            "text/plain; charset=utf-8",
        ):
            admitted = copy.deepcopy(self.attachment)
            admitted["content"][0]["attachment"]["contentType"] = content_type
            with self.subTest(content_type=content_type):
                self.admit(admitted)
        for content_type in ("Application/PDF", "pdf", "application/pdf;charset=utf-8"):
            rejected = copy.deepcopy(self.attachment)
            rejected["content"][0]["attachment"]["contentType"] = content_type
            with self.subTest(content_type=content_type), self.assertRaisesRegex(
                ProducerValidationError, "lowercase IANA media type"
            ):
                self.admit(rejected)

    def test_the_payload_is_exactly_one_source_file(self) -> None:
        wrong_format = copy.deepcopy(self.attachment)
        wrong_format["content"][0]["format"]["code"] = "provider-issued-fhir-json"
        with self.assertRaisesRegex(ProducerValidationError, "exactly one source-file payload"):
            self.admit(wrong_format)

        two_contents = copy.deepcopy(self.attachment)
        two_contents["content"].append(copy.deepcopy(two_contents["content"][0]))
        with self.assertRaisesRegex(ProducerValidationError, "exactly one source-file payload"):
            self.admit(two_contents)

    def test_source_file_is_never_a_recording_format(self) -> None:
        recording = copy.deepcopy(self.attachment)
        recording["meta"]["profile"] = [context.SENSOR_RECORDING_PROFILE]
        del recording["relatesTo"]
        del recording["extension"]
        with self.assertRaisesRegex(
            ProducerValidationError, "admits only formats the sensor guide owns"
        ):
            exchange_bundle.validate_resource_profile_claims(
                recording, "Recording", set()
            )

    def test_the_relationship_is_one_literal_appends(self) -> None:
        cases = {
            "missing": lambda resource: resource.pop("relatesTo"),
            "replaces": lambda resource: resource["relatesTo"][0].update(code="replaces"),
            "identifier-only": lambda resource: resource["relatesTo"][0].update(
                target={"identifier": role(self.document, "source-output")}
            ),
            "two": lambda resource: resource["relatesTo"].append(
                copy.deepcopy(resource["relatesTo"][0])
            ),
        }
        for name, mutate in cases.items():
            invalid = copy.deepcopy(self.attachment)
            mutate(invalid)
            with self.subTest(case=name), self.assertRaises(ProducerValidationError) as raised:
                self.admit(invalid)
            self.assertEqual(
                raised.exception.diagnostic["code"], "clinical-record.attachment-graph"
            )

    def test_only_the_primary_output_carries_writer_or_native_identity(self) -> None:
        writer = copy.deepcopy(self.attachment)
        writer["identifier"].append(copy.deepcopy(role(self.attachment, "source-output")))
        writer["identifier"][-1]["type"]["coding"][0]["code"] = "writer-record"
        writer["identifier"][-1]["system"] = (
            "https://study.example.org/fhir/NamingSystem/grove-writer-record-v0/test-key/1"
        )
        writer["extension"].append({
            "url": clinical_records.WRITER_RECORD_VERSION_EXTENSION,
            "valueString": "1",
        })
        with self.assertRaisesRegex(ProducerValidationError, "no writer record"):
            self.admit(writer)

        for partial in ("identifier", "version"):
            half = copy.deepcopy(writer)
            if partial == "identifier":
                half["extension"].pop()
            else:
                half["identifier"].pop()
            with self.subTest(partial=partial), self.assertRaisesRegex(
                ProducerValidationError, "writer"
            ):
                self.admit(half)

        native = next(item for item in self.document["identifier"] if "type" not in item)
        with_native = copy.deepcopy(self.attachment)
        with_native["identifier"].append(copy.deepcopy(native))
        with self.assertRaisesRegex(ProducerValidationError, "native identifier"):
            self.admit(with_native)

    def test_the_clinical_document_stays_primary_beside_its_attachments(self) -> None:
        second = copy.deepcopy(self.attachment)
        role(second, "source-output")["value"] = "v0:test-key:1:" + "S" * 43
        outputs = [self.document, self.attachment, second]
        designated = context.EXCHANGE_PROTOCOL["governedSourceIdentifier"]["validation"][
            "designatedNode"
        ]
        self.assertIs(identity.catalog_designated_primary(outputs, designated), self.document)
        identity.validate_governed_source_identifiers(outputs, "Record")

        native = next(item for item in self.document["identifier"] if "type" not in item)
        moved = copy.deepcopy(self.attachment)
        moved["identifier"].append(copy.deepcopy(native))
        without_native = copy.deepcopy(self.document)
        without_native["identifier"].remove(native)
        with self.assertRaisesRegex(ProducerValidationError, "catalog-designated primary"):
            identity.validate_governed_source_identifiers([without_native, moved], "Record")

    def test_attachments_append_to_their_own_records_clinical_document(self) -> None:
        second = copy.deepcopy(self.attachment)
        role(second, "source-output")["value"] = "v0:test-key:1:" + "S" * 43
        validate_graph(bundled(self.document, copy.deepcopy(self.attachment), second))

        def failing(resources: dict[str, dict[str, Any]], message: str) -> None:
            with self.assertRaises(ProducerValidationError) as raised:
                validate_graph(resources)
            self.assertEqual(
                raised.exception.diagnostic["code"], "clinical-record.attachment-graph"
            )
            self.assertIn(message, str(raised.exception))

        dangling = bundled(self.document, copy.deepcopy(self.attachment))
        dangling[ATTACHMENT_URL]["relatesTo"][0]["target"]["reference"] = (
            "urn:uuid:00000000-0000-5000-8000-000000000399"
        )
        failing(dangling, "in the same Bundle")

        other_record = bundled(copy.deepcopy(self.document), copy.deepcopy(self.attachment))
        role(other_record[DOCUMENT_URL], "source-record")["value"] = "v0:test-key:1:" + "R" * 43
        failing(other_record, "share the source-record identity")

        other_type = bundled(self.document, copy.deepcopy(self.attachment))
        other_type[ATTACHMENT_URL]["extension"][0]["valueCode"] = (
            "HKClinicalTypeIdentifierLabResultRecord"
        )
        failing(other_type, "source type")

        other_document_type = bundled(self.document, copy.deepcopy(self.attachment))
        other_document_type[ATTACHMENT_URL]["type"] = {
            "coding": [{
                "system": self.document["type"]["coding"][0]["system"],
                "code": "allergy-record",
            }]
        }
        self.assertNotEqual(self.document["type"]["coding"][0]["code"], "allergy-record")
        failing(other_document_type, "type coding")

        untyped = bundled(self.document, copy.deepcopy(self.attachment))
        del untyped[ATTACHMENT_URL]["type"]
        failing(untyped, "type coding")

        # The subject is the Bundle's single-subject rule's to judge, by what each reference
        # resolves to; optional Reference.type and display text never make two subjects differ.
        annotated_subject = bundled(self.document, copy.deepcopy(self.attachment))
        annotated_subject[ATTACHMENT_URL]["subject"] = {
            **self.document["subject"], "type": "Patient", "display": "Participant",
        }
        validate_graph(annotated_subject)

        duplicate = bundled(
            self.document, copy.deepcopy(self.attachment), copy.deepcopy(self.attachment)
        )
        failing(duplicate, "own source-output identity")

        onto_attachment = bundled(self.document, copy.deepcopy(self.attachment))
        onto_attachment[DOCUMENT_URL] = copy.deepcopy(self.attachment)
        failing(onto_attachment, "in the same Bundle")

    def test_attachments_state_the_date_authors_and_studies_of_their_document(self) -> None:
        study = {"reference": "ResearchStudy/HealthKitResearchStudyExample"}
        other_study = {"reference": "ResearchStudy/another-study"}
        device = {"reference": "Device/recording-device"}
        other_device = {"reference": "Device/another-device"}

        def pair(**document_fields: Any) -> tuple[dict[str, Any], dict[str, Any]]:
            document = copy.deepcopy(self.document)
            attachment = copy.deepcopy(self.attachment)
            for name in ("author", "context"):
                document.pop(name, None)
                attachment.pop(name, None)
            document.update(copy.deepcopy(document_fields))
            attachment.update(copy.deepcopy(document_fields))
            return document, attachment

        def failing(document: dict[str, Any], attachment: dict[str, Any], message: str) -> None:
            with self.assertRaises(ProducerValidationError) as raised:
                validate_graph(bundled(document, attachment))
            self.assertEqual(
                raised.exception.diagnostic["code"], "clinical-record.attachment-graph"
            )
            self.assertIn(message, str(raised.exception))

        # Equal fields pass, and so do fields both documents leave out.
        validate_graph(bundled(*pair()))
        validate_graph(bundled(*pair(author=[device], context={"related": [study]})))

        # Equal means naming the same targets: order, Reference.type, display, and the lexeme
        # of an equal instant do not matter.
        document, attachment = pair(
            author=[device, other_device], context={"related": [study, other_study]}
        )
        attachment["author"] = [{**other_device, "display": "Watch"}, {**device, "type": "Device"}]
        attachment["context"]["related"] = [other_study, study]
        attachment["date"] = "2026-08-20T19:07:01.000+02:00"
        self.assertEqual(document["date"], "2026-08-20T17:07:01Z")
        validate_graph(bundled(document, attachment))

        document, attachment = pair()
        attachment["date"] = "2026-08-20T17:07:02Z"
        failing(document, attachment, "date of its clinical record document")

        document, attachment = pair()
        del attachment["date"]
        failing(document, attachment, "date of its clinical record document")

        document, attachment = pair(author=[device])
        attachment["author"] = [other_device]
        failing(document, attachment, "authors of its clinical record document")

        document, attachment = pair(author=[device])
        del attachment["author"]
        failing(document, attachment, "authors of its clinical record document")

        document, attachment = pair()
        attachment["author"] = [device]
        failing(document, attachment, "authors of its clinical record document")

        document, attachment = pair(context={"related": [study]})
        attachment["context"]["related"] = [other_study]
        failing(document, attachment, "studies of its clinical record document")

        document, attachment = pair(context={"related": [study]})
        del attachment["context"]
        failing(document, attachment, "studies of its clinical record document")

        document, attachment = pair()
        attachment["context"] = {"related": [study]}
        failing(document, attachment, "studies of its clinical record document")


if __name__ == "__main__":
    unittest.main()
