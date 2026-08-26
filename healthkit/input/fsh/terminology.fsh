//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: HealthKitMetadataKeyCS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "HealthKit metadata keys retained by Grove FHIR HealthKit 0.3.0 after standard FHIR mappings have been applied."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #HKMetadataKeyHeartRateMotionContext "Heart Rate Motion Context" "The HealthKit metadata key whose NSNumber value is mapped to a bounded motion-context code."
* #HKMetadataKeyAppleECGAlgorithmVersion "Apple ECG Algorithm Version" "The HealthKit metadata key whose NSNumber value identifies the Apple ECG classification algorithm version."
* #HKMetadataKeySyncIdentifier "Sync Identifier" "The HealthKit metadata key whose value is the writer-assigned logical identity of a sample, stable across the replacements HealthKit performs when a higher sync version is saved."
* #HKMetadataKeySyncVersion "Sync Version" "The HealthKit metadata key whose NSNumber value orders revisions of one sync identifier; HealthKit keeps the higher version and discards the lower."

ValueSet: HealthKitMetadataKeyVS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "The HealthKit 0.3.0 allowlist of retained metadata keys. Each key maps to its published representation: a named Observation component, a named extension, or a named identifier slice."
* ^experimental = false
* include codes from system HealthKitMetadataKeyCS

CodeSystem: HealthKitHeartRateMotionContextCS
Id: healthkit-heart-rate-motion-context
Title: "HealthKit Heart Rate Motion Context"
Description: "Adapter codes for the HKHeartRateMotionContext raw values retained by Grove FHIR HealthKit 0.3.0. The mapping to HealthKit source cases is documented separately."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #not-set "Not Set" "The adapter code for HealthKit raw NSNumber value 0."
* #sedentary "Sedentary" "The adapter code for HealthKit raw NSNumber value 1."
* #active "Active" "The adapter code for HealthKit raw NSNumber value 2."

ValueSet: HealthKitHeartRateMotionContextVS
Id: healthkit-heart-rate-motion-context
Title: "HealthKit Heart Rate Motion Context"
Description: "Motion contexts permitted by the HealthKit 0.3.0 heart-rate metadata mapping."
* ^experimental = false
* include codes from system HealthKitHeartRateMotionContextCS

CodeSystem: HealthKitSleepAnalysisCS
Id: healthkit-sleep-analysis
Title: "HealthKit Sleep Analysis"
Description: "Exact HealthKit HKCategoryValueSleepAnalysis cases retained alongside the source-neutral Grove sleep-stage coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #inBed "In bed" "HealthKit HKCategoryValueSleepAnalysis.inBed."
* #asleepUnspecified "Asleep, unspecified" "HealthKit HKCategoryValueSleepAnalysis.asleepUnspecified."
* #awake "Awake" "HealthKit HKCategoryValueSleepAnalysis.awake."
* #asleepCore "Asleep, core" "HealthKit HKCategoryValueSleepAnalysis.asleepCore."
* #asleepDeep "Asleep, deep" "HealthKit HKCategoryValueSleepAnalysis.asleepDeep."
* #asleepREM "Asleep, REM" "HealthKit HKCategoryValueSleepAnalysis.asleepREM."

ValueSet: HealthKitSleepAnalysisVS
Id: healthkit-sleep-analysis
Title: "HealthKit Sleep Analysis"
Description: "HealthKit sleep-analysis source cases admitted as the second coding of a shared sleep-stage result."
* ^experimental = false
* include codes from system HealthKitSleepAnalysisCS

CodeSystem: HealthKitECGClassificationCS
Id: healthkit-ecg-classification
Title: "HealthKit ECG Classification"
Description: "Exact HKElectrocardiogram.Classification cases retained on a lossless HealthKit ECG adapter result."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #notSet "Not set" "HealthKit stated no classification for the recording."
* #sinusRhythm "Sinus rhythm" "The algorithm classified the recording as sinus rhythm."
* #atrialFibrillation "Atrial fibrillation" "The algorithm classified the recording as atrial fibrillation."
* #inconclusiveLowHeartRate "Inconclusive: low heart rate" "No classification was reached because the heart rate was below the algorithm's supported range."
* #inconclusiveHighHeartRate "Inconclusive: high heart rate" "No classification was reached because the heart rate was above the algorithm's supported range."
* #inconclusivePoorReading "Inconclusive: poor reading" "No classification was reached because the recording quality was insufficient."
* #inconclusiveOther "Inconclusive: other" "No classification was reached for a reason HealthKit does not enumerate."
* #unrecognized "Unrecognized" "The recording carries a classification this catalog baseline does not define."

