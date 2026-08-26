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

Extension: SensorKitVisitLocation
Id: sensorkit-visit-location
Title: "SensorKit Visit Location"
Description: "The place a visit was to, as SensorKit's own opaque identifier. It recurs across visits to the same place and never names or positions it, so it is carried as a business identifier rather than a Location resource: a Location holding nothing but this value would add a resource without adding a fact. Its recurrence is both the analytic value and the linkability risk, so a producer emits it only under explicit disclosure authorization. It belongs on a SensorKit visit Observation and nowhere else: the content-free SensorKit profiles must never carry it. Without it a visit still converts; repeat visits to one unnamed place simply cannot be recognised."
Context: Observation
* value[x] 1..1 MS
* value[x] only Identifier
* valueIdentifier.system 1..1 MS
* valueIdentifier.system = "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-visit-location-id" (exactly)
* valueIdentifier.value 1..1 MS


Extension: SensorKitWristTemperatureAlgorithmVersion
Id: sensorkit-wrist-temperature-algorithm-version
Title: "SensorKit Wrist Temperature Algorithm Version"
Description: "The SRWristTemperatureSession version: the on-device algorithm that produced the session. It describes how the samples were derived rather than being a result of its own, which is why it is an extension and not a component."
Context: Observation
* value[x] 1..1 MS
* value[x] only string
