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
Description: "Measurement concepts defined by the HealthKit adapter for platform-specific results for which no established code is sufficiently precise."
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
* #environmental-audio-exposure-notification "Environmental Audio Exposure Notification" "A device notification that environmental sound reached the momentary exposure limit."
* #environmental-sound-reduction "Environmental sound reduction" "The difference in equivalent continuous sound pressure level attenuated by the user's noise-reducing headphones during the exact Observation effective Period."
* #food-correlation "Food correlation" "One eating occasion grouping the nutrient results recorded for it."
* #handwashing-session "Handwashing session" "The duration of one handwashing event during the exact Observation effective Period."
* #headphone-audio-exposure "Headphone audio exposure" "The A-weighted equivalent continuous sound pressure level of headphone audio the user was exposed to during the exact Observation effective Period."
* #headphone-audio-exposure-notification "Headphone Audio Exposure Notification" "A device notification that headphone audio exposure reached the seven-day limit."
* #heart-rate-recovery-one-minute "Heart rate recovery one minute" "The decrease in heart rate, in beats per minute, from peak exercise to one minute after the end of exercise."
* #high-heart-rate-notification "High Heart Rate Notification" "A device notification that heart rate stayed above the wearer's configured threshold while apparently inactive."
* #hypertension-notification "Hypertension Notification" "A device notification of blood-pressure readings consistent with hypertension."
* #infrequent-menstrual-cycles "Infrequent menstrual cycles" "Cycles occurring less often than expected, derived from the participant's logged cycle records. Corresponds to SNOMED CT 52073004 (Oligomenorrhea); the concept is cited rather than bound, because this guide carries no SNOMED dependency."
* #inhaler-usage "Inhaler usage" "The total number of inhaler puffs the user took during the exact Observation effective Period."
* #insulin-delivery "Insulin delivery" "The amount of insulin delivered during the exact Observation effective Period, qualified by a required basal or bolus delivery reason."
* #irregular-heart-rhythm-notification "Irregular Heart Rhythm Notification" "A device notification of a heart rhythm irregularity consistent with atrial fibrillation."
* #irregular-menstrual-cycles "Irregular menstrual cycles" "Cycle lengths outside the expected range, derived from the participant's logged cycle records. Corresponds to SNOMED CT 80182007 (Irregular periods); the concept is cited rather than bound, because this guide carries no SNOMED dependency."
* #low-cardio-fitness-notification "Low Cardio Fitness Notification" "A device notification that estimated cardio fitness fell below the configured threshold."
* #low-heart-rate-notification "Low Heart Rate Notification" "A device notification that heart rate stayed below the wearer's configured threshold while apparently inactive."
* #number-of-alcoholic-beverages "Number of alcoholic beverages" "The number of standard alcoholic drinks attributed to the exact Observation effective Period."
* #number-of-times-fallen "Number of times fallen" "The total number of falls attributed to the exact Observation effective Period."
* #persistent-intermenstrual-bleeding "Persistent intermenstrual bleeding" "Bleeding between periods persisting across cycles, derived from logged cycle records."
* #physical-effort "Physical effort" "Estimated exertion intensity, in energy per body mass per time, over the exact Observation effective Period."
* #progesterone-test-result "Progesterone (PdG) test result" "Qualitative result of a home urine pregnanediol-3-glucuronide test."
* #prolonged-menstrual-periods "Prolonged menstrual periods" "Periods lasting longer than expected, derived from logged cycle records."
* #running-ground-contact-time "Running ground contact time" "The ground contact time of one running stride at the sample instant."
* #running-stride-length "Running stride length" "The distance covered by one running stride at the sample instant."
* #running-vertical-oscillation "Running vertical oscillation" "The vertical oscillation of the torso during running at the sample instant."
* #sleep-apnea-notification "Sleep Apnea Notification" "A device notification of breathing disturbances consistent with sleep apnea."
* #sleeping-breathing-disturbances "Sleeping breathing disturbances" "The number of accelerometer-detected breathing disturbance events per hour of sleep during the exact nightly Observation effective Period."
* #state-of-mind "State of mind" "A self-reported reflection on felt experience, valenced from unpleasant to pleasant."
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
* #walking-steadiness-notification "Walking Steadiness Notification" "A device notification that walking steadiness reached a low or very low classification."
* #walking-step-length "Walking step length" "The distance covered by a single step during ordinary walking, as sampled by the source."
* #water-temperature "Water temperature" "The temperature of the water surrounding the wearer during a water activity, as sampled by the device."
* #wheelchair-use "Wheelchair use" "Whether the subject uses a wheelchair, as recorded in the HealthKit wheelchair-use characteristic."
* #workout-effort-score "Workout effort score" "An Apple-proprietary 1-10 rating of perceived or estimated workout effort for the exact associated workout Period."
* #high-heart-rate-threshold "Notification threshold" "The wearer-configured heart rate above which the device raises this notification."
* #low-cardio-fitness-threshold "Notification threshold" "The cardio fitness estimate below which the device raises this notification."
* #low-heart-rate-threshold "Notification threshold" "The wearer-configured heart rate below which the device raises this notification."
* #kind "Reflection kind" "HKStateOfMind.Kind: whether the reflection describes a momentary feeling or a longer period."
* #valence-classification "Valence classification" "HKStateOfMind.ValenceClassification: the coarse band the reported valence falls in."
* #state-of-mind-label "Label" "HKStateOfMind.Label: a word the participant chose for the feeling. Repeats once per chosen label."
* #state-of-mind-association "Association" "HKStateOfMind.Association: a life area the participant attributed the feeling to. Repeats once per association."
* #walking-steadiness-notification-occurrence "Notification occurrence" "Whether this is the first notification at the classification or a repeat."

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

CodeSystem: HealthkitBiologicalSexCS
Id: healthkit-biological-sex
Title: "Grove HealthKit Biological Sex Result"
Description: "The closed result codes of the Grove HealthKit Biological Sex measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #female "Female" "HKBiologicalSex female."
* #male "Male" "HKBiologicalSex male."
* #other "Other" "HKBiologicalSex other."

ValueSet: HealthkitBiologicalSexVS
Id: healthkit-biological-sex
Title: "Grove HealthKit Biological Sex Result"
Description: "Every admitted result code of the Grove HealthKit Biological Sex measurement."
* ^experimental = false
* include codes from system HealthkitBiologicalSexCS

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

CodeSystem: HealthkitEnvironmentalAudioExposureNotificationCS
Id: healthkit-environmental-audio-exposure-notification
Title: "Environmental Audio Exposure Notification Result"
Description: "The closed result codes of the Environmental Audio Exposure Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #momentary-limit "Momentary limit" "HKCategoryValueEnvironmentalAudioExposureEvent.momentaryLimit: the momentary exposure limit was reached."

ValueSet: HealthkitEnvironmentalAudioExposureNotificationVS
Id: healthkit-environmental-audio-exposure-notification
Title: "Environmental Audio Exposure Notification Result"
Description: "Every admitted result code of the Environmental Audio Exposure Notification measurement."
* ^experimental = false
* include codes from system HealthkitEnvironmentalAudioExposureNotificationCS

CodeSystem: HealthkitFitzpatrickSkinTypeCS
Id: healthkit-fitzpatrick-skin-type
Title: "Grove HealthKit Fitzpatrick Skin Type Result"
Description: "The closed result codes of the Grove HealthKit Fitzpatrick Skin Type measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #type-i "Type I" "Always burns, never tans."
* #type-ii "Type II" "Usually burns, tans minimally."
* #type-iii "Type III" "Sometimes burns mildly, tans uniformly."
* #type-iv "Type IV" "Burns minimally, always tans well."
* #type-v "Type V" "Very rarely burns, tans very easily."
* #type-vi "Type VI" "Never burns, deeply pigmented."

ValueSet: HealthkitFitzpatrickSkinTypeVS
Id: healthkit-fitzpatrick-skin-type
Title: "Grove HealthKit Fitzpatrick Skin Type Result"
Description: "Every admitted result code of the Grove HealthKit Fitzpatrick Skin Type measurement."
* ^experimental = false
* include codes from system HealthkitFitzpatrickSkinTypeCS

CodeSystem: HealthkitHeadphoneAudioExposureNotificationCS
Id: healthkit-headphone-audio-exposure-notification
Title: "Headphone Audio Exposure Notification Result"
Description: "The closed result codes of the Headphone Audio Exposure Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #seven-day-limit "Seven day limit" "HKCategoryValueHeadphoneAudioExposureEvent.sevenDayLimit: the rolling seven-day exposure limit was reached."

ValueSet: HealthkitHeadphoneAudioExposureNotificationVS
Id: healthkit-headphone-audio-exposure-notification
Title: "Headphone Audio Exposure Notification Result"
Description: "Every admitted result code of the Headphone Audio Exposure Notification measurement."
* ^experimental = false
* include codes from system HealthkitHeadphoneAudioExposureNotificationCS

CodeSystem: HealthkitHighHeartRateNotificationCS
Id: healthkit-high-heart-rate-notification
Title: "High Heart Rate Notification Result"
Description: "The closed result codes of the High Heart Rate Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #occurred "Occurred" "The device raised this notification over the stated Period. HealthKit carries no further value for it."

ValueSet: HealthkitHighHeartRateNotificationVS
Id: healthkit-high-heart-rate-notification
Title: "High Heart Rate Notification Result"
Description: "Every admitted result code of the High Heart Rate Notification measurement."
* ^experimental = false
* include codes from system HealthkitHighHeartRateNotificationCS

CodeSystem: HealthkitHypertensionNotificationCS
Id: healthkit-hypertension-notification
Title: "Hypertension Notification Result"
Description: "The closed result codes of the Hypertension Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #occurred "Occurred" "The device raised this notification over the stated Period. HealthKit carries no further value for it."

ValueSet: HealthkitHypertensionNotificationVS
Id: healthkit-hypertension-notification
Title: "Hypertension Notification Result"
Description: "Every admitted result code of the Hypertension Notification measurement."
* ^experimental = false
* include codes from system HealthkitHypertensionNotificationCS

CodeSystem: HealthkitInfrequentMenstrualCyclesCS
Id: healthkit-infrequent-menstrual-cycles
Title: "Infrequent Menstrual Cycles Result"
Description: "The closed result codes of the Infrequent Menstrual Cycles measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #present "Present" "The pattern was detected over the stated Period from the wearer's own logged cycle records."
* #not-present "Not present" "The pattern was evaluated over the stated Period and not detected."

ValueSet: HealthkitInfrequentMenstrualCyclesVS
Id: healthkit-infrequent-menstrual-cycles
Title: "Infrequent Menstrual Cycles Result"
Description: "Every admitted result code of the Infrequent Menstrual Cycles measurement."
* ^experimental = false
* include codes from system HealthkitInfrequentMenstrualCyclesCS

CodeSystem: HealthkitIrregularHeartRhythmNotificationCS
Id: healthkit-irregular-heart-rhythm-notification
Title: "Irregular Heart Rhythm Notification Result"
Description: "The closed result codes of the Irregular Heart Rhythm Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #occurred "Occurred" "The device raised this notification over the stated Period. HealthKit carries no further value for it."

ValueSet: HealthkitIrregularHeartRhythmNotificationVS
Id: healthkit-irregular-heart-rhythm-notification
Title: "Irregular Heart Rhythm Notification Result"
Description: "Every admitted result code of the Irregular Heart Rhythm Notification measurement."
* ^experimental = false
* include codes from system HealthkitIrregularHeartRhythmNotificationCS

CodeSystem: HealthkitIrregularMenstrualCyclesCS
Id: healthkit-irregular-menstrual-cycles
Title: "Irregular Menstrual Cycles Result"
Description: "The closed result codes of the Irregular Menstrual Cycles measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #present "Present" "The pattern was detected over the stated Period from the wearer's own logged cycle records."
* #not-present "Not present" "The pattern was evaluated over the stated Period and not detected."

ValueSet: HealthkitIrregularMenstrualCyclesVS
Id: healthkit-irregular-menstrual-cycles
Title: "Irregular Menstrual Cycles Result"
Description: "Every admitted result code of the Irregular Menstrual Cycles measurement."
* ^experimental = false
* include codes from system HealthkitIrregularMenstrualCyclesCS

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

CodeSystem: HealthkitLowCardioFitnessNotificationCS
Id: healthkit-low-cardio-fitness-notification
Title: "Low Cardio Fitness Notification Result"
Description: "The closed result codes of the Low Cardio Fitness Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #low-fitness "Low fitness" "HKCategoryValueLowCardioFitnessEvent.lowFitness: the cardio fitness estimate is below the threshold."

ValueSet: HealthkitLowCardioFitnessNotificationVS
Id: healthkit-low-cardio-fitness-notification
Title: "Low Cardio Fitness Notification Result"
Description: "Every admitted result code of the Low Cardio Fitness Notification measurement."
* ^experimental = false
* include codes from system HealthkitLowCardioFitnessNotificationCS

CodeSystem: HealthkitLowHeartRateNotificationCS
Id: healthkit-low-heart-rate-notification
Title: "Low Heart Rate Notification Result"
Description: "The closed result codes of the Low Heart Rate Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #occurred "Occurred" "The device raised this notification over the stated Period. HealthKit carries no further value for it."

ValueSet: HealthkitLowHeartRateNotificationVS
Id: healthkit-low-heart-rate-notification
Title: "Low Heart Rate Notification Result"
Description: "Every admitted result code of the Low Heart Rate Notification measurement."
* ^experimental = false
* include codes from system HealthkitLowHeartRateNotificationCS

CodeSystem: HealthkitPersistentIntermenstrualBleedingCS
Id: healthkit-persistent-intermenstrual-bleeding
Title: "Persistent Intermenstrual Bleeding Result"
Description: "The closed result codes of the Persistent Intermenstrual Bleeding measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #present "Present" "The pattern was detected over the stated Period from the wearer's own logged cycle records."
* #not-present "Not present" "The pattern was evaluated over the stated Period and not detected."

ValueSet: HealthkitPersistentIntermenstrualBleedingVS
Id: healthkit-persistent-intermenstrual-bleeding
Title: "Persistent Intermenstrual Bleeding Result"
Description: "Every admitted result code of the Persistent Intermenstrual Bleeding measurement."
* ^experimental = false
* include codes from system HealthkitPersistentIntermenstrualBleedingCS

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

CodeSystem: HealthkitProlongedMenstrualPeriodsCS
Id: healthkit-prolonged-menstrual-periods
Title: "Prolonged Menstrual Periods Result"
Description: "The closed result codes of the Prolonged Menstrual Periods measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #present "Present" "The pattern was detected over the stated Period from the wearer's own logged cycle records."
* #not-present "Not present" "The pattern was evaluated over the stated Period and not detected."

