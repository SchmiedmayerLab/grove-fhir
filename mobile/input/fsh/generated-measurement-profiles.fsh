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
* #basal-energy-burned "Basal energy burned" "Resting energy expended by basal metabolism, excluding activity energy, during the exact Observation effective Period."
* #cervical-mucus-quality "Cervical mucus quality" "The observed cervical mucus quality at the stated instant."
* #cycling-cadence "Cycling cadence" "The rate of crank revolutions the subject pedals at the exact Observation effective instant."
* #dietary-biotin "Dietary biotin" "Biotin consumed during the exact Observation effective Period."
* #dietary-caffeine "Dietary caffeine" "Caffeine consumed during the exact Observation effective Period."
* #dietary-calcium "Dietary calcium" "Calcium consumed during the exact Observation effective Period."
* #dietary-chloride "Dietary chloride" "Chloride consumed during the exact Observation effective Period."
* #dietary-cholesterol "Dietary cholesterol" "Cholesterol consumed during the exact Observation effective Period."
* #dietary-chromium "Dietary chromium" "Chromium consumed during the exact Observation effective Period."
* #dietary-copper "Dietary copper" "Copper consumed during the exact Observation effective Period."
* #dietary-fat-monounsaturated "Dietary monounsaturated fat" "Monounsaturated fat consumed during the exact Observation effective Period."
* #dietary-fat-polyunsaturated "Dietary polyunsaturated fat" "Polyunsaturated fat consumed during the exact Observation effective Period."
* #dietary-fat-saturated "Dietary saturated fat" "Saturated fat consumed during the exact Observation effective Period."
* #dietary-fiber "Dietary fiber" "Dietary fiber consumed during the exact Observation effective Period."
* #dietary-folate "Dietary folate" "Total folate consumed during the exact Observation effective Period."
* #dietary-iodine "Dietary iodine" "Iodine consumed during the exact Observation effective Period."
* #dietary-iron "Dietary iron" "Iron consumed during the exact Observation effective Period."
* #dietary-magnesium "Dietary magnesium" "Magnesium consumed during the exact Observation effective Period."
* #dietary-manganese "Dietary manganese" "Manganese consumed during the exact Observation effective Period."
* #dietary-molybdenum "Dietary molybdenum" "Molybdenum consumed during the exact Observation effective Period."
* #dietary-niacin "Dietary niacin" "Niacin consumed during the exact Observation effective Period."
* #dietary-pantothenic-acid "Dietary pantothenic acid" "Pantothenic acid consumed during the exact Observation effective Period."
* #dietary-phosphorus "Dietary phosphorus" "Phosphorus consumed during the exact Observation effective Period."
* #dietary-potassium "Dietary potassium" "Potassium consumed during the exact Observation effective Period."
* #dietary-riboflavin "Dietary riboflavin" "Riboflavin consumed during the exact Observation effective Period."
* #dietary-selenium "Dietary selenium" "Selenium consumed during the exact Observation effective Period."
* #dietary-sodium "Dietary sodium" "Sodium consumed during the exact Observation effective Period."
* #dietary-sugar "Dietary sugar" "Total sugars consumed from food and drink during the exact Observation effective Period."
* #dietary-thiamin "Dietary thiamin" "Thiamin consumed during the exact Observation effective Period."
* #dietary-vitamin-a "Dietary vitamin A" "Vitamin A consumed during the exact Observation effective Period."
* #dietary-vitamin-b12 "Dietary vitamin B12" "Vitamin B12 consumed during the exact Observation effective Period."
* #dietary-vitamin-b6 "Dietary vitamin B6" "Vitamin B6 consumed during the exact Observation effective Period."
* #dietary-vitamin-c "Dietary vitamin C" "Vitamin C consumed during the exact Observation effective Period."
* #dietary-vitamin-d "Dietary vitamin D" "Vitamin D consumed during the exact Observation effective Period."
* #dietary-vitamin-e "Dietary vitamin E" "Vitamin E consumed during the exact Observation effective Period."
* #dietary-vitamin-k "Dietary vitamin K" "Vitamin K consumed during the exact Observation effective Period."
* #dietary-zinc "Dietary zinc" "Zinc consumed during the exact Observation effective Period."
* #electrodermal-activity "Electrodermal activity" "The electrical conductance of the skin at the Observation effective instant."
* #heart-rate-variability-rmssd "Heart rate variability RMSSD" "The root mean square of successive differences between adjacent NN intervals at the Observation effective instant."
* #intermenstrual-bleeding "Intermenstrual bleeding" "An observed bleeding event between menstrual periods."
* #menstruation-flow "Menstruation flow" "The observed menstrual flow classification at the stated instant."
* #mindfulness-session-duration "Mindfulness session duration" "The duration of a single mindfulness session covering the exact Observation effective Period."
* #ovulation-test-result "Ovulation test result" "The classified result of a home ovulation test."
* #power "Power" "The mechanical power the subject produces at the exact Observation effective instant, recorded during activity."
* #sexual-activity "Sexual activity" "A logged sexual-activity event with its protection-used classification."
* #sleep-heart-rate "Sleep heart rate" "A heart-rate statistic aggregated over the exact sleep-session effective Period."
* #sleep-stage "Sleep stage" "The classification assigned to an exact interval within a sleep session."
* #speed "Speed" "The subject's instantaneous speed of travel at the exact Observation effective instant, recorded during activity."
* #step-count-total "Step count total" "The total number of steps attributed to the exact Observation effective Period."
* #vo2-max "VO2 max" "The maximal oxygen consumption per kilogram of body mass, whether measured or estimated, reported at the Observation effective instant."
* #workout "Workout session" "One recorded workout session over the exact Observation effective Period."
* #workout-segment "Workout segment" "One classified interval or event within a workout session."
* #cervical-mucus-sensation "Cervical mucus sensation" "The reported cervical mucus sensation accompanying a quality observation."
* #menstrual-cycle-start "Menstrual cycle start" "Whether the flow observation marks the first day of a menstrual cycle, as the source states it."

ValueSet: GroveMobileMeasurementVS
Id: grove-mobile-measurement
Title: "Grove Mobile Measurement"
Description: "Measurement concepts defined by Grove Mobile for use in its focused domain profiles."
* ^experimental = false
* include codes from system GroveMobileMeasurementCS

CodeSystem: GroveCervicalMucusQualityCS
Id: grove-cervical-mucus-quality
Title: "Cervical Mucus Quality Result"
Description: "The closed result codes of the Cervical Mucus Quality measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #dry "Dry" "No cervical mucus observed."
* #sticky "Sticky" "Sticky cervical mucus."
* #creamy "Creamy" "Creamy cervical mucus."
* #watery "Watery" "Watery cervical mucus."
* #egg-white "Egg white" "Stretchy egg-white cervical mucus."
* #unusual "Unusual" "An unusual observation that fits no listed quality."
* #unknown "Unknown" "The quality was recorded without a usable classification."

ValueSet: GroveCervicalMucusQualityVS
Id: grove-cervical-mucus-quality
Title: "Cervical Mucus Quality Result"
Description: "Every admitted result code of the Cervical Mucus Quality measurement."
* ^experimental = false
* include codes from system GroveCervicalMucusQualityCS

CodeSystem: GroveCervicalMucusSensationCS
Id: grove-cervical-mucus-sensation
Title: "Cervical Mucus Sensation Result"
Description: "The closed result codes of the Cervical Mucus Sensation measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #light "Light" "A light sensation."
* #medium "Medium" "A medium sensation."
* #heavy "Heavy" "A heavy sensation."

ValueSet: GroveCervicalMucusSensationVS
Id: grove-cervical-mucus-sensation
Title: "Cervical Mucus Sensation Result"
Description: "Every admitted result code of the Cervical Mucus Sensation measurement."
* ^experimental = false
* include codes from system GroveCervicalMucusSensationCS

CodeSystem: GroveIntermenstrualBleedingCS
Id: grove-intermenstrual-bleeding
Title: "Intermenstrual Bleeding Result"
Description: "The closed result codes of the Intermenstrual Bleeding measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #present "Present" "Intermenstrual bleeding was observed."

ValueSet: GroveIntermenstrualBleedingVS
Id: grove-intermenstrual-bleeding
Title: "Intermenstrual Bleeding Result"
Description: "Every admitted result code of the Intermenstrual Bleeding measurement."
* ^experimental = false
* include codes from system GroveIntermenstrualBleedingCS

CodeSystem: GroveMenstruationFlowCS
Id: grove-menstruation-flow
Title: "Menstruation Flow Result"
Description: "The closed result codes of the Menstruation Flow measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #unspecified "Unspecified" "Flow was recorded without an amount."
* #light "Light" "Light flow."
* #medium "Medium" "Medium flow."
* #heavy "Heavy" "Heavy flow."
* #none "None" "No flow was observed; recorded only by HealthKit."

ValueSet: GroveMenstruationFlowVS
Id: grove-menstruation-flow
Title: "Menstruation Flow Result"
Description: "Every admitted result code of the Menstruation Flow measurement."
* ^experimental = false
* include codes from system GroveMenstruationFlowCS

CodeSystem: GroveMenstrualCycleStartCS
Id: grove-menstrual-cycle-start
Title: "Menstrual Cycle Start Result"
Description: "The closed result codes of the Menstrual Cycle Start measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #cycle-start "Cycle start" "The observation marks the first day of a menstrual cycle."
* #not-cycle-start "Not cycle start" "The observation does not mark the first day of a menstrual cycle."

ValueSet: GroveMenstrualCycleStartVS
Id: grove-menstrual-cycle-start
Title: "Menstrual Cycle Start Result"
Description: "Every admitted result code of the Menstrual Cycle Start measurement."
* ^experimental = false
* include codes from system GroveMenstrualCycleStartCS

CodeSystem: GroveOvulationTestResultCS
Id: grove-ovulation-test-result
Title: "Ovulation Test Result Result"
Description: "The closed result codes of the Ovulation Test Result measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #negative "Negative" "No fertility surge detected."
* #high-fertility "High fertility" "An elevated fertility indicator short of a confirmed LH surge."
* #luteinizing-hormone-surge "Luteinizing hormone surge" "A confirmed luteinizing hormone surge."
* #indeterminate "Indeterminate" "The test could not be interpreted."

ValueSet: GroveOvulationTestResultVS
Id: grove-ovulation-test-result
Title: "Ovulation Test Result Result"
Description: "Every admitted result code of the Ovulation Test Result measurement."
* ^experimental = false
* include codes from system GroveOvulationTestResultCS

CodeSystem: GroveSexualActivityCS
Id: grove-sexual-activity
Title: "Sexual Activity Result"
Description: "The closed result codes of the Sexual Activity measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #protected "Protection used" "Protection was reported used."
* #unprotected "Protection not used" "Protection was reported not used."
* #unknown "Unknown" "Protection use was not reported."

