//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: ProviderPatientExample
InstanceOf: Patient
Usage: #example
Title: "Provider Example Participant"
Description: "The Patient referenced by the Provider adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: ProviderApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Provider Converting Application"
Description: "The application that converted already-obtained provider records into source-neutral FHIR resources."
* status = #active
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "provider-mapper"
* deviceName[applicationName].name = "Provider Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: GoogleHealthStepsExample
InstanceOf: ProviderObservation
Usage: #example
Title: "Google Health Step Count"
Description: "An already-obtained Google Health API steps interval converted to the shared step-count contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:google-health-api|acct-7f3a9c|steps|content|2026-08-20T16:00:00Z|2026-08-20T17:00:00Z|1042"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity "Activity"
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectivePeriod.start = "2026-08-20T09:00:00-07:00"
* effectivePeriod.end = "2026-08-20T10:00:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* valueQuantity = 1042 '{steps}' "steps"
* extension[provider].valueCode = #google-health-api
* extension[providerSourceType].valueCode = #google-health-api/steps

Instance: GoogleHealthStepsProvenanceExample
InstanceOf: ProviderConversionProvenance
Usage: #example
Title: "Google Health Step Conversion Provenance"
Description: "The conversion event linking one already-obtained Google Health steps source record to its shared step-count output."
* target = Reference(GoogleHealthStepsExample)
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(ProviderApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $providerSourceRecordId
* entity.what.identifier.value = "v1:google-health-api|acct-7f3a9c|steps|content|2026-08-20T16:00:00Z|2026-08-20T17:00:00Z|1042"

Instance: GoogleHealthHeartRateRecordingExample
InstanceOf: ProviderRecordingDocument
Usage: #example
Title: "Google Health Native Heart-rate Recording"
Description: "An explicitly authorized caller encoding of already-obtained irregular heart-rate points, retained without resampling."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:google-health-api|acct-7f3a9c|heart-rate|content|2026-08-20T16:03:00Z|2026-08-20T16:03:00Z|71"
* extension[provider].valueCode = #google-health-api
* extension[providerSourceType].valueCode = #google-health-api/heart-rate
* status = #current
* type.text = "Google Health API heart-rate archive"
* subject = Reference(ProviderPatientExample)
* date = "2026-08-20T17:00:01Z"
* author = Reference(ProviderApplicationExample)
* content.attachment.contentType = #application/vnd.grovealliance.provider+json
* content.attachment.title = "Authorized minimized provider recording"
* content.attachment.data = "eyJwb2ludCI6W3sic3RhcnRUaW1lTmFub3MiOiIxNzg3MjM2OTgwMDAwMDAwMDAwIiwiZW5kVGltZU5hbm9zIjoiMTc4NzIzNjk4MDAwMDAwMDAwMCIsImRhdGFUeXBlTmFtZSI6ImNvbS5nb29nbGUuaGVhcnRfcmF0ZS5icG0iLCJ2YWx1ZSI6W3siZnBWYWwiOjcxLjB9XX1dfQ=="
* content.attachment.size = 157
* content.attachment.hash = "W77rFQFjzMqkuSpq6pY7XVnlw8A="
* content.format = $recordingFormat#provider-recording "Provider Recording"
* content.format.version = "0.5.0"

Instance: GoogleHealthHeartRateRecordingProvenanceExample
InstanceOf: ProviderConversionProvenance
Usage: #example
Title: "Google Health Native Heart-rate Conversion Provenance"
Description: "The conversion event linking one already-obtained source record to its native Recording Document."
* target = Reference(GoogleHealthHeartRateRecordingExample)
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(ProviderApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $providerSourceRecordId
* entity.what.identifier.value = "v1:google-health-api|acct-7f3a9c|heart-rate|content|2026-08-20T16:03:00Z|2026-08-20T16:03:00Z|71"

Instance: OuraDailyStepCountExample
InstanceOf: ProviderObservation
Usage: #example
Title: "Oura Daily Step Count"
Description: "One already-obtained Oura daily-activity record converted to the shared step-count contract. Oura documents its document ids as UUIDs unique across every account, so the identifier is that key exactly as Oura supplied it, with nothing joined to it."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "8f9a5221-639e-4a85-81cb-4065ef23f979"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity "Activity"
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* issued = "2026-08-21T07:00:01Z"
* valueQuantity = 9218 '{steps}' "steps"
* extension[provider].valueCode = #oura
* extension[providerSourceType].valueCode = #oura/daily_activity

Instance: WithingsBloodPressureExample
InstanceOf: ProviderObservation
Usage: #example
Title: "Withings Grouped Blood Pressure"
Description: "One already-obtained Withings measure group holding one diastolic (type 9) and one systolic (type 10) value converted into one shared blood-pressure panel. It also carries the shared writer-record identity, which names the measurement as Withings itself does; the identical value appears when the Withings application writes the same measurement into HealthKit or Health Connect, so a deployment that has confirmed those key spaces agree can recognise one measurement arriving by more than one route."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|measure|17348211"
* identifier[writerRecordId].system = $groveWriterRecordId
* identifier[writerRecordId].value = "v1:withings|17348211"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#vital-signs "Vital Signs"
* code = http://loinc.org#85354-9 "Blood pressure panel with all children optional"
* subject.reference = "urn:uuid:8e270383-7562-584e-a754-972a899031f8"
* performer.reference = "urn:uuid:8e270383-7562-584e-a754-972a899031f8"
* effectiveDateTime = "2026-08-20T07:45:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* component[0].code = http://loinc.org#8480-6 "Systolic blood pressure"
* component[0].valueQuantity = 118 'mm[Hg]' "mmHg"
* component[1].code = http://loinc.org#8462-4 "Diastolic blood pressure"
* component[1].valueQuantity = 76 'mm[Hg]' "mmHg"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:9+10

Instance: WithingsBloodPressureProvenanceExample
InstanceOf: ProviderConversionProvenance
Usage: #example
Title: "Withings Grouped Blood Pressure Conversion Provenance"
Description: "The conversion event linking one Withings measure-group source record to its single grouped blood-pressure output."
* target.reference = "urn:uuid:9bab53d6-0eec-52eb-9425-a556dd9238b4"
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who.reference = "urn:uuid:f3ec89f2-5381-5b86-a800-c85ef81bdc7c"
* entity.role = #source
* entity.what.identifier.system = $providerSourceRecordId
* entity.what.identifier.value = "v1:withings|acct-7f3a9c|measure|17348211"

Instance: WithingsExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "Withings Exchange Bundle"
Description: "The complete deterministic collection graph for one converted Withings blood-pressure measure group."
* identifier.system = "https://study.example.org/fhir/identifiers/provider-graph"
* identifier.value = "withings|1|exchange-bundle"
* type = #collection
* timestamp = "2026-08-20T17:00:01Z"
* entry[0].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/participant"
* entry[0].extension[entryIdentifier].valueIdentifier.value = "participant-connected-001"
* entry[0].fullUrl = "urn:uuid:8e270383-7562-584e-a754-972a899031f8"
* entry[0].resource = ProviderPatientExample
* entry[1].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/application"
* entry[1].extension[entryIdentifier].valueIdentifier.value = "provider-mapper"
* entry[1].fullUrl = "urn:uuid:f3ec89f2-5381-5b86-a800-c85ef81bdc7c"
* entry[1].resource = ProviderApplicationExample
* entry[2].extension[entryIdentifier].valueIdentifier.system = $providerSourceRecordId
* entry[2].extension[entryIdentifier].valueIdentifier.value = "v1:withings|acct-7f3a9c|measure|17348211"
* entry[2].fullUrl = "urn:uuid:9bab53d6-0eec-52eb-9425-a556dd9238b4"
* entry[2].resource = WithingsBloodPressureExample
* entry[3].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/provider-graph"
* entry[3].extension[entryIdentifier].valueIdentifier.value = "withings|1|conversion-provenance"
* entry[3].fullUrl = "urn:uuid:996be494-199d-5a2d-836b-24f45a1c14b8"
* entry[3].resource = WithingsBloodPressureProvenanceExample
