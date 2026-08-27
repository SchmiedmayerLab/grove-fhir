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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Du7c9mRSc_fCuQW7iGjpBiJeDIqwVrDcICSFcObFKLw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:2lXSlUkA6BQcP5ze6E5fx6RHYcQg7ng_3KYJsp3_HfQ"
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
