//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: HealthKitECGSymptomsStatus
Id: healthkit-ecg-symptoms-status
Title: "HealthKit ECG Symptoms Status"
Description: "Whether the participant reported correlated symptoms for the HealthKit ECG."
Context: Observation
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitECGSymptomsStatusVS (required)

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
Description: "The exact HealthKit SDK source type from which this resource was derived. This is lineage, not an alternative coding of the clinical result or document type, so it is kept separate from Observation.code and DocumentReference.type."
Context: Observation, DocumentReference, VisionPrescription, MedicationAdministration, MedicationStatement
* value[x] 1..1 MS
* value[x] only code
* valueCode from HealthKitSourceTypeVS (required)
