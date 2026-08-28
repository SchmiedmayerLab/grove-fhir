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

Instance: WithingsApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Withings Converter Snapshot"
Description: "The immutable event-time application snapshot that converted one already-obtained Withings record."
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:UGzHY2SuM3Fy_2XiJrLUV5avqMwtZBJRRGoL-m6GBhE"
* status = #active
* deviceName[applicationName].name = "Withings Provider Mapper"
* deviceName[applicationName].type = #user-friendly-name

Instance: WithingsBodyWeightExample
InstanceOf: WithingsObservation
Usage: #example
Title: "Withings Body Weight"
Description: "An already-obtained Withings weight measure on the Withings narrowing of the provider contract."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:v_LvUBZOa15LA0p5kXQXNZcARLmPPt7FiVgibReTE4o"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:X-D71tzCpCFqbofgYb8jTudUur0gx2J5Vv1seXFQchw"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 72.5 'kg' "kg"
* extension[providerSourceType].valueCode = #withings/getmeas:1

Instance: WithingsBloodPressureExample
InstanceOf: WithingsObservation
Usage: #example
Title: "Withings Grouped Blood Pressure"
Description: "One Withings measure group converted to one blood-pressure panel under the exact semantic and Withings lineage profiles."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:xcGtq_GbAQhydEiOKVmFc1iLIbtqP1Xa6WG8sT17Ws8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:YlJWGJsSEmsyv8i-R9edsO8HpySQzLap4F6yvclNm-w"
* identifier[writerRecord].system = "https://study.example.org/fhir/NamingSystem/grove-writer-record-v2/test-key/1"
* identifier[writerRecord].value = "v2:test-key:1:b6CrOt2Bn8qBpBi_0IesPTPhIzN5DbRQLPz_Di3GfSQ"
* extension[writerRecordVersion].valueString = "1"
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#vital-signs "Vital Signs"
* code = http://loinc.org#85354-9 "Blood pressure panel with all children optional"
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-20T07:45:00-07:00"
* component[0].code = http://loinc.org#8480-6 "Systolic blood pressure"
* component[0].valueQuantity = 118 'mm[Hg]' "mmHg"
* component[1].code = http://loinc.org#8462-4 "Diastolic blood pressure"
* component[1].valueQuantity = 76 'mm[Hg]' "mmHg"
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
* agent[assembler].who = Reference(WithingsApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:xcGtq_GbAQhydEiOKVmFc1iLIbtqP1Xa6WG8sT17Ws8"
