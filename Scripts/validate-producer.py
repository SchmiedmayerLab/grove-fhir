#!/usr/bin/env python3
"""Validate producer-emitted R4 resources without executing the producer."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from pathlib import Path, PurePosixPath
from typing import Any


PACKAGE_ALIAS = re.compile(r"^[a-z][a-z0-9-]*$")
PACKAGE_ID = re.compile(r"^[a-z0-9.-]+$")
GROVE_PROFILE = "https://grovealliance.org/fhir/"
EXCHANGE_BUNDLE_PROFILE = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-exchange-bundle"
)
ENTRY_IDENTIFIER_EXTENSION = (
    "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-identifier"
)
ENTRY_UUID_NAMESPACE = uuid.UUID("a9a39cf1-c944-5d15-a3c2-c395969ea101")
VALIDATOR_FILE_EXTENSION = (
    "http://hl7.org/fhir/StructureDefinition/operationoutcome-file"
)
VALIDATOR_ATTEMPTS = 2
VALIDATOR_LOG_LIMIT = 4000
TOP_LEVEL_KEYS = {
    "schemaVersion",
    "fhirVersion",
    "producer",
    "packages",
    "resources",
    "semanticVectors",
}
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = REPOSITORY_ROOT / "catalog"
FHIR_TOOL_HOME = REPOSITORY_ROOT / ".build" / "fhir-home"
ADAPTER_PACKAGE_PROFILES = {
    "org.grovealliance.fhir.sensorkit": {
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-accelerometer-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-conversion-provenance",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-device-usage-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-ecg-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-keyboard-metrics-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-messages-usage-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-on-wrist-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-phone-usage-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-ppg-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-recording-document",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-sleep-session-observation",
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-visit-observation",
    },
    "org.grovealliance.fhir.healthkit": {
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-apple-exercise-time",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-apple-move-time",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-apple-stand-hour",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-apple-stand-time",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-atrial-fibrillation-burden",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-bladder-incontinence",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-bleeding-after-pregnancy",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-bleeding-during-pregnancy",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-blood-alcohol-content",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-blood-type",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-clinical-record-document",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-contraceptive-use",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-conversion-provenance",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-cycling-functional-threshold-power",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-observation",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-environmental-audio-exposure",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-environmental-sound-reduction",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-forced-expiratory-volume-1",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-forced-vital-capacity",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-gad7-assessment",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-handwashing-session",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-headphone-audio-exposure",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-heart-rate-recovery-one-minute",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-inhaler-usage",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-insulin-delivery",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-lactation-status",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-number-of-alcoholic-beverages",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-number-of-times-fallen",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-observation",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-peak-expiratory-flow-rate",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-peripheral-perfusion-index",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-phq9-assessment",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-physical-effort",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-pregnancy-status",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-pregnancy-test-result",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-progesterone-test-result",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-running-ground-contact-time",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-running-stride-length",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-running-vertical-oscillation",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-six-minute-walk-test-distance",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-sleeping-breathing-disturbances",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-stair-ascent-speed",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-stair-descent-speed",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-swimming-stroke-count",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-abdominal-cramps",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-acne",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-appetite-changes",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-bloating",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-breast-pain",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-chest-tightness-or-pain",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-chills",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-constipation",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-coughing",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-diarrhea",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-dizziness",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-dry-skin",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-fainting",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-fatigue",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-fever",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-generalized-body-ache",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-hair-loss",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-headache",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-heartburn",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-hot-flashes",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-loss-of-smell",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-loss-of-taste",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-lower-back-pain",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-memory-lapse",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-mood-changes",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-nausea",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-night-sweats",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-pelvic-pain",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-rapid-pounding-or-fluttering-heartbeat",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-runny-nose",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-shortness-of-breath",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-sinus-congestion",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-skipped-heartbeat",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-sleep-changes",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-sore-throat",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-vomiting",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-symptom-wheezing",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-time-in-daylight",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-toothbrushing-session",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-underwater-depth",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-uv-exposure",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-vaginal-dryness",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-waist-circumference",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-walking-asymmetry",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-walking-double-support",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-walking-heart-rate-average",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-walking-speed",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-walking-steadiness",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-walking-step-length",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-water-temperature",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-wheelchair-use",
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-workout-effort-score",
    },
    "org.grovealliance.fhir.health-connect": {
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-basal-metabolic-rate",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-capillary-blood-glucose",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-conversion-provenance",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-dietary-energy-from-fat",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-dietary-fat-trans",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-dietary-fat-unsaturated",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-dietary-folic-acid",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-elevation-gained",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-interstitial-glucose",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-menstruation-period",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-observation",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-serum-plasma-glucose",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-specimen",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-step-cadence",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-total-energy",
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-whole-blood-glucose",
    },
    "org.grovealliance.fhir.providers": {
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-body-fat-mass",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-conversion-provenance",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-extracellular-water-mass",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-intracellular-water-mass",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-muscle-mass",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-observation",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-recording-document",
        "https://grovealliance.org/fhir/providers/StructureDefinition/provider-sleeping-heart-rate-average",
    },
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
HEALTHKIT_ECG_PROFILE = (
    "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
    "healthkit-ecg-observation"
)
SAMPLED_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")
FHIR_INSTANT = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?:\.(?P<fraction>[0-9]+))?"
    r"(?P<offset>Z|[+-][0-9]{2}:[0-9]{2})$"
)


class ProducerValidationError(ValueError):
    """A deterministic producer-contract validation failure."""


def unlinked_path(path: Path, label: str) -> Path:
    """Return one lexical path after rejecting every supplied symlink component."""
    if not isinstance(path, Path) or not path.parts:
        raise ProducerValidationError(f"{label} path is invalid")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ProducerValidationError(f"{label} path must not contain traversal components")
    if path.is_absolute():
        current = Path(path.anchor)
        components = path.parts[1:]
    else:
        # Path.cwd() is the process's physical working directory. The supplied
        # relative components are still inspected before resolution.
        current = Path.cwd()
        components = path.parts
    for component in components:
        current = current / component
        if current.is_symlink():
            raise ProducerValidationError(
                f"{label} path contains a symlink component: {path}"
            )
    return current


def resolve_unlinked_regular_file(path: Path, label: str) -> Path:
    """Require a regular, non-symlink file and resolve only after inspection."""
    candidate = unlinked_path(path, label)
    try:
        mode = candidate.stat().st_mode
    except OSError as error:
        raise ProducerValidationError(f"{label} file is absent: {path}") from error
    if not stat.S_ISREG(mode):
        raise ProducerValidationError(f"{label} path is not a regular file: {path}")
    try:
        return candidate.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(f"{label} file cannot be resolved: {path}") from error


def resolve_unlinked_directory(path: Path, label: str) -> Path:
    """Require a prepared directory whose supplied path contains no symlink."""
    candidate = unlinked_path(path, label)
    try:
        mode = candidate.stat().st_mode
    except OSError as error:
        raise ProducerValidationError(f"{label} directory is absent: {path}") from error
    if not stat.S_ISDIR(mode):
        raise ProducerValidationError(f"{label} path is not a directory: {path}")
    try:
        return candidate.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(
            f"{label} directory cannot be resolved: {path}"
        ) from error


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProducerValidationError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_float=Decimal,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read JSON {path}: {error}") from error


def require_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = set(value) - expected
    if unknown:
        raise ProducerValidationError(f"{label} has unsupported fields: {', '.join(sorted(unknown))}")


def safe_resource_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.endswith(".json"):
        raise ProducerValidationError("resource path must be a relative JSON file")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ProducerValidationError(f"unsafe resource path: {value!r}")
    if root.is_symlink():
        raise ProducerValidationError("manifest resource directory must not be a symlink")
    path = root
    for part in candidate.parts:
        path = path / part
        if path.is_symlink():
            raise ProducerValidationError(
                f"resource path contains a symlink component: {value}"
            )
    try:
        resolved_root = root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
    except OSError as error:
        raise ProducerValidationError(f"resource is absent: {value}") from error
    if not path.is_file() or (
        resolved_path.parent != resolved_root and resolved_root not in resolved_path.parents
    ):
        raise ProducerValidationError(f"resource is absent, linked, or outside the manifest directory: {value}")
    return path


def json_pointer(value: Any, pointer: Any, label: str) -> Any:
    """Resolve one strict RFC 6901 pointer without accepting ambiguous array indexes."""
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise ProducerValidationError(f"{label} must be an RFC 6901 JSON Pointer")
    current = value
    if not pointer:
        return current
    for raw_token in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw_token):
            raise ProducerValidationError(f"{label} contains an invalid JSON Pointer escape")
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise ProducerValidationError(f"{label} does not resolve")
            current = current[token]
        elif isinstance(current, list):
            if re.fullmatch(r"0|[1-9][0-9]*", token) is None:
                raise ProducerValidationError(f"{label} has an invalid array index")
            index = int(token)
            if index >= len(current):
                raise ProducerValidationError(f"{label} does not resolve")
            current = current[index]
        else:
            raise ProducerValidationError(f"{label} traverses a scalar value")
    return current


def nested_fhir_resources(resource: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a resource and every directly embedded Bundle entry resource."""
    resources = [resource]
    if resource.get("resourceType") != "Bundle":
        return resources
    entries = resource.get("entry", [])
    if not isinstance(entries, list):
        return resources
    for entry in entries:
        child = entry.get("resource") if isinstance(entry, dict) else None
        if isinstance(child, dict) and isinstance(child.get("resourceType"), str):
            resources.extend(nested_fhir_resources(child))
    return resources


