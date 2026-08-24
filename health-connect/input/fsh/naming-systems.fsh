//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: HealthConnectRecordIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Health Connect Record Identifier"
Description: "The identifier namespace for the repository-scoped identity of a Health Connect Record."
* id = "health-connect-record-id"
* name = "HealthConnectRecordIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one source Record within a specific Health Connect repository without exposing the repository scope or platform-assigned Metadata.id. Values use the versioned digest algorithm defined by this guide. Every FHIR output derived from one Record carries the same identifier. Compare the complete system and value pair; equal pairs identify the same scoped source Record. The digest is an identity and synchronization key, not an access-control or confidentiality boundary."
* uniqueId.type = #uri
* uniqueId.value = $healthConnectRecordId
* uniqueId.preferred = true


Instance: HealthConnectOutputIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Health Connect Output Identifier"
Description: "The identifier namespace for the stable identity of one FHIR Observation emitted by a Health Connect conversion."
* id = "health-connect-output-id"
* name = "HealthConnectOutputIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one logical FHIR Observation emitted from a Health Connect Record. A one-to-one conversion and every element of a one-to-many conversion receive distinct stable values. Values use the versioned digest algorithm defined by this guide so clinical values are not exposed directly in identifier indexes. The digest is a business identifier for synchronization and deduplication, not a FHIR Resource.id, version id, access-control mechanism, or confidentiality boundary."
* uniqueId.type = #uri
* uniqueId.value = $healthConnectOutputId
* uniqueId.preferred = true

Instance: HealthConnectSpecimenIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Health Connect Specimen Identifier"
Description: "The identifier namespace for a specimen node deterministically derived from one Health Connect BloodGlucoseRecord and its admitted specimen-source token."
* id = "health-connect-specimen-id"
* name = "HealthConnectSpecimenIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one synthesized Specimen resource by the complete source Record identifier and exact supported Health Connect specimen-source token. It is a business identifier, never a FHIR Resource.id."
* uniqueId.type = #uri
* uniqueId.value = $healthConnectSpecimenId
* uniqueId.preferred = true

Instance: AndroidPackageName
InstanceOf: NamingSystem
Usage: #definition
Title: "Android Package Name"
Description: "The identifier namespace for an Android application package name used on a Grove Application Device."
* id = "android-package-name"
* name = "AndroidPackageName"
* status = #active
* kind = #identifier
* date = "2026-08-19"
* publisher = "Schmiedmayer Lab"
* description = "Identifies an Android application product by package name. Health Connect DataOrigin.packageName uses this namespace. Together with a typed application version when that version is independently known, it identifies an application product and build, not an installation, host, account, or person."
* uniqueId.type = #uri
* uniqueId.value = $androidPackageName
* uniqueId.preferred = true
