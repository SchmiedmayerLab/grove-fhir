// GENERATED FILE. Edit catalog/measurement-catalog.json and run
// Scripts/render-measurement-profiles.py; do not edit by hand.
//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

CodeSystem: HealthKitMeasurementCS
Id: healthkit-measurement
Title: "HealthKit Measurement"
Description: "Measurement concepts defined by the HealthKit adapter for platform-exclusive results no established code represents faithfully."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #apple-exercise-time "Apple exercise time" "Time credited by Apple's proprietary Exercise-ring algorithm during the exact Observation effective Period."
* #apple-move-time "Apple move time" "Time credited by Apple's proprietary time-based Move-ring algorithm during the exact Observation effective Period."
* #apple-stand-hour "Apple stand hour" "Apple-defined per-hour stand/idle classification from the Activity Stand ring."
* #apple-stand-time "Apple stand time" "Standing time credited by Apple's proprietary Stand algorithm during the exact Observation effective Period."
* #atrial-fibrillation-burden "Atrial fibrillation burden" "The percentage of analyzed heart-rhythm time classified as atrial fibrillation within the exact Observation effective Period."
* #bladder-incontinence "Bladder incontinence" "Logged severity of bladder incontinence."
* #bleeding-after-pregnancy "Bleeding after pregnancy" "Logged vaginal bleeding amount after pregnancy."
* #bleeding-during-pregnancy "Bleeding during pregnancy" "Logged vaginal bleeding amount during pregnancy."
* #blood-alcohol-content "Blood alcohol content" "The blood alcohol concentration expressed as a percent, as reported by the source at the Observation effective instant."
* #cycling-functional-threshold-power "Cycling functional threshold power" "The source-estimated highest cycling power output the subject can sustain for approximately one hour."
* #environmental-audio-exposure "Environmental audio exposure" "The A-weighted equivalent continuous sound pressure level of environmental sound the user was exposed to during the exact Observation effective Period."
* #environmental-sound-reduction "Environmental sound reduction" "The difference in equivalent continuous sound pressure level attenuated by the user's noise-reducing headphones during the exact Observation effective Period."
* #handwashing-session "Handwashing session" "The duration of one handwashing event during the exact Observation effective Period."
* #headphone-audio-exposure "Headphone audio exposure" "The A-weighted equivalent continuous sound pressure level of headphone audio the user was exposed to during the exact Observation effective Period."
* #heart-rate-recovery-one-minute "Heart rate recovery one minute" "The decrease in heart rate, in beats per minute, from peak exercise to one minute after the end of exercise."
* #inhaler-usage "Inhaler usage" "The total number of inhaler puffs the user took during the exact Observation effective Period."
* #insulin-delivery "Insulin delivery" "The amount of insulin delivered during the exact Observation effective Period, qualified by a required basal or bolus delivery reason."
* #number-of-alcoholic-beverages "Number of alcoholic beverages" "The number of standard alcoholic drinks attributed to the exact Observation effective Period."
* #number-of-times-fallen "Number of times fallen" "The total number of falls attributed to the exact Observation effective Period."
* #physical-effort "Physical effort" "Estimated exertion intensity, in energy per body mass per time, over the exact Observation effective Period."
* #progesterone-test-result "Progesterone (PdG) test result" "Qualitative result of a home urine pregnanediol-3-glucuronide test."
* #running-ground-contact-time "Running ground contact time" "The ground contact time of one running stride at the sample instant."
* #running-stride-length "Running stride length" "The distance covered by one running stride at the sample instant."
* #running-vertical-oscillation "Running vertical oscillation" "The vertical oscillation of the torso during running at the sample instant."
* #sleeping-breathing-disturbances "Sleeping breathing disturbances" "The number of accelerometer-detected breathing disturbance events per hour of sleep during the exact nightly Observation effective Period."
* #swimming-stroke-count "Swimming stroke count" "The total number of swimming strokes attributed to the exact Observation effective Period."
* #symptom-abdominal-cramps "Abdominal cramps" "Presence and severity of abdominal cramps as reported by the user."
* #symptom-acne "Acne" "Presence and severity of acne as reported by the user."
* #symptom-appetite-changes "Appetite changes" "Direction of a reported change in appetite."
* #symptom-bloating "Bloating" "Presence and severity of abdominal bloating as reported by the user."
* #symptom-breast-pain "Breast pain" "Presence and severity of breast pain as reported by the user."
* #symptom-chest-tightness-or-pain "Chest tightness or pain" "Presence and severity of chest tightness or pain as reported by the user."
* #symptom-chills "Chills" "Presence and severity of chills as reported by the user."
* #symptom-constipation "Constipation" "Presence and severity of constipation as reported by the user."
* #symptom-coughing "Coughing" "Presence and severity of coughing as reported by the user."
* #symptom-diarrhea "Diarrhea" "Presence and severity of diarrhea as reported by the user."
* #symptom-dizziness "Dizziness" "Presence and severity of dizziness as reported by the user."
* #symptom-dry-skin "Dry skin" "Presence and severity of dry skin as reported by the user."
* #symptom-fainting "Fainting" "Presence and severity of fainting as reported by the user."
* #symptom-fatigue "Fatigue" "Presence and severity of fatigue as reported by the user."
* #symptom-fever "Fever" "Presence and severity of fever as reported by the user."
* #symptom-generalized-body-ache "Generalized body ache" "Presence and severity of generalized body ache as reported by the user."
* #symptom-hair-loss "Hair loss" "Presence and severity of hair loss as reported by the user."
* #symptom-headache "Headache" "Presence and severity of headache as reported by the user."
* #symptom-heartburn "Heartburn" "Presence and severity of heartburn as reported by the user."
* #symptom-hot-flashes "Hot flashes" "Presence and severity of hot flashes as reported by the user."
* #symptom-loss-of-smell "Loss of smell" "Presence and severity of loss of smell as reported by the user."
* #symptom-loss-of-taste "Loss of taste" "Presence and severity of loss of taste as reported by the user."
* #symptom-lower-back-pain "Lower back pain" "Presence and severity of lower back pain as reported by the user."
* #symptom-memory-lapse "Memory lapse" "Presence and severity of memory lapses as reported by the user."
* #symptom-mood-changes "Mood changes" "Whether the user reported experiencing mood changes."
* #symptom-night-sweats "Night sweats" "Presence and severity of night sweats as reported by the user."
* #symptom-pelvic-pain "Pelvic pain" "Presence and severity of pelvic pain as reported by the user."
* #symptom-rapid-pounding-or-fluttering-heartbeat "Rapid, pounding, or fluttering heartbeat" "Presence and severity of a rapid, pounding, or fluttering heartbeat as reported by the user."
* #symptom-runny-nose "Runny nose" "Presence and severity of a runny nose as reported by the user."
* #symptom-shortness-of-breath "Shortness of breath" "Presence and severity of shortness of breath as reported by the user."
* #symptom-sinus-congestion "Sinus congestion" "Presence and severity of sinus congestion as reported by the user."
* #symptom-skipped-heartbeat "Skipped heartbeat" "Presence and severity of a skipped heartbeat sensation as reported by the user."
* #symptom-sleep-changes "Sleep changes" "Whether the user reported changes in their sleep."
* #symptom-sore-throat "Sore throat" "Presence and severity of a sore throat as reported by the user."
* #symptom-vomiting "Vomiting" "Presence and severity of vomiting as reported by the user."
* #symptom-wheezing "Wheezing" "Presence and severity of wheezing as reported by the user."
* #time-in-daylight "Time in daylight" "The cumulative time the user spent in daylight during the exact Observation effective Period, as measured by the source ambient light sensing."
* #toothbrushing-session "Toothbrushing session" "The duration of one toothbrushing event during the exact Observation effective Period."
* #underwater-depth "Underwater depth" "The depth of the wearer below the water surface during a submersion, as sampled by the device."
* #uv-exposure "UV exposure" "The Global Solar UV Index value the user was exposed to during the exact Observation effective Period."
* #vaginal-dryness "Vaginal dryness" "Logged severity of vaginal dryness."
* #walking-heart-rate-average "Walking heart rate average" "The mean heart rate during periods classified as walking within the exact Observation effective Period."
* #walking-speed "Walking speed" "The speed at which the subject walks, sampled by the source during ordinary walking bouts."
* #walking-steadiness "Walking steadiness" "A windowed percentage score summarizing the stability of the subject's gait over the aggregation period."
* #walking-step-length "Walking step length" "The distance covered by a single step during ordinary walking, as sampled by the source."
* #water-temperature "Water temperature" "The temperature of the water surrounding the wearer during a water activity, as sampled by the device."
* #wheelchair-use "Wheelchair use" "Whether the subject uses a wheelchair, as recorded in the HealthKit wheelchair-use characteristic."
* #workout-effort-score "Workout effort score" "An Apple-proprietary 1-10 rating of perceived or estimated workout effort for the exact associated workout Period."

