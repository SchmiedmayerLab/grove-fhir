//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: SensorKitPatientExample
InstanceOf: Patient
Usage: #example
Title: "SensorKit Example Participant"
Description: "The Patient referenced by the SensorKit adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "sensorkit-participant-001"

Instance: SensorKitDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "SensorKit Example Recording Device"
Description: "The watch that captured the example SensorKit streams."
* identifier.system = "https://study.example.org/fhir/identifiers/device"
* identifier.value = "sensorkit-watch-001"
* status = #active
* manufacturer = "Example Manufacturer"
* type.text = "Watch"

Instance: SensorKitApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "SensorKit Converting Application"
Description: "The application that transforms already-obtained SensorKit records into the FHIR graph."
* status = #active
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "sensorkit-mapper"
* deviceName[applicationName].name = "SensorKit Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: SensorKitRotationRateExample
InstanceOf: SensorKitObservation
Usage: #example
Title: "SensorKit Rotation Rate Sampled Data"
Description: "A lossless, uniformly sampled three-axis rotation-rate stream that declares exactly the source-neutral SampledData profile and the SensorKit adapter profile."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-sampled-data-observation"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "879d9ea2-21cb-4527-b59b-2831dc4c84ab"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:879d9ea2-21cb-4527-b59b-2831dc4c84ab|sampled-data"
* extension[sensorKitSourceType].valueCode = #rotation-rate
* status = #final
* code = $sensorKitSourceType#rotation-rate "Rotation rate"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T09:00:00-07:00"
* effectivePeriod.end = "2026-08-20T09:00:00.020-07:00"
* valueSampledData.origin.value = 0
* valueSampledData.origin.system = $ucum
* valueSampledData.origin.code = #rad/s
* valueSampledData.period = 10
* valueSampledData.dimensions = 3
* valueSampledData.data = "0.01 -0.02 0.03 0.02 -0.01 0.04 0.01 -0.01 0.02"
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitRotationRateProvenanceExample
InstanceOf: SensorKitConversionProvenance
Usage: #example
Title: "SensorKit Rotation-rate Conversion Provenance"
Description: "The transformation event linking one SensorKit source record to its structured SampledData output."
* target = Reference(SensorKitRotationRateExample)
* recorded = "2026-08-20T16:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $sensorKitRecordId
* entity.what.identifier.value = "879d9ea2-21cb-4527-b59b-2831dc4c84ab"

Instance: SensorKitECGExample
InstanceOf: SensorKitECGObservation
Usage: #example
Title: "SensorKit ECG Waveform Projection"
Description: "The complete uniform voltage projection of one SensorKit ECG record. The linked native document preserves exact session state and per-voltage flags."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "2fea27a0-5575-4fd2-83d7-d46b03059ddc"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:2fea27a0-5575-4fd2-83d7-d46b03059ddc|ecg-waveform"
* extension[sensorKitSourceType].valueCode = #ecg
* extension[sensorKitECGSessionGuidance].valueCode = #guided
* status = #final
* code = $loinc#11524-6 "EKG study"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T09:10:00.000-07:00"
* effectivePeriod.end = "2026-08-20T09:10:00.012-07:00"
* derivedFrom = Reference(SensorKitECGDocumentExample)
* component.code.coding[sensorKitECGLead] = $sensorKitECGLead#leftArmMinusRightArm "Left arm minus right arm"
* component.code.coding[mdcLead] = $mdc#131329 "MDC_ECG_ELEC_POTL_I"
* component[0].valueSampledData.origin.value = 0
* component[0].valueSampledData.origin.system = $ucum
* component[0].valueSampledData.origin.code = #mV
* component[0].valueSampledData.period = 4
* component[0].valueSampledData.dimensions = 1
* component[0].valueSampledData.data = "0.011 0.023 -0.005 0.014"
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitECGDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Native ECG Recording"
Description: "The caller-supplied exact native encoding that retains session identifiers/states and each signalInvalid and crownTouched flag."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "2fea27a0-5575-4fd2-83d7-d46b03059ddc"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:2fea27a0-5575-4fd2-83d7-d46b03059ddc|native-recording"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:10:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit ECG native recording"
* content.attachment.data = "eyJndWlkYW5jZSI6Imd1aWRlZCIsImZsYWdzIjpbMCwyLDEsMF19"
* content.attachment.size = 39
* content.attachment.hash = "uuvrA7QHOUD+1r204rKEqJg7hY8="
* context.related = Reference(SensorKitECGExample)

