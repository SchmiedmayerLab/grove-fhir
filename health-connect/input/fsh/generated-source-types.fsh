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
* #ActiveCaloriesBurnedRecord "Active Calories Burned" "The Health Connect ActiveCaloriesBurnedRecord source type. Grove converts it to active-energy."
* #ActiveCaloriesBurnedRecord ^property[0].code = #documentation
* #ActiveCaloriesBurnedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/ActiveCaloriesBurnedRecord"
* #BasalBodyTemperatureRecord "Basal Body Temperature" "The Health Connect BasalBodyTemperatureRecord source type. Grove converts it to basal-body-temperature."
* #BasalBodyTemperatureRecord ^property[0].code = #documentation
* #BasalBodyTemperatureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BasalBodyTemperatureRecord"
* #BasalMetabolicRateRecord "Basal Metabolic Rate" "The Health Connect BasalMetabolicRateRecord source type. Grove converts it to basal-metabolic-rate."
* #BasalMetabolicRateRecord ^property[0].code = #documentation
* #BasalMetabolicRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BasalMetabolicRateRecord"
* #BloodGlucoseRecord "Blood Glucose" "The Health Connect BloodGlucoseRecord source type. Grove converts it to blood-glucose, capillary-blood-glucose, serum-plasma-glucose and interstitial-glucose."
* #BloodGlucoseRecord ^property[0].code = #documentation
* #BloodGlucoseRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BloodGlucoseRecord"
* #BloodPressureRecord "Blood Pressure" "The Health Connect BloodPressureRecord source type. Grove converts it to blood-pressure."
* #BloodPressureRecord ^property[0].code = #documentation
* #BloodPressureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BloodPressureRecord"
* #BodyFatRecord "Body Fat" "The Health Connect BodyFatRecord source type. Grove converts it to body-fat-percentage."
* #BodyFatRecord ^property[0].code = #documentation
* #BodyFatRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BodyFatRecord"
* #BodyTemperatureRecord "Body Temperature" "The Health Connect BodyTemperatureRecord source type. Grove converts it to body-temperature."
* #BodyTemperatureRecord ^property[0].code = #documentation
* #BodyTemperatureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BodyTemperatureRecord"
* #BodyWaterMassRecord "Body Water Mass" "The Health Connect BodyWaterMassRecord source type. Grove converts it to body-water-mass."
* #BodyWaterMassRecord ^property[0].code = #documentation
* #BodyWaterMassRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BodyWaterMassRecord"
* #BoneMassRecord "Bone Mass" "The Health Connect BoneMassRecord source type. Grove converts it to bone-mass."
* #BoneMassRecord ^property[0].code = #documentation
* #BoneMassRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/BoneMassRecord"
* #CervicalMucusRecord "Cervical Mucus" "The Health Connect CervicalMucusRecord source type. Grove converts it to cervical-mucus-quality."
* #CervicalMucusRecord ^property[0].code = #documentation
* #CervicalMucusRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/CervicalMucusRecord"
* #CyclingPedalingCadenceRecord "Cycling Pedaling Cadence" "The Health Connect CyclingPedalingCadenceRecord source type. Grove converts it to cycling-cadence."
* #CyclingPedalingCadenceRecord ^property[0].code = #documentation
* #CyclingPedalingCadenceRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/CyclingPedalingCadenceRecord"
* #DistanceRecord "Distance" "The Health Connect DistanceRecord source type. Grove converts it to distance."
* #DistanceRecord ^property[0].code = #documentation
* #DistanceRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/DistanceRecord"
* #ElevationGainedRecord "Elevation Gained" "The Health Connect ElevationGainedRecord source type. Grove converts it to elevation-gained."
* #ElevationGainedRecord ^property[0].code = #documentation
* #ElevationGainedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/ElevationGainedRecord"
* #ExerciseSessionRecord "Exercise Session" "The Health Connect ExerciseSessionRecord source type. Grove converts it to workout and workout-segment."
* #ExerciseSessionRecord ^property[0].code = #documentation
* #ExerciseSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/ExerciseSessionRecord"
* #FloorsClimbedRecord "Floors Climbed" "The Health Connect FloorsClimbedRecord source type. Grove converts it to flights-climbed."
* #FloorsClimbedRecord ^property[0].code = #documentation
* #FloorsClimbedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/FloorsClimbedRecord"
* #HeartRateRecord "Heart Rate" "The Health Connect HeartRateRecord source type. Grove converts it to heart-rate."
* #HeartRateRecord ^property[0].code = #documentation
* #HeartRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HeartRateRecord"
* #HeartRateVariabilityRmssdRecord "Heart Rate Variability RMSSD" "The Health Connect HeartRateVariabilityRmssdRecord source type. Grove converts it to heart-rate-variability-rmssd."
* #HeartRateVariabilityRmssdRecord ^property[0].code = #documentation
* #HeartRateVariabilityRmssdRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HeartRateVariabilityRmssdRecord"
* #HeightRecord "Height" "The Health Connect HeightRecord source type. Grove converts it to body-height."
* #HeightRecord ^property[0].code = #documentation
* #HeightRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HeightRecord"
* #HydrationRecord "Hydration" "The Health Connect HydrationRecord source type. Grove converts it to fluid-intake."
* #HydrationRecord ^property[0].code = #documentation
* #HydrationRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/HydrationRecord"
* #IntermenstrualBleedingRecord "Intermenstrual Bleeding" "The Health Connect IntermenstrualBleedingRecord source type. Grove converts it to intermenstrual-bleeding."
* #IntermenstrualBleedingRecord ^property[0].code = #documentation
* #IntermenstrualBleedingRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/IntermenstrualBleedingRecord"
* #LeanBodyMassRecord "Lean Body Mass" "The Health Connect LeanBodyMassRecord source type. Grove converts it to lean-body-mass."
* #LeanBodyMassRecord ^property[0].code = #documentation
* #LeanBodyMassRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/LeanBodyMassRecord"
* #MenstruationFlowRecord "Menstruation Flow" "The Health Connect MenstruationFlowRecord source type. Grove converts it to menstruation-flow."
* #MenstruationFlowRecord ^property[0].code = #documentation
* #MenstruationFlowRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/MenstruationFlowRecord"
* #MenstruationPeriodRecord "Menstruation Period" "The Health Connect MenstruationPeriodRecord source type. Grove converts it to menstruation-period."
* #MenstruationPeriodRecord ^property[0].code = #documentation
* #MenstruationPeriodRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/MenstruationPeriodRecord"
* #MindfulnessSessionRecord "Mindfulness Session" "The Health Connect MindfulnessSessionRecord source type. Grove converts it to mindfulness-session."
* #MindfulnessSessionRecord ^property[0].code = #documentation
* #MindfulnessSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/MindfulnessSessionRecord"
* #NutritionRecord "Nutrition" "The Health Connect NutritionRecord source type. Grove converts it to dietary-biotin, dietary-caffeine, dietary-calcium, dietary-carbohydrates, dietary-chloride, dietary-cholesterol, dietary-chromium, dietary-copper, dietary-energy, dietary-energy-from-fat, dietary-fat-monounsaturated, dietary-fat-polyunsaturated, dietary-fat-saturated, dietary-fat-total, dietary-fat-trans, dietary-fat-unsaturated, dietary-fiber, dietary-folate, dietary-folic-acid, dietary-iodine, dietary-iron, dietary-magnesium, dietary-manganese, dietary-molybdenum, dietary-niacin, dietary-pantothenic-acid, dietary-phosphorus, dietary-potassium, dietary-protein, dietary-riboflavin, dietary-selenium, dietary-sodium, dietary-sugar, dietary-thiamin, dietary-vitamin-a, dietary-vitamin-b12, dietary-vitamin-b6, dietary-vitamin-c, dietary-vitamin-d, dietary-vitamin-e, dietary-vitamin-k and dietary-zinc."
* #NutritionRecord ^property[0].code = #documentation
* #NutritionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/NutritionRecord"
* #OvulationTestRecord "Ovulation Test" "The Health Connect OvulationTestRecord source type. Grove converts it to ovulation-test-result."
* #OvulationTestRecord ^property[0].code = #documentation
* #OvulationTestRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/OvulationTestRecord"
* #OxygenSaturationRecord "Oxygen Saturation" "The Health Connect OxygenSaturationRecord source type. Grove converts it to oxygen-saturation."
* #OxygenSaturationRecord ^property[0].code = #documentation
* #OxygenSaturationRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/OxygenSaturationRecord"
* #PlannedExerciseSessionRecord "Planned Exercise Session" "The Health Connect PlannedExerciseSessionRecord source type. Grove admits no output for it. A planned exercise session states future intent rather than an observed measurement, so it has no place in a measurement contract. R4 CarePlan would carry it if a deployment ever needs the plan itself."
* #PlannedExerciseSessionRecord ^property[0].code = #documentation
* #PlannedExerciseSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/PlannedExerciseSessionRecord"
* #PowerRecord "Power" "The Health Connect PowerRecord source type. Grove converts it to power."
* #PowerRecord ^property[0].code = #documentation
* #PowerRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/PowerRecord"
* #RespiratoryRateRecord "Respiratory Rate" "The Health Connect RespiratoryRateRecord source type. Grove converts it to respiratory-rate."
* #RespiratoryRateRecord ^property[0].code = #documentation
* #RespiratoryRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/RespiratoryRateRecord"
* #RestingHeartRateRecord "Resting Heart Rate" "The Health Connect RestingHeartRateRecord source type. Grove converts it to resting-heart-rate."
* #RestingHeartRateRecord ^property[0].code = #documentation
* #RestingHeartRateRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/RestingHeartRateRecord"
* #SexualActivityRecord "Sexual Activity" "The Health Connect SexualActivityRecord source type. Grove converts it to sexual-activity."
* #SexualActivityRecord ^property[0].code = #documentation
* #SexualActivityRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SexualActivityRecord"
* #SkinTemperatureRecord "Skin Temperature" "The Health Connect SkinTemperatureRecord source type. Grove converts it to skin-temperature."
* #SkinTemperatureRecord ^property[0].code = #documentation
* #SkinTemperatureRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SkinTemperatureRecord"
* #SleepSessionRecord "Sleep Session" "The Health Connect SleepSessionRecord source type. Grove converts it to sleep-duration and sleep-stage."
* #SleepSessionRecord ^property[0].code = #documentation
* #SleepSessionRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SleepSessionRecord"
* #SpeedRecord "Speed" "The Health Connect SpeedRecord source type. Grove converts it to speed."
* #SpeedRecord ^property[0].code = #documentation
* #SpeedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/SpeedRecord"
* #StepsCadenceRecord "Steps Cadence" "The Health Connect StepsCadenceRecord source type. Grove converts it to step-cadence."
* #StepsCadenceRecord ^property[0].code = #documentation
* #StepsCadenceRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/StepsCadenceRecord"
* #StepsRecord "Steps" "The Health Connect StepsRecord source type. Grove converts it to step-count."
* #StepsRecord ^property[0].code = #documentation
* #StepsRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/StepsRecord"
* #TotalCaloriesBurnedRecord "Total Calories Burned" "The Health Connect TotalCaloriesBurnedRecord source type. Grove converts it to total-energy."
* #TotalCaloriesBurnedRecord ^property[0].code = #documentation
* #TotalCaloriesBurnedRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/TotalCaloriesBurnedRecord"
* #Vo2MaxRecord "VO2 Max" "The Health Connect Vo2MaxRecord source type. Grove converts it to vo2-max."
* #Vo2MaxRecord ^property[0].code = #documentation
* #Vo2MaxRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/Vo2MaxRecord"
* #WeightRecord "Weight" "The Health Connect WeightRecord source type. Grove converts it to body-weight."
* #WeightRecord ^property[0].code = #documentation
* #WeightRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/WeightRecord"
* #WheelchairPushesRecord "Wheelchair Pushes" "The Health Connect WheelchairPushesRecord source type. Grove converts it to wheelchair-push-count."
* #WheelchairPushesRecord ^property[0].code = #documentation
* #WheelchairPushesRecord ^property[0].valueString = "https://developer.android.com/reference/androidx/health/connect/client/records/WheelchairPushesRecord"

ValueSet: HealthConnectRecordTypeVS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "The complete closed Health Connect 1.1.0 source Record class inventory."
* ^experimental = false
* include codes from system HealthConnectRecordTypeCS