ValueSet: GroveSexualActivityVS
Id: grove-sexual-activity
Title: "Sexual Activity Result"
Description: "Every admitted result code of the Sexual Activity measurement."
* ^experimental = false
* include codes from system GroveSexualActivityCS

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

Profile: GroveMobileBasalEnergy
Parent: GroveMobileObservation
Id: grove-mobile-basal-energy
Title: "Basal Energy Burned"
Description: "Resting (basal) energy expenditure accrued during an exact effective Period, normalized to UCUM kilocalories. It is disjoint from active-energy: the two measurements never overlap in meaning and are summed only by consumers."
* code = GroveMobileMeasurementCS#basal-energy-burned
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

Profile: GroveMobileBloodGlucoseUnspecifiedSpecimen
Parent: GroveMobileObservation
Id: grove-mobile-blood-glucose-unspecified-specimen
Title: "Blood Glucose (Unspecified Specimen)"
Description: "A glucose mass concentration whose source supplies no specimen evidence, normalized to UCUM mg/dL. The profile REQUIRES the Observation specimen coding to be ABSENT, keeping it disjoint from the four specimen-specific Health Connect glucose profiles that require an exact SNOMED specimen coding."
* code = $loinc#2339-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 0..0

Profile: GroveMobileBloodPressure
Parent: GroveMobileObservation
Id: grove-mobile-blood-pressure
Title: "Grove Mobile Blood Pressure"
Description: "A source-neutral mobile blood-pressure panel that is required to conform to the authoritative FHIR R4 Blood Pressure profile. Systolic and diastolic components are normalized to UCUM millimetres of mercury."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bloodPressure
* code = $loinc#85354-9
* category = $observationCategory#vital-signs
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

Invariant: grove-mobile-body-fat-percentage-value-domain-1
Description: "A populated Body Fat Percentage value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: GroveMobileBodyFatPercentage
Parent: GroveMobileObservation
Id: grove-mobile-body-fat-percentage
Title: "Body Fat Percentage"
Description: "A source-neutral body fat measurement expressed as a percentage of total body mass and normalized to UCUM percent. The measurement is method-neutral: sources include bioimpedance scales, connected providers, and manual entry, so no measurement method is asserted."
* obeys grove-mobile-body-fat-percentage-value-domain-1
* code = $loinc#41982-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)
* valueQuantity.value ^minValueDecimal = 0
* valueQuantity.value ^maxValueDecimal = 100

Profile: GroveMobileBodyHeight
Parent: GroveMobileObservation
Id: grove-mobile-body-height
Title: "Grove Mobile Body Height"
Description: "A source-neutral mobile body height that is required to conform to the authoritative FHIR R4 Body Height profile. Values are normalized to UCUM centimetres."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyHeight
* code = $loinc#8302-2
* category = $observationCategory#vital-signs
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #cm (exactly)

Profile: GroveMobileBodyTemperature
Parent: GroveMobileObservation
Id: grove-mobile-body-temperature
Title: "Grove Mobile Body Temperature"
Description: "A source-neutral mobile body temperature that is required to conform to the authoritative FHIR R4 Body Temperature profile. Values are normalized to UCUM degrees Celsius."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyTemperature
* code = $loinc#8310-5
* category = $observationCategory#vital-signs
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #Cel (exactly)

Profile: GroveMobileBodyWaterMass
Parent: GroveMobileObservation
Id: grove-mobile-body-water-mass
Title: "Body Water Mass"
Description: "A source-neutral total body water mass from body-composition analysis, normalized to UCUM kilograms. Despite Withings labeling its measure 'hydration', this is a body-composition mass and is deliberately distinct from dietary water intake."
* code = $loinc#101683-1
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: GroveMobileBodyWeight
Parent: GroveMobileObservation
Id: grove-mobile-body-weight
Title: "Grove Mobile Body Weight"
Description: "A source-neutral mobile body weight that is required to conform to the authoritative FHIR R4 Body Weight profile. Values are normalized to UCUM kilograms."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyWeight
* code = $loinc#29463-7
* category = $observationCategory#vital-signs
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: GroveMobileBoneMass
Parent: GroveMobileObservation
Id: grove-mobile-bone-mass
Title: "Bone Mass"
Description: "A source-neutral total bone mass from body-composition analysis, normalized to UCUM kilograms. It is an impedance-estimated mass and is deliberately distinct from DXA bone mineral density, which it never claims."
* code = $loinc#101685-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: GroveMobileCervicalMucusQuality
Parent: GroveMobileObservation
Id: grove-mobile-cervical-mucus-quality
Title: "Cervical Mucus Quality"
Description: "The observed cervical mucus quality for fertility awareness, with the exact platform value retained as a secondary coding. Health Connect's separate sensation axis rides an optional coded component that HealthKit never emits."
* code = GroveMobileMeasurementCS#cervical-mucus-quality
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveCervicalMucusQualityVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains sensation 0..1 MS
* component[sensation].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#cervical-mucus-sensation
* component[sensation].value[x] only CodeableConcept
* component[sensation].valueCodeableConcept MS
* component[sensation].valueCodeableConcept from GroveCervicalMucusSensationVS (required)

Profile: GroveMobileCyclingCadence
Parent: GroveMobileObservation
Id: grove-mobile-cycling-cadence
Title: "Cycling Cadence"
Description: "A source-neutral instantaneous cycling pedaling cadence sample, normalized to UCUM per minute and displayed as crank revolutions per minute. It is distinct from step cadence, whose counted event is a step rather than a crank revolution."
* code = GroveMobileMeasurementCS#cycling-cadence
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileDeepSleepDuration
Parent: GroveMobileObservation
Id: grove-mobile-deep-sleep-duration
Title: "Deep Sleep Duration"
Description: "Total time classified as deep sleep within one sleep session or civil-day summary, normalized to UCUM minutes over the exact session Period. It is a stage-total aggregate without per-stage intervals, distinct from the interval sleep-stage Observation, and is implemented by the phase-2 aggregate design."
* code = $loinc#93831-6
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = GroveAggregationMethodCS#session-total
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: GroveMobileDietaryBiotin
Parent: GroveMobileObservation
Id: grove-mobile-dietary-biotin
Title: "Grove Mobile Dietary Biotin"
Description: "Biotin (vitamin B7) consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC B7 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-biotin
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryCaffeine
Parent: GroveMobileObservation
Id: grove-mobile-dietary-caffeine
Title: "Grove Mobile Dietary Caffeine"
Description: "Caffeine consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC caffeine-intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-caffeine
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryCalcium
Parent: GroveMobileObservation
Id: grove-mobile-dietary-calcium
Title: "Grove Mobile Dietary Calcium"
Description: "Calcium consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the Pt-timed LOINC calcium intake concepts are substance-amount and the mass concepts are 24-hour rates."
* code = GroveMobileMeasurementCS#dietary-calcium
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryCarbohydrates
Parent: GroveMobileObservation
Id: grove-mobile-dietary-carbohydrates
Title: "Grove Mobile Dietary Carbohydrates"
Description: "Total carbohydrate consumed during an exact effective Period, normalized to UCUM grams."
* code = $loinc#9060-5
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryChloride
Parent: GroveMobileObservation
Id: grove-mobile-dietary-chloride
Title: "Grove Mobile Dietary Chloride"
Description: "Chloride consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC chloride intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-chloride
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryCholesterol
Parent: GroveMobileObservation
Id: grove-mobile-dietary-cholesterol
Title: "Grove Mobile Dietary Cholesterol"
Description: "Cholesterol consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC cholesterol-intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-cholesterol
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryChromium
Parent: GroveMobileObservation
Id: grove-mobile-dietary-chromium
Title: "Grove Mobile Dietary Chromium"
Description: "Chromium consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC chromium intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-chromium
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryCopper
Parent: GroveMobileObservation
Id: grove-mobile-dietary-copper
Title: "Grove Mobile Dietary Copper"
Description: "Copper consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC copper intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-copper
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryEnergy
Parent: GroveMobileObservation
Id: grove-mobile-dietary-energy
Title: "Grove Mobile Dietary Energy"
Description: "Energy consumed from food and drink during an exact effective Period, normalized to UCUM kilocalories. Distinct from the active/basal energy-expenditure family; intake and expenditure never share a code."
* code = $loinc#9052-2
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal (exactly)

