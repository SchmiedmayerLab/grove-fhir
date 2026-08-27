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

Extension: HealthKitVisionPrescriptionExpiration
Id: healthkit-vision-prescription-expiration
Title: "HealthKit Vision Prescription Expiration"
Description: "The exact HKVisionPrescription.expirationDate. R4 VisionPrescription states when a prescription was written but never when it lapses."
Context: VisionPrescription
* value[x] 1..1 MS
* value[x] only dateTime

Extension: HealthKitLensVertexDistance
Id: healthkit-lens-vertex-distance
Title: "HealthKit Lens Vertex Distance"
Description: "The exact HKGlassesLensSpecification.vertexDistance, the distance between the back of the lens and the eye."
Context: VisionPrescription.lensSpecification
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mm (exactly)

Extension: HealthKitLensFarPupillaryDistance
Id: healthkit-lens-far-pupillary-distance
Title: "HealthKit Lens Far Pupillary Distance"
Description: "The exact HKGlassesLensSpecification.farPupillaryDistance, measured for this lens while the person looks at a distant object."
Context: VisionPrescription.lensSpecification
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mm (exactly)

Extension: HealthKitLensNearPupillaryDistance
Id: healthkit-lens-near-pupillary-distance
Title: "HealthKit Lens Near Pupillary Distance"
Description: "The exact HKGlassesLensSpecification.nearPupillaryDistance, measured for this lens while the person looks at a nearby object."
Context: VisionPrescription.lensSpecification
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mm (exactly)

Extension: HealthKitMedicationDoseLogStatus
Id: healthkit-medication-dose-log-status
Title: "HealthKit Medication Dose Log Status"
Description: "The exact HKMedicationDoseEvent.LogStatus. Six source cases reach three R4 administration statuses, so the status alone cannot say whether a dose was skipped, snoozed, or never acted on."
Context: MedicationAdministration
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitMedicationDoseLogStatusVS (required)

Extension: HealthKitMedicationDoseSchedule
Id: healthkit-medication-dose-schedule
Title: "HealthKit Medication Dose Schedule"
Description: "The schedule a dose event was logged against: the HKMedicationDoseEvent.ScheduleType, and the scheduled time and amount when the platform supplies them."
Context: MedicationAdministration
* extension contains
    type 1..1 MS and
    expectedDate 0..1 MS and
    expectedQuantity 0..1 MS
* extension[type].value[x] 1..1 MS
* extension[type].value[x] only code
* extension[type].valueCode from HealthKitMedicationScheduleTypeVS (required)
* extension[expectedDate].value[x] 1..1 MS
* extension[expectedDate].value[x] only dateTime
* extension[expectedQuantity].value[x] 1..1 MS
* extension[expectedQuantity].value[x] only Quantity
* extension[expectedQuantity].valueQuantity.value 1..1 MS
* extension[expectedQuantity].valueQuantity.system 1..1 MS
* extension[expectedQuantity].valueQuantity.system = $ucum (exactly)
* extension[expectedQuantity].valueQuantity.code 1..1 MS
* value[x] 0..0

Extension: HealthKitMedicationNickname
Id: healthkit-medication-nickname
Title: "HealthKit Medication Nickname"
Description: "The exact HKUserAnnotatedMedication.nickname the person gave the medication while adding it."
Context: MedicationStatement
* value[x] 1..1 MS
* value[x] only string

Extension: HealthKitMedicationHasSchedule
Id: healthkit-medication-has-schedule
Title: "HealthKit Medication Has Schedule"
Description: "The exact HKUserAnnotatedMedication.hasSchedule flag. It states that a schedule exists, never what the schedule is, so it is not a Dosage."
Context: MedicationStatement
* value[x] 1..1 MS
* value[x] only boolean

Extension: HealthKitMedicationGeneralForm
Id: healthkit-medication-general-form
Title: "HealthKit Medication General Form"
Description: "The exact HKMedicationConcept.generalForm. R4 carries a medication form only on a Medication resource, and HealthKit publishes no medication record to hold one."
Context: MedicationStatement
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitMedicationGeneralFormVS (required)


Extension: HealthKitSourceType
Id: healthkit-source-type-extension
Title: "HealthKit Source Type"
Description: "The exact HealthKit source type this resource was derived from, for resources that carry no classifying element of their own. An Observation states it in `code.coding` and a recording document in `type.coding`; a prescription or a medication record has no such element, and `meta.tag` cannot hold it because a tag may be ignored when interpreting a resource."
Context: VisionPrescription, MedicationAdministration, MedicationStatement
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitSourceTypeVS (required)
