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
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v0/test-key/1"
* identifier[physicalUnit].value = "v0:test-key:1:cJAjPtBEVCTnnwsMUKciYeJx6OfRsikB6q-K3SWVFKs"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[eventSnapshot].value = "v0:test-key:1:ATVCLxSureccbQ7AwmvG6NNLUi_ZS4Puw5HD7HonXPI"
* status = #active
* manufacturer = "Example Manufacturer"
* type.text = "Watch"

Instance: SensorKitApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "SensorKit Converting Application"
Description: "The application that transforms already-obtained SensorKit records into the FHIR graph."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:oPo1uGEd7tR0bTNv5UKq2L-4mHGX86JdNrqB3aYW1LE"
* deviceName[applicationName].name = "SensorKit Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: SensorKitRotationRateExample
InstanceOf: SensorKitObservation
Usage: #example
Title: "SensorKit Rotation Rate Sampled Data"
Description: "A lossless, uniformly sampled three-axis rotation-rate stream that declares exactly the source-neutral SampledData profile and the SensorKit adapter profile."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-sampled-data-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:4BxIRTHcopOlCM3qYdI5WAXBsQ4fsPM0f7zkh9yIE3U"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Wf6QiPG60utBF3pWSe5pdn0_3L069JjNkaHdZT5tsek"
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:4BxIRTHcopOlCM3qYdI5WAXBsQ4fsPM0f7zkh9yIE3U"

Instance: SensorKitECGExample
InstanceOf: SensorKitECGObservation
Usage: #example
Title: "SensorKit ECG Waveform Projection"
Description: "The complete uniform voltage projection of one SensorKit ECG record. The linked native document preserves exact session state and per-voltage flags."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:76FsTE1X6aQawWHO18g8d5XXd5Uz_rdVVv0FmRwYWro"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Kl4ausf7Z199v2a16mys61TcdDHntBqGXtajOC7EAz8"
* extension[sensorKitSourceType].valueCode = #ecg
* method = $sensorKitValue#guided "Guided"
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
Description: "The exact native encoding supplied as input, retaining session identifiers/states and each signalInvalid and crownTouched flag."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:76FsTE1X6aQawWHO18g8d5XXd5Uz_rdVVv0FmRwYWro"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:DbNtRutwVjAHgEhLYZW2eQTL_vhcapgBU0RLHEBVlkM"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:6fKmMekWJIaGf8AymXhAXaVHBrodZgX7PtzyTWWVfhs"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:10:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.attachment.title = "SensorKit ECG native recording"
* content.attachment.data = "W3siZGF0ZSI6MTc4NzI0MjIwMCwiZnJlcXVlbmN5IjoyNTAsInNlc3Npb24iOnsiaWRlbnRpZmllciI6InNlc3Npb24tMSIsInN0YXRlIjoiYmVnaW4iLCJndWlkYW5jZSI6Imd1aWRlZCJ9LCJsZWFkIjoibGVmdEFybU1pbnVzUmlnaHRBcm0iLCJkYXRhIjpbeyJ2YWx1ZU1pY3Jvdm9sdHMiOjExLCJzaWduYWxJbnZhbGlkIjpmYWxzZSwiY3Jvd25Ub3VjaGVkIjpmYWxzZX0seyJ2YWx1ZU1pY3Jvdm9sdHMiOjIzLCJzaWduYWxJbnZhbGlkIjpmYWxzZSwiY3Jvd25Ub3VjaGVkIjp0cnVlfV19LHsiZGF0ZSI6MTc4NzI0MjIwMC4wMDgsImZyZXF1ZW5jeSI6MjUwLCJzZXNzaW9uIjp7ImlkZW50aWZpZXIiOiJzZXNzaW9uLTEiLCJzdGF0ZSI6ImVuZCIsImd1aWRhbmNlIjoiZ3VpZGVkIn0sImxlYWQiOiJsZWZ0QXJtTWludXNSaWdodEFybSIsImRhdGEiOlt7InZhbHVlTWljcm92b2x0cyI6LTUsInNpZ25hbEludmFsaWQiOnRydWUsImNyb3duVG91Y2hlZCI6ZmFsc2V9LHsidmFsdWVNaWNyb3ZvbHRzIjoxNCwic2lnbmFsSW52YWxpZCI6ZmFsc2UsImNyb3duVG91Y2hlZCI6ZmFsc2V9XX1d"
* content.attachment.size = 561
* content.attachment.hash = "W4B/lt8nJTh3oDg8TjKFjkU8e8s="
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:76FsTE1X6aQawWHO18g8d5XXd5Uz_rdVVv0FmRwYWro"

