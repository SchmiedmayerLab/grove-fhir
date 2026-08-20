//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: SensorKitSourceTypeCS
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "Closed source tokens for the SensorKit platform inventory admitted by Grove FHIR 0.2.0."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #accelerometer "Accelerometer"
* #acoustic-settings "Acoustic settings"
* #ambient-light "Ambient light"
* #ambient-pressure "Ambient pressure"
* #device-usage "Device usage report"
* #ecg "Electrocardiogram"
* #face-metrics "Face metrics"
* #headphone-motion "Headphone motion"
* #headphone-settings "Headphone settings"
* #heart-rate "High-frequency heart rate"
* #keyboard-metrics "Keyboard metrics"
* #media-events "Media events"
* #messages-usage "Messages usage report"
* #odometer "Odometer"
* #on-wrist "On-wrist state"
* #pedometer "Pedometer data"
* #phone-usage "Phone usage report"
* #ppg "Photoplethysmogram"
* #rotation-rate "Rotation rate"
* #siri-speech-metrics "Siri speech metrics"
* #sleep-sessions "Sleep sessions"
* #telephony-speech-metrics "Telephony speech metrics"
* #visits "Visits"
* #wrist-temperature "Wrist temperature"

ValueSet: SensorKitSourceTypeVS
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "The exact SensorKit source stream token."
* ^experimental = false
* include codes from system SensorKitSourceTypeCS

CodeSystem: SensorKitConceptCS
Id: sensorkit-concept
Title: "SensorKit Adapter Concept"
Description: "Provider-specific SensorKit concepts for which no exact international code was identified."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #on-wrist-state "On-wrist state"
* #wrist-location "Wrist location"
* #crown-orientation "Crown orientation"
* #device-usage-summary "Device usage summary"
* #screen-wakes "Screen wakes"
* #unlocks "Unlocks"
* #visit-summary "Visit summary"
* #visit-location-category "Visit location category"
* #distance-from-home "Distance from home"
* #arrival-window "Arrival window"
* #departure-window "Departure window"
* #ecg-session-guidance "ECG session guidance"

CodeSystem: SensorKitValueCS
Id: sensorkit-value
Title: "SensorKit Adapter Value"
Description: "Closed coded values used by structured SensorKit-only adapter profiles."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #on-wrist "On wrist"
* #off-wrist "Off wrist"
* #left "Left"
* #right "Right"
* #home "Home"
* #work "Work"
* #school "School"
* #gym "Gym"
* #unknown "Unknown"
* #guided "Guided"
* #unguided "Unguided"

ValueSet: SensorKitWearStateVS
Id: sensorkit-wear-state
Title: "SensorKit Wear State"
Description: "Whether SensorKit reports that the watch is on or off the wrist."
* ^experimental = false
* $sensorKitValue#on-wrist
* $sensorKitValue#off-wrist

ValueSet: SensorKitSideVS
Id: sensorkit-side
Title: "SensorKit Side"
Description: "The closed left or right placement values reported by SensorKit."
* ^experimental = false
* $sensorKitValue#left
* $sensorKitValue#right

ValueSet: SensorKitVisitLocationCategoryVS
Id: sensorkit-visit-location-category
Title: "SensorKit Visit Location Category"
Description: "The closed visit location categories reported by SensorKit."
* ^experimental = false
* $sensorKitValue#home
* $sensorKitValue#work
* $sensorKitValue#school
* $sensorKitValue#gym
* $sensorKitValue#unknown

ValueSet: SensorKitECGSessionGuidanceVS
Id: sensorkit-ecg-session-guidance
Title: "SensorKit ECG Session Guidance"
Description: "The exact guided or unguided session mode reported by SensorKit."
* ^experimental = false
* $sensorKitValue#guided
* $sensorKitValue#unguided

CodeSystem: SensorKitECGLeadCS
Id: sensorkit-ecg-lead
Title: "SensorKit ECG Lead Orientation"
Description: "Exact SRElectrocardiogramSample.Lead cases retained as an adapter coding on the ECG component."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #rightArmMinusLeftArm "Right arm minus left arm"
* #leftArmMinusRightArm "Left arm minus right arm"

ValueSet: SensorKitECGLeadVS
Id: sensorkit-ecg-lead
Title: "SensorKit ECG Lead Orientation"
Description: "The exact SensorKit ECG lead orientation."
* ^experimental = false
* include codes from system SensorKitECGLeadCS
