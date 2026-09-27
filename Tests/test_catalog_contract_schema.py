"""Regression tests for the recursively closed normative catalog schemas."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
CONTRACT_SCHEMA = CATALOG_DIR / "schemas/catalog-contracts.schema.json"
VALIDATOR = ROOT / "Scripts/validate-json-schema.cjs"


def _read(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class CatalogContractSchemaTests(unittest.TestCase):
    maxDiff = None

    def _validation_result(
        self,
        document: dict[str, Any],
        schema: Path = CONTRACT_SCHEMA,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["node", str(VALIDATOR), str(schema), "-"],
            cwd=ROOT,
            input=json.dumps(document),
            capture_output=True,
            text=True,
            check=False,
        )

    def _assert_valid(
        self,
        document: dict[str, Any],
        schema: Path = CONTRACT_SCHEMA,
    ) -> None:
        result = self._validation_result(document, schema)
        self.assertEqual(result.returncode, 0, result.stderr)

    def _assert_invalid(
        self,
        document: dict[str, Any],
        schema: Path = CONTRACT_SCHEMA,
    ) -> None:
        result = self._validation_result(document, schema)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    @staticmethod
    def _at(document: dict[str, Any], path: tuple[str | int, ...]) -> Any:
        value: Any = document
        for component in path:
            value = value[component]
        return value

    def test_release_manifest_normative_catalogs_validate_against_declared_schema(self) -> None:
        manifest = _read("catalog/release-manifest.json")
        for declaration in manifest["normativeCatalogs"]:
            with self.subTest(path=declaration["path"]):
                self._assert_valid(
                    _read(declaration["path"]),
                    ROOT / declaration["schema"],
                )

    def test_shared_contract_catalogs_reject_unknown_members_at_nested_boundaries(self) -> None:
        cases: dict[str, tuple[tuple[str | int, ...], ...]] = {
            "catalog/format-registry.json": (
                (),
                ("encodings",),
                ("encodings", "csv"),
                ("mediaTypes",),
                ("formats",),
                ("formats", "heart-rate-samples"),
                ("formats", "heart-rate-samples", "columns", 0),
                ("formats", "fhir-resource", "specification"),
                ("formats", "photoplethysmogram-samples", "specification"),
                ("formats", "photoplethysmogram-samples", "specification", "primitives"),
                ("formats", "photoplethysmogram-samples", "specification", "record", 0),
            ),
            "catalog/health-connect-adapter.json": (
                (),
                ("source",),
                ("sourceTypeExtension",),
                ("dataOriginApplication",),
                ("statusVocabulary",),
                ("outputCountRules",),
                ("graphRules",),
                ("graphRules", "exactly-one-admitted-specimen-output"),
                ("graphRules", "exactly-one-admitted-specimen-output", "outputs", 0),
                ("adapterMeasurements", 0),
                ("adapterMeasurements", 0, "code"),
                ("recordTypes", 0),
                ("recordTypes", 0, "outputs", 0),
                ("contextMappings",),
                ("contextMappings", "bloodGlucoseSpecimen"),
                ("contextMappings", "bloodGlucoseSpecimen", "values", 0),
                ("contextMappings", "bloodGlucoseSpecimen", "values", 0, "coding"),
                ("contextMappings", "bloodGlucoseMealContext", "relationToMeal"),
                ("contextMappings", "sessionTitle"),
                ("recordingDeviceIdentity",),
                ("identity",),
                ("identity", "sourceRecord"),
                ("identity", "sourceRecord", "bindings"),
                ("identity", "sourceOutput"),
                ("identity", "writerRecord"),
            ),
            "catalog/healthkit-adapter.json": (
                (),
                ("source",),
                ("source", "sdkBaseline"),
                ("source", "evidence", 0),
                ("producerCanonicalization",),
                ("sourceTypeExtension",),
                ("clinicalRecordAdmission",),
                ("statusVocabulary",),
                ("standardAdapterClaims",),
                ("standardAdapterClaims", "body-mass-index"),
                ("sensorAdapterClaims", "electrocardiogram"),
                ("sensorAdapterClaims", "electrocardiogram", "leadCode"),
                ("sensorAdapterClaims", "electrocardiogram", "correlatedSymptomEvidence"),
                ("sensorAdapterClaims", "electrocardiogram", "outputs", 0),
                ("sensorAdapterClaims", "electrocardiogram", "closedValueMappings", "classification", "values", 0),
                ("derivedAggregates", 0),
                ("rows", 0),
                ("recordingDeviceIdentity",),
                ("applicationDeviceIdentity",),
                ("applicationDeviceIdentity", "bundleIdentifier"),
                ("identity",),
                ("identity", "sourceContext"),
            ),
            "catalog/providers-adapter.json": (
                (),
                ("sourceTypeExtension",),
                ("providerExtension",),
                ("recordingDocument",),
                ("rawPayloadAdmission",),
                ("statusVocabulary",),
                ("sourceEvidence",),
                ("sourceEvidence", "providers", 0),
                ("providers", 0),
                ("providers", 0, "sourceTypes", 0),
                ("providers", 0, "sourceTypes", 0, "elements", 0),
                ("providers", 2, "groupedMappings", 0),
                ("identity",),
                ("recordingDeviceIdentity",),
            ),
            "catalog/sensor-catalog.json": (
                (),
                ("contracts", 0),
                ("contracts", 0, "timing"),
                ("contracts", 0, "timing", "vectors", 0),
                ("contracts", 1),
                ("contracts", 1, "code"),
                ("contracts", 1, "channelUnit"),
                ("contracts", 2),
                ("contracts", 2, "integrity"),
                ("contracts", 2, "payloadAdmission"),
                ("contracts", 3),
            ),
            "catalog/sensorkit-adapter.json": (
                (),
                ("sourceTypeExtension",),
                ("statusVocabulary",),
                ("sourceEvidence",),
                ("sourceEvidence", "sdkBaseline"),
                ("inventoryScopes",),
                ("profileClaims",),
                ("profileClaims", "recordingDocument"),
                ("rawPayloadAdmission",),
                ("entries", 0),
                ("entries", 0, "structured"),
                ("entries", 4, "structured", "graphContract"),
                ("entries", 0, "raw"),
                ("identity",),
                ("recordingDeviceIdentity",),
            ),
            "catalog/profile-claims.json": (
                (),
                ("observationAdapterClaim",),
                ("observationAdapterClaim", "standardAdapterClaims", 0),
                ("sensorRecordingDocumentClaim",),
                ("activeDeviceClaims", 0),
                ("activeQuestionnaireResponseClaim",),
                ("healthKitPlatformExclusiveResourceClaims", 0),
                ("healthConnectSpecimenClaim",),
                ("sensorKitHybridObservationClaims",),
                ("adapterConversionProvenanceClaims", 0),
            ),
        }

        for relative_path, paths in cases.items():
            document = _read(relative_path)
            for path in paths:
                with self.subTest(catalog=relative_path, path=path):
                    mutated = copy.deepcopy(document)
                    target = self._at(mutated, path)
                    self.assertIsInstance(target, dict)
                    target["unexpectedContractMember"] = "must fail closed"
                    self._assert_invalid(mutated)

    def test_release_constants_and_schema_uris_fail_closed(self) -> None:
        manifest = _read("catalog/release-manifest.json")
        for declaration in manifest["normativeCatalogs"]:
            document = _read(declaration["path"])
            schema = ROOT / declaration["schema"]
            for key, value in (
                ("$schema", "https://example.org/not-the-declared-schema.json"),
                ("schemaVersion", 2),
            ):
                with self.subTest(path=declaration["path"], key=key):
                    mutated = copy.deepcopy(document)
                    mutated[key] = value
                    self._assert_invalid(mutated, schema)

            version_key = "releaseVersion" if declaration["path"].endswith("release-manifest.json") else "version"
            if version_key in document:
                with self.subTest(path=declaration["path"], key=version_key):
                    mutated = copy.deepcopy(document)
                    mutated[version_key] = "9.9.9"
                    self._assert_invalid(mutated, schema)

    def test_package_graph_rows_are_discriminated_by_source(self) -> None:
        graph = _read("catalog/package-graph.json")
        schema = CATALOG_DIR / "schemas/package-graph.schema.json"
        self._assert_valid(graph, schema)

        for field, replacement in (
            ("packageId", "org.grovealliance.fhir.healthkit"),
            ("canonical", "https://grovealliance.org/fhir/healthkit"),
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(graph)
                mutated["packages"][0][field] = replacement
                self._assert_invalid(mutated, schema)

    def test_uri_date_and_date_time_formats_are_asserted(self) -> None:
        measurement_catalog = _read("catalog/measurement-catalog.json")
        invalid_uri = copy.deepcopy(measurement_catalog)
        invalid_uri["measurements"][0]["code"]["system"] = "not a uri"
        self._assert_invalid(
            invalid_uri,
            CATALOG_DIR / "schemas/measurement-catalog.schema.json",
        )

        healthkit = _read("catalog/healthkit-adapter.json")
        invalid_date = copy.deepcopy(healthkit)
        invalid_date["source"]["accessed"] = "2026-02-30"
        self._assert_invalid(invalid_date)

        sensor = _read("catalog/sensor-catalog.json")
        invalid_date_time = copy.deepcopy(sensor)
        invalid_date_time["contracts"][0]["timing"]["vectors"][0]["start"] = (
            "not-a-date-time"
        )
        self._assert_invalid(invalid_date_time)

    def test_healthkit_clinical_admission_accepts_only_dstu2_and_r4(self) -> None:
        healthkit = _read("catalog/healthkit-adapter.json")
        admission = healthkit["clinicalRecordAdmission"]
        self.assertEqual(admission["payloadFormat"], "fhir-resource")
        self.assertEqual(
            admission["sourceFHIRReleaseField"], "HKFHIRVersion.fhirRelease"
        )
        self.assertEqual(admission["admittedFHIRReleases"], ["dstu2", "r4"])
        self.assertEqual(admission["rejectedFHIRReleases"], ["unknown"])
        self.assertEqual(
            admission["fhirRepresentation"],
            {
                "resourceType": "DocumentReference",
                "contentTypeByRelease": {
                    "dstu2": "application/fhir+json; fhirVersion=1.0",
                    "r4": "application/fhir+json; fhirVersion=4.0",
                },
            },
        )
        clinical_rows = [
            row
            for row in healthkit["rows"]
            if row["sourceTypeIdentifier"].startswith("HKClinicalTypeIdentifier")
        ]
        self.assertEqual(len(clinical_rows), 9)
        self.assertTrue(
            all(
                row["clinicalAdmissionContract"] == "clinicalRecordAdmission"
                for row in clinical_rows
            )
        )
        self._assert_valid(healthkit)

        for replacement in (["r4"], ["dstu2"], ["dstu2", "r4", "r5"]):
            with self.subTest(admittedFHIRReleases=replacement):
                rejected = copy.deepcopy(healthkit)
                rejected["clinicalRecordAdmission"]["admittedFHIRReleases"] = replacement
                self._assert_invalid(rejected)

        omitted = copy.deepcopy(healthkit)
        del omitted["clinicalRecordAdmission"]["admittedFHIRReleases"]
        self._assert_invalid(omitted)

        for path, replacement in (
            (("contentTypeByRelease", "dstu2"), "application/fhir+json"),
        ):
            with self.subTest(fhirRepresentation=path):
                mutated = copy.deepcopy(healthkit)
                target = mutated["clinicalRecordAdmission"]["fhirRepresentation"]
                for segment in path[:-1]:
                    target = target[segment]
                target[path[-1]] = replacement
                self._assert_invalid(mutated)

        missing_representation = copy.deepcopy(healthkit)
        del missing_representation["clinicalRecordAdmission"]["fhirRepresentation"]
        self._assert_invalid(missing_representation)

        unbound_row = copy.deepcopy(healthkit)
        row = next(
            candidate
            for candidate in unbound_row["rows"]
            if candidate["sourceTypeIdentifier"].startswith("HKClinicalTypeIdentifier")
        )
        del row["clinicalAdmissionContract"]
        self._assert_invalid(unbound_row)

        disguised_clinical_row = copy.deepcopy(healthkit)
        row = next(
            candidate
            for candidate in disguised_clinical_row["rows"]
            if candidate["sourceTypeIdentifier"].startswith("HKClinicalTypeIdentifier")
        )
        row["profiles"] = [
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation"
        ]
        del row["clinicalAdmissionContract"]
        self._assert_invalid(disguised_clinical_row)

        extra_clinical_profile = copy.deepcopy(healthkit)
        row = next(
            candidate
            for candidate in extra_clinical_profile["rows"]
            if candidate["sourceTypeIdentifier"].startswith("HKClinicalTypeIdentifier")
        )
        row["profiles"].append(
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation"
        )
        self._assert_invalid(extra_clinical_profile)

        nonclinical_claiming_clinical_profile = copy.deepcopy(healthkit)
        row = next(
            candidate
            for candidate in nonclinical_claiming_clinical_profile["rows"]
            if not candidate["sourceTypeIdentifier"].startswith("HKClinicalTypeIdentifier")
        )
        row["profiles"] = [
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-clinical-record-document"
        ]
        row["clinicalAdmissionContract"] = "clinicalRecordAdmission"
        self._assert_invalid(nonclinical_claiming_clinical_profile)

    def test_profile_claim_modes_are_exact_unique_and_complete(self) -> None:
        claims = _read("catalog/profile-claims.json")
        self._assert_valid(claims)

        for field in ("activeDeviceClaims", "adapterConversionProvenanceClaims"):
            with self.subTest(field=field, mutation="duplicate-and-omit"):
                duplicated = copy.deepcopy(claims)
                duplicated[field][1] = copy.deepcopy(duplicated[field][0])
                self._assert_invalid(duplicated)

            with self.subTest(field=field, mutation="missing"):
                missing = copy.deepcopy(claims)
                missing[field].pop()
                self._assert_invalid(missing)

        mismatched_device_mode = copy.deepcopy(claims)
        mismatched_device_mode["activeDeviceClaims"][0]["profiles"] = [
            "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-application-device"
        ]
        self._assert_invalid(mismatched_device_mode)

        mismatched_provenance_mode = copy.deepcopy(claims)
        mismatched_provenance_mode["adapterConversionProvenanceClaims"][0]["profile"] = (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-conversion-provenance"
        )
        self._assert_invalid(mismatched_provenance_mode)

    def test_governed_source_identifier_primary_and_disclosure_rules_are_closed(self) -> None:
        protocol = _read("catalog/exchange-protocol.json")
        governed = protocol["governedSourceIdentifier"]["validation"]
        self.assertEqual(
            governed["designatedNode"]["designationMode"],
            "catalog-output-selector",
        )
        self.assertEqual(
            governed["identifier"]["classification"]["activeOutputNonGroveIdentifier"],
            "governed-source-identifier",
        )
        source_type = governed["identifier"]["type"]
        self.assertTrue(source_type["textOnlyAllowed"])
        self.assertTrue(source_type["coding"]["systemAbsoluteUri"])
        self.assertEqual(source_type["coding"]["codeLexicalForm"], "fhir-code")
        self.assertFalse(source_type["coding"]["groveRoleCodingAllowed"])
        enforcement = governed["forbiddenIdentityUseEnforcement"]
        self.assertEqual(
            enforcement["observationComponent"]["r4Paths"],
            ["Observation.component.value[x]"],
        )
        self.assertEqual(
            enforcement["untypedMetadata"]["matchRule"],
            "no-generic-carrier-admitted",
        )
        information = protocol["opaqueIdentity"]["informationPreservation"]
        self.assertFalse(information["reversible"])
        self.assertEqual(
            information["exactNativeRoundTrip"],
            "optional-governed-source-identifier-on-catalog-designated-primary",
        )

        selectors = governed["designatedNode"]["adapterSelectors"]
        healthkit = _read(selectors["healthkit"]["catalog"])
        self.assertTrue(healthkit[selectors["healthkit"]["rowCollection"]])
        self.assertIn(
            "https://grovealliance.org/fhir/mobile/StructureDefinition/"
            "grove-mobile-workout-segment",
            selectors["healthkit"]["excludedProfiles"],
        )
        health_connect = _read(selectors["health-connect"]["catalog"])
        admitted_count_rules = {
            output["countRule"]
            for row in health_connect[selectors["health-connect"]["rowCollection"]]
            for output in row.get("outputs", [])
        }
        self.assertTrue(
            set(selectors["health-connect"]["eligibleCountRules"])
            <= admitted_count_rules
        )

    def test_health_connect_data_origin_is_identifier_only_and_not_an_event_node(self) -> None:
        catalog = _read("catalog/health-connect-adapter.json")
        contract = catalog["dataOriginApplication"]
        self.assertEqual(contract["referenceMode"], "identifier-only")
        self.assertFalse(contract["literalReferenceAllowed"])
        self.assertFalse(contract["eventBundleEntryRequired"])
        self.assertFalse(contract["profileClaimRequired"])

        for field, replacement in (
            ("referenceMode", "literal-reference"),
            ("literalReferenceAllowed", True),
            ("eventBundleEntryRequired", True),
            ("profileClaimRequired", True),
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(catalog)
                mutated["dataOriginApplication"][field] = replacement
                self._assert_invalid(mutated)

    def test_status_discriminators_reject_incomplete_or_mixed_rows(self) -> None:
        health_connect = _read("catalog/health-connect-adapter.json")
        supported = next(row for row in health_connect["recordTypes"] if row["status"] == "supported")
        mutated_health_connect = copy.deepcopy(health_connect)
        index = health_connect["recordTypes"].index(supported)
        mutated_health_connect["recordTypes"][index]["status"] = "deferred"
        self._assert_invalid(mutated_health_connect)

        providers = _read("catalog/providers-adapter.json")
        mutated_providers = copy.deepcopy(providers)
        source_type = next(
            row
            for provider in mutated_providers["providers"]
            for row in provider["sourceTypes"]
            if row["status"] == "mapped-standard"
        )
        del source_type["raw"]
        self._assert_invalid(mutated_providers)

        sensor = _read("catalog/sensor-catalog.json")
        mutated_sensor = copy.deepcopy(sensor)
        mutated_sensor["contracts"][0]["id"] = "unknown-contract-kind"
        self._assert_invalid(mutated_sensor)

        sensorkit = _read("catalog/sensorkit-adapter.json")
        mutated_sensorkit = copy.deepcopy(sensorkit)
        deferred = next(row for row in mutated_sensorkit["entries"] if row["status"] == "deferred")
        deferred["structured"] = {"status": "deferred", "reason": "must remain absent"}
        self._assert_invalid(mutated_sensorkit)


if __name__ == "__main__":
    unittest.main()
