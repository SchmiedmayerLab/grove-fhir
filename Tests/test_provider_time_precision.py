"""Source precision remains exact while native adapter canonicalization is unchanged."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

import copy
import json
import unittest
from pathlib import Path

from Scripts.producer_validation.diagnostics import ProducerValidationError
from Scripts.producer_validation.mobile_semantics import mobile_semantic_projection


class ProviderTimePrecisionTests(unittest.TestCase):
    @staticmethod
    def fixture(adapter="oura", period=False):
        profile = "https://grovealliance.org/fhir/mobile/StructureDefinition/" + (
            "grove-mobile-step-count" if period else "grove-mobile-heart-rate"
        )
        code = {"system": "http://loinc.org", "code": "55423-8" if period else "8867-4"}
        unit = "{steps}" if period else "/min"
        value = {"type": "Quantity", "value": 72, "system": "http://unitsofmeasure.org", "code": unit, "unit": unit}
        effective = ({"type": "Period", "start": "2026-11-01T01:59:59.999999999-07:00", "end": "2026-11-01T01:00:00.000000001-08:00"}
                     if period else {"type": "dateTime", "value": "2026-11-01T00:00:00.123456789Z"})
        vector = {"id": "time-regression", "profile": profile, "code": code, "effective": effective, "result": value}
        resource = {
            "resourceType": "Observation", "meta": {"profile": [profile, f"https://grovealliance.org/fhir/{adapter}/StructureDefinition/{adapter}-observation"]},
            "code": {"coding": [code]}, "valueQuantity": {key: item for key, item in value.items() if key != "type"},
        }
        if period:
            resource["effectivePeriod"] = {key: effective[key] for key in ("start", "end")}
        else:
            resource["effectiveDateTime"] = effective["value"]
        return resource, vector

    def test_all_provider_adapters_preserve_source_fraction(self):
        for adapter in ("oura", "google-health", "withings"):
            with self.subTest(adapter=adapter):
                resource, vector = self.fixture(adapter)
                mobile_semantic_projection(resource, vector, "exact provider time")
                resource["effectiveDateTime"] = "2026-11-01T00:00:00.123Z"
                with self.assertRaisesRegex(ProducerValidationError, "does not equal"):
                    mobile_semantic_projection(resource, vector, "rounded provider time")

    def test_exact_period_accepts_distinct_source_offsets_and_rejects_nanosecond_change(self):
        resource, vector = self.fixture(period=True)
        mobile_semantic_projection(resource, vector, "exact interval")
        changed = copy.deepcopy(resource)
        changed["effectivePeriod"]["end"] = "2026-11-01T01:00:00.000000002-08:00"
        with self.assertRaisesRegex(ProducerValidationError, "does not equal"):
            mobile_semantic_projection(changed, vector, "changed endpoint")
        for endpoint, rounded in (("start", "2026-11-01T02:00:00.000-07:00"), ("end", "2026-11-01T01:00:00.000-08:00")):
            with self.subTest(endpoint=endpoint):
                rounded_period = copy.deepcopy(resource)
                rounded_period["effectivePeriod"][endpoint] = rounded
                with self.assertRaisesRegex(ProducerValidationError, "does not equal"):
                    mobile_semantic_projection(rounded_period, vector, "rounded provider endpoint")

    def test_native_adapters_still_require_millisecond_canonicalization(self):
        for adapter in ("healthkit", "health-connect"):
            with self.subTest(adapter=adapter):
                resource, vector = self.fixture(adapter)
                with self.assertRaisesRegex(ProducerValidationError, "not millisecond-canonical"):
                    mobile_semantic_projection(resource, vector, "native time")
                resource["effectiveDateTime"] = "2026-11-01T00:00:00.123Z"
                mobile_semantic_projection(resource, vector, "canonical native time")

    def test_insignificant_zero_fraction_does_not_change_source_instant(self):
        resource, vector = self.fixture()
        resource["effectiveDateTime"] = "2026-11-01T00:00:00.123456789000Z"
        mobile_semantic_projection(resource, vector, "same source instant")

    def test_oura_daily_activity_uses_the_source_activity_day(self):
        catalog = json.loads((Path(__file__).resolve().parents[1] / "catalog" / "providers-adapter.json").read_text(encoding="utf-8"))
        oura = next(provider for provider in catalog["providers"] if provider["measurementOwner"] == "oura")
        daily = next(source for source in oura["sourceTypes"] if source["token"] == "daily_activity")
        for element in daily["elements"]:
            with self.subTest(path=element["path"]):
                self.assertIn("from 04:00 on its named date to 04:00 on the following date", element["effective"])
                self.assertIn("midnight substitution is forbidden", element["effective"])
                self.assertNotIn("civil day", element["effective"])


if __name__ == "__main__":
    unittest.main()
