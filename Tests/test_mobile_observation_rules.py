"""Pin the base Mobile Observation rules and the negative corpus that proves them."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
CORPUS = ROOT / "Conformance/corpora/mobile-profile-invariants/corpus.json"
DATA_ABSENT_REASON = "http://hl7.org/fhir/ValueSet/data-absent-reason"
GROVE_CODE_SYSTEM = (
    "system.startsWith('https://grovealliance.org/fhir/') and system.contains('/CodeSystem/')"
)
INVARIANTS = {
    "grove-mobile-effective-1": (
        "(effective.ofType(dateTime) | effective.ofType(Period).start | "
        "effective.ofType(Period).end).all($this.toString().contains('T'))"
    ),
    "grove-mobile-code-system-1": (
        "code.coding.exists() and code.coding.all(system = 'http://loinc.org' or "
        f"system = 'urn:iso:std:iso:11073:10101' or ({GROVE_CODE_SYSTEM}))"
    ),
    "grove-mobile-body-site-1": (
        "bodySite.all(coding.exists() and coding.all(system = 'http://snomed.info/sct'))"
    ),
    "grove-mobile-method-1": (
        "method.all(coding.exists() and coding.all(system = 'http://snomed.info/sct' or "
        f"({GROVE_CODE_SYSTEM})))"
    ),
}

_spec = importlib.util.spec_from_file_location(
    "render_measurement_profiles", ROOT / "Scripts/render-measurement-profiles.py"
)
assert _spec is not None and _spec.loader is not None
RENDERER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RENDERER)


def fsh_block(text: str, header: str) -> str:
    """One FSH entity from its header line to the blank line that ends it."""
    start = text.index(f"\n{header}\n") + 1
    end = text.find("\n\n", start)
    return text[start:] if end == -1 else text[start:end]


class MobileObservationRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profiles = (ROOT / "mobile/input/fsh/profiles.fsh").read_text(encoding="utf-8")
        cls.generated = (
            ROOT / "mobile/input/fsh/generated-measurement-profiles.fsh"
        ).read_text(encoding="utf-8")
        cls.rules = fsh_block(cls.profiles, "RuleSet: GroveMobileObservationRules")
        cls.measurements = json.loads(
            (ROOT / "catalog/measurement-catalog.json").read_text(encoding="utf-8")
        )["measurements"]

    def test_observation_rules_obey_every_base_invariant_once(self) -> None:
        obeys = next(line for line in self.rules.splitlines() if line.startswith("* obeys "))
        names = obeys[len("* obeys "):].split(" and ")
        self.assertEqual(len(names), len(set(names)))
        for key in INVARIANTS:
            self.assertIn(key, names)

    def test_every_base_invariant_is_an_error_with_its_exact_expression(self) -> None:
        for key, expression in INVARIANTS.items():
            with self.subTest(invariant=key):
                lines = fsh_block(self.profiles, f"Invariant: {key}").splitlines()
                self.assertEqual(len(lines), 4)
                self.assertTrue(lines[1].startswith('Description: "'))
                self.assertEqual(lines[2], f'Expression: "{expression}"')
                self.assertEqual(lines[3], "Severity: #error")

    def test_data_absent_reason_bindings_are_required(self) -> None:
        for element in ("dataAbsentReason", "component.dataAbsentReason"):
            with self.subTest(element=element):
                self.assertIn(f"* {element} from {DATA_ABSENT_REASON} (required)", self.rules)

    def test_measurement_code_allow_list_is_exactly_the_mobile_catalog(self) -> None:
        owner = RENDERER.OWNERS["mobile"]
        listed = [
            line[2:]
            for line in fsh_block(self.generated, "ValueSet: GroveMobileMeasurementCodeVS").splitlines()
            if line.startswith("* ") and not line.startswith("* ^")
        ]
        expected = []
        for measurement in self.measurements:
            if measurement.get("owner", "mobile") != "mobile":
                continue
            code = measurement["code"]
            if code["system"] == RENDERER.LOINC:
                expected.append(f"$loinc#{code['code']}")
            else:
                self.assertTrue(code["system"].endswith(owner["measurementSystemTail"]))
                expected.append(f"{owner['codeSystem']}#{code['code']}")
        self.assertEqual(listed, expected)
        self.assertEqual(len(listed), len(set(listed)))

    def test_allow_list_refuses_a_code_system_mobile_does_not_own(self) -> None:
        foreign = {
            "id": "heart-rate",
            "code": {
                "system": "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement",
                "code": "heart-rate",
            },
        }
        with self.assertRaisesRegex(SystemExit, "heart-rate: unsupported code system"):
            RENDERER.render_mobile_code_allowlist([foreign])


class MobileProfileInvariantCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        cls.control = json.loads((CORPUS.parent / cls.corpus["control"]).read_text(encoding="utf-8"))

    def test_every_base_invariant_and_the_binding_have_a_negative_case(self) -> None:
        cases = self.corpus["cases"]
        self.assertEqual(
            {case["expectedInvariant"] for case in cases if "expectedInvariant" in case},
            set(INVARIANTS),
        )
        self.assertEqual(
            {case["expectedBinding"] for case in cases if "expectedBinding" in case},
            {DATA_ABSENT_REASON},
        )

    def test_every_case_is_a_mutation_of_the_control(self) -> None:
        profile = self.corpus["profile"]
        self.assertEqual(self.control["meta"]["profile"], [profile])
        for case in self.corpus["cases"]:
            with self.subTest(case=case["path"]):
                resource = json.loads((CORPUS.parent / case["path"]).read_text(encoding="utf-8"))
                self.assertEqual(resource["id"], Path(case["path"]).stem)
                self.assertEqual(resource["meta"]["profile"], [profile])
                self.assertEqual(resource["identifier"], self.control["identifier"])
                self.assertNotEqual(
                    {key: value for key, value in resource.items() if key != "id"},
                    {key: value for key, value in self.control.items() if key != "id"},
                )


if __name__ == "__main__":
    unittest.main()