Instance: SensorKitECGProvenanceExample
InstanceOf: SensorKitConversionProvenance
Usage: #example
Title: "SensorKit ECG Conversion Provenance"
Description: "One conversion event targets both the structured waveform and exact native companion for the same SensorKit source record."
* target[+] = Reference(SensorKitECGExample)
* target[+] = Reference(SensorKitECGDocumentExample)
* recorded = "2026-08-20T16:10:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $sensorKitRecordId
* entity.what.identifier.value = "2fea27a0-5575-4fd2-83d7-d46b03059ddc"

Instance: SensorKitInverseECGExample
InstanceOf: SensorKitECGObservation
Usage: #example
Title: "SensorKit Inverse-Lead ECG Waveform Projection"
Description: "A complete right-arm-minus-left-arm voltage projection. The exact SensorKit orientation is retained without falsely labeling the inverse signal as standard MDC Lead I."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "725f35ec-8df0-4f35-9477-88472f35e670"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:725f35ec-8df0-4f35-9477-88472f35e670|ecg-waveform"
* extension[sensorKitSourceType].valueCode = #ecg
* extension[sensorKitECGSessionGuidance].valueCode = #unguided
* status = #final
* code = $loinc#11524-6 "EKG study"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T09:12:00.000-07:00"
* effectivePeriod.end = "2026-08-20T09:12:00.012-07:00"
* derivedFrom = Reference(SensorKitInverseECGDocumentExample)
* component.code.coding[sensorKitECGLead] = $sensorKitECGLead#rightArmMinusLeftArm "Right arm minus left arm"
* component[0].valueSampledData.origin.value = 0
* component[0].valueSampledData.origin.system = $ucum
* component[0].valueSampledData.origin.code = #mV
* component[0].valueSampledData.period = 4
* component[0].valueSampledData.dimensions = 1
* component[0].valueSampledData.data = "-0.011 -0.023 0.005 -0.014"
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitInverseECGDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Native Inverse-Lead ECG Recording"
Description: "The caller-supplied exact native encoding paired with the inverse-lead waveform projection."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "725f35ec-8df0-4f35-9477-88472f35e670"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:725f35ec-8df0-4f35-9477-88472f35e670|native-recording"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:12:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit inverse-lead ECG native recording"
* content.attachment.data = "eyJndWlkYW5jZSI6InVuZ3VpZGVkIiwiZmxhZ3MiOlswLDAsMCwwXX0="
* content.attachment.size = 41
* content.attachment.hash = "rGAihY2Jsbtsbgf6IgtNSlsW6Cs="
* context.related = Reference(SensorKitInverseECGExample)

Instance: SensorKitInverseECGProvenanceExample
InstanceOf: SensorKitConversionProvenance
Usage: #example
Title: "SensorKit Inverse-Lead ECG Conversion Provenance"
Description: "One conversion event targets both inverse-lead ECG representations for the same SensorKit source record."
* target[+] = Reference(SensorKitInverseECGExample)
* target[+] = Reference(SensorKitInverseECGDocumentExample)
* recorded = "2026-08-20T16:12:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $sensorKitRecordId
* entity.what.identifier.value = "725f35ec-8df0-4f35-9477-88472f35e670"

