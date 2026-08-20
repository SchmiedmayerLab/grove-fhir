//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: GroveMobileActiveEnergyExample
InstanceOf: GroveMobileActiveEnergy
Usage: #example
Title: "Source-neutral Mobile Active Energy"
Description: "An interval total of activity-related energy expenditure."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "active-energy-20260820-001"
* status = #final
* category = $observationCategory#activity "Activity"
* code = GroveMobileMeasurementCS#active-energy-burned "Active energy burned"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-20T08:00:00-07:00"
* effectivePeriod.end = "2026-08-20T09:00:00-07:00"
* issued = "2026-08-20T16:00:02Z"
* valueQuantity = 215 'kcal' "kcal"

Instance: GroveMobileBasalBodyTemperatureExample
InstanceOf: GroveMobileBasalBodyTemperature
Usage: #example
Title: "Source-neutral Mobile Basal Body Temperature"
Description: "A basal body temperature normalized to degrees Celsius."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "basal-body-temperature-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = GroveMobileMeasurementCS#basal-body-temperature "Basal body temperature"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T06:30:00-07:00"
* issued = "2026-08-20T13:30:02Z"
* valueQuantity = 36.4 'Cel' "°C"

Instance: GroveMobileBloodPressureExample
InstanceOf: GroveMobileBloodPressure
Usage: #example
Title: "Source-neutral Mobile Blood Pressure"
Description: "A blood-pressure panel with normalized systolic and diastolic components."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "blood-pressure-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#85354-9 "Blood pressure panel with all children optional"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T08:20:00-07:00"
* issued = "2026-08-20T15:20:02Z"
* component[systolic].code = $loinc#8480-6 "Systolic blood pressure"
* component[systolic].valueQuantity = 118 'mm[Hg]' "mmHg"
* component[diastolic].code = $loinc#8462-4 "Diastolic blood pressure"
* component[diastolic].valueQuantity = 76 'mm[Hg]' "mmHg"

Instance: GroveMobileBodyHeightExample
InstanceOf: GroveMobileBodyHeight
Usage: #example
Title: "Source-neutral Mobile Body Height"
Description: "A body height normalized to centimetres."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "body-height-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8302-2 "Body height"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T08:30:00-07:00"
* issued = "2026-08-20T15:30:02Z"
* valueQuantity = 174 'cm' "cm"

Instance: GroveMobileBodyTemperatureExample
InstanceOf: GroveMobileBodyTemperature
Usage: #example
Title: "Source-neutral Mobile Body Temperature"
Description: "A body temperature normalized to degrees Celsius."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "body-temperature-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8310-5 "Body temperature"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T08:35:00-07:00"
* issued = "2026-08-20T15:35:02Z"
* valueQuantity = 36.8 'Cel' "°C"

Instance: GroveMobileBodyWeightExample
InstanceOf: GroveMobileBodyWeight
Usage: #example
Title: "Source-neutral Mobile Body Weight"
Description: "A body weight normalized to kilograms."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "body-weight-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T08:40:00-07:00"
* issued = "2026-08-20T15:40:02Z"
* valueQuantity = 68.2 'kg' "kg"

Instance: GroveMobileDistanceExample
InstanceOf: GroveMobileDistance
Usage: #example
Title: "Source-neutral Mobile Distance"
Description: "An interval total of distance traveled."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "distance-20260820-001"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $loinc#103208-5 "Distance traveled"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-20T08:00:00-07:00"
* effectivePeriod.end = "2026-08-20T09:00:00-07:00"
* issued = "2026-08-20T16:00:02Z"
* valueQuantity = 1620 'm' "m"

Instance: GroveMobileOxygenSaturationExample
InstanceOf: GroveMobileOxygenSaturation
Usage: #example
Title: "Source-neutral Mobile Oxygen Saturation"
Description: "A peripheral oxygen saturation normalized to percent."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "oxygen-saturation-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#2708-6 "Oxygen saturation in Arterial blood"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T08:45:00-07:00"
* issued = "2026-08-20T15:45:02Z"
* valueQuantity = 98 '%' "%"

Instance: GroveMobileRespiratoryRateExample
InstanceOf: GroveMobileRespiratoryRate
Usage: #example
Title: "Source-neutral Mobile Respiratory Rate"
Description: "A respiratory rate normalized to breaths per minute."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "respiratory-rate-20260820-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#9279-1 "Respiratory rate"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-20T08:50:00-07:00"
* issued = "2026-08-20T15:50:02Z"
* valueQuantity = 15 '/min' "breaths/minute"

Instance: GroveMobileSleepStageExample
InstanceOf: GroveMobileSleepStage
Usage: #example
Title: "Source-neutral Mobile Sleep Stage"
Description: "One classified interval within a sleep session."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "sleep-stage-20260820-001"
* status = #final
* category = $observationCategory#activity "Activity"
* code = GroveMobileMeasurementCS#sleep-stage "Sleep stage"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-20T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:42:00-07:00"
* issued = "2026-08-20T14:00:02Z"
* valueCodeableConcept = GroveSleepStageCS#deep "Deep sleep"

Instance: GroveMobileSleepDurationExample
InstanceOf: GroveMobileSleepDuration
Usage: #example
Title: "Source-neutral Mobile Sleep Duration"
Description: "A sleep-session summary linked to its stage observations."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-observation"
* identifier.value = "sleep-duration-20260820-001"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $loinc#93832-4 "Sleep duration"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T23:00:00-07:00"
* effectivePeriod.end = "2026-08-20T07:00:00-07:00"
* issued = "2026-08-20T14:00:02Z"
* valueQuantity = 7.4 'h' "h"
* hasMember = Reference(GroveMobileSleepStageExample)
