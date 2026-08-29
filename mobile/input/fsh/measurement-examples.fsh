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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:yGe6KDyVzvGSzueoxgUdq7iS4_OJx9ytlyiB0DcjFos"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:7AuldIGGAR2Wsz3Q3dNqQbsbpyr-svBj_JR9ncLR4dM"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:6AykPv-ckpB_hZvBZf42tZlCFTyFdxYMUTBi8sStA8A"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:SCbojcAqxKO6feQGH_XGjfL5teOCQ9CRI5hRbKE6OQs"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:MZcxSiVOcCnyGZdLNt0ZIGGYhiS4s0BvF0mk3C2xNBQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:XK9Tw0QtuyK9pCXAl5RXFYSsl8wF5bU_sFsaobpb2JM"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:7GMRoxEYrskAZlk7X61RA01CvVyBxJQQVg5VnZR82sQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:fLEOsPu95GWnD-w9OpRoV6H_VtAyuuP278ELMu0ybIw"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:zZ6mbj6vg0JPw09r0XI6SGorZPfSiBPgKagJRO42BUU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:qd5LVBCUpNKL54W9N8uJktNzs7wMRKGIXpYU6TtqE3A"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:kMnrY36dIWrOc1siPQSlo33KJIneTlBYjqCiACu_Szg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:isqLm4lzkBL2SxUyCCEQ_EQledYKxU40G_Dh71p8CMk"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ps9kiZbdAAGgODsQeMvRSdxdMZ2Vt69NEk0bKvxvcUc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:O3VR_P2iGFYHZmxKcsnkU4rAm0r9Zizibx1BvJnWDII"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:YFEDhhLWTdiXopijWy8K1GJ_qkzigZbvTOdWZkQRKIo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:H76mdecriUGFn5Yk40cTqWhmynug32ZhU3kbpDqqh_c"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:7CbBvKGGSqyNoRAvuF5y9Mf7XVr7wSc4b21_Uc5bQ7A"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:DyaWNxYfqUAc31DBSJPXW6h0aJkg9sPfvYKRIePxXjw"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:SUSJfi0zdKdcNxk2zJWHciyqNRljqTTtlA0fkP8nf04"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:duhz86mYGMPiKFHymhOinO5eYGmNK6lYEqpC6UFmQBQ"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:GO87h82yTSfH2jVPz6Npx7090eQ1NMiPV0e_80RsiY8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:qla_P5YCyjaHqGwpc3mDpht0TFCIyU8UL3wB86JGIQg"
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
