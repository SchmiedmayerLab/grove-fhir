"""Check the worked attribution graphs and policy counterexamples, not a production grant engine."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

import copy
import hashlib
import json
import unittest
from datetime import datetime

from Scripts.fhir_fixture_corpus import build_cases, load_bases, load_manifest
from Scripts.producer_validation.diagnostics import ProducerValidationError
from Scripts.producer_validation.exchange_bundle import validate_exchange_bundle
from Scripts.producer_validation.manifest import validate_manifest
from Scripts.study_attribution_fixtures import CORPUS, STUDY_EXTENSION, export_graph, generated_files, policy_negative_files


def resources(bundle, kind):
    return [entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == kind]


def references(value):
    if isinstance(value, dict):
        if "reference" in value:
            yield value["reference"]
        for child in value.values():
            yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def protocol_pair(bundle):
    entries = {entry["fullUrl"]: entry["resource"] for entry in bundle["entry"]}
    study = resources(bundle, "ResearchStudy")[0]
    plan = entries[study["protocol"][0]["reference"]]
    return {"url": plan["url"], "version": plan["version"]}


def grant_authority_failure(grant, authority, source, lock):
    """Predicate for this fixed point-sample corpus; not a receiver authorization implementation."""
    binding_id = grant.get("sourceBinding")
    binding = authority["sourceBindings"].get(binding_id)
    participant = resources(source, "Patient")[0]["identifier"][0]
    if (not binding or binding_id != authority["verifiedSourceBinding"]
            or binding["participant"] != participant
            or source["identifier"]["system"] != binding["eventSystem"]
            or source["identifier"]["value"].split(":")[1] != binding["sourceID"]):
        return "source-binding"
    receipt = authority["consentReceipts"].get(grant.get("consentReceipt"))
    if not receipt:
        return "missing-consent"
    if (receipt["enrollment"] != grant["enrollment"] or receipt["protocol"] != grant["protocol"]
            or receipt["participant"] != participant or receipt["sourceBinding"] != binding_id):
        return "consent-binding"
    if grant["output"] != {"eventLock": "event-lock.json", "pointer": lock["outputPointer"]}:
        return "output-version"
    collected = datetime.fromisoformat(source["entry"][2]["resource"]["effectiveDateTime"])
    window = receipt.get("collectionWindow")
    if (not window or datetime.fromisoformat(receipt["acceptedAt"]) > collected
            or not datetime.fromisoformat(window["startInclusive"]) <= collected
            < datetime.fromisoformat(window["endExclusive"])):
        return "collection-authority"
    return None


class StudyAttributionTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((CORPUS / "source-event.json").read_text())
        self.lock = json.loads((CORPUS / "event-lock.json").read_text())
        self.history = json.loads((CORPUS / "history.json").read_text())
        self.authority = json.loads((CORPUS / self.history["authority"]).read_text())

    def test_generated_files_and_event_lock_match_exact_bytes(self):
        for path, expected in {**generated_files(), **policy_negative_files()}.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_text(), expected)
        self.assertEqual(self.lock["eventIdentity"], self.source["identifier"])
        self.assertEqual(self.lock["sourceEventSHA256"], hashlib.sha256((CORPUS / "source-event.json").read_bytes()).hexdigest())

    def test_both_supported_source_shapes_pass_the_producer_contract(self):
        _, paths = validate_manifest(CORPUS / "official-validator-manifest.json")
        self.assertEqual(len(paths), 2)
        self.assertEqual(len(resources(self.source, "ResearchStudy")), 1)
        both = json.loads((CORPUS / "context-two-studies.json").read_text())
        self.assertEqual(len(resources(both, "ResearchStudy")), 2)
        self.assertEqual(len(resources(both, "ResearchSubject")), 2)
        self.assertEqual(len(resources(both, "PlanDefinition")), 2)
        self.assertEqual(len(resources(both, "Observation")), 1)
        self.assertNotEqual(self.source["identifier"], both["identifier"])
        entries = {entry["fullUrl"]: entry["resource"] for entry in both["entry"]}
        associations = [item for item in resources(both, "Observation")[0]["extension"] if item["url"] == STUDY_EXTENSION]
        pairs = []
        for association in associations:
            study = entries[association["valueReference"]["reference"]]
            plan = entries[study["protocol"][0]["reference"]]
            pairs.append((plan["url"], plan["version"]))
        self.assertCountEqual(pairs, [(value["url"], value["version"]) for value in self.lock["protocols"].values()])

    def test_exports_close_the_graph_and_do_not_expose_the_other_membership(self):
        clinical = copy.deepcopy(resources(self.source, "Observation")[0])
        clinical["extension"] = [item for item in clinical["extension"] if item["url"] != STUDY_EXTENSION]
        for study, other in (("a", "b"), ("b", "a")):
            with self.subTest(study=study):
                export = json.loads((CORPUS / f"export-{study}.json").read_text())
                full_urls = [entry["fullUrl"] for entry in export["entry"]]
                self.assertEqual(len(full_urls), len(set(full_urls)))
                self.assertLessEqual(set(references(export)), set(full_urls))
                self.assertNotEqual(export["identifier"], self.source["identifier"])
                self.assertNotIn("meta", export)
                self.assertTrue(all("extension" not in entry for entry in export["entry"]))
                self.assertEqual(protocol_pair(export), self.lock["protocols"][study])
                self.assertEqual(len(resources(export, "ResearchSubject")), 1)
                serialized = json.dumps(export)
                for marker in (f"enrollment-{other}", f"study-{other}", f"plan-{other}", f"Study {other.upper()}"):
                    self.assertNotIn(marker, serialized)
                observed = copy.deepcopy(resources(export, "Observation")[0])
                observed["extension"] = [item for item in observed["extension"] if item["url"] != STUDY_EXTENSION]
                self.assertEqual(observed, clinical)
                provenance = resources(export, "Provenance")
                self.assertEqual(len(provenance), 1)
                self.assertNotIn("meta", provenance[0])
                self.assertEqual(provenance[0]["entity"][0]["what"]["identifier"]["value"], self.lock["exportLineage"][study])

    def test_revision_publication_and_withdrawal_do_not_retarget_existing_grants(self):
        later = json.loads((CORPUS / "revision-a2.json").read_text())
        self.assertEqual(protocol_pair(later), {"url": self.lock["protocols"]["a"]["url"], "version": "2"})
        self.assertEqual(protocol_pair(self.source), self.lock["protocols"]["a"])
        steps = self.history["steps"]
        self.assertEqual([step["operation"] for step in steps], [
            "accept-source-with-grant-a1", "authorize-late-b3", "publish-a2", "withdraw-a", "restart-and-replay-source"
        ])
        self.assertEqual([step["expect"]["activeGrants"] for step in steps], [["a1"], ["a1", "b3"], ["a1", "b3"], ["b3"], ["b3"]])
        self.assertEqual([step["expect"]["retainedGrantDecisions"] for step in steps], [
            {"a1": "active"}, {"a1": "active", "b3": "active"}, {"a1": "active", "b3": "active"},
            {"a1": "revoked", "b3": "active"}, {"a1": "revoked", "b3": "active"},
        ])
        self.assertEqual([step["expect"]["exports"] for step in steps], [
            {"a": "export-a.json", "b": None}, {"a": "export-a.json", "b": "export-b.json"},
            {"a": "export-a.json", "b": "export-b.json"}, {"a": None, "b": "export-b.json"}, {"a": None, "b": "export-b.json"},
        ])
        for step in steps:
            self.assertEqual(step["expect"]["storedEvents"], 1)
            self.assertEqual(step["expect"]["storedClinicalPayloads"], 1)
            self.assertIs(step["expect"]["sourceUnchanged"], True)
        self.assertEqual(self.history["grants"]["a1"]["output"], self.history["grants"]["b3"]["output"])

    def test_exact_server_owned_receipts_authorize_both_grants(self):
        for grant in self.history["grants"].values():
            with self.subTest(receipt=grant["consentReceipt"]):
                self.assertIsNone(grant_authority_failure(grant, self.authority, self.source, self.lock))
        # A late association does not mean late consent. B's authority already covers collection.
        collected = datetime.fromisoformat(resources(self.source, "Observation")[0]["effectiveDateTime"])
        self.assertLess(datetime.fromisoformat(self.authority["consentReceipts"]["consent-b3"]["acceptedAt"]), collected)
        self.assertNotIn("consentReceipts", self.source)
        self.assertNotIn("consentReceipts", json.loads((CORPUS / "repository-b.json").read_text()))

    def test_profile_valid_graphs_cannot_replace_missing_or_mismatched_authority(self):
        manifest = json.loads((CORPUS / "authority-negative-cases.json").read_text())
        self.assertEqual(manifest["expectAfterEveryRejection"], self.history["steps"][0]["expect"])
        original = copy.deepcopy(self.source)
        for case in manifest["cases"]:
            with self.subTest(case=case["id"]):
                authority = copy.deepcopy(self.authority)
                grant = copy.deepcopy(self.history["grants"]["b3"])
                grant.update(case.get("grantChanges", {}))
                authority["consentReceipts"]["consent-b3"].update(case.get("receiptChanges", {}))
                self.assertEqual(grant_authority_failure(grant, authority, self.source, self.lock), case["expectedFailure"])
                # Existing A authority survives B's failed request, with no new B decision.
                self.assertIsNone(grant_authority_failure(self.history["grants"]["a1"], authority, self.source, self.lock))
                validate_exchange_bundle(self.source, "fixture", set())
                self.assertEqual(self.source, original)
        self.assertEqual(len(manifest["cases"]), 10)

    def test_withdrawal_retains_decision_but_never_reactivates_access(self):
        withdrawal = self.authority["withdrawal"]
        revoked = withdrawal["activeGrantRemoved"]
        grant = self.history["grants"][revoked]
        self.assertEqual(grant["enrollment"], withdrawal["enrollment"])
        self.assertEqual(withdrawal["retainedDecision"], {
            "grant": revoked, "status": "revoked", "reason": "enrollment-withdrawal"
        })
        self.assertFalse(withdrawal["newGrantAllowed"])
        self.assertFalse(withdrawal["sourceReplayCanReactivate"])
        for step in self.history["steps"][-2:]:
            self.assertNotIn(revoked, step["expect"]["activeGrants"])
            self.assertEqual(step["expect"]["retainedGrantDecisions"][revoked], "revoked")
            self.assertEqual(step["expect"]["retainedGrantDecisions"]["b3"], "active")
        # Historical collection eligibility alone is not current authorization after withdrawal.
        self.assertIsNone(grant_authority_failure(grant, self.authority, self.source, self.lock))

    def test_late_grant_matches_the_subject_and_exact_repository_protocol(self):
        repository = json.loads((CORPUS / "repository-b.json").read_text())
        subject = resources(repository, "ResearchSubject")[0]
        self.assertEqual(subject["individual"]["identifier"], resources(self.source, "Patient")[0]["identifier"][0])
        self.assertEqual(protocol_pair(repository), self.lock["protocols"]["b"])
        self.assertEqual(len(resources(repository, "Observation")), 0)
        self.assertNotIn("enrollment-b", json.dumps(self.source))
        self.assertEqual(self.history["eventLock"], "event-lock.json")
        self.assertEqual(self.history["source"], "source-event.json")
        self.assertEqual(self.history["steps"][1]["repositoryInput"], "repository-b.json")
        self.assertEqual(self.history["steps"][2]["repositoryInput"], "revision-a2.json")
        self.assertEqual(self.lock["outputPointer"], "/entry/2/resource")
        self.assertEqual(self.source["entry"][2]["resource"]["resourceType"], "Observation")
        for study, grant_id, graph in (("a", "a1", self.source), ("b", "b3", repository)):
            grant = self.history["grants"][grant_id]
            enrollment = resources(graph, "ResearchSubject")[0]
            study_entry = next(entry for entry in graph["entry"] if entry["resource"]["resourceType"] == "ResearchStudy")
            self.assertEqual(enrollment["study"]["reference"], study_entry["fullUrl"])
            self.assertEqual(grant["enrollment"], enrollment["identifier"][0]["value"])
            self.assertEqual(grant["protocol"], self.lock["protocols"][study])
            self.assertEqual(grant["output"], {"eventLock": "event-lock.json", "pointer": self.lock["outputPointer"]})
        original = copy.deepcopy(self.source)
        export_graph(self.source, "a")
        export_graph(self.source, "b")
        self.assertEqual(self.source, original)

    def test_negative_cases_distinguish_graph_shape_from_receiver_policy(self):
        path = CORPUS / "negative-cases.json"
        manifest = load_manifest(path)
        cases = build_cases(manifest, load_bases(manifest, path))
        with self.assertRaises(ProducerValidationError) as error:
            validate_exchange_bundle(cases["protocol-is-not-a-reference"], "fixture", set())
        self.assertEqual(error.exception.diagnostic["code"], "mobile-exchange.reference-shape")
        mismatch = cases["subject-mismatch"]
        validate_exchange_bundle(mismatch, "fixture", set())
        subject = resources(mismatch, "ResearchSubject")[0]["individual"]["identifier"]
        self.assertNotEqual(subject, resources(mismatch, "Patient")[0]["identifier"][0])
        self.assertNotEqual(protocol_pair(cases["lost-historical-revision"]), self.lock["protocols"]["a"])
        retry = cases["derived-export-as-event-retry"]
        self.assertEqual(retry["identifier"], self.source["identifier"])
        self.assertNotEqual(retry, self.source)
        self.assertEqual(len(cases), 4)


if __name__ == "__main__":
    unittest.main()