ValueSet: HealthkitProlongedMenstrualPeriodsVS
Id: healthkit-prolonged-menstrual-periods
Title: "Prolonged Menstrual Periods Result"
Description: "Every admitted result code of the Prolonged Menstrual Periods measurement."
* ^experimental = false
* include codes from system HealthkitProlongedMenstrualPeriodsCS

CodeSystem: HealthkitSleepApneaNotificationCS
Id: healthkit-sleep-apnea-notification
Title: "Sleep Apnea Notification Result"
Description: "The closed result codes of the Sleep Apnea Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #occurred "Occurred" "The device raised this notification over the stated Period. HealthKit carries no further value for it."

ValueSet: HealthkitSleepApneaNotificationVS
Id: healthkit-sleep-apnea-notification
Title: "Sleep Apnea Notification Result"
Description: "Every admitted result code of the Sleep Apnea Notification measurement."
* ^experimental = false
* include codes from system HealthkitSleepApneaNotificationCS

CodeSystem: HealthkitStateOfMindKindCS
Id: healthkit-state-of-mind-kind
Title: "Reflection kind Result"
Description: "The closed result codes of the Reflection kind measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #momentary-emotion "Momentary emotion" "HKStateOfMind.Kind.momentaryEmotion: how the participant felt at the moment of reflection."
* #daily-mood "Daily mood" "HKStateOfMind.Kind.dailyMood: how the participant felt over the day."

ValueSet: HealthkitStateOfMindKindVS
Id: healthkit-state-of-mind-kind
Title: "Reflection kind Result"
Description: "Every admitted result code of the Reflection kind measurement."
* ^experimental = false
* include codes from system HealthkitStateOfMindKindCS

CodeSystem: HealthkitStateOfMindValenceClassificationCS
Id: healthkit-state-of-mind-valence-classification
Title: "Valence classification Result"
Description: "The closed result codes of the Valence classification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #very-unpleasant "Very unpleasant" "HKStateOfMind.ValenceClassification.veryUnpleasant."
* #unpleasant "Unpleasant" "HKStateOfMind.ValenceClassification.unpleasant."
* #slightly-unpleasant "Slightly unpleasant" "HKStateOfMind.ValenceClassification.slightlyUnpleasant."
* #neutral "Neutral" "HKStateOfMind.ValenceClassification.neutral."
* #slightly-pleasant "Slightly pleasant" "HKStateOfMind.ValenceClassification.slightlyPleasant."
* #pleasant "Pleasant" "HKStateOfMind.ValenceClassification.pleasant."
* #very-pleasant "Very pleasant" "HKStateOfMind.ValenceClassification.veryPleasant."

ValueSet: HealthkitStateOfMindValenceClassificationVS
Id: healthkit-state-of-mind-valence-classification
Title: "Valence classification Result"
Description: "Every admitted result code of the Valence classification measurement."
* ^experimental = false
* include codes from system HealthkitStateOfMindValenceClassificationCS

CodeSystem: HealthkitStateOfMindLabelCS
Id: healthkit-state-of-mind-label
Title: "Label Result"
Description: "The closed result codes of the Label measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #amazed "Amazed" "HKStateOfMind.Label.amazed."
* #amused "Amused" "HKStateOfMind.Label.amused."
* #angry "Angry" "HKStateOfMind.Label.angry."
* #anxious "Anxious" "HKStateOfMind.Label.anxious."
* #ashamed "Ashamed" "HKStateOfMind.Label.ashamed."
* #brave "Brave" "HKStateOfMind.Label.brave."
* #calm "Calm" "HKStateOfMind.Label.calm."
* #content "Content" "HKStateOfMind.Label.content."
* #disappointed "Disappointed" "HKStateOfMind.Label.disappointed."
* #discouraged "Discouraged" "HKStateOfMind.Label.discouraged."
* #disgusted "Disgusted" "HKStateOfMind.Label.disgusted."
* #embarrassed "Embarrassed" "HKStateOfMind.Label.embarrassed."
* #excited "Excited" "HKStateOfMind.Label.excited."
* #frustrated "Frustrated" "HKStateOfMind.Label.frustrated."
* #grateful "Grateful" "HKStateOfMind.Label.grateful."
* #guilty "Guilty" "HKStateOfMind.Label.guilty."
* #happy "Happy" "HKStateOfMind.Label.happy."
* #hopeless "Hopeless" "HKStateOfMind.Label.hopeless."
* #irritated "Irritated" "HKStateOfMind.Label.irritated."
* #jealous "Jealous" "HKStateOfMind.Label.jealous."
* #joyful "Joyful" "HKStateOfMind.Label.joyful."
* #lonely "Lonely" "HKStateOfMind.Label.lonely."
* #passionate "Passionate" "HKStateOfMind.Label.passionate."
* #peaceful "Peaceful" "HKStateOfMind.Label.peaceful."
* #proud "Proud" "HKStateOfMind.Label.proud."
* #relieved "Relieved" "HKStateOfMind.Label.relieved."
* #sad "Sad" "HKStateOfMind.Label.sad."
* #scared "Scared" "HKStateOfMind.Label.scared."
* #stressed "Stressed" "HKStateOfMind.Label.stressed."
* #surprised "Surprised" "HKStateOfMind.Label.surprised."
* #worried "Worried" "HKStateOfMind.Label.worried."
* #annoyed "Annoyed" "HKStateOfMind.Label.annoyed."
* #confident "Confident" "HKStateOfMind.Label.confident."
* #drained "Drained" "HKStateOfMind.Label.drained."
* #hopeful "Hopeful" "HKStateOfMind.Label.hopeful."
* #indifferent "Indifferent" "HKStateOfMind.Label.indifferent."
* #overwhelmed "Overwhelmed" "HKStateOfMind.Label.overwhelmed."
* #satisfied "Satisfied" "HKStateOfMind.Label.satisfied."

ValueSet: HealthkitStateOfMindLabelVS
Id: healthkit-state-of-mind-label
Title: "Label Result"
Description: "Every admitted result code of the Label measurement."
* ^experimental = false
* include codes from system HealthkitStateOfMindLabelCS

CodeSystem: HealthkitStateOfMindAssociationCS
Id: healthkit-state-of-mind-association
Title: "Association Result"
Description: "The closed result codes of the Association measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #community "Community" "HKStateOfMind.Association.community."
* #current-events "Current events" "HKStateOfMind.Association.currentEvents."
* #dating "Dating" "HKStateOfMind.Association.dating."
* #education "Education" "HKStateOfMind.Association.education."
* #family "Family" "HKStateOfMind.Association.family."
* #fitness "Fitness" "HKStateOfMind.Association.fitness."
* #friends "Friends" "HKStateOfMind.Association.friends."
* #health "Health" "HKStateOfMind.Association.health."
* #hobbies "Hobbies" "HKStateOfMind.Association.hobbies."
* #identity "Identity" "HKStateOfMind.Association.identity."
* #money "Money" "HKStateOfMind.Association.money."
* #partner "Partner" "HKStateOfMind.Association.partner."
* #self-care "Self care" "HKStateOfMind.Association.selfCare."
* #spirituality "Spirituality" "HKStateOfMind.Association.spirituality."
* #tasks "Tasks" "HKStateOfMind.Association.tasks."
* #travel "Travel" "HKStateOfMind.Association.travel."
* #work "Work" "HKStateOfMind.Association.work."
* #weather "Weather" "HKStateOfMind.Association.weather."

ValueSet: HealthkitStateOfMindAssociationVS
Id: healthkit-state-of-mind-association
Title: "Association Result"
Description: "Every admitted result code of the Association measurement."
* ^experimental = false
* include codes from system HealthkitStateOfMindAssociationCS

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

CodeSystem: HealthkitWalkingSteadinessNotificationCS
Id: healthkit-walking-steadiness-notification
Title: "Walking Steadiness Notification Result"
Description: "The closed result codes of the Walking Steadiness Notification measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #low "Low" "HKCategoryValueAppleWalkingSteadinessEvent low classification."
* #very-low "Very low" "HKCategoryValueAppleWalkingSteadinessEvent very low classification."

ValueSet: HealthkitWalkingSteadinessNotificationVS
Id: healthkit-walking-steadiness-notification
Title: "Walking Steadiness Notification Result"
Description: "Every admitted result code of the Walking Steadiness Notification measurement."
* ^experimental = false
* include codes from system HealthkitWalkingSteadinessNotificationCS

CodeSystem: HealthkitNotificationOccurrenceCS
Id: healthkit-notification-occurrence
Title: "Notification occurrence Result"
Description: "The closed result codes of the Notification occurrence measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #initial "Initial" "HKCategoryValueAppleWalkingSteadinessEvent initial notification."
* #repeat "Repeat" "HKCategoryValueAppleWalkingSteadinessEvent repeat notification."

ValueSet: HealthkitNotificationOccurrenceVS
Id: healthkit-notification-occurrence
Title: "Notification occurrence Result"
Description: "Every admitted result code of the Notification occurrence measurement."
* ^experimental = false
* include codes from system HealthkitNotificationOccurrenceCS

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

Invariant: healthkit-atrial-fibrillation-burden-value-domain-1
Description: "A populated Atrial Fibrillation Burden value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: HealthkitAtrialFibrillationBurden
Parent: HealthKitObservation
Id: healthkit-atrial-fibrillation-burden
Title: "Atrial Fibrillation Burden"
Description: "The estimated percentage of analyzed time showing atrial fibrillation over a multi-day estimation window, normalized to UCUM percent. It is a source-supplied windowed estimate whose exact analysis window is carried by effectivePeriod; the Withings AFib classification scalars remain intentionally unsupported and never join it."
* obeys healthkit-atrial-fibrillation-burden-value-domain-1
* code = HealthKitMeasurementCS#atrial-fibrillation-burden
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#percentage-of-time
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)
* valueQuantity.value ^minValueDecimal = 0
* valueQuantity.value ^maxValueDecimal = 100

Profile: HealthkitAudiogramPanel
Parent: HealthKitObservation
Id: healthkit-audiogram-panel
Title: "Audiogram Panel"
Description: "HKAudiogramSample: a hearing test reporting an air conduction threshold per ear at each frequency it measured. The thresholds are parts of one test rather than results that stand alone, so they are components. Every component is optional: a test states the frequencies it measured and no others, and a frequency outside this set is carried by its own component keyed to the frequency rather than forced onto a neighbouring code."
* code = $loinc#89015-2
* effective[x] only dateTime
* value[x] 0..0
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains left-250 0..1 MS and right-250 0..1 MS and left-500 0..1 MS and right-500 0..1 MS and left-750 0..1 MS and right-750 0..1 MS and left-1000 0..1 MS and right-1000 0..1 MS and left-1500 0..1 MS and right-1500 0..1 MS and left-2000 0..1 MS and right-2000 0..1 MS and left-3000 0..1 MS and right-3000 0..1 MS and left-4000 0..1 MS and right-4000 0..1 MS and left-5000 0..1 MS and right-5000 0..1 MS and left-6000 0..1 MS and right-6000 0..1 MS and left-8000 0..1 MS and right-8000 0..1 MS
* component[left-250].code = $loinc#91375-6
* component[left-250].value[x] only Quantity
* component[left-250].valueQuantity.value 1..1 MS
* component[left-250].valueQuantity.system = $ucum (exactly)
* component[left-250].valueQuantity.code = #dB (exactly)
* component[right-250].code = $loinc#91374-9
* component[right-250].value[x] only Quantity
* component[right-250].valueQuantity.value 1..1 MS
* component[right-250].valueQuantity.system = $ucum (exactly)
* component[right-250].valueQuantity.code = #dB (exactly)
* component[left-500].code = $loinc#89024-4
* component[left-500].value[x] only Quantity
* component[left-500].valueQuantity.value 1..1 MS
* component[left-500].valueQuantity.system = $ucum (exactly)
* component[left-500].valueQuantity.code = #dB (exactly)
* component[right-500].code = $loinc#89025-1
* component[right-500].value[x] only Quantity
* component[right-500].valueQuantity.value 1..1 MS
* component[right-500].valueQuantity.system = $ucum (exactly)
* component[right-500].valueQuantity.code = #dB (exactly)
* component[left-750].code = $loinc#91379-8
* component[left-750].value[x] only Quantity
* component[left-750].valueQuantity.value 1..1 MS
* component[left-750].valueQuantity.system = $ucum (exactly)
* component[left-750].valueQuantity.code = #dB (exactly)
* component[right-750].code = $loinc#91378-0
* component[right-750].value[x] only Quantity
* component[right-750].valueQuantity.value 1..1 MS
* component[right-750].valueQuantity.system = $ucum (exactly)
* component[right-750].valueQuantity.code = #dB (exactly)
* component[left-1000].code = $loinc#89016-0
* component[left-1000].value[x] only Quantity
* component[left-1000].valueQuantity.value 1..1 MS
* component[left-1000].valueQuantity.system = $ucum (exactly)
* component[left-1000].valueQuantity.code = #dB (exactly)
* component[right-1000].code = $loinc#89017-8
* component[right-1000].value[x] only Quantity
* component[right-1000].valueQuantity.value 1..1 MS
* component[right-1000].valueQuantity.system = $ucum (exactly)
* component[right-1000].valueQuantity.code = #dB (exactly)
* component[left-1500].code = $loinc#91373-1
* component[left-1500].value[x] only Quantity
* component[left-1500].valueQuantity.value 1..1 MS
* component[left-1500].valueQuantity.system = $ucum (exactly)
* component[left-1500].valueQuantity.code = #dB (exactly)
* component[right-1500].code = $loinc#91372-3
* component[right-1500].value[x] only Quantity
* component[right-1500].valueQuantity.value 1..1 MS
* component[right-1500].valueQuantity.system = $ucum (exactly)
* component[right-1500].valueQuantity.code = #dB (exactly)
* component[left-2000].code = $loinc#89018-6
* component[left-2000].value[x] only Quantity
* component[left-2000].valueQuantity.value 1..1 MS
* component[left-2000].valueQuantity.system = $ucum (exactly)
* component[left-2000].valueQuantity.code = #dB (exactly)
* component[right-2000].code = $loinc#89019-4
* component[right-2000].value[x] only Quantity
* component[right-2000].valueQuantity.value 1..1 MS
* component[right-2000].valueQuantity.system = $ucum (exactly)
* component[right-2000].valueQuantity.code = #dB (exactly)
* component[left-3000].code = $loinc#89020-2
* component[left-3000].value[x] only Quantity
* component[left-3000].valueQuantity.value 1..1 MS
* component[left-3000].valueQuantity.system = $ucum (exactly)
* component[left-3000].valueQuantity.code = #dB (exactly)
* component[right-3000].code = $loinc#89021-0
* component[right-3000].value[x] only Quantity
* component[right-3000].valueQuantity.value 1..1 MS
* component[right-3000].valueQuantity.system = $ucum (exactly)
* component[right-3000].valueQuantity.code = #dB (exactly)
* component[left-4000].code = $loinc#89022-8
* component[left-4000].value[x] only Quantity
* component[left-4000].valueQuantity.value 1..1 MS
* component[left-4000].valueQuantity.system = $ucum (exactly)
* component[left-4000].valueQuantity.code = #dB (exactly)
* component[right-4000].code = $loinc#89023-6
* component[right-4000].value[x] only Quantity
* component[right-4000].valueQuantity.value 1..1 MS
* component[right-4000].valueQuantity.system = $ucum (exactly)
* component[right-4000].valueQuantity.code = #dB (exactly)
* component[left-5000].code = $loinc#91377-2
* component[left-5000].value[x] only Quantity
* component[left-5000].valueQuantity.value 1..1 MS
* component[left-5000].valueQuantity.system = $ucum (exactly)
* component[left-5000].valueQuantity.code = #dB (exactly)
* component[right-5000].code = $loinc#91376-4
* component[right-5000].value[x] only Quantity
* component[right-5000].valueQuantity.value 1..1 MS
* component[right-5000].valueQuantity.system = $ucum (exactly)
* component[right-5000].valueQuantity.code = #dB (exactly)
* component[left-6000].code = $loinc#89026-9
* component[left-6000].value[x] only Quantity
* component[left-6000].valueQuantity.value 1..1 MS
* component[left-6000].valueQuantity.system = $ucum (exactly)
* component[left-6000].valueQuantity.code = #dB (exactly)
* component[right-6000].code = $loinc#89027-7
* component[right-6000].value[x] only Quantity
* component[right-6000].valueQuantity.value 1..1 MS
* component[right-6000].valueQuantity.system = $ucum (exactly)
* component[right-6000].valueQuantity.code = #dB (exactly)
* component[left-8000].code = $loinc#89028-5
* component[left-8000].value[x] only Quantity
* component[left-8000].valueQuantity.value 1..1 MS
* component[left-8000].valueQuantity.system = $ucum (exactly)
* component[left-8000].valueQuantity.code = #dB (exactly)
* component[right-8000].code = $loinc#89029-3
* component[right-8000].value[x] only Quantity
* component[right-8000].valueQuantity.value 1..1 MS
* component[right-8000].valueQuantity.system = $ucum (exactly)
* component[right-8000].valueQuantity.code = #dB (exactly)

