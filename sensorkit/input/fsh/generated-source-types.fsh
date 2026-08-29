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

CodeSystem: SensorKitConceptPropertyCS
Id: sensorkit-concept-property
Title: "SensorKit Concept Properties"
Description: "The concept properties the SensorKit source-type code system carries."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #identifier "Identifier" "The SRSensor value a producer reads back."
* #documentation "Documentation" "Canonical Apple documentation page for the constant."

CodeSystem: SensorKitSourceTypeCS
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "The 22 public SensorKit sensors published by the iPhoneOS 26.5 SDK baseline (Xcode 26.6, build 17F113). Membership is derived from, and verified against, sensorkit/input/data/sensorkit-inventory.json. A code is a Grove token rather than an Apple string; the SRSensor value a producer reads back is carried as the identifier property."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "SensorKit API symbols originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* ^property[0].code = #identifier
* ^property[0].uri = "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept-property#identifier"
* ^property[0].description = "The SRSensor value this token names, which is what a producer reads back."
* ^property[0].type = #string
* ^property[1].code = #documentation
* ^property[1].uri = "https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-concept-property#documentation"
* ^property[1].description = "Canonical Apple documentation page for the SRSensor constant, recorded verbatim from Apple's published symbol index."
* ^property[1].type = #string
* #accelerometer "Accelerometer" "The SensorKit SRSensor.accelerometer source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-accelerometer-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #accelerometer ^property[0].code = #identifier
* #accelerometer ^property[0].valueString = "com.apple.SensorKit.motion.accelerometer"
* #accelerometer ^property[1].code = #documentation
* #accelerometer ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/accelerometer"
* #acoustic-settings "Acoustic settings" "The SensorKit SRSensor.acousticSettings source type. Grove admits no output for it. The Grove FHIR contracts publish no admitted output contract for this stable platform symbol."
* #acoustic-settings ^property[0].code = #identifier
* #acoustic-settings ^property[0].valueString = "com.apple.SensorKit.hearing.acousticSettings"
* #acoustic-settings ^property[1].code = #documentation
* #acoustic-settings ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/acousticsettings"
* #ambient-light "Ambient light" "The SensorKit SRSensor.ambientLightSensor source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #ambient-light ^property[0].code = #identifier
* #ambient-light ^property[0].valueString = "com.apple.SensorKit.als"
* #ambient-light ^property[1].code = #documentation
* #ambient-light ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/ambientlightsensor"
* #ambient-pressure "Ambient pressure" "The SensorKit SRSensor.ambientPressure source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #ambient-pressure ^property[0].code = #identifier
* #ambient-pressure ^property[0].valueString = "com.apple.SensorKit.ambientPressure"
* #ambient-pressure ^property[1].code = #documentation
* #ambient-pressure ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/ambientpressure"
* #device-usage "Device usage report" "The SensorKit SRSensor.deviceUsageReport source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-device-usage-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #device-usage ^property[0].code = #identifier
* #device-usage ^property[0].valueString = "com.apple.SensorKit.deviceUsageReport"
* #device-usage ^property[1].code = #documentation
* #device-usage ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/deviceusagereport"
* #ecg "Electrocardiogram" "The SensorKit SRSensor.electrocardiogram source type. Grove admits a structured Observation with the direct `meta.profile` claims grove-sensor-ecg-observation and sensorkit-ecg-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #ecg ^property[0].code = #identifier
* #ecg ^property[0].valueString = "com.apple.SensorKit.ECG"
* #ecg ^property[1].code = #documentation
* #ecg ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/electrocardiogram"
* #face-metrics "Face metrics" "The SensorKit SRSensor.faceMetrics source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #face-metrics ^property[0].code = #identifier
* #face-metrics ^property[0].valueString = "com.apple.SensorKit.faceMetrics"
* #face-metrics ^property[1].code = #documentation
* #face-metrics ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/facemetrics"
* #heart-rate "High-frequency heart rate" "The SensorKit SRSensor.heartRate source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #heart-rate ^property[0].code = #identifier
* #heart-rate ^property[0].valueString = "com.apple.SensorKit.heart.rate"
* #heart-rate ^property[1].code = #documentation
* #heart-rate ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/heartrate"
* #keyboard-metrics "Keyboard metrics" "The SensorKit SRSensor.keyboardMetrics source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-keyboard-metrics-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #keyboard-metrics ^property[0].code = #identifier
* #keyboard-metrics ^property[0].valueString = "com.apple.SensorKit.keyboardMetrics"
* #keyboard-metrics ^property[1].code = #documentation
* #keyboard-metrics ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/keyboardmetrics"
* #media-events "Media events" "The SensorKit SRSensor.mediaEvents source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #media-events ^property[0].code = #identifier
* #media-events ^property[0].valueString = "com.apple.SensorKit.mediaEvents"
* #media-events ^property[1].code = #documentation
* #media-events ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/mediaevents"
* #messages-usage "Messages usage report" "The SensorKit SRSensor.messagesUsageReport source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-messages-usage-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #messages-usage ^property[0].code = #identifier
* #messages-usage ^property[0].valueString = "com.apple.SensorKit.messagesUsageReport"
* #messages-usage ^property[1].code = #documentation
* #messages-usage ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/messagesusagereport"
* #odometer "Odometer" "The SensorKit SRSensor.odometer source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #odometer ^property[0].code = #identifier
* #odometer ^property[0].valueString = "com.apple.SensorKit.odometer"
* #odometer ^property[1].code = #documentation
* #odometer ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/odometer"
* #on-wrist "On-wrist state" "The SensorKit SRSensor.onWristState source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-on-wrist-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #on-wrist ^property[0].code = #identifier
* #on-wrist ^property[0].valueString = "com.apple.SensorKit.onWristState"
* #on-wrist ^property[1].code = #documentation
* #on-wrist ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/onwriststate"
* #pedometer "Pedometer data" "The SensorKit SRSensor.pedometerData source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #pedometer ^property[0].code = #identifier
* #pedometer ^property[0].valueString = "com.apple.SensorKit.pedometer.data"
* #pedometer ^property[1].code = #documentation
* #pedometer ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/pedometerdata"
* #phone-usage "Phone usage report" "The SensorKit SRSensor.phoneUsageReport source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-phone-usage-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #phone-usage ^property[0].code = #identifier
* #phone-usage ^property[0].valueString = "com.apple.SensorKit.phoneUsageReport"
* #phone-usage ^property[1].code = #documentation
* #phone-usage ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/phoneusagereport"
* #ppg "Photoplethysmogram" "The SensorKit SRSensor.photoplethysmogram source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-ppg-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #ppg ^property[0].code = #identifier
* #ppg ^property[0].valueString = "com.apple.SensorKit.PPG"
* #ppg ^property[1].code = #documentation
* #ppg ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/photoplethysmogram"
* #rotation-rate "Rotation rate" "The SensorKit SRSensor.rotationRate source type. Grove admits a structured Observation with the direct `meta.profile` claims grove-sensor-sampled-data-observation and sensorkit-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #rotation-rate ^property[0].code = #identifier
* #rotation-rate ^property[0].valueString = "com.apple.SensorKit.motion.gyroscope"
* #rotation-rate ^property[1].code = #documentation
* #rotation-rate ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/rotationrate"
* #siri-speech-metrics "Siri speech metrics" "The SensorKit SRSensor.siriSpeechMetrics source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #siri-speech-metrics ^property[0].code = #identifier
* #siri-speech-metrics ^property[0].valueString = "com.apple.SensorKit.speechMetrics.siri"
* #siri-speech-metrics ^property[1].code = #documentation
* #siri-speech-metrics ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/sirispeechmetrics"
* #sleep-sessions "Sleep sessions" "The SensorKit SRSensor.sleepSessions source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-sleep-session-observation."
* #sleep-sessions ^property[0].code = #identifier
* #sleep-sessions ^property[0].valueString = "com.apple.SensorKit.sleep.sessions"
* #sleep-sessions ^property[1].code = #documentation
* #sleep-sessions ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/sleepsessions"
* #telephony-speech-metrics "Telephony speech metrics" "The SensorKit SRSensor.telephonySpeechMetrics source type. Grove admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #telephony-speech-metrics ^property[0].code = #identifier
* #telephony-speech-metrics ^property[0].valueString = "com.apple.SensorKit.speechMetrics.telephony"
* #telephony-speech-metrics ^property[1].code = #documentation
* #telephony-speech-metrics ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/telephonyspeechmetrics"
* #visits "Visits" "The SensorKit SRSensor.visits source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-visit-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #visits ^property[0].code = #identifier
* #visits ^property[0].valueString = "com.apple.SensorKit.visits"
* #visits ^property[1].code = #documentation
* #visits ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/visits"
* #wrist-temperature "Wrist temperature" "The SensorKit SRSensor.wristTemperature source type. Grove admits a structured Observation with the direct `meta.profile` claim sensorkit-wrist-temperature-observation. It also admits a Recording Document with the direct `meta.profile` claims grove-sensor-recording-document and sensorkit-recording-document."
* #wrist-temperature ^property[0].code = #identifier
* #wrist-temperature ^property[0].valueString = "com.apple.SensorKit.wristTemperature"
* #wrist-temperature ^property[1].code = #documentation
* #wrist-temperature ^property[1].valueString = "https://developer.apple.com/documentation/sensorkit/srsensor/wristtemperature"

ValueSet: SensorKitSourceTypeVS
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "The exact SensorKit source stream token."
* ^experimental = false
* include codes from system SensorKitSourceTypeCS
