//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// SensorKit sensor streams. Codes are SRSensor raw values, pinned to the
// framework by GroveSensorKitFHIRTests.

CodeSystem: GroveSensorKitSampleType
Id: sensorkit-sample-type
Title: "SensorKit Sample Types"
Description: """
Apple SensorKit sensor streams, coded by their SensorKit identifiers. Used as
`Observation.code` for summary observations derived from a SensorKit stream, and as
the format discriminator for raw sensor batches. The identifier space belongs to
Apple and grows with the platform, so this system is a fragment.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/sensorkit-sample-type"
* ^valueSet = "https://grovealliance.org/fhir/platforms/ValueSet/sensorkit-sample-type"
* ^experimental = false
* ^caseSensitive = true
* ^content = #fragment
* #com.apple.SensorKit.deviceUsageReport "Device Usage" "Screen wakes, unlocks, and app/notification/web usage summaries."
* #com.apple.SensorKit.onWristState "On-Wrist State" "Whether the watch is being worn, with wrist and crown placement."
* #com.apple.SensorKit.visits "Visits" "Coarse location-category visits (home, work, school, gym) without coordinates."
* #com.apple.SensorKit.ECG "Electrocardiogram" "Raw single-lead ECG voltage streams."
* #com.apple.SensorKit.PPG "Photoplethysmogram" "Raw PPG optical sensor streams."
* #com.apple.SensorKit.wristTemperature "Wrist Temperature" "Sleep-time wrist temperature streams."
* #com.apple.SensorKit.heart.rate "Heart Rate" "SensorKit heart-rate estimates."
* #com.apple.SensorKit.pedometer.data "Pedometer" "Step cadence and pace streams."
* #com.apple.SensorKit.motion.accelerometer "Accelerometer" "Raw accelerometer streams."
* #com.apple.SensorKit.als "Ambient Light" "Ambient light level samples."
* #com.apple.SensorKit.ambientPressure "Ambient Pressure" "Barometric pressure samples."

ValueSet: GroveSensorKitSampleTypeVS
Id: sensorkit-sample-type
Title: "SensorKit Sample Types"
Description: "All SensorKit sensor streams. Bind extensibly: the identifier space is Apple's and grows with the platform."
* ^url = "https://grovealliance.org/fhir/platforms/ValueSet/sensorkit-sample-type"
* ^experimental = false
* include codes from system GroveSensorKitSampleType

