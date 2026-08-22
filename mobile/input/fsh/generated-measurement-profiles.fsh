// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: GroveMobileMeasurementCS
Id: grove-mobile-measurement
Title: "Grove Mobile Measurement"
Description: "Measurement concepts defined by the Grove Mobile contract when an established code would not faithfully represent the exchanged result."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #active-energy-burned "Active energy burned" "Energy expended through activity, excluding basal energy, during the exact Observation effective Period."
* #basal-body-temperature "Basal body temperature" "Body temperature recorded at physiologic rest for fertility-awareness or cycle-tracking use; it is distinct from a general body-temperature vital sign."
* #sleep-stage "Sleep stage" "The classification assigned to an exact interval within a sleep session."
* #step-count-total "Step count total" "The total number of steps attributed to the exact Observation effective Period."

ValueSet: GroveMobileMeasurementVS
Id: grove-mobile-measurement
Title: "Grove Mobile Measurement"
Description: "Measurement concepts defined by Grove Mobile for use in its focused domain profiles."
* ^experimental = false
* include codes from system GroveMobileMeasurementCS

Profile: GroveMobileActiveEnergy
Parent: GroveMobileObservation
Id: grove-mobile-active-energy
Title: "Grove Mobile Active Energy"
Description: "Activity-related energy expenditure, excluding basal energy, during an exact effective Period and normalized to UCUM kilocalories."
* code = GroveMobileMeasurementCS#active-energy-burned
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal (exactly)

Profile: GroveMobileBasalBodyTemperature
Parent: GroveMobileObservation
Id: grove-mobile-basal-body-temperature
Title: "Grove Mobile Basal Body Temperature"
Description: "A source-neutral basal body temperature recorded at physiologic rest and normalized to UCUM degrees Celsius. It is not the general body-temperature vital sign."
* code = GroveMobileMeasurementCS#basal-body-temperature
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #Cel (exactly)

Profile: GroveMobileBloodPressure
Parent: GroveMobileObservation
Id: grove-mobile-blood-pressure
Title: "Grove Mobile Blood Pressure"
Description: "A source-neutral mobile blood-pressure panel that is required to conform to the authoritative FHIR R4 Blood Pressure profile. Systolic and diastolic components are normalized to UCUM millimetres of mercury."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bloodPressure
* code = $loinc#85354-9
* effective[x] only dateTime
* value[x] 0..0
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains systolic 1..1 MS and diastolic 1..1 MS
* component[systolic].code = $loinc#8480-6
* component[systolic].value[x] only Quantity
* component[systolic].valueQuantity.value 1..1 MS
* component[systolic].valueQuantity.system = $ucum (exactly)
* component[systolic].valueQuantity.code = #mm[Hg] (exactly)
* component[diastolic].code = $loinc#8462-4
* component[diastolic].value[x] only Quantity
* component[diastolic].valueQuantity.value 1..1 MS
* component[diastolic].valueQuantity.system = $ucum (exactly)
* component[diastolic].valueQuantity.code = #mm[Hg] (exactly)

Profile: GroveMobileBodyHeight
Parent: GroveMobileObservation
Id: grove-mobile-body-height
Title: "Grove Mobile Body Height"
Description: "A source-neutral mobile body height that is required to conform to the authoritative FHIR R4 Body Height profile. Values are normalized to UCUM centimetres."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyHeight
* code = $loinc#8302-2
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #cm (exactly)

Profile: GroveMobileBodyTemperature
Parent: GroveMobileObservation
Id: grove-mobile-body-temperature
Title: "Grove Mobile Body Temperature"
Description: "A source-neutral mobile body temperature that is required to conform to the authoritative FHIR R4 Body Temperature profile. Values are normalized to UCUM degrees Celsius."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyTemperature
* code = $loinc#8310-5
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #Cel (exactly)

Profile: GroveMobileBodyWeight
Parent: GroveMobileObservation
Id: grove-mobile-body-weight
Title: "Grove Mobile Body Weight"
Description: "A source-neutral mobile body weight that is required to conform to the authoritative FHIR R4 Body Weight profile. Values are normalized to UCUM kilograms."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyWeight
* code = $loinc#29463-7
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #kg (exactly)

Profile: GroveMobileDistance
Parent: GroveMobileObservation
Id: grove-mobile-distance
Title: "Grove Mobile Distance"
Description: "Distance traveled during an exact effective Period, normalized to UCUM metres."
* code = $loinc#103208-5
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: GroveMobileHeartRate
Parent: GroveMobileObservation
Id: grove-mobile-heart-rate
Title: "Grove Mobile Heart Rate"
Description: "A source-neutral mobile heart rate that is required to conform to the authoritative FHIR R4 Heart Rate profile and adds Grove exchange identity and provenance context. Values are normalized to UCUM beats per minute."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $heartRate
* code = $loinc#8867-4
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileOxygenSaturation
Parent: GroveMobileObservation
Id: grove-mobile-oxygen-saturation
Title: "Grove Mobile Oxygen Saturation"
Description: "A source-neutral mobile oxygen saturation that is required to conform to the authoritative FHIR R4 Oxygen Saturation profile. Values are normalized to UCUM percent."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $oxygenSaturation
* code = $loinc#2708-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #% (exactly)

Profile: GroveMobileRespiratoryRate
Parent: GroveMobileObservation
Id: grove-mobile-respiratory-rate
Title: "Grove Mobile Respiratory Rate"
Description: "A source-neutral mobile respiratory rate that is required to conform to the authoritative FHIR R4 Respiratory Rate profile. Values are normalized to breaths per minute."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $respiratoryRate
* code = $loinc#9279-1
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileSleepDuration
Parent: GroveMobileObservation
Id: grove-mobile-sleep-duration
Title: "Grove Mobile Sleep Duration"
Description: "Total duration classified as sleep during an exact effective Period, using LOINC Sleep duration and normalized to UCUM hours. This summary does not encode sleep stages."
* code = $loinc#93832-4
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #h (exactly)
* hasMember only Reference(GroveMobileSleepStage)

Profile: GroveMobileSleepStage
Parent: GroveMobileObservation
Id: grove-mobile-sleep-stage
Title: "Grove Mobile Sleep Stage"
Description: "A source-neutral sleep-stage classification for one exact interval. A session summary links its ordered, non-overlapping stage Observations through hasMember."
* code = GroveMobileMeasurementCS#sleep-stage
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSleepStageVS (required)

Profile: GroveMobileStepCount
Parent: GroveMobileObservation
Id: grove-mobile-step-count
Title: "Grove Mobile Step Count"
Description: "The number of steps recorded during an exact effective Period."
* obeys grove-step-count-result-1 and grove-step-count-period-1 and grove-step-count-value-1
* code = GroveMobileMeasurementCS#step-count-total
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.unit MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{steps} (exactly)
