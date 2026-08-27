// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: WithingsMeasurementCS
Id: withings-measurement
Title: "Withings Measurement"
Description: "Measurement concepts defined by the Withings adapter for vendor-exclusive results no established code represents faithfully."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #extracellular-water-mass "Extracellular water mass" "The mass of body water outside cells as estimated by bioelectrical impedance analysis."
* #intracellular-water-mass "Intracellular water mass" "The mass of body water inside cells as estimated by bioelectrical impedance analysis."
* #sleeping-heart-rate-average "Sleeping heart rate average" "The mean heart rate across the exact sleep-session Observation effective Period."
* #withings-atrial-fibrillation-notification-ecg "Withings atrial fibrillation notification (ECG)" "A Withings screening notification stating that the vendor's electrocardiogram algorithm flagged signs of atrial fibrillation in the recording taken at the Observation effective instant."
* #withings-atrial-fibrillation-notification-ppg "Withings atrial fibrillation notification (PPG)" "A Withings screening notification stating that the vendor's photoplethysmography algorithm flagged signs of atrial fibrillation in the reading taken at the Observation effective instant."
* #withings-nerve-health-score "Withings nerve health score" "The bounded figure Withings' proprietary nerve-health algorithm computes from electrochemical skin conductance at the feet, at the Observation effective instant."
* #withings-pulse-wave-velocity "Withings pulse wave velocity" "The aortic pulse-wave velocity Withings' proprietary scale algorithm estimates at the Observation effective instant, in metres per second."
* #withings-vascular-age "Withings vascular age" "The age-scaled figure Withings' proprietary vascular-age algorithm derives from its own pulse-wave velocity estimate, at the Observation effective instant."
* #withings-visceral-fat-index "Withings visceral fat index" "The bounded figure Withings' proprietary body-composition algorithm reports for abdominal visceral fat at the Observation effective instant."

ValueSet: WithingsMeasurementVS
Id: withings-measurement
Title: "Withings Measurement"
Description: "Measurement concepts defined by the Withings adapter for its vendor-exclusive profiles."
* ^experimental = false
* include codes from system WithingsMeasurementCS

CodeSystem: WithingsAtrialFibrillationNotificationEcgCS
Id: withings-atrial-fibrillation-notification-ecg
Title: "Withings Atrial Fibrillation Notification (ECG) Result"
Description: "The closed result codes of the Withings Atrial Fibrillation Notification (ECG) measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #signs-detected "Signs Detected" "The vendor's electrocardiogram screening algorithm flagged signs of atrial fibrillation in this recording. Nothing beyond the notification is asserted."

ValueSet: WithingsAtrialFibrillationNotificationEcgVS
Id: withings-atrial-fibrillation-notification-ecg
Title: "Withings Atrial Fibrillation Notification (ECG) Result"
Description: "Every admitted result code of the Withings Atrial Fibrillation Notification (ECG) measurement."
* ^experimental = false
* include codes from system WithingsAtrialFibrillationNotificationEcgCS

CodeSystem: WithingsAtrialFibrillationNotificationPpgCS
Id: withings-atrial-fibrillation-notification-ppg
Title: "Withings Atrial Fibrillation Notification (PPG) Result"
Description: "The closed result codes of the Withings Atrial Fibrillation Notification (PPG) measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #signs-detected "Signs Detected" "The vendor's photoplethysmography screening algorithm flagged signs of atrial fibrillation in this reading. Nothing beyond the notification is asserted."

ValueSet: WithingsAtrialFibrillationNotificationPpgVS
Id: withings-atrial-fibrillation-notification-ppg
Title: "Withings Atrial Fibrillation Notification (PPG) Result"
Description: "Every admitted result code of the Withings Atrial Fibrillation Notification (PPG) measurement."
* ^experimental = false
* include codes from system WithingsAtrialFibrillationNotificationPpgCS

Profile: WithingsBodyFatMass
Parent: WithingsObservation
Id: withings-body-fat-mass
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

