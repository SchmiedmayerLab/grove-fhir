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
* identifier[sensorKitOutputId].value = "746739c0-630c-581d-8808-f12114c2adf9"
* extension[sensorKitSourceType].valueCode = #rotation-rate
* status = #final
* code = $sensorKitSourceType#rotation-rate "Rotation rate"
* subject = Reference(SensorKitPatientExample)
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
* identifier[sensorKitOutputId].value = "36440490-b02b-5bc5-8542-7137a6525d57"
* extension[sensorKitSourceType].valueCode = #ecg
* extension[sensorKitECGSessionGuidance].valueCode = #guided
* status = #final
* code = $loinc#11524-6 "EKG study"
* subject = Reference(SensorKitPatientExample)
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
* identifier[sensorKitOutputId].value = "2db9ff85-802e-5e77-a26c-9801fcef1211"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:10:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
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
* identifier[sensorKitOutputId].value = "9c118a12-360d-5f31-908c-a806cf1296ce"
* extension[sensorKitSourceType].valueCode = #ecg
* extension[sensorKitECGSessionGuidance].valueCode = #unguided
* status = #final
* code = $loinc#11524-6 "EKG study"
* subject = Reference(SensorKitPatientExample)
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
* identifier[sensorKitOutputId].value = "e3bf91bb-f79f-544d-b7e5-d67b46552b67"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:12:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
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
* identifier[sensorKitOutputId].value = "cfdca78b-4ff3-5a97-9576-c878247b1ea3"
* extension[sensorKitSourceType].valueCode = #on-wrist
* status = #final
* code = $sensorKitConcept#on-wrist-state "On-wrist state"
* subject = Reference(SensorKitPatientExample)
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
* identifier[sensorKitOutputId].value = "6e7453a7-0045-5f96-a847-5a956a817dd4"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #final
* code = $sensorKitConcept#device-usage-summary "Device usage summary"
* subject = Reference(SensorKitPatientExample)
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
* identifier[sensorKitOutputId].value = "d703cbe1-eb28-5132-8d08-adefe8842fb9"
* extension[sensorKitSourceType].valueCode = #visits
* status = #final
* code = $sensorKitConcept#visit-summary "Visit summary"
* subject = Reference(SensorKitPatientExample)
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
* identifier[sensorKitOutputId].value = "d42f2915-17ba-5891-a068-9a6a9d6732b6"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #current
* type = $sensorKitSourceType#device-usage "Device usage report"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T15:15:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
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
* identifier[sensorKitOutputId].value = "6e7453a7-0045-5f96-a847-5a956a817dd4"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #final
* code = $sensorKitConcept#device-usage-summary "Device usage summary"
* subject.reference = "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"
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
* identifier[sensorKitOutputId].value = "d42f2915-17ba-5891-a068-9a6a9d6732b6"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #current
* type = $sensorKitSourceType#device-usage "Device usage report"
* subject.reference = "urn:uuid:d66ce444-2f05-5661-ac7c-86f080cf3be4"
* date = "2026-08-20T15:15:01Z"
* author.reference = "urn:uuid:7b38448e-4b35-5813-979a-65f2b724c703"
* content.attachment.contentType = #application/json
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
