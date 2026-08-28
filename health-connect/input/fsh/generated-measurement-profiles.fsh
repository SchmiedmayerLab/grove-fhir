// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: HealthConnectMeasurementCS
Id: health-connect-measurement
Title: "Health Connect Measurement"
Description: "Measurement concepts defined by the Health Connect adapter for platform-exclusive results no established code represents faithfully."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #basal-metabolic-rate "Basal metabolic rate" "The subject's basal metabolic rate, expressed as energy per day, reported at the Observation effective instant."
* #dietary-energy-from-fat "Nutrition energy from fat" "Energy-from-fat component of NutritionRecord, distinct from total energy."
* #dietary-fat-trans "Nutrition trans fat" "Trans fat component of NutritionRecord; the only LOINC trans-fat intake concepts (81034-1 Estimated, 81035-8 Measured) are 24-hour mass-rates and are rejected for the same axis reason as the shared fat rows."
* #dietary-fat-unsaturated "Nutrition unsaturated fat" "Total unsaturated fat component of NutritionRecord."
* #dietary-folic-acid "Nutrition folic acid" "Synthetic folic acid component of NutritionRecord; LOINC has no folic-acid intake concept separate from total folate (NLM search returns only the vitamin B9 folate pair)."
* #elevation-gained "Elevation gained" "The total vertical distance ascended during the exact Observation effective Period."
* #menstruation-period "Menstruation period" "One recorded menstruation period over the exact Observation effective Period."
* #step-cadence "Step cadence" "The rate of steps the subject takes at the exact Observation effective instant."
* #total-energy-burned "Total energy burned" "The sum of basal and activity energy expended during the exact Observation effective Period."

ValueSet: HealthConnectMeasurementVS
Id: health-connect-measurement
Title: "Health Connect Measurement"
Description: "Measurement concepts defined by the Health Connect adapter for its platform-exclusive profiles."
* ^experimental = false
* include codes from system HealthConnectMeasurementCS

CodeSystem: HealthConnectMenstruationPeriodCS
Id: health-connect-menstruation-period
Title: "Menstruation Period Result"
Description: "The closed result codes of the Menstruation Period measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #present "Present" "A menstruation period spanned the effective Period."

ValueSet: HealthConnectMenstruationPeriodVS
Id: health-connect-menstruation-period
Title: "Menstruation Period Result"
Description: "Every admitted result code of the Menstruation Period measurement."
* ^experimental = false
* include codes from system HealthConnectMenstruationPeriodCS

Profile: HealthConnectBasalMetabolicRate
Parent: HealthConnectObservation
Id: health-connect-basal-metabolic-rate
Title: "Basal Metabolic Rate"
Description: "The basal metabolic rate as a power, normalized to UCUM kilocalories per day. Only Health Connect evidences it (BasalMetabolicRateRecord), so it stays in the Health Connect adapter guide; it is never relabeled as resting metabolic rate or as an energy total."
* code = HealthConnectMeasurementCS#basal-metabolic-rate
* code from HealthConnectMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal/d (exactly)

Profile: HealthConnectDietaryEnergyFromFat
Parent: HealthConnectObservation
Id: health-connect-dietary-energy-from-fat
Title: "Health Connect Dietary Energy from Fat"
Description: "Health Connect-only energy from fat consumed during an exact effective Period, normalized to UCUM kilocalories; HealthKit has no counterpart identifier."
* code = HealthConnectMeasurementCS#dietary-energy-from-fat
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal (exactly)

Profile: HealthConnectDietaryFatTrans
Parent: HealthConnectObservation
Id: health-connect-dietary-fat-trans
Title: "Health Connect Dietary Trans Fat"
Description: "Health Connect-only trans fat mass consumed during an exact effective Period, normalized to UCUM grams; HealthKit has no trans-fat dietary identifier."
* code = HealthConnectMeasurementCS#dietary-fat-trans
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: HealthConnectDietaryFatUnsaturated
Parent: HealthConnectObservation
Id: health-connect-dietary-fat-unsaturated
Title: "Health Connect Dietary Unsaturated Fat"
Description: "Health Connect-only total unsaturated fat mass consumed during an exact effective Period, normalized to UCUM grams; HealthKit has no combined unsaturated-fat identifier and the value cannot be derived when the mono and poly fields are null."
* code = HealthConnectMeasurementCS#dietary-fat-unsaturated
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #g (exactly)

