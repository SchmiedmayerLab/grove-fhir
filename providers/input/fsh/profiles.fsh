//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: grove-writer-record-id-value-1
Description: "A writer record identifier scopes the writer's own identifier to the writer: the scheme version, the writing application's reverse-DNS identifier, a vertical bar, then the identifier it assigned. Neither part may contain a vertical bar."
Expression: "$this.matches('^v1:[A-Za-z0-9._-]+[|].+$')"
Severity: #error

Invariant: provider-composed-id-1
Description: "A connected-provider identifier is either the provider's own record key passed through verbatim, where that key is unique across the whole provider, or a versioned composition of the provider code, the account pseudonym, the source type and the key, joined by vertical bars."
Severity: #error
Expression: "matches('^(v1:[^|]+([|][^|]+)+|[^|]+)$')"

Profile: ProvidersObservation
Parent: GroveMobileObservation
Id: providers-observation
Title: "Provider Observation"
Description: "Source lineage and deterministic business identity for a shared Mobile or Sensor Observation converted from already-obtained Google Health API, Oura, or Withings data. Every output also declares exactly one exact source-neutral semantic profile."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    sourceRecordId 1..1 MS and
    outputId 0..1 MS and
    writerRecordId 0..1 MS
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value 1..1 MS
* identifier[sourceRecordId].value obeys provider-composed-id-1
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value 1..1 MS
* identifier[outputId].value obeys provider-composed-id-1
* identifier[writerRecordId].system = $groveWriterRecordId
* identifier[writerRecordId].value 1..1 MS
* identifier[writerRecordId].value obeys grove-writer-record-id-value-1
* issued 1..1 MS
* extension contains
    ProviderProvider named provider 1..1 MS and
    ProviderSourceType named providerSourceType 1..1 MS

Profile: ProvidersRecordingDocument
Parent: GroveSensorRecordingDocument
Id: providers-recording-document
Title: "Provider Recording Document"
Description: "A provider-native payload already obtained from Google Health API, Oura, or Withings and retained without inventing uniform timing or scalar semantics."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    sourceRecordId 1..1 MS and
    outputId 0..1 MS and
    writerRecordId 0..1 MS
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value 1..1 MS
* identifier[sourceRecordId].value obeys provider-composed-id-1
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value 1..1 MS
* identifier[outputId].value obeys provider-composed-id-1
* identifier[writerRecordId].system = $groveWriterRecordId
* identifier[writerRecordId].value 1..1 MS
* identifier[writerRecordId].value obeys grove-writer-record-id-value-1
* extension contains
    ProviderProvider named provider 1..1 MS and
    ProviderSourceType named providerSourceType 1..1 MS

Profile: ProvidersConversionProvenance
Parent: GroveSensorConversionProvenance
Id: providers-conversion-provenance
Title: "Provider Conversion Provenance"
Description: "Provenance for converting one already-obtained connected-provider record into one or more source-neutral Observations or native Recording Documents."
* target 1..* MS
* target only Reference(ProvidersObservation or ProvidersRecordingDocument)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.system = $providerSourceRecordId
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys provider-composed-id-1
