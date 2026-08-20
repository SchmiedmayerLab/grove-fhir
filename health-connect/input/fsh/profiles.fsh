//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: health-connect-output-id-1
Description: "The Health Connect output identifier uses the versioned lowercase SHA-256 form defined by this guide."
Severity: #error
Expression: "identifier.where(system = 'https://grovealliance.org/fhir/health-connect/NamingSystem/health-connect-output-id').all(value.matches('^v1:[0-9a-f]{64}$'))"

Invariant: health-connect-record-id-value-1
Description: "The Health Connect record identifier uses the repository-scoped lowercase SHA-256 form defined by this guide."
Severity: #error
Expression: "matches('^v1:[0-9a-f]{64}$')"

Invariant: health-connect-specimen-id-value-1
Description: "A Health Connect specimen identifier uses the versioned lowercase SHA-256 form defined by this guide."
Severity: #error
Expression: "matches('^v1:[0-9a-f]{64}$')"

Invariant: health-connect-specimen-type-1
Description: "A synthesized glucose specimen carries exactly one admitted standard SNOMED CT specimen concept."
Severity: #error
Expression: "type.coding.where(system = 'http://snomed.info/sct' and (code = '258580003' or code = '122554006' or code = '119361006' or code = '119364003' or code = '258479004')).count() = 1"

Invariant: health-connect-glucose-specimen-1
Description: "Only a supported glucose output has a specimen, and every supported glucose output has one."
Severity: #error
Expression: "(code.coding.where(system = 'http://loinc.org' and (code = '2339-0' or code = '32016-8' or code = '2345-7' or code = '99504-3')).exists()) = specimen.exists()"

Invariant: health-connect-body-position-1
Description: "The standard body-position extension is present only on a blood-pressure panel."
Severity: #error
Expression: "extension.where(url = 'http://hl7.org/fhir/StructureDefinition/observation-bodyPosition').empty() or code.coding.where(system = 'http://loinc.org' and code = '85354-9').exists()"

Invariant: health-connect-meal-context-1
Description: "Health Connect meal context is present only on a supported glucose output."
Severity: #error
Expression: "extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-glucose-meal-context').empty() or code.coding.where(system = 'http://loinc.org' and (code = '2339-0' or code = '32016-8' or code = '2345-7' or code = '99504-3')).exists()"

Invariant: health-connect-sleep-title-1
Description: "A Health Connect sleep title and source notes are present only on the sleep-duration summary."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-sleep-title').empty() and note.empty()) or code.coding.where(system = 'http://loinc.org' and code = '93832-4').exists()"

Invariant: health-connect-sleep-stage-1
Description: "A shared sleep-stage output carries exactly one exact Health Connect source stage coding, and no other output carries one."
Severity: #error
Expression: "(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sleep-stage').count() = 1) or (code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').empty() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sleep-stage').empty())"

Profile: HealthConnectObservation
Parent: GroveMobileObservation
Id: health-connect-observation
Title: "Health Connect Observation"
Description: "The source and output identities plus allowlisted source context for a result converted from an AndroidX Health Connect 1.1 Record. Every output also declares exactly one shared Grove measurement profile."
* obeys health-connect-glucose-specimen-1 and health-connect-body-position-1 and health-connect-meal-context-1 and health-connect-sleep-title-1 and health-connect-sleep-stage-1
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    recordId 1..1 MS and
    outputId 1..1 MS
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value 1..1 MS
* identifier[recordId].value obeys health-connect-record-id-value-1
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value 1..1 MS
* obeys health-connect-output-id-1
* issued 1..1 MS
* specimen only Reference(HealthConnectSpecimen)
* extension contains
    $bodyPosition named bodyPosition 0..1 MS and
    HealthConnectGlucoseMealContext named glucoseMealContext 0..1 MS and
    HealthConnectSleepTitle named sleepTitle 0..1 MS
* note MS

Profile: HealthConnectSpecimen
Parent: Specimen
Id: health-connect-specimen
Title: "Health Connect Glucose Specimen"
Description: "A standard-coded specimen node synthesized only when a supported Health Connect BloodGlucoseRecord supplies an exact admitted specimen-source enum."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains specimenId 1..1 MS
* identifier[specimenId].system = $healthConnectSpecimenId
* identifier[specimenId].value 1..1 MS
* identifier[specimenId].value obeys health-connect-specimen-id-value-1
* status = #available
* type 1..1 MS
* obeys health-connect-specimen-type-1
* subject 1..1 MS
* subject only Reference(Patient)

Profile: HealthConnectConversionProvenance
Parent: GroveMobileConversionProvenance
Id: health-connect-conversion-provenance
Title: "Health Connect Conversion Provenance"
Description: "Provenance for transforming one Health Connect source Record into one or more Health Connect Observations, including the DataOrigin application that entered the Record into Health Connect."
* target 1..* MS
* target only Reference(HealthConnectObservation)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys health-connect-record-id-value-1
* entity.agent 1..1 MS
* entity.agent.type 1..1 MS
* entity.agent.type = $provenanceParticipantType#enterer
* entity.agent.who 1..1 MS
* entity.agent.who only Reference(Device)
