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

from Scripts.canonical_json import JSONNumber
from Scripts.exchange_fixtures import (
    KEY, encoded, entry_key, plain, read_lossless, rekey, typed_identifier,
)
from Scripts.exchange_protocol import derive_hmac_identity, entry_full_url


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "Conformance/corpora/receiver-lifecycle"
BASE = ROOT / "Conformance/corpora/mobile-exchange"
PRODUCER = "1f5c58aa-6ec6-4e79-a682-829a9debd3f5"
MOBILE = "https://grovealliance.org/fhir/mobile/"
ROLES = MOBILE + "CodeSystem/grove-identifier-role"
VERSION = MOBILE + "StructureDefinition/grove-writer-record-version"
WRITER = ["https://study.example.org/apps", "fixture-writer", "heart-rate-1"]
OTHER_WRITER = ["https://study.example.org/apps", "another-writer", "heart-rate-1"]
# The IG revision the record-centric bases were cut from, and its exchange protocol.
BASE_SOURCE_REVISION = "be0e370cbc9e789f5ad30df18d3332713387a9c3"
BASE_EXCHANGE_PROTOCOL_SHA256 = "fec45c4aaa7c9b63b2db25cfb0b82088a61f061ef404cbb17073025649072768"
RELEASE_VERSION = "0.8.0"
PRIMARY_NOTE = "Primary reading from the synthetic source record."
OTHER_NOTE = "Other source content claiming the same writer version."
REVISION_CANDIDATES = (
    "equal-version-later-recorded",
    "equal-version-reconversion",
    "equal-version-equal-recorded",
    "other-writer",
    "missing-order",
)


def opaque(kind, components):
    return derive_hmac_identity(key=KEY, key_id="test-key", epoch=1, identity_kind=kind, components=components)


def typed(role, value):
    return typed_identifier(role, value)


def observation(bundle):
    return next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Observation")


