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
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|body-fat-mass|record-body-fat-mass"
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
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|extracellular-water-mass|record-extracellular-water-mass"
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
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|intracellular-water-mass|record-intracellular-water-mass"
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
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|muscle-mass|record-muscle-mass"
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
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|sleeping-heart-rate-average|record-sleeping-heart-rate-average"
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
