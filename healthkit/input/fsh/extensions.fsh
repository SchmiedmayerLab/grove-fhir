//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: healthkit-ecg-count-positive-1
Description: "A HealthKit ECG voltage-measurement count is greater than zero."
Expression: "$this > 0"
Severity: #error

Extension: HealthKitECGClassification
Id: healthkit-ecg-classification
Title: "HealthKit ECG Classification"
Description: "The exact classification reported by HKElectrocardiogram."
Context: Observation
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitECGClassificationVS (required)

Extension: HealthKitECGSymptomsStatus
Id: healthkit-ecg-symptoms-status
Title: "HealthKit ECG Symptoms Status"
Description: "Whether the participant reported correlated symptoms for the HealthKit ECG."
Context: Observation
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitECGSymptomsStatusVS (required)

Extension: HealthKitECGCorrelatedSymptom
Id: healthkit-ecg-correlated-symptom
Title: "HealthKit ECG Correlated Symptom"
Description: "One exact HealthKit symptom category sample associated with an ECG by the HealthKit API, including the complete HKSourceRevision evidence supplied with that sample."
Context: Observation
* extension contains
    sourceIdentifier 1..1 MS and
    effectivePeriod 1..1 MS and
    symptomType 1..1 MS and
    severity 1..1 MS and
    sourceName 1..1 MS and
    sourceBundleIdentifier 1..1 MS and
    sourceVersion 0..1 MS and
    sourceProductType 0..1 MS and
    sourceOperatingSystemMajorVersion 1..1 MS and
    sourceOperatingSystemMinorVersion 1..1 MS and
    sourceOperatingSystemPatchVersion 1..1 MS
* extension[sourceIdentifier].value[x] 1..1 MS
* extension[sourceIdentifier].value[x] only Identifier
* extension[sourceIdentifier].valueIdentifier.system 1..1 MS
* extension[sourceIdentifier].valueIdentifier.system = $healthKitObjectId (exactly)
* extension[sourceIdentifier].valueIdentifier.value 1..1 MS
* extension[sourceIdentifier].valueIdentifier.value obeys healthkit-object-id-1
* extension[effectivePeriod].value[x] 1..1 MS
* extension[effectivePeriod].value[x] only Period
* extension[effectivePeriod].valuePeriod.start 1..1 MS
* extension[effectivePeriod].valuePeriod.end 1..1 MS
* extension[symptomType].value[x] 1..1 MS
* extension[symptomType].value[x] only code
* extension[symptomType].valueCode from HealthKitECGCorrelatedSymptomTypeVS (required)
* extension[severity].value[x] 1..1 MS
* extension[severity].value[x] only code
* extension[severity].valueCode from HealthKitSymptomSeverityVS (required)
* extension[sourceName].value[x] 1..1 MS
* extension[sourceName].value[x] only string
* extension[sourceBundleIdentifier].value[x] 1..1 MS
* extension[sourceBundleIdentifier].value[x] only string
* extension[sourceVersion].value[x] 1..1 MS
* extension[sourceVersion].value[x] only string
* extension[sourceProductType].value[x] 1..1 MS
* extension[sourceProductType].value[x] only string
* extension[sourceOperatingSystemMajorVersion].value[x] 1..1 MS
* extension[sourceOperatingSystemMajorVersion].value[x] only integer
* extension[sourceOperatingSystemMinorVersion].value[x] 1..1 MS
* extension[sourceOperatingSystemMinorVersion].value[x] only integer
* extension[sourceOperatingSystemPatchVersion].value[x] 1..1 MS
* extension[sourceOperatingSystemPatchVersion].value[x] only integer
* value[x] 0..0

Extension: HealthKitECGAverageHeartRate
Id: healthkit-ecg-average-heart-rate
Title: "HealthKit ECG Average Heart Rate"
Description: "The optional average heart rate reported by HKElectrocardiogram, retained separately from the voltage waveform."
Context: Observation
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Extension: HealthKitECGSamplingFrequency
Id: healthkit-ecg-sampling-frequency
Title: "HealthKit ECG Sampling Frequency"
Description: "The optional sampling frequency reported by HKElectrocardiogram, retained exactly and required to agree with SampledData.period when present."
Context: Observation
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #Hz (exactly)

Extension: HealthKitECGVoltageMeasurementCount
Id: healthkit-ecg-voltage-measurement-count
Title: "HealthKit ECG Voltage Measurement Count"
Description: "The exact numberOfVoltageMeasurements reported by HKElectrocardiogram."
Context: Observation
* value[x] 1..1 MS
* value[x] only integer
* valueInteger obeys healthkit-ecg-count-positive-1

Extension: HealthKitECGAlgorithmVersion
Id: healthkit-ecg-algorithm-version
Title: "HealthKit ECG Algorithm Version"
Description: "The exact HKAppleECGAlgorithmVersion supplied by HKMetadataKeyAppleECGAlgorithmVersion when that metadata key is present."
Context: Observation
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitECGAlgorithmVersionVS (required)

Extension: HealthKitECGSourcePeriod
Id: healthkit-ecg-source-period
Title: "HealthKit ECG Source Period"
Description: "The exact HKElectrocardiogram.startDate and endDate. Observation.effectivePeriod instead spans the first through last supplied voltage measurement, so the two intervals are never silently conflated."
Context: Observation
* value[x] 1..1 MS
* value[x] only Period
* valuePeriod.start 1..1 MS
* valuePeriod.end 1..1 MS
