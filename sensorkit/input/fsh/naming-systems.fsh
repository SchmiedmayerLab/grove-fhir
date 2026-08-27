//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: SensorKitVisitLocationIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "SensorKit Visit Location Identifier"
Description: "The identifier namespace for one SensorKit visit location."
* id = "sensorkit-visit-location-id"
* name = "SensorKitVisitLocationIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-25"
* publisher = "Grove Alliance"
* description = "Identifies the place a SensorKit visit was to. The value is SensorKit's own opaque location identifier, which recurs across visits to the same place and never names or positions it. Because that recurrence is exactly what makes it linkable, a producer emits this identifier only under explicit disclosure authorization."
* uniqueId.type = #uri
* uniqueId.value = "https://grovealliance.org/fhir/sensorkit/NamingSystem/sensorkit-visit-location-id"
* uniqueId.preferred = true