Instance: SensorKitOnWristExample
InstanceOf: SensorKitOnWristObservation
Usage: #example
Title: "SensorKit On-Wrist State"
Description: "A platform-exclusive on-wrist state with wrist and crown placement preserved as coded components."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "f66d92c6-6819-4d9d-8f0f-d12f9c0a1f03"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:f66d92c6-6819-4d9d-8f0f-d12f9c0a1f03|on-wrist"
* extension[sensorKitSourceType].valueCode = #on-wrist
* status = #final
* code = $sensorKitConcept#on-wrist-state "On-wrist state"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T08:30:00-07:00"
* effectivePeriod.end = "2026-08-20T09:02:00-07:00"
* valueCodeableConcept = $sensorKitValue#on-wrist "On wrist"
* component[wristLocation].code = $sensorKitConcept#wrist-location "Wrist location"
* component[wristLocation].valueCodeableConcept = $sensorKitValue#left "Left"
* component[crownOrientation].code = $sensorKitConcept#crown-orientation "Crown orientation"
* component[crownOrientation].valueCodeableConcept = $sensorKitValue#right "Right"
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitDeviceUsageExample
InstanceOf: SensorKitDeviceUsageObservation
Usage: #example
Title: "SensorKit Device Usage Summary"
Description: "A platform-exclusive device-usage summary; detailed application, notification, and web usage remains in the native recording."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:b4df30d0-2a34-492e-a68e-b1eab1cb471d|device-usage-summary"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #final
* code = $sensorKitConcept#device-usage-summary "Device usage summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T08:00:00-07:00"
* effectivePeriod.end = "2026-08-20T08:15:00-07:00"
* valueQuantity = 372 's' "seconds"
* derivedFrom = Reference(SensorKitDeviceUsageDocumentExample)
* component[screenWakes].code = $sensorKitConcept#screen-wakes "Screen wakes"
* component[screenWakes].valueQuantity = 6 '{count}' "{count}"
* component[unlocks].code = $sensorKitConcept#unlocks "Unlocks"
* component[unlocks].valueQuantity = 4 '{count}' "{count}"
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitVisitExample
InstanceOf: SensorKitVisitObservation
Usage: #example
Title: "SensorKit Visit Summary"
Description: "A platform-exclusive visit summary that preserves uncertain arrival and departure windows without asserting a clinical Encounter."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "d75fc337-6aac-4edf-931d-bbf1b24736aa"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:d75fc337-6aac-4edf-931d-bbf1b24736aa|visit-summary"
* extension[sensorKitSourceType].valueCode = #visits
// Present because this example's deployment authorized disclosure; without that authorization the
// visit still converts and this extension is simply absent.
* extension[visitLocation].valueIdentifier.system = "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-visit-location-id"
* extension[visitLocation].valueIdentifier.value = "0f1f2c48-2b45-4a2a-9a2a-8b4d3a2f61c7"
* status = #final
* code = $sensorKitConcept#visit-summary "Visit summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T07:59:00-07:00"
* effectivePeriod.end = "2026-08-20T09:31:00-07:00"
* component[locationCategory].code = $sensorKitConcept#visit-location-category "Visit location category"
* component[locationCategory].valueCodeableConcept = $sensorKitValue#work "Work"
* component[distanceFromHome].code = $sensorKitConcept#distance-from-home "Distance from home"
* component[distanceFromHome].valueQuantity = 4200 'm' "m"
* component[arrivalWindow].code = $sensorKitConcept#arrival-window "Arrival window"
* component[arrivalWindow].valuePeriod.start = "2026-08-20T07:59:00-07:00"
* component[arrivalWindow].valuePeriod.end = "2026-08-20T08:02:00-07:00"
* component[departureWindow].code = $sensorKitConcept#departure-window "Departure window"
* component[departureWindow].valuePeriod.start = "2026-08-20T09:29:00-07:00"
* component[departureWindow].valuePeriod.end = "2026-08-20T09:31:00-07:00"
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitDeviceUsageDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Native Device Usage Recording"
Description: "The complete caller-encoded SensorKit device-usage report related to the structured summary."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:b4df30d0-2a34-492e-a68e-b1eab1cb471d|native-recording"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #current
* type = $sensorKitSourceType#device-usage "Device usage report"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T15:15:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit device usage report"
* content.attachment.data = "eyJ2ZXJzaW9uIjoiMSJ9"
* content.attachment.size = 15
* content.attachment.hash = "sHigu4BMVa0IJ0LR3NDJ5y8l4sc="
* context.related = Reference(SensorKitDeviceUsageExample)

