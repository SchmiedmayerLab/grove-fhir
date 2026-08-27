//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Profile: ProvidersObservation
Parent: GroveMobileObservation
Id: providers-observation
Title: "Provider Observation"
Description: "Source lineage and deterministic business identity for a shared Mobile or Sensor Observation converted from already-obtained Google Health API, Oura, or Withings data. Every output also declares exactly one exact source-neutral semantic profile."
* issued 1..1 MS
* extension contains
    ProviderProvider named provider 1..1 MS and
    ProviderSourceType named providerSourceType 1..1 MS

Profile: ProvidersRecordingDocument
Parent: GroveSensorRecordingDocument
Id: providers-recording-document
Title: "Provider Recording Document"
Description: "A provider-native payload already obtained from Google Health API, Oura, or Withings and retained without inventing uniform timing or scalar semantics."
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
* entity.what.identifier.type = $groveIdentifierRole#source-record
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.value 1..1 MS
