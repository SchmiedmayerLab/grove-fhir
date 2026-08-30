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

Invariant: healthkit-opaque-identifier-value-1
Description: "A HealthKit source, output, or writer identifier is a canonical deployment-scoped Grove v0 HMAC value."
Expression: "$this.matches('^v0:[A-Za-z0-9._-]+:[1-9][0-9]*:[A-Za-z0-9_-]{43}$')"
Severity: #error

Invariant: healthkit-writer-record-1
Description: "HealthKit requires a sync version exactly when a sync identifier is present, so the two appear together or not at all. A sync version orders revisions of one logical sample, so it appears only with the sync identifier it versions."
Expression: "extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-writer-record-version').exists() = identifier.where(type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'writer-record').exists()).exists()"
Severity: #error

Invariant: healthkit-clinical-fhir-content-type-1
Description: "The clinical attachment declares DSTU2 or R4 with the standard FHIR media-type parameter."
Expression: "content.attachment.contentType.all($this = 'application/fhir+json; fhirVersion=1.0' or $this = 'application/fhir+json; fhirVersion=4.0')"
Severity: #error

RuleSet: HealthKitOutputIdentitySlices
* obeys healthkit-writer-record-1
* identifier 2..* MS
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #open
* identifier contains sourceRecord 1..1 MS and sourceOutput 1..1 MS and writerRecord 0..1 MS
* identifier[sourceRecord].type = $groveIdentifierRole#source-record
* identifier[sourceRecord].system 1..1 MS
* identifier[sourceRecord].value 1..1 MS
* identifier[sourceRecord].value obeys healthkit-opaque-identifier-value-1
* identifier[sourceOutput].type = $groveIdentifierRole#source-output
* identifier[sourceOutput].system 1..1 MS
* identifier[sourceOutput].value 1..1 MS
* identifier[sourceOutput].value obeys healthkit-opaque-identifier-value-1
* identifier[writerRecord].type = $groveIdentifierRole#writer-record
* identifier[writerRecord].system 1..1 MS
* identifier[writerRecord].value 1..1 MS
* identifier[writerRecord].value obeys healthkit-opaque-identifier-value-1

Invariant: healthkit-sleep-stage-1
Description: "A shared sleep-stage output carries exactly one exact HealthKit sleep-analysis source coding, and no other output carries one."
Expression: "(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-sleep-analysis').count() = 1) or (code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').empty() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-sleep-analysis').empty())"
Severity: #error

Invariant: healthkit-ecg-symptom-state-1
Description: "A present symptoms status has at least one separately identified symptom Observation member; none and not-set have no member."
Expression: "(extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-symptoms-status').value.first() = 'present' and hasMember.exists()) or (extension('https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-ecg-symptoms-status').value.first() != 'present' and hasMember.empty())"
Severity: #error

Invariant: healthkit-medication-concept-identity-1
Description: "A tracked medication has exactly one deployment-scoped opaque source-context identity in addition to its source and output identities."
Expression: "identifier.where(type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-context').exists()).count() = 1"
Severity: #error

Profile: HealthKitApplicationDevice
Parent: GroveApplicationDevice
Id: healthkit-application-device
Title: "HealthKit Application Device"
Description: "An immutable Grove application snapshot with exactly one typed Apple bundle identifier for either the converting application or a producer-classified HKSourceRevision application. The bundle identifier names an application product, never an installation or host."
* identifier contains appleBundleId 1..1 MS
* identifier[appleBundleId].type 1..1 MS
* identifier[appleBundleId].type = $healthKitIdentifierType#apple-bundle-id
* identifier[appleBundleId].system 1..1 MS
* identifier[appleBundleId].system = $appleBundleId (exactly)
* identifier[appleBundleId].value 1..1 MS

Profile: HealthKitObservation
Parent: GroveMobileObservation
Id: healthkit-observation
Title: "HealthKit Observation"
Description: "The source identity and allowlisted HealthKit context for an Observation that also conforms to an appropriate clinical or research profile."
* obeys healthkit-motion-context-1 and healthkit-sleep-stage-1 and healthkit-writer-record-1
* issued 0..0
* extension contains HealthKitSourceType named healthKitSourceType 1..1 MS
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
Description: "A HealthKit Lead-I-like waveform that directly claims the source-neutral Grove Sensor ECG profile. Native R4 elements carry classification, classification method, and references to separately exchanged symptom Observations; validation inputs such as reported count and sampling frequency are not duplicated on the wire."
* obeys healthkit-ecg-symptom-state-1
* extension[healthKitSourceType].valueCode = #HKDataTypeIdentifierElectrocardiogram
* extension contains
    HealthKitECGSymptomsStatus named healthKitECGSymptomsStatus 1..1 MS and
    HealthKitECGSourcePeriod named healthKitECGSourcePeriod 1..1 MS
