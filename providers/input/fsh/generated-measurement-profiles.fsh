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
