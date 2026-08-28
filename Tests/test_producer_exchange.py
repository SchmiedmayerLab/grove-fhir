"""Domain regressions for Grove producer conformance."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from Scripts.producer_validation import (
    context,
    diagnostics,
    exchange_bundle,
    health_connect as health_connect_validation,
    healthkit as healthkit_validation,
    identity,
    manifest as manifest_validation,
    profiles as profile_validation,
    providers,
)
from Tests.producer_validation_test_support import (
    CORPUS,
    Decimal,
    Path,
    ProducerValidationTestCase,
    ROOT,
    copy,
    derive_hmac_identity,
    json,
    tempfile,
    typed_identifier,
)

class ProducerExchangeTests(ProducerValidationTestCase):
    def test_missing_profile_is_rejected(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(encoding="utf-8")
        )
        resource["meta"]["profile"] = ["http://hl7.org/fhir/StructureDefinition/heartrate"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "resources/exchange-bundle.json").write_text(json.dumps(resource), encoding="utf-8")
            with self.assertRaisesRegex(diagnostics.ProducerValidationError, "missing required profiles"):
                manifest_validation.validate_manifest(root / "manifest.json")

    def test_exchange_references_are_closed_over_bundle_entries(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        observation = next(
            entry["resource"] for entry in resource["entry"]
            if entry["resource"].get("resourceType") == "Observation"
        )
        observation["subject"]["reference"] = (
            "https://outside.example/fhir/Patient/123"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            (root / "resources/exchange-bundle.json").write_text(
                json.dumps(resource), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "reference must resolve to an entry UUID URN",
            ):
                manifest_validation.validate_manifest(root / "manifest.json")

    def test_exchange_profiles_references_entities_and_retraction_roles_fail_closed(self) -> None:
        active = json.loads(
            (ROOT / "Conformance/example-producer/resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        exchange_bundle.validate_exchange_bundle(active, "active")
        observation_index = next(
            index for index, entry in enumerate(active["entry"])
            if entry["resource"].get("resourceType") == "Observation"
        )
        provenance_index = next(
            index for index, entry in enumerate(active["entry"])
            if entry["resource"].get("resourceType") == "Provenance"
        )
        patient_url = next(
            entry["fullUrl"] for entry in active["entry"]
            if entry["resource"].get("resourceType") == "Patient"
        )
        device_url = next(
            entry["fullUrl"] for entry in active["entry"]
            if entry["resource"].get("resourceType") == "Device"
        )

        for profiles in ([], ["https://example.org/fhir/StructureDefinition/arbitrary"]):
            invalid = copy.deepcopy(active)
            invalid["entry"][observation_index]["resource"]["meta"]["profile"] = profiles
            with self.subTest(profiles=profiles), self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "active Observation must carry|admitted semantic profile",
            ):
                exchange_bundle.validate_exchange_bundle(invalid, "active")

        wrong_subject = copy.deepcopy(active)
        wrong_subject["entry"][observation_index]["resource"]["subject"]["reference"] = device_url
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, r"Observation\.subject must reference Patient"
        ):
            exchange_bundle.validate_exchange_bundle(wrong_subject, "active")

        false_declared_type = copy.deepcopy(active)
        false_declared_type["entry"][observation_index]["resource"]["subject"]["type"] = "Device"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "type must equal the referenced resource type Patient",
        ):
            exchange_bundle.validate_exchange_bundle(false_declared_type, "active")

        logical_subject = copy.deepcopy(active)
        logical_subject["entry"][observation_index]["resource"]["subject"] = {
            "type": "Patient",
            "identifier": {
                "system": "https://deployment.example/fhir/NamingSystem/patient-pseudonym",
                "value": "participant-42",
            },
        }
        exchange_bundle.validate_exchange_bundle(logical_subject, "active")

        untyped_logical_subject = copy.deepcopy(logical_subject)
        del untyped_logical_subject["entry"][observation_index]["resource"]["subject"]["type"]
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "logical reference type must be Patient",
        ):
            exchange_bundle.validate_exchange_bundle(untyped_logical_subject, "active")

        mixed_subject = copy.deepcopy(active)
        mixed_subject["entry"][observation_index]["resource"]["subject"]["identifier"] = {
            "system": "https://deployment.example/fhir/NamingSystem/patient-pseudonym",
            "value": "participant-42",
        }
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "must not mix a resolving literal with a logical identifier",
        ):
            exchange_bundle.validate_exchange_bundle(mixed_subject, "active")

        wrong_gateway = copy.deepcopy(active)
        wrong_gateway["entry"][observation_index]["resource"]["extension"][0][
            "valueReference"
        ]["reference"] = patient_url
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            r"extension\[[0-9]+\]\.valueReference must reference Device",
        ):
            exchange_bundle.validate_exchange_bundle(wrong_gateway, "active")

        literal_source = copy.deepcopy(active)
        literal_source["entry"][provenance_index]["resource"]["entity"][0]["what"][
            "reference"
        ] = patient_url
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "source must be exactly one logical Identifier entity",
        ):
            exchange_bundle.validate_exchange_bundle(literal_source, "active")

        additional_source = copy.deepcopy(active)
        additional_source["entry"][provenance_index]["resource"]["entity"].append(
            copy.deepcopy(
                additional_source["entry"][provenance_index]["resource"]["entity"][0]
            )
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "identify exactly one source record"
        ):
            exchange_bundle.validate_exchange_bundle(additional_source, "active")

        retraction = json.loads(
            (ROOT / "Conformance/corpora/mobile-exchange/retraction-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        exchange_bundle.validate_exchange_bundle(retraction, "retraction")
        wrong_target_type = copy.deepcopy(retraction)
        wrong_target_type["entry"][0]["resource"]["target"][0]["type"] = "Device"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "role primary-output does not admit resource type Device",
        ):
            exchange_bundle.validate_exchange_bundle(wrong_target_type, "retraction")

        wrong_target_identifier_role = copy.deepcopy(retraction)
        wrong_target_identifier_role["entry"][0]["resource"]["target"][0]["identifier"][
            "type"
        ]["coding"][0]["code"] = "device-snapshot"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "role primary-output requires the source-output identifier role",
        ):
            exchange_bundle.validate_exchange_bundle(wrong_target_identifier_role, "retraction")

        retraction_literal_source = copy.deepcopy(retraction)
        retraction_provenance = retraction_literal_source["entry"][0]["resource"]
        retraction_provenance["contained"] = [{
            "resourceType": "Patient",
            "id": "forbidden-source",
        }]
        retraction_provenance["entity"][0]["what"]["reference"] = "#forbidden-source"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError,
            "contains a Resource; Mobile event graphs require addressable Bundle entries",
        ):
            exchange_bundle.validate_exchange_bundle(retraction_literal_source, "retraction")

    def test_reviewed_quantity_value_domains_accept_boundaries_and_reject_bypasses(self) -> None:
        body_fat = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-body-fat-percentage"
        )
        step_count = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-step-count"
        )
        state_of_mind = (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-state-of-mind"
        )
        for profile, values in (
            (body_fat, (0, Decimal("23.5"), 100)),
            (step_count, (0, 12)),
            (state_of_mind, (-1, 0, 1)),
        ):
            for value in values:
                profile_validation.validate_quantity_value_domain(
                    {"valueQuantity": {"value": value}}, "Observation/test", profile
                )
        try:
            profile_validation.validate_quantity_value_domain(
                {"valueQuantity": {"value": -1}},
                "active entry[2].resource",
                step_count,
            )
        except diagnostics.ProducerValidationError as error:
            self.assertEqual(
                error.diagnostic,
                {
                    "code": "mobile-output.quantity-value-domain",
                    "reason": (
                        "Every Quantity-valued catalog measurement stays within its "
                        "reviewed representational minimum, maximum, and integer-only "
                        "domain without inventing a physiologic range."
                    ),
                    "location": "Bundle.entry[2].resource.valueQuantity.value",
                    "severity": "error",
                },
            )
        else:
            self.fail("a value-domain violation must fail with a registered diagnostic")
        for profile, value, message in (
            (body_fat, -0.1, "inclusive minimum 0"),
            (body_fat, 100.1, "inclusive maximum 100"),
            (step_count, -1, "inclusive minimum 0"),
            (step_count, 1.5, "must be an integer"),
            (state_of_mind, -1.1, "inclusive minimum -1"),
            (state_of_mind, 1.1, "inclusive maximum 1"),
        ):
            with self.subTest(profile=profile, value=value), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, message
            ):
                profile_validation.validate_quantity_value_domain(
                    {"valueQuantity": {"value": value}}, "Observation/test", profile
                )

    def test_manifest_cannot_hide_an_extra_direct_grove_profile(self) -> None:
        manifest = json.loads(self.example.read_text(encoding="utf-8"))
        resource = json.loads(
            (self.example.parent / "resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        resource["meta"]["profile"].append(
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-recording-document"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            (root / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            (root / "resources/exchange-bundle.json").write_text(
                json.dumps(resource), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "requiredProfiles must equal",
            ):
                manifest_validation.validate_manifest(root / "manifest.json")

    def test_mobile_exchange_corpus_is_closed_and_reason_specific(self) -> None:
        corpus_root = ROOT / "Conformance/corpora/mobile-exchange"
        corpus = CORPUS.load_manifest(corpus_root / "corpus.json")
        self.assertEqual(CORPUS.validate_manifest(corpus), [])
        bases = CORPUS.load_bases(corpus, corpus_root / "corpus.json")
        example = json.loads(
            (ROOT / "Conformance/example-producer/resources/exchange-bundle.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(bases["mobile-exchange"], example)
        cases = CORPUS.build_cases(corpus, bases)
        self.assertEqual(
            set(cases),
            {case["id"] for case in corpus["cases"]},
        )
        results = {
            "schemaVersion": 1,
            "baseDiagnostics": {
                base_id: exchange_bundle.exchange_bundle_diagnostics(resource, base_id)
                for base_id, resource in bases.items()
            },
            "caseDiagnostics": {
                case_id: exchange_bundle.exchange_bundle_diagnostics(resource, case_id)
                for case_id, resource in cases.items()
            },
        }
        self.assertEqual(CORPUS.validate_results(corpus, results), [])

    def test_every_emitted_exchange_diagnostic_is_catalog_registered(self) -> None:
        registered = {
            row["code"]: row["reason"]
            for row in context.EXCHANGE_PROTOCOL["producerDiagnostics"]
        }
        fallback = exchange_bundle.exchange_bundle_diagnostics(
            {"meta": {"profile": [context.EXCHANGE_BUNDLE_PROFILE]}},
            "Invalid Bundle",
        )
        self.assertEqual(len(fallback), 1)
        self.assertEqual(fallback[0]["code"], "mobile-exchange.unclassified")
        for result in fallback:
            self.assertIn(result["code"], registered)
            self.assertEqual(result["reason"], registered[result["code"]])
        self.assertEqual(diagnostics.PRODUCER_RULE_REASONS, registered)
        with self.assertRaisesRegex(ValueError, "is not registered"):
            diagnostics.contract_failure(
                "mobile-output.dynamic-and-unregistered",
                "Observation.valueQuantity.code",
                "detail",
                reason="A custom reason must not bypass the registry.",
            )

    def test_adapter_observation_claims_exactly_semantic_plus_adapter(self) -> None:
        shared = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-heart-rate"
        )
        adapter = (
            "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
            "health-connect-observation"
        )
        observation = {
            "resourceType": "Observation",
            "meta": {"profile": [shared, adapter]},
        }
        profile_validation.validate_adapter_profile_claim(observation, "Observation")
        for extra in (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-observation",
            "http://hl7.org/fhir/StructureDefinition/heartrate",
        ):
            invalid = copy.deepcopy(observation)
            invalid["meta"]["profile"].append(extra)
            with self.subTest(extra=extra), self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                "exactly one semantic profile",
            ):
                profile_validation.validate_adapter_profile_claim(invalid, "Observation")

        missing_shared = copy.deepcopy(observation)
        missing_shared["meta"]["profile"] = [adapter]
        with self.assertRaises(diagnostics.ProducerValidationError):
            profile_validation.validate_adapter_profile_claim(missing_shared, "Observation")

        sensor = copy.deepcopy(observation)
        sensor["meta"]["profile"][0] = (
            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
            "grove-sensor-ecg-observation"
        )
        profile_validation.validate_adapter_profile_claim(sensor, "Observation")

        # A producer manifest is a package capability declaration, not a claim that
        # every resource was produced by every listed adapter. Source-neutral output
        # therefore remains valid when an otherwise unused adapter package is present.
        source_neutral = {
            "resourceType": "Observation", "meta": {"profile": [shared]}
        }
        profile_validation.validate_adapter_profile_claim(
            source_neutral, "Observation", {adapter}
        )
        profile_validation.validate_active_observation_profile_claim(
            source_neutral, "Observation", {adapter}
        )
        wrong_adapter = copy.deepcopy(observation)
        wrong_adapter["meta"]["profile"][1] = (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-observation"
        )
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exact package is absent"
        ):
            profile_validation.validate_adapter_profile_claim(
                wrong_adapter, "Observation", {adapter}
            )

    def test_adapter_source_markers_require_their_adapter_profile(self) -> None:
        shared = (
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-heart-rate"
        )
        base = {
            "resourceType": "Observation",
            "meta": {"profile": [shared]},
            "code": {"coding": []},
            "extension": [],
        }
        healthkit = copy.deepcopy(base)
        healthkit["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-source-type-extension",
                "valueCode": "HKQuantityTypeIdentifierHeartRate",
            }
        )
        health_connect = copy.deepcopy(base)
        health_connect["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type",
                "valueCode": "HeartRateRecord",
            }
        )
        provider = copy.deepcopy(base)
        provider["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                "valueCode": "withings",
            }
        )
        sensorkit = copy.deepcopy(base)
        sensorkit["extension"].append(
            {
                "url": "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type",
                "valueCode": "accelerometer",
            }
        )
        for name, resource in (
            ("HealthKit", healthkit),
            ("Health Connect", health_connect),
            ("Provider", provider),
            ("SensorKit", sensorkit),
        ):
            with self.subTest(adapter=name), self.assertRaisesRegex(
                diagnostics.ProducerValidationError,
                rf"{name} source marker without an exact {name} adapter profile",
            ):
                profile_validation.validate_adapter_source_marker_claim(resource, "Observation")

    def test_every_adapter_profile_requires_its_exact_manifest_package(self) -> None:
        graph = json.loads(
            (ROOT / "catalog/package-graph.json").read_text(encoding="utf-8")
        )
        expected_by_package = {
            package["packageId"]: {
                f"{package['canonical']}/StructureDefinition/{profile}"
                for profile in package["profiles"]
            }
            for package in graph["packages"]
            if package["packageId"] in context.ADAPTER_PACKAGE_PROFILES
        }
        self.assertEqual(context.ADAPTER_PACKAGE_PROFILES, expected_by_package)
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        profiles = [
            claims["healthConnectPlatformExclusiveClaims"]["profiles"][0],
            claims["sensorKitPlatformExclusiveClaims"]["profiles"][0],
            claims["sensorKitRecordingDocumentClaim"]["profiles"][1],
            claims["providerRecordingDocumentClaim"]["profiles"][1],
            *[
                claim["profile"]
                for claim in claims["adapterConversionProvenanceClaims"]
            ],
        ]
        for profile in profiles:
            resource = {"resourceType": "Basic", "meta": {"profile": [profile]}}
            with self.subTest(profile=profile), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "exact package is absent"
            ):
                profile_validation.validate_active_adapter_package_claims(
                    resource, "Resource", set()
                )
            profile_validation.validate_active_adapter_package_claims(
                resource, "Resource", {profile}
            )

    def test_conversion_claim_rules_never_encode_retraction_by_status_mutation(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        for claim in claims["adapterConversionProvenanceClaims"]:
            rule = claim["rule"]
            with self.subTest(adapter=claim["adapter"]):
                self.assertNotIn("entered-in-error", rule)
                self.assertIn("never encodes retraction by mutating output status", rule)
                self.assertIn("separate retraction Bundle", rule)
                self.assertIn("no conversion Provenance", rule)

    def test_adapter_only_active_output_types_reject_unprofiled_mobile_targets(self) -> None:
        claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )
        expected = {
            claims["healthConnectSpecimenClaim"]["resourceType"]:
                claims["healthConnectSpecimenClaim"]["profile"],
            **{
                claim["resourceType"]: claim["profile"]
                for claim in claims["healthKitPlatformExclusiveResourceClaims"]
            },
        }
        for resource_type, profile in expected.items():
            with self.subTest(resource_type=resource_type, shape="unprofiled"), self.assertRaisesRegex(
                diagnostics.ProducerValidationError, "adapter-only profile"
            ):
                profile_validation.validate_active_adapter_only_output_profile_claim(
                    {"resourceType": resource_type}, resource_type
                )
            with self.subTest(resource_type=resource_type, shape="exact"):
                profile_validation.validate_active_adapter_only_output_profile_claim(
                    {"resourceType": resource_type, "meta": {"profile": [profile]}},
                    resource_type,
                )

    def test_adapter_source_types_are_explicit_and_contract_bound(self) -> None:
        healthkit_catalog = json.loads(
            (ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8")
        )
        healthkit_row = next(
            row for row in healthkit_catalog["rows"]
            if row["sourceTypeIdentifier"] == "HKQuantityTypeIdentifierHeartRate"
        )
        healthkit = {
            "resourceType": "Observation",
            "meta": {"profile": [
                *healthkit_row["profiles"],
                "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
                "healthkit-observation",
            ]},
            "extension": [{
                "url": healthkit_catalog["sourceTypeExtension"]["url"],
                "valueCode": healthkit_row["sourceTypeIdentifier"],
            }],
        }
        healthkit_validation.validate_healthkit_source_type(healthkit, "HealthKit")
        missing_healthkit = copy.deepcopy(healthkit)
        missing_healthkit["extension"] = []
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "exactly one.*HealthKit source-type"
        ):
            healthkit_validation.validate_healthkit_source_type(missing_healthkit, "HealthKit")

        health_connect_catalog = json.loads(
            (ROOT / "catalog/health-connect-adapter.json").read_text(encoding="utf-8")
        )
        health_connect = {
            "resourceType": "Observation",
            "meta": {"profile": [
                "https://grovealliance.org/fhir/mobile/StructureDefinition/"
                "grove-mobile-heart-rate",
                "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
                "health-connect-observation",
            ]},
            "extension": [{
                "url": health_connect_catalog["sourceTypeExtension"]["url"],
                "valueCode": "HeartRateRecord",
            }],
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/source-record/test-key/1",
                    "v2:test-key:1:" + "A" * 43,
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/source-output/test-key/1",
                    "v2:test-key:1:" + "B" * 43,
                ),
            ],
        }
        health_connect_validation.validate_health_connect_source_type(health_connect, "HealthConnect")
        wrong_record = copy.deepcopy(health_connect)
        wrong_record["extension"][0]["valueCode"] = "StepsRecord"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "does not admit its claimed measurement"
        ):
            health_connect_validation.validate_health_connect_source_type(wrong_record, "HealthConnect")

        clear_identifier = copy.deepcopy(health_connect)
        clear_identifier["identifier"].append({
            "system": "https://source.example/native",
            "value": "clear-native-id",
        })
        health_connect_validation.validate_health_connect_source_type(clear_identifier, "HealthConnect")
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "catalog-designated primary"
        ):
            identity.validate_governed_source_identifiers(
                [clear_identifier], "HealthConnect event"
            )

        invalid_unselected_system = copy.deepcopy(health_connect)
        invalid_unselected_system["identifier"][0]["system"] = "relative/system"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "absolute RFC 3986 URI"
        ):
            health_connect_validation.validate_health_connect_source_type(
                invalid_unselected_system, "HealthConnect"
            )

        connected_catalog = json.loads(
            (ROOT / "catalog/providers-adapter.json").read_text(encoding="utf-8")
        )
        provider_components = [
            "google-health-api",
            "heart-rate",
            "https://accounts.example.org",
            "participant-1",
            "native-1",
        ]
        source_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="provider-record", components=provider_components,
        )
        output_value = derive_hmac_identity(
            key=bytes(range(32)), key_id="test-key", epoch=1,
            identity_kind="provider-output",
            components=[
                "google-health-api", "heart-rate", "https://accounts.example.org",
                "participant-1", "native-1", "source-artifact", "native-recording",
            ],
        )
        connected = {
            "resourceType": "DocumentReference",
            "meta": {"profile": [
                connected_catalog["recordingDocument"]["sourceNeutralProfile"],
                connected_catalog["recordingDocument"]["adapterProfile"],
            ]},
            "identifier": [
                typed_identifier(
                    "source-record",
                    "https://example.org/fhir/NamingSystem/provider-record/test-key/1",
                    source_value,
                ),
                typed_identifier(
                    "source-output",
                    "https://example.org/fhir/NamingSystem/provider-output/test-key/1",
                    output_value,
                ),
            ],
            "extension": [
                {
                    "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                    "valueCode": "google-health-api",
                },
                {
                    "url": connected_catalog["sourceTypeExtension"]["url"],
                    "valueCode": "google-health-api/heart-rate",
                },
            ],
        }
        providers.validate_provider_identity(connected, "Connected")
        cross_provider = copy.deepcopy(connected)
        cross_provider["extension"][1]["valueCode"] = "oura/heartrate"
        with self.assertRaisesRegex(
            diagnostics.ProducerValidationError, "unknown or cross-provider"
        ):
            providers.validate_provider_identity(cross_provider, "Connected")