* code = $loinc#11524-6
* interpretation 1..1 MS
* interpretation.coding 1..1 MS
* interpretation.coding.system = $healthKitECGClassification (exactly)
* interpretation from HealthKitECGClassificationVS (required)
* method 0..1 MS
* method.coding 1..1 MS
* method.coding.system = $healthKitECGAlgorithmVersion (exactly)
* method from HealthKitECGAlgorithmVersionVS (required)
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* hasMember 0..* MS
* hasMember only Reference(Observation)
* hasMember.reference 0..0
* hasMember.type 1..1 MS
* hasMember.type = "Observation" (exactly)
* hasMember.identifier 1..1 MS
* hasMember.identifier.type 1..1 MS
* hasMember.identifier.type = $groveIdentifierRole#source-output
* hasMember.identifier.system 1..1 MS
* hasMember.identifier.value 1..1 MS
* hasMember.identifier.value obeys healthkit-opaque-identifier-value-1
* component 1..1 MS
* component contains voltage 1..1 MS
* component[voltage].code = $mdc#131329
* component[voltage].value[x] 1..1 MS
* component[voltage].value[x] only SampledData
* component[voltage].dataAbsentReason 0..0

Profile: HealthKitECGAverageHeartRateObservation
Parent: HealthKitObservation
Id: healthkit-ecg-average-heart-rate-observation
Title: "HealthKit ECG Average Heart Rate Observation"
Description: "The user's average heart rate during one HealthKit ECG, represented as an independently identifiable LOINC Observation over the exact ECG waveform Period."
* code.coding 1..1 MS
* code.coding.system 1..1 MS
* code.coding.system = $loinc (exactly)
* code.coding.code 1..1 MS
* code.coding.code = #8867-4 (exactly)
* extension[healthKitSourceType].valueCode = #HKDataTypeIdentifierElectrocardiogram
* category 1..1 MS
* category.coding 1..1 MS
* category.coding.system 1..1 MS
* category.coding.system = $observationCategory (exactly)
* category.coding.code 1..1 MS
* category.coding.code = #vital-signs (exactly)
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)
* dataAbsentReason 0..0
* derivedFrom 1..1 MS
* derivedFrom only Reference(HealthKitECGObservation)
* derivedFrom.reference 1..1 MS
* derivedFrom.identifier 0..0

Profile: HealthKitConversionProvenance
Parent: GroveMobileConversionProvenance
Id: healthkit-conversion-provenance
Title: "HealthKit Conversion Provenance"
Description: "Provenance for transforming or byte-preserving one HealthKit object into every admitted HealthKit adapter output without fetching source data."
* target 1..* MS
* target only Reference(HealthKitObservation or HealthKitRecordingDocument or HealthKitVisionPrescription or HealthKitMedicationDoseEvent or HealthKitUserAnnotatedMedication)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.type = $groveIdentifierRole#source-record
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.value 1..1 MS

Profile: HealthKitRecordingDocument
Parent: GroveSensorRecordingDocument
Id: healthkit-recording-document
Title: "HealthKit Recording Document"
Description: "A byte-preserved HealthKit source document or series whose native representation is not a scalar result. Beat-to-beat intervals and workout routes use registered column schemas; provider-issued clinical resources use a stricter derived profile that declares their source FHIR release in the attachment media type."
// The SDK source class is lineage, not a document-type coding.
* extension contains HealthKitSourceType named healthKitSourceType 1..1 MS
* type 1..1 MS


Profile: HealthKitClinicalRecordDocument
Parent: HealthKitRecordingDocument
Id: healthkit-clinical-record-document
Title: "HealthKit Clinical Record Document"
Description: "A pass-through envelope for one provider-issued clinical FHIR resource surfaced by HealthKit. The payload is byte-preserved in the declared source FHIR release; Grove asserts identity and provenance, never conformance over the issuer's resource."
* status MS
* type 1..1 MS
* type from HealthKitClinicalRecordTypeVS (required)
* subject 1..1 MS
* subject only Reference(Patient)
* date 1..1 MS
* content 1..1 MS
* content.format 1..1 MS
* content.format = $recordingFormat#fhir-resource
// Required by the inherited HealthKit recording parent and repeated here for clinical clarity.
* content.format.version 0..0
* content.attachment.contentType 1..1 MS
* content.attachment.size 1..1 MS
* content.attachment.hash 1..1 MS
* obeys healthkit-clinical-fhir-content-type-1





Profile: HealthKitVisionPrescription
Parent: VisionPrescription
Id: healthkit-vision-prescription
Title: "HealthKit Vision Prescription"
Description: "A glasses or contacts prescription a person entered in Health, carried as the structured lens specification HealthKit publishes rather than as an opaque document. HealthKit exposes no separate record-creation instant, so `created` and `dateWritten` both carry HKVisionPrescription.dateIssued. It exposes no prescriber either, and R4 makes that reference mandatory, so the reference is stated absent rather than invented."
* insert HealthKitOutputIdentitySlices
// No classifying element exists on this resource, and a tag may be ignored when a resource is
// interpreted, so the source type is stated as an extension.
* extension contains HealthKitSourceType named healthKitSourceType 1..1 MS
* extension contains HealthKitVisionPrescriptionExpiration named expiration 0..1 MS
* status = #active (exactly)
* created 1..1 MS
* patient 1..1 MS
* patient only Reference(Patient)
* dateWritten 1..1 MS
* prescriber.reference 0..0
* prescriber.identifier 0..0
* prescriber.display 0..0
* prescriber.extension contains $dataAbsentReason named dataAbsentReason 1..1 MS
* prescriber.extension[dataAbsentReason].valueCode = #unknown (exactly)
* lensSpecification 1..2 MS
* lensSpecification.extension contains
    HealthKitLensVertexDistance named vertexDistance 0..1 MS and
    HealthKitLensFarPupillaryDistance named farPupillaryDistance 0..1 MS and
    HealthKitLensNearPupillaryDistance named nearPupillaryDistance 0..1 MS
