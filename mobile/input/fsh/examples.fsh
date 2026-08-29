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
* uniqueId.value = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
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
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v0/test-key/1"
* identifier[physicalUnit].value = "v0:test-key:1:6MCZSHEfrM1QhfZn-Fw6afErSknFcKZvUJWbaCfXJkQ"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[eventSnapshot].value = "v0:test-key:1:0r6LXag2sC31FrT2G9Kr2cP-XtAdYpV_ZwKrRibE6CI"
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
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier.value = "v0:test-key:1:slBBD5_Givbgp2tKVh8PfQH2nf2xU2sq27J6B2e7iLg"
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
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:Q2sME_dGFj94xyprI1HtMokER94GYsHINZi0ilnsnRY"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:zWzm0Y6YnBhCPLB05VFK_MgY2Q0k35fz_M1AwJctAuw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:IarnucLc3veELjAFflufAwxnhn7k-6P0DPZw-Q06nlQ"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:wDJzInRAMviaEeH_3qneCxRQJTkaqm5hTdBmPAW97JU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:SUyjklEkKYJXiPuwqhjdcF4rbLgU8x7c098cbodlws0"
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:zWzm0Y6YnBhCPLB05VFK_MgY2Q0k35fz_M1AwJctAuw"

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
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:Q2sME_dGFj94xyprI1HtMokER94GYsHINZi0ilnsnRY"
* status = #active
* deviceName[applicationName].name = "Mobile Study"
* deviceName[applicationName].type = #user-friendly-name

Instance: GroveMobileExchangeHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Exchange Bundle Heart Rate"
Description: "A heart-rate node whose internal references use deterministic Bundle UUID URNs."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject.reference = "urn:uuid:d5137e30-79b1-5110-a09c-bd2528e25085"
* performer.reference = "urn:uuid:d5137e30-79b1-5110-a09c-bd2528e25085"
* effectiveDateTime = "2026-08-20T08:30:00.251-07:00"
* issued = "2026-08-20T17:30:02Z"
* valueQuantity = 72 '/min' "beats/minute"
* extension[gatewayDevice].valueReference.reference = "urn:uuid:aef62dba-db7e-5a99-a854-3b5ec312312f"

Instance: GroveMobileExchangeProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Exchange Bundle Conversion Provenance"
Description: "Conversion provenance whose target and assembler references resolve through deterministic Bundle UUID URNs."
* target.reference = "urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5"
* occurredDateTime = "2026-08-20T10:30:02-07:00"
* recorded = "2026-08-20T17:30:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:aef62dba-db7e-5a99-a854-3b5ec312312f"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"

Instance: GroveMobileExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "Deterministic Mobile Exchange Bundle"
Description: "One source-record conversion event with v0 event identity, typed entry keys, deterministic UUID URNs, and one conversion Provenance."
* identifier.type = GroveIdentifierRoleCS#event "Event"
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-event-v0"
* identifier.value = "e0:1f5c58aa-6ec6-4e79-a682-829a9debd3f5:42"
* type = #collection
* timestamp = "2026-08-20T17:30:02Z"
* entry[0].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#entry-node "Entry node"
* entry[0].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-entry-node-v0"
* entry[0].extension[entryNodeKey].valueIdentifier.value = "n0:patient:0:BMLA8cDb0x8fjNhv70m6l8dDSHIk2zWfOScLokevBQQ"
* entry[0].fullUrl = "urn:uuid:d5137e30-79b1-5110-a09c-bd2528e25085"
* entry[0].resource = GroveMobileExchangePatientExample
* entry[1].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[1].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[1].extension[entryNodeKey].valueIdentifier.value = "v0:test-key:1:Q2sME_dGFj94xyprI1HtMokER94GYsHINZi0ilnsnRY"
* entry[1].fullUrl = "urn:uuid:aef62dba-db7e-5a99-a854-3b5ec312312f"
* entry[1].resource = GroveMobileExchangeApplicationExample
* entry[2].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#source-output "Source output"
* entry[2].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* entry[2].extension[entryNodeKey].valueIdentifier.value = "v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"
* entry[2].fullUrl = "urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5"
* entry[2].resource = GroveMobileExchangeHeartRateExample
* entry[3].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#entry-node "Entry node"
* entry[3].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-entry-node-v0"
* entry[3].extension[entryNodeKey].valueIdentifier.value = "n0:conversion-provenance:0:8JmcQF7rmULm9uJBkHWruJwfMu3GJTxGWqXWn2DGqWk"
* entry[3].fullUrl = "urn:uuid:71abc484-b9ee-511e-b22a-5b35d026d620"
* entry[3].resource = GroveMobileExchangeProvenanceExample

Instance: GroveMobileRetractionProvenanceExample
InstanceOf: GroveMobileRetractionProvenance
Usage: #example
Title: "Example Mobile Retraction Provenance"
Description: "A later append-only assertion that the source record behind the exchange example is no longer exposed. The logical target identifies the exact prior output without copying it or requesting a FHIR DELETE."
* target.type = "Observation"
* target.identifier.type = GroveIdentifierRoleCS#source-output "Source output"
* target.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* target.identifier.value = "v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"
* target.extension[targetRole].valueCode = #primary-output
* occurredDateTime = "2026-08-21T08:00:00Z"
* recorded = "2026-08-21T08:00:01Z"
* activity = GroveLifecycleEventCS#source-record-retracted "Source record retracted"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.type = "Device"
* agent[assembler].who.identifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* agent[assembler].who.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* agent[assembler].who.identifier.value = "v0:test-key:1:JUZooa4NZX-rlMn9-NC8W078xzEuUO9X3Xo1mgk0Vac"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"

Instance: GroveMobileRetractionBundleExample
InstanceOf: GroveMobileRetractionBundle
Usage: #example
Title: "Example Mobile Retraction Bundle"
Description: "One immutable retraction event containing only its lifecycle Provenance. Repository deletion or status projection remains a separate deployment policy."
* identifier.type = GroveIdentifierRoleCS#event "Event"
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-event-v0"
* identifier.value = "e0:1f5c58aa-6ec6-4e79-a682-829a9debd3f5:43"
* type = #collection
* timestamp = "2026-08-21T08:00:01Z"
* entry[0].extension[entryNodeKey].valueIdentifier.type = GroveIdentifierRoleCS#entry-node "Entry node"
* entry[0].extension[entryNodeKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-entry-node-v0"
* entry[0].extension[entryNodeKey].valueIdentifier.value = "n0:retraction-provenance:0:o0Qrv-QfsfhozEJ5jeXVloNGbKrhYM9Rk6eziKoPmV4"
* entry[0].fullUrl = "urn:uuid:f99194b8-aaf8-5fdb-91fa-19309bdd6716"
* entry[0].resource = GroveMobileRetractionProvenanceExample

Instance: GroveMobileWriterRecordIdentityExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Writer Record Identity and Version"
Description: "One measurement carrying opaque source, exact output, and writer identities. The writer HMAC includes the complete writing-application Identifier pair and is comparable only within the configured deployment key epoch."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:zT15-qZa1ZBiSNVchkZ-Wpdf1FuX2PFomttu-7UEq2w"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:lCAE3ge3khFSSMmAGHi7M6XICSfaVnc6EjaWsofB4-Y"
* identifier[writerRecord].system = "https://study.example.org/fhir/NamingSystem/grove-writer-record-v0/test-key/1"
* identifier[writerRecord].value = "v0:test-key:1:qxujzFH9irQKon1KMxiN8jK8ahVB36Fq0JIKoBDNa2s"
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
