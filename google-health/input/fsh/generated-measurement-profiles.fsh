// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: GoogleHealthMeasurementCS
Id: google-health-measurement
Title: "Google Health Measurement"
Description: "Measurement concepts defined by the Google Health adapter for vendor-exclusive results no established code represents faithfully."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #resting-heart-rate-daily-average "Resting heart rate daily average" "The mean resting heart-rate estimate reported for the exact civil-day Period."

ValueSet: GoogleHealthMeasurementVS
Id: google-health-measurement
Title: "Google Health Measurement"
Description: "Measurement concepts defined by the Google Health adapter for its vendor-exclusive profiles."
* ^experimental = false
* include codes from system GoogleHealthMeasurementCS

Profile: GoogleHealthDailyRestingHeartRate
Parent: GroveMobileObservation
Id: google-health-daily-resting-heart-rate
Title: "Resting Heart Rate Daily Average"
Description: "A source-supplied mean resting heart rate over an exact civil-day Period, normalized to UCUM beats per minute. It is an aggregate estimate and is never substituted for a point RestingHeartRateRecord or HealthKit resting-heart-rate sample."
* code = GoogleHealthMeasurementCS#resting-heart-rate-daily-average
* code from GoogleHealthMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#daily-mean
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Instance: GoogleHealthDailyRestingHeartRateExample
InstanceOf: GoogleHealthDailyRestingHeartRate
Usage: #example
Title: "Resting Heart Rate Daily Average Example"
Description: "A conformant Resting Heart Rate Daily Average instance."
* meta.profile[+] = "https://grovealliance.org/fhir/google-health/StructureDefinition/google-health-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-provider-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:t5hiT7DZ1u93lWURgukgniISuD0-5cIhrNSbWDWW8mA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-provider-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:PdC0BGBTIeaB1hdvwbvGHk8SAqZg6cia6E4TQ9JDRyM"
* status = #final
* code = GoogleHealthMeasurementCS#resting-heart-rate-daily-average
* extension[+].url = "https://grovealliance.org/fhir/providers/StructureDefinition/provider"
* extension[=].valueCode = #google-health-api
* extension[+].url = "https://grovealliance.org/fhir/providers/StructureDefinition/provider-source-type"
* extension[=].valueCode = #google-health-api/daily-resting-heart-rate
* subject = Reference(GoogleHealthPatientExample)
* performer = Reference(GoogleHealthPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 58 '/min' "beats/minute"
