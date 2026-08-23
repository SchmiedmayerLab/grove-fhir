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

Invariant: health-connect-client-record-version-1
Description: "A client record version orders revisions of one writer-assigned record, so it appears only with the client record identifier it versions."
Expression: "extension('https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-client-record-version').empty() or identifier.where(system = 'https://grovealliance.org/fhir/health-connect/NamingSystem/health-connect-client-record-id').exists()"
Severity: #error


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
    outputId 1..1 MS and
    clientRecordId 0..1 MS
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value 1..1 MS
* identifier[recordId].value obeys health-connect-record-id-value-1
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value 1..1 MS
* identifier[clientRecordId].system = $healthConnectClientRecordId
* identifier[clientRecordId].value 1..1 MS
* obeys health-connect-output-id-1 and health-connect-client-record-version-1
* issued 1..1 MS
* specimen only Reference(HealthConnectSpecimen)
* extension contains
    HealthConnectRecordType named healthConnectRecordType 1..1 MS and
    $bodyPosition named bodyPosition 0..1 MS and
    HealthConnectGlucoseMealContext named glucoseMealContext 0..1 MS and
    HealthConnectSleepTitle named sleepTitle 0..1 MS and
    HealthConnectClientRecordVersion named clientRecordVersion 0..1 MS
* note MS

Profile: HealthConnectWholeBloodGlucose
Parent: HealthConnectObservation
Id: health-connect-whole-blood-glucose
Title: "Health Connect Whole-blood Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit whole-blood specimen evidence. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#2339-0
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectCapillaryBloodGlucose
Parent: HealthConnectObservation
Id: health-connect-capillary-blood-glucose
Title: "Health Connect Capillary-blood Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit capillary-blood specimen evidence. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#32016-8
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectSerumPlasmaGlucose
Parent: HealthConnectObservation
Id: health-connect-serum-plasma-glucose
Title: "Health Connect Serum or Plasma Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit serum or plasma specimen evidence. The referenced Specimen preserves which source enum was present. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#2345-7
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectInterstitialGlucose
Parent: HealthConnectObservation
Id: health-connect-interstitial-glucose
Title: "Health Connect Interstitial-fluid Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit interstitial-fluid specimen evidence. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#99504-3
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

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


Extension: HealthConnectClientRecordVersion
Id: health-connect-client-record-version
Title: "Health Connect Client Record Version"
Description: "The clientRecordVersion of the Record this Observation was converted from. A writer that re-imports a measurement reuses its clientRecordId and raises this version, and Health Connect keeps the higher one; the version orders those revisions so a receiver can supersede rather than double-count."
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only integer
* valueInteger 1..1