ValueSet: HealthKitECGClassificationVS
Id: healthkit-ecg-classification
Title: "HealthKit ECG Classification"
Description: "The closed HealthKit ECG classification cases admitted by version 0.5.0."
* ^experimental = false
* include codes from system HealthKitECGClassificationCS

CodeSystem: HealthKitECGSymptomsStatusCS
Id: healthkit-ecg-symptoms-status
Title: "HealthKit ECG Symptoms Status"
Description: "Exact HKElectrocardiogram.SymptomsStatus cases retained on a lossless HealthKit ECG adapter result."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #notSet "Not set" "HealthKit stated no symptom status for the recording."
* #none "None" "The wearer reported no symptoms during the recording."
* #present "Present" "The wearer reported one or more symptoms during the recording."

ValueSet: HealthKitECGSymptomsStatusVS
Id: healthkit-ecg-symptoms-status
Title: "HealthKit ECG Symptoms Status"
Description: "The closed HealthKit ECG symptoms-status cases admitted by version 0.5.0."
* ^experimental = false
* include codes from system HealthKitECGSymptomsStatusCS

CodeSystem: HealthKitSymptomSeverityCS
Id: healthkit-symptom-severity
Title: "HealthKit Symptom Severity"
Description: "Exact HKCategoryValueSeverity cases retained for a correlated HealthKit ECG symptom."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #unspecified "Unspecified" "The symptom was logged without a severity grade."
* #notPresent "Not present" "The symptom was assessed and reported as not present."
* #mild "Mild" "The symptom was reported as mild."
* #moderate "Moderate" "The symptom was reported as moderate."
* #severe "Severe" "The symptom was reported as severe."

ValueSet: HealthKitSymptomSeverityVS
Id: healthkit-symptom-severity
Title: "HealthKit Symptom Severity"
Description: "The closed HealthKit symptom severity cases admitted by version 0.5.0."
* ^experimental = false
* include codes from system HealthKitSymptomSeverityCS

ValueSet: HealthKitECGCorrelatedSymptomTypeVS
Id: healthkit-ecg-correlated-symptom-type
Title: "HealthKit ECG Correlated Symptom Type"
Description: "The seven HealthKit category types that the HealthKit API associates with an ECG."
* ^experimental = false
* $healthKitSourceType#HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat
* $healthKitSourceType#HKCategoryTypeIdentifierSkippedHeartbeat
* $healthKitSourceType#HKCategoryTypeIdentifierFatigue
* $healthKitSourceType#HKCategoryTypeIdentifierShortnessOfBreath
* $healthKitSourceType#HKCategoryTypeIdentifierChestTightnessOrPain
* $healthKitSourceType#HKCategoryTypeIdentifierFainting
* $healthKitSourceType#HKCategoryTypeIdentifierDizziness

CodeSystem: HealthKitECGAlgorithmVersionCS
Id: healthkit-ecg-algorithm-version
Title: "HealthKit ECG Algorithm Version"
Description: "Exact HKAppleECGAlgorithmVersion cases retained when the HealthKit ECG metadata key is present."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #version1 "Version 1" "The first-generation Apple electrocardiogram classification algorithm."
* #version2 "Version 2" "The second-generation Apple electrocardiogram classification algorithm."

ValueSet: HealthKitECGAlgorithmVersionVS
Id: healthkit-ecg-algorithm-version
Title: "HealthKit ECG Algorithm Version"
Description: "The closed Apple ECG algorithm versions admitted by version 0.5.0."
* ^experimental = false
* include codes from system HealthKitECGAlgorithmVersionCS

CodeSystem: GroveSymptomSeverityCS
Id: grove-symptom-severity
Title: "Grove Symptom Severity"
Description: "The normalized ordinal severity a user-logged HealthKit symptom Observation reports; the exact HealthKit category value is retained as a secondary coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #not-present "Not present" "The symptom was assessed and reported as not present."
* #present "Present, severity unspecified" "The symptom was reported present without a severity grade."
* #mild "Mild" "The symptom was reported as mild."
* #moderate "Moderate" "The symptom was reported as moderate."
* #severe "Severe" "The symptom was reported as severe."

