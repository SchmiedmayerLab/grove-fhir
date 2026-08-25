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
* #HKCategoryTypeIdentifierAbdominalCramps "Abdominal Cramps" "The HealthKit HKCategoryTypeIdentifierAbdominalCramps source type. Grove converts it to healthkit-symptom-abdominal-cramps."
* #HKCategoryTypeIdentifierAbdominalCramps ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAbdominalCramps ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/abdominalcramps"
* #HKCategoryTypeIdentifierAcne "Acne" "The HealthKit HKCategoryTypeIdentifierAcne source type. Grove converts it to healthkit-symptom-acne."
* #HKCategoryTypeIdentifierAcne ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAcne ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/acne"
* #HKCategoryTypeIdentifierAppetiteChanges "Appetite Changes" "The HealthKit HKCategoryTypeIdentifierAppetiteChanges source type. Grove converts it to healthkit-symptom-appetite-changes."
* #HKCategoryTypeIdentifierAppetiteChanges ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAppetiteChanges ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/appetitechanges"
* #HKCategoryTypeIdentifierAppleStandHour "Apple Stand Hour" "The HealthKit HKCategoryTypeIdentifierAppleStandHour source type. Grove converts it to healthkit-apple-stand-hour."
* #HKCategoryTypeIdentifierAppleStandHour ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAppleStandHour ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/applestandhour"
* #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent "Apple Walking Steadiness Event" "The HealthKit HKCategoryTypeIdentifierAppleWalkingSteadinessEvent source type. Grove converts it to healthkit-walking-steadiness-notification."
* #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/applewalkingsteadinessevent"
* #HKCategoryTypeIdentifierAudioExposureEvent "Audio Exposure Event" "The HealthKit HKCategoryTypeIdentifierAudioExposureEvent source type. Grove converts it to healthkit-environmental-audio-exposure-notification."
* #HKCategoryTypeIdentifierAudioExposureEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierAudioExposureEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/environmentalaudioexposureevent"
* #HKCategoryTypeIdentifierBladderIncontinence "Bladder Incontinence" "The HealthKit HKCategoryTypeIdentifierBladderIncontinence source type. Grove converts it to healthkit-bladder-incontinence."
* #HKCategoryTypeIdentifierBladderIncontinence ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBladderIncontinence ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bladderincontinence"
* #HKCategoryTypeIdentifierBleedingAfterPregnancy "Bleeding After Pregnancy" "The HealthKit HKCategoryTypeIdentifierBleedingAfterPregnancy source type. Grove converts it to healthkit-bleeding-after-pregnancy."
* #HKCategoryTypeIdentifierBleedingAfterPregnancy ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBleedingAfterPregnancy ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bleedingafterpregnancy"
* #HKCategoryTypeIdentifierBleedingDuringPregnancy "Bleeding During Pregnancy" "The HealthKit HKCategoryTypeIdentifierBleedingDuringPregnancy source type. Grove converts it to healthkit-bleeding-during-pregnancy."
* #HKCategoryTypeIdentifierBleedingDuringPregnancy ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBleedingDuringPregnancy ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bleedingduringpregnancy"
* #HKCategoryTypeIdentifierBloating "Bloating" "The HealthKit HKCategoryTypeIdentifierBloating source type. Grove converts it to healthkit-symptom-bloating."
* #HKCategoryTypeIdentifierBloating ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBloating ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/bloating"
* #HKCategoryTypeIdentifierBreastPain "Breast Pain" "The HealthKit HKCategoryTypeIdentifierBreastPain source type. Grove converts it to healthkit-symptom-breast-pain."
* #HKCategoryTypeIdentifierBreastPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierBreastPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/breastpain"
* #HKCategoryTypeIdentifierCervicalMucusQuality "Cervical Mucus Quality" "The HealthKit HKCategoryTypeIdentifierCervicalMucusQuality source type. Grove converts it to grove-mobile-cervical-mucus-quality."
* #HKCategoryTypeIdentifierCervicalMucusQuality ^property[0].code = #documentation
* #HKCategoryTypeIdentifierCervicalMucusQuality ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/cervicalmucusquality"
* #HKCategoryTypeIdentifierChestTightnessOrPain "Chest Tightness/Pain" "The HealthKit HKCategoryTypeIdentifierChestTightnessOrPain source type. Grove converts it to healthkit-symptom-chest-tightness-or-pain."
* #HKCategoryTypeIdentifierChestTightnessOrPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierChestTightnessOrPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/chesttightnessorpain"
* #HKCategoryTypeIdentifierChills "Chills" "The HealthKit HKCategoryTypeIdentifierChills source type. Grove converts it to healthkit-symptom-chills."
* #HKCategoryTypeIdentifierChills ^property[0].code = #documentation
* #HKCategoryTypeIdentifierChills ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/chills"
* #HKCategoryTypeIdentifierConstipation "Constipation" "The HealthKit HKCategoryTypeIdentifierConstipation source type. Grove converts it to healthkit-symptom-constipation."
* #HKCategoryTypeIdentifierConstipation ^property[0].code = #documentation
* #HKCategoryTypeIdentifierConstipation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/constipation"
* #HKCategoryTypeIdentifierContraceptive "Contraceptive" "The HealthKit HKCategoryTypeIdentifierContraceptive source type. Grove converts it to healthkit-contraceptive-use."
* #HKCategoryTypeIdentifierContraceptive ^property[0].code = #documentation
* #HKCategoryTypeIdentifierContraceptive ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/contraceptive"
* #HKCategoryTypeIdentifierCoughing "Coughing" "The HealthKit HKCategoryTypeIdentifierCoughing source type. Grove converts it to healthkit-symptom-coughing."
* #HKCategoryTypeIdentifierCoughing ^property[0].code = #documentation
* #HKCategoryTypeIdentifierCoughing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/coughing"
* #HKCategoryTypeIdentifierDiarrhea "Diarrhea" "The HealthKit HKCategoryTypeIdentifierDiarrhea source type. Grove converts it to healthkit-symptom-diarrhea."
* #HKCategoryTypeIdentifierDiarrhea ^property[0].code = #documentation
* #HKCategoryTypeIdentifierDiarrhea ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/diarrhea"
* #HKCategoryTypeIdentifierDizziness "Dizziness" "The HealthKit HKCategoryTypeIdentifierDizziness source type. Grove converts it to healthkit-symptom-dizziness."
* #HKCategoryTypeIdentifierDizziness ^property[0].code = #documentation
* #HKCategoryTypeIdentifierDizziness ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/dizziness"
* #HKCategoryTypeIdentifierDrySkin "Dry Skin" "The HealthKit HKCategoryTypeIdentifierDrySkin source type. Grove converts it to healthkit-symptom-dry-skin."
* #HKCategoryTypeIdentifierDrySkin ^property[0].code = #documentation
* #HKCategoryTypeIdentifierDrySkin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/dryskin"
* #HKCategoryTypeIdentifierFainting "Fainting" "The HealthKit HKCategoryTypeIdentifierFainting source type. Grove converts it to healthkit-symptom-fainting."
* #HKCategoryTypeIdentifierFainting ^property[0].code = #documentation
* #HKCategoryTypeIdentifierFainting ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/fainting"
* #HKCategoryTypeIdentifierFatigue "Fatigue" "The HealthKit HKCategoryTypeIdentifierFatigue source type. Grove converts it to healthkit-symptom-fatigue."
* #HKCategoryTypeIdentifierFatigue ^property[0].code = #documentation
* #HKCategoryTypeIdentifierFatigue ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/fatigue"
* #HKCategoryTypeIdentifierFever "Fever" "The HealthKit HKCategoryTypeIdentifierFever source type. Grove converts it to healthkit-symptom-fever."
* #HKCategoryTypeIdentifierFever ^property[0].code = #documentation
* #HKCategoryTypeIdentifierFever ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/fever"
* #HKCategoryTypeIdentifierGeneralizedBodyAche "Generalized Body Ache" "The HealthKit HKCategoryTypeIdentifierGeneralizedBodyAche source type. Grove converts it to healthkit-symptom-generalized-body-ache."
* #HKCategoryTypeIdentifierGeneralizedBodyAche ^property[0].code = #documentation
* #HKCategoryTypeIdentifierGeneralizedBodyAche ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/generalizedbodyache"
* #HKCategoryTypeIdentifierHairLoss "Hair Loss" "The HealthKit HKCategoryTypeIdentifierHairLoss source type. Grove converts it to healthkit-symptom-hair-loss."
* #HKCategoryTypeIdentifierHairLoss ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHairLoss ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/hairloss"
* #HKCategoryTypeIdentifierHandwashingEvent "Handwashing Event" "The HealthKit HKCategoryTypeIdentifierHandwashingEvent source type. Grove converts it to healthkit-handwashing-session."
* #HKCategoryTypeIdentifierHandwashingEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHandwashingEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/handwashingevent"
* #HKCategoryTypeIdentifierHeadache "Headache" "The HealthKit HKCategoryTypeIdentifierHeadache source type. Grove converts it to healthkit-symptom-headache."
* #HKCategoryTypeIdentifierHeadache ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHeadache ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/headache"
* #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent "Headphone Audio Exposure Event" "The HealthKit HKCategoryTypeIdentifierHeadphoneAudioExposureEvent source type. Grove converts it to healthkit-headphone-audio-exposure-notification."
* #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/headphoneaudioexposureevent"
* #HKCategoryTypeIdentifierHeartburn "Heartburn" "The HealthKit HKCategoryTypeIdentifierHeartburn source type. Grove converts it to healthkit-symptom-heartburn."
* #HKCategoryTypeIdentifierHeartburn ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHeartburn ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/heartburn"
* #HKCategoryTypeIdentifierHighHeartRateEvent "High Heart Rate Event" "The HealthKit HKCategoryTypeIdentifierHighHeartRateEvent source type. Grove converts it to healthkit-high-heart-rate-notification."
* #HKCategoryTypeIdentifierHighHeartRateEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHighHeartRateEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/highheartrateevent"
* #HKCategoryTypeIdentifierHotFlashes "Hot Flashes" "The HealthKit HKCategoryTypeIdentifierHotFlashes source type. Grove converts it to healthkit-symptom-hot-flashes."
* #HKCategoryTypeIdentifierHotFlashes ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHotFlashes ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/hotflashes"
* #HKCategoryTypeIdentifierHypertensionEvent "Hypertension Event" "The HealthKit HKCategoryTypeIdentifierHypertensionEvent source type. Grove admits no output for it. Device alert from a proprietary screening algorithm asserting possible pathology without any pressure measurement; emitting it as an Observation would fabricate a blood-pressure-adjacent finding with no quantity. Cuff blood-pressure quantities remain the measurement surface."
* #HKCategoryTypeIdentifierHypertensionEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierHypertensionEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/hypertensionevent"
* #HKCategoryTypeIdentifierInfrequentMenstrualCycles "Infrequent Menstrual Cycles" "The HealthKit HKCategoryTypeIdentifierInfrequentMenstrualCycles source type. Grove converts it to healthkit-infrequent-menstrual-cycles."
* #HKCategoryTypeIdentifierInfrequentMenstrualCycles ^property[0].code = #documentation
* #HKCategoryTypeIdentifierInfrequentMenstrualCycles ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/infrequentmenstrualcycles"
* #HKCategoryTypeIdentifierIntermenstrualBleeding "Intermenstrual Bleeding" "The HealthKit HKCategoryTypeIdentifierIntermenstrualBleeding source type. Grove converts it to grove-mobile-intermenstrual-bleeding."
* #HKCategoryTypeIdentifierIntermenstrualBleeding ^property[0].code = #documentation
* #HKCategoryTypeIdentifierIntermenstrualBleeding ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/intermenstrualbleeding"
* #HKCategoryTypeIdentifierIrregularHeartRhythmEvent "Irregular Heart Rhythm Event" "The HealthKit HKCategoryTypeIdentifierIrregularHeartRhythmEvent source type. Grove converts it to healthkit-irregular-heart-rhythm-notification."
* #HKCategoryTypeIdentifierIrregularHeartRhythmEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierIrregularHeartRhythmEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/irregularheartrhythmevent"
* #HKCategoryTypeIdentifierIrregularMenstrualCycles "Irregular Menstrual Cycles" "The HealthKit HKCategoryTypeIdentifierIrregularMenstrualCycles source type. Grove converts it to healthkit-irregular-menstrual-cycles."
* #HKCategoryTypeIdentifierIrregularMenstrualCycles ^property[0].code = #documentation
* #HKCategoryTypeIdentifierIrregularMenstrualCycles ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/irregularmenstrualcycles"
* #HKCategoryTypeIdentifierLactation "Lactation" "The HealthKit HKCategoryTypeIdentifierLactation source type. Grove converts it to healthkit-lactation-status."
* #HKCategoryTypeIdentifierLactation ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLactation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lactation"
* #HKCategoryTypeIdentifierLossOfSmell "Loss of Smell" "The HealthKit HKCategoryTypeIdentifierLossOfSmell source type. Grove converts it to healthkit-symptom-loss-of-smell."
* #HKCategoryTypeIdentifierLossOfSmell ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLossOfSmell ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lossofsmell"
* #HKCategoryTypeIdentifierLossOfTaste "Loss of Taste" "The HealthKit HKCategoryTypeIdentifierLossOfTaste source type. Grove converts it to healthkit-symptom-loss-of-taste."
* #HKCategoryTypeIdentifierLossOfTaste ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLossOfTaste ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lossoftaste"
* #HKCategoryTypeIdentifierLowCardioFitnessEvent "Low Cardio Fitness Event" "The HealthKit HKCategoryTypeIdentifierLowCardioFitnessEvent source type. Grove converts it to healthkit-low-cardio-fitness-notification."
* #HKCategoryTypeIdentifierLowCardioFitnessEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLowCardioFitnessEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lowcardiofitnessevent"
* #HKCategoryTypeIdentifierLowHeartRateEvent "Low Heart Rate Event" "The HealthKit HKCategoryTypeIdentifierLowHeartRateEvent source type. Grove converts it to healthkit-low-heart-rate-notification."
* #HKCategoryTypeIdentifierLowHeartRateEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLowHeartRateEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lowheartrateevent"
* #HKCategoryTypeIdentifierLowerBackPain "Lower Back Pain" "The HealthKit HKCategoryTypeIdentifierLowerBackPain source type. Grove converts it to healthkit-symptom-lower-back-pain."
* #HKCategoryTypeIdentifierLowerBackPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierLowerBackPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/lowerbackpain"
* #HKCategoryTypeIdentifierMemoryLapse "Memory Lapse" "The HealthKit HKCategoryTypeIdentifierMemoryLapse source type. Grove converts it to healthkit-symptom-memory-lapse."
* #HKCategoryTypeIdentifierMemoryLapse ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMemoryLapse ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/memorylapse"
* #HKCategoryTypeIdentifierMenstrualFlow "Menstrual Flow" "The HealthKit HKCategoryTypeIdentifierMenstrualFlow source type. Grove converts it to grove-mobile-menstruation-flow."
* #HKCategoryTypeIdentifierMenstrualFlow ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMenstrualFlow ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/menstrualflow"
* #HKCategoryTypeIdentifierMindfulSession "Mindful Session" "The HealthKit HKCategoryTypeIdentifierMindfulSession source type. Grove converts it to grove-mobile-mindfulness-session."
* #HKCategoryTypeIdentifierMindfulSession ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMindfulSession ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/mindfulsession"
* #HKCategoryTypeIdentifierMoodChanges "Mood Changes" "The HealthKit HKCategoryTypeIdentifierMoodChanges source type. Grove converts it to healthkit-symptom-mood-changes."
* #HKCategoryTypeIdentifierMoodChanges ^property[0].code = #documentation
* #HKCategoryTypeIdentifierMoodChanges ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/moodchanges"
* #HKCategoryTypeIdentifierNausea "Nausea" "The HealthKit HKCategoryTypeIdentifierNausea source type. Grove converts it to healthkit-symptom-nausea."
* #HKCategoryTypeIdentifierNausea ^property[0].code = #documentation
* #HKCategoryTypeIdentifierNausea ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/nausea"
* #HKCategoryTypeIdentifierNightSweats "Night Sweats" "The HealthKit HKCategoryTypeIdentifierNightSweats source type. Grove converts it to healthkit-symptom-night-sweats."
* #HKCategoryTypeIdentifierNightSweats ^property[0].code = #documentation
* #HKCategoryTypeIdentifierNightSweats ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/nightsweats"
* #HKCategoryTypeIdentifierOvulationTestResult "Ovulation Test Result" "The HealthKit HKCategoryTypeIdentifierOvulationTestResult source type. Grove converts it to grove-mobile-ovulation-test-result."
* #HKCategoryTypeIdentifierOvulationTestResult ^property[0].code = #documentation
* #HKCategoryTypeIdentifierOvulationTestResult ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/ovulationtestresult"
* #HKCategoryTypeIdentifierPelvicPain "Pelvic Pain" "The HealthKit HKCategoryTypeIdentifierPelvicPain source type. Grove converts it to healthkit-symptom-pelvic-pain."
* #HKCategoryTypeIdentifierPelvicPain ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPelvicPain ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/pelvicpain"
* #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding "Persistent Intermenstrual Bleeding" "The HealthKit HKCategoryTypeIdentifierPersistentIntermenstrualBleeding source type. Grove converts it to healthkit-persistent-intermenstrual-bleeding."
* #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/persistentintermenstrualbleeding"
* #HKCategoryTypeIdentifierPregnancy "Pregnancy" "The HealthKit HKCategoryTypeIdentifierPregnancy source type. Grove converts it to healthkit-pregnancy-status."
* #HKCategoryTypeIdentifierPregnancy ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPregnancy ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/pregnancy"
* #HKCategoryTypeIdentifierPregnancyTestResult "Pregnancy Test Result" "The HealthKit HKCategoryTypeIdentifierPregnancyTestResult source type. Grove converts it to healthkit-pregnancy-test-result."
* #HKCategoryTypeIdentifierPregnancyTestResult ^property[0].code = #documentation
* #HKCategoryTypeIdentifierPregnancyTestResult ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/pregnancytestresult"
* #HKCategoryTypeIdentifierProgesteroneTestResult "Progesterone Test Result" "The HealthKit HKCategoryTypeIdentifierProgesteroneTestResult source type. Grove converts it to healthkit-progesterone-test-result."
* #HKCategoryTypeIdentifierProgesteroneTestResult ^property[0].code = #documentation
* #HKCategoryTypeIdentifierProgesteroneTestResult ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/progesteronetestresult"
* #HKCategoryTypeIdentifierProlongedMenstrualPeriods "Prolonged Menstrual Periods" "The HealthKit HKCategoryTypeIdentifierProlongedMenstrualPeriods source type. Grove converts it to healthkit-prolonged-menstrual-periods."
* #HKCategoryTypeIdentifierProlongedMenstrualPeriods ^property[0].code = #documentation
* #HKCategoryTypeIdentifierProlongedMenstrualPeriods ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/prolongedmenstrualperiods"
* #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat "Rapid/Pounding/Fluttering Heartbeat" "The HealthKit HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat source type. Grove converts it to healthkit-symptom-rapid-pounding-or-fluttering-heartbeat."
* #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat ^property[0].code = #documentation
* #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/rapidpoundingorflutteringheartbeat"
* #HKCategoryTypeIdentifierRunnyNose "Runny Nose" "The HealthKit HKCategoryTypeIdentifierRunnyNose source type. Grove converts it to healthkit-symptom-runny-nose."
* #HKCategoryTypeIdentifierRunnyNose ^property[0].code = #documentation
* #HKCategoryTypeIdentifierRunnyNose ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/runnynose"
* #HKCategoryTypeIdentifierSexualActivity "Sexual Activity" "The HealthKit HKCategoryTypeIdentifierSexualActivity source type. Grove converts it to grove-mobile-sexual-activity."
* #HKCategoryTypeIdentifierSexualActivity ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSexualActivity ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sexualactivity"
* #HKCategoryTypeIdentifierShortnessOfBreath "Shortness of Breath" "The HealthKit HKCategoryTypeIdentifierShortnessOfBreath source type. Grove converts it to healthkit-symptom-shortness-of-breath."
* #HKCategoryTypeIdentifierShortnessOfBreath ^property[0].code = #documentation
* #HKCategoryTypeIdentifierShortnessOfBreath ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/shortnessofbreath"
* #HKCategoryTypeIdentifierSinusCongestion "Sinus Congestion" "The HealthKit HKCategoryTypeIdentifierSinusCongestion source type. Grove converts it to healthkit-symptom-sinus-congestion."
* #HKCategoryTypeIdentifierSinusCongestion ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSinusCongestion ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sinuscongestion"
* #HKCategoryTypeIdentifierSkippedHeartbeat "Skipped Heartbeat" "The HealthKit HKCategoryTypeIdentifierSkippedHeartbeat source type. Grove converts it to healthkit-symptom-skipped-heartbeat."
* #HKCategoryTypeIdentifierSkippedHeartbeat ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSkippedHeartbeat ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/skippedheartbeat"
* #HKCategoryTypeIdentifierSleepAnalysis "Sleep Analysis" "The HealthKit HKCategoryTypeIdentifierSleepAnalysis source type. Grove converts it to grove-mobile-sleep-stage."
* #HKCategoryTypeIdentifierSleepAnalysis ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSleepAnalysis ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sleepanalysis"
* #HKCategoryTypeIdentifierSleepApneaEvent "Sleep Apnea Event" "The HealthKit HKCategoryTypeIdentifierSleepApneaEvent source type. Grove converts it to healthkit-sleep-apnea-notification."
* #HKCategoryTypeIdentifierSleepApneaEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSleepApneaEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sleepapneaevent"
* #HKCategoryTypeIdentifierSleepChanges "Sleep Changes" "The HealthKit HKCategoryTypeIdentifierSleepChanges source type. Grove converts it to healthkit-symptom-sleep-changes."
* #HKCategoryTypeIdentifierSleepChanges ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSleepChanges ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sleepchanges"
* #HKCategoryTypeIdentifierSoreThroat "Sore Throat" "The HealthKit HKCategoryTypeIdentifierSoreThroat source type. Grove converts it to healthkit-symptom-sore-throat."
* #HKCategoryTypeIdentifierSoreThroat ^property[0].code = #documentation
* #HKCategoryTypeIdentifierSoreThroat ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/sorethroat"
* #HKCategoryTypeIdentifierToothbrushingEvent "Toothbrushing Event" "The HealthKit HKCategoryTypeIdentifierToothbrushingEvent source type. Grove converts it to healthkit-toothbrushing-session."
* #HKCategoryTypeIdentifierToothbrushingEvent ^property[0].code = #documentation
* #HKCategoryTypeIdentifierToothbrushingEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/toothbrushingevent"
* #HKCategoryTypeIdentifierVaginalDryness "Vaginal Dryness" "The HealthKit HKCategoryTypeIdentifierVaginalDryness source type. Grove converts it to healthkit-vaginal-dryness."
* #HKCategoryTypeIdentifierVaginalDryness ^property[0].code = #documentation
* #HKCategoryTypeIdentifierVaginalDryness ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/vaginaldryness"
* #HKCategoryTypeIdentifierVomiting "Vomiting" "The HealthKit HKCategoryTypeIdentifierVomiting source type. Grove converts it to healthkit-symptom-vomiting."
* #HKCategoryTypeIdentifierVomiting ^property[0].code = #documentation
* #HKCategoryTypeIdentifierVomiting ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/vomiting"
* #HKCategoryTypeIdentifierWheezing "Wheezing" "The HealthKit HKCategoryTypeIdentifierWheezing source type. Grove converts it to healthkit-symptom-wheezing."
* #HKCategoryTypeIdentifierWheezing ^property[0].code = #documentation
* #HKCategoryTypeIdentifierWheezing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcategorytypeidentifier/wheezing"
* #HKCharacteristicTypeIdentifierActivityMoveMode "Activity Move Mode" "The HealthKit HKCharacteristicTypeIdentifierActivityMoveMode source type. Grove admits no output for it. A ring-display preference has no semantically exact Mobile meaning, and converting it would encode an Apple product configuration as clinical data. The mode is interpretive context for the Apple move-time and active-energy rows, which carry their own units and are converted in their own right; it adds no measurement content of its own."
* #HKCharacteristicTypeIdentifierActivityMoveMode ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierActivityMoveMode ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/activitymovemode"
* #HKCharacteristicTypeIdentifierBiologicalSex "Biological Sex" "The HealthKit HKCharacteristicTypeIdentifierBiologicalSex source type. Grove admits no output for it. Version 0.4.0 publishes no reviewed contract for this characteristic. LOINC 76689-9 'Sex assigned at birth' represents it faithfully, and the supported blood-type and wheelchair-use rows show a characteristic can carry an Observation, so this is unfinished work rather than a modelling refusal."
* #HKCharacteristicTypeIdentifierBiologicalSex ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierBiologicalSex ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/biologicalsex"
* #HKCharacteristicTypeIdentifierBloodType "Blood Type" "The HealthKit HKCharacteristicTypeIdentifierBloodType source type. Grove converts it to healthkit-blood-type."
* #HKCharacteristicTypeIdentifierBloodType ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierBloodType ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/bloodtype"
* #HKCharacteristicTypeIdentifierDateOfBirth "Date of Birth" "The HealthKit HKCharacteristicTypeIdentifierDateOfBirth source type. Grove admits no output for it. A date of birth is a direct identifier, and the exchange's Patient node is deliberately pseudonymous. Publishing it needs a privacy decision, not a mapping; age at observation is the research-safe alternative."
* #HKCharacteristicTypeIdentifierDateOfBirth ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierDateOfBirth ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/dateofbirth"
* #HKCharacteristicTypeIdentifierFitzpatrickSkinType "Fitzpatrick Skin Type" "The HealthKit HKCharacteristicTypeIdentifierFitzpatrickSkinType source type. Grove admits no output for it. A single-platform self-reported phenotype outside the measurement contract, with no consumer in the exchange set. LOINC 66555-4 represents it exactly, so this is a scope decision rather than a terminology gap."
* #HKCharacteristicTypeIdentifierFitzpatrickSkinType ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierFitzpatrickSkinType ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/fitzpatrickskintype"
* #HKCharacteristicTypeIdentifierWheelchairUse "Wheelchair Use" "The HealthKit HKCharacteristicTypeIdentifierWheelchairUse source type. Grove converts it to healthkit-wheelchair-use."
* #HKCharacteristicTypeIdentifierWheelchairUse ^property[0].code = #documentation
* #HKCharacteristicTypeIdentifierWheelchairUse ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcharacteristictypeidentifier/wheelchairuse"
* #HKClinicalTypeIdentifierAllergyRecord "Allergy Record" "The HealthKit HKClinicalTypeIdentifierAllergyRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierAllergyRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierAllergyRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/allergyrecord"
* #HKClinicalTypeIdentifierClinicalNoteRecord "Clinical Note Record" "The HealthKit HKClinicalTypeIdentifierClinicalNoteRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierClinicalNoteRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierClinicalNoteRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/clinicalnoterecord"
* #HKClinicalTypeIdentifierConditionRecord "Condition Record" "The HealthKit HKClinicalTypeIdentifierConditionRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierConditionRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierConditionRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/conditionrecord"
* #HKClinicalTypeIdentifierCoverageRecord "Coverage Record" "The HealthKit HKClinicalTypeIdentifierCoverageRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierCoverageRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierCoverageRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/coveragerecord"
* #HKClinicalTypeIdentifierImmunizationRecord "Immunization Record" "The HealthKit HKClinicalTypeIdentifierImmunizationRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierImmunizationRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierImmunizationRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/immunizationrecord"
* #HKClinicalTypeIdentifierLabResultRecord "Lab Result Record" "The HealthKit HKClinicalTypeIdentifierLabResultRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierLabResultRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierLabResultRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/labresultrecord"
* #HKClinicalTypeIdentifierMedicationRecord "Medication Record" "The HealthKit HKClinicalTypeIdentifierMedicationRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierMedicationRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierMedicationRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/medicationrecord"
* #HKClinicalTypeIdentifierProcedureRecord "Procedure Record" "The HealthKit HKClinicalTypeIdentifierProcedureRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierProcedureRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierProcedureRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/procedurerecord"
* #HKClinicalTypeIdentifierVitalSignRecord "Vital Sign Record" "The HealthKit HKClinicalTypeIdentifierVitalSignRecord source type. Grove converts it to healthkit-clinical-record-document."
* #HKClinicalTypeIdentifierVitalSignRecord ^property[0].code = #documentation
* #HKClinicalTypeIdentifierVitalSignRecord ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkclinicaltypeidentifier/vitalsignrecord"
* #HKCorrelationTypeIdentifierBloodPressure "Blood Pressure" "The HealthKit HKCorrelationTypeIdentifierBloodPressure source type. Grove converts it to grove-mobile-blood-pressure."
* #HKCorrelationTypeIdentifierBloodPressure ^property[0].code = #documentation
* #HKCorrelationTypeIdentifierBloodPressure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcorrelationtypeidentifier/bloodpressure"
* #HKCorrelationTypeIdentifierFood "Food" "The HealthKit HKCorrelationTypeIdentifierFood source type. Grove admits no output for it. No shared or adapter-specific output contract is published for this type."
* #HKCorrelationTypeIdentifierFood ^property[0].code = #documentation
* #HKCorrelationTypeIdentifierFood ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkcorrelationtypeidentifier/food"
* #HKDataTypeIdentifierAudiogram "Audiogram" "The HealthKit HKDataTypeIdentifierAudiogram source type. Grove admits no output for it. No shared or HealthKit-adapter output contract is published for this sample type."
* #HKDataTypeIdentifierAudiogram ^property[0].code = #documentation
* #HKDataTypeIdentifierAudiogram ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkaudiogramsampletype"
* #HKDataTypeIdentifierElectrocardiogram "ECG" "The HealthKit HKDataTypeIdentifierElectrocardiogram source type. Grove converts it to grove-sensor-ecg-observation and healthkit-ecg-observation."
* #HKDataTypeIdentifierElectrocardiogram ^property[0].code = #documentation
* #HKDataTypeIdentifierElectrocardiogram ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkelectrocardiogramtype"
* #HKDataTypeIdentifierHeartbeatSeries "Heartbeat Series" "The HealthKit HKDataTypeIdentifierHeartbeatSeries source type. Grove admits no output for it. The beat-to-beat interval series has a published grove-csv-1 column schema, but the HealthKit adapter has no recording-document profile to carry it yet, so no output is admitted."
* #HKDataTypeIdentifierHeartbeatSeries ^property[0].code = #documentation
* #HKDataTypeIdentifierHeartbeatSeries ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdatatypeidentifierheartbeatseries"
* #HKDataTypeStateOfMind "State of Mind" "The HealthKit HKDataTypeStateOfMind source type. Grove converts it to healthkit-state-of-mind."
* #HKDataTypeStateOfMind ^property[0].code = #documentation
* #HKDataTypeStateOfMind ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdatatypeidentifierstateofmind"
* #HKDataTypeUserAnnotatedMedicationConcept "User Annotated Medication Concept" "The HealthKit HKDataTypeUserAnnotatedMedicationConcept source type. Grove admits no output for it. No shared or adapter-specific output contract is published for this type."
* #HKDataTypeUserAnnotatedMedicationConcept ^property[0].code = #documentation
* #HKDataTypeUserAnnotatedMedicationConcept ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdatatypeidentifieruserannotatedmedicationconcept"
* #HKDocumentTypeIdentifierCDA "CDA Document" "The HealthKit HKDocumentTypeIdentifierCDA source type. Grove admits no output for it. No shared or adapter-specific output contract is published for this type."
* #HKDocumentTypeIdentifierCDA ^property[0].code = #documentation
* #HKDocumentTypeIdentifierCDA ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkdocumenttypeidentifier/cda"
* #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent "Medication Dose Event" "The HealthKit HKMedicationDoseEventTypeIdentifierMedicationDoseEvent source type. Grove admits no output for it. No shared or adapter-specific output contract is published for this type."
* #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent ^property[0].code = #documentation
* #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkmedicationdoseeventtypeidentifiermedicationdoseevent"
* #HKQuantityTypeIdentifierActiveEnergyBurned "Active Energy Burned" "The HealthKit HKQuantityTypeIdentifierActiveEnergyBurned source type. Grove converts it to grove-mobile-active-energy."
* #HKQuantityTypeIdentifierActiveEnergyBurned ^property[0].code = #documentation
* #HKQuantityTypeIdentifierActiveEnergyBurned ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/activeenergyburned"
* #HKQuantityTypeIdentifierAppleExerciseTime "Apple Exercise Time" "The HealthKit HKQuantityTypeIdentifierAppleExerciseTime source type. Grove converts it to healthkit-apple-exercise-time."
* #HKQuantityTypeIdentifierAppleExerciseTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleExerciseTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/appleexercisetime"
* #HKQuantityTypeIdentifierAppleMoveTime "Apple Move Time" "The HealthKit HKQuantityTypeIdentifierAppleMoveTime source type. Grove converts it to healthkit-apple-move-time."
* #HKQuantityTypeIdentifierAppleMoveTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleMoveTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applemovetime"
* #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances "Apple Sleeping Breathing Disturbances" "The HealthKit HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances source type. Grove converts it to healthkit-sleeping-breathing-disturbances."
* #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applesleepingbreathingdisturbances"
* #HKQuantityTypeIdentifierAppleSleepingWristTemperature "Apple Sleeping Wrist Temperature" "The HealthKit HKQuantityTypeIdentifierAppleSleepingWristTemperature source type. Grove converts it to grove-mobile-skin-temperature."
* #HKQuantityTypeIdentifierAppleSleepingWristTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleSleepingWristTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applesleepingwristtemperature"
* #HKQuantityTypeIdentifierAppleStandTime "Apple Stand Time" "The HealthKit HKQuantityTypeIdentifierAppleStandTime source type. Grove converts it to healthkit-apple-stand-time."
* #HKQuantityTypeIdentifierAppleStandTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleStandTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applestandtime"
* #HKQuantityTypeIdentifierAppleWalkingSteadiness "Apple Walking Steadiness" "The HealthKit HKQuantityTypeIdentifierAppleWalkingSteadiness source type. Grove converts it to healthkit-walking-steadiness."
* #HKQuantityTypeIdentifierAppleWalkingSteadiness ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAppleWalkingSteadiness ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/applewalkingsteadiness"
* #HKQuantityTypeIdentifierAtrialFibrillationBurden "AFib Burden" "The HealthKit HKQuantityTypeIdentifierAtrialFibrillationBurden source type. Grove converts it to healthkit-atrial-fibrillation-burden."
* #HKQuantityTypeIdentifierAtrialFibrillationBurden ^property[0].code = #documentation
* #HKQuantityTypeIdentifierAtrialFibrillationBurden ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/atrialfibrillationburden"
* #HKQuantityTypeIdentifierBasalBodyTemperature "Basal Body Temperature" "The HealthKit HKQuantityTypeIdentifierBasalBodyTemperature source type. Grove converts it to grove-mobile-basal-body-temperature."
* #HKQuantityTypeIdentifierBasalBodyTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBasalBodyTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/basalbodytemperature"
* #HKQuantityTypeIdentifierBasalEnergyBurned "Basal Energy Burned" "The HealthKit HKQuantityTypeIdentifierBasalEnergyBurned source type. Grove converts it to grove-mobile-basal-energy."
* #HKQuantityTypeIdentifierBasalEnergyBurned ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBasalEnergyBurned ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/basalenergyburned"
* #HKQuantityTypeIdentifierBloodAlcoholContent "Blood Alcohol Content" "The HealthKit HKQuantityTypeIdentifierBloodAlcoholContent source type. Grove converts it to healthkit-blood-alcohol-content."
* #HKQuantityTypeIdentifierBloodAlcoholContent ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodAlcoholContent ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodalcoholcontent"
* #HKQuantityTypeIdentifierBloodGlucose "Blood Glucose" "The HealthKit HKQuantityTypeIdentifierBloodGlucose source type. Grove converts it to grove-mobile-blood-glucose-unspecified-specimen."
* #HKQuantityTypeIdentifierBloodGlucose ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodGlucose ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodglucose"
* #HKQuantityTypeIdentifierBloodPressureDiastolic "Blood Pressure (Diastolic)" "The HealthKit HKQuantityTypeIdentifierBloodPressureDiastolic source type. Grove converts it to grove-mobile-blood-pressure."
* #HKQuantityTypeIdentifierBloodPressureDiastolic ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodPressureDiastolic ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodpressurediastolic"
* #HKQuantityTypeIdentifierBloodPressureSystolic "Blood Pressure (Systolic)" "The HealthKit HKQuantityTypeIdentifierBloodPressureSystolic source type. Grove converts it to grove-mobile-blood-pressure."
* #HKQuantityTypeIdentifierBloodPressureSystolic ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBloodPressureSystolic ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bloodpressuresystolic"
* #HKQuantityTypeIdentifierBodyFatPercentage "Body Fat Percentage" "The HealthKit HKQuantityTypeIdentifierBodyFatPercentage source type. Grove converts it to grove-mobile-body-fat-percentage."
* #HKQuantityTypeIdentifierBodyFatPercentage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyFatPercentage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodyfatpercentage"
* #HKQuantityTypeIdentifierBodyMass "Body Mass" "The HealthKit HKQuantityTypeIdentifierBodyMass source type. Grove converts it to grove-mobile-body-weight."
* #HKQuantityTypeIdentifierBodyMass ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyMass ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodymass"
* #HKQuantityTypeIdentifierBodyMassIndex "BMI" "The HealthKit HKQuantityTypeIdentifierBodyMassIndex source type. Grove converts it to bmi and healthkit-observation."
* #HKQuantityTypeIdentifierBodyMassIndex ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyMassIndex ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodymassindex"
* #HKQuantityTypeIdentifierBodyTemperature "Body Temperature" "The HealthKit HKQuantityTypeIdentifierBodyTemperature source type. Grove converts it to grove-mobile-body-temperature."
* #HKQuantityTypeIdentifierBodyTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierBodyTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/bodytemperature"
* #HKQuantityTypeIdentifierCrossCountrySkiingSpeed "Cross Country Skiing Speed" "The HealthKit HKQuantityTypeIdentifierCrossCountrySkiingSpeed source type. Grove converts it to grove-mobile-speed."
* #HKQuantityTypeIdentifierCrossCountrySkiingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCrossCountrySkiingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/crosscountryskiingspeed"
* #HKQuantityTypeIdentifierCyclingCadence "Cycling Cadence" "The HealthKit HKQuantityTypeIdentifierCyclingCadence source type. Grove converts it to grove-mobile-cycling-cadence."
* #HKQuantityTypeIdentifierCyclingCadence ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingCadence ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingcadence"
* #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower "Cycling Functional Threshold Power" "The HealthKit HKQuantityTypeIdentifierCyclingFunctionalThresholdPower source type. Grove converts it to healthkit-cycling-functional-threshold-power."
* #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingfunctionalthresholdpower"
* #HKQuantityTypeIdentifierCyclingPower "Cycling Power" "The HealthKit HKQuantityTypeIdentifierCyclingPower source type. Grove converts it to grove-mobile-power."
* #HKQuantityTypeIdentifierCyclingPower ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingPower ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingpower"
* #HKQuantityTypeIdentifierCyclingSpeed "Cycling Speed" "The HealthKit HKQuantityTypeIdentifierCyclingSpeed source type. Grove converts it to grove-mobile-speed."
* #HKQuantityTypeIdentifierCyclingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierCyclingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/cyclingspeed"
* #HKQuantityTypeIdentifierDietaryBiotin "Dietary Biotin Intake" "The HealthKit HKQuantityTypeIdentifierDietaryBiotin source type. Grove converts it to grove-mobile-dietary-biotin."
* #HKQuantityTypeIdentifierDietaryBiotin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryBiotin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarybiotin"
* #HKQuantityTypeIdentifierDietaryCaffeine "Dietary Caffeine Intake" "The HealthKit HKQuantityTypeIdentifierDietaryCaffeine source type. Grove converts it to grove-mobile-dietary-caffeine."
* #HKQuantityTypeIdentifierDietaryCaffeine ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCaffeine ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycaffeine"
* #HKQuantityTypeIdentifierDietaryCalcium "Dietary Calcium Intake" "The HealthKit HKQuantityTypeIdentifierDietaryCalcium source type. Grove converts it to grove-mobile-dietary-calcium."
* #HKQuantityTypeIdentifierDietaryCalcium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCalcium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycalcium"
* #HKQuantityTypeIdentifierDietaryCarbohydrates "Dietary Carbohydrates Intake" "The HealthKit HKQuantityTypeIdentifierDietaryCarbohydrates source type. Grove converts it to grove-mobile-dietary-carbohydrates."
* #HKQuantityTypeIdentifierDietaryCarbohydrates ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCarbohydrates ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycarbohydrates"
* #HKQuantityTypeIdentifierDietaryChloride "Dietary Chloride Intake" "The HealthKit HKQuantityTypeIdentifierDietaryChloride source type. Grove converts it to grove-mobile-dietary-chloride."
* #HKQuantityTypeIdentifierDietaryChloride ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryChloride ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarychloride"
* #HKQuantityTypeIdentifierDietaryCholesterol "Dietary Cholesterol Intake" "The HealthKit HKQuantityTypeIdentifierDietaryCholesterol source type. Grove converts it to grove-mobile-dietary-cholesterol."
* #HKQuantityTypeIdentifierDietaryCholesterol ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCholesterol ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycholesterol"
* #HKQuantityTypeIdentifierDietaryChromium "Dietary Chromium Intake" "The HealthKit HKQuantityTypeIdentifierDietaryChromium source type. Grove converts it to grove-mobile-dietary-chromium."
* #HKQuantityTypeIdentifierDietaryChromium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryChromium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarychromium"
* #HKQuantityTypeIdentifierDietaryCopper "Dietary Copper Intake" "The HealthKit HKQuantityTypeIdentifierDietaryCopper source type. Grove converts it to grove-mobile-dietary-copper."
* #HKQuantityTypeIdentifierDietaryCopper ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryCopper ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarycopper"
* #HKQuantityTypeIdentifierDietaryEnergyConsumed "Dietary Energy Consumed" "The HealthKit HKQuantityTypeIdentifierDietaryEnergyConsumed source type. Grove converts it to grove-mobile-dietary-energy."
* #HKQuantityTypeIdentifierDietaryEnergyConsumed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryEnergyConsumed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryenergyconsumed"
* #HKQuantityTypeIdentifierDietaryFatMonounsaturated "Dietary Monounsaturated Fat Intake" "The HealthKit HKQuantityTypeIdentifierDietaryFatMonounsaturated source type. Grove converts it to grove-mobile-dietary-fat-monounsaturated."
* #HKQuantityTypeIdentifierDietaryFatMonounsaturated ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatMonounsaturated ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfatmonounsaturated"
* #HKQuantityTypeIdentifierDietaryFatPolyunsaturated "Dietary Polyunsaturated Fat Intake" "The HealthKit HKQuantityTypeIdentifierDietaryFatPolyunsaturated source type. Grove converts it to grove-mobile-dietary-fat-polyunsaturated."
* #HKQuantityTypeIdentifierDietaryFatPolyunsaturated ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatPolyunsaturated ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfatpolyunsaturated"
* #HKQuantityTypeIdentifierDietaryFatSaturated "Dietary Saturated Fat Intake" "The HealthKit HKQuantityTypeIdentifierDietaryFatSaturated source type. Grove converts it to grove-mobile-dietary-fat-saturated."
* #HKQuantityTypeIdentifierDietaryFatSaturated ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatSaturated ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfatsaturated"
* #HKQuantityTypeIdentifierDietaryFatTotal "Dietary Total Fat Intake" "The HealthKit HKQuantityTypeIdentifierDietaryFatTotal source type. Grove converts it to grove-mobile-dietary-fat-total."
* #HKQuantityTypeIdentifierDietaryFatTotal ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFatTotal ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfattotal"
* #HKQuantityTypeIdentifierDietaryFiber "Dietary Fiber Intake" "The HealthKit HKQuantityTypeIdentifierDietaryFiber source type. Grove converts it to grove-mobile-dietary-fiber."
* #HKQuantityTypeIdentifierDietaryFiber ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFiber ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfiber"
* #HKQuantityTypeIdentifierDietaryFolate "Dietary Folate Intake" "The HealthKit HKQuantityTypeIdentifierDietaryFolate source type. Grove converts it to grove-mobile-dietary-folate."
* #HKQuantityTypeIdentifierDietaryFolate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryFolate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryfolate"
* #HKQuantityTypeIdentifierDietaryIodine "Dietary Iodine Intake" "The HealthKit HKQuantityTypeIdentifierDietaryIodine source type. Grove converts it to grove-mobile-dietary-iodine."
* #HKQuantityTypeIdentifierDietaryIodine ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryIodine ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryiodine"
* #HKQuantityTypeIdentifierDietaryIron "Dietary Iron Intake" "The HealthKit HKQuantityTypeIdentifierDietaryIron source type. Grove converts it to grove-mobile-dietary-iron."
* #HKQuantityTypeIdentifierDietaryIron ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryIron ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryiron"
* #HKQuantityTypeIdentifierDietaryMagnesium "Dietary Magnesium Intake" "The HealthKit HKQuantityTypeIdentifierDietaryMagnesium source type. Grove converts it to grove-mobile-dietary-magnesium."
* #HKQuantityTypeIdentifierDietaryMagnesium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryMagnesium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarymagnesium"
* #HKQuantityTypeIdentifierDietaryManganese "Dietary Manganese Intake" "The HealthKit HKQuantityTypeIdentifierDietaryManganese source type. Grove converts it to grove-mobile-dietary-manganese."
* #HKQuantityTypeIdentifierDietaryManganese ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryManganese ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarymanganese"
* #HKQuantityTypeIdentifierDietaryMolybdenum "Dietary Molybdenum Intake" "The HealthKit HKQuantityTypeIdentifierDietaryMolybdenum source type. Grove converts it to grove-mobile-dietary-molybdenum."
* #HKQuantityTypeIdentifierDietaryMolybdenum ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryMolybdenum ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarymolybdenum"
* #HKQuantityTypeIdentifierDietaryNiacin "Dietary Niacin Intake" "The HealthKit HKQuantityTypeIdentifierDietaryNiacin source type. Grove converts it to grove-mobile-dietary-niacin."
* #HKQuantityTypeIdentifierDietaryNiacin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryNiacin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryniacin"
* #HKQuantityTypeIdentifierDietaryPantothenicAcid "Dietary Pantothenic Acid Intake" "The HealthKit HKQuantityTypeIdentifierDietaryPantothenicAcid source type. Grove converts it to grove-mobile-dietary-pantothenic-acid."
* #HKQuantityTypeIdentifierDietaryPantothenicAcid ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryPantothenicAcid ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarypantothenicacid"
* #HKQuantityTypeIdentifierDietaryPhosphorus "Dietary Phosphorus Intake" "The HealthKit HKQuantityTypeIdentifierDietaryPhosphorus source type. Grove converts it to grove-mobile-dietary-phosphorus."
* #HKQuantityTypeIdentifierDietaryPhosphorus ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryPhosphorus ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryphosphorus"
* #HKQuantityTypeIdentifierDietaryPotassium "Dietary Potassium Intake" "The HealthKit HKQuantityTypeIdentifierDietaryPotassium source type. Grove converts it to grove-mobile-dietary-potassium."
* #HKQuantityTypeIdentifierDietaryPotassium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryPotassium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarypotassium"
* #HKQuantityTypeIdentifierDietaryProtein "Dietary Protein Intake" "The HealthKit HKQuantityTypeIdentifierDietaryProtein source type. Grove converts it to grove-mobile-dietary-protein."
* #HKQuantityTypeIdentifierDietaryProtein ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryProtein ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryprotein"
* #HKQuantityTypeIdentifierDietaryRiboflavin "Dietary Riboflavin Intake" "The HealthKit HKQuantityTypeIdentifierDietaryRiboflavin source type. Grove converts it to grove-mobile-dietary-riboflavin."
* #HKQuantityTypeIdentifierDietaryRiboflavin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryRiboflavin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryriboflavin"
* #HKQuantityTypeIdentifierDietarySelenium "Dietary Selenium Intake" "The HealthKit HKQuantityTypeIdentifierDietarySelenium source type. Grove converts it to grove-mobile-dietary-selenium."
* #HKQuantityTypeIdentifierDietarySelenium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietarySelenium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryselenium"
* #HKQuantityTypeIdentifierDietarySodium "Dietary Sodium Intake" "The HealthKit HKQuantityTypeIdentifierDietarySodium source type. Grove converts it to grove-mobile-dietary-sodium."
* #HKQuantityTypeIdentifierDietarySodium ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietarySodium ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarysodium"
* #HKQuantityTypeIdentifierDietarySugar "Dietary Sugar Intake" "The HealthKit HKQuantityTypeIdentifierDietarySugar source type. Grove converts it to grove-mobile-dietary-sugar."
* #HKQuantityTypeIdentifierDietarySugar ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietarySugar ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarysugar"
* #HKQuantityTypeIdentifierDietaryThiamin "Dietary Thiamin Intake" "The HealthKit HKQuantityTypeIdentifierDietaryThiamin source type. Grove converts it to grove-mobile-dietary-thiamin."
* #HKQuantityTypeIdentifierDietaryThiamin ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryThiamin ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarythiamin"
* #HKQuantityTypeIdentifierDietaryVitaminA "Dietary Vitamin A Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminA source type. Grove converts it to grove-mobile-dietary-vitamin-a."
* #HKQuantityTypeIdentifierDietaryVitaminA ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminA ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamina"
* #HKQuantityTypeIdentifierDietaryVitaminB12 "Dietary Vitamin B12 Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminB12 source type. Grove converts it to grove-mobile-dietary-vitamin-b12."
* #HKQuantityTypeIdentifierDietaryVitaminB12 ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminB12 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitaminb12"
* #HKQuantityTypeIdentifierDietaryVitaminB6 "Dietary Vitamin B6 Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminB6 source type. Grove converts it to grove-mobile-dietary-vitamin-b6."
* #HKQuantityTypeIdentifierDietaryVitaminB6 ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminB6 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitaminb6"
* #HKQuantityTypeIdentifierDietaryVitaminC "Dietary Vitamin C Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminC source type. Grove converts it to grove-mobile-dietary-vitamin-c."
* #HKQuantityTypeIdentifierDietaryVitaminC ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminC ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitaminc"
* #HKQuantityTypeIdentifierDietaryVitaminD "Dietary Vitamin D Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminD source type. Grove converts it to grove-mobile-dietary-vitamin-d."
* #HKQuantityTypeIdentifierDietaryVitaminD ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminD ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamind"
* #HKQuantityTypeIdentifierDietaryVitaminE "Dietary Vitamin E Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminE source type. Grove converts it to grove-mobile-dietary-vitamin-e."
* #HKQuantityTypeIdentifierDietaryVitaminE ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminE ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamine"
* #HKQuantityTypeIdentifierDietaryVitaminK "Dietary Vitamin K Intake" "The HealthKit HKQuantityTypeIdentifierDietaryVitaminK source type. Grove converts it to grove-mobile-dietary-vitamin-k."
* #HKQuantityTypeIdentifierDietaryVitaminK ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryVitaminK ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryvitamink"
* #HKQuantityTypeIdentifierDietaryWater "Dietary Water Intake" "The HealthKit HKQuantityTypeIdentifierDietaryWater source type. Grove converts it to grove-mobile-fluid-intake."
* #HKQuantityTypeIdentifierDietaryWater ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryWater ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietarywater"
* #HKQuantityTypeIdentifierDietaryZinc "Dietary Zinc Intake" "The HealthKit HKQuantityTypeIdentifierDietaryZinc source type. Grove converts it to grove-mobile-dietary-zinc."
* #HKQuantityTypeIdentifierDietaryZinc ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDietaryZinc ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/dietaryzinc"
* #HKQuantityTypeIdentifierDistanceCrossCountrySkiing "Cross-Country Skiing Distance" "The HealthKit HKQuantityTypeIdentifierDistanceCrossCountrySkiing source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceCrossCountrySkiing ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceCrossCountrySkiing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancecrosscountryskiing"
* #HKQuantityTypeIdentifierDistanceCycling "Cycling Distance" "The HealthKit HKQuantityTypeIdentifierDistanceCycling source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceCycling ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceCycling ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancecycling"
* #HKQuantityTypeIdentifierDistanceDownhillSnowSports "Downhill Snow Sports Distance" "The HealthKit HKQuantityTypeIdentifierDistanceDownhillSnowSports source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceDownhillSnowSports ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceDownhillSnowSports ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancedownhillsnowsports"
* #HKQuantityTypeIdentifierDistancePaddleSports "Paddle Sports Distance" "The HealthKit HKQuantityTypeIdentifierDistancePaddleSports source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistancePaddleSports ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistancePaddleSports ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancepaddlesports"
* #HKQuantityTypeIdentifierDistanceRowing "Rowing Distance" "The HealthKit HKQuantityTypeIdentifierDistanceRowing source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceRowing ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceRowing ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancerowing"
* #HKQuantityTypeIdentifierDistanceSkatingSports "Skating Sports Distance" "The HealthKit HKQuantityTypeIdentifierDistanceSkatingSports source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceSkatingSports ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceSkatingSports ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distanceskatingsports"
* #HKQuantityTypeIdentifierDistanceSwimming "Swimming Distance" "The HealthKit HKQuantityTypeIdentifierDistanceSwimming source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceSwimming ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceSwimming ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distanceswimming"
* #HKQuantityTypeIdentifierDistanceWalkingRunning "Distance Walking/Running" "The HealthKit HKQuantityTypeIdentifierDistanceWalkingRunning source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceWalkingRunning ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceWalkingRunning ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancewalkingrunning"
* #HKQuantityTypeIdentifierDistanceWheelchair "Wheelchair Distance" "The HealthKit HKQuantityTypeIdentifierDistanceWheelchair source type. Grove converts it to grove-mobile-distance."
* #HKQuantityTypeIdentifierDistanceWheelchair ^property[0].code = #documentation
* #HKQuantityTypeIdentifierDistanceWheelchair ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/distancewheelchair"
* #HKQuantityTypeIdentifierElectrodermalActivity "Electrodermal Activity" "The HealthKit HKQuantityTypeIdentifierElectrodermalActivity source type. Grove converts it to grove-mobile-electrodermal-activity."
* #HKQuantityTypeIdentifierElectrodermalActivity ^property[0].code = #documentation
* #HKQuantityTypeIdentifierElectrodermalActivity ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/electrodermalactivity"
* #HKQuantityTypeIdentifierEnvironmentalAudioExposure "Environmental Audio Exposure" "The HealthKit HKQuantityTypeIdentifierEnvironmentalAudioExposure source type. Grove converts it to healthkit-environmental-audio-exposure."
* #HKQuantityTypeIdentifierEnvironmentalAudioExposure ^property[0].code = #documentation
* #HKQuantityTypeIdentifierEnvironmentalAudioExposure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/environmentalaudioexposure"
* #HKQuantityTypeIdentifierEnvironmentalSoundReduction "Environmental Sound Reduction" "The HealthKit HKQuantityTypeIdentifierEnvironmentalSoundReduction source type. Grove converts it to healthkit-environmental-sound-reduction."
* #HKQuantityTypeIdentifierEnvironmentalSoundReduction ^property[0].code = #documentation
* #HKQuantityTypeIdentifierEnvironmentalSoundReduction ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/environmentalsoundreduction"
* #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore "Estimated Workout Effort" "The HealthKit HKQuantityTypeIdentifierEstimatedWorkoutEffortScore source type. Grove converts it to healthkit-workout-effort-score."
* #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore ^property[0].code = #documentation
* #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/estimatedworkouteffortscore"
* #HKQuantityTypeIdentifierFlightsClimbed "Flights Climbed" "The HealthKit HKQuantityTypeIdentifierFlightsClimbed source type. Grove converts it to grove-mobile-flights-climbed."
* #HKQuantityTypeIdentifierFlightsClimbed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierFlightsClimbed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/flightsclimbed"
* #HKQuantityTypeIdentifierForcedExpiratoryVolume1 "Forced Expiratory Volume (1 sec)" "The HealthKit HKQuantityTypeIdentifierForcedExpiratoryVolume1 source type. Grove converts it to healthkit-forced-expiratory-volume-1."
* #HKQuantityTypeIdentifierForcedExpiratoryVolume1 ^property[0].code = #documentation
* #HKQuantityTypeIdentifierForcedExpiratoryVolume1 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/forcedexpiratoryvolume1"
* #HKQuantityTypeIdentifierForcedVitalCapacity "Forced Vital Capacity" "The HealthKit HKQuantityTypeIdentifierForcedVitalCapacity source type. Grove converts it to healthkit-forced-vital-capacity."
* #HKQuantityTypeIdentifierForcedVitalCapacity ^property[0].code = #documentation
* #HKQuantityTypeIdentifierForcedVitalCapacity ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/forcedvitalcapacity"
* #HKQuantityTypeIdentifierHeadphoneAudioExposure "Headphone Audio Exposure" "The HealthKit HKQuantityTypeIdentifierHeadphoneAudioExposure source type. Grove converts it to healthkit-headphone-audio-exposure."
* #HKQuantityTypeIdentifierHeadphoneAudioExposure ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeadphoneAudioExposure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/headphoneaudioexposure"
* #HKQuantityTypeIdentifierHeartRate "Heart Rate" "The HealthKit HKQuantityTypeIdentifierHeartRate source type. Grove converts it to grove-mobile-heart-rate."
* #HKQuantityTypeIdentifierHeartRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeartRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/heartrate"
* #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute "Heart Rate Recovery (1 min)" "The HealthKit HKQuantityTypeIdentifierHeartRateRecoveryOneMinute source type. Grove converts it to healthkit-heart-rate-recovery-one-minute."
* #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/heartraterecoveryoneminute"
* #HKQuantityTypeIdentifierHeartRateVariabilitySDNN "Heart Rate Variability SDNN" "The HealthKit HKQuantityTypeIdentifierHeartRateVariabilitySDNN source type. Grove converts it to grove-mobile-heart-rate-variability-sdnn."
* #HKQuantityTypeIdentifierHeartRateVariabilitySDNN ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeartRateVariabilitySDNN ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/heartratevariabilitysdnn"
* #HKQuantityTypeIdentifierHeight "Height" "The HealthKit HKQuantityTypeIdentifierHeight source type. Grove converts it to grove-mobile-body-height."
* #HKQuantityTypeIdentifierHeight ^property[0].code = #documentation
* #HKQuantityTypeIdentifierHeight ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/height"
* #HKQuantityTypeIdentifierInhalerUsage "Inhaler Usage" "The HealthKit HKQuantityTypeIdentifierInhalerUsage source type. Grove converts it to healthkit-inhaler-usage."
* #HKQuantityTypeIdentifierInhalerUsage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierInhalerUsage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/inhalerusage"
* #HKQuantityTypeIdentifierInsulinDelivery "Insulin Delivery" "The HealthKit HKQuantityTypeIdentifierInsulinDelivery source type. Grove converts it to healthkit-insulin-delivery."
* #HKQuantityTypeIdentifierInsulinDelivery ^property[0].code = #documentation
* #HKQuantityTypeIdentifierInsulinDelivery ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/insulindelivery"
* #HKQuantityTypeIdentifierLeanBodyMass "Lean Body Mass" "The HealthKit HKQuantityTypeIdentifierLeanBodyMass source type. Grove converts it to grove-mobile-lean-body-mass."
* #HKQuantityTypeIdentifierLeanBodyMass ^property[0].code = #documentation
* #HKQuantityTypeIdentifierLeanBodyMass ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/leanbodymass"
* #HKQuantityTypeIdentifierNikeFuel "NikeFuel" "The HealthKit HKQuantityTypeIdentifierNikeFuel source type. Grove admits no output for it. NikeFuel is an opaque vendor index with an unpublished formula and a retired ecosystem; it has no physiological dimension, no UCUM representation beyond an arbitrary annotation, and no second source, so normalizing it would launder an undefined score into an exchange measurement."
* #HKQuantityTypeIdentifierNikeFuel ^property[0].code = #documentation
* #HKQuantityTypeIdentifierNikeFuel ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/nikefuel"
* #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages "Number of Alcoholic Beverages" "The HealthKit HKQuantityTypeIdentifierNumberOfAlcoholicBeverages source type. Grove converts it to healthkit-number-of-alcoholic-beverages."
* #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages ^property[0].code = #documentation
* #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/numberofalcoholicbeverages"
* #HKQuantityTypeIdentifierNumberOfTimesFallen "Number of Times Fallen" "The HealthKit HKQuantityTypeIdentifierNumberOfTimesFallen source type. Grove converts it to healthkit-number-of-times-fallen."
* #HKQuantityTypeIdentifierNumberOfTimesFallen ^property[0].code = #documentation
* #HKQuantityTypeIdentifierNumberOfTimesFallen ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/numberoftimesfallen"
* #HKQuantityTypeIdentifierOxygenSaturation "Oxygen Saturation" "The HealthKit HKQuantityTypeIdentifierOxygenSaturation source type. Grove converts it to grove-mobile-oxygen-saturation."
* #HKQuantityTypeIdentifierOxygenSaturation ^property[0].code = #documentation
* #HKQuantityTypeIdentifierOxygenSaturation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/oxygensaturation"
* #HKQuantityTypeIdentifierPaddleSportsSpeed "Paddle Sports Speed" "The HealthKit HKQuantityTypeIdentifierPaddleSportsSpeed source type. Grove converts it to grove-mobile-speed."
* #HKQuantityTypeIdentifierPaddleSportsSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPaddleSportsSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/paddlesportsspeed"
* #HKQuantityTypeIdentifierPeakExpiratoryFlowRate "Peak Expiratory Flow Rate" "The HealthKit HKQuantityTypeIdentifierPeakExpiratoryFlowRate source type. Grove converts it to healthkit-peak-expiratory-flow-rate."
* #HKQuantityTypeIdentifierPeakExpiratoryFlowRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPeakExpiratoryFlowRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/peakexpiratoryflowrate"
* #HKQuantityTypeIdentifierPeripheralPerfusionIndex "Peripheral Perfusion Index" "The HealthKit HKQuantityTypeIdentifierPeripheralPerfusionIndex source type. Grove converts it to healthkit-peripheral-perfusion-index."
* #HKQuantityTypeIdentifierPeripheralPerfusionIndex ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPeripheralPerfusionIndex ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/peripheralperfusionindex"
* #HKQuantityTypeIdentifierPhysicalEffort "Physical Effort" "The HealthKit HKQuantityTypeIdentifierPhysicalEffort source type. Grove converts it to healthkit-physical-effort."
* #HKQuantityTypeIdentifierPhysicalEffort ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPhysicalEffort ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/physicaleffort"
* #HKQuantityTypeIdentifierPushCount "Wheelchair Push Count" "The HealthKit HKQuantityTypeIdentifierPushCount source type. Grove converts it to grove-mobile-wheelchair-push-count."
* #HKQuantityTypeIdentifierPushCount ^property[0].code = #documentation
* #HKQuantityTypeIdentifierPushCount ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/pushcount"
* #HKQuantityTypeIdentifierRespiratoryRate "Respiratory Rate" "The HealthKit HKQuantityTypeIdentifierRespiratoryRate source type. Grove converts it to grove-mobile-respiratory-rate."
* #HKQuantityTypeIdentifierRespiratoryRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRespiratoryRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/respiratoryrate"
* #HKQuantityTypeIdentifierRestingHeartRate "Resting Heart Rate" "The HealthKit HKQuantityTypeIdentifierRestingHeartRate source type. Grove converts it to grove-mobile-resting-heart-rate."
* #HKQuantityTypeIdentifierRestingHeartRate ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRestingHeartRate ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/restingheartrate"
* #HKQuantityTypeIdentifierRowingSpeed "Rowing Speed" "The HealthKit HKQuantityTypeIdentifierRowingSpeed source type. Grove converts it to grove-mobile-speed."
* #HKQuantityTypeIdentifierRowingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRowingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/rowingspeed"
* #HKQuantityTypeIdentifierRunningGroundContactTime "Ground Contact Time" "The HealthKit HKQuantityTypeIdentifierRunningGroundContactTime source type. Grove converts it to healthkit-running-ground-contact-time."
* #HKQuantityTypeIdentifierRunningGroundContactTime ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningGroundContactTime ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runninggroundcontacttime"
* #HKQuantityTypeIdentifierRunningPower "Running Power" "The HealthKit HKQuantityTypeIdentifierRunningPower source type. Grove converts it to grove-mobile-power."
* #HKQuantityTypeIdentifierRunningPower ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningPower ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningpower"
* #HKQuantityTypeIdentifierRunningSpeed "Running Speed" "The HealthKit HKQuantityTypeIdentifierRunningSpeed source type. Grove converts it to grove-mobile-speed."
* #HKQuantityTypeIdentifierRunningSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningspeed"
* #HKQuantityTypeIdentifierRunningStrideLength "Running Stride Length" "The HealthKit HKQuantityTypeIdentifierRunningStrideLength source type. Grove converts it to healthkit-running-stride-length."
* #HKQuantityTypeIdentifierRunningStrideLength ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningStrideLength ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningstridelength"
* #HKQuantityTypeIdentifierRunningVerticalOscillation "Running Vertical Oscillation" "The HealthKit HKQuantityTypeIdentifierRunningVerticalOscillation source type. Grove converts it to healthkit-running-vertical-oscillation."
* #HKQuantityTypeIdentifierRunningVerticalOscillation ^property[0].code = #documentation
* #HKQuantityTypeIdentifierRunningVerticalOscillation ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/runningverticaloscillation"
* #HKQuantityTypeIdentifierSixMinuteWalkTestDistance "6 Minute Walk Test Distance" "The HealthKit HKQuantityTypeIdentifierSixMinuteWalkTestDistance source type. Grove converts it to healthkit-six-minute-walk-test-distance."
* #HKQuantityTypeIdentifierSixMinuteWalkTestDistance ^property[0].code = #documentation
* #HKQuantityTypeIdentifierSixMinuteWalkTestDistance ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/sixminutewalktestdistance"
* #HKQuantityTypeIdentifierStairAscentSpeed "Stair Ascent Speed" "The HealthKit HKQuantityTypeIdentifierStairAscentSpeed source type. Grove converts it to healthkit-stair-ascent-speed."
* #HKQuantityTypeIdentifierStairAscentSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierStairAscentSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/stairascentspeed"
* #HKQuantityTypeIdentifierStairDescentSpeed "Stair Descent Speed" "The HealthKit HKQuantityTypeIdentifierStairDescentSpeed source type. Grove converts it to healthkit-stair-descent-speed."
* #HKQuantityTypeIdentifierStairDescentSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierStairDescentSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/stairdescentspeed"
* #HKQuantityTypeIdentifierStepCount "Step Count" "The HealthKit HKQuantityTypeIdentifierStepCount source type. Grove converts it to grove-mobile-step-count."
* #HKQuantityTypeIdentifierStepCount ^property[0].code = #documentation
* #HKQuantityTypeIdentifierStepCount ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/stepcount"
* #HKQuantityTypeIdentifierSwimmingStrokeCount "Swimming Stroke Count" "The HealthKit HKQuantityTypeIdentifierSwimmingStrokeCount source type. Grove converts it to healthkit-swimming-stroke-count."
* #HKQuantityTypeIdentifierSwimmingStrokeCount ^property[0].code = #documentation
* #HKQuantityTypeIdentifierSwimmingStrokeCount ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/swimmingstrokecount"
* #HKQuantityTypeIdentifierTimeInDaylight "Time in Daylight" "The HealthKit HKQuantityTypeIdentifierTimeInDaylight source type. Grove converts it to healthkit-time-in-daylight."
* #HKQuantityTypeIdentifierTimeInDaylight ^property[0].code = #documentation
* #HKQuantityTypeIdentifierTimeInDaylight ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/timeindaylight"
* #HKQuantityTypeIdentifierUVExposure "UV Exposure" "The HealthKit HKQuantityTypeIdentifierUVExposure source type. Grove converts it to healthkit-uv-exposure."
* #HKQuantityTypeIdentifierUVExposure ^property[0].code = #documentation
* #HKQuantityTypeIdentifierUVExposure ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/uvexposure"
* #HKQuantityTypeIdentifierUnderwaterDepth "Underwater Depth" "The HealthKit HKQuantityTypeIdentifierUnderwaterDepth source type. Grove converts it to healthkit-underwater-depth."
* #HKQuantityTypeIdentifierUnderwaterDepth ^property[0].code = #documentation
* #HKQuantityTypeIdentifierUnderwaterDepth ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/underwaterdepth"
* #HKQuantityTypeIdentifierVO2Max "VO2Max" "The HealthKit HKQuantityTypeIdentifierVO2Max source type. Grove converts it to grove-mobile-vo2-max."
* #HKQuantityTypeIdentifierVO2Max ^property[0].code = #documentation
* #HKQuantityTypeIdentifierVO2Max ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/vo2max"
* #HKQuantityTypeIdentifierWaistCircumference "Waist Circumference" "The HealthKit HKQuantityTypeIdentifierWaistCircumference source type. Grove converts it to healthkit-waist-circumference."
* #HKQuantityTypeIdentifierWaistCircumference ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWaistCircumference ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/waistcircumference"
* #HKQuantityTypeIdentifierWalkingAsymmetryPercentage "Walking Asymmetry Percentage" "The HealthKit HKQuantityTypeIdentifierWalkingAsymmetryPercentage source type. Grove converts it to healthkit-walking-asymmetry."
* #HKQuantityTypeIdentifierWalkingAsymmetryPercentage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingAsymmetryPercentage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingasymmetrypercentage"
* #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage "Walking Double Support Percentage" "The HealthKit HKQuantityTypeIdentifierWalkingDoubleSupportPercentage source type. Grove converts it to healthkit-walking-double-support."
* #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingdoublesupportpercentage"
* #HKQuantityTypeIdentifierWalkingHeartRateAverage "Walking Heart Rate Average" "The HealthKit HKQuantityTypeIdentifierWalkingHeartRateAverage source type. Grove converts it to healthkit-walking-heart-rate-average."
* #HKQuantityTypeIdentifierWalkingHeartRateAverage ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingHeartRateAverage ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingheartrateaverage"
* #HKQuantityTypeIdentifierWalkingSpeed "Walking Speed" "The HealthKit HKQuantityTypeIdentifierWalkingSpeed source type. Grove converts it to healthkit-walking-speed."
* #HKQuantityTypeIdentifierWalkingSpeed ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingSpeed ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingspeed"
* #HKQuantityTypeIdentifierWalkingStepLength "Walking Step Length" "The HealthKit HKQuantityTypeIdentifierWalkingStepLength source type. Grove converts it to healthkit-walking-step-length."
* #HKQuantityTypeIdentifierWalkingStepLength ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWalkingStepLength ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/walkingsteplength"
* #HKQuantityTypeIdentifierWaterTemperature "Water Temperature" "The HealthKit HKQuantityTypeIdentifierWaterTemperature source type. Grove converts it to healthkit-water-temperature."
* #HKQuantityTypeIdentifierWaterTemperature ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWaterTemperature ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/watertemperature"
* #HKQuantityTypeIdentifierWorkoutEffortScore "Workout Effort" "The HealthKit HKQuantityTypeIdentifierWorkoutEffortScore source type. Grove converts it to healthkit-workout-effort-score."
* #HKQuantityTypeIdentifierWorkoutEffortScore ^property[0].code = #documentation
* #HKQuantityTypeIdentifierWorkoutEffortScore ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkquantitytypeidentifier/workouteffortscore"
* #HKScoredAssessmentTypeIdentifierGAD7 "GAD-7" "The HealthKit HKScoredAssessmentTypeIdentifierGAD7 source type. Grove converts it to healthkit-gad7-assessment."
* #HKScoredAssessmentTypeIdentifierGAD7 ^property[0].code = #documentation
* #HKScoredAssessmentTypeIdentifierGAD7 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkscoredassessmenttypeidentifier/gad7"
* #HKScoredAssessmentTypeIdentifierPHQ9 "PHQ-9" "The HealthKit HKScoredAssessmentTypeIdentifierPHQ9 source type. Grove converts it to healthkit-phq9-assessment."
* #HKScoredAssessmentTypeIdentifierPHQ9 ^property[0].code = #documentation
* #HKScoredAssessmentTypeIdentifierPHQ9 ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkscoredassessmenttypeidentifier/phq9"
* #HKVisionPrescriptionTypeIdentifier "Vision Prescription" "The HealthKit HKVisionPrescriptionTypeIdentifier source type. Grove admits no output for it. R4 VisionPrescription represents the structured glasses and contacts prescriptions faithfully, but it requires a prescriber the platform does not supply, and the vertex and pupillary distances need extensions to stay lossless. Deferred pending that design, not because the data is unmodellable."
* #HKVisionPrescriptionTypeIdentifier ^property[0].code = #documentation
* #HKVisionPrescriptionTypeIdentifier ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkvisionprescriptiontypeidentifier"
* #HKWorkoutRouteTypeIdentifier "Workout Route" "The HealthKit HKWorkoutRouteTypeIdentifier source type. Grove admits no output for it. No shared or HealthKit-adapter output contract is published for this sample type."
* #HKWorkoutRouteTypeIdentifier ^property[0].code = #documentation
* #HKWorkoutRouteTypeIdentifier ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkworkoutroutetypeidentifier"
* #HKWorkoutTypeIdentifier "Workout" "The HealthKit HKWorkoutTypeIdentifier source type. Grove converts it to grove-mobile-workout and grove-mobile-workout-segment."
* #HKWorkoutTypeIdentifier ^property[0].code = #documentation
* #HKWorkoutTypeIdentifier ^property[0].valueString = "https://developer.apple.com/documentation/healthkit/hkworkouttypeidentifier"

ValueSet: HealthKitSourceTypeVS
Id: healthkit-source-type
Title: "HealthKit Source Types"
Description: "The complete closed set of HealthKit platform source types in the version 0.3.0 catalog."
* ^experimental = false
* include codes from system HealthKitSourceTypeCS
