//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: MobileObservationIdentifierExample
InstanceOf: NamingSystem
Usage: #example
Title: "Example Mobile Observation Identifier Namespace"
Description: "An example deployment-owned namespace for stable mobile Observation identifiers. Implementations define their own URI namespace."
* name = "MobileObservationIdentifierExample"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Example Study"
* uniqueId.type = #uri
* uniqueId.value = "https://study.example.org/fhir/identifiers/mobile-observation"
* uniqueId.preferred = true

Instance: GroveMobilePatientExample
InstanceOf: Patient
Usage: #example
Title: "Example Mobile Study Participant"
Description: "A minimal Patient used by the Mobile guide examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-001"

Instance: GroveMobileStudyPlanExample
InstanceOf: PlanDefinition
Usage: #example
Title: "Example Mobile Study Protocol"
Description: "The versioned protocol definition that governs the example study. PlanDefinition.version carries the study-definition revision."
* url = "https://study.example.org/fhir/PlanDefinition/mobile-study-protocol"
* version = "2026.08"
* name = "MobileStudyProtocol"
* title = "Mobile Study Protocol"
* status = #active
* experimental = false
* date = "2026-08-19"
* publisher = "Example Study"
* description = "Collect a daily mobile heart-rate measurement."

Instance: GroveMobileResearchStudyExample
InstanceOf: ResearchStudy
Usage: #example
Title: "Example Mobile Research Study"
Description: "The study associated with the example Observation. Its protocol points to the versioned PlanDefinition."
* identifier.system = "https://study.example.org/fhir/identifiers/research-study"
* identifier.value = "mobile-study"
* title = "Example Mobile Study"
* protocol = Reference(GroveMobileStudyPlanExample)
* status = #active
* description = "A study demonstrating the Grove Mobile exchange contract."

Instance: GroveMobileResearchSubjectExample
InstanceOf: ResearchSubject
Usage: #example
Title: "Example Mobile Research Subject"
Description: "The participant's enrollment in the example study."
* identifier.system = "https://study.example.org/fhir/identifiers/research-subject"
* identifier.value = "mobile-study-participant-001"
* status = #on-study
* period.start = "2026-08-01"
* study = Reference(GroveMobileResearchStudyExample)
* individual = Reference(GroveMobilePatientExample)

Instance: GroveRecordingDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "Example Recording Device"
Description: "The physical wrist-worn device that measured the example heart rate."
* status = #active
* deviceName.name = "Study Watch"
* deviceName.type = #user-friendly-name
* manufacturer = "Example Device Company"
* modelNumber = "Watch One"
* type.text = "Wrist-worn heart-rate sensor"
* version.type = $mdc#531976 "MDC_ID_PROD_SPEC_FW"
* version.value = "2.1"

Instance: GroveApplicationDeviceExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Example Gateway and Converting Application"
Description: "The application received the measurement from the recording device, routed it into the study workflow, and assembled the FHIR Observation."
* status = #active
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "org.example.mobile-study"
* deviceName[applicationName].name = "Mobile Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "3.2.0"