ValueSet: GroveSymptomSeverityVS
Id: grove-symptom-severity
Title: "Grove Symptom Severity"
Description: "Every normalized severity a graded HealthKit symptom Observation may report."
* ^experimental = false
* include codes from system GroveSymptomSeverityCS

ValueSet: GroveSymptomPresenceVS
Id: grove-symptom-presence
Title: "Grove Symptom Presence"
Description: "The presence subset for HealthKit symptom types that report presence without a severity grade."
* ^experimental = false
* GroveSymptomSeverityCS#not-present
* GroveSymptomSeverityCS#present


CodeSystem: HealthKitClinicalRecordTypeCS
Id: healthkit-clinical-record-type
Title: "HealthKit Clinical Record Type"
Description: "The nine HKClinicalTypeIdentifier record classes a pass-through clinical document may carry; the corresponding LOINC document/section code is stated per concept."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #allergy-record "Allergy record" "The HealthKit allergy record class; the corresponding LOINC document code is 48765-2."
* #condition-record "Condition record" "The HealthKit condition record class; the corresponding LOINC document code is 11450-4."
* #coverage-record "Coverage record" "The HealthKit coverage record class; the corresponding LOINC document code is 48768-6."
* #immunization-record "Immunization record" "The HealthKit immunization record class; the corresponding LOINC document code is 11369-6."
* #lab-result-record "Laboratory result record" "The HealthKit laboratory result record class; the corresponding LOINC document code is 11502-2."
* #medication-record "Medication record" "The HealthKit medication record class; the corresponding LOINC document code is 10160-0."
* #procedure-record "Procedure record" "The HealthKit procedure record class; the corresponding LOINC document code is 47519-4."
* #vital-sign-record "Vital sign record" "The HealthKit vital sign record class; the corresponding LOINC document code is 8716-3."
* #clinical-note-record "Clinical note record" "The HealthKit clinical note record class; the corresponding LOINC document code is 34109-9."

ValueSet: HealthKitClinicalRecordTypeVS
Id: healthkit-clinical-record-type
Title: "HealthKit Clinical Record Type"
Description: "Every admitted pass-through clinical record class."
* ^experimental = false
* include codes from system HealthKitClinicalRecordTypeCS

CodeSystem: HealthKitClinicalFHIRReleaseCS
Id: healthkit-clinical-fhir-release
Title: "HealthKit Clinical FHIR Release"
Description: "The FHIR releases HealthKit surfaces for provider-issued clinical resources (HKFHIRRelease)."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #dstu2 "DSTU2" "The payload is FHIR DSTU2."
* #r4 "R4" "The payload is FHIR R4."

ValueSet: HealthKitClinicalFHIRReleaseVS
Id: healthkit-clinical-fhir-release
Title: "HealthKit Clinical FHIR Release"
Description: "Every admitted pass-through payload FHIR release; HKFHIRRelease.unknown fails closed and is never emitted."
* ^experimental = false
* include codes from system HealthKitClinicalFHIRReleaseCS

CodeSystem: HealthKitPresenceCS
Id: healthkit-presence
Title: "HealthKit Presence"
Description: "Exact HealthKit HKCategoryValuePresence cases retained alongside the source-neutral Grove presence coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #present "Present" "HealthKit HKCategoryValuePresence.present."
* #notPresent "Not present" "HealthKit HKCategoryValuePresence.notPresent."

CodeSystem: HealthKitAppetiteChangesCS
Id: healthkit-appetite-changes
Title: "HealthKit Appetite Changes"
Description: "Exact HealthKit HKCategoryValueAppetiteChanges cases retained alongside the source-neutral Grove appetite coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #unspecified "Unspecified" "HealthKit HKCategoryValueAppetiteChanges.unspecified."
* #noChange "No change" "HealthKit HKCategoryValueAppetiteChanges.noChange."
* #decreased "Decreased" "HealthKit HKCategoryValueAppetiteChanges.decreased."
* #increased "Increased" "HealthKit HKCategoryValueAppetiteChanges.increased."

CodeSystem: HealthKitAppleStandHourCS
Id: healthkit-apple-stand-hour-value
Title: "HealthKit Apple Stand Hour"
Description: "Exact HealthKit HKCategoryValueAppleStandHour cases retained alongside the source-neutral Grove stand-hour coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #stood "Stood" "HealthKit HKCategoryValueAppleStandHour.stood."
* #idle "Idle" "HealthKit HKCategoryValueAppleStandHour.idle."

