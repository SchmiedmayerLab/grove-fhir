//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// GENERATED FILE. Edit the adapter catalog and run
// `python3 Scripts/render-adapter-source-terminology.py`.
//

CodeSystem: HealthConnectRecordTypeCS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete AndroidX Health Connect 1.1.0 RecordType.all inventory. The code identifies the exact already-read source Record class; it is not a clinical result code."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #ActiveCaloriesBurnedRecord "ActiveCaloriesBurnedRecord"
* #BasalBodyTemperatureRecord "BasalBodyTemperatureRecord"
* #BasalMetabolicRateRecord "BasalMetabolicRateRecord"
* #BloodGlucoseRecord "BloodGlucoseRecord"
* #BloodPressureRecord "BloodPressureRecord"
* #BodyFatRecord "BodyFatRecord"
* #BodyTemperatureRecord "BodyTemperatureRecord"
* #BodyWaterMassRecord "BodyWaterMassRecord"
* #BoneMassRecord "BoneMassRecord"
* #CervicalMucusRecord "CervicalMucusRecord"
* #CyclingPedalingCadenceRecord "CyclingPedalingCadenceRecord"
* #DistanceRecord "DistanceRecord"
* #ElevationGainedRecord "ElevationGainedRecord"
* #ExerciseSessionRecord "ExerciseSessionRecord"
* #FloorsClimbedRecord "FloorsClimbedRecord"
* #HeartRateRecord "HeartRateRecord"
* #HeartRateVariabilityRmssdRecord "HeartRateVariabilityRmssdRecord"
* #HeightRecord "HeightRecord"
* #HydrationRecord "HydrationRecord"
* #IntermenstrualBleedingRecord "IntermenstrualBleedingRecord"
* #LeanBodyMassRecord "LeanBodyMassRecord"
* #MenstruationFlowRecord "MenstruationFlowRecord"
* #MenstruationPeriodRecord "MenstruationPeriodRecord"
* #MindfulnessSessionRecord "MindfulnessSessionRecord"
* #NutritionRecord "NutritionRecord"
* #OvulationTestRecord "OvulationTestRecord"
* #OxygenSaturationRecord "OxygenSaturationRecord"
* #PlannedExerciseSessionRecord "PlannedExerciseSessionRecord"
* #PowerRecord "PowerRecord"
* #RespiratoryRateRecord "RespiratoryRateRecord"
* #RestingHeartRateRecord "RestingHeartRateRecord"
* #SexualActivityRecord "SexualActivityRecord"
* #SkinTemperatureRecord "SkinTemperatureRecord"
* #SleepSessionRecord "SleepSessionRecord"
* #SpeedRecord "SpeedRecord"
* #StepsCadenceRecord "StepsCadenceRecord"
* #StepsRecord "StepsRecord"
* #TotalCaloriesBurnedRecord "TotalCaloriesBurnedRecord"
* #Vo2MaxRecord "Vo2MaxRecord"
* #WeightRecord "WeightRecord"
* #WheelchairPushesRecord "WheelchairPushesRecord"

ValueSet: HealthConnectRecordTypeVS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete closed Health Connect 1.1.0 source Record class inventory."
* ^experimental = false
* include codes from system HealthConnectRecordTypeCS