Instance: SensorKitInverseECGExample
InstanceOf: SensorKitECGObservation
Usage: #example
Title: "SensorKit Inverse-Lead ECG Waveform Projection"
Description: "A complete right-arm-minus-left-arm voltage projection. The exact SensorKit orientation is retained without falsely labeling the inverse signal as standard MDC Lead I."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:FluAVez_GqSsN-wxONF3sTBeHGtcZsVWZjkEq1VOlYw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:97el2-1gfqhpi_jsiekJ9wIf5EB7gn2ce4icmqB5Yg8"
* extension[sensorKitSourceType].valueCode = #ecg
* method = $sensorKitValue#unguided "Unguided"
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
Description: "The exact native encoding supplied as input and paired with the inverse-lead waveform projection."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:FluAVez_GqSsN-wxONF3sTBeHGtcZsVWZjkEq1VOlYw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:T8xgXxrTPYnLktrFMRgjnJV7qBPN4hWq_tcfPv8iTYQ"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:Ls_eIsD_nwV5bYLJAiea6XwylflrVfM8UmsEYhqLbvg"
* extension[sensorKitSourceType].valueCode = #ecg
* status = #current
* type = $sensorKitSourceType#ecg "Electrocardiogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T16:12:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.attachment.title = "SensorKit inverse-lead ECG native recording"
* content.attachment.data = "W3siZGF0ZSI6MTc4NzI0MjMyMCwiZnJlcXVlbmN5IjoyNTAsInNlc3Npb24iOnsiaWRlbnRpZmllciI6InNlc3Npb24tMiIsInN0YXRlIjoiYmVnaW4iLCJndWlkYW5jZSI6InVuZ3VpZGVkIn0sImxlYWQiOiJyaWdodEFybU1pbnVzTGVmdEFybSIsImRhdGEiOlt7InZhbHVlTWljcm92b2x0cyI6LTExLCJzaWduYWxJbnZhbGlkIjpmYWxzZSwiY3Jvd25Ub3VjaGVkIjpmYWxzZX0seyJ2YWx1ZU1pY3Jvdm9sdHMiOi0yMywic2lnbmFsSW52YWxpZCI6ZmFsc2UsImNyb3duVG91Y2hlZCI6ZmFsc2V9XX0seyJkYXRlIjoxNzg3MjQyMzIwLjAwOCwiZnJlcXVlbmN5IjoyNTAsInNlc3Npb24iOnsiaWRlbnRpZmllciI6InNlc3Npb24tMiIsInN0YXRlIjoiZW5kIiwiZ3VpZGFuY2UiOiJ1bmd1aWRlZCJ9LCJsZWFkIjoicmlnaHRBcm1NaW51c0xlZnRBcm0iLCJkYXRhIjpbeyJ2YWx1ZU1pY3Jvdm9sdHMiOjUsInNpZ25hbEludmFsaWQiOmZhbHNlLCJjcm93blRvdWNoZWQiOmZhbHNlfSx7InZhbHVlTWljcm92b2x0cyI6LTE0LCJzaWduYWxJbnZhbGlkIjpmYWxzZSwiY3Jvd25Ub3VjaGVkIjpmYWxzZX1dfV0="
* content.attachment.size = 569
* content.attachment.hash = "LJkRtgfqcnS8o6cMLcTkR6chaMU="
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:FluAVez_GqSsN-wxONF3sTBeHGtcZsVWZjkEq1VOlYw"