Instance: SensorKitDeviceUsageProvenanceExample
InstanceOf: SensorKitConversionProvenance
Usage: #example
Title: "SensorKit Device-usage Conversion Provenance"
Description: "One conversion event targeting both the structured summary and required native Recording Document for the same source record."
* target[+] = Reference(SensorKitDeviceUsageExample)
* target[+] = Reference(SensorKitDeviceUsageDocumentExample)
* recorded = "2026-08-20T15:15:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $sensorKitRecordId
* entity.what.identifier.value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"

Instance: SensorKitExchangePatientExample
InstanceOf: Patient
Usage: #example
Title: "Exchange Bundle SensorKit Participant"
Description: "The Patient node in the deterministic SensorKit device-usage exchange Bundle."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "sensorkit-participant-001"

Instance: SensorKitExchangeDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "Exchange Bundle SensorKit Recording Device"
Description: "The watch node in the deterministic SensorKit device-usage exchange Bundle."
* identifier.system = "https://study.example.org/fhir/identifiers/device"
* identifier.value = "sensorkit-watch-001"
* status = #active
* manufacturer = "Example Manufacturer"
* type.text = "Watch"

Instance: SensorKitExchangeApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Exchange Bundle SensorKit Application"
Description: "The converting-application node in the deterministic SensorKit device-usage exchange Bundle."
* status = #active
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "sensorkit-mapper"
* deviceName[applicationName].name = "SensorKit Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: SensorKitExchangeDeviceUsageExample
InstanceOf: SensorKitDeviceUsageObservation
Usage: #example
Title: "Exchange Bundle SensorKit Device Usage Summary"
Description: "The structured device-usage output whose internal references use deterministic Bundle UUID URNs."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:b4df30d0-2a34-492e-a68e-b1eab1cb471d|device-usage-summary"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #final
* code = $sensorKitConcept#device-usage-summary "Device usage summary"
* subject.reference = "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"
* performer.reference = "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"
* effectivePeriod.start = "2026-08-20T08:00:00-07:00"
* effectivePeriod.end = "2026-08-20T08:15:00-07:00"
* valueQuantity = 372 's' "seconds"
* derivedFrom.reference = "urn:uuid:6f4e4010-4e0b-5f04-adf2-78b20c1a196b"
* component[screenWakes].code = $sensorKitConcept#screen-wakes "Screen wakes"
* component[screenWakes].valueQuantity = 6 '{count}' "{count}"
* component[unlocks].code = $sensorKitConcept#unlocks "Unlocks"
* component[unlocks].valueQuantity = 4 '{count}' "{count}"
* device.reference = "urn:uuid:7b38448e-4b35-5813-979a-65f2b724c703"

Instance: SensorKitExchangeDeviceUsageDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "Exchange Bundle SensorKit Native Device Usage Recording"
Description: "The raw device-usage output whose internal references use deterministic Bundle UUID URNs."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:b4df30d0-2a34-492e-a68e-b1eab1cb471d|native-recording"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #current
* type = $sensorKitSourceType#device-usage "Device usage report"
* subject.reference = "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"
* date = "2026-08-20T15:15:01Z"
* author.reference = "urn:uuid:7b38448e-4b35-5813-979a-65f2b724c703"
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit device usage report"
* content.attachment.data = "eyJ2ZXJzaW9uIjoiMSJ9"
* content.attachment.size = 15
* content.attachment.hash = "sHigu4BMVa0IJ0LR3NDJ5y8l4sc="
* context.related.reference = "urn:uuid:f83aa5e2-ed76-5ddb-a9eb-8d30858b8b55"

