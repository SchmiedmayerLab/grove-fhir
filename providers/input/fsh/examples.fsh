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
* identifier[sourceRecordId].value = "v1:9caeaee8e6d50dc85bb5f91cadfa4f8a3303a5eb612e8d6e6a58017454996102"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:6fae7466ee846e8ed1c3d56589a748d8d621eeea49aee9c1b5cd3a740a99ddf1"
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
* entity.what.identifier.value = "v1:9caeaee8e6d50dc85bb5f91cadfa4f8a3303a5eb612e8d6e6a58017454996102"

Instance: GoogleHealthHeartRateRecordingExample
InstanceOf: ProviderRecordingDocument
Usage: #example
Title: "Google Health Native Heart-rate Recording"
Description: "An explicitly authorized caller encoding of already-obtained irregular heart-rate points, retained without resampling."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:e9174b24826045a9d8bfb85888baea27526e626b5049f7c8d0cb6a1479c965d5"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:277b888059d003e8c0fe6b6d131b09a703bf6bc56f9be37fb8bb97582cf98e7a"
* extension[provider].valueCode = #google-health-api
* extension[providerSourceType].valueCode = #google-health-api/heart-rate
* status = #current
* type.text = "Google Health API heart-rate archive"
* subject = Reference(ProviderPatientExample)
* date = "2026-08-20T17:00:01Z"
* author = Reference(ProviderApplicationExample)
* content.attachment.contentType = #application/json
* content.attachment.title = "Authorized minimized provider recording"
* content.attachment.data = "eyJwb2ludCI6W3sic3RhcnRUaW1lTmFub3MiOiIxNzg3MjM2OTgwMDAwMDAwMDAwIiwiZW5kVGltZU5hbm9zIjoiMTc4NzIzNjk4MDAwMDAwMDAwMCIsImRhdGFUeXBlTmFtZSI6ImNvbS5nb29nbGUuaGVhcnRfcmF0ZS5icG0iLCJ2YWx1ZSI6W3siZnBWYWwiOjcxLjB9XX1dfQ=="
* content.attachment.size = 157
* content.attachment.hash = "W77rFQFjzMqkuSpq6pY7XVnlw8A="
* content.format = $recordingFormat#provider-json-1 "Provider JSON 1"

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
* entity.what.identifier.value = "v1:e9174b24826045a9d8bfb85888baea27526e626b5049f7c8d0cb6a1479c965d5"

Instance: WithingsBloodPressureExample
InstanceOf: ProviderObservation
Usage: #example
Title: "Withings Grouped Blood Pressure"
Description: "One already-obtained Withings measure group holding one diastolic (type 9) and one systolic (type 10) value converted into one shared blood-pressure panel."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:335d6070863e13e73a8b1a1e7ca87f3517761dd157e5bd4e13824e06b5cb924c"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:69164aa34a29ecfcd5b8ffef92b7257d0c5bcd039ae88955c3688b4efab95793"
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
* entity.what.identifier.value = "v1:335d6070863e13e73a8b1a1e7ca87f3517761dd157e5bd4e13824e06b5cb924c"

Instance: WithingsExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "Withings Exchange Bundle"
Description: "The complete deterministic collection graph for one converted Withings blood-pressure measure group."
* identifier.system = $providerExchangeId
* identifier.value = "v1:8e2bafe52854eecf1223dcc706c615348dfe26754f6bc816e479bc1ef22d3f8c"
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
* entry[2].extension[entryIdentifier].valueIdentifier.system = $providerOutputId
* entry[2].extension[entryIdentifier].valueIdentifier.value = "v1:69164aa34a29ecfcd5b8ffef92b7257d0c5bcd039ae88955c3688b4efab95793"
* entry[2].fullUrl = "urn:uuid:9bab53d6-0eec-52eb-9425-a556dd9238b4"
* entry[2].resource = WithingsBloodPressureExample
* entry[3].extension[entryIdentifier].valueIdentifier.system = $providerConversionId
* entry[3].extension[entryIdentifier].valueIdentifier.value = "v1:8e2bafe52854eecf1223dcc706c615348dfe26754f6bc816e479bc1ef22d3f8c"
* entry[3].fullUrl = "urn:uuid:996be494-199d-5a2d-836b-24f45a1c14b8"
* entry[3].resource = WithingsBloodPressureProvenanceExample
