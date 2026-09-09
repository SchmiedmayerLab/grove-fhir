"""Build the small, synthetic receiver lifecycle corpus from the pinned exchange bases."""

# This source file is part of the Grove FHIR open-source project
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import hashlib
from itertools import permutations
import json
from pathlib import Path

from Scripts.exchange_protocol import derive_hmac_identity, entry_full_url, entry_node_identity, event_identity


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "Conformance/corpora/receiver-lifecycle"
BASE = ROOT / "Conformance/corpora/mobile-exchange"
PRODUCER = "1f5c58aa-6ec6-4e79-a682-829a9debd3f5"
MOBILE = "https://grovealliance.org/fhir/mobile/"
ROLES = MOBILE + "CodeSystem/grove-identifier-role"
VERSION = MOBILE + "StructureDefinition/grove-writer-record-version"
# Public synthetic fixture key; never a deployment secret.
KEY = bytes(range(32))


def encoded(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def opaque(kind, components):
    return derive_hmac_identity(key=KEY, key_id="test-key", epoch=1, identity_kind=kind, components=components)


def typed(role, value):
    return {
        "type": {"coding": [{"system": ROLES, "code": role}]},
        "system": f"https://study.example.org/fhir/NamingSystem/grove-{role}-v0/test-key/1",
        "value": value,
    }


def rewrite_references(value, replacements):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "reference" and isinstance(child, str) and child in replacements:
                value[key] = replacements[child]
            else:
                rewrite_references(child, replacements)
    elif isinstance(value, list):
        for child in value:
            rewrite_references(child, replacements)


def rekey(bundle, sequence):
    """Rebuild event-scoped identities; stable source-output identity is deliberately retained."""
    bundle["identifier"]["value"] = event_identity(PRODUCER, sequence)
    event = bundle["identifier"]
    replacements = {}
    ordinals = {}
    for entry in bundle["entry"]:
        key = entry["extension"][0]["valueIdentifier"]
        role = key["type"]["coding"][0]["code"]
        if role == "entry-node":
            node_role = key["value"].split(":")[1]
            ordinal = ordinals.get(node_role, 0)
            ordinals[node_role] = ordinal + 1
            key["value"] = entry_node_identity(
                event_system=event["system"], event_value=event["value"], role=node_role, ordinal=ordinal
            )
        elif role == "device-snapshot":
            key["value"] = opaque("device-snapshot", [event["system"], event["value"], "application", "fixture-app"])
            entry["resource"]["identifier"] = [copy.deepcopy(key)]
        elif role == "source-output":
            key.update(copy.deepcopy(next(
                item for item in entry["resource"]["identifier"]
                if item["type"]["coding"][0]["code"] == "source-output"
            )))
        previous = entry["fullUrl"]
        entry["fullUrl"] = entry_full_url(key["system"], key["value"])
        replacements[previous] = entry["fullUrl"]
    rewrite_references(bundle, replacements)
    return bundle


def observation(bundle):
    return next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Observation")


def active(sequence, writer_version=None, note=None):
    bundle = json.loads((BASE / "exchange-bundle.json").read_text())
    resource = observation(bundle)
    if writer_version is not None:
        resource["identifier"].append(typed("writer-record", opaque("writer-record", [
            "https://study.example.org/apps", "fixture-writer", "heart-rate-1"
        ])))
        resource["extension"].append({"url": VERSION, "valueString": writer_version})
    if note is not None:
        resource["note"] = [{"text": note}]
    return rekey(bundle, sequence)


def resources():
    original = active(42, "9007199254740992", "Original source wording.")
    corrected = active(41, "9007199254740993", "Corrected source wording.")
    # Source version, producer sequence and time must not be interchangeable ordering evidence.
    observation(corrected)["issued"] = "2026-08-19T17:30:02Z"
    altered = copy.deepcopy(original)
    observation(altered)["note"] = [{"text": "Different content under an already accepted event identity."}]
    pending = active(46)
    questionnaire = next(entry for entry in pending["entry"] if entry["resource"]["resourceType"] == "QuestionnaireResponse")
    observation(pending)["derivedFrom"] = [{
        "type": "QuestionnaireResponse", "identifier": copy.deepcopy(questionnaire["resource"]["identifier"])
    }]
    pending["entry"].remove(questionnaire)
    target = active(47)
    source = typed("source-record", opaque("source-record", [
        "questionnaire", "heart-rate", "https://study.example.org/repositories", "fixture", "record-2"
    ]))
    output = typed("source-output", opaque("source-output", [
        "questionnaire", "heart-rate", "https://study.example.org/repositories", "fixture", "record-2", "primary", "0"
    ]))
    observation(target)["identifier"] = [source, output]
    provenance = next(entry["resource"] for entry in target["entry"] if entry["resource"]["resourceType"] == "Provenance")
    provenance["entity"][0]["what"]["identifier"] = copy.deepcopy(source)
    rekey(target, 47)
    return {
        "original": original, "corrected": corrected, "altered-retry": altered,
        "unordered-a": active(44, note="First source wording without writer ordering evidence."),
        "unordered-b": active(45, note="Different wording without comparable writer ordering evidence."),
        "pending": pending, "target": target,
        "retraction": json.loads((BASE / "retraction-bundle.json").read_text()),
        **revision_resources(),
        "changed-source-record": changed_source_record(),
    }


def changed_source_record():
    """Profile-valid claim that contradicts another event's opaque output binding."""
    bundle = active(67, "9007199254740994")
    source = typed("source-record", opaque("source-record", [
        "health-connect", "HeartRateRecord", "urn:uuid:" + PRODUCER, "default", "another-record",
    ]))
    resource = observation(bundle)
    resource["identifier"] = [
        copy.deepcopy(source) if item["type"]["coding"][0]["code"] == "source-record" else item
        for item in resource["identifier"]
    ]
    provenance = next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")
    provenance["entity"][0]["what"]["identifier"] = copy.deepcopy(source)
    return bundle


def identity_sequences():
    """First committed binding wins; version ordering never moves an output between records."""
    sequences = []
    for first, rejected in (("multi-v2", "changed-source-record"), ("changed-source-record", "multi-v2")):
        state = {
            "history": [first], "bindingEvent": first, "current": [first],
            "grants": {"purpose-a": [first], "purpose-b": []}, "retractionEvents": [],
        }
        steps = []
        for event, disposition in ((first, "accepted"), (rejected, "rejected"), (first, "replayed"), (rejected, "rejected")):
            steps.append({"event": event, "expect": {
                **state, "disposition": disposition,
                "receiptEvent": first if disposition != "rejected" else None,
                "reason": "source-output-record-conflict" if disposition == "rejected" else None,
            }})
        sequences.append({"id": first + "-binds-output-first", "steps": steps})
    sequences.extend(retraction_binding_sequences())
    return {
        "schemaVersion": 0,
        "events": "events.json",
        "policy": {
            "scope": "One authenticated participant and verified source binding; the complete output Identifier includes system and value.",
            "binding": "The first committed active event or retraction assertion binds its source-output Identifier to the complete source-record Identifier. Subsequent active or retraction events cannot move that output to another record, even with a greater writer version.",
            "rejection": "A contradictory binding rejects the complete candidate event without receipt, custody, grants or changes to the accepted record. This is contextual admission failure, not an equal-version revision conflict or a standalone FHIR validation error.",
            "trust": "The receiver cannot reconstruct a producer's secret HMAC preimage. The first binding records the authenticated producer claim; it does not prove that claim is clinically correct. Corrected identity requires a new correctly derived output identity, not rebinding retained history.",
            "concurrency": "Serialize the binding and event transaction. Concurrent contradictory first claims may commit either one, but never both. Audit or transaction failure must not reserve a binding.",
            "authorization": "Accepted active events receive exact output grants for purpose-a; retractions receive no clinical grants. Purpose-b has no grants. A rejected event cannot change either purpose or retract the accepted output; a grant never overrides an accepted retraction.",
        },
        "sequences": sequences,
        "replayWholeSequence": {"repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []},
    }


def retraction_binding_sequences():
    """Explicit cross-kind expectations, not a receiver or version-selection algorithm."""
    def step(event, disposition, *, binding, history, current, grants, retractions):
        return {"event": event, "expect": {
            "history": history, "bindingEvent": binding, "current": current,
            "grants": {"purpose-a": grants, "purpose-b": []}, "retractionEvents": retractions,
            "disposition": disposition, "receiptEvent": None if disposition == "rejected" else event,
            "reason": "source-output-record-conflict" if disposition == "rejected" else None,
        }}

    retracted = dict(binding="retraction", history=["retraction"], current=[], grants=[], retractions=["retraction"])
    arrived = dict(retracted, history=["retraction", "multi-v2"], grants=["multi-v2"])
    claimed = dict(binding="changed-source-record", history=["changed-source-record"],
                   current=["changed-source-record"], grants=["changed-source-record"], retractions=[])
    return [
        {"id": "retraction-binds-before-active-claim", "steps": [
            step("retraction", "accepted", **retracted),
            step("changed-source-record", "rejected", **retracted),
            step("multi-v2", "accepted", **arrived),
            step("multi-v2", "replayed", **arrived),
            step("retraction", "replayed", **arrived),
            step("changed-source-record", "rejected", **arrived),
        ]},
        {"id": "active-binding-rejects-contradictory-retraction", "steps": [
            step("changed-source-record", "accepted", **claimed),
            step("retraction", "rejected", **claimed),
            step("changed-source-record", "replayed", **claimed),
            step("retraction", "rejected", **claimed),
        ]},
    ]


def revision_resources():
    """Complete source revisions; the removed child is not a permanent retraction."""
    def revision(sequence, version, include_secondary):
        bundle = active(sequence, version, "Primary reading from the synthetic source record.")
        if include_secondary:
            primary = next(entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Observation")
            secondary = copy.deepcopy(primary)
            output = typed("source-output", opaque("source-output", [
                "health-connect", "HeartRateRecord", "urn:uuid:" + PRODUCER, "default",
                "record-heart-001", "sample", "2026-08-20T15:30:01.251000000Z|0",
            ]))
            secondary["resource"]["id"] = "ReceiverSecondaryHeartRate"
            secondary["resource"]["identifier"] = [
                output if item["type"]["coding"][0]["code"] == "source-output" else item
                for item in secondary["resource"]["identifier"]
            ]
            secondary["resource"]["note"] = [{"text": "Secondary reading from the same source record."}]
            secondary["resource"]["effectiveDateTime"] = "2026-08-20T08:30:01.251-07:00"
            secondary["extension"][0]["valueIdentifier"] = copy.deepcopy(output)
            secondary["fullUrl"] = entry_full_url(output["system"], output["value"])
            bundle["entry"].append(secondary)
            provenance = next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")
            provenance["target"].append({"reference": secondary["fullUrl"]})
        return bundle

    first = revision(62, "9007199254740992", True)
    second = revision(61, "9007199254740993", False)
    third = revision(60, "9007199254740994", True)
    conflicting = copy.deepcopy(second)
    observation(conflicting)["note"] = [{"text": "Conflicting source content claiming the same writer version."}]
    reassembled = rekey(copy.deepcopy(second), 64)
    other_writer = revision(65, "9007199254740994", False)
    writer = next(item for item in observation(other_writer)["identifier"] if item["type"]["coding"][0]["code"] == "writer-record")
    writer["value"] = opaque("writer-record", ["https://study.example.org/apps", "another-writer", "heart-rate-1"])
    return {
        "multi-v1": first, "multi-v2": second, "multi-v3": third,
        "equal-version-conflict": rekey(conflicting, 63),
        "equal-version-reassembly": reassembled,
        "other-writer": other_writer,
        "missing-order": revision(66, None, False),
    }


def revision_sequences(bundles):
    """Declarative expected choices, not a receiver or a version-selection algorithm."""
    outputs = {}
    for event, bundle in bundles.items():
        for index, entry in enumerate(item for item in bundle["entry"] if item["resource"]["resourceType"] == "Observation"):
            alias = event + (".primary" if index == 0 else ".secondary")
            outputs[alias] = {"event": event, "fullUrl": entry["fullUrl"]}
    authorized = sorted(alias for alias in outputs if alias != "multi-v3.secondary")

    def sequence(name, deliveries):
        steps, previous_visible = [], set()
        for event, history, current, conflicts in deliveries:
            versions = sorted(alias for alias, output in outputs.items() if output["event"] in history)
            visible = sorted(set(current) & set(authorized))
            steps.append({"event": event, "expect": {
                "history": history, "versions": versions, "current": current, "conflicts": conflicts,
                "visible": visible, "newlyVisible": sorted(set(visible) - previous_visible),
            }})
            previous_visible = set(visible)
        return {"id": name, "steps": steps}

    first_outputs = ["multi-v1.primary", "multi-v1.secondary"]
    second_output = ["multi-v2.primary"]
    third_outputs = ["multi-v3.primary", "multi-v3.secondary"]
    sequences = [
        sequence("removed-child-does-not-remain-current", [
            ("multi-v1", ["multi-v1"], first_outputs, []),
            ("multi-v2", ["multi-v1", "multi-v2"], second_output, []),
            ("multi-v1", ["multi-v1", "multi-v2"], second_output, []),
        ]),
        sequence("late-old-revision-does-not-add-a-child", [
            ("multi-v2", ["multi-v2"], second_output, []),
            ("multi-v1", ["multi-v2", "multi-v1"], second_output, []),
        ]),
        sequence("membership-removal-is-not-a-tombstone-or-a-grant", [
            ("multi-v1", ["multi-v1"], first_outputs, []),
            ("multi-v2", ["multi-v1", "multi-v2"], second_output, []),
            ("multi-v3", ["multi-v1", "multi-v2", "multi-v3"], third_outputs, []),
        ]),
    ]
    for candidate in ("equal-version-conflict", "equal-version-reassembly", "other-writer", "missing-order"):
        sequences.append(sequence(candidate + "-requires-resolution", [
            ("multi-v2", ["multi-v2"], second_output, []),
            (candidate, ["multi-v2", candidate], [], ["multi-v2", candidate]),
            ("multi-v2", ["multi-v2", candidate], [], ["multi-v2", candidate]),
        ]))
        sequences.append(sequence(candidate + "-arrives-first", [
            (candidate, [candidate], [candidate + ".primary"], []),
            ("multi-v2", [candidate, "multi-v2"], [], [candidate, "multi-v2"]),
            (candidate, [candidate, "multi-v2"], [], [candidate, "multi-v2"]),
        ]))
        # Explicit states for the seven possible accepted subsets. Permuting the
        # deliveries tests arrival independence without embedding a receiver here.
        comparable = candidate in ("equal-version-conflict", "equal-version-reassembly")
        declared_states = {
            frozenset(["multi-v2"]): (second_output, []),
            frozenset([candidate]): ([candidate + ".primary"], []),
            frozenset(["multi-v3"]): (third_outputs, []),
            frozenset(["multi-v2", candidate]): ([], ["multi-v2", candidate]),
            frozenset(["multi-v2", "multi-v3"]): (third_outputs, []),
            frozenset([candidate, "multi-v3"]): (
                (third_outputs, []) if comparable else ([], [candidate, "multi-v3"])
            ),
            frozenset(["multi-v2", candidate, "multi-v3"]): (
                (third_outputs, ["multi-v2", candidate]) if comparable
                else ([], ["multi-v2", candidate, "multi-v3"])
            ),
        }
        labels = {"older": "multi-v2", "competing": candidate, "newer": "multi-v3"}
        for order in permutations(labels):
            history, deliveries = [], []
            for label in order:
                event = labels[label]
                history.append(event)
                current, conflicts = declared_states[frozenset(history)]
                deliveries.append((event, list(history), current, conflicts))
            # Replaying every participant must preserve final selection and conflict
            # evidence; a replay never makes a formerly authorized old version current.
            for event in history:
                deliveries.append((event, list(history), current, conflicts))
            sequences.append(sequence(candidate + "-with-higher-revision-" + "-".join(order), deliveries))
    return {
        "schemaVersion": 0,
        "events": "events.json",
        "outputs": outputs,
        "policy": {
            "scope": "One verified participant/source repository and the same complete source-record identity.",
            "membership": "Comparable writer versions select one complete source-record revision, including its output membership, not a maximum independently for each output.",
            "equivalence": "Exact event replay is proven equality. This receiver policy does not infer cross-event source-content equality by stripping graph fields. Distinct events with equal writer versions remain unresolved, even when displayed measurements agree.",
            "ordering": "Different writer identities or absent comparable writer evidence cannot order candidates. A missing output in a later complete revision is not a retraction tombstone.",
            "supersession": "A unique higher complete revision under the same writer identity can become current while equal-version conflicts among older revisions remain in history. A higher version cannot resolve missing or different writer evidence. Conflict evidence is not erased when current selection advances.",
            "authorization": "Only the listed exact output versions are authorized. Current selection never carries a previous version's grant forward.",
        },
        "authorizedOutputs": {"purpose-a": authorized, "purpose-b": []},
        "sequences": sequences,
        "replayWholeSequence": {"repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []},
    }


def generated_files():
    bundles = resources()
    files = {CORPUS / "resources" / f"{name}.json": encoded(bundle) for name, bundle in bundles.items()}
    manifest = json.loads((BASE / "official-validator-manifest.json").read_text())
    manifest["producer"]["name"] = "Grove FHIR receiver lifecycle fixtures"
    manifest["resources"] = [
        {"path": f"resources/{name}.json", "requiredProfiles": bundle["meta"]["profile"]}
        for name, bundle in bundles.items()
    ]
    manifest["semanticVectors"][0]["path"] = "resources/original.json"
    files[CORPUS / "official-validator-manifest.json"] = encoded(manifest)
    files[CORPUS / "events.json"] = encoded({
        "schemaVersion": 0,
        "contractLock": {
            "baseSourceRevision": "444e06fb25680c3af29e5d3ccbebeb0249be7318",
            "baseExchangeProtocolSHA256": "bbc9e980c2c674d5ef6f9900958d29c5602031ead8a3b6325cff508799106bb5",
            "releaseVersion": "0.6.0", "fhirVersion": "4.0.1",
            "exchangeProtocolSHA256": hashlib.sha256((ROOT / "catalog/exchange-protocol.json").read_bytes()).hexdigest(),
        },
        "events": {
            name: {
                "path": f"resources/{name}.json",
                "sha256": hashlib.sha256(encoded(bundle).encode()).hexdigest(),
                "eventIdentity": bundle["identifier"],
            }
            for name, bundle in bundles.items()
        },
    })
    files[CORPUS / "revision-sequences.json"] = encoded(revision_sequences(revision_resources()))
    files[CORPUS / "identity-sequences.json"] = encoded(identity_sequences())
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = generated_files()
    differences = [path for path, value in files.items() if not path.is_file() or path.read_text() != value]
    if args.check:
        if differences:
            raise SystemExit("Receiver fixtures differ: " + ", ".join(path.name for path in differences))
        print(f"Verified {len(files)} reproducible receiver fixture and manifest files.")
        return
    for path, value in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")


if __name__ == "__main__":
    main()