Profile: GroveMobileDietaryFatMonounsaturated
Parent: GroveMobileObservation
Id: grove-mobile-dietary-fat-monounsaturated
Title: "Grove Mobile Dietary Monounsaturated Fat"
Description: "Monounsaturated fat consumed during an exact effective Period, normalized to UCUM grams. Grove-coded; only 24-hour LOINC concepts exist."
* code = GroveMobileMeasurementCS#dietary-fat-monounsaturated
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryFatPolyunsaturated
Parent: GroveMobileObservation
Id: grove-mobile-dietary-fat-polyunsaturated
Title: "Grove Mobile Dietary Polyunsaturated Fat"
Description: "Polyunsaturated fat consumed during an exact effective Period, normalized to UCUM grams. Grove-coded; only 24-hour LOINC concepts exist."
* code = GroveMobileMeasurementCS#dietary-fat-polyunsaturated
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryFatSaturated
Parent: GroveMobileObservation
Id: grove-mobile-dietary-fat-saturated
Title: "Grove Mobile Dietary Saturated Fat"
Description: "Saturated fat consumed during an exact effective Period, normalized to UCUM grams. Grove-coded; both LOINC saturated-fat intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-fat-saturated
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryFatTotal
Parent: GroveMobileObservation
Id: grove-mobile-dietary-fat-total
Title: "Grove Mobile Dietary Fat"
Description: "Total fat consumed during an exact effective Period, normalized to UCUM grams."
* code = $loinc#9067-0
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryFiber
Parent: GroveMobileObservation
Id: grove-mobile-dietary-fiber
Title: "Grove Mobile Dietary Fiber"
Description: "Dietary fiber consumed during an exact effective Period, normalized to UCUM grams. Grove-coded because the only measured LOINC fiber concept is a 24-hour mass-rate, not a per-event mass."
* code = GroveMobileMeasurementCS#dietary-fiber
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryFolate
Parent: GroveMobileObservation
Id: grove-mobile-dietary-folate
Title: "Grove Mobile Dietary Folate"
Description: "Total folate (vitamin B9) consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC B9 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-folate
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryIodine
Parent: GroveMobileObservation
Id: grove-mobile-dietary-iodine
Title: "Grove Mobile Dietary Iodine"
Description: "Iodine consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC iodine intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-iodine
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryIron
Parent: GroveMobileObservation
Id: grove-mobile-dietary-iron
Title: "Grove Mobile Dietary Iron"
Description: "Iron consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC iron intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-iron
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryMagnesium
Parent: GroveMobileObservation
Id: grove-mobile-dietary-magnesium
Title: "Grove Mobile Dietary Magnesium"
Description: "Magnesium consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC magnesium intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-magnesium
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryManganese
Parent: GroveMobileObservation
Id: grove-mobile-dietary-manganese
Title: "Grove Mobile Dietary Manganese"
Description: "Manganese consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC manganese intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-manganese
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryMolybdenum
Parent: GroveMobileObservation
Id: grove-mobile-dietary-molybdenum
Title: "Grove Mobile Dietary Molybdenum"
Description: "Molybdenum consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC molybdenum intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-molybdenum
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryNiacin
Parent: GroveMobileObservation
Id: grove-mobile-dietary-niacin
Title: "Grove Mobile Dietary Niacin"
Description: "Niacin (vitamin B3) consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC B3 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-niacin
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryPantothenicAcid
Parent: GroveMobileObservation
Id: grove-mobile-dietary-pantothenic-acid
Title: "Grove Mobile Dietary Pantothenic Acid"
Description: "Pantothenic acid (vitamin B5) consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC B5 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-pantothenic-acid
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryPhosphorus
Parent: GroveMobileObservation
Id: grove-mobile-dietary-phosphorus
Title: "Grove Mobile Dietary Phosphorus"
Description: "Phosphorus consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC phosphorus intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-phosphorus
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryPotassium
Parent: GroveMobileObservation
Id: grove-mobile-dietary-potassium
Title: "Grove Mobile Dietary Potassium"
Description: "Potassium consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded for the same substance-versus-mass property mismatch as sodium."
* code = GroveMobileMeasurementCS#dietary-potassium
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryProtein
Parent: GroveMobileObservation
Id: grove-mobile-dietary-protein
Title: "Grove Mobile Dietary Protein"
Description: "Protein consumed during an exact effective Period, normalized to UCUM grams."
* code = $loinc#9080-3
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryRiboflavin
Parent: GroveMobileObservation
Id: grove-mobile-dietary-riboflavin
Title: "Grove Mobile Dietary Riboflavin"
Description: "Riboflavin (vitamin B2) consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC B2 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-riboflavin
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietarySelenium
Parent: GroveMobileObservation
Id: grove-mobile-dietary-selenium
Title: "Grove Mobile Dietary Selenium"
Description: "Selenium consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC selenium intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-selenium
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietarySodium
Parent: GroveMobileObservation
Id: grove-mobile-dietary-sodium
Title: "Grove Mobile Dietary Sodium"
Description: "Sodium consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded because the point-timed LOINC sodium-intake concept is substance-amount, not mass."
* code = GroveMobileMeasurementCS#dietary-sodium
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietarySugar
Parent: GroveMobileObservation
Id: grove-mobile-dietary-sugar
Title: "Grove Mobile Dietary Sugar"
Description: "Total sugars consumed during an exact effective Period, normalized to UCUM grams. Grove-coded because LOINC has no active point-timed sugar-intake mass concept."
* code = GroveMobileMeasurementCS#dietary-sugar
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: GroveMobileDietaryThiamin
Parent: GroveMobileObservation
Id: grove-mobile-dietary-thiamin
Title: "Grove Mobile Dietary Thiamin"
Description: "Thiamin (vitamin B1) consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC B1 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-thiamin
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryVitaminA
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-a
Title: "Grove Mobile Dietary Vitamin A"
Description: "Vitamin A consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the only LOINC vitamin A intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-a
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryVitaminB12
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-b12
Title: "Grove Mobile Dietary Vitamin B12"
Description: "Vitamin B12 consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC B12 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-b12
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryVitaminB6
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-b6
Title: "Grove Mobile Dietary Vitamin B6"
Description: "Vitamin B6 consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC B6 intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-b6
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryVitaminC
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-c
Title: "Grove Mobile Dietary Vitamin C"
Description: "Vitamin C consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC vitamin C intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-c
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryVitaminD
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-d
Title: "Grove Mobile Dietary Vitamin D"
Description: "Vitamin D consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC vitamin D intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-d
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryVitaminE
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-e
Title: "Grove Mobile Dietary Vitamin E"
Description: "Vitamin E consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC vitamin E intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-e
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

Profile: GroveMobileDietaryVitaminK
Parent: GroveMobileObservation
Id: grove-mobile-dietary-vitamin-k
Title: "Grove Mobile Dietary Vitamin K"
Description: "Vitamin K consumed during an exact effective Period, normalized to UCUM micrograms. Grove-coded; the LOINC vitamin K intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-vitamin-k
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: GroveMobileDietaryZinc
Parent: GroveMobileObservation
Id: grove-mobile-dietary-zinc
Title: "Grove Mobile Dietary Zinc"
Description: "Zinc consumed during an exact effective Period, normalized to UCUM milligrams. Grove-coded; the LOINC zinc intake concepts are 24-hour mass-rates."
* code = GroveMobileMeasurementCS#dietary-zinc
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg (exactly)

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

Profile: GroveMobileElectrodermalActivity
Parent: GroveMobileObservation
Id: grove-mobile-electrodermal-activity
Title: "Electrodermal Activity"
Description: "Skin electrical conductance normalized to UCUM microsiemens. Two sources evidence the raw scalar — HealthKit's electrodermal activity samples and the Withings Body Scan feet measurement (meastype 196) — and the sensor body site is preserved as a body-site coding rather than collapsed."
* code = GroveMobileMeasurementCS#electrodermal-activity
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #uS (exactly)

Invariant: grove-mobile-flights-climbed-value-domain-1
Description: "A populated Flights Climbed value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: GroveMobileFlightsClimbed
Parent: GroveMobileObservation
Id: grove-mobile-flights-climbed
Title: "Flights Climbed"
Description: "The number of flights of stairs (floors) ascended during an exact effective Period. Health Connect's fractional floors are preserved as a decimal count of the same measurand."
* obeys grove-mobile-flights-climbed-value-domain-1
* code = $loinc#100304-5
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{flights} (exactly)
* valueQuantity.value ^minValueDecimal = 0

Profile: GroveMobileFluidIntake
Parent: GroveMobileObservation
Id: grove-mobile-fluid-intake
Title: "Grove Mobile Fluid Intake"
Description: "Water or fluid consumed during an exact effective Period, normalized to UCUM millilitres. Carries HealthKit dietary water and Health Connect hydration under one shared concept; it belongs to the hydration family, not the dietary-nutrient family, hence the id outside the dietary- prefix."
* code = $loinc#8985-4
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mL (exactly)

Profile: GroveMobileHeartRate
Parent: GroveMobileObservation
Id: grove-mobile-heart-rate
Title: "Grove Mobile Heart Rate"
Description: "A source-neutral mobile heart rate that is required to conform to the authoritative FHIR R4 Heart Rate profile and adds Grove exchange identity and provenance context. Values are normalized to UCUM beats per minute."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $heartRate
* code = $loinc#8867-4
* category = $observationCategory#vital-signs
* effective[x] only dateTime or Period
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileHeartRateVariabilityRmssd
Parent: GroveMobileObservation
Id: grove-mobile-heart-rate-variability-rmssd
Title: "Heart Rate Variability RMSSD"
Description: "The root mean square of successive differences between NN (R-R) intervals, normalized to UCUM milliseconds. RMSSD is never relabeled as SDNN; the two HRV statistics remain separate measurements."
* code = GroveMobileMeasurementCS#heart-rate-variability-rmssd
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: GroveMobileHeartRateVariabilitySdnn
Parent: GroveMobileObservation
Id: grove-mobile-heart-rate-variability-sdnn
Title: "Heart Rate Variability SDNN"
Description: "Standard deviation of NN (normal-to-normal R-R) intervals over the source measurement window, normalized to UCUM milliseconds. SDNN is not interchangeable with RMSSD; the two statistics are distinct measurements and never merge."
* code = $loinc#112429-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: GroveMobileIntermenstrualBleeding
Parent: GroveMobileObservation
Id: grove-mobile-intermenstrual-bleeding
Title: "Intermenstrual Bleeding"
Description: "A logged intermenstrual (spotting) bleeding event; the fixed result states presence."
* code = GroveMobileMeasurementCS#intermenstrual-bleeding
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveIntermenstrualBleedingVS (required)

Profile: GroveMobileLeanBodyMass
Parent: GroveMobileObservation
Id: grove-mobile-lean-body-mass
Title: "Lean Body Mass"
Description: "A source-neutral lean body mass normalized to UCUM kilograms. Consumer bioimpedance sources report fat-free mass under this label; the lean-body-mass versus fat-free-mass distinction (essential fat) is not recoverable from any source, so Withings fat-free mass joins this measurement with that caveat rather than forming a separate concept."
* code = $loinc#91557-9
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kg (exactly)

Profile: GroveMobileLightSleepDuration
Parent: GroveMobileObservation
Id: grove-mobile-light-sleep-duration
Title: "Light Sleep Duration"
Description: "Total time classified as light sleep within one sleep session or civil-day summary, normalized to UCUM minutes over the exact session Period. It is a stage-total aggregate without per-stage intervals and is implemented by the phase-2 aggregate design."
* code = $loinc#93830-8
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = GroveAggregationMethodCS#session-total
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: GroveMobileMenstruationFlow
Parent: GroveMobileObservation
Id: grove-mobile-menstruation-flow
Title: "Menstruation Flow"
Description: "The observed menstrual flow classification, with the exact platform value retained as a secondary coding. The HealthKit iOS 18 vaginal-bleeding replacement uses the identical case set. HealthKit's mandatory cycle-start metadata is carried as an optional coded component so no source information is dropped."
* code = GroveMobileMeasurementCS#menstruation-flow
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveMenstruationFlowVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains cycleStart 0..1 MS
* component[cycleStart].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement#menstrual-cycle-start
* component[cycleStart].value[x] only CodeableConcept
* component[cycleStart].valueCodeableConcept MS
* component[cycleStart].valueCodeableConcept from GroveMenstrualCycleStartVS (required)

Profile: GroveMobileMindfulnessSession
Parent: GroveMobileObservation
Id: grove-mobile-mindfulness-session
Title: "Mindfulness Session"
Description: "The duration of one mindfulness session over its exact effective Period, normalized to UCUM minutes. Source session subtype (meditation, breathing, etc.) is adapter context and does not alter the normalized duration."
* code = GroveMobileMeasurementCS#mindfulness-session-duration
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: GroveMobileOvulationTestResult
Parent: GroveMobileObservation
Id: grove-mobile-ovulation-test-result
Title: "Ovulation Test Result"
Description: "The result of a home ovulation test, with the exact platform value retained as a secondary coding. HealthKit's estrogen-surge case widens to high-fertility with the source coding preserving the distinction."
* code = GroveMobileMeasurementCS#ovulation-test-result
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveOvulationTestResultVS (required)

