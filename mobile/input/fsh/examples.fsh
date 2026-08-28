//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: MobileSourceRecordIdentifierExample
InstanceOf: NamingSystem
Usage: #example
Title: "Example Opaque Source-record Identifier Namespace"
Description: "An example deployment-owned namespace for one HMAC key epoch and source-record identity kind. Production deployments define their own immutable URI and managed key."
* name = "MobileSourceRecordIdentifierExample"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Example Study"
* uniqueId.type = #uri
* uniqueId.value = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
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
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v2/test-key/1"
* identifier[physicalUnit].value = "v2:test-key:1:bzipB2Az_xUAOsp4kBM4nhu8YS4VyLh3vPsk0mL3GbA"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[eventSnapshot].value = "v2:test-key:1:odRE_bG_NLjZD3lKvvC0w0JNPrfE3UCfDQ1YLkl2SnY"
* status = #active
* deviceName.name = "Study Watch"
* deviceName.type = #user-friendly-name
* manufacturer = "Example Device Company"
* modelNumber = "Watch One"
* type.text = "Wrist-worn heart-rate sensor"
* version.type = $mdc#531976 "MDC_ID_PROD_SPEC_FW"
* version.value = "2.1"

Instance: GroveHostDeviceExample
InstanceOf: GroveHostDevice
Usage: #example
Title: "Example Host Device Snapshot"
Description: "The immutable event-time host hardware and operating-system snapshot for the converting application."
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier.value = "v2:test-key:1:DbSfJZHKtuBgKm24kZBazM3NW5Veo8_fXyUpU3KhOGk"
* status = #active
* manufacturer = "Example Device Company"
* modelNumber = "Phone One"
* deviceName.name = "Study Phone"
* deviceName.type = #user-friendly-name
* version[operatingSystemVersion].type = $groveApplicationVersionType#os-version "Operating system version"
* version[operatingSystemVersion].value = "20.1"

Instance: GroveApplicationDeviceExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Example Gateway and Converting Application"
Description: "The application received the measurement from the recording device, routed it into the study workflow, and assembled the FHIR Observation."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:UEdJx7eiKElpKK_oPmjTu3fK072oUz8JKwgtF0CBe8A"
* deviceName[applicationName].name = "Mobile Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "3.2.0"
* version[applicationBuild].type = $groveApplicationVersionType#build "Build"
* version[applicationBuild].value = "32014"
* parent = Reference(GroveHostDeviceExample)

Instance: GroveMobileHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Source-neutral Mobile Heart Rate"
Description: "An automatically recorded heart-rate measurement with stable identity, recording device, gateway application, study context, and full-precision time."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:D2f2lnPlZ6XI5L3uOVJrhpLE55ltpgC6sNXRv8_65D4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:LmIAsdN9oEgV7BHugInyYfqBh5ZfTKlAbeSyLqMvAuA"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:9uojWOy5j4L7kQ9_w-eU6gDoTOjICCd2Lx4NbaWk3uU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:3-yg_WPl-eQYQYz1IxH086jzdKqK1mEnpB3Sosi3QTc"
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
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:D2f2lnPlZ6XI5L3uOVJrhpLE55ltpgC6sNXRv8_65D4"

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
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:UEdJx7eiKElpKK_oPmjTu3fK072oUz8JKwgtF0CBe8A"
* status = #active
* deviceName[applicationName].name = "Mobile Study"
* deviceName[applicationName].type = #user-friendly-name

Instance: GroveMobileExchangeHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Exchange Bundle Heart Rate"
Description: "A heart-rate node whose internal references use deterministic Bundle UUID URNs."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:1y-KjnPSgOBDI5pE69EVN8U7Oaen_WM4cPL-sBxDKgw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:_sudqhgnrCDWXSytfxliI_fzd0qjFUMFobOIMP6Z5gw"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject.reference = "urn:uuid:3314ab4c-4ab3-536f-a556-e3b6ff97762d"
* performer.reference = "urn:uuid:3314ab4c-4ab3-536f-a556-e3b6ff97762d"
* effectiveDateTime = "2026-08-20T08:30:00.251-07:00"
* issued = "2026-08-20T17:30:02Z"
* valueQuantity = 72 '/min' "beats/minute"
* extension[gatewayDevice].valueReference.reference = "urn:uuid:8f87a88a-8744-5116-8901-9274f62472ac"

Instance: GroveMobileExchangeProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Exchange Bundle Conversion Provenance"
Description: "Conversion provenance whose target and assembler references resolve through deterministic Bundle UUID URNs."
* target.reference = "urn:uuid:13bc1990-e0d8-57cf-8772-8f959664241d"
* occurredDateTime = "2026-08-20T10:30:02-07:00"
* recorded = "2026-08-20T17:30:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:8f87a88a-8744-5116-8901-9274f62472ac"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:1y-KjnPSgOBDI5pE69EVN8U7Oaen_WM4cPL-sBxDKgw"

