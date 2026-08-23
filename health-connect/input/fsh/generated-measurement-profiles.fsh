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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:6f1192eb1274c0af4c17ba91bde4befd19633817742e566d8856b586881283cf"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:17f01407c70d7f78eb9526758a443e8921d6a58b6ca75aaad5c69415ea594965"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:0aa09948e7b7b50c17ee4d15ff2a986105562bca43fc24a70af07de282c9fe0e"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:bf789f6016ce18a80f152b79c5aee80e4947c2de128766c92c9bc0886cefb156"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:b76a9bb95cb2033ff472edb1202b0193f758cc27f1d7d1e2ef294d05e3bd2989"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:23e51b7c498a3a753410081684dc0e95572111571258fd27cfee50123bca192c"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:937aa4ce7b3856d67f304fac31314298d610afe2429489a1dbb2ff8756d220d7"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:4fae3662f485d22cbd8df417e387f1499819dd2f8a43b6d499903984cc127b30"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:cb22dc0b9bc8b9a6814d41845f465fa401bcd4ef7b6946b461fbf603d72b99c1"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:92bdcd501e77b10060b3a884ee9e1c8ae5432bcd04ec82c270f9c774ce5ef967"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:7579b6016a7a2ed611b6d7526b32832e7278d1ed90b932231ff983117cb89c34"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:8893714749973afb64a5915dd4ee7c7bd0f85639da3a3181e7cc3d81635551d7"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:61eac76ca4859a415cd6f3b958e196b289db61fab106f5eac67e492cf9f21bbe"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:96ac7dfd816f13641820552aaa197600c5ac8a660296a07335428bf68a03d31a"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:e1a251ed622be36681a7f339257807c026e8bde9b4d2b1dde202083d78cb0249"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:fc35f1a9a71fac3477256a88cfcae0fb573403a8183cbc77f0492190e5aabab6"
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
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:395056fa53f3474e6b5a27ea12f24f8f9f9c4eef9b85d97579d936793b555de3"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:650e8582f14cdff70bcedb6f649ac6ecf9272c48b7715f7c9e32062f15e7aae5"
* status = #final
* code = HealthConnectMeasurementCS#total-energy-burned
* extension[healthConnectRecordType].valueCode = #TotalCaloriesBurnedRecord
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 2200 'kcal'