Invariant: grove-mobile-oxygen-saturation-value-domain-1
Description: "A populated Grove Mobile Oxygen Saturation value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: GroveMobileOxygenSaturation
Parent: GroveMobileObservation
Id: grove-mobile-oxygen-saturation
Title: "Grove Mobile Oxygen Saturation"
Description: "A source-neutral mobile oxygen saturation that is required to conform to the authoritative FHIR R4 Oxygen Saturation profile. Values are normalized to UCUM percent."
* obeys grove-mobile-oxygen-saturation-value-domain-1
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $oxygenSaturation
* code = $loinc#2708-6
* category = $observationCategory#vital-signs
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)
* valueQuantity.value ^minValueDecimal = 0
* valueQuantity.value ^maxValueDecimal = 100

Invariant: grove-mobile-oxygen-saturation-daily-average-value-domain-1
Description: "A populated Oxygen Saturation Daily Average value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: GroveMobileOxygenSaturationDailyAverage
Parent: GroveMobileObservation
Id: grove-mobile-oxygen-saturation-daily-average
Title: "Oxygen Saturation Daily Average"
Description: "The mean oxygen saturation over a civil-date effective Period, normalized to UCUM percent. It is distinct from the point-in-time shared oxygen-saturation measurement and is implemented by the phase-2 aggregate design."
* obeys grove-mobile-oxygen-saturation-daily-average-value-domain-1
* code = $loinc#103209-3
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = GroveAggregationMethodCS#daily-mean
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)
* valueQuantity.value ^minValueDecimal = 0
* valueQuantity.value ^maxValueDecimal = 100

Profile: GroveMobilePower
Parent: GroveMobileObservation
Id: grove-mobile-power
Title: "Power"
Description: "A source-neutral instantaneous mechanical power output sample recorded during activity, normalized to UCUM watts. The activity binding (running, cycling) is carried by source context and workout session linkage, not by the code. It is distinct from the cycling functional threshold power estimate, which is a derived capacity value rather than an instantaneous sample."
* code = GroveMobileMeasurementCS#power
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #W (exactly)

Profile: GroveMobileRemSleepDuration
Parent: GroveMobileObservation
Id: grove-mobile-rem-sleep-duration
Title: "REM Sleep Duration"
Description: "Total time classified as REM sleep within one sleep session or civil-day summary, normalized to UCUM minutes over the exact session Period. It is a stage-total aggregate without per-stage intervals and is implemented by the phase-2 aggregate design."
* code = $loinc#93829-0
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = GroveAggregationMethodCS#session-total
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: GroveMobileRespiratoryRate
Parent: GroveMobileObservation
Id: grove-mobile-respiratory-rate
Title: "Grove Mobile Respiratory Rate"
Description: "A source-neutral mobile respiratory rate that is required to conform to the authoritative FHIR R4 Respiratory Rate profile. Values are normalized to breaths per minute."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $respiratoryRate
* code = $loinc#9279-1
* category = $observationCategory#vital-signs
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileRespiratoryRateAverage
Parent: GroveMobileObservation
Id: grove-mobile-respiratory-rate-average
Title: "Respiratory Rate Average"
Description: "The mean respiratory rate over a windowed effective Period, normalized to UCUM breaths per minute; current source windows are a civil date (Google) and a sleep session (Oura, Withings), and the window is carried entirely by the effectivePeriod. It is distinct from the point-in-time shared respiratory-rate measurement and is implemented by the phase-2 aggregate design."
* code = $loinc#103217-6
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method from GroveAggregationMethodVS (required)
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileRestingHeartRate
Parent: GroveMobileObservation
Id: grove-mobile-resting-heart-rate
Title: "Resting Heart Rate"
Description: "One instantaneous heart-rate measurement explicitly classified by its source as taken at rest, normalized to UCUM beats per minute. This is not an aggregate result: any daily or windowed estimate uses the separate resting-heart-rate-daily-average profile."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $heartRate
* code = $loinc#40443-4
* code.coding ^slicing.discriminator.type = #pattern
* code.coding ^slicing.discriminator.path = "$this"
* code.coding ^slicing.rules = #open
* code.coding contains heartRate 1..1 MS
* code.coding[heartRate] = $loinc#8867-4
* category = $observationCategory#vital-signs
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileSexualActivity
Parent: GroveMobileObservation
Id: grove-mobile-sexual-activity
Title: "Sexual Activity"
Description: "A logged sexual-activity event whose result states whether protection was used, with the exact platform value retained where a platform enum exists."
* code = GroveMobileMeasurementCS#sexual-activity
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSexualActivityVS (required)

Profile: GroveMobileSkinTemperature
Parent: GroveMobileObservation
Id: grove-mobile-skin-temperature
Title: "Skin Temperature"
Description: "A source-neutral skin (body surface) temperature normalized to UCUM degrees Celsius and carrying a body-site coding (wrist for Apple sleeping wrist temperature; the Health Connect measurement location when present). It is deliberately distinct from the core body-temperature vital sign and is never relabeled as it."
* code = $loinc#61008-9
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #Cel (exactly)

Profile: GroveMobileSleepAwakeDuration
Parent: GroveMobileObservation
Id: grove-mobile-sleep-awake-duration
Title: "Awake Duration During Sleep"
Description: "Total time awake within one sleep session or civil-day sleep summary, normalized to UCUM minutes over the exact session Period. It is a stage-total aggregate without per-stage intervals and is implemented by the phase-2 aggregate design."
* code = $loinc#93828-2
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = GroveAggregationMethodCS#session-total
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

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

Profile: GroveMobileSleepHeartRate
Parent: GroveMobileObservation
Id: grove-mobile-sleep-heart-rate
Title: "Sleep Heart Rate"
Description: "A heart-rate statistic computed over one sleep session (Oura reports the session minimum, Withings the session mean), normalized to UCUM beats per minute over the exact session Period. The statistic is carried by the aggregate design's fixed method coding, never collapsed into the shared point heart-rate measurement."
* code = GroveMobileMeasurementCS#sleep-heart-rate
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method from GroveAggregationMethodVS (required)
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

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

Profile: GroveMobileSpeed
Parent: GroveMobileObservation
Id: grove-mobile-speed
Title: "Speed"
Description: "A source-neutral instantaneous speed sample recorded during activity, normalized to UCUM metres per second. The activity binding (running, cycling, skiing, paddling, rowing) is carried by source context and workout session linkage, not by the code, mirroring the shipped generic distance measurement. It is distinct from walking speed and the stair speeds, whose gait-health bindings are part of those concepts."
* code = GroveMobileMeasurementCS#speed
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m/s (exactly)

Invariant: grove-mobile-step-count-value-domain-1
Description: "A populated Grove Mobile Step Count value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: GroveMobileStepCount
Parent: GroveMobileObservation
Id: grove-mobile-step-count
Title: "Grove Mobile Step Count"
Description: "The number of steps recorded during an exact effective Period."
* obeys grove-step-count-result-1 and grove-step-count-period-1 and grove-mobile-step-count-value-domain-1
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
* valueQuantity.value ^minValueDecimal = 0

Profile: GroveMobileVo2Max
Parent: GroveMobileObservation
Id: grove-mobile-vo2-max
Title: "VO2 Max"
Description: "The maximal oxygen consumption per body mass, normalized to UCUM millilitres per kilogram per minute. Sources deliver estimated or test-derived maxima; the estimation method is adapter context and does not alter the normalized value."
* code = GroveMobileMeasurementCS#vo2-max
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mL/kg/min (exactly)

Invariant: grove-mobile-wheelchair-push-count-value-domain-1
Description: "A populated Wheelchair Push Count value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: GroveMobileWheelchairPushCount
Parent: GroveMobileObservation
Id: grove-mobile-wheelchair-push-count
Title: "Wheelchair Push Count"
Description: "The number of wheelchair pushes recorded during an exact effective Period, using LOINC Number of wheelchair pushes per time period and normalized to the UCUM annotation {pushes}. It is the wheelchair analogue of step-count and never substitutes for it."
* obeys grove-mobile-wheelchair-push-count-value-domain-1
* code = $loinc#96502-0
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{pushes} (exactly)
* valueQuantity.value ^minValueDecimal = 0

Profile: GroveMobileWorkout
Parent: GroveMobileObservation
Id: grove-mobile-workout
Title: "Workout"
Description: "One recorded workout session: the shared activity classification as the result, the exact session bounds as the effective Period, and optional per-session statistics as components. The exact platform activity token is retained as a secondary coding; segments and laps are linked child Observations, so no session information is dropped."
* code = GroveMobileMeasurementCS#workout
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveWorkoutActivityVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains active-duration 0..1 MS and distance-sum 0..1 MS and active-energy-sum 0..1 MS and heart-rate-avg 0..1 MS and heart-rate-max 0..1 MS and heart-rate-min 0..1 MS and step-count-sum 0..1 MS and elevation-gain 0..1 MS and flights-climbed-sum 0..1 MS and speed-avg 0..1 MS and swimming-stroke-count-sum 0..1 MS and pool-lap-count 0..1 MS
* component[active-duration].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#active-duration
* component[active-duration].value[x] only Quantity
* component[active-duration].valueQuantity.value 1..1 MS
* component[active-duration].valueQuantity.system = $ucum (exactly)
* component[active-duration].valueQuantity.code = #s (exactly)
* component[distance-sum].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#distance-sum
* component[distance-sum].value[x] only Quantity
* component[distance-sum].valueQuantity.value 1..1 MS
* component[distance-sum].valueQuantity.system = $ucum (exactly)
* component[distance-sum].valueQuantity.code = #m (exactly)
* component[active-energy-sum].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#active-energy-sum
* component[active-energy-sum].value[x] only Quantity
* component[active-energy-sum].valueQuantity.value 1..1 MS
* component[active-energy-sum].valueQuantity.system = $ucum (exactly)
* component[active-energy-sum].valueQuantity.code = #kcal (exactly)
* component[heart-rate-avg].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#heart-rate-avg
* component[heart-rate-avg].value[x] only Quantity
* component[heart-rate-avg].valueQuantity.value 1..1 MS
* component[heart-rate-avg].valueQuantity.system = $ucum (exactly)
* component[heart-rate-avg].valueQuantity.code = #/min (exactly)
* component[heart-rate-max].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#heart-rate-max
* component[heart-rate-max].value[x] only Quantity
* component[heart-rate-max].valueQuantity.value 1..1 MS
* component[heart-rate-max].valueQuantity.system = $ucum (exactly)
* component[heart-rate-max].valueQuantity.code = #/min (exactly)
* component[heart-rate-min].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#heart-rate-min
* component[heart-rate-min].value[x] only Quantity
* component[heart-rate-min].valueQuantity.value 1..1 MS
* component[heart-rate-min].valueQuantity.system = $ucum (exactly)
* component[heart-rate-min].valueQuantity.code = #/min (exactly)
* component[step-count-sum].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#step-count-sum
* component[step-count-sum].value[x] only Quantity
* component[step-count-sum].valueQuantity.value 1..1 MS
* component[step-count-sum].valueQuantity.system = $ucum (exactly)
* component[step-count-sum].valueQuantity.code = #{steps} (exactly)
* component[elevation-gain].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#elevation-gain
* component[elevation-gain].value[x] only Quantity
* component[elevation-gain].valueQuantity.value 1..1 MS
* component[elevation-gain].valueQuantity.system = $ucum (exactly)
* component[elevation-gain].valueQuantity.code = #m (exactly)
* component[flights-climbed-sum].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#flights-climbed-sum
* component[flights-climbed-sum].value[x] only Quantity
* component[flights-climbed-sum].valueQuantity.value 1..1 MS
* component[flights-climbed-sum].valueQuantity.system = $ucum (exactly)
* component[flights-climbed-sum].valueQuantity.code = #{flights} (exactly)
* component[speed-avg].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#speed-avg
* component[speed-avg].value[x] only Quantity
* component[speed-avg].valueQuantity.value 1..1 MS
* component[speed-avg].valueQuantity.system = $ucum (exactly)
* component[speed-avg].valueQuantity.code = #m/s (exactly)
* component[swimming-stroke-count-sum].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#swimming-stroke-count-sum
* component[swimming-stroke-count-sum].value[x] only Quantity
* component[swimming-stroke-count-sum].valueQuantity.value 1..1 MS
* component[swimming-stroke-count-sum].valueQuantity.system = $ucum (exactly)
* component[swimming-stroke-count-sum].valueQuantity.code = #{strokes} (exactly)
* component[pool-lap-count].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#pool-lap-count
* component[pool-lap-count].value[x] only Quantity
* component[pool-lap-count].valueQuantity.value 1..1 MS
* component[pool-lap-count].valueQuantity.system = $ucum (exactly)
* component[pool-lap-count].valueQuantity.code = #{laps} (exactly)
* hasMember only Reference(GroveMobileWorkoutSegment)

