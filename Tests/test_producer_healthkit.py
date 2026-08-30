"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import hashlib
from typing import Any

from Scripts.producer_validation import (
    context,
    diagnostics,
    exchange_bundle,
    graphs,
    healthkit as healthkit_validation,
    profiles as profile_validation,
)
from Tests.producer_validation_test_support import (
    ProducerValidationTestCase,
    ROOT,
    copy,
    derive_hmac_identity,
    json,
    typed_identifier,
)

class ProducerHealthkitTests(ProducerValidationTestCase):
    @staticmethod
    def _clinical_document(
        release: str = "r4",
        payload: bytes = b'{"resourceType":"AllergyIntolerance"}',
    ) -> dict[str, Any]:
        content_type_by_release = {
            "dstu2": "application/fhir+json; fhirVersion=1.0",
            "r4": "application/fhir+json; fhirVersion=4.0",
        }
        return {
            "resourceType": "DocumentReference",
            "meta": {"profile": [context.HEALTHKIT_CLINICAL_RECORD_PROFILE]},
            "identifier": [
                typed_identifier(
                    role,
                    f"https://example.org/fhir/NamingSystem/{role}/test-key/1",
                    f"v0:test-key:1:{fill * 43}",
                )
                for role, fill in (
                    ("source-record", "A"),
                    ("source-output", "B"),
                    ("source-artifact", "C"),
                )
            ],
            "extension": [{
                "url": (
                    "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
                    "healthkit-source-type-extension"
                ),
                "valueCode": "HKClinicalTypeIdentifierAllergyRecord",
            }],
            "content": [{
                "attachment": {
                    "contentType": content_type_by_release[release],
                    "data": base64.b64encode(payload).decode(),
                    "size": len(payload),
                    "hash": base64.b64encode(
                        hashlib.sha1(payload).digest()  # noqa: S324 -- FHIR Attachment.hash
                    ).decode(),
                },
                "format": {
                    "system": (
                        "https://grovealliance.org/fhir/sensor/CodeSystem/"
                        "grove-recording-format"
                    ),
                    "code": "fhir-resource",
                },
            }],
        }

    def test_healthkit_child_profiles_and_multi_output_rows_are_per_resource(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        child = claims["healthKitSingleProfileObservationClaims"]["profiles"][0]
        row = next(
            item for item in catalog["rows"]
            if item["status"] == "supported" and child in item["profiles"]
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [child]},
            "extension": [{
                "url": catalog["sourceTypeExtension"]["url"],
                "valueCode": row["sourceTypeIdentifier"],
            }],
        }
        profile_validation.validate_active_observation_profile_claim(
            observation, "HealthKit child", {child}
        )
        healthkit_validation.validate_healthkit_source_type(observation, "HealthKit child")

        extra = copy.deepcopy(observation)
        extra["meta"]["profile"].append(
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-heart-rate"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "no arbitrary direct profile"
        ):
            profile_validation.validate_active_observation_profile_claim(
                extra, "HealthKit child", {child}
            )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exact direct profile claims"
        ):
            healthkit_validation.validate_healthkit_source_type(extra, "HealthKit child")

        workout = next(
            item for item in catalog["rows"]
            if item["sourceTypeIdentifier"] == "HKWorkoutTypeIdentifier"
        )
        generic = context.HEALTHKIT_OBSERVATION_PROFILE
        for shared_profile in workout["profiles"]:
            output = {
                "resourceType": "Observation",
                "meta": {"profile": [shared_profile, generic]},
                "extension": [{
                    "url": catalog["sourceTypeExtension"]["url"],
                    "valueCode": workout["sourceTypeIdentifier"],
                }],
            }
            with self.subTest(profile=shared_profile):
                healthkit_validation.validate_healthkit_source_type(output, "HealthKit workout")
        combined = copy.deepcopy(output)
        combined["meta"]["profile"] = [*workout["profiles"], generic]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exact direct profile claims"
        ):
            healthkit_validation.validate_healthkit_source_type(combined, "HealthKit workout")

    def test_healthkit_native_resource_claims_and_document_provenance_are_closed(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )

        def grove(role: str, fill: str) -> dict[str, object]:
            return typed_identifier(
                role,
                f"https://example.org/fhir/NamingSystem/{role}/test-key/1",
                "v0:test-key:1:" + fill * 43,
            )

        source = grove("source-record", "A")
        clinical_profile = claims["healthKitClinicalRecordDocumentClaim"]["profiles"][0]
        document = self._clinical_document()
        document["meta"] = {"profile": [clinical_profile]}
        document["identifier"][0] = copy.deepcopy(source)
        healthkit_validation.validate_healthkit_resource_claims(document, "HealthKit clinical")

        extra_profile = copy.deepcopy(document)
        extra_profile["meta"]["profile"].append(context.SENSOR_RECORDING_PROFILE)
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "directly claim exactly"
        ):
            healthkit_validation.validate_healthkit_resource_claims(
                extra_profile, "HealthKit clinical"
            )

        healthkit_provenance = next(
            claim for claim in claims["adapterConversionProvenanceClaims"]
            if claim["adapter"] == "healthkit"
        )
        document_url = "urn:uuid:00000000-0000-5000-8000-000000000201"
        provenance_url = "urn:uuid:00000000-0000-5000-8000-000000000202"
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [healthkit_provenance["profile"]]},
            "target": [{"reference": document_url}],
            "entity": [{
                "role": "source",
                "what": {"identifier": copy.deepcopy(source)},
            }],
        }
        graphs.validate_adapter_provenance_graph(
            [document, provenance],
            {document_url: document, provenance_url: provenance},
            "HealthKit graph",
        )

    def test_healthkit_clinical_document_runs_shared_payload_pipeline(self) -> None:
        clinical_profile = context.HEALTHKIT_CLINICAL_RECORD_PROFILE
        for release in ("dstu2", "r4"):
            with self.subTest(release=release):
                exchange_bundle.validate_resource_profile_claims(
                    self._clinical_document(release),
                    "HealthKit clinical",
                    {clinical_profile},
                )

        document = self._clinical_document()

        defects = (
            ("format", "exactly one fhir-resource payload"),
            ("size", "size is required"),
            ("hash", "hash does not match embedded bytes"),
        )
        for defect, message in defects:
            invalid = copy.deepcopy(document)
            if defect == "format":
                del invalid["content"][0]["format"]
            elif defect == "size":
                del invalid["content"][0]["attachment"]["size"]
            else:
                invalid["content"][0]["attachment"]["hash"] = (
                    "cDeAcZjCKn0rCAc3HXY3eahP388="
                )
            with self.subTest(defect=defect), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, message
            ):
                exchange_bundle.validate_resource_profile_claims(
                    invalid, "HealthKit clinical", {clinical_profile}
                )

        wrong_format = self._clinical_document()
        wrong_format["content"][0]["format"]["code"] = "native-recording"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly one fhir-resource payload"
        ):
            exchange_bundle.validate_resource_profile_claims(
                wrong_format, "HealthKit clinical", {clinical_profile}
            )

        for wrong_content_type in (
            "application/fhir+json",
            "application/fhir+json; fhirVersion=5.0",
        ):
            invalid_content_type = self._clinical_document()
            invalid_content_type["content"][0]["attachment"]["contentType"] = (
                wrong_content_type
            )
            with self.subTest(
                wrong_content_type=wrong_content_type
            ), self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "HealthKit clinical record must use one admitted Attachment.contentType",
            ):
                exchange_bundle.validate_resource_profile_claims(
                    invalid_content_type, "HealthKit clinical", {clinical_profile}
                )

        for payload, diagnostic in (
            (b"{}", "resourceType"),
            (
                b'{"resourceType":"Observation","resourceType":"Patient"}',
                "strict well-formed UTF-8 JSON",
            ),
        ):
            for release in ("dstu2", "r4"):
                with self.subTest(
                    release=release, payload_diagnostic=diagnostic
                ), self.assertRaisesRegex(
                    diagnostics.ProducerValidationError, diagnostic
                ):
                    exchange_bundle.validate_resource_profile_claims(
                        self._clinical_document(release, payload),
                        "HealthKit clinical",
                        {clinical_profile},
                    )

    def test_healthkit_ecg_contract_uses_native_r4_and_closed_graph(self) -> None:
        healthkit_root = "https://grovealliance.org/fhir/healthkit/"
        output_system = "https://example.org/fhir/NamingSystem/source-output/test-key/1"
        source_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        source_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-record",
            components=["healthkit", "ecg", "scope", "default", "record"],
        )
        waveform_output = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-output",
            components=[
                "healthkit", "ecg", "scope", "default", "record",
                "electrocardiogram", "single",
            ],
        )
        symptom_output = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-output",
            components=[
                "healthkit", "dizziness", "scope", "default", "symptom",
                "dizziness", "single",
            ],
        )
        ecg = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-ecg-observation",
                healthkit_root + "StructureDefinition/healthkit-ecg-observation",
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, waveform_output),
            ],
            "code": {"coding": [{"system": "http://loinc.org", "code": "11524-6"}]},
            "interpretation": [{"coding": [{
                "system": healthkit_root + "CodeSystem/healthkit-ecg-classification",
                "code": "sinusRhythm",
            }]}],
            "method": {"coding": [{
                "system": healthkit_root + "CodeSystem/healthkit-ecg-algorithm-version",
                "code": "version2",
            }]},
            "effectivePeriod": {
                "start": "2026-08-20T09:00:00.002000001Z",
                "end": "2026-08-20T09:00:00.006000001Z",
            },
            "extension": [
                {
                    "url": healthkit_root
                    + "StructureDefinition/healthkit-source-type-extension",
                    "valueCode": "HKDataTypeIdentifierElectrocardiogram",
                },
                {
                    "url": healthkit_root + "StructureDefinition/healthkit-ecg-symptoms-status",
                    "valueCode": "none",
                },
                {
                    "url": healthkit_root + "StructureDefinition/healthkit-ecg-source-period",
                    "valuePeriod": {
                        "start": "2026-08-20T09:00:00.000000001Z",
                        "end": "2026-08-20T09:00:00.010000001Z",
                    },
                },
            ],
            "component": [{
                "code": {"coding": [{
                    "system": "urn:iso:std:iso:11073:10101", "code": "131329",
                }]},
                "valueSampledData": {
                    "origin": {"value": 0, "system": "http://unitsofmeasure.org", "code": "mV"},
                    "period": 2, "dimensions": 1, "data": "0.01 0.02 0.03",
                },
            }],
        }
        exchange_bundle.validate_resource_profile_claims(ecg, "HealthKit ECG")

        with_symptom = copy.deepcopy(ecg)
        with_symptom["extension"][1]["valueCode"] = "present"
        with_symptom["hasMember"] = [{
            "type": "Observation",
            "identifier": typed_identifier("source-output", output_system, symptom_output),
        }]
        exchange_bundle.validate_resource_profile_claims(with_symptom, "HealthKit ECG")

        more_than_one_sample_per_admitted_type = copy.deepcopy(with_symptom)
        more_than_one_sample_per_admitted_type["hasMember"] = [
            {
                "type": "Observation",
                "identifier": typed_identifier(
                    "source-output",
                    output_system,
                    "v0:test-key:1:" + chr(ord("C") + index) * 43,
                ),
            }
            for index in range(8)
        ]
        exchange_bundle.validate_resource_profile_claims(
            more_than_one_sample_per_admitted_type,
            "HealthKit ECG with repeated symptom types but distinct samples",
        )

        mutations = []
        missing_source_period = copy.deepcopy(ecg)
        missing_source_period["extension"] = missing_source_period["extension"][:2]
        mutations.append((missing_source_period, "exactly one sourcePeriod"))
        status_mismatch = copy.deepcopy(ecg)
        status_mismatch["extension"][1]["valueCode"] = "present"
        mutations.append((status_mismatch, "must agree with symptomsStatus"))
        duplicate_member = copy.deepcopy(with_symptom)
        duplicate_member["hasMember"].append(copy.deepcopy(duplicate_member["hasMember"][0]))
        mutations.append((duplicate_member, "invalid or repeated"))
        self_member = copy.deepcopy(with_symptom)
        self_member["hasMember"][0]["identifier"]["value"] = waveform_output
        mutations.append((self_member, "must not reference the waveform itself"))
        wrong_role = copy.deepcopy(with_symptom)
        wrong_role["hasMember"][0]["identifier"]["type"]["coding"][0]["code"] = "source-record"
        mutations.append((wrong_role, "must use a source-output"))
        obsolete = copy.deepcopy(ecg)
        obsolete["extension"].append({
            "url": healthkit_root + "StructureDefinition/healthkit-ecg-average-heart-rate",
            "valueQuantity": {"value": 70},
        })
        mutations.append((obsolete, "obsolete extension"))
        bad_classification = copy.deepcopy(ecg)
        bad_classification["interpretation"][0]["coding"][0]["code"] = "invented"
        mutations.append((bad_classification, "unknown HealthKit ECG classification"))
        bad_algorithm = copy.deepcopy(ecg)
        bad_algorithm["method"]["coding"][0]["code"] = "version3"
        mutations.append((bad_algorithm, "unknown HealthKit ECG algorithm version"))
        outside_source_period = copy.deepcopy(ecg)
        outside_source_period["extension"][2]["valuePeriod"]["end"] = (
            "2026-08-20T09:00:00.005000001Z"
        )
        mutations.append((outside_source_period, "must lie within"))
        for invalid, diagnostic in mutations:
            with self.subTest(diagnostic=diagnostic), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, diagnostic
            ):
                exchange_bundle.validate_resource_profile_claims(invalid, "HealthKit ECG")

        average_output = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-output",
            components=[
                "healthkit", "ecg", "scope", "default", "record",
                "average-heart-rate", "single",
            ],
        )
        average = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate",
                healthkit_root + "StructureDefinition/healthkit-ecg-average-heart-rate-observation"
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, average_output),
            ],
            "extension": [{
                "url": healthkit_root + "StructureDefinition/healthkit-source-type-extension",
                "valueCode": "HKDataTypeIdentifierElectrocardiogram",
            }],
            "code": {"coding": [
                {"system": "http://loinc.org", "code": "8867-4"}
            ]},
            "effectivePeriod": copy.deepcopy(ecg["effectivePeriod"]),
            "valueQuantity": {
                "value": 68, "system": "http://unitsofmeasure.org", "code": "/min",
            },
            "derivedFrom": [{"reference": "urn:uuid:ecg"}],
        }
        exchange_bundle.validate_resource_profile_claims(average, "HealthKit ECG average")
        healthkit_validation.validate_healthkit_ecg_output_graph(
            [ecg, average], {"urn:uuid:ecg": ecg}, "HealthKit ECG graph"
        )
        reversed_graph = copy.deepcopy(ecg)
        reversed_graph["derivedFrom"] = [{"reference": "urn:uuid:average"}]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "relationship is reversed"
        ):
            healthkit_validation.validate_healthkit_ecg_output_graph(
                [reversed_graph, average],
                {"urn:uuid:ecg": reversed_graph, "urn:uuid:average": average},
                "HealthKit ECG graph",
            )
