"""Shared fixtures for producer-validation domain regressions."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest import mock

from Scripts import fhir_fixture_corpus as CORPUS
from Scripts.canonical_json import CanonicalJSONError, JSONNumber, canonical_bytes, loads_lossless
from Scripts.exchange_protocol import (
    CONTEXT_SNAPSHOT_EXTENSION,
    ExchangeProtocolError,
    IDENTIFIER_ROLE_SYSTEM,
    RECORD_VERSION_EXTENSION,
    content_digest,
    context_snapshot_identity,
    derive_hmac_identity,
    device_snapshot_identity,
    entry_full_url,
    record_content_digest,
    record_outputs,
    record_retraction_identity,
    record_version_identity,
)
from Scripts.producer_validation import context


ROOT = Path(__file__).parents[1]
ENTRY_KEY_EXTENSION = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key"
# The public conformance key of testVectors; never a deployment secret.
TEST_KEY = bytes(range(32))


class NoSubject(ValueError):
    """A Bundle that states no subject, such as a retraction Bundle, cannot key its snapshots."""


# A malformed node keeps its key, so the defect a negative case plants is the one reported.
UNKEYABLE = (KeyError, IndexError, TypeError, StopIteration, NoSubject, ExchangeProtocolError, CanonicalJSONError)
DEVICE_NODE_ROLES = {
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-application-device": "application",
    "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-application-device": "application",
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-host-device": "host",
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-recording-device": "recording-device",
}
CONTEXT_NODE_ROLES = {
    "Patient": "patient",
    "ResearchStudy": "research-study",
    "ResearchSubject": "research-subject",
    "PlanDefinition": "plan-definition",
    "QuestionnaireResponse": "questionnaire-response",
}


def typed_identifier(role: str, system: str, value: str) -> dict[str, object]:
    return {
        "type": {"coding": [{
            "system": context.IDENTIFIER_ROLE_SYSTEM,
            "code": role,
        }]},
        "system": system,
        "value": value,
    }


def lossless(tree: Any) -> Any:
    """Return a lossless copy of a `json.loads` tree, every number written as its lexeme."""
    if isinstance(tree, dict):
        return {name: lossless(value) for name, value in tree.items()}
    if isinstance(tree, list):
        return [lossless(value) for value in tree]
    if isinstance(tree, (str, bool)) or tree is None:
        return tree
    if isinstance(tree, int):
        return JSONNumber(str(tree))
    if isinstance(tree, float):
        return JSONNumber(repr(tree))
    if isinstance(tree, Decimal):
        return JSONNumber(str(tree))
    raise TypeError(f"{type(tree).__name__} is no JSON value")


def identifier_role(identifier: Any) -> str | None:
    codings = identifier.get("type", {}).get("coding", []) if isinstance(identifier, dict) else []
    return next(
        (coding.get("code") for coding in codings if coding.get("system") == IDENTIFIER_ROLE_SYSTEM),
        None,
    )


def entry_key(entry: dict[str, Any]) -> dict[str, Any]:
    return next(item["valueIdentifier"] for item in entry["extension"] if item["url"] == ENTRY_KEY_EXTENSION)


def _snapshot_key(bundle: dict[str, Any], entry: dict[str, Any], common: dict[str, Any], subject: Any) -> str | None:
    resource, role = entry["resource"], identifier_role(entry_key(entry))
    if role not in ("device-snapshot", "context-snapshot"):
        return None
    subject_system, subject_value = subject or bundle_subject(bundle)
    if role == "device-snapshot":
        node_role = next(
            DEVICE_NODE_ROLES[profile] for profile in resource["meta"]["profile"] if profile in DEVICE_NODE_ROLES
        )
        return device_snapshot_identity(
            **common, subject_system=subject_system, subject_value=subject_value,
            node_role=node_role, content_digest=content_digest(lossless(resource)),
        )
    return context_snapshot_identity(
        **common, subject_system=subject_system, subject_value=subject_value,
        node_role=CONTEXT_NODE_ROLES[resource["resourceType"]],
        content_digest=content_digest(lossless(resource)),
    )


def _record_key(bundle: dict[str, Any], entry: dict[str, Any], common: dict[str, Any]) -> str:
    resource = entry["resource"]
    source = resource["entity"][0]["what"]["identifier"]
    if identifier_role(entry_key(entry)) == "record-retraction":
        return record_retraction_identity(
            **common, source_record_system=source["system"], source_record_value=source["value"]
        )
    snapshot = lossless(bundle)
    provenance = next(item["resource"] for item in snapshot["entry"] if item.get("fullUrl") == entry["fullUrl"])
    return record_version_identity(
        **common, source_record_system=source["system"], source_record_value=source["value"],
        record_content_digest=record_content_digest(provenance, record_outputs(snapshot, provenance)),
    )


def provenances(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Provenance"]


def bundle_subject(bundle: dict[str, Any]) -> tuple[str, str]:
    """Return the one subject pair the records of a Bundle state, as the snapshot kinds take it.

    A Patient entry names it through its one identifier without a Grove role. A Patient with
    several has no pseudonym to take, so a test that builds one passes `subject` to rekey_records
    rather than letting this pick one.
    """
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource["resourceType"] == "Patient":
            plain = [
                identifier for identifier in resource.get("identifier", [])
                if identifier_role(identifier) is None
            ]
            if len(plain) != 1:
                raise NoSubject(f"the Patient states {len(plain)} identifiers without a Grove role")
            return plain[0]["system"], plain[0]["value"]
    for entry in bundle["entry"]:
        subject = entry["resource"].get("subject")
        if isinstance(subject, dict) and isinstance(subject.get("identifier"), dict):
            return subject["identifier"]["system"], subject["identifier"]["value"]
    raise NoSubject("the Bundle states no subject")


def _rewrite_references(tree: Any, replacements: dict[str, str]) -> None:
    if isinstance(tree, dict):
        for name, value in tree.items():
            if name == "reference" and isinstance(value, str) and value in replacements:
                tree[name] = replacements[value]
            else:
                _rewrite_references(value, replacements)
    elif isinstance(tree, list):
        for value in tree:
            _rewrite_references(value, replacements)


def _set_extension(resource: dict[str, Any], url: str, identifier: dict[str, Any]) -> None:
    extensions = resource.setdefault("extension", [])
    matching = [item for item in extensions if item.get("url") == url]
    if matching:
        matching[0]["valueIdentifier"] = copy.deepcopy(identifier)
        for extra in matching[1:]:
            extensions.remove(extra)
    else:
        extensions.append({"url": url, "valueIdentifier": copy.deepcopy(identifier)})


def _move(bundle: dict[str, Any], entry: dict[str, Any], key: dict[str, Any], value: str) -> bool:
    if key["value"] == value:
        return False
    key["value"] = value
    previous, entry["fullUrl"] = entry["fullUrl"], entry_full_url(key["system"], value)
    _rewrite_references(bundle, {previous: entry["fullUrl"]})
    return True


def rekey_records(
    bundle: dict[str, Any],
    *,
    subject: tuple[str, str] | None = None,
    key: bytes = TEST_KEY,
    key_id: str = "test-key",
    epoch: int = 1,
) -> dict[str, Any]:
    """Recompute every content-snapshot and record key of `bundle` in place, under the test key.

    Shared nodes are rekeyed until no fullUrl moves, because a node's content includes the
    fullUrls it references (an application Device names its host). Then every conversion
    Provenance gets the record-version key over its record content, repeated in its
    grove-record-version extension, and every retraction Provenance its record-retraction key.
    Keys keep their type and system; only values, fullUrls and references change, and the
    caller's number types are kept. A conversion Provenance whose targets do not resolve keeps
    its key. Negative cases mutate the Bundle after this call.
    """
    common = {"key": key, "key_id": key_id, "epoch": epoch}
    entries = [entry for entry in bundle["entry"] if isinstance(entry, dict) and isinstance(entry.get("resource"), dict)]
    for _ in range(len(entries) + 1):
        moved = False
        for entry in entries:
            try:
                value = _snapshot_key(bundle, entry, common, subject)
            except UNKEYABLE:
                continue
            if value is None:
                continue
            resource, identifier = entry["resource"], entry_key(entry)
            moved = _move(bundle, entry, identifier, value) or moved
            if resource["resourceType"] == "QuestionnaireResponse":
                _set_extension(resource, CONTEXT_SNAPSHOT_EXTENSION, identifier)
            else:
                for typed in resource.get("identifier", []):
                    if identifier_role(typed) == identifier_role(identifier):
                        typed["value"] = identifier["value"]
        if not moved:
            break
    else:
        raise ValueError("shared-node references form a cycle")
    for entry in entries:
        if entry["resource"].get("resourceType") != "Provenance":
            continue
        try:
            value = _record_key(bundle, entry, common)
        except UNKEYABLE:
            continue
        identifier = entry_key(entry)
        _move(bundle, entry, identifier, value)
        if identifier_role(identifier) == "record-version":
            _set_extension(entry["resource"], RECORD_VERSION_EXTENSION, identifier)
    return bundle


STUDY_NAMING_SYSTEM = "https://study.example.org/fhir/NamingSystem"
MOBILE = "https://grovealliance.org/fhir/mobile/"
RETRACTION_TARGET_ROLE_EXTENSION = MOBILE + "StructureDefinition/grove-retraction-target-role"
EXCHANGE_BUNDLE_PROFILE = MOBILE + "StructureDefinition/grove-mobile-exchange-bundle"
RETRACTION_BUNDLE_PROFILE = MOBILE + "StructureDefinition/grove-mobile-retraction-bundle"
RETRACTION_PROVENANCE_PROFILE = MOBILE + "StructureDefinition/grove-mobile-retraction-provenance"
LIFECYCLE_EVENT_SYSTEM = MOBILE + "CodeSystem/grove-lifecycle-event"
ACTIVE_BASE = ROOT / "Conformance/corpora/mobile-exchange/exchange-bundle.json"


def key_system(kind: str) -> str:
    return f"{STUDY_NAMING_SYSTEM}/grove-{kind}-v0/test-key/1"


def test_identity(kind: str, components: list[str]) -> str:
    return derive_hmac_identity(key=TEST_KEY, key_id="test-key", epoch=1, identity_kind=kind, components=components)


def is_retraction_provenance(resource: dict[str, Any]) -> bool:
    return any(
        coding.get("system") == LIFECYCLE_EVENT_SYSTEM
        for coding in resource.get("activity", {}).get("coding", [])
    )


def active_base() -> dict[str, Any]:
    """The two-record mobile-exchange base, keyed under the test key."""
    return json.loads(ACTIVE_BASE.read_text(encoding="utf-8"))


def source_record_pair(native_record_id: str) -> tuple[dict[str, object], dict[str, object]]:
    """A synthetic Health Connect heart-rate source record and its one primary output."""
    components = [
        "health-connect", "HeartRateRecord", "urn:uuid:1f5c58aa-6ec6-4e79-a682-829a9debd3f5",
        "default", native_record_id,
    ]
    return (
        typed_identifier("source-record", key_system("source-record"), test_identity("source-record", components)),
        typed_identifier(
            "source-output", key_system("source-output"),
            test_identity("source-output", [*components, "primary", "0"]),
        ),
    )


def add_record(
    bundle: dict[str, Any],
    native_record_id: str,
    *,
    value: Any = 73,
    recorded: str = "2026-08-20T17:30:03Z",
) -> dict[str, Any]:
    """Append another record, copied from the Bundle's first and sharing its nodes, and rekey."""
    observation = next(entry for entry in bundle["entry"] if entry["resource"]["resourceType"] == "Observation")
    provenance = next(
        entry for entry in provenances(bundle) if not is_retraction_provenance(entry["resource"])
    )
    source, output = source_record_pair(native_record_id)
    new_observation, new_provenance = copy.deepcopy(observation), copy.deepcopy(provenance)
    resource = new_observation["resource"]
    resource["id"] = f"{resource.get('id', 'Observation')}-{native_record_id}"
    resource["identifier"] = [
        copy.deepcopy(source) if identifier_role(item) == "source-record"
        else copy.deepcopy(output) if identifier_role(item) == "source-output" else item
        for item in resource["identifier"]
    ]
    resource["valueQuantity"]["value"] = value
    key = entry_key(new_observation)
    key.clear()
    key.update(copy.deepcopy(output))
    new_observation["fullUrl"] = entry_full_url(output["system"], output["value"])
    record = new_provenance["resource"]
    record["id"] = f"{record.get('id', 'Provenance')}-{native_record_id}"
    record["entity"][0]["what"]["identifier"] = copy.deepcopy(source)
    record["target"] = [{"reference": new_observation["fullUrl"]}]
    record["recorded"] = recorded
    bundle["entry"].extend([new_observation, new_provenance])
    return rekey_records(bundle)


