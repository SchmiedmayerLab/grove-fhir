# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog/connected-health-adapter.json"
MEASUREMENT_PATH = ROOT / "catalog/measurement-catalog.json"
GRAPH_PATH = ROOT / "catalog/package-graph.json"


class ConnectedHealthCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.measurements = json.loads(MEASUREMENT_PATH.read_text(encoding="utf-8"))
        cls.graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

    def test_release_and_package_identity_are_exact(self) -> None:
        self.assertEqual(self.catalog["schemaVersion"], 1)
        self.assertEqual(self.catalog["fhirVersion"], "4.0.1")
        self.assertEqual(self.catalog["version"], "0.2.0")
        self.assertEqual(
            self.catalog["packageId"], "org.grovealliance.fhir.connected-health"
        )
        package = next(
            package
            for package in self.graph["packages"]
            if package["source"] == "connected-health"
        )
        self.assertEqual(package["packageId"], self.catalog["packageId"])
        self.assertEqual(package["canonical"], self.catalog["canonical"])
        self.assertEqual(
            package["dependencies"],
            ["org.grovealliance.fhir.mobile#0.2.0"],
        )
        self.assertEqual(
            set(package["profiles"]),
            {
                "connected-health-conversion-provenance",
                "connected-health-observation",
            },
        )

    def test_provider_and_source_type_inventory_is_closed(self) -> None:
        providers = {provider["id"]: provider for provider in self.catalog["providers"]}
        self.assertEqual(set(providers), {"google-health-api", "oura", "withings"})

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
                    if status == "supported":
                        self.assertGreater(len(element.get("measurementIds", [])), 0)
                    elif status == "mapped-standard":
                        self.assertEqual(
                            element.get("sensorProfile"),
                            "https://grovealliance.org/fhir/sensor/StructureDefinition/"
                            "grove-sensor-recording-document",
                        )
                    else:
                        self.assertIsInstance(element.get("reason"), str)
                        self.assertTrue(element["reason"])

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

    def test_fail_closed_provider_boundaries_are_frozen(self) -> None:
        providers = {provider["id"]: provider for provider in self.catalog["providers"]}
        google = {row["token"]: row for row in providers["google-health-api"]["sourceTypes"]}
        self.assertEqual(google["blood-glucose"]["status"], "deferred")
        self.assertNotIn(
            "measurementIds", google["blood-glucose"]["elements"][0]
        )
        self.assertEqual(google["daily-oxygen-saturation"]["status"], "deferred")
        self.assertEqual(google["daily-respiratory-rate"]["status"], "deferred")

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
        for code in (130, 135, 136, 137, 138, 139):
            self.assertEqual(
                withings[f"getmeas:{code}"]["status"],
                "intentionally-unsupported",
            )

    def test_identity_preimages_and_resource_id_policy_are_exact(self) -> None:
        identity = self.catalog["identity"]
        self.assertIn("RFC 8785/JCS", identity["canonicalization"])
        self.assertEqual(
            identity["sourceRecord"]["preimage"],
            [
                "providerCode",
                "providerAccountIdentifier.system",
                "providerAccountIdentifier.value",
                "sourceType",
                "sourceNativeId",
            ],
        )
        self.assertEqual(
            identity["output"]["preimage"],
            [
                "sourceRecordIdentifier.system",
                "sourceRecordIdentifier.value",
                "outputDiscriminator",
            ],
        )
        self.assertEqual(
            identity["output"]["outputDiscriminatorRule"],
            {
                "ordinarySupportedMeasurement": (
                    "the exact measurementId string from the supported element mapping"
                ),
                "groupedMapping": (
                    "the exact outputDiscriminator declared on that groupedMappings row"
                ),
                "noFallback": True,
            },
        )
        self.assertIn("optional and repository-assigned", identity["resourceIdPolicy"])
        for vector in identity["vectors"]:
            preimage = json.dumps(
                vector["inputs"], ensure_ascii=False, separators=(",", ":")
            )
            if "canonicalPreimage" in vector:
                self.assertEqual(preimage, vector["canonicalPreimage"])
            if "canonicalUtf8Hex" in vector:
                self.assertEqual(preimage.encode("utf-8").hex(), vector["canonicalUtf8Hex"])
            self.assertEqual(
                "v1:" + hashlib.sha256(preimage.encode("utf-8")).hexdigest(),
                vector["identifierValue"],
            )


if __name__ == "__main__":
    unittest.main()
