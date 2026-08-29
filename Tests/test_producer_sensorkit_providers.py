"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from Scripts.producer_validation import (
    context, diagnostics, exchange_bundle, identity, profiles, providers, sensorkit,
)
from Tests.producer_validation_test_support import (
    ProducerValidationTestCase,
    ROOT,
    copy,
    derive_hmac_identity,
    entry_node_identity,
    event_identity,
    json,
    typed_identifier,
)

class ProducerSensorkitProvidersTests(ProducerValidationTestCase):
    def test_provider_identity_kinds_validate_in_active_and_retraction_events(self) -> None:
        source_system = (
            "https://study.example.org/fhir/NamingSystem/"
            "grove-provider-record-v0/test-key/1"
        )
        output_system = (
            "https://study.example.org/fhir/NamingSystem/"
            "grove-provider-output-v0/test-key/1"
        )
        components = [
            "withings",
            "getmeas:11",
            "https://study.example.org/fhir/NamingSystem/provider-account",
            "acct-7f3a9c",
            "record-heart-rate",
        ]
        source_value = derive_hmac_identity(
            key=bytes(range(32)),
            key_id="test-key",
            epoch=1,
            identity_kind="provider-record",
            components=components,
        )
        output_value = derive_hmac_identity(
            key=bytes(range(32)),
            key_id="test-key",
            epoch=1,
            identity_kind="provider-output",
            components=[*components, "heart-rate", "single"],
        )

        active = json.loads(
            (ROOT / "Conformance/example-producer/resources/exchange-bundle.json")
            .read_text(encoding="utf-8")
        )
        observation_entry = next(
            entry for entry in active["entry"]
            if entry["resource"].get("resourceType") == "Observation"
        )
        observation = observation_entry["resource"]
        observation["meta"]["profile"].append(
            "https://grovealliance.org/fhir/withings/StructureDefinition/"
            "withings-observation"
        )
        observation.pop("issued")
        observation["extension"].extend([
            {
                "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                "valueCode": "withings",
            },
            {
                "url": (
                    "https://grovealliance.org/fhir/providers/StructureDefinition/"
                    "provider-source-type"
                ),
                "valueCode": "withings/getmeas:11",
            },
        ])
        observation["identifier"] = [
            typed_identifier("source-record", source_system, source_value),
            typed_identifier("source-output", output_system, output_value),
        ]
        node_identifier = observation_entry["extension"][0]["valueIdentifier"]
        node_identifier.update(
            typed_identifier("source-output", output_system, output_value)
        )
        observation_entry["fullUrl"] = identity.expected_entry_full_url(
            output_system, output_value
        )
        provenance = next(
            entry["resource"] for entry in active["entry"]
            if entry["resource"].get("resourceType") == "Provenance"
        )
        provenance["meta"]["profile"] = [
            "https://grovealliance.org/fhir/providers/StructureDefinition/"
            "providers-conversion-provenance"
        ]
        provenance["entity"][0]["what"]["identifier"] = typed_identifier(
            "source-record", source_system, source_value
        )
        provenance["target"] = [{"reference": observation_entry["fullUrl"]}]
        exchange_bundle.validate_exchange_bundle(active, "Provider active event")

        retraction = json.loads(
            (ROOT / "Conformance/corpora/mobile-exchange/retraction-bundle.json")
            .read_text(encoding="utf-8")
        )
        assertion = retraction["entry"][0]["resource"]
        assertion["entity"][0]["what"]["identifier"] = typed_identifier(
            "source-record", source_system, source_value
        )
        assertion["target"][0]["identifier"] = typed_identifier(
            "source-output", output_system, output_value
        )
        exchange_bundle.validate_exchange_bundle(
            retraction, "Provider retraction event"
        )

        with self.assertRaisesRegex(
            ValueError, "provider components require identity kind provider-output"
        ):
            derive_hmac_identity(
                key=bytes(range(32)),
                key_id="test-key",
                epoch=1,
                identity_kind="source-output",
                components=[*components, "heart-rate", "single"],
            )

    def test_abstract_provider_observation_is_not_a_direct_claim(self) -> None:
        resource = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                "grove-mobile-heart-rate",
                "https://grovealliance.org/fhir/providers/StructureDefinition/"
                "providers-observation",
            ]},
        }
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "exactly one admitted semantic profile and no arbitrary direct profile",
        ):
            profiles.validate_active_observation_profile_claim(
                resource, "Abstract Provider Observation", None
            )

    def test_sensorkit_summary_quantity_domains_accept_boundaries_and_reject_bypasses(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        domains = catalog["quantityValueDomains"]
        count_profiles = set(domains["integerCountProfiles"])
        for profile in domains["nonNegativeProfiles"]:
            quantity = {
                "value": 0,
                "system": "http://unitsofmeasure.org",
                "code": "{count}" if profile in count_profiles else "s",
            }
            resource = {
                "resourceType": "Observation",
                "meta": {"profile": [profile]},
                "component": [{"valueQuantity": quantity}],
            }
            with self.subTest(profile=profile):
                sensorkit.validate_sensorkit_quantity_domains(resource, "SensorKit")
                negative = copy.deepcopy(resource)
                negative["component"][0]["valueQuantity"]["value"] = -1
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError, "present non-negative number"
                ):
                    sensorkit.validate_sensorkit_quantity_domains(
                        negative, "SensorKit"
                    )
                missing = copy.deepcopy(resource)
                del missing["component"][0]["valueQuantity"]["value"]
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError, "present non-negative number"
                ):
                    sensorkit.validate_sensorkit_quantity_domains(missing, "SensorKit")
                if profile in count_profiles:
                    fractional = copy.deepcopy(resource)
                    fractional["component"][0]["valueQuantity"]["value"] = 1.5
                    with self.assertRaisesRegex(
                        diagnostics.ProducerValidationError, "must be an integer"
                    ):
                        sensorkit.validate_sensorkit_quantity_domains(
                            fractional, "SensorKit"
                        )
        sensorkit.validate_sensorkit_quantity_domains(
            {
                "resourceType": "Observation",
                "meta": {"profile": [
                    "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                    "sensorkit-keyboard-metrics-observation"
                ]},
                "component": [{
                    "valueQuantity": {
                        "value": 1.5,
                        "system": "http://unitsofmeasure.org",
                        "code": "/s",
                    }
                }],
            },
            "SensorKit speed",
        )

    def test_provider_owned_semantics_use_exact_envelope_and_native_id_primary(self) -> None:
        cases = [
            (
                "Oura cardiovascular age",
                ROOT / "oura/input/fsh/generated-measurement-profiles.fsh",
                "OuraCardiovascularAgeExample",
                "oura",
                "oura/daily_cardiovascular_age",
                "https://grovealliance.org/fhir/oura/StructureDefinition/oura-cardiovascular-age",
                "https://grovealliance.org/fhir/oura/StructureDefinition/oura-observation",
                "https://grovealliance.org/fhir/oura/CodeSystem/oura-measurement",
                "oura-cardiovascular-age",
                "v0:test-key:1:8sShnFJZdY3lig52cRyVwGQLRYrAzEnFYBdZvsebuhA",
                "v0:test-key:1:fWfV53Bqz3Gw7mN6Mxkwzyv2Kfxvc5BHhAAdtLV8YH0",
                38,
            ),
            (
                "Withings vascular age",
                ROOT / "withings/input/fsh/generated-measurement-profiles.fsh",
                "WithingsVascularAgeExample",
                "withings",
                "withings/getmeas:155",
                "https://grovealliance.org/fhir/withings/StructureDefinition/withings-vascular-age",
                "https://grovealliance.org/fhir/withings/StructureDefinition/withings-observation",
                "https://grovealliance.org/fhir/withings/CodeSystem/withings-measurement",
                "withings-vascular-age",
                "v0:test-key:1:rQQgVI9MRynajmjVuAM61ZOh8wZSP1t3LmTNSw5yMu0",
                "v0:test-key:1:NS29R6m0YYpIT7dj-dPs1o1VNhGGOhBWaqVrrjXkpjE",
                45,
            ),
        ]
        resources_by_label = {}
        for (
            label,
            path,
            instance,
            provider,
            source_type,
            semantic_profile,
            adapter_profile,
            code_system,
            code,
            source_record,
            source_output,
            value,
        ) in cases:
            authored = path.read_text(encoding="utf-8")
            instance_block = authored.split(f"Instance: {instance}", 1)[1].split(
                "\nInstance:", 1
            )[0]
            with self.subTest(label=label):
                self.assertIn(
                    f"* meta.profile[+] = \"{adapter_profile}\"", instance_block
                )
                self.assertIn(
                    f"* identifier[sourceRecord].value = \"{source_record}\"",
                    instance_block,
                )
                self.assertIn(
                    f"* identifier[sourceOutput].value = \"{source_output}\"",
                    instance_block,
                )

                resource = {
                    "resourceType": "Observation",
                    "meta": {"profile": [semantic_profile, adapter_profile]},
                    "identifier": [
                        typed_identifier(
                            "source-record",
                            "https://study.example.org/fhir/NamingSystem/"
                            "grove-provider-record-v0/test-key/1",
                            source_record,
                        ),
                        typed_identifier(
                            "source-output",
                            "https://study.example.org/fhir/NamingSystem/"
                            "grove-provider-output-v0/test-key/1",
                            source_output,
                        ),
                    ],
                    "status": "final",
                    "code": {"coding": [{"system": code_system, "code": code}]},
                    "extension": [
                        {
                            "url": (
                                "https://grovealliance.org/fhir/providers/"
                                "StructureDefinition/provider"
                            ),
                            "valueCode": provider,
                        },
                        {
                            "url": (
                                "https://grovealliance.org/fhir/providers/"
                                "StructureDefinition/provider-source-type"
                            ),
                            "valueCode": source_type,
                        },
                    ],
                    "valueQuantity": {
                        "value": value,
                        "system": "http://unitsofmeasure.org",
                        "code": "a",
                    },
                }
                resources_by_label[label] = resource
                self.assertEqual(
                    set(resource["meta"]["profile"]),
                    {semantic_profile, adapter_profile},
                )
                exchange_bundle.validate_resource_profile_claims(resource, label)
                profiles.validate_active_observation_profile_claim(resource, label, None)

                governed = copy.deepcopy(resource)
                governed["identifier"].append({
                    "system": (
                        "https://study.example.org/fhir/NamingSystem/"
                        "provider-native-record"
                    ),
                    "value": "exact-native-record-" + label.lower().replace(" ", "-"),
                })
                identity.validate_governed_source_identifiers([governed], label)

                missing_envelope = copy.deepcopy(resource)
                missing_envelope["meta"]["profile"] = [semantic_profile]
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError,
                    "provider-owned semantic profile must be paired",
                ):
                    profiles.validate_active_observation_profile_claim(
                        missing_envelope, label, None
                    )

                wrong_envelope = copy.deepcopy(resource)
                envelope_index = wrong_envelope["meta"]["profile"].index(
                    adapter_profile
                )
                wrong_envelope["meta"]["profile"][envelope_index] = (
                    "https://grovealliance.org/fhir/withings/StructureDefinition/withings-observation"
                    if "oura/" in adapter_profile
                    else "https://grovealliance.org/fhir/oura/StructureDefinition/oura-observation"
                )
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError,
                    "must directly claim exactly its semantic profile",
                ):
                    providers.validate_provider_identity(wrong_envelope, label)

        oura_wrong_semantic = copy.deepcopy(
            resources_by_label["Oura cardiovascular age"]
        )
        semantic_index = oura_wrong_semantic["meta"]["profile"].index(cases[0][5])
        oura_wrong_semantic["meta"]["profile"][semantic_index] = (
            "https://grovealliance.org/fhir/oura/StructureDefinition/oura-readiness-score"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "source type does not admit its claimed measurement",
        ):
            providers.validate_provider_identity(
                oura_wrong_semantic, "Oura cardiovascular age"
            )

    def test_sensorkit_specific_and_recording_claims_are_exact(self) -> None:
        provider_profile = (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-on-wrist-observation"
        )
        provider = {
            "resourceType": "Observation",
            "meta": {"profile": [provider_profile]},
        }
        sensorkit.validate_sensorkit_profile_claim(provider, "Observation")
        invalid_provider = copy.deepcopy(provider)
        invalid_provider["meta"]["profile"].append(
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-observation"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "directly claim exactly one"
        ):
            sensorkit.validate_sensorkit_profile_claim(
                invalid_provider, "Observation"
            )

        document_profiles = [
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-recording-document",
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-recording-document",
        ]
        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": document_profiles},
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/source-record/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-record",
                        components=["sensorkit", "rotation-rate", "scope", "one", "record"],
                    ),
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-output",
                        components=[
                            "sensorkit", "rotation-rate", "scope", "one", "record",
                            "source-artifact", "native-recording",
                        ],
                    ),
                ),
                typed_identifier(
                    "source-artifact",
                    "https://example.org/fhir/NamingSystem/source-artifact/test-key/1",
                    derive_hmac_identity(
                        key=bytes(range(32)),
                        key_id="test-key",
                        epoch=1,
                        identity_kind="source-artifact",
                        components=[
                            "sensorkit", "rotation-rate", "scope", "one", "record",
                            "native-recording", "0",
                        ],
                    ),
                ),
            ],
        }
        sensorkit.validate_sensorkit_profile_claim(document, "DocumentReference")
        invalid_document = copy.deepcopy(document)
        invalid_document["meta"]["profile"] = document_profiles[1:]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "directly claim exactly"
        ):
            sensorkit.validate_sensorkit_profile_claim(
                invalid_document, "DocumentReference"
            )

        marker_without_adapter_profile = copy.deepcopy(document)
        marker_without_adapter_profile["meta"]["profile"] = document_profiles[:1]
        marker_without_adapter_profile["extension"] = [{
            "url": (
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-source-type"
            ),
            "valueCode": "face-metrics",
        }]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "must directly claim exactly the source-neutral and SensorKit recording profiles",
        ):
            sensorkit.validate_sensorkit_identity(
                marker_without_adapter_profile, "Unprofiled SensorKit document"
            )

    def test_sensorkit_ecg_structured_projection_is_exact(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        source_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        output_system = "https://example.org/fhir/NamingSystem/source-output/test-key/1"
        components = [
            "sensorkit", "ecg", "https://example.org/repository", "default",
            "2fea27a0-5575-4fd2-83d7-d46b03059ddc",
        ]
        source_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-record", components=components,
        )
        output_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="source-output",
            components=[*components, "waveform", "0"],
        )
        ecg = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-ecg-observation",
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-ecg-observation",
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, output_value),
            ],
            "extension": [
                {
                    "url": (
                        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                        "sensorkit-source-type"
                    ),
                    "valueCode": "ecg",
                },
            ],
            "method": {"coding": [{
                "system": (
                    "https://grovealliance.org/fhir/sensorkit/CodeSystem/"
                    "sensorkit-value"
                ),
                "code": "guided",
            }]},
            "effectivePeriod": {
                "start": "2026-08-20T09:10:00Z",
                "end": "2026-08-20T09:10:00.012Z",
            },
            "component": [{
                "code": {"coding": [
                    {
                        "system": "urn:iso:std:iso:11073:10101",
                        "code": "131329",
                    },
                    {
                        "system": (
                            "https://grovealliance.org/fhir/sensorkit/CodeSystem/"
                            "sensorkit-ecg-lead"
                        ),
                        "code": "leftArmMinusRightArm",
                    },
                ]},
                "valueSampledData": {
                    "origin": {
                        "value": 0,
                        "system": "http://unitsofmeasure.org",
                        "code": "mV",
                    },
                    "period": 4,
                    "dimensions": 1,
                    "data": "0.01 0.02 0.03 0.04",
                },
            }],
        }
        exchange_bundle.validate_resource_profile_claims(ecg, "SensorKit ECG")

        source_type_with_element_id = copy.deepcopy(ecg)
        source_type_with_element_id["extension"][0]["id"] = "source-type"
        sensorkit.validate_sensorkit_identity(
            source_type_with_element_id, "SensorKit source type with Element.id"
        )

        for duplicate_marker in (
            {"url": ecg["extension"][0]["url"], "valueCode": "ecg"},
            {"url": ecg["extension"][0]["url"], "valueString": "ecg"},
        ):
            with self.subTest(duplicate_marker=duplicate_marker):
                duplicate_source_type = copy.deepcopy(ecg)
                duplicate_source_type["extension"].append(duplicate_marker)
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError,
                    "exactly one valueCode-only SensorKit source type",
                ):
                    sensorkit.validate_sensorkit_identity(
                        duplicate_source_type, "SensorKit duplicate source type"
                    )

        ecg_with_rotation_source = copy.deepcopy(ecg)
        ecg_with_rotation_source["extension"][0]["valueCode"] = "rotation-rate"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "exact source-neutral and SensorKit profiles admitted for its source type",
        ):
            exchange_bundle.validate_resource_profile_claims(
                ecg_with_rotation_source, "SensorKit ECG with rotation source"
            )

        rotation_rate = copy.deepcopy(ecg)
        rotation_rate["meta"]["profile"] = [
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-sampled-data-observation",
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-observation",
        ]
        rotation_rate["extension"][0]["valueCode"] = "rotation-rate"
        sensorkit.validate_sensorkit_identity(rotation_rate, "SensorKit rotation rate")
        rotation_with_ecg_source = copy.deepcopy(rotation_rate)
        rotation_with_ecg_source["extension"][0]["valueCode"] = "ecg"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "exact source-neutral and SensorKit profiles admitted for its source type",
        ):
            sensorkit.validate_sensorkit_identity(
                rotation_with_ecg_source, "SensorKit rotation with ECG source"
            )

        missing_guidance = copy.deepcopy(ecg)
        missing_guidance.pop("method")
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "session guidance"
        ):
            exchange_bundle.validate_resource_profile_claims(
                missing_guidance, "SensorKit ECG"
            )
        left_without_standard_lead = copy.deepcopy(ecg)
        left_without_standard_lead["component"][0]["code"]["coding"] = (
            left_without_standard_lead["component"][0]["code"]["coding"][1:]
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "orientation and standard Lead-I"
        ):
            exchange_bundle.validate_resource_profile_claims(
                left_without_standard_lead, "SensorKit ECG"
            )
        inverse_lead = copy.deepcopy(ecg)
        inverse_lead["component"][0]["code"]["coding"] = [
            {
                "system": (
                    "https://grovealliance.org/fhir/sensorkit/CodeSystem/"
                    "sensorkit-ecg-lead"
                ),
                "code": "rightArmMinusLeftArm",
            }
        ]
        exchange_bundle.validate_resource_profile_claims(
            inverse_lead, "SensorKit inverse-lead ECG"
        )
        inverse_with_false_lead_i = copy.deepcopy(ecg)
        inverse_with_false_lead_i["component"][0]["code"]["coding"][1]["code"] = (
            "rightArmMinusLeftArm"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "orientation and standard Lead-I"
        ):
            exchange_bundle.validate_resource_profile_claims(
                inverse_with_false_lead_i, "SensorKit ECG"
            )

    def test_sensorkit_visit_and_algorithm_use_native_r4_elements(self) -> None:
        prefix = "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        visit = {
            "resourceType": "Observation",
            "meta": {"profile": [prefix + "sensorkit-visit-observation"]},
            "focus": [{
                "type": "Location",
                "identifier": {
                    "system": "https://study.example.org/fhir/NamingSystem/sensorkit-location/store-a",
                    "value": "0f1f2c48-2b45-4a2a-9a2a-8b4d3a2f61c7",
                },
            }],
        }
        sensorkit.validate_sensorkit_native_r4_context(visit, "SensorKit visit")
        relative_system = copy.deepcopy(visit)
        relative_system["focus"][0]["identifier"]["system"] = "store-a"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "absolute.*URI"):
            sensorkit.validate_sensorkit_native_r4_context(
                relative_system, "SensorKit visit"
            )
        grove_role = copy.deepcopy(visit)
        grove_role["focus"][0]["identifier"]["type"] = {
            "coding": [{"system": context.IDENTIFIER_ROLE_SYSTEM, "code": "source-context"}]
        }
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "must not claim"):
            sensorkit.validate_sensorkit_native_r4_context(grove_role, "SensorKit visit")
        literal_location = copy.deepcopy(visit)
        literal_location["focus"][0]["reference"] = "Location/one"
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "must not mix"):
            sensorkit.validate_sensorkit_native_r4_context(
                literal_location, "SensorKit visit"
            )

        wrist = {
            "resourceType": "Observation",
            "meta": {"profile": [prefix + "sensorkit-wrist-temperature-observation"]},
            "extension": [{
                "url": prefix + "sensorkit-wrist-temperature-algorithm-version",
                "valueString": "1",
            }],
        }
        sensorkit.validate_sensorkit_native_r4_context(wrist, "SensorKit wrist temperature")
        blank_version = copy.deepcopy(wrist)
        blank_version["extension"][0]["valueString"] = "   "
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "non-blank"):
            sensorkit.validate_sensorkit_native_r4_context(
                blank_version, "SensorKit wrist temperature"
            )
        invented_coding = copy.deepcopy(wrist)
        invented_coding["method"] = {"coding": [{"system": "urn:example", "code": "1"}]}
        with self.assertRaisesRegex(diagnostics.ProducerValidationError, "governed valueString extension"):
            sensorkit.validate_sensorkit_native_r4_context(
                invented_coding, "SensorKit wrist temperature"
            )

    def test_sensor_recording_allows_writer_and_open_untyped_identifiers_only(self) -> None:
        def grove(role: str, fill: str) -> dict[str, object]:
            return typed_identifier(
                role,
                f"https://example.org/fhir/NamingSystem/{role}/test-key/1",
                "v0:test-key:1:" + fill * 43,
            )

        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [context.SENSOR_RECORDING_PROFILE]},
            "identifier": [
                grove("source-record", "A"),
                grove("source-output", "B"),
                grove("source-artifact", "C"),
                grove("writer-record", "D"),
                {
                    "system": "https://example.org/fhir/identifiers/local-accession",
                    "value": "local-1",
                },
            ],
            "content": [{
                "attachment": {
                    "contentType": "application/json",
                    "data": "e30=",
                    "size": 2,
                    "hash": "vyGp6PvFo4RvsFtPoIWeCReyIC8=",
                }
            }],
        }
        sensorkit.validate_sensor_contract(document, "DocumentReference/test")

        unexpected = copy.deepcopy(document)
        unexpected["identifier"].append(grove("source-context", "E"))
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "unexpected=\\['source-context'\\]"
        ):
            sensorkit.validate_sensor_contract(
                unexpected, "DocumentReference/test"
            )

    def test_sensorkit_device_usage_graph_requires_linked_native_recording(self) -> None:
        key = bytes(range(32))
        source_system = "https://example.org/fhir/NamingSystem/source-record/test-key/1"
        output_system = "https://example.org/fhir/NamingSystem/source-output/test-key/1"
        artifact_system = "https://example.org/fhir/NamingSystem/source-artifact/test-key/1"
        event_system = "https://example.org/fhir/NamingSystem/event"
        node_system = "https://example.org/fhir/NamingSystem/entry-node"
        components = [
            "sensorkit",
            "device-usage",
            "https://example.org/fhir/NamingSystem/source-repository",
            "default",
            "b4df30d0-2a34-492e-a68e-b1eab1cb471d",
        ]
        source_value = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-record",
            components=components,
        )
        observation_output = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-output",
            components=[*components, "summary", "0"],
        )
        document_output = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-output",
            components=[*components, "source-artifact", "native-recording"],
        )
        artifact_value = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-artifact",
            components=[*components, "native-recording", "0"],
        )

        def typed_identifier(role: str, system: str, value: str) -> dict[str, object]:
            return {
                "type": {"coding": [{
                    "system": context.IDENTIFIER_ROLE_SYSTEM,
                    "code": role,
                }]},
                "system": system,
                "value": value,
            }

        source_type_url = (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-source-type"
        )
        observation_url = identity.expected_entry_full_url(output_system, observation_output)
        document_url = identity.expected_entry_full_url(output_system, document_output)
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-device-usage-observation"
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, observation_output),
            ],
            "extension": [{"url": source_type_url, "valueCode": "device-usage"}],
            "derivedFrom": [{"reference": document_url}],
        }
        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                "grove-sensor-recording-document",
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-recording-document",
            ]},
            "identifier": [
                typed_identifier("source-record", source_system, source_value),
                typed_identifier("source-output", output_system, document_output),
                typed_identifier("source-artifact", artifact_system, artifact_value),
            ],
            "extension": [{"url": source_type_url, "valueCode": "device-usage"}],
            "content": [{
                "attachment": {
                    "contentType": "application/json",
                    "data": "e30=",
                    "size": 2,
                    "hash": "vyGp6PvFo4RvsFtPoIWeCReyIC8=",
                },
                "format": {
                    "system": "https://grovealliance.org/fhir/sensor/CodeSystem/grove-recording-format",
                    "code": "native-recording",
                },
            }],
            "context": {"related": [{
                "reference": observation_url
            }]},
        }

        event_value = event_identity("1f5c58aa-6ec6-4e79-a682-829a9debd3f5", 9)
        provenance_entry_value = entry_node_identity(
            event_system=event_system,
            event_value=event_value,
            role="conversion-provenance",
            ordinal=0,
        )
        provenance_url = identity.expected_entry_full_url(
            node_system, provenance_entry_value
        )
        provenance = {
            "resourceType": "Provenance",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
                "sensorkit-conversion-provenance"
            ]},
            "target": [
                {"reference": observation_url},
                {"reference": document_url},
            ],
            "occurredDateTime": "2026-08-20T08:00:00Z",
            "recorded": "2026-08-20T08:00:01Z",
            "activity": {"coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle",
                "code": "transform",
            }]},
            "entity": [{
                "role": "source",
                "what": {"identifier": typed_identifier(
                    "source-record", source_system, source_value
                )},
            }],
        }

        def entry(
            resource: dict[str, object], output: str, role: str, system: str
        ) -> dict[str, object]:
            return {
                "extension": [{
                    "url": context.ENTRY_IDENTIFIER_EXTENSION,
                    "valueIdentifier": typed_identifier(role, system, output),
                }],
                "fullUrl": identity.expected_entry_full_url(system, output),
                "resource": resource,
            }

        bundle = {
            "resourceType": "Bundle",
            "meta": {"profile": [context.EXCHANGE_BUNDLE_PROFILE]},
            "identifier": typed_identifier("event", event_system, event_value),
            "type": "collection",
            "timestamp": "2026-08-20T08:00:01Z",
            "entry": [
                entry(observation, observation_output, "source-output", output_system),
                entry(document, document_output, "source-output", output_system),
                entry(provenance, provenance_entry_value, "entry-node", node_system),
            ],
        }
        exchange_bundle.validate_exchange_bundle(bundle, "Bundle")

        raw_only = copy.deepcopy(bundle)
        raw_only_document = raw_only["entry"][1]["resource"]
        raw_only_document["extension"][0]["valueCode"] = "face-metrics"
        raw_only_document.pop("context")
        raw_only["entry"][2]["resource"]["target"] = [
            {"reference": document_url}
        ]
        raw_only["entry"] = raw_only["entry"][1:]
        exchange_bundle.validate_exchange_bundle(raw_only, "Raw-only Bundle")

        unprofiled_raw = copy.deepcopy(raw_only)
        unprofiled_raw["entry"][0]["resource"]["meta"]["profile"] = [
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-recording-document"
        ]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "must directly claim exactly the source-neutral and SensorKit recording profiles",
        ):
            exchange_bundle.validate_exchange_bundle(
                unprofiled_raw, "Unprofiled raw-only Bundle"
            )

        orphan_hybrid = copy.deepcopy(raw_only)
        orphan_hybrid["entry"][0]["resource"]["extension"][0][
            "valueCode"
        ] = "device-usage"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "requires exactly one linked structured Observation",
        ):
            exchange_bundle.validate_exchange_bundle(
                orphan_hybrid, "Orphan hybrid Bundle"
            )

        duplicate_transform_system = copy.deepcopy(bundle)
        duplicate_transform_system["entry"][2]["resource"]["activity"]["coding"].append({
            "system": "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle",
            "code": "amend",
        })
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "exactly one coding across the ISO transform and Grove retraction lifecycle systems",
        ):
            exchange_bundle.validate_exchange_bundle(duplicate_transform_system, "Bundle")

        contradictory_lifecycle = copy.deepcopy(bundle)
        contradictory_lifecycle["entry"][2]["resource"]["activity"]["coding"].append({
            "system": context.LIFECYCLE_EVENT_SYSTEM,
            "code": context.SOURCE_RECORD_RETRACTED,
        })
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "exactly one coding across the ISO transform and Grove retraction lifecycle systems",
        ):
            exchange_bundle.validate_exchange_bundle(contradictory_lifecycle, "Bundle")

        translated_lifecycle = copy.deepcopy(bundle)
        translated_lifecycle["entry"][2]["resource"]["activity"]["coding"].append({
            "system": "https://study.example.org/fhir/CodeSystem/lifecycle-translation",
            "code": "converted",
        })
        exchange_bundle.validate_exchange_bundle(translated_lifecycle, "Bundle")

        cross_stream_document = copy.deepcopy(bundle)
        cross_stream_document["entry"][1]["resource"]["extension"][0][
            "valueCode"
        ] = "keyboard-metrics"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "must carry the same matching SensorKit source type",
        ):
            exchange_bundle.validate_exchange_bundle(cross_stream_document, "Bundle")

        for malformed_related in (
            [{"reference": observation_url}, "ignored"],
            [{"reference": observation_url}, {}],
            [{"reference": observation_url, "identifier": {}}],
            [{"reference": observation_url, "type": "Device"}],
        ):
            with self.subTest(related=malformed_related):
                malformed_backlink = copy.deepcopy(bundle)
                malformed_backlink["entry"][1]["resource"]["context"][
                    "related"
                ] = malformed_related
                with self.assertRaisesRegex(
                    diagnostics.ProducerValidationError,
                    "relate back to exactly its structured Observation|"
                    "must equal the referenced resource type Observation",
                ):
                    exchange_bundle.validate_exchange_bundle(
                        malformed_backlink, "Bundle"
                    )

        missing_raw_target = copy.deepcopy(bundle)
        missing_raw_target["entry"][2]["resource"]["target"] = [
            missing_raw_target["entry"][2]["resource"]["target"][0]
        ]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "target every and only source-derived output|target every structured and raw output",
        ):
            exchange_bundle.validate_exchange_bundle(missing_raw_target, "Bundle")

        missing_document = copy.deepcopy(bundle)
        missing_document["entry"] = missing_document["entry"][:1]
        with self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "exactly one transform Provenance|reference must resolve to an entry UUID URN|same Bundle",
        ):
            exchange_bundle.validate_exchange_bundle(missing_document, "Bundle")

        mismatched_identity = copy.deepcopy(bundle)
        other_source = derive_hmac_identity(
            key=key,
            key_id="test-key",
            epoch=1,
            identity_kind="source-record",
            components=[*components[:-1], "95ee78bd-a754-4d3d-b084-6031b42d666c"],
        )
        mismatched_identity["entry"][1]["resource"]["identifier"][0]["value"] = other_source
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly one source record|same source-record [Ii]dentifier"
        ):
            exchange_bundle.validate_exchange_bundle(mismatched_identity, "Bundle")

        wrong_provenance_source = copy.deepcopy(bundle)
        wrong_provenance_source["entry"][2]["resource"]["entity"][0]["what"][
            "identifier"
        ]["value"] = other_source
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "source must equal|exactly one conversion Provenance|no output for its source record",
        ):
            exchange_bundle.validate_exchange_bundle(wrong_provenance_source, "Bundle")
