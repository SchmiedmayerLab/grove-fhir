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
Description: "The physical sensor that captured the example recordings."
* identifier.system = "https://study.example.org/fhir/identifiers/sensor-device"
* identifier.value = "sensor-device-001"
* manufacturer = "Example Devices"
* modelNumber = "Wave 2"
* type.text = "Wearable sensor"

Instance: GroveSensorConverterExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Grove Sensor Example Converter"
Description: "The already-running application that transformed the caller-supplied sensor recording into FHIR resources."
* status = #active
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "org.example.sensor-converter"
* deviceName[applicationName].name = "Sensor Converter"
* deviceName[applicationName].type = #user-friendly-name

Instance: GroveSensorSampledDataExample
InstanceOf: GroveSensorSampledDataObservation
Usage: #example
Title: "Grove Sensor Sampled Plethysmogram"
Description: "A single-channel uniformly sampled waveform represented inline."
* identifier.system = "https://study.example.org/fhir/identifiers/sensor-observation"
* identifier.value = "pleth-20260820-001"
* status = #final
* code = $mdc#150452 "MDC_PULS_OXIM_PLETH"
* subject = Reference(GroveSensorPatientExample)
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
Description: "A Lead I ECG channel using the ISO/IEEE 11073 MDC lead code and UCUM millivolts."
* identifier.system = "https://study.example.org/fhir/identifiers/sensor-observation"
* identifier.value = "ecg-20260820-001"
* status = #final
* subject = Reference(GroveSensorPatientExample)
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
Description: "A compact embedded native recording linked to the parsed ECG Observation."
* identifier.system = "https://study.example.org/fhir/identifiers/sensor-document"
* identifier.value = "ecg-native-20260820-001"
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
* content.format = GroveRecordingFormatCS#native-json-1 "Native JSON 1"
* context.related = Reference(GroveSensorECGExample)

Instance: GroveSensorConversionProvenanceExample
InstanceOf: GroveSensorConversionProvenance
Usage: #example
Title: "Grove Sensor Conversion Provenance"
Description: "The source-neutral conversion event that targets both the structured ECG and its native Recording Document."
* target[+] = Reference(GroveSensorECGExample)
* target[+] = Reference(GroveSensorRecordingDocumentExample)
* recorded = "2026-08-20T17:31:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(GroveSensorConverterExample)
* entity[0].role = #source
* entity[0].what.identifier.system = "https://study.example.org/fhir/identifiers/native-sensor-record"
* entity[0].what.identifier.value = "native-ecg-20260820-001"
* entity[0].what.display = "Caller-supplied native ECG record"
