"""Admission and rejection cases for the HealthKit source document time extension."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import copy
import json
from pathlib import Path
import unittest

from Scripts.producer_validation.diagnostics import ProducerValidationError
from Scripts.producer_validation.healthkit import validate_healthkit_source_document_time


ROOT = Path(__file__).parents[1]
CATALOG = json.loads((ROOT / "catalog/healthkit-adapter.json").read_text(encoding="utf-8"))
CONTRACT = CATALOG["sourceDocumentTimeExtension"]


def provenance(basis="clinical-record-download", start="2026-08-18T09:41:07.000-07:00", end="2026-08-18T09:41:07.000-07:00"):
    return {
        "resourceType": "Provenance",
        "meta": {"profile": [CATALOG["conversionProvenanceProfile"]]},
        "entity": [{
            "role": "source",
            "extension": [{"url": CONTRACT["url"], "extension": [
                {"url": "basis", "valueCode": basis},
                {"url": "period", "valuePeriod": {"start": start, "end": end}},
            ]}],
        }],
    }


def zoned(start_zone="America/Los_Angeles", end_zone="America/Los_Angeles"):
    resource = provenance()
    period = resource["entity"][0]["extension"][0]["extension"][1]["valuePeriod"]
    for endpoint, zone in (("start", start_zone), ("end", end_zone)):
        if zone is not None:
            period[f"_{endpoint}"] = {"extension": [{"url": "http://hl7.org/fhir/StructureDefinition/timezone", "valueCode": zone}]}
    return resource


class HealthKitSourceDocumentTimeTests(unittest.TestCase):
    def test_contract_profile_and_page_agree(self):
        self.assertEqual(CONTRACT["r4Context"], "Provenance.entity")
        self.assertEqual(CONTRACT["cardinality"], "0..1")
        self.assertEqual(
            {item["code"]: item["sourceClass"] for item in CONTRACT["bases"]},
            {"clinical-record-download": "HKClinicalRecord", "cda-document-app-supplied": "HKCDADocumentSample"},
        )
        definition = (ROOT / "healthkit/input/fsh/source-document-time.fsh").read_text(encoding="utf-8")
        self.assertIn("Id: healthkit-source-document-time\n", definition)
        self.assertIn("Context: Provenance.entity\n", definition)
        for item in CONTRACT["bases"]:
            self.assertIn(f"* #{item['code']} ", definition)
        profiles = (ROOT / "healthkit/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        self.assertIn(
            "* entity.extension contains HealthKitSourceDocumentTime named sourceDocumentTime 0..1 MS", profiles
        )
        mapping = (ROOT / "healthkit/input/pagecontent/mapping.md").read_text(encoding="utf-8")
        section = mapping.split("### Clinical FHIR records\n", 1)[1].split("\n### ", 1)[0]
        for item in CONTRACT["bases"]:
            self.assertIn(f"| `{item['sourceClass']}` | `{item['code']}` |", section)
        self.assertIn("Never copy these dates into `DocumentReference.context.period`", section)

    def test_both_bases_and_equal_or_ordered_bounds_are_admitted(self):
        validate_healthkit_source_document_time(provenance(), "download")
        validate_healthkit_source_document_time(
            provenance("cda-document-app-supplied", "2026-08-01T00:00:00Z", "2026-08-02T12:30:00.500+02:00"),
            "document",
        )
        validate_healthkit_source_document_time(zoned(), "zoned")
        validate_healthkit_source_document_time({"resourceType": "Provenance", "entity": [{"role": "source"}]}, "absent")

    def test_time_zone_is_on_both_endpoints_or_neither(self):
        validate_healthkit_source_document_time(zoned(), "both")
        validate_healthkit_source_document_time(zoned(None, None), "neither")
        other_extension = zoned()
        other_extension["entity"][0]["extension"][0]["extension"][1]["valuePeriod"]["_end"]["extension"][0]["url"] = "https://example.org/zone"
        cases = {
            "start only": zoned("America/Los_Angeles", None),
            "end only": zoned(None, "America/Los_Angeles"),
            "different zones": zoned("America/Los_Angeles", "Europe/Berlin"),
            "other extension": other_extension,
        }
        for name, resource in cases.items():
            with self.subTest(case=name), self.assertRaisesRegex(ProducerValidationError, "endpoint|timezone"):
                validate_healthkit_source_document_time(resource, name)

    def test_incomplete_reversed_or_unknown_values_are_rejected(self):
        cases = [
            provenance(basis="download"),
            provenance(start="2026-08-18", end="2026-08-18"),
            provenance(start="2026-08-18T09:41:07", end="2026-08-18T09:41:08"),
            provenance(start="2026-08-18T09:41:08Z", end="2026-08-18T09:41:07Z"),
        ]
        missing_end = provenance()
        del missing_end["entity"][0]["extension"][0]["extension"][1]["valuePeriod"]["end"]
        reordered = provenance()
        reordered["entity"][0]["extension"][0]["extension"].reverse()
        extra = provenance()
        extra["entity"][0]["extension"][0]["extension"].append({"url": "note", "valueString": "x"})
        repeated = provenance()
        repeated["entity"][0]["extension"] *= 2
        for index, resource in enumerate([*cases, missing_end, reordered, extra, repeated]):
            with self.subTest(case=index), self.assertRaises(ProducerValidationError):
                validate_healthkit_source_document_time(resource, "source")

    def test_only_a_healthkit_conversion_source_entity_carries_it(self):
        extension = provenance()["entity"][0]["extension"][0]
        derivation = provenance()
        derivation["entity"][0]["role"] = "derivation"
        other_profile = provenance()
        other_profile["meta"]["profile"] = ["https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-conversion-provenance"]
        on_root = provenance()
        on_root["extension"] = [copy.deepcopy(extension)]
        document = {
            "resourceType": "DocumentReference",
            "meta": {"profile": ["https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-clinical-record-document"]},
            "extension": [copy.deepcopy(extension)],
        }
        for index, resource in enumerate([derivation, other_profile, on_root, document]):
            with self.subTest(case=index), self.assertRaisesRegex(ProducerValidationError, "source entity"):
                validate_healthkit_source_document_time(resource, "misplaced")


if __name__ == "__main__":
    unittest.main()
