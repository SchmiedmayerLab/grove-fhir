"""Deterministic Health Connect 1.1 identity primitives for Grove FHIR 0.2.0."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable


UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
UNSIGNED = re.compile(r"^(?:0|[1-9][0-9]*)$")
POSITIVE = re.compile(r"^[1-9][0-9]*$")
UTC9 = re.compile(
    r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])"
    r"T(?:[01][0-9]|2[0-3]):[0-5][0-9]:(?:[0-5][0-9])\.[0-9]{9}Z$"
)
RECORD_TYPES = frozenset(
    {
        "ActiveCaloriesBurnedRecord", "BasalBodyTemperatureRecord", "BasalMetabolicRateRecord",
        "BloodGlucoseRecord", "BloodPressureRecord", "BodyFatRecord", "BodyTemperatureRecord",
        "BodyWaterMassRecord", "BoneMassRecord", "CervicalMucusRecord",
        "CyclingPedalingCadenceRecord", "DistanceRecord", "ElevationGainedRecord",
        "ExerciseSessionRecord", "FloorsClimbedRecord", "HeartRateRecord",
        "HeartRateVariabilityRmssdRecord", "HeightRecord", "HydrationRecord",
        "IntermenstrualBleedingRecord", "LeanBodyMassRecord", "MenstruationFlowRecord",
        "MenstruationPeriodRecord", "MindfulnessSessionRecord", "NutritionRecord",
        "OvulationTestRecord", "OxygenSaturationRecord", "PlannedExerciseSessionRecord",
        "PowerRecord", "RespiratoryRateRecord", "RestingHeartRateRecord", "SexualActivityRecord",
        "SkinTemperatureRecord", "SleepSessionRecord", "SpeedRecord", "StepsCadenceRecord",
        "StepsRecord", "TotalCaloriesBurnedRecord", "Vo2MaxRecord", "WeightRecord",
        "WheelchairPushesRecord",
    }
)
SLEEP_STAGE_TYPES = frozenset(
    {
        "STAGE_TYPE_UNKNOWN", "STAGE_TYPE_AWAKE", "STAGE_TYPE_SLEEPING",
        "STAGE_TYPE_OUT_OF_BED", "STAGE_TYPE_LIGHT", "STAGE_TYPE_DEEP",
        "STAGE_TYPE_REM", "STAGE_TYPE_AWAKE_IN_BED",
    }
)
SPECIMEN_TYPES = frozenset(
    {
        "SPECIMEN_SOURCE_WHOLE_BLOOD", "SPECIMEN_SOURCE_CAPILLARY_BLOOD",
        "SPECIMEN_SOURCE_PLASMA", "SPECIMEN_SOURCE_SERUM",
        "SPECIMEN_SOURCE_INTERSTITIAL_FLUID",
    }
)


class HealthConnectIdentityError(ValueError):
    """A value cannot participate in the closed v1 identity grammar."""


def canonical_string(value: str) -> str:
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
            raise HealthConnectIdentityError("identity input contains an invalid Unicode surrogate")
        if character in escapes:
            output.append(escapes[character])
        elif point <= 0x1F:
            output.append(f"\\u{point:04x}")
        else:
            output.append(character)
    output.append('"')
    return "".join(output)


def canonical_json(value: Any) -> str:
    if isinstance(value, str):
        return canonical_string(value)
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(item) for item in value) + "]"
    raise HealthConnectIdentityError("identity grammar permits only arrays and strings")


def digest(value: list[Any]) -> str:
    encoded = canonical_json(value).encode("utf-8")
    return "v1:" + hashlib.sha256(encoded).hexdigest()


def identifier_set(identifiers: Iterable[tuple[str, str]]) -> list[list[str]]:
    pairs = [_identifier(identifier) for identifier in identifiers]
    pairs.sort(key=lambda pair: canonical_json(pair).encode("utf-8"))
    if len({canonical_json(pair) for pair in pairs}) != len(pairs):
        raise HealthConnectIdentityError("source Identifier set contains a duplicate tuple")
    if not pairs:
        raise HealthConnectIdentityError("source Identifier set must not be empty")
    return pairs


def _identifier(identifier: tuple[str, str]) -> list[str]:
    if len(identifier) != 2 or not all(isinstance(item, str) and item for item in identifier):
        raise HealthConnectIdentityError("source Identifier must contain a non-empty system and value")
    pair = list(identifier)
    canonical_json(pair)
    return pair


def record(repository_scope: str, record_type: str, raw_record_id: str) -> str:
    if not UUID.fullmatch(repository_scope):
        raise HealthConnectIdentityError("repository scope must be lowercase UUID text")
    if record_type not in RECORD_TYPES:
        raise HealthConnectIdentityError("record type is not in the closed Health Connect 1.1 inventory")
    if not raw_record_id:
        raise HealthConnectIdentityError("raw record id must not be empty")
    return digest(["health-connect-record-id-v1", repository_scope, record_type, raw_record_id])


def output(source: tuple[str, str], selector: list[str]) -> str:
    source_pair = _identifier(source)
    if not selector or selector[0] not in {"single", "sample", "sleep-stage"}:
        raise HealthConnectIdentityError("unsupported output selector")
    if selector[0] == "single" and len(selector) != 1:
        raise HealthConnectIdentityError("single output selector has no additional fields")
    if selector[0] == "sample" and len(selector) != 4:
        raise HealthConnectIdentityError("sample output selector is incomplete")
    if selector[0] == "sleep-stage" and len(selector) != 5:
        raise HealthConnectIdentityError("sleep-stage output selector is incomplete")
    if selector[0] != "single" and not UNSIGNED.fullmatch(selector[-1]):
        raise HealthConnectIdentityError("output occurrence must be canonical unsigned decimal")
    if selector[0] == "sample":
        if not UTC9.fullmatch(selector[1]):
            raise HealthConnectIdentityError("sample instant must be canonical UTC instant with nine fractional digits")
        if not UNSIGNED.fullmatch(selector[2]):
            raise HealthConnectIdentityError("beats per minute must be canonical unsigned decimal")
    if selector[0] == "sleep-stage":
        if not UTC9.fullmatch(selector[1]) or not UTC9.fullmatch(selector[2]):
            raise HealthConnectIdentityError("sleep stage bounds must be canonical UTC instants with nine fractional digits")
        if selector[3] not in SLEEP_STAGE_TYPES:
            raise HealthConnectIdentityError("sleep stage token is not in the closed Health Connect 1.1 inventory")
    return digest(["health-connect-output-id-v1", source_pair, *selector])


def specimen(source: tuple[str, str], source_specimen_token: str) -> str:
    if source_specimen_token not in SPECIMEN_TYPES:
        raise HealthConnectIdentityError("specimen token is not admitted by the Health Connect 0.2 adapter")
    return digest(["health-connect-specimen-id-v1", _identifier(source), source_specimen_token])


def event(role: str, sources: Iterable[tuple[str, str]], event_sequence: str) -> str:
    if role not in {"conversion", "exchange"}:
        raise HealthConnectIdentityError("event role must be conversion or exchange")
    if not POSITIVE.fullmatch(event_sequence):
        raise HealthConnectIdentityError("event sequence must be canonical positive decimal")
    return digest([f"health-connect-{role}-id-v1", identifier_set(sources), event_sequence])
