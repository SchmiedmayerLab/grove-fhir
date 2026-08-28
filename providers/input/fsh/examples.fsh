//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: ProviderPatientExample
InstanceOf: Patient
Usage: #example
Title: "Provider Example Participant"
Description: "The Patient referenced by the connected-provider examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: ProviderApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Provider Converter Snapshot"
Description: "The immutable event-time application snapshot that converted one already-obtained provider record."
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:UGzHY2SuM3Fy_2XiJrLUV5avqMwtZBJRRGoL-m6GBhE"
* status = #active
* deviceName[applicationName].name = "Provider Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: GoogleHealthHeartRateRecordingExample
InstanceOf: ProvidersRecordingDocument
Usage: #example
Title: "Google Health Native Heart-rate Recording"
Description: "An authorized exact source artifact for irregular heart-rate points, retained without resampling or invented scalar semantics."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:xypyeIwaavd61qkEQqVGhLU4TSfIuclCc1B8mP6SXcc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:bBcAqxHEG5lYosZths148rzR5__1-_vtbS4mGfDy7X4"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-provider-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:EVXFzOc-5bN3pTBcEfjCzg4Z7suyJAKRzN8TRxR5Ls8"
* extension[provider].valueCode = #google-health-api
* extension[providerSourceType].valueCode = #google-health-api/heart-rate
* status = #current
* type.text = "Google Health API heart-rate archive"
* subject = Reference(ProviderPatientExample)
* date = "2026-08-20T17:00:01Z"
* author = Reference(ProviderApplicationExample)
* content.attachment.contentType = #application/vnd.grovealliance.provider+json
* content.attachment.title = "Authorized minimized provider recording"
* content.attachment.data = "eyJwb2ludCI6W3sic3RhcnRUaW1lTmFub3MiOiIxNzg3MjM2OTgwMDAwMDAwMDAwIiwiZW5kVGltZU5hbm9zIjoiMTc4NzIzNjk4MDAwMDAwMDAwMCIsImRhdGFUeXBlTmFtZSI6ImNvbS5nb29nbGUuaGVhcnRfcmF0ZS5icG0iLCJ2YWx1ZSI6W3siZnBWYWwiOjcxLjB9XX1dfQ=="
* content.attachment.size = 157
* content.attachment.hash = "W77rFQFjzMqkuSpq6pY7XVnlw8A="
* content.format = $recordingFormat#provider-recording "Provider Recording"
* content.format.version = "0.6.0"

Instance: GoogleHealthHeartRateRecordingProvenanceExample
InstanceOf: ProvidersConversionProvenance
Usage: #example
Title: "Google Health Native Heart-rate Recording Provenance"
Description: "The one-source conversion event that preserved the authorized Google Health heart-rate payload as a native recording document."
* target = Reference(GoogleHealthHeartRateRecordingExample)
* occurredDateTime = "2026-08-20T17:00:00Z"
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(ProviderApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:xypyeIwaavd61qkEQqVGhLU4TSfIuclCc1B8mP6SXcc"