Profile: HealthConnectDietaryFolicAcid
Parent: HealthConnectObservation
Id: health-connect-dietary-folic-acid
Title: "Health Connect Dietary Folic Acid"
Description: "Health Connect-only synthetic folic acid mass consumed during an exact effective Period, normalized to UCUM micrograms; distinct from total folate."
* code = HealthConnectMeasurementCS#dietary-folic-acid
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ug (exactly)

Profile: HealthConnectElevationGained
Parent: HealthConnectObservation
Id: health-connect-elevation-gained
Title: "Elevation Gained"
Description: "Vertical elevation gained during an exact effective Period, normalized to UCUM metres. Withings intraday elevation series remain in the provider recording document and do not implement this profile."
* code = HealthConnectMeasurementCS#elevation-gained
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: HealthConnectMenstruationPeriod
Parent: HealthConnectObservation
Id: health-connect-menstruation-period
Title: "Menstruation Period"
Description: "One user-recorded menstruation period interval. Health Connect records the interval directly; HealthKit derives intervals from flow samples and therefore never emits this profile."
* code = HealthConnectMeasurementCS#menstruation-period
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthConnectMenstruationPeriodVS (required)

Profile: HealthConnectStepCadence
Parent: HealthConnectObservation
Id: health-connect-step-cadence
Title: "Step Cadence"
Description: "The instantaneous rate of steps taken, normalized to UCUM steps per minute using the allowlisted {steps} annotation. It is distinct from cycling cadence (crank revolutions) and from the shared step-count total (a Period sum, not a rate)."
* code = HealthConnectMeasurementCS#step-cadence
* code from HealthConnectMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{steps}/min (exactly)

Profile: HealthConnectTotalEnergy
Parent: HealthConnectObservation
Id: health-connect-total-energy
Title: "Total Energy Burned"
Description: "Total energy expenditure - basal plus active - during an exact effective Period, normalized to UCUM kilocalories. It overlaps the shared active-energy and basal-energy measurements by definition and is therefore never emitted alongside a decomposition for the same interval by the same producer."
* code = HealthConnectMeasurementCS#total-energy-burned
* code from HealthConnectMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal (exactly)

Instance: HealthConnectBasalMetabolicRateExample
InstanceOf: HealthConnectBasalMetabolicRate
Usage: #example
Title: "Basal Metabolic Rate Example"
Description: "A conformant Basal Metabolic Rate instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:vYaeDJowQfbyyWy53rCPMHiyhrgfcYD_3GVPcCXzk9E"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:dUbFKDHglylLvGnY14T9HSs0WSOHQyN8f5pJnBau3-8"
* status = #final
* code = HealthConnectMeasurementCS#basal-metabolic-rate
* extension[healthConnectRecordType].valueCode = #BasalMetabolicRateRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 1580 'kcal/d' "kcal/day"

Instance: HealthConnectDietaryEnergyFromFatExample
InstanceOf: HealthConnectDietaryEnergyFromFat
Usage: #example
Title: "Health Connect Dietary Energy from Fat Example"
Description: "A conformant Health Connect Dietary Energy from Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:KY5afLGTwH74v6jyZz0YRsjSIla1Peeso1ltNmXBrzE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:-ihnn0OnV6Ftn4eoUHmN7z33vvsvoODzMKJZFvRTkPs"
* status = #final
* code = HealthConnectMeasurementCS#dietary-energy-from-fat
* extension[healthConnectRecordType].valueCode = #NutritionRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 700 'kcal'

Instance: HealthConnectDietaryFatTransExample
InstanceOf: HealthConnectDietaryFatTrans
Usage: #example
Title: "Health Connect Dietary Trans Fat Example"
Description: "A conformant Health Connect Dietary Trans Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:RSgOHa_kKD_aslV3aafWZzharGboNRGlUPIycPf3iko"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:jICJgMpDzu7LLBvgiWGR_pJDZn3kfBmYExM953C3l-o"
* status = #final
* code = HealthConnectMeasurementCS#dietary-fat-trans
* extension[healthConnectRecordType].valueCode = #NutritionRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 1 'g'