Profile: HealthkitBiologicalSex
Parent: HealthKitObservation
Id: healthkit-biological-sex
Title: "Grove HealthKit Biological Sex"
Description: "Biological sex as a coded Observation using LOINC 46098-0 'Sex'. LOINC 76689-9 'Sex assigned at birth' is not used because the HealthKit characteristic states only sex and does not assert birth-assignment provenance. The value uses a Grove code with the exact HKBiologicalSex token retained as secondary coding; HKBiologicalSex.notSet produces no Observation."
* code = $loinc#46098-0
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitBiologicalSexVS (required)

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

Invariant: healthkit-blood-alcohol-content-value-domain-1
Description: "A populated Blood Alcohol Content value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: HealthkitBloodAlcoholContent
Parent: HealthKitObservation
Id: healthkit-blood-alcohol-content
Title: "Blood Alcohol Content"
Description: "Blood alcohol content as the mass-percent concentration figure a breathalyzer or user reports, represented as a UCUM percent scalar. It is not converted into a laboratory ethanol mass concentration."
* obeys healthkit-blood-alcohol-content-value-domain-1
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
* valueQuantity.value ^minValueDecimal = 0
* valueQuantity.value ^maxValueDecimal = 100

Profile: HealthkitBloodType
Parent: HealthKitObservation
Id: healthkit-blood-type
Title: "Grove HealthKit Blood Type"
Description: "ABO and Rh group as a coded Observation using LOINC 882-1 'ABO and Rh group [Type] in Blood'. The value uses a Grove ABO/Rh code with the exact HKBloodType token retained as secondary coding."
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

Profile: HealthkitDateOfBirth
Parent: HealthKitObservation
Id: healthkit-date-of-birth
Title: "Grove HealthKit Date of Birth"
Description: "Date of birth as an Observation using LOINC 21112-8 'Birth date'. A date of birth identifies a person across systems, so the adapter withholds it unless the deployment authorizes disclosure; a deployment that already knows its participant's demographics from enrollment should prefer that authoritative record over this assertion."
* code = $loinc#21112-8
* effective[x] only dateTime
* value[x] only dateTime
* valueDateTime 1..1 MS

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

Profile: HealthkitEnvironmentalAudioExposureNotification
Parent: HealthKitObservation
Id: healthkit-environmental-audio-exposure-notification
Title: "Environmental Audio Exposure Notification"
Description: "HKCategoryTypeIdentifierAudioExposureEvent: raised when environmental sound reaches the momentary limit. The environmental audio exposure quantity remains the measurement surface."
* code = HealthKitMeasurementCS#environmental-audio-exposure-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitEnvironmentalAudioExposureNotificationVS (required)

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

Profile: HealthkitFitzpatrickSkinType
Parent: HealthKitObservation
Id: healthkit-fitzpatrick-skin-type
Title: "Grove HealthKit Fitzpatrick Skin Type"
Description: "Fitzpatrick sun-reactive skin type as a coded Observation using LOINC 66555-4 'Skin type [Fitzpatrick Classification Scale]'. The scale materially conditions UV-exposure interpretation, which is why it is modelled rather than left to the deployment. HKFitzpatrickSkinType.notSet produces no Observation."
* code = $loinc#66555-4
* effective[x] only dateTime
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitFitzpatrickSkinTypeVS (required)

Profile: HealthkitFoodCorrelation
Parent: HealthKitObservation
Id: healthkit-food-correlation
Title: "Food Correlation"
Description: "One eating occasion, whose members are the nutrient Observations recorded for it. The nutrients are independently meaningful and are already modelled one by one, so the occasion groups them rather than restating them as components."
* code = HealthKitMeasurementCS#food-correlation
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] 0..0
* hasMember 1..* MS
* hasMember only Reference(Observation)

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
Description: "A HealthKit GAD-7 assessment represented by its 0-21 total score using LOINC 70274-6 'Generalized anxiety disorder 7 item (GAD-7) total score [Reported.PHQ]'. The seven item answers are retained as components using the standard LOINC GAD-7 item and answer codes under panel 69737-5. HealthKit's risk classification is redundant with the score bands and is retained as a Grove interpretation coding rather than a second result value."
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

Profile: HealthkitHeadphoneAudioExposureNotification
Parent: HealthKitObservation
Id: healthkit-headphone-audio-exposure-notification
Title: "Headphone Audio Exposure Notification"
Description: "HKCategoryTypeIdentifierHeadphoneAudioExposureEvent: raised when headphone exposure reaches the seven-day limit. The headphone audio exposure quantity remains the measurement surface."
* code = HealthKitMeasurementCS#headphone-audio-exposure-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitHeadphoneAudioExposureNotificationVS (required)

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

Profile: HealthkitHighHeartRateNotification
Parent: HealthKitObservation
Id: healthkit-high-heart-rate-notification
Title: "High Heart Rate Notification"
Description: "HKCategoryTypeIdentifierHighHeartRateEvent: an Apple Watch notification raised against a user-configurable threshold. This is the notification, not a rhythm finding; the heart-rate quantities remain the measurement surface, and the threshold that raised it is carried as a component so the notification can be interpreted at all."
* code = HealthKitMeasurementCS#high-heart-rate-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitHighHeartRateNotificationVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains threshold 0..1 MS
* component[threshold].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#high-heart-rate-threshold
* component[threshold].value[x] only Quantity
* component[threshold].valueQuantity.value 1..1 MS
* component[threshold].valueQuantity.system = $ucum (exactly)
* component[threshold].valueQuantity.code = #/min (exactly)

Profile: HealthkitHypertensionNotification
Parent: HealthKitObservation
Id: healthkit-hypertension-notification
Title: "Hypertension Notification"
Description: "HKCategoryTypeIdentifierHypertensionEvent: a proprietary screening notification. Blood pressure remains the measurement surface; this records only that the notification was raised, and never asserts a hypertension diagnosis."
* code = HealthKitMeasurementCS#hypertension-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitHypertensionNotificationVS (required)

Profile: HealthkitInfrequentMenstrualCycles
Parent: HealthKitObservation
Id: healthkit-infrequent-menstrual-cycles
Title: "Infrequent Menstrual Cycles"
Description: "HKCategoryTypeIdentifierInfrequentMenstrualCycles: a deviation derived from the wearer's own logged cycle records over the stated Period."
* code = HealthKitMeasurementCS#infrequent-menstrual-cycles
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitInfrequentMenstrualCyclesVS (required)

Invariant: healthkit-inhaler-usage-value-domain-1
Description: "A populated Inhaler Usage value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: HealthkitInhalerUsage
Parent: HealthKitObservation
Id: healthkit-inhaler-usage
Title: "Inhaler Usage"
Description: "The number of inhaler puffs taken during an exact effective Period. The count is a device-usage total, not a medication-administration record, and only HealthKit evidences it."
* obeys healthkit-inhaler-usage-value-domain-1
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
* valueQuantity.value ^minValueDecimal = 0

Profile: HealthkitInsulinDelivery
Parent: HealthKitObservation
Id: healthkit-insulin-delivery
Title: "Insulin Delivery"
Description: "The quantity of insulin delivered during the exact effective Period, normalized to UCUM international units. A required delivery-reason component distinguishes basal from bolus delivery; a sample without HKMetadataKeyInsulinDeliveryReason fails closed."
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

Profile: HealthkitIrregularHeartRhythmNotification
Parent: HealthKitObservation
Id: healthkit-irregular-heart-rhythm-notification
Title: "Irregular Heart Rhythm Notification"
Description: "HKCategoryTypeIdentifierIrregularHeartRhythmEvent: an FDA-cleared screening notification from a proprietary algorithm. It is emitted as a notification and never as a rhythm finding: the electrocardiogram and the atrial-fibrillation burden percentage remain the rhythm evidence, and this Observation links to them through derivedFrom."
* code = HealthKitMeasurementCS#irregular-heart-rhythm-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitIrregularHeartRhythmNotificationVS (required)

Profile: HealthkitIrregularMenstrualCycles
Parent: HealthKitObservation
Id: healthkit-irregular-menstrual-cycles
Title: "Irregular Menstrual Cycles"
Description: "HKCategoryTypeIdentifierIrregularMenstrualCycles: a deviation derived from the wearer's own logged cycle records over the stated Period. This is a finding, not a device notification: nothing was sensed, and the pattern is computed from data the participant entered."
* code = HealthKitMeasurementCS#irregular-menstrual-cycles
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitIrregularMenstrualCyclesVS (required)

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

Profile: HealthkitLowCardioFitnessNotification
Parent: HealthKitObservation
Id: healthkit-low-cardio-fitness-notification
Title: "Low Cardio Fitness Notification"
Description: "HKCategoryTypeIdentifierLowCardioFitnessEvent: raised when the VO2 max estimate falls below a threshold. The threshold is carried as a component."
* code = HealthKitMeasurementCS#low-cardio-fitness-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitLowCardioFitnessNotificationVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains threshold 0..1 MS
* component[threshold].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#low-cardio-fitness-threshold
* component[threshold].value[x] only Quantity
* component[threshold].valueQuantity.value 1..1 MS
* component[threshold].valueQuantity.system = $ucum (exactly)
* component[threshold].valueQuantity.code = #mL/kg/min (exactly)

Profile: HealthkitLowHeartRateNotification
Parent: HealthKitObservation
Id: healthkit-low-heart-rate-notification
Title: "Low Heart Rate Notification"
Description: "HKCategoryTypeIdentifierLowHeartRateEvent: an Apple Watch notification raised against a user-configurable threshold. The threshold is carried as a component; the heart-rate quantities remain the measurement surface."
* code = HealthKitMeasurementCS#low-heart-rate-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitLowHeartRateNotificationVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains threshold 0..1 MS
* component[threshold].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#low-heart-rate-threshold
* component[threshold].value[x] only Quantity
* component[threshold].valueQuantity.value 1..1 MS
* component[threshold].valueQuantity.system = $ucum (exactly)
* component[threshold].valueQuantity.code = #/min (exactly)

Invariant: healthkit-number-of-alcoholic-beverages-value-domain-1
Description: "A populated Number of Alcoholic Beverages value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: HealthkitNumberOfAlcoholicBeverages
Parent: HealthKitObservation
Id: healthkit-number-of-alcoholic-beverages
Title: "Number of Alcoholic Beverages"
Description: "The count of standard alcoholic drinks consumed during the exact effective Period, using the annotated dimensionless UCUM unit {drinks}. Counting semantics follow the source's standard-drink definition and are not converted to ethanol mass."
* obeys healthkit-number-of-alcoholic-beverages-value-domain-1
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
* valueQuantity.value ^minValueDecimal = 0

Invariant: healthkit-number-of-times-fallen-value-domain-1
Description: "A populated Number of Times Fallen value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: HealthkitNumberOfTimesFallen
Parent: HealthKitObservation
Id: healthkit-number-of-times-fallen
Title: "Number of Times Fallen"
Description: "The number of falls recorded during an exact effective Period, normalized to the UCUM annotation {falls}. This is a device or user-recorded interval count, not a clinical falls-history assessment."
* obeys healthkit-number-of-times-fallen-value-domain-1
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
* valueQuantity.value ^minValueDecimal = 0

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

Invariant: healthkit-peripheral-perfusion-index-value-domain-1
Description: "A populated Peripheral Perfusion Index value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: HealthkitPeripheralPerfusionIndex
Parent: HealthKitObservation
Id: healthkit-peripheral-perfusion-index
Title: "Peripheral Perfusion Index"
Description: "The pulse-oximetry perfusion index — the ratio of pulsatile to non-pulsatile blood flow at the sensor site — normalized to UCUM percent. Only HealthKit evidences it, so it stays in the HealthKit adapter guide."
* obeys healthkit-peripheral-perfusion-index-value-domain-1
* code = $loinc#61006-3
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

