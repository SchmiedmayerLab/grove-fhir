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

Instance: HealthConnectClientRecordIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Health Connect Client Record Identifier"
Description: "The identifier namespace for the writer-assigned logical record behind a Health Connect Record, taken from metadata.clientRecordId."
* id = "health-connect-client-record-id"
* name = "HealthConnectClientRecordIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-24"
* publisher = "Schmiedmayer Lab"
* description = "Identifies the writer-assigned logical record behind a Health Connect Record, taken from metadata.clientRecordId. A writer that re-imports a measurement reuses this value and raises its clientRecordVersion, and the stored Record then carries a new metadata.id, so this namespace names the measurement while the record namespace names the exact row it was read from. The value is opaque writer text; compare the complete system and value pair."
* uniqueId.type = #uri
* uniqueId.value = $healthConnectClientRecordId
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

Instance: HealthConnectConversionIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Health Connect Conversion Identifier"
Description: "The identifier namespace for one durable conversion event represented by a Provenance Bundle entry."
* id = "health-connect-conversion-id"
* name = "HealthConnectConversionIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one conversion event from a nonempty sorted set of complete source Record identifiers and a durable positive event sequence. In FHIR R4 Provenance has no native identifier, so this complete pair is carried by the enclosing Grove exchange entry-identifier extension."
* uniqueId.type = #uri
* uniqueId.value = $healthConnectConversionId
* uniqueId.preferred = true

Instance: HealthConnectExchangeIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Health Connect Exchange Identifier"
Description: "The identifier namespace for one acknowledged Health Connect exchange event Bundle."
* id = "health-connect-exchange-id"
* name = "HealthConnectExchangeIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies the Grove Mobile collection Bundle for one event from a nonempty sorted set of complete source Record identifiers and a durable positive event sequence. It is carried in Bundle.identifier, not Resource.id."
* uniqueId.type = #uri
* uniqueId.value = $healthConnectExchangeId
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
