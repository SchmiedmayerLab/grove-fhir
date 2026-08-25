//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: SensorKitRecordIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "SensorKit Record Identifier"
Description: "The identifier namespace for one exact SensorKit-derived record."
* id = "sensorkit-record-id"
* name = "SensorKitRecordIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Grove Alliance"
* description = "Identifies one exact SensorKit-derived structured record or native recording. SensorKit does not publish a durable sample identifier, so a producer derives a stable lowercase UUID from the exact source stream and complete represented content. The complete system and value pair is a business identifier, never FHIR Resource.id."
* uniqueId.type = #uri
* uniqueId.value = $sensorKitRecordId
* uniqueId.preferred = true

Instance: SensorKitOutputIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "SensorKit Output Identifier"
Description: "The identifier namespace for one structured or native FHIR output derived from a SensorKit source record."
* id = "sensorkit-output-id"
* name = "SensorKitOutputIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Grove Alliance"
* description = "Identifies one logical output of a SensorKit conversion. Values use the UUIDv5 source-record-plus-discriminator algorithm in the machine catalog, are complete business identifiers, and are never copied into FHIR Resource.id."
* uniqueId.type = #uri
* uniqueId.value = $sensorKitOutputId
* uniqueId.preferred = true

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
