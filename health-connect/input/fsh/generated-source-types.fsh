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

CodeSystem: HealthConnectConceptPropertyCS
Id: health-connect-concept-property
Title: "Health Connect Concept Properties"
Description: "The concept properties the Health Connect source-type code system carries."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #documentation "Documentation" "Canonical AndroidX documentation page for this record class."

CodeSystem: HealthConnectRecordTypeCS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "Every concrete Record class published by androidx.health.connect:connect-client:1.1.0, excluding the abstract supertypes. Membership is derived from, and verified against, health-connect/input/data/health-connect-inventory.json. The code identifies the exact already-read source Record class; it is not a clinical result code."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "Health Connect record class names originate from the AndroidX project and are used here only to identify source API concepts for interoperability. AndroidX is licensed under Apache-2.0. The MIT license applies to Grove-authored definitions."
* ^property[0].code = #documentation
* ^property[0].uri = "https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-concept-property#documentation"
* ^property[0].description = "Canonical AndroidX documentation page for this record class."
* ^property[0].type = #string
* #ActiveCaloriesBurnedRecord "Active Calories Burned"
* #ActiveCaloriesBurnedRecord ^property[0].code = #documentation
* #ActiveCaloriesBurnedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/ActiveCaloriesBurnedRecord"
* #BasalBodyTemperatureRecord "Basal Body Temperature"
* #BasalBodyTemperatureRecord ^property[0].code = #documentation
* #BasalBodyTemperatureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BasalBodyTemperatureRecord"
* #BasalMetabolicRateRecord "Basal Metabolic Rate"
* #BasalMetabolicRateRecord ^property[0].code = #documentation
* #BasalMetabolicRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BasalMetabolicRateRecord"
* #BloodGlucoseRecord "Blood Glucose"
* #BloodGlucoseRecord ^property[0].code = #documentation
* #BloodGlucoseRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BloodGlucoseRecord"
* #BloodPressureRecord "Blood Pressure"
* #BloodPressureRecord ^property[0].code = #documentation
* #BloodPressureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BloodPressureRecord"
* #BodyFatRecord "Body Fat"
* #BodyFatRecord ^property[0].code = #documentation
* #BodyFatRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BodyFatRecord"
* #BodyTemperatureRecord "Body Temperature"
* #BodyTemperatureRecord ^property[0].code = #documentation
* #BodyTemperatureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BodyTemperatureRecord"
* #BodyWaterMassRecord "Body Water Mass"
* #BodyWaterMassRecord ^property[0].code = #documentation
* #BodyWaterMassRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BodyWaterMassRecord"
* #BoneMassRecord "Bone Mass"
* #BoneMassRecord ^property[0].code = #documentation
* #BoneMassRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BoneMassRecord"
* #CervicalMucusRecord "Cervical Mucus"
* #CervicalMucusRecord ^property[0].code = #documentation
* #CervicalMucusRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/CervicalMucusRecord"
* #CyclingPedalingCadenceRecord "Cycling Pedaling Cadence"
* #CyclingPedalingCadenceRecord ^property[0].code = #documentation
* #CyclingPedalingCadenceRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/CyclingPedalingCadenceRecord"
* #DistanceRecord "Distance"
* #DistanceRecord ^property[0].code = #documentation
* #DistanceRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/DistanceRecord"
* #ElevationGainedRecord "Elevation Gained"
* #ElevationGainedRecord ^property[0].code = #documentation
* #ElevationGainedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/ElevationGainedRecord"
* #ExerciseSessionRecord "Exercise Session"
* #ExerciseSessionRecord ^property[0].code = #documentation
* #ExerciseSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/ExerciseSessionRecord"
* #FloorsClimbedRecord "Floors Climbed"
* #FloorsClimbedRecord ^property[0].code = #documentation
* #FloorsClimbedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/FloorsClimbedRecord"
* #HeartRateRecord "Heart Rate"
* #HeartRateRecord ^property[0].code = #documentation
* #HeartRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HeartRateRecord"
* #HeartRateVariabilityRmssdRecord "Heart Rate Variability RMSSD"
* #HeartRateVariabilityRmssdRecord ^property[0].code = #documentation
* #HeartRateVariabilityRmssdRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HeartRateVariabilityRmssdRecord"
* #HeightRecord "Height"
* #HeightRecord ^property[0].code = #documentation
* #HeightRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HeightRecord"
* #HydrationRecord "Hydration"
* #HydrationRecord ^property[0].code = #documentation
* #HydrationRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HydrationRecord"
* #IntermenstrualBleedingRecord "Intermenstrual Bleeding"
* #IntermenstrualBleedingRecord ^property[0].code = #documentation
* #IntermenstrualBleedingRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/IntermenstrualBleedingRecord"
* #LeanBodyMassRecord "Lean Body Mass"
* #LeanBodyMassRecord ^property[0].code = #documentation
* #LeanBodyMassRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/LeanBodyMassRecord"
* #MenstruationFlowRecord "Menstruation Flow"
* #MenstruationFlowRecord ^property[0].code = #documentation
* #MenstruationFlowRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/MenstruationFlowRecord"
* #MenstruationPeriodRecord "Menstruation Period"
* #MenstruationPeriodRecord ^property[0].code = #documentation
* #MenstruationPeriodRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/MenstruationPeriodRecord"
* #MindfulnessSessionRecord "Mindfulness Session"
* #MindfulnessSessionRecord ^property[0].code = #documentation
* #MindfulnessSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/MindfulnessSessionRecord"
* #NutritionRecord "Nutrition"
* #NutritionRecord ^property[0].code = #documentation
* #NutritionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/NutritionRecord"
* #OvulationTestRecord "Ovulation Test"
* #OvulationTestRecord ^property[0].code = #documentation
* #OvulationTestRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/OvulationTestRecord"
* #OxygenSaturationRecord "Oxygen Saturation"
* #OxygenSaturationRecord ^property[0].code = #documentation
* #OxygenSaturationRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/OxygenSaturationRecord"
* #PlannedExerciseSessionRecord "Planned Exercise Session"
* #PlannedExerciseSessionRecord ^property[0].code = #documentation
* #PlannedExerciseSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/PlannedExerciseSessionRecord"
* #PowerRecord "Power"
* #PowerRecord ^property[0].code = #documentation
* #PowerRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/PowerRecord"
* #RespiratoryRateRecord "Respiratory Rate"
* #RespiratoryRateRecord ^property[0].code = #documentation
* #RespiratoryRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/RespiratoryRateRecord"
* #RestingHeartRateRecord "Resting Heart Rate"
* #RestingHeartRateRecord ^property[0].code = #documentation
* #RestingHeartRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/RestingHeartRateRecord"
* #SexualActivityRecord "Sexual Activity"
* #SexualActivityRecord ^property[0].code = #documentation
* #SexualActivityRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SexualActivityRecord"
* #SkinTemperatureRecord "Skin Temperature"
* #SkinTemperatureRecord ^property[0].code = #documentation
* #SkinTemperatureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SkinTemperatureRecord"
* #SleepSessionRecord "Sleep Session"
* #SleepSessionRecord ^property[0].code = #documentation
* #SleepSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SleepSessionRecord"
* #SpeedRecord "Speed"
* #SpeedRecord ^property[0].code = #documentation
* #SpeedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SpeedRecord"
* #StepsCadenceRecord "Steps Cadence"
* #StepsCadenceRecord ^property[0].code = #documentation
* #StepsCadenceRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/StepsCadenceRecord"
* #StepsRecord "Steps"
* #StepsRecord ^property[0].code = #documentation
* #StepsRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/StepsRecord"
* #TotalCaloriesBurnedRecord "Total Calories Burned"
* #TotalCaloriesBurnedRecord ^property[0].code = #documentation
* #TotalCaloriesBurnedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/TotalCaloriesBurnedRecord"
* #Vo2MaxRecord "VO2 Max"
* #Vo2MaxRecord ^property[0].code = #documentation
* #Vo2MaxRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/Vo2MaxRecord"
* #WeightRecord "Weight"
* #WeightRecord ^property[0].code = #documentation
* #WeightRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/WeightRecord"
* #WheelchairPushesRecord "Wheelchair Pushes"
* #WheelchairPushesRecord ^property[0].code = #documentation
* #WheelchairPushesRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/WheelchairPushesRecord"

ValueSet: HealthConnectRecordTypeVS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete closed Health Connect 1.1.0 source Record class inventory."
* ^experimental = false
* include codes from system HealthConnectRecordTypeCS
