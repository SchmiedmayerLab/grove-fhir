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
        self.assertEqual(catalog["version"], "0.3.0")
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
            {"active-energy", "apple-exercise-time", "apple-move-time", "apple-stand-hour", "apple-stand-time", "atrial-fibrillation-burden", "basal-body-temperature", "basal-energy", "basal-metabolic-rate", "bladder-incontinence", "bleeding-after-pregnancy", "bleeding-during-pregnancy", "blood-alcohol-content", "blood-glucose-unspecified-specimen", "blood-pressure", "blood-type", "body-fat-mass", "body-fat-percentage", "body-height", "body-temperature", "body-water-mass", "body-weight", "bone-mass", "cervical-mucus-quality", "contraceptive-use", "cycling-cadence", "cycling-functional-threshold-power", "deep-sleep-duration", "dietary-biotin", "dietary-caffeine", "dietary-calcium", "dietary-carbohydrates", "dietary-chloride", "dietary-cholesterol", "dietary-chromium", "dietary-copper", "dietary-energy", "dietary-energy-from-fat", "dietary-fat-monounsaturated", "dietary-fat-polyunsaturated", "dietary-fat-saturated", "dietary-fat-total", "dietary-fat-trans", "dietary-fat-unsaturated", "dietary-fiber", "dietary-folate", "dietary-folic-acid", "dietary-iodine", "dietary-iron", "dietary-magnesium", "dietary-manganese", "dietary-molybdenum", "dietary-niacin", "dietary-pantothenic-acid", "dietary-phosphorus", "dietary-potassium", "dietary-protein", "dietary-riboflavin", "dietary-selenium", "dietary-sodium", "dietary-sugar", "dietary-thiamin", "dietary-vitamin-a", "dietary-vitamin-b12", "dietary-vitamin-b6", "dietary-vitamin-c", "dietary-vitamin-d", "dietary-vitamin-e", "dietary-vitamin-k", "dietary-zinc", "distance", "electrodermal-activity", "elevation-gained", "environmental-audio-exposure", "environmental-sound-reduction", "extracellular-water-mass", "flights-climbed", "fluid-intake", "forced-expiratory-volume-1", "forced-vital-capacity", "gad7-assessment", "handwashing-session", "headphone-audio-exposure", "heart-rate", "heart-rate-recovery-one-minute", "heart-rate-variability-rmssd", "heart-rate-variability-sdnn", "inhaler-usage", "insulin-delivery", "intermenstrual-bleeding", "intracellular-water-mass", "lactation-status", "lean-body-mass", "light-sleep-duration", "menstruation-flow", "menstruation-period", "mindfulness-session", "muscle-mass", "number-of-alcoholic-beverages", "number-of-times-fallen", "ovulation-test-result", "oxygen-saturation", "oxygen-saturation-daily-average", "peak-expiratory-flow-rate", "peripheral-perfusion-index", "phq9-assessment", "physical-effort", "power", "pregnancy-status", "pregnancy-test-result", "progesterone-test-result", "rem-sleep-duration", "respiratory-rate", "respiratory-rate-average", "resting-heart-rate", "running-ground-contact-time", "running-stride-length", "running-vertical-oscillation", "sexual-activity", "six-minute-walk-test-distance", "skin-temperature", "sleep-awake-duration", "sleep-duration", "sleep-heart-rate", "sleep-stage", "sleeping-breathing-disturbances", "sleeping-heart-rate-average", "speed", "stair-ascent-speed", "stair-descent-speed", "step-cadence", "step-count", "swimming-stroke-count", "symptom-abdominal-cramps", "symptom-acne", "symptom-appetite-changes", "symptom-bloating", "symptom-breast-pain", "symptom-chest-tightness-or-pain", "symptom-chills", "symptom-constipation", "symptom-coughing", "symptom-diarrhea", "symptom-dizziness", "symptom-dry-skin", "symptom-fainting", "symptom-fatigue", "symptom-fever", "symptom-generalized-body-ache", "symptom-hair-loss", "symptom-headache", "symptom-heartburn", "symptom-hot-flashes", "symptom-loss-of-smell", "symptom-loss-of-taste", "symptom-lower-back-pain", "symptom-memory-lapse", "symptom-mood-changes", "symptom-nausea", "symptom-night-sweats", "symptom-pelvic-pain", "symptom-rapid-pounding-or-fluttering-heartbeat", "symptom-runny-nose", "symptom-shortness-of-breath", "symptom-sinus-congestion", "symptom-skipped-heartbeat", "symptom-sleep-changes", "symptom-sore-throat", "symptom-vomiting", "symptom-wheezing", "time-in-daylight", "toothbrushing-session", "total-energy", "underwater-depth", "uv-exposure", "vaginal-dryness", "vo2-max", "waist-circumference", "walking-asymmetry", "walking-double-support", "walking-heart-rate-average", "walking-speed", "walking-steadiness", "walking-step-length", "water-temperature", "wheelchair-push-count", "wheelchair-use", "workout", "workout-effort-score", "workout-segment"},





        )

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

    def test_uuid_vector_uses_the_normative_entry_identity_algorithm(self) -> None:
        import importlib.util
        import uuid

        spec = importlib.util.spec_from_file_location(
            "validate_producer", ROOT / "Scripts/validate-producer.py"
        )
        assert spec and spec.loader
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        contract = json.loads((ROOT / "catalog/exchange-identity.json").read_text(encoding="utf-8"))
        for vector in contract["vectors"]:
            if vector["input"] is None:
                self.assertIn("|", vector["system"])
                continue
            with self.subTest(case=vector["case"]):
                value = validator.canonical_identifier_name(vector["system"], vector["value"])
                self.assertEqual(value, vector["input"])
                generated = uuid.uuid5(uuid.UUID(contract["fullUrlAlgorithm"]["namespace"]), value)
                self.assertEqual(f"urn:uuid:{generated}", vector["fullUrl"])

    def test_recording_device_identity_vectors_are_exact(self) -> None:
        contract = json.loads((ROOT / "catalog/exchange-identity.json").read_text(encoding="utf-8"))
        device = contract["recordingDeviceIdentity"]

        self.assertEqual(
            device["composition"],
            ["subjectReference", "adapterId", "manufacturer", "model", "hardwareVersion"],
        )
        self.assertNotIn("digest", device)

        self.assertTrue(device["vectors"])
        for vector in device["vectors"]:
            with self.subTest(case=vector["case"]):
                self.assertEqual(len(vector["components"]), len(device["composition"]))
                self.assertEqual("v1:" + "|".join(vector["components"]), vector["value"])

        # Two participants wearing the same model are two devices; that is the whole point of
        # keying on the subject rather than the product configuration alone.
        by_case = {vector["case"]: vector["value"] for vector in device["vectors"]}
        self.assertNotEqual(by_case["apple-watch"], by_case["different-participant-same-model"])

    def test_every_adapter_declares_its_recording_device_identity(self) -> None:
        contract = json.loads((ROOT / "catalog/exchange-identity.json").read_text(encoding="utf-8"))
        keyed = {
            field
            for field in contract["recordingDeviceIdentity"]["composition"]
            if field in {"manufacturer", "model", "hardwareVersion"}
        }
        adapters = {}
        for name in ("healthkit", "sensorkit", "health-connect", "providers"):
            catalog = json.loads(
                (ROOT / f"catalog/{name}-adapter.json").read_text(encoding="utf-8")
            )
            declaration = catalog.get("recordingDeviceIdentity")
            self.assertIsNotNone(declaration, f"{name} declares no recording-device identity")
            self.assertIn(declaration["status"], {"derived", "unavailable"}, name)
            # A deriving adapter maps every keyed field, so a source that silently stops
            # supplying one cannot quietly change the identity it mints.
            if declaration["status"] == "derived":
                self.assertEqual(set(declaration["sourceFields"]), keyed, name)
            else:
                self.assertFalse(declaration["sourceFields"], name)
                self.assertTrue(declaration.get("note"), f"{name} must say why it cannot derive one")
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
