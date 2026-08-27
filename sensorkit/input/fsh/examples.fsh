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
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v2/test-key/1"
* identifier[physicalUnit].value = "v2:test-key:1:pZx5ARahj8YybkJ6Gjp4bsGxqjS8ZCMopkZnaWSYxw8"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[eventSnapshot].value = "v2:test-key:1:Z6nW3akX-P_h7spZl-NPAMbDwSSV4bUdE09Kq4xClPU"
* status = #active
* manufacturer = "Example Manufacturer"
* type.text = "Watch"

Instance: SensorKitApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "SensorKit Converting Application"
Description: "The application that transforms already-obtained SensorKit records into the FHIR graph."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:sGzDek4hAO9SOAmIvnvd32NDtO3UMIwm9nQgw8uV6u4"
* deviceName[applicationName].name = "SensorKit Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: SensorKitRotationRateExample
InstanceOf: SensorKitObservation
Usage: #example
Title: "SensorKit Rotation Rate Sampled Data"
Description: "A lossless, uniformly sampled three-axis rotation-rate stream that declares exactly the source-neutral SampledData profile and the SensorKit adapter profile."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-sampled-data-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:l2gfZ5lmjsq1zyyetPQRKy7Jenb5IDqebysEAZITzgg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:bfdPkNW0Ktj7fR0jaHCCyFKDlUs8Z-uHOogEZzVcxzc"
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
* occurredDateTime = "2026-08-20T16:00:01Z"
* recorded = "2026-08-20T16:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:l2gfZ5lmjsq1zyyetPQRKy7Jenb5IDqebysEAZITzgg"

Instance: SensorKitECGExample
InstanceOf: SensorKitECGObservation
Usage: #example
Title: "SensorKit ECG Waveform Projection"
Description: "The complete uniform voltage projection of one SensorKit ECG record. The linked native document preserves exact session state and per-voltage flags."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ac2HjtTOXQDORJ2XHpbfgSjGDtg4bGkT2kxWzroHlfY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:GV8ntg6BUwB9gzp_p7-yXghTfdQxrr8jklm0dMNyq10"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ac2HjtTOXQDORJ2XHpbfgSjGDtg4bGkT2kxWzroHlfY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:G8awxhxHEz8ZFRNusODCHf_ySeVFp4D2NzJ7Y7NHwzQ"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:9sarugkGUGjpBWI7jDWFRvKwIXcnellduGuZJIa9BvI"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:10:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.6.0"
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
* occurredDateTime = "2026-08-20T16:10:01Z"
* recorded = "2026-08-20T16:10:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:ac2HjtTOXQDORJ2XHpbfgSjGDtg4bGkT2kxWzroHlfY"

Instance: SensorKitInverseECGExample
InstanceOf: SensorKitECGObservation
Usage: #example
Title: "SensorKit Inverse-Lead ECG Waveform Projection"
Description: "A complete right-arm-minus-left-arm voltage projection. The exact SensorKit orientation is retained without falsely labeling the inverse signal as standard MDC Lead I."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:myQG-o3YVMi0V_DUDxq9v9ZoLTqv5h3zA0iKdKDjhLk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:R4qVfHx16m6XqwZAaIQypVGaXs0jM9LDHmIEj69-3MI"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:myQG-o3YVMi0V_DUDxq9v9ZoLTqv5h3zA0iKdKDjhLk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:_yjlPg27loh2lpj8Btpsv62galfMGDIYf3w5w9r6NwM"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:XIWtNdBjvjSOzRLjZzHjpliWPhwO9jMw1VuKFMD_cmY"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:12:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.6.0"
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
* occurredDateTime = "2026-08-20T16:12:01Z"
* recorded = "2026-08-20T16:12:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:myQG-o3YVMi0V_DUDxq9v9ZoLTqv5h3zA0iKdKDjhLk"

Instance: SensorKitOnWristExample
InstanceOf: SensorKitOnWristObservation
Usage: #example
Title: "SensorKit On-Wrist State"
Description: "A platform-exclusive on-wrist state with wrist and crown placement preserved as coded components."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:76xrc23iIo43pWzlzlRR_UjBx-w7TFxaq0_2kLXdGYA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Yr0URSoyUaiOEkhEXsc6PetgVyz29A1yoH_NEv_Tp1c"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ct2xsuoLAjG1lDQTq8kvZ-59YXjBr84LPF8Adi-x6eE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ey9U9SGqloQ8RIGcBQLPw1NDNuUovyfwlUcmbKDODcE"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Fcp7ZKx7zBfpgWqSKQLonZejqEIADXyD2_PwQ3H3HaU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:85uYi-Nuuw3FayWI5QOwrbzTKez6mf42VPaqcaXgQis"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ct2xsuoLAjG1lDQTq8kvZ-59YXjBr84LPF8Adi-x6eE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:NsQH4D0yoTsbEg9zuUMwbqAKqFbJq808gDQqXlWZJm0"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:GrBgxM7stWNYtCREHYwGKKLjcPbW3NWeV_rRZQNqN1o"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #current
* type = $sensorKitSourceType#device-usage "Device usage report"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T15:15:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.6.0"
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
* occurredDateTime = "2026-08-20T15:15:01Z"
* recorded = "2026-08-20T15:15:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(SensorKitApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:ct2xsuoLAjG1lDQTq8kvZ-59YXjBr84LPF8Adi-x6eE"

