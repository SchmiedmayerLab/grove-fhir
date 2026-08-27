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
* identifier[sourceRecordId].system = "https://grovealliance.org/fhir/providers/NamingSystem/provider-source-record-id"
* identifier[sourceRecordId].value = "v1:google-health-api|acct-7f3a9c|steps|content|2026-08-20T16:00:00Z|2026-08-20T17:00:00Z|1042"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity "Activity"
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(GoogleHealthPatientExample)
* performer = Reference(GoogleHealthPatientExample)
* effectivePeriod.start = "2026-08-20T09:00:00-07:00"
* effectivePeriod.end = "2026-08-20T10:00:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* valueQuantity = 1042 '{steps}' "steps"
* extension[providerSourceType].valueCode = #google-health-api/steps
