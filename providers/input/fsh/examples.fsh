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
* content.attachment.contentType = #application/octet-stream
* content.attachment.title = "Authorized minimized provider recording"
* content.attachment.data = "AQID"
* content.attachment.size = 3
* content.attachment.hash = "cDeAcZjCKn0rCAc3HXY3eahP388="

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