Instance: GroveMobileHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Source-neutral Mobile Heart Rate"
Description: "An automatically recorded heart-rate measurement with stable identity, recording device, gateway application, study context, and full-precision time."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "heart-rate-20260819-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00.251-07:00"
* effectiveDateTime.extension[timezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 72 '/min' "beats/minute"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* device = Reference(GroveRecordingDeviceExample)
* extension[gatewayDevice].valueReference = Reference(GroveApplicationDeviceExample)
* extension[researchStudy].valueReference = Reference(GroveMobileResearchStudyExample)

Instance: GroveMobileStepCountExample
InstanceOf: GroveMobileStepCount
Usage: #example
Title: "Source-neutral Mobile Step Count"
Description: "An interval step count with stable exchange identity, an exact source Period, a non-negative source count, recording device, and study context."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "step-count-20260819-001"
* status = #final
* category = $observationCategory#activity "Activity"
* code = GroveMobileMeasurementCS#step-count-total "Step count total"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T09:00:00-07:00"
* effectivePeriod.start.extension[startTimezone].valueCode = #America/Los_Angeles
* effectivePeriod.end = "2026-08-19T10:00:00-07:00"
* effectivePeriod.end.extension[endTimezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(GroveRecordingDeviceExample)
* extension[researchStudy].valueReference = Reference(GroveMobileResearchStudyExample)

Instance: GroveMobileConversionProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Example Mobile Conversion Provenance"
Description: "The application transformed the source record identified in Provenance.entity into the example Observation."
* target = Reference(GroveMobileHeartRateExample)
* occurredDateTime = "2026-08-19T10:30:02-07:00"
* recorded = "2026-08-19T17:30:02.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(GroveApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.system = "https://source.example.org/records"
* entity.what.identifier.value = "record-7351"

Instance: GroveMobileExchangePatientExample
InstanceOf: Patient
Usage: #example
Title: "Exchange Bundle Patient"
Description: "The Patient node in the deterministic exchange Bundle example."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-001"

Instance: GroveMobileExchangeApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Exchange Bundle Application"
Description: "The converting application node in the deterministic exchange Bundle example."
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "org.example.mobile-study"
* status = #active
* deviceName[applicationName].name = "Mobile Study"
* deviceName[applicationName].type = #user-friendly-name

Instance: GroveMobileExchangeHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Exchange Bundle Heart Rate"
Description: "A heart-rate node whose internal references use deterministic Bundle UUID URNs."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "heart-rate-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject.reference = "urn:uuid:9610c841-e815-599e-a2bf-9bdb688d6737"
* performer.reference = "urn:uuid:9610c841-e815-599e-a2bf-9bdb688d6737"
* effectiveDateTime = "2026-08-20T10:30:00-07:00"
* issued = "2026-08-20T17:30:02Z"
* valueQuantity = 72 '/min' "beats/minute"
* extension[gatewayDevice].valueReference.reference = "urn:uuid:7b4f430b-2fe2-5592-b879-e0ca6453bafe"

Instance: GroveMobileExchangeProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Exchange Bundle Conversion Provenance"
Description: "Conversion provenance whose target and assembler references resolve through deterministic Bundle UUID URNs."
* target.reference = "urn:uuid:cd27941b-2a75-5f7a-bd25-71e9480eac24"
* occurredDateTime = "2026-08-20T10:30:02-07:00"
* recorded = "2026-08-20T17:30:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:7b4f430b-2fe2-5592-b879-e0ca6453bafe"
* entity.role = #source
* entity.what.identifier.system = "https://source.example.org/records"
* entity.what.identifier.value = "record-7351"

Instance: GroveMobileExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "Deterministic Mobile Exchange Bundle"
Description: "A collection graph with deterministic UUID URN fullUrls and complete entry business identifiers."
* identifier.system = "https://study.example.org/fhir/identifiers/exchange-bundle"
* identifier.value = "exchange-20260820-001"
* type = #collection
* timestamp = "2026-08-20T17:30:02Z"
* entry[0].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/participant"
* entry[0].extension[entryIdentifier].valueIdentifier.value = "participant-001"
* entry[0].fullUrl = "urn:uuid:9610c841-e815-599e-a2bf-9bdb688d6737"
* entry[0].resource = GroveMobileExchangePatientExample
* entry[1].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/application"
* entry[1].extension[entryIdentifier].valueIdentifier.value = "org.example.mobile-study"
* entry[1].fullUrl = "urn:uuid:7b4f430b-2fe2-5592-b879-e0ca6453bafe"
* entry[1].resource = GroveMobileExchangeApplicationExample
* entry[2].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* entry[2].extension[entryIdentifier].valueIdentifier.value = "heart-rate-20260820-001"
* entry[2].fullUrl = "urn:uuid:cd27941b-2a75-5f7a-bd25-71e9480eac24"
* entry[2].resource = GroveMobileExchangeHeartRateExample
* entry[3].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/provenance"
* entry[3].extension[entryIdentifier].valueIdentifier.value = "conversion-20260820-001"
* entry[3].fullUrl = "urn:uuid:a0c89770-d357-5e23-aa5c-35ce7b249de7"
* entry[3].resource = GroveMobileExchangeProvenanceExample
