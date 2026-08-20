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

CodeSystem: ConnectedHealthSourceTypeCS
Id: connected-health-source-type
Title: "Connected Health Source Types"
Description: "The complete provider-qualified Google Health API, Oura, and Withings source inventory admitted or explicitly classified by version 0.2.0. The code is source lineage, not a clinical result code or fetch instruction."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #google-health-api/active-energy-burned "Google Health API: active-energy-burned"
* #google-health-api/basal-energy-burned "Google Health API: basal-energy-burned"
* #google-health-api/blood-glucose "Google Health API: blood-glucose"
* #google-health-api/body-fat "Google Health API: body-fat"
* #google-health-api/core-body-temperature "Google Health API: core-body-temperature"
* #google-health-api/daily-oxygen-saturation "Google Health API: daily-oxygen-saturation"
* #google-health-api/daily-respiratory-rate "Google Health API: daily-respiratory-rate"
* #google-health-api/daily-resting-heart-rate "Google Health API: daily-resting-heart-rate"
* #google-health-api/distance "Google Health API: distance"
* #google-health-api/exercise "Google Health API: exercise"
* #google-health-api/floors "Google Health API: floors"
* #google-health-api/heart-rate "Google Health API: heart-rate"
* #google-health-api/heart-rate-variability "Google Health API: heart-rate-variability"
* #google-health-api/height "Google Health API: height"
* #google-health-api/sleep "Google Health API: sleep"
* #google-health-api/steps "Google Health API: steps"
* #google-health-api/vo2-max "Google Health API: vo2-max"
* #google-health-api/weight "Google Health API: weight"
* #oura/daily_activity "Oura: daily_activity"
* #oura/daily_cardiovascular_age "Oura: daily_cardiovascular_age"
* #oura/daily_readiness "Oura: daily_readiness"
* #oura/daily_spo2 "Oura: daily_spo2"
* #oura/heartrate "Oura: heartrate"
* #oura/sleep "Oura: sleep"
* #oura/vO2_max "Oura: vO2_max"
* #oura/workout "Oura: workout"
* #withings/activityIntraday "Withings: activityIntraday"
* #withings/getactivity:calories "Withings: getactivity:calories"
* #withings/getactivity:distance "Withings: getactivity:distance"
* #withings/getactivity:steps "Withings: getactivity:steps"
* #withings/getmeas:1 "Withings: getmeas:1"
* #withings/getmeas:10 "Withings: getmeas:10"
* #withings/getmeas:11 "Withings: getmeas:11"
* #withings/getmeas:123 "Withings: getmeas:123"
* #withings/getmeas:130 "Withings: getmeas:130"
* #withings/getmeas:135 "Withings: getmeas:135"
* #withings/getmeas:136 "Withings: getmeas:136"
* #withings/getmeas:137 "Withings: getmeas:137"
* #withings/getmeas:138 "Withings: getmeas:138"
* #withings/getmeas:139 "Withings: getmeas:139"
* #withings/getmeas:155 "Withings: getmeas:155"
* #withings/getmeas:167 "Withings: getmeas:167"
* #withings/getmeas:168 "Withings: getmeas:168"
* #withings/getmeas:169 "Withings: getmeas:169"
* #withings/getmeas:170 "Withings: getmeas:170"
* #withings/getmeas:174 "Withings: getmeas:174"
* #withings/getmeas:175 "Withings: getmeas:175"
* #withings/getmeas:196 "Withings: getmeas:196"
* #withings/getmeas:4 "Withings: getmeas:4"
* #withings/getmeas:5 "Withings: getmeas:5"
* #withings/getmeas:54 "Withings: getmeas:54"
* #withings/getmeas:6 "Withings: getmeas:6"
* #withings/getmeas:71 "Withings: getmeas:71"
* #withings/getmeas:73 "Withings: getmeas:73"
* #withings/getmeas:76 "Withings: getmeas:76"
* #withings/getmeas:77 "Withings: getmeas:77"
* #withings/getmeas:8 "Withings: getmeas:8"
* #withings/getmeas:88 "Withings: getmeas:88"
* #withings/getmeas:9 "Withings: getmeas:9"
* #withings/getmeas:9+10 "Withings: getmeas:9+10 (atomic grouped mapping)"
* #withings/getmeas:91 "Withings: getmeas:91"
* #withings/getsummary:deepsleepduration "Withings: getsummary:deepsleepduration"
* #withings/getsummary:hr_average "Withings: getsummary:hr_average"
* #withings/getsummary:lightsleepduration "Withings: getsummary:lightsleepduration"
* #withings/getsummary:remsleepduration "Withings: getsummary:remsleepduration"
* #withings/getsummary:rr_average "Withings: getsummary:rr_average"
* #withings/getsummary:wakeupduration "Withings: getsummary:wakeupduration"
* #withings/getworkouts:interval "Withings: getworkouts:interval"
* #withings/sleepIntraday "Withings: sleepIntraday"

ValueSet: ConnectedHealthSourceTypeVS
Id: connected-health-source-type
Title: "Connected Health Source Types"
Description: "The complete closed provider-qualified source-type inventory for the Connected Health 0.2.0 adapter."
* ^experimental = false
* include codes from system ConnectedHealthSourceTypeCS
