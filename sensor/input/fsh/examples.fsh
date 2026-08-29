//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: GroveSensorPatientExample
InstanceOf: Patient
Usage: #example
Title: "Grove Sensor Example Participant"
Description: "The participant referenced by the waveform examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "sensor-participant-001"

Instance: GroveSensorDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "Grove Sensor Example Device"
Description: "An event-time snapshot of the physical sensor that captured the examples, backed by a governed stable per-unit token."
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v0/test-key/1"
* identifier[physicalUnit].value = "v0:test-key:1:izeNpl55_7d6M_9MCfZNMbX2Uu-on5fNZ7fedyWW1g8"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[eventSnapshot].value = "v0:test-key:1:Wwnmc-OpfPgk4HXP3hG_xPwlF5OLcqYHduQ3vIKqOj8"
* status = #active
* manufacturer = "Example Devices"
* modelNumber = "Wave 2"
* type.text = "Wearable sensor"

Instance: GroveSensorConverterExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Grove Sensor Example Converter"
Description: "The already-running application that transformed an already-obtained sensor recording into FHIR resources."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:_cdbrIUf-0-RxDX02Z1TvNslbnXran1mhDn_kEfsvn0"
* deviceName[applicationName].name = "Sensor Converter"
* deviceName[applicationName].type = #user-friendly-name

Instance: GroveSensorSampledDataExample
InstanceOf: GroveSensorSampledDataObservation
Usage: #example
Title: "Grove Sensor Sampled Plethysmogram"
Description: "A single-channel uniformly sampled waveform represented inline with typed source and output identities."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:04vTNIPMpGMi4a1YXLaYvyXdqDeDdrpZZS5VeOJ_kfc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Gdb2GLAXza5bR3ahsrdqVHyCvtBCa_l3Qxt8WbvY4S0"
* status = #final
* code = $mdc#150452 "MDC_PULS_OXIM_PLETH"
* subject = Reference(GroveSensorPatientExample)
* performer = Reference(GroveSensorPatientExample)
* effectivePeriod.start = "2026-08-20T10:30:00-07:00"
* effectivePeriod.end = "2026-08-20T10:30:00.050-07:00"
* valueSampledData.origin.value = 0
* valueSampledData.origin.system = $ucum
* valueSampledData.origin.code = #1
* valueSampledData.period = 10
* valueSampledData.dimensions = 1
* valueSampledData.data = "1 3 5 4 2 1"
* device = Reference(GroveSensorDeviceExample)

Instance: GroveSensorECGExample
InstanceOf: GroveSensorECGObservation
Usage: #example
Title: "Grove Sensor Lead I ECG"
Description: "A Lead I ECG channel using the ISO/IEEE 11073 MDC lead code, UCUM millivolts, and the same logical source-record identity as its native artifact."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:LoDxoZVC20IZs7vodESEapjYVyoFVvimBgDvQJEbsn4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:2CsQrfS-JuC6DoGFIUevA9SEvVf1cvWbxhqkxnf7tu4"
* status = #final
* subject = Reference(GroveSensorPatientExample)
* performer = Reference(GroveSensorPatientExample)
* effectivePeriod.start = "2026-08-20T10:31:00-07:00"
* effectivePeriod.end = "2026-08-20T10:31:00.020-07:00"
* component[0].code = $mdc#131329 "MDC_ECG_ELEC_POTL_I"
* component[0].valueSampledData.origin.value = 0
* component[0].valueSampledData.origin.system = $ucum
* component[0].valueSampledData.origin.code = #mV
* component[0].valueSampledData.period = 5
* component[0].valueSampledData.dimensions = 1
* component[0].valueSampledData.data = "0.01 0.04 0.12 0.03 -0.01"
* device = Reference(GroveSensorDeviceExample)

Instance: GroveSensorRecordingDocumentExample
InstanceOf: GroveSensorRecordingDocument
Usage: #example
Title: "Grove Native Sensor Recording"
Description: "A compact embedded native recording linked to the parsed ECG Observation and sharing its logical source-record identity."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:LoDxoZVC20IZs7vodESEapjYVyoFVvimBgDvQJEbsn4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Jed7SZ6XUTODp1fmIy-w_D6ftt-jECzQwscAzOYCU3I"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:GoQCxPhPOHCKLE1stomWyG911JO0i1JzohK7Dy9nE4s"
* status = #current
* type = $loinc#11524-6 "EKG study"
* subject = Reference(GroveSensorPatientExample)
* date = "2026-08-20T17:31:01Z"
* author = Reference(GroveSensorDeviceExample)
* content.attachment.contentType = #application/json
* content.attachment.title = "Native ECG recording"
* content.attachment.data = "eyJsZWFkIjoiSSIsInVuaXQiOiJ1ViIsInNhbXBsZXMiOlszMTIsMzA1LDI5MV19"
* content.attachment.size = 48
* content.attachment.hash = "mzgiyiPRcgwlAYq6ZhFBwSs26gw="
* content.format = GroveRecordingFormatCS#native-recording "Native Recording"
* context.related = Reference(GroveSensorECGExample)

Instance: GroveSensorConversionProvenanceExample
InstanceOf: GroveSensorConversionProvenance
Usage: #example
Title: "Grove Sensor Conversion Provenance"
Description: "The source-neutral conversion event that targets both the structured ECG and its native Recording Document."
* target[0] = Reference(GroveSensorECGExample)
* target[0].display = "Lead I ECG"
* target[1] = Reference(GroveSensorRecordingDocumentExample)
* target[1].display = "Native ECG recording"
* occurredDateTime = "2026-08-20T17:31:00Z"
* recorded = "2026-08-20T17:31:01Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(GroveSensorConverterExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:LoDxoZVC20IZs7vodESEapjYVyoFVvimBgDvQJEbsn4"
