//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: connected-health-digest-id-1
Description: "A connected-provider digest identifier uses the versioned lowercase SHA-256 form defined by this guide."
Severity: #error
Expression: "matches('^v1:[0-9a-f]{64}$')"

Profile: ConnectedHealthObservation
Parent: GroveMobileObservation
Id: connected-health-observation
Title: "Connected Health Observation"
Description: "Source lineage and deterministic business identity for a shared Mobile or Sensor Observation converted from already-obtained Google Health API, Oura, or Withings data. Every output also declares exactly one exact source-neutral semantic profile."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    sourceRecordId 1..1 MS and
    outputId 1..1 MS
* identifier[sourceRecordId].system = $connectedHealthSourceRecordId
* identifier[sourceRecordId].value 1..1 MS
* identifier[sourceRecordId].value obeys connected-health-digest-id-1
* identifier[outputId].system = $connectedHealthOutputId
* identifier[outputId].value 1..1 MS
* identifier[outputId].value obeys connected-health-digest-id-1
* issued 1..1 MS
* extension contains ConnectedHealthProvider named connectedHealthProvider 1..1 MS

Profile: ConnectedHealthConversionProvenance
Parent: GroveMobileConversionProvenance
Id: connected-health-conversion-provenance
Title: "Connected Health Conversion Provenance"
Description: "Provenance for converting one already-obtained connected-provider record into one or more source-neutral Observations."
* target 1..* MS
* target only Reference(ConnectedHealthObservation)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.system = $connectedHealthSourceRecordId
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys connected-health-digest-id-1