Instance: SensorKitExchangeDeviceUsageProvenanceExample
InstanceOf: SensorKitConversionProvenance
Usage: #example
Title: "Exchange Bundle SensorKit Device-usage Conversion Provenance"
Description: "One conversion event whose deterministic UUID targets cover both device-usage outputs of the same source record."
* target[+].reference = "urn:uuid:f83aa5e2-ed76-5ddb-a9eb-8d30858b8b55"
* target[+].reference = "urn:uuid:6f4e4010-4e0b-5f04-adf2-78b20c1a196b"
* recorded = "2026-08-20T15:15:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who.reference = "urn:uuid:247b668e-0fb3-5b9f-ac46-bd66c9536d8b"
* entity.role = #source
* entity.what.identifier.system = $sensorKitRecordId
* entity.what.identifier.value = "b4df30d0-2a34-492e-a68e-b1eab1cb471d"

Instance: SensorKitDeviceUsageExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "SensorKit Device-usage Exchange Bundle"
Description: "The mandated dual-output graph for one SensorKit device-usage record: the structured summary, its required native Recording Document, the shared devices, and one Provenance covering both outputs, with deterministic UUID URN fullUrls."
* identifier.system = "https://study.example.org/fhir/identifiers/exchange-bundle"
* identifier.value = "sensorkit-device-usage-20260820-001"
* type = #collection
* timestamp = "2026-08-20T15:15:01Z"
* entry[0].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/participant"
* entry[0].extension[entryIdentifier].valueIdentifier.value = "sensorkit-participant-001"
* entry[0].fullUrl = "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"
* entry[0].resource = SensorKitExchangePatientExample
* entry[1].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/device"
* entry[1].extension[entryIdentifier].valueIdentifier.value = "sensorkit-watch-001"
* entry[1].fullUrl = "urn:uuid:7b38448e-4b35-5813-979a-65f2b724c703"
* entry[1].resource = SensorKitExchangeDeviceExample
* entry[2].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/application"
* entry[2].extension[entryIdentifier].valueIdentifier.value = "sensorkit-mapper"
* entry[2].fullUrl = "urn:uuid:247b668e-0fb3-5b9f-ac46-bd66c9536d8b"
* entry[2].resource = SensorKitExchangeApplicationExample
* entry[3].extension[entryIdentifier].valueIdentifier.system = $sensorKitOutputId
* entry[3].extension[entryIdentifier].valueIdentifier.value = "6e7453a7-0045-5f96-a847-5a956a817dd4"
* entry[3].fullUrl = "urn:uuid:f83aa5e2-ed76-5ddb-a9eb-8d30858b8b55"
* entry[3].resource = SensorKitExchangeDeviceUsageExample
* entry[4].extension[entryIdentifier].valueIdentifier.system = $sensorKitOutputId
* entry[4].extension[entryIdentifier].valueIdentifier.value = "d42f2915-17ba-5891-a068-9a6a9d6732b6"
* entry[4].fullUrl = "urn:uuid:6f4e4010-4e0b-5f04-adf2-78b20c1a196b"
* entry[4].resource = SensorKitExchangeDeviceUsageDocumentExample
* entry[5].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/provenance"
* entry[5].extension[entryIdentifier].valueIdentifier.value = "device-usage-conversion-20260820-001"
* entry[5].fullUrl = "urn:uuid:4f82250f-1bf7-5c5f-b13a-d967fb3a9592"
* entry[5].resource = SensorKitExchangeDeviceUsageProvenanceExample

