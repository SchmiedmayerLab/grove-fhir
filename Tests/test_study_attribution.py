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
from Scripts.producer_validation.io import json_pointer
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


ENTRY_KEY = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key"
CONTEXT_SNAPSHOT = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-context-snapshot"
RECORD_VERSION = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-record-version"
CONTEXT_TYPES = ("Patient", "ResearchStudy", "ResearchSubject", "PlanDefinition", "QuestionnaireResponse")


def role(identifier):
    return identifier["type"]["coding"][0]["code"]


def entry_key(entry):
    return next(item["valueIdentifier"] for item in entry["extension"] if item["url"] == ENTRY_KEY)


def record_versions(bundle):
    """The record-version entry keys of a Bundle's conversion Provenances, in entry order."""
    return [
        {"system": entry_key(entry)["system"], "value": entry_key(entry)["value"]}
        for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"
    ]


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
    # No Bundle names its producer any more: the binding names the repository-scoped
    # source-record namespace every record of the source states.
    systems = {
        provenance["entity"][0]["what"]["identifier"]["system"] for provenance in resources(source, "Provenance")
    }
    if (not binding or binding_id != authority["verifiedSourceBinding"]
            or binding["participant"] != participant
            or systems != {binding["sourceRecordSystem"]}):
        return "source-binding"
    receipt = authority["consentReceipts"].get(grant.get("consentReceipt"))
    if not receipt:
        return "missing-consent"
    if (receipt["enrollment"] != grant["enrollment"] or receipt["protocol"] != grant["protocol"]
            or receipt["participant"] != participant or receipt["sourceBinding"] != binding_id):
        return "consent-binding"
    if set(grant["output"].values()) != {lock["path"], lock["outputPointer"]}:
        return "output-version"
    collected = datetime.fromisoformat(json_pointer(source, lock["outputPointer"], "outputPointer")["effectiveDateTime"])
    window = receipt.get("collectionWindow")
    if (not window or datetime.fromisoformat(receipt["acceptedAt"]) > collected
            or not datetime.fromisoformat(window["startInclusive"]) <= collected
            < datetime.fromisoformat(window["endExclusive"])):
        return "collection-authority"
    return None


class StudyAttributionTests(unittest.TestCase):
    def setUp(self):
        self.history = json.loads((CORPUS / "history.json").read_text())
        self.source = json.loads((CORPUS / self.history["source"]).read_text())
        self.lock = {**json.loads((CORPUS / self.history["eventLock"]).read_text()), "path": self.history["eventLock"]}
        self.authority = json.loads((CORPUS / self.history["authority"]).read_text())

    def test_generated_files_and_record_version_lock_match_exact_bytes(self):
        for path, expected in {**generated_files(), **policy_negative_files()}.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_text(), expected)
        # The lock names the source's record versions; no Bundle carries an event identity.
        self.assertNotIn("identifier", self.source)
        self.assertNotIn("eventIdentity", self.lock)
        self.assertEqual(
            [{"system": key["system"], "value": key["value"]} for key in self.lock["recordVersions"]],
            record_versions(self.source),
        )
        self.assertEqual(self.lock["releaseVersion"], "0.8.0")
        self.assertEqual(self.lock["sourceEventSHA256"], hashlib.sha256((CORPUS / self.history["source"]).read_bytes()).hexdigest())

    def test_study_context_nodes_are_content_addressed(self):
        for name in (self.history["source"], "context-two-studies.json"):
            bundle = json.loads((CORPUS / name).read_text())
            for entry in bundle["entry"]:
                resource = entry["resource"]
                if resource["resourceType"] not in CONTEXT_TYPES:
                    continue
                key = entry_key(entry)
                with self.subTest(bundle=name, node=resource["resourceType"]):
                    self.assertEqual(role(key), "context-snapshot")
                    if resource["resourceType"] == "QuestionnaireResponse":
                        copies = [item["valueIdentifier"] for item in resource.get("extension", []) if item["url"] == CONTEXT_SNAPSHOT]
                    else:
                        copies = [item for item in resource.get("identifier", []) if "type" in item and role(item) == "context-snapshot"]
                    self.assertEqual([(item["system"], item["value"]) for item in copies], [(key["system"], key["value"])])
            for entry in bundle["entry"]:
                if entry["resource"]["resourceType"] == "Provenance":
                    with self.subTest(bundle=name, provenance=entry["fullUrl"]):
                        self.assertEqual(role(entry_key(entry)), "record-version")
                        versions = [item["valueIdentifier"] for item in entry["resource"]["extension"] if item["url"] == RECORD_VERSION]
                        self.assertEqual(
                            [(item["system"], item["value"]) for item in versions],
                            [(entry_key(entry)["system"], entry_key(entry)["value"])],
                        )

    def test_both_supported_source_shapes_pass_the_producer_contract(self):
        _, paths = validate_manifest(CORPUS / "official-validator-manifest.json")
        self.assertEqual(len(paths), 2)
        self.assertEqual(len(resources(self.source, "ResearchStudy")), 1)
        both = json.loads((CORPUS / "context-two-studies.json").read_text())
        self.assertEqual(len(resources(both, "ResearchStudy")), 2)
        self.assertEqual(len(resources(both, "ResearchSubject")), 2)
        self.assertEqual(len(resources(both, "PlanDefinition")), 2)
        self.assertEqual(len(resources(both, "Observation")), 1)
        # The same record in another study context is another version: its outputs reference other nodes.
        self.assertNotEqual(record_versions(self.source), record_versions(both))
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
            self.assertEqual(step["expect"]["storedRecordVersions"], 1)
            self.assertNotIn("storedEvents", step["expect"])
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
        self.assertEqual(self.history["steps"][1]["repositoryInput"], "repository-b.json")
        self.assertEqual(self.history["steps"][2]["repositoryInput"], "revision-a2.json")
        self.assertEqual(json_pointer(self.source, self.lock["outputPointer"], "outputPointer")["resourceType"], "Observation")
        for study, grant_id, graph in (("a", "a1", self.source), ("b", "b3", repository)):
            grant = self.history["grants"][grant_id]
            enrollment = resources(graph, "ResearchSubject")[0]
            study_entry = next(entry for entry in graph["entry"] if entry["resource"]["resourceType"] == "ResearchStudy")
            self.assertEqual(enrollment["study"]["reference"], study_entry["fullUrl"])
            self.assertEqual(grant["enrollment"], enrollment["identifier"][0]["value"])
            self.assertEqual(grant["protocol"], self.lock["protocols"][study])
            self.assertEqual(set(grant["output"].values()), {self.lock["path"], self.lock["outputPointer"]})
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
        # A derived export presented as a retry of the source record version is not one.
        retry = cases["derived-export-as-record-retry"]
        self.assertNotEqual(retry, self.source)
        self.assertNotIn("derived-export-as-event-retry", cases)
        self.assertEqual(len(cases), 4)


if __name__ == "__main__":
    unittest.main()