Profile: GroveMobileWorkoutSegment
Parent: GroveMobileObservation
Id: grove-mobile-workout-segment
Title: "Workout Segment"
Description: "One segment, lap, pause, marker, or event within a workout session, linked from the parent workout through hasMember. The value is the segment classification — an activity code or a structural code — with the exact platform token retained; per-segment statistics ride the open component slicing."
* code = GroveMobileMeasurementCS#workout-segment
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveWorkoutSegmentTypeVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains repetitions 0..1 MS and set-weight 0..1 MS and set-index 0..1 MS and rating-of-perceived-exertion 0..1 MS and lap-length 0..1 MS
* component[repetitions].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#repetitions
* component[repetitions].value[x] only Quantity
* component[repetitions].valueQuantity.value 1..1 MS
* component[repetitions].valueQuantity.system = $ucum (exactly)
* component[repetitions].valueQuantity.code = #{count} (exactly)
* component[set-weight].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#set-weight
* component[set-weight].value[x] only Quantity
* component[set-weight].valueQuantity.value 1..1 MS
* component[set-weight].valueQuantity.system = $ucum (exactly)
* component[set-weight].valueQuantity.code = #kg (exactly)
* component[set-index].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#set-index
* component[set-index].value[x] only Quantity
* component[set-index].valueQuantity.value 1..1 MS
* component[set-index].valueQuantity.system = $ucum (exactly)
* component[set-index].valueQuantity.code = #{count} (exactly)
* component[rating-of-perceived-exertion].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#rating-of-perceived-exertion
* component[rating-of-perceived-exertion].value[x] only Quantity
* component[rating-of-perceived-exertion].valueQuantity.value 1..1 MS
* component[rating-of-perceived-exertion].valueQuantity.system = $ucum (exactly)
* component[rating-of-perceived-exertion].valueQuantity.code = #{score} (exactly)
* component[lap-length].code = https://grovealliance.org/fhir/mobile/CodeSystem/grove-workout-statistic#lap-length
* component[lap-length].value[x] only Quantity
* component[lap-length].valueQuantity.value 1..1 MS
* component[lap-length].valueQuantity.system = $ucum (exactly)
* component[lap-length].valueQuantity.code = #m (exactly)

Instance: GroveMobileBasalEnergyExample
InstanceOf: GroveMobileBasalEnergy
Usage: #example
Title: "Basal Energy Burned Example"
Description: "A conformant Basal Energy Burned instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:b0h-Tv159OxMNwMqEYAAgMW42STfSndEoD6m_2u2tf8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:xtvK4rJpnbSWJhddddLqT8BbX5TLDMosEdKl6K_VwzA"
* status = #final
* code = GroveMobileMeasurementCS#basal-energy-burned
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1580 'kcal'

Instance: GroveMobileBloodGlucoseUnspecifiedSpecimenExample
InstanceOf: GroveMobileBloodGlucoseUnspecifiedSpecimen
Usage: #example
Title: "Blood Glucose (Unspecified Specimen) Example"
Description: "A conformant Blood Glucose (Unspecified Specimen) instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:L1XBuBTK3gXIJKQUAkrCSiyaWe-ziGY9BTf7vMO-kcs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Zrbw41y8yt3t-yKCIvt5Wqz8MRkl1-OpPqoHr0PLOlI"
* status = #final
* code = $loinc#2339-0 "Glucose [Mass/volume] in Blood"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 95 'mg/dL'

Instance: GroveMobileBodyFatPercentageExample
InstanceOf: GroveMobileBodyFatPercentage
Usage: #example
Title: "Body Fat Percentage Example"
Description: "A conformant Body Fat Percentage instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:J6eqTG1RKl_vcw8AK9HDqTygo1sJeqRydgE_KLemgz4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:mNgI2tiikqfqjEAi0ZncfjtzJyM-O2uw4G4ZdAeJH1Y"
* status = #final
* code = $loinc#41982-0 "Percentage of body fat Measured"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 22 '%'

Instance: GroveMobileBodyWaterMassExample
InstanceOf: GroveMobileBodyWaterMass
Usage: #example
Title: "Body Water Mass Example"
Description: "A conformant Body Water Mass instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:PZdqjQCkfQrrDuYxbZtD6Io4d5xde9CpxX9y-4bveGw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:67s11hpaGPdtYQAq9bUrRLMmmBolYbXOETzkz9dqMLM"
* status = #final
* code = $loinc#101683-1 "Body water mass"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 42 'kg'

Instance: GroveMobileBoneMassExample
InstanceOf: GroveMobileBoneMass
Usage: #example
Title: "Bone Mass Example"
Description: "A conformant Bone Mass instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:bDm9l2Xv02AgAJAlP3M0y2_mdNCmHN5QmltsO2KUS70"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Bq8j9DQKnL8sWvvpNcPZki88krCMXK03BX1Wcj5R5k4"
* status = #final
* code = $loinc#101685-6 "Body bone mass"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 3.1 'kg'

Instance: GroveMobileCervicalMucusQualityExample
InstanceOf: GroveMobileCervicalMucusQuality
Usage: #example
Title: "Cervical Mucus Quality Example"
Description: "A conformant Cervical Mucus Quality instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:VGMM94JzSK-xO-g-HRr8clV-RILwY4WYhqGIBOcgE08"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:TiKE6NDj3n8QoOBFkFTYv1HkcBn75GvSo67wYu-xdh8"
* status = #final
* code = GroveMobileMeasurementCS#cervical-mucus-quality
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveCervicalMucusQualityCS#dry "Dry"

Instance: GroveMobileCyclingCadenceExample
InstanceOf: GroveMobileCyclingCadence
Usage: #example
Title: "Cycling Cadence Example"
Description: "A conformant Cycling Cadence instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:5ZQh_hjggElq4WxYxeraFLavHZvPf6_b6qsMSZjkUJA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:xW-o8zgTF_Oa1Ligj9vTXPq04jzrO3iytdq9GXTudqo"
* status = #final
* code = GroveMobileMeasurementCS#cycling-cadence
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 85 '/min' "revolutions/minute"

Instance: GroveMobileDeepSleepDurationExample
InstanceOf: GroveMobileDeepSleepDuration
Usage: #example
Title: "Deep Sleep Duration Example"
Description: "A conformant Deep Sleep Duration instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:srb7Ja2wDKEr3iwJUrvV4ZhpDEyZ2N8Y_3TQiWakXVI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:iP79PHlckpYBBUM3A2jjjbQQVcHOvr3YzjYlzvjghAY"
* status = #final
* code = $loinc#93831-6 "Deep sleep duration"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 78 'min'

Instance: GroveMobileDietaryBiotinExample
InstanceOf: GroveMobileDietaryBiotin
Usage: #example
Title: "Grove Mobile Dietary Biotin Example"
Description: "A conformant Grove Mobile Dietary Biotin instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:X9twDnAAql7qNNf6GXV4WZilYoyaqI_hsrT_WMcpDAE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:a6WbjuY2HjndVi4nyLjjNfXKdS13UGmMFDoaj0QsEQY"
* status = #final
* code = GroveMobileMeasurementCS#dietary-biotin
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 30 'ug'

Instance: GroveMobileDietaryCaffeineExample
InstanceOf: GroveMobileDietaryCaffeine
Usage: #example
Title: "Grove Mobile Dietary Caffeine Example"
Description: "A conformant Grove Mobile Dietary Caffeine instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:sNBQ8bfxLu3NQxRdyCJyfcmK1f4HHL55G5aeCXyuFjM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:hNhLwKu7lxoBZCsBGH1gZi8jWJGXuA4YfOL2DfqHJpk"
* status = #final
* code = GroveMobileMeasurementCS#dietary-caffeine
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 95 'mg'

Instance: GroveMobileDietaryCalciumExample
InstanceOf: GroveMobileDietaryCalcium
Usage: #example
Title: "Grove Mobile Dietary Calcium Example"
Description: "A conformant Grove Mobile Dietary Calcium instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:NByNNOekeXsWNpCmjiuaU6xiWOpP2VGmpTgXg3fYTFY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:waSpA_mKHWIlo41wzbIavH9dPBdWEPIOzOdan1ceZsY"
* status = #final
* code = GroveMobileMeasurementCS#dietary-calcium
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1000 'mg'

Instance: GroveMobileDietaryCarbohydratesExample
InstanceOf: GroveMobileDietaryCarbohydrates
Usage: #example
Title: "Grove Mobile Dietary Carbohydrates Example"
Description: "A conformant Grove Mobile Dietary Carbohydrates instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:k6W8iGPQStIW9xcM_NcT_Gt980Rf0jqsADkHn7ENUb8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:-jaXUNj3FNmmpoIPsdQnqn_7RZOIcFLCpK2fAYdPY_Q"
* status = #final
* code = $loinc#9060-5 "Carbohydrate intake Measured"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 275 'g'