Instance: SensorKitAccelerometerDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Accelerometer Native Recording"
Description: "The caller-supplied native recording the summary counts, retained verbatim."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "8c910da2-ed1c-58c6-b2d9-fda1364d3acd"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:8c910da2-ed1c-58c6-b2d9-fda1364d3acd|native-recording"
* extension[sensorKitSourceType].valueCode = #accelerometer
* status = #current
* type = $sensorKitSourceType#accelerometer "Accelerometer"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit Accelerometer Native Recording"
* content.attachment.data = "eyJiYXRjaGVzIjoxMiwic2FtcGxlcyI6Mzg0MDB9"
* content.attachment.size = 30
* content.attachment.hash = "hQFxt+175NpnZIjpgDT0QoDkqH0="

Instance: SensorKitAccelerometerExample
InstanceOf: SensorKitAccelerometerObservation
Usage: #example
Title: "SensorKit Accelerometer Recording Summary"
Description: "A platform-exclusive coverage summary of one accelerometer batch; the recording document carries the signal."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "770e985b-a934-5a76-98da-2fb465055555"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:770e985b-a934-5a76-98da-2fb465055555|accelerometer-recording-summary"
* extension[sensorKitSourceType].valueCode = #accelerometer
* status = #final
* code = $sensorKitConcept#accelerometer-recording-summary "Accelerometer recording summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* derivedFrom = Reference(SensorKitAccelerometerDocumentExample)
* component[sampleCount].code = $sensorKitConcept#sample-count "Sample count"
* component[sampleCount].valueQuantity = 38400 '{count}'
* component[batchCount].code = $sensorKitConcept#batch-count "Batch count"
* component[batchCount].valueQuantity = 12 '{count}'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitPPGDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit PPG Native Recording"
Description: "The caller-supplied native recording the summary counts, retained verbatim."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "dbf9ec4d-b3fa-5315-9525-56ab63618b9a"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:dbf9ec4d-b3fa-5315-9525-56ab63618b9a|native-recording"
* extension[sensorKitSourceType].valueCode = #ppg
* status = #current
* type = $sensorKitSourceType#ppg "Photoplethysmogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit PPG Native Recording"
* content.attachment.data = "eyJyZWNvcmRzIjo0LCJvcHRpY2FsIjoyMDQ4MCwiYWNjZWxlcm9tZXRlciI6NTEyMH0="
* content.attachment.size = 50
* content.attachment.hash = "dDmCExc+PsQ3oVKFE/dphZDJFb4="