def mobile_semantic_projection(
    resource: Any, vector: dict[str, Any], label: str
) -> dict[str, Any]:
    """Extract the closed source-neutral clinical projection for one Mobile vector."""
    if not isinstance(resource, dict) or resource.get("resourceType") != "Observation":
        raise ProducerValidationError(f"{label} must resolve to an Observation")
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or vector["profile"] not in profiles:
        raise ProducerValidationError(
            f"{label} does not directly claim semantic vector {vector['id']}"
        )

    expected_code = vector["code"]
    codings = resource.get("code", {}).get("coding", [])
    code_matches = [
        coding
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == expected_code["system"]
        and coding.get("code") == expected_code["code"]
    ] if isinstance(codings, list) else []
    if len(code_matches) != 1:
        raise ProducerValidationError(
            f"{label} must contain exactly one normalized semantic code"
        )

    expected_effective = vector["effective"]
    if expected_effective["type"] == "dateTime":
        actual_value = resource.get("effectiveDateTime")
        actual_milliseconds = parse_fhir_instant(
            actual_value, f"{label}.effectiveDateTime"
        )
        if actual_milliseconds != round_mobile_epoch_milliseconds(actual_milliseconds):
            raise ProducerValidationError(
                f"{label} effective instant is not millisecond-canonical"
            )
        expected_milliseconds = round_mobile_epoch_milliseconds(parse_fhir_instant(
            expected_effective["value"],
            f"Mobile semantic vector {vector['id']} effectiveDateTime",
        ))
        if actual_milliseconds != expected_milliseconds:
            raise ProducerValidationError(
                f"{label} effective instant does not equal Mobile semantic vector {vector['id']}"
            )
        effective = expected_effective
    else:
        period = resource.get("effectivePeriod")
        if not isinstance(period, dict):
            raise ProducerValidationError(f"{label} must contain an effectivePeriod")
        for endpoint in ("start", "end"):
            actual_milliseconds = parse_fhir_instant(
                period.get(endpoint), f"{label}.effectivePeriod.{endpoint}"
            )
            if actual_milliseconds != round_mobile_epoch_milliseconds(actual_milliseconds):
                raise ProducerValidationError(
                    f"{label} effective Period {endpoint} is not millisecond-canonical"
                )
            expected_milliseconds = round_mobile_epoch_milliseconds(parse_fhir_instant(
                expected_effective[endpoint],
                f"Mobile semantic vector {vector['id']} effectivePeriod.{endpoint}",
            ))
            if actual_milliseconds != expected_milliseconds:
                raise ProducerValidationError(
                    f"{label} effective Period does not equal Mobile semantic vector {vector['id']}"
                )
        effective = expected_effective

    expected_result = vector["result"]
    if expected_result["type"] == "Quantity":
        quantity = resource.get("valueQuantity")
        result = {
            "type": "Quantity",
            "value": quantity.get("value") if isinstance(quantity, dict) else None,
            "system": quantity.get("system") if isinstance(quantity, dict) else None,
            "code": quantity.get("code") if isinstance(quantity, dict) else None,
            "unit": quantity.get("unit") if isinstance(quantity, dict) else None,
        }
    elif expected_result["type"] == "components":
        actual_components = resource.get("component")
        if not isinstance(actual_components, list) or len(actual_components) != len(
            expected_result["components"]
        ):
            raise ProducerValidationError(
                f"{label} must contain exactly the normalized result components"
            )
        projected_components: list[dict[str, Any]] = []
        for expected_component in expected_result["components"]:
            matches = []
            for component in actual_components:
                component_codings = (
                    component.get("code", {}).get("coding", [])
                    if isinstance(component, dict)
                    else []
                )
                if any(
                    isinstance(coding, dict)
                    and coding.get("system") == expected_component["system"]
                    and coding.get("code") == expected_component["code"]
                    for coding in component_codings
                ):
                    matches.append(component)
            if len(matches) != 1:
                raise ProducerValidationError(
                    f"{label} must contain exactly one {expected_component['id']} component"
                )
            quantity = matches[0].get("valueQuantity")
            projected_components.append({
                "id": expected_component["id"],
                "system": expected_component["system"],
                "code": expected_component["code"],
                "value": quantity.get("value") if isinstance(quantity, dict) else None,
                "quantitySystem": quantity.get("system") if isinstance(quantity, dict) else None,
                "quantityCode": quantity.get("code") if isinstance(quantity, dict) else None,
                "unit": quantity.get("unit") if isinstance(quantity, dict) else None,
            })
        result = {"type": "components", "components": projected_components}
    else:
        concept = resource.get("valueCodeableConcept")
        value_codings = concept.get("coding", []) if isinstance(concept, dict) else []
        matches = [
            coding
            for coding in value_codings
            if isinstance(coding, dict)
            and coding.get("system") == expected_result["system"]
            and coding.get("code") == expected_result["code"]
        ] if isinstance(value_codings, list) else []
        if len(matches) != 1:
            raise ProducerValidationError(
                f"{label} must contain exactly one normalized result coding"
            )
        result = {
            "type": "CodeableConcept",
            "system": expected_result["system"],
            "code": expected_result["code"],
        }

    return {
        "profile": vector["profile"],
        "code": expected_code,
        "effective": effective,
        "result": result,
    }


def all_references(value: Any) -> list[str]:
    references: list[str] = []
    if isinstance(value, dict):
        reference = value.get("reference")
        if isinstance(reference, str):
            references.append(reference)
        for child in value.values():
            references.extend(all_references(child))
    elif isinstance(value, list):
        for child in value:
            references.extend(all_references(child))
    return references


def complete_identifier(value: Any, label: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise ProducerValidationError(f"{label} must be an Identifier")
    system = value.get("system")
    identifier_value = value.get("value")
    if not isinstance(system, str) or not system or not isinstance(identifier_value, str) or not identifier_value:
        raise ProducerValidationError(f"{label} must have a complete system and value")
    return system, identifier_value


def canonical_json_string(value: str) -> str:
    """Serialize one Unicode scalar-value string using RFC 8785/JCS escaping."""
    escapes = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
    }
    output = ['"']
    for character in value:
        point = ord(character)
        if 0xD800 <= point <= 0xDFFF:
            raise ProducerValidationError("entry identity contains an invalid Unicode surrogate")
        if character in escapes:
            output.append(escapes[character])
        elif point <= 0x1F:
            output.append(f"\\u{point:04x}")
        else:
            output.append(character)
    output.append('"')
    return "".join(output)


def canonical_identifier_name(system: str, value: str) -> str:
    """Return the UUID-v5 name for one identifier: the system, a vertical bar, then the value."""
    if "|" in system:
        raise ProducerValidationError(
            "an identifier system must not contain a vertical bar, so the name splits at the first one"
        )
    for text in (system, value):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in text):
            raise ProducerValidationError("identifier contains an invalid Unicode surrogate")
    return f"{system}|{value}"


def canonical_string_array(values: list[str]) -> str:
    """Return the RFC 8785 serialization of one string-only array."""
    if any(not isinstance(value, str) for value in values):
        raise ProducerValidationError("canonical identity arrays contain only strings")
    return "[" + ",".join(canonical_json_string(value) for value in values) + "]"


def expected_entry_full_url(system: str, value: str) -> str:
    name = canonical_identifier_name(system, value)
    return f"urn:uuid:{uuid.uuid5(ENTRY_UUID_NAMESPACE, name)}"


def adapter_profile_contract() -> tuple[set[str], set[str]]:
    """Return the exact shared-measurement and adapter profile sets."""
    measurements = read_json(CATALOG_ROOT / "measurement-catalog.json")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    shared = {
        f"https://grovealliance.org/fhir/{entry.get('owner', 'mobile')}"
        f"/StructureDefinition/{entry['profile']}"
        for entry in measurements["measurements"]
    }
    shared.update(claims["observationAdapterClaim"].get("sharedSensorProfiles", []))
    shared.update(
        entry["semanticProfile"]
        for entry in claims["observationAdapterClaim"].get("standardAdapterClaims", [])
    )
    adapters = set(claims["observationAdapterClaim"]["adapterProfiles"])
    return shared, adapters


def validate_adapter_profile_claim(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    """Require an adapter Observation to claim exactly shared metric + adapter."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    shared_profiles, adapter_profiles = adapter_profile_contract()
    claimed_adapters = set(profiles) & adapter_profiles
    claimed_shared = set(profiles) & shared_profiles
    if active_adapter_profiles is not None:
        inactive = claimed_adapters - active_adapter_profiles
        if inactive:
            raise ProducerValidationError(
                f"{label} claims an adapter profile whose exact package is absent: "
                + ", ".join(sorted(inactive))
            )
        if claimed_shared and active_adapter_profiles and not claimed_adapters:
            raise ProducerValidationError(
                f"{label} shared Observation is missing the applicable adapter profile"
            )
    if not claimed_adapters:
        return
    if (
        len(claimed_adapters) != 1
        or len(claimed_shared) != 1
        or len(profiles) != 2
        or len(set(profiles)) != 2
    ):
        raise ProducerValidationError(
            f"{label} adapter Observation must claim exactly one shared semantic profile "
            "and exactly one adapter profile"
        )


def validate_active_adapter_package_claims(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None,
) -> None:
    """Reject every adapter artifact whose exact package is absent from the manifest."""
    if active_adapter_profiles is None:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(
        not isinstance(profile, str) for profile in profiles
    ):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claimed = set(profiles) & KNOWN_ADAPTER_PROFILES
    inactive = claimed - active_adapter_profiles
    if inactive:
        raise ProducerValidationError(
            f"{label} claims an adapter profile whose exact package is absent: "
            + ", ".join(sorted(inactive))
        )


def validate_health_connect_specimen_claim(resource: dict[str, Any], label: str) -> None:
    """Require an exact direct profile claim on synthesized Health Connect Specimens."""
    if resource.get("resourceType") != "Specimen":
        return
    claims = read_json(CATALOG_ROOT / "profile-claims.json")["healthConnectSpecimenClaim"]
    identifiers = resource.get("identifier", [])
    if not isinstance(identifiers, list):
        raise ProducerValidationError(f"{label} has invalid identifier")
    if not any(
        isinstance(identifier, dict)
        and identifier.get("system") == claims["identifierSystem"]
        for identifier in identifiers
    ):
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if profiles != [claims["profile"]]:
        raise ProducerValidationError(
            f"{label} synthesized Health Connect Specimen must directly claim exactly "
            f"{claims['profile']}"
        )


def validate_sensorkit_profile_claim(resource: dict[str, Any], label: str) -> None:
    """Require exact direct claims for SensorKit-only and native-recording outputs."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(not isinstance(profile, str) for profile in profiles):
        raise ProducerValidationError(f"{label} has invalid meta.profile")

    hybrid_claim = claims["sensorKitHybridObservationClaims"]
    if hybrid_claim["profiles"][1] in profiles and (
        len(profiles) != hybrid_claim["cardinality"]
        or set(profiles) != set(hybrid_claim["profiles"])
    ):
        raise ProducerValidationError(
            f"{label} SensorKit hybrid Observation must directly claim exactly the "
            "source-neutral Sensor and exact SensorKit adapter profiles"
        )

    provider_claim = claims["sensorKitPlatformExclusiveClaims"]
    claimed_provider_profiles = set(profiles) & set(provider_claim["profiles"])
    if claimed_provider_profiles and (
        len(claimed_provider_profiles) != 1
        or profiles != list(claimed_provider_profiles)
    ):
        raise ProducerValidationError(
            f"{label} SensorKit-only Observation must directly claim exactly one "
            "platform-exclusive SensorKit profile"
        )

    if resource.get("resourceType") != "DocumentReference":
        return
    document_claim = claims["sensorKitRecordingDocumentClaim"]
    identifiers = resource.get("identifier", [])
    if not isinstance(identifiers, list):
        raise ProducerValidationError(f"{label} has invalid identifier")
    if not any(
        isinstance(identifier, dict)
        and identifier.get("system") == document_claim["identifierSystem"]
        for identifier in identifiers
    ):
        return
    if len(profiles) != document_claim["cardinality"] or set(profiles) != set(
        document_claim["profiles"]
    ):
        raise ProducerValidationError(
            f"{label} SensorKit Recording Document must directly claim exactly the "
            "source-neutral and SensorKit recording profiles"
        )


def validate_health_connect_provider_claim(resource: dict[str, Any], label: str) -> None:
    """Require one exact direct profile for Health Connect-only glucose semantics."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "healthConnectPlatformExclusiveClaims"
    ]
    claimed = set(profiles) & set(claims["profiles"])
    if claimed and (len(claimed) != 1 or len(profiles) != 1):
        raise ProducerValidationError(
            f"{label} Health Connect-only glucose Observation must directly claim "
            "exactly one adapter-specific profile"
        )


def validate_healthkit_source_type(resource: dict[str, Any], label: str) -> None:
    """Bind one exact HealthKit source coding to its admitted output contract."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    generic_adapter = (
        "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
        "healthkit-observation"
    )
    healthkit_adapters = {generic_adapter, HEALTHKIT_ECG_PROFILE}
    if not isinstance(profiles, list) or not set(profiles) & healthkit_adapters:
        return
    catalog = read_json(CATALOG_ROOT / "healthkit-adapter.json")
    coding_system = catalog["sourceTypeCoding"]["system"]
    codings = resource.get("code", {}).get("coding", [])
    source_codings = [
        coding for coding in codings
        if isinstance(coding, dict) and coding.get("system") == coding_system
    ] if isinstance(codings, list) else []
    if len(source_codings) != 1 or not isinstance(source_codings[0].get("code"), str):
        raise ProducerValidationError(
            f"{label} must carry exactly one HealthKit source-type coding"
        )
    rows = {
        row["sourceTypeIdentifier"]: row for row in catalog["rows"]
        if row["status"] == "supported"
    }
    row = rows.get(source_codings[0]["code"])
    if row is None:
        raise ProducerValidationError(
            f"{label} uses a HealthKit source type without an admitted output contract"
        )
    expected_profiles = set(row["profiles"])
    if not expected_profiles & healthkit_adapters:
        expected_profiles.add(generic_adapter)
    if set(profiles) != expected_profiles or len(profiles) != len(expected_profiles):
        raise ProducerValidationError(
            f"{label} HealthKit source type does not match its exact direct profile claims"
        )