Instance: GroveMobileDietaryChlorideExample
InstanceOf: GroveMobileDietaryChloride
Usage: #example
Title: "Grove Mobile Dietary Chloride Example"
Description: "A conformant Grove Mobile Dietary Chloride instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:n2W4-F_Hpu4DvVC4jryXQrmIk9Tt8j4RKk8WvGEptas"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:PlYil3uOM6M361ZNnSuTifUduGMmMAHw4LElEflTT-c"
* status = #final
* code = GroveMobileMeasurementCS#dietary-chloride
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2300 'mg'

Instance: GroveMobileDietaryCholesterolExample
InstanceOf: GroveMobileDietaryCholesterol
Usage: #example
Title: "Grove Mobile Dietary Cholesterol Example"
Description: "A conformant Grove Mobile Dietary Cholesterol instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:-lj2FC_x2-ws9Sq3204jXMg9RkCdr5MxPnXtD54Xhlo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:VgE_1OGAeaRJljgxLrWatSR7MotVQ-IA2JA0KrIzUG4"
* status = #final
* code = GroveMobileMeasurementCS#dietary-cholesterol
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 250 'mg'

Instance: GroveMobileDietaryChromiumExample
InstanceOf: GroveMobileDietaryChromium
Usage: #example
Title: "Grove Mobile Dietary Chromium Example"
Description: "A conformant Grove Mobile Dietary Chromium instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:NaWeVvG-3H08hBs2FaUy7a4Z8QINpHvcPhyCpGS53jI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:HGVKG6WXz-vgOyCxsL7SIwQHiqdI8T3C7555QHltmAI"
* status = #final
* code = GroveMobileMeasurementCS#dietary-chromium
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 35 'ug'

Instance: GroveMobileDietaryCopperExample
InstanceOf: GroveMobileDietaryCopper
Usage: #example
Title: "Grove Mobile Dietary Copper Example"
Description: "A conformant Grove Mobile Dietary Copper instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:n8jszaQfy1EPvyCml6bjy1-hfAKoxaKd13-xkrgsC9k"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ZXSOhQdu-9amgsmkW5PJW5KLAgwtS87LPHe38AY-0vs"
* status = #final
* code = GroveMobileMeasurementCS#dietary-copper
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 900 'ug'

Instance: GroveMobileDietaryEnergyExample
InstanceOf: GroveMobileDietaryEnergy
Usage: #example
Title: "Grove Mobile Dietary Energy Example"
Description: "A conformant Grove Mobile Dietary Energy instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:fAMrwUoCsLAM20PPNIF8vS1BJT-r75UXFpLN8n_xqfA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:U31eSnzCkQ2beH_ps4PVuGj76HERM9o4OexAHaTpO3M"
* status = #final
* code = $loinc#9052-2 "Calorie intake total"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2100 'kcal'

Instance: GroveMobileDietaryFatMonounsaturatedExample
InstanceOf: GroveMobileDietaryFatMonounsaturated
Usage: #example
Title: "Grove Mobile Dietary Monounsaturated Fat Example"
Description: "A conformant Grove Mobile Dietary Monounsaturated Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:w_rMNASnogtx9-Rf1rXWnmWA1ev7CbMquLmHK6nuMI4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:RighmIFWO_fT6mBPOHY7sJofuZnXz754esKVvoJq6vc"
* status = #final
* code = GroveMobileMeasurementCS#dietary-fat-monounsaturated
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 35 'g'

Instance: GroveMobileDietaryFatPolyunsaturatedExample
InstanceOf: GroveMobileDietaryFatPolyunsaturated
Usage: #example
Title: "Grove Mobile Dietary Polyunsaturated Fat Example"
Description: "A conformant Grove Mobile Dietary Polyunsaturated Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:DlqmhPeED1cfGGJl9K0C4-MPiUjInZ4Mrne530TwHvg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Z_vxOBhn3ySSOfUukZKpzTyLaM_TfdhQHGMw_FOc7pc"
* status = #final
* code = GroveMobileMeasurementCS#dietary-fat-polyunsaturated
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 22 'g'

Instance: GroveMobileDietaryFatSaturatedExample
InstanceOf: GroveMobileDietaryFatSaturated
Usage: #example
Title: "Grove Mobile Dietary Saturated Fat Example"
Description: "A conformant Grove Mobile Dietary Saturated Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:kxx60GVz_qTVXW-MI0D4sz6n1X7tfz4f5oiLzGlF-ec"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:JMbjr6WG7Gnmq_SqR69VgSAa7CPrN3wsQPBtzbMyP7E"
* status = #final
* code = GroveMobileMeasurementCS#dietary-fat-saturated
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 20 'g'

Instance: GroveMobileDietaryFatTotalExample
InstanceOf: GroveMobileDietaryFatTotal
Usage: #example
Title: "Grove Mobile Dietary Fat Example"
Description: "A conformant Grove Mobile Dietary Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:y-Z5c1oRB5x3VnBMENLdzdXaY890N0MBtD8nOWQdwts"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:O3lATbEFT2kDl04tB94Mnn7Szigx1f2RY2zpRo1tH3Y"
* status = #final
* code = $loinc#9067-0 "Fat intake Measured"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 78 'g'

Instance: GroveMobileDietaryFiberExample
InstanceOf: GroveMobileDietaryFiber
Usage: #example
Title: "Grove Mobile Dietary Fiber Example"
Description: "A conformant Grove Mobile Dietary Fiber instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:8S7TuqwKgE2ClEjZrBH7c07pVcATVgz_-Hzxaa84BIY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:6C5xZ3LcNTa7oV_sNVhPokhWkSPzPhJmOZygk6XIJfg"
* status = #final
* code = GroveMobileMeasurementCS#dietary-fiber
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 28 'g'

Instance: GroveMobileDietaryFolateExample
InstanceOf: GroveMobileDietaryFolate
Usage: #example
Title: "Grove Mobile Dietary Folate Example"
Description: "A conformant Grove Mobile Dietary Folate instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:PcX3mh9niQwtpPx9jy98EI4ihy_8a_1JK_8qnXtksxA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:1DYELStGJEFRDBBUHkNStJoFdYsajUgWQCT4qsM3oY0"
* status = #final
* code = GroveMobileMeasurementCS#dietary-folate
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 400 'ug'

Instance: GroveMobileDietaryIodineExample
InstanceOf: GroveMobileDietaryIodine
Usage: #example
Title: "Grove Mobile Dietary Iodine Example"
Description: "A conformant Grove Mobile Dietary Iodine instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:KDiEwmKaaseLsoNdG07w4rcwC79pKDV7blcO_0TZywg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:L28t5l9VkxAvpA1qKnH3F6xGwVlLhV4o9jPFwASBKik"
* status = #final
* code = GroveMobileMeasurementCS#dietary-iodine
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 150 'ug'

Instance: GroveMobileDietaryIronExample
InstanceOf: GroveMobileDietaryIron
Usage: #example
Title: "Grove Mobile Dietary Iron Example"
Description: "A conformant Grove Mobile Dietary Iron instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:mYXREMZ7uBhoegb_Szzth6AsEWKdMoaiwNiH9r8IRPU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:MHFgqIZuSFIUt89kuoCQpWpKAbSUw2cfqqXPrsfnorQ"
* status = #final
* code = GroveMobileMeasurementCS#dietary-iron
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 18 'mg'

Instance: GroveMobileDietaryMagnesiumExample
InstanceOf: GroveMobileDietaryMagnesium
Usage: #example
Title: "Grove Mobile Dietary Magnesium Example"
Description: "A conformant Grove Mobile Dietary Magnesium instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ekPySoOojc7c4DxBVM7fiwXTssqAJN4r5IjcruEZZ4A"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:_vdgAyBT3hhGD6qaraTQa0E5tNxtQC6j9fGauy0HALQ"
* status = #final
* code = GroveMobileMeasurementCS#dietary-magnesium
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 400 'mg'

Instance: GroveMobileDietaryManganeseExample
InstanceOf: GroveMobileDietaryManganese
Usage: #example
Title: "Grove Mobile Dietary Manganese Example"
Description: "A conformant Grove Mobile Dietary Manganese instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:H864g9AtvusNDo4vOITBIOczPeaCW1N6v8jC3v6zpls"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:YJyXU9_p_8l-AKJKuPBOo1esAmWSVaFpRu96smfm4kY"
* status = #final
* code = GroveMobileMeasurementCS#dietary-manganese
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2.3 'mg'

Instance: GroveMobileDietaryMolybdenumExample
InstanceOf: GroveMobileDietaryMolybdenum
Usage: #example
Title: "Grove Mobile Dietary Molybdenum Example"
Description: "A conformant Grove Mobile Dietary Molybdenum instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:cqKk1hg3NfSGXwrJynmDeQqsR9RB0J1BaXTcfxnC0ok"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:V_UD6xeHU1VCoZYq5Uv5H7cIidbLKsB9qrneOrNvgvE"
* status = #final
* code = GroveMobileMeasurementCS#dietary-molybdenum
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 45 'ug'

Instance: GroveMobileDietaryNiacinExample
InstanceOf: GroveMobileDietaryNiacin
Usage: #example
Title: "Grove Mobile Dietary Niacin Example"
Description: "A conformant Grove Mobile Dietary Niacin instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:RAQCt3XU5OoslAOWFiooYmbPWCgw83c456Xi7f8mZFY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:hLJqksJH8hoLKSr2ep4pxHpZBIE6c5_5ycdTWVA84Zg"
* status = #final
* code = GroveMobileMeasurementCS#dietary-niacin
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 16 'mg'

Instance: GroveMobileDietaryPantothenicAcidExample
InstanceOf: GroveMobileDietaryPantothenicAcid
Usage: #example
Title: "Grove Mobile Dietary Pantothenic Acid Example"
Description: "A conformant Grove Mobile Dietary Pantothenic Acid instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:y8hu9ppyRpKuMAQZHrjH83Ss5v42jTT_rmJDmgbA0LI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:_QpmlrjqWiWUeLSxft_yyNtf3UNEkOHpJdtDjCP6IeQ"
* status = #final
* code = GroveMobileMeasurementCS#dietary-pantothenic-acid
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 5 'mg'

Instance: GroveMobileDietaryPhosphorusExample
InstanceOf: GroveMobileDietaryPhosphorus
Usage: #example
Title: "Grove Mobile Dietary Phosphorus Example"
Description: "A conformant Grove Mobile Dietary Phosphorus instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:-5XMU46YCaabTejCotEMCFXWuC8OVeCW3q7TdkMVzvA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Sgvuqch4UGRW8OvTFJCDN2bBr5oPYGWecvY3UR-cyvY"
* status = #final
* code = GroveMobileMeasurementCS#dietary-phosphorus
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 700 'mg'

