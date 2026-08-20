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

Profile: HealthConnectObservation
Parent: GroveMobileObservation
Id: health-connect-observation
Title: "Health Connect Observation"
Description: "The source and output identities for a quantity result converted from an Android Health Connect Record. Combine it with the profile that defines the clinical or research meaning."
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
* value[x] 1..1 MS
* value[x] only Quantity
* dataAbsentReason 0..0

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