def validate_healthkit_ecg_contract(resource: dict[str, Any], label: str) -> None:
    """Validate lossless HealthKit ECG evidence beyond R4 FHIRPath precision."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or HEALTHKIT_ECG_PROFILE not in profiles:
        return

    extension_urls = {
        "classification": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-classification"
        ),
        "symptomsStatus": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-symptoms-status"
        ),
        "correlatedSymptom": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-correlated-symptom"
        ),
        "averageHeartRate": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-average-heart-rate"
        ),
        "samplingFrequency": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-sampling-frequency"
        ),
        "count": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-voltage-measurement-count"
        ),
        "algorithmVersion": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-algorithm-version"
        ),
        "sourcePeriod": (
            "https://grovealliance.org/fhir/healthkit/StructureDefinition/"
            "healthkit-ecg-source-period"
        ),
    }
    extensions = resource.get("extension", [])
    if not isinstance(extensions, list):
        raise ProducerValidationError(f"{label} has invalid ECG extensions")

    def exact_extension(name: str, required: bool = True) -> dict[str, Any] | None:
        matches = [
            extension
            for extension in extensions
            if isinstance(extension, dict)
            and extension.get("url") == extension_urls[name]
        ]
        if len(matches) > 1 or (required and len(matches) != 1):
            requirement = "exactly one" if required else "at most one"
            raise ProducerValidationError(
                f"{label} HealthKit ECG must carry {requirement} {name} extension"
            )
        return matches[0] if matches else None

    classification = exact_extension("classification")
    classification_code = classification.get("valueCode") if classification else None
    if classification_code not in {
        "notSet",
        "sinusRhythm",
        "atrialFibrillation",
        "inconclusiveLowHeartRate",
        "inconclusiveHighHeartRate",
        "inconclusivePoorReading",
        "inconclusiveOther",
        "unrecognized",
    }:
        raise ProducerValidationError(f"{label} has an unknown HealthKit ECG classification")

    status = exact_extension("symptomsStatus")
    status_code = status.get("valueCode") if status else None
    if status_code not in {"notSet", "none", "present"}:
        raise ProducerValidationError(f"{label} has an unknown HealthKit ECG symptoms status")
    correlated = [
        extension
        for extension in extensions
        if isinstance(extension, dict)
        and extension.get("url") == extension_urls["correlatedSymptom"]
    ]
    if len(correlated) > 7 or (status_code == "present") != bool(correlated):
        raise ProducerValidationError(
            f"{label} HealthKit ECG correlated symptoms must agree with symptomsStatus"
        )
    admitted_symptoms = {
        "HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat",
        "HKCategoryTypeIdentifierSkippedHeartbeat",
        "HKCategoryTypeIdentifierFatigue",
        "HKCategoryTypeIdentifierShortnessOfBreath",
        "HKCategoryTypeIdentifierChestTightnessOrPain",
        "HKCategoryTypeIdentifierFainting",
        "HKCategoryTypeIdentifierDizziness",
    }
    admitted_severities = {"unspecified", "notPresent", "mild", "moderate", "severe"}
    seen_symptom_identifiers: set[str] = set()
    required_symptom_children = {
        "sourceIdentifier",
        "effectivePeriod",
        "symptomType",
        "severity",
        "sourceName",
        "sourceBundleIdentifier",
        "sourceOperatingSystemMajorVersion",
        "sourceOperatingSystemMinorVersion",
        "sourceOperatingSystemPatchVersion",
    }
    optional_symptom_children = {"sourceVersion", "sourceProductType"}
    for index, symptom in enumerate(correlated):
        children = symptom.get("extension")
        if not isinstance(children, list):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] is incomplete"
            )
        by_url = {
            child.get("url"): child
            for child in children
            if isinstance(child, dict) and isinstance(child.get("url"), str)
        }
        if (
            len(by_url) != len(children)
            or not required_symptom_children <= set(by_url)
            or not set(by_url) <= required_symptom_children | optional_symptom_children
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] is incomplete"
            )
        symptom_type = by_url["symptomType"].get("valueCode")
        severity = by_url["severity"].get("valueCode")
        if symptom_type not in admitted_symptoms or severity not in admitted_severities:
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] uses an unknown code"
            )
        symptom_system, symptom_identifier = complete_identifier(
            by_url["sourceIdentifier"].get("valueIdentifier"),
            f"{label} HealthKit ECG correlated symptom[{index}] source",
        )
        if (
            symptom_system
            != "https://grovealliance.org/fhir/healthkit/NamingSystem/healthkit-object-id"
            or re.fullmatch(
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                symptom_identifier,
            )
            is None
            or symptom_identifier in seen_symptom_identifiers
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] has invalid or repeated source identity"
            )
        seen_symptom_identifiers.add(symptom_identifier)
        symptom_period = by_url["effectivePeriod"].get("valuePeriod")
        if not isinstance(symptom_period, dict):
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] has no exact period"
            )
        symptom_start = parse_fhir_instant(
            symptom_period.get("start"),
            f"{label} HealthKit ECG correlated symptom[{index}] start",
        )
        symptom_end = parse_fhir_instant(
            symptom_period.get("end"),
            f"{label} HealthKit ECG correlated symptom[{index}] end",
        )
        if symptom_end < symptom_start:
            raise ProducerValidationError(
                f"{label} HealthKit ECG correlated symptom[{index}] period is reversed"
            )
        for child_name in ("sourceName", "sourceBundleIdentifier"):
            value = by_url[child_name].get("valueString")
            if not isinstance(value, str) or not value:
                raise ProducerValidationError(
                    f"{label} HealthKit ECG correlated symptom[{index}] has incomplete HKSourceRevision"
                )
        for child_name in optional_symptom_children:
            if child_name in by_url:
                value = by_url[child_name].get("valueString")
                if not isinstance(value, str) or not value:
                    raise ProducerValidationError(
                        f"{label} HealthKit ECG correlated symptom[{index}] has incomplete HKSourceRevision"
                    )
        for child_name in (
            "sourceOperatingSystemMajorVersion",
            "sourceOperatingSystemMinorVersion",
            "sourceOperatingSystemPatchVersion",
        ):
            value = by_url[child_name].get("valueInteger")
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ProducerValidationError(
                    f"{label} HealthKit ECG correlated symptom[{index}] has incomplete HKSourceRevision"
                )

    count_extension = exact_extension("count")
    count = count_extension.get("valueInteger") if count_extension else None
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ProducerValidationError(
            f"{label} HealthKit ECG voltage measurement count must be positive"
        )
    components = resource.get("component")
    if not isinstance(components, list) or len(components) != 1:
        raise ProducerValidationError(f"{label} HealthKit ECG must contain exactly one lead")
    component = components[0]
    codings = component.get("code", {}).get("coding", []) if isinstance(component, dict) else []
    lead_codings = [
        coding
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == "urn:iso:std:iso:11073:10101"
        and coding.get("code") == "131329"
    ] if isinstance(codings, list) else []
    if len(lead_codings) != 1:
        raise ProducerValidationError(
            f"{label} HealthKit ECG must use the exact Lead-I-like MDC channel"
        )
    sampled = component.get("valueSampledData") if isinstance(component, dict) else None
    data = sampled.get("data") if isinstance(sampled, dict) else None
    if not isinstance(data, str) or len(re.split(r"\s+", data)) != count:
        raise ProducerValidationError(
            f"{label} HealthKit ECG voltage count does not match SampledData frames"
        )

    for name, code in (("averageHeartRate", "/min"), ("samplingFrequency", "Hz")):
        extension = exact_extension(name, required=False)
        if extension is None:
            continue
        quantity = extension.get("valueQuantity")
        value = quantity.get("value") if isinstance(quantity, dict) else None
        if (
            not isinstance(quantity, dict)
            or quantity.get("system") != "http://unitsofmeasure.org"
            or quantity.get("code") != code
            or isinstance(value, bool)
            or not isinstance(value, (int, float, Decimal))
            or Decimal(str(value)) <= 0
        ):
            raise ProducerValidationError(
                f"{label} HealthKit ECG {name} must be a positive exact UCUM Quantity"
            )
        if name == "samplingFrequency":
            period = sampled.get("period") if isinstance(sampled, dict) else None
            if not isinstance(period, (int, float, Decimal)) or isinstance(period, bool):
                raise ProducerValidationError(f"{label} HealthKit ECG has no sampling period")
            if Decimal(str(period)) * Decimal(str(value)) != Decimal(1000):
                raise ProducerValidationError(
                    f"{label} HealthKit ECG sampling frequency and SampledData.period disagree"
                )
    algorithm = exact_extension("algorithmVersion", required=False)
    if algorithm is not None and algorithm.get("valueCode") not in {"version1", "version2"}:
        raise ProducerValidationError(
            f"{label} has an unknown HealthKit ECG algorithm version"
        )
    source_period_extension = exact_extension("sourcePeriod")
    source_period = (
        source_period_extension.get("valuePeriod")
        if source_period_extension is not None
        else None
    )
    effective_period = resource.get("effectivePeriod")
    if not isinstance(source_period, dict) or not isinstance(effective_period, dict):
        raise ProducerValidationError(
            f"{label} HealthKit ECG must preserve source and waveform periods"
        )
    source_start = parse_fhir_instant(source_period.get("start"), f"{label} source start")
    source_end = parse_fhir_instant(source_period.get("end"), f"{label} source end")
    waveform_start = parse_fhir_instant(
        effective_period.get("start"), f"{label} waveform start"
    )
    waveform_end = parse_fhir_instant(
        effective_period.get("end"), f"{label} waveform end"
    )
    if not source_start <= waveform_start <= waveform_end <= source_end:
        raise ProducerValidationError(
            f"{label} HealthKit ECG waveform period must lie within its exact source period"
        )


def validate_health_connect_source_type(resource: dict[str, Any], label: str) -> None:
    """Bind one exact Health Connect Record class to its output measurement."""
    if resource.get("resourceType") != "Observation":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    adapter_prefix = (
        "https://grovealliance.org/fhir/health-connect/StructureDefinition/"
    )
    if not isinstance(profiles, list) or not any(
        isinstance(profile, str) and profile.startswith(adapter_prefix)
        for profile in profiles
    ):
        return
    catalog = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    extension_url = catalog["sourceTypeExtension"]["url"]
    extensions = resource.get("extension", [])
    values = [
        extension.get("valueCode") for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == extension_url
    ] if isinstance(extensions, list) else []
    if len(values) != 1 or not isinstance(values[0], str):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded Health Connect Record type"
        )
    row = next(
        (item for item in catalog["recordTypes"] if item["token"] == values[0]),
        None,
    )
    if row is None or row["status"] != "supported":
        raise ProducerValidationError(
            f"{label} uses a Health Connect Record type without an admitted output contract"
        )
    measurement_profiles = {
        f"https://grovealliance.org/fhir/mobile/StructureDefinition/{item['profile']}": item["id"]
        for item in read_json(CATALOG_ROOT / "measurement-catalog.json")["measurements"]
    }
    measurement_profiles.update(
        {item["profile"]: item["id"] for item in catalog["adapterMeasurements"]}
    )
    claimed = {
        measurement_profiles[profile] for profile in profiles
        if profile in measurement_profiles
    }
    admitted = {output["measurement"] for output in row["outputs"]}
    if len(claimed) != 1 or not claimed <= admitted:
        raise ProducerValidationError(
            f"{label} Health Connect Record type does not admit its claimed measurement"
        )


def validate_provider_claim(resource: dict[str, Any], label: str) -> None:
    """Require the exact source-neutral plus adapter pair on connected raw data."""
    if resource.get("resourceType") != "DocumentReference":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claim = read_json(CATALOG_ROOT / "profile-claims.json")[
        "providerRecordingDocumentClaim"
    ]
    if claim["profiles"][1] not in profiles:
        return
    if len(profiles) != claim["cardinality"] or set(profiles) != set(claim["profiles"]):
        raise ProducerValidationError(
            f"{label} Provider Recording Document must directly claim exactly "
            "the source-neutral and connected adapter profiles"
        )


def validate_adapter_conversion_provenance(
    resource: dict[str, Any], label: str
) -> None:
    """Require the exact adapter source entity on conversion Provenance resources."""
    if resource.get("resourceType") != "Provenance":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or any(
        not isinstance(profile, str) for profile in profiles
    ):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "adapterConversionProvenanceClaims"
    ]
    matches = [claim for claim in claims if claim["profile"] in profiles]
    if not matches:
        return
    if len(matches) != 1 or profiles != [matches[0]["profile"]]:
        raise ProducerValidationError(
            f"{label} adapter conversion Provenance must directly claim exactly "
            "its adapter-specific Provenance profile"
        )
    claim = matches[0]
    targets = resource.get("target")
    if not isinstance(targets, list) or not targets:
        raise ProducerValidationError(f"{label} must contain conversion targets")
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or not isinstance(target.get("reference"), str):
            raise ProducerValidationError(
                f"{label}.target[{index}] must contain an exact reference"
            )
    entities = resource.get("entity")
    if not isinstance(entities, list) or len(entities) != 1:
        raise ProducerValidationError(
            f"{label} must carry exactly one source entity"
        )
    entity = entities[0]
    what = entity.get("what") if isinstance(entity, dict) else None
    if (
        not isinstance(entity, dict)
        or entity.get("role") != "source"
        or not isinstance(what, dict)
        or "reference" in what
    ):
        raise ProducerValidationError(
            f"{label} must carry its source as exactly one Identifier entity"
        )
    system, _ = complete_identifier(
        what.get("identifier"), f"{label} source entity"
    )
    if system != claim["sourceIdentifierSystem"]:
        raise ProducerValidationError(
            f"{label} source entity uses the wrong adapter identifier system"
        )


def validate_provider_identity(resource: dict[str, Any], label: str) -> None:
    """Validate provider lineage and deterministic source/output business identity."""
    if resource.get("resourceType") not in {"Observation", "DocumentReference"}:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    adapter = (
        "https://grovealliance.org/fhir/providers/StructureDefinition/"
        "provider-observation"
    )
    document_adapter = (
        "https://grovealliance.org/fhir/providers/StructureDefinition/"
        "provider-recording-document"
    )
    if adapter not in profiles and document_adapter not in profiles:
        return
    catalog = read_json(CATALOG_ROOT / "providers-adapter.json")
    source_system = catalog["identity"]["sourceRecord"]["system"]
    output_system = catalog["identity"]["output"]["system"]
    identifiers = resource.get("identifier", [])
    if not isinstance(identifiers, list):
        raise ProducerValidationError(f"{label} has invalid identifier")

    def identifier_value(system: str, role: str) -> str:
        matches = [
            item for item in identifiers
            if isinstance(item, dict) and item.get("system") == system
        ]
        if len(matches) != 1:
            raise ProducerValidationError(
                f"{label} must carry exactly one Provider {role} identifier"
            )
        return complete_identifier(matches[0], f"{label} {role} identifier")[1]

    source_value = identifier_value(source_system, "source-record")
    output_value = identifier_value(output_system, "output")
    composition_pattern = r"^v1:[^|]+(?:\|[^|]+)+$"
    if re.fullmatch(composition_pattern, source_value) is None or re.fullmatch(
        composition_pattern, output_value
    ) is None:
        raise ProducerValidationError(
            f"{label} has a Provider identifier that is not a v1 composition"
        )
    if resource.get("id") in {source_value, output_value}:
        raise ProducerValidationError(
            f"{label} must not copy a Provider business identifier into Resource.id"
        )
    provider_url = (
        "https://grovealliance.org/fhir/providers/StructureDefinition/"
        "provider"
    )
    extensions = resource.get("extension", [])
    providers = [
        item.get("valueCode") for item in extensions
        if isinstance(item, dict) and item.get("url") == provider_url
    ] if isinstance(extensions, list) else []
    admitted_providers = {item["id"] for item in catalog["providers"]}
    if len(providers) != 1 or providers[0] not in admitted_providers:
        raise ProducerValidationError(
            f"{label} must carry exactly one admitted Provider provider"
        )
    source_type_url = catalog["sourceTypeExtension"]["url"]
    source_types = [
        item.get("valueCode") for item in extensions
        if isinstance(item, dict) and item.get("url") == source_type_url
    ] if isinstance(extensions, list) else []
    if len(source_types) != 1 or not isinstance(source_types[0], str):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded Provider source type"
        )
    provider = next(item for item in catalog["providers"] if item["id"] == providers[0])
    ordinary = {
        f"{provider['id']}/{item['token']}": item
        for item in provider["sourceTypes"]
    }
    grouped = {
        f"{provider['id']}/{item['token']}": item
        for item in provider.get("groupedMappings", [])
    }
    source_row = ordinary.get(source_types[0])
    grouped_row = grouped.get(source_types[0])
    if source_row is None and grouped_row is None:
        raise ProducerValidationError(
            f"{label} uses an unknown or cross-provider Provider source type"
        )
    if resource["resourceType"] == "DocumentReference":
        if source_row is None or "raw" not in source_row:
            raise ProducerValidationError(
                f"{label} source type does not admit a native Recording Document"
            )
        discriminator = catalog["recordingDocument"]["outputDiscriminator"]
    else:
        measurement_profiles = {
            f"https://grovealliance.org/fhir/mobile/StructureDefinition/{item['profile']}": item["id"]
            for item in read_json(CATALOG_ROOT / "measurement-catalog.json")["measurements"]
        }
        claimed = [measurement_profiles[item] for item in profiles if item in measurement_profiles]
        if len(claimed) != 1:
            raise ProducerValidationError(
                f"{label} Provider Observation has no exact shared measurement"
            )
        if grouped_row is not None:
            admitted_measurements = set(grouped_row["measurementIds"])
        else:
            admitted_measurements = {
                measurement
                for element in source_row["elements"]
                if element["status"] == "supported"
                for measurement in element.get("measurementIds", [])
            }
        if claimed[0] not in admitted_measurements:
            raise ProducerValidationError(
                f"{label} Provider source type does not admit its claimed measurement"
            )
        discriminator = (
            "blood-pressure-panel"
            if providers[0] == "withings" and claimed[0] == "blood-pressure"
            else claimed[0]
        )
    expected = f"{source_value}|{discriminator}"
    if output_value != expected:
        raise ProducerValidationError(
            f"{label} Provider output identifier does not match its exact "
            "source and discriminator"
        )


def validate_sensorkit_identity(resource: dict[str, Any], label: str) -> None:
    """Bind SensorKit source type, source identity, output identity, and status row."""
    if resource.get("resourceType") not in {"Observation", "DocumentReference"}:
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        raise ProducerValidationError(f"{label} has invalid meta.profile")
    sensorkit_profile_prefix = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
    )
    if not any(
        isinstance(profile, str) and profile.startswith(sensorkit_profile_prefix)
        for profile in profiles
    ):
        return

    catalog = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    identity = catalog["identity"]
    source_system = identity["sourceRecord"]["system"]
    output_system = identity["output"]["system"]
    identifiers = resource.get("identifier", [])
    if not isinstance(identifiers, list):
        raise ProducerValidationError(f"{label} has invalid identifier")

    def exact_identifier(system: str, role: str) -> tuple[str, str]:
        matches = [
            identifier for identifier in identifiers
            if isinstance(identifier, dict) and identifier.get("system") == system
        ]
        if len(matches) != 1:
            raise ProducerValidationError(
                f"{label} must carry exactly one SensorKit {role} identifier"
            )
        return complete_identifier(matches[0], f"{label} SensorKit {role} identifier")

    source_pair = exact_identifier(source_system, "source-record")
    output_pair = exact_identifier(output_system, "output")
    if not re.fullmatch(identity["valuePattern"], source_pair[1]):
        raise ProducerValidationError(f"{label} has an invalid SensorKit source-record UUID")
    if not re.fullmatch(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        output_pair[1],
    ):
        raise ProducerValidationError(f"{label} has an invalid SensorKit output UUIDv5")
    if resource.get("id") in {source_pair[1], output_pair[1]}:
        raise ProducerValidationError(
            f"{label} must not copy a SensorKit business identifier into Resource.id"
        )

    source_type_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-source-type"
    )
    extensions = resource.get("extension", [])
    source_types = [
        extension.get("valueCode")
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == source_type_url
    ] if isinstance(extensions, list) else []
    if len(source_types) != 1 or not isinstance(source_types[0], str):
        raise ProducerValidationError(
            f"{label} must carry exactly one coded SensorKit source type"
        )
    rows = {
        row["sourceTypeCode"]: row for row in catalog["entries"]
    }
    row = rows.get(source_types[0])
    if row is None:
        raise ProducerValidationError(f"{label} uses an unknown SensorKit source type")

    if resource["resourceType"] == "DocumentReference":
        representation = row.get("raw")
    else:
        representation = row.get("structured")
        if not isinstance(representation, dict) or "outputDiscriminator" not in representation:
            raise ProducerValidationError(
                f"{label} source type has no admitted structured SensorKit output"
            )
        expected_profile = representation.get("profile")
        if expected_profile is not None and profiles != [expected_profile]:
            raise ProducerValidationError(
                f"{label} must directly claim its exact SensorKit-only profile"
            )
    if not isinstance(representation, dict):
        raise ProducerValidationError(
            f"{label} source type has no admitted SensorKit representation"
        )
    discriminator = representation.get("outputDiscriminator")
    if not isinstance(discriminator, str) or not discriminator:
        raise ProducerValidationError(
            f"{label} admitted SensorKit representation has no output discriminator"
        )
    preimage = canonical_string_array([source_pair[0], source_pair[1], discriminator])
    expected = str(uuid.uuid5(uuid.UUID(identity["output"]["namespace"]), preimage))
    if output_pair[1] != expected:
        raise ProducerValidationError(
            f"{label} SensorKit output identifier does not match its exact source and discriminator"
        )


def validate_sensorkit_ecg_contract(resource: dict[str, Any], label: str) -> None:
    """Validate the exact structured portion of the mandatory SensorKit ECG hybrid."""
    if resource.get("resourceType") != "Observation":
        return
    profile = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-ecg-observation"
    )
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or profile not in profiles:
        return
    guidance_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-ecg-session-guidance"
    )
    extensions = resource.get("extension", [])
    guidance = [
        extension.get("valueCode")
        for extension in extensions
        if isinstance(extension, dict) and extension.get("url") == guidance_url
    ] if isinstance(extensions, list) else []
    if len(guidance) != 1 or guidance[0] not in {"guided", "unguided"}:
        raise ProducerValidationError(
            f"{label} must carry exactly one coded SensorKit ECG session guidance"
        )
    components = resource.get("component")
    if not isinstance(components, list) or len(components) != 1:
        raise ProducerValidationError(f"{label} SensorKit ECG must contain exactly one lead")
    codings = components[0].get("code", {}).get("coding", [])
    source_leads = [
        coding.get("code")
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system")
        == "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-ecg-lead"
    ] if isinstance(codings, list) else []
    if len(source_leads) != 1 or source_leads[0] not in {
        "rightArmMinusLeftArm",
        "leftArmMinusRightArm",
    }:
        raise ProducerValidationError(
            f"{label} must carry exactly one exact SensorKit ECG lead orientation"
        )
    lead_i = [
        coding
        for coding in codings
        if isinstance(coding, dict)
        and coding.get("system") == "urn:iso:std:iso:11073:10101"
        and coding.get("code") == "131329"
    ]
    if (source_leads[0] == "leftArmMinusRightArm" and len(lead_i) != 1) or (
        source_leads[0] == "rightArmMinusLeftArm" and lead_i
    ):
        raise ProducerValidationError(
            f"{label} SensorKit ECG source orientation and standard Lead-I coding disagree"
        )


def parse_fhir_instant(value: Any, label: str) -> Decimal:
    """Return exact epoch milliseconds without truncating fractional seconds."""
    if not isinstance(value, str):
        raise ProducerValidationError(f"{label} must be an offset-bearing dateTime")
    match = FHIR_INSTANT.fullmatch(value)
    if match is None:
        raise ProducerValidationError(f"{label} is not an exact offset-bearing dateTime")
    offset = "+00:00" if match.group("offset") == "Z" else match.group("offset")
    try:
        parsed = datetime.fromisoformat(
            f"{match.group('date')}T{match.group('time')}{offset}"
        )
    except ValueError as error:
        raise ProducerValidationError(f"{label} is not a valid dateTime") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProducerValidationError(f"{label} must carry a UTC offset")
    utc = parsed.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    whole = utc - epoch
    seconds = Decimal(whole.days) * Decimal(86_400) + Decimal(whole.seconds)
    fraction_text = match.group("fraction")
    fraction = (
        Decimal(int(fraction_text)) / (Decimal(10) ** len(fraction_text))
        if fraction_text is not None
        else Decimal(0)
    )
    return (seconds + fraction) * Decimal(1000)


def round_mobile_epoch_milliseconds(value: Decimal) -> Decimal:
    """Round an exact epoch-millisecond value to a millisecond, ties to even."""
    return value.quantize(Decimal(1), rounding=ROUND_HALF_EVEN)


def validate_sampled_data(
    sampled: Any,
    effective: Any,
    label: str,
) -> None:
    """Enforce the exact v0.3 uniform-frame and interval semantics."""
    if not isinstance(sampled, dict):
        raise ProducerValidationError(f"{label} must be SampledData")
    for forbidden in ("factor", "lowerLimit", "upperLimit"):
        if forbidden in sampled:
            raise ProducerValidationError(f"{label}.{forbidden} is not admitted")
    period_value = sampled.get("period")
    if isinstance(period_value, bool) or not isinstance(
        period_value, (int, float, Decimal)
    ):
        raise ProducerValidationError(f"{label}.period must be a positive number")
    try:
        period = Decimal(str(period_value))
    except InvalidOperation as error:
        raise ProducerValidationError(f"{label}.period must be a positive number") from error
    if not period.is_finite() or period <= 0:
        raise ProducerValidationError(f"{label}.period must be greater than zero")
    dimensions = sampled.get("dimensions")
    if isinstance(dimensions, bool) or not isinstance(dimensions, int) or dimensions <= 0:
        raise ProducerValidationError(f"{label}.dimensions must be a positive integer")
    data = sampled.get("data")
    if not isinstance(data, str) or not data or data != data.strip():
        raise ProducerValidationError(f"{label}.data must be a non-empty decimal sequence")
    tokens = re.split(r"\s+", data)
    if any(SAMPLED_DECIMAL.fullmatch(token) is None for token in tokens):
        raise ProducerValidationError(
            f"{label}.data admits only complete decimal values; E, U, L, and missing tokens fail closed"
        )
    if len(tokens) % dimensions != 0:
        raise ProducerValidationError(
            f"{label}.data token count must be divisible by dimensions"
        )
    frame_count = len(tokens) // dimensions
    if frame_count < 2:
        raise ProducerValidationError(
            f"{label} must contain at least two complete sampled-data frames"
        )
    if not isinstance(effective, dict):
        raise ProducerValidationError(f"{label} requires an effectivePeriod")
    start = parse_fhir_instant(effective.get("start"), f"{label} effectivePeriod.start")
    end = parse_fhir_instant(effective.get("end"), f"{label} effectivePeriod.end")
    actual_milliseconds = end - start
    expected_milliseconds = Decimal(frame_count - 1) * period
    if actual_milliseconds != expected_milliseconds:
        raise ProducerValidationError(
            f"{label} effectivePeriod.end must equal first frame plus "
            "(frameCount - 1) * period milliseconds"
        )


def validate_recording_attachment(attachment: Any, label: str) -> None:
    """Require verifiable exact bytes for every admitted native recording."""
    if not isinstance(attachment, dict):
        raise ProducerValidationError(f"{label} must be an Attachment")
    has_data = isinstance(attachment.get("data"), str)
    has_url = isinstance(attachment.get("url"), str) and bool(attachment.get("url"))
    if has_data == has_url:
        raise ProducerValidationError(f"{label} must contain exactly one of data or url")
    size = attachment.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ProducerValidationError(f"{label}.size is required and must be a byte count")
    encoded_hash = attachment.get("hash")
    if not isinstance(encoded_hash, str):
        raise ProducerValidationError(f"{label}.hash is required")
    try:
        digest = base64.b64decode(encoded_hash, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ProducerValidationError(f"{label}.hash must be base64 SHA-1") from error
    if len(digest) != 20:
        raise ProducerValidationError(f"{label}.hash must encode exactly one SHA-1 digest")
    if has_data:
        try:
            payload = base64.b64decode(attachment["data"], validate=True)
        except (binascii.Error, ValueError) as error:
            raise ProducerValidationError(f"{label}.data must be valid base64") from error
        if len(payload) != size:
            raise ProducerValidationError(f"{label}.size does not match embedded bytes")
        if hashlib.sha1(payload).digest() != digest:  # noqa: S324 -- mandated by FHIR R4 Attachment.hash
            raise ProducerValidationError(f"{label}.hash does not match embedded bytes")


def validate_sensor_contract(resource: dict[str, Any], label: str) -> None:
    """Validate source-neutral Sensor payload rules not expressible in R4 FHIRPath."""
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list):
        return
    if SENSOR_SAMPLED_PROFILE in profiles:
        validate_sampled_data(
            resource.get("valueSampledData"), resource.get("effectivePeriod"), label
        )
    if SENSOR_ECG_PROFILE in profiles:
        components = resource.get("component")
        if not isinstance(components, list) or not components:
            raise ProducerValidationError(f"{label} ECG must contain sampled-data components")
        for index, component in enumerate(components):
            sampled = component.get("valueSampledData") if isinstance(component, dict) else None
            validate_sampled_data(
                sampled, resource.get("effectivePeriod"), f"{label}.component[{index}]"
            )
    if SENSOR_RECORDING_PROFILE in profiles:
        contents = resource.get("content")
        if not isinstance(contents, list) or not contents:
            raise ProducerValidationError(f"{label} Recording Document must contain content")
        for index, content in enumerate(contents):
            attachment = content.get("attachment") if isinstance(content, dict) else None
            validate_recording_attachment(attachment, f"{label}.content[{index}].attachment")


RECORDING_DOCUMENT_PROFILE_TAIL = "-recording-document"


def validate_recording_format(resource: dict[str, Any], label: str) -> None:
    """Require one registered payload format per recording content entry."""
    if resource.get("resourceType") != "DocumentReference":
        return
    profiles = resource.get("meta", {}).get("profile", [])
    if not isinstance(profiles, list) or not any(
        isinstance(profile, str) and profile.endswith(RECORDING_DOCUMENT_PROFILE_TAIL)
        for profile in profiles
    ):
        return
    registry = read_json(CATALOG_ROOT / "format-registry.json")
    formats = registry["formats"]
    contents = resource.get("content", [])
    if not isinstance(contents, list) or not contents:
        raise ProducerValidationError(f"{label} recording document has no content")
    declared_codes: list[str] = []
    for index, content in enumerate(contents):
        format_coding = content.get("format") if isinstance(content, dict) else None
        if not isinstance(format_coding, dict):
            raise ProducerValidationError(
                f"{label} content[{index}] declares no registry payload format"
            )
        if format_coding.get("system") != registry["codeSystem"]:
            raise ProducerValidationError(
                f"{label} content[{index}] format system is not the Grove "
                "recording-format registry"
            )
        code = format_coding.get("code")
        entry = formats.get(code) if isinstance(code, str) else None
        if entry is None:
            raise ProducerValidationError(
                f"{label} content[{index}] declares unregistered format {code!r}"
            )
        content_type = content.get("attachment", {}).get("contentType")
        if content_type != entry["contentType"]:
            raise ProducerValidationError(
                f"{label} content[{index}] contentType {content_type!r} does not "
                f"match registry format {code} ({entry['contentType']})"
            )
        declared_codes.append(code)

    sensorkit = read_json(CATALOG_ROOT / "sensorkit-adapter.json")
    extension_url = (
        "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
        "sensorkit-source-type"
    )
    source_codes = [
        extension.get("valueCode")
        for extension in resource.get("extension", [])
        if isinstance(extension, dict) and extension.get("url") == extension_url
    ]
    if len(source_codes) == 1 and isinstance(source_codes[0], str):
        rows = {entry["sourceTypeCode"]: entry for entry in sensorkit["entries"]}
        row = rows.get(source_codes[0])
        admitted = (row or {}).get("raw", {}).get("formats")
        if isinstance(admitted, list):
            for code in declared_codes:
                if code not in admitted:
                    raise ProducerValidationError(
                        f"{label} declares format {code!r}, which the SensorKit "
                        f"stream {source_codes[0]!r} does not admit"
                    )


def validate_resource_profile_claims(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    validate_active_adapter_package_claims(resource, label, active_adapter_profiles)
    validate_adapter_profile_claim(resource, label, active_adapter_profiles)
    validate_health_connect_specimen_claim(resource, label)
    validate_health_connect_provider_claim(resource, label)
    validate_healthkit_source_type(resource, label)
    validate_healthkit_ecg_contract(resource, label)
    validate_health_connect_source_type(resource, label)
    validate_provider_claim(resource, label)
    validate_adapter_conversion_provenance(resource, label)
    validate_provider_identity(resource, label)
    validate_sensorkit_profile_claim(resource, label)
    validate_sensorkit_identity(resource, label)
    validate_sensorkit_ecg_contract(resource, label)
    validate_sensor_contract(resource, label)
    validate_recording_format(resource, label)


def validate_adapter_provenance_graph(
    entry_resources: list[dict[str, Any]],
    resources_by_full_url: dict[str, dict[str, Any]],
    label: str,
) -> None:
    """Bind every adapter output for one source record to one internal Provenance."""
    claims = read_json(CATALOG_ROOT / "profile-claims.json")[
        "adapterConversionProvenanceClaims"
    ]

    def source_value(resource: dict[str, Any], system: str, role: str) -> str:
        identifiers = resource.get("identifier", [])
        matches = [
            identifier
            for identifier in identifiers
            if isinstance(identifier, dict) and identifier.get("system") == system
        ] if isinstance(identifiers, list) else []
        if len(matches) != 1:
            raise ProducerValidationError(
                f"{label} {role} must carry exactly one adapter source-record Identifier"
            )
        return complete_identifier(matches[0], f"{label} {role} source identifier")[1]

    url_by_resource = {id(resource): url for url, resource in resources_by_full_url.items()}
    for claim in claims:
        target_profiles = set(claim["targetAdapterProfiles"])
        outputs_by_source: dict[str, set[str]] = {}
        provenances_by_source: dict[str, list[dict[str, Any]]] = {}
        # A bundle whose outputs for a source are all retractions records a lifecycle event
        # rather than a conversion, so it carries no conversion Provenance to describe.
        converted_sources: set[str] = set()
        for resource in entry_resources:
            profiles = resource.get("meta", {}).get("profile", [])
            profile_set = set(profiles) if isinstance(profiles, list) else set()
            if profile_set & target_profiles:
                source = source_value(resource, claim["sourceIdentifierSystem"], "output")
                outputs_by_source.setdefault(source, set()).add(url_by_resource[id(resource)])
                if resource.get("status") != "entered-in-error":
                    converted_sources.add(source)
            if claim["profile"] in profile_set:
                entity = resource["entity"][0]["what"]["identifier"]
                source = complete_identifier(entity, f"{label} Provenance source entity")[1]
                provenances_by_source.setdefault(source, []).append(resource)

        for source, output_urls in outputs_by_source.items():
            provenances = provenances_by_source.get(source, [])
            if source not in converted_sources:
                if provenances:
                    raise ProducerValidationError(
                        f"{label} {claim['adapter']} retraction must not claim a conversion "
                        "Provenance"
                    )
                continue
            if len(provenances) != 1:
                raise ProducerValidationError(
                    f"{label} {claim['adapter']} source record must have exactly one "
                    "conversion Provenance in the same Bundle"
                )
            provenance = provenances[0]
            target_urls = [target["reference"] for target in provenance["target"]]
            if any(not url.startswith("urn:uuid:") for url in target_urls):
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance targets must be internal UUID references"
                )
            if len(target_urls) != len(set(target_urls)):
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance repeats a target"
                )
            for target_url in target_urls:
                target = resources_by_full_url.get(target_url)
                if target is None:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance has an unresolved target"
                    )
                target_profile_set = set(target.get("meta", {}).get("profile", []))
                if not target_profile_set & target_profiles:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance targets a resource "
                        "outside its adapter output contract"
                    )
                if source_value(target, claim["sourceIdentifierSystem"], "target") != source:
                    raise ProducerValidationError(
                        f"{label} adapter conversion Provenance source entity and target "
                        "must carry the same source-record Identifier"
                    )
            if set(target_urls) != output_urls:
                raise ProducerValidationError(
                    f"{label} adapter conversion Provenance must target every structured "
                    "and raw output for its source record"
                )
        extra_sources = set(provenances_by_source) - set(outputs_by_source)
        if extra_sources:
            raise ProducerValidationError(
                f"{label} adapter conversion Provenance has no output for its source record"
            )


PROVIDER_CONVERSION_ID = (
    "https://grovealliance.org/fhir/providers/NamingSystem/provider-conversion-id"
)
PROVIDER_EXCHANGE_ID = (
    "https://grovealliance.org/fhir/providers/NamingSystem/provider-exchange-id"
)
PROVIDER_CONVERSION_PROVENANCE_PROFILE = (
    "https://grovealliance.org/fhir/providers/StructureDefinition/"
    "provider-conversion-provenance"
)
V1_DIGEST = re.compile(r"^v1:[0-9a-f]{64}$")


def validate_provider_exchange_identity(
    bundle: dict[str, Any],
    entry_identities: list[tuple[str, str, dict[str, Any]]],
    label: str,
) -> None:
    """Enforce the frozen provider conversion/exchange identity encoding."""
    conversion_values: list[str] = []
    for index, (system, value, entry_resource) in enumerate(entry_identities):
        profiles = entry_resource.get("meta", {}).get("profile", [])
        claims_profile = (
            isinstance(profiles, list)
            and PROVIDER_CONVERSION_PROVENANCE_PROFILE in profiles
        )
        if system == PROVIDER_CONVERSION_ID:
            if not V1_DIGEST.match(value):
                raise ProducerValidationError(
                    f"{label} entry[{index}] provider conversion identifier is not "
                    "a v1 digest"
                )
            if not claims_profile:
                raise ProducerValidationError(
                    f"{label} entry[{index}] uses the provider conversion "
                    "namespace without claiming the provider conversion "
                    "provenance profile"
                )
            conversion_values.append(value)
        elif claims_profile:
            raise ProducerValidationError(
                f"{label} entry[{index}] claims the provider conversion "
                "provenance profile without the provider conversion namespace"
            )
    if not conversion_values:
        return
    identifier = bundle.get("identifier", {})
    if identifier.get("system") != PROVIDER_EXCHANGE_ID or not V1_DIGEST.match(
        str(identifier.get("value"))
    ):
        raise ProducerValidationError(
            f"{label} provider exchange Bundle.identifier must be a v1 digest in "
            "the provider exchange namespace"
        )
    if len(conversion_values) != len(set(conversion_values)):
        raise ProducerValidationError(
            f"{label} repeats a provider conversion identifier value"
        )
    if len(conversion_values) == 1 and identifier.get("value") != conversion_values[0]:
        raise ProducerValidationError(
            f"{label} single-conversion exchange identifier must equal the "
            "conversion identifier byte for byte"
        )


def validate_exchange_bundle(
    resource: dict[str, Any],
    label: str,
    active_adapter_profiles: set[str] | None = None,
) -> None:
    profiles = resource.get("meta", {}).get("profile", [])
    if EXCHANGE_BUNDLE_PROFILE not in profiles:
        return
    if resource.get("type") != "collection":
        raise ProducerValidationError(f"{label} exchange Bundle must have type collection")
    complete_identifier(resource.get("identifier"), f"{label} Bundle.identifier")
    entries = resource.get("entry")
    if not isinstance(entries, list) or not entries:
        raise ProducerValidationError(f"{label} exchange Bundle must contain entries")
    full_urls: set[str] = set()
    internal_logical_references: set[str] = set()
    entry_resources: list[dict[str, Any]] = []
    entry_identities: list[tuple[str, str, dict[str, Any]]] = []
    resources_by_full_url: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
            raise ProducerValidationError(f"{label} entry[{index}] must contain a resource")
        extensions = entry.get("extension", [])
        identities = [
            extension.get("valueIdentifier")
            for extension in extensions
            if isinstance(extension, dict) and extension.get("url") == ENTRY_IDENTIFIER_EXTENSION
        ] if isinstance(extensions, list) else []
        if len(identities) != 1:
            raise ProducerValidationError(f"{label} entry[{index}] must have one entry identifier")
        system, value = complete_identifier(identities[0], f"{label} entry[{index}] identity")
        expected = expected_entry_full_url(system, value)
        if entry.get("fullUrl") != expected:
            raise ProducerValidationError(f"{label} entry[{index}] fullUrl is not the deterministic UUID URN")
        if expected in full_urls:
            raise ProducerValidationError(f"{label} repeats entry fullUrl {expected}")
        full_urls.add(expected)
        entry_resource = entry["resource"]
        validate_resource_profile_claims(
            entry_resource,
            f"{label} entry[{index}].resource",
            active_adapter_profiles,
        )
        entry_resources.append(entry_resource)
        entry_identities.append((system, value, entry_resource))
        resources_by_full_url[expected] = entry_resource
        resource_type = entry_resource.get("resourceType")
        resource_id = entry_resource.get("id")
        if isinstance(resource_type, str) and isinstance(resource_id, str):
            internal_logical_references.add(f"{resource_type}/{resource_id}")
    for reference in all_references(entry_resources):
        if reference.startswith("urn:uuid:") and reference not in full_urls:
            raise ProducerValidationError(f"{label} has unresolved internal UUID reference {reference}")
        if reference in internal_logical_references:
            raise ProducerValidationError(f"{label} internal entry reference must use its UUID URN: {reference}")

    validate_adapter_provenance_graph(entry_resources, resources_by_full_url, label)
    validate_provider_exchange_identity(resource, entry_identities, label)

    sensorkit_hybrid_profiles = {
        (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-device-usage-observation"
        ): "device-usage",
        (
            "https://grovealliance.org/fhir/sensorkit/StructureDefinition/"
            "sensorkit-ecg-observation"
        ): "ECG",
    }
    sensorkit_record_system = (
        "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-record-id"
    )
    full_url_by_resource = {
        id(entry_resource): full_url
        for full_url, entry_resource in resources_by_full_url.items()
    }
    for index, observation in enumerate(entry_resources):
        direct_profiles = observation.get("meta", {}).get("profile", [])
        matches = [
            (profile, name)
            for profile, name in sensorkit_hybrid_profiles.items()
            if profile in direct_profiles
        ] if isinstance(direct_profiles, list) else []
        if not matches:
            continue
        _, graph_name = matches[0]
        derived_from = observation.get("derivedFrom")
        if not isinstance(derived_from, list) or len(derived_from) != 1:
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} entry[{index}] must derive from "
                "exactly one native Recording Document"
            )
        reference = derived_from[0].get("reference") if isinstance(derived_from[0], dict) else None
        document = resources_by_full_url.get(reference) if isinstance(reference, str) else None
        if not isinstance(document, dict) or document.get("resourceType") != "DocumentReference":
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} entry[{index}] must reference its "
                "native Recording Document in the same Bundle"
            )

        def matching_identifier(candidate: dict[str, Any]) -> tuple[str, str] | None:
            identifiers = candidate.get("identifier", [])
            if not isinstance(identifiers, list):
                return None
            matches = [
                identifier for identifier in identifiers
                if isinstance(identifier, dict)
                and identifier.get("system") == sensorkit_record_system
            ]
            if len(matches) != 1:
                return None
            return complete_identifier(matches[0], "SensorKit source-record identifier")

        observation_identity = matching_identifier(observation)
        document_identity = matching_identifier(document)
        if (
            observation_identity is None
            or document_identity is None
            or observation_identity != document_identity
        ):
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} Observation and native document must "
                "carry the same source-record identifier"
            )
        related = document.get("context", {}).get("related", [])
        observation_url = full_url_by_resource[id(observation)]
        related_urls = [
            item.get("reference")
            for item in related
            if isinstance(item, dict)
        ] if isinstance(related, list) else []
        if related_urls != [observation_url]:
            raise ProducerValidationError(
                f"{label} SensorKit {graph_name} native document must relate back to "
                "exactly its structured Observation"
            )

    health_connect = read_json(CATALOG_ROOT / "health-connect-adapter.json")
    glucose_by_profile = {
        measurement["profile"]: measurement
        for measurement in health_connect.get("adapterMeasurements", [])
    }
    for index, observation in enumerate(entry_resources):
        direct_profiles = observation.get("meta", {}).get("profile", [])
        matches = [
            glucose_by_profile[profile]
            for profile in direct_profiles
            if profile in glucose_by_profile
        ] if isinstance(direct_profiles, list) else []
        if not matches:
            continue
        measurement = matches[0]
        specimens = observation.get("specimen")
        reference = specimens.get("reference") if isinstance(specimens, dict) else None
        specimen = resources_by_full_url.get(reference) if isinstance(reference, str) else None
        if not isinstance(specimen, dict) or specimen.get("resourceType") != "Specimen":
            raise ProducerValidationError(
                f"{label} Health Connect glucose entry[{index}] must reference its "
                "synthesized Specimen in the same Bundle"
            )
        admitted = (
            [measurement["specimen"]]
            if "specimen" in measurement
            else measurement["specimenAlternatives"]
        )
        admitted_pairs = {(item["system"], item["code"]) for item in admitted}
        codings = specimen.get("type", {}).get("coding", [])
        actual_pairs = {
            (coding.get("system"), coding.get("code"))
            for coding in codings
            if isinstance(coding, dict)
        } if isinstance(codings, list) else set()
        if len(actual_pairs & admitted_pairs) != 1:
            raise ProducerValidationError(
                f"{label} Health Connect glucose entry[{index}] Specimen meaning "
                "does not match its exact adapter-specific profile"
            )


def validate_mobile_semantic_vectors(
    bindings: Any,
    resources_by_path: dict[str, dict[str, Any]],
) -> None:
    """Require one exact vector fixture for every shared Mobile meaning in scope."""
    if not isinstance(bindings, list):
        raise ProducerValidationError("semanticVectors must be an array")
    corpus = read_json(
        REPOSITORY_ROOT / "Conformance/corpora/mobile-semantics/corpus.json"
    )
    vectors = {vector["id"]: vector for vector in corpus["vectors"]}
    profile_to_id = {vector["profile"]: vector_id for vector_id, vector in vectors.items()}

    observed: set[str] = set()
    for root_resource in resources_by_path.values():
        for resource in nested_fhir_resources(root_resource):
            profiles = resource.get("meta", {}).get("profile", [])
            if isinstance(profiles, list):
                observed.update(
                    profile_to_id[profile]
                    for profile in profiles
                    if profile in profile_to_id
                )

    bound: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"semanticVectors[{index}]"
        if not isinstance(binding, dict):
            raise ProducerValidationError(f"{label} must be an object")
        require_keys(binding, {"id", "path", "resourcePointer"}, label)
        if set(binding) != {"id", "path", "resourcePointer"}:
            raise ProducerValidationError(f"{label} is incomplete")
        vector_id = binding["id"]
        if not isinstance(vector_id, str) or vector_id not in vectors:
            raise ProducerValidationError(f"{label} names an unknown Mobile semantic vector")
        if vector_id in bound:
            raise ProducerValidationError(
                f"Mobile semantic vector {vector_id} is bound more than once"
            )
        resource_path = binding["path"]
        if not isinstance(resource_path, str) or resource_path not in resources_by_path:
            raise ProducerValidationError(
                f"{label}.path must name a declared producer resource"
            )
        selected = json_pointer(
            resources_by_path[resource_path],
            binding["resourcePointer"],
            f"{label}.resourcePointer",
        )
        vector = vectors[vector_id]
        actual = mobile_semantic_projection(selected, vector, label)
        expected = {
            key: vector[key] for key in ("profile", "code", "effective", "result")
        }
        if actual != expected:
            raise ProducerValidationError(
                f"{label} clinical projection does not equal Mobile semantic vector {vector_id}"
            )
        bound.add(vector_id)

    if bound != observed:
        missing = sorted(observed - bound)
        extra = sorted(bound - observed)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("not present " + ", ".join(extra))
        raise ProducerValidationError(
            "semanticVectors must cover exactly the shared Mobile measurements present: "
            + "; ".join(details)
        )


def validate_manifest(path: Path) -> tuple[dict[str, Any], list[Path]]:
    manifest = read_json(path)
    if not isinstance(manifest, dict):
        raise ProducerValidationError("manifest must be a JSON object")
    require_keys(manifest, TOP_LEVEL_KEYS, "manifest")
    if set(manifest) != TOP_LEVEL_KEYS:
        raise ProducerValidationError("manifest is missing required fields")
    if manifest["schemaVersion"] != 1 or manifest["fhirVersion"] != "4.0.1":
        raise ProducerValidationError("manifest must declare schemaVersion 1 and FHIR 4.0.1")

    producer = manifest["producer"]
    if not isinstance(producer, dict):
        raise ProducerValidationError("producer must be an object")
    require_keys(producer, {"name", "version", "revision"}, "producer")
    if not all(isinstance(producer.get(key), str) and producer[key] for key in ("name", "version")):
        raise ProducerValidationError("producer name and version must be non-empty strings")
    if "revision" in producer and (not isinstance(producer["revision"], str) or not producer["revision"]):
        raise ProducerValidationError("producer revision must be a non-empty string")

    packages = manifest["packages"]
    if not isinstance(packages, list) or not packages:
        raise ProducerValidationError("packages must be a non-empty array")
    aliases: set[str] = set()
    package_ids: set[str] = set()
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise ProducerValidationError(f"packages[{index}] must be an object")
        require_keys(package, {"alias", "packageId", "version"}, f"packages[{index}]")
        if set(package) != {"alias", "packageId", "version"}:
            raise ProducerValidationError(f"packages[{index}] is incomplete")
        alias = package["alias"]
        package_id = package["packageId"]
        if not isinstance(alias, str) or not PACKAGE_ALIAS.fullmatch(alias):
            raise ProducerValidationError(f"invalid package alias: {alias!r}")
        if not isinstance(package_id, str) or not PACKAGE_ID.fullmatch(package_id):
            raise ProducerValidationError(f"invalid package id: {package_id!r}")
        if package["version"] != "0.3.0":
            raise ProducerValidationError("Grove FHIR producer manifests must use package version 0.3.0")
        if alias in aliases or package_id in package_ids:
            raise ProducerValidationError("package aliases and ids must be unique")
        aliases.add(alias)
        package_ids.add(package_id)

    active_adapter_profiles = {
        profile
        for package_id in package_ids
        if package_id in ADAPTER_PACKAGE_PROFILES
        for profile in ADAPTER_PACKAGE_PROFILES[package_id]
    }

    resources = manifest["resources"]
    if not isinstance(resources, list) or not resources:
        raise ProducerValidationError("resources must be a non-empty array")
    paths: list[Path] = []
    resources_by_path: dict[str, dict[str, Any]] = {}
    relative_paths: set[str] = set()
    for index, entry in enumerate(resources):
        if not isinstance(entry, dict):
            raise ProducerValidationError(f"resources[{index}] must be an object")
        require_keys(entry, {"path", "requiredProfiles"}, f"resources[{index}]")
        if set(entry) != {"path", "requiredProfiles"}:
            raise ProducerValidationError(f"resources[{index}] is incomplete")
        relative = entry["path"]
        if relative in relative_paths:
            raise ProducerValidationError(f"duplicate resource path: {relative}")
        relative_paths.add(relative)
        resource_path = safe_resource_path(path.parent, relative)
        resource = read_json(resource_path)
        if not isinstance(resource, dict) or not isinstance(resource.get("resourceType"), str):
            raise ProducerValidationError(f"{relative} is not a FHIR resource")
        required = entry["requiredProfiles"]
        if (
            not isinstance(required, list)
            or not required
            or any(not isinstance(profile, str) or not profile.startswith(GROVE_PROFILE) for profile in required)
            or len(required) != len(set(required))
        ):
            raise ProducerValidationError(f"{relative} has invalid requiredProfiles")
        actual = resource.get("meta", {}).get("profile", []) if isinstance(resource.get("meta"), dict) else []
        if not isinstance(actual, list) or any(not isinstance(profile, str) for profile in actual):
            raise ProducerValidationError(f"{relative} has invalid meta.profile")
        missing = set(required) - set(actual)
        if missing:
            raise ProducerValidationError(f"{relative} is missing required profiles: {', '.join(sorted(missing))}")
        actual_grove_profiles = {
            profile for profile in actual if profile.startswith(GROVE_PROFILE)
        }
        if set(required) != actual_grove_profiles:
            hidden = actual_grove_profiles - set(required)
            raise ProducerValidationError(
                f"{relative} requiredProfiles must equal its direct Grove meta.profile set; "
                f"unlisted: {', '.join(sorted(hidden))}"
            )
        validate_resource_profile_claims(resource, relative, active_adapter_profiles)
        validate_exchange_bundle(resource, relative, active_adapter_profiles)
        resources_by_path[relative] = resource
        paths.append(resource_path)
    validate_mobile_semantic_vectors(manifest["semanticVectors"], resources_by_path)
    return manifest, paths


def package_metadata(path: Path) -> dict[str, Any]:
    path = resolve_unlinked_regular_file(path, "package")
    try:
        with tarfile.open(path, "r:gz") as archive:
            member = archive.extractfile("package/package.json")
            if member is None:
                raise ProducerValidationError(f"package has no package/package.json: {path}")
            return json.load(member, object_pairs_hook=unique_object)
    except (tarfile.TarError, OSError, json.JSONDecodeError) as error:
        raise ProducerValidationError(f"cannot read package {path}: {error}") from error


def parse_package_arguments(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        alias, separator, raw_path = value.partition("=")
        if not separator or not PACKAGE_ALIAS.fullmatch(alias) or not raw_path:
            raise ProducerValidationError(f"--package must be alias=path: {value!r}")
        if alias in result:
            raise ProducerValidationError(f"duplicate --package alias: {alias}")
        result[alias] = resolve_unlinked_regular_file(
            Path(raw_path), f"{alias} package"
        )
    return result


def validate_packages(manifest: dict[str, Any], supplied: dict[str, Path]) -> list[Path]:
    expected = {entry["alias"]: entry for entry in manifest["packages"]}
    if supplied.keys() != expected.keys():
        missing = expected.keys() - supplied.keys()
        extra = supplied.keys() - expected.keys()
        details = [*(f"missing {item}" for item in sorted(missing)), *(f"unexpected {item}" for item in sorted(extra))]
        raise ProducerValidationError("package arguments do not match manifest: " + ", ".join(details))
    paths: list[Path] = []
    for alias, declaration in expected.items():
        path = supplied[alias]
        metadata = package_metadata(path)
        if metadata.get("name") != declaration["packageId"] or metadata.get("version") != declaration["version"]:
            raise ProducerValidationError(f"{alias} package identity/version does not match the manifest")
        fhir_versions = metadata.get("fhirVersions")
        if fhir_versions != ["4.0.1"]:
            raise ProducerValidationError(f"{alias} package must declare only FHIR 4.0.1")
        paths.append(path)
    return paths


def validator_outcomes(
    value: Any, resources: list[Path]
) -> list[tuple[Path, dict[str, Any]]]:
    """Require Validator's exact one-input or ordered multi-input output shape."""
    if not isinstance(value, dict):
        raise ProducerValidationError("FHIR Validator output must be a JSON resource")
    if len(resources) == 1:
        if value.get("resourceType") != "OperationOutcome":
            raise ProducerValidationError(
                "one-input FHIR Validator output must be one OperationOutcome"
            )
        outcomes = [value]
    else:
        if value.get("resourceType") != "Bundle" or value.get("type") != "collection":
            raise ProducerValidationError(
                "multi-input FHIR Validator output must be a collection Bundle"
            )
        entries = value.get("entry")
        if not isinstance(entries, list) or len(entries) != len(resources):
            actual = len(entries) if isinstance(entries, list) else "invalid"
            raise ProducerValidationError(
                "FHIR Validator output count does not match inputs: "
                f"{actual} != {len(resources)}"
            )
        outcomes = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or set(entry) != {"resource"}:
                raise ProducerValidationError(
                    f"FHIR Validator output Bundle entry[{index}] must contain only resource"
                )
            outcome = entry["resource"]
            if not isinstance(outcome, dict) or outcome.get("resourceType") != "OperationOutcome":
                raise ProducerValidationError(
                    f"FHIR Validator output Bundle entry[{index}] is not one OperationOutcome"
                )
            outcomes.append(outcome)

    result: list[tuple[Path, dict[str, Any]]] = []
    for index, (resource, outcome) in enumerate(zip(resources, outcomes, strict=True)):
        extensions = outcome.get("extension", [])
        matches = [
            extension.get("valueString")
            for extension in extensions
            if isinstance(extension, dict)
            and extension.get("url") == VALIDATOR_FILE_EXTENSION
        ] if isinstance(extensions, list) else []
        if matches != [str(resource)]:
            raise ProducerValidationError(
                f"FHIR Validator output[{index}] file attribution does not match input "
                f"{resource}"
            )
        result.append((resource, outcome))
    return result


