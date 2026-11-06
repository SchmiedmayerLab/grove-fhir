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

from Scripts.exchange_fixtures import (
    encoded, entry_key, plain, read_lossless, rekey, rewrite_references, role_of,
)
from Scripts.exchange_protocol import RECORD_VERSION_EXTENSION
from Scripts.fhir_fixture_corpus import build_cases


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Conformance/corpora/mobile-exchange"
CORPUS = ROOT / "Conformance/corpora/study-attribution"
MOBILE = "https://grovealliance.org/fhir/mobile/"
STUDY_EXTENSION = "http://hl7.org/fhir/StructureDefinition/workflow-researchStudy"
ROLE_SYSTEM = MOBILE + "CodeSystem/grove-identifier-role"
PARTICIPANT = "https://study.example.org/fhir/identifiers/participant"
# The IG revision the record-centric bases were cut from.
BASE_SOURCE_REVISION = "be0e370cbc9e789f5ad30df18d3332713387a9c3"
RELEASE_VERSION = "0.8.0"
OUTPUT_POINTER = "/entry/2/resource"


def source_graph(include_second_study=False):
    """One record with study A's context, or with both studies' contexts, as shared nodes."""
    bundle = read_lossless(BASE / "exchange-bundle.json")
    bundle["id"] = "GroveMultiStudySourceExample" if not include_second_study else "GroveTwoStudySourceExample"
    # The base's record-heart-001 record and its shared nodes; its second record is dropped.
    bundle["entry"] = bundle["entry"][:5]
    patient = bundle["entry"][0]["fullUrl"]
    observation = bundle["entry"][2]["resource"]

    def append(resource, placeholder):
        # rekey mints the context-snapshot key and fullUrl once the node's content is final.
        bundle["entry"].append({"fullUrl": placeholder, "resource": resource})
        return placeholder

    studies = (("a", "1"), ("b", "3")) if include_second_study else (("a", "1"),)
    for study, revision in studies:
        plan = append({
            "resourceType": "PlanDefinition", "id": f"plan-{study}-r{revision}",
            "url": f"https://study.example.org/PlanDefinition/{study}",
            "version": revision, "status": "active", "title": f"Study {study.upper()} Protocol",
        }, f"plan-{study}")
        research_study = append({
            "resourceType": "ResearchStudy", "id": f"study-{study}-r{revision}",
            "identifier": [{"system": "https://study.example.org/studies", "value": study}],
            "status": "active", "title": f"Study {study.upper()}", "protocol": [{"reference": plan}],
        }, f"study-{study}")
        append({
            "resourceType": "ResearchSubject", "id": f"enrollment-{study}",
            "identifier": [{"system": "https://study.example.org/enrollments", "value": f"enrollment-{study}"}],
            "status": "on-study", "study": {"reference": research_study}, "individual": {"reference": patient},
        }, f"enrollment-{study}")
        observation["extension"].append({"url": STUDY_EXTENSION, "valueReference": {"reference": research_study}})
    return rekey(bundle)


def without_grove_identifiers(resource):
    """Drop the producer's typed Grove keys from a node a receiver repository holds itself."""
    identifiers = [item for item in resource.get("identifier", []) if role_of(item) is None]
    if identifiers:
        resource["identifier"] = identifiers
    else:
        resource.pop("identifier", None)
    return resource


def repository_b():
    entries = [copy.deepcopy(entry) for entry in source_graph(True)["entry"] if
        entry["resource"]["id"].startswith(("plan-b-", "study-b-", "enrollment-b"))
    ]
    replacements = {}
    for entry in entries:
        entry.pop("extension")
        resource = without_grove_identifiers(entry["resource"])
        previous = entry["fullUrl"]
        entry["fullUrl"] = f"https://receiver.example.org/{resource['resourceType']}/{resource['id']}"
        replacements[previous] = entry["fullUrl"]
        if resource["resourceType"] == "ResearchSubject":
            resource["individual"] = {"type": "Patient", "identifier": {
                "system": PARTICIPANT, "value": "participant-001"
            }}
    rewrite_references(entries, replacements)
    return {"resourceType": "Bundle", "type": "collection", "id": "StudyBRepositoryExample", "entry": entries}


def export_graph(source, study):
    """Create a fixed example of an already-authorized export; not an access-control function."""
    export = copy.deepcopy(source)
    export["id"] = f"GroveStudy{study.upper()}DerivedExportExample"
    export.pop("meta")  # A derived repository collection is not a Mobile exchange Bundle.
    export["identifier"] = {"system": "https://receiver.example.org/exports", "value": f"study-{study}-export-1"}
    export["timestamp"] = "2026-08-22T10:00:00Z"
    if study == "b":
        # Fixture input supplied by the receiver, not retroactively inserted into the source record.
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