Instance: GroveMobileDietaryPotassiumExample
InstanceOf: GroveMobileDietaryPotassium
Usage: #example
Title: "Grove Mobile Dietary Potassium Example"
Description: "A conformant Grove Mobile Dietary Potassium instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Y-TmkzHPuIUv0Puk-4wohSUEkW4jkp33w53zo-FIEOk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:X5vGe6cHdSMvktuoFO8gyN80Sf395AL0E4xeRnSsPLU"
* status = #final
* code = GroveMobileMeasurementCS#dietary-potassium
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 3400 'mg'

Instance: GroveMobileDietaryProteinExample
InstanceOf: GroveMobileDietaryProtein
Usage: #example
Title: "Grove Mobile Dietary Protein Example"
Description: "A conformant Grove Mobile Dietary Protein instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:1C-bRPIJa3IOM8mOTAyJyAijSrnXnO_Kl0UXjocJe9E"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:TiZbrUuzLA2eGq5Nz5sN5eFgmbSzDChGKx3QHyoQYoY"
* status = #final
* code = $loinc#9080-3 "Protein intake Measured"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 50 'g'

Instance: GroveMobileDietaryRiboflavinExample
InstanceOf: GroveMobileDietaryRiboflavin
Usage: #example
Title: "Grove Mobile Dietary Riboflavin Example"
Description: "A conformant Grove Mobile Dietary Riboflavin instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:xkQ5FVUWzRZ1lzJN6iuS0ItzKLZ8DLOvpAtC8JJ1azo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:FtmvTfm--Q5I8vydMeKSvw5kRV8sz4Uyr-xbXRH9Gto"
* status = #final
* code = GroveMobileMeasurementCS#dietary-riboflavin
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1.3 'mg'

Instance: GroveMobileDietarySeleniumExample
InstanceOf: GroveMobileDietarySelenium
Usage: #example
Title: "Grove Mobile Dietary Selenium Example"
Description: "A conformant Grove Mobile Dietary Selenium instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:b8Hweo1ibHXxjV6hcTFNd8YCYBsS6WblYPb0obIqHzY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:_zuu54ZNhIGgXyBHqyU_fO9Di65TMfUtXPv09UQHn5s"
* status = #final
* code = GroveMobileMeasurementCS#dietary-selenium
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 55 'ug'

Instance: GroveMobileDietarySodiumExample
InstanceOf: GroveMobileDietarySodium
Usage: #example
Title: "Grove Mobile Dietary Sodium Example"
Description: "A conformant Grove Mobile Dietary Sodium instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:1_7z5xKT3MOKzuJgduBDZCGaIZeKQNxOl8oCbm1ox5I"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:mMN9kY3psQr8_dp7bduOruykW30KpoTkelNHMhLyNHc"
* status = #final
* code = GroveMobileMeasurementCS#dietary-sodium
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2300 'mg'

Instance: GroveMobileDietarySugarExample
InstanceOf: GroveMobileDietarySugar
Usage: #example
Title: "Grove Mobile Dietary Sugar Example"
Description: "A conformant Grove Mobile Dietary Sugar instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:HM4yOKAZ20NAgRT93L1XlI0YrY5kQSOcgHCSuMek49c"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ulfpzxyBBt3-1yoU6_bD9nY3z5JKRnK7VOIWyl-ALjI"
* status = #final
* code = GroveMobileMeasurementCS#dietary-sugar
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 50 'g'

Instance: GroveMobileDietaryThiaminExample
InstanceOf: GroveMobileDietaryThiamin
Usage: #example
Title: "Grove Mobile Dietary Thiamin Example"
Description: "A conformant Grove Mobile Dietary Thiamin instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:mn8hehXlLTT4iIViCiOVn8wJjje6F4b6FVszoVGzPyE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:tvQ4VYvKPp_NS7Z-X7I9J-OEU9ECzhRcz6_n2UUpVOs"
* status = #final
* code = GroveMobileMeasurementCS#dietary-thiamin
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1.2 'mg'

Instance: GroveMobileDietaryVitaminAExample
InstanceOf: GroveMobileDietaryVitaminA
Usage: #example
Title: "Grove Mobile Dietary Vitamin A Example"
Description: "A conformant Grove Mobile Dietary Vitamin A instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:nS5QCqL8MXTd0VUQdx9cgxxC-khCc4ZvZVrqGmL35sM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ZjQB6Q2DRl2cfXhLfGvwSl6UWy8lc1tkPcNDdWEChPc"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-a
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 900 'ug'

Instance: GroveMobileDietaryVitaminB12Example
InstanceOf: GroveMobileDietaryVitaminB12
Usage: #example
Title: "Grove Mobile Dietary Vitamin B12 Example"
Description: "A conformant Grove Mobile Dietary Vitamin B12 instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:BRqKBl7gOp_0xFuvOaB2ifmoxRaQoBtxyV6LVKvPOsc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:tQ_1S4DVLKmVWKa0Jkk6TPUZjIMx8bWBb8Bk6ZB9mgM"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-b12
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2.4 'ug'

Instance: GroveMobileDietaryVitaminB6Example
InstanceOf: GroveMobileDietaryVitaminB6
Usage: #example
Title: "Grove Mobile Dietary Vitamin B6 Example"
Description: "A conformant Grove Mobile Dietary Vitamin B6 instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:VUW1UahCOdREe1lviTzp73xYbX1T9xPymuxGxvJddKA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:9CNfB75H1hpv7vKn0cx7x0sZh-jHuSLhL92ccg1rokc"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-b6
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1.7 'mg'

Instance: GroveMobileDietaryVitaminCExample
InstanceOf: GroveMobileDietaryVitaminC
Usage: #example
Title: "Grove Mobile Dietary Vitamin C Example"
Description: "A conformant Grove Mobile Dietary Vitamin C instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ceq6O2dCQ2XDztajkHbNO4dbODGYEA-NbTG0cMiFB7I"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:4fiuMmnruQRWjfCMy-tlmd3cCvaZ7tsbwEyUob39uY4"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-c
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 90 'mg'

Instance: GroveMobileDietaryVitaminDExample
InstanceOf: GroveMobileDietaryVitaminD
Usage: #example
Title: "Grove Mobile Dietary Vitamin D Example"
Description: "A conformant Grove Mobile Dietary Vitamin D instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:o9jzXdva8yvQrnPHdP4gfqLyTAoVEyXOd87OyqV4gbw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:yT8sxxanN5Qe2HUoQER2kCSwwxNVMdTijLhObJb3dNc"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-d
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 20 'ug'

Instance: GroveMobileDietaryVitaminEExample
InstanceOf: GroveMobileDietaryVitaminE
Usage: #example
Title: "Grove Mobile Dietary Vitamin E Example"
Description: "A conformant Grove Mobile Dietary Vitamin E instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:UdW11d-g6rFNaGwSyKq_lQc6b4EwjADYAM9KwbhlOAw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Iyn8l8EIg1ZC0VtIcAm9OqZ5CUmgW4FO7YIt9db4cuI"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-e
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 15 'mg'

Instance: GroveMobileDietaryVitaminKExample
InstanceOf: GroveMobileDietaryVitaminK
Usage: #example
Title: "Grove Mobile Dietary Vitamin K Example"
Description: "A conformant Grove Mobile Dietary Vitamin K instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:WoVd1WJy89mfDw4bgdE_HC7PI62q16kn3d41WHL4Row"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:9W4pjwv_s2VjJtwOlGzil3v2QkBa1IFZOyWKMtwh9KU"
* status = #final
* code = GroveMobileMeasurementCS#dietary-vitamin-k
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 120 'ug'

Instance: GroveMobileDietaryZincExample
InstanceOf: GroveMobileDietaryZinc
Usage: #example
Title: "Grove Mobile Dietary Zinc Example"
Description: "A conformant Grove Mobile Dietary Zinc instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:HqMGR5p9oQKk5auHQjU-ygEKF2GlB9mSSbDx-qmFLiE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:hZLvZ8VZcKHhaO_qPYiH1YTKVX9zhWwKC7dX3iZt9lA"
* status = #final
* code = GroveMobileMeasurementCS#dietary-zinc
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 11 'mg'

Instance: GroveMobileElectrodermalActivityExample
InstanceOf: GroveMobileElectrodermalActivity
Usage: #example
Title: "Electrodermal Activity Example"
Description: "A conformant Electrodermal Activity instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:K7i8m1h-K94_qZhvyNd1NxmeywKGCJX99utvYSua__4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:pNxvVKhdE8x5Eq09a36chMFn9kdMXjpAdtndLoOBrXE"
* status = #final
* code = GroveMobileMeasurementCS#electrodermal-activity
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 0.8 'uS'

Instance: GroveMobileFlightsClimbedExample
InstanceOf: GroveMobileFlightsClimbed
Usage: #example
Title: "Flights Climbed Example"
Description: "A conformant Flights Climbed instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:dViQny2b3xBum5JORCy1x1kWUoZ39IDGGt1Z2abVeT0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:3SMnKhWPsOp2xjaydR7L5aWGmzkiG7p8fkjXUpdr5_o"
* status = #final
* code = $loinc#100304-5 "Flights climbed [#] Reporting Period"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 12 '{flights}' "flights"

Instance: GroveMobileFluidIntakeExample
InstanceOf: GroveMobileFluidIntake
Usage: #example
Title: "Grove Mobile Fluid Intake Example"
Description: "A conformant Grove Mobile Fluid Intake instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:A1ENaiugF8jxoIbxuiw1kHief3NT0D8pt6HRHwgiqR4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:CKqalY-OzvgQJ_t8bbMPY7uIE_siHYaGNEwNm-uhoTw"
* status = #final
* code = $loinc#8985-4 "Fluid intake Measured"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 250 'mL'

Instance: GroveMobileHeartRateVariabilityRmssdExample
InstanceOf: GroveMobileHeartRateVariabilityRmssd
Usage: #example
Title: "Heart Rate Variability RMSSD Example"
Description: "A conformant Heart Rate Variability RMSSD instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:M5tezfFiBy-hxMfdua0j4VRq2jOBMTii3IB398C8zGI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:XeUKbW7pTo8Re3JT_UmGkBYDLCXbB8NcBZzq2GmVcQg"
* status = #final
* code = GroveMobileMeasurementCS#heart-rate-variability-rmssd
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 42 'ms'

Instance: GroveMobileHeartRateVariabilitySdnnExample
InstanceOf: GroveMobileHeartRateVariabilitySdnn
Usage: #example
Title: "Heart Rate Variability SDNN Example"
Description: "A conformant Heart Rate Variability SDNN instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:MGZr9sI3IR_-IZ0oBd9_rVpCFDz6uj3xWGMLkDGVmfs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:4d3Dt8L8JbbCEyX2FxHqthtJsxBttxsvp0yXjSu63WU"
* status = #final
* code = $loinc#112429-6 "Heart rate variability SDNN [Time]"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 58 'ms'