CodeSystem: HealthKitCervicalMucusQualityCS
Id: healthkit-cervical-mucus-quality
Title: "HealthKit Cervical Mucus Quality"
Description: "Exact HealthKit HKCategoryValueCervicalMucusQuality cases retained alongside the source-neutral Grove cervical-mucus coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #dry "Dry" "HealthKit HKCategoryValueCervicalMucusQuality.dry."
* #sticky "Sticky" "HealthKit HKCategoryValueCervicalMucusQuality.sticky."
* #creamy "Creamy" "HealthKit HKCategoryValueCervicalMucusQuality.creamy."
* #watery "Watery" "HealthKit HKCategoryValueCervicalMucusQuality.watery."
* #eggWhite "Egg white" "HealthKit HKCategoryValueCervicalMucusQuality.eggWhite."

CodeSystem: HealthKitContraceptiveCS
Id: healthkit-contraceptive
Title: "HealthKit Contraceptive"
Description: "Exact HealthKit HKCategoryValueContraceptive cases retained alongside the source-neutral Grove contraceptive coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #unspecified "Unspecified" "HealthKit HKCategoryValueContraceptive.unspecified."
* #implant "Implant" "HealthKit HKCategoryValueContraceptive.implant."
* #injection "Injection" "HealthKit HKCategoryValueContraceptive.injection."
* #intrauterineDevice "Intrauterine device" "HealthKit HKCategoryValueContraceptive.intrauterineDevice."
* #intravaginalRing "Intravaginal ring" "HealthKit HKCategoryValueContraceptive.intravaginalRing."
* #oral "Oral" "HealthKit HKCategoryValueContraceptive.oral."
* #patch "Patch" "HealthKit HKCategoryValueContraceptive.patch."

CodeSystem: HealthKitOvulationTestResultCS
Id: healthkit-ovulation-test-result
Title: "HealthKit Ovulation Test Result"
Description: "Exact HealthKit HKCategoryValueOvulationTestResult cases retained alongside the source-neutral Grove ovulation-result coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #negative "Negative" "HealthKit HKCategoryValueOvulationTestResult.negative."
* #luteinizingHormoneSurge "Luteinizing hormone surge" "HealthKit HKCategoryValueOvulationTestResult.luteinizingHormoneSurge."
* #indeterminate "Indeterminate" "HealthKit HKCategoryValueOvulationTestResult.indeterminate."
* #estrogenSurge "Estrogen surge" "HealthKit HKCategoryValueOvulationTestResult.estrogenSurge."

CodeSystem: HealthKitTestResultCS
Id: healthkit-test-result
Title: "HealthKit Test Result"
Description: "Exact HealthKit pregnancy and progesterone test-result cases retained alongside the source-neutral Grove result coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #positive "Positive" "HealthKit HKCategoryValuePregnancyTestResult.positive or HKCategoryValueProgesteroneTestResult.positive."
* #negative "Negative" "HealthKit HKCategoryValuePregnancyTestResult.negative or HKCategoryValueProgesteroneTestResult.negative."
* #indeterminate "Indeterminate" "HealthKit HKCategoryValuePregnancyTestResult.indeterminate or HKCategoryValueProgesteroneTestResult.indeterminate."

CodeSystem: HealthKitVaginalBleedingCS
Id: healthkit-vaginal-bleeding
Title: "HealthKit Vaginal Bleeding"
Description: "Exact HealthKit HKCategoryValueVaginalBleeding cases retained alongside the source-neutral Grove flow coding; the retired HKCategoryValueMenstrualFlow shares this case set."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #unspecified "Unspecified" "HealthKit HKCategoryValueVaginalBleeding.unspecified."
* #light "Light" "HealthKit HKCategoryValueVaginalBleeding.light."
* #medium "Medium" "HealthKit HKCategoryValueVaginalBleeding.medium."
* #heavy "Heavy" "HealthKit HKCategoryValueVaginalBleeding.heavy."
* #none "None" "HealthKit HKCategoryValueVaginalBleeding.none."

