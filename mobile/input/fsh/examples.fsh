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
Description: "The physical wrist-worn device that measured the example heart rate. The device-snapshot identifier is its content key; the deployment's governed stable per-unit token gives it its recording-device unit key."
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v0/test-key/1"
* identifier[physicalUnit].value = "v0:test-key:1:6MCZSHEfrM1QhfZn-Fw6afErSknFcKZvUJWbaCfXJkQ"
* identifier[snapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[snapshot].value = "v0:test-key:1:aC-W5CzErQDjX3e9aNHd-pjPgYgDGkUJGjMZ0a0QI-M"
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
Description: "The immutable content snapshot of the host hardware and operating system on which the application converted the example."
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier.value = "v0:test-key:1:kNx7SybOxz-E8O4JYPluK5lXFbbpNcH3iC7SZsZCkFY"
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
Description: "The application received the measurement from the recording device, routed it into the study workflow, and assembled the FHIR Observation. Its parent is the host it ran on, so its content key changes when the host snapshot does."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:T3AsXl1ENiY6_9LS5Xkl1oqP9d7I4cKdGQpRAhyGIJ0"
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
Description: "The application transformed the source record identified in Provenance.entity into the example Observation. Its grove-record-version extension repeats the record-version key computed over this Provenance and the Observation it targets; the extension is excluded from that computation."
* extension[recordVersion].valueIdentifier.type = GroveIdentifierRoleCS#record-version "Record version"
* extension[recordVersion].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
* extension[recordVersion].valueIdentifier.value = "v0:test-key:1:iAdN9xk6Iq0FlJ9S2xsyo4mX_JTi3EVz3EByQ7kRO-M"
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
Description: "The shared Patient node of the exchange Bundle example. It carries its content key as a typed context-snapshot Identifier beside its business identifier, so it has the same key and fullUrl in every Bundle while its content is unchanged."
* identifier[+].system = "https://study.example.org/fhir/identifiers/participant"
* identifier[=].value = "participant-001"
* identifier[+].type = GroveIdentifierRoleCS#context-snapshot "Context snapshot"
* identifier[=].system = "https://study.example.org/fhir/NamingSystem/grove-context-snapshot-v0/test-key/1"
* identifier[=].value = "v0:test-key:1:3ZTiYqzi8xk9ZhSE3U_roFsDtUYoNTQ_CbWEDvOZwLQ"

Instance: GroveMobileExchangeHostExample
InstanceOf: GroveHostDevice
Usage: #example
Title: "Exchange Bundle Host"
Description: "The shared host node of the exchange and retraction Bundle examples, keyed by its content."
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier.value = "v0:test-key:1:01dJDxR9bIctHh_m-iQIOMvapXGnIq_0wmLCNEXTIvo"
* status = #active
* modelNumber = "Phone1,1"
* version[operatingSystemVersion].type = $groveApplicationVersionType#os-version "Operating system version"
* version[operatingSystemVersion].value = "20.1"

Instance: GroveMobileExchangeApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Exchange Bundle Application"
Description: "The shared converting application node of the exchange and retraction Bundle examples. Its parent reference names the host's content-derived fullUrl, so its own content key covers the host it ran on."
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:H9mN3DGJkpaJ785z-KtZ7dZ3Gz274Ea1sL2oGs3Jkf4"
* status = #active
* deviceName[applicationName].name = "Mobile Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "3.2.0"
* version[applicationBuild].type = $groveApplicationVersionType#build "Build"
* version[applicationBuild].value = "32014"
* parent.reference = "urn:uuid:76a3c913-b4e7-5299-b4ac-caf23054b231"

Instance: GroveMobileExchangeHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Exchange Bundle Heart Rate"
Description: "The output of the first record of the exchange Bundle example. Its literal references name the shared nodes' content-derived Bundle UUID URNs."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject.reference = "urn:uuid:a3a3368b-fb0f-5113-9d9d-7c651a4b96ca"
* effectiveDateTime = "2026-08-20T08:30:00.251-07:00"
* issued = "2026-08-20T17:30:02Z"
* valueQuantity = 72 '/min' "beats/minute"
* extension[gatewayDevice].valueReference.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"

Instance: GroveMobileExchangeProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Exchange Bundle Conversion Provenance"
Description: "The conversion Provenance of the first record. Its entry key is its record-version Identifier, repeated in grove-record-version; target and assembler references resolve through Bundle UUID URNs."
* extension[recordVersion].valueIdentifier.type = GroveIdentifierRoleCS#record-version "Record version"
* extension[recordVersion].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
* extension[recordVersion].valueIdentifier.value = "v0:test-key:1:1b32Y3AcBpsWou7Vw8hQfJ-R3_h-uIQgmaNzRPQ4Jus"
* target.reference = "urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5"
* occurredDateTime = "2026-08-20T10:30:02-07:00"
* recorded = "2026-08-20T17:30:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"

Instance: GroveMobileExchangeSecondHeartRateExample
InstanceOf: GroveMobileHeartRate
Usage: #example
Title: "Exchange Bundle Second Heart Rate"
Description: "The output of the second record of the exchange Bundle example. It references the same shared Patient and application as the first record, each of which appears once in the Bundle."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Ce4AD2kT5yierXkx5QJNFu7d8qqaSSQOCKGFeYpu2M0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:N8Rta5CkBmwGgJDKxdrh7xI0h9EgCKlQLPGxr7QRpAw"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject.reference = "urn:uuid:a3a3368b-fb0f-5113-9d9d-7c651a4b96ca"
* effectiveDateTime = "2026-08-20T08:35:00.251-07:00"
* issued = "2026-08-20T17:35:02Z"
* valueQuantity = 75 '/min' "beats/minute"
* extension[gatewayDevice].valueReference.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"

Instance: GroveMobileExchangeSecondProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Exchange Bundle Second Conversion Provenance"
Description: "The conversion Provenance of the second record, keyed by its own record-version Identifier."
* extension[recordVersion].valueIdentifier.type = GroveIdentifierRoleCS#record-version "Record version"
* extension[recordVersion].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
* extension[recordVersion].valueIdentifier.value = "v0:test-key:1:Fiz_W2KPmuHp0lqnmBcrjgY1hwfsHAAUuXNVq6LP05Q"
* target.reference = "urn:uuid:923c35c9-6909-5d65-89ac-ef130e9e019d"
* occurredDateTime = "2026-08-20T10:35:02-07:00"
* recorded = "2026-08-20T17:35:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:Ce4AD2kT5yierXkx5QJNFu7d8qqaSSQOCKGFeYpu2M0"

Instance: GroveMobileExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "Deterministic Mobile Exchange Bundle"
Description: "One upload of two heart-rate records of one participant. Each record is its Observation and one conversion Provenance keyed by its record-version Identifier. The two records share the Patient and the converting application with its host; each shared node is keyed by its content and appears once. The Bundle has no identifier: it is a container and names no record."
* type = #collection
* timestamp = "2026-08-20T17:35:03Z"
* entry[0].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#context-snapshot "Context snapshot"
* entry[0].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-context-snapshot-v0/test-key/1"
* entry[0].extension[entryKey].valueIdentifier.value = "v0:test-key:1:3ZTiYqzi8xk9ZhSE3U_roFsDtUYoNTQ_CbWEDvOZwLQ"
* entry[0].fullUrl = "urn:uuid:a3a3368b-fb0f-5113-9d9d-7c651a4b96ca"
* entry[0].resource = GroveMobileExchangePatientExample
* entry[1].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[1].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[1].extension[entryKey].valueIdentifier.value = "v0:test-key:1:01dJDxR9bIctHh_m-iQIOMvapXGnIq_0wmLCNEXTIvo"
* entry[1].fullUrl = "urn:uuid:76a3c913-b4e7-5299-b4ac-caf23054b231"
* entry[1].resource = GroveMobileExchangeHostExample
* entry[2].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[2].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[2].extension[entryKey].valueIdentifier.value = "v0:test-key:1:H9mN3DGJkpaJ785z-KtZ7dZ3Gz274Ea1sL2oGs3Jkf4"
* entry[2].fullUrl = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entry[2].resource = GroveMobileExchangeApplicationExample
* entry[3].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#source-output "Source output"
* entry[3].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* entry[3].extension[entryKey].valueIdentifier.value = "v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"
* entry[3].fullUrl = "urn:uuid:a9b76bbc-f523-5ef4-9919-813ec70553e5"
* entry[3].resource = GroveMobileExchangeHeartRateExample
* entry[4].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#record-version "Record version"
* entry[4].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
* entry[4].extension[entryKey].valueIdentifier.value = "v0:test-key:1:1b32Y3AcBpsWou7Vw8hQfJ-R3_h-uIQgmaNzRPQ4Jus"
* entry[4].fullUrl = "urn:uuid:20c970e9-1df8-5af7-ba42-ba4a4621c422"
* entry[4].resource = GroveMobileExchangeProvenanceExample
* entry[5].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#source-output "Source output"
* entry[5].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* entry[5].extension[entryKey].valueIdentifier.value = "v0:test-key:1:N8Rta5CkBmwGgJDKxdrh7xI0h9EgCKlQLPGxr7QRpAw"
* entry[5].fullUrl = "urn:uuid:923c35c9-6909-5d65-89ac-ef130e9e019d"
* entry[5].resource = GroveMobileExchangeSecondHeartRateExample
* entry[6].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#record-version "Record version"
* entry[6].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
* entry[6].extension[entryKey].valueIdentifier.value = "v0:test-key:1:Fiz_W2KPmuHp0lqnmBcrjgY1hwfsHAAUuXNVq6LP05Q"
* entry[6].fullUrl = "urn:uuid:555e8629-6601-58e7-b030-e6540a933aa0"
* entry[6].resource = GroveMobileExchangeSecondProvenanceExample

Instance: GroveMobileRetractionProvenanceExample
InstanceOf: GroveMobileRetractionProvenance
Usage: #example
Title: "Example Mobile Retraction Provenance"
Description: "A later append-only assertion that the source record behind the first exchange record is no longer exposed. It addresses that whole source record, every output of every version of it; its typed target names the output the producer emitted and is informative. It copies no output, requests no FHIR DELETE, and discloses the native record identifier so the source store can delete the exact record. Its assembler is a literal reference to the shared application Device in the same Bundle."
* target.type = "Observation"
* target.identifier.type = GroveIdentifierRoleCS#source-output "Source output"
* target.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* target.identifier.value = "v0:test-key:1:PPULnf0LKpASjIj8mU5TKafPKig_oqWND3_dHFShGd8"
* target.extension[targetRole].valueCode = #primary-output
* target.extension[nativeIdentifier].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/native-record/health-connect/1f5c58aa-6ec6-4e79-a682-829a9debd3f5"
* target.extension[nativeIdentifier].valueIdentifier.value = "record-heart-001"
* occurredDateTime = "2026-08-21T08:00:00Z"
* recorded = "2026-08-21T08:00:01Z"
* activity = GroveLifecycleEventCS#source-record-retracted "Source record retracted"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"

Instance: GroveMobileSecondRetractionProvenanceExample
InstanceOf: GroveMobileRetractionProvenance
Usage: #example
Title: "Example Mobile Second Retraction Provenance"
Description: "The retraction of the second exchange record's source record, packed into the same retraction Bundle as the first under its own record-retraction key."
* target.type = "Observation"
* target.identifier.type = GroveIdentifierRoleCS#source-output "Source output"
* target.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* target.identifier.value = "v0:test-key:1:N8Rta5CkBmwGgJDKxdrh7xI0h9EgCKlQLPGxr7QRpAw"
* target.extension[targetRole].valueCode = #primary-output
* target.extension[nativeIdentifier].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/native-record/health-connect/1f5c58aa-6ec6-4e79-a682-829a9debd3f5"
* target.extension[nativeIdentifier].valueIdentifier.value = "record-heart-002"
* occurredDateTime = "2026-08-21T08:00:00Z"
* recorded = "2026-08-21T08:00:01Z"
* activity = GroveLifecycleEventCS#source-record-retracted "Source record retracted"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:Ce4AD2kT5yierXkx5QJNFu7d8qqaSSQOCKGFeYpu2M0"

Instance: GroveMobileRetractionBundleExample
InstanceOf: GroveMobileRetractionBundle
Usage: #example
Title: "Example Mobile Retraction Bundle"
Description: "One upload of two retraction records: one retraction Provenance per retracted source record, each keyed by its record-retraction Identifier, and the shared application Device that assembled them with its host. The Devices have the same content, and so the same keys and fullUrls, as in the exchange Bundle example. Repository deletion or status projection remains a separate deployment policy."
* type = #collection
* timestamp = "2026-08-21T08:00:02Z"
* entry[0].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[0].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[0].extension[entryKey].valueIdentifier.value = "v0:test-key:1:01dJDxR9bIctHh_m-iQIOMvapXGnIq_0wmLCNEXTIvo"
* entry[0].fullUrl = "urn:uuid:76a3c913-b4e7-5299-b4ac-caf23054b231"
* entry[0].resource = GroveMobileExchangeHostExample
* entry[1].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[1].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[1].extension[entryKey].valueIdentifier.value = "v0:test-key:1:H9mN3DGJkpaJ785z-KtZ7dZ3Gz274Ea1sL2oGs3Jkf4"
* entry[1].fullUrl = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entry[1].resource = GroveMobileExchangeApplicationExample
* entry[2].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#record-retraction "Record retraction"
* entry[2].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-retraction-v0/test-key/1"
* entry[2].extension[entryKey].valueIdentifier.value = "v0:test-key:1:0JJ96w-JxTpK7Bb-910L_61f3KJdI8Cr4eSGTpJ7L7o"
* entry[2].fullUrl = "urn:uuid:03e766bb-9cc6-51b2-b67e-e8902e01513f"
* entry[2].resource = GroveMobileRetractionProvenanceExample
* entry[3].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#record-retraction "Record retraction"
* entry[3].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-retraction-v0/test-key/1"
* entry[3].extension[entryKey].valueIdentifier.value = "v0:test-key:1:B21Bfil3Angm31WXctopw5mzf3r2zaP3cR4dfxh-gbg"
* entry[3].fullUrl = "urn:uuid:59badeab-e83b-5a78-9c1b-43966d24777b"
* entry[3].resource = GroveMobileSecondRetractionProvenanceExample

Instance: GroveMobileSourceRecordTargetRetractionProvenanceExample
InstanceOf: GroveMobileRetractionProvenance
Usage: #example
Title: "Example Mobile Source-Record Target Retraction Provenance"
Description: "Retracts the same source record as the first retraction example, asserted by a producer that cannot establish which outputs its conversion of the record emitted. Its only target is untyped and repeats the source-record Identifier of Provenance.entity, so it names the source record as a whole without listing any of its outputs. The retraction key depends only on the source record, so this re-report carries the same record-retraction key and fullUrl as the first retraction; a receiver keeps the first it accepts, which loses nothing because both address the whole record."
* target.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* target.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* target.identifier.value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"
* target.extension[targetRole].valueCode = #source-record
* target.extension[nativeIdentifier].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/native-record/health-connect/1f5c58aa-6ec6-4e79-a682-829a9debd3f5"
* target.extension[nativeIdentifier].valueIdentifier.value = "record-heart-001"
* occurredDateTime = "2026-08-21T08:00:00Z"
* recorded = "2026-08-21T08:00:01Z"
* activity = GroveLifecycleEventCS#source-record-retracted "Source record retracted"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entity.role = #source
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:ptHr751zWyYfaR2WIvrP1TfnVEK4bInC__ibP_AYfVY"

Instance: GroveMobileSourceRecordTargetRetractionBundleExample
InstanceOf: GroveMobileRetractionBundle
Usage: #example
Title: "Example Mobile Source-Record Target Retraction Bundle"
Description: "One retraction record whose lifecycle Provenance names its source record as a whole through one source-record target, with the shared application Device that assembled it and its host. Repository deletion or status projection remains a separate deployment policy."
* type = #collection
* timestamp = "2026-08-21T08:00:02Z"
* entry[0].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[0].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[0].extension[entryKey].valueIdentifier.value = "v0:test-key:1:01dJDxR9bIctHh_m-iQIOMvapXGnIq_0wmLCNEXTIvo"
* entry[0].fullUrl = "urn:uuid:76a3c913-b4e7-5299-b4ac-caf23054b231"
* entry[0].resource = GroveMobileExchangeHostExample
* entry[1].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#device-snapshot "Device snapshot"
* entry[1].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* entry[1].extension[entryKey].valueIdentifier.value = "v0:test-key:1:H9mN3DGJkpaJ785z-KtZ7dZ3Gz274Ea1sL2oGs3Jkf4"
* entry[1].fullUrl = "urn:uuid:d39c21c3-97f6-5ce8-bcae-d3d65339e429"
* entry[1].resource = GroveMobileExchangeApplicationExample
* entry[2].extension[entryKey].valueIdentifier.type = GroveIdentifierRoleCS#record-retraction "Record retraction"
* entry[2].extension[entryKey].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-retraction-v0/test-key/1"
* entry[2].extension[entryKey].valueIdentifier.value = "v0:test-key:1:0JJ96w-JxTpK7Bb-910L_61f3KJdI8Cr4eSGTpJ7L7o"
* entry[2].fullUrl = "urn:uuid:03e766bb-9cc6-51b2-b67e-e8902e01513f"
* entry[2].resource = GroveMobileSourceRecordTargetRetractionProvenanceExample

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
* effectiveDateTime = "2026-08-19T10:30:00.251-07:00"
* effectiveDateTime.extension[timezone].valueCode = #America/Los_Angeles
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 72 '/min' "beats/minute"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[writerRecordVersion].valueString = "3"
