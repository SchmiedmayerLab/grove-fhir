"""Verify the Questionnaire package, fixture corpora, and paired validator."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "questionnaire/output"
GENERATED = ROOT / "questionnaire/fsh-generated/resources"
VALIDATOR_FIXTURES = ROOT / "questionnaire/fixtures/validator"
PAIR_FIXTURES = ROOT / "questionnaire/fixtures/pairs"
QUESTIONNAIRE_CANONICAL = (
    "https://grovealliance.org/fhir/questionnaire/"
    "Questionnaire/GroveWeeklySymptomCheckInExample"
)

sys.path.insert(0, str(ROOT / "Scripts"))
from questionnaire_fixture_corpus import apply_mutation, load_json, write_json  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "validate_questionnaire", ROOT / "Scripts/validate-questionnaire.py"
)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load Questionnaire validator")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)

fhir_spec = importlib.util.spec_from_file_location(
    "validate_questionnaire_fhir", ROOT / "Scripts/validate-questionnaire-fhir.py"
)
if fhir_spec is None or fhir_spec.loader is None:
    raise RuntimeError("Cannot load Questionnaire FHIR validator")
fhir_validator = importlib.util.module_from_spec(fhir_spec)
sys.modules[fhir_spec.name] = fhir_validator
fhir_spec.loader.exec_module(fhir_validator)


def load_generated(filename: str) -> dict:
    path = GENERATED / filename
    if not path.is_file():
        raise unittest.SkipTest("Questionnaire SUSHI output is not present")
    return json.loads(path.read_text(encoding="utf-8"))


class QuestionnaireContractTests(unittest.TestCase):
    def test_fixture_writer_preserves_exact_decimal_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            destination = Path(temporary) / "destination.json"
            source.write_text('{"valueDecimal":1.20}\n', encoding="utf-8")

            write_json(destination, load_json(source))

            self.assertEqual(destination.read_bytes(), b'{"valueDecimal":1.20}\n')

    def test_official_corpus_paths_cannot_escape_or_traverse_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            corpus = root / "corpus"
            corpus.mkdir()
            valid = corpus / "valid.json"
            valid.write_text("{}\n", encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            (corpus / "linked.json").symlink_to(outside)

            self.assertEqual(
                fhir_validator.resolve_corpus_file(
                    corpus, "valid.json", "Questionnaire fixture"
                ),
                valid,
            )
            with self.assertRaisesRegex(ValueError, "safe relative POSIX path"):
                fhir_validator.resolve_corpus_file(
                    corpus, "../outside.json", "Questionnaire fixture"
                )
            with self.assertRaisesRegex(ValueError, "may not traverse a symlink"):
                fhir_validator.resolve_corpus_file(
                    corpus, "linked.json", "Questionnaire fixture"
                )

    def test_profiles_derive_from_sdc_and_publish_named_rules(self) -> None:
        questionnaire = load_generated("StructureDefinition-grove-questionnaire.json")
        response = load_generated("StructureDefinition-grove-questionnaire-response.json")

        self.assertEqual(
            questionnaire["baseDefinition"],
            "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire",
        )
        self.assertEqual(
            response["baseDefinition"],
            "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaireresponse",
        )
        questionnaire_rules = {
            constraint["key"]
            for element in questionnaire["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertEqual(
            questionnaire_rules,
            {
                "qg-version-1",
                "qg-version-algorithm-1",
                "qg-item-text-1",
                "qg-reference-1",
                "qg-repeats-1",
                "qg-enable-1",
                "qg-expression-1",
                "qg-variable-name-1",
                "qg-initial-1",
                "qg-length-1",
                "qg-decimal-1",
                "qg-value-bounds-1",
                "qg-quantity-1",
                "qg-unit-1",
                "qg-attachment-1",
                "qg-occurrence-1",
                "qg-min-max-1",
                "qg-style-sensitive-1",
            },
        )
        response_rules = {
            constraint["key"]
            for element in response["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertEqual(
            response_rules,
            {
                "gqr-canonical-1",
                "gqr-identifier-1",
                "gqr-text-1",
                "gqr-completion-mode-1",
            },
        )
        response_constraints = {
            constraint["key"]: constraint["expression"]
            for element in response["differential"]["element"]
            for constraint in element.get("constraint", [])
        }
        self.assertIn(
            "^[^|#]+[|][^|#]+$",
            response_constraints["gqr-canonical-1"],
        )

    def test_profile_exposes_root_target_constraints_and_sdc_hidden_behavior(self) -> None:
        questionnaire = load_generated("StructureDefinition-grove-questionnaire.json")
        elements = {
            element["id"]: element
            for element in questionnaire["differential"]["element"]
        }
        self.assertIn("Questionnaire.extension:targetConstraint", elements)
        self.assertIn("Questionnaire.item.extension:targetConstraint", elements)
        self.assertEqual(
            elements["Questionnaire.extension:variable.value[x].name"]["min"],
            1,
        )
        self.assertEqual(
            elements["Questionnaire.item.extension:variable.value[x].name"]["min"],
            1,
        )

        published_path = OUTPUT / "StructureDefinition-grove-questionnaire.json"
        if published_path.is_file():
            published = json.loads(published_path.read_text(encoding="utf-8"))
            hidden = next(
                element
                for element in published["snapshot"]["element"]
                if element["id"] == "Questionnaire.item.extension:hidden"
            )
            self.assertTrue(hidden["mustSupport"])

        all_text = json.dumps(questionnaire["differential"], sort_keys=True)
        self.assertIn("rendering-styleSensitive", all_text)

    def test_completion_mode_fixes_system_and_code_but_not_display(self) -> None:
        response = load_generated("StructureDefinition-grove-questionnaire-response.json")
        elements = {
            element["id"]: element
            for element in response["differential"]["element"]
        }
        coding = elements[
            "QuestionnaireResponse.extension:completionMode.value[x].coding"
        ]
        self.assertEqual((coding["min"], coding["max"]), (1, "1"))
        self.assertEqual(
            elements[
                "QuestionnaireResponse.extension:completionMode.value[x].coding.system"
            ]["fixedUri"],
            "http://terminology.hl7.org/CodeSystem/v3-ParticipationMode",
        )
        self.assertEqual(
            elements[
                "QuestionnaireResponse.extension:completionMode.value[x].coding.code"
            ]["fixedCode"],
            "ELECTRONIC",
        )
        self.assertFalse(
            any("coding.display" in element["id"] for element in elements.values())
        )

    def test_introductory_pair_uses_exact_identity_and_answer_nesting(self) -> None:
        questionnaire = load_generated(
            "Questionnaire-GroveWeeklySymptomCheckInExample.json"
        )
        response = load_generated(
            "QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json"
        )

        self.assertEqual(questionnaire["url"], QUESTIONNAIRE_CANONICAL)
        self.assertEqual(questionnaire["version"], "1.0.0")
        self.assertEqual(response["questionnaire"], f"{QUESTIONNAIRE_CANONICAL}|1.0.0")
        severity = response["item"][0]["item"][0]["answer"][0]["item"][0]
        self.assertEqual(severity["linkId"], "pain-severity")
        self.assertEqual(
            severity["answer"][0]["valueCoding"],
            {
                "system": "http://snomed.info/sct",
                "code": "6736007",
                "display": "Moderate severity",
            },
        )
        self.assertEqual(validator.validate_pair(questionnaire, response), [])

    def test_static_validator_corpus_has_one_mutation_and_expected_rule(self) -> None:
        manifest = load_json(VALIDATOR_FIXTURES / "cases.json")
        official_case_ids = {
            case["id"]
            for case in manifest["invalid"]
            if case.get("fhirValidator") is not False
        }
        self.assertEqual(
            set(fhir_validator.load_expectations(official_case_ids)),
            official_case_ids,
        )
        for relative in manifest["valid"]:
            resource = load_json(VALIDATOR_FIXTURES / relative)
            issues = (
                validator.validate_questionnaire(resource)
                if resource["resourceType"] == "Questionnaire"
                else validator.validate_response(resource)
            )
            self.assertEqual(issues, [], relative)

        identifiers: set[str] = set()
        for case in manifest["invalid"]:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], identifiers)
                identifiers.add(case["id"])
                self.assertEqual(set(case["mutation"]), set(case["mutation"]) & {"op", "path", "from", "value"})
                base = load_json(VALIDATOR_FIXTURES / case["base"])
                invalid = apply_mutation(base, case["mutation"])
                issues = (
                    validator.validate_questionnaire(invalid)
                    if invalid["resourceType"] == "Questionnaire"
                    else validator.validate_response(invalid)
                )
                self.assertEqual(
                    [(issue.rule, issue.severity) for issue in issues],
                    [(case["expectedRule"], "error")],
                )

    def test_official_validator_expectations_reject_extra_or_overlapping_errors(self) -> None:
        def issue(message_id: str) -> dict:
            return {
                "severity": "error",
                "code": "invariant",
                "expression": ["Questionnaire"],
                "details": {"text": f"Constraint failed: {message_id}"},
                "extension": [
                    {
                        "url": fhir_validator.MESSAGE_ID_URL,
                        "valueString": message_id,
                    }
                ],
            }

        expected = [
            {
                "messageId": "intended-rule",
                "code": "invariant",
                "expression": "Questionnaire",
            }
        ]
        self.assertIsNone(
            fhir_validator.exact_error_failure([issue("intended-rule")], expected)
        )
        self.assertIsNotNone(
            fhir_validator.exact_error_failure(
                [issue("intended-rule"), issue("unrelated-rule")], expected
            )
        )
        self.assertIsNotNone(
            fhir_validator.exact_error_failure(
                [issue("intended-rule")], expected + [{"code": "invariant"}]
            )
        )

    def test_pair_corpus_covers_each_cross_resource_rule(self) -> None:
        manifest = load_json(PAIR_FIXTURES / "cases.json")
        questionnaire = load_json(PAIR_FIXTURES / manifest["questionnaire"])
        response = load_json(PAIR_FIXTURES / manifest["response"])
        in_progress = load_json(PAIR_FIXTURES / manifest["additionalValidResponses"][0])
        value_sets = [load_json(PAIR_FIXTURES / path) for path in manifest["valueSets"]]
        self.assertEqual(validator.validate_pair(questionnaire, response, value_sets), [])
        self.assertEqual(validator.validate_pair(questionnaire, in_progress, value_sets), [])

        expected_rules: set[str] = set()
        for case in manifest["invalid"]:
            with self.subTest(case=case["id"]):
                target = in_progress if case["target"] == "inProgressResponse" else response
                invalid = apply_mutation(target, case["mutation"])
                issues = validator.validate_pair(questionnaire, invalid, value_sets)
                self.assertEqual(
                    [(issue.rule, issue.severity) for issue in issues],
                    [(case["expectedRule"], "error")],
                )
                expected_rules.add(case["expectedRule"])
        self.assertEqual(
            expected_rules,
            {
                "pair-questionnaire-canonical",
                "pair-item-nesting",
                "pair-answer-type",
                "pair-inline-option",
                "pair-valueset-membership",
                "pair-response-text",
                "pair-repeats",
                "pair-answer-occurrence",
                "pair-required-item",
                "pair-item-unknown",
                "pair-item-duplicate",
                "pair-item-misplaced",
                "pair-item-disabled",
                "pair-response-entered-in-error",
            },
        )

    def test_cli_emits_stable_machine_readable_report(self) -> None:
        command = [
            sys.executable,
            str(ROOT / "Scripts/validate-questionnaire.py"),
            "--questionnaire",
            str(PAIR_FIXTURES / "valid/questionnaire.json"),
            "--response",
            str(PAIR_FIXTURES / "valid/response.json"),
            "--value-set",
            str(PAIR_FIXTURES / "valid/value-set.json"),
            "--json",
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout), {"issues": [], "valid": True})

    def test_enable_when_not_equal_uses_any_answer_semantics(self) -> None:
        condition = {
            "enableWhen": [
                {
                    "question": "choice",
                    "operator": "!=",
                    "answerCoding": {
                        "system": "https://example.org/codes",
                        "code": "a",
                    },
                }
            ]
        }
        expected = {"system": "https://example.org/codes", "code": "a"}
        other = {"system": "https://example.org/codes", "code": "b"}

        self.assertFalse(validator.evaluate_enable_when(condition, {}))
        self.assertFalse(
            validator.evaluate_enable_when(condition, {"choice": [expected]})
        )
        self.assertTrue(
            validator.evaluate_enable_when(condition, {"choice": [expected, other]})
        )

    def test_target_constraint_evaluation_is_status_and_severity_aware(self) -> None:
        questionnaire = load_json(PAIR_FIXTURES / "valid/questionnaire.json")
        completed = load_json(PAIR_FIXTURES / "valid/response.json")
        in_progress = load_json(PAIR_FIXTURES / "valid/response-in-progress.json")
        value_sets = [load_json(PAIR_FIXTURES / "valid/value-set.json")]

        def with_constraint(severity: str) -> dict:
            constrained = copy.deepcopy(questionnaire)
            constrained.setdefault("extension", []).append(
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/targetConstraint",
                    "extension": [
                        {"url": "key", "valueId": f"review-{severity}"},
                        {"url": "severity", "valueCode": severity},
                        {
                            "url": "expression",
                            "valueExpression": {
                                "language": "text/fhirpath",
                                "expression": "%resource.item.exists()",
                            },
                        },
                        {"url": "human", "valueString": "Review the response."},
                    ],
                }
            )
            return constrained

        error_issues = validator.validate_pair(
            with_constraint("error"), completed, value_sets
        )
        warning_issues = validator.validate_pair(
            with_constraint("warning"), completed, value_sets
        )
        in_progress_issues = validator.validate_pair(
            with_constraint("error"), in_progress, value_sets
        )

        self.assertIn(
            ("pair-expression-engine-required", "error"),
            {(issue.rule, issue.severity) for issue in error_issues},
        )
        self.assertIn(
            ("pair-expression-engine-required", "warning"),
            {(issue.rule, issue.severity) for issue in warning_issues},
        )
        self.assertNotIn(
            "pair-expression-engine-required",
            {issue.rule for issue in in_progress_issues},
        )

    def test_built_package_pins_sdc_and_the_matching_extension_package(self) -> None:
        archive_path = OUTPUT / "package.tgz"
        if not archive_path.is_file():
            self.skipTest("Questionnaire Publisher package is not present")
        with tarfile.open(archive_path, "r:gz") as archive:
            package_file = archive.extractfile("package/package.json")
            self.assertIsNotNone(package_file)
            package = json.load(package_file)
        self.assertEqual(package["name"], "org.grovealliance.fhir.questionnaire")
        self.assertEqual(package["version"], "0.2.0")
        self.assertEqual(package["dependencies"].get("hl7.fhir.uv.sdc"), "4.0.0")
        self.assertEqual(
            package["dependencies"].get("hl7.fhir.uv.extensions.r4"),
            "5.3.0",
        )


if __name__ == "__main__":
    unittest.main()