ValueSet: HealthKitMeasurementVS
Id: healthkit-measurement
Title: "HealthKit Measurement"
Description: "Measurement concepts defined by the HealthKit adapter for its platform-exclusive profiles."
* ^experimental = false
* include codes from system HealthKitMeasurementCS

CodeSystem: HealthkitAppleStandHourCS
Id: healthkit-apple-stand-hour
Title: "Apple Stand Hour Result"
Description: "The closed result codes of the Apple Stand Hour measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #stood "Stood" "The user stood and moved at least one minute during the hour."
* #idle "Idle" "The user did not stand and move at least one minute during the hour."

ValueSet: HealthkitAppleStandHourVS
Id: healthkit-apple-stand-hour
Title: "Apple Stand Hour Result"
Description: "Every admitted result code of the Apple Stand Hour measurement."
* ^experimental = false
* include codes from system HealthkitAppleStandHourCS

CodeSystem: HealthkitBleedingAfterPregnancyCS
Id: healthkit-bleeding-after-pregnancy
Title: "Bleeding After Pregnancy Result"
Description: "The closed result codes of the Bleeding After Pregnancy measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #unspecified "Unspecified" "Bleeding of unspecified amount."
* #light "Light" "Light bleeding."
* #medium "Medium" "Medium bleeding."
* #heavy "Heavy" "Heavy bleeding."
* #none "None" "No bleeding."

ValueSet: HealthkitBleedingAfterPregnancyVS
Id: healthkit-bleeding-after-pregnancy
Title: "Bleeding After Pregnancy Result"
Description: "Every admitted result code of the Bleeding After Pregnancy measurement."
* ^experimental = false
* include codes from system HealthkitBleedingAfterPregnancyCS

CodeSystem: HealthkitBleedingDuringPregnancyCS
Id: healthkit-bleeding-during-pregnancy
Title: "Bleeding During Pregnancy Result"
Description: "The closed result codes of the Bleeding During Pregnancy measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #unspecified "Unspecified" "Bleeding of unspecified amount."
* #light "Light" "Light bleeding."
* #medium "Medium" "Medium bleeding."
* #heavy "Heavy" "Heavy bleeding."
* #none "None" "No bleeding."

ValueSet: HealthkitBleedingDuringPregnancyVS
Id: healthkit-bleeding-during-pregnancy
Title: "Bleeding During Pregnancy Result"
Description: "Every admitted result code of the Bleeding During Pregnancy measurement."
* ^experimental = false
* include codes from system HealthkitBleedingDuringPregnancyCS

CodeSystem: HealthkitBloodTypeCS
Id: healthkit-blood-type
Title: "Grove HealthKit Blood Type Result"
Description: "The closed result codes of the Grove HealthKit Blood Type measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #a-positive "A positive" "ABO group A, Rh positive."
* #a-negative "A negative" "ABO group A, Rh negative."
* #b-positive "B positive" "ABO group B, Rh positive."
* #b-negative "B negative" "ABO group B, Rh negative."
* #ab-positive "AB positive" "ABO group AB, Rh positive."
* #ab-negative "AB negative" "ABO group AB, Rh negative."
* #o-positive "O positive" "ABO group O, Rh positive."
* #o-negative "O negative" "ABO group O, Rh negative."

ValueSet: HealthkitBloodTypeVS
Id: healthkit-blood-type
Title: "Grove HealthKit Blood Type Result"
Description: "Every admitted result code of the Grove HealthKit Blood Type measurement."
* ^experimental = false
* include codes from system HealthkitBloodTypeCS

CodeSystem: HealthkitContraceptiveUseCS
Id: healthkit-contraceptive-use
Title: "Contraceptive Use Result"
Description: "The closed result codes of the Contraceptive Use measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #unspecified "Unspecified" "A contraceptive whose method is not specified."
* #implant "Implant" "A contraceptive implant."
* #injection "Injection" "A contraceptive injection."
* #intrauterine-device "Intrauterine device" "An intrauterine device (IUD)."
* #intravaginal-ring "Intravaginal ring" "An intravaginal contraceptive ring."
* #oral "Oral" "An oral contraceptive."
* #patch "Patch" "A contraceptive patch."

ValueSet: HealthkitContraceptiveUseVS
Id: healthkit-contraceptive-use
Title: "Contraceptive Use Result"
Description: "Every admitted result code of the Contraceptive Use measurement."
* ^experimental = false
* include codes from system HealthkitContraceptiveUseCS

