//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: GoogleHealthPatientExample
InstanceOf: Patient
Usage: #example
Title: "Google Health Example Participant"
Description: "The Patient referenced by the Google Health adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: GoogleHealthStepCountExample
InstanceOf: GoogleHealthObservation
Usage: #example
Title: "Google Health Step Count"
Description: "An already-obtained Google Health API steps interval on the Google Health narrowing of the provider contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:N0eoeAizxv2r52-apeG3hX1hFBXfsmuIPjQEcpf8x_8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:WnlDcVrpqbr59z48UBWz6kbAk54f1i1F6VvwH_hVv9U"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity "Activity"
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(GoogleHealthPatientExample)
* performer = Reference(GoogleHealthPatientExample)
* effectivePeriod.start = "2026-08-20T09:00:00-07:00"
* effectivePeriod.end = "2026-08-20T10:00:00-07:00"
* valueQuantity = 1042 '{steps}' "steps"
* extension[providerSourceType].valueCode = #google-health-api/steps