Profile: WithingsCorrectedQtInterval
Parent: WithingsObservation
Id: withings-corrected-qt-interval
Title: "Corrected QT Interval"
Description: "The rate-corrected QT interval a Withings device reports alongside its own electrocardiogram, normalized to UCUM milliseconds. Only Withings reports the correction as a discrete measure, so the profile is provider-scoped. The interval is the vendor algorithm's reading of its own recording; no rhythm interpretation, repolarization finding, or diagnosis is asserted, and the correction formula the vendor applied is not published, so the value is not interchangeable with a QTc read from a clinical twelve-lead electrocardiogram."
* code = $loinc#8636-3
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: WithingsExtracellularWaterMass
Parent: WithingsObservation
Id: withings-extracellular-water-mass
Title: "Extracellular Water Mass"
Description: "Mass of extracellular body water estimated by bioelectrical impedance, normalized to UCUM kilograms. Only Withings evidences the compartmentalized value, so the profile is provider-scoped and is distinct from total body-water mass."
* code = WithingsMeasurementCS#extracellular-water-mass
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: WithingsIntracellularWaterMass
Parent: WithingsObservation
Id: withings-intracellular-water-mass
Title: "Intracellular Water Mass"
Description: "Mass of intracellular body water estimated by bioelectrical impedance, normalized to UCUM kilograms. Only Withings evidences the compartmentalized value, so the profile is provider-scoped and is distinct from total body-water mass."
* code = WithingsMeasurementCS#intracellular-water-mass
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: WithingsMuscleMass
Parent: WithingsObservation
Id: withings-muscle-mass
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

Profile: WithingsPrInterval
Parent: WithingsObservation
Id: withings-pr-interval
Title: "PR Interval"
Description: "The PR interval a Withings device measures from its own electrocardiogram, normalized to UCUM milliseconds. Only Withings reports it as a discrete measure, so the profile is provider-scoped. The interval is the vendor algorithm's reading of its own recording; no conduction finding, rhythm interpretation, or diagnosis is asserted."
* code = $loinc#8625-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: WithingsQrsDuration
Parent: WithingsObservation
Id: withings-qrs-duration
Title: "QRS Duration"
Description: "The QRS complex duration a Withings device measures from its own electrocardiogram, normalized to UCUM milliseconds. Only Withings reports it as a discrete measure, so the profile is provider-scoped. The interval is the vendor algorithm's reading of its own recording; no conduction finding, rhythm interpretation, or diagnosis is asserted."
* code = $loinc#8633-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: WithingsQtInterval
Parent: WithingsObservation
Id: withings-qt-interval
Title: "QT Interval"
Description: "The uncorrected QT interval a Withings device measures from its own electrocardiogram, normalized to UCUM milliseconds. Only Withings reports it as a discrete measure, so the profile is provider-scoped. The interval is the vendor algorithm's reading of its own recording; no repolarization finding, rhythm interpretation, or diagnosis is asserted, and the rate correction is a separate measurement."
* code = $loinc#8634-8
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: WithingsSleepingHeartRateAverage
Parent: WithingsObservation
Id: withings-sleeping-heart-rate-average
Title: "Sleeping Heart Rate Average"
Description: "The average heart rate across one sleep session, normalized to UCUM beats per minute. It is a session-windowed average, distinct from both the shared point heart-rate measurement and the daily resting-heart-rate estimate, and is implemented by the phase-2 aggregate design."
* code = WithingsMeasurementCS#sleeping-heart-rate-average
* code from WithingsMeasurementVS (required)
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

Profile: WithingsAtrialFibrillationNotificationEcg
Parent: WithingsObservation
Id: withings-atrial-fibrillation-notification-ecg
Title: "Withings Atrial Fibrillation Notification (ECG)"
Description: "Withings meastype 130: a screening notification from the vendor's proprietary electrocardiogram algorithm. It is emitted as a notification and never as a rhythm finding, exactly as the HealthKit irregular-heart-rhythm notification is: the recording itself remains the rhythm evidence. The adapter admits an Observation only for the vendor's positive screening classification; Withings publishes no encoding for the numeric measure.value, so no negative result, no inconclusive result, and no diagnosis is asserted. The code is deliberately taken from the providers code system so no receiver can read it as an atrial-fibrillation finding."
* code = WithingsMeasurementCS#withings-atrial-fibrillation-notification-ecg
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from WithingsAtrialFibrillationNotificationEcgVS (required)

Profile: WithingsAtrialFibrillationNotificationPpg
Parent: WithingsObservation
Id: withings-atrial-fibrillation-notification-ppg
Title: "Withings Atrial Fibrillation Notification (PPG)"
Description: "Withings meastype 139: a screening notification from the vendor's proprietary photoplethysmography algorithm, kept separate from the electrocardiogram notification because it screens a different signal. It is emitted as a notification and never as a rhythm finding. The adapter admits an Observation only for the vendor's positive screening classification; Withings publishes no encoding for the numeric measure.value, so no negative result, no inconclusive result, and no diagnosis is asserted. The code is deliberately taken from the providers code system so no receiver can read it as an atrial-fibrillation finding."
* code = WithingsMeasurementCS#withings-atrial-fibrillation-notification-ppg
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from WithingsAtrialFibrillationNotificationPpgVS (required)