CodeSystem: HealthkitLactationStatusCS
Id: healthkit-lactation-status
Title: "Lactation Status Result"
Description: "The closed result codes of the Lactation Status measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #lactating "Lactating" "The person was lactating during the exact Observation effective Period."

ValueSet: HealthkitLactationStatusVS
Id: healthkit-lactation-status
Title: "Lactation Status Result"
Description: "Every admitted result code of the Lactation Status measurement."
* ^experimental = false
* include codes from system HealthkitLactationStatusCS

CodeSystem: HealthkitPregnancyStatusCS
Id: healthkit-pregnancy-status
Title: "Pregnancy Status Result"
Description: "The closed result codes of the Pregnancy Status measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #pregnant "Pregnant" "The person was pregnant during the exact Observation effective Period."

ValueSet: HealthkitPregnancyStatusVS
Id: healthkit-pregnancy-status
Title: "Pregnancy Status Result"
Description: "Every admitted result code of the Pregnancy Status measurement."
* ^experimental = false
* include codes from system HealthkitPregnancyStatusCS

CodeSystem: HealthkitPregnancyTestResultCS
Id: healthkit-pregnancy-test-result
Title: "Pregnancy Test Result Result"
Description: "The closed result codes of the Pregnancy Test Result measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #negative "Negative" "The pregnancy test was negative."
* #positive "Positive" "The pregnancy test was positive."
* #indeterminate "Indeterminate" "The pregnancy test result could not be determined."

ValueSet: HealthkitPregnancyTestResultVS
Id: healthkit-pregnancy-test-result
Title: "Pregnancy Test Result Result"
Description: "Every admitted result code of the Pregnancy Test Result measurement."
* ^experimental = false
* include codes from system HealthkitPregnancyTestResultCS

CodeSystem: HealthkitProgesteroneTestResultCS
Id: healthkit-progesterone-test-result
Title: "Progesterone Test Result Result"
Description: "The closed result codes of the Progesterone Test Result measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #negative "Negative" "The PdG test was negative."
* #positive "Positive" "The PdG test was positive."
* #indeterminate "Indeterminate" "The PdG test result could not be determined."

ValueSet: HealthkitProgesteroneTestResultVS
Id: healthkit-progesterone-test-result
Title: "Progesterone Test Result Result"
Description: "Every admitted result code of the Progesterone Test Result measurement."
* ^experimental = false
* include codes from system HealthkitProgesteroneTestResultCS

CodeSystem: HealthkitSymptomAppetiteChangesCS
Id: healthkit-symptom-appetite-changes
Title: "Symptom: Appetite Changes Result"
Description: "The closed result codes of the Symptom: Appetite Changes measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #no-change "No change" "No change in appetite."
* #decreased "Decreased" "Appetite decreased."
* #increased "Increased" "Appetite increased."
* #change-unspecified "Changed, direction unspecified" "Appetite changed; the direction was not specified."

ValueSet: HealthkitSymptomAppetiteChangesVS
Id: healthkit-symptom-appetite-changes
Title: "Symptom: Appetite Changes Result"
Description: "Every admitted result code of the Symptom: Appetite Changes measurement."
* ^experimental = false
* include codes from system HealthkitSymptomAppetiteChangesCS

CodeSystem: HealthkitWheelchairUseCS
Id: healthkit-wheelchair-use
Title: "Grove HealthKit Wheelchair Use Result"
Description: "The closed result codes of the Grove HealthKit Wheelchair Use measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #uses-wheelchair "Uses wheelchair" "The subject uses a wheelchair."
* #does-not-use-wheelchair "Does not use wheelchair" "The subject does not use a wheelchair."

ValueSet: HealthkitWheelchairUseVS
Id: healthkit-wheelchair-use
Title: "Grove HealthKit Wheelchair Use Result"
Description: "Every admitted result code of the Grove HealthKit Wheelchair Use measurement."
* ^experimental = false
* include codes from system HealthkitWheelchairUseCS

Profile: HealthkitAppleExerciseTime
Parent: HealthKitObservation
Id: healthkit-apple-exercise-time
Title: "Apple Exercise Time"
Description: "Minutes credited to the Apple Watch Exercise ring during an exact effective Period, normalized to UCUM minutes. The crediting threshold is an Apple-proprietary brisk-activity heuristic, so this is not generic exercise duration and is never mapped to LOINC 55411-3."
* code = HealthKitMeasurementCS#apple-exercise-time
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: HealthkitAppleMoveTime
Parent: HealthKitObservation
Id: healthkit-apple-move-time
Title: "Apple Move Time"
Description: "Minutes credited to the Apple Watch Move ring in its time-based mode during an exact effective Period, normalized to UCUM minutes. It is Apple-proprietary ring credit, distinct from both apple-exercise-time and any energy measurement."
* code = HealthKitMeasurementCS#apple-move-time
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: HealthkitAppleStandHour
Parent: HealthKitObservation
Id: healthkit-apple-stand-hour
Title: "Apple Stand Hour"
Description: "HKCategoryTypeIdentifierAppleStandHour: per-hour classification of whether the user stood (or, for wheelchair users, rolled) and moved for at least one minute, as tracked by the Apple Watch Stand ring. Coded result over the exact hour Period."
* code = HealthKitMeasurementCS#apple-stand-hour
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitAppleStandHourVS (required)

Profile: HealthkitAppleStandTime
Parent: HealthKitObservation
Id: healthkit-apple-stand-time
Title: "Apple Stand Time"
Description: "Minutes the user was standing and moving, as credited by the Apple Watch Stand algorithm, during an exact effective Period and normalized to UCUM minutes."
* code = HealthKitMeasurementCS#apple-stand-time
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: HealthkitAtrialFibrillationBurden
Parent: HealthKitObservation
Id: healthkit-atrial-fibrillation-burden
Title: "Atrial Fibrillation Burden"
Description: "The estimated percentage of analyzed time showing atrial fibrillation over a multi-day estimation window, normalized to UCUM percent. It is a windowed estimate implemented by the phase-2 aggregate design; the Withings AFib classification scalars remain intentionally unsupported and never join it."
* code = HealthKitMeasurementCS#atrial-fibrillation-burden
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#percentage-of-time "Percentage of time"
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)

