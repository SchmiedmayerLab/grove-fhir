# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog/providers-adapter.json"
MEASUREMENT_PATH = ROOT / "catalog/measurement-catalog.json"
GRAPH_PATH = ROOT / "catalog/package-graph.json"


class ProviderCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.measurements = json.loads(MEASUREMENT_PATH.read_text(encoding="utf-8"))
        cls.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        cls.claims = json.loads(
            (ROOT / "catalog/profile-claims.json").read_text(encoding="utf-8")
        )

    def test_release_and_package_identity_are_exact(self) -> None:
        self.assertEqual(self.catalog["schemaVersion"], 1)
        self.assertEqual(self.catalog["fhirVersion"], "4.0.1")
        self.assertEqual(self.catalog["version"], "0.6.0")
        self.assertEqual(
            self.catalog["packageId"], "org.grovealliance.fhir.providers"
        )
        self.assertEqual(
            self.catalog["sourceTypeExtension"]["codeRule"],
            "provider id + '/' + exact source token; the atomic Withings blood-pressure output uses withings/getmeas:9+10",
        )
        self.assertEqual(
            self.catalog["providerExtension"],
            {
                "url": "https://grovealliance.org/fhir/providers/StructureDefinition/provider",
                "codeSystem": "https://grovealliance.org/fhir/providers/CodeSystem/provider",
                "r4Element": "Observation.extension.valueCode or DocumentReference.extension.valueCode",
                "cardinality": "exactly one",
                "rule": "Every admitted connected-provider output states the exact provider id that owns its catalog row.",
            },
        )
        self.assertTrue(
            self.catalog["recordingDocument"]["adapterProfile"].endswith(
                "/providers-recording-document"
            )
        )
        self.assertTrue(
            self.catalog["conversionProvenanceProfile"].endswith(
                "/providers-conversion-provenance"
            )
        )
        package = next(
            package
            for package in self.graph["packages"]
            if package["source"] == "providers"
        )
        self.assertEqual(package["packageId"], self.catalog["packageId"])
        self.assertEqual(package["canonical"], self.catalog["canonical"])
        self.assertEqual(
            package["dependencies"],
            [
                "hl7.terminology.r4#7.3.0",
                "hl7.fhir.uv.extensions.r4#5.3.0",
                "org.grovealliance.fhir.mobile#0.6.0",
                "org.grovealliance.fhir.sensor#0.6.0",
            ],
        )
        self.assertEqual(
            set(package["profiles"]),
            {
                "providers-conversion-provenance",
                "providers-observation",
                "providers-recording-document",
            },
        )
        provenance = next(
            claim for claim in self.claims["adapterConversionProvenanceClaims"]
            if claim["adapter"] == "providers"
        )
        self.assertEqual(provenance["profile"], self.catalog["conversionProvenanceProfile"])
        self.assertEqual(provenance["sourceIdentifierRole"], "source-record")
        self.assertEqual(provenance["sourceIdentityKind"], "provider-record")
        self.assertIn(
            self.catalog["recordingDocument"]["adapterProfile"],
            provenance["targetAdapterProfiles"],
        )
        abstract_profile = self.catalog["adapterProfile"]
        self.assertNotIn(
            abstract_profile,
            self.claims["observationAdapterClaim"]["adapterProfiles"],
        )
        self.assertNotIn(abstract_profile, provenance["targetAdapterProfiles"])
        admission = self.catalog["rawPayloadAdmission"]
        self.assertEqual(
            admission["allowedAssertions"],
            ["caller-authorized-opaque-payload", "verified-sanitized-input"],
        )
        self.assertIn("exactly one", admission["failureRule"])
        self.assertTrue(admission["notFHIRAuthorization"])

    def test_provider_and_source_type_inventory_is_closed(self) -> None:
        source_evidence = self.catalog["sourceEvidence"]
        self.assertEqual(
            source_evidence["accessed"],
            "2026-08-20",
        )
        self.assertIn("already-obtained payloads", source_evidence["scope"])
        self.assertIn("providers[].sourceTypes[].token", source_evidence["tokenBinding"])
        evidence_providers = {
            provider["id"]: provider for provider in source_evidence["providers"]
        }
        self.assertEqual(
            {provider_id: provider["version"] for provider_id, provider in evidence_providers.items()},
            {"google-health-api": "v4", "oura": "2.0", "withings": "2.0"},
        )
        for provider in evidence_providers.values():
            self.assertTrue(provider["documentation"])
            self.assertTrue(
                all(url.startswith("https://") for url in provider["documentation"])
            )
        providers = {provider["id"]: provider for provider in self.catalog["providers"]}
        self.assertEqual(set(providers), {"google-health-api", "oura", "withings"})
        self.assertEqual(set(evidence_providers), set(providers))
        self.assertEqual(
            {
                provider_id: (
                    provider["measurementOwner"], provider["observationProfile"]
                )
                for provider_id, provider in providers.items()
            },
            {
                "google-health-api": (
                    "google-health",
                    "https://grovealliance.org/fhir/google-health/StructureDefinition/google-health-observation",
                ),
                "oura": (
                    "oura",
                    "https://grovealliance.org/fhir/oura/StructureDefinition/oura-observation",
                ),
                "withings": (
                    "withings",
                    "https://grovealliance.org/fhir/withings/StructureDefinition/withings-observation",
                ),
            },
        )

        expected_google = {
            "steps",
            "distance",
            "active-energy-burned",
            "weight",
            "body-fat",
            "height",
            "vo2-max",
            "daily-oxygen-saturation",
            "heart-rate-variability",
            "daily-resting-heart-rate",
            "daily-respiratory-rate",
            "blood-glucose",
            "core-body-temperature",
            "floors",
            "basal-energy-burned",
            "sleep",
            "exercise",
            "heart-rate",
        }
        expected_oura = {
            "daily_activity",
            "sleep",
            "daily_spo2",
            "workout",
            "vO2_max",
            "daily_cardiovascular_age",
            "daily_readiness",
            "heartrate",
        }
        expected_withings = {
            *(f"getmeas:{code}" for code in (
                1, 4, 5, 6, 8, 9, 10, 11, 54, 71, 73, 76, 77, 88, 91,
                123, 130, 135, 136, 137, 138, 139, 155, 167, 168, 169,
                170, 174, 175, 196,
            )),
            "getactivity:steps",
            "getactivity:distance",
            "getactivity:calories",
            "getsummary:deepsleepduration",
            "getsummary:remsleepduration",
            "getsummary:lightsleepduration",
            "getsummary:wakeupduration",
            "getsummary:hr_average",
            "getsummary:rr_average",
            "getworkouts:interval",
            "activityIntraday",
            "sleepIntraday",
        }
        for provider_id, expected in {
            "google-health-api": expected_google,
            "oura": expected_oura,
            "withings": expected_withings,
        }.items():
            provider = providers[provider_id]
            actual = [source_type["token"] for source_type in provider["sourceTypes"]]
            self.assertEqual(len(actual), len(set(actual)))
            self.assertEqual(set(actual), expected)
            self.assertEqual(provider["sourceTypeCount"], len(expected))

    def test_every_source_element_has_one_definitive_status(self) -> None:
        statuses = set(self.catalog["statusVocabulary"])
        self.assertEqual(statuses, set(self.catalog["statusDefinitions"]))
        measurement_ids = {
            measurement["id"] for measurement in self.measurements["measurements"]
        }
        for provider in self.catalog["providers"]:
            for source_type in provider["sourceTypes"]:
                self.assertIn(source_type["status"], statuses)
                elements = source_type["elements"]
                self.assertGreater(len(elements), 0)
                paths = [element["path"] for element in elements]
                self.assertEqual(len(paths), len(set(paths)))
                for element in elements:
                    status = element["status"]
                    self.assertIn(status, statuses)
                    for measurement_id in element.get("measurementIds", []):
                        self.assertIn(measurement_id, measurement_ids)
                    if status in {"supported", "platform-exclusive"}:
                        self.assertGreater(len(element.get("measurementIds", [])), 0)
                    if status == "mapped-standard":
                        self.assertEqual(
                            element.get("sensorProfile"),
                            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                            "grove-sensor-recording-document",
                        )
                        raw = source_type["raw"]
                        self.assertEqual(
                            raw["adapterProfile"],
                            self.catalog["recordingDocument"]["adapterProfile"],
                        )
                        self.assertEqual(raw["outputRole"], "native-recording")
                        self.assertEqual(raw["outputDiscriminator"], "single")
                    elif status != "supported":
                        self.assertIsInstance(element.get("reason"), str)
                        self.assertTrue(element["reason"])

    def test_admitted_semantic_profiles_match_status_owner_and_source_row(self) -> None:
        by_id = {
            measurement["id"]: measurement
            for measurement in self.measurements["measurements"]
        }
        for provider in self.catalog["providers"]:
            for source_type in provider["sourceTypes"]:
                for element in source_type["elements"]:
                    if element["status"] not in {"supported", "platform-exclusive"}:
                        continue
                    for measurement_id in element["measurementIds"]:
                        measurement = by_id[measurement_id]
                        label = (
                            f"{provider['id']}/{source_type['token']}/"
                            f"{element['path']}/{measurement_id}"
                        )
                        self.assertEqual(
                            measurement["coverage"][provider["id"]],
                            element["status"],
                            label,
                        )
                        owner = measurement.get("owner", "mobile")
                        self.assertIn(
                            owner,
                            {"mobile", provider["measurementOwner"]},
                            label,
                        )
                        if element["status"] == "platform-exclusive":
                            canonical = (
                                f"https://grovealliance.org/fhir/{owner}/"
                                f"StructureDefinition/{measurement['profile']}"
                            )
                            self.assertIn(canonical, source_type["profiles"], label)

    def test_method_choice_measurements_declare_their_aggregation(self) -> None:
        choices = {
            measurement["id"]: measurement["methodChoice"]
            for measurement in self.measurements["measurements"]
            if measurement.get("methodChoice")
        }
        for provider in self.catalog["providers"]:
            for source_type in provider["sourceTypes"]:
                for element in source_type["elements"]:
                    label = f"{provider['id']}/{source_type['token']}/{element['path']}"
                    declared = element.get("aggregationMethod", {})
                    expected = {
                        measurement_id
                        for measurement_id in element.get("measurementIds", [])
                        if measurement_id in choices
                    }
                    self.assertEqual(set(declared), expected, label)
                    for measurement_id, method in declared.items():
                        self.assertIn(method, choices[measurement_id], label)

    def test_supported_rows_match_mobile_coverage(self) -> None:
        by_id = {
            measurement["id"]: measurement
            for measurement in self.measurements["measurements"]
        }
        for provider in self.catalog["providers"]:
            for source_type in provider["sourceTypes"]:
                for element in source_type["elements"]:
                    if element["status"] != "supported":
                        continue
                    for measurement_id in element["measurementIds"]:
                        self.assertEqual(
                            by_id[measurement_id]["coverage"][provider["id"]],
                            "supported",
                            f"{provider['id']} {source_type['token']} {element['path']}",
                        )

    def test_mobile_provider_coverage_is_bidirectional(self) -> None:
        by_id = {
            measurement["id"]: measurement
            for measurement in self.measurements["measurements"]
        }
        for provider in self.catalog["providers"]:
            supported = {
                measurement_id
                for source_type in provider["sourceTypes"]
                for element in source_type["elements"]
                if element["status"] == "supported"
                for measurement_id in element["measurementIds"]
            }
            for measurement_id, measurement in by_id.items():
                claimed = measurement["coverage"][provider["id"]] == "supported"
                self.assertEqual(
                    claimed,
                    measurement_id in supported,
                    f"{provider['id']} {measurement_id}",
                )

    def test_fail_closed_provider_boundaries_are_frozen(self) -> None:
        providers = {provider["id"]: provider for provider in self.catalog["providers"]}
        google = {row["token"]: row for row in providers["google-health-api"]["sourceTypes"]}
        self.assertEqual(google["blood-glucose"]["status"], "supported")
        self.assertEqual(
            google["blood-glucose"]["elements"][0]["measurementIds"],
            ["blood-glucose-unspecified-specimen"],
        )
        self.assertEqual(google["daily-oxygen-saturation"]["status"], "supported")
        self.assertEqual(google["daily-respiratory-rate"]["status"], "supported")

        withings = {row["token"]: row for row in providers["withings"]["sourceTypes"]}
        grouped = providers["withings"]["groupedMappings"]
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]["token"], "getmeas:9+10")
        self.assertEqual(grouped[0]["members"], ["getmeas:9", "getmeas:10"])
        self.assertEqual(grouped[0]["sourceNativeId"], "the common measure-group grpid")
        self.assertEqual(grouped[0]["measurementIds"], ["blood-pressure"])
        self.assertIn("Use getmeas:9+10", grouped[0]["rule"])
        self.assertEqual(
            withings["getmeas:9"]["elements"][0]["groupedMapping"],
            "getmeas:9+10",
        )
        self.assertEqual(
            withings["getmeas:10"]["elements"][0]["groupedMapping"],
            "getmeas:9+10",
        )
        # The electrocardiogram intervals and the two atrial-fibrillation screening notifications
        # are carried under provider-scoped profiles that name exactly what they are; only the body
        # segment masses stay refused, because their consumed shape loses the segment.
        for code in (130, 135, 136, 137, 138, 139):
            row = withings[f"getmeas:{code}"]
            self.assertEqual(row["status"], "platform-exclusive")
            self.assertTrue(row["profiles"])
        for code in (174, 175):
            self.assertEqual(
                withings[f"getmeas:{code}"]["status"],
                "intentionally-unsupported",
            )

    def test_identity_compositions_and_resource_id_policy_are_exact(self) -> None:
        identity = self.catalog["identity"]
        self.assertEqual(identity["contract"], "catalog/exchange-protocol.json")
        self.assertEqual(identity["protocolVersion"], 2)
        self.assertEqual(identity["adapterId"], "providers")
        self.assertEqual(
            identity["sourceRecord"]["components"],
            [
                "provider-code",
                "source-type",
                "provider-scope-system",
                "provider-scope-value",
                "native-record-id",
            ],
        )
        self.assertEqual(
            identity["sourceOutput"]["components"],
            [
                "provider-code",
                "source-type",
                "provider-scope-system",
                "provider-scope-value",
                "native-record-id",
                "output-role",
                "output-discriminator",
            ],
        )
        self.assertEqual(identity["sourceRecord"]["identityKind"], "provider-record")
        self.assertEqual(identity["sourceOutput"]["identityKind"], "provider-output")
        self.assertIn("complete Identifier pair", identity["sourceRecord"]["scopeRule"])
        self.assertIn("never omit the system", identity["sourceRecord"]["scopeRule"].lower())
        self.assertIn("single", identity["sourceOutput"]["outputDiscriminatorRule"])
        self.assertIn("No fallback", identity["sourceOutput"]["outputDiscriminatorRule"])
        self.assertIn("optional and repository-assigned", identity["resourceIdPolicy"])
        self.assertEqual(identity["sourceArtifact"]["identityKind"], "provider-artifact")

    def test_every_provider_declares_an_identifier_scope_with_a_reason(self) -> None:
        expected_modes = {
            "account": "deployment-scoped-account-pseudonym",
            "global": "documented-global-key-space",
        }
        for provider in self.catalog["providers"]:
            with self.subTest(provider=provider["id"]):
                self.assertIn(provider["identifierScope"], {"account", "global"})
                self.assertEqual(
                    provider["providerScopeMode"],
                    expected_modes[provider["identifierScope"]],
                )
                self.assertTrue(provider["identifierScopeReason"].strip())
        self.assertNotIn("contentDerived", json.dumps(self.catalog))

    def test_a_global_provider_documents_global_uniqueness(self) -> None:
        scope_rule = self.catalog["identity"]["sourceRecord"]["scopeRule"]
        self.assertIn("documented global key-space pair", scope_rule)
        for provider in self.catalog["providers"]:
            if provider["identifierScope"] == "global":
                with self.subTest(provider=provider["id"]):
                    self.assertIn("unique", provider["identifierScopeReason"])
                    self.assertIn("never replaced with a per-account", provider["identifierScopeReason"])

    def test_missing_native_ids_receive_persistent_import_keys_not_content_hashes(self) -> None:
        rule = self.catalog["identity"]["sourceRecord"]["absentNativeId"]
        self.assertIn("Assign and persist", rule)
        self.assertIn("Never derive", rule)
        self.assertIn("serialized content", rule)

    def test_writer_record_identity_requires_source_supplied_cross_channel_evidence(self) -> None:
        writer = self.catalog["identity"]["writerRecord"]
        self.assertEqual(writer["identityKind"], "writer-record")
        self.assertEqual(writer["identifierRole"], "writer-record")
        self.assertIn("only when", writer["rule"])
        self.assertIn("not evidence", writer["rule"])


if __name__ == "__main__":
    unittest.main()
