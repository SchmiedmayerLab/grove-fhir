//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: SensorKitSourceType
Id: sensorkit-source-type
Title: "SensorKit Source Type"
Description: "The exact SensorKit stream from which this adapter resource was derived."
Context: Observation, DocumentReference
* value[x] 1..1 MS
* value[x] only code
* valueCode from SensorKitSourceTypeVS (required)

Extension: SensorKitWristTemperatureAlgorithmVersion
Id: sensorkit-wrist-temperature-algorithm-version
Title: "SensorKit Wrist Temperature Algorithm Version"
Description: "The exact opaque SRWristTemperatureSession.version string for the on-device algorithm that produced the session. SensorKit does not supply a method code or a complete method concept; placing a bare version in Observation.method would not identify the method, and Coding.version has code-system-version semantics."
Context: Observation
* value[x] 1..1 MS
* value[x] only string