def conversion(bundle):
    return next(entry["resource"] for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance")


def local(recorded):
    """Return a UTC instant as the Pacific daylight wall-clock time Provenance.occurred states."""
    date, time = recorded[:-1].split("T")
    return f"{date}T{int(time[:2]) - 7:02d}{time[2:]}-07:00"


def stamp(bundle, recorded):
    """Set the conversion instant: Provenance.recorded, and occurred at the same instant."""
    provenance = conversion(bundle)
    provenance["occurredDateTime"] = local(recorded)
    provenance["recorded"] = recorded


def base_record():
    """The base's record-heart-001 record and its shared nodes; its second record is dropped."""
    bundle = read_lossless(BASE / "exchange-bundle.json")
    bundle["entry"] = bundle["entry"][:5]
    return bundle


def active(recorded, writer_version=None, note=None, writer=WRITER):
    bundle = base_record()
    resource = observation(bundle)
    if writer_version is not None:
        resource["identifier"].append(typed("writer-record", opaque("writer-record", writer)))
        resource["extension"].append({"url": VERSION, "valueString": writer_version})
    if note is not None:
        resource["note"] = [{"text": note}]
    stamp(bundle, recorded)
    return rekey(bundle)


def reidentified(bundle, source, output=None):
    """Attribute a record to another source record; its conversion Provenance follows it."""
    def replacement(item):
        role = item["type"]["coding"][0]["code"]
        if role == "source-record":
            return copy.deepcopy(source)
        if role == "source-output" and output is not None:
            return copy.deepcopy(output)
        return item

    resource = observation(bundle)
    resource["identifier"] = [replacement(item) for item in resource["identifier"]]
    conversion(bundle)["entity"][0]["what"]["identifier"] = copy.deepcopy(source)
    return rekey(bundle)


def lossless_resources():
    original = active("2026-08-20T17:30:02Z", "9007199254740992", "Original source wording.")
    # Writer evidence orders versions: corrected carries the higher writer version and the earlier
    # conversion instant, so a receiver that orders by recorded alone selects the wrong version.
    corrected = active("2026-08-20T17:30:01Z", "9007199254740993", "Corrected source wording.")
    # Other tokens under original's record-version key: an altered retry, deliberately not rekeyed.
    altered = copy.deepcopy(original)
    observation(altered)["note"] = [{"text": "Different content under an already accepted record version."}]
    # Same tokens in another member order: the exact retry, although the bytes differ.
    reformatted = dict(reversed(list(copy.deepcopy(original).items())))
    for entry in reformatted["entry"]:
        if entry["resource"]["resourceType"] == "Observation":
            entry["resource"] = dict(reversed(list(entry["resource"].items())))
    # 72.0 is a different decimal lexeme from 72: different content, so a new record version.
    lexeme = copy.deepcopy(original)
    observation(lexeme)["valueQuantity"]["value"] = JSONNumber("72.0")
    rekey(lexeme)
    # The same source content converted again later: a new version with a later recorded instant.
    reconverted = copy.deepcopy(original)
    stamp(reconverted, "2026-08-20T17:31:02Z")
    rekey(reconverted)
    pending = active("2026-08-20T17:30:02Z")
    questionnaire = next(entry for entry in pending["entry"] if entry["resource"]["resourceType"] == "QuestionnaireResponse")
    observation(pending)["derivedFrom"] = [{
        "type": "QuestionnaireResponse", "identifier": copy.deepcopy(questionnaire["resource"]["identifier"])
    }]
    pending["entry"].remove(questionnaire)
    rekey(pending)
    target = reidentified(
        active("2026-08-20T17:30:02Z"),
        typed("source-record", opaque("source-record", [
            "questionnaire", "heart-rate", "https://study.example.org/repositories", "fixture", "record-2"
        ])),
        typed("source-output", opaque("source-output", [
            "questionnaire", "heart-rate", "https://study.example.org/repositories", "fixture", "record-2", "primary", "0"
        ])),
    )
    changed = changed_source_record()
    return {
        "original": original, "corrected": corrected, "altered-retry": altered,
        "reformatted-retry": reformatted, "lexeme-retry": lexeme, "reconverted": reconverted,
        "unordered-a": active("2026-08-20T17:30:05Z", note="First source wording without writer ordering evidence."),
        "unordered-b": active("2026-08-20T17:30:04Z", note="Different wording without comparable writer ordering evidence."),
        "pending": pending, "target": target,
        "retraction": read_lossless(BASE / "retraction-bundle.json"),
        "source-record-target-retraction": read_lossless(BASE / "source-record-target-retraction-bundle.json"),
        **lossless_revision_resources(),
        "changed-source-record": changed,
        "mixed-admission": mixed_admission(changed, target),
    }


def resources():
    """Every fixture Bundle as json.loads reads its committed file."""
    return {name: plain(bundle) for name, bundle in lossless_resources().items()}


def changed_source_record():
    """Profile-valid claim that contradicts another record's opaque output binding."""
    return reidentified(
        active("2026-08-20T17:30:02Z", "9007199254740994"),
        typed("source-record", opaque("source-record", [
            "health-connect", "HeartRateRecord", "urn:uuid:" + PRODUCER, "default", "another-record",
        ])),
    )


def mixed_admission(changed, target):
    """The changed-source-record and target records in one Bundle, sharing their nodes."""
    bundle = copy.deepcopy(changed)
    shared = {entry["fullUrl"] for entry in bundle["entry"]}
    bundle["entry"].extend(copy.deepcopy(entry) for entry in target["entry"] if entry["fullUrl"] not in shared)
    return rekey(bundle)


def identity_sequences():
    """First accepted active binding wins; version ordering never moves an output between records."""
    sequences = []
    for first, rejected in (("multi-v2", "changed-source-record"), ("changed-source-record", "multi-v2")):
        state = {
            "history": [first], "bindingBundle": first, "current": [first],
            "grants": {"purpose-a": [first], "purpose-b": []}, "retractionBundles": [],
        }
        steps = []
        for bundle, disposition in ((first, "accepted"), (rejected, "rejected"), (first, "replayed"), (rejected, "rejected")):
            steps.append({"bundle": bundle, "expect": {
                **state, "disposition": disposition,
                "rejectedRecords": [rejected] if disposition == "rejected" else [],
                "receiptBundle": first if disposition != "rejected" else None,
                "reason": "source-output-record-conflict" if disposition == "rejected" else None,
            }})
        sequences.append({"id": first + "-binds-output-first", "steps": steps})
    sequences.append(mixed_admission_sequence())
    sequences.extend(retraction_binding_sequences())
    return {
        "schemaVersion": 0,
        "bundles": "bundles.json",
        "policy": {
            "scope": "One authenticated participant and verified source binding; the complete output Identifier includes system and value.",
            "binding": "The first accepted active record version binds its source-output Identifiers to its complete source-record Identifier. A retraction binds nothing: it addresses its whole source record, and its targets are informative. No later record version can move a bound output to another record, even with a greater writer version.",
            "rejection": "Admission is per record. A record whose output contradicts a binding is rejected alone, without receipt, custody, grants or changes to the accepted record, and the other records of its Bundle are admitted. This is contextual admission failure, not a version-selection outcome or a standalone FHIR validation error.",
            "trust": "The receiver cannot reconstruct a producer's secret HMAC preimage. The first binding records the authenticated producer claim; it does not prove that claim is clinically correct. Corrected identity requires a new correctly derived output identity, not rebinding retained history.",
            "concurrency": "Serialize the binding and record transaction. Concurrent contradictory first claims may commit either one, but never both. Audit or transaction failure must not reserve a binding.",
            "authorization": "Accepted active record versions receive exact output grants for purpose-a; retractions receive no clinical grants. Purpose-b has no grants. A rejected record cannot change either purpose or retract the accepted output; a grant never overrides an accepted retraction.",
            "arrays": "history, bindingBundle, current, grants, retractionBundles and receiptBundle name Bundle aliases; an alias in current or grants names its Bundle's one output, and mixed-admission.target names the output of mixed-admission's target record. rejectedRecords names the records a delivery rejected, by the alias of the Bundle that carries each one alone.",
        },
        "sequences": sequences,
        "replayWholeSequence": {"repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []},
    }


def mixed_admission_sequence():
    """A contradictory record is rejected alone; the other record of its Bundle is admitted."""
    def step(bundle, disposition, history, current, rejected):
        return {"bundle": bundle, "expect": {
            "history": history, "bindingBundle": "multi-v2", "current": current,
            "grants": {"purpose-a": current, "purpose-b": []}, "retractionBundles": [],
            "disposition": disposition, "rejectedRecords": rejected,
            "receiptBundle": bundle, "reason": "source-output-record-conflict" if rejected else None,
        }}

    both = ["multi-v2", "mixed-admission"]
    admitted = ["multi-v2", "mixed-admission.target"]
    return {"id": "mixed-admission-rejects-only-the-contradictory-record", "steps": [
        step("multi-v2", "accepted", ["multi-v2"], ["multi-v2"], []),
        step("mixed-admission", "partially-accepted", both, admitted, ["changed-source-record"]),
        step("multi-v2", "replayed", both, admitted, []),
        step("mixed-admission", "partially-replayed", both, admitted, ["changed-source-record"]),
    ]}


def retraction_binding_sequences():
    """Explicit cross-kind expectations, not a receiver or version-selection algorithm."""
    def step(bundle, disposition, *, binding, history, current, grants, retractions):
        return {"bundle": bundle, "expect": {
            "history": history, "bindingBundle": binding, "current": current,
            "grants": {"purpose-a": grants, "purpose-b": []}, "retractionBundles": retractions,
            "disposition": disposition, "rejectedRecords": [bundle] if disposition == "rejected" else [],
            "receiptBundle": None if disposition == "rejected" else bundle,
            "reason": "source-output-record-conflict" if disposition == "rejected" else None,
        }}

    retracted = dict(binding=None, history=["retraction"], current=[], grants=[], retractions=["retraction"])
    claimed_after = dict(
        binding="changed-source-record", history=["retraction", "changed-source-record"],
        current=["changed-source-record"], grants=["changed-source-record"], retractions=["retraction"],
    )
    claimed = dict(
        binding="changed-source-record", history=["changed-source-record"],
        current=["changed-source-record"], grants=["changed-source-record"], retractions=[],
    )
    claimed_then_retracted = dict(claimed, history=["changed-source-record", "retraction"], retractions=["retraction"])
    return [
        # The retraction addresses record-heart-001 and binds nothing, so changed-source-record
        # binds the shared output to another-record and multi-v2's later claim is rejected.
        {"id": "typed-retraction-binds-no-output", "steps": [
            step("retraction", "accepted", **retracted),
            step("changed-source-record", "accepted", **claimed_after),
            step("multi-v2", "rejected", **claimed_after),
            step("retraction", "replayed", **claimed_after),
            step("changed-source-record", "replayed", **claimed_after),
            step("multi-v2", "rejected", **claimed_after),
        ]},
        # The retraction is accepted and suppresses record-heart-001, which holds nothing current.
        {"id": "retraction-after-contradictory-claim", "steps": [
            step("changed-source-record", "accepted", **claimed),
            step("retraction", "accepted", **claimed_then_retracted),
            step("changed-source-record", "replayed", **claimed_then_retracted),
            step("retraction", "replayed", **claimed_then_retracted),
        ]},
    ]


def source_record_target_retraction_sequences(bundles):
    """Explicit retraction expectations, not a receiver or a selection algorithm."""
    # An output is any node the conversion Provenance targets, whatever its resource type.
    outputs = {}
    for bundle in ("multi-v1", "multi-v2", "multi-v3", "target", "changed-source-record"):
        for index, target in enumerate(conversion(bundles[bundle])["target"]):
            outputs[bundle + (".primary" if index == 0 else ".secondary")] = {"bundle": bundle, "fullUrl": target["reference"]}

    def source(provenance):
        identifier = provenance["entity"][0]["what"]["identifier"]
        return {"system": identifier["system"], "value": identifier["value"]}

    retractions = [
        entry["resource"] for entry in bundles["retraction"]["entry"]
        if entry["resource"]["resourceType"] == "Provenance"
    ]

    def sequence(name, deliveries):
        steps, history, previous_visible = [], [], set()
        for bundle, disposition, current, retracted in deliveries:
            if disposition == "accepted":
                history.append(bundle)
            # Every output version is authorized for purpose-a, so visibility is current selection.
            visible = sorted(current)
            steps.append({"bundle": bundle, "expect": {
                "history": list(history),
                "versions": sorted(alias for alias, output in outputs.items() if output["bundle"] in history),
                "current": visible, "retractedRecords": retracted,
                "visible": visible, "newlyVisible": sorted(set(visible) - previous_visible),
                "disposition": disposition, "receiptBundle": None if disposition == "rejected" else bundle,
                "reason": "source-output-record-conflict" if disposition == "rejected" else None,
            }})
            previous_visible = set(visible)
        return {"id": name, "steps": steps}

    retraction = "source-record-target-retraction"
    heart = ["record-heart-001", "record-heart-002"]
    claimed = ["changed-source-record.primary"]
    whole = ["multi-v3.primary", "multi-v3.secondary"]
    return {
        "schemaVersion": 0,
        "bundles": "bundles.json",
        "records": {
            "record-heart-001": source(conversion(bundles["multi-v1"])),
            "record-heart-002": source(retractions[1]),
            "record-2": source(conversion(bundles["target"])),
            "another-record": source(conversion(bundles["changed-source-record"])),
        },
        "outputs": outputs,
        "policy": {
            "scope": "One verified participant and source repository. A record alias names the complete source-record Identifier, system and value, of a conversion or retraction Provenance source entity. Both retraction Bundles retract record-heart-001 and record-heart-002; no version of record-heart-002 arrives here.",
            "addressing": "A retraction addresses its whole source record: every output of every accepted record version whose conversion Provenance source entity is that complete source-record Identifier, whether the version is accepted before or after the retraction. Its targets are informative, a typed output target and a source-record target alike. A retraction that addresses no accepted record version yet is still accepted and applies to later versions.",
            "selection": "An addressed output never becomes current, and a record is never un-retracted, while every accepted record version and output version stays in history. Outputs of every other source record are unaffected.",
            "binding": "A retraction binds no output to its record, whatever its targets name. The first accepted active record version still binds each of its outputs; a later version that claims a bound output under another record is rejected as source-output-record-conflict, and a rejected record is never addressed.",
            "authorization": "Every output version is authorized for purpose-a, so visibility follows current selection and a grant never overrides an accepted retraction. Purpose-b has no grants, and replay creates no new access.",
        },
        "authorizedOutputs": {"purpose-a": sorted(outputs), "purpose-b": []},
        "sequences": [
            sequence("source-record-target-retraction-after-its-record", [
                ("multi-v1", "accepted", ["multi-v1.primary", "multi-v1.secondary"], []),
                (retraction, "accepted", [], heart),
                ("multi-v1", "replayed", [], heart),
                (retraction, "replayed", [], heart),
            ]),
            sequence("source-record-target-retraction-before-any-version", [
                (retraction, "accepted", [], heart),
                ("multi-v1", "accepted", [], heart),
                ("multi-v3", "accepted", [], heart),
            ]),
            sequence("source-record-target-retraction-leaves-other-records-current", [
                ("target", "accepted", ["target.primary"], []),
                (retraction, "accepted", ["target.primary"], heart),
                ("multi-v2", "accepted", ["target.primary"], heart),
            ]),
            # As in identity-sequences.json's typed-retraction-binds-no-output, no retraction binds.
            sequence("source-record-target-retraction-binds-no-output", [
                (retraction, "accepted", [], heart),
                ("changed-source-record", "accepted", claimed, heart),
                ("multi-v2", "rejected", claimed, heart),
                (retraction, "replayed", claimed, heart),
            ]),
            # The typed retraction names only the primary output, yet suppresses the whole record:
            # multi-v3.secondary, which it does not name, and a version that arrives after it.
            sequence("typed-retraction-suppresses-whole-record", [
                ("multi-v3", "accepted", whole, []),
                ("retraction", "accepted", [], heart),
                ("multi-v1", "accepted", [], heart),
                ("retraction", "replayed", [], heart),
            ]),
            # The other arrival order: multi-v3.secondary arrives after the typed retraction and
            # never becomes current.
            sequence("typed-retraction-suppresses-whole-record-before-its-version", [
                ("retraction", "accepted", [], heart),
                ("multi-v3", "accepted", [], heart),
                ("multi-v3", "replayed", [], heart),
                ("retraction", "replayed", [], heart),
            ]),
        ],
        "replayWholeSequence": {"repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []},
    }


def lossless_revision_resources():
    """Complete source revisions; the removed child is not a permanent retraction."""
    def revision(recorded, version, include_secondary, note=PRIMARY_NOTE, writer=WRITER):
        bundle = active(recorded, version, note, writer)
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
            secondary["fullUrl"] = entry_full_url(output["system"], output["value"])
            bundle["entry"].append(secondary)
            conversion(bundle)["target"].append({"reference": secondary["fullUrl"]})
        return rekey(bundle)

    # Writer evidence orders multi-v1 < multi-v2 < multi-v3, against their recorded instants.
    return {
        "multi-v1": revision("2026-08-20T17:30:09Z", "9007199254740992", True),
        "multi-v2": revision("2026-08-20T17:30:08Z", "9007199254740993", False),
        "multi-v3": revision("2026-08-20T17:30:07Z", "9007199254740994", True),
        "equal-version-later-recorded": revision("2026-08-20T17:30:10Z", "9007199254740993", False, OTHER_NOTE),
        "equal-version-reconversion": revision("2026-08-20T17:30:11Z", "9007199254740993", False),
        # The same instant as multi-v2 in another lexeme: only the tie-break orders the two.
        "equal-version-equal-recorded": revision("2026-08-20T17:30:08.000Z", "9007199254740993", False, OTHER_NOTE),
        "other-writer": revision("2026-08-20T17:30:06Z", "9007199254740994", False, writer=OTHER_WRITER),
        "missing-order": revision("2026-08-20T17:30:07.500Z", None, False),
    }


def revision_resources():
    """Every revision fixture Bundle as json.loads reads its committed file."""
    return {name: plain(bundle) for name, bundle in lossless_revision_resources().items()}


def record_version(bundle):
    return entry_key(next(entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"))


def bytewise_greater(first, second):
    """Return the alias of the (alias, Bundle) version that versionSelection.tieBreak selects."""
    def order(version):
        key = record_version(version[1])
        return key["value"].encode("utf-8"), key["system"].encode("utf-8")

    return first[0] if order(first) > order(second) else second[0]


def revision_sequences(bundles):
    """Declarative expected choices, not a receiver or a version-selection algorithm."""
    outputs = {}
    for bundle_name, bundle in bundles.items():
        for index, entry in enumerate(item for item in bundle["entry"] if item["resource"]["resourceType"] == "Observation"):
            alias = bundle_name + (".primary" if index == 0 else ".secondary")
            outputs[alias] = {"bundle": bundle_name, "fullUrl": entry["fullUrl"]}
    authorized = sorted(alias for alias in outputs if alias != "multi-v3.secondary")
    members = {
        bundle_name: sorted(alias for alias, output in outputs.items() if output["bundle"] == bundle_name)
        for bundle_name in bundles
    }

    def sequence(name, deliveries):
        steps, previous_visible = [], set()
        for bundle_name, history, selected in deliveries:
            versions = sorted(alias for alias, output in outputs.items() if output["bundle"] in history)
            current = members[selected]
            visible = sorted(set(current) & set(authorized))
            steps.append({"bundle": bundle_name, "expect": {
                "history": history, "versions": versions, "current": current,
                "visible": visible, "newlyVisible": sorted(set(visible) - previous_visible),
            }})
            previous_visible = set(visible)
        return {"id": name, "steps": steps}

    sequences = [
        sequence("removed-child-does-not-remain-current", [
            ("multi-v1", ["multi-v1"], "multi-v1"),
            ("multi-v2", ["multi-v1", "multi-v2"], "multi-v2"),
            ("multi-v1", ["multi-v1", "multi-v2"], "multi-v2"),
        ]),
        sequence("late-old-revision-does-not-add-a-child", [
            ("multi-v2", ["multi-v2"], "multi-v2"),
            ("multi-v1", ["multi-v2", "multi-v1"], "multi-v2"),
        ]),
        sequence("membership-removal-is-not-a-tombstone-or-a-grant", [
            ("multi-v1", ["multi-v1"], "multi-v1"),
            ("multi-v2", ["multi-v1", "multi-v2"], "multi-v2"),
            ("multi-v3", ["multi-v1", "multi-v2", "multi-v3"], "multi-v3"),
        ]),
    ]
    # The declared current version of each accepted set. Writer evidence decides first (multi-v3
    # drops every lower version of writer W; other-writer is another writer and missing-order has
    # none), then the later recorded instant. The tie-break is the only computed choice.
    after_older = {
        "equal-version-later-recorded": "equal-version-later-recorded",
        "equal-version-reconversion": "equal-version-reconversion",
        "equal-version-equal-recorded": bytewise_greater(
            ("multi-v2", bundles["multi-v2"]),
            ("equal-version-equal-recorded", bundles["equal-version-equal-recorded"]),
        ),
        "other-writer": "multi-v2",
        "missing-order": "multi-v2",
    }
    # The set rule: multi-v3 drops multi-v2, and missing-order, without writer evidence, is later.
    with_newer = {candidate: "multi-v3" for candidate in REVISION_CANDIDATES}
    with_newer["missing-order"] = "missing-order"
    for candidate in REVISION_CANDIDATES:
        declared_states = {
            frozenset(["multi-v2"]): "multi-v2",
            frozenset([candidate]): candidate,
            frozenset(["multi-v3"]): "multi-v3",
            frozenset(["multi-v2", candidate]): after_older[candidate],
            frozenset(["multi-v2", "multi-v3"]): "multi-v3",
            frozenset([candidate, "multi-v3"]): with_newer[candidate],
            frozenset(["multi-v2", candidate, "multi-v3"]): with_newer[candidate],
        }
        sequences.append(sequence(candidate + "-after-older", [
            ("multi-v2", ["multi-v2"], "multi-v2"),
            (candidate, ["multi-v2", candidate], after_older[candidate]),
            ("multi-v2", ["multi-v2", candidate], after_older[candidate]),
        ]))
        sequences.append(sequence(candidate + "-before-older", [
            (candidate, [candidate], candidate),
            ("multi-v2", [candidate, "multi-v2"], after_older[candidate]),
            (candidate, [candidate, "multi-v2"], after_older[candidate]),
        ]))
        # Explicit states for the seven possible accepted subsets. Permuting the
        # deliveries tests arrival independence without embedding a receiver here.
        labels = {"older": "multi-v2", "candidate": candidate, "newer": "multi-v3"}
        for order in permutations(labels):
            history, deliveries = [], []
            for label in order:
                bundle_name = labels[label]
                history.append(bundle_name)
                deliveries.append((bundle_name, list(history), declared_states[frozenset(history)]))
            # Replaying every version preserves the final selection; a replay never makes a
            # formerly authorized old version current.
            for bundle_name in list(history):
                deliveries.append((bundle_name, list(history), declared_states[frozenset(history)]))
            sequences.append(sequence(candidate + "-with-newer-revision-" + "-".join(order), deliveries))
    return {
        "schemaVersion": 0,
        "bundles": "bundles.json",
        "outputs": outputs,
        "recordVersions": {name: record_version(bundle) for name, bundle in bundles.items()},
        "policy": {
            "scope": "One verified participant/source repository and the same complete source-record identity.",
            "membership": "The selected record version's targets are the record's current outputs, its output membership included; selection is never a maximum taken independently for each output. An output missing from a later version is not a retraction tombstone.",
            "selection": "lifecycle.active.versionSelection: drop every version that another version beats with a greater writer version under the same complete writer-record pair; of the rest, select the latest Provenance.recorded as an exact instant; equal instants select the bytewise-greater record-version Identifier value, then system. A different writer identity or absent writer evidence leaves the order to recorded.",
            "equivalence": "The same record-version Identifier with the same lossless tokens is an exact retry. Any other content, the same source content converted again included, is a distinct version. This receiver policy never infers source-content equality across versions by stripping graph fields.",
            "history": "Every accepted version stays in history; advancing the current selection never removes one.",
            "authorization": "Only the listed exact output versions are authorized. Current selection never carries a previous version's grant forward.",
        },
        "authorizedOutputs": {"purpose-a": authorized, "purpose-b": []},
        "sequences": sequences,
        "replayWholeSequence": {"repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []},
    }


def lifecycle_sequences(bundles):
    """The receiver lifecycle expectations; only the lexeme tie-break is computed."""
    lexeme_winner = bytewise_greater(("original", bundles["original"]), ("lexeme-retry", bundles["lexeme-retry"]))

    def sequence(name, deliveries):
        steps, history, previous_visible = [], [], set()
        for bundle, current, *rest in deliveries:
            options = rest[0] if rest else {}
            if options.get("accepted", True) and bundle not in history:
                history.append(bundle)
            pending = options.get("pending", [])
            visible = sorted(set(current) - set(pending))
            step = {"bundle": bundle}
            if "transport" in options:
                step["transport"] = options["transport"]
            step["expect"] = {
                "history": list(history),
                "versions": [alias for alias in history if alias != "retraction"],
                "current": sorted(current),
                "pending": pending,
                "retracted": ["original"] if "retraction" in history else [],
                "visible": visible,
                "newlyVisible": sorted(set(visible) - previous_visible),
                "references": options.get("references", {}),
            }
            steps.append(step)
            previous_visible = set(visible)
        return {"id": name, "steps": steps}

    restored = {"transport": "restored-transport"}
    retry = {"accepted": False}
    return {
        "schemaVersion": 0,
        "bundles": "bundles.json",
        "policy": {
            "visiblePurpose": "purpose-a",
            "deniedPurposes": ["purpose-b"],
            "scope": "One verified participant and source repository; transport restoration preserves that scope.",
            "order": "lifecycle.active.versionSelection: comparable writer versions under the same complete writer-record Identifier pair decide first; otherwise the later Provenance.recorded instant; equal instants select the bytewise-greater record-version Identifier. Neither arrival nor Bundle.timestamp orders versions.",
            "retraction": "lifecycle.active.versionSelection.retraction: the tombstone covers the whole source record, every output of every version accepted before or after it, and replay never removes it. A record is never un-retracted.",
            "references": "An unresolved logical clinical reference keeps the referring output pending and undisclosed. A later target must match its complete Identifier and verified subject/source scope.",
            "authorization": "The harness independently authorizes purpose-a for the named output versions only; purpose-b has no authorization. Profile validity and graph readiness never create authorization.",
            "arrays": "State arrays are sets of Bundle aliases. Versions/current/visible aliases select the Observation in the named Bundle. A retracted alias names an output of a retracted source record and suppresses every output of every version of that source record, not only versions sharing its source-output Identifier. history includes retractions; versions does not. newlyVisible is the access newly made available at this step, not an HTTP receipt code.",
        },
        "replayWholeSequence": {"repeat": 1, "restartBeforeReplay": True, "preserveFinalState": True, "newlyVisible": []},
        "logicalReferences": {
            "questionnaire": {
                "sourceBundle": "pending",
                "referencePointer": "/entry/2/resource/derivedFrom/0",
                "targetBundle": "target",
                "targetPointer": "/entry/4/resource",
            }
        },
        "sequences": [
            # The altered retry repeats original's record-version key with other tokens: disregarded.
            sequence("exact-and-conflicting-replay", [
                ("original", ["original"]), ("original", ["original"]), ("altered-retry", ["original"], retry),
            ]),
            sequence("reformatted-replay", [
                ("original", ["original"]), ("reformatted-retry", ["original"], retry),
            ]),
            sequence("lexeme-version-after-original", [
                ("original", ["original"]), ("lexeme-retry", [lexeme_winner]),
            ]),
            sequence("lexeme-version-before-original", [
                ("lexeme-retry", ["lexeme-retry"]), ("original", [lexeme_winner]),
            ]),
            sequence("correction-before-original", [
                ("corrected", ["corrected"]), ("original", ["corrected"]), ("corrected", ["corrected"]),
            ]),
            sequence("original-before-correction", [
                ("original", ["original"]), ("corrected", ["corrected"]),
            ]),
            sequence("unordered-later-recorded-first", [
                ("unordered-a", ["unordered-a"]), ("unordered-b", ["unordered-a"]), ("unordered-a", ["unordered-a"]),
            ]),
            sequence("unordered-later-recorded-last", [
                ("unordered-b", ["unordered-b"]), ("unordered-a", ["unordered-a"]), ("unordered-b", ["unordered-a"]),
            ]),
            sequence("reconversion-after-original", [
                ("original", ["original"]), ("reconverted", ["reconverted"]),
            ]),
            sequence("reconversion-before-original", [
                ("reconverted", ["reconverted"]), ("original", ["reconverted"]),
            ]),
            sequence("pending-reference-resolution", [
                ("pending", ["pending"], {"pending": ["pending"], "references": {"questionnaire": "pending"}}),
                ("target", ["pending", "target"], {"references": {"questionnaire": "resolved"}}),
            ]),
            sequence("retraction-before-target", [
                ("retraction", []), ("original", []), ("retraction", []), ("original", [], restored),
            ]),
            sequence("retraction-after-target", [
                ("original", ["original"]), ("retraction", []), ("original", []),
            ]),
            sequence("correction-before-retraction", [
                ("corrected", ["corrected"]), ("retraction", []), ("original", []), ("corrected", [], restored),
            ]),
            sequence("retraction-before-correction", [
                ("retraction", []), ("corrected", []), ("original", []), ("corrected", [], restored),
            ]),
        ],
    }


def generated_files():
    bundles = lossless_resources()
    files = {CORPUS / "resources" / f"{name}.json": encoded(bundle) for name, bundle in bundles.items()}
    manifest = json.loads((BASE / "official-validator-manifest.json").read_text())
    manifest["producer"]["name"] = "Grove FHIR receiver lifecycle fixtures"
    # The altered retry is FHIR-valid, but its record-version key no longer recomputes under the
    # test key, so the structural kit refuses it and it stays out of this producer manifest.
    manifest["resources"] = [
        {"path": f"resources/{name}.json", "requiredProfiles": bundle["meta"]["profile"]}
        for name, bundle in bundles.items() if name != "altered-retry"
    ]
    manifest["semanticVectors"][0]["path"] = "resources/original.json"
    files[CORPUS / "official-validator-manifest.json"] = encoded(manifest)
    files[CORPUS / "bundles.json"] = encoded({
        "schemaVersion": 0,
        "contractLock": {
            "baseSourceRevision": BASE_SOURCE_REVISION,
            "baseExchangeProtocolSHA256": BASE_EXCHANGE_PROTOCOL_SHA256,
            "releaseVersion": RELEASE_VERSION, "fhirVersion": "4.0.1",
            "exchangeProtocolSHA256": hashlib.sha256((ROOT / "catalog/exchange-protocol.json").read_bytes()).hexdigest(),
        },
        "bundles": {
            name: {
                "path": f"resources/{name}.json",
                "sha256": hashlib.sha256(encoded(bundle).encode()).hexdigest(),
                "recordVersions": [
                    entry_key(entry) for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"
                ],
            }
            for name, bundle in bundles.items()
        },
    })
    files[CORPUS / "sequences.json"] = encoded(lifecycle_sequences(bundles))
    files[CORPUS / "revision-sequences.json"] = encoded(revision_sequences(lossless_revision_resources()))
    files[CORPUS / "identity-sequences.json"] = encoded(identity_sequences())
    files[CORPUS / "source-record-target-retraction-sequences.json"] = encoded(source_record_target_retraction_sequences(bundles))
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