Instance: SensorKitOnWristExample
InstanceOf: SensorKitOnWristObservation
Usage: #example
Title: "SensorKit On-Wrist State"
Description: "A platform-exclusive on-wrist state with wrist and crown placement preserved as coded components."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:_7eqYcBO_DDk58N5Kz_QQLJ3-GgSmjVTQc0kxUyrB5k"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:kEmAt3XZJHC6iL0gPMgaYapBnqZISF8PeY-R3pAcUQs"
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
Description: "A platform-exclusive device-usage summary linked to the complete native representation required to retain the report's detailed fields."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:XfBsB8DhhwPTDdRigZOhN_7GmlkBWaF0veZtk8sEyhg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:KcWbN61Kb4btfwStg6WyYmqzCp-0-HPfE-pXZzHaXDU"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:kP5btUbyueJgz9hwgKwSvNNyD1v1fv6Q4l2u8-S0Ezk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:TbZW_QIQaipAkG9f78z4on1taf1KOiIYhM8l9Zaxng0"
* extension[sensorKitSourceType].valueCode = #visits
* focus.type = "Location"
* focus.identifier.system = "https://study.example.org/fhir/NamingSystem/sensorkit-visit-location/example-store"
* focus.identifier.value = "0f1f2c48-2b45-4a2a-9a2a-8b4d3a2f61c7"
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
Description: "The complete native SensorKit device-usage report, including text-input-session detail, related to the structured summary."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:XfBsB8DhhwPTDdRigZOhN_7GmlkBWaF0veZtk8sEyhg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Xy0TRPU4svxS-cj-cv0U48zTjvs5nlVF1CYL85p-7nM"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:G4Gb_IbIQ7BUhTlwmHngwOrL7Zk1Lx0xMtKXxIikoNw"
* extension[sensorKitSourceType].valueCode = #device-usage
* status = #current
* type = $sensorKitSourceType#device-usage "Device usage report"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-20T15:15:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.attachment.title = "SensorKit device usage report"
* content.attachment.data = "eyJ0aW1lc3RhbXAiOjE3ODcyMzgwMDAsImR1cmF0aW9uIjo5MDAsInRvdGFsU2NyZWVuV2FrZXMiOjYsInRvdGFsVW5sb2NrcyI6NCwidG90YWxVbmxvY2tEdXJhdGlvbiI6MzcyLCJ2ZXJzaW9uIjoiMSIsImFwcFVzYWdlQnlDYXRlZ29yeSI6eyJwcm9kdWN0aXZpdHkiOlt7ImJ1bmRsZUlkZW50aWZpZXIiOiJjb20uYXBwbGUubW9iaWxlbm90ZXMiLCJyZXBvcnRBcHBsaWNhdGlvbklkZW50aWZpZXIiOiJyZXBvcnQtYXBwLTEiLCJyZWxhdGl2ZVN0YXJ0VGltZSI6MCwidXNhZ2VUaW1lIjo0ODAsInN1cHBsZW1lbnRhbENhdGVnb3JpZXMiOlt7ImlkZW50aWZpZXIiOiJ3cml0aW5nIn1dLCJ0ZXh0SW5wdXRTZXNzaW9ucyI6W3siZHVyYXRpb24iOjQyLCJzZXNzaW9uVHlwZVJhd1ZhbHVlIjowLCJpZGVudGlmaWVyIjoidGV4dC1zZXNzaW9uLTEifV19XX0sIm5vdGlmaWNhdGlvblVzYWdlQnlDYXRlZ29yeSI6eyJwcm9kdWN0aXZpdHkiOlt7ImJ1bmRsZUlkZW50aWZpZXIiOiJjb20uYXBwbGUubW9iaWxlbm90ZXMiLCJldmVudFJhd1ZhbHVlIjowfV19LCJ3ZWJVc2FnZUJ5Q2F0ZWdvcnkiOnsicHJvZHVjdGl2aXR5IjpbeyJ0b3RhbFVzYWdlVGltZSI6MTIwfV19fQ=="
* content.attachment.size = 604
* content.attachment.hash = "G0xkrUr5NvJP9Tj9yjkJfrNRYnE="
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:XfBsB8DhhwPTDdRigZOhN_7GmlkBWaF0veZtk8sEyhg"

Instance: SensorKitAccelerometerDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Accelerometer Recording"
Description: "The exact registered triaxial-acceleration CSV recording; the summary sample count is its row count and the batch count is its number of distinct (device, identifier) batch keys."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:CW66aVk17hvflRLE5a5jxQDRZcADhAsl72KS5DcFHPk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:TXEs94g5XfkLxdOmbOtIGj80pfTNx71xoqodcZr7M0E"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:Cqoq0yba1Ifpmg4qRYM856KJIaeSnd_jowLobIMoYOs"
* extension[sensorKitSourceType].valueCode = #accelerometer
* status = #current
* type = $sensorKitSourceType#accelerometer "Accelerometer"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-21T07:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #text/csv
* content.format = $recordingFormat#triaxial-acceleration-samples "Triaxial Acceleration Samples"
* content.attachment.title = "SensorKit Accelerometer Recording"
* content.attachment.data = "dGltZXN0YW1wLGlkZW50aWZpZXIseCx5LHosZGV2aWNlCjE3ODcyMDkyMDAsMTcsMC4xMjUsLTAuMjUsMSwiV2F0Y2g2LDE4IgoxNzg3MjA5MjAxLDE3LDAuNSwwLC0wLjUsIldhdGNoNiwxOCIKMTc4NzIwOTIwMiwxOCwtMSwwLjI1LDAuNzUsIldhdGNoNiwxOCIK"
* content.attachment.size = 150
* content.attachment.hash = "bhtlVICnAmczd5WmihC2XNLCqh4="
* context.related = Reference(SensorKitAccelerometerExample)

