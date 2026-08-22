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