Instance: GroveMobileIntermenstrualBleedingExample
InstanceOf: GroveMobileIntermenstrualBleeding
Usage: #example
Title: "Intermenstrual Bleeding Example"
Description: "A conformant Intermenstrual Bleeding instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:c4Ub2nGjkMx4MXkE7KcBV3cIaO-EolM1tJvDwjhymfQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:V0YdlDrwO2KaHP2Wc9ueR8g1WuTadZ_mVqRG904UmmY"
* status = #final
* code = GroveMobileMeasurementCS#intermenstrual-bleeding
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveIntermenstrualBleedingCS#present "Present"

Instance: GroveMobileLeanBodyMassExample
InstanceOf: GroveMobileLeanBodyMass
Usage: #example
Title: "Lean Body Mass Example"
Description: "A conformant Lean Body Mass instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:2xU2bXM74wzwhdAdrW_Is6gD-aq_ooaBQIE0SSaBf1g"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:B6jF9DkEL22Va85R6szCy12UzsnyujSPIIKpcRqrPAQ"
* status = #final
* code = $loinc#91557-9 "Lean body weight"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 56 'kg'

Instance: GroveMobileLightSleepDurationExample
InstanceOf: GroveMobileLightSleepDuration
Usage: #example
Title: "Light Sleep Duration Example"
Description: "A conformant Light Sleep Duration instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:GBNHVKU3Lf9N_HlopzOJyXj2nqIQlUU51BUtOyNiHJ0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:GhJkieGOY_DaYGuTIeGXYZYW5LfthRtjX6OQ-BuDcD0"
* status = #final
* code = $loinc#93830-8 "Light sleep duration"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 244 'min'

Instance: GroveMobileMenstruationFlowExample
InstanceOf: GroveMobileMenstruationFlow
Usage: #example
Title: "Menstruation Flow Example"
Description: "A conformant Menstruation Flow instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:1pA76E_AAXu-LKwmbc55MlXDWNjlApEKvFFES3ScVZ4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:K2xYEIsRm9Jw6W_ZDXU1VbWGzdTcY8_5oF7tuXO5s6E"
* status = #final
* code = GroveMobileMeasurementCS#menstruation-flow
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveMenstruationFlowCS#unspecified "Unspecified"

Instance: GroveMobileMindfulnessSessionExample
InstanceOf: GroveMobileMindfulnessSession
Usage: #example
Title: "Mindfulness Session Example"
Description: "A conformant Mindfulness Session instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:AaJkyMlm-PhHkYlhfGP4qtrZvz7WJrwbDq7NwuF9Hqw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:HE4s9A7suhyBuI17QMtOT3dw3fih8CykMkvR7mBy1MQ"
* status = #final
* code = GroveMobileMeasurementCS#mindfulness-session-duration
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 10 'min'

Instance: GroveMobileOvulationTestResultExample
InstanceOf: GroveMobileOvulationTestResult
Usage: #example
Title: "Ovulation Test Result Example"
Description: "A conformant Ovulation Test Result instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:j7paCkeKFTwFnbRdD-KTgbsIL2x1awqvWn8d4yDOIK4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:75VKX6LlqsW5VUfNIrthT-ZBhQI-SF3ETKZQxfgVXsY"
* status = #final
* code = GroveMobileMeasurementCS#ovulation-test-result
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveOvulationTestResultCS#negative "Negative"

Instance: GroveMobileOxygenSaturationDailyAverageExample
InstanceOf: GroveMobileOxygenSaturationDailyAverage
Usage: #example
Title: "Oxygen Saturation Daily Average Example"
Description: "A conformant Oxygen Saturation Daily Average instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:XIBI774mmTxqXa6CaKMFaCj0BKqGNBonys5Ly51UJjo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:PeAbzLPdL1zZ5X-9Miz54Rio1Txl_8MyFgToh5Wevvw"
* status = #final
* code = $loinc#103209-3 "Mean oxygen saturation"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 96 '%'

Instance: GroveMobilePowerExample
InstanceOf: GroveMobilePower
Usage: #example
Title: "Power Example"
Description: "A conformant Power instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:de27AT_tTkWI_OnXLLl7Ln8RLAZ0mjLF-hK9vbTYMCM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:UJe0ZTUMCPJjyOlDtzwdaMHYhAs_bw8u9_7pxcjXJfY"
* status = #final
* code = GroveMobileMeasurementCS#power
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 180 'W'

Instance: GroveMobileRemSleepDurationExample
InstanceOf: GroveMobileRemSleepDuration
Usage: #example
Title: "REM Sleep Duration Example"
Description: "A conformant REM Sleep Duration instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:_8sJGAE0NX_v6CLxeoEzVSs9Pu48VzOFwN58hvFF9Ec"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:IXS9ZabRqYZfr12xj7n439URo1ZoyAkxltGzE4z4_JA"
* status = #final
* code = $loinc#93829-0 "REM sleep duration"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 96 'min'

Instance: GroveMobileRespiratoryRateAverageExample
InstanceOf: GroveMobileRespiratoryRateAverage
Usage: #example
Title: "Respiratory Rate Average Example"
Description: "A conformant Respiratory Rate Average instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:iX253wwpQhtHcAKUFRsFnsMCVsly_VCLvcXfUF9COvg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:gMEXEl8oZk5veVTsVp3EQFd_6MlryjHoClPrh0F0XDs"
* status = #final
* code = $loinc#103217-6 "Mean respiratory rate"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* method = GroveAggregationMethodCS#daily-mean
* valueQuantity = 15 '/min' "breaths/minute"

Instance: GroveMobileRestingHeartRateExample
InstanceOf: GroveMobileRestingHeartRate
Usage: #example
Title: "Resting Heart Rate Example"
Description: "A conformant Resting Heart Rate instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:JlZcRJRneNAdPRWy9w13Os5Or4Guccm-UDAYxFtO86Y"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:4OwQ-rPzuaPV3YIU_QOU2kfOetrnQVSC8W1H8pYHMjA"
* status = #final
* code = $loinc#40443-4 "Heart rate --resting"
* code.coding[heartRate] = $loinc#8867-4 "Heart rate"
* category = $observationCategory#vital-signs "Vital Signs"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 58 '/min' "beats/minute"

Instance: GroveMobileSexualActivityExample
InstanceOf: GroveMobileSexualActivity
Usage: #example
Title: "Sexual Activity Example"
Description: "A conformant Sexual Activity instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:minvQLb6ftFLRlrlVtlnK1qtIt8WefDtRsh8q4C8Jxg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:6_zmpT7paKOUjXu-r9vTWqsRUkrPrAH_nGDWTsegWfI"
* status = #final
* code = GroveMobileMeasurementCS#sexual-activity
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveSexualActivityCS#protected "Protection used"

Instance: GroveMobileSkinTemperatureExample
InstanceOf: GroveMobileSkinTemperature
Usage: #example
Title: "Skin Temperature Example"
Description: "A conformant Skin Temperature instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:4hSAhYPUMbvZvQ2_s16G7rA2XZl23WTTXejSh0vr2to"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:_pu8QaPhdNf-yBZx8EboGkpT9GsMXfH_SkgeHi6x1KE"
* status = #final
* code = $loinc#61008-9 "Body surface temperature"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 33.2 'Cel'

Instance: GroveMobileSleepAwakeDurationExample
InstanceOf: GroveMobileSleepAwakeDuration
Usage: #example
Title: "Awake Duration During Sleep Example"
Description: "A conformant Awake Duration During Sleep instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:2ggk7tdHYlAweKTH_ZlOpT1hWNrNxJxNXxuoFyq74KU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:JFzAGXcTm7gtvpovs60ru_lKKw_l1_mxE04Jdw8XzXw"
* status = #final
* code = $loinc#93828-2 "Nighttime awakening duration"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 22 'min'

Instance: GroveMobileSleepHeartRateExample
InstanceOf: GroveMobileSleepHeartRate
Usage: #example
Title: "Sleep Heart Rate Example"
Description: "A conformant Sleep Heart Rate instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:yIQoN_ABnNnB91-zEsN_LG13PNx0mi9kUSJBB_PxPP0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:AGn7h916nAYvR1gUKlomDUjneFpLPT8g7w59EZeXoyc"
* status = #final
* code = GroveMobileMeasurementCS#sleep-heart-rate
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* method = GroveAggregationMethodCS#session-mean
* valueQuantity = 54 '/min' "beats/minute"

Instance: GroveMobileSpeedExample
InstanceOf: GroveMobileSpeed
Usage: #example
Title: "Speed Example"
Description: "A conformant Speed instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:VL2S9xJJUz5DoKnjjH3uvupsAGmibrdXq9H7qmNf-gQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Jss6l_AfaoEMU4VsoF8WodLv0ZajEzblRSrPHSHAuco"
* status = #final
* code = GroveMobileMeasurementCS#speed
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 3.2 'm/s'

Instance: GroveMobileVo2MaxExample
InstanceOf: GroveMobileVo2Max
Usage: #example
Title: "VO2 Max Example"
Description: "A conformant VO2 Max instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:fhLIVrrk5dF2Nyr131fcWheKgezEUgTG6G1ORL99TVo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:EbMhpCGhsNlMFcN3nP39MlX49Kse5nVabb3fJpzFPDE"
* status = #final
* code = GroveMobileMeasurementCS#vo2-max
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 42.5 'mL/kg/min'

Instance: GroveMobileWheelchairPushCountExample
InstanceOf: GroveMobileWheelchairPushCount
Usage: #example
Title: "Wheelchair Push Count Example"
Description: "A conformant Wheelchair Push Count instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:-Qiyxh_EMBQENZqnHA1bhF6__XnrsPYxp61iGofBHMA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ggiS89m2AzS6BxMxzBv9fPyTcJYhi8jyLkBBapZd0RA"
* status = #final
* code = $loinc#96502-0 "Number of wheelchair pushes per time period"
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1240 '{pushes}' "pushes"

Instance: GroveMobileWorkoutExample
InstanceOf: GroveMobileWorkout
Usage: #example
Title: "Workout Example"
Description: "A conformant Workout instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:dDG_oDGF72FIPxbm1fcFJXagQr0M77n1ll-NKinfsC4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:bWS3B3IzVM_p7VysM22LPfyA4Jt8m9_en9XwPmRJdfE"
* status = #final
* code = GroveMobileMeasurementCS#workout
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveWorkoutActivityCS#running "Running"

Instance: GroveMobileWorkoutSegmentExample
InstanceOf: GroveMobileWorkoutSegment
Usage: #example
Title: "Workout Segment Example"
Description: "A conformant Workout Segment instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Ee7ab8zwXqNdrqqxRhY-AFHVVVxbhCt_ck4d3Q37b0w"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ZPqZgkOkGv-iSM5yYtxoHhUnEtACfqm1kbu-D9qapiI"
* status = #final
* code = GroveMobileMeasurementCS#workout-segment
* subject = Reference(GroveMobilePatientExample)
* performer = Reference(GroveMobilePatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveWorkoutSegmentTypeCS#lap "Lap"