def record_version(bundle):
    return entry_key(next(entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"))


def negative_cases(source, export):
    """One mutation per case; a receiver-study case stays structurally and profile valid."""
    # Another enrollment subject under a correctly rekeyed ResearchSubject: the kit accepts it, so
    # only the receiver's verified-subject check can refuse it.
    mismatch = copy.deepcopy(source)
    subject_entry = mismatch["entry"][7]
    subject_entry["resource"]["individual"] = {"type": "Patient", "identifier": {"system": PARTICIPANT, "value": "participant-002"}}
    rekey(mismatch)
    export_provenance = len(export["entry"]) - 1
    return {
        "schemaVersion": 0,
        "version": RELEASE_VERSION,
        "bases": [
            {"id": "source-event", "path": "source-event.json"},
            {"id": "export-a", "path": "export-a.json"},
        ],
        "cases": [
            {
                "id": "subject-mismatch",
                "base": "source-event",
                "patch": [{"op": "replace", "path": "/entry/7", "value": mismatch["entry"][7]}],
                "expectedRule": {"code": "receiver-study.subject-mismatch", "reason": "Study enrollment subject differs from the verified source subject."},
            },
            {
                "id": "protocol-is-not-a-reference",
                "base": "source-event",
                "patch": [{"op": "replace", "path": "/entry/6/resource/protocol/0", "value": "https://study.example.org/PlanDefinition/a|1"}],
                "expectedRule": {"code": "mobile-exchange.reference-shape", "reason": "ResearchStudy.protocol requires a Reference, not a canonical string."},
            },
            {
                "id": "lost-historical-revision",
                "base": "export-a",
                "patch": [{"op": "replace", "path": "/entry/4/resource/version", "value": "2"}],
                "expectedRule": {"code": "receiver-study.historical-revision", "reason": "The export's protocol differs from the immutable revision authorized by its grant."},
            },
            {
                "id": "derived-export-as-record-retry",
                "base": "export-a",
                "patch": [{"op": "add", "path": f"/entry/{export_provenance}/resource/extension", "value": [
                    {"url": RECORD_VERSION_EXTENSION, "valueIdentifier": record_version(source)},
                ]}],
                "expectedRule": {"code": "receiver-study.not-exact-replay", "reason": "A filtered export cannot reuse the immutable source record version for different bytes."},
            },
        ],
    }


def generated_files():
    source = source_graph()
    files = {CORPUS / "source-event.json": encoded(source)}
    files[CORPUS / "context-two-studies.json"] = encoded(source_graph(True))
    files[CORPUS / "repository-b.json"] = encoded(repository_b())
    exports = {study: export_graph(source, study) for study in ("a", "b")}
    for study, export in exports.items():
        files[CORPUS / f"export-{study}.json"] = encoded(export)
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
    manifest["producer"]["name"] = "Grove FHIR multi-study source fixture"
    manifest["resources"] = [
        {"path": path, "requiredProfiles": plain(source)["meta"]["profile"]}
        for path in ("source-event.json", "context-two-studies.json")
    ]
    manifest["semanticVectors"][0]["path"] = "source-event.json"
    files[CORPUS / "official-validator-manifest.json"] = encoded(manifest)
    files[CORPUS / "event-lock.json"] = encoded({
        "baseSourceRevision": BASE_SOURCE_REVISION, "releaseVersion": RELEASE_VERSION,
        "recordVersions": [record_version(source)],
        "sourceEventSHA256": hashlib.sha256(encoded(source).encode()).hexdigest(),
        "outputPointer": OUTPUT_POINTER,
        "protocols": {"a": {"url": "https://study.example.org/PlanDefinition/a", "version": "1"}, "b": {"url": "https://study.example.org/PlanDefinition/b", "version": "3"}},
        "exportLineage": {"a": "study-a-source-1", "b": "study-b-source-1"},
    })
    files[CORPUS / "negative-cases.json"] = encoded(negative_cases(source, exports["a"]))
    return files


def policy_negative_files(files=None):
    """Materialize every receiver-study case, which stays a valid FHIR resource."""
    files = generated_files() if files is None else files
    path = CORPUS / "negative-cases.json"
    manifest = json.loads(files[path])
    bases = {
        base["id"]: json.loads(files[CORPUS / base["path"]]) for base in manifest["bases"]
    }
    cases = build_cases(manifest, bases)
    return {
        CORPUS / f"policy-negative-{case['id']}.json": encoded(cases[case["id"]])
        for case in manifest["cases"] if case["expectedRule"]["code"].startswith("receiver-study.")
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = generated_files()
    policy_files = policy_negative_files(files)
    if args.check:
        changed = [path.name for path, value in {**files, **policy_files}.items() if not path.is_file() or path.read_text() != value]
        if changed:
            raise SystemExit("Study fixtures differ: " + ", ".join(changed))
        print(f"Verified {len(files) + len(policy_files)} reproducible study-attribution files.")
        return
    for path, value in {**files, **policy_files}.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")


if __name__ == "__main__":
    main()
