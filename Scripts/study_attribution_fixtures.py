"""Build multi-study source and derived-export examples; never implements receiver authorization."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from Scripts.exchange_protocol import derive_hmac_identity, entry_full_url, entry_node_identity, event_identity
from Scripts.fhir_fixture_corpus import build_cases, load_bases, load_manifest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Conformance/corpora/mobile-exchange"
CORPUS = ROOT / "Conformance/corpora/study-attribution"
MOBILE = "https://grovealliance.org/fhir/mobile/"
STUDY_EXTENSION = "http://hl7.org/fhir/StructureDefinition/workflow-researchStudy"
ROLE_SYSTEM = MOBILE + "CodeSystem/grove-identifier-role"


def encoded(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def rewrite(value, replacements):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "reference" and isinstance(child, str) and child in replacements:
                value[key] = replacements[child]
            else:
                rewrite(child, replacements)
    elif isinstance(value, list):
        for child in value:
            rewrite(child, replacements)


def event_graph(include_second_study=False):
    event = json.loads((BASE / "exchange-bundle.json").read_text())
    event["id"] = "GroveMultiStudyEventExample"
    event["identifier"]["value"] = event_identity("1f5c58aa-6ec6-4e79-a682-829a9debd3f5", 51 if include_second_study else 50)
    identity = event["identifier"]
    replacements = {}
    for entry in event["entry"]:
        key = entry["extension"][0]["valueIdentifier"]
        role = key["type"]["coding"][0]["code"]
        if role == "entry-node":
            _, node_role, ordinal, _ = key["value"].split(":")
            key["value"] = entry_node_identity(event_system=identity["system"], event_value=identity["value"], role=node_role, ordinal=ordinal)
        elif role == "device-snapshot":
            key["value"] = derive_hmac_identity(
                key=bytes(range(32)), key_id="test-key", epoch=1, identity_kind="device-snapshot",
                components=[identity["system"], identity["value"], "application", "fixture-app"],
            )
            entry["resource"]["identifier"] = [copy.deepcopy(key)]
        previous = entry["fullUrl"]
        entry["fullUrl"] = entry_full_url(key["system"], key["value"])
        replacements[previous] = entry["fullUrl"]
    rewrite(event, replacements)
    patient = event["entry"][0]["fullUrl"]
    observation = event["entry"][2]["resource"]

    def append(resource, role, ordinal):
        key = {
            "type": {"coding": [{"system": ROLE_SYSTEM, "code": "entry-node"}]},
            "system": "https://study.example.org/fhir/NamingSystem/grove-entry-node-v0",
            "value": entry_node_identity(event_system=identity["system"], event_value=identity["value"], role=role, ordinal=ordinal),
        }
        full_url = entry_full_url(key["system"], key["value"])
        event["entry"].append({
            "extension": [{"url": MOBILE + "StructureDefinition/grove-exchange-entry-node-key", "valueIdentifier": key}],
            "fullUrl": full_url, "resource": resource,
        })
        return full_url

    studies = (("a", "1"), ("b", "3")) if include_second_study else (("a", "1"),)
    for ordinal, (study, revision) in enumerate(studies):
        plan = append({
            "resourceType": "PlanDefinition", "id": f"plan-{study}-r{revision}",
            "url": f"https://study.example.org/PlanDefinition/{study}",
            "version": revision, "status": "active", "title": f"Study {study.upper()} Protocol",
        }, "plan-definition", ordinal)
        research_study = append({
            "resourceType": "ResearchStudy", "id": f"study-{study}-r{revision}",
            "identifier": [{"system": "https://study.example.org/studies", "value": study}],
            "status": "active", "title": f"Study {study.upper()}", "protocol": [{"reference": plan}],
        }, "research-study", ordinal)
        append({
            "resourceType": "ResearchSubject", "id": f"enrollment-{study}",
            "identifier": [{"system": "https://study.example.org/enrollments", "value": f"enrollment-{study}"}],
            "status": "on-study", "study": {"reference": research_study}, "individual": {"reference": patient},
        }, "research-subject", ordinal)
        observation["extension"].append({"url": STUDY_EXTENSION, "valueReference": {"reference": research_study}})
    return event


def repository_b():
    entries = [copy.deepcopy(entry) for entry in event_graph(True)["entry"] if
        entry["resource"]["id"].startswith(("plan-b-", "study-b-", "enrollment-b"))
    ]
    replacements = {}
    for entry in entries:
        entry.pop("extension")
        resource = entry["resource"]
        previous = entry["fullUrl"]
        entry["fullUrl"] = f"https://receiver.example.org/{resource['resourceType']}/{resource['id']}"
        replacements[previous] = entry["fullUrl"]
        if resource["resourceType"] == "ResearchSubject":
            resource["individual"] = {"type": "Patient", "identifier": {
                "system": "https://study.example.org/fhir/identifiers/participant", "value": "participant-001"
            }}
    rewrite(entries, replacements)
    return {"resourceType": "Bundle", "type": "collection", "id": "StudyBRepositoryExample", "entry": entries}


def export_graph(source, study):
    """Create a fixed example of an already-authorized export; not an access-control function."""
    export = copy.deepcopy(source)
    export["id"] = f"GroveStudy{study.upper()}DerivedExportExample"
    export.pop("meta")  # A derived repository collection is not a Mobile producer event.
    export["identifier"] = {"system": "https://receiver.example.org/exports", "value": f"study-{study}-export-1"}
    export["timestamp"] = "2026-08-22T10:00:00Z"
    if study == "b":
        # Fixture input supplied by the receiver, not retroactively inserted into the source event.
        entries = repository_b()["entry"]
        enrollment = next(entry["resource"] for entry in entries if entry["resource"]["resourceType"] == "ResearchSubject")
        enrollment["individual"] = {"reference": source["entry"][0]["fullUrl"]}
        export["entry"].extend(entries)
    other = "b" if study == "a" else "a"
    export["entry"] = [entry for entry in export["entry"] if
        entry["resource"]["resourceType"] != "Provenance"
        and not entry["resource"]["id"].startswith((f"plan-{other}-", f"study-{other}-", f"enrollment-{other}"))
    ]
    study_url = next(entry["fullUrl"] for entry in export["entry"] if entry["resource"]["resourceType"] == "ResearchStudy")
    for entry in export["entry"]:
        entry.pop("extension", None)
        if entry["resource"]["resourceType"] == "Observation":
            observation = entry["resource"]
            observation["extension"] = [extension for extension in observation["extension"] if extension["url"] != STUDY_EXTENSION]
            observation["extension"].append({"url": STUDY_EXTENSION, "valueReference": {"reference": study_url}})
    output_url = next(entry["fullUrl"] for entry in export["entry"] if entry["resource"]["resourceType"] == "Observation")
    export["entry"].append({
        "fullUrl": f"https://receiver.example.org/Provenance/export-{study}-1",
        "resource": {
            "resourceType": "Provenance", "id": f"export-{study}-1",
            "target": [{"reference": output_url}], "recorded": export["timestamp"],
            "activity": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle", "code": "transform"}]},
            "agent": [{"who": {"type": "Device", "identifier": {"system": "https://receiver.example.org/services", "value": "study-export"}}}],
            "entity": [{"role": "source", "what": {"identifier": {"system": "https://receiver.example.org/custody", "value": f"study-{study}-source-1"}}}],
        },
    })
    return export


def generated_files():
    source = event_graph()
    files = {CORPUS / "source-event.json": encoded(source)}
    files[CORPUS / "context-two-studies.json"] = encoded(event_graph(True))
    files[CORPUS / "repository-b.json"] = encoded(repository_b())
    for study in ("a", "b"):
        files[CORPUS / f"export-{study}.json"] = encoded(export_graph(source, study))
    files[CORPUS / "revision-a2.json"] = encoded({
        "resourceType": "Bundle", "type": "collection", "id": "StudyARevision2Example",
        "entry": [
            {"fullUrl": "https://receiver.example.org/PlanDefinition/a-r2", "resource": {
                "resourceType": "PlanDefinition", "id": "a-r2", "url": "https://study.example.org/PlanDefinition/a",
                "version": "2", "status": "active", "title": "Study A Protocol",
            }},
            {"fullUrl": "https://receiver.example.org/ResearchStudy/a-r2", "resource": {
                "resourceType": "ResearchStudy", "id": "a-r2", "status": "active", "title": "Study A",
                "identifier": [{"system": "https://study.example.org/studies", "value": "a"}],
                "protocol": [{"reference": "https://receiver.example.org/PlanDefinition/a-r2"}],
            }},
        ],
    })
    manifest = json.loads((BASE / "official-validator-manifest.json").read_text())
    manifest["producer"]["name"] = "Grove FHIR multi-study event fixture"
    manifest["resources"] = [
        {"path": path, "requiredProfiles": source["meta"]["profile"]}
        for path in ("source-event.json", "context-two-studies.json")
    ]
    manifest["semanticVectors"][0]["path"] = "source-event.json"
    files[CORPUS / "official-validator-manifest.json"] = encoded(manifest)
    files[CORPUS / "event-lock.json"] = encoded({
        "baseSourceRevision": "444e06fb25680c3af29e5d3ccbebeb0249be7318", "releaseVersion": "0.6.0",
        "eventIdentity": source["identifier"], "sourceEventSHA256": hashlib.sha256(encoded(source).encode()).hexdigest(),
        "outputPointer": "/entry/2/resource",
        "protocols": {"a": {"url": "https://study.example.org/PlanDefinition/a", "version": "1"}, "b": {"url": "https://study.example.org/PlanDefinition/b", "version": "3"}},
        "exportLineage": {"a": "study-a-source-1", "b": "study-b-source-1"},
    })
    return files


def policy_negative_files():
    path = CORPUS / "negative-cases.json"
    manifest = load_manifest(path)
    cases = build_cases(manifest, load_bases(manifest, path))
    return {
        CORPUS / f"policy-negative-{case['id']}.json": encoded(cases[case["id"]])
        for case in manifest["cases"] if case["expectedRule"]["code"].startswith("receiver-study.")
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = generated_files()
    if args.check:
        changed = [path.name for path, value in files.items() if not path.is_file() or path.read_text() != value]
        if changed:
            raise SystemExit("Study fixtures differ: " + ", ".join(changed))
        policy_files = policy_negative_files()
        changed = [path.name for path, value in policy_files.items() if not path.is_file() or path.read_text() != value]
        if changed:
            raise SystemExit("Study policy fixtures differ: " + ", ".join(changed))
        print(f"Verified {len(files) + len(policy_files)} reproducible study-attribution files.")
        return
    for path, value in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    for path, value in policy_negative_files().items():
        path.write_text(value, encoding="utf-8")


if __name__ == "__main__":
    main()
