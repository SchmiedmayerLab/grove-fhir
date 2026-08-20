<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative Health Connect status matrix

This table is the complete, closed AndroidX Health Connect 1.1.0 `RecordType.all` inventory. Each of the 41 record classes has exactly one definitive v0.2.0 status. An empty output cell means this release admits no FHIR producer output for that class; it is not an implementation queue.

| Record class | Status | Admitted output(s) | Exact context mapping(s) |
| --- | --- | --- | --- |
| `ActiveCaloriesBurnedRecord` | `supported` | active-energy (1) | — |
| `BasalBodyTemperatureRecord` | `supported` | basal-body-temperature (1) | `temperatureMeasurementLocation` |
| `BasalMetabolicRateRecord` | `deferred` | — | — |
| `BloodGlucoseRecord` | `supported` | blood-glucose (1; SPECIMEN_SOURCE_WHOLE_BLOOD); capillary-blood-glucose (1; SPECIMEN_SOURCE_CAPILLARY_BLOOD); serum-plasma-glucose (1; SPECIMEN_SOURCE_PLASMA or SPECIMEN_SOURCE_SERUM); interstitial-glucose (1; SPECIMEN_SOURCE_INTERSTITIAL_FLUID) | `bloodGlucoseSpecimen`; `bloodGlucoseMealContext` |
| `BloodPressureRecord` | `supported` | blood-pressure (1) | `bloodPressureBodyPosition`; `bloodPressureMeasurementLocation` |
| `BodyFatRecord` | `deferred` | — | — |
| `BodyTemperatureRecord` | `supported` | body-temperature (1) | `temperatureMeasurementLocation` |
| `BodyWaterMassRecord` | `deferred` | — | — |
| `BoneMassRecord` | `deferred` | — | — |
| `CervicalMucusRecord` | `deferred` | — | — |
| `CyclingPedalingCadenceRecord` | `deferred` | — | — |
| `DistanceRecord` | `supported` | distance (1) | — |
| `ElevationGainedRecord` | `deferred` | — | — |
| `ExerciseSessionRecord` | `deferred` | — | — |
| `FloorsClimbedRecord` | `deferred` | — | — |
| `HeartRateRecord` | `supported` | heart-rate (0..*; one per sample) | — |
| `HeartRateVariabilityRmssdRecord` | `deferred` | — | — |
| `HeightRecord` | `supported` | body-height (1) | — |
| `HydrationRecord` | `deferred` | — | — |
| `IntermenstrualBleedingRecord` | `deferred` | — | — |
| `LeanBodyMassRecord` | `deferred` | — | — |
| `MenstruationFlowRecord` | `deferred` | — | — |
| `MenstruationPeriodRecord` | `deferred` | — | — |
| `MindfulnessSessionRecord` | `deferred` | — | — |
| `NutritionRecord` | `deferred` | — | — |
| `OvulationTestRecord` | `deferred` | — | — |
| `OxygenSaturationRecord` | `supported` | oxygen-saturation (1) | — |
| `PlannedExerciseSessionRecord` | `deferred` | — | — |
| `PowerRecord` | `deferred` | — | — |
| `RespiratoryRateRecord` | `supported` | respiratory-rate (1) | — |
| `RestingHeartRateRecord` | `deferred` | — | — |
| `SexualActivityRecord` | `deferred` | — | — |
| `SkinTemperatureRecord` | `deferred` | — | — |
| `SleepSessionRecord` | `supported` | sleep-duration (1); sleep-stage (0..*; one per stage) | `sleepStage`; `sleepTitle`; `sleepNotes` |
| `SpeedRecord` | `deferred` | — | — |
| `StepsCadenceRecord` | `deferred` | — | — |
| `StepsRecord` | `supported` | step-count (1) | — |
| `TotalCaloriesBurnedRecord` | `deferred` | — | — |
| `Vo2MaxRecord` | `deferred` | — | — |
| `WeightRecord` | `supported` | body-weight (1) | — |
| `WheelchairPushesRecord` | `deferred` | — | — |
