<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative HealthKit status matrix

This table is the complete, closed v0.3.0 inventory of all 218 Apple HealthKit platform source types frozen against iPhoneOS 26.5 from Xcode 26.6 build `17F113`. The evidence is the official Apple platform documentation and the exact SDK provenance declared by the catalog. Each row has one definitive contract status; this is a release contract, not a roadmap. `supported` means v0.3.0 admits a conformant output contract. All other rows are not admitted and producers fail closed.

| HealthKit type | Title | Contract status | Measurement | Direct profile claim(s) | Binding reason / requirement |
| --- | --- | --- | --- | --- | --- |
| `HKCategoryTypeIdentifierAbdominalCramps` | Abdominal Cramps | `supported` | symptom-abdominal-cramps | healthkit-symptom-abdominal-cramps | — |
| `HKCategoryTypeIdentifierAcne` | Acne | `supported` | symptom-acne | healthkit-symptom-acne | — |
| `HKCategoryTypeIdentifierAppetiteChanges` | Appetite Changes | `supported` | symptom-appetite-changes | healthkit-symptom-appetite-changes | — |
| `HKCategoryTypeIdentifierAppleStandHour` | Apple Stand Hour | `supported` | apple-stand-hour | healthkit-apple-stand-hour | — |
| `HKCategoryTypeIdentifierAppleWalkingSteadinessEvent` | Apple Walking Steadiness Event | `intentionally-unsupported` | — | — | Device alert: the enum encodes notification cadence (initial vs repeat) crossed with an Apple-defined banding of the appleWalkingSteadiness percent score, which is the actual measurement and is handled as a quantity type. The alert adds no measurement content beyond that score. |
| `HKCategoryTypeIdentifierAudioExposureEvent` | Audio Exposure Event | `intentionally-unsupported` | — | — | Device alert: a threshold-crossing notification against a user-configurable limit, not a measurement. The measurement is the environmentalAudioExposure dB(A) quantity type, which carries the actual exposure level. |
| `HKCategoryTypeIdentifierBladderIncontinence` | Bladder Incontinence | `supported` | bladder-incontinence | healthkit-bladder-incontinence | — |
| `HKCategoryTypeIdentifierBleedingAfterPregnancy` | Bleeding After Pregnancy | `supported` | bleeding-after-pregnancy | healthkit-bleeding-after-pregnancy | — |
| `HKCategoryTypeIdentifierBleedingDuringPregnancy` | Bleeding During Pregnancy | `supported` | bleeding-during-pregnancy | healthkit-bleeding-during-pregnancy | — |
| `HKCategoryTypeIdentifierBloating` | Bloating | `supported` | symptom-bloating | healthkit-symptom-bloating | — |
| `HKCategoryTypeIdentifierBreastPain` | Breast Pain | `supported` | symptom-breast-pain | healthkit-symptom-breast-pain | — |
| `HKCategoryTypeIdentifierCervicalMucusQuality` | Cervical Mucus Quality | `supported` | cervical-mucus-quality | grove-mobile-cervical-mucus-quality | — |
| `HKCategoryTypeIdentifierChestTightnessOrPain` | Chest Tightness/Pain | `supported` | symptom-chest-tightness-or-pain | healthkit-symptom-chest-tightness-or-pain | — |
| `HKCategoryTypeIdentifierChills` | Chills | `supported` | symptom-chills | healthkit-symptom-chills | — |
| `HKCategoryTypeIdentifierConstipation` | Constipation | `supported` | symptom-constipation | healthkit-symptom-constipation | — |
| `HKCategoryTypeIdentifierContraceptive` | Contraceptive | `supported` | contraceptive-use | healthkit-contraceptive-use | — |
| `HKCategoryTypeIdentifierCoughing` | Coughing | `supported` | symptom-coughing | healthkit-symptom-coughing | — |
| `HKCategoryTypeIdentifierDiarrhea` | Diarrhea | `supported` | symptom-diarrhea | healthkit-symptom-diarrhea | — |
| `HKCategoryTypeIdentifierDizziness` | Dizziness | `supported` | symptom-dizziness | healthkit-symptom-dizziness | — |
| `HKCategoryTypeIdentifierDrySkin` | Dry Skin | `supported` | symptom-dry-skin | healthkit-symptom-dry-skin | — |
| `HKCategoryTypeIdentifierFainting` | Fainting | `supported` | symptom-fainting | healthkit-symptom-fainting | — |
| `HKCategoryTypeIdentifierFatigue` | Fatigue | `supported` | symptom-fatigue | healthkit-symptom-fatigue | — |
| `HKCategoryTypeIdentifierFever` | Fever | `supported` | symptom-fever | healthkit-symptom-fever | — |
| `HKCategoryTypeIdentifierGeneralizedBodyAche` | Generalized Body Ache | `supported` | symptom-generalized-body-ache | healthkit-symptom-generalized-body-ache | — |
| `HKCategoryTypeIdentifierHairLoss` | Hair Loss | `supported` | symptom-hair-loss | healthkit-symptom-hair-loss | — |
| `HKCategoryTypeIdentifierHandwashingEvent` | Handwashing Event | `supported` | handwashing-session | healthkit-handwashing-session | — |
| `HKCategoryTypeIdentifierHeadache` | Headache | `supported` | symptom-headache | healthkit-symptom-headache | — |
| `HKCategoryTypeIdentifierHeadphoneAudioExposureEvent` | Headphone Audio Exposure Event | `intentionally-unsupported` | — | — | Device alert over an OS-computed rolling seven-day dose limit; not a measurement. The headphoneAudioExposure quantity type carries the measured levels. |
| `HKCategoryTypeIdentifierHeartburn` | Heartburn | `supported` | symptom-heartburn | healthkit-symptom-heartburn | — |
| `HKCategoryTypeIdentifierHighHeartRateEvent` | High Heart Rate Event | `intentionally-unsupported` | — | — | Device alert against a user-configurable threshold; not a measurement. Heart-rate quantities remain the measurement surface. |
| `HKCategoryTypeIdentifierHotFlashes` | Hot Flashes | `supported` | symptom-hot-flashes | healthkit-symptom-hot-flashes | — |
| `HKCategoryTypeIdentifierHypertensionEvent` | Hypertension Event | `intentionally-unsupported` | — | — | Device alert from a proprietary screening algorithm asserting possible pathology without any pressure measurement; emitting it as an Observation would fabricate a blood-pressure-adjacent finding with no quantity. Cuff blood-pressure quantities remain the measurement surface. |
| `HKCategoryTypeIdentifierInfrequentMenstrualCycles` | Infrequent Menstrual Cycles | `intentionally-unsupported` | — | — | Algorithmic screening alert over derived cycle history; not a measurement. |
| `HKCategoryTypeIdentifierIntermenstrualBleeding` | Intermenstrual Bleeding | `supported` | intermenstrual-bleeding | grove-mobile-intermenstrual-bleeding | — |
| `HKCategoryTypeIdentifierIrregularHeartRhythmEvent` | Irregular Heart Rhythm Event | `intentionally-unsupported` | — | — | FDA-cleared screening notification from a proprietary algorithm, valueless and read-only. Grove admits the ECG itself (sensor ECG adapter claim, HKDataTypeIdentifierElectrocardiogram) and the atrial-fibrillation burden percentage (HKQuantityTypeIdentifierAtrialFibrillationBurden) as the rhythm evidence surfaces; re-emitting the alert would present a screening trigger as a rhythm finding without any waveform or classification payload. |
| `HKCategoryTypeIdentifierIrregularMenstrualCycles` | Irregular Menstrual Cycles | `intentionally-unsupported` | — | — | Algorithmic screening alert over derived cycle history; not a measurement. |
| `HKCategoryTypeIdentifierLactation` | Lactation | `supported` | lactation-status | healthkit-lactation-status | — |
| `HKCategoryTypeIdentifierLossOfSmell` | Loss of Smell | `supported` | symptom-loss-of-smell | healthkit-symptom-loss-of-smell | — |
| `HKCategoryTypeIdentifierLossOfTaste` | Loss of Taste | `supported` | symptom-loss-of-taste | healthkit-symptom-loss-of-taste | — |
| `HKCategoryTypeIdentifierLowCardioFitnessEvent` | Low Cardio Fitness Event | `intentionally-unsupported` | — | — | Device alert over an Apple-defined classification band of the VO2Max quantity, which is the measurement. Single enum case lowFitness carries no additional measurement meaning. |
| `HKCategoryTypeIdentifierLowHeartRateEvent` | Low Heart Rate Event | `intentionally-unsupported` | — | — | Device alert against a user-configurable threshold; the heart-rate quantity series is the admitted measurement. An alert Observation would encode a preference-dependent trigger, not a physiologic result. |
| `HKCategoryTypeIdentifierLowerBackPain` | Lower Back Pain | `supported` | symptom-lower-back-pain | healthkit-symptom-lower-back-pain | — |
| `HKCategoryTypeIdentifierMemoryLapse` | Memory Lapse | `supported` | symptom-memory-lapse | healthkit-symptom-memory-lapse | — |
| `HKCategoryTypeIdentifierMenstrualFlow` | Menstrual Flow | `supported` | menstruation-flow | grove-mobile-menstruation-flow | — |
| `HKCategoryTypeIdentifierMindfulSession` | Mindful Session | `supported` | mindfulness-session | grove-mobile-mindfulness-session | — |
| `HKCategoryTypeIdentifierMoodChanges` | Mood Changes | `supported` | symptom-mood-changes | healthkit-symptom-mood-changes | — |
| `HKCategoryTypeIdentifierNausea` | Nausea | `supported` | symptom-nausea | healthkit-symptom-nausea | — |
| `HKCategoryTypeIdentifierNightSweats` | Night Sweats | `supported` | symptom-night-sweats | healthkit-symptom-night-sweats | — |
| `HKCategoryTypeIdentifierOvulationTestResult` | Ovulation Test Result | `supported` | ovulation-test-result | grove-mobile-ovulation-test-result | — |
| `HKCategoryTypeIdentifierPelvicPain` | Pelvic Pain | `supported` | symptom-pelvic-pain | healthkit-symptom-pelvic-pain | — |
| `HKCategoryTypeIdentifierPersistentIntermenstrualBleeding` | Persistent Intermenstrual Bleeding | `intentionally-unsupported` | — | — | Algorithmic screening alert derived from user-entered cycle data, not a measurement. The primary data (intermenstrualBleeding and menstrualFlow samples) is admitted through the cycle-tracking enum-absorption design; re-emitting HealthKit's derived possible-pathology flag would present a screening notification as a clinical finding. |
| `HKCategoryTypeIdentifierPregnancy` | Pregnancy | `supported` | pregnancy-status | healthkit-pregnancy-status | — |
| `HKCategoryTypeIdentifierPregnancyTestResult` | Pregnancy Test Result | `supported` | pregnancy-test-result | healthkit-pregnancy-test-result | — |
| `HKCategoryTypeIdentifierProgesteroneTestResult` | Progesterone Test Result | `supported` | progesterone-test-result | healthkit-progesterone-test-result | — |
| `HKCategoryTypeIdentifierProlongedMenstrualPeriods` | Prolonged Menstrual Periods | `intentionally-unsupported` | — | — | Algorithmic screening alert over derived cycle history; the underlying menstrualFlow data is the measurement and is covered by the cycle-tracking design. |
| `HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat` | Rapid/Pounding/Fluttering Heartbeat | `supported` | symptom-rapid-pounding-or-fluttering-heartbeat | healthkit-symptom-rapid-pounding-or-fluttering-heartbeat | — |
| `HKCategoryTypeIdentifierRunnyNose` | Runny Nose | `supported` | symptom-runny-nose | healthkit-symptom-runny-nose | — |
| `HKCategoryTypeIdentifierSexualActivity` | Sexual Activity | `supported` | sexual-activity | grove-mobile-sexual-activity | — |
| `HKCategoryTypeIdentifierShortnessOfBreath` | Shortness of Breath | `supported` | symptom-shortness-of-breath | healthkit-symptom-shortness-of-breath | — |
| `HKCategoryTypeIdentifierSinusCongestion` | Sinus Congestion | `supported` | symptom-sinus-congestion | healthkit-symptom-sinus-congestion | — |
| `HKCategoryTypeIdentifierSkippedHeartbeat` | Skipped Heartbeat | `supported` | symptom-skipped-heartbeat | healthkit-symptom-skipped-heartbeat | — |
| `HKCategoryTypeIdentifierSleepAnalysis` | Sleep Analysis | `supported` | sleep-stage | grove-mobile-sleep-stage | — |
| `HKCategoryTypeIdentifierSleepApneaEvent` | Sleep Apnea Event | `intentionally-unsupported` | — | — | Device alert, not a measurement: an Apple proprietary screening algorithm's notification of possible pathology. The underlying signal (HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances) is the measurement surface; emitting the alert as an Observation would misrepresent a screening notification as a clinical finding. |
| `HKCategoryTypeIdentifierSleepChanges` | Sleep Changes | `supported` | symptom-sleep-changes | healthkit-symptom-sleep-changes | — |
| `HKCategoryTypeIdentifierSoreThroat` | Sore Throat | `supported` | symptom-sore-throat | healthkit-symptom-sore-throat | — |
| `HKCategoryTypeIdentifierToothbrushingEvent` | Toothbrushing Event | `supported` | toothbrushing-session | healthkit-toothbrushing-session | — |
| `HKCategoryTypeIdentifierVaginalDryness` | Vaginal Dryness | `supported` | vaginal-dryness | healthkit-vaginal-dryness | — |
| `HKCategoryTypeIdentifierVomiting` | Vomiting | `supported` | symptom-vomiting | healthkit-symptom-vomiting | — |
| `HKCategoryTypeIdentifierWheezing` | Wheezing | `supported` | symptom-wheezing | healthkit-symptom-wheezing | — |
| `HKCharacteristicTypeIdentifierActivityMoveMode` | Activity Move Mode | `intentionally-unsupported` | — | — | DECIDED: intentionally-unsupported. A ring-display preference has no semantically exact Mobile meaning; converting it would encode Apple product configuration as clinical data. Verifier attack (would a researcher want it?): the mode is only interpretive context for AppleMoveTime/ActiveEnergy rows, which carry their own units and are handled in their own rows; the mode adds no measurement content of its own. Reason survives. |
| `HKCharacteristicTypeIdentifierBiologicalSex` | Biological Sex | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.3.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierBloodType` | Blood Type | `supported` | blood-type | healthkit-blood-type | — |
| `HKCharacteristicTypeIdentifierDateOfBirth` | Date of Birth | `deferred` | — | — | A HealthKit characteristic describes the subject rather than a measurement. Version 0.3.0 publishes no admitted output contract for characteristics. |
| `HKCharacteristicTypeIdentifierFitzpatrickSkinType` | Fitzpatrick Skin Type | `intentionally-unsupported` | — | — | DECIDED: intentionally-unsupported — applied as decided, not re-decided. Verifier correction to the stated reason: an exact LOINC does exist (66555-4), so the decision cannot rest on missing terminology; it rests solely on the decided scope call (single-platform self-reported phenotype outside the measurement contract, no consumer in the exchange set). |
| `HKCharacteristicTypeIdentifierWheelchairUse` | Wheelchair Use | `supported` | wheelchair-use | healthkit-wheelchair-use | — |
| `HKClinicalTypeIdentifierAllergyRecord` | Allergy Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierClinicalNoteRecord` | Clinical Note Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierConditionRecord` | Condition Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierCoverageRecord` | Coverage Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierImmunizationRecord` | Immunization Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierLabResultRecord` | Lab Result Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierMedicationRecord` | Medication Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierProcedureRecord` | Procedure Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKClinicalTypeIdentifierVitalSignRecord` | Vital Sign Record | `platform-exclusive` | — | healthkit-clinical-record-document | — |
| `HKCorrelationTypeIdentifierBloodPressure` | Blood Pressure | `supported` | blood-pressure | grove-mobile-blood-pressure | — |
| `HKCorrelationTypeIdentifierFood` | Food | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKDataTypeIdentifierAudiogram` | Audiogram | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKDataTypeIdentifierElectrocardiogram` | ECG | `supported` | electrocardiogram | grove-sensor-ecg-observation; healthkit-ecg-observation | The caller supplies the HKElectrocardiogram, every voltage measurement with its exact timeSinceSampleStart, and each associated HKCategorySample when symptomsStatus is present. The adapter preserves symptom UUID/timing/type/severity and complete HKSourceRevision fields, classification, average heart rate, sampling frequency, reported count, Apple ECG algorithm-version metadata when present, source and waveform intervals, lead, offsets, and voltages without fetching or resampling. Explicit caller authorization for linkable symptom-source disclosure is required; otherwise conversion fails closed. |
| `HKDataTypeIdentifierHeartbeatSeries` | Heartbeat Series | `deferred` | — | — | The beat-to-beat interval series ships as a grove-csv-1 recording (heartbeat-series column schema) in the residual design pass; no Observation output is admitted. |
| `HKDataTypeStateOfMind` | State of Mind | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKDataTypeUserAnnotatedMedicationConcept` | User Annotated Medication Concept | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKDocumentTypeIdentifierCDA` | CDA Document | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKMedicationDoseEventTypeIdentifierMedicationDoseEvent` | Medication Dose Event | `deferred` | — | — | No shared or adapter-specific v0.2 output contract is published for this type. |
| `HKQuantityTypeIdentifierActiveEnergyBurned` | Active Energy Burned | `supported` | active-energy | grove-mobile-active-energy | — |
| `HKQuantityTypeIdentifierAppleExerciseTime` | Apple Exercise Time | `supported` | apple-exercise-time | healthkit-apple-exercise-time | — |
| `HKQuantityTypeIdentifierAppleMoveTime` | Apple Move Time | `supported` | apple-move-time | healthkit-apple-move-time | — |
| `HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances` | Apple Sleeping Breathing Disturbances | `supported` | sleeping-breathing-disturbances | healthkit-sleeping-breathing-disturbances | — |
| `HKQuantityTypeIdentifierAppleSleepingWristTemperature` | Apple Sleeping Wrist Temperature | `supported` | skin-temperature | grove-mobile-skin-temperature | — |
| `HKQuantityTypeIdentifierAppleStandTime` | Apple Stand Time | `supported` | apple-stand-time | healthkit-apple-stand-time | — |
| `HKQuantityTypeIdentifierAppleWalkingSteadiness` | Apple Walking Steadiness | `supported` | walking-steadiness | healthkit-walking-steadiness | — |
| `HKQuantityTypeIdentifierAtrialFibrillationBurden` | AFib Burden | `supported` | atrial-fibrillation-burden | healthkit-atrial-fibrillation-burden | — |
| `HKQuantityTypeIdentifierBasalBodyTemperature` | Basal Body Temperature | `supported` | basal-body-temperature | grove-mobile-basal-body-temperature | — |
| `HKQuantityTypeIdentifierBasalEnergyBurned` | Basal Energy Burned | `supported` | basal-energy | grove-mobile-basal-energy | — |
| `HKQuantityTypeIdentifierBloodAlcoholContent` | Blood Alcohol Content | `supported` | blood-alcohol-content | healthkit-blood-alcohol-content | — |
| `HKQuantityTypeIdentifierBloodGlucose` | Blood Glucose | `supported` | blood-glucose-unspecified-specimen | grove-mobile-blood-glucose-unspecified-specimen | — |
| `HKQuantityTypeIdentifierBloodPressureDiastolic` | Blood Pressure (Diastolic) | `supported` | blood-pressure | grove-mobile-blood-pressure | — |
| `HKQuantityTypeIdentifierBloodPressureSystolic` | Blood Pressure (Systolic) | `supported` | blood-pressure | grove-mobile-blood-pressure | — |
| `HKQuantityTypeIdentifierBodyFatPercentage` | Body Fat Percentage | `supported` | body-fat-percentage | grove-mobile-body-fat-percentage | — |
| `HKQuantityTypeIdentifierBodyMass` | Body Mass | `supported` | body-weight | grove-mobile-body-weight | — |
| `HKQuantityTypeIdentifierBodyMassIndex` | BMI | `supported` | body-mass-index | bmi; healthkit-observation | — |
| `HKQuantityTypeIdentifierBodyTemperature` | Body Temperature | `supported` | body-temperature | grove-mobile-body-temperature | — |
| `HKQuantityTypeIdentifierCrossCountrySkiingSpeed` | Cross Country Skiing Speed | `supported` | speed | grove-mobile-speed | — |
| `HKQuantityTypeIdentifierCyclingCadence` | Cycling Cadence | `supported` | cycling-cadence | grove-mobile-cycling-cadence | — |
| `HKQuantityTypeIdentifierCyclingFunctionalThresholdPower` | Cycling Functional Threshold Power | `supported` | cycling-functional-threshold-power | healthkit-cycling-functional-threshold-power | — |
| `HKQuantityTypeIdentifierCyclingPower` | Cycling Power | `supported` | power | grove-mobile-power | — |
| `HKQuantityTypeIdentifierCyclingSpeed` | Cycling Speed | `supported` | speed | grove-mobile-speed | — |
| `HKQuantityTypeIdentifierDietaryBiotin` | Dietary Biotin Intake | `supported` | dietary-biotin | grove-mobile-dietary-biotin | — |
| `HKQuantityTypeIdentifierDietaryCaffeine` | Dietary Caffeine Intake | `supported` | dietary-caffeine | grove-mobile-dietary-caffeine | — |
| `HKQuantityTypeIdentifierDietaryCalcium` | Dietary Calcium Intake | `supported` | dietary-calcium | grove-mobile-dietary-calcium | — |
| `HKQuantityTypeIdentifierDietaryCarbohydrates` | Dietary Carbohydrates Intake | `supported` | dietary-carbohydrates | grove-mobile-dietary-carbohydrates | — |
| `HKQuantityTypeIdentifierDietaryChloride` | Dietary Chloride Intake | `supported` | dietary-chloride | grove-mobile-dietary-chloride | — |
| `HKQuantityTypeIdentifierDietaryCholesterol` | Dietary Cholesterol Intake | `supported` | dietary-cholesterol | grove-mobile-dietary-cholesterol | — |
| `HKQuantityTypeIdentifierDietaryChromium` | Dietary Chromium Intake | `supported` | dietary-chromium | grove-mobile-dietary-chromium | — |
| `HKQuantityTypeIdentifierDietaryCopper` | Dietary Copper Intake | `supported` | dietary-copper | grove-mobile-dietary-copper | — |
| `HKQuantityTypeIdentifierDietaryEnergyConsumed` | Dietary Energy Consumed | `supported` | dietary-energy | grove-mobile-dietary-energy | — |
| `HKQuantityTypeIdentifierDietaryFatMonounsaturated` | Dietary Monounsaturated Fat Intake | `supported` | dietary-fat-monounsaturated | grove-mobile-dietary-fat-monounsaturated | — |
| `HKQuantityTypeIdentifierDietaryFatPolyunsaturated` | Dietary Polyunsaturated Fat Intake | `supported` | dietary-fat-polyunsaturated | grove-mobile-dietary-fat-polyunsaturated | — |
| `HKQuantityTypeIdentifierDietaryFatSaturated` | Dietary Saturated Fat Intake | `supported` | dietary-fat-saturated | grove-mobile-dietary-fat-saturated | — |
| `HKQuantityTypeIdentifierDietaryFatTotal` | Dietary Total Fat Intake | `supported` | dietary-fat-total | grove-mobile-dietary-fat-total | — |
| `HKQuantityTypeIdentifierDietaryFiber` | Dietary Fiber Intake | `supported` | dietary-fiber | grove-mobile-dietary-fiber | — |
| `HKQuantityTypeIdentifierDietaryFolate` | Dietary Folate Intake | `supported` | dietary-folate | grove-mobile-dietary-folate | — |
| `HKQuantityTypeIdentifierDietaryIodine` | Dietary Iodine Intake | `supported` | dietary-iodine | grove-mobile-dietary-iodine | — |
| `HKQuantityTypeIdentifierDietaryIron` | Dietary Iron Intake | `supported` | dietary-iron | grove-mobile-dietary-iron | — |
| `HKQuantityTypeIdentifierDietaryMagnesium` | Dietary Magnesium Intake | `supported` | dietary-magnesium | grove-mobile-dietary-magnesium | — |
| `HKQuantityTypeIdentifierDietaryManganese` | Dietary Manganese Intake | `supported` | dietary-manganese | grove-mobile-dietary-manganese | — |
| `HKQuantityTypeIdentifierDietaryMolybdenum` | Dietary Molybdenum Intake | `supported` | dietary-molybdenum | grove-mobile-dietary-molybdenum | — |
| `HKQuantityTypeIdentifierDietaryNiacin` | Dietary Niacin Intake | `supported` | dietary-niacin | grove-mobile-dietary-niacin | — |
| `HKQuantityTypeIdentifierDietaryPantothenicAcid` | Dietary Pantothenic Acid Intake | `supported` | dietary-pantothenic-acid | grove-mobile-dietary-pantothenic-acid | — |
| `HKQuantityTypeIdentifierDietaryPhosphorus` | Dietary Phosphorus Intake | `supported` | dietary-phosphorus | grove-mobile-dietary-phosphorus | — |
| `HKQuantityTypeIdentifierDietaryPotassium` | Dietary Potassium Intake | `supported` | dietary-potassium | grove-mobile-dietary-potassium | — |
| `HKQuantityTypeIdentifierDietaryProtein` | Dietary Protein Intake | `supported` | dietary-protein | grove-mobile-dietary-protein | — |
| `HKQuantityTypeIdentifierDietaryRiboflavin` | Dietary Riboflavin Intake | `supported` | dietary-riboflavin | grove-mobile-dietary-riboflavin | — |
| `HKQuantityTypeIdentifierDietarySelenium` | Dietary Selenium Intake | `supported` | dietary-selenium | grove-mobile-dietary-selenium | — |
| `HKQuantityTypeIdentifierDietarySodium` | Dietary Sodium Intake | `supported` | dietary-sodium | grove-mobile-dietary-sodium | — |
| `HKQuantityTypeIdentifierDietarySugar` | Dietary Sugar Intake | `supported` | dietary-sugar | grove-mobile-dietary-sugar | — |
| `HKQuantityTypeIdentifierDietaryThiamin` | Dietary Thiamin Intake | `supported` | dietary-thiamin | grove-mobile-dietary-thiamin | — |
| `HKQuantityTypeIdentifierDietaryVitaminA` | Dietary Vitamin A Intake | `supported` | dietary-vitamin-a | grove-mobile-dietary-vitamin-a | — |
| `HKQuantityTypeIdentifierDietaryVitaminB12` | Dietary Vitamin B12 Intake | `supported` | dietary-vitamin-b12 | grove-mobile-dietary-vitamin-b12 | — |
| `HKQuantityTypeIdentifierDietaryVitaminB6` | Dietary Vitamin B6 Intake | `supported` | dietary-vitamin-b6 | grove-mobile-dietary-vitamin-b6 | — |
| `HKQuantityTypeIdentifierDietaryVitaminC` | Dietary Vitamin C Intake | `supported` | dietary-vitamin-c | grove-mobile-dietary-vitamin-c | — |
| `HKQuantityTypeIdentifierDietaryVitaminD` | Dietary Vitamin D Intake | `supported` | dietary-vitamin-d | grove-mobile-dietary-vitamin-d | — |
| `HKQuantityTypeIdentifierDietaryVitaminE` | Dietary Vitamin E Intake | `supported` | dietary-vitamin-e | grove-mobile-dietary-vitamin-e | — |
| `HKQuantityTypeIdentifierDietaryVitaminK` | Dietary Vitamin K Intake | `supported` | dietary-vitamin-k | grove-mobile-dietary-vitamin-k | — |
| `HKQuantityTypeIdentifierDietaryWater` | Dietary Water Intake | `supported` | fluid-intake | grove-mobile-fluid-intake | — |
| `HKQuantityTypeIdentifierDietaryZinc` | Dietary Zinc Intake | `supported` | dietary-zinc | grove-mobile-dietary-zinc | — |
| `HKQuantityTypeIdentifierDistanceCrossCountrySkiing` | Cross-Country Skiing Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceCycling` | Cycling Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceDownhillSnowSports` | Downhill Snow Sports Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistancePaddleSports` | Paddle Sports Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceRowing` | Rowing Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceSkatingSports` | Skating Sports Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceSwimming` | Swimming Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceWalkingRunning` | Distance Walking/Running | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierDistanceWheelchair` | Wheelchair Distance | `supported` | distance | grove-mobile-distance | — |
| `HKQuantityTypeIdentifierElectrodermalActivity` | Electrodermal Activity | `supported` | electrodermal-activity | grove-mobile-electrodermal-activity | — |
| `HKQuantityTypeIdentifierEnvironmentalAudioExposure` | Environmental Audio Exposure | `supported` | environmental-audio-exposure | healthkit-environmental-audio-exposure | — |
| `HKQuantityTypeIdentifierEnvironmentalSoundReduction` | Environmental Sound Reduction | `supported` | environmental-sound-reduction | healthkit-environmental-sound-reduction | — |
| `HKQuantityTypeIdentifierEstimatedWorkoutEffortScore` | Estimated Workout Effort | `supported` | workout-effort-score | healthkit-workout-effort-score | — |
| `HKQuantityTypeIdentifierFlightsClimbed` | Flights Climbed | `supported` | flights-climbed | grove-mobile-flights-climbed | — |
| `HKQuantityTypeIdentifierForcedExpiratoryVolume1` | Forced Expiratory Volume (1 sec) | `supported` | forced-expiratory-volume-1 | healthkit-forced-expiratory-volume-1 | — |
| `HKQuantityTypeIdentifierForcedVitalCapacity` | Forced Vital Capacity | `supported` | forced-vital-capacity | healthkit-forced-vital-capacity | — |
| `HKQuantityTypeIdentifierHeadphoneAudioExposure` | Headphone Audio Exposure | `supported` | headphone-audio-exposure | healthkit-headphone-audio-exposure | — |
| `HKQuantityTypeIdentifierHeartRate` | Heart Rate | `supported` | heart-rate | grove-mobile-heart-rate | — |
| `HKQuantityTypeIdentifierHeartRateRecoveryOneMinute` | Heart Rate Recovery (1 min) | `supported` | heart-rate-recovery-one-minute | healthkit-heart-rate-recovery-one-minute | — |
| `HKQuantityTypeIdentifierHeartRateVariabilitySDNN` | Heart Rate Variability SDNN | `supported` | heart-rate-variability-sdnn | grove-mobile-heart-rate-variability-sdnn | — |
| `HKQuantityTypeIdentifierHeight` | Height | `supported` | body-height | grove-mobile-body-height | — |
| `HKQuantityTypeIdentifierInhalerUsage` | Inhaler Usage | `supported` | inhaler-usage | healthkit-inhaler-usage | — |
| `HKQuantityTypeIdentifierInsulinDelivery` | Insulin Delivery | `supported` | insulin-delivery | healthkit-insulin-delivery | — |
| `HKQuantityTypeIdentifierLeanBodyMass` | Lean Body Mass | `supported` | lean-body-mass | grove-mobile-lean-body-mass | — |
| `HKQuantityTypeIdentifierNikeFuel` | NikeFuel | `intentionally-unsupported` | — | — | NikeFuel is an opaque vendor index with an unpublished formula and a retired ecosystem; it has no physiological dimension, no UCUM representation beyond an arbitrary annotation, and no second source, so normalizing it would launder an undefined score into an exchange measurement. |
| `HKQuantityTypeIdentifierNumberOfAlcoholicBeverages` | Number of Alcoholic Beverages | `supported` | number-of-alcoholic-beverages | healthkit-number-of-alcoholic-beverages | — |
| `HKQuantityTypeIdentifierNumberOfTimesFallen` | Number of Times Fallen | `supported` | number-of-times-fallen | healthkit-number-of-times-fallen | — |
| `HKQuantityTypeIdentifierOxygenSaturation` | Oxygen Saturation | `supported` | oxygen-saturation | grove-mobile-oxygen-saturation | — |
| `HKQuantityTypeIdentifierPaddleSportsSpeed` | Paddle Sports Speed | `supported` | speed | grove-mobile-speed | — |
| `HKQuantityTypeIdentifierPeakExpiratoryFlowRate` | Peak Expiratory Flow Rate | `supported` | peak-expiratory-flow-rate | healthkit-peak-expiratory-flow-rate | — |
| `HKQuantityTypeIdentifierPeripheralPerfusionIndex` | Peripheral Perfusion Index | `supported` | peripheral-perfusion-index | healthkit-peripheral-perfusion-index | — |
| `HKQuantityTypeIdentifierPhysicalEffort` | Physical Effort | `supported` | physical-effort | healthkit-physical-effort | — |
| `HKQuantityTypeIdentifierPushCount` | Wheelchair Push Count | `supported` | wheelchair-push-count | grove-mobile-wheelchair-push-count | — |
| `HKQuantityTypeIdentifierRespiratoryRate` | Respiratory Rate | `supported` | respiratory-rate | grove-mobile-respiratory-rate | — |
| `HKQuantityTypeIdentifierRestingHeartRate` | Resting Heart Rate | `supported` | resting-heart-rate | grove-mobile-resting-heart-rate | — |
| `HKQuantityTypeIdentifierRowingSpeed` | Rowing Speed | `supported` | speed | grove-mobile-speed | — |
| `HKQuantityTypeIdentifierRunningGroundContactTime` | Ground Contact Time | `supported` | running-ground-contact-time | healthkit-running-ground-contact-time | — |
| `HKQuantityTypeIdentifierRunningPower` | Running Power | `supported` | power | grove-mobile-power | — |
| `HKQuantityTypeIdentifierRunningSpeed` | Running Speed | `supported` | speed | grove-mobile-speed | — |
| `HKQuantityTypeIdentifierRunningStrideLength` | Running Stride Length | `supported` | running-stride-length | healthkit-running-stride-length | — |
| `HKQuantityTypeIdentifierRunningVerticalOscillation` | Running Vertical Oscillation | `supported` | running-vertical-oscillation | healthkit-running-vertical-oscillation | — |
| `HKQuantityTypeIdentifierSixMinuteWalkTestDistance` | 6 Minute Walk Test Distance | `supported` | six-minute-walk-test-distance | healthkit-six-minute-walk-test-distance | — |
| `HKQuantityTypeIdentifierStairAscentSpeed` | Stair Ascent Speed | `supported` | stair-ascent-speed | healthkit-stair-ascent-speed | — |
| `HKQuantityTypeIdentifierStairDescentSpeed` | Stair Descent Speed | `supported` | stair-descent-speed | healthkit-stair-descent-speed | — |
| `HKQuantityTypeIdentifierStepCount` | Step Count | `supported` | step-count | grove-mobile-step-count | — |
| `HKQuantityTypeIdentifierSwimmingStrokeCount` | Swimming Stroke Count | `supported` | swimming-stroke-count | healthkit-swimming-stroke-count | — |
| `HKQuantityTypeIdentifierTimeInDaylight` | Time in Daylight | `supported` | time-in-daylight | healthkit-time-in-daylight | — |
| `HKQuantityTypeIdentifierUVExposure` | UV Exposure | `supported` | uv-exposure | healthkit-uv-exposure | — |
| `HKQuantityTypeIdentifierUnderwaterDepth` | Underwater Depth | `supported` | underwater-depth | healthkit-underwater-depth | — |
| `HKQuantityTypeIdentifierVO2Max` | VO2Max | `supported` | vo2-max | grove-mobile-vo2-max | — |
| `HKQuantityTypeIdentifierWaistCircumference` | Waist Circumference | `supported` | waist-circumference | healthkit-waist-circumference | — |
| `HKQuantityTypeIdentifierWalkingAsymmetryPercentage` | Walking Asymmetry Percentage | `supported` | walking-asymmetry | healthkit-walking-asymmetry | — |
| `HKQuantityTypeIdentifierWalkingDoubleSupportPercentage` | Walking Double Support Percentage | `supported` | walking-double-support | healthkit-walking-double-support | — |
| `HKQuantityTypeIdentifierWalkingHeartRateAverage` | Walking Heart Rate Average | `supported` | walking-heart-rate-average | healthkit-walking-heart-rate-average | — |
| `HKQuantityTypeIdentifierWalkingSpeed` | Walking Speed | `supported` | walking-speed | healthkit-walking-speed | — |
| `HKQuantityTypeIdentifierWalkingStepLength` | Walking Step Length | `supported` | walking-step-length | healthkit-walking-step-length | — |
| `HKQuantityTypeIdentifierWaterTemperature` | Water Temperature | `supported` | water-temperature | healthkit-water-temperature | — |
| `HKQuantityTypeIdentifierWorkoutEffortScore` | Workout Effort | `supported` | workout-effort-score | healthkit-workout-effort-score | — |
| `HKScoredAssessmentTypeIdentifierGAD7` | GAD-7 | `supported` | gad7-assessment | healthkit-gad7-assessment | — |
| `HKScoredAssessmentTypeIdentifierPHQ9` | PHQ-9 | `supported` | phq9-assessment | healthkit-phq9-assessment | — |
| `HKVisionPrescriptionTypeIdentifier` | Vision Prescription | `deferred` | — | — | A vision prescription is a clinical document, not a measurement; the residual design pass decides its envelope route and no Observation output is admitted. |
| `HKWorkoutRouteTypeIdentifier` | Workout Route | `deferred` | — | — | No shared or HealthKit-adapter v0.2 output contract is published for this sample type. |
| `HKWorkoutTypeIdentifier` | Workout | `supported` | workout, workout-segment | grove-mobile-workout; grove-mobile-workout-segment | — |

## Derived aggregate contracts

These rows are derived mappings, not HealthKit platform source identifiers, and are excluded from the source-type count and source-type CodeSystem.

| Aggregate | Title | Input source type(s) | Contract status | Measurement | Target profile | Binding reason / requirement |
| --- | --- | --- | --- | --- | --- | --- |
| `sleep-duration-session-aggregate` | Sleep Duration Session Aggregate | `HKCategoryTypeIdentifierSleepAnalysis` | `deferred` | sleep-duration | grove-mobile-sleep-duration | This is not a HealthKit platform source identifier. Version 0.3.0 does not define the session-boundary aggregation contract; individual admitted samples map only to sleep stage. |
