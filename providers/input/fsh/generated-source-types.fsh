//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// GENERATED FILE. Edit the adapter catalog and run
// `python3 Scripts/render-adapter-source-terminology.py`.
//

CodeSystem: ProviderSourceTypeCS
Id: provider-source-type
Title: "Provider Source Types"
Description: "The complete provider-qualified Google Health API, Oura, and Withings source inventory admitted or explicitly classified by version 0.3.0. The code is source lineage, not a clinical result code or fetch instruction."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #google-health-api/active-energy-burned "Google Health API: active-energy-burned" "The Google Health API active-energy-burned source type. Grove converts it to active-energy."
* #google-health-api/basal-energy-burned "Google Health API: basal-energy-burned" "The Google Health API basal-energy-burned source type. Grove converts it to basal-energy."
* #google-health-api/blood-glucose "Google Health API: blood-glucose" "The Google Health API blood-glucose source type. Grove converts it to blood-glucose-unspecified-specimen."
* #google-health-api/body-fat "Google Health API: body-fat" "The Google Health API body-fat source type. Grove converts it to body-fat-percentage."
* #google-health-api/core-body-temperature "Google Health API: core-body-temperature" "The Google Health API core-body-temperature source type. Grove converts it to body-temperature."
* #google-health-api/daily-oxygen-saturation "Google Health API: daily-oxygen-saturation" "The Google Health API daily-oxygen-saturation source type. Grove converts it to oxygen-saturation-daily-average."
* #google-health-api/daily-respiratory-rate "Google Health API: daily-respiratory-rate" "The Google Health API daily-respiratory-rate source type. Grove converts it to respiratory-rate-average."
* #google-health-api/daily-resting-heart-rate "Google Health API: daily-resting-heart-rate" "The Google Health API daily-resting-heart-rate source type. Grove converts it to resting-heart-rate."
* #google-health-api/distance "Google Health API: distance" "The Google Health API distance source type. Grove converts it to distance."
* #google-health-api/exercise "Google Health API: exercise" "The Google Health API exercise source type. Grove converts it to workout."
* #google-health-api/floors "Google Health API: floors" "The Google Health API floors source type. Grove converts it to flights-climbed."
* #google-health-api/heart-rate "Google Health API: heart-rate" "The Google Health API heart-rate source type. Grove admits no output for it."
* #google-health-api/heart-rate-variability "Google Health API: heart-rate-variability" "The Google Health API heart-rate-variability source type. Grove converts it to heart-rate-variability-rmssd and heart-rate-variability-sdnn."
* #google-health-api/height "Google Health API: height" "The Google Health API height source type. Grove converts it to body-height."
* #google-health-api/sleep "Google Health API: sleep" "The Google Health API sleep source type. Grove converts it to deep-sleep-duration, light-sleep-duration, rem-sleep-duration, sleep-awake-duration and sleep-duration."
* #google-health-api/steps "Google Health API: steps" "The Google Health API steps source type. Grove converts it to step-count."
* #google-health-api/vo2-max "Google Health API: vo2-max" "The Google Health API vo2-max source type. Grove converts it to vo2-max."
* #google-health-api/weight "Google Health API: weight" "The Google Health API weight source type. Grove converts it to body-weight."
* #oura/daily_activity "Oura: daily_activity" "The Oura daily_activity source type. Grove converts it to active-energy, distance and step-count."
* #oura/daily_cardiovascular_age "Oura: daily_cardiovascular_age" "The Oura daily_cardiovascular_age source type. Grove admits no output for it."
* #oura/daily_readiness "Oura: daily_readiness" "The Oura daily_readiness source type. Grove admits no output for it."
* #oura/daily_spo2 "Oura: daily_spo2" "The Oura daily_spo2 source type. Grove converts it to oxygen-saturation-daily-average."
* #oura/heartrate "Oura: heartrate" "The Oura heartrate source type. Grove admits no output for it."
* #oura/sleep "Oura: sleep" "The Oura sleep source type. Grove converts it to deep-sleep-duration, light-sleep-duration, rem-sleep-duration, respiratory-rate-average, sleep-awake-duration, sleep-duration and sleep-heart-rate."
* #oura/vO2_max "Oura: vO2_max" "The Oura vO2_max source type. Grove converts it to vo2-max."
* #oura/workout "Oura: workout" "The Oura workout source type. Grove converts it to workout."
* #withings/activityIntraday "Withings: activityIntraday" "The Withings activityIntraday source type. Grove admits no output for it."
* #withings/getactivity:calories "Withings: getactivity:calories" "The Withings getactivity:calories source type. Grove converts it to active-energy."
* #withings/getactivity:distance "Withings: getactivity:distance" "The Withings getactivity:distance source type. Grove converts it to distance."
* #withings/getactivity:steps "Withings: getactivity:steps" "The Withings getactivity:steps source type. Grove converts it to step-count."
* #withings/getmeas:1 "Withings: getmeas:1" "The Withings getmeas:1 source type. Grove converts it to body-weight."
* #withings/getmeas:10 "Withings: getmeas:10" "The Withings getmeas:10 source type. Grove converts it to blood-pressure."
* #withings/getmeas:11 "Withings: getmeas:11" "The Withings getmeas:11 source type. Grove converts it to heart-rate."
* #withings/getmeas:123 "Withings: getmeas:123" "The Withings getmeas:123 source type. Grove converts it to vo2-max."
* #withings/getmeas:130 "Withings: getmeas:130" "The Withings getmeas:130 source type. Grove admits no output for it."
* #withings/getmeas:135 "Withings: getmeas:135" "The Withings getmeas:135 source type. Grove admits no output for it."
* #withings/getmeas:136 "Withings: getmeas:136" "The Withings getmeas:136 source type. Grove admits no output for it."
* #withings/getmeas:137 "Withings: getmeas:137" "The Withings getmeas:137 source type. Grove admits no output for it."
* #withings/getmeas:138 "Withings: getmeas:138" "The Withings getmeas:138 source type. Grove admits no output for it."
* #withings/getmeas:139 "Withings: getmeas:139" "The Withings getmeas:139 source type. Grove admits no output for it."
* #withings/getmeas:155 "Withings: getmeas:155" "The Withings getmeas:155 source type. Grove admits no output for it."
* #withings/getmeas:167 "Withings: getmeas:167" "The Withings getmeas:167 source type. Grove admits no output for it."
* #withings/getmeas:168 "Withings: getmeas:168" "The Withings getmeas:168 source type. Grove converts it to extracellular-water-mass."
* #withings/getmeas:169 "Withings: getmeas:169" "The Withings getmeas:169 source type. Grove converts it to intracellular-water-mass."
* #withings/getmeas:170 "Withings: getmeas:170" "The Withings getmeas:170 source type. Grove admits no output for it."
* #withings/getmeas:174 "Withings: getmeas:174" "The Withings getmeas:174 source type. Grove admits no output for it."
* #withings/getmeas:175 "Withings: getmeas:175" "The Withings getmeas:175 source type. Grove admits no output for it."
* #withings/getmeas:196 "Withings: getmeas:196" "The Withings getmeas:196 source type. Grove converts it to electrodermal-activity."
* #withings/getmeas:4 "Withings: getmeas:4" "The Withings getmeas:4 source type. Grove converts it to body-height."
* #withings/getmeas:5 "Withings: getmeas:5" "The Withings getmeas:5 source type. Grove converts it to lean-body-mass."
* #withings/getmeas:54 "Withings: getmeas:54" "The Withings getmeas:54 source type. Grove converts it to oxygen-saturation."
* #withings/getmeas:6 "Withings: getmeas:6" "The Withings getmeas:6 source type. Grove converts it to body-fat-percentage."
* #withings/getmeas:71 "Withings: getmeas:71" "The Withings getmeas:71 source type. Grove converts it to body-temperature."
* #withings/getmeas:73 "Withings: getmeas:73" "The Withings getmeas:73 source type. Grove converts it to skin-temperature."
* #withings/getmeas:76 "Withings: getmeas:76" "The Withings getmeas:76 source type. Grove converts it to muscle-mass."
* #withings/getmeas:77 "Withings: getmeas:77" "The Withings getmeas:77 source type. Grove converts it to body-water-mass."
* #withings/getmeas:8 "Withings: getmeas:8" "The Withings getmeas:8 source type. Grove converts it to body-fat-mass."
* #withings/getmeas:88 "Withings: getmeas:88" "The Withings getmeas:88 source type. Grove converts it to bone-mass."
* #withings/getmeas:9 "Withings: getmeas:9" "The Withings getmeas:9 source type. Grove converts it to blood-pressure."
* #withings/getmeas:9+10 "Withings: getmeas:9+10 (atomic grouped mapping)" "The Withings getmeas:9+10 grouped mapping. Grove converts it to blood-pressure."
* #withings/getmeas:91 "Withings: getmeas:91" "The Withings getmeas:91 source type. Grove admits no output for it."
* #withings/getsummary:deepsleepduration "Withings: getsummary:deepsleepduration" "The Withings getsummary:deepsleepduration source type. Grove converts it to deep-sleep-duration."
* #withings/getsummary:hr_average "Withings: getsummary:hr_average" "The Withings getsummary:hr_average source type. Grove converts it to sleep-heart-rate and sleeping-heart-rate-average."
* #withings/getsummary:lightsleepduration "Withings: getsummary:lightsleepduration" "The Withings getsummary:lightsleepduration source type. Grove converts it to light-sleep-duration."
* #withings/getsummary:remsleepduration "Withings: getsummary:remsleepduration" "The Withings getsummary:remsleepduration source type. Grove converts it to rem-sleep-duration."
* #withings/getsummary:rr_average "Withings: getsummary:rr_average" "The Withings getsummary:rr_average source type. Grove converts it to respiratory-rate-average."
* #withings/getsummary:wakeupduration "Withings: getsummary:wakeupduration" "The Withings getsummary:wakeupduration source type. Grove converts it to sleep-awake-duration."
* #withings/getworkouts:interval "Withings: getworkouts:interval" "The Withings getworkouts:interval source type. Grove converts it to workout."
* #withings/sleepIntraday "Withings: sleepIntraday" "The Withings sleepIntraday source type. Grove admits no output for it."

ValueSet: ProviderSourceTypeVS
Id: provider-source-type
Title: "Provider Source Types"
Description: "The complete closed provider-qualified source-type inventory for the Provider 0.3.0 adapter."
* ^experimental = false
* include codes from system ProviderSourceTypeCS