Instance: SensorKitPPGExample
InstanceOf: SensorKitPpgObservation
Usage: #example
Title: "SensorKit PPG Recording Summary"
Description: "A platform-exclusive coverage summary of one photoplethysmography recording."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "ea336fe9-c965-5921-aa55-98ee77c9a99e"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:ea336fe9-c965-5921-aa55-98ee77c9a99e|ppg-recording-summary"
* extension[sensorKitSourceType].valueCode = #ppg
* status = #final
* code = $sensorKitConcept#ppg-recording-summary "PPG recording summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* derivedFrom = Reference(SensorKitPPGDocumentExample)
* component[recordCount].code = $sensorKitConcept#record-count "Record count"
* component[recordCount].valueQuantity = 4 '{count}'
* component[opticalSampleCount].code = $sensorKitConcept#optical-sample-count "Optical sample count"
* component[opticalSampleCount].valueQuantity = 20480 '{count}'
* component[accelerometerSampleCount].code = $sensorKitConcept#accelerometer-sample-count "Accelerometer sample count"
* component[accelerometerSampleCount].valueQuantity = 5120 '{count}'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitMessagesUsageExample
InstanceOf: SensorKitMessagesUsageObservation
Usage: #example
Title: "SensorKit Messages Usage Summary"
Description: "A platform-exclusive messaging summary over one day, with no message content exchanged."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "05077f73-0625-5b44-a83a-c9a0fbed0849"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:05077f73-0625-5b44-a83a-c9a0fbed0849|messages-usage-summary"
* extension[sensorKitSourceType].valueCode = #messages-usage
* status = #final
* code = $sensorKitConcept#messages-usage-summary "Messages usage summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* component[incomingMessages].code = $sensorKitConcept#incoming-messages "Incoming messages"
* component[incomingMessages].valueQuantity = 34 '{count}'
* component[outgoingMessages].code = $sensorKitConcept#outgoing-messages "Outgoing messages"
* component[outgoingMessages].valueQuantity = 28 '{count}'
* component[uniqueContacts].code = $sensorKitConcept#unique-contacts "Unique contacts"
* component[uniqueContacts].valueQuantity = 9 '{count}'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitPhoneUsageExample
InstanceOf: SensorKitPhoneUsageObservation
Usage: #example
Title: "SensorKit Phone Usage Summary"
Description: "A platform-exclusive call summary over one day, with no call content or correspondent exchanged."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "fa4a2356-84a6-54be-b5b3-da5bec5b0067"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:fa4a2356-84a6-54be-b5b3-da5bec5b0067|phone-usage-summary"
* extension[sensorKitSourceType].valueCode = #phone-usage
* status = #final
* code = $sensorKitConcept#phone-usage-summary "Phone usage summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* valueQuantity = 1860 's'
* component[incomingCalls].code = $sensorKitConcept#incoming-calls "Incoming calls"
* component[incomingCalls].valueQuantity = 5 '{count}'
* component[outgoingCalls].code = $sensorKitConcept#outgoing-calls "Outgoing calls"
* component[outgoingCalls].valueQuantity = 3 '{count}'
* component[uniqueContacts].code = $sensorKitConcept#unique-contacts "Unique contacts"
* component[uniqueContacts].valueQuantity = 6 '{count}'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitKeyboardMetricsExample
InstanceOf: SensorKitKeyboardMetricsObservation
Usage: #example
Title: "SensorKit Keyboard Metrics Summary"
Description: "A platform-exclusive typing summary over one day; no typed text is exchanged."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "d2e21dfe-2ead-5b27-a31d-07ad1b95dac4"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:d2e21dfe-2ead-5b27-a31d-07ad1b95dac4|keyboard-metrics-summary"
* extension[sensorKitSourceType].valueCode = #keyboard-metrics
* status = #final
* code = $sensorKitConcept#keyboard-metrics-summary "Keyboard metrics summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* derivedFrom = Reference(SensorKitKeyboardMetricsDocumentExample)
* valueQuantity = 2400 's'
* component[totalWords].code = $sensorKitConcept#total-words "Total words"
* component[totalWords].valueQuantity = 1840 '{count}'
* component[totalAlteredWords].code = $sensorKitConcept#total-altered-words "Total altered words"
* component[totalAlteredWords].valueQuantity = 96 '{count}'
* component[totalTaps].code = $sensorKitConcept#total-taps "Total taps"
* component[totalTaps].valueQuantity = 9820 '{count}'
* component[totalDeletes].code = $sensorKitConcept#total-deletes "Total deletes"
* component[totalDeletes].valueQuantity = 412 '{count}'
* component[totalEmojis].code = $sensorKitConcept#total-emojis "Total emojis"
* component[totalEmojis].valueQuantity = 23 '{count}'
* component[totalAutocorrections].code = $sensorKitConcept#total-autocorrections "Total autocorrections"
* component[totalAutocorrections].valueQuantity = 57 '{count}'
* component[totalPauses].code = $sensorKitConcept#total-pauses "Total pauses"
* component[totalPauses].valueQuantity = 148 '{count}'
* component[totalTypingEpisodes].code = $sensorKitConcept#total-typing-episodes "Total typing episodes"
* component[totalTypingEpisodes].valueQuantity = 31 '{count}'
* component[typingSpeed].code = $sensorKitConcept#typing-speed "Typing speed"
* component[typingSpeed].valueQuantity = 0.77 '/s'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitSleepSessionExample
InstanceOf: SensorKitSleepSessionObservation
Usage: #example
Title: "SensorKit Sleep Session"
Description: "A platform-exclusive inferred sleep period, stating the exact length of its own interval."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "d9b729ee-589e-5beb-913e-f8f9057ef98a"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:d9b729ee-589e-5beb-913e-f8f9057ef98a|sleep-session"
* extension[sensorKitSourceType].valueCode = #sleep-sessions
* status = #final
* code = $sensorKitConcept#sleep-session "Sleep session"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* valueQuantity = 27000 's'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitKeyboardMetricsDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Keyboard Metrics Native Recording"
Description: "The caller-supplied native recording the summary counts, retained verbatim; no typed text is included."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "26521dbb-e8ab-529a-9ca8-8725d4ebdd1d"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:26521dbb-e8ab-529a-9ca8-8725d4ebdd1d|native-recording"
* extension[sensorKitSourceType].valueCode = #keyboard-metrics
* status = #current
* type = $sensorKitSourceType#keyboard-metrics "Keyboard Metrics"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit Keyboard Metrics Native Recording"
* content.attachment.data = "eyJlcGlzb2RlcyI6MzEsIndvcmRzIjoxODQwLCJ0YXBzIjo5ODIwfQ=="
* content.attachment.size = 40
* content.attachment.hash = "+Txt/nnCONsThnkqlptxXARG9Ig="

Instance: SensorKitWristTemperatureDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Wrist Temperature Recording"
Description: "The session's samples as the tabular recording the registry publishes for this stream."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "3f0a1c77-52b8-5d41-9a6e-7c1e58d0b2aa"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:3f0a1c77-52b8-5d41-9a6e-7c1e58d0b2aa|sensorkit-wrist-temperature"
* extension[sensorKitSourceType].valueCode = #wrist-temperature
* status = #current
* type = $sensorKitSourceType#wrist-temperature "Wrist temperature"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #text/csv
* content.format = $recordingFormat#sensorkit-wrist-temperature "SensorKit Wrist Temperature"
* content.format.version = "0.5.0"
* content.attachment.title = "SensorKit Wrist Temperature Recording"
* content.attachment.data = "dGltZXN0YW1wLHZhbHVlLGVycm9yRXN0aW1hdGUsY29uZGl0aW9uCjE3ODcwMDk0MDAuMCwzMy40LDAuMSwKMTc4NzAxMzAwMC4wLDMzLjcsMC4xLCJvZmZXcmlzdCxpbk1vdGlvbiIK"
* content.attachment.size = 105
* content.attachment.hash = "V1AsMqJkY8eDvsdWWR7YIUR/LsQ="

Instance: SensorKitWristTemperatureExample
InstanceOf: SensorKitWristTemperatureObservation
Usage: #example
Title: "SensorKit Wrist Temperature Recording Summary"
Description: "A platform-exclusive coverage summary of one wrist-temperature session; the recording document carries the samples."
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value = "3f0a1c77-52b8-5d41-9a6e-7c1e58d0b2aa"
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value = "v1:3f0a1c77-52b8-5d41-9a6e-7c1e58d0b2aa|wrist-temperature-recording-summary"
* extension[sensorKitSourceType].valueCode = #wrist-temperature
* status = #final
* code = $sensorKitConcept#wrist-temperature-recording-summary "Wrist temperature recording summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T23:10:00-07:00"
* effectivePeriod.end = "2026-08-21T06:40:00-07:00"
* derivedFrom = Reference(SensorKitWristTemperatureDocumentExample)
* component[sampleCount].code = $sensorKitConcept#sample-count "Sample count"
* component[sampleCount].valueQuantity = 2 '{count}' "{count}"
* extension[algorithmVersion].valueString = "1"
* device = Reference(SensorKitDeviceExample)
