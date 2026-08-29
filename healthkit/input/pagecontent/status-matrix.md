<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

### HealthKit support matrix

This table is the normative support inventory for all 218 Apple HealthKit source types in the iPhoneOS 26.5 baseline from Xcode 26.6 build `17F113`. Each source type has one status, and producers may emit only the output contracts named for admitted rows. `supported`, `platform-exclusive`, and `mapped-standard` each admit only the output contract(s) named in that row. `unmodeled`, `deferred`, and `intentionally-unsupported` admit no output; producers fail closed.

| HealthKit type | Title | Contract status | Measurement | Direct profile claim(s) | Binding reason / requirement |
| --- | --- | --- | --- | --- | --- |
| `HKCategoryTypeIdentifierAbdominalCramps` | Abdominal Cramps | `supported` | symptom-abdominal-cramps | healthkit-symptom-abdominal-cramps | — |
| `HKCategoryTypeIdentifierAcne` | Acne | `supported` | symptom-acne | healthkit-symptom-acne | — |
| `HKCategoryTypeIdentifierAppetiteChanges` | Appetite Changes | `supported` | symptom-appetite-changes | healthkit-symptom-appetite-changes | — |
| `HKCategoryTypeIdentifierAppleStandHour` | Apple Stand Hour | `supported` | apple-stand-hour | healthkit-apple-stand-hour | — |
| `HKCategoryTypeIdentifierAppleWalkingSteadinessEvent` | Apple Walking Steadiness Event | `supported` | walking-steadiness-notification | healthkit-walking-steadiness-notification | — |
| `HKCategoryTypeIdentifierAudioExposureEvent` | Audio Exposure Event | `supported` | environmental-audio-exposure-notification | healthkit-environmental-audio-exposure-notification | — |
| `HKCategoryTypeIdentifierBladderIncontinence` | Bladder Incontinence | `supported` | bladder-incontinence | healthkit-bladder-incontinence | — |
| `HKCategoryTypeIdentifierBleedingAfterPregnancy` | Bleeding After Pregnancy | `supported` | bleeding-after-pregnancy | healthkit-bleeding-after-pregnancy | — |
| `HKCategoryTypeIdentifierBleedingDuringPregnancy` | Bleeding During Pregnancy | `supported` | bleeding-during-pregnancy | healthkit-bleeding-during-pregnancy | — |
| `HKCategoryTypeIdentifierBloating` | Bloating | `supported` | symptom-bloating | healthkit-symptom-bloating | — |
| `HKCategoryTypeIdentifierBreastPain` | Breast Pain | `supported` | symptom-breast-pain | healthkit-symptom-breast-pain | — |
| `HKCategoryTypeIdentifierCervicalMucusQuality` | Cervical Mucus Quality | `supported` | cervical-mucus-quality | grove-mobile-cervical-mucus-quality; healthkit-observation | — |
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
| `HKCategoryTypeIdentifierHeadphoneAudioExposureEvent` | Headphone Audio Exposure Event | `supported` | headphone-audio-exposure-notification | healthkit-headphone-audio-exposure-notification | — |
| `HKCategoryTypeIdentifierHeartburn` | Heartburn | `supported` | symptom-heartburn | healthkit-symptom-heartburn | — |
| `HKCategoryTypeIdentifierHighHeartRateEvent` | High Heart Rate Event | `supported` | high-heart-rate-notification | healthkit-high-heart-rate-notification | — |
| `HKCategoryTypeIdentifierHotFlashes` | Hot Flashes | `supported` | symptom-hot-flashes | healthkit-symptom-hot-flashes | — |
| `HKCategoryTypeIdentifierHypertensionEvent` | Hypertension Event | `supported` | hypertension-notification | healthkit-hypertension-notification | Admit only the occurrence of the source platform's proprietary screening notification. The Observation code and result remain HealthKit-specific; no blood-pressure quantity, hypertension diagnosis, clinical finding, threshold, or algorithmic interpretation may be inferred. Cuff blood-pressure quantities remain a separate measurement surface. |
| `HKCategoryTypeIdentifierInfrequentMenstrualCycles` | Infrequent Menstrual Cycles | `supported` | infrequent-menstrual-cycles | healthkit-infrequent-menstrual-cycles | — |
| `HKCategoryTypeIdentifierIntermenstrualBleeding` | Intermenstrual Bleeding | `supported` | intermenstrual-bleeding | grove-mobile-intermenstrual-bleeding; healthkit-observation | — |
| `HKCategoryTypeIdentifierIrregularHeartRhythmEvent` | Irregular Heart Rhythm Event | `supported` | irregular-heart-rhythm-notification | healthkit-irregular-heart-rhythm-notification | — |
| `HKCategoryTypeIdentifierIrregularMenstrualCycles` | Irregular Menstrual Cycles | `supported` | irregular-menstrual-cycles | healthkit-irregular-menstrual-cycles | — |
| `HKCategoryTypeIdentifierLactation` | Lactation | `supported` | lactation-status | healthkit-lactation-status | — |
| `HKCategoryTypeIdentifierLossOfSmell` | Loss of Smell | `supported` | symptom-loss-of-smell | healthkit-symptom-loss-of-smell | — |
| `HKCategoryTypeIdentifierLossOfTaste` | Loss of Taste | `supported` | symptom-loss-of-taste | healthkit-symptom-loss-of-taste | — |
| `HKCategoryTypeIdentifierLowCardioFitnessEvent` | Low Cardio Fitness Event | `supported` | low-cardio-fitness-notification | healthkit-low-cardio-fitness-notification | — |
| `HKCategoryTypeIdentifierLowHeartRateEvent` | Low Heart Rate Event | `supported` | low-heart-rate-notification | healthkit-low-heart-rate-notification | — |
| `HKCategoryTypeIdentifierLowerBackPain` | Lower Back Pain | `supported` | symptom-lower-back-pain | healthkit-symptom-lower-back-pain | — |
| `HKCategoryTypeIdentifierMemoryLapse` | Memory Lapse | `supported` | symptom-memory-lapse | healthkit-symptom-memory-lapse | — |
| `HKCategoryTypeIdentifierMenstrualFlow` | Menstrual Flow | `supported` | menstruation-flow | grove-mobile-menstruation-flow; healthkit-observation | — |
| `HKCategoryTypeIdentifierMindfulSession` | Mindful Session | `supported` | mindfulness-session | grove-mobile-mindfulness-session; healthkit-observation | — |
| `HKCategoryTypeIdentifierMoodChanges` | Mood Changes | `supported` | symptom-mood-changes | healthkit-symptom-mood-changes | — |
| `HKCategoryTypeIdentifierNausea` | Nausea | `supported` | symptom-nausea | healthkit-symptom-nausea | — |
| `HKCategoryTypeIdentifierNightSweats` | Night Sweats | `supported` | symptom-night-sweats | healthkit-symptom-night-sweats | — |
| `HKCategoryTypeIdentifierOvulationTestResult` | Ovulation Test Result | `supported` | ovulation-test-result | grove-mobile-ovulation-test-result; healthkit-observation | — |
| `HKCategoryTypeIdentifierPelvicPain` | Pelvic Pain | `supported` | symptom-pelvic-pain | healthkit-symptom-pelvic-pain | — |
| `HKCategoryTypeIdentifierPersistentIntermenstrualBleeding` | Persistent Intermenstrual Bleeding | `supported` | persistent-intermenstrual-bleeding | healthkit-persistent-intermenstrual-bleeding | — |
| `HKCategoryTypeIdentifierPregnancy` | Pregnancy | `supported` | pregnancy-status | healthkit-pregnancy-status | — |
| `HKCategoryTypeIdentifierPregnancyTestResult` | Pregnancy Test Result | `supported` | pregnancy-test-result | healthkit-pregnancy-test-result | — |
| `HKCategoryTypeIdentifierProgesteroneTestResult` | Progesterone Test Result | `supported` | progesterone-test-result | healthkit-progesterone-test-result | — |
| `HKCategoryTypeIdentifierProlongedMenstrualPeriods` | Prolonged Menstrual Periods | `supported` | prolonged-menstrual-periods | healthkit-prolonged-menstrual-periods | — |
| `HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat` | Rapid/Pounding/Fluttering Heartbeat | `supported` | symptom-rapid-pounding-or-fluttering-heartbeat | healthkit-symptom-rapid-pounding-or-fluttering-heartbeat | — |
| `HKCategoryTypeIdentifierRunnyNose` | Runny Nose | `supported` | symptom-runny-nose | healthkit-symptom-runny-nose | — |
| `HKCategoryTypeIdentifierSexualActivity` | Sexual Activity | `supported` | sexual-activity | grove-mobile-sexual-activity; healthkit-observation | — |
| `HKCategoryTypeIdentifierShortnessOfBreath` | Shortness of Breath | `supported` | symptom-shortness-of-breath | healthkit-symptom-shortness-of-breath | — |
| `HKCategoryTypeIdentifierSinusCongestion` | Sinus Congestion | `supported` | symptom-sinus-congestion | healthkit-symptom-sinus-congestion | — |
| `HKCategoryTypeIdentifierSkippedHeartbeat` | Skipped Heartbeat | `supported` | symptom-skipped-heartbeat | healthkit-symptom-skipped-heartbeat | — |
| `HKCategoryTypeIdentifierSleepAnalysis` | Sleep Analysis | `supported` | sleep-stage | grove-mobile-sleep-stage; healthkit-observation | — |
| `HKCategoryTypeIdentifierSleepApneaEvent` | Sleep Apnea Event | `supported` | sleep-apnea-notification | healthkit-sleep-apnea-notification | — |
| `HKCategoryTypeIdentifierSleepChanges` | Sleep Changes | `supported` | symptom-sleep-changes | healthkit-symptom-sleep-changes | — |
| `HKCategoryTypeIdentifierSoreThroat` | Sore Throat | `supported` | symptom-sore-throat | healthkit-symptom-sore-throat | — |
| `HKCategoryTypeIdentifierToothbrushingEvent` | Toothbrushing Event | `supported` | toothbrushing-session | healthkit-toothbrushing-session | — |
| `HKCategoryTypeIdentifierVaginalDryness` | Vaginal Dryness | `supported` | vaginal-dryness | healthkit-vaginal-dryness | — |
| `HKCategoryTypeIdentifierVomiting` | Vomiting | `supported` | symptom-vomiting | healthkit-symptom-vomiting | — |
| `HKCategoryTypeIdentifierWheezing` | Wheezing | `supported` | symptom-wheezing | healthkit-symptom-wheezing | — |
| `HKCharacteristicTypeIdentifierActivityMoveMode` | Activity Move Mode | `intentionally-unsupported` | — | — | A ring-display preference has no semantically exact Mobile meaning, and converting it would encode an Apple product configuration as clinical data. The mode is interpretive context for the Apple move-time and active-energy rows, which carry their own units and are converted in their own right; it adds no measurement content of its own. |
| `HKCharacteristicTypeIdentifierBiologicalSex` | Biological Sex | `supported` | biological-sex | healthkit-biological-sex | Emit the healthkit-biological-sex Observation only for HKBiologicalSex.female, .male, or .other. LOINC 46098-0 'Sex' identifies the observation concept; do not relabel the source as LOINC 76689-9 'Sex assigned at birth', because HealthKit does not assert that provenance. Preserve the exact HealthKit result in the required Grove value set, and emit no Observation for .notSet. |
| `HKCharacteristicTypeIdentifierBloodType` | Blood Type | `supported` | blood-type | healthkit-blood-type | — |
| `HKCharacteristicTypeIdentifierDateOfBirth` | Date of Birth | `supported` | date-of-birth | healthkit-date-of-birth | The mapping is defined, but disclosure is fail-closed: emit the healthkit-date-of-birth Observation only when deployment policy explicitly authorizes exchanging this direct identifier. Otherwise emit no resource. Never substitute an inferred date, silently reduce precision, or place the value on the pseudonymous exchange Patient; deployments that only require age must derive it under their own approved policy. |
| `HKCharacteristicTypeIdentifierFitzpatrickSkinType` | Fitzpatrick Skin Type | `supported` | fitzpatrick-skin-type | healthkit-fitzpatrick-skin-type | Emit the healthkit-fitzpatrick-skin-type Observation only for HealthKit's six stated Fitzpatrick categories, preserving the exact category in the required Grove value set. Treat the value as source-reported classification, not a measured or inferred skin phenotype, and emit no Observation for .notSet. |
| `HKCharacteristicTypeIdentifierWheelchairUse` | Wheelchair Use | `supported` | wheelchair-use | healthkit-wheelchair-use | — |
| `HKClinicalTypeIdentifierAllergyRecord` | Allergy Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierClinicalNoteRecord` | Clinical Note Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierConditionRecord` | Condition Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierCoverageRecord` | Coverage Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierImmunizationRecord` | Immunization Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierLabResultRecord` | Lab Result Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierMedicationRecord` | Medication Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierProcedureRecord` | Procedure Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKClinicalTypeIdentifierVitalSignRecord` | Vital Sign Record | `platform-exclusive` | — | healthkit-clinical-record-document | Admit a HealthKit clinical record only when HKFHIRVersion.fhirRelease is r4. Reject dstu2, unknown, a missing release, and every future release before emitting a DocumentReference; the payload is preserved byte-for-byte and never upgraded, downgraded, or inferred from its JSON shape. |
| `HKCorrelationTypeIdentifierBloodPressure` | Blood Pressure | `supported` | blood-pressure | grove-mobile-blood-pressure; healthkit-observation | — |
| `HKCorrelationTypeIdentifierFood` | Food | `supported` | food-correlation | healthkit-food-correlation | — |
| `HKDataTypeIdentifierAudiogram` | Audiogram | `supported` | audiogram-panel | healthkit-audiogram-panel | — |
| `HKDataTypeIdentifierElectrocardiogram` | ECG | `supported` | electrocardiogram | grove-sensor-ecg-observation; healthkit-ecg-observation | The caller supplies the HKElectrocardiogram, every voltage measurement with its exact timeSinceSampleStart, and each associated HKCategorySample when symptomsStatus is present. Classification is Observation.interpretation; Apple ECG algorithm version is Observation.method; optional average heart rate is a separate LOINC 8867-4 Observation derived from the waveform. Each supplied symptom is converted through its existing HealthKit symptom Observation profile as a separate source event, and the ECG hasMember carries that Observation's opaque source-output Identifier. Sampling frequency and reported count are validated against SampledData but are not duplicated on the wire. The adapter preserves source and waveform intervals, lead, offsets, and voltages without fetching or resampling. |
| `HKDataTypeIdentifierHeartbeatSeries` | Heartbeat Series | `platform-exclusive` | — | grove-sensor-recording-document; healthkit-recording-document | The beat-to-beat interval series is admitted as a recording document carrying the published beat-interval-series column schema. No shared measurement models a beat series, so the samples are carried rather than reduced to a scalar. |
| `HKDataTypeStateOfMind` | State of Mind | `supported` | state-of-mind | healthkit-state-of-mind | — |
| `HKDataTypeUserAnnotatedMedicationConcept` | User Annotated Medication Concept | `platform-exclusive` | — | healthkit-user-annotated-medication | A non-archived tracked medication is admitted as a MedicationStatement identified by the HKHealthConceptIdentifier of its concept, carrying the person's nickname, the platform's general form, whether a schedule exists, and status active. An archived medication is not admitted, because archival alone does not establish that medication use was completed or stopped. |
| `HKDocumentTypeIdentifierCDA` | CDA Document | `platform-exclusive` | — | grove-sensor-recording-document; healthkit-recording-document | A CDA document is carried byte-for-byte as a recording document. Grove never asserts conformance over another issuer's document, the same treatment a provider-issued clinical record receives. |
| `HKMedicationDoseEventTypeIdentifierMedicationDoseEvent` | Medication Dose Event | `platform-exclusive` | — | healthkit-medication-dose-event | A logged dose is admitted as a MedicationAdministration that keeps the exact HKMedicationDoseEvent.LogStatus and the schedule it was logged against beside the R4 status, which collapses six source cases onto three codes. The medication is named by the same HKHealthConceptIdentifier the tracked-medication statement carries. |
| `HKQuantityTypeIdentifierActiveEnergyBurned` | Active Energy Burned | `supported` | active-energy | grove-mobile-active-energy; healthkit-observation | — |
| `HKQuantityTypeIdentifierAppleExerciseTime` | Apple Exercise Time | `supported` | apple-exercise-time | healthkit-apple-exercise-time | — |
| `HKQuantityTypeIdentifierAppleMoveTime` | Apple Move Time | `supported` | apple-move-time | healthkit-apple-move-time | — |
| `HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances` | Apple Sleeping Breathing Disturbances | `supported` | sleeping-breathing-disturbances | healthkit-sleeping-breathing-disturbances | — |
| `HKQuantityTypeIdentifierAppleSleepingWristTemperature` | Apple Sleeping Wrist Temperature | `supported` | skin-temperature | grove-mobile-skin-temperature; healthkit-observation | — |
| `HKQuantityTypeIdentifierAppleStandTime` | Apple Stand Time | `supported` | apple-stand-time | healthkit-apple-stand-time | — |
| `HKQuantityTypeIdentifierAppleWalkingSteadiness` | Apple Walking Steadiness | `supported` | walking-steadiness | healthkit-walking-steadiness | — |
| `HKQuantityTypeIdentifierAtrialFibrillationBurden` | AFib Burden | `supported` | atrial-fibrillation-burden | healthkit-atrial-fibrillation-burden | — |
| `HKQuantityTypeIdentifierBasalBodyTemperature` | Basal Body Temperature | `supported` | basal-body-temperature | grove-mobile-basal-body-temperature; healthkit-observation | — |
| `HKQuantityTypeIdentifierBasalEnergyBurned` | Basal Energy Burned | `supported` | basal-energy | grove-mobile-basal-energy; healthkit-observation | — |
| `HKQuantityTypeIdentifierBloodAlcoholContent` | Blood Alcohol Content | `supported` | blood-alcohol-content | healthkit-blood-alcohol-content | — |
| `HKQuantityTypeIdentifierBloodGlucose` | Blood Glucose | `supported` | blood-glucose-unspecified-specimen | grove-mobile-blood-glucose-unspecified-specimen; healthkit-observation | — |
| `HKQuantityTypeIdentifierBloodPressureDiastolic` | Blood Pressure (Diastolic) | `intentionally-unsupported` | — | — | A diastolic quantity alone cannot populate the required two-component blood-pressure panel. Convert blood pressure only from HKCorrelationTypeIdentifierBloodPressure. |
| `HKQuantityTypeIdentifierBloodPressureSystolic` | Blood Pressure (Systolic) | `intentionally-unsupported` | — | — | A systolic quantity alone cannot populate the required two-component blood-pressure panel. Convert blood pressure only from HKCorrelationTypeIdentifierBloodPressure. |
| `HKQuantityTypeIdentifierBodyFatPercentage` | Body Fat Percentage | `supported` | body-fat-percentage | grove-mobile-body-fat-percentage; healthkit-observation | — |
| `HKQuantityTypeIdentifierBodyMass` | Body Mass | `supported` | body-weight | grove-mobile-body-weight; healthkit-observation | — |
| `HKQuantityTypeIdentifierBodyMassIndex` | BMI | `supported` | body-mass-index | bmi; healthkit-observation | — |
| `HKQuantityTypeIdentifierBodyTemperature` | Body Temperature | `supported` | body-temperature | grove-mobile-body-temperature; healthkit-observation | — |
| `HKQuantityTypeIdentifierCrossCountrySkiingSpeed` | Cross Country Skiing Speed | `supported` | speed | grove-mobile-speed; healthkit-observation | — |
| `HKQuantityTypeIdentifierCyclingCadence` | Cycling Cadence | `supported` | cycling-cadence | grove-mobile-cycling-cadence; healthkit-observation | — |
| `HKQuantityTypeIdentifierCyclingFunctionalThresholdPower` | Cycling Functional Threshold Power | `supported` | cycling-functional-threshold-power | healthkit-cycling-functional-threshold-power | — |
| `HKQuantityTypeIdentifierCyclingPower` | Cycling Power | `supported` | power | grove-mobile-power; healthkit-observation | — |
| `HKQuantityTypeIdentifierCyclingSpeed` | Cycling Speed | `supported` | speed | grove-mobile-speed; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryBiotin` | Dietary Biotin Intake | `supported` | dietary-biotin | grove-mobile-dietary-biotin; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryCaffeine` | Dietary Caffeine Intake | `supported` | dietary-caffeine | grove-mobile-dietary-caffeine; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryCalcium` | Dietary Calcium Intake | `supported` | dietary-calcium | grove-mobile-dietary-calcium; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryCarbohydrates` | Dietary Carbohydrates Intake | `supported` | dietary-carbohydrates | grove-mobile-dietary-carbohydrates; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryChloride` | Dietary Chloride Intake | `supported` | dietary-chloride | grove-mobile-dietary-chloride; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryCholesterol` | Dietary Cholesterol Intake | `supported` | dietary-cholesterol | grove-mobile-dietary-cholesterol; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryChromium` | Dietary Chromium Intake | `supported` | dietary-chromium | grove-mobile-dietary-chromium; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryCopper` | Dietary Copper Intake | `supported` | dietary-copper | grove-mobile-dietary-copper; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryEnergyConsumed` | Dietary Energy Consumed | `supported` | dietary-energy | grove-mobile-dietary-energy; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryFatMonounsaturated` | Dietary Monounsaturated Fat Intake | `supported` | dietary-fat-monounsaturated | grove-mobile-dietary-fat-monounsaturated; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryFatPolyunsaturated` | Dietary Polyunsaturated Fat Intake | `supported` | dietary-fat-polyunsaturated | grove-mobile-dietary-fat-polyunsaturated; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryFatSaturated` | Dietary Saturated Fat Intake | `supported` | dietary-fat-saturated | grove-mobile-dietary-fat-saturated; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryFatTotal` | Dietary Total Fat Intake | `supported` | dietary-fat-total | grove-mobile-dietary-fat-total; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryFiber` | Dietary Fiber Intake | `supported` | dietary-fiber | grove-mobile-dietary-fiber; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryFolate` | Dietary Folate Intake | `supported` | dietary-folate | grove-mobile-dietary-folate; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryIodine` | Dietary Iodine Intake | `supported` | dietary-iodine | grove-mobile-dietary-iodine; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryIron` | Dietary Iron Intake | `supported` | dietary-iron | grove-mobile-dietary-iron; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryMagnesium` | Dietary Magnesium Intake | `supported` | dietary-magnesium | grove-mobile-dietary-magnesium; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryManganese` | Dietary Manganese Intake | `supported` | dietary-manganese | grove-mobile-dietary-manganese; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryMolybdenum` | Dietary Molybdenum Intake | `supported` | dietary-molybdenum | grove-mobile-dietary-molybdenum; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryNiacin` | Dietary Niacin Intake | `supported` | dietary-niacin | grove-mobile-dietary-niacin; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryPantothenicAcid` | Dietary Pantothenic Acid Intake | `supported` | dietary-pantothenic-acid | grove-mobile-dietary-pantothenic-acid; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryPhosphorus` | Dietary Phosphorus Intake | `supported` | dietary-phosphorus | grove-mobile-dietary-phosphorus; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryPotassium` | Dietary Potassium Intake | `supported` | dietary-potassium | grove-mobile-dietary-potassium; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryProtein` | Dietary Protein Intake | `supported` | dietary-protein | grove-mobile-dietary-protein; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryRiboflavin` | Dietary Riboflavin Intake | `supported` | dietary-riboflavin | grove-mobile-dietary-riboflavin; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietarySelenium` | Dietary Selenium Intake | `supported` | dietary-selenium | grove-mobile-dietary-selenium; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietarySodium` | Dietary Sodium Intake | `supported` | dietary-sodium | grove-mobile-dietary-sodium; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietarySugar` | Dietary Sugar Intake | `supported` | dietary-sugar | grove-mobile-dietary-sugar; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryThiamin` | Dietary Thiamin Intake | `supported` | dietary-thiamin | grove-mobile-dietary-thiamin; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminA` | Dietary Vitamin A Intake | `supported` | dietary-vitamin-a | grove-mobile-dietary-vitamin-a; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminB12` | Dietary Vitamin B12 Intake | `supported` | dietary-vitamin-b12 | grove-mobile-dietary-vitamin-b12; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminB6` | Dietary Vitamin B6 Intake | `supported` | dietary-vitamin-b6 | grove-mobile-dietary-vitamin-b6; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminC` | Dietary Vitamin C Intake | `supported` | dietary-vitamin-c | grove-mobile-dietary-vitamin-c; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminD` | Dietary Vitamin D Intake | `supported` | dietary-vitamin-d | grove-mobile-dietary-vitamin-d; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminE` | Dietary Vitamin E Intake | `supported` | dietary-vitamin-e | grove-mobile-dietary-vitamin-e; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryVitaminK` | Dietary Vitamin K Intake | `supported` | dietary-vitamin-k | grove-mobile-dietary-vitamin-k; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryWater` | Dietary Water Intake | `supported` | fluid-intake | grove-mobile-fluid-intake; healthkit-observation | — |
| `HKQuantityTypeIdentifierDietaryZinc` | Dietary Zinc Intake | `supported` | dietary-zinc | grove-mobile-dietary-zinc; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceCrossCountrySkiing` | Cross-Country Skiing Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceCycling` | Cycling Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceDownhillSnowSports` | Downhill Snow Sports Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistancePaddleSports` | Paddle Sports Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceRowing` | Rowing Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceSkatingSports` | Skating Sports Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceSwimming` | Swimming Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceWalkingRunning` | Distance Walking/Running | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierDistanceWheelchair` | Wheelchair Distance | `supported` | distance | grove-mobile-distance; healthkit-observation | — |
| `HKQuantityTypeIdentifierElectrodermalActivity` | Electrodermal Activity | `supported` | electrodermal-activity | grove-mobile-electrodermal-activity; healthkit-observation | — |
| `HKQuantityTypeIdentifierEnvironmentalAudioExposure` | Environmental Audio Exposure | `supported` | environmental-audio-exposure | healthkit-environmental-audio-exposure | — |
| `HKQuantityTypeIdentifierEnvironmentalSoundReduction` | Environmental Sound Reduction | `supported` | environmental-sound-reduction | healthkit-environmental-sound-reduction | — |
| `HKQuantityTypeIdentifierEstimatedWorkoutEffortScore` | Estimated Workout Effort | `supported` | workout-effort-score | healthkit-workout-effort-score | — |
| `HKQuantityTypeIdentifierFlightsClimbed` | Flights Climbed | `supported` | flights-climbed | grove-mobile-flights-climbed; healthkit-observation | — |
| `HKQuantityTypeIdentifierForcedExpiratoryVolume1` | Forced Expiratory Volume (1 sec) | `supported` | forced-expiratory-volume-1 | healthkit-forced-expiratory-volume-1 | — |
| `HKQuantityTypeIdentifierForcedVitalCapacity` | Forced Vital Capacity | `supported` | forced-vital-capacity | healthkit-forced-vital-capacity | — |
| `HKQuantityTypeIdentifierHeadphoneAudioExposure` | Headphone Audio Exposure | `supported` | headphone-audio-exposure | healthkit-headphone-audio-exposure | — |
| `HKQuantityTypeIdentifierHeartRate` | Heart Rate | `supported` | heart-rate | grove-mobile-heart-rate; healthkit-observation | — |
| `HKQuantityTypeIdentifierHeartRateRecoveryOneMinute` | Heart Rate Recovery (1 min) | `supported` | heart-rate-recovery-one-minute | healthkit-heart-rate-recovery-one-minute | — |
| `HKQuantityTypeIdentifierHeartRateVariabilitySDNN` | Heart Rate Variability SDNN | `supported` | heart-rate-variability-sdnn | grove-mobile-heart-rate-variability-sdnn; healthkit-observation | — |
| `HKQuantityTypeIdentifierHeight` | Height | `supported` | body-height | grove-mobile-body-height; healthkit-observation | — |
| `HKQuantityTypeIdentifierInhalerUsage` | Inhaler Usage | `supported` | inhaler-usage | healthkit-inhaler-usage | — |
| `HKQuantityTypeIdentifierInsulinDelivery` | Insulin Delivery | `supported` | insulin-delivery | healthkit-insulin-delivery | — |
| `HKQuantityTypeIdentifierLeanBodyMass` | Lean Body Mass | `supported` | lean-body-mass | grove-mobile-lean-body-mass; healthkit-observation | — |
| `HKQuantityTypeIdentifierNikeFuel` | NikeFuel | `intentionally-unsupported` | — | — | NikeFuel is an opaque vendor index with an unpublished formula and a retired ecosystem; it has no physiological dimension, no UCUM representation beyond an arbitrary annotation, and no second source, so normalizing it would launder an undefined score into an exchange measurement. |
| `HKQuantityTypeIdentifierNumberOfAlcoholicBeverages` | Number of Alcoholic Beverages | `supported` | number-of-alcoholic-beverages | healthkit-number-of-alcoholic-beverages | — |
| `HKQuantityTypeIdentifierNumberOfTimesFallen` | Number of Times Fallen | `supported` | number-of-times-fallen | healthkit-number-of-times-fallen | — |
| `HKQuantityTypeIdentifierOxygenSaturation` | Oxygen Saturation | `supported` | oxygen-saturation | grove-mobile-oxygen-saturation; healthkit-observation | — |
| `HKQuantityTypeIdentifierPaddleSportsSpeed` | Paddle Sports Speed | `supported` | speed | grove-mobile-speed; healthkit-observation | — |
| `HKQuantityTypeIdentifierPeakExpiratoryFlowRate` | Peak Expiratory Flow Rate | `supported` | peak-expiratory-flow-rate | healthkit-peak-expiratory-flow-rate | — |
| `HKQuantityTypeIdentifierPeripheralPerfusionIndex` | Peripheral Perfusion Index | `supported` | peripheral-perfusion-index | healthkit-peripheral-perfusion-index | — |
| `HKQuantityTypeIdentifierPhysicalEffort` | Physical Effort | `supported` | physical-effort | healthkit-physical-effort | — |
| `HKQuantityTypeIdentifierPushCount` | Wheelchair Push Count | `supported` | wheelchair-push-count | grove-mobile-wheelchair-push-count; healthkit-observation | — |
| `HKQuantityTypeIdentifierRespiratoryRate` | Respiratory Rate | `supported` | respiratory-rate | grove-mobile-respiratory-rate; healthkit-observation | — |
| `HKQuantityTypeIdentifierRestingHeartRate` | Resting Heart Rate | `supported` | resting-heart-rate | grove-mobile-resting-heart-rate; healthkit-observation | — |
| `HKQuantityTypeIdentifierRowingSpeed` | Rowing Speed | `supported` | speed | grove-mobile-speed; healthkit-observation | — |
| `HKQuantityTypeIdentifierRunningGroundContactTime` | Ground Contact Time | `supported` | running-ground-contact-time | healthkit-running-ground-contact-time | — |
| `HKQuantityTypeIdentifierRunningPower` | Running Power | `supported` | power | grove-mobile-power; healthkit-observation | — |
| `HKQuantityTypeIdentifierRunningSpeed` | Running Speed | `supported` | speed | grove-mobile-speed; healthkit-observation | — |
| `HKQuantityTypeIdentifierRunningStrideLength` | Running Stride Length | `supported` | running-stride-length | healthkit-running-stride-length | — |
| `HKQuantityTypeIdentifierRunningVerticalOscillation` | Running Vertical Oscillation | `supported` | running-vertical-oscillation | healthkit-running-vertical-oscillation | — |
| `HKQuantityTypeIdentifierSixMinuteWalkTestDistance` | 6 Minute Walk Test Distance | `supported` | six-minute-walk-test-distance | healthkit-six-minute-walk-test-distance | — |
| `HKQuantityTypeIdentifierStairAscentSpeed` | Stair Ascent Speed | `supported` | stair-ascent-speed | healthkit-stair-ascent-speed | — |
| `HKQuantityTypeIdentifierStairDescentSpeed` | Stair Descent Speed | `supported` | stair-descent-speed | healthkit-stair-descent-speed | — |
| `HKQuantityTypeIdentifierStepCount` | Step Count | `supported` | step-count | grove-mobile-step-count; healthkit-observation | — |
| `HKQuantityTypeIdentifierSwimmingStrokeCount` | Swimming Stroke Count | `supported` | swimming-stroke-count | healthkit-swimming-stroke-count | — |
| `HKQuantityTypeIdentifierTimeInDaylight` | Time in Daylight | `supported` | time-in-daylight | healthkit-time-in-daylight | — |
| `HKQuantityTypeIdentifierUVExposure` | UV Exposure | `supported` | uv-exposure | healthkit-uv-exposure | — |
| `HKQuantityTypeIdentifierUnderwaterDepth` | Underwater Depth | `supported` | underwater-depth | healthkit-underwater-depth | — |
| `HKQuantityTypeIdentifierVO2Max` | VO2Max | `supported` | vo2-max | grove-mobile-vo2-max; healthkit-observation | — |
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
| `HKVisionPrescriptionTypeIdentifier` | Vision Prescription | `platform-exclusive` | — | healthkit-vision-prescription | A glasses or contacts prescription is admitted as a structured R4 VisionPrescription: the lens specifications map natively, one HKVisionPrism resolves into its vertical and horizontal components, and vertex distance, the two pupillary distances, and the expiration date are represented by extensions. HealthKit supplies no prescriber, so the mandatory reference is stated absent rather than invented. |
| `HKWorkoutRouteTypeIdentifier` | Workout Route | `platform-exclusive` | — | grove-sensor-recording-document; healthkit-recording-document | The recorded route is admitted as a recording document carrying the published location-track-samples column schema. A route re-identifies readily, so a producer discloses it only under an explicit route-disclosure authorization. |
| `HKWorkoutTypeIdentifier` | Workout | `supported` | workout, workout-segment | workout: grove-mobile-workout + healthkit-observation; workout-segment: grove-mobile-workout-segment + healthkit-observation | — |

#### Derived aggregate contracts

These rows are derived mappings, not HealthKit platform source identifiers, and are excluded from the source-type count and source-type CodeSystem.

| Aggregate | Title | Input source type(s) | Contract status | Measurement | Target profile | Binding reason / requirement |
| --- | --- | --- | --- | --- | --- | --- |
| `sleep-duration-session-aggregate` | Sleep Duration Session Aggregate | `HKCategoryTypeIdentifierSleepAnalysis` | `deferred` | sleep-duration | grove-mobile-sleep-duration | This is not a HealthKit platform source identifier. The Grove FHIR contracts do not define the session-boundary aggregation contract; individual admitted samples map only to sleep stage. |
