// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: OuraMeasurementCS
Id: oura-measurement
Title: "Oura Measurement"
Description: "Measurement concepts defined by the Oura adapter for vendor-exclusive results no established code represents faithfully."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #oura-cardiovascular-age "Oura cardiovascular age" "The age-scaled figure Oura's proprietary cardiovascular-age algorithm derives from its own photoplethysmography features over the exact civil-day effective Period."
* #oura-readiness-score "Oura readiness score" "The bounded composite figure Oura's proprietary readiness algorithm reports for the exact civil-day effective Period."

ValueSet: OuraMeasurementVS
Id: oura-measurement
Title: "Oura Measurement"
Description: "Measurement concepts defined by the Oura adapter for its vendor-exclusive profiles."
* ^experimental = false
* include codes from system OuraMeasurementCS

Profile: OuraCardiovascularAge
Parent: OuraObservation
Id: oura-cardiovascular-age
Title: "Oura Cardiovascular Age"
Description: "Oura's proprietary cardiovascular-age figure over a civil-day effective Period, reported on an age scale in UCUM years. It is a vendor score expressed in years, not a chronological age and not a vascular assessment. It is deliberately a separate measurement from the Withings vascular age: the two are undisclosed algorithms over different inputs, so a shared code would fabricate a comparability neither vendor defines."
* code = OuraMeasurementCS#oura-cardiovascular-age
* code from OuraMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #a (exactly)

Profile: OuraReadinessScore
Parent: OuraObservation
Id: oura-readiness-score
Title: "Oura Readiness Score"
Description: "Oura's proprietary daily readiness figure over a civil-day effective Period. The vendor publishes no physical unit for it and it measures no observable quantity, so it carries the dimensionless UCUM {score} annotation rather than an invented unit, and the profile description is the only statement of its scale. It is a vendor composite, not a physiological measurement, and nothing about the inputs, weighting, or comparability across people or firmware versions is asserted."
* code = OuraMeasurementCS#oura-readiness-score
* code from OuraMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{score} (exactly)

Instance: OuraCardiovascularAgeExample
InstanceOf: OuraCardiovascularAge
Usage: #example
Title: "Oura Cardiovascular Age Example"
Description: "A conformant Oura Cardiovascular Age instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:pgwzCFk8dUQm_AB8_nMxWZK0Elud1y8VdenFtf115iM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:HBzgZpoU3pDCLsZXq9ZD3XK0Aq6KCmMIaw_2d2lCPP4"
* status = #final
* code = OuraMeasurementCS#oura-cardiovascular-age
* extension[provider].valueCode = #oura
* extension[providerSourceType].valueCode = #oura/daily_cardiovascular_age
* subject = Reference(OuraPatientExample)
* performer = Reference(OuraPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 38 'a' "years"

Instance: OuraReadinessScoreExample
InstanceOf: OuraReadinessScore
Usage: #example
Title: "Oura Readiness Score Example"
Description: "A conformant Oura Readiness Score instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:lS6Q5pNJc2J35RHDkDrmTM9Ya48fvmHdyeHjeo7-Qus"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:1P1D8Z4pMgSy5aZo3SfpctEWRODDN5wBv_nPaNumn8w"
* status = #final
* code = OuraMeasurementCS#oura-readiness-score
* extension[provider].valueCode = #oura
* extension[providerSourceType].valueCode = #oura/daily_readiness
* subject = Reference(OuraPatientExample)
* performer = Reference(OuraPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 78 '{score}' "score"