Instance: HealthConnectDietaryFatUnsaturatedExample
InstanceOf: HealthConnectDietaryFatUnsaturated
Usage: #example
Title: "Health Connect Dietary Unsaturated Fat Example"
Description: "A conformant Health Connect Dietary Unsaturated Fat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:GfPv-5rLdU-J5iBTjdsFEb-fA4Uvn9uiYF3RidP1_u0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:5zXLUchruOQPQhHLZEBBPUpnZNmW7zdBkjaU5fF_qkI"
* status = #final
* code = HealthConnectMeasurementCS#dietary-fat-unsaturated
* extension[healthConnectRecordType].valueCode = #NutritionRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 57 'g'

Instance: HealthConnectDietaryFolicAcidExample
InstanceOf: HealthConnectDietaryFolicAcid
Usage: #example
Title: "Health Connect Dietary Folic Acid Example"
Description: "A conformant Health Connect Dietary Folic Acid instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:FRbaSGQ7pSfmKUOpfseV1Tp7-Nc8CbyJ5oIwrC-b5Q8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:nS8c8GQI3S4ruUnhKrOTKqQmO92Q_SVN8cTPbunBCN4"
* status = #final
* code = HealthConnectMeasurementCS#dietary-folic-acid
* extension[healthConnectRecordType].valueCode = #NutritionRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 400 'ug'

Instance: HealthConnectElevationGainedExample
InstanceOf: HealthConnectElevationGained
Usage: #example
Title: "Elevation Gained Example"
Description: "A conformant Elevation Gained instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:V6QsinJVPSjbnx_zjSPlPKF_2sqHSZRQsUWZ9_yWxwU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:EGFPDUS9JFvXG7yr1krUg9ZWwHBob4KFF6r0FB4cKds"
* status = #final
* code = HealthConnectMeasurementCS#elevation-gained
* extension[healthConnectRecordType].valueCode = #ElevationGainedRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 120 'm'

Instance: HealthConnectMenstruationPeriodExample
InstanceOf: HealthConnectMenstruationPeriod
Usage: #example
Title: "Menstruation Period Example"
Description: "A conformant Menstruation Period instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:YyYWSJXYKVXzYjc-4HXX0CF5s1BhQUVjRao03HMD_hU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:tAqnivDyI2QkzwHKIEFwvZMgZIW1GvCAlm9nAFvX0Mw"
* status = #final
* code = HealthConnectMeasurementCS#menstruation-period
* extension[healthConnectRecordType].valueCode = #MenstruationPeriodRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueCodeableConcept = HealthConnectMenstruationPeriodCS#present "Present"

Instance: HealthConnectStepCadenceExample
InstanceOf: HealthConnectStepCadence
Usage: #example
Title: "Step Cadence Example"
Description: "A conformant Step Cadence instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:UvsZj4IoPl2PMM8LZU-luMPQzIvJjz6RkEdT_Fixvbc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:G5Drw0KxVhk84CV64_LrFygJ4Ps4cVAodHhDID9QwO8"
* status = #final
* code = HealthConnectMeasurementCS#step-cadence
* extension[healthConnectRecordType].valueCode = #StepsCadenceRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 112 '{steps}/min' "steps/minute"

Instance: HealthConnectTotalEnergyExample
InstanceOf: HealthConnectTotalEnergy
Usage: #example
Title: "Total Energy Burned Example"
Description: "A conformant Total Energy Burned instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:tXuqbDO6MUoKF7Qtc1djtJ46dfTj1R__9hkHIZR191g"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:JRZTIZat6h1Du_w9plXJzP4xcKjVuPeMJhh1uhGrmRY"
* status = #final
* code = HealthConnectMeasurementCS#total-energy-burned
* extension[healthConnectRecordType].valueCode = #TotalCaloriesBurnedRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 2200 'kcal'