Profile: HealthkitPersistentIntermenstrualBleeding
Parent: HealthKitObservation
Id: healthkit-persistent-intermenstrual-bleeding
Title: "Persistent Intermenstrual Bleeding"
Description: "HKCategoryTypeIdentifierPersistentIntermenstrualBleeding: a deviation derived from the wearer's own logged cycle records over the stated Period. No verified SNOMED concept is bound; the adapter code system carries the meaning rather than approximating a clinical concept."
* code = HealthKitMeasurementCS#persistent-intermenstrual-bleeding
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitPersistentIntermenstrualBleedingVS (required)

Profile: HealthkitPhq9Assessment
Parent: HealthKitObservation
Id: healthkit-phq9-assessment
Title: "Grove HealthKit PHQ-9 Score"
Description: "A HealthKit PHQ-9 assessment represented by its 0-27 total score using LOINC 44261-6 'Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]'. Item answers are retained as components under LOINC panel 44249-1 with the standard answer codes; preferNotToAnswer maps to dataAbsentReason asked-declined. HealthKit's risk classification is retained as a Grove interpretation coding rather than a second result value."
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

Profile: HealthkitProlongedMenstrualPeriods
Parent: HealthKitObservation
Id: healthkit-prolonged-menstrual-periods
Title: "Prolonged Menstrual Periods"
Description: "HKCategoryTypeIdentifierProlongedMenstrualPeriods: a deviation derived from the wearer's own logged cycle records over the stated Period. No verified SNOMED concept is bound; the adapter code system carries the meaning rather than approximating a clinical concept."
* code = HealthKitMeasurementCS#prolonged-menstrual-periods
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitProlongedMenstrualPeriodsVS (required)

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
Description: "The distance walked (or estimated walkable) in six minutes, using LOINC Six minute walk test and normalized to UCUM metres. Apple's samples are predominantly rolling-window mobility estimates rather than administered tests, so effectivePeriod carries the exact measurement window."
* code = $loinc#64098-7
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#rolling-mean
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: HealthkitSleepApneaNotification
Parent: HealthKitObservation
Id: healthkit-sleep-apnea-notification
Title: "Sleep Apnea Notification"
Description: "HKCategoryTypeIdentifierSleepApneaEvent: a proprietary screening notification. The sleeping breathing disturbances quantity remains the measurement surface; this records that the notification was raised."
* code = HealthKitMeasurementCS#sleep-apnea-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitSleepApneaNotificationVS (required)

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
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#session-rate
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

Invariant: healthkit-state-of-mind-value-domain-1
Description: "A populated State of Mind value is >= -1, <= 1."
Expression: "value.empty() or (value.ofType(Quantity).value >= -1 and value.ofType(Quantity).value <= 1)"
Severity: #error

Profile: HealthkitStateOfMind
Parent: HealthKitObservation
Id: healthkit-state-of-mind
Title: "State of Mind"
Description: "HKStateOfMind: a self-reported reflection on how the participant felt. Valence is the one numeric axis and carries the Observation value, reported on HealthKit's closed −1.0 to 1.0 scale; the reflection's kind, its classification, and its labels and associations are coded components. Every axis is the participant's own report, not a measurement."
* obeys healthkit-state-of-mind-value-domain-1
* code = HealthKitMeasurementCS#state-of-mind
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #1 (exactly)
* valueQuantity.value ^minValueDecimal = -1
* valueQuantity.value ^maxValueDecimal = 1
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains kind 1..1 MS and valence-classification 0..1 MS and label 0..* MS and association 0..* MS
* component[kind].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#kind
* component[kind].value[x] only CodeableConcept
* component[kind].valueCodeableConcept 1..1 MS
* component[kind].valueCodeableConcept from HealthkitStateOfMindKindVS (required)
* component[valence-classification].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#valence-classification
* component[valence-classification].value[x] only CodeableConcept
* component[valence-classification].valueCodeableConcept MS
* component[valence-classification].valueCodeableConcept from HealthkitStateOfMindValenceClassificationVS (required)
* component[label].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#state-of-mind-label
* component[label].value[x] only CodeableConcept
* component[label].valueCodeableConcept MS
* component[label].valueCodeableConcept from HealthkitStateOfMindLabelVS (required)
* component[association].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#state-of-mind-association
* component[association].value[x] only CodeableConcept
* component[association].valueCodeableConcept MS
* component[association].valueCodeableConcept from HealthkitStateOfMindAssociationVS (required)

Invariant: healthkit-swimming-stroke-count-value-domain-1
Description: "A populated Swimming Stroke Count value is >= 0, an integer."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and (value.ofType(Quantity).value mod 1) = 0)"
Severity: #error

Profile: HealthkitSwimmingStrokeCount
Parent: HealthKitObservation
Id: healthkit-swimming-stroke-count
Title: "Swimming Stroke Count"
Description: "The number of swimming strokes recorded during an exact effective Period, normalized to the UCUM annotation {strokes}."
* obeys healthkit-swimming-stroke-count-value-domain-1
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
* valueQuantity.value ^minValueDecimal = 0

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
Description: "A HealthKit-exclusive waist circumference normalized to UCUM centimetres. The selected LOINC code asserts the umbilicus site and tape-measure method that HealthKit does not itself state; the profile documents that caveat rather than inventing a Grove code."
* code = $loinc#8280-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #cm (exactly)

Invariant: healthkit-walking-asymmetry-value-domain-1
Description: "A populated Walking Asymmetry value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: HealthkitWalkingAsymmetry
Parent: HealthKitObservation
Id: healthkit-walking-asymmetry
Title: "Walking Asymmetry"
Description: "The percentage of walking time in which the step timing of one foot differs from the other, recorded passively by HealthKit and normalized to UCUM percent. Higher values indicate a less even gait."
* obeys healthkit-walking-asymmetry-value-domain-1
* code = $loinc#112432-0
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

Invariant: healthkit-walking-double-support-value-domain-1
Description: "A populated Walking Double Support value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: HealthkitWalkingDoubleSupport
Parent: HealthKitObservation
Id: healthkit-walking-double-support
Title: "Walking Double Support"
Description: "The percentage of walking time in which both feet are in contact with the ground, recorded passively by HealthKit and normalized to UCUM percent."
* obeys healthkit-walking-double-support-value-domain-1
* code = $loinc#112434-6
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

Profile: HealthkitWalkingHeartRateAverage
Parent: HealthKitObservation
Id: healthkit-walking-heart-rate-average
Title: "Walking Heart Rate Average"
Description: "The average heart rate during walking activity over a daily window, normalized to UCUM beats per minute. This is a HealthKit-specific source-supplied aggregate whose exact daily window is carried by effectivePeriod."
* code = HealthKitMeasurementCS#walking-heart-rate-average
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#daily-mean
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

Invariant: healthkit-walking-steadiness-value-domain-1
Description: "A populated Walking Steadiness value is >= 0, <= 100."
Expression: "value.empty() or (value.ofType(Quantity).value >= 0 and value.ofType(Quantity).value <= 100)"
Severity: #error

Profile: HealthkitWalkingSteadiness
Parent: HealthKitObservation
Id: healthkit-walking-steadiness
Title: "Walking Steadiness"
Description: "Apple's windowed walking-steadiness score, a rolling multi-day percentage summarizing gait stability, normalized to UCUM percent over the exact aggregation Period. It is represented as a source-supplied aggregate with an exact effectivePeriod, not as a point measurement."
* obeys healthkit-walking-steadiness-value-domain-1
* code = HealthKitMeasurementCS#walking-steadiness
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* method 1..1 MS
* method = https://grovealliance.org/fhir/mobile/CodeSystem/grove-aggregation-method#rolling-mean
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #% (exactly)
* valueQuantity.value ^minValueDecimal = 0
* valueQuantity.value ^maxValueDecimal = 100

Profile: HealthkitWalkingSteadinessNotification
Parent: HealthKitObservation
Id: healthkit-walking-steadiness-notification
Title: "Walking Steadiness Notification"
Description: "HKCategoryTypeIdentifierAppleWalkingSteadinessEvent: raised when the walking steadiness classification is low or very low, distinguishing a first occurrence from a repeat. The walking steadiness percentage remains the measurement surface."
* code = HealthKitMeasurementCS#walking-steadiness-notification
* code from HealthKitMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from HealthkitWalkingSteadinessNotificationVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains notification-occurrence 1..1 MS
* component[notification-occurrence].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#walking-steadiness-notification-occurrence
* component[notification-occurrence].value[x] only CodeableConcept
* component[notification-occurrence].valueCodeableConcept 1..1 MS
* component[notification-occurrence].valueCodeableConcept from HealthkitNotificationOccurrenceVS (required)

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

Instance: HealthkitAppleExerciseTimeExample
InstanceOf: HealthkitAppleExerciseTime
Usage: #example
Title: "Apple Exercise Time Example"
Description: "A conformant Apple Exercise Time instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Z_bjp9zx4TXdsU37sp06fLJBhwl08on002eP1Hb1EuE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:mqBYiN7MgRepMPyViyRcSUEf3z4S5SohFpX-x3pQA1s"
* status = #final
* code = HealthKitMeasurementCS#apple-exercise-time
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierAppleExerciseTime
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 32 'min'

Instance: HealthkitAppleMoveTimeExample
InstanceOf: HealthkitAppleMoveTime
Usage: #example
Title: "Apple Move Time Example"
Description: "A conformant Apple Move Time instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:fuWn9dCY8HcgRgTeZKQ-BKCWg_8ED5sJqZKQa9nBPKU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:PVGGFk9CBvJeTLoWQF7x-2Sj2RwQZCoNX-hukqjATzQ"
* status = #final
* code = HealthKitMeasurementCS#apple-move-time
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierAppleMoveTime
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 45 'min'

Instance: HealthkitAppleStandHourExample
InstanceOf: HealthkitAppleStandHour
Usage: #example
Title: "Apple Stand Hour Example"
Description: "A conformant Apple Stand Hour instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:65oAdGWPXmNiDFzUlNvPTvv7ulQcW1nTT5Lt0Gw89O4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:4-stv9sPDDAQMXCUBFWJFGMzPSEhkHxrLQ0KIzPRQGk"
* status = #final
* code = HealthKitMeasurementCS#apple-stand-hour
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierAppleStandHour
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitAppleStandHourCS#stood "Stood"

Instance: HealthkitAppleStandTimeExample
InstanceOf: HealthkitAppleStandTime
Usage: #example
Title: "Apple Stand Time Example"
Description: "A conformant Apple Stand Time instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ZTY4yjX_lC17lWmRHP-sT-6Do7SfKP0i5eTuaqTakjE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:fU5XaHisX2mf7suUE5UVKxdknaDoiPh-F8CHIKlVUeQ"
* status = #final
* code = HealthKitMeasurementCS#apple-stand-time
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierAppleStandTime
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 12 'min'

Instance: HealthkitAtrialFibrillationBurdenExample
InstanceOf: HealthkitAtrialFibrillationBurden
Usage: #example
Title: "Atrial Fibrillation Burden Example"
Description: "A conformant Atrial Fibrillation Burden instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:08zruYiRc3jt0bO3nhKQ5dH77Xm2s0Bgu1pmj1p3N4o"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:BUe-GQ5nU140mBfztz9qQS8R_VntMnFibYYCJMvDi68"
* status = #final
* code = HealthKitMeasurementCS#atrial-fibrillation-burden
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierAtrialFibrillationBurden
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2 '%'

Instance: HealthkitAudiogramPanelExample
InstanceOf: HealthkitAudiogramPanel
Usage: #example
Title: "Audiogram Panel Example"
Description: "A conformant Audiogram Panel instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:uwLiwgk9OTQrv3qkxWF8fpUypKAzzhqhB4Ldn525hWs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Oq1zXA2sxeiXD3kRDrcIZH15W_KHI8GbrsRpSHbWoXg"
* status = #final
* code = $loinc#89015-2 "Pure tone air conduction threshold audiometry panel"
* extension[healthKitSourceType].valueCode = #HKDataTypeIdentifierAudiogram
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* component[left-250].code = $loinc#91375-6
* component[left-250].valueQuantity = 20 'dB'
* component[right-250].code = $loinc#91374-9
* component[right-250].valueQuantity = 25 'dB'

Instance: HealthkitBiologicalSexExample
InstanceOf: HealthkitBiologicalSex
Usage: #example
Title: "Grove HealthKit Biological Sex Example"
Description: "A conformant Grove HealthKit Biological Sex instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:rcc2O8yOH3O8NySRJPr7babrphLU0-KKU_iXwKHcW94"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:iK2bbzaHI8rjcaED2acHt9rab9nyo6UxLxLbRNcEG1o"
* status = #final
* code = $loinc#46098-0 "Sex"
* extension[healthKitSourceType].valueCode = #HKCharacteristicTypeIdentifierBiologicalSex
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitBiologicalSexCS#female "Female"

Instance: HealthkitBladderIncontinenceExample
InstanceOf: HealthkitBladderIncontinence
Usage: #example
Title: "Bladder Incontinence Example"
Description: "A conformant Bladder Incontinence instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:VsHxvkUfXPhOV7q7uT6XbsKyfD-Ztcs35yMlHlLOoJA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:V22jPOeY1yNW002LRclBGgbb2Wa06W-DKmFSM_2PaHU"
* status = #final
* code = HealthKitMeasurementCS#bladder-incontinence
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierBladderIncontinence
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitBleedingAfterPregnancyExample
InstanceOf: HealthkitBleedingAfterPregnancy
Usage: #example
Title: "Bleeding After Pregnancy Example"
Description: "A conformant Bleeding After Pregnancy instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:OVP-phh2gI8PciS8J9m9xCZzAN8L3QhRiSdeEQ43c70"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:UoJnWcE5q8f1ltMN1QvFa5Yxe80C4U8S_rkVYOJ9xHs"
* status = #final
* code = HealthKitMeasurementCS#bleeding-after-pregnancy
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierBleedingAfterPregnancy
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitBleedingAfterPregnancyCS#unspecified "Unspecified"

Instance: HealthkitBleedingDuringPregnancyExample
InstanceOf: HealthkitBleedingDuringPregnancy
Usage: #example
Title: "Bleeding During Pregnancy Example"
Description: "A conformant Bleeding During Pregnancy instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:yQ01zaKR64bqYo0XFc15V4N9HMguSyF_BKhkFMnZuFg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:D00xJbzwP2WWJNP0G-b5a5GWXsPLhHxCsiyh2GWEcbY"
* status = #final
* code = HealthKitMeasurementCS#bleeding-during-pregnancy
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierBleedingDuringPregnancy
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitBleedingDuringPregnancyCS#unspecified "Unspecified"

