//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: healthkit-motion-context-1
Description: "Heart-rate motion context is present only on an Observation coded with LOINC 8867-4."
Expression: "component.where(code.coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-metadata-key' and code = 'HKMetadataKeyHeartRateMotionContext').exists()).empty() or code.coding.where(system = 'http://loinc.org' and code = '8867-4').exists()"
Severity: #error

Invariant: healthkit-object-id-1
Description: "A HealthKit object identifier value is lowercase UUID text in 8-4-4-4-12 hyphenated form."
Expression: "value.matches('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')"
Severity: #error

Invariant: healthkit-sync-version-1
Description: "HealthKit requires a sync version exactly when a sync identifier is present, so the two appear together or not at all. A sync version orders revisions of one logical sample, so it appears only with the sync identifier it versions."
Expression: "extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-sync-version').exists() = identifier.where(system = 'https://grovealliance.org/fhir/healthkit/NamingSystem/healthkit-sync-id').exists()"
Severity: #error

Invariant: healthkit-sleep-stage-1
Description: "A shared sleep-stage output carries exactly one exact HealthKit sleep-analysis source coding, and no other output carries one."
Expression: "(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-sleep-analysis').count() = 1) or (code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').empty() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-sleep-analysis').empty())"
Severity: #error

Invariant: healthkit-ecg-symptom-state-1
Description: "A present symptoms status has at least one caller-supplied correlated symptom; none and not-set have no correlated symptom."
Expression: "(extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-symptoms-status').value.first() = 'present' and extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-correlated-symptom').exists()) or (extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-symptoms-status').value.first() != 'present' and extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-correlated-symptom').empty())"
Severity: #error

Profile: HealthKitObservation
Parent: GroveMobileObservation
Id: healthkit-observation
Title: "HealthKit Observation"
Description: "The source identity and allowlisted HealthKit context for an Observation that also conforms to an appropriate clinical or research profile."
* obeys healthkit-motion-context-1 and healthkit-sleep-stage-1 and healthkit-sync-version-1
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains healthKitObjectId 1..1 MS and healthKitSyncId 0..1 MS
* identifier[healthKitObjectId] obeys healthkit-object-id-1
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value 1..1 MS
* identifier[healthKitSyncId].system = $healthKitSyncId
* identifier[healthKitSyncId].value 1..1 MS
* extension contains HealthKitSyncVersion named syncVersion 0..1 MS
* code.coding ^slicing.discriminator.type = #value
* code.coding ^slicing.discriminator.path = "system"
* code.coding ^slicing.rules = #open
* code.coding contains healthKitSourceType 1..1 MS
* code.coding[healthKitSourceType].system = $healthKitSourceType
* code.coding[healthKitSourceType].code 1..1 MS
* code.coding[healthKitSourceType] from HealthKitSourceTypeVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains heartRateMotionContext 0..1 MS
* component[heartRateMotionContext].code = $healthKitMetadataKey#HKMetadataKeyHeartRateMotionContext
* component[heartRateMotionContext].value[x] 1..1 MS
* component[heartRateMotionContext].value[x] only CodeableConcept
* component[heartRateMotionContext].valueCodeableConcept from HealthKitHeartRateMotionContextVS (required)
* component[heartRateMotionContext].dataAbsentReason 0..0

Profile: HealthKitECGObservation
Parent: HealthKitObservation
Id: healthkit-ecg-observation
Title: "HealthKit ECG Observation"
Description: "A lossless HealthKit ECG adapter result that is directly claimed together with the source-neutral Grove Sensor ECG profile. It retains the exact HealthKit classification, symptom evidence, optional average heart rate and sampling frequency, reported voltage count, and complete Lead-I-like voltage series supplied by the caller; it performs no HealthKit query."
* obeys healthkit-ecg-symptom-state-1
* code.coding[healthKitSourceType] = $healthKitSourceType#HKDataTypeIdentifierElectrocardiogram "ECG"
* extension contains
    HealthKitECGClassification named healthKitECGClassification 1..1 MS and
    HealthKitECGSymptomsStatus named healthKitECGSymptomsStatus 1..1 MS and
    HealthKitECGCorrelatedSymptom named healthKitECGCorrelatedSymptom 0..7 MS and
    HealthKitECGAverageHeartRate named healthKitECGAverageHeartRate 0..1 MS and
    HealthKitECGSamplingFrequency named healthKitECGSamplingFrequency 0..1 MS and
    HealthKitECGVoltageMeasurementCount named healthKitECGVoltageMeasurementCount 1..1 MS and
    HealthKitECGAlgorithmVersion named healthKitECGAlgorithmVersion 0..1 MS and
    HealthKitECGSourcePeriod named healthKitECGSourcePeriod 1..1 MS
* code = $loinc#11524-6 "EKG study"
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* component 1..1 MS
* component contains voltage 1..1 MS
* component[voltage].code = $mdc#131329 "MDC_ECG_ELEC_POTL_I"
* component[voltage].value[x] 1..1 MS
* component[voltage].value[x] only SampledData
* component[voltage].dataAbsentReason 0..0

Profile: HealthKitConversionProvenance
Parent: GroveMobileConversionProvenance
Id: healthkit-conversion-provenance
Title: "HealthKit Conversion Provenance"
Description: "Provenance for transforming one HealthKit object into one or more HealthKit adapter Observations without fetching source data."
* target 1..* MS
* target only Reference(HealthKitObservation)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys healthkit-object-id-1

Profile: HealthKitClinicalRecordDocument
Parent: DocumentReference
Id: healthkit-clinical-record-document
Title: "HealthKit Clinical Record Document"
Description: "A pass-through envelope for one provider-issued clinical FHIR resource surfaced by HealthKit. The payload is byte-preserved in the declared source FHIR release; Grove asserts identity and provenance, never conformance over the issuer's resource."
* identifier 1..* MS
* status MS
* type 1..1 MS
* type from HealthKitClinicalRecordTypeVS (required)
* subject 1..1 MS
* subject only Reference(Patient)
* date 1..1 MS
* content 1..1 MS
* content.format 1..1 MS
* content.format = $recordingFormat#fhir-resource-1 "FHIR Resource 1"
* content.attachment.contentType 1..1 MS
* content.attachment.contentType = #application/fhir+json (exactly)
* content.attachment.title 1..1 MS
* content.attachment.size 1..1 MS
* content.attachment.hash 1..1 MS
* extension contains HealthKitClinicalFHIRRelease named fhirRelease 1..1 MS

Extension: HealthKitClinicalFHIRRelease
Id: healthkit-clinical-fhir-release
Title: "HealthKit Clinical FHIR Release"
Description: "The FHIR release of the pass-through payload, read from HKFHIRVersion.fhirRelease and never inferred."
* ^context[+].type = #element
* ^context[=].expression = "DocumentReference"
* value[x] only code
* valueCode 1..1
* valueCode from HealthKitClinicalFHIRReleaseVS (required)


Extension: HealthKitSyncVersion
Id: healthkit-sync-version
Title: "HealthKit Sync Version"
Description: "The HKMetadataKeySyncVersion of the sample this Observation was converted from. HealthKit replaces a sample when a writer saves a higher version under the same sync identifier, and the replacement carries a new object UUID; the version orders those revisions so a receiver can supersede rather than double-count."
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only string
* valueString 1..1
* valueString obeys healthkit-sync-version-value-1


Invariant: healthkit-sync-version-value-1
Description: "A sync version is a canonical non-negative decimal integer, written without a sign, leading zeros, or separators."
Expression: "$this.matches('^(0|[1-9][0-9]*)$')"
Severity: #error
