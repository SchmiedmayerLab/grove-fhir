//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: HealthKitPatientExample
InstanceOf: Patient
Usage: #example
Title: "HealthKit Example Participant"
Description: "The Patient referenced by the HealthKit adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-hk-001"

Instance: HealthKitStudyPlanExample
InstanceOf: PlanDefinition
Usage: #example
Title: "HealthKit Study Protocol"
Description: "The versioned study protocol governing the HealthKit example collection."
* url = "https://study.example.org/fhir/PlanDefinition/healthkit-study-protocol"
* version = "2026.08"
* name = "HealthKitStudyProtocol"
* title = "HealthKit Study Protocol"
* status = #active
* experimental = false
* date = "2026-08-19"
* publisher = "Example Study"
* description = "Collect heart rate, step count, and manually entered body weight from HealthKit."

Instance: HealthKitResearchStudyExample
InstanceOf: ResearchStudy
Usage: #example
Title: "HealthKit Research Study"
Description: "A ResearchStudy whose protocol references the exact PlanDefinition revision used for collection."
* identifier.system = "https://study.example.org/fhir/identifiers/research-study"
* identifier.value = "healthkit-study"
* title = "Example HealthKit Study"
* protocol = Reference(HealthKitStudyPlanExample)
* status = #active

Instance: HealthKitResearchSubjectExample
InstanceOf: ResearchSubject
Usage: #example
Title: "HealthKit Research Subject"
Description: "The participant's enrollment in the HealthKit example study."
* identifier.system = "https://study.example.org/fhir/identifiers/research-subject"
* identifier.value = "healthkit-study-participant-hk-001"
* status = #on-study
* period.start = "2026-08-01"
* study = Reference(HealthKitResearchStudyExample)
* individual = Reference(HealthKitPatientExample)

Instance: HealthKitRecordingDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "HealthKit Recording Device"
Description: "The watch reported by HealthKit as the physical recorder for the passive examples."
* status = #active
* deviceName.name = "Study Watch"
* deviceName.type = #user-friendly-name
* manufacturer = "Apple Inc."
* modelNumber = "Watch"
* type.text = "Wrist-worn sensor"
* version.type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version.value = "11.2"

Instance: HealthKitApplicationDeviceExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "HealthKit Converting Application"
Description: "The application that read the HealthKit objects and transformed them into FHIR resources. It is a Provenance agent, not the recording device."
* status = #active
* identifier.system = $appleBundleId
* identifier.value = "org.grovealliance.example"
* deviceName[applicationName].name = "Grove Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "1.4.0"

Instance: HealthKitSourceApplicationDeviceExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "HealthKit Source Application"
Description: "The application reported by HKSourceRevision as the author of the source HealthKit object. It is distinct from the application that converted the object to FHIR."
* status = #active
* identifier.system = $appleBundleId
* identifier.value = "com.example.health-source"
* deviceName[applicationName].name = "Example Health Source"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "4.7.2"

Instance: HealthKitBluetoothSourceDeviceExample
InstanceOf: Device
Usage: #example
Title: "HealthKit Bluetooth Source Device"
Description: "A supported Bluetooth Low Energy source explicitly classified by the producer. Its opaque HealthKit source identifier is included only under an authorized exchange policy."
* status = #active
* identifier.system = $healthKitSourceDeviceId
* identifier.value = "c614cf5b-8a89-4a50-a5c8-78c1a8397f63"
* deviceName.name = "Example Bluetooth Source"
* deviceName.type = #user-friendly-name