def reject_validator_errors(outcome: dict[str, Any], label: str) -> None:
    errors: list[str] = []
    issues = outcome.get("issue")
    if not isinstance(issues, list) or not issues:
        raise ProducerValidationError(
            f"FHIR Validator OperationOutcome has no populated issue array for {label}"
        )
    for issue_index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ProducerValidationError(
                f"FHIR Validator OperationOutcome.issue[{issue_index}] is invalid for {label}"
            )
        severity = issue.get("severity")
        if severity not in {"fatal", "error", "warning", "information"}:
            raise ProducerValidationError(
                f"FHIR Validator issue has invalid severity for {label}: {severity!r}"
            )
        if severity in {"fatal", "error"}:
            diagnostics = issue.get("diagnostics")
            if not isinstance(diagnostics, str) or not diagnostics:
                details = issue.get("details")
                diagnostics = details.get("text") if isinstance(details, dict) else None
            errors.append(
                diagnostics
                if isinstance(diagnostics, str) and diagnostics
                else "unspecified validation error"
            )
    if errors:
        raise ProducerValidationError(
            f"FHIR Validator rejected {label}: " + " | ".join(errors)
        )


def truncated_validator_log(value: str | None) -> str:
    """Return a bounded, printable process log for a terminal infrastructure failure."""
    if not value:
        return "<empty>"
    normalized = value.replace("\x00", "\\0").strip()
    if len(normalized) <= VALIDATOR_LOG_LIMIT:
        return normalized
    return "…" + normalized[-VALIDATOR_LOG_LIMIT:]


