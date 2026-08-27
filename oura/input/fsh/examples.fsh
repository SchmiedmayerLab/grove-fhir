//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: OuraPatientExample
InstanceOf: Patient
Usage: #example
Title: "Oura Example Participant"
Description: "The Patient referenced by the Oura adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: OuraStepCountExample
InstanceOf: OuraObservation
Usage: #example
Title: "Oura Step Count"
Description: "An already-obtained Oura daily activity step total on the Oura narrowing of the provider contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecordId].system = "https://grovealliance.org/fhir/providers/NamingSystem/provider-source-record-id"
* identifier[sourceRecordId].value = "v1:oura|acct-7f3a9c|daily_activity|content|2026-08-20T00:00:00Z|2026-08-21T00:00:00Z|8241"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(OuraPatientExample)
* performer = Reference(OuraPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* valueQuantity = 8241 '{steps}' "steps"
* extension[providerSourceType].valueCode = #oura/daily_activity
