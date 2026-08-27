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
Description: "The Patient referenced by the connected-provider examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: ProviderApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Provider Converter Snapshot"
Description: "The immutable event-time application snapshot that converted one already-obtained provider record."
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:UGzHY2SuM3Fy_2XiJrLUV5avqMwtZBJRRGoL-m6GBhE"
* status = #active
* deviceName[applicationName].name = "Provider Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: GoogleHealthStepsExample
InstanceOf: ProvidersObservation
Usage: #example
Title: "Google Health Step Count"
Description: "An already-obtained Google Health API steps interval converted to the shared step-count contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:qgrk2z3ezCQPDLCievOnUDQm089yVRjCSaUp7uc3vU0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Xm1OIJA5vuDwPrAXzRR1229vsyVVNYidsYw_zf3dPA8"
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
InstanceOf: ProvidersConversionProvenance
Usage: #example
Title: "Google Health Step Conversion Provenance"
Description: "The conversion event linking exactly one provider source record revision to all of its outputs."
* target = Reference(GoogleHealthStepsExample)
* occurredDateTime = "2026-08-20T17:00:00Z"
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(ProviderApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:qgrk2z3ezCQPDLCievOnUDQm089yVRjCSaUp7uc3vU0"

Instance: GoogleHealthHeartRateRecordingExample
InstanceOf: ProvidersRecordingDocument
Usage: #example
Title: "Google Health Native Heart-rate Recording"
Description: "An authorized exact source artifact for irregular heart-rate points, retained without resampling or invented scalar semantics."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:wZpU3mAbk81CexNeSe82tMi6UzJqUOef7g0vUQAatEo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:fGKVshiEwT6r_6b940qrh_jQoETX2yXRyvleBsiV7tY"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:rTWgo0M-JFztgaUs9275SV126DALfHiBjY79mMCYAc0"
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
* content.format.version = "0.6.0"

Instance: OuraDailyStepCountExample
InstanceOf: ProvidersObservation
Usage: #example
Title: "Oura Daily Step Count"
Description: "An Oura daily-activity record whose globally unique native UUID is still HMAC input rather than a clear wire identifier."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:LXyniwcDxftNTHseMuLu9TRIUPKgIyGWNz95_Kl6H_M"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:PPhgR8OERaB2BMlHSGBGTCkKucBwxCcqTA3cyqQCA14"
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
InstanceOf: ProvidersObservation
Usage: #example
Title: "Withings Grouped Blood Pressure"
Description: "One Withings measure group converted to one blood-pressure panel, with opaque provider and cross-route writer identities."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:zYsyvBapI-3CLhIPYgWoFNvkxOZ1vY2FgrIwzdE339A"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:bvcLuxdpOMk3XTRHdhQxY8QLqijlsN4XlQJx3gLBAWk"
* identifier[writerRecord].system = "https://study.example.org/fhir/NamingSystem/grove-writer-record-v2/test-key/1"
* identifier[writerRecord].value = "v2:test-key:1:b6CrOt2Bn8qBpBi_0IesPTPhIzN5DbRQLPz_Di3GfSQ"
* extension[writerRecordVersion].valueString = "1"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#vital-signs "Vital Signs"
* code = http://loinc.org#85354-9 "Blood pressure panel with all children optional"
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectiveDateTime = "2026-08-20T07:45:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* component[0].code = http://loinc.org#8480-6 "Systolic blood pressure"
* component[0].valueQuantity = 118 'mm[Hg]' "mmHg"
* component[1].code = http://loinc.org#8462-4 "Diastolic blood pressure"
* component[1].valueQuantity = 76 'mm[Hg]' "mmHg"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:9+10

Instance: WithingsBloodPressureProvenanceExample
InstanceOf: ProvidersConversionProvenance
Usage: #example
Title: "Withings Blood Pressure Conversion Provenance"
Description: "The one-source conversion event for the grouped blood-pressure output."
* target = Reference(WithingsBloodPressureExample)
* occurredDateTime = "2026-08-20T17:00:00Z"
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(ProviderApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:zYsyvBapI-3CLhIPYgWoFNvkxOZ1vY2FgrIwzdE339A"