Instance: HealthkitBloodAlcoholContentExample
InstanceOf: HealthkitBloodAlcoholContent
Usage: #example
Title: "Blood Alcohol Content Example"
Description: "A conformant Blood Alcohol Content instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:CtQsbzBcK1cL-4gAVVDFLL0ZHuwf1AWlZuOGwbIfsvY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Ulr4hwXoVHtSYcUoWKavDZzfE_8QmykjQaF7H6fWgNk"
* status = #final
* code = HealthKitMeasurementCS#blood-alcohol-content
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierBloodAlcoholContent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 0.04 '%'

Instance: HealthkitBloodTypeExample
InstanceOf: HealthkitBloodType
Usage: #example
Title: "Grove HealthKit Blood Type Example"
Description: "A conformant Grove HealthKit Blood Type instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:m6iCgW6uQq8iK7QrncDfqEPJULm7uYYBLlOMwwqA6wY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:FlCLTNmEmpV3zBbwLNoMD6dtXR9-lRxIDUAxp84qZ08"
* status = #final
* code = $loinc#882-1 "ABO and Rh group [Type] in Blood"
* extension[healthKitSourceType].valueCode = #HKCharacteristicTypeIdentifierBloodType
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitBloodTypeCS#a-positive "A positive"

Instance: HealthkitContraceptiveUseExample
InstanceOf: HealthkitContraceptiveUse
Usage: #example
Title: "Contraceptive Use Example"
Description: "A conformant Contraceptive Use instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:XLyeoKjPnh4ZuTkJ1mWydpQ5suqRCcdr5YjJkEHXsIM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:9cW-5lyTsfWf1U9L0eFof5usFHDsuLBlKD7xDjyulRY"
* status = #final
* code = $loinc#8659-5 "Birth control method - Reported"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierContraceptive
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitContraceptiveUseCS#unspecified "Unspecified"

Instance: HealthkitCyclingFunctionalThresholdPowerExample
InstanceOf: HealthkitCyclingFunctionalThresholdPower
Usage: #example
Title: "Cycling Functional Threshold Power Example"
Description: "A conformant Cycling Functional Threshold Power instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:drI44V4MHp0Ye3eckyRLFzXUkvbtKaQxAta_PrvDLUY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ODNYHkyGzzjphNMJikSDtEwf3lb7Bi72jbhHR6SoUXw"
* status = #final
* code = HealthKitMeasurementCS#cycling-functional-threshold-power
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierCyclingFunctionalThresholdPower
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 235 'W'

Instance: HealthkitDateOfBirthExample
InstanceOf: HealthkitDateOfBirth
Usage: #example
Title: "Grove HealthKit Date of Birth Example"
Description: "A conformant Grove HealthKit Date of Birth instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:SyFqVTn7DBcfrPQ0QaERcO4rQMPgae3utIxL6UcW47I"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:TG_l2S9WAUxvBy3YrpY3aVseb1VyGgYsGuwSADvztjU"
* status = #final
* code = $loinc#21112-8 "Birth date"
* extension[healthKitSourceType].valueCode = #HKCharacteristicTypeIdentifierDateOfBirth
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueDateTime = "1985-04-12"

Instance: HealthkitEnvironmentalAudioExposureExample
InstanceOf: HealthkitEnvironmentalAudioExposure
Usage: #example
Title: "Environmental Audio Exposure Example"
Description: "A conformant Environmental Audio Exposure instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:stgQnHSz9R_ALunGtGxx7jXTIajQLKTLqxqmzLclCVo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:EIVMmcBp5ADHugZWdgcoKsXxMNmW_x8FEkSKPmgpUMY"
* status = #final
* code = HealthKitMeasurementCS#environmental-audio-exposure
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierEnvironmentalAudioExposure
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 68 'dB[SPL]' "dB(SPL)"

Instance: HealthkitEnvironmentalAudioExposureNotificationExample
InstanceOf: HealthkitEnvironmentalAudioExposureNotification
Usage: #example
Title: "Environmental Audio Exposure Notification Example"
Description: "A conformant Environmental Audio Exposure Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:rAvVPk9vpw4wlGaDC0tU2cQmo7Sa7h0cbsIIvsQ4BH8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:LcLwi0lfGsziYRL3Q4r_L6BFfwkZ6JC9HmbkzLdPpzE"
* status = #final
* code = HealthKitMeasurementCS#environmental-audio-exposure-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierAudioExposureEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitEnvironmentalAudioExposureNotificationCS#momentary-limit "Momentary limit"

Instance: HealthkitEnvironmentalSoundReductionExample
InstanceOf: HealthkitEnvironmentalSoundReduction
Usage: #example
Title: "Environmental Sound Reduction Example"
Description: "A conformant Environmental Sound Reduction instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:3GmkNtHK6qqgqDadPBACGCqYnuCg9ii6vf0CGQJ-Srs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:BF_m_DZ_LTKA2HDgu8AC2ugAC7TK_OuooFCRjya6tgk"
* status = #final
* code = HealthKitMeasurementCS#environmental-sound-reduction
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierEnvironmentalSoundReduction
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 22 'dB[SPL]' "dB(SPL)"

Instance: HealthkitFitzpatrickSkinTypeExample
InstanceOf: HealthkitFitzpatrickSkinType
Usage: #example
Title: "Grove HealthKit Fitzpatrick Skin Type Example"
Description: "A conformant Grove HealthKit Fitzpatrick Skin Type instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:mK_VuN5AdFv--zap7QRi4zWOXO3gnL8c2upixq5Eaco"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:MwEyLWWHJTnlITW1P2com4yG43J2n2ne6g4aZi4m79I"
* status = #final
* code = $loinc#66555-4 "Skin type [Fitzpatrick Classification Scale]"
* extension[healthKitSourceType].valueCode = #HKCharacteristicTypeIdentifierFitzpatrickSkinType
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitFitzpatrickSkinTypeCS#type-i "Type I"

Instance: HealthkitFoodCorrelationExample
InstanceOf: HealthkitFoodCorrelation
Usage: #example
Title: "Food Correlation Example"
Description: "A conformant Food Correlation instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:BoM_Gv2bXf7byvhol_fWfKv04DOYFQ9WT9Ovpdx8mos"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:V16Jt2WEDfHntPn7vCZzIQYx8fOk6VVgpo6QYjMv1UE"
* status = #final
* code = HealthKitMeasurementCS#food-correlation
* extension[healthKitSourceType].valueCode = #HKCorrelationTypeIdentifierFood
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* hasMember[+] = Reference(Observation/GroveMobileDietaryEnergyExample)

Instance: HealthkitForcedExpiratoryVolume1Example
InstanceOf: HealthkitForcedExpiratoryVolume1
Usage: #example
Title: "Forced Expiratory Volume in 1 Second Example"
Description: "A conformant Forced Expiratory Volume in 1 Second instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:CgLciuL9hopYmoC9yYeBjeq9GCIlTtb5T08GBT7Xry0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:c7CBvqTKAoKg3hOU1yEk4HARpz-Pr5bLn4x7_7SI24o"
* status = #final
* code = $loinc#20150-9 "FEV1"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierForcedExpiratoryVolume1
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 3.6 'L'

Instance: HealthkitForcedVitalCapacityExample
InstanceOf: HealthkitForcedVitalCapacity
Usage: #example
Title: "Forced Vital Capacity Example"
Description: "A conformant Forced Vital Capacity instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:1qO8Qdx9qFAG5sSNFQcTpaYM-DdvMyzuksFq6eMEGMY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:AXLL_q3T1M_P8kp9WKbmEeLX-E6rZY-n0Nc3osLZQYs"
* status = #final
* code = $loinc#19868-9 "Forced vital capacity [Volume] Respiratory system by Spirometry"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierForcedVitalCapacity
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 4.5 'L'

Instance: HealthkitGad7AssessmentExample
InstanceOf: HealthkitGad7Assessment
Usage: #example
Title: "Grove HealthKit GAD-7 Score Example"
Description: "A conformant Grove HealthKit GAD-7 Score instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:5x-hPlwYvsMHa-IGnmRAml7woCMzBIJcUmN4kvrGDmg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:hV7xtNcXFXFjXt6daWrYKtmutoqNe0r8KxyCy-VCi0M"
* status = #final
* code = $loinc#70274-6 "Generalized anxiety disorder 7 item (GAD-7) total score [Reported.PHQ]"
* extension[healthKitSourceType].valueCode = #HKScoredAssessmentTypeIdentifierGAD7
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 6 '{score}' "score"

Instance: HealthkitHandwashingSessionExample
InstanceOf: HealthkitHandwashingSession
Usage: #example
Title: "Handwashing Session Example"
Description: "A conformant Handwashing Session instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:MtQ_CCWqm1liJsnSjkH5GiNskVG-yVMrRyNUl3H2iYo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:DFXDFFu9nvD6HyUX0hzfj-GzpzVeIvFQW3wps6Cgb6k"
* status = #final
* code = HealthKitMeasurementCS#handwashing-session
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHandwashingEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 22 's'

Instance: HealthkitHeadphoneAudioExposureExample
InstanceOf: HealthkitHeadphoneAudioExposure
Usage: #example
Title: "Headphone Audio Exposure Example"
Description: "A conformant Headphone Audio Exposure instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:SeErBcvyFRrzBzGteBTjeLYgwTeU-Us8ymLShZdxFZk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:tYTd27G48ziqtq5MdlsiQ0NriKF5OIfn4t02_alT8YU"
* status = #final
* code = HealthKitMeasurementCS#headphone-audio-exposure
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierHeadphoneAudioExposure
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 74 'dB[SPL]' "dB(SPL)"

Instance: HealthkitHeadphoneAudioExposureNotificationExample
InstanceOf: HealthkitHeadphoneAudioExposureNotification
Usage: #example
Title: "Headphone Audio Exposure Notification Example"
Description: "A conformant Headphone Audio Exposure Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:lLxrpyrE97UU49NU7wepvgPhSatv5iJt2nDPeEY7KUQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:w_rzqt5eFo-19lUw_ypF1dJlNC-gtcw7NRKlbNP8XWk"
* status = #final
* code = HealthKitMeasurementCS#headphone-audio-exposure-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHeadphoneAudioExposureEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitHeadphoneAudioExposureNotificationCS#seven-day-limit "Seven day limit"

Instance: HealthkitHeartRateRecoveryOneMinuteExample
InstanceOf: HealthkitHeartRateRecoveryOneMinute
Usage: #example
Title: "Heart Rate Recovery (One Minute) Example"
Description: "A conformant Heart Rate Recovery (One Minute) instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ozfqq5QEIq3spxfjjeHnh3BJ2T5zAd__uvpJLIN1Ir4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:CEHQJyf6ZnDE3glevZ-N-baRc1NOWbw_CjWdTYLo__8"
* status = #final
* code = HealthKitMeasurementCS#heart-rate-recovery-one-minute
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierHeartRateRecoveryOneMinute
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 24 '/min' "beats/minute"

Instance: HealthkitHighHeartRateNotificationExample
InstanceOf: HealthkitHighHeartRateNotification
Usage: #example
Title: "High Heart Rate Notification Example"
Description: "A conformant High Heart Rate Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:i3ZdhmIU1R1wHK7f9bVnl6B_-zz-3Y6yGVnyDGlHurQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:oX0rYqsUetSD6IxA42lyIcET6XoFqX6kmdKG8pJZaAg"
* status = #final
* code = HealthKitMeasurementCS#high-heart-rate-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHighHeartRateEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitHighHeartRateNotificationCS#occurred "Occurred"

Instance: HealthkitHypertensionNotificationExample
InstanceOf: HealthkitHypertensionNotification
Usage: #example
Title: "Hypertension Notification Example"
Description: "A conformant Hypertension Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:mSGDKM3sdqFGYmgW9gw4zBEiVBNYWk1hKBrkKQ96a_g"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:cN8FJsxTHTRO4h9MkZ8ECDo9Q7_B0DC4qPCOeAwv2zI"
* status = #final
* code = HealthKitMeasurementCS#hypertension-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHypertensionEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitHypertensionNotificationCS#occurred "Occurred"

Instance: HealthkitInfrequentMenstrualCyclesExample
InstanceOf: HealthkitInfrequentMenstrualCycles
Usage: #example
Title: "Infrequent Menstrual Cycles Example"
Description: "A conformant Infrequent Menstrual Cycles instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:202Quhpm0Y6FyP0_W5D9r2Wl2QN8VZCnakE_pdtY9sk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:hkt_B-A0v1SJBdMPH6H5DlgjbY7nzoruHyHZRXgR4Hs"
* status = #final
* code = HealthKitMeasurementCS#infrequent-menstrual-cycles
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierInfrequentMenstrualCycles
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitInfrequentMenstrualCyclesCS#present "Present"

Instance: HealthkitInhalerUsageExample
InstanceOf: HealthkitInhalerUsage
Usage: #example
Title: "Inhaler Usage Example"
Description: "A conformant Inhaler Usage instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:H0Wm0faErLx8zhp286witXZH4h3maaHMHgzRjVyJ7js"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:2bRHVSsoUht_O24YDvCugJWyaHC3vus89oI0pkpa4lE"
* status = #final
* code = HealthKitMeasurementCS#inhaler-usage
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierInhalerUsage
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2 '{puff}' "puffs"

Instance: HealthkitInsulinDeliveryExample
InstanceOf: HealthkitInsulinDelivery
Usage: #example
Title: "Insulin Delivery Example"
Description: "A conformant Insulin Delivery instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:cBCVAOwmOndbXKTkEvuABJ3SOihJN-qHzx41r8f-iPA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:iXkd4P4yyDhIiPAS-c748bmb3XGtS_ANJCF0CkiPME0"
* status = #final
* code = HealthKitMeasurementCS#insulin-delivery
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierInsulinDelivery
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 6 '[iU]' "IU"

Instance: HealthkitIrregularHeartRhythmNotificationExample
InstanceOf: HealthkitIrregularHeartRhythmNotification
Usage: #example
Title: "Irregular Heart Rhythm Notification Example"
Description: "A conformant Irregular Heart Rhythm Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:uSasK26RUKQCylIsyn29Hd1UsIVCnUrePk3L_u45_JE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-sNrJCV_xEFSXASfKP0YMdsgpTTCWrSdi0bbs4b1cT4"
* status = #final
* code = HealthKitMeasurementCS#irregular-heart-rhythm-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierIrregularHeartRhythmEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitIrregularHeartRhythmNotificationCS#occurred "Occurred"

