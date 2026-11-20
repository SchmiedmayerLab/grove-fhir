"""Check the study task graph cases, the graph rules, and the published study examples."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "study/fixtures/graph"
STRUCTURAL = ROOT / "study/fixtures/structural"
GENERATED = ROOT / "study/fsh-generated/resources"

spec = importlib.util.spec_from_file_location(
    "validate_study_graph", ROOT / "Scripts/validate-study-graph.py"
)
if spec is None or spec.loader is None:
    raise RuntimeError("Cannot load the study graph validator")
graph = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = graph
spec.loader.exec_module(graph)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def outcome(result) -> dict:
    if result.rejected:
        return {"rejected": sorted({issue.rule for issue in result.issues})}
    return {"outcomes": result.outcomes}


class StudyGraphCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load(GRAPH / "cases.json")
        cls.definitions = graph.load(GRAPH / cls.manifest["definitions"])

    def receiver(self):
        return graph.Receiver(self.definitions)

    def delivery(self, name: str) -> dict:
        return load(GRAPH / "deliveries" / f"{name}.json")

    def test_every_case_reaches_its_recorded_outcome(self) -> None:
        self.assertEqual(set(self.manifest), {"schemaVersion", "purpose", "definitions", "cases"})
        self.assertEqual(self.manifest["schemaVersion"], 0)
        identifiers = [case["id"] for case in self.manifest["cases"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for case in self.manifest["cases"]:
            receiver = self.receiver()
            for step, delivery in enumerate(case["deliveries"]):
                with self.subTest(case=case["id"], step=step, path=delivery["path"]):
                    self.assertEqual(len({"outcomes", "rejected"} & set(delivery)), 1)
                    expected = (
                        {"rejected": sorted(delivery["rejected"])}
                        if "rejected" in delivery
                        else {"outcomes": delivery["outcomes"]}
                    )
                    result = receiver.apply(graph.load(GRAPH / delivery["path"]))
                    self.assertEqual(outcome(result), expected, result.issues)

    def test_every_delivery_fixture_is_used_by_a_case(self) -> None:
        used = {
            delivery["path"] for case in self.manifest["cases"] for delivery in case["deliveries"]
        }
        present = {
            path.relative_to(GRAPH).as_posix() for path in (GRAPH / "deliveries").glob("*.json")
        }
        self.assertEqual(used, present)

    def test_cases_cover_the_acceptance_scenarios(self) -> None:
        identifiers = {case["id"] for case in self.manifest["cases"]}
        self.assertTrue({
            "assigned-then-completed", "exact-replay", "conflicting-reuse", "same-time-occurrences",
            "re-enrollment", "corrected-result", "wrong-subject", "wrong-instrument-version",
            "pending-as-completed", "invalid-result-reference", "result-outside-window",
            "informational-completed", "completed-after-window", "questionnaire-completed-without-result",
        } <= identifiers)

    def test_every_graph_fixture_passes_through_the_official_validator(self) -> None:
        manifest = load(ROOT / "Conformance/fixture-validator-manifest.json")
        validated = {entry["path"] for entry in manifest["resources"]}
        for path in [GRAPH / "definitions.json", *sorted((GRAPH / "deliveries").glob("*.json"))]:
            with self.subTest(path=path.name):
                self.assertIn(path.relative_to(ROOT).as_posix(), validated)
        self.assertIn("study/fixtures/structural/corpus.json", manifest["negativeCorpora"])
        self.assertIn("study/fixtures/structural/base/corpus.json", manifest["negativeCorpora"])

    def test_completion_is_counted_once_across_replay_and_correction(self) -> None:
        receiver = self.receiver()
        for name in ("assigned", "completed", "completed", "corrected"):
            self.assertFalse(receiver.apply(graph.resources_of(self.delivery(name))).rejected)
        state = receiver.occurrences[("https://example.org/research/occurrence-id", "occurrence-0001")]
        self.assertEqual(state.status, "completed")
        self.assertEqual(state.result_version, "2")
        self.assertEqual(len(receiver.occurrences), 1)

    def test_a_rejected_delivery_changes_no_state(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("assigned")))
        before = dict(receiver.occurrences)
        self.assertTrue(receiver.apply(graph.resources_of(self.delivery("wrong-subject"))).rejected)
        self.assertEqual(receiver.occurrences, before)

    def test_a_correction_must_be_amended(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("completed")))
        corrected = self.delivery("corrected")
        corrected["entry"][1]["resource"]["status"] = "completed"
        corrected["entry"][1]["resource"]["authored"] = "2026-08-19T21:00:00-07:00"
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(corrected))),
            {"rejected": ["study-task-correction"]},
        )

    def test_an_altered_replay_and_an_altered_result_are_rejected(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("completed")))
        altered = self.delivery("completed")
        altered["entry"][0]["resource"]["executionPeriod"] = {"start": "2026-08-19T09:20:00-07:00"}
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(altered))),
            {"rejected": ["study-task-altered-replay"]},
        )
        altered = self.delivery("completed")
        altered["entry"][1]["resource"]["item"][1]["answer"][0]["valueInteger"] = 3
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(altered))),
            {"rejected": ["study-task-altered-result"]},
        )

    def test_a_cancelled_occurrence_is_final_and_stopped_before_its_window_ends(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("excused")))
        reopened = self.delivery("excused")
        task = reopened["entry"][0]["resource"]
        task["status"] = "ready"
        del task["statusReason"]
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(reopened))),
            {"rejected": ["study-task-status-transition"]},
        )
        late = self.delivery("excused")
        late["entry"][0]["resource"]["lastModified"] = "2026-08-22T00:00:01-07:00"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(late))),
            {"rejected": ["study-task-cancelled-after-window"]},
        )

    def test_one_response_completes_one_occurrence(self) -> None:
        shared = self.delivery("completed")
        other = copy.deepcopy(shared["entry"][0])
        other["fullUrl"] = other["fullUrl"].replace("occurrence-0001", "occurrence-0004")
        other["resource"]["id"] = "occurrence-0004"
        other["resource"]["identifier"][0]["value"] = "occurrence-0004"
        shared["entry"].append(other)
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(shared))),
            {"rejected": ["study-task-result-shared"]},
        )
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("completed")))
        later = self.delivery("completed")
        later["entry"].pop()
        later["entry"][0] = other
        later["entry"].append(self.delivery("completed")["entry"][1])
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(later))),
            {"rejected": ["study-task-result-shared"]},
        )

    def test_one_delivery_carries_an_occurrence_once(self) -> None:
        duplicated = self.delivery("assigned")
        duplicated["entry"].append(copy.deepcopy(duplicated["entry"][0]))
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(duplicated))),
            {"rejected": ["study-task-duplicate-occurrence"]},
        )

    def test_a_response_never_points_back_through_part_of(self) -> None:
        delivery = self.delivery("completed")
        delivery["entry"][1]["resource"]["partOf"] = [{"reference": "Task/occurrence-0001"}]
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-result-part-of"]},
        )

    def test_definitions_and_enrollment_must_resolve_and_agree(self) -> None:
        cases = {
            "study-task-instrument": ("/entry/0/resource/input/3/valueCanonical", "https://example.org/fhir/Questionnaire/daily-check-in|1.1.0"),
            "study-task-protocol": ("/entry/0/resource/input/2/valueCanonical", "https://example.org/fhir/PlanDefinition/daily-check-in-protocol|2.0.0"),
            "study-task-enrollment": ("/entry/0/resource/input/1/valueReference/identifier/value", "enrollment-999"),
        }
        for rule, (pointer, value) in cases.items():
            with self.subTest(rule=rule):
                delivery = self.delivery("assigned")
                *parents, last = [int(part) if part.isdigit() else part for part in pointer.strip("/").split("/")]
                node = delivery
                for part in parents:
                    node = node[part]
                node[last] = value
                self.assertEqual(
                    outcome(self.receiver().apply(graph.resources_of(delivery))),
                    {"rejected": [rule]},
                )

    def test_another_participant_cannot_use_the_enrollment(self) -> None:
        delivery = self.delivery("assigned")
        delivery["entry"][0]["resource"]["for"]["identifier"]["value"] = "participant-002"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-enrollment"]},
        )

    def test_an_occurrence_without_a_result_kind_carries_no_output(self) -> None:
        delivery = self.delivery("informational-completed")
        delivery["entry"][0]["resource"]["output"] = [{
            "type": {"coding": [{"system": graph.SDC_SYSTEM, "code": "questionnaire-response"}]},
            "valueReference": {"reference": "QuestionnaireResponse/response-0001/_history/1"},
        }]
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-output"]},
        )

    def test_a_completed_informational_occurrence_replays_and_stays_final(self) -> None:
        receiver = self.receiver()
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(self.delivery("informational-completed")))),
            {"outcomes": {"welcome-0001": "accepted"}},
        )
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(self.delivery("informational-completed")))),
            {"outcomes": {"welcome-0001": "replayed"}},
        )
        reopened = self.delivery("informational-completed")
        reopened["entry"][0]["resource"]["status"] = "ready"
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(reopened))),
            {"rejected": ["study-task-status-transition"]},
        )

    def test_an_occurrence_without_a_result_is_completed_within_its_window(self) -> None:
        for last_modified in ("2026-08-17T23:59:59-07:00", "2026-08-25T08:00:01-07:00"):
            with self.subTest(last_modified=last_modified):
                delivery = self.delivery("informational-completed")
                delivery["entry"][0]["resource"]["lastModified"] = last_modified
                self.assertEqual(
                    outcome(self.receiver().apply(graph.resources_of(delivery))),
                    {"rejected": ["study-task-completion-window"]},
                )
        on_time = self.delivery("informational-completed")
        on_time["entry"][0]["resource"]["lastModified"] = "2026-08-25T08:00:00-07:00"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(on_time))),
            {"outcomes": {"welcome-0001": "accepted"}},
        )

    def test_a_base_task_of_a_questionnaire_component_carries_the_questionnaire_input(self) -> None:
        delivery = self.delivery("assigned")
        task = delivery["entry"][0]["resource"]
        task["meta"]["profile"] = ["https://grovealliance.org/fhir/study/StructureDefinition/grove-study-task"]
        task["input"] = [
            entry for entry in task["input"]
            if not any(coding.get("code") == "questionnaire" for coding in entry["type"]["coding"])
        ]
        self.assertEqual(task["status"], "ready")
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-instrument"]},
        )

    def test_a_questionnaire_code_applies_the_questionnaire_rules(self) -> None:
        delivery = self.delivery("informational-completed")
        delivery["entry"][0]["resource"]["code"] = {
            "coding": [{"system": graph.SDC_SYSTEM, "code": "complete-questionnaire"}]
        }
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-instrument", "study-task-result-reference"]},
        )

    def test_an_occurrence_without_an_instrument_carries_no_questionnaire_input(self) -> None:
        delivery = self.delivery("informational-completed")
        delivery["entry"][0]["resource"]["input"].append(
            copy.deepcopy(self.delivery("assigned")["entry"][0]["resource"]["input"][3])
        )
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-instrument"]},
        )

    def test_an_unresolved_component_is_rejected_for_its_definition_only(self) -> None:
        delivery = self.delivery("informational-completed")
        task = delivery["entry"][0]["resource"]
        task["instantiatesCanonical"] = "https://example.org/fhir/ActivityDefinition/unknown|1.0.0"
        task["output"] = [{"type": {"text": "result"}, "valueString": "done"}]
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-definition", "study-task-protocol"]},
        )

    def test_rule_groups_are_disjoint(self) -> None:
        self.assertEqual(set(graph.OCCURRENCE_RULES) & set(graph.QUESTIONNAIRE_RULES), set())
        self.assertEqual(len(graph.RULES), len(set(graph.RULES)))

    def test_paired_questionnaire_rules_apply_to_the_linked_response(self) -> None:
        delivery = self.delivery("completed")
        delivery["entry"][1]["resource"]["language"] = "fr"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["pair-response-language"]},
        )

    def test_an_absolute_result_link_resolves_against_the_entry_full_url(self) -> None:
        delivery = self.delivery("completed")
        output = delivery["entry"][0]["resource"]["output"][0]["valueReference"]
        output["reference"] = "https://example.org/fhir/QuestionnaireResponse/response-0001/_history/1"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"outcomes": {"occurrence-0001": "accepted"}},
        )
        output["reference"] = "https://elsewhere.example.org/fhir/QuestionnaireResponse/response-0001/_history/1"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-result-reference"]},
        )

    def test_a_single_task_is_a_delivery(self) -> None:
        task = self.delivery("assigned")["entry"][0]["resource"]
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(task))),
            {"outcomes": {"occurrence-0001": "accepted"}},
        )

    def test_a_task_without_one_complete_identifier_is_refused(self) -> None:
        task = self.delivery("assigned")["entry"][0]["resource"]
        del task["identifier"][0]["system"]
        with self.assertRaisesRegex(ValueError, "occurrence identifier"):
            self.receiver().apply(graph.resources_of(task))

    def test_a_delivery_may_repeat_a_definition_it_shares_with_the_receiver(self) -> None:
        definitions = load(GRAPH / "definitions.json")
        delivery = self.delivery("completed")
        delivery["entry"].append(copy.deepcopy(definitions["entry"][2]))
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"outcomes": {"occurrence-0001": "accepted"}},
        )
        changed = copy.deepcopy(definitions["entry"][2])
        changed["resource"]["title"] = "Another title"
        delivery["entry"][-1] = changed
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-instrument"]},
        )

    def test_a_result_link_without_a_restful_base_resolves_only_without_one(self) -> None:
        delivery = self.delivery("completed")
        delivery["entry"][0]["fullUrl"] = "urn:uuid:5a8f0c2e-6b4e-4c1d-9f1e-2d3c4b5a6f70"
        delivery["entry"][1]["fullUrl"] = "urn:uuid:0b1c2d3e-4f50-4617-8293-a4b5c6d7e8f9"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"outcomes": {"occurrence-0001": "accepted"}},
        )
        delivery["entry"][1]["fullUrl"] = "https://other.example.org/fhir/QuestionnaireResponse/response-0001"
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(delivery))),
            {"rejected": ["study-task-result-reference"]},
        )

    def test_a_correction_keeps_the_response_resource(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("completed")))
        swapped = self.delivery("corrected")
        swapped["entry"][0]["resource"]["output"][0]["valueReference"]["reference"] = (
            "QuestionnaireResponse/response-0009/_history/2"
        )
        swapped["entry"][1]["fullUrl"] = "https://example.org/fhir/QuestionnaireResponse/response-0009"
        swapped["entry"][1]["resource"]["id"] = "response-0009"
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(swapped))),
            {"rejected": ["study-task-correction"]},
        )

    def test_a_corrected_response_records_when_it_was_corrected(self) -> None:
        corrected = self.delivery("corrected")
        self.assertEqual(corrected["entry"][1]["resource"]["status"], "amended")
        self.assertGreater(corrected["entry"][1]["resource"]["authored"], "2026-08-19T23:59:59-07:00")
        completed = self.delivery("completed")
        completed["entry"][1]["resource"]["authored"] = corrected["entry"][1]["resource"]["authored"]
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(completed))),
            {"rejected": ["study-task-result-window"]},
        )

    def test_an_amended_response_does_not_complete_an_assigned_occurrence(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("assigned")))
        amended = self.delivery("completed")
        amended["entry"][1]["resource"]["status"] = "amended"
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(amended))),
            {"rejected": ["study-task-result-status"]},
        )

    def test_an_amended_response_is_never_authored_before_the_window_or_its_predecessor(self) -> None:
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("completed")))
        early = self.delivery("corrected")
        early["entry"][1]["resource"]["authored"] = "2026-08-19T05:00:00-07:00"
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(early))),
            {"rejected": ["study-task-result-window"]},
        )
        receiver = self.receiver()
        receiver.apply(graph.resources_of(self.delivery("completed")))
        backdated = self.delivery("corrected")
        backdated["entry"][1]["resource"]["authored"] = "2026-08-19T09:00:00-07:00"
        self.assertEqual(
            outcome(receiver.apply(graph.resources_of(backdated))),
            {"rejected": ["study-task-correction"]},
        )

    def test_a_corrected_result_travels_after_the_version_it_corrects(self) -> None:
        self.assertEqual(
            outcome(self.receiver().apply(graph.resources_of(self.delivery("corrected")))),
            {"rejected": ["study-task-result-status"]},
        )

    def test_malformed_members_fail_closed_without_a_crash(self) -> None:
        delivery = self.delivery("assigned")
        task = delivery["entry"][0]["resource"]
        task["input"][0]["type"] = ["performance-window"]
        task["input"][1]["valueReference"] = "enrollment-001"
        result = self.receiver().apply(graph.resources_of(delivery))
        self.assertEqual(outcome(result), {"rejected": ["study-task-enrollment"]})

    def test_the_conformance_page_lists_every_graph_rule(self) -> None:
        page = (ROOT / "study/input/pagecontent/conformance.md").read_text(encoding="utf-8")
        documented = re.findall(r"^\| `(study-task-[a-z-]+)` \|", page, re.MULTILINE)
        self.assertEqual(documented, list(graph.RULES))

    def test_every_rule_is_exercised(self) -> None:
        recorded = {
            rule
            for case in self.manifest["cases"]
            for delivery in case["deliveries"]
            for rule in delivery.get("rejected", [])
        }
        source = Path(__file__).read_text(encoding="utf-8")
        exercised = recorded | set(re.findall(r'"(study-task-[a-z-]+)"', source))
        self.assertEqual(set(graph.RULES) - exercised, set())

    def test_cli_reports_each_delivery_and_fails_on_a_rejection(self) -> None:
        command = [
            sys.executable, str(ROOT / "Scripts/validate-study-graph.py"),
            "--definitions", str(GRAPH / "definitions.json"),
            str(GRAPH / "deliveries/completed.json"), str(GRAPH / "deliveries/corrected.json"),
        ]
        accepted = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn("accepted occurrence-0001", accepted.stdout)
        self.assertIn("corrected occurrence-0001", accepted.stdout)
        rejected = subprocess.run(
            [*command[:4], str(GRAPH / "deliveries/wrong-subject.json")],
            capture_output=True, text=True, check=False, timeout=60,
        )
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("REJECTED study-task-result-subject occurrence-0001", rejected.stdout)


class StudyStructuralCorpusTests(unittest.TestCase):
    def test_each_case_differs_from_the_control_in_one_place(self) -> None:
        for directory in (STRUCTURAL, STRUCTURAL / "base"):
            corpus = load(directory / "corpus.json")
            control = load(directory / corpus["control"])
            for case in corpus["cases"]:
                with self.subTest(corpus=directory.name, case=case["path"]):
                    mutated = load(directory / case["path"])
                    changed = {key for key in set(control) | set(mutated) if control.get(key) != mutated.get(key)}
                    self.assertEqual(len(changed), 1, changed)

    def test_the_control_completes_the_graph_fixture_occurrence(self) -> None:
        control = load(STRUCTURAL / "control.json")
        completed = load(GRAPH / "deliveries/completed.json")["entry"][0]["resource"]
        self.assertEqual(control, completed)

    def test_the_base_control_assigns_the_informational_graph_occurrence(self) -> None:
        control = load(STRUCTURAL / "base/control.json")
        completed = load(GRAPH / "deliveries/informational-completed.json")["entry"][0]["resource"]
        self.assertEqual(control["status"], "ready")
        self.assertEqual(
            {key: value for key, value in control.items() if key not in {"status", "lastModified"}},
            {key: value for key, value in completed.items() if key not in {"status", "lastModified", "executionPeriod"}},
        )
        delivery = load(GRAPH / "deliveries/informational-completed.json")
        delivery["entry"][0]["resource"] = control
        assigned = graph.Receiver(graph.load(GRAPH / "definitions.json")).apply(graph.resources_of(delivery))
        self.assertEqual(outcome(assigned), {"outcomes": {"welcome-0001": "accepted"}})


class StudyExampleTests(unittest.TestCase):
    def test_example_versions_track_the_release(self) -> None:
        release = load(ROOT / "catalog/release-manifest.json")["releaseVersion"]
        source = (ROOT / "study/input/fsh/examples.fsh").read_text(encoding="utf-8")
        declared = re.findall(r'^\* version = "(.+)"$', source, re.MULTILINE)
        joined = re.findall(r'"https://grovealliance\.org/fhir/[^"|]+\|([^"]+)"', source)
        self.assertTrue(declared and joined)
        self.assertEqual(set(declared) | set(joined), {release})

    @unittest.skipUnless(
        (GENERATED / "Questionnaire-GroveStudyDailyCheckInExample.json").is_file()
        and (GENERATED / "QuestionnaireResponse-GroveStudyDailyCheckInResponseExample.json").is_file(),
        "the study guide has not been built",
    )
    def test_published_examples_form_an_accepted_graph(self) -> None:
        resources = [
            graph.Resolved(None, load(path))
            for path in sorted(GENERATED.glob("*.json"))
            if load(path).get("resourceType")
            in {"PlanDefinition", "ActivityDefinition", "Questionnaire", "ResearchSubject", "Task", "QuestionnaireResponse"}
        ]
        definitions = [item for item in resources if item.resource["resourceType"] not in {"Task", "QuestionnaireResponse"}]
        delivery = [item for item in resources if item.resource["resourceType"] in {"Task", "QuestionnaireResponse"}]
        result = graph.Receiver(definitions).apply(delivery)
        self.assertEqual(result.issues, [])
        self.assertEqual(
            result.outcomes,
            {
                "occurrence-0001": "accepted", "occurrence-0002": "accepted",
                "occurrence-0003": "accepted", "welcome-0001": "accepted",
            },
        )


if __name__ == "__main__":
    unittest.main()