Instance: SensorKitAccelerometerExample
InstanceOf: SensorKitAccelerometerObservation
Usage: #example
Title: "SensorKit Accelerometer Recording Summary"
Description: "A platform-exclusive coverage summary of one accelerometer recording spanning two CoreMotion delivery batches; the recording document carries the signal."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:CW66aVk17hvflRLE5a5jxQDRZcADhAsl72KS5DcFHPk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:qOsiHr9nD4PS7UEo-SdztDf9ghKUR3bVnrFsDJgMNAg"
* extension[sensorKitSourceType].valueCode = #accelerometer
* status = #final
* code = $sensorKitConcept#accelerometer-recording-summary "Accelerometer recording summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* derivedFrom = Reference(SensorKitAccelerometerDocumentExample)
* component[sampleCount].code = $sensorKitConcept#sample-count "Sample count"
* component[sampleCount].valueQuantity = 3 '{count}'
* component[batchCount].code = $sensorKitConcept#batch-count "Batch count"
* component[batchCount].valueQuantity = 2 '{count}'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitPPGDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit PPG Recording"
Description: "The exact registered Grove PPG binary recording; the summary record and sample counts are derived from its wire structure."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:lv-YI8qLPCHshC4TUz8qJ2QWPZDRLLApR6xdBQ-ZLL4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ip2jjPRDObV174zYvFBjPw0HxOOTxO63VJi_3YpfsQY"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:gYk6u2hngAyUkQ1dBsb63ODkIrzcS0RXYaWNplpL9bE"
* extension[sensorKitSourceType].valueCode = #ppg
* status = #current
* type = $sensorKitSourceType#ppg "Photoplethysmogram"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-21T07:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/octet-stream
* content.format = $recordingFormat#photoplethysmogram-samples "Photoplethysmogram Samples"
* content.attachment.title = "SensorKit PPG Recording"
* content.attachment.data = "AUHaoal8AAAAAgABAXUBAwIBAgQ/8AAAAAAAAEAAAAAAAAAAQBAAAAAAAAAFAQFjAT/wAAAAAAAAv/AAAAAAAABAAAAAAAAAAMAAAAAAAAAAAT/gAAAAAAAAAQZAIAAAAAAAAD/wAAAAAAAAv/AAAAAAAAAAAAAAAAAAAA=="
* content.attachment.size = 124
* content.attachment.hash = "EUIYvP3929camULujA1TxHgSHco="
* context.related = Reference(SensorKitPPGExample)