Instance: HealthkitIrregularMenstrualCyclesExample
InstanceOf: HealthkitIrregularMenstrualCycles
Usage: #example
Title: "Irregular Menstrual Cycles Example"
Description: "A conformant Irregular Menstrual Cycles instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:RNM1H5a48klcvTOdJycF94WSO1E6Cv2a4oVhgXDepHQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Kyf0OVT0ajJUeZ2u2yThQEA9Q-JQun0Yz7DCNQZYQ34"
* status = #final
* code = HealthKitMeasurementCS#irregular-menstrual-cycles
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierIrregularMenstrualCycles
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitIrregularMenstrualCyclesCS#present "Present"

Instance: HealthkitLactationStatusExample
InstanceOf: HealthkitLactationStatus
Usage: #example
Title: "Lactation Status Example"
Description: "A conformant Lactation Status instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:zBDLjT-yPwpdIATFyaYXD0n3_B48uniiB3gfcZAHW6U"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:CbQIOoLhWxM9NTYPR-ujoOR_8e2pAfWPREQbHgJEvOk"
* status = #final
* code = $loinc#63895-7 "Breastfeeding status"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierLactation
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitLactationStatusCS#lactating "Lactating"

Instance: HealthkitLowCardioFitnessNotificationExample
InstanceOf: HealthkitLowCardioFitnessNotification
Usage: #example
Title: "Low Cardio Fitness Notification Example"
Description: "A conformant Low Cardio Fitness Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:TkEQwWalgOKlOpbC6os8N3nyXNkq2uMSWhl5f_8Lyrs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:v1cyGZ9mV1c7ahmKJIRygw8IMvawKnWze5CtqYk5Edc"
* status = #final
* code = HealthKitMeasurementCS#low-cardio-fitness-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierLowCardioFitnessEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitLowCardioFitnessNotificationCS#low-fitness "Low fitness"

Instance: HealthkitLowHeartRateNotificationExample
InstanceOf: HealthkitLowHeartRateNotification
Usage: #example
Title: "Low Heart Rate Notification Example"
Description: "A conformant Low Heart Rate Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:lfyl1dbUSh_HuS_6eHvGWd0lQfHMFDE9i6lqDPHkQt8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:tJADAhLNsfWi6cMr5-enyq0x-f_MqW7werJ0blqmoeU"
* status = #final
* code = HealthKitMeasurementCS#low-heart-rate-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierLowHeartRateEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitLowHeartRateNotificationCS#occurred "Occurred"

Instance: HealthkitNumberOfAlcoholicBeveragesExample
InstanceOf: HealthkitNumberOfAlcoholicBeverages
Usage: #example
Title: "Number of Alcoholic Beverages Example"
Description: "A conformant Number of Alcoholic Beverages instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:NuHF5OE7-NfQN6DjxMvOzX0Hteh--puI2-8XJlQ5kqg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:gMoUBnLhpQBpvWH2PL8T8XQJ1tjW5sgNV5FRqei-6yE"
* status = #final
* code = HealthKitMeasurementCS#number-of-alcoholic-beverages
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierNumberOfAlcoholicBeverages
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 2 '{drinks}' "drinks"

Instance: HealthkitNumberOfTimesFallenExample
InstanceOf: HealthkitNumberOfTimesFallen
Usage: #example
Title: "Number of Times Fallen Example"
Description: "A conformant Number of Times Fallen instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:5gVCEKoT41FRg1dyfBteMG76WE_He2wrvk2VvNZBp4U"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:stzlELqfgFpVRihlyDEKuiOWK0SqPNTBBKLuPtdSF1I"
* status = #final
* code = HealthKitMeasurementCS#number-of-times-fallen
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierNumberOfTimesFallen
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 1 '{falls}' "falls"

Instance: HealthkitPeakExpiratoryFlowRateExample
InstanceOf: HealthkitPeakExpiratoryFlowRate
Usage: #example
Title: "Peak Expiratory Flow Rate Example"
Description: "A conformant Peak Expiratory Flow Rate instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:FLgVjQlipbfhcd3AdLf3u6W2UeG8G2JmnDIVFdULkEs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:RRr1hssTUpnOfHaw_BBx36YjTAEAAfaC8ZzR9_yLPK0"
* status = #final
* code = $loinc#33452-4 "Maximum expiratory gas flow Respiratory system airway"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierPeakExpiratoryFlowRate
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 480 'L/min'

Instance: HealthkitPeripheralPerfusionIndexExample
InstanceOf: HealthkitPeripheralPerfusionIndex
Usage: #example
Title: "Peripheral Perfusion Index Example"
Description: "A conformant Peripheral Perfusion Index instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:3-acW_ccSNEJCadc-ypbAj1JmmWUJRS_SbeIUDgLLg4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:8jy-IBJ0GOZrIkJoqJhm-rGYKob2UvL-AzC-LMXv20s"
* status = #final
* code = $loinc#61006-3 "Perfusion index Tissue by Pulse oximetry"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierPeripheralPerfusionIndex
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 3.5 '%'

Instance: HealthkitPersistentIntermenstrualBleedingExample
InstanceOf: HealthkitPersistentIntermenstrualBleeding
Usage: #example
Title: "Persistent Intermenstrual Bleeding Example"
Description: "A conformant Persistent Intermenstrual Bleeding instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:p1pBv4aORwehAVo5OItFezQ5WN-rXTQm-J8t7GmO6gk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:TiT8BqC_eSXZG_Ti8Aa0pNPc9fiC7tWYk6SClKf-C3I"
* status = #final
* code = HealthKitMeasurementCS#persistent-intermenstrual-bleeding
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierPersistentIntermenstrualBleeding
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitPersistentIntermenstrualBleedingCS#present "Present"

Instance: HealthkitPhq9AssessmentExample
InstanceOf: HealthkitPhq9Assessment
Usage: #example
Title: "Grove HealthKit PHQ-9 Score Example"
Description: "A conformant Grove HealthKit PHQ-9 Score instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:nrlxtecbRkruMacOXNJMwULg3QOoT_dfc-oNN6mZXis"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:EQCWfS7qYnY8tC5SfIBHWsPBklKFE4GkE0xVssoW3Bc"
* status = #final
* code = $loinc#44261-6 "Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]"
* extension[healthKitSourceType].valueCode = #HKScoredAssessmentTypeIdentifierPHQ9
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 8 '{score}' "score"

Instance: HealthkitPhysicalEffortExample
InstanceOf: HealthkitPhysicalEffort
Usage: #example
Title: "Physical Effort Example"
Description: "A conformant Physical Effort instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:eVctlMZg7iJUpWn5sOFHLlK77wxt6BMLhI01J-_IBjk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-R3WMF3iLW1jRG-mkl1bgeqmCLFWnPYcV4wXYmxKNy4"
* status = #final
* code = HealthKitMeasurementCS#physical-effort
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierPhysicalEffort
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 4.5 'kcal/kg/h' "kcal/(kg.h)"

Instance: HealthkitPregnancyStatusExample
InstanceOf: HealthkitPregnancyStatus
Usage: #example
Title: "Pregnancy Status Example"
Description: "A conformant Pregnancy Status instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:xGdfe6UhIpbogYNVPaI45vVe8j_oT_ZaeZEmc4QcT0o"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:UA0T-BNfPYZEK8xcy8ZU2WR4tuzOtQfaW9u-QINn-mY"
* status = #final
* code = $loinc#82810-3 "Pregnancy status"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierPregnancy
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitPregnancyStatusCS#pregnant "Pregnant"

Instance: HealthkitPregnancyTestResultExample
InstanceOf: HealthkitPregnancyTestResult
Usage: #example
Title: "Pregnancy Test Result Example"
Description: "A conformant Pregnancy Test Result instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:hr6WPCGrYuBaeb6cIpnCOIFhv3gRj_ZCkCNO_RMO0Wk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:mPLMiB6H2fUilwvfnZqwLtHaGOKCCRCA1DJ86VPhQpY"
* status = #final
* code = $loinc#2106-3 "Choriogonadotropin [Presence] in Urine"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierPregnancyTestResult
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitPregnancyTestResultCS#negative "Negative"

Instance: HealthkitProgesteroneTestResultExample
InstanceOf: HealthkitProgesteroneTestResult
Usage: #example
Title: "Progesterone Test Result Example"
Description: "A conformant Progesterone Test Result instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:H5s-uEE0SGdqPWOB0WZLbRQaDflyiqAIg8LMWh1rR98"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:z9nz12n0JQ_RVJLvdFYTkMotdCRyXA2H45nfw73t3ZI"
* status = #final
* code = HealthKitMeasurementCS#progesterone-test-result
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierProgesteroneTestResult
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitProgesteroneTestResultCS#negative "Negative"

Instance: HealthkitProlongedMenstrualPeriodsExample
InstanceOf: HealthkitProlongedMenstrualPeriods
Usage: #example
Title: "Prolonged Menstrual Periods Example"
Description: "A conformant Prolonged Menstrual Periods instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:lrj82_L_qm7z2_WXgkHQzXvHJwKD4tZmpPeTYDh0W1M"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:S0g7wtKpGfqUp7SDwj1YcrQZhIhru6z5-BuV19Z7NZ0"
* status = #final
* code = HealthKitMeasurementCS#prolonged-menstrual-periods
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierProlongedMenstrualPeriods
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitProlongedMenstrualPeriodsCS#present "Present"

Instance: HealthkitRunningGroundContactTimeExample
InstanceOf: HealthkitRunningGroundContactTime
Usage: #example
Title: "Running Ground Contact Time Example"
Description: "A conformant Running Ground Contact Time instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:VhRu8SzvlfQPQrZW9Kx_pcw1vevfSeR0JioM1JPWtxY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Uos17k1zUNMTuYYUIkph78FcLOnC-UbUytV1tps4pHg"
* status = #final
* code = HealthKitMeasurementCS#running-ground-contact-time
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierRunningGroundContactTime
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 245 'ms'

Instance: HealthkitRunningStrideLengthExample
InstanceOf: HealthkitRunningStrideLength
Usage: #example
Title: "Running Stride Length Example"
Description: "A conformant Running Stride Length instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:JJOhw9LBhxUXSGwYR9MH4ELY_tqiR9Ag6htnLGeMbjM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:gJXwKoTQQwY8nCCP373Qgr1eG7u6mipEDFuL9s6EjlQ"
* status = #final
* code = HealthKitMeasurementCS#running-stride-length
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierRunningStrideLength
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 1.15 'm'

Instance: HealthkitRunningVerticalOscillationExample
InstanceOf: HealthkitRunningVerticalOscillation
Usage: #example
Title: "Running Vertical Oscillation Example"
Description: "A conformant Running Vertical Oscillation instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:yOHjpaAwEjlO9yzG5NN-MfG6uydjuUeCp1TGbcJAKzw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Yq-dtRUJu8z8MQzbMAHYTYCW04FjVOG4U0AGrmkhiXM"
* status = #final
* code = HealthKitMeasurementCS#running-vertical-oscillation
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierRunningVerticalOscillation
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 8.4 'cm'

Instance: HealthkitSixMinuteWalkTestDistanceExample
InstanceOf: HealthkitSixMinuteWalkTestDistance
Usage: #example
Title: "Six-Minute Walk Test Distance Example"
Description: "A conformant Six-Minute Walk Test Distance instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Sq_D4RdjV8Mk2XiaUl48WH9s4ZvtSEPjYUFMNYWdFco"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:yiInKk33sg3RG6pLpZAH53PzocqlL755bgGCsIYYnes"
* status = #final
* code = $loinc#64098-7 "Six minute walk test"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierSixMinuteWalkTestDistance
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 540 'm'

Instance: HealthkitSleepApneaNotificationExample
InstanceOf: HealthkitSleepApneaNotification
Usage: #example
Title: "Sleep Apnea Notification Example"
Description: "A conformant Sleep Apnea Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:c6TeeZYofYYtlCn_-rououOCmBBsukqBO3w-xjf9fMw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:peWLmAF9OauI5hPNr57SmC1MAX1QzPLd1KzEAJ0L03k"
* status = #final
* code = HealthKitMeasurementCS#sleep-apnea-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierSleepApneaEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitSleepApneaNotificationCS#occurred "Occurred"

Instance: HealthkitSleepingBreathingDisturbancesExample
InstanceOf: HealthkitSleepingBreathingDisturbances
Usage: #example
Title: "Sleeping Breathing Disturbances Example"
Description: "A conformant Sleeping Breathing Disturbances instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:8RiOmzuyl2dJAn-KyMqozT41S-Lp_UwZHGvXUzoAFwQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:FGWUccI-pK9bhURHEFtk4JbwiiT8kx8m97ShW47dV8A"
* status = #final
* code = HealthKitMeasurementCS#sleeping-breathing-disturbances
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 4.2 '/h' "events/hour"

Instance: HealthkitStairAscentSpeedExample
InstanceOf: HealthkitStairAscentSpeed
Usage: #example
Title: "Stair Ascent Speed Example"
Description: "A conformant Stair Ascent Speed instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:N1ZNOrH876j5i1kcIFQZW0DhyLt1WHEzPW3MiOU3gPs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:7imzZJjmCT717Kp43K_rD9f2UC76_-QUeuqtI1IRKK0"
* status = #final
* code = $loinc#112431-2 "Stair ascent speed [Velocity]"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierStairAscentSpeed
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 0.42 'm/s'

Instance: HealthkitStairDescentSpeedExample
InstanceOf: HealthkitStairDescentSpeed
Usage: #example
Title: "Stair Descent Speed Example"
Description: "A conformant Stair Descent Speed instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:RiXOYBDrqHD8J959oP3ay7WQ1olIaKxrOU1jPc8foR4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:TNzdSA5BxQY33aK86y8jbCsQa0io5Q34v8NV9x_hNek"
* status = #final
* code = $loinc#112430-4 "Stair descent speed [Velocity]"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierStairDescentSpeed
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 0.52 'm/s'

Instance: HealthkitStateOfMindExample
InstanceOf: HealthkitStateOfMind
Usage: #example
Title: "State of Mind Example"
Description: "A conformant State of Mind instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:2r7OBisXZ7xPU6C9VxiORRKJP0ue2pSqhZR-trK4_xE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:YGRXQRyFSCOKKWnu1cwIbVHB4p6qxfOj0cT9Il7QPjs"
* status = #final
* code = HealthKitMeasurementCS#state-of-mind
* extension[healthKitSourceType].valueCode = #HKDataTypeStateOfMind
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 0.4 '1' "valence"
* component[kind].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#kind
* component[kind].valueCodeableConcept = HealthkitStateOfMindKindCS#momentary-emotion "Momentary emotion"