def literal_references(tree: Any) -> list[str]:
    if isinstance(tree, dict):
        found = [tree["reference"]] if isinstance(tree.get("reference"), str) else []
        return found + [item for value in tree.values() for item in literal_references(value)]
    if isinstance(tree, list):
        return [item for value in tree for item in literal_references(value)]
    return []


def record_unit(bundle: dict[str, Any], provenance: dict[str, Any]) -> set[str]:
    """The fullUrls of one record unit (H10): its Provenance, targets, and forward literal closure.

    A ResearchSubject joins every record whose closure contains the ResearchStudy it references.
    This is an independent reference of the catalog's bundle.recordUnit, not the validator's.
    """
    by_url = {entry["fullUrl"]: entry["resource"] for entry in bundle["entry"]}
    unit, pending = {provenance["fullUrl"]}, [provenance["resource"]]
    for target in provenance["resource"].get("target", []):
        if target.get("reference") in by_url:
            unit.add(target["reference"])
            pending.append(by_url[target["reference"]])
    while pending:
        for reference in literal_references(pending.pop()):
            if reference in by_url and reference not in unit:
                unit.add(reference)
                pending.append(by_url[reference])
    for url, resource in by_url.items():
        if resource["resourceType"] == "ResearchSubject" and set(literal_references(resource.get("study", {}))) & unit:
            unit.add(url)
    return unit