Instance: SensorKitPPGExample
InstanceOf: SensorKitPpgObservation
Usage: #example
Title: "SensorKit PPG Recording Summary"
Description: "A platform-exclusive coverage summary of one photoplethysmography recording."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:lv-YI8qLPCHshC4TUz8qJ2QWPZDRLLApR6xdBQ-ZLL4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:CvYcwUuKHWQNYqVo7eJ6tFfsSZzN5nyxkzafY3tfk34"
* extension[sensorKitSourceType].valueCode = #ppg
* status = #final
* code = $sensorKitConcept#ppg-recording-summary "PPG recording summary"
* subject = Reference(SensorKitPatientExample)
* performer = Reference(SensorKitPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* derivedFrom = Reference(SensorKitPPGDocumentExample)
* component[recordCount].code = $sensorKitConcept#record-count "Record count"
* component[recordCount].valueQuantity = 1 '{count}'
* component[opticalSampleCount].code = $sensorKitConcept#optical-sample-count "Optical sample count"
* component[opticalSampleCount].valueQuantity = 1 '{count}'
* component[accelerometerSampleCount].code = $sensorKitConcept#accelerometer-sample-count "Accelerometer sample count"
* component[accelerometerSampleCount].valueQuantity = 1 '{count}'
* device = Reference(SensorKitDeviceExample)

Instance: SensorKitMessagesUsageExample
InstanceOf: SensorKitMessagesUsageObservation
Usage: #example
Title: "SensorKit Messages Usage Summary"
Description: "A platform-exclusive messaging summary over one day, with no message content exchanged."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:89hMXwON-GI4HU4F2Yf0GWnrjExd2P5rRUKqZtQe42M"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:8UFB5V29t-MWIv712BKoioygFP5GX-SNH9OSY6klvXI"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:owCR_CUowP_G8XZLKsvzTNZ_hnkKiFwcgEkGIFde4yE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:nsHR-huO799guEVij2P3R9DwHAY1E8GIrN-vSlCpxL8"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:hwbq6DQCv0dfJGQ0p5ukI1aHpKkC_0DNrxWA1gEDXVc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:b3TCfbWFiP7lV5V7zZAw2g08O2QDY3BY6teiVbhJMeE"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ufvuXYMV4jIwMtsf8xLbLQ__GQLXRtCeT3R0ayaXsCY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:I0Vio7owRxnIwv-yv65VNyaUuzls7XiZbmeBu2ZdUsY"
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
Description: "One deployment-defined native JSON recording retained verbatim alongside the summary, with no typed text. Its member layout is illustrative; native-recording standardizes only the JSON container."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:hwbq6DQCv0dfJGQ0p5ukI1aHpKkC_0DNrxWA1gEDXVc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ENqth_sZIu2arNr1B1g0AiRrsgjwYv4yohUE9VP4Gys"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:nE5fDGQkgetCt1_5ReL_VyrQhElonwW9SppWKx9w49U"
* extension[sensorKitSourceType].valueCode = #keyboard-metrics
* status = #current
* type = $sensorKitSourceType#keyboard-metrics "Keyboard Metrics"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-21T07:05:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #application/json
* content.format = $recordingFormat#native-recording "Native Recording"
* content.attachment.title = "SensorKit Keyboard Metrics Native Recording"
* content.attachment.data = "W3sidGltZXN0YW1wIjoxNzg3MjA5MjAwLCJkdXJhdGlvbiI6ODY0MDAsImNvdW50cyI6eyJ0b3RhbFdvcmRzIjoxODQwLCJ0b3RhbEFsdGVyZWRXb3JkcyI6OTYsInRvdGFsVGFwcyI6OTgyMCwidG90YWxEZWxldGVzIjo0MTIsInRvdGFsRW1vamlzIjoyMywidG90YWxBdXRvQ29ycmVjdGlvbnMiOjU3LCJ0b3RhbFBhdXNlcyI6MTQ4LCJ0b3RhbFR5cGluZ0VwaXNvZGVzIjozMX0sInRvdGFsVHlwaW5nRHVyYXRpb24iOjI0MDAsInR5cGluZ1NwZWVkIjo0Ni4yLCJkdXJhdGlvbk1ldHJpY3MiOnsidG91Y2hEb3duVXAiOnsidmFsdWVzIjpbXX19fV0="
* content.attachment.size = 311
* content.attachment.hash = "3WCpc/XQYJr8t20BHOEQ7b3gdHQ="
* context.related = Reference(SensorKitKeyboardMetricsExample)

Instance: SensorKitWristTemperatureDocumentExample
InstanceOf: SensorKitRecordingDocument
Usage: #example
Title: "SensorKit Wrist Temperature Recording"
Description: "The session's samples as the tabular recording the registry publishes for this stream."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:IDoldR5FPgZopz5g1M8zbxOJvT47lhhUSqYX4hHkS48"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:A5bz9a4Cdhiy6FvIU-0V3WJvdoRU9Skn2bho3tZlVtw"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:rMp0yG6wJvv_5xyjUUeW0ILCTYKFgHnB0V8ZF9zaX6k"
* extension[sensorKitSourceType].valueCode = #wrist-temperature
* status = #current
* type = $sensorKitSourceType#wrist-temperature "Wrist temperature"
* subject = Reference(SensorKitPatientExample)
* date = "2026-08-21T13:45:01Z"
* author = Reference(SensorKitDeviceExample)
* content.attachment.contentType = #text/csv
* content.format = $recordingFormat#wrist-temperature-samples "Wrist Temperature Samples"
* content.attachment.title = "SensorKit Wrist Temperature Recording"
* content.attachment.data = "dGltZXN0YW1wLHZhbHVlLGVycm9yRXN0aW1hdGUsY29uZGl0aW9uCjE3ODcyOTI2MDAuMCwzMy40LDAuMSwKMTc4NzMxOTYwMC4wLDMzLjcsMC4xLCJvZmZXcmlzdCxpbk1vdGlvbiIK"
* content.attachment.size = 105
* content.attachment.hash = "G/F1UpQcjqnwuE8LjU18aDVYovM="
* context.related = Reference(SensorKitWristTemperatureExample)

Instance: SensorKitWristTemperatureExample
InstanceOf: SensorKitWristTemperatureObservation
Usage: #example
Title: "SensorKit Wrist Temperature Recording Summary"
Description: "A platform-exclusive coverage summary of one wrist-temperature session; the recording document carries the samples."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:IDoldR5FPgZopz5g1M8zbxOJvT47lhhUSqYX4hHkS48"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:GDPMVuQo5y6EUG5lT4fA-FiCmE0CK_nlTVY4W8KFOtU"
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
