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
Description: "An already-obtained Google Health API step-count interval conforming to both the Google Health lineage profile and the shared step-count profile."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:cgqFmbbaOjUQy_ODPOPu2tARCP6Yljc0OoPoySUjpdE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:kTrVGXL6OJ9m89zrseMUqWnA0G4rghOLlTzcC20sE2M"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity "Activity"
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(GoogleHealthPatientExample)
* performer = Reference(GoogleHealthPatientExample)
* effectivePeriod.start = "2026-08-20T09:00:00-07:00"
* effectivePeriod.end = "2026-08-20T10:00:00-07:00"
* valueQuantity = 1042 '{steps}' "steps"
* extension[providerSourceType].valueCode = #google-health-api/steps
