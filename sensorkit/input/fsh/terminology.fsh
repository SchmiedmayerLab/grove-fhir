//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: SensorKitConceptCS
Id: sensorkit-concept
Title: "SensorKit Adapter Concept"
Description: "Provider-specific SensorKit concepts for which no exact international code was identified."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #on-wrist-state "On-wrist state" "Whether the watch reported itself worn at the sampled instant."
* #wrist-location "Wrist location" "The wrist the wearer set the watch to, as the device reports it."
* #crown-orientation "Crown orientation" "The side the digital crown faces, as the device reports it."
* #device-usage-summary "Device usage summary" "One SRDeviceUsageReport covering a stated interval of device interaction."
* #screen-wakes "Screen wakes" "How many times the screen woke during the summarised interval."
* #messages-usage-summary "Messages usage summary" "The messaging counts one device-usage report covers."
* #incoming-messages "Incoming messages" "How many messages arrived during the summarised interval."
* #outgoing-messages "Outgoing messages" "How many messages were sent during the summarised interval."
* #unique-contacts "Unique contacts" "How many distinct correspondents the summarised interval involved."
* #phone-usage-summary "Phone usage summary" "The call counts one device-usage report covers."
* #incoming-calls "Incoming calls" "How many calls were received during the summarised interval."
* #outgoing-calls "Outgoing calls" "How many calls were placed during the summarised interval."
* #keyboard-metrics-summary "Keyboard metrics summary" "One SRKeyboardMetrics report covering a stated typing interval."
* #total-words "Total words" "How many words were typed during the summarised interval."
* #total-altered-words "Total altered words" "How many typed words were subsequently changed by the writer."
* #total-taps "Total taps" "How many key taps the summarised interval recorded."
* #total-deletes "Total deletes" "How many deletions the summarised interval recorded."
* #total-emojis "Total emojis" "How many emoji were entered during the summarised interval."
* #total-autocorrections "Total autocorrections" "How many autocorrections the keyboard applied."
* #total-pauses "Total pauses" "How many typing pauses the keyboard detected."
* #total-typing-episodes "Total typing episodes" "How many distinct typing episodes the interval contained."
* #typing-speed "Typing speed" "Typing rate over the summarised interval, in words per minute."
* #wrist-temperature-recording-summary "Wrist temperature recording summary" "One SRWristTemperatureSession covering a stated sleep interval. This is a wrist skin measurement, not body or basal body temperature."
* #sleep-session "Sleep session" "One contiguous sleep period the platform inferred."
* #accelerometer-recording-summary "Accelerometer recording summary" "Counts describing one accelerometer recording, without its samples."
* #sample-count "Sample count" "How many samples the summarised recording contains."
* #batch-count "Batch count" "How many delivery batches the summarised recording arrived in."
* #ppg-recording-summary "PPG recording summary" "Counts describing one photoplethysmography recording, without its samples."
* #record-count "Record count" "How many records the summarised recording contains."
* #optical-sample-count "Optical sample count" "How many optical samples the summarised recording contains."
* #accelerometer-sample-count "Accelerometer sample count" "How many accelerometer samples accompany the summarised recording."
* #unlocks "Unlocks" "How many device unlocks the summarised interval recorded."
* #visit-summary "Visit summary" "One SRVisit describing a stay at a categorised place."
* #visit-location-category "Visit location category" "The category the platform assigned the visited place; no coordinates are exchanged."
* #distance-from-home "Distance from home" "Straight-line distance from the wearer's home category to the visited place."
* #arrival-window "Arrival window" "The uncertainty window the platform gives for the arrival time."
* #departure-window "Departure window" "The uncertainty window the platform gives for the departure time."
* #ecg-session-guidance "ECG session guidance" "Whether the electrocardiogram session was taken under on-screen guidance."

CodeSystem: SensorKitValueCS
Id: sensorkit-value
Title: "SensorKit Adapter Value"
Description: "Closed coded values used by structured SensorKit-only adapter profiles."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #on-wrist "On wrist" "The device reported itself worn."
* #off-wrist "Off wrist" "The device reported itself not worn."
* #left "Left" "The wearer set the device to the left wrist."
* #right "Right" "The wearer set the device to the right wrist."
* #home "Home" "The platform categorised the visited place as the wearer's home."
* #work "Work" "The platform categorised the visited place as the wearer's workplace."
* #school "School" "The platform categorised the visited place as the wearer's place of study."
* #gym "Gym" "The platform categorised the visited place as a gym."
* #unknown "Unknown" "The platform assigned no category to the visited place."
* #guided "Guided" "The session ran with on-screen guidance."
* #unguided "Unguided" "The session ran without on-screen guidance."

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
* #rightArmMinusLeftArm "Right arm minus left arm" "Voltage measured as right arm minus left arm, the inverse of Lead I."
* #leftArmMinusRightArm "Left arm minus right arm" "Voltage measured as left arm minus right arm, equivalent to Lead I."

ValueSet: SensorKitECGLeadVS
Id: sensorkit-ecg-lead
Title: "SensorKit ECG Lead Orientation"
Description: "The exact SensorKit ECG lead orientation."
* ^experimental = false
* include codes from system SensorKitECGLeadCS
