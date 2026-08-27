"""Validate the normative source-neutral measurement catalog."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SOURCES = {"healthkit", "health-connect", "sensorkit", "google-health-api", "oura", "withings"}


class MeasurementCatalogTests(unittest.TestCase):
    def test_catalog_is_closed_complete_and_matches_package_graph(self) -> None:
        catalog = json.loads((ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8"))
        graph = json.loads((ROOT / "catalog/package-graph.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["fhirVersion"], "4.0.1")
        self.assertEqual(catalog["version"], "0.6.0")
        package_profiles = {
            package["source"]: set(package["profiles"]) for package in graph["packages"]
        }
        profiles = package_profiles["mobile"]
        statuses = set(catalog["statusVocabulary"])
        self.assertEqual(set(catalog["statusDefinitions"]), statuses)
        for definition in catalog["statusDefinitions"].values():
            self.assertIsInstance(definition, str)
            self.assertTrue(definition)
        identifiers: set[str] = set()
        for measurement in catalog["measurements"]:
            self.assertNotIn(measurement["id"], identifiers)
            identifiers.add(measurement["id"])
            owner = measurement.get("owner", "mobile")
            self.assertIn(measurement["profile"], package_profiles[owner])
            self.assertEqual(set(measurement["coverage"]), SOURCES)
            self.assertTrue(set(measurement["coverage"].values()) <= statuses)
            mapped_sources = {
                source
                for source, status in measurement["coverage"].items()
                if status == "mapped-standard"
            }
            self.assertEqual(
                set(measurement.get("coverageDetails", {})), mapped_sources
            )
            for source, detail in measurement.get("coverageDetails", {}).items():
                self.assertIn("does not implement the Mobile", detail["reason"])
                self.assertTrue(detail["sourceTokens"])
                self.assertTrue(
                    detail["alternateRepresentation"].startswith(
                        "https://grovealliance.org/fhir/"
                    )
                )
            self.assertIn(measurement["effective"], {"dateTime", "Period"})
            code = measurement["code"]
            self.assertTrue(code["system"].startswith(("http://loinc.org", "https://grovealliance.org/fhir/")))
            required_codings = measurement.get("requiredCodings", [])
            self.assertEqual(
                len({coding["slice"] for coding in required_codings}),
                len(required_codings),
            )
            self.assertEqual(
                len({(coding["system"], coding["code"]) for coding in required_codings}),
                len(required_codings),
            )
            self.assertNotIn(
                (code["system"], code["code"]),
                {(coding["system"], coding["code"]) for coding in required_codings},
            )
            if measurement["quantity"] is not None:
                self.assertEqual(measurement["quantity"]["system"], "http://unitsofmeasure.org")
                self.assertIsInstance(measurement["quantity"]["unit"], str)
                self.assertTrue(measurement["quantity"]["unit"])
            for component in measurement.get("components") or []:
                if component.get("quantity"):
                    self.assertEqual(
                        component["quantity"]["system"], "http://unitsofmeasure.org"
                    )
                    self.assertIsInstance(component["quantity"]["unit"], str)
                    self.assertTrue(component["quantity"]["unit"])
                else:
                    self.assertTrue(component.get("valueSet"), measurement["id"])
        sleep_stage = next(item for item in catalog["measurements"] if item["id"] == "sleep-stage")
        self.assertEqual(
            sleep_stage["allowedValues"],
            ["awake", "in-bed", "out-of-bed", "asleep-unspecified", "light", "deep", "rem", "unknown"],
        )
        self.assertEqual(
            identifiers,
            {"active-energy", "apple-exercise-time", "apple-move-time", "apple-stand-hour", "apple-stand-time", "atrial-fibrillation-burden", "audiogram-panel", "basal-body-temperature", "basal-energy", "basal-metabolic-rate", "bladder-incontinence", "bleeding-after-pregnancy", "bleeding-during-pregnancy", "blood-alcohol-content", "blood-glucose-unspecified-specimen", "blood-pressure", "biological-sex", "blood-type", "body-fat-mass", "body-fat-percentage", "body-height", "body-temperature", "body-water-mass", "body-weight", "bone-mass", "cervical-mucus-quality", "contraceptive-use", "date-of-birth", "corrected-qt-interval", "cycling-cadence", "cycling-functional-threshold-power", "deep-sleep-duration", "dietary-biotin", "dietary-caffeine", "dietary-calcium", "dietary-carbohydrates", "dietary-chloride", "dietary-cholesterol", "dietary-chromium", "dietary-copper", "dietary-energy", "dietary-energy-from-fat", "dietary-fat-monounsaturated", "dietary-fat-polyunsaturated", "dietary-fat-saturated", "dietary-fat-total", "dietary-fat-trans", "dietary-fat-unsaturated", "dietary-fiber", "dietary-folate", "dietary-folic-acid", "dietary-iodine", "dietary-iron", "dietary-magnesium", "dietary-manganese", "dietary-molybdenum", "dietary-niacin", "dietary-pantothenic-acid", "dietary-phosphorus", "dietary-potassium", "dietary-protein", "dietary-riboflavin", "dietary-selenium", "dietary-sodium", "dietary-sugar", "dietary-thiamin", "dietary-vitamin-a", "dietary-vitamin-b12", "dietary-vitamin-b6", "dietary-vitamin-c", "dietary-vitamin-d", "dietary-vitamin-e", "dietary-vitamin-k", "dietary-zinc", "distance", "electrodermal-activity", "elevation-gained", "environmental-audio-exposure", "environmental-audio-exposure-notification", "environmental-sound-reduction", "extracellular-water-mass", "flights-climbed", "fitzpatrick-skin-type", "fluid-intake", "food-correlation", "forced-expiratory-volume-1", "forced-vital-capacity", "gad7-assessment", "handwashing-session", "headphone-audio-exposure", "headphone-audio-exposure-notification", "heart-rate", "heart-rate-recovery-one-minute", "heart-rate-variability-rmssd", "heart-rate-variability-sdnn", "high-heart-rate-notification", "hypertension-notification", "infrequent-menstrual-cycles", "inhaler-usage", "insulin-delivery", "intermenstrual-bleeding", "intracellular-water-mass", "irregular-heart-rhythm-notification", "irregular-menstrual-cycles", "lactation-status", "lean-body-mass", "light-sleep-duration", "low-cardio-fitness-notification", "low-heart-rate-notification", "menstruation-flow", "menstruation-period", "mindfulness-session", "muscle-mass", "number-of-alcoholic-beverages", "number-of-times-fallen", "oura-cardiovascular-age", "oura-readiness-score", "ovulation-test-result", "oxygen-saturation", "oxygen-saturation-daily-average", "peak-expiratory-flow-rate", "peripheral-perfusion-index", "persistent-intermenstrual-bleeding", "phq9-assessment", "physical-effort", "power", "pr-interval", "pregnancy-status", "pregnancy-test-result", "progesterone-test-result", "prolonged-menstrual-periods", "qrs-duration", "qt-interval", "rem-sleep-duration", "respiratory-rate", "respiratory-rate-average", "resting-heart-rate", "resting-heart-rate-daily-average", "running-ground-contact-time", "running-stride-length", "running-vertical-oscillation", "sexual-activity", "six-minute-walk-test-distance", "skin-temperature", "sleep-apnea-notification", "sleep-awake-duration", "sleep-duration", "sleep-heart-rate", "sleep-stage", "sleeping-breathing-disturbances", "sleeping-heart-rate-average", "speed", "stair-ascent-speed", "stair-descent-speed", "state-of-mind", "step-cadence", "step-count", "swimming-stroke-count", "symptom-abdominal-cramps", "symptom-acne", "symptom-appetite-changes", "symptom-bloating", "symptom-breast-pain", "symptom-chest-tightness-or-pain", "symptom-chills", "symptom-constipation", "symptom-coughing", "symptom-diarrhea", "symptom-dizziness", "symptom-dry-skin", "symptom-fainting", "symptom-fatigue", "symptom-fever", "symptom-generalized-body-ache", "symptom-hair-loss", "symptom-headache", "symptom-heartburn", "symptom-hot-flashes", "symptom-loss-of-smell", "symptom-loss-of-taste", "symptom-lower-back-pain", "symptom-memory-lapse", "symptom-mood-changes", "symptom-nausea", "symptom-night-sweats", "symptom-pelvic-pain", "symptom-rapid-pounding-or-fluttering-heartbeat", "symptom-runny-nose", "symptom-shortness-of-breath", "symptom-sinus-congestion", "symptom-skipped-heartbeat", "symptom-sleep-changes", "symptom-sore-throat", "symptom-vomiting", "symptom-wheezing", "time-in-daylight", "toothbrushing-session", "total-energy", "underwater-depth", "uv-exposure", "vaginal-dryness", "vo2-max", "waist-circumference", "walking-asymmetry", "walking-double-support", "walking-heart-rate-average", "walking-speed", "walking-steadiness", "walking-steadiness-notification", "walking-step-length", "water-temperature", "wheelchair-push-count", "wheelchair-use", "withings-atrial-fibrillation-notification-ecg", "withings-atrial-fibrillation-notification-ppg", "withings-nerve-health-score", "withings-pulse-wave-velocity", "withings-vascular-age", "withings-visceral-fat-index", "workout", "workout-effort-score", "workout-segment"},
        )

    def test_resting_heart_rate_is_a_point_vital_sign_with_specific_and_r4_codes(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        measurement = next(
            item for item in catalog["measurements"]
            if item["id"] == "resting-heart-rate"
        )
        self.assertEqual(measurement["effective"], "dateTime")
        self.assertEqual(
            measurement["standardProfile"],
            "http://hl7.org/fhir/StructureDefinition/heartrate",
        )
        self.assertEqual(
            (measurement["code"]["system"], measurement["code"]["code"]),
            ("http://loinc.org", "40443-4"),
        )
        self.assertEqual(
            [
                (coding["system"], coding["code"])
                for coding in measurement["requiredCodings"]
            ],
            [("http://loinc.org", "8867-4")],
        )

    def test_every_imposed_r4_vital_sign_exposes_its_effective_category(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        vital_profiles = {
            "http://hl7.org/fhir/StructureDefinition/bp",
            "http://hl7.org/fhir/StructureDefinition/bodyheight",
            "http://hl7.org/fhir/StructureDefinition/bodytemp",
            "http://hl7.org/fhir/StructureDefinition/bodyweight",
            "http://hl7.org/fhir/StructureDefinition/heartrate",
            "http://hl7.org/fhir/StructureDefinition/oxygensat",
            "http://hl7.org/fhir/StructureDefinition/resprate",
        }
        expected = {
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "vital-signs",
            "display": "Vital Signs",
        }
        imposed_vitals = [
            measurement
            for measurement in catalog["measurements"]
            if measurement.get("standardProfile") in vital_profiles
        ]
        self.assertEqual(
            {measurement["standardProfile"] for measurement in imposed_vitals},
            vital_profiles,
        )
        for measurement in imposed_vitals:
            with self.subTest(measurement=measurement["id"]):
                self.assertEqual(measurement.get("category"), expected)

    def test_mapped_standard_coverage_is_backed_by_exact_raw_adapter_rows(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        sensorkit = json.loads(
            (ROOT / "catalog/sensorkit-adapter.json").read_text(encoding="utf-8")
        )
        connected = json.loads(
            (ROOT / "catalog/providers-adapter.json").read_text(
                encoding="utf-8"
            )
        )
        sensorkit_rows = {row["sourceToken"]: row for row in sensorkit["entries"]}
        provider_rows = {
            (provider["id"], row["token"]): row
            for provider in connected["providers"]
            for row in provider["sourceTypes"]
        }
        for measurement in catalog["measurements"]:
            for source, detail in measurement.get("coverageDetails", {}).items():
                for token in detail["sourceTokens"]:
                    if source == "sensorkit":
                        row = sensorkit_rows[token]
                        self.assertEqual(row["status"], "mapped-standard")
                        self.assertEqual(
                            row["raw"]["profile"], detail["alternateRepresentation"]
                        )
                        self.assertEqual(row["structured"]["status"], "deferred")
                    else:
                        row = provider_rows[(source, token)]
                        self.assertEqual(row["status"], "mapped-standard")
                        self.assertEqual(
                            row["raw"]["adapterProfile"],
                            detail["alternateRepresentation"],
                        )
                        self.assertFalse(
                            any(
                                measurement["id"] in element.get("measurementIds", [])
                                for element in row["elements"]
                            )
                        )

    def test_every_mobile_measurement_is_genuinely_shared(self) -> None:
        catalog = json.loads((ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8"))
        for measurement in catalog["measurements"]:
            if measurement.get("owner", "mobile") != "mobile":
                continue
            supported = [
                source for source, status in measurement["coverage"].items()
                if status == "supported"
            ]
            self.assertGreaterEqual(
                len(supported),
                2,
                f"{measurement['id']} is adapter-only and must not be a Mobile profile",
            )

    def test_full_url_vectors_use_the_normative_framed_identifier_pair(self) -> None:
        from Scripts import exchange_protocol

        contract = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            str(exchange_protocol.FULL_URL_NAMESPACE),
            contract["entryIdentity"]["fullUrl"]["namespace"],
        )
        for vector in contract["testVectors"]["fullUrls"]:
            with self.subTest(case=vector["id"]):
                self.assertEqual(
                    exchange_protocol.entry_full_url(vector["system"], vector["value"]),
                    vector["fullUrl"],
                )

    def test_recording_device_identity_is_per_unit_and_snapshot_identity_is_event_scoped(self) -> None:
        contract = json.loads(
            (ROOT / "catalog/exchange-protocol.json").read_text(encoding="utf-8")
        )
        kinds = {
            row["kind"]: row for row in contract["opaqueIdentity"]["identityKinds"]
        }
        self.assertEqual(
            kinds["recording-device"]["components"],
            ["adapter-id", "subject-system", "subject-value", "stable-unit-token"],
        )
        self.assertEqual(
            kinds["device-snapshot"]["components"],
            ["event-system", "event-value", "device-role", "source-device-token"],
        )
        recording = contract["recordingDevice"]
        self.assertIn("stable per-unit token", recording["instanceRule"])
        self.assertIn("omit", recording["unknownInstance"].lower())
        self.assertIn("application, host, or recording-device", recording["roles"])
        for forbidden in ("manufacturer", "model", "hardware version"):
            self.assertIn(forbidden, recording["instanceRule"].lower())

    def test_every_adapter_declares_its_recording_device_identity(self) -> None:
        adapters = {}
        for name in ("healthkit", "sensorkit", "health-connect", "providers"):
            catalog = json.loads(
                (ROOT / f"catalog/{name}-adapter.json").read_text(encoding="utf-8")
            )
            declaration = catalog.get("recordingDeviceIdentity")
            self.assertIsNotNone(declaration, f"{name} declares no recording-device identity")
            self.assertEqual(declaration["status"], "stable-token-required", name)
            self.assertIn("Omit", declaration["fallback"], name)
            self.assertIn("stable", json.dumps(declaration).lower(), name)
            self.assertIn("device-snapshot", declaration["snapshot"], name)
            adapters[name] = declaration["adapterId"]
        self.assertEqual(len(set(adapters.values())), len(adapters), "adapter ids must be distinct")

    def test_every_quantity_carries_an_example_value_within_its_unit(self) -> None:
        """Every generated profile ships an example, so every quantity needs a value to show.

        Plausibility is a review question, but a value outside the range its own unit declares is
        a defect any reader can see, so those are checked here.
        """
        catalog = json.loads((ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8"))
        for measurement in catalog["measurements"]:
            quantities = []
            if measurement.get("valueKind") == "quantity" and measurement["generation"]["emit"]:
                quantities.append((measurement["id"], measurement["quantity"]))
            for component in measurement.get("components", []):
                if component.get("quantity"):
                    quantities.append((f"{measurement['id']}/{component['id']}", component["quantity"]))
            for name, quantity in quantities:
                example = quantity.get("example")
                self.assertIsInstance(example, (int, float), f"{name} states no example value")
                self.assertGreater(example, 0, f"{name} has a placeholder example value")
                if quantity["code"] == "%":
                    self.assertLessEqual(example, 100, f"{name} exceeds a percentage")
                declared = re.search(r"(\d+)\s*-\s*(\d+)", quantity.get("unit", ""))
                if declared:
                    low, high = int(declared.group(1)), int(declared.group(2))
                    self.assertGreaterEqual(example, low, f"{name} is below its declared range")
                    self.assertLessEqual(example, high, f"{name} is above its declared range")

    def test_reviewed_quantity_value_domains_are_closed_and_self_consistent(self) -> None:
        catalog = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )
        integer_totals = {
            "flights-climbed",
            "inhaler-usage",
            "number-of-alcoholic-beverages",
            "number-of-times-fallen",
            "step-count",
            "swimming-stroke-count",
            "wheelchair-push-count",
        }
        actual_integer_totals: set[str] = set()
        for measurement in catalog["measurements"]:
            quantity = measurement.get("quantity")
            if not isinstance(quantity, dict):
                continue
            domain = quantity.get("valueDomain")
            if quantity["code"] == "%":
                self.assertEqual(
                    domain,
                    {
                        "minimum": {"value": 0, "inclusive": True},
                        "maximum": {"value": 100, "inclusive": True},
                        "integerOnly": False,
                    },
                    measurement["id"],
                )
            if measurement["id"] in integer_totals:
                self.assertEqual(
                    domain,
                    {
                        "minimum": {"value": 0, "inclusive": True},
                        "integerOnly": True,
                    },
                    measurement["id"],
                )
                actual_integer_totals.add(measurement["id"])
            if domain is None:
                continue
            minimum = domain.get("minimum")
            maximum = domain.get("maximum")
            if minimum and maximum:
                self.assertLessEqual(minimum["value"], maximum["value"], measurement["id"])
            value = quantity["example"]
            if minimum:
                assertion = self.assertGreaterEqual if minimum["inclusive"] else self.assertGreater
                assertion(value, minimum["value"], measurement["id"])
            if maximum:
                assertion = self.assertLessEqual if maximum["inclusive"] else self.assertLess
                assertion(value, maximum["value"], measurement["id"])
            if domain["integerOnly"]:
                self.assertEqual(value, int(value), measurement["id"])
        self.assertEqual(actual_integer_totals, integer_totals)
        state_of_mind = next(
            item for item in catalog["measurements"] if item["id"] == "state-of-mind"
        )
        self.assertEqual(
            state_of_mind["quantity"]["valueDomain"],
            {
                "minimum": {"value": -1, "inclusive": True},
                "maximum": {"value": 1, "inclusive": True},
                "integerOnly": False,
            },
        )


    def test_every_fhir_element_path_declares_the_version_it_belongs_to(self) -> None:
        """A version move has to be able to find every R4-shaped statement by name.

        The catalogs mix platform facts, which survive a FHIR major version, with the projection
        onto R4 elements, which does not. Naming the version-bound keys keeps the second set
        greppable instead of leaving a reader to recognise element paths by eye.
        """
        resources = (
            "Observation", "DocumentReference", "Provenance", "Device", "Bundle", "Patient",
            "ResearchStudy", "ResearchSubject", "Questionnaire", "QuestionnaireResponse", "Specimen",
        )
        step = r"(?:\.[A-Za-z0-9_'-]+|\[[^\]\s]*\]|\([^)\s]*\))"
        one = rf"(?:{'|'.join(resources)}){step}+"
        # A bare path only: prose that merely opens with an element name is documentation.
        bare_path = re.compile(rf"^{one}(?: -> {one})?$")

        def findings(node: object, trail: list[str]) -> list[str]:
            if isinstance(node, dict):
                for key in node:
                    self.assertNotEqual(
                        key,
                        "element",
                        f"rename to r4Element so a version move can find it: {'.'.join(trail + [key])}",
                    )
                return [f for key, value in node.items() for f in findings(value, trail + [key])]
            if isinstance(node, list):
                return [f for index, value in enumerate(node) for f in findings(value, trail + [str(index)])]
            if isinstance(node, str) and bare_path.match(node.strip()):
                # The key naming the version must be the value's own key, or the map it sits
                # directly in. Marking a container does not exempt an arbitrarily deep subtree.
                if not any(key.startswith("r4") for key in trail[-2:]):
                    return [".".join(trail) + f" = {node}"]
            return []

        for source in sorted((ROOT / "catalog").rglob("*.json")):
            self.assertEqual(
                findings(json.loads(source.read_text(encoding="utf-8")), []),
                [],
                f"{source.name} states an R4 element path under a key that does not name the version",
            )


    def test_uuid_algorithm_rejects_invalid_unicode(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "validate_producer_invalid_unicode", ROOT / "Scripts/validate-producer.py"
        )
        assert spec and spec.loader
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        with self.assertRaisesRegex(validator.ProducerValidationError, "invalid Unicode surrogate"):
            validator.canonical_identifier_name("https://example.org", "bad\ud800value")


if __name__ == "__main__":
    unittest.main()