Profile: HealthkitBladderIncontinence
Parent: HealthKitObservation
Id: healthkit-bladder-incontinence
Title: "Bladder Incontinence"
Description: "HKCategoryTypeIdentifierBladderIncontinence: records bladder incontinence as a symptom using HKCategoryValueSeverity (unspecified, notPresent, mild, moderate, severe)."
* code = HealthKitMeasurementCS#bladder-incontinence
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitBleedingAfterPregnancy
Parent: HealthKitObservation
Id: healthkit-bleeding-after-pregnancy
Title: "Bleeding After Pregnancy"
Description: "HKCategoryTypeIdentifierBleedingAfterPregnancy: records postpartum bleeding (lochia) using HKCategoryValueVaginalBleeding (unspecified, light, medium, heavy, none). Coded amount result at a point in time."
* code = HealthKitMeasurementCS#bleeding-after-pregnancy
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitBleedingAfterPregnancyVS (required)

Profile: HealthkitBleedingDuringPregnancy
Parent: HealthKitObservation
Id: healthkit-bleeding-during-pregnancy
Title: "Bleeding During Pregnancy"
Description: "HKCategoryTypeIdentifierBleedingDuringPregnancy: records bleeding during pregnancy as a symptom using HKCategoryValueVaginalBleeding (verified cases: unspecified, light, medium, heavy, none). Coded amount result at a point in time."
* code = HealthKitMeasurementCS#bleeding-during-pregnancy
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitBleedingDuringPregnancyVS (required)

Profile: HealthkitBloodAlcoholContent
Parent: HealthKitObservation
Id: healthkit-blood-alcohol-content
Title: "Blood Alcohol Content"
Description: "Blood alcohol content as the mass-percent concentration figure a breathalyzer or user reports, kept as the plain UCUM percent scalar per the decided contract. It is not converted into a laboratory ethanol mass concentration."
* code = HealthKitMeasurementCS#blood-alcohol-content
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)

Profile: HealthkitBloodType
Parent: HealthKitObservation
Id: healthkit-blood-type
Title: "Grove HealthKit Blood Type"
Description: "ABO and Rh group as a coded Observation. LOINC 882-1 'ABO and Rh group [Type] in Blood' is the exact concept (re-verified ACTIVE, PROPERTY LP6886-8 Type, SCALE_TYP LP7750-5 Nom). Value is a Grove-coded ABO/Rh concept with the HKBloodType token retained as secondary coding per the sleep-stage absorption pattern."
* code = $loinc#882-1
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitBloodTypeVS (required)

Profile: HealthkitContraceptiveUse
Parent: HealthKitObservation
Id: healthkit-contraceptive-use
Title: "Contraceptive Use"
Description: "HKCategoryTypeIdentifierContraceptive: records use of a contraceptive method over the sample interval. Coded result under LOINC 8659-5 Birth control method - Reported (Type/Nom, ACTIVE) with a Grove method value set absorbing HKCategoryValueContraceptive."
* code = $loinc#8659-5
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitContraceptiveUseVS (required)

Profile: HealthkitCyclingFunctionalThresholdPower
Parent: HealthKitObservation
Id: healthkit-cycling-functional-threshold-power
Title: "Cycling Functional Threshold Power"
Description: "The estimated maximum cycling power output the subject can sustain for about an hour, as derived by the source, normalized to UCUM watts. It is a derived capacity estimate, distinct from the shared instantaneous power measurement."
* code = HealthKitMeasurementCS#cycling-functional-threshold-power
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #W (exactly)

Profile: HealthkitEnvironmentalAudioExposure
Parent: HealthKitObservation
Id: healthkit-environmental-audio-exposure
Title: "Environmental Audio Exposure"
Description: "The A-weighted equivalent continuous sound pressure level of environmental sound over an exact effective Period, normalized to UCUM decibels sound pressure level per the pinned Grove decibel convention. Only HealthKit evidences this concept."
* code = HealthKitMeasurementCS#environmental-audio-exposure
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #dB[SPL] (exactly)

Profile: HealthkitEnvironmentalSoundReduction
Parent: HealthKitObservation
Id: healthkit-environmental-sound-reduction
Title: "Environmental Sound Reduction"
Description: "The reduction in equivalent continuous sound pressure level provided by noise-reducing headphones over an exact effective Period, expressed in UCUM decibels sound pressure level per the pinned Grove decibel convention. The value is a level difference, not an absolute exposure level."
* code = HealthKitMeasurementCS#environmental-sound-reduction
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #dB[SPL] (exactly)

Profile: HealthkitForcedExpiratoryVolume1
Parent: HealthKitObservation
Id: healthkit-forced-expiratory-volume-1
Title: "Forced Expiratory Volume in 1 Second"
Description: "The volume of air forcibly exhaled during the first second of a forced exhalation, captured as a point spirometry result and normalized to UCUM litres. Only HealthKit evidences this concept, so it lands in the HealthKit adapter guide."
* code = $loinc#20150-9
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #L (exactly)

Profile: HealthkitForcedVitalCapacity
Parent: HealthKitObservation
Id: healthkit-forced-vital-capacity
Title: "Forced Vital Capacity"
Description: "The volume of air forcibly exhaled after the deepest possible breath, captured as a point spirometry result and normalized to UCUM litres. Only HealthKit evidences this concept, so it lands in the HealthKit adapter guide."
* code = $loinc#19868-9
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #L (exactly)

Profile: HealthkitGad7Assessment
Parent: HealthKitObservation
Id: healthkit-gad7-assessment
Title: "Grove HealthKit GAD-7 Score"
Description: "HKGAD7Assessment (iOS 18, HKScoredAssessment subclass): score 0-21, answers [HKGAD7Assessment.Answer], risk. Routing recommendation: platform-exclusive score Observation on exact LOINC 70274-6 'Generalized anxiety disorder 7 item (GAD-7) total score [Reported.PHQ]' (re-verified ACTIVE, PROPERTY LP185820-0 Score, SCALE_TYP LP7753-9 Qn). The seven answers are retained as components coded with the LOINC GAD-7 item codes under panel 69737-5 (re-verified), each valued with the standard LOINC answer codes (LA6568-5 'Not at all', LA6569-3 'Several days', LA6570-1 'More than half the days', LA6571-9 'Nearly every day' — all four displays re-verified against LOINC 2.82 via tx.fhir.org) absorbing Answer cases notAtAll, severalDays, moreThanHalfTheDays, nearlyEveryDay; Risk (noneToMinimal, mild, moderate, severe — re-verified) is redundant with the published score bands and is carried only as an Observation.interpretation-style Grove coding, not a value."
* code = $loinc#70274-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{score} (exactly)