Instance: SensorKitAccelerometerDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Accelerometer Native Recording"
Description: "The caller-supplied native recording the summary counts, retained verbatim."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:0JhbYSp9rL1xSNT54SvNzZy21A-6hk_6V6bNTMWIWFY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:MgYzsIbvnOMqCZo62N2hHS5EViq0jj_dcJdpMG6ibvE"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:Ab1aDqzRnHWev3hwA6-aA1piCAUjiDow56UYJPmOmN0"
* extension[sensorKitSourceType].valueCode = #accelerometer
* status = #current
* type = $sensorKitSourceType#accelerometer "Accelerometer"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.6.0"
* content.attachment.title = "SensorKit Accelerometer Native Recording"
* content.attachment.data = "eyJiYXRjaGVzIjoxMiwic2FtcGxlcyI6Mzg0MDB9"
* content.attachment.size = 30
* content.attachment.hash = "hQFxt+175NpnZIjpgDT0QoDkqH0="

Instance: SensorKitAccelerometerExample
InstanceOf: SensorKitAccelerometerObservation
Usage: #example
Title: "SensorKit Accelerometer Recording Summary"
Description: "A platform-exclusive coverage summary of one accelerometer batch; the recording document carries the signal."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:iqb1xhsDDgfXV8dvC6deRLElb4x1AD4E5JfirNlGZAY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:nlnKQRmSfCeCAKWQcvhgcCYClkjPzw47i3XxW1gI6e8"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:1tbd8L9Z0bPIFyuWU2sbn4vE9ehz7_4O7x-Jpcf07VM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:5pHXgLN0e_NbLgrZKIiWnDZr0NVz_x6Pr9JAnFiK18Y"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:wmMOstcQARC59bJixk40KTFhuZQMxL-3_0lIdtVfbxk"
* extension[sensorKitSourceType].valueCode = #ppg
* status = #current
* type = $sensorKitSourceType#ppg "Photoplethysmogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.6.0"
* content.attachment.title = "SensorKit PPG Native Recording"
* content.attachment.data = "eyJyZWNvcmRzIjo0LCJvcHRpY2FsIjoyMDQ4MCwiYWNjZWxlcm9tZXRlciI6NTEyMH0="
* content.attachment.size = 50
* content.attachment.hash = "dDmCExc+PsQ3oVKFE/dphZDJFb4="

Instance: SensorKitPPGExample
InstanceOf: SensorKitPpgObservation
Usage: #example
Title: "SensorKit PPG Recording Summary"
Description: "A platform-exclusive coverage summary of one photoplethysmography recording."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:7g-OWHqFsb_VDw18-ORHuQRy_pbQsOGcZ-loa8rY83Y"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Gi2GxhmFGtuptw0fDLCo3a6JN46sIActl6tN99Zf578"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:EuQ0wjPlf3WlHAHve789RdIE4hSOuUpDbnvds3gRF9o"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:m4vdB0HZ2L2gCXVs74My4p9kwChOwAV0tfiBYRbEuZ0"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:YabFITOApqbwWJmX4wm2hruN5XoG5Zt-Cu1Uoco5puQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:kMJsIpan1DN4kfIVXfzys1Z8xrxTK0dr5_r4WbqHsqs"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:dF8LX4Kgxqjmpx639kWx8W8mrP618r05Cg7RC7keG50"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:pQajw81Zv2jCxDR_B7lBvxUfF3BM_obAMMO8YKQJe9s"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:-Nz5f9Byc6XFojwdQDQonz_N3hxEYtydeyTnrq7pjLo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:dtohiYJL5elrXExtE36Faz1k-1VZzYRl_UPnNI3zC38"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:4t4s3c9Gth-bAFbBwSqdvnwG6IlwuBsC-8WH9wF_29Y"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:V2iSB2I08t2seGTD1qNuuW4EJFfU1qr7tE-YsGeicTI"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:WzC5ecUhiXzYafh6W6p920RMOd4ooq259CjMnjHytkI"
* extension[sensorKitSourceType].valueCode = #keyboard-metrics
* status = #current
* type = $sensorKitSourceType#keyboard-metrics "Keyboard Metrics"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/vnd.grovealliance.native+json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.format.version = "0.6.0"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:2MTU8Q2G2VrQfESUK5yekG4pDTEfvM0xaS95wHM62uw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:EDhCEvmB2oD9ou6qWFML1-TZV-A3MOrZommBPTyvteA"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:_rPn57PcaIOtFHihenAYBVzistgCkAb1-Vy2SsZXcd4"
* extension[sensorKitSourceType].valueCode = #wrist-temperature
* status = #current
* type = $sensorKitSourceType#wrist-temperature "Wrist temperature"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #text/csv
* content.format = $recordingFormat#wrist-temperature-samples "Wrist Temperature Samples"
* content.format.version = "0.6.0"
* content.attachment.title = "SensorKit Wrist Temperature Recording"
* content.attachment.data = "dGltZXN0YW1wLHZhbHVlLGVycm9yRXN0aW1hdGUsY29uZGl0aW9uCjE3ODcwMDk0MDAuMCwzMy40LDAuMSwKMTc4NzAxMzAwMC4wLDMzLjcsMC4xLCJvZmZXcmlzdCxpbk1vdGlvbiIK"
* content.attachment.size = 105
* content.attachment.hash = "V1AsMqJkY8eDvsdWWR7YIUR/LsQ="

Instance: SensorKitWristTemperatureExample
InstanceOf: SensorKitWristTemperatureObservation
Usage: #example
Title: "SensorKit Wrist Temperature Recording Summary"
Description: "A platform-exclusive coverage summary of one wrist-temperature session; the recording document carries the samples."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:2MTU8Q2G2VrQfESUK5yekG4pDTEfvM0xaS95wHM62uw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:9kkL-lpmHyhnjgL7NQnyQ5XK0CYKotPs9v02BHhmRuE"
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