def single_record(bundle: dict[str, Any], index: int = 0) -> dict[str, Any]:
    """The Bundle cut down to the record unit of its `index`-th Provenance, keys unchanged."""
    unit = record_unit(bundle, provenances(bundle)[index])
    single = copy.deepcopy(bundle)
    single["entry"] = [entry for entry in single["entry"] if entry["fullUrl"] in unit]
    return single


def two_record_bundle() -> dict[str, Any]:
    """An active Bundle of at least two records that share their Patient, Device and QuestionnaireResponse."""
    bundle = active_base()
    if len(provenances(bundle)) >= 2:
        return bundle
    return add_record(bundle, "record-heart-002")


def retraction_bundle(active: dict[str, Any]) -> dict[str, Any]:
    """A retraction Bundle with one source-record retraction per record of `active`.

    Each retraction Provenance names its literal assembler, the shared application Device of the
    active Bundle, which the retraction Bundle carries once.
    """
    devices = [entry for entry in active["entry"] if entry["resource"]["resourceType"] == "Device"]
    entries = [copy.deepcopy(entry) for entry in devices]
    for index, conversion in enumerate(provenances(active)):
        resource = conversion["resource"]
        source = copy.deepcopy(resource["entity"][0]["what"]["identifier"])
        entries.append({
            "extension": [{
                "url": ENTRY_KEY_EXTENSION,
                "valueIdentifier": typed_identifier(
                    "record-retraction", key_system("record-retraction"), "v0:test-key:1:" + "A" * 43
                ),
            }],
            "fullUrl": f"urn:uuid:00000000-0000-5000-8000-{index:012d}",
            "resource": {
                "resourceType": "Provenance",
                "id": f"retraction-{index}",
                "meta": {"profile": [RETRACTION_PROVENANCE_PROFILE]},
                "activity": {"coding": [{"system": LIFECYCLE_EVENT_SYSTEM, "code": "source-record-retracted"}]},
                "agent": copy.deepcopy(resource["agent"]),
                "entity": [{"role": "source", "what": {"identifier": source}}],
                "target": [{
                    "extension": [{"url": RETRACTION_TARGET_ROLE_EXTENSION, "valueCode": "source-record"}],
                    "identifier": copy.deepcopy(source),
                }],
                "occurredDateTime": "2026-08-21T08:00:00Z",
                "recorded": "2026-08-21T08:00:01Z",
            },
        })
    # A retraction Bundle names no subject; its Device keeps the active Bundle's subject.
    return rekey_records({
        "resourceType": "Bundle",
        "meta": {"profile": [RETRACTION_BUNDLE_PROFILE]},
        "type": "collection",
        "timestamp": "2026-08-21T08:00:01Z",
        "entry": entries,
    }, subject=bundle_subject(active))


class ProducerValidationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.example = ROOT / "Conformance/example-producer/manifest.json"

    @staticmethod
    def outcome(path: Path, issues: list[dict[str, str]]) -> dict[str, object]:
        return {
            "resourceType": "OperationOutcome",
            "extension": [{
                "url": context.VALIDATOR_FILE_EXTENSION,
                "valueString": str(path),
            }],
            "issue": issues,
        }
