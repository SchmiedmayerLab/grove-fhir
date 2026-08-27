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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:CgJR6EVUlWnxOnyiukqmVBJ8ko8YtTsMgRm7s-UNY6E"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:H3fU-ODXFfHnfUbXUBI-DQpfzBfHQCkDb9dmyAuAzeE"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ew4CVFKZHEpHNqNsw-A8dRLmogxC-Y1xc0FVW9fu8lE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:OrfDA2z9goXP0DXRBeCX0HfLu7slTvztkEYxvwF8Xuk"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:EOj0LOJpCrmTlMqoGQZKlk1I9pi3Q2B2cBRr0oHRsnM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:nAZFdvmLuuWfhmn2Wx7e0RIjc43acMY30zbYKCWXpBU"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:EomMSvG1D6I2PxXi2kHJjTzv-OJHEp4i-MliBLoeRss"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:PH8AzPMxL-7PMO59h-gB2ktMmOvMWloPfxMQt0U1iV8"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:tvQXzIZ925fQQqX-RguslTK8CnDZDTdMkB0xvvD-Ai8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:zyKd7MT0WOCi57SWEN9XCGxZCNTWPw70CRxQdNVuvp8"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:cYCx6vDFVjZmTE8X8x8Rph0u6eLD6HmLikQp_CuUQyQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:UAPDJojd1TWQAac7E8VolZH4xqOe5zFFr_ogKqoW7ks"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:pwvJiT77MfG8sY98PROASrWY7N8zdYDapXQ8TNQ-9nk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:knOcSq4ss9D7ypabt878hFRY7tnjFBTetlI5_8doeh8"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:rGvghR-g-p3aKIl3ZPBVzeB7Tu9npcO21X3E2UrJCuE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:h8pBGMJg6dJUe7lnF-C7Ok5YsdPGGEJq9GsagGGMgI0"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:2MTgpCH0n7Q53Y7vsPy5Io1meQfbFErUvZGnIIXUo_8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:7A2Q5yTo-M7eZk5vmI59Do8pjVw8WwuYBexZ127-c6U"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:8TTPXp507BaiNyrJck7KWiQimVNMMM8c8fAM4-u9Zwc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:48FbQsxK0lP-5tJ0-Jldw92XDOGg0gXEE0CIwsg7wWo"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:xloSJDkZYn2eR9IDArBKEu4542JNdTSlYEse4u8MUbQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:EP1a0ltu4N8LJlbZKUtN9dHFI1inpFL0it9glOvQX2U"
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