* lensSpecification.product 1..1 MS
* lensSpecification.eye 1..1 MS
* lensSpecification.sphere 1..1 MS
// One HKVisionPrism resolves into its vertical and horizontal components, each an R4 prism entry.
* lensSpecification.prism 0..2 MS
// HealthKit reports one sphere for glasses and contacts alike; `power` would state it twice.
* lensSpecification.power 0..0
* lensSpecification.duration 0..0
* lensSpecification.color 0..0
* lensSpecification.note 0..0

Profile: HealthKitMedicationDoseEvent
Parent: MedicationAdministration
Id: healthkit-medication-dose-event
Title: "HealthKit Medication Dose Event"
Description: "One dose a person logged against a medication they track in Health. The R4 administration status collapses the six HealthKit log statuses onto three codes, so the exact HKMedicationDoseEvent.LogStatus is retained beside it together with the schedule the dose was logged against. HealthKit publishes no medication record, so the medication is named by the same HKHealthConceptIdentifier the tracked-medication statement carries and by nothing else."
* insert HealthKitOutputIdentitySlices
// No classifying element exists on this resource, and a tag may be ignored when a resource is
// interpreted, so the source type is stated as an extension.
* extension contains
    HealthKitSourceType named healthKitSourceType 1..1 MS and
    HealthKitMedicationDoseLogStatus named logStatus 1..1 MS and
    HealthKitMedicationDoseSchedule named schedule 1..1 MS
* status MS
* medication[x] 1..1 MS
* medication[x] only Reference
* medicationReference.reference 0..0
* medicationReference.identifier 1..1 MS
* medicationReference.identifier.type 1..1 MS
* medicationReference.identifier.type = $groveIdentifierRole#source-context
* medicationReference.identifier.system 1..1 MS
* medicationReference.identifier.value 1..1 MS
* medicationReference.identifier.value obeys healthkit-opaque-identifier-value-1
* subject 1..1 MS
* subject only Reference(Patient)
* effective[x] 1..1 MS
* effective[x] only Period
* effectivePeriod.start 1..1 MS
* effectivePeriod.end 1..1 MS
* dosage 0..1 MS
* dosage.dose 1..1 MS
* dosage.dose.value 1..1 MS
* dosage.dose.system 1..1 MS
* dosage.dose.system = $ucum (exactly)
* dosage.dose.code 1..1 MS
* dosage.rate[x] 0..0
// HealthKit reports the amount and its unit and nothing about how the dose was given.
* dosage.site 0..0
* dosage.route 0..0
* dosage.method 0..0
* dosage.text 0..0
* performer 0..0
* request 0..0

Profile: HealthKitUserAnnotatedMedication
Parent: MedicationStatement
Id: healthkit-user-annotated-medication
Title: "HealthKit User Annotated Medication"
Description: "A non-archived medication a person tracks in Health, with the annotations they added while adding it. HealthKit publishes no sample identity for a tracked medication, so the HKHealthConceptIdentifier of the underlying concept is the identity a dose event refers to. The status is active; archived entries are not admitted because archival alone does not establish that medication use was completed or stopped."
* insert HealthKitOutputIdentitySlices
* identifier 3..* MS
* identifier contains healthConcept 1..1 MS
* identifier[healthConcept].type = $groveIdentifierRole#source-context
* identifier[healthConcept].system 1..1 MS
* identifier[healthConcept].value 1..1 MS
* identifier[healthConcept].value obeys healthkit-opaque-identifier-value-1
* obeys healthkit-medication-concept-identity-1
// No classifying element exists on this resource, and a tag may be ignored when a resource is
// interpreted, so the source type is stated as an extension.
* extension contains
    HealthKitSourceType named healthKitSourceType 1..1 MS and
    HealthKitMedicationNickname named nickname 0..1 MS and
    HealthKitMedicationHasSchedule named hasSchedule 1..1 MS and
    HealthKitMedicationGeneralForm named generalForm 1..1 MS
* status from HealthKitTrackedMedicationStatusVS (required)
* medication[x] only CodeableConcept
* medicationCodeableConcept 1..1 MS
* medicationCodeableConcept.text 1..1 MS
* medicationCodeableConcept.coding 0..* MS
* subject 1..1 MS
* subject only Reference(Patient)
// HealthKit states that a schedule exists, never its times or amounts.
* dosage 0..0