Profile: WithingsNerveHealthScore
Parent: WithingsObservation
Id: withings-nerve-health-score
Title: "Withings Nerve Health Score"
Description: "Withings meastype 167: the vendor's nerve-health figure, computed by an undisclosed algorithm from electrochemical skin conductance measured at the feet. The vendor publishes no physical unit for it, so it carries the dimensionless UCUM {score} annotation rather than an invented unit or the conductance it derives from, and the profile description is the only statement of its scale. Withings positions the figure as small-fiber-neuropathy screening, so it is deliberately coded from the providers code system: it is a vendor screening figure and never a neuropathy finding or a diagnosis."
* code = WithingsMeasurementCS#withings-nerve-health-score
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{score} (exactly)

Profile: WithingsPulseWaveVelocity
Parent: WithingsObservation
Id: withings-pulse-wave-velocity
Title: "Withings Pulse Wave Velocity"
Description: "Withings meastype 91: the vendor's aortic pulse-wave velocity estimate, produced by an undisclosed single-vendor scale algorithm and normalized to UCUM metres per second. It is deliberately coded from the providers code system rather than a shared arterial-stiffness code, because no second source evidences it and the estimate is not interchangeable with a tonometric pulse-wave velocity measured in clinic. It is a wellness estimate and never an arterial-stiffness diagnosis."
* code = WithingsMeasurementCS#withings-pulse-wave-velocity
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m/s (exactly)

Profile: WithingsVascularAge
Parent: WithingsObservation
Id: withings-vascular-age
Title: "Withings Vascular Age"
Description: "Withings meastype 155: the vendor's vascular-age figure, derived by an undisclosed algorithm from the pulse-wave velocity the same scale estimates, and reported on an age scale in UCUM years. It is a vendor score expressed in years, not a chronological age and not a vascular assessment. It is deliberately a separate measurement from the Oura cardiovascular age: the two are undisclosed algorithms over different inputs, so a shared code would fabricate a comparability neither vendor defines."
* code = WithingsMeasurementCS#withings-vascular-age
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #a (exactly)

Profile: WithingsVisceralFatIndex
Parent: WithingsObservation
Id: withings-visceral-fat-index
Title: "Withings Visceral Fat Index"
Description: "Withings meastype 170: the vendor's visceral-fat figure, which the API returns without a unit. It is a bounded rating on the vendor's own scale rather than a mass or an area, so it carries the dimensionless UCUM {score} annotation instead of an invented mass or area unit, and it is kept apart from every shared body-composition measurement. The profile description is the only statement of its scale, and no comparability with another vendor's visceral-fat figure is asserted."
* code = WithingsMeasurementCS#withings-visceral-fat-index
* code from WithingsMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{score} (exactly)

Instance: WithingsBodyFatMassExample
InstanceOf: WithingsBodyFatMass
Usage: #example
Title: "Body Fat Mass Example"
Description: "A conformant Body Fat Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|body-fat-mass|record-body-fat-mass"
* status = #final
* code = $loinc#73708-0 "Body fat [Mass] Calculated"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:8
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 16.4 'kg'

Instance: WithingsCorrectedQtIntervalExample
InstanceOf: WithingsCorrectedQtInterval
Usage: #example
Title: "Corrected QT Interval Example"
Description: "A conformant Corrected QT Interval instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|corrected-qt-interval|record-corrected-qt-interval"
* status = #final
* code = $loinc#8636-3 "Q-T interval corrected"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:138
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 410 'ms'

Instance: WithingsExtracellularWaterMassExample
InstanceOf: WithingsExtracellularWaterMass
Usage: #example
Title: "Extracellular Water Mass Example"
Description: "A conformant Extracellular Water Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|extracellular-water-mass|record-extracellular-water-mass"
* status = #final
* code = WithingsMeasurementCS#extracellular-water-mass
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:168
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 17 'kg'

Instance: WithingsIntracellularWaterMassExample
InstanceOf: WithingsIntracellularWaterMass
Usage: #example
Title: "Intracellular Water Mass Example"
Description: "A conformant Intracellular Water Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|intracellular-water-mass|record-intracellular-water-mass"
* status = #final
* code = WithingsMeasurementCS#intracellular-water-mass
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:169
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 25 'kg'

Instance: WithingsMuscleMassExample
InstanceOf: WithingsMuscleMass
Usage: #example
Title: "Muscle Mass Example"
Description: "A conformant Muscle Mass instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|muscle-mass|record-muscle-mass"
* status = #final
* code = $loinc#73964-9 "Body muscle mass Calculated"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:76
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 31.5 'kg'

