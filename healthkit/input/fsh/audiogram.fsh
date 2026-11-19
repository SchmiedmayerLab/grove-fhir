//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: HealthKitAudiogramSensitivityTest
Id: healthkit-audiogram-sensitivity-test
Title: "HealthKit Audiogram Sensitivity Test"
Description: "The exact ear, frequency, conduction method, masking state and optional clamping bounds of one HealthKit audiogram sensitivity test. The component value retains the supplied sensitivity; clamping bounds describe source limitations and do not authorize replacing that value or inventing a censoring comparator. Masking is absent only when the source API does not expose it."
Context: Observation.component
* value[x] 0..0
* extension contains frequency 1..1 and ear 1..1 and conduction 1..1 and masked 0..1 and clampingRange 0..1
* extension ^slicing.rules = #closed
* extension[frequency].extension 0..0
* extension[frequency].value[x] only Quantity
* extension[frequency].valueQuantity 1..1
* extension[frequency].valueQuantity.value 1..1
* extension[frequency].valueQuantity.system 1..1
* extension[frequency].valueQuantity.system = "http://unitsofmeasure.org" (exactly)
* extension[frequency].valueQuantity.code 1..1
* extension[frequency].valueQuantity.code = #Hz (exactly)
* extension[frequency].valueQuantity.comparator 0..0
* extension[frequency].valueQuantity obeys healthkit-audiogram-frequency-1
* extension[ear].extension 0..0
* extension[ear].value[x] only code
* extension[ear].valueCode 1..1
* extension[ear].valueCode from HealthKitAudiogramEarVS (required)
* extension[conduction].extension 0..0
* extension[conduction].value[x] only code
* extension[conduction].valueCode 1..1
* extension[conduction].valueCode = #air (exactly)
* extension[masked].extension 0..0
* extension[masked].value[x] only boolean
* extension[masked].valueBoolean 1..1
* extension[clampingRange].extension 0..0
* extension[clampingRange].value[x] only Range
* extension[clampingRange].valueRange 1..1
* extension[clampingRange].valueRange obeys healthkit-audiogram-clamping-1
* extension[clampingRange].valueRange.low.comparator 0..0
* extension[clampingRange].valueRange.high.comparator 0..0
* extension[clampingRange].valueRange.low.value 1..1
* extension[clampingRange].valueRange.low.system 1..1
* extension[clampingRange].valueRange.low.system = "http://unitsofmeasure.org" (exactly)
* extension[clampingRange].valueRange.low.code 1..1
* extension[clampingRange].valueRange.low.code = #dB (exactly)
* extension[clampingRange].valueRange.high.value 1..1
* extension[clampingRange].valueRange.high.system 1..1
* extension[clampingRange].valueRange.high.system = "http://unitsofmeasure.org" (exactly)
* extension[clampingRange].valueRange.high.code 1..1
* extension[clampingRange].valueRange.high.code = #dB (exactly)

CodeSystem: HealthKitAudiogramEarCS
Id: healthkit-audiogram-ear
Title: "HealthKit Audiogram Ear"
Description: "The ear tested by an audiogram sensitivity reading."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #left "Left ear" "The sensitivity test was presented to the left ear (HKAudiogramSensitivityTestSideLeft)."
* #right "Right ear" "The sensitivity test was presented to the right ear (HKAudiogramSensitivityTestSideRight)."

ValueSet: HealthKitAudiogramEarVS
Id: healthkit-audiogram-ear
Title: "HealthKit Audiogram Ear"
Description: "The ear tested by an audiogram sensitivity reading."
* ^experimental = false
* include codes from system HealthKitAudiogramEarCS

Invariant: healthkit-audiogram-frequency-1
Description: "An audiogram test frequency is positive."
Severity: #error
Expression: "value > 0"

Invariant: healthkit-audiogram-clamping-1
Description: "A source clamping range supplies at least one bound, and its lower bound is strictly less than its upper bound when both are present."
Severity: #error
Expression: "(low.exists() or high.exists()) and ((low.exists() and high.exists()) implies (low.value < high.value))"
