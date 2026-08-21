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
Description: "HealthKit metadata keys retained by Grove FHIR HealthKit 0.2.0 after standard FHIR mappings have been applied."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #HKMetadataKeyHeartRateMotionContext "Heart Rate Motion Context" "The HealthKit metadata key whose NSNumber value is mapped to a bounded motion-context code."
* #HKMetadataKeyAppleECGAlgorithmVersion "Apple ECG Algorithm Version" "The HealthKit metadata key whose NSNumber value identifies the Apple ECG classification algorithm version."

ValueSet: HealthKitMetadataKeyVS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "The HealthKit 0.2.0 allowlist of retained metadata keys. Each key maps to its published representation: a named Observation component or a named extension."
* ^experimental = false
* include codes from system HealthKitMetadataKeyCS

CodeSystem: HealthKitHeartRateMotionContextCS
Id: healthkit-heart-rate-motion-context
Title: "HealthKit Heart Rate Motion Context"
Description: "Adapter codes for the HKHeartRateMotionContext raw values retained by Grove FHIR HealthKit 0.2.0. The mapping to HealthKit source cases is documented separately."
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
Description: "Motion contexts permitted by the HealthKit 0.2.0 heart-rate metadata mapping."
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
* #notSet "Not set"
* #sinusRhythm "Sinus rhythm"
* #atrialFibrillation "Atrial fibrillation"
* #inconclusiveLowHeartRate "Inconclusive: low heart rate"
* #inconclusiveHighHeartRate "Inconclusive: high heart rate"
* #inconclusivePoorReading "Inconclusive: poor reading"
* #inconclusiveOther "Inconclusive: other"
* #unrecognized "Unrecognized"

ValueSet: HealthKitECGClassificationVS
Id: healthkit-ecg-classification
Title: "HealthKit ECG Classification"
Description: "The closed HealthKit ECG classification cases admitted by version 0.2.0."
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
* #notSet "Not set"
* #none "None"
* #present "Present"

ValueSet: HealthKitECGSymptomsStatusVS
Id: healthkit-ecg-symptoms-status
Title: "HealthKit ECG Symptoms Status"
Description: "The closed HealthKit ECG symptoms-status cases admitted by version 0.2.0."
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
* #unspecified "Unspecified"
* #notPresent "Not present"
* #mild "Mild"
* #moderate "Moderate"
* #severe "Severe"

ValueSet: HealthKitSymptomSeverityVS
Id: healthkit-symptom-severity
Title: "HealthKit Symptom Severity"
Description: "The closed HealthKit symptom severity cases admitted by version 0.2.0."
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
* #version1 "Version 1"
* #version2 "Version 2"

ValueSet: HealthKitECGAlgorithmVersionVS
Id: healthkit-ecg-algorithm-version
Title: "HealthKit ECG Algorithm Version"
Description: "The closed Apple ECG algorithm versions admitted by version 0.2.0."
* ^experimental = false
* include codes from system HealthKitECGAlgorithmVersionCS