Profile: HealthkitHandwashingSession
Parent: HealthKitObservation
Id: healthkit-handwashing-session
Title: "Handwashing Session"
Description: "HKCategoryTypeIdentifierHandwashingEvent: an interval sample (notApplicable value) recorded automatically by Apple Watch Series 4+ or written by apps; the sample duration is the handwashing duration. Emitted as a duration quantity over the exact Period."
* code = HealthKitMeasurementCS#handwashing-session
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #s (exactly)

Profile: HealthkitHeadphoneAudioExposure
Parent: HealthKitObservation
Id: healthkit-headphone-audio-exposure
Title: "Headphone Audio Exposure"
Description: "The A-weighted equivalent continuous sound pressure level delivered through headphones over an exact effective Period, normalized to UCUM decibels sound pressure level per the pinned Grove decibel convention. Only HealthKit evidences this concept."
* code = HealthKitMeasurementCS#headphone-audio-exposure
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #dB[SPL] (exactly)

Profile: HealthkitHeartRateRecoveryOneMinute
Parent: HealthKitObservation
Id: healthkit-heart-rate-recovery-one-minute
Title: "Heart Rate Recovery (One Minute)"
Description: "The reduction in heart rate from workout peak to exactly one minute after exercise ends, normalized to UCUM beats per minute. The one-minute protocol is part of the meaning, so the value is not a heart rate and never joins the shared heart-rate measurement."
* code = HealthKitMeasurementCS#heart-rate-recovery-one-minute
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: HealthkitInhalerUsage
Parent: HealthKitObservation
Id: healthkit-inhaler-usage
Title: "Inhaler Usage"
Description: "The number of inhaler puffs taken during an exact effective Period. The count is a device-usage total, not a medication-administration record, and only HealthKit evidences it."
* code = HealthKitMeasurementCS#inhaler-usage
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{puff} (exactly)

Profile: HealthkitInsulinDelivery
Parent: HealthKitObservation
Id: healthkit-insulin-delivery
Title: "Insulin Delivery"
Description: "The quantity of insulin delivered during the exact effective Period, normalized to UCUM international units, with a REQUIRED delivery-reason component distinguishing basal from bolus delivery per the decided contract. A sample without the HKMetadataKeyInsulinDeliveryReason metadata fails closed."
* code = HealthKitMeasurementCS#insulin-delivery
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #[iU] (exactly)

Profile: HealthkitLactationStatus
Parent: HealthKitObservation
Id: healthkit-lactation-status
Title: "Lactation Status"
Description: "HKCategoryTypeIdentifierLactation: an interval flag (notApplicable value) asserting lactation over the sample period. Emitted as a coded Observation under LOINC 63895-7 Breastfeeding status (Find/Nom, ACTIVE) with the fixed Grove result lactating over the exact effective Period."
* code = $loinc#63895-7
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitLactationStatusVS (required)

Profile: HealthkitNumberOfAlcoholicBeverages
Parent: HealthKitObservation
Id: healthkit-number-of-alcoholic-beverages
Title: "Number of Alcoholic Beverages"
Description: "The count of standard alcoholic drinks consumed during the exact effective Period, using the annotated dimensionless UCUM unit {drinks}. Counting semantics follow the source's standard-drink definition and are not converted to ethanol mass."
* code = HealthKitMeasurementCS#number-of-alcoholic-beverages
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{drinks} (exactly)

Profile: HealthkitNumberOfTimesFallen
Parent: HealthKitObservation
Id: healthkit-number-of-times-fallen
Title: "Number of Times Fallen"
Description: "The number of falls recorded during an exact effective Period, normalized to the UCUM annotation {falls}. This is a device or user-recorded interval count, not a clinical falls-history assessment."
* code = HealthKitMeasurementCS#number-of-times-fallen
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{falls} (exactly)

Profile: HealthkitPeakExpiratoryFlowRate
Parent: HealthKitObservation
Id: healthkit-peak-expiratory-flow-rate
Title: "Peak Expiratory Flow Rate"
Description: "The maximum expiratory gas flow generated during a forceful exhalation, captured as a point result and normalized to UCUM litres per minute. The method-agnostic LOINC concept is chosen because HealthKit does not constrain the measuring device."
* code = $loinc#33452-4
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #L/min (exactly)

Profile: HealthkitPeripheralPerfusionIndex
Parent: HealthKitObservation
Id: healthkit-peripheral-perfusion-index
Title: "Peripheral Perfusion Index"
Description: "The pulse-oximetry perfusion index — the ratio of pulsatile to non-pulsatile blood flow at the sensor site — normalized to UCUM percent. Only HealthKit evidences it, so it stays in the HealthKit adapter guide."
* code = $loinc#61006-3
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)

Profile: HealthkitPhq9Assessment
Parent: HealthKitObservation
Id: healthkit-phq9-assessment
Title: "Grove HealthKit PHQ-9 Score"
Description: "HKPHQ9Assessment (iOS 18, HKScoredAssessment subclass): score 0-27, answers [HKPHQ9Assessment.Answer] including preferNotToAnswer, risk. Routing recommendation: platform-exclusive score Observation on exact LOINC 44261-6 'Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]' (re-verified ACTIVE, Score, Qn); item answers retained as components under panel 44249-1 'PHQ-9 quick depression assessment panel [Reported.PHQ]' (re-verified) with the standard LA answer codes; preferNotToAnswer maps to a component with dataAbsentReason asked-declined, which is the semantically exact FHIR mechanism; Risk (noneToMinimal, mild, moderate, moderatelySevere, severe — re-verified) carried as interpretation-style Grove coding only."
* code = $loinc#44261-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{score} (exactly)

Profile: HealthkitPhysicalEffort
Parent: HealthKitObservation
Id: healthkit-physical-effort
Title: "Physical Effort"
Description: "The estimated intensity of physical exertion over an exact effective Period, normalized to UCUM kilocalories per kilogram per hour as sourced from Apple's physicalEffort samples. It is an energy-normalized intensity rate, deliberately not converted to the oxygen-based UCUM [MET]."
* code = HealthKitMeasurementCS#physical-effort
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal/kg/h (exactly)

Profile: HealthkitPregnancyStatus
Parent: HealthKitObservation
Id: healthkit-pregnancy-status
Title: "Pregnancy Status"
Description: "HKCategoryTypeIdentifierPregnancy: an interval flag (notApplicable value) asserting pregnancy over the sample period. Emitted as a coded Observation under LOINC 82810-3 Pregnancy status (Find/Nom, ACTIVE) with the fixed Grove result pregnant over the exact effective Period."
* code = $loinc#82810-3
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitPregnancyStatusVS (required)

