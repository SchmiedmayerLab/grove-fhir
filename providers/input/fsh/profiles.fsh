//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: provider-digest-id-1
Description: "A connected-provider digest identifier uses the versioned lowercase SHA-256 form defined by this guide."
Severity: #error
Expression: "matches('^v1:[0-9a-f]{64}$')"

Profile: ProviderObservation
Parent: GroveMobileObservation
Id: provider-observation
Title: "Provider Observation"
Description: "Source lineage and deterministic business identity for a shared Mobile or Sensor Observation converted from already-obtained Google Health API, Oura, or Withings data. Every output also declares exactly one exact source-neutral semantic profile."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    sourceRecordId 1..1 MS and
    outputId 1..1 MS
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value 1..1 MS
* identifier[sourceRecordId].value obeys provider-digest-id-1
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value 1..1 MS
* identifier[outputId].value obeys provider-digest-id-1
* issued 1..1 MS
* extension contains
    ProviderProvider named provider 1..1 MS and
    ProviderSourceType named providerSourceType 1..1 MS

Profile: ProviderRecordingDocument
Parent: GroveSensorRecordingDocument
Id: provider-recording-document
Title: "Provider Recording Document"
Description: "A provider-native payload already obtained from Google Health API, Oura, or Withings and retained without inventing uniform timing or scalar semantics."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    sourceRecordId 1..1 MS and
    outputId 1..1 MS
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value 1..1 MS
* identifier[sourceRecordId].value obeys provider-digest-id-1
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value 1..1 MS
* identifier[outputId].value obeys provider-digest-id-1
* extension contains
    ProviderProvider named provider 1..1 MS and
    ProviderSourceType named providerSourceType 1..1 MS

Profile: ProviderConversionProvenance
Parent: GroveSensorConversionProvenance
Id: provider-conversion-provenance
Title: "Provider Conversion Provenance"
Description: "Provenance for converting one already-obtained connected-provider record into one or more source-neutral Observations or native Recording Documents."
* target 1..* MS
* target only Reference(ProviderObservation or ProviderRecordingDocument)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.system = $providerSourceRecordId
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys provider-digest-id-1
