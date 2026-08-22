<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative Health Connect status matrix

This table is the complete, closed AndroidX Health Connect 1.1.0 `RecordType.all` inventory. Each of the 41 record classes has exactly one definitive v0.3.0 status. An empty output cell means this release admits no FHIR producer output for that class; it is not an implementation queue.

| Record class | Status | Admitted output(s) | Exact context mapping(s) |
| --- | --- | --- | --- |
| `ActiveCaloriesBurnedRecord` | `supported` | active-energy (1) | — |
| `BasalBodyTemperatureRecord` | `supported` | basal-body-temperature (1) | `temperatureMeasurementLocation` |
| `BasalMetabolicRateRecord` | `supported` | basal-metabolic-rate (0..*; one per record) | — |
| `BloodGlucoseRecord` | `supported` | blood-glucose (1; SPECIMEN_SOURCE_WHOLE_BLOOD); capillary-blood-glucose (1; SPECIMEN_SOURCE_CAPILLARY_BLOOD); serum-plasma-glucose (1; SPECIMEN_SOURCE_PLASMA or SPECIMEN_SOURCE_SERUM); interstitial-glucose (1; SPECIMEN_SOURCE_INTERSTITIAL_FLUID) | `bloodGlucoseSpecimen`; `bloodGlucoseMealContext` |
| `BloodPressureRecord` | `supported` | blood-pressure (1) | `bloodPressureBodyPosition`; `bloodPressureMeasurementLocation` |
| `BodyFatRecord` | `supported` | body-fat-percentage (0..*; one per record) | — |
| `BodyTemperatureRecord` | `supported` | body-temperature (1) | `temperatureMeasurementLocation` |
| `BodyWaterMassRecord` | `supported` | body-water-mass (0..*; one per record) | — |
| `BoneMassRecord` | `supported` | bone-mass (0..*; one per record) | — |
| `CervicalMucusRecord` | `supported` | cervical-mucus-quality (0..*; one per record) | — |
| `CyclingPedalingCadenceRecord` | `supported` | cycling-cadence (0..*; one per record) | — |
| `DistanceRecord` | `supported` | distance (1) | — |
| `ElevationGainedRecord` | `supported` | elevation-gained (0..*; one per record) | — |
| `ExerciseSessionRecord` | `supported` | workout (0..*; one per record); workout-segment (0..*; one per segment) | — |
| `FloorsClimbedRecord` | `supported` | flights-climbed (0..*; one per record) | — |
| `HeartRateRecord` | `supported` | heart-rate (0..*; one per sample) | — |
| `HeartRateVariabilityRmssdRecord` | `supported` | heart-rate-variability-rmssd (0..*; one per record) | — |
| `HeightRecord` | `supported` | body-height (1) | — |
| `HydrationRecord` | `supported` | fluid-intake (0..*; one per record) | — |
| `IntermenstrualBleedingRecord` | `supported` | intermenstrual-bleeding (0..*; one per record) | — |
| `LeanBodyMassRecord` | `supported` | lean-body-mass (0..*; one per record) | — |
| `MenstruationFlowRecord` | `supported` | menstruation-flow (0..*; one per record) | — |
| `MenstruationPeriodRecord` | `supported` | menstruation-period (0..*; one per record) | — |
| `MindfulnessSessionRecord` | `supported` | mindfulness-session (0..*; one per record) | — |
| `NutritionRecord` | `supported` | dietary-biotin (0..*; one per record); dietary-caffeine (0..1; one per record); dietary-calcium (0..1; one per record); dietary-carbohydrates (0..1; one per record); dietary-chloride (0..1; one per record); dietary-cholesterol (0..1; one per record); dietary-chromium (0..1; one per record); dietary-copper (0..1; one per record); dietary-energy (0..1; one per record); dietary-energy-from-fat (0..1; one per record); dietary-fat-monounsaturated (0..1; one per record); dietary-fat-polyunsaturated (0..1; one per record); dietary-fat-saturated (0..1; one per record); dietary-fat-total (0..1; one per record); dietary-fat-trans (0..1; one per record); dietary-fat-unsaturated (0..1; one per record); dietary-fiber (0..1; one per record); dietary-folate (0..1; one per record); dietary-folic-acid (0..1; one per record); dietary-iodine (0..1; one per record); dietary-iron (0..1; one per record); dietary-magnesium (0..1; one per record); dietary-manganese (0..1; one per record); dietary-molybdenum (0..1; one per record); dietary-niacin (0..1; one per record); dietary-pantothenic-acid (0..1; one per record); dietary-phosphorus (0..1; one per record); dietary-potassium (0..1; one per record); dietary-protein (0..1; one per record); dietary-riboflavin (0..1; one per record); dietary-selenium (0..1; one per record); dietary-sodium (0..1; one per record); dietary-sugar (0..1; one per record); dietary-thiamin (0..1; one per record); dietary-vitamin-a (0..1; one per record); dietary-vitamin-b12 (0..1; one per record); dietary-vitamin-b6 (0..1; one per record); dietary-vitamin-c (0..1; one per record); dietary-vitamin-d (0..1; one per record); dietary-vitamin-e (0..1; one per record); dietary-vitamin-k (0..1; one per record); dietary-zinc (0..1; one per record) | — |
| `OvulationTestRecord` | `supported` | ovulation-test-result (0..*; one per record) | — |
| `OxygenSaturationRecord` | `supported` | oxygen-saturation (1) | — |
| `PlannedExerciseSessionRecord` | `deferred` | — | — |
| `PowerRecord` | `supported` | power (0..*; one per record) | — |
| `RespiratoryRateRecord` | `supported` | respiratory-rate (1) | — |
| `RestingHeartRateRecord` | `supported` | resting-heart-rate (0..*; one per record) | — |
| `SexualActivityRecord` | `supported` | sexual-activity (0..*; one per record) | — |
| `SkinTemperatureRecord` | `supported` | skin-temperature (0..*; one per record) | — |
| `SleepSessionRecord` | `supported` | sleep-duration (1); sleep-stage (0..*; one per stage) | `sleepStage`; `sleepTitle`; `sleepNotes` |
| `SpeedRecord` | `supported` | speed (0..*; one per record) | — |
| `StepsCadenceRecord` | `supported` | step-cadence (0..*; one per record) | — |
| `StepsRecord` | `supported` | step-count (1) | — |
| `TotalCaloriesBurnedRecord` | `supported` | total-energy (0..*; one per record) | — |
| `Vo2MaxRecord` | `supported` | vo2-max (0..*; one per record) | — |
| `WeightRecord` | `supported` | body-weight (1) | — |
| `WheelchairPushesRecord` | `supported` | wheelchair-push-count (0..*; one per record) | — |