Profile: HealthkitPregnancyTestResult
Parent: HealthKitObservation
Id: healthkit-pregnancy-test-result
Title: "Pregnancy Test Result"
Description: "HKCategoryTypeIdentifierPregnancyTestResult: the result of a home urine hCG pregnancy test. Apple documentation states these tests check for hCG in a urine sample, so LOINC 2106-3 (Choriogonadotropin [Presence] in Urine, PrThr/Ord, ACTIVE) is semantically exact."
* code = $loinc#2106-3
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitPregnancyTestResultVS (required)

Profile: HealthkitProgesteroneTestResult
Parent: HealthKitObservation
Id: healthkit-progesterone-test-result
Title: "Progesterone Test Result"
Description: "HKCategoryTypeIdentifierProgesteroneTestResult: the result of a home urine test for pregnanediol-3-glucuronide (PdG) confirming ovulation, per Apple documentation. Qualitative positive/negative/indeterminate result."
* code = HealthKitMeasurementCS#progesterone-test-result
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitProgesteroneTestResultVS (required)

Profile: HealthkitRunningGroundContactTime
Parent: HealthKitObservation
Id: healthkit-running-ground-contact-time
Title: "Running Ground Contact Time"
Description: "The time the foot is in contact with the ground per running stride, normalized to UCUM milliseconds. A per-sample running dynamics metric recorded during workouts."
* code = HealthKitMeasurementCS#running-ground-contact-time
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #ms (exactly)

Profile: HealthkitRunningStrideLength
Parent: HealthKitObservation
Id: healthkit-running-stride-length
Title: "Running Stride Length"
Description: "The distance covered by one running stride, normalized to UCUM metres. A per-sample running dynamics metric recorded during workouts."
* code = HealthKitMeasurementCS#running-stride-length
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: HealthkitRunningVerticalOscillation
Parent: HealthKitObservation
Id: healthkit-running-vertical-oscillation
Title: "Running Vertical Oscillation"
Description: "The vertical bounce of the torso per running stride, normalized to UCUM centimetres. A per-sample running dynamics metric recorded during workouts."
* code = HealthKitMeasurementCS#running-vertical-oscillation
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #cm (exactly)

Profile: HealthkitSixMinuteWalkTestDistance
Parent: HealthKitObservation
Id: healthkit-six-minute-walk-test-distance
Title: "Six-Minute Walk Test Distance"
Description: "The distance walked (or estimated walkable) in six minutes, using LOINC Six minute walk test and normalized to UCUM metres. Apple's samples are predominantly rolling-window mobility estimates rather than administered tests, so the phase-2 aggregate design owns the emission contract."
* code = $loinc#64098-7
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#rolling-mean "Rolling mean"
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: HealthkitSleepingBreathingDisturbances
Parent: HealthKitObservation
Id: healthkit-sleeping-breathing-disturbances
Title: "Sleeping Breathing Disturbances"
Description: "A nightly windowed aggregate of accelerometry-detected breathing disturbances during sleep, expressed as disturbance events per hour of sleep over the night's effective Period. It is a proprietary screening metric and is deliberately not coded as a clinical respiratory disturbance or apnea-hypopnea index."
* code = HealthKitMeasurementCS#sleeping-breathing-disturbances
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#session-rate "Session rate"
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/h (exactly)

Profile: HealthkitStairAscentSpeed
Parent: HealthKitObservation
Id: healthkit-stair-ascent-speed
Title: "Stair Ascent Speed"
Description: "The vertical speed at which the subject climbs stairs, recorded passively by HealthKit and normalized to UCUM metres per second. It is distinct from the shared exercise speed measurement because the stair-climbing binding is part of the concept."
* code = $loinc#112431-2
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m/s (exactly)

Profile: HealthkitStairDescentSpeed
Parent: HealthKitObservation
Id: healthkit-stair-descent-speed
Title: "Stair Descent Speed"
Description: "The vertical speed at which the subject descends stairs, recorded passively by HealthKit and normalized to UCUM metres per second. It is distinct from the shared exercise speed measurement because the stair-descent binding is part of the concept."
* code = $loinc#112430-4
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m/s (exactly)

Profile: HealthkitSwimmingStrokeCount
Parent: HealthKitObservation
Id: healthkit-swimming-stroke-count
Title: "Swimming Stroke Count"
Description: "The number of swimming strokes recorded during an exact effective Period, normalized to the UCUM annotation {strokes}."
* code = HealthKitMeasurementCS#swimming-stroke-count
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{strokes} (exactly)

Profile: HealthkitSymptomAbdominalCramps
Parent: HealthKitObservation
Id: healthkit-symptom-abdominal-cramps
Title: "Symptom: Abdominal Cramps"
Description: "User-logged abdominal cramps with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-abdominal-cramps
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomAcne
Parent: HealthKitObservation
Id: healthkit-symptom-acne
Title: "Symptom: Acne"
Description: "User-logged acne with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-acne
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomAppetiteChanges
Parent: HealthKitObservation
Id: healthkit-symptom-appetite-changes
Title: "Symptom: Appetite Changes"
Description: "User-logged change in appetite. Uses its own Grove appetite-change value set, not the severity set: HealthKit types this with HKCategoryValueAppetiteChanges (direction of change), not HKCategoryValueSeverity."
* code = HealthKitMeasurementCS#symptom-appetite-changes
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitSymptomAppetiteChangesVS (required)

Profile: HealthkitSymptomBloating
Parent: HealthKitObservation
Id: healthkit-symptom-bloating
Title: "Symptom: Bloating"
Description: "User-logged abdominal bloating with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-bloating
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomBreastPain
Parent: HealthKitObservation
Id: healthkit-symptom-breast-pain
Title: "Symptom: Breast Pain"
Description: "User-logged breast pain with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-breast-pain
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomChestTightnessOrPain
Parent: HealthKitObservation
Id: healthkit-symptom-chest-tightness-or-pain
Title: "Symptom: Chest Tightness or Pain"
Description: "User-logged chest tightness or pain with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-chest-tightness-or-pain
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomChills
Parent: HealthKitObservation
Id: healthkit-symptom-chills
Title: "Symptom: Chills"
Description: "User-logged chills with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-chills
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomConstipation
Parent: HealthKitObservation
Id: healthkit-symptom-constipation
Title: "Symptom: Constipation"
Description: "User-logged constipation with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-constipation
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomCoughing
Parent: HealthKitObservation
Id: healthkit-symptom-coughing
Title: "Symptom: Coughing"
Description: "User-logged coughing with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-coughing
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomDiarrhea
Parent: HealthKitObservation
Id: healthkit-symptom-diarrhea
Title: "Symptom: Diarrhea"
Description: "User-logged diarrhea with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-diarrhea
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomDizziness
Parent: HealthKitObservation
Id: healthkit-symptom-dizziness
Title: "Symptom: Dizziness"
Description: "User-logged dizziness with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-dizziness
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomDrySkin
Parent: HealthKitObservation
Id: healthkit-symptom-dry-skin
Title: "Symptom: Dry Skin"
Description: "User-logged dry skin with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-dry-skin
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomFainting
Parent: HealthKitObservation
Id: healthkit-symptom-fainting
Title: "Symptom: Fainting"
Description: "User-logged fainting (syncope) with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-fainting
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomFatigue
Parent: HealthKitObservation
Id: healthkit-symptom-fatigue
Title: "Symptom: Fatigue"
Description: "User-logged fatigue with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-fatigue
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomFever
Parent: HealthKitObservation
Id: healthkit-symptom-fever
Title: "Symptom: Fever"
Description: "User-logged fever with an ordinal severity grade from the shared Grove symptom-severity value set. This is symptom self-report, not a body-temperature quantity; measured temperature stays a separate measurement."
* code = HealthKitMeasurementCS#symptom-fever
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomGeneralizedBodyAche
Parent: HealthKitObservation
Id: healthkit-symptom-generalized-body-ache
Title: "Symptom: Generalized Body Ache"
Description: "User-logged generalized body ache with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-generalized-body-ache
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomHairLoss
Parent: HealthKitObservation
Id: healthkit-symptom-hair-loss
Title: "Symptom: Hair Loss"
Description: "User-logged hair loss with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-hair-loss
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomHeadache
Parent: HealthKitObservation
Id: healthkit-symptom-headache
Title: "Symptom: Headache"
Description: "User-logged headache with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-headache
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomHeartburn
Parent: HealthKitObservation
Id: healthkit-symptom-heartburn
Title: "Symptom: Heartburn"
Description: "User-logged heartburn with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-heartburn
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomHotFlashes
Parent: HealthKitObservation
Id: healthkit-symptom-hot-flashes
Title: "Symptom: Hot Flashes"
Description: "User-logged hot flashes with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-hot-flashes
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomLossOfSmell
Parent: HealthKitObservation
Id: healthkit-symptom-loss-of-smell
Title: "Symptom: Loss of Smell"
Description: "User-logged loss of smell with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-loss-of-smell
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomLossOfTaste
Parent: HealthKitObservation
Id: healthkit-symptom-loss-of-taste
Title: "Symptom: Loss of Taste"
Description: "User-logged loss of taste with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-loss-of-taste
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomLowerBackPain
Parent: HealthKitObservation
Id: healthkit-symptom-lower-back-pain
Title: "Symptom: Lower Back Pain"
Description: "User-logged lower back pain with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-lower-back-pain
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomMemoryLapse
Parent: HealthKitObservation
Id: healthkit-symptom-memory-lapse
Title: "Symptom: Memory Lapse"
Description: "User-logged memory lapse with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-memory-lapse
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomMoodChanges
Parent: HealthKitObservation
Id: healthkit-symptom-mood-changes
Title: "Symptom: Mood Changes"
Description: "User-logged mood changes recorded as presence only. HealthKit types this with HKCategoryValuePresence, so it binds the two-code presence subset of the Grove symptom value set, not the severity grades."
* code = HealthKitMeasurementCS#symptom-mood-changes
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomPresenceVS (required)

Profile: HealthkitSymptomNausea
Parent: HealthKitObservation
Id: healthkit-symptom-nausea
Title: "Symptom: Nausea"
Description: "User-logged nausea with an ordinal severity grade from the shared Grove symptom-severity value set. Coded with exact LOINC 81660-3 Nausea [Presence], the one generic, non-instrument LOINC symptom code found for this family."
* code = $loinc#81660-3
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomNightSweats
Parent: HealthKitObservation
Id: healthkit-symptom-night-sweats
Title: "Symptom: Night Sweats"
Description: "User-logged night sweats with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-night-sweats
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomPelvicPain
Parent: HealthKitObservation
Id: healthkit-symptom-pelvic-pain
Title: "Symptom: Pelvic Pain"
Description: "User-logged pelvic pain with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-pelvic-pain
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomRapidPoundingOrFlutteringHeartbeat
Parent: HealthKitObservation
Id: healthkit-symptom-rapid-pounding-or-fluttering-heartbeat
Title: "Symptom: Rapid, Pounding, or Fluttering Heartbeat"
Description: "User-logged palpitations (rapid, pounding, or fluttering heartbeat) with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-rapid-pounding-or-fluttering-heartbeat
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomRunnyNose
Parent: HealthKitObservation
Id: healthkit-symptom-runny-nose
Title: "Symptom: Runny Nose"
Description: "User-logged runny nose with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-runny-nose
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomShortnessOfBreath
Parent: HealthKitObservation
Id: healthkit-symptom-shortness-of-breath
Title: "Symptom: Shortness of Breath"
Description: "User-logged shortness of breath with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-shortness-of-breath
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomSinusCongestion
Parent: HealthKitObservation
Id: healthkit-symptom-sinus-congestion
Title: "Symptom: Sinus Congestion"
Description: "User-logged sinus congestion with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-sinus-congestion
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomSkippedHeartbeat
Parent: HealthKitObservation
Id: healthkit-symptom-skipped-heartbeat
Title: "Symptom: Skipped Heartbeat"
Description: "User-logged skipped heartbeat with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-skipped-heartbeat
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomSleepChanges
Parent: HealthKitObservation
Id: healthkit-symptom-sleep-changes
Title: "Symptom: Sleep Changes"
Description: "User-logged sleep changes recorded as presence only. HealthKit types this with HKCategoryValuePresence, so it binds the two-code presence subset of the Grove symptom value set, not the severity grades."
* code = HealthKitMeasurementCS#symptom-sleep-changes
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomPresenceVS (required)

Profile: HealthkitSymptomSoreThroat
Parent: HealthKitObservation
Id: healthkit-symptom-sore-throat
Title: "Symptom: Sore Throat"
Description: "User-logged sore throat with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-sore-throat
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomVomiting
Parent: HealthKitObservation
Id: healthkit-symptom-vomiting
Title: "Symptom: Vomiting"
Description: "User-logged vomiting with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-vomiting
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitSymptomWheezing
Parent: HealthKitObservation
Id: healthkit-symptom-wheezing
Title: "Symptom: Wheezing"
Description: "User-logged wheezing with an ordinal severity grade from the shared Grove symptom-severity value set."
* code = HealthKitMeasurementCS#symptom-wheezing
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitTimeInDaylight
Parent: HealthKitObservation
Id: healthkit-time-in-daylight
Title: "Time in Daylight"
Description: "The total time the user spent in daylight during an exact effective Period, normalized to UCUM minutes. Only HealthKit evidences this concept."
* code = HealthKitMeasurementCS#time-in-daylight
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #min (exactly)

