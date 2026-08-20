<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative HealthKit status matrix

This table is the complete, closed v0.2.0 inventory of all 220 Apple HealthKit platform source types frozen against iPhoneOS 27.0 from Xcode 27.0 build `27A5237l`. The evidence is the official Apple platform documentation and the exact SDK provenance declared by the catalog. Each row has one definitive contract status; this is a release contract, not a roadmap. `supported` means v0.2.0 admits a conformant output contract. All other rows are not admitted and producers fail closed.

| HealthKit type | Title | Contract status | Measurement | Direct profile claim(s) | Binding reason / requirement |
| --- | --- | --- | --- | --- | --- |
| `HKCategoryTypeIdentifierAbdominalCramps` | Abdominal Cramps | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierAcne` | Acne | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierAppetiteChanges` | Appetite Changes | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierAppleStandHour` | Apple Stand Hour | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierAppleWalkingSteadinessEvent` | Apple Walking Steadiness Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierAudioExposureEvent` | Audio Exposure Event | `deferred` | — | — | Apple renames this constant to HKCategoryTypeIdentifierEnvironmentalAudioExposureEvent while keeping its identifier. Version 0.2.0 publishes no admitted output contract. |
| `HKCategoryTypeIdentifierBladderIncontinence` | Bladder Incontinence | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierBleedingAfterMenopause` | Bleeding After Menopause | `deferred` | — | — | The source type is beta in the stated SDK baseline and v0.2.0 publishes no admitted output contract. |
| `HKCategoryTypeIdentifierBleedingAfterPregnancy` | Bleeding After Pregnancy | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierBleedingDuringPregnancy` | Bleeding During Pregnancy | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierBloating` | Bloating | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierBreastPain` | Breast Pain | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierCervicalMucusQuality` | Cervical Mucus Quality | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierChestTightnessOrPain` | Chest Tightness/Pain | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierChills` | Chills | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierConstipation` | Constipation | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierContraceptive` | Contraceptive | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierCoughing` | Coughing | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierDiarrhea` | Diarrhea | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierDizziness` | Dizziness | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierDrySkin` | Dry Skin | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierFainting` | Fainting | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierFatigue` | Fatigue | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierFever` | Fever | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierGeneralizedBodyAche` | Generalized Body Ache | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHairLoss` | Hair Loss | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHandwashingEvent` | Handwashing Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHeadache` | Headache | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHeadphoneAudioExposureEvent` | Headphone Audio Exposure Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHeartburn` | Heartburn | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHighHeartRateEvent` | High Heart Rate Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHotFlashes` | Hot Flashes | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierHypertensionEvent` | Hypertension Event | `deferred` | — | — | No shared or adapter-specific v0.2.0 output contract is published for this platform source type. |
| `HKCategoryTypeIdentifierInfrequentMenstrualCycles` | Infrequent Menstrual Cycles | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierIntermenstrualBleeding` | Intermenstrual Bleeding | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierIrregularHeartRhythmEvent` | Irregular Heart Rhythm Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierIrregularMenstrualCycles` | Irregular Menstrual Cycles | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierLactation` | Lactation | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierLossOfSmell` | Loss of Smell | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierLossOfTaste` | Loss of Taste | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierLowCardioFitnessEvent` | Low Cardio Fitness Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierLowHeartRateEvent` | Low Heart Rate Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierLowerBackPain` | Lower Back Pain | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierMemoryLapse` | Memory Lapse | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierMenopausalState` | Menopausal State | `deferred` | — | — | The source type is beta in the stated SDK baseline and v0.2.0 publishes no admitted output contract. |
| `HKCategoryTypeIdentifierMenstrualFlow` | Menstrual Flow | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierMindfulSession` | Mindful Session | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierMoodChanges` | Mood Changes | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierNausea` | Nausea | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierNightSweats` | Night Sweats | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierOvulationTestResult` | Ovulation Test Result | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierPelvicPain` | Pelvic Pain | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierPersistentIntermenstrualBleeding` | Persistent Intermenstrual Bleeding | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierPregnancy` | Pregnancy | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierPregnancyTestResult` | Pregnancy Test Result | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierProgesteroneTestResult` | Progesterone Test Result | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierProlongedMenstrualPeriods` | Prolonged Menstrual Periods | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat` | Rapid/Pounding/Fluttering Heartbeat | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierRunnyNose` | Runny Nose | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierSexualActivity` | Sexual Activity | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierShortnessOfBreath` | Shortness of Breath | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierSinusCongestion` | Sinus Congestion | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierSkippedHeartbeat` | Skipped Heartbeat | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierSleepAnalysis` | Sleep Analysis | `supported` | sleep-stage | grove-mobile-sleep-stage | — |
| `HKCategoryTypeIdentifierSleepApneaEvent` | Sleep Apnea Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierSleepChanges` | Sleep Changes | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierSoreThroat` | Sore Throat | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierToothbrushingEvent` | Toothbrushing Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierVaginalDryness` | Vaginal Dryness | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierVomiting` | Vomiting | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCategoryTypeIdentifierWheezing` | Wheezing | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKCharacteristicTypeIdentifierActivityMoveMode` | Activity Move Mode | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.2.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierBiologicalSex` | Biological Sex | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.2.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierBloodType` | Blood Type | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.2.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierDateOfBirth` | Date of Birth | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.2.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierFitzpatrickSkinType` | Fitzpatrick Skin Type | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.2.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierWheelchairUse` | Wheelchair Use | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.2.0 publishes no admitted output contract for characteristics. |
| `HKClinicalTypeIdentifierAllergyRecord` | Allergy Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierClinicalNoteRecord` | Clinical Note Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierConditionRecord` | Condition Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierCoverageRecord` | Coverage Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierImmunizationRecord` | Immunization Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierLabResultRecord` | Lab Result Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierMedicationRecord` | Medication Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierProcedureRecord` | Procedure Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKClinicalTypeIdentifierVitalSignRecord` | Vital Sign Record | `deferred` | — | — | HealthKit clinical records already carry provider FHIR; the v0.2 HealthKit Observation adapter does not rewrite or re-profile them. |
| `HKCorrelationTypeIdentifierBloodPressure` | Blood Pressure | `supported` | blood-pressure | grove-mobile-blood-pressure | — |
| `HKCorrelationTypeIdentifierFood` | Food | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKDataTypeIdentifierAudiogram` | Audiogram | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKDataTypeIdentifierElectrocardiogram` | ECG | `supported` | electrocardiogram | grove-sensor-ecg-observation; healthkit-ecg-observation | The caller supplies the HKElectrocardiogram, every voltage measurement with its exact timeSinceSampleStart, and each associated HKCategorySample when symptomsStatus is present. The adapter preserves symptom UUID/timing/type/severity and complete HKSourceRevision fields, classification, average heart rate, sampling frequency, reported count, Apple ECG algorithm-version metadata when present, source and waveform intervals, lead, offsets, and voltages without fetching or resampling. Explicit caller authorization for linkable symptom-source disclosure is required; otherwise conversion fails closed. |
| `HKDataTypeIdentifierHeartbeatSeries` | Heartbeat Series | `deferred` | — | — | Use a Grove Sensor waveform graph once the HealthKit heartbeat-series adapter is implemented. |
| `HKDataTypeStateOfMind` | State of Mind | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKDataTypeUserAnnotatedMedicationConcept` | User Annotated Medication Concept | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKDocumentTypeIdentifierCDA` | CDA Document | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKMedicationDoseEventTypeIdentifierMedicationDoseEvent` | Medication Dose Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierActiveEnergyBurned` | Active Energy Burned | `supported` | active-energy | grove-mobile-active-energy | — |
| `HKQuantityTypeIdentifierAppleExerciseTime` | Apple Exercise Time | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierAppleMoveTime` | Apple Move Time | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances` | Apple Sleeping Breathing Disturbances | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierAppleSleepingWristTemperature` | Apple Sleeping Wrist Temperature | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierAppleStandTime` | Apple Stand Time | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierAppleWalkingSteadiness` | Apple Walking Steadiness | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierAtrialFibrillationBurden` | AFib Burden | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierBasalBodyTemperature` | Basal Body Temperature | `supported` | basal-body-temperature | grove-mobile-basal-body-temperature | — |
| `HKQuantityTypeIdentifierBasalEnergyBurned` | Basal Energy Burned | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierBloodAlcoholContent` | Blood Alcohol Content | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierBloodGlucose` | Blood Glucose | `deferred` | — | — | HealthKit does not identify the specimen needed by the Health Connect-only glucose profiles; source-only conversion fails closed. |
| `HKQuantityTypeIdentifierBloodPressureDiastolic` | Blood Pressure (Diastolic) | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierBloodPressureSystolic` | Blood Pressure (Systolic) | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierBodyFatPercentage` | Body Fat Percentage | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierBodyMass` | Body Mass | `supported` | body-weight | grove-mobile-body-weight | — |
| `HKQuantityTypeIdentifierBodyMassIndex` | BMI | `supported` | body-mass-index | bmi; healthkit-observation | — |
| `HKQuantityTypeIdentifierBodyTemperature` | Body Temperature | `supported` | body-temperature | grove-mobile-body-temperature | — |
| `HKQuantityTypeIdentifierCrossCountrySkiingSpeed` | Cross Country Skiing Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierCyclingCadence` | Cycling Cadence | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierCyclingFunctionalThresholdPower` | Cycling Functional Threshold Power | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierCyclingPower` | Cycling Power | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierCyclingSpeed` | Cycling Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryBiotin` | Dietary Biotin Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryCaffeine` | Dietary Caffeine Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryCalcium` | Dietary Calcium Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryCarbohydrates` | Dietary Carbohydrates Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryChloride` | Dietary Chloride Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryCholesterol` | Dietary Cholesterol Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryChromium` | Dietary Chromium Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryCopper` | Dietary Copper Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryEnergyConsumed` | Dietary Energy Consumed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryFatMonounsaturated` | Dietary Monounsaturated Fat Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryFatPolyunsaturated` | Dietary Polyunsaturated Fat Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryFatSaturated` | Dietary Saturated Fat Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryFatTotal` | Dietary Total Fat Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryFiber` | Dietary Fiber Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryFolate` | Dietary Folate Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryIodine` | Dietary Iodine Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryIron` | Dietary Iron Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryMagnesium` | Dietary Magnesium Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryManganese` | Dietary Manganese Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryMolybdenum` | Dietary Molybdenum Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryNiacin` | Dietary Niacin Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryPantothenicAcid` | Dietary Pantothenic Acid Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryPhosphorus` | Dietary Phosphorus Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryPotassium` | Dietary Potassium Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryProtein` | Dietary Protein Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryRiboflavin` | Dietary Riboflavin Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietarySelenium` | Dietary Selenium Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietarySodium` | Dietary Sodium Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietarySugar` | Dietary Sugar Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryThiamin` | Dietary Thiamin Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminA` | Dietary Vitamin A Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminB12` | Dietary Vitamin B12 Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminB6` | Dietary Vitamin B6 Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminC` | Dietary Vitamin C Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminD` | Dietary Vitamin D Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminE` | Dietary Vitamin E Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryVitaminK` | Dietary Vitamin K Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryWater` | Dietary Water Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDietaryZinc` | Dietary Zinc Intake | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierDistanceCrossCountrySkiing` | Cross-Country Skiing Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceCycling` | Cycling Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceDownhillSnowSports` | Downhill Snow Sports Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistancePaddleSports` | Paddle Sports Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceRowing` | Rowing Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceSkatingSports` | Skating Sports Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceSwimming` | Swimming Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceWalkingRunning` | Distance Walking/Running | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceWheelchair` | Wheelchair Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierElectrodermalActivity` | Electrodermal Activity | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierEnvironmentalAudioExposure` | Environmental Audio Exposure | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierEnvironmentalSoundReduction` | Environmental Sound Reduction | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierEstimatedWorkoutEffortScore` | Estimated Workout Effort | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierFlightsClimbed` | Flights Climbed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierForcedExpiratoryVolume1` | Forced Expiratory Volume (1 sec) | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierForcedVitalCapacity` | Forced Vital Capacity | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierHeadphoneAudioExposure` | Headphone Audio Exposure | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierHeartRate` | Heart Rate | `supported` | heart-rate | grove-mobile-heart-rate | — |
| `HKQuantityTypeIdentifierHeartRateRecoveryOneMinute` | Heart Rate Recovery (1 min) | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierHeartRateVariabilitySDNN` | Heart Rate Variability SDNN | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierHeight` | Height | `supported` | body-height | grove-mobile-body-height | — |
| `HKQuantityTypeIdentifierInhalerUsage` | Inhaler Usage | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierInsulinDelivery` | Insulin Delivery | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierLeanBodyMass` | Lean Body Mass | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierNikeFuel` | NikeFuel | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierNumberOfAlcoholicBeverages` | Number of Alcoholic Beverages | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierNumberOfTimesFallen` | Number of Times Fallen | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierOxygenSaturation` | Oxygen Saturation | `supported` | oxygen-saturation | grove-mobile-oxygen-saturation | — |
| `HKQuantityTypeIdentifierPaddleSportsSpeed` | Paddle Sports Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierPeakExpiratoryFlowRate` | Peak Expiratory Flow Rate | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierPeripheralPerfusionIndex` | Peripheral Perfusion Index | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierPhysicalEffort` | Physical Effort | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierPushCount` | Wheelchair Push Count | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRespiratoryRate` | Respiratory Rate | `supported` | respiratory-rate | grove-mobile-respiratory-rate | — |
| `HKQuantityTypeIdentifierRestingHeartRate` | Resting Heart Rate | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRowingSpeed` | Rowing Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRunningGroundContactTime` | Ground Contact Time | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRunningPower` | Running Power | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRunningSpeed` | Running Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRunningStrideLength` | Running Stride Length | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierRunningVerticalOscillation` | Running Vertical Oscillation | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierSixMinuteWalkTestDistance` | 6 Minute Walk Test Distance | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierStairAscentSpeed` | Stair Ascent Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierStairDescentSpeed` | Stair Descent Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierStepCount` | Step Count | `supported` | step-count | grove-mobile-step-count | — |
| `HKQuantityTypeIdentifierSwimmingStrokeCount` | Swimming Stroke Count | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierTimeInDaylight` | Time in Daylight | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierUVExposure` | UV Exposure | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierUnderwaterDepth` | Underwater Depth | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierVO2Max` | VO2Max | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWaistCircumference` | Waist Circumference | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWalkingAsymmetryPercentage` | Walking Asymmetry Percentage | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWalkingDoubleSupportPercentage` | Walking Double Support Percentage | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWalkingHeartRateAverage` | Walking Heart Rate Average | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWalkingSpeed` | Walking Speed | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWalkingStepLength` | Walking Step Length | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWaterTemperature` | Water Temperature | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierWorkoutEffortScore` | Workout Effort | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKScoredAssessmentTypeIdentifierGAD7` | GAD-7 | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKScoredAssessmentTypeIdentifierPHQ9` | PHQ-9 | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKVisionPrescriptionTypeIdentifier` | Vision Prescription | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKWorkoutRouteTypeIdentifier` | Workout Route | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKWorkoutTypeIdentifier` | Workout | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |

## Derived aggregate contracts

These rows are derived mappings, not HealthKit platform source identifiers, and are excluded from the source-type count and source-type CodeSystem.

| Aggregate | Title | Input source type(s) | Contract status | Measurement | Target profile | Binding reason / requirement |
| --- | --- | --- | --- | --- | --- | --- |
| `sleep-duration-session-aggregate` | Sleep Duration Session Aggregate | `HKCategoryTypeIdentifierSleepAnalysis` | `deferred` | sleep-duration | grove-mobile-sleep-duration | This is not a HealthKit platform source identifier. Version 0.2.0 does not define the session-boundary aggregation contract; individual admitted samples map only to sleep stage. |
