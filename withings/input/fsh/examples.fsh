//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: WithingsPatientExample
InstanceOf: Patient
Usage: #example
Title: "Withings Example Participant"
Description: "The Patient referenced by the Withings adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-connected-001"

Instance: WithingsBodyWeightExample
InstanceOf: WithingsObservation
Usage: #example
Title: "Withings Body Weight"
Description: "An already-obtained Withings weight measure on the Withings narrowing of the provider contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:v_LvUBZOa15LA0p5kXQXNZcARLmPPt7FiVgibReTE4o"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:7-b5T3TLWURN3kGgXY8JSaNkTU8SAIwcMrKVWxRoLN4"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T17:00:01Z"
* valueQuantity = 72.5 'kg' "kg"
* extension[providerSourceType].valueCode = #withings/getmeas:1