Instance: HealthKitHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Heart Rate"
Description: "A passive HealthKit heart-rate sample with the standard clinical profile and an allowlisted motion-context value."
* meta.profile[+] = "http://hl7.org/fhir/StructureDefinition/heartrate"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "1e091e2a-9f3e-49cd-b237-2ef5a3d0f213"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00.251-07:00"
* effectiveDateTime.extension[timezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 72 '/min' "beats/minute"
* device = Reference(HealthKitRecordingDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)
* component[heartRateMotionContext].code = $healthKitMetadataKey#HKMetadataKeyHeartRateMotionContext "Heart Rate Motion Context"
* component[heartRateMotionContext].valueCodeableConcept = $healthKitHeartRateMotionContext#sedentary "Sedentary"

Instance: HealthKitStepCountObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Step Count"
Description: "A HealthKit interval sample preserving the recorded count of 1,042 steps over one hour."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "f1e2d3c4-4b5a-4c6d-8e9f-1234567890ab"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#step-count-total "Step count total"
* subject = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T09:00:00-07:00"
* effectivePeriod.start.extension[startTimezone].valueCode = #America/Los_Angeles
* effectivePeriod.end = "2026-08-19T10:00:00-07:00"
* effectivePeriod.end.extension[endTimezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(HealthKitRecordingDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitBluetoothHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Bluetooth Heart Rate"
Description: "A heart-rate sample imported directly from a supported Bluetooth Low Energy heart-rate monitor under an exchange policy that permits the source identifier."
* meta.profile[+] = "http://hl7.org/fhir/StructureDefinition/heartrate"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "d7f395c0-7e4a-4eb8-943d-5e32dc70071a"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:45:00.251-07:00"
* effectiveDateTime.extension[timezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T17:45:02.000Z"
* valueQuantity = 78 '/min' "beats/minute"
* device = Reference(HealthKitBluetoothSourceDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitManuallyEnteredBodyWeightExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Manually Entered Body Weight"
Description: "A body weight with an explicit HealthKit user-entered indication mapped to manual-entry."
* meta.profile[+] = "http://hl7.org/fhir/StructureDefinition/bodyweight"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "a4b6fbcd-a358-4b2b-bea5-eb1ed80a8a63"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T08:15:00-07:00"
* effectiveDateTime.extension[timezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T15:15:01.000Z"
* valueQuantity = 68.4 'kg' "kg"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#manual-entry "Manual entry"
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitConversionProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "HealthKit Conversion Provenance"
Description: "The application transformed the HealthKit object identified as the source entity into the heart-rate Observation."
* target = Reference(HealthKitHeartRateObservationExample)
* occurredDateTime = "2026-08-19T10:30:02-07:00"
* recorded = "2026-08-19T17:30:02.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value = "1e091e2a-9f3e-49cd-b237-2ef5a3d0f213"
* entity.agent.type = $provenanceParticipantType#author "Author"
* entity.agent.who = Reference(HealthKitSourceApplicationDeviceExample)

Instance: HealthKitBluetoothSourceProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "HealthKit Bluetooth Source Provenance"
Description: "A producer-supplied Bluetooth heart-rate monitor authored the HealthKit object transformed into the Bluetooth heart-rate Observation."
* target = Reference(HealthKitBluetoothHeartRateObservationExample)
* occurredDateTime = "2026-08-19T10:45:02-07:00"
* recorded = "2026-08-19T17:45:02.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value = "d7f395c0-7e4a-4eb8-943d-5e32dc70071a"
* entity.agent.type = $provenanceParticipantType#author "Author"
* entity.agent.who = Reference(HealthKitBluetoothSourceDeviceExample)

Instance: HealthKitStudyBundleExample
InstanceOf: Bundle
Usage: #example
Title: "HealthKit Study Exchange Bundle"
Description: "A collection of the participant, versioned protocol, study enrollment, devices, converted Observations, and conversion Provenance."
* type = #collection
* timestamp = "2026-08-19T17:30:03.000Z"
* entry[+].fullUrl = "https://study.example.org/fhir/Patient/HealthKitPatientExample"
* entry[=].resource = HealthKitPatientExample
* entry[+].fullUrl = "https://study.example.org/fhir/PlanDefinition/HealthKitStudyPlanExample"
* entry[=].resource = HealthKitStudyPlanExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchStudy/HealthKitResearchStudyExample"
* entry[=].resource = HealthKitResearchStudyExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchSubject/HealthKitResearchSubjectExample"
* entry[=].resource = HealthKitResearchSubjectExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitRecordingDeviceExample"
* entry[=].resource = HealthKitRecordingDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitApplicationDeviceExample"
* entry[=].resource = HealthKitApplicationDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitSourceApplicationDeviceExample"
* entry[=].resource = HealthKitSourceApplicationDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthKitHeartRateObservationExample"
* entry[=].resource = HealthKitHeartRateObservationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthKitStepCountObservationExample"
* entry[=].resource = HealthKitStepCountObservationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthKitConversionProvenanceExample"
* entry[=].resource = HealthKitConversionProvenanceExample