Profile: HealthkitToothbrushingSession
Parent: HealthKitObservation
Id: healthkit-toothbrushing-session
Title: "Toothbrushing Session"
Description: "HKCategoryTypeIdentifierToothbrushingEvent: an interval sample (notApplicable value) whose start/end dates carry the toothbrushing duration. Emitted as a duration quantity over the exact Period."
* code = HealthKitMeasurementCS#toothbrushing-session
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #s (exactly)

Profile: HealthkitUnderwaterDepth
Parent: HealthKitObservation
Id: healthkit-underwater-depth
Title: "Underwater Depth"
Description: "A HealthKit-exclusive measurement of the wearer's depth below the water surface during a submersion, normalized to UCUM metres. It is an environmental position reading exclusive to Apple Watch Ultra submersions."
* code = HealthKitMeasurementCS#underwater-depth
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: HealthkitUvExposure
Parent: HealthKitObservation
Id: healthkit-uv-exposure
Title: "UV Exposure"
Description: "The dimensionless Global Solar UV Index the user was exposed to during an exact effective Period. Only HealthKit evidences this concept, and values are typically app-contributed rather than sensor-derived."
* code = HealthKitMeasurementCS#uv-exposure
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{uvindex} (exactly)

Profile: HealthkitVaginalDryness
Parent: HealthKitObservation
Id: healthkit-vaginal-dryness
Title: "Vaginal Dryness"
Description: "HKCategoryTypeIdentifierVaginalDryness: records vaginal dryness as a symptom using HKCategoryValueSeverity (verified cases: unspecified, notPresent, mild, moderate, severe)."
* code = HealthKitMeasurementCS#vaginal-dryness
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSymptomSeverityVS (required)

Profile: HealthkitWaistCircumference
Parent: HealthKitObservation
Id: healthkit-waist-circumference
Title: "Waist Circumference"
Description: "A HealthKit-exclusive waist circumference normalized to UCUM centimetres. The LOINC code asserts the umbilicus site and tape-measure method that HealthKit does not itself state; this is the established consumer-health interoperability mapping and the caveat is documented rather than inventing a Grove code."
* code = $loinc#8280-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #cm (exactly)

Profile: HealthkitWalkingAsymmetry
Parent: HealthKitObservation
Id: healthkit-walking-asymmetry
Title: "Walking Asymmetry"
Description: "The percentage of walking time in which the step timing of one foot differs from the other, recorded passively by HealthKit and normalized to UCUM percent. Higher values indicate a less even gait."
* code = $loinc#112432-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)

Profile: HealthkitWalkingDoubleSupport
Parent: HealthKitObservation
Id: healthkit-walking-double-support
Title: "Walking Double Support"
Description: "The percentage of walking time in which both feet are in contact with the ground, recorded passively by HealthKit and normalized to UCUM percent."
* code = $loinc#112434-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)

Profile: HealthkitWalkingHeartRateAverage
Parent: HealthKitObservation
Id: healthkit-walking-heart-rate-average
Title: "Walking Heart Rate Average"
Description: "The average heart rate during walking activity over a daily window, normalized to UCUM beats per minute. HealthKit-only evidence today; the phase-2 aggregate design implements the windowing."
* code = HealthKitMeasurementCS#walking-heart-rate-average
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#daily-mean "Daily mean"
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #/min (exactly)

Profile: HealthkitWalkingSpeed
Parent: HealthKitObservation
Id: healthkit-walking-speed
Title: "Walking Speed"
Description: "The instantaneous-to-short-bout walking speed HealthKit records passively as a mobility metric, normalized to UCUM metres per second. It is distinct from the shared exercise speed measurement: the walking binding is part of the concept, and it is a gait-health signal rather than a workout series."
* code = HealthKitMeasurementCS#walking-speed
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m/s (exactly)

Profile: HealthkitWalkingSteadiness
Parent: HealthKitObservation
Id: healthkit-walking-steadiness
Title: "Walking Steadiness"
Description: "Apple's windowed walking-steadiness score, a rolling multi-day percentage summarizing gait stability, normalized to UCUM percent over the exact aggregation Period. As a windowed aggregate it is implemented by the phase-2 aggregate design rather than as a point measurement."
* code = HealthKitMeasurementCS#walking-steadiness
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#rolling-mean "Rolling mean"
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)

Profile: HealthkitWalkingStepLength
Parent: HealthKitObservation
Id: healthkit-walking-step-length
Title: "Walking Step Length"
Description: "The average length of a single step during ordinary walking, recorded passively by HealthKit and normalized to UCUM centimetres."
* code = HealthKitMeasurementCS#walking-step-length
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #cm (exactly)

Profile: HealthkitWaterTemperature
Parent: HealthKitObservation
Id: healthkit-water-temperature
Title: "Water Temperature"
Description: "A HealthKit-exclusive environmental measurement of the water temperature surrounding the wearer during a water activity, normalized to UCUM degrees Celsius. It is an environmental context reading, not a body measurement, and is never mapped to any body-temperature concept."
* code = HealthKitMeasurementCS#water-temperature
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #Cel (exactly)

Profile: HealthkitWheelchairUse
Parent: HealthKitObservation
Id: healthkit-wheelchair-use
Title: "Grove HealthKit Wheelchair Use"
Description: "Wheelchair-use status as a coded Observation. No context-free ACTIVE LOINC exists: 89411-3 'Does the patient use a wheelchair/scooter' is Deprecated, and its ACTIVE successor 95738-1 'Does the patient use a wheelchair/scooter during assessment period [CMS Assessment]' is bound to a CMS assessment-period context and method, which the HealthKit characteristic does not carry — adopting it would fabricate an assessment context. Observation.code is therefore Grove-coded. The status materially changes interpretation of HK distanceWheelchair and pushCount data, which is why platform-exclusive support is defensible rather than intentionally-unsupported."
* code = HealthKitMeasurementCS#wheelchair-use
* code from HealthKitMeasurementVS (required)
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitWheelchairUseVS (required)

Profile: HealthkitWorkoutEffortScore
Parent: HealthKitObservation
Id: healthkit-workout-effort-score
Title: "Workout Effort Score"
Description: "Apple's 1-10 workout effort rating over the associated workout's exact effective Period, covering both the user-entered WorkoutEffortScore and the system-computed EstimatedWorkoutEffortScore; the rating method (user-entered versus estimated) is a required adapter distinction. The value is normalized to the UCUM annotation {score}."
* code = HealthKitMeasurementCS#workout-effort-score
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{score} (exactly)
