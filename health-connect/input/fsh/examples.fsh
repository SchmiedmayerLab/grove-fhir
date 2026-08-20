//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: HealthConnectPatientExample
InstanceOf: Patient
Usage: #example
Title: "Health Connect Example Participant"
Description: "The Patient referenced by the Health Connect adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-hc-001"

Instance: HealthConnectStudyPlanExample
InstanceOf: PlanDefinition
Usage: #example
Title: "Health Connect Study Protocol"
Description: "The versioned study protocol governing the Health Connect example collection."
* url = "https://study.example.org/fhir/PlanDefinition/health-connect-study-protocol"
* version = "2026.08"
* name = "HealthConnectStudyProtocol"
* title = "Health Connect Study Protocol"
* status = #active
* experimental = false
* date = "2026-08-19"
* publisher = "Example Study"
* description = "Collect heart rate, step count, and body weight through Health Connect."

Instance: HealthConnectResearchStudyExample
InstanceOf: ResearchStudy
Usage: #example
Title: "Health Connect Research Study"
Description: "A ResearchStudy whose protocol references the exact PlanDefinition revision used for collection."
* identifier.system = "https://study.example.org/fhir/identifiers/research-study"
* identifier.value = "health-connect-study"
* title = "Example Health Connect Study"
* protocol = Reference(HealthConnectStudyPlanExample)
* status = #active

Instance: HealthConnectResearchSubjectExample
InstanceOf: ResearchSubject
Usage: #example
Title: "Health Connect Research Subject"
Description: "The participant's enrollment in the Health Connect example study."
* identifier.system = "https://study.example.org/fhir/identifiers/research-subject"
* identifier.value = "health-connect-study-participant-hc-001"
* status = #on-study
* period.start = "2026-08-01"
* study = Reference(HealthConnectResearchStudyExample)
* individual = Reference(HealthConnectPatientExample)

Instance: HealthConnectRecordingDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "Health Connect Recording Device"
Description: "The watch supplied in Health Connect metadata as the physical device that recorded the passive examples."
* type.text = "Watch"
* manufacturer = "Example Devices"
* modelNumber = "Study Watch 2"

Instance: HealthConnectConverterApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Health Connect Converting Application"
Description: "The application that transformed Health Connect Records into FHIR resources."
* status = #active
* identifier.system = $androidPackageName
* identifier.value = "org.grovealliance.example"
* deviceName[applicationName].name = "Grove Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "1.4.0"

Instance: HealthConnectSourceApplicationExample
InstanceOf: Device
Usage: #example
Title: "Health Connect Data Origin Application"
Description: "The application identified by Health Connect DataOrigin.packageName as the enterer of the example Records. No display name or version is asserted because DataOrigin does not supply either value."
* identifier.system = $androidPackageName
* identifier.value = "com.example.wearable"

Instance: HealthConnectHeartRateSampleOneExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Heart Rate Sample One"
Description: "The first FHIR heart-rate Observation emitted from a Health Connect HeartRateRecord containing two samples."
* meta.profile[+] = "http://hl7.org/fhir/StructureDefinition/heartrate"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:5d81fd22df74bcb7d9571b201cadf87b3935072c126dffbc2af908d994d054a2"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:95e250a54a2ec574e981ab6fae82ac85ac77d9a03e805d5ba7967af0697faf6c"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T17:30:15Z"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 72 '/min' "beats/minute"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectHeartRateSampleTwoExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Heart Rate Sample Two"
Description: "The second FHIR heart-rate Observation emitted from the same Health Connect HeartRateRecord."
* meta.profile[+] = "http://hl7.org/fhir/StructureDefinition/heartrate"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:5d81fd22df74bcb7d9571b201cadf87b3935072c126dffbc2af908d994d054a2"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:906d2a041f2e73004a52f33c943b4c6a53759094c993747e2c3074c32733a66d"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T17:30:45Z"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 75 '/min' "beats/minute"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectBodyWeightExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Body Weight"
Description: "A manually entered Health Connect WeightRecord represented with the standard FHIR body-weight profile."
* meta.profile[+] = "http://hl7.org/fhir/StructureDefinition/bodyweight"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:9607c85191132deb33f7519e1487aa51c66292ff47c73f5a26fe75ea77418e57"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:13be909196c3762bf744e4cb185438e1f5c628b90f3f4a78c6793c6ad0c447b5"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T08:15:00-07:00"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 68.4 'kg' "kg"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#manual-entry "Manual entry"
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectStepCountExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Step Count"
Description: "A Health Connect StepsRecord preserving the source interval and count."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:2145220948c744c2f6ad52d58991c466bcb09cb0e81c986580bfb2f89b54a639"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:52c47544652e896224f9ecc987111949f5f97e3dcc1916fcbe9369309ed912c0"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#step-count-total "Step count total"
* subject = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T09:00:00-07:00"
* effectivePeriod.end = "2026-08-19T10:00:00-07:00"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectHeartRateProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Heart Rate Conversion Provenance"
Description: "One source HeartRateRecord was transformed into two FHIR heart-rate Observations."
* target[+] = Reference(HealthConnectHeartRateSampleOneExample)
* target[+] = Reference(HealthConnectHeartRateSampleTwoExample)
* occurredDateTime = "2026-08-19T18:00:00Z"
* recorded = "2026-08-19T18:00:00Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value = "v1:5d81fd22df74bcb7d9571b201cadf87b3935072c126dffbc2af908d994d054a2"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who = Reference(HealthConnectSourceApplicationExample)

Instance: HealthConnectBodyWeightProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Body Weight Conversion Provenance"
Description: "The source WeightRecord and DataOrigin application for the converted body-weight Observation."
* target = Reference(HealthConnectBodyWeightExample)
* occurredDateTime = "2026-08-19T18:00:00Z"
* recorded = "2026-08-19T18:00:00Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value = "v1:9607c85191132deb33f7519e1487aa51c66292ff47c73f5a26fe75ea77418e57"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who = Reference(HealthConnectSourceApplicationExample)

Instance: HealthConnectStepCountProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Step Count Conversion Provenance"
Description: "The source StepsRecord and DataOrigin application for the converted step-count Observation."
* target = Reference(HealthConnectStepCountExample)
* occurredDateTime = "2026-08-19T18:00:00Z"
* recorded = "2026-08-19T18:00:00Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value = "v1:2145220948c744c2f6ad52d58991c466bcb09cb0e81c986580bfb2f89b54a639"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who = Reference(HealthConnectSourceApplicationExample)

Instance: HealthConnectStudyBundleExample
InstanceOf: Bundle
Usage: #example
Title: "Health Connect Documentation Bundle"
Description: "An aggregate profile-validation fixture containing the participant, study context, devices, converted Observations, and source-linked conversion Provenance from several source records. It is not an operational synchronization event."
* type = #collection
* timestamp = "2026-08-19T18:00:00Z"
* entry[+].fullUrl = "https://study.example.org/fhir/Patient/HealthConnectPatientExample"
* entry[=].resource = HealthConnectPatientExample
* entry[+].fullUrl = "https://study.example.org/fhir/PlanDefinition/HealthConnectStudyPlanExample"
* entry[=].resource = HealthConnectStudyPlanExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchStudy/HealthConnectResearchStudyExample"
* entry[=].resource = HealthConnectResearchStudyExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchSubject/HealthConnectResearchSubjectExample"
* entry[=].resource = HealthConnectResearchSubjectExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthConnectRecordingDeviceExample"
* entry[=].resource = HealthConnectRecordingDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthConnectConverterApplicationExample"
* entry[=].resource = HealthConnectConverterApplicationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthConnectSourceApplicationExample"
* entry[=].resource = HealthConnectSourceApplicationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectHeartRateSampleOneExample"
* entry[=].resource = HealthConnectHeartRateSampleOneExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectHeartRateSampleTwoExample"
* entry[=].resource = HealthConnectHeartRateSampleTwoExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectBodyWeightExample"
* entry[=].resource = HealthConnectBodyWeightExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectStepCountExample"
* entry[=].resource = HealthConnectStepCountExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthConnectHeartRateProvenanceExample"
* entry[=].resource = HealthConnectHeartRateProvenanceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthConnectBodyWeightProvenanceExample"
* entry[=].resource = HealthConnectBodyWeightProvenanceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthConnectStepCountProvenanceExample"
* entry[=].resource = HealthConnectStepCountProvenanceExample