Instance: HealthkitSwimmingStrokeCountExample
InstanceOf: HealthkitSwimmingStrokeCount
Usage: #example
Title: "Swimming Stroke Count Example"
Description: "A conformant Swimming Stroke Count instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:w6FT7fXIknjWw87xm8kEI49h5_A6v3GXJBVb65CF1sw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:YSgjfOd-Mcihq4WxvtNshwxtrNVezW1IsO9wIrmX6W0"
* status = #final
* code = HealthKitMeasurementCS#swimming-stroke-count
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierSwimmingStrokeCount
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 640 '{strokes}' "strokes"

Instance: HealthkitSymptomAbdominalCrampsExample
InstanceOf: HealthkitSymptomAbdominalCramps
Usage: #example
Title: "Symptom: Abdominal Cramps Example"
Description: "A conformant Symptom: Abdominal Cramps instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:u02GgMN16NYKaipIn8Q-mNlnAWZge_rvzZuC4GMBduE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:_UPICU_JqK1jdhhQPJbpKFsKqbD1_gSBbeVjzeb0ioQ"
* status = #final
* code = HealthKitMeasurementCS#symptom-abdominal-cramps
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierAbdominalCramps
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomAcneExample
InstanceOf: HealthkitSymptomAcne
Usage: #example
Title: "Symptom: Acne Example"
Description: "A conformant Symptom: Acne instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:i_IBy1YXPp_ppKmSrRbl1LIFXb3HGrci4YQLuPd40uM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:0cZPS1motYNnQYThfEHVnJC4wCemYTYxIA7eCx9KIig"
* status = #final
* code = HealthKitMeasurementCS#symptom-acne
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierAcne
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomAppetiteChangesExample
InstanceOf: HealthkitSymptomAppetiteChanges
Usage: #example
Title: "Symptom: Appetite Changes Example"
Description: "A conformant Symptom: Appetite Changes instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:U8sCcAhhSI3LTO-xkXAD80ghGhPtgYiDIxO1RMLmbrU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Gpb-gt49G5MD0Qj4s2IGXi8Q-0usA7qw1-ww_UNB_y8"
* status = #final
* code = HealthKitMeasurementCS#symptom-appetite-changes
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierAppetiteChanges
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitSymptomAppetiteChangesCS#no-change "No change"

Instance: HealthkitSymptomBloatingExample
InstanceOf: HealthkitSymptomBloating
Usage: #example
Title: "Symptom: Bloating Example"
Description: "A conformant Symptom: Bloating instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:HfLkOqVHIcbOLaRQ4kQrK-seuba8ws004SOl2t9WgIc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-dnAO39HdFPaftf-e7px5yCBhvPi-lYBUHm08GPYN6c"
* status = #final
* code = HealthKitMeasurementCS#symptom-bloating
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierBloating
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomBreastPainExample
InstanceOf: HealthkitSymptomBreastPain
Usage: #example
Title: "Symptom: Breast Pain Example"
Description: "A conformant Symptom: Breast Pain instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:2L1XZcm3c_fxVRg-ECDV3qIuCzJQfTvKn9Ce3UpbuXY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:i7Pj461B8zBeroS2-nGLxvpV8sAM-nXDHsC88SuCGgU"
* status = #final
* code = HealthKitMeasurementCS#symptom-breast-pain
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierBreastPain
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomChestTightnessOrPainExample
InstanceOf: HealthkitSymptomChestTightnessOrPain
Usage: #example
Title: "Symptom: Chest Tightness or Pain Example"
Description: "A conformant Symptom: Chest Tightness or Pain instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:nGkYs07TvHnyefTc2OKosXg2LAq0P50suCxFLY-JFyU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:frNnZVdnKQBj2SPw7Bu6xsJJ-65eZu21aYCFwzlrjwQ"
* status = #final
* code = HealthKitMeasurementCS#symptom-chest-tightness-or-pain
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierChestTightnessOrPain
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomChillsExample
InstanceOf: HealthkitSymptomChills
Usage: #example
Title: "Symptom: Chills Example"
Description: "A conformant Symptom: Chills instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:B8IoDO5KD4jJUWol0mng5FU4A7NMPGfwC6Jq6R-b4Sc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:q_v2apm8tI3UYwnk80wtW3e15904CmAVu2SwHkmY0dA"
* status = #final
* code = HealthKitMeasurementCS#symptom-chills
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierChills
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomConstipationExample
InstanceOf: HealthkitSymptomConstipation
Usage: #example
Title: "Symptom: Constipation Example"
Description: "A conformant Symptom: Constipation instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:aCS1Ck1b51ER7kt3HkXLBD9Rt2_K1Zxw8CVvqxA2tlU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ZNE-9XY5Hi-n9miRBafxRx7UmlTi8YGGJH69TEF20WY"
* status = #final
* code = HealthKitMeasurementCS#symptom-constipation
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierConstipation
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomCoughingExample
InstanceOf: HealthkitSymptomCoughing
Usage: #example
Title: "Symptom: Coughing Example"
Description: "A conformant Symptom: Coughing instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:9RfQmHP-RBOgQAb7WEIaIi5y8bzhgMqptUrfbTWlXTw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:6ae0SKNV_pgEdz7LrvuQ6qj9lZkGFYCIjf-lJViqLDk"
* status = #final
* code = HealthKitMeasurementCS#symptom-coughing
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierCoughing
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomDiarrheaExample
InstanceOf: HealthkitSymptomDiarrhea
Usage: #example
Title: "Symptom: Diarrhea Example"
Description: "A conformant Symptom: Diarrhea instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:TGXuo9NHPrFqGTKAnRttM_7xkqF7Yv6hyTHgWHmSMBk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:uCjBgV28HP_aUdqMUMamkUbZvMKezAdULtVTD9h7nUY"
* status = #final
* code = HealthKitMeasurementCS#symptom-diarrhea
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierDiarrhea
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomDizzinessExample
InstanceOf: HealthkitSymptomDizziness
Usage: #example
Title: "Symptom: Dizziness Example"
Description: "A conformant Symptom: Dizziness instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:KP5hvgGUWhHVB0WKeYZ7jzzVNaID4u50IAIs7GQzsOc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:vWG3clcCEyB-5EjjnbWfMmCcuQGSHQwmMoE0AbPwx50"
* status = #final
* code = HealthKitMeasurementCS#symptom-dizziness
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierDizziness
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomDrySkinExample
InstanceOf: HealthkitSymptomDrySkin
Usage: #example
Title: "Symptom: Dry Skin Example"
Description: "A conformant Symptom: Dry Skin instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:B_iXCTLJyhHerfUp5aJ1FjXwU5Nw61elzgPymffPtCw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:2KqI66d0sngqtSyBO3KSvod41pzEoF96XuzqDZy743E"
* status = #final
* code = HealthKitMeasurementCS#symptom-dry-skin
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierDrySkin
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomFaintingExample
InstanceOf: HealthkitSymptomFainting
Usage: #example
Title: "Symptom: Fainting Example"
Description: "A conformant Symptom: Fainting instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:7MgFSPI7dClpHZ-8Cj-_cGcZwcsFkHRKg98WV16iq38"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:P_g65MxlJAdmrN7CZIpF_YlwYCvBPrGtci-NiI03jM8"
* status = #final
* code = HealthKitMeasurementCS#symptom-fainting
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierFainting
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomFatigueExample
InstanceOf: HealthkitSymptomFatigue
Usage: #example
Title: "Symptom: Fatigue Example"
Description: "A conformant Symptom: Fatigue instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:IBGLlADpTxtb9Gg7MbJDZ_054hWRhJC87XZZoMRA6rM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ALX8Juvukma2hVeopCnVBAyCBNr4VdRXcpFZnkxToIU"
* status = #final
* code = HealthKitMeasurementCS#symptom-fatigue
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierFatigue
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomFeverExample
InstanceOf: HealthkitSymptomFever
Usage: #example
Title: "Symptom: Fever Example"
Description: "A conformant Symptom: Fever instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:IkQKDeFzua5ditNxwBDPwlpIa8Pz5i-K6BcJtiXHKEw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-UV4jxgEsBJYjkMdobj4GgNwOX6Fe_id0LfJpCIp3Qw"
* status = #final
* code = HealthKitMeasurementCS#symptom-fever
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierFever
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomGeneralizedBodyAcheExample
InstanceOf: HealthkitSymptomGeneralizedBodyAche
Usage: #example
Title: "Symptom: Generalized Body Ache Example"
Description: "A conformant Symptom: Generalized Body Ache instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Q8so_D3PsguJ-mTbE6N491PPv9P0mRJNBY1uISaBwug"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:btm3VAPLCe87141APxu38AzS9KQu2qdOqO9DtDRdhow"
* status = #final
* code = HealthKitMeasurementCS#symptom-generalized-body-ache
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierGeneralizedBodyAche
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomHairLossExample
InstanceOf: HealthkitSymptomHairLoss
Usage: #example
Title: "Symptom: Hair Loss Example"
Description: "A conformant Symptom: Hair Loss instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:DKm7Hybpzcmf203LvEXdb5YPIE1_ai3JXskFequN_2I"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:npgkzXbxukuQisPBlU4Y439adgbQPrIUiSNPAzJPNaA"
* status = #final
* code = HealthKitMeasurementCS#symptom-hair-loss
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHairLoss
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomHeadacheExample
InstanceOf: HealthkitSymptomHeadache
Usage: #example
Title: "Symptom: Headache Example"
Description: "A conformant Symptom: Headache instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:yFCIUVAEFMN2u81YF-wDun4hIdZoVfbxWM2UyMRxtYo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:O2aHf5w6F6NxcCl7QjUBm1d1nXItckKzdB8GBMFxtTo"
* status = #final
* code = HealthKitMeasurementCS#symptom-headache
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHeadache
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomHeartburnExample
InstanceOf: HealthkitSymptomHeartburn
Usage: #example
Title: "Symptom: Heartburn Example"
Description: "A conformant Symptom: Heartburn instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:KSBdvwCDbGAhRmGAgbAPhXGHtGK4AN1b_wbPWExu8lo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:vB7PjoQSH6r3SFRVCauCkp0oGjUbNTbJi2Sr4ymsUcA"
* status = #final
* code = HealthKitMeasurementCS#symptom-heartburn
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHeartburn
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomHotFlashesExample
InstanceOf: HealthkitSymptomHotFlashes
Usage: #example
Title: "Symptom: Hot Flashes Example"
Description: "A conformant Symptom: Hot Flashes instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:KvveE4E4VW0nKFnOL42p_Kmp7uwco06pyKe9vPUamUU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:HerxHX4votQoR2I8OFpHfVN4JDkyNLhcCif7ohIoPSM"
* status = #final
* code = HealthKitMeasurementCS#symptom-hot-flashes
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierHotFlashes
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomLossOfSmellExample
InstanceOf: HealthkitSymptomLossOfSmell
Usage: #example
Title: "Symptom: Loss of Smell Example"
Description: "A conformant Symptom: Loss of Smell instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:P_u3SM5VprzOsfWAV7jt4KLi7llm4S-Jo8obTEvTcvs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:312MvShjjDxXwnobQUSU-ag3UGUyra4J2sbCJH7P4Y0"
* status = #final
* code = HealthKitMeasurementCS#symptom-loss-of-smell
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierLossOfSmell
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomLossOfTasteExample
InstanceOf: HealthkitSymptomLossOfTaste
Usage: #example
Title: "Symptom: Loss of Taste Example"
Description: "A conformant Symptom: Loss of Taste instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ZSTigABkBOsa1U9LFNLd0md1vxfFRBFFumb2dJGd16c"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:6IsiEHl_8z2l-l7Nkjmeglo1dV0_1w9WJsBYyA312FU"
* status = #final
* code = HealthKitMeasurementCS#symptom-loss-of-taste
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierLossOfTaste
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomLowerBackPainExample
InstanceOf: HealthkitSymptomLowerBackPain
Usage: #example
Title: "Symptom: Lower Back Pain Example"
Description: "A conformant Symptom: Lower Back Pain instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:JXTkB_7WEZaVaRyyAjcE9z34Jb16MftOV9hrQWph6XU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:pq74uWPZ8HcHSlHmgGaqAK_ZX0ll9VEkln8YsmEi-5s"
* status = #final
* code = HealthKitMeasurementCS#symptom-lower-back-pain
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierLowerBackPain
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomMemoryLapseExample
InstanceOf: HealthkitSymptomMemoryLapse
Usage: #example
Title: "Symptom: Memory Lapse Example"
Description: "A conformant Symptom: Memory Lapse instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:SEt6mBlvyW9snV7LcbyH3yUKulR4NcLqHpRYgNer68Q"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Rz97NHKuZYFW-bYQGMQ2hR4afw-d2vBnLfFmRrPzSMQ"
* status = #final
* code = HealthKitMeasurementCS#symptom-memory-lapse
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierMemoryLapse
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomMoodChangesExample
InstanceOf: HealthkitSymptomMoodChanges
Usage: #example
Title: "Symptom: Mood Changes Example"
Description: "A conformant Symptom: Mood Changes instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:vt8GD3KU_gNAbKCuIlj7G-qetGEb4u4grYiMeHpUd_Q"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:NH3zELLMEu_eixpaRfFdoqxkW-eNw7dedRFlU7vx2KA"
* status = #final
* code = HealthKitMeasurementCS#symptom-mood-changes
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierMoodChanges
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomNauseaExample
InstanceOf: HealthkitSymptomNausea
Usage: #example
Title: "Symptom: Nausea Example"
Description: "A conformant Symptom: Nausea instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:1ITV4oj3BKrIbnSUt2J0U9YUEoUcs0eNzVJjRws-CbU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:4Y2bCBa8fWAA6fWl2or-5eDdFLvTe7p_AGBa0-OAqFQ"
* status = #final
* code = $loinc#81660-3 "Nausea [Presence]"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierNausea
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomNightSweatsExample
InstanceOf: HealthkitSymptomNightSweats
Usage: #example
Title: "Symptom: Night Sweats Example"
Description: "A conformant Symptom: Night Sweats instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:rfzIQDm0RbbLpZUP-l5vAARgYy9pswKEt_OfVAJatPY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Wvq6UH0lsV1czV7Dp_XxqOyMTHd6qXMF0fbTg_VNIlg"
* status = #final
* code = HealthKitMeasurementCS#symptom-night-sweats
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierNightSweats
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomPelvicPainExample
InstanceOf: HealthkitSymptomPelvicPain
Usage: #example
Title: "Symptom: Pelvic Pain Example"
Description: "A conformant Symptom: Pelvic Pain instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Q7Fooa4cjqw5Kas3wHB1gI6lf9n-4IF4YrKqbYl-tzE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ne9MrcIYKfWS8YMeOwurra3Z2mCUbXrki5RZxfxx-d0"
* status = #final
* code = HealthKitMeasurementCS#symptom-pelvic-pain
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierPelvicPain
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomRapidPoundingOrFlutteringHeartbeatExample
InstanceOf: HealthkitSymptomRapidPoundingOrFlutteringHeartbeat
Usage: #example
Title: "Symptom: Rapid, Pounding, or Fluttering Heartbeat Example"
Description: "A conformant Symptom: Rapid, Pounding, or Fluttering Heartbeat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:LTLcgSAzC7kFcaLMFQFXHvXhb5ZMYVHht3mf1umfVTs"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-G1TULTkkROSC3DF7hpGCOwR1uw0uJtOUCOJJ9ADFJk"
* status = #final
* code = HealthKitMeasurementCS#symptom-rapid-pounding-or-fluttering-heartbeat
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierRapidPoundingOrFlutteringHeartbeat
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomRunnyNoseExample
InstanceOf: HealthkitSymptomRunnyNose
Usage: #example
Title: "Symptom: Runny Nose Example"
Description: "A conformant Symptom: Runny Nose instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:9tQvJTZIdAiSxrx-6VVWjZU8oSvBDIbWLkQrZQXNn_M"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:LXRE48-JKIbgzWIbo0B-TTvLhDAr2JFtBgMtWuqQdxM"
* status = #final
* code = HealthKitMeasurementCS#symptom-runny-nose
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierRunnyNose
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomShortnessOfBreathExample
InstanceOf: HealthkitSymptomShortnessOfBreath
Usage: #example
Title: "Symptom: Shortness of Breath Example"
Description: "A conformant Symptom: Shortness of Breath instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:meMpJQc6e-xGLlrkpKCofZ-rd-nul_Frt39GVa92dwA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:OXNgFNh9ftmhtEmEFAzKfQRNY_OW8gASV8AIqM7o-Fk"
* status = #final
* code = HealthKitMeasurementCS#symptom-shortness-of-breath
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierShortnessOfBreath
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomSinusCongestionExample
InstanceOf: HealthkitSymptomSinusCongestion
Usage: #example
Title: "Symptom: Sinus Congestion Example"
Description: "A conformant Symptom: Sinus Congestion instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:XzNFYihUJFgz1j1jyxrPAr-3u1RDUeAheX_gPi39Gi4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:VFUJymDMiyQZWQI8bXsSHOw_QAJleC84zpv7o3U64o4"
* status = #final
* code = HealthKitMeasurementCS#symptom-sinus-congestion
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierSinusCongestion
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomSkippedHeartbeatExample
InstanceOf: HealthkitSymptomSkippedHeartbeat
Usage: #example
Title: "Symptom: Skipped Heartbeat Example"
Description: "A conformant Symptom: Skipped Heartbeat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:-vwDQ0oQ-BvlL5YNcYDoTkvosBPYERW2pmcCif9pKy8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:60ELXjRUQFlzqW8JTjhbww-77DGyhRxKjR5yuM4MUAA"
* status = #final
* code = HealthKitMeasurementCS#symptom-skipped-heartbeat
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierSkippedHeartbeat
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomSleepChangesExample
InstanceOf: HealthkitSymptomSleepChanges
Usage: #example
Title: "Symptom: Sleep Changes Example"
Description: "A conformant Symptom: Sleep Changes instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:eAEguJKfpTgdonV7SAnYoFd852y5CDYgv-mXM1DiHUU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:QcvuvGGMSnB4O4Yvb8ZlPqPtXe-NK5Ps-aQlkLkQ0oU"
* status = #final
* code = HealthKitMeasurementCS#symptom-sleep-changes
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierSleepChanges
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomSoreThroatExample
InstanceOf: HealthkitSymptomSoreThroat
Usage: #example
Title: "Symptom: Sore Throat Example"
Description: "A conformant Symptom: Sore Throat instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:zJp9qitmugxtal3noh-ixgcKL5Bu6hp15QfmtHGqnDI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:aG8tjTp5WHqyW23aTwJvWl9y2mGqz0LxFdnH243rYFQ"
* status = #final
* code = HealthKitMeasurementCS#symptom-sore-throat
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierSoreThroat
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomVomitingExample
InstanceOf: HealthkitSymptomVomiting
Usage: #example
Title: "Symptom: Vomiting Example"
Description: "A conformant Symptom: Vomiting instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:VzRsHRmRvzIWVXtcxAgB5A3vJ6ZumQODUwvmUn7V27M"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Ucv7kv0BnxsvyVjo1_vSFVFnWVOXbhopgHgvBXxI-5c"
* status = #final
* code = HealthKitMeasurementCS#symptom-vomiting
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierVomiting
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitSymptomWheezingExample
InstanceOf: HealthkitSymptomWheezing
Usage: #example
Title: "Symptom: Wheezing Example"
Description: "A conformant Symptom: Wheezing instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Jw_7LqZ3Et4tpt8pjTaayH-Jd2-HRwGrXT-Al0pXYAA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:APPMJG5FmP0JrvzHCGs285Hpg6UpDxf60bJR6YO1qNg"
* status = #final
* code = HealthKitMeasurementCS#symptom-wheezing
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierWheezing
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitTimeInDaylightExample
InstanceOf: HealthkitTimeInDaylight
Usage: #example
Title: "Time in Daylight Example"
Description: "A conformant Time in Daylight instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:wGN13SxW_TwF0gaSKCy_3A4SDmDp1crrbv82xIluTqE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:eIzND2efKCGAeizV8pjqW3zzTjUHAPX0SL6TPPOKLYE"
* status = #final
* code = HealthKitMeasurementCS#time-in-daylight
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierTimeInDaylight
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 47 'min'

