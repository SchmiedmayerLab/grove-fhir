// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: ProviderMeasurementCS
Id: provider-measurement
Title: "Provider Measurement"
Description: "Measurement concepts defined by the providers adapter for provider-scoped results no established code represents faithfully."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #extracellular-water-mass "Extracellular water mass" "The mass of body water outside cells as estimated by bioelectrical impedance analysis."
* #intracellular-water-mass "Intracellular water mass" "The mass of body water inside cells as estimated by bioelectrical impedance analysis."
* #sleeping-heart-rate-average "Sleeping heart rate average" "The mean heart rate across the exact sleep-session Observation effective Period."

ValueSet: ProviderMeasurementVS
Id: provider-measurement
Title: "Provider Measurement"
Description: "Measurement concepts defined by the providers adapter for its provider-scoped profiles."
* ^experimental = false
* include codes from system ProviderMeasurementCS

Profile: ProviderBodyFatMass
Parent: ProviderObservation
Id: provider-body-fat-mass
Title: "Body Fat Mass"
Description: "Absolute fat mass computed by a body-composition scale, normalized to UCUM kilograms. Distinct from body-fat percentage; only Withings evidences an absolute fat-mass output, so the profile is provider-scoped."
* code = $loinc#73708-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: ProviderExtracellularWaterMass
Parent: ProviderObservation
Id: provider-extracellular-water-mass
Title: "Extracellular Water Mass"
Description: "Mass of extracellular body water estimated by bioelectrical impedance, normalized to UCUM kilograms. Only Withings evidences the compartmentalized value, so the profile is provider-scoped and is distinct from total body-water mass."
* code = ProviderMeasurementCS#extracellular-water-mass
* code from ProviderMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: ProviderIntracellularWaterMass
Parent: ProviderObservation
Id: provider-intracellular-water-mass
Title: "Intracellular Water Mass"
Description: "Mass of intracellular body water estimated by bioelectrical impedance, normalized to UCUM kilograms. Only Withings evidences the compartmentalized value, so the profile is provider-scoped and is distinct from total body-water mass."
* code = ProviderMeasurementCS#intracellular-water-mass
* code from ProviderMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: ProviderMuscleMass
Parent: ProviderObservation
Id: provider-muscle-mass
Title: "Muscle Mass"
Description: "A providers-exclusive whole-body muscle mass calculated by bioimpedance analysis, normalized to UCUM kilograms. It is distinct from lean body mass (which additionally includes bone, water, and organ mass) and is not folded into that shared measurement."
* code = $loinc#73964-9
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: ProviderSleepingHeartRateAverage
Parent: ProviderObservation
Id: provider-sleeping-heart-rate-average
Title: "Sleeping Heart Rate Average"
Description: "The average heart rate across one sleep session, normalized to UCUM beats per minute. It is a session-windowed average, distinct from both the shared point heart-rate measurement and the daily resting-heart-rate estimate, and is implemented by the phase-2 aggregate design."
* code = ProviderMeasurementCS#sleeping-heart-rate-average
* code from ProviderMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#session-mean "Session mean"
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Instance: ProviderBodyFatMassExample
InstanceOf: ProviderBodyFatMass
Usage: #example
Title: "Body Fat Mass Example"
Description: "A conformant Body Fat Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:abc6a7f4a60be193b3fdc39c93aeeab6bd1c472f673a078ac554960114a14882"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:97346a7be297df20ff6cf03e5afff55ca25b0f027d28fe5fe657ea6f350d1da1"
* status = #final
* code = $loinc#73708-0 "Body fat [Mass] Calculated"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:8
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 16.4 'kg'

Instance: ProviderExtracellularWaterMassExample
InstanceOf: ProviderExtracellularWaterMass
Usage: #example
Title: "Extracellular Water Mass Example"
Description: "A conformant Extracellular Water Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:7a26245a81bdc837ca1f96ad882293148687f99c0d99daaf67dcb15b2dfcbadf"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:15afe9ce860d34f9732fd1b2c20fd971acbe44cbace2566ecd6aa08c7ad6b24f"
* status = #final
* code = ProviderMeasurementCS#extracellular-water-mass
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:168
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 17 'kg'

Instance: ProviderIntracellularWaterMassExample
InstanceOf: ProviderIntracellularWaterMass
Usage: #example
Title: "Intracellular Water Mass Example"
Description: "A conformant Intracellular Water Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:18d7cb4f4a835433d698586571c346b13053e1603d4ed6e99e69a8450447278d"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:3e297e22fd6c3ee657f8f57c270ccdb0f75ffc6a1404a31e6a0dd6f0dff0b7a0"
* status = #final
* code = ProviderMeasurementCS#intracellular-water-mass
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:169
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 25 'kg'

Instance: ProviderMuscleMassExample
InstanceOf: ProviderMuscleMass
Usage: #example
Title: "Muscle Mass Example"
Description: "A conformant Muscle Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:c67cf823fd0eb4a5974af31b4ac2e217314e6fdbd413bf9a02db08cdd76a3134"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:91afb64241c71d49ea80e44466964c693a7d8fba952988c980e67f954b698ae6"
* status = #final
* code = $loinc#73964-9 "Body muscle mass Calculated"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:76
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 31.5 'kg'

Instance: ProviderSleepingHeartRateAverageExample
InstanceOf: ProviderSleepingHeartRateAverage
Usage: #example
Title: "Sleeping Heart Rate Average Example"
Description: "A conformant Sleeping Heart Rate Average instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:1c3a40ad3439d8794bd8c8d9c6634ff9d0bff2f850130f9091fb4bc38a15a2c0"
* identifier[outputId].system = $providerOutputId
* identifier[outputId].value = "v1:e575642678b543e54b470558f874a2455d7df7c8d4d97b9832697fbb36441ee9"
* status = #final
* code = ProviderMeasurementCS#sleeping-heart-rate-average
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getsummary:hr_average
* subject = Reference(ProviderPatientExample)
* performer = Reference(ProviderPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 55 '/min' "beats/minute"