def run_validator(validator: Path, packages: list[Path], resources: list[Path]) -> None:
    validator = resolve_unlinked_regular_file(validator, "Validator JAR")
    packages = [
        resolve_unlinked_regular_file(package, "FHIR package")
        for package in packages
    ]
    fhir_tool_home = resolve_unlinked_directory(FHIR_TOOL_HOME, "private FHIR home")
    resolve_unlinked_directory(
        fhir_tool_home / ".fhir" / "packages", "private FHIR package cache"
    )
    ordered_resources = sorted(resources, key=lambda path: path.as_posix())
    with tempfile.TemporaryDirectory(prefix="grove-fhir-producer-") as directory:
        output = Path(directory) / "operation-outcomes.json"
        command = [
            "java", f"-Duser.home={fhir_tool_home}", "-jar", str(validator),
            "-version", "4.0.1",
            "-tx", "n/a",
            "-no-http-access",
            "-level", "errors",
        ]
        for package in packages:
            command.extend(("-ig", str(package)))
        command.extend(("-output", str(output)))
        command.extend(str(resource) for resource in ordered_resources)

        last_failure = ""
        for attempt in range(1, VALIDATOR_ATTEMPTS + 1):
            if output.exists() or output.is_symlink():
                output.unlink()
            result = subprocess.run(
                command,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            process_log = truncated_validator_log(result.stdout)
            if not output.is_file() or output.is_symlink():
                last_failure = (
                    "FHIR Validator produced no trustworthy OperationOutcome output "
                    f"(exit {result.returncode}); log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure)
            try:
                parsed = read_json(output)
                outcomes = validator_outcomes(parsed, ordered_resources)
            except ProducerValidationError as error:
                last_failure = (
                    f"untrustworthy FHIR Validator output: {error} "
                    f"(exit {result.returncode}); log: {process_log}"
                )
                if attempt < VALIDATOR_ATTEMPTS:
                    continue
                raise ProducerValidationError(last_failure) from error

            # A real FHIR fatal/error is final and is never retried or ignored.
            for resource, outcome in outcomes:
                reject_validator_errors(outcome, resource.name)
            if result.returncode == 0:
                return
            last_failure = (
                "FHIR Validator process failed after producing only error-free, correctly "
                f"attributed OperationOutcomes (exit {result.returncode}); log: {process_log}"
            )
            if attempt == VALIDATOR_ATTEMPTS:
                raise ProducerValidationError(last_failure)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--validator", type=Path)
    parser.add_argument("--structural-only", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        manifest_path = resolve_unlinked_regular_file(arguments.manifest, "manifest")
        manifest, resources = validate_manifest(manifest_path)
        if arguments.structural_only:
            if arguments.package or arguments.validator is not None:
                raise ProducerValidationError("--structural-only cannot be combined with package or Validator arguments")
        else:
            if arguments.validator is None:
                raise ProducerValidationError("--validator is required unless --structural-only is used")
            supplied = parse_package_arguments(arguments.package)
            packages = validate_packages(manifest, supplied)
            run_validator(arguments.validator, packages, resources)
    except ProducerValidationError as error:
        print(f"Producer conformance failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(resources)} producer resource(s) against FHIR R4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
