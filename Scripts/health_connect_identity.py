"""Health Connect 1.1 identity composition for Grove FHIR 0.3.0."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re


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


SEPARATOR = "|"
SCHEME = "v1"


def compose(*components: str) -> str:
    """Join components behind the scheme version. Nothing is hashed, escaped, or re-encoded."""
    return SCHEME + ":" + SEPARATOR.join(_component(component) for component in components)


def _component(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise HealthConnectIdentityError("an identity component must be a non-empty string")
    if SEPARATOR in value:
        raise HealthConnectIdentityError(
            "an identity component must not contain a vertical bar; such a value is rejected, never escaped"
        )
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        raise HealthConnectIdentityError("identity input contains an invalid Unicode surrogate")
    return value


def _scoped_record(repository_scope: str, record_type: str, raw_record_id: str) -> tuple[str, str, str]:
    if not UUID.fullmatch(repository_scope):
        raise HealthConnectIdentityError("repository scope must be lowercase UUID text")
    if record_type not in RECORD_TYPES:
        raise HealthConnectIdentityError("record type is not in the closed Health Connect 1.1 inventory")
    if not raw_record_id:
        raise HealthConnectIdentityError("raw record id must not be empty")
    return repository_scope, record_type, raw_record_id


def record(repository_scope: str, record_type: str, raw_record_id: str) -> str:
    return compose(*_scoped_record(repository_scope, record_type, raw_record_id))


NUTRIENT_TOKENS = frozenset({
    "dietary-biotin",
    "dietary-caffeine",
    "dietary-calcium",
    "dietary-carbohydrates",
    "dietary-chloride",
    "dietary-cholesterol",
    "dietary-chromium",
    "dietary-copper",
    "dietary-energy",
    "dietary-energy-from-fat",
    "dietary-fat-monounsaturated",
    "dietary-fat-polyunsaturated",
    "dietary-fat-saturated",
    "dietary-fat-total",
    "dietary-fat-trans",
    "dietary-fat-unsaturated",
    "dietary-fiber",
    "dietary-folate",
    "dietary-folic-acid",
    "dietary-iodine",
    "dietary-iron",
    "dietary-magnesium",
    "dietary-manganese",
    "dietary-molybdenum",
    "dietary-niacin",
    "dietary-pantothenic-acid",
    "dietary-phosphorus",
    "dietary-potassium",
    "dietary-protein",
    "dietary-riboflavin",
    "dietary-selenium",
    "dietary-sodium",
    "dietary-sugar",
    "dietary-thiamin",
    "dietary-vitamin-a",
    "dietary-vitamin-b12",
    "dietary-vitamin-b6",
    "dietary-vitamin-c",
    "dietary-vitamin-d",
    "dietary-vitamin-e",
    "dietary-vitamin-k",
    "dietary-zinc",
    "fluid-intake",
})

WORKOUT_SEGMENT_TOKENS = frozenset({
    "EXERCISE_LAP",
    "EXERCISE_SEGMENT_TYPE_ARM_CURL",
    "EXERCISE_SEGMENT_TYPE_BACK_EXTENSION",
    "EXERCISE_SEGMENT_TYPE_BALL_SLAM",
    "EXERCISE_SEGMENT_TYPE_BARBELL_SHOULDER_PRESS",
    "EXERCISE_SEGMENT_TYPE_BENCH_PRESS",
    "EXERCISE_SEGMENT_TYPE_BENCH_SIT_UP",
    "EXERCISE_SEGMENT_TYPE_BIKING",
    "EXERCISE_SEGMENT_TYPE_BIKING_STATIONARY",
    "EXERCISE_SEGMENT_TYPE_BURPEE",
    "EXERCISE_SEGMENT_TYPE_CRUNCH",
    "EXERCISE_SEGMENT_TYPE_DEADLIFT",
    "EXERCISE_SEGMENT_TYPE_DOUBLE_ARM_TRICEPS_EXTENSION",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_LEFT_ARM",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_RIGHT_ARM",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_FRONT_RAISE",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_LATERAL_RAISE",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_ROW",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_LEFT_ARM",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_RIGHT_ARM",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_TWO_ARM",
    "EXERCISE_SEGMENT_TYPE_ELLIPTICAL",
    "EXERCISE_SEGMENT_TYPE_FORWARD_TWIST",
    "EXERCISE_SEGMENT_TYPE_FRONT_RAISE",
    "EXERCISE_SEGMENT_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING",
    "EXERCISE_SEGMENT_TYPE_HIP_THRUST",
    "EXERCISE_SEGMENT_TYPE_HULA_HOOP",
    "EXERCISE_SEGMENT_TYPE_JUMPING_JACK",
    "EXERCISE_SEGMENT_TYPE_JUMP_ROPE",
    "EXERCISE_SEGMENT_TYPE_KETTLEBELL_SWING",
    "EXERCISE_SEGMENT_TYPE_LATERAL_RAISE",
    "EXERCISE_SEGMENT_TYPE_LAT_PULL_DOWN",
    "EXERCISE_SEGMENT_TYPE_LEG_CURL",
    "EXERCISE_SEGMENT_TYPE_LEG_EXTENSION",
    "EXERCISE_SEGMENT_TYPE_LEG_PRESS",
    "EXERCISE_SEGMENT_TYPE_LEG_RAISE",
    "EXERCISE_SEGMENT_TYPE_LUNGE",
    "EXERCISE_SEGMENT_TYPE_MOUNTAIN_CLIMBER",
    "EXERCISE_SEGMENT_TYPE_OTHER_WORKOUT",
    "EXERCISE_SEGMENT_TYPE_PAUSE",
    "EXERCISE_SEGMENT_TYPE_PILATES",
    "EXERCISE_SEGMENT_TYPE_PLANK",
    "EXERCISE_SEGMENT_TYPE_PULL_UP",
    "EXERCISE_SEGMENT_TYPE_PUNCH",
    "EXERCISE_SEGMENT_TYPE_REST",
    "EXERCISE_SEGMENT_TYPE_ROWING_MACHINE",
    "EXERCISE_SEGMENT_TYPE_RUNNING",
    "EXERCISE_SEGMENT_TYPE_RUNNING_TREADMILL",
    "EXERCISE_SEGMENT_TYPE_SHOULDER_PRESS",
    "EXERCISE_SEGMENT_TYPE_SINGLE_ARM_TRICEPS_EXTENSION",
    "EXERCISE_SEGMENT_TYPE_SIT_UP",
    "EXERCISE_SEGMENT_TYPE_SQUAT",
    "EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING",
    "EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING_MACHINE",
    "EXERCISE_SEGMENT_TYPE_STRETCHING",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_BACKSTROKE",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_BREASTSTROKE",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_BUTTERFLY",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_FREESTYLE",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_MIXED",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_OPEN_WATER",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_OTHER",
    "EXERCISE_SEGMENT_TYPE_SWIMMING_POOL",
    "EXERCISE_SEGMENT_TYPE_UNKNOWN",
    "EXERCISE_SEGMENT_TYPE_UPPER_TWIST",
    "EXERCISE_SEGMENT_TYPE_WALKING",
    "EXERCISE_SEGMENT_TYPE_WEIGHTLIFTING",
    "EXERCISE_SEGMENT_TYPE_WHEELCHAIR",
    "EXERCISE_SEGMENT_TYPE_YOGA",
})


def output(repository_scope: str, record_type: str, raw_record_id: str, selector: list[str]) -> str:
    scoped = _scoped_record(repository_scope, record_type, raw_record_id)
    if not selector or selector[0] not in {"single", "sample", "sleep-stage", "nutrient", "workout-segment"}:
        raise HealthConnectIdentityError("unsupported output selector")
    if selector[0] == "single" and len(selector) != 1:
        raise HealthConnectIdentityError("single output selector has no additional fields")
    if selector[0] == "sample" and len(selector) != 3:
        raise HealthConnectIdentityError("sample output selector is incomplete")
    if selector[0] == "sleep-stage" and len(selector) != 5:
        raise HealthConnectIdentityError("sleep-stage output selector is incomplete")
    if selector[0] == "nutrient" and len(selector) != 2:
        raise HealthConnectIdentityError("nutrient output selector is incomplete")
    if selector[0] == "workout-segment" and len(selector) != 5:
        raise HealthConnectIdentityError("workout-segment output selector is incomplete")
    if selector[0] not in {"single", "nutrient"} and not UNSIGNED.fullmatch(selector[-1]):
        raise HealthConnectIdentityError("output occurrence must be canonical unsigned decimal")
    if selector[0] == "sample" and not UTC9.fullmatch(selector[1]):
        raise HealthConnectIdentityError("sample instant must be canonical UTC instant with nine fractional digits")
    if selector[0] == "sleep-stage":
        if not UTC9.fullmatch(selector[1]) or not UTC9.fullmatch(selector[2]):
            raise HealthConnectIdentityError("sleep stage bounds must be canonical UTC instants with nine fractional digits")
        if selector[3] not in SLEEP_STAGE_TYPES:
            raise HealthConnectIdentityError("sleep stage token is not in the closed Health Connect 1.1 inventory")
    if selector[0] == "nutrient" and selector[1] not in NUTRIENT_TOKENS:
        raise HealthConnectIdentityError("nutrient token is not an admitted dietary measurement")
    if selector[0] == "workout-segment":
        if not UTC9.fullmatch(selector[1]) or not UTC9.fullmatch(selector[2]):
            raise HealthConnectIdentityError("workout segment bounds must be canonical UTC instants with nine fractional digits")
        if selector[3] not in WORKOUT_SEGMENT_TOKENS:
            raise HealthConnectIdentityError("workout segment token is not in the closed Health Connect 1.1 inventory")
    return compose(*scoped, *selector)


def specimen(repository_scope: str, record_type: str, raw_record_id: str, source_specimen_token: str) -> str:
    scoped = _scoped_record(repository_scope, record_type, raw_record_id)
    if source_specimen_token not in SPECIMEN_TYPES:
        raise HealthConnectIdentityError("specimen token is not admitted by the Health Connect adapter")
    return compose(*scoped, "specimen", source_specimen_token)


def writer_record(writer_package_name: str, client_record_id: str) -> str:
    """The shared writer-record identity, in the Mobile guide's namespace rather than this one."""
    return compose(writer_package_name, client_record_id)


def event(role: str, repository_scope: str, event_sequence: str) -> str:
    """A deployment-owned graph identity, minted in the deployment's namespace and so unprefixed."""
    if role not in {"conversion-provenance", "exchange-bundle"}:
        raise HealthConnectIdentityError("event role must be conversion-provenance or exchange-bundle")
    if not UUID.fullmatch(repository_scope):
        raise HealthConnectIdentityError("repository scope must be lowercase UUID text")
    if not POSITIVE.fullmatch(event_sequence):
        raise HealthConnectIdentityError("event sequence must be canonical positive decimal")
    return SEPARATOR.join(_component(part) for part in (repository_scope, event_sequence, role))
