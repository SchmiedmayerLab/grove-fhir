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

CodeSystem: HealthKitConceptPropertyCS
Id: healthkit-concept-property
Title: "HealthKit Concept Properties"
Description: "The concept properties the HealthKit source-type code system carries."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #documentation "Documentation" "Canonical Apple documentation page for this source type."

CodeSystem: HealthKitSourceTypeCS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The 218 source-type identifiers the iPhoneOS 26.5 SDK baseline (Xcode 26.6, build 17F113) hands back at runtime. A code is the identifier a producer reads from the sample, not the name of the constant that holds it. Membership is derived from, and verified against, healthkit/input/data/healthkit-inventory.json; the derived sleep-duration session aggregate is a Grove transformation contract rather than a platform source type and is excluded. A coding preserves exact source semantics and does not replace the shared or standard clinical coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* ^property[0].code = #documentation
* ^property[0].uri = "https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-concept-property#documentation"
* ^property[0].description = "Canonical Apple documentation page for this source type, recorded verbatim from Apple's published symbol index."
* ^property[0].type = #string
* #HKCategoryTypeIdentifierAbdominalCramps "Abdominal Cramps"
* #HKCategoryTypeIdentifierAbdominalCramps ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAbdominalCramps ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/abdominalcramps"
* #HKCategoryTypeIdentifierAcne "Acne"
* #HKCategoryTypeIdentifierAcne ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAcne ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/acne"
* #HKCategoryTypeIdentifierAppetiteChanges "Appetite Changes"
* #HKCategoryTypeIdentifierAppetiteChanges ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAppetiteChanges ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/appetitechanges"
* #HKCategoryTypeIdentifierAppleStandHour "Apple Stand Hour"
* #HKCategoryTypeIdentifierAppleStandHour ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAppleStandHour ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/applestandhour"
* #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent "Apple Walking Steadiness Event"
* #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/applewalkingsteadinessevent"
* #HKCategoryTypeIdentifierAudioExposureEvent "Audio Exposure Event"
* #HKCategoryTypeIdentifierAudioExposureEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAudioExposureEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/environmentalaudioexposureevent"
* #HKCategoryTypeIdentifierBladderIncontinence "Bladder Incontinence"
* #HKCategoryTypeIdentifierBladderIncontinence ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBladderIncontinence ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bladderincontinence"
* #HKCategoryTypeIdentifierBleedingAfterPregnancy "Bleeding After Pregnancy"
* #HKCategoryTypeIdentifierBleedingAfterPregnancy ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBleedingAfterPregnancy ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bleedingafterpregnancy"
* #HKCategoryTypeIdentifierBleedingDuringPregnancy "Bleeding During Pregnancy"
* #HKCategoryTypeIdentifierBleedingDuringPregnancy ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBleedingDuringPregnancy ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bleedingduringpregnancy"
* #HKCategoryTypeIdentifierBloating "Bloating"
* #HKCategoryTypeIdentifierBloating ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBloating ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bloating"
* #HKCategoryTypeIdentifierBreastPain "Breast Pain"
* #HKCategoryTypeIdentifierBreastPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBreastPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/breastpain"
* #HKCategoryTypeIdentifierCervicalMucusQuality "Cervical Mucus Quality"
* #HKCategoryTypeIdentifierCervicalMucusQuality ^property[0].code = #documentation
* #HKCategoryTypeIdentifierCervicalMucusQuality ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/cervicalmucusquality"
* #HKCategoryTypeIdentifierChestTightnessOrPain "Chest Tightness/Pain"
* #HKCategoryTypeIdentifierChestTightnessOrPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierChestTightnessOrPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/chesttightnessorpain"
* #HKCategoryTypeIdentifierChills "Chills"
* #HKCategoryTypeIdentifierChills ^property[0].code = #documentation
* #HKCategoryTypeIdentifierChills ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/chills"
* #HKCategoryTypeIdentifierConstipation "Constipation"
* #HKCategoryTypeIdentifierConstipation ^property[0].code = #documentation
* #HKCategoryTypeIdentifierConstipation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/constipation"
* #HKCategoryTypeIdentifierContraceptive "Contraceptive"
* #HKCategoryTypeIdentifierContraceptive ^property[0].code = #documentation
* #HKCategoryTypeIdentifierContraceptive ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/contraceptive"
* #HKCategoryTypeIdentifierCoughing "Coughing"
* #HKCategoryTypeIdentifierCoughing ^property[0].code = #documentation
* #HKCategoryTypeIdentifierCoughing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/coughing"
* #HKCategoryTypeIdentifierDiarrhea "Diarrhea"
* #HKCategoryTypeIdentifierDiarrhea ^property[0].code = #documentation
* #HKCategoryTypeIdentifierDiarrhea ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/diarrhea"
* #HKCategoryTypeIdentifierDizziness "Dizziness"
* #HKCategoryTypeIdentifierDizziness ^property[0].code = #documentation
* #HKCategoryTypeIdentifierDizziness ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/dizziness"
* #HKCategoryTypeIdentifierDrySkin "Dry Skin"
* #HKCategoryTypeIdentifierDrySkin ^property[0].code = #documentation
* #HKCategoryTypeIdentifierDrySkin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/dryskin"
* #HKCategoryTypeIdentifierFainting "Fainting"
* #HKCategoryTypeIdentifierFainting ^property[0].code = #documentation
* #HKCategoryTypeIdentifierFainting ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/fainting"
* #HKCategoryTypeIdentifierFatigue "Fatigue"
* #HKCategoryTypeIdentifierFatigue ^property[0].code = #documentation
* #HKCategoryTypeIdentifierFatigue ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/fatigue"
* #HKCategoryTypeIdentifierFever "Fever"
* #HKCategoryTypeIdentifierFever ^property[0].code = #documentation
* #HKCategoryTypeIdentifierFever ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/fever"
* #HKCategoryTypeIdentifierGeneralizedBodyAche "Generalized Body Ache"
* #HKCategoryTypeIdentifierGeneralizedBodyAche ^property[0].code = #documentation
* #HKCategoryTypeIdentifierGeneralizedBodyAche ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/generalizedbodyache"
* #HKCategoryTypeIdentifierHairLoss "Hair Loss"
* #HKCategoryTypeIdentifierHairLoss ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHairLoss ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/hairloss"
* #HKCategoryTypeIdentifierHandwashingEvent "Handwashing Event"
* #HKCategoryTypeIdentifierHandwashingEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHandwashingEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/handwashingevent"
* #HKCategoryTypeIdentifierHeadache "Headache"
* #HKCategoryTypeIdentifierHeadache ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHeadache ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/headache"
* #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent "Headphone Audio Exposure Event"
* #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/headphoneaudioexposureevent"
* #HKCategoryTypeIdentifierHeartburn "Heartburn"
* #HKCategoryTypeIdentifierHeartburn ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHeartburn ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/heartburn"
* #HKCategoryTypeIdentifierHighHeartRateEvent "High Heart Rate Event"
* #HKCategoryTypeIdentifierHighHeartRateEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHighHeartRateEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/highheartrateevent"
* #HKCategoryTypeIdentifierHotFlashes "Hot Flashes"
* #HKCategoryTypeIdentifierHotFlashes ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHotFlashes ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/hotflashes"
* #HKCategoryTypeIdentifierHypertensionEvent "Hypertension Event"
* #HKCategoryTypeIdentifierHypertensionEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHypertensionEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/hypertensionevent"
* #HKCategoryTypeIdentifierInfrequentMenstrualCycles "Infrequent Menstrual Cycles"
* #HKCategoryTypeIdentifierInfrequentMenstrualCycles ^property[0].code = #documentation
* #HKCategoryTypeIdentifierInfrequentMenstrualCycles ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/infrequentmenstrualcycles"
* #HKCategoryTypeIdentifierIntermenstrualBleeding "Intermenstrual Bleeding"
* #HKCategoryTypeIdentifierIntermenstrualBleeding ^property[0].code = #documentation
* #HKCategoryTypeIdentifierIntermenstrualBleeding ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/intermenstrualbleeding"
* #HKCategoryTypeIdentifierIrregularHeartRhythmEvent "Irregular Heart Rhythm Event"
* #HKCategoryTypeIdentifierIrregularHeartRhythmEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierIrregularHeartRhythmEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/irregularheartrhythmevent"
* #HKCategoryTypeIdentifierIrregularMenstrualCycles "Irregular Menstrual Cycles"
* #HKCategoryTypeIdentifierIrregularMenstrualCycles ^property[0].code = #documentation
* #HKCategoryTypeIdentifierIrregularMenstrualCycles ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/irregularmenstrualcycles"
* #HKCategoryTypeIdentifierLactation "Lactation"
* #HKCategoryTypeIdentifierLactation ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLactation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lactation"
* #HKCategoryTypeIdentifierLossOfSmell "Loss of Smell"
* #HKCategoryTypeIdentifierLossOfSmell ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLossOfSmell ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lossofsmell"
* #HKCategoryTypeIdentifierLossOfTaste "Loss of Taste"
* #HKCategoryTypeIdentifierLossOfTaste ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLossOfTaste ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lossoftaste"
* #HKCategoryTypeIdentifierLowCardioFitnessEvent "Low Cardio Fitness Event"
* #HKCategoryTypeIdentifierLowCardioFitnessEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLowCardioFitnessEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lowcardiofitnessevent"
* #HKCategoryTypeIdentifierLowHeartRateEvent "Low Heart Rate Event"
* #HKCategoryTypeIdentifierLowHeartRateEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLowHeartRateEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lowheartrateevent"
* #HKCategoryTypeIdentifierLowerBackPain "Lower Back Pain"
* #HKCategoryTypeIdentifierLowerBackPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLowerBackPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lowerbackpain"
* #HKCategoryTypeIdentifierMemoryLapse "Memory Lapse"
* #HKCategoryTypeIdentifierMemoryLapse ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMemoryLapse ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/memorylapse"
* #HKCategoryTypeIdentifierMenstrualFlow "Menstrual Flow"
* #HKCategoryTypeIdentifierMenstrualFlow ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMenstrualFlow ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/menstrualflow"
* #HKCategoryTypeIdentifierMindfulSession "Mindful Session"
* #HKCategoryTypeIdentifierMindfulSession ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMindfulSession ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/mindfulsession"
* #HKCategoryTypeIdentifierMoodChanges "Mood Changes"
* #HKCategoryTypeIdentifierMoodChanges ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMoodChanges ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/moodchanges"
* #HKCategoryTypeIdentifierNausea "Nausea"
* #HKCategoryTypeIdentifierNausea ^property[0].code = #documentation
* #HKCategoryTypeIdentifierNausea ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/nausea"
* #HKCategoryTypeIdentifierNightSweats "Night Sweats"
* #HKCategoryTypeIdentifierNightSweats ^property[0].code = #documentation
* #HKCategoryTypeIdentifierNightSweats ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/nightsweats"
* #HKCategoryTypeIdentifierOvulationTestResult "Ovulation Test Result"
* #HKCategoryTypeIdentifierOvulationTestResult ^property[0].code = #documentation
* #HKCategoryTypeIdentifierOvulationTestResult ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/ovulationtestresult"
* #HKCategoryTypeIdentifierPelvicPain "Pelvic Pain"
* #HKCategoryTypeIdentifierPelvicPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPelvicPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/pelvicpain"
* #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding "Persistent Intermenstrual Bleeding"
* #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/persistentintermenstrualbleeding"
* #HKCategoryTypeIdentifierPregnancy "Pregnancy"
* #HKCategoryTypeIdentifierPregnancy ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPregnancy ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/pregnancy"
* #HKCategoryTypeIdentifierPregnancyTestResult "Pregnancy Test Result"
* #HKCategoryTypeIdentifierPregnancyTestResult ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPregnancyTestResult ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/pregnancytestresult"
* #HKCategoryTypeIdentifierProgesteroneTestResult "Progesterone Test Result"
* #HKCategoryTypeIdentifierProgesteroneTestResult ^property[0].code = #documentation
* #HKCategoryTypeIdentifierProgesteroneTestResult ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/progesteronetestresult"
* #HKCategoryTypeIdentifierProlongedMenstrualPeriods "Prolonged Menstrual Periods"
* #HKCategoryTypeIdentifierProlongedMenstrualPeriods ^property[0].code = #documentation
* #HKCategoryTypeIdentifierProlongedMenstrualPeriods ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/prolongedmenstrualperiods"
* #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat "Rapid/Pounding/Fluttering Heartbeat"
* #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat ^property[0].code = #documentation
* #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/rapidpoundingorflutteringheartbeat"
* #HKCategoryTypeIdentifierRunnyNose "Runny Nose"
* #HKCategoryTypeIdentifierRunnyNose ^property[0].code = #documentation
* #HKCategoryTypeIdentifierRunnyNose ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/runnynose"
* #HKCategoryTypeIdentifierSexualActivity "Sexual Activity"
* #HKCategoryTypeIdentifierSexualActivity ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSexualActivity ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sexualactivity"
* #HKCategoryTypeIdentifierShortnessOfBreath "Shortness of Breath"
* #HKCategoryTypeIdentifierShortnessOfBreath ^property[0].code = #documentation
* #HKCategoryTypeIdentifierShortnessOfBreath ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/shortnessofbreath"
* #HKCategoryTypeIdentifierSinusCongestion "Sinus Congestion"
* #HKCategoryTypeIdentifierSinusCongestion ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSinusCongestion ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sinuscongestion"
* #HKCategoryTypeIdentifierSkippedHeartbeat "Skipped Heartbeat"
* #HKCategoryTypeIdentifierSkippedHeartbeat ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSkippedHeartbeat ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/skippedheartbeat"
* #HKCategoryTypeIdentifierSleepAnalysis "Sleep Analysis"
* #HKCategoryTypeIdentifierSleepAnalysis ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSleepAnalysis ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sleepanalysis"
* #HKCategoryTypeIdentifierSleepApneaEvent "Sleep Apnea Event"
* #HKCategoryTypeIdentifierSleepApneaEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSleepApneaEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sleepapneaevent"
* #HKCategoryTypeIdentifierSleepChanges "Sleep Changes"
* #HKCategoryTypeIdentifierSleepChanges ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSleepChanges ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sleepchanges"
* #HKCategoryTypeIdentifierSoreThroat "Sore Throat"
* #HKCategoryTypeIdentifierSoreThroat ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSoreThroat ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sorethroat"
* #HKCategoryTypeIdentifierToothbrushingEvent "Toothbrushing Event"
* #HKCategoryTypeIdentifierToothbrushingEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierToothbrushingEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/toothbrushingevent"
* #HKCategoryTypeIdentifierVaginalDryness "Vaginal Dryness"
* #HKCategoryTypeIdentifierVaginalDryness ^property[0].code = #documentation
* #HKCategoryTypeIdentifierVaginalDryness ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/vaginaldryness"
* #HKCategoryTypeIdentifierVomiting "Vomiting"
* #HKCategoryTypeIdentifierVomiting ^property[0].code = #documentation
* #HKCategoryTypeIdentifierVomiting ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/vomiting"
* #HKCategoryTypeIdentifierWheezing "Wheezing"
* #HKCategoryTypeIdentifierWheezing ^property[0].code = #documentation
* #HKCategoryTypeIdentifierWheezing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/wheezing"
* #HKCharacteristicTypeIdentifierActivityMoveMode "Activity Move Mode"
* #HKCharacteristicTypeIdentifierActivityMoveMode ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierActivityMoveMode ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/activitymovemode"
* #HKCharacteristicTypeIdentifierBiologicalSex "Biological Sex"
* #HKCharacteristicTypeIdentifierBiologicalSex ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierBiologicalSex ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/biologicalsex"
* #HKCharacteristicTypeIdentifierBloodType "Blood Type"
* #HKCharacteristicTypeIdentifierBloodType ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierBloodType ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/bloodtype"
* #HKCharacteristicTypeIdentifierDateOfBirth "Date of Birth"
* #HKCharacteristicTypeIdentifierDateOfBirth ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierDateOfBirth ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/dateofbirth"
* #HKCharacteristicTypeIdentifierFitzpatrickSkinType "Fitzpatrick Skin Type"
* #HKCharacteristicTypeIdentifierFitzpatrickSkinType ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierFitzpatrickSkinType ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/fitzpatrickskintype"
* #HKCharacteristicTypeIdentifierWheelchairUse "Wheelchair Use"
* #HKCharacteristicTypeIdentifierWheelchairUse ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierWheelchairUse ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/wheelchairuse"
* #HKClinicalTypeIdentifierAllergyRecord "Allergy Record"
* #HKClinicalTypeIdentifierAllergyRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierAllergyRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/allergyrecord"
* #HKClinicalTypeIdentifierClinicalNoteRecord "Clinical Note Record"
* #HKClinicalTypeIdentifierClinicalNoteRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierClinicalNoteRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/clinicalnoterecord"
* #HKClinicalTypeIdentifierConditionRecord "Condition Record"
* #HKClinicalTypeIdentifierConditionRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierConditionRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/conditionrecord"
* #HKClinicalTypeIdentifierCoverageRecord "Coverage Record"
* #HKClinicalTypeIdentifierCoverageRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierCoverageRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/coveragerecord"
* #HKClinicalTypeIdentifierImmunizationRecord "Immunization Record"
* #HKClinicalTypeIdentifierImmunizationRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierImmunizationRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/immunizationrecord"
* #HKClinicalTypeIdentifierLabResultRecord "Lab Result Record"
* #HKClinicalTypeIdentifierLabResultRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierLabResultRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/labresultrecord"
* #HKClinicalTypeIdentifierMedicationRecord "Medication Record"
* #HKClinicalTypeIdentifierMedicationRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierMedicationRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/medicationrecord"
* #HKClinicalTypeIdentifierProcedureRecord "Procedure Record"
* #HKClinicalTypeIdentifierProcedureRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierProcedureRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/procedurerecord"
* #HKClinicalTypeIdentifierVitalSignRecord "Vital Sign Record"
* #HKClinicalTypeIdentifierVitalSignRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierVitalSignRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/vitalsignrecord"
* #HKCorrelationTypeIdentifierBloodPressure "Blood Pressure"
* #HKCorrelationTypeIdentifierBloodPressure ^property[0].code = #documentation
* #HKCorrelationTypeIdentifierBloodPressure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcorrelationtypeidentifier/bloodpressure"
* #HKCorrelationTypeIdentifierFood "Food"
* #HKCorrelationTypeIdentifierFood ^property[0].code = #documentation
* #HKCorrelationTypeIdentifierFood ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcorrelationtypeidentifier/food"
* #HKDataTypeIdentifierAudiogram "Audiogram"
* #HKDataTypeIdentifierAudiogram ^property[0].code = #documentation
* #HKDataTypeIdentifierAudiogram ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkaudiogramsampletype"
* #HKDataTypeIdentifierElectrocardiogram "ECG"
* #HKDataTypeIdentifierElectrocardiogram ^property[0].code = #documentation
* #HKDataTypeIdentifierElectrocardiogram ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkelectrocardiogramtype"
* #HKDataTypeIdentifierHeartbeatSeries "Heartbeat Series"
* #HKDataTypeIdentifierHeartbeatSeries ^property[0].code = #documentation
* #HKDataTypeIdentifierHeartbeatSeries ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdatatypeidentifierheartbeatseries"
* #HKDataTypeStateOfMind "State of Mind"
* #HKDataTypeStateOfMind ^property[0].code = #documentation
* #HKDataTypeStateOfMind ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdatatypeidentifierstateofmind"
* #HKDataTypeUserAnnotatedMedicationConcept "User Annotated Medication Concept"
* #HKDataTypeUserAnnotatedMedicationConcept ^property[0].code = #documentation
* #HKDataTypeUserAnnotatedMedicationConcept ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdatatypeidentifieruserannotatedmedicationconcept"
* #HKDocumentTypeIdentifierCDA "CDA Document"
* #HKDocumentTypeIdentifierCDA ^property[0].code = #documentation
* #HKDocumentTypeIdentifierCDA ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdocumenttypeidentifier/cda"
* #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent "Medication Dose Event"
* #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent ^property[0].code = #documentation
* #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkmedicationdoseeventtypeidentifiermedicationdoseevent"
* #HKQuantityTypeIdentifierActiveEnergyBurned "Active Energy Burned"
* #HKQuantityTypeIdentifierActiveEnergyBurned ^property[0].code = #documentation
* #HKQuantityTypeIdentifierActiveEnergyBurned ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/activeenergyburned"
* #HKQuantityTypeIdentifierAppleExerciseTime "Apple Exercise Time"
* #HKQuantityTypeIdentifierAppleExerciseTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleExerciseTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/appleexercisetime"
* #HKQuantityTypeIdentifierAppleMoveTime "Apple Move Time"
* #HKQuantityTypeIdentifierAppleMoveTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleMoveTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applemovetime"
* #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances "Apple Sleeping Breathing Disturbances"
* #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applesleepingbreathingdisturbances"
* #HKQuantityTypeIdentifierAppleSleepingWristTemperature "Apple Sleeping Wrist Temperature"
* #HKQuantityTypeIdentifierAppleSleepingWristTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleSleepingWristTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applesleepingwristtemperature"
* #HKQuantityTypeIdentifierAppleStandTime "Apple Stand Time"
* #HKQuantityTypeIdentifierAppleStandTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleStandTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applestandtime"
* #HKQuantityTypeIdentifierAppleWalkingSteadiness "Apple Walking Steadiness"
* #HKQuantityTypeIdentifierAppleWalkingSteadiness ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleWalkingSteadiness ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applewalkingsteadiness"
* #HKQuantityTypeIdentifierAtrialFibrillationBurden "AFib Burden"
* #HKQuantityTypeIdentifierAtrialFibrillationBurden ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAtrialFibrillationBurden ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/atrialfibrillationburden"
* #HKQuantityTypeIdentifierBasalBodyTemperature "Basal Body Temperature"
* #HKQuantityTypeIdentifierBasalBodyTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBasalBodyTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/basalbodytemperature"
* #HKQuantityTypeIdentifierBasalEnergyBurned "Basal Energy Burned"
* #HKQuantityTypeIdentifierBasalEnergyBurned ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBasalEnergyBurned ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/basalenergyburned"
* #HKQuantityTypeIdentifierBloodAlcoholContent "Blood Alcohol Content"
* #HKQuantityTypeIdentifierBloodAlcoholContent ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodAlcoholContent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodalcoholcontent"
* #HKQuantityTypeIdentifierBloodGlucose "Blood Glucose"
* #HKQuantityTypeIdentifierBloodGlucose ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodGlucose ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodglucose"
* #HKQuantityTypeIdentifierBloodPressureDiastolic "Blood Pressure (Diastolic)"
* #HKQuantityTypeIdentifierBloodPressureDiastolic ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodPressureDiastolic ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodpressurediastolic"
* #HKQuantityTypeIdentifierBloodPressureSystolic "Blood Pressure (Systolic)"
* #HKQuantityTypeIdentifierBloodPressureSystolic ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodPressureSystolic ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodpressuresystolic"
* #HKQuantityTypeIdentifierBodyFatPercentage "Body Fat Percentage"
* #HKQuantityTypeIdentifierBodyFatPercentage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyFatPercentage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodyfatpercentage"
* #HKQuantityTypeIdentifierBodyMass "Body Mass"
* #HKQuantityTypeIdentifierBodyMass ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyMass ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodymass"
* #HKQuantityTypeIdentifierBodyMassIndex "BMI"
* #HKQuantityTypeIdentifierBodyMassIndex ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyMassIndex ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodymassindex"
* #HKQuantityTypeIdentifierBodyTemperature "Body Temperature"
* #HKQuantityTypeIdentifierBodyTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodytemperature"
* #HKQuantityTypeIdentifierCrossCountrySkiingSpeed "Cross Country Skiing Speed"
* #HKQuantityTypeIdentifierCrossCountrySkiingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCrossCountrySkiingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/crosscountryskiingspeed"
* #HKQuantityTypeIdentifierCyclingCadence "Cycling Cadence"
* #HKQuantityTypeIdentifierCyclingCadence ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingCadence ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingcadence"
* #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower "Cycling Functional Threshold Power"
* #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingfunctionalthresholdpower"
* #HKQuantityTypeIdentifierCyclingPower "Cycling Power"
* #HKQuantityTypeIdentifierCyclingPower ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingPower ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingpower"
* #HKQuantityTypeIdentifierCyclingSpeed "Cycling Speed"
* #HKQuantityTypeIdentifierCyclingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingspeed"
* #HKQuantityTypeIdentifierDietaryBiotin "Dietary Biotin Intake"
* #HKQuantityTypeIdentifierDietaryBiotin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryBiotin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarybiotin"
* #HKQuantityTypeIdentifierDietaryCaffeine "Dietary Caffeine Intake"
* #HKQuantityTypeIdentifierDietaryCaffeine ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCaffeine ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycaffeine"
* #HKQuantityTypeIdentifierDietaryCalcium "Dietary Calcium Intake"
* #HKQuantityTypeIdentifierDietaryCalcium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCalcium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycalcium"
* #HKQuantityTypeIdentifierDietaryCarbohydrates "Dietary Carbohydrates Intake"
* #HKQuantityTypeIdentifierDietaryCarbohydrates ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCarbohydrates ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycarbohydrates"
* #HKQuantityTypeIdentifierDietaryChloride "Dietary Chloride Intake"
* #HKQuantityTypeIdentifierDietaryChloride ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryChloride ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarychloride"
* #HKQuantityTypeIdentifierDietaryCholesterol "Dietary Cholesterol Intake"
* #HKQuantityTypeIdentifierDietaryCholesterol ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCholesterol ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycholesterol"
* #HKQuantityTypeIdentifierDietaryChromium "Dietary Chromium Intake"
* #HKQuantityTypeIdentifierDietaryChromium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryChromium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarychromium"
* #HKQuantityTypeIdentifierDietaryCopper "Dietary Copper Intake"
* #HKQuantityTypeIdentifierDietaryCopper ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCopper ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycopper"
* #HKQuantityTypeIdentifierDietaryEnergyConsumed "Dietary Energy Consumed"
* #HKQuantityTypeIdentifierDietaryEnergyConsumed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryEnergyConsumed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryenergyconsumed"
* #HKQuantityTypeIdentifierDietaryFatMonounsaturated "Dietary Monounsaturated Fat Intake"
* #HKQuantityTypeIdentifierDietaryFatMonounsaturated ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatMonounsaturated ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfatmonounsaturated"
* #HKQuantityTypeIdentifierDietaryFatPolyunsaturated "Dietary Polyunsaturated Fat Intake"
* #HKQuantityTypeIdentifierDietaryFatPolyunsaturated ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatPolyunsaturated ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfatpolyunsaturated"
* #HKQuantityTypeIdentifierDietaryFatSaturated "Dietary Saturated Fat Intake"
* #HKQuantityTypeIdentifierDietaryFatSaturated ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatSaturated ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfatsaturated"
* #HKQuantityTypeIdentifierDietaryFatTotal "Dietary Total Fat Intake"
* #HKQuantityTypeIdentifierDietaryFatTotal ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatTotal ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfattotal"
* #HKQuantityTypeIdentifierDietaryFiber "Dietary Fiber Intake"
* #HKQuantityTypeIdentifierDietaryFiber ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFiber ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfiber"
* #HKQuantityTypeIdentifierDietaryFolate "Dietary Folate Intake"
* #HKQuantityTypeIdentifierDietaryFolate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFolate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfolate"
* #HKQuantityTypeIdentifierDietaryIodine "Dietary Iodine Intake"
* #HKQuantityTypeIdentifierDietaryIodine ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryIodine ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryiodine"
* #HKQuantityTypeIdentifierDietaryIron "Dietary Iron Intake"
* #HKQuantityTypeIdentifierDietaryIron ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryIron ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryiron"
* #HKQuantityTypeIdentifierDietaryMagnesium "Dietary Magnesium Intake"
* #HKQuantityTypeIdentifierDietaryMagnesium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryMagnesium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarymagnesium"
* #HKQuantityTypeIdentifierDietaryManganese "Dietary Manganese Intake"
* #HKQuantityTypeIdentifierDietaryManganese ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryManganese ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarymanganese"
* #HKQuantityTypeIdentifierDietaryMolybdenum "Dietary Molybdenum Intake"
* #HKQuantityTypeIdentifierDietaryMolybdenum ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryMolybdenum ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarymolybdenum"
* #HKQuantityTypeIdentifierDietaryNiacin "Dietary Niacin Intake"
* #HKQuantityTypeIdentifierDietaryNiacin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryNiacin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryniacin"
* #HKQuantityTypeIdentifierDietaryPantothenicAcid "Dietary Pantothenic Acid Intake"
* #HKQuantityTypeIdentifierDietaryPantothenicAcid ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryPantothenicAcid ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarypantothenicacid"
* #HKQuantityTypeIdentifierDietaryPhosphorus "Dietary Phosphorus Intake"
* #HKQuantityTypeIdentifierDietaryPhosphorus ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryPhosphorus ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryphosphorus"
* #HKQuantityTypeIdentifierDietaryPotassium "Dietary Potassium Intake"
* #HKQuantityTypeIdentifierDietaryPotassium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryPotassium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarypotassium"
* #HKQuantityTypeIdentifierDietaryProtein "Dietary Protein Intake"
* #HKQuantityTypeIdentifierDietaryProtein ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryProtein ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryprotein"
* #HKQuantityTypeIdentifierDietaryRiboflavin "Dietary Riboflavin Intake"
* #HKQuantityTypeIdentifierDietaryRiboflavin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryRiboflavin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryriboflavin"
* #HKQuantityTypeIdentifierDietarySelenium "Dietary Selenium Intake"
* #HKQuantityTypeIdentifierDietarySelenium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietarySelenium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryselenium"
* #HKQuantityTypeIdentifierDietarySodium "Dietary Sodium Intake"
* #HKQuantityTypeIdentifierDietarySodium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietarySodium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarysodium"
* #HKQuantityTypeIdentifierDietarySugar "Dietary Sugar Intake"
* #HKQuantityTypeIdentifierDietarySugar ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietarySugar ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarysugar"
* #HKQuantityTypeIdentifierDietaryThiamin "Dietary Thiamin Intake"
* #HKQuantityTypeIdentifierDietaryThiamin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryThiamin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarythiamin"
* #HKQuantityTypeIdentifierDietaryVitaminA "Dietary Vitamin A Intake"
* #HKQuantityTypeIdentifierDietaryVitaminA ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminA ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamina"
* #HKQuantityTypeIdentifierDietaryVitaminB12 "Dietary Vitamin B12 Intake"
* #HKQuantityTypeIdentifierDietaryVitaminB12 ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminB12 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitaminb12"
* #HKQuantityTypeIdentifierDietaryVitaminB6 "Dietary Vitamin B6 Intake"
* #HKQuantityTypeIdentifierDietaryVitaminB6 ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminB6 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitaminb6"
* #HKQuantityTypeIdentifierDietaryVitaminC "Dietary Vitamin C Intake"
* #HKQuantityTypeIdentifierDietaryVitaminC ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminC ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitaminc"
* #HKQuantityTypeIdentifierDietaryVitaminD "Dietary Vitamin D Intake"
* #HKQuantityTypeIdentifierDietaryVitaminD ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminD ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamind"
* #HKQuantityTypeIdentifierDietaryVitaminE "Dietary Vitamin E Intake"
* #HKQuantityTypeIdentifierDietaryVitaminE ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminE ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamine"
* #HKQuantityTypeIdentifierDietaryVitaminK "Dietary Vitamin K Intake"
* #HKQuantityTypeIdentifierDietaryVitaminK ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminK ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamink"
* #HKQuantityTypeIdentifierDietaryWater "Dietary Water Intake"
* #HKQuantityTypeIdentifierDietaryWater ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryWater ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarywater"
* #HKQuantityTypeIdentifierDietaryZinc "Dietary Zinc Intake"
* #HKQuantityTypeIdentifierDietaryZinc ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryZinc ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryzinc"
* #HKQuantityTypeIdentifierDistanceCrossCountrySkiing "Cross-Country Skiing Distance"
* #HKQuantityTypeIdentifierDistanceCrossCountrySkiing ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceCrossCountrySkiing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancecrosscountryskiing"
* #HKQuantityTypeIdentifierDistanceCycling "Cycling Distance"
* #HKQuantityTypeIdentifierDistanceCycling ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceCycling ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancecycling"
* #HKQuantityTypeIdentifierDistanceDownhillSnowSports "Downhill Snow Sports Distance"
* #HKQuantityTypeIdentifierDistanceDownhillSnowSports ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceDownhillSnowSports ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancedownhillsnowsports"
* #HKQuantityTypeIdentifierDistancePaddleSports "Paddle Sports Distance"
* #HKQuantityTypeIdentifierDistancePaddleSports ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistancePaddleSports ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancepaddlesports"
* #HKQuantityTypeIdentifierDistanceRowing "Rowing Distance"
* #HKQuantityTypeIdentifierDistanceRowing ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceRowing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancerowing"
* #HKQuantityTypeIdentifierDistanceSkatingSports "Skating Sports Distance"
* #HKQuantityTypeIdentifierDistanceSkatingSports ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceSkatingSports ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distanceskatingsports"
* #HKQuantityTypeIdentifierDistanceSwimming "Swimming Distance"
* #HKQuantityTypeIdentifierDistanceSwimming ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceSwimming ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distanceswimming"
* #HKQuantityTypeIdentifierDistanceWalkingRunning "Distance Walking/Running"
* #HKQuantityTypeIdentifierDistanceWalkingRunning ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceWalkingRunning ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancewalkingrunning"
* #HKQuantityTypeIdentifierDistanceWheelchair "Wheelchair Distance"
* #HKQuantityTypeIdentifierDistanceWheelchair ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceWheelchair ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancewheelchair"
* #HKQuantityTypeIdentifierElectrodermalActivity "Electrodermal Activity"
* #HKQuantityTypeIdentifierElectrodermalActivity ^property[0].code = #documentation
* #HKQuantityTypeIdentifierElectrodermalActivity ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/electrodermalactivity"
* #HKQuantityTypeIdentifierEnvironmentalAudioExposure "Environmental Audio Exposure"
* #HKQuantityTypeIdentifierEnvironmentalAudioExposure ^property[0].code = #documentation
* #HKQuantityTypeIdentifierEnvironmentalAudioExposure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/environmentalaudioexposure"
* #HKQuantityTypeIdentifierEnvironmentalSoundReduction "Environmental Sound Reduction"
* #HKQuantityTypeIdentifierEnvironmentalSoundReduction ^property[0].code = #documentation
* #HKQuantityTypeIdentifierEnvironmentalSoundReduction ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/environmentalsoundreduction"
* #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore "Estimated Workout Effort"
* #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore ^property[0].code = #documentation
* #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/estimatedworkouteffortscore"
* #HKQuantityTypeIdentifierFlightsClimbed "Flights Climbed"
* #HKQuantityTypeIdentifierFlightsClimbed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierFlightsClimbed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/flightsclimbed"
* #HKQuantityTypeIdentifierForcedExpiratoryVolume1 "Forced Expiratory Volume (1 sec)"
* #HKQuantityTypeIdentifierForcedExpiratoryVolume1 ^property[0].code = #documentation
* #HKQuantityTypeIdentifierForcedExpiratoryVolume1 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/forcedexpiratoryvolume1"
* #HKQuantityTypeIdentifierForcedVitalCapacity "Forced Vital Capacity"
* #HKQuantityTypeIdentifierForcedVitalCapacity ^property[0].code = #documentation
* #HKQuantityTypeIdentifierForcedVitalCapacity ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/forcedvitalcapacity"
* #HKQuantityTypeIdentifierHeadphoneAudioExposure "Headphone Audio Exposure"
* #HKQuantityTypeIdentifierHeadphoneAudioExposure ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeadphoneAudioExposure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/headphoneaudioexposure"
* #HKQuantityTypeIdentifierHeartRate "Heart Rate"
* #HKQuantityTypeIdentifierHeartRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeartRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/heartrate"
* #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute "Heart Rate Recovery (1 min)"
* #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/heartraterecoveryoneminute"
* #HKQuantityTypeIdentifierHeartRateVariabilitySDNN "Heart Rate Variability SDNN"
* #HKQuantityTypeIdentifierHeartRateVariabilitySDNN ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeartRateVariabilitySDNN ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/heartratevariabilitysdnn"
* #HKQuantityTypeIdentifierHeight "Height"
* #HKQuantityTypeIdentifierHeight ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeight ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/height"
* #HKQuantityTypeIdentifierInhalerUsage "Inhaler Usage"
* #HKQuantityTypeIdentifierInhalerUsage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierInhalerUsage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/inhalerusage"
* #HKQuantityTypeIdentifierInsulinDelivery "Insulin Delivery"
* #HKQuantityTypeIdentifierInsulinDelivery ^property[0].code = #documentation
* #HKQuantityTypeIdentifierInsulinDelivery ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/insulindelivery"
* #HKQuantityTypeIdentifierLeanBodyMass "Lean Body Mass"
* #HKQuantityTypeIdentifierLeanBodyMass ^property[0].code = #documentation
* #HKQuantityTypeIdentifierLeanBodyMass ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/leanbodymass"
* #HKQuantityTypeIdentifierNikeFuel "NikeFuel"
* #HKQuantityTypeIdentifierNikeFuel ^property[0].code = #documentation
* #HKQuantityTypeIdentifierNikeFuel ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/nikefuel"
* #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages "Number of Alcoholic Beverages"
* #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages ^property[0].code = #documentation
* #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/numberofalcoholicbeverages"
* #HKQuantityTypeIdentifierNumberOfTimesFallen "Number of Times Fallen"
* #HKQuantityTypeIdentifierNumberOfTimesFallen ^property[0].code = #documentation
* #HKQuantityTypeIdentifierNumberOfTimesFallen ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/numberoftimesfallen"
* #HKQuantityTypeIdentifierOxygenSaturation "Oxygen Saturation"
* #HKQuantityTypeIdentifierOxygenSaturation ^property[0].code = #documentation
* #HKQuantityTypeIdentifierOxygenSaturation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/oxygensaturation"
* #HKQuantityTypeIdentifierPaddleSportsSpeed "Paddle Sports Speed"
* #HKQuantityTypeIdentifierPaddleSportsSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPaddleSportsSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/paddlesportsspeed"
* #HKQuantityTypeIdentifierPeakExpiratoryFlowRate "Peak Expiratory Flow Rate"
* #HKQuantityTypeIdentifierPeakExpiratoryFlowRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPeakExpiratoryFlowRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/peakexpiratoryflowrate"
* #HKQuantityTypeIdentifierPeripheralPerfusionIndex "Peripheral Perfusion Index"
* #HKQuantityTypeIdentifierPeripheralPerfusionIndex ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPeripheralPerfusionIndex ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/peripheralperfusionindex"
* #HKQuantityTypeIdentifierPhysicalEffort "Physical Effort"
* #HKQuantityTypeIdentifierPhysicalEffort ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPhysicalEffort ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/physicaleffort"
* #HKQuantityTypeIdentifierPushCount "Wheelchair Push Count"
* #HKQuantityTypeIdentifierPushCount ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPushCount ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/pushcount"
* #HKQuantityTypeIdentifierRespiratoryRate "Respiratory Rate"
* #HKQuantityTypeIdentifierRespiratoryRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRespiratoryRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/respiratoryrate"
* #HKQuantityTypeIdentifierRestingHeartRate "Resting Heart Rate"
* #HKQuantityTypeIdentifierRestingHeartRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRestingHeartRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/restingheartrate"
* #HKQuantityTypeIdentifierRowingSpeed "Rowing Speed"
* #HKQuantityTypeIdentifierRowingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRowingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/rowingspeed"
* #HKQuantityTypeIdentifierRunningGroundContactTime "Ground Contact Time"
* #HKQuantityTypeIdentifierRunningGroundContactTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningGroundContactTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runninggroundcontacttime"
* #HKQuantityTypeIdentifierRunningPower "Running Power"
* #HKQuantityTypeIdentifierRunningPower ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningPower ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningpower"
* #HKQuantityTypeIdentifierRunningSpeed "Running Speed"
* #HKQuantityTypeIdentifierRunningSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningspeed"
* #HKQuantityTypeIdentifierRunningStrideLength "Running Stride Length"
* #HKQuantityTypeIdentifierRunningStrideLength ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningStrideLength ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningstridelength"
* #HKQuantityTypeIdentifierRunningVerticalOscillation "Running Vertical Oscillation"
* #HKQuantityTypeIdentifierRunningVerticalOscillation ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningVerticalOscillation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningverticaloscillation"
* #HKQuantityTypeIdentifierSixMinuteWalkTestDistance "6 Minute Walk Test Distance"
* #HKQuantityTypeIdentifierSixMinuteWalkTestDistance ^property[0].code = #documentation
* #HKQuantityTypeIdentifierSixMinuteWalkTestDistance ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/sixminutewalktestdistance"
* #HKQuantityTypeIdentifierStairAscentSpeed "Stair Ascent Speed"
* #HKQuantityTypeIdentifierStairAscentSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierStairAscentSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/stairascentspeed"
* #HKQuantityTypeIdentifierStairDescentSpeed "Stair Descent Speed"
* #HKQuantityTypeIdentifierStairDescentSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierStairDescentSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/stairdescentspeed"
* #HKQuantityTypeIdentifierStepCount "Step Count"
* #HKQuantityTypeIdentifierStepCount ^property[0].code = #documentation
* #HKQuantityTypeIdentifierStepCount ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/stepcount"
* #HKQuantityTypeIdentifierSwimmingStrokeCount "Swimming Stroke Count"
* #HKQuantityTypeIdentifierSwimmingStrokeCount ^property[0].code = #documentation
* #HKQuantityTypeIdentifierSwimmingStrokeCount ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/swimmingstrokecount"
* #HKQuantityTypeIdentifierTimeInDaylight "Time in Daylight"
* #HKQuantityTypeIdentifierTimeInDaylight ^property[0].code = #documentation
* #HKQuantityTypeIdentifierTimeInDaylight ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/timeindaylight"
* #HKQuantityTypeIdentifierUVExposure "UV Exposure"
* #HKQuantityTypeIdentifierUVExposure ^property[0].code = #documentation
* #HKQuantityTypeIdentifierUVExposure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/uvexposure"
* #HKQuantityTypeIdentifierUnderwaterDepth "Underwater Depth"
* #HKQuantityTypeIdentifierUnderwaterDepth ^property[0].code = #documentation
* #HKQuantityTypeIdentifierUnderwaterDepth ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/underwaterdepth"
* #HKQuantityTypeIdentifierVO2Max "VO2Max"
* #HKQuantityTypeIdentifierVO2Max ^property[0].code = #documentation
* #HKQuantityTypeIdentifierVO2Max ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/vo2max"
* #HKQuantityTypeIdentifierWaistCircumference "Waist Circumference"
* #HKQuantityTypeIdentifierWaistCircumference ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWaistCircumference ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/waistcircumference"
* #HKQuantityTypeIdentifierWalkingAsymmetryPercentage "Walking Asymmetry Percentage"
* #HKQuantityTypeIdentifierWalkingAsymmetryPercentage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingAsymmetryPercentage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingasymmetrypercentage"
* #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage "Walking Double Support Percentage"
* #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingdoublesupportpercentage"
* #HKQuantityTypeIdentifierWalkingHeartRateAverage "Walking Heart Rate Average"
* #HKQuantityTypeIdentifierWalkingHeartRateAverage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingHeartRateAverage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingheartrateaverage"
* #HKQuantityTypeIdentifierWalkingSpeed "Walking Speed"
* #HKQuantityTypeIdentifierWalkingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingspeed"
* #HKQuantityTypeIdentifierWalkingStepLength "Walking Step Length"
* #HKQuantityTypeIdentifierWalkingStepLength ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingStepLength ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingsteplength"
* #HKQuantityTypeIdentifierWaterTemperature "Water Temperature"
* #HKQuantityTypeIdentifierWaterTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWaterTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/watertemperature"
* #HKQuantityTypeIdentifierWorkoutEffortScore "Workout Effort"
* #HKQuantityTypeIdentifierWorkoutEffortScore ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWorkoutEffortScore ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/workouteffortscore"
* #HKScoredAssessmentTypeIdentifierGAD7 "GAD-7"
* #HKScoredAssessmentTypeIdentifierGAD7 ^property[0].code = #documentation
* #HKScoredAssessmentTypeIdentifierGAD7 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkscoredassessmenttypeidentifier/gad7"
* #HKScoredAssessmentTypeIdentifierPHQ9 "PHQ-9"
* #HKScoredAssessmentTypeIdentifierPHQ9 ^property[0].code = #documentation
* #HKScoredAssessmentTypeIdentifierPHQ9 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkscoredassessmenttypeidentifier/phq9"
* #HKVisionPrescriptionTypeIdentifier "Vision Prescription"
* #HKVisionPrescriptionTypeIdentifier ^property[0].code = #documentation
* #HKVisionPrescriptionTypeIdentifier ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkvisionprescriptiontypeidentifier"
* #HKWorkoutRouteTypeIdentifier "Workout Route"
* #HKWorkoutRouteTypeIdentifier ^property[0].code = #documentation
* #HKWorkoutRouteTypeIdentifier ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkworkoutroutetypeidentifier"
* #HKWorkoutTypeIdentifier "Workout"
* #HKWorkoutTypeIdentifier ^property[0].code = #documentation
* #HKWorkoutTypeIdentifier ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkworkouttypeidentifier"

ValueSet: HealthKitSourceTypeVS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The complete closed set of HealthKit platform source types in the version 0.3.0 catalog."
* ^experimental = false
* include codes from system HealthKitSourceTypeCS
