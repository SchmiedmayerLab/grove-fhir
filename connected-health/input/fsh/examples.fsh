//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: ConnectedHealthPatientExample
InstanceOf: Patient
Usage: #example
Title: "Connected Health Example Participant"
Description: "The Patient referenced by the Connected Health adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: ConnectedHealthApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Connected Health Converting Application"
Description: "The application that converted already-obtained provider records into source-neutral FHIR resources."
* status = #active
* identifier.system = "https://study.example.org/fhir/identifiers/application"
* identifier.value = "connected-health-mapper"
* deviceName[applicationName].name = "Connected Health Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: GoogleHealthStepsExample
InstanceOf: ConnectedHealthObservation
Usage: #example
Title: "Google Health Step Count"
Description: "An already-obtained Google Health API steps interval converted to the shared step-count contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecordId].system = $connectedHealthSourceRecordId
* identifier[sourceRecordId].value = "v1:9caeaee8e6d50dc85bb5f91cadfa4f8a3303a5eb612e8d6e6a58017454996102"
* identifier[outputId].system = $connectedHealthOutputId
* identifier[outputId].value = "v1:6fae7466ee846e8ed1c3d56589a748d8d621eeea49aee9c1b5cd3a740a99ddf1"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity "Activity"
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(ConnectedHealthPatientExample)
* effectivePeriod.start = "2026-08-20T09:00:00-07:00"
* effectivePeriod.end = "2026-08-20T10:00:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* valueQuantity = 1042 '{steps}' "steps"
* extension[connectedHealthProvider].valueCode = #google-health-api

Instance: GoogleHealthStepsProvenanceExample
InstanceOf: ConnectedHealthConversionProvenance
Usage: #example
Title: "Google Health Step Conversion Provenance"
Description: "The conversion event linking one already-obtained Google Health steps source record to its shared step-count output."
* target = Reference(GoogleHealthStepsExample)
* recorded = "2026-08-20T17:00:01Z"
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who = Reference(ConnectedHealthApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $connectedHealthSourceRecordId
* entity.what.identifier.value = "v1:9caeaee8e6d50dc85bb5f91cadfa4f8a3303a5eb612e8d6e6a58017454996102"
