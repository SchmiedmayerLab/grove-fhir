<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

### Authoritative Health Connect status matrix

This table is the complete, closed AndroidX Health Connect 1.1.0 `RecordType.all` inventory. Each of the 41 record classes has exactly one definitive status under the Grove FHIR contracts. An empty output cell means the relevant Grove FHIR Implementation Guide admits no FHIR producer output for that class; it is not an implementation queue.

| Record class | Status | Admitted output(s) | Exact context mapping(s) |
| --- | --- | --- | --- |
| `ActiveCaloriesBurnedRecord` | `supported` | active-energy (1) | — |
| `BasalBodyTemperatureRecord` | `supported` | basal-body-temperature (1) | `temperatureMeasurementLocation` |
| `BasalMetabolicRateRecord` | `supported` | basal-metabolic-rate (1) | — |
| `BloodGlucoseRecord` | `supported` | blood-glucose (1 Observation + 1 Specimen; SPECIMEN_SOURCE_WHOLE_BLOOD); capillary-blood-glucose (1 Observation + 1 Specimen; SPECIMEN_SOURCE_CAPILLARY_BLOOD); serum-plasma-glucose (1 Observation + 1 Specimen; SPECIMEN_SOURCE_PLASMA or SPECIMEN_SOURCE_SERUM); interstitial-glucose (1 Observation + 1 Specimen; SPECIMEN_SOURCE_INTERSTITIAL_FLUID) | `bloodGlucoseSpecimen`; `bloodGlucoseMealContext` |
| `BloodPressureRecord` | `supported` | blood-pressure (1) | `bloodPressureBodyPosition`; `bloodPressureMeasurementLocation` |
| `BodyFatRecord` | `supported` | body-fat-percentage (1) | — |
| `BodyTemperatureRecord` | `supported` | body-temperature (1) | `temperatureMeasurementLocation` |
| `BodyWaterMassRecord` | `supported` | body-water-mass (1) | — |
| `BoneMassRecord` | `supported` | bone-mass (1) | — |
| `CervicalMucusRecord` | `supported` | cervical-mucus-quality (1) | `cervicalMucusAppearance`; `cervicalMucusSensation` |
| `CyclingPedalingCadenceRecord` | `supported` | cycling-cadence (0..*; one per sample) | — |
| `DistanceRecord` | `supported` | distance (1) | — |
| `ElevationGainedRecord` | `supported` | elevation-gained (1) | — |
| `ExerciseSessionRecord` | `supported` | workout (1); workout-segment (0..*; one per segment or lap) | `exerciseType`; `exerciseSegmentType`; `sessionTitle`; `exerciseNotes` |
| `FloorsClimbedRecord` | `supported` | flights-climbed (1) | — |
| `HeartRateRecord` | `supported` | heart-rate (0..*; one per sample) | — |
| `HeartRateVariabilityRmssdRecord` | `supported` | heart-rate-variability-rmssd (1) | — |
| `HeightRecord` | `supported` | body-height (1) | — |
| `HydrationRecord` | `supported` | fluid-intake (1) | — |
| `IntermenstrualBleedingRecord` | `supported` | intermenstrual-bleeding (1) | — |
| `LeanBodyMassRecord` | `supported` | lean-body-mass (1) | — |
| `MenstruationFlowRecord` | `supported` | menstruation-flow (1) | `menstruationFlow` |
| `MenstruationPeriodRecord` | `supported` | menstruation-period (1) | — |
| `MindfulnessSessionRecord` | `supported` | mindfulness-session (1) | `mindfulnessSessionType`; `sessionTitle`; `mindfulnessNotes` |
| `NutritionRecord` | `supported` | dietary-biotin (0..*; one per present field); dietary-caffeine (0..*; one per present field); dietary-calcium (0..*; one per present field); dietary-carbohydrates (0..*; one per present field); dietary-chloride (0..*; one per present field); dietary-cholesterol (0..*; one per present field); dietary-chromium (0..*; one per present field); dietary-copper (0..*; one per present field); dietary-energy (0..*; one per present field); dietary-energy-from-fat (0..*; one per present field); dietary-fat-monounsaturated (0..*; one per present field); dietary-fat-polyunsaturated (0..*; one per present field); dietary-fat-saturated (0..*; one per present field); dietary-fat-total (0..*; one per present field); dietary-fat-trans (0..*; one per present field); dietary-fat-unsaturated (0..*; one per present field); dietary-fiber (0..*; one per present field); dietary-folate (0..*; one per present field); dietary-folic-acid (0..*; one per present field); dietary-iodine (0..*; one per present field); dietary-iron (0..*; one per present field); dietary-magnesium (0..*; one per present field); dietary-manganese (0..*; one per present field); dietary-molybdenum (0..*; one per present field); dietary-niacin (0..*; one per present field); dietary-pantothenic-acid (0..*; one per present field); dietary-phosphorus (0..*; one per present field); dietary-potassium (0..*; one per present field); dietary-protein (0..*; one per present field); dietary-riboflavin (0..*; one per present field); dietary-selenium (0..*; one per present field); dietary-sodium (0..*; one per present field); dietary-sugar (0..*; one per present field); dietary-thiamin (0..*; one per present field); dietary-vitamin-a (0..*; one per present field); dietary-vitamin-b12 (0..*; one per present field); dietary-vitamin-b6 (0..*; one per present field); dietary-vitamin-c (0..*; one per present field); dietary-vitamin-d (0..*; one per present field); dietary-vitamin-e (0..*; one per present field); dietary-vitamin-k (0..*; one per present field); dietary-zinc (0..*; one per present field) | — |
| `OvulationTestRecord` | `supported` | ovulation-test-result (1) | `ovulationTestResult` |
| `OxygenSaturationRecord` | `supported` | oxygen-saturation (1) | — |
| `PlannedExerciseSessionRecord` | `deferred` | — | — |
| `PowerRecord` | `supported` | power (0..*; one per sample) | — |
| `RespiratoryRateRecord` | `supported` | respiratory-rate (1) | — |
| `RestingHeartRateRecord` | `supported` | resting-heart-rate (1) | — |
| `SexualActivityRecord` | `supported` | sexual-activity (1) | `sexualActivityProtection` |
| `SkinTemperatureRecord` | `supported` | skin-temperature (0..*; one per delta) | `skinTemperatureMeasurementLocation` |
| `SleepSessionRecord` | `supported` | sleep-duration (1); sleep-stage (0..*; one per stage) | `sleepStage`; `sessionTitle`; `sleepNotes` |
| `SpeedRecord` | `supported` | speed (0..*; one per sample) | — |
| `StepsCadenceRecord` | `supported` | step-cadence (0..*; one per sample) | — |
| `StepsRecord` | `supported` | step-count (1) | — |
| `TotalCaloriesBurnedRecord` | `supported` | total-energy (1) | — |
| `Vo2MaxRecord` | `supported` | vo2-max (1) | `vo2MaxMeasurementMethod` |
| `WeightRecord` | `supported` | body-weight (1) | — |
| `WheelchairPushesRecord` | `supported` | wheelchair-push-count (1) | — |