Instance: HealthkitToothbrushingSessionExample
InstanceOf: HealthkitToothbrushingSession
Usage: #example
Title: "Toothbrushing Session Example"
Description: "A conformant Toothbrushing Session instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:2t81xUyxWRWLhG-32p9PfBhFnvCEemVIY-9zAOng2Vw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:mwufbEK-E9WA-f2oGyNk53YG8Z_lbhfE878jA-Zu2i0"
* status = #final
* code = HealthKitMeasurementCS#toothbrushing-session
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierToothbrushingEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 120 's'

Instance: HealthkitUnderwaterDepthExample
InstanceOf: HealthkitUnderwaterDepth
Usage: #example
Title: "Underwater Depth Example"
Description: "A conformant Underwater Depth instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:ax7u4NW7aGdNNWpTRiGx1eeK45viQFLoCVola5LpC3U"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-2KFaNy2iQEyknNOTQk89UtlNaDMWh_2E1B6G_Ki1GU"
* status = #final
* code = HealthKitMeasurementCS#underwater-depth
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierUnderwaterDepth
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 12 'm'

Instance: HealthkitUvExposureExample
InstanceOf: HealthkitUvExposure
Usage: #example
Title: "UV Exposure Example"
Description: "A conformant UV Exposure instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:I_qlIdq3oMSiyqIji3-A72PkpBM9EbuNBYMIVd0UheE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:ka0Z2srDp5UcKs7kFkjR9cnt7fSw5CFMYuk29ZQxH4Q"
* status = #final
* code = HealthKitMeasurementCS#uv-exposure
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierUVExposure
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 6 '{uvindex}' "UV index"

Instance: HealthkitVaginalDrynessExample
InstanceOf: HealthkitVaginalDryness
Usage: #example
Title: "Vaginal Dryness Example"
Description: "A conformant Vaginal Dryness instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:PFke7T7KlPy4YhJnqz8w0kGKG83fGuK-0PUUD-nWx44"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:B6GHRfGtczVtz9hh09-ScE_63TGsaJ6k6W8ZeWOvRvc"
* status = #final
* code = HealthKitMeasurementCS#vaginal-dryness
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierVaginalDryness
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#not-present "Not present"

Instance: HealthkitWaistCircumferenceExample
InstanceOf: HealthkitWaistCircumference
Usage: #example
Title: "Waist Circumference Example"
Description: "A conformant Waist Circumference instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:OB59Rgpzo6-SVJfYsb89Es-E2j9e8CVoNHZ9zDXni6w"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:TXIhgkmhwjibNCtKUEBXkQb6iI4cQjg5L-rhiRhQz40"
* status = #final
* code = $loinc#8280-0 "Waist Circumference at umbilicus by Tape measure"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWaistCircumference
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 84 'cm'

Instance: HealthkitWalkingAsymmetryExample
InstanceOf: HealthkitWalkingAsymmetry
Usage: #example
Title: "Walking Asymmetry Example"
Description: "A conformant Walking Asymmetry instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:yq74Fz1XbZ7bGIyKVTOGvSQ1tV9enmATXcEUwZrsJRM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:MmjIkq0wz7Y7pGDvF-q_KZxSXfI4T-kxhIGTJmG94W0"
* status = #final
* code = $loinc#112432-0 "Walking asymmetry"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWalkingAsymmetryPercentage
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 1.4 '%'

Instance: HealthkitWalkingDoubleSupportExample
InstanceOf: HealthkitWalkingDoubleSupport
Usage: #example
Title: "Walking Double Support Example"
Description: "A conformant Walking Double Support instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:MzwIdsaSoPgjFy2ToisjIL1sJRhaIkhBEHcnWbEx4Eo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:DbBnCxyfns5hi2vepebv_Ti3rVe0atXXXM0_Lj3giWs"
* status = #final
* code = $loinc#112434-6 "Walking double support [Percentile]"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWalkingDoubleSupportPercentage
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 27 '%'

Instance: HealthkitWalkingHeartRateAverageExample
InstanceOf: HealthkitWalkingHeartRateAverage
Usage: #example
Title: "Walking Heart Rate Average Example"
Description: "A conformant Walking Heart Rate Average instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:5gstTOARsy-UL_kKN8aPQINjZUufJWVLl4HEG6KKDXI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:tl0x8xbTrb5UOyEwQkSn3TS53BPlrlfb1S2RzmZI0tw"
* status = #final
* code = HealthKitMeasurementCS#walking-heart-rate-average
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWalkingHeartRateAverage
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 98 '/min' "beats/minute"

Instance: HealthkitWalkingSpeedExample
InstanceOf: HealthkitWalkingSpeed
Usage: #example
Title: "Walking Speed Example"
Description: "A conformant Walking Speed instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:tFoblU9VVkoTx6JbH53bUwEMrnOoVNG-N31mrW1vkV4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:3tAKJOCDnUjzW3x8-wdxe20j5tG8SlqhwynMNjqIxgw"
* status = #final
* code = HealthKitMeasurementCS#walking-speed
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWalkingSpeed
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 1.32 'm/s'

Instance: HealthkitWalkingSteadinessExample
InstanceOf: HealthkitWalkingSteadiness
Usage: #example
Title: "Walking Steadiness Example"
Description: "A conformant Walking Steadiness instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Zixe-VId630LOt0xJIILjSB5bX3fZukDjSSCqZIqlDY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:eDUdUFU--gJp9Rl7vJlegJjtXdvCO5khldC3aByNiBk"
* status = #final
* code = HealthKitMeasurementCS#walking-steadiness
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierAppleWalkingSteadiness
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 82 '%'

Instance: HealthkitWalkingSteadinessNotificationExample
InstanceOf: HealthkitWalkingSteadinessNotification
Usage: #example
Title: "Walking Steadiness Notification Example"
Description: "A conformant Walking Steadiness Notification instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:FZju-Vo1_FFPV38NvXiM7se6csfsXyM6vIiLI-aLdX0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Q4QmgGKW_wU_tIVIlwBcXrkqEK8V3aWrInJGRGmftSU"
* status = #final
* code = HealthKitMeasurementCS#walking-steadiness-notification
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierAppleWalkingSteadinessEvent
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueCodeableConcept = HealthkitWalkingSteadinessNotificationCS#low "Low"
* component[notification-occurrence].code = https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-measurement#walking-steadiness-notification-occurrence
* component[notification-occurrence].valueCodeableConcept = HealthkitNotificationOccurrenceCS#initial "Initial"

Instance: HealthkitWalkingStepLengthExample
InstanceOf: HealthkitWalkingStepLength
Usage: #example
Title: "Walking Step Length Example"
Description: "A conformant Walking Step Length instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Jj7xSxd5_c9RYVvM2S_Axn2BcgFpDuEFazsxcCtw03I"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-dy5dm3smddAVn0vrJqdhEr_ui_9240fEsc52yRGnC8"
* status = #final
* code = HealthKitMeasurementCS#walking-step-length
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWalkingStepLength
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 72 'cm'

Instance: HealthkitWaterTemperatureExample
InstanceOf: HealthkitWaterTemperature
Usage: #example
Title: "Water Temperature Example"
Description: "A conformant Water Temperature instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:C_1giMPaaALRFgo70DolOIhYIJGN4saAKcyrs2Ib34k"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:uGDuPYl6UOngzEwXMBB33hlHxW8eH28eADyu4sYAz64"
* status = #final
* code = HealthKitMeasurementCS#water-temperature
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierWaterTemperature
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueQuantity = 24.5 'Cel'

Instance: HealthkitWheelchairUseExample
InstanceOf: HealthkitWheelchairUse
Usage: #example
Title: "Grove HealthKit Wheelchair Use Example"
Description: "A conformant Grove HealthKit Wheelchair Use instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:nGOmNvMuHcxyHbzR6_z53J9OCnYfy1lgvWe7cRSKSd8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:_5w9NUIcPgiuzwaP5jQKBAr3fBHCmJPhSVsciS5y2eY"
* status = #final
* code = HealthKitMeasurementCS#wheelchair-use
* extension[healthKitSourceType].valueCode = #HKCharacteristicTypeIdentifierWheelchairUse
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00-07:00"
* valueCodeableConcept = HealthkitWheelchairUseCS#uses-wheelchair "Uses wheelchair"

Instance: HealthkitWorkoutEffortScoreExample
InstanceOf: HealthkitWorkoutEffortScore
Usage: #example
Title: "Workout Effort Score Example"
Description: "A conformant Workout Effort Score instance."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:lb9EcqKIla4gqHlSPiMUzSZgkx4moCs3o6PlyEnMg0U"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:wa_fXIm4M5q-LMbrpQWOma9ABeCqkR8wJjJv4pyaAaI"
* status = #final
* code = HealthKitMeasurementCS#workout-effort-score
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierEstimatedWorkoutEffortScore
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T00:00:00-07:00"
* effectivePeriod.end = "2026-08-20T00:00:00-07:00"
* valueQuantity = 7 '{score}' "score"
