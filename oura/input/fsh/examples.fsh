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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:W93IcvTZkGdlJFCzeohtA_2xSuJD729FQTCRL7Gi9OI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:PjcyiJIJrutw-WWQDm2wDaJgCBn1hPcvnVyD9S5uDIo"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#activity
* code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#step-count-total "Step count total"
* subject = Reference(OuraPatientExample)
* performer = Reference(OuraPatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-21T00:00:00-07:00"
* valueQuantity = 8241 '{steps}' "steps"
* extension[providerSourceType].valueCode = #oura/daily_activity