Instance: GroveMobileExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "Deterministic Mobile Exchange Bundle"
Description: "One source-record conversion event with v2 event identity, typed entry keys, deterministic UUID URNs, and one conversion Provenance."
* identifier.type = GroveIdentifierRoleCS#event "Event"
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-event-v2"
* identifier.value = "e2:1f5c58aa-6ec6-4e79-a682-829a9debd3f5:42"
* type = #collection
* timestamp = "2026-08-20T17:30:02Z"
* entry[0].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#entry-node "Entry node"
* entry[0].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-entry-node-v2"
* entry[0].extension[entryNodeKey].valueIdentifier.value = "n2:patient:0:wMhqO_kIRVFR8etQrCbgX0FXhz7h3f-LnsfUhRcrC9A"
* entry[0].fullUrl = "urn:uuid:3314ab4c-4ab3-536f-a556-e3b6ff97762d"
* entry[0].resource = GroveMobileExchangePatientExample
* entry[1].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[1].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* entry[1].extension[entryNodeKey].valueIdentifier.value = "v2:test-key:1:UEdJx7eiKElpKK_oPmjTu3fK072oUz8JKwgtF0CBe8A"
* entry[1].fullUrl = "urn:uuid:8f87a88a-8744-5116-8901-9274f62472ac"
* entry[1].resource = GroveMobileExchangeApplicationExample
* entry[2].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#source-output "Source output"
* entry[2].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* entry[2].extension[entryNodeKey].valueIdentifier.value = "v2:test-key:1:_sudqhgnrCDWXSytfxliI_fzd0qjFUMFobOIMP6Z5gw"
* entry[2].fullUrl = "urn:uuid:13bc1990-e0d8-57cf-8772-8f959664241d"
* entry[2].resource = GroveMobileExchangeHeartRateExample
* entry[3].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#entry-node "Entry node"
* entry[3].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-entry-node-v2"
* entry[3].extension[entryNodeKey].valueIdentifier.value = "n2:conversion-provenance:0:SwGD7C4DT5_9kgIOQ9h7W8I4UdwJPuEOnkh2TgQVwko"
* entry[3].fullUrl = "urn:uuid:9908feb7-0370-5f06-a689-f8afa210eb41"
* entry[3].resource = GroveMobileExchangeProvenanceExample

Instance: GroveMobileRetractionProvenanceExample
InstanceOf: GroveMobileRetractionProvenance
Usage: #example
Title: "Example Mobile Retraction Provenance"
Description: "A later append-only assertion that the source record behind the exchange example is no longer exposed. The logical target identifies the exact prior output without copying it or requesting a FHIR DELETE."
* target.type = "Observation"
* target.identifier.type = GroveIdentifierRoleCS#source-output "Source output"
* target.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* target.identifier.value = "v2:test-key:1:_sudqhgnrCDWXSytfxliI_fzd0qjFUMFobOIMP6Z5gw"
* target.extension[targetRole].valueCode = #primary-output
* occurredDateTime = "2026-08-21T08:00:00Z"
* recorded = "2026-08-21T08:00:01Z"
* activity = GroveLifecycleEventCS#source-record-retracted "Source record retracted"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.type = "Device"
* agent[assembler].who.identifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* agent[assembler].who.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* agent[assembler].who.identifier.value = "v2:test-key:1:4hdZeDHmzYotDYvBYG1H5YZPDtfGbMiEftruwDvait4"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:1y-KjnPSgOBDI5pE69EVN8U7Oaen_WM4cPL-sBxDKgw"

Instance: GroveMobileRetractionBundleExample
InstanceOf: GroveMobileRetractionBundle
Usage: #example
Title: "Example Mobile Retraction Bundle"
Description: "One immutable retraction event containing only its lifecycle Provenance. Repository deletion or status projection is a separate receiver policy."
* identifier.type = GroveIdentifierRoleCS#event "Event"
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-event-v2"
* identifier.value = "e2:1f5c58aa-6ec6-4e79-a682-829a9debd3f5:43"
* type = #collection
* timestamp = "2026-08-21T08:00:01Z"
* entry[0].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#entry-node "Entry node"
* entry[0].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-entry-node-v2"
* entry[0].extension[entryNodeKey].valueIdentifier.value = "n2:retraction-provenance:0:kry9tA8wKNb5VGuzulTG-msyl6iRqHJuR2y1eK-7VOc"
* entry[0].fullUrl = "urn:uuid:39f1693a-d1b3-597c-998f-0837dbd1d6d1"
* entry[0].resource = GroveMobileRetractionProvenanceExample

Instance: GroveMobileWriterRecordIdentityExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Writer Record Identity and Version"
Description: "One measurement carrying opaque source, exact output, and writer identities. The writer HMAC includes the complete writing-application Identifier pair and is comparable only within the configured deployment key epoch."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:S1wLvSKL_nUEK2cigKX92ley7RDPxOUvHmyqJAMNhvw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:yqxk1YXMuiPMVGsaEOdzhM4kdj9Uvj4XmTdQpHyBB3E"
* identifier[writerRecord].system = "https://study.example.org/fhir/NamingSystem/grove-writer-record-v2/test-key/1"
* identifier[writerRecord].value = "v2:test-key:1:b6CrOt2Bn8qBpBi_0IesPTPhIzN5DbRQLPz_Di3GfSQ"
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
* extension[writerRecordVersion].valueString = "3"