Instance: WithingsPrIntervalExample
InstanceOf: WithingsPrInterval
Usage: #example
Title: "PR Interval Example"
Description: "A conformant PR Interval instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|pr-interval|record-pr-interval"
* status = #final
* code = $loinc#8625-6 "P-R Interval"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:136
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 160 'ms'

Instance: WithingsQrsDurationExample
InstanceOf: WithingsQrsDuration
Usage: #example
Title: "QRS Duration Example"
Description: "A conformant QRS Duration instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|qrs-duration|record-qrs-duration"
* status = #final
* code = $loinc#8633-0 "QRS duration"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:135
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 92 'ms'

Instance: WithingsQtIntervalExample
InstanceOf: WithingsQtInterval
Usage: #example
Title: "QT Interval Example"
Description: "A conformant QT Interval instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|qt-interval|record-qt-interval"
* status = #final
* code = $loinc#8634-8 "Q-T interval"
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:137
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 390 'ms'

Instance: WithingsSleepingHeartRateAverageExample
InstanceOf: WithingsSleepingHeartRateAverage
Usage: #example
Title: "Sleeping Heart Rate Average Example"
Description: "A conformant Sleeping Heart Rate Average instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|sleeping-heart-rate-average|record-sleeping-heart-rate-average"
* status = #final
* code = WithingsMeasurementCS#sleeping-heart-rate-average
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getsummary:hr_average
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 55 '/min' "beats/minute"

Instance: WithingsAtrialFibrillationNotificationEcgExample
InstanceOf: WithingsAtrialFibrillationNotificationEcg
Usage: #example
Title: "Withings Atrial Fibrillation Notification (ECG) Example"
Description: "A conformant Withings Atrial Fibrillation Notification (ECG) instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|withings-atrial-fibrillation-notification-ecg|record-withings-atrial-fibrillation-notification-ecg"
* status = #final
* code = WithingsMeasurementCS#withings-atrial-fibrillation-notification-ecg
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:130
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueCodeableConcept = WithingsAtrialFibrillationNotificationEcgCS#signs-detected "Signs Detected"

Instance: WithingsAtrialFibrillationNotificationPpgExample
InstanceOf: WithingsAtrialFibrillationNotificationPpg
Usage: #example
Title: "Withings Atrial Fibrillation Notification (PPG) Example"
Description: "A conformant Withings Atrial Fibrillation Notification (PPG) instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|withings-atrial-fibrillation-notification-ppg|record-withings-atrial-fibrillation-notification-ppg"
* status = #final
* code = WithingsMeasurementCS#withings-atrial-fibrillation-notification-ppg
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:139
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueCodeableConcept = WithingsAtrialFibrillationNotificationPpgCS#signs-detected "Signs Detected"

Instance: WithingsNerveHealthScoreExample
InstanceOf: WithingsNerveHealthScore
Usage: #example
Title: "Withings Nerve Health Score Example"
Description: "A conformant Withings Nerve Health Score instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|withings-nerve-health-score|record-withings-nerve-health-score"
* status = #final
* code = WithingsMeasurementCS#withings-nerve-health-score
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:167
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 80 '{score}' "score"

Instance: WithingsPulseWaveVelocityExample
InstanceOf: WithingsPulseWaveVelocity
Usage: #example
Title: "Withings Pulse Wave Velocity Example"
Description: "A conformant Withings Pulse Wave Velocity instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|withings-pulse-wave-velocity|record-withings-pulse-wave-velocity"
* status = #final
* code = WithingsMeasurementCS#withings-pulse-wave-velocity
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:91
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 7.5 'm/s'

Instance: WithingsVascularAgeExample
InstanceOf: WithingsVascularAge
Usage: #example
Title: "Withings Vascular Age Example"
Description: "A conformant Withings Vascular Age instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|withings-vascular-age|record-withings-vascular-age"
* status = #final
* code = WithingsMeasurementCS#withings-vascular-age
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:155
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 45 'a' "years"

Instance: WithingsVisceralFatIndexExample
InstanceOf: WithingsVisceralFatIndex
Usage: #example
Title: "Withings Visceral Fat Index Example"
Description: "A conformant Withings Visceral Fat Index instance."
* identifier[sourceRecordId].system = $providerSourceRecordId
* identifier[sourceRecordId].value = "v1:withings|acct-7f3a9c|withings-visceral-fat-index|record-withings-visceral-fat-index"
* status = #final
* code = WithingsMeasurementCS#withings-visceral-fat-index
* extension[provider].valueCode = #withings
* extension[providerSourceType].valueCode = #withings/getmeas:170
* subject = Reference(WithingsPatientExample)
* performer = Reference(WithingsPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 8 '{score}' "score"
