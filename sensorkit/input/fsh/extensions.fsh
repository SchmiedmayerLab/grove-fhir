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

Extension: SensorKitECGSessionGuidance
Id: sensorkit-ecg-session-guidance
Title: "SensorKit ECG Session Guidance"
Description: "The exact guided or unguided session mode reported by the SensorKit ECG session. Per-voltage flags and complete native session detail remain in the required linked Recording Document."
Context: Observation
* value[x] 1..1 MS
* value[x] only code
* valueCode from SensorKitECGSessionGuidanceVS (required)
