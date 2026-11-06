"""Catalog-backed constants shared by producer-validation domains."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    from Scripts.exchange_protocol import (
        HMAC_IDENTITY,
        ExchangeProtocolError,
        content_digest,
        context_snapshot_identity,
        device_snapshot_identity,
        entry_full_url,
        parse_hmac_identity,
        record_content_digest,
        record_retraction_identity,
        record_version_identity,
        require_absolute_uri,
    )
except ModuleNotFoundError:  # Direct `python Scripts/validate-producer.py` execution.
    from exchange_protocol import (  # type: ignore[no-redef]
        HMAC_IDENTITY,
        ExchangeProtocolError,
        content_digest,
        context_snapshot_identity,
        device_snapshot_identity,
        entry_full_url,
        parse_hmac_identity,
        record_content_digest,
        record_retraction_identity,
        record_version_identity,
        require_absolute_uri,
    )

PACKAGE_ALIAS = re.compile(r"^[a-z][a-z0-9-]*$")
PACKAGE_ID = re.compile(r"^[a-z0-9.-]+$")
FHIR_ID = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")
GROVE_PROFILE = "https://grovealliance.org/fhir/"
EXCHANGE_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle"
)
RETRACTION_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-retraction-bundle"
)
IDENTIFIER_ROLE_SYSTEM = (
    "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role"
)
LIFECYCLE_EVENT_SYSTEM = (
    "https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event"
)
RETRACTION_TARGET_ROLE_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role"
)
SOURCE_RECORD_RETRACTED = "source-record-retracted"
SOURCE_RECORD_TARGET_ROLE = "source-record"
VALIDATOR_FILE_EXTENSION = "http://hl7.org/fhir/StructureDefinition/operationoutcome-file"
VALIDATOR_ATTEMPTS = 2
VALIDATOR_LOG_LIMIT = 4000
VALIDATOR_TIMEOUT_SECONDS = 180
TOP_LEVEL_KEYS = {
    "schemaVersion",
    "fhirVersion",
    "producer",
    "packages",
    "resources",
    "semanticVectors",
}
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG_ROOT = REPOSITORY_ROOT / "catalog"
# The seeding scripts all write to ${GROVE_FHIR_HOME_OVERRIDE:-.build/fhir-home}; reading the
# same variable here keeps one configuration value with one home.
FHIR_TOOL_HOME = Path(
    os.environ.get("GROVE_FHIR_HOME_OVERRIDE") or REPOSITORY_ROOT / ".build" / "fhir-home"
)
EXCHANGE_PROTOCOL = json.loads(
    (CATALOG_ROOT / "exchange-protocol.json").read_text(encoding="utf-8")
)
WRITER_RECORD_VERSION_EXTENSION = EXCHANGE_PROTOCOL["extensions"]["writerRecordVersion"]
ENTRY_IDENTIFIER_EXTENSION = EXCHANGE_PROTOCOL["extensions"]["entryKey"]
RECORD_VERSION_EXTENSION = EXCHANGE_PROTOCOL["extensions"]["recordVersion"]
CONTEXT_SNAPSHOT_EXTENSION = EXCHANGE_PROTOCOL["extensions"]["contextSnapshot"]
RETRACTION_NATIVE_RECORD_IDENTIFIER_EXTENSION = EXCHANGE_PROTOCOL["extensions"][
    "retractionTargetNativeIdentifier"
]
RETRACTION_NATIVE_RECORD_IDENTIFIER = EXCHANGE_PROTOCOL["lifecycle"]["retraction"][
    "nativeRecordIdentifier"
]
ACTIVE_ENTRY_POLICY = EXCHANGE_PROTOCOL["lifecycle"]["active"]["entryResourcePolicy"]
ACTIVE_OUTPUT_RESOURCE_TYPES = frozenset(ACTIVE_ENTRY_POLICY["outputResourceTypes"])
ACTIVE_SUPPORTING_RESOURCE_TYPES = frozenset(
    ACTIVE_ENTRY_POLICY["supportingResourceTypes"]
)
ACTIVE_ENTRY_RESOURCE_TYPES = frozenset(
    {
        *ACTIVE_OUTPUT_RESOURCE_TYPES,
        *ACTIVE_SUPPORTING_RESOURCE_TYPES,
        ACTIVE_ENTRY_POLICY["lifecycleResourceType"],
    }
)
RETRACTION_TARGET_CONTRACTS = EXCHANGE_PROTOCOL["lifecycle"]["retraction"][
    "targetRoles"
]
RETRACTION_TARGET_ROLES = frozenset(RETRACTION_TARGET_CONTRACTS)
REFERENCE_POLICY = EXCHANGE_PROTOCOL["referencePolicy"]
IDENTIFIER_PRIORITY = tuple(
    EXCHANGE_PROTOCOL["entryIdentity"]["resourceIdentifierPriority"]
)
# A Provenance has no R4 identifier, so its entry key is its record version (active) or its
# record-retraction key (retraction); a QuestionnaireResponse's one identifier holds its
# submission identifier, so its entry key is its context snapshot.
PROVENANCE_KEY_ROLES = EXCHANGE_PROTOCOL["entryIdentity"]["provenanceKey"]
CONTEXT_SNAPSHOT_ROLES = tuple(EXCHANGE_PROTOCOL["entryIdentity"]["contextSnapshotRoles"])
CONTEXT_NODE_ROLES = {
    "Patient": "patient",
    "ResearchStudy": "research-study",
    "ResearchSubject": "research-subject",
    "PlanDefinition": "plan-definition",
    "QuestionnaireResponse": "questionnaire-response",
}
if set(CONTEXT_NODE_ROLES.values()) != set(CONTEXT_SNAPSHOT_ROLES):
    raise RuntimeError("the context-snapshot node roles must match entryIdentity.contextSnapshotRoles")
TEST_VECTORS = EXCHANGE_PROTOCOL["testVectors"]
# The published test key. Keys minted under it are recomputed; every other key is checked for
# shape only, because a receiver never holds a deployment's key.
TEST_KEY = bytes.fromhex(TEST_VECTORS["keyHex"])
TEST_KEY_ID = TEST_VECTORS["keyId"]
OPAQUE_IDENTIFIER_ROLES = frozenset(
    identity["identifierRole"]
    for identity in EXCHANGE_PROTOCOL["opaqueIdentity"]["identityKinds"]
)
PROFILE_CLAIMS = json.loads(
    (CATALOG_ROOT / "profile-claims.json").read_text(encoding="utf-8")
)
_DEVICE_CLAIM_ROLES = {
    "-application-device": "application",
    "-host-device": "host",
    "-recording-device": "recording-device",
}
# The device-snapshot node role of each admitted Device profile, which the claim id names.
DEVICE_NODE_ROLES: dict[str, str] = {}
for _claim in PROFILE_CLAIMS["activeDeviceClaims"]:
    _roles = [role for suffix, role in _DEVICE_CLAIM_ROLES.items() if _claim["id"].endswith(suffix)]
    if len(_roles) != 1 or len(_claim["profiles"]) != 1:
        raise RuntimeError(f"Device claim {_claim['id']} names no device-snapshot node role")
    DEVICE_NODE_ROLES[_claim["profiles"][0]] = _roles[0]
RELEASE_VERSION = json.loads(
    (CATALOG_ROOT / "package-graph.json").read_text(encoding="utf-8")
)["version"]
PACKAGE_GRAPH = json.loads(
    (CATALOG_ROOT / "package-graph.json").read_text(encoding="utf-8")
)
MEASUREMENT_CATALOG = json.loads(
    (CATALOG_ROOT / "measurement-catalog.json").read_text(encoding="utf-8")
)
MEASUREMENT_BY_PROFILE = {
    f"https://grovealliance.org/fhir/{entry.get('owner', 'mobile')}"
    f"/StructureDefinition/{entry['profile']}": entry
    for entry in MEASUREMENT_CATALOG["measurements"]
}
NON_ADAPTER_SOURCES = {"mobile", "questionnaire", "sensor"}
ADAPTER_PACKAGE_PROFILES = {
    package["packageId"]: {
        f"{package['canonical']}/StructureDefinition/{profile}"
        for profile in package["profiles"]
    }
    for package in PACKAGE_GRAPH["packages"]
    if package["source"] not in NON_ADAPTER_SOURCES
}
KNOWN_ADAPTER_PROFILES = {
    profile
    for package_profiles in ADAPTER_PACKAGE_PROFILES.values()
    for profile in package_profiles
}
SENSOR_SAMPLED_PROFILE = (
    "https://grovealliance.org/fhir/sensor/StructureDefinition/"
    "grove-sensor-sampled-data-observation"
)
SENSOR_ECG_PROFILE = (
    "https://grovealliance.org/fhir/sensor/StructureDefinition/"
    "grove-sensor-ecg-observation"
)
SENSOR_RECORDING_PROFILE = (
    "https://grovealliance.org/fhir/sensor/StructureDefinition/"
    "grove-sensor-recording-document"
)
HEALTHKIT_PROFILE_PREFIX = (
    "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
)
HEALTHKIT_OBSERVATION_PROFILE = HEALTHKIT_PROFILE_PREFIX + "healthkit-observation"
HEALTHKIT_RECORDING_PROFILE = HEALTHKIT_PROFILE_PREFIX + "healthkit-recording-document"
HEALTHKIT_CLINICAL_RECORD_PROFILE = (
    HEALTHKIT_PROFILE_PREFIX + "healthkit-clinical-record-document"
)
HEALTHKIT_ECG_PROFILE = HEALTHKIT_PROFILE_PREFIX + "healthkit-ecg-observation"
HEALTHKIT_ECG_AVERAGE_HEART_RATE_PROFILE = (
    HEALTHKIT_PROFILE_PREFIX + "healthkit-ecg-average-heart-rate-observation"
)
SAMPLED_DATA_SEPARATOR = " "
_SAMPLED_DECIMAL = r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
# The same sequence the sensor-inline-data-1 invariant states: exactly one space between
# values. Folding runs of whitespace here would admit output the official Validator rejects.
SAMPLED_DATA_SEQUENCE = re.compile(
    rf"^{_SAMPLED_DECIMAL}(?:{SAMPLED_DATA_SEPARATOR}{_SAMPLED_DECIMAL})*$"
)
FHIR_INSTANT = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?P<offset>Z|[+-][0-9]{2}:[0-9]{2})$"
)