CodeSystem: HealthKitInsulinDeliveryReasonCS
Id: healthkit-insulin-delivery-reason
Title: "HealthKit Insulin Delivery Reason"
Description: "Exact HealthKit HKInsulinDeliveryReason cases carried as the required reason component of an insulin-delivery Observation."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #basal "Basal" "HealthKit HKInsulinDeliveryReason.basal."
* #bolus "Bolus" "HealthKit HKInsulinDeliveryReason.bolus."

CodeSystem: HealthKitWorkoutActivityCS
Id: healthkit-workout-activity
Title: "HealthKit Workout Activity"
Description: "Exact HealthKit HKWorkoutActivityType cases retained alongside the source-neutral Grove workout-activity coding. The shared vocabulary collapses related activities; this preserves which one the platform reported."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #americanFootball "American football" "HealthKit HKWorkoutActivityType.americanFootball."
* #archery "Archery" "HealthKit HKWorkoutActivityType.archery."
* #australianFootball "Australian football" "HealthKit HKWorkoutActivityType.australianFootball."
* #badminton "Badminton" "HealthKit HKWorkoutActivityType.badminton."
* #barre "Barre" "HealthKit HKWorkoutActivityType.barre."
* #baseball "Baseball" "HealthKit HKWorkoutActivityType.baseball."
* #basketball "Basketball" "HealthKit HKWorkoutActivityType.basketball."
* #bowling "Bowling" "HealthKit HKWorkoutActivityType.bowling."
* #boxing "Boxing" "HealthKit HKWorkoutActivityType.boxing."
* #cardioDance "Cardio dance" "HealthKit HKWorkoutActivityType.cardioDance."
* #climbing "Climbing" "HealthKit HKWorkoutActivityType.climbing."
* #cooldown "Cooldown" "HealthKit HKWorkoutActivityType.cooldown."
* #coreTraining "Core training" "HealthKit HKWorkoutActivityType.coreTraining."
* #cricket "Cricket" "HealthKit HKWorkoutActivityType.cricket."
* #crossCountrySkiing "Cross country skiing" "HealthKit HKWorkoutActivityType.crossCountrySkiing."
* #crossTraining "Cross training" "HealthKit HKWorkoutActivityType.crossTraining."
* #curling "Curling" "HealthKit HKWorkoutActivityType.curling."
* #cycling "Cycling" "HealthKit HKWorkoutActivityType.cycling."
* #dance "Dance" "HealthKit HKWorkoutActivityType.dance."
* #danceInspiredTraining "Dance inspired training" "HealthKit HKWorkoutActivityType.danceInspiredTraining."
* #discSports "Disc sports" "HealthKit HKWorkoutActivityType.discSports."
* #downhillSkiing "Downhill skiing" "HealthKit HKWorkoutActivityType.downhillSkiing."
* #elliptical "Elliptical" "HealthKit HKWorkoutActivityType.elliptical."
* #equestrianSports "Equestrian sports" "HealthKit HKWorkoutActivityType.equestrianSports."
* #fencing "Fencing" "HealthKit HKWorkoutActivityType.fencing."
* #fishing "Fishing" "HealthKit HKWorkoutActivityType.fishing."
* #fitnessGaming "Fitness gaming" "HealthKit HKWorkoutActivityType.fitnessGaming."
* #flexibility "Flexibility" "HealthKit HKWorkoutActivityType.flexibility."
* #functionalStrengthTraining "Functional strength training" "HealthKit HKWorkoutActivityType.functionalStrengthTraining."
* #golf "Golf" "HealthKit HKWorkoutActivityType.golf."
* #gymnastics "Gymnastics" "HealthKit HKWorkoutActivityType.gymnastics."
* #handCycling "Hand cycling" "HealthKit HKWorkoutActivityType.handCycling."
* #handball "Handball" "HealthKit HKWorkoutActivityType.handball."
* #highIntensityIntervalTraining "High intensity interval training" "HealthKit HKWorkoutActivityType.highIntensityIntervalTraining."
* #hiking "Hiking" "HealthKit HKWorkoutActivityType.hiking."
* #hockey "Hockey" "HealthKit HKWorkoutActivityType.hockey."
* #hunting "Hunting" "HealthKit HKWorkoutActivityType.hunting."
* #jumpRope "Jump rope" "HealthKit HKWorkoutActivityType.jumpRope."
* #kickboxing "Kickboxing" "HealthKit HKWorkoutActivityType.kickboxing."
* #lacrosse "Lacrosse" "HealthKit HKWorkoutActivityType.lacrosse."
* #martialArts "Martial arts" "HealthKit HKWorkoutActivityType.martialArts."
* #mindAndBody "Mind and body" "HealthKit HKWorkoutActivityType.mindAndBody."
* #mixedCardio "Mixed cardio" "HealthKit HKWorkoutActivityType.mixedCardio."
* #mixedMetabolicCardioTraining "Mixed metabolic cardio training" "HealthKit HKWorkoutActivityType.mixedMetabolicCardioTraining."
* #other "Other" "HealthKit HKWorkoutActivityType.other."
* #paddleSports "Paddle sports" "HealthKit HKWorkoutActivityType.paddleSports."
* #pickleball "Pickleball" "HealthKit HKWorkoutActivityType.pickleball."
* #pilates "Pilates" "HealthKit HKWorkoutActivityType.pilates."
* #play "Play" "HealthKit HKWorkoutActivityType.play."
* #preparationAndRecovery "Preparation and recovery" "HealthKit HKWorkoutActivityType.preparationAndRecovery."
* #racquetball "Racquetball" "HealthKit HKWorkoutActivityType.racquetball."
* #rowing "Rowing" "HealthKit HKWorkoutActivityType.rowing."
* #rugby "Rugby" "HealthKit HKWorkoutActivityType.rugby."
* #running "Running" "HealthKit HKWorkoutActivityType.running."
* #sailing "Sailing" "HealthKit HKWorkoutActivityType.sailing."
* #skatingSports "Skating sports" "HealthKit HKWorkoutActivityType.skatingSports."
* #snowboarding "Snowboarding" "HealthKit HKWorkoutActivityType.snowboarding."
* #snowSports "Snow sports" "HealthKit HKWorkoutActivityType.snowSports."
* #soccer "Soccer" "HealthKit HKWorkoutActivityType.soccer."
* #socialDance "Social dance" "HealthKit HKWorkoutActivityType.socialDance."
* #softball "Softball" "HealthKit HKWorkoutActivityType.softball."
* #squash "Squash" "HealthKit HKWorkoutActivityType.squash."
* #stairClimbing "Stair climbing" "HealthKit HKWorkoutActivityType.stairClimbing."
* #stairs "Stairs" "HealthKit HKWorkoutActivityType.stairs."
* #stepTraining "Step training" "HealthKit HKWorkoutActivityType.stepTraining."
* #surfingSports "Surfing sports" "HealthKit HKWorkoutActivityType.surfingSports."
* #swimBikeRun "Swim bike run" "HealthKit HKWorkoutActivityType.swimBikeRun."
* #swimming "Swimming" "HealthKit HKWorkoutActivityType.swimming."
* #tableTennis "Table tennis" "HealthKit HKWorkoutActivityType.tableTennis."
* #taiChi "Tai chi" "HealthKit HKWorkoutActivityType.taiChi."
* #tennis "Tennis" "HealthKit HKWorkoutActivityType.tennis."
* #trackAndField "Track and field" "HealthKit HKWorkoutActivityType.trackAndField."
* #traditionalStrengthTraining "Traditional strength training" "HealthKit HKWorkoutActivityType.traditionalStrengthTraining."
* #transition "Transition" "HealthKit HKWorkoutActivityType.transition."
* #underwaterDiving "Underwater diving" "HealthKit HKWorkoutActivityType.underwaterDiving."
* #volleyball "Volleyball" "HealthKit HKWorkoutActivityType.volleyball."
* #walking "Walking" "HealthKit HKWorkoutActivityType.walking."
* #waterFitness "Water fitness" "HealthKit HKWorkoutActivityType.waterFitness."
* #waterPolo "Water polo" "HealthKit HKWorkoutActivityType.waterPolo."
* #waterSports "Water sports" "HealthKit HKWorkoutActivityType.waterSports."
* #wheelchairRunPace "Wheelchair run pace" "HealthKit HKWorkoutActivityType.wheelchairRunPace."
* #wheelchairWalkPace "Wheelchair walk pace" "HealthKit HKWorkoutActivityType.wheelchairWalkPace."
* #wrestling "Wrestling" "HealthKit HKWorkoutActivityType.wrestling."
* #yoga "Yoga" "HealthKit HKWorkoutActivityType.yoga."
