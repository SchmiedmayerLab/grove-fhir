//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: ConnectedHealthSourceRecordIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Connected Health Source Record Identifier"
Description: "The identifier namespace for a provider-scoped source record converted by the Connected Health adapter."
* id = "connected-health-source-record-id"
* name = "ConnectedHealthSourceRecordIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one provider-scoped source record without exposing its provider-native key. The provider account input is deployment-scoped and pseudonymous, and the raw source-native key is digest input only. Values use the versioned digest algorithm defined by the machine-readable adapter catalog. The complete system and value pair is business identity, never a FHIR Resource.id, access token, authorization credential, or permission to fetch provider data."
* uniqueId.type = #uri
* uniqueId.value = $connectedHealthSourceRecordId
* uniqueId.preferred = true

Instance: ConnectedHealthOutputIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Connected Health Output Identifier"
Description: "The identifier namespace for one source-neutral Observation emitted from a connected-provider record."
* id = "connected-health-output-id"
* name = "ConnectedHealthOutputIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one logical output of a connected-provider conversion. One-to-many conversions use distinct output discriminants. Values are stable business identifiers and are not FHIR Resource.id values."
* uniqueId.type = #uri
* uniqueId.value = $connectedHealthOutputId
* uniqueId.preferred = true

Instance: ConnectedHealthConversionIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Connected Health Conversion Identifier"
Description: "The identifier namespace for one durable connected-provider conversion event."
* id = "connected-health-conversion-id"
* name = "ConnectedHealthConversionIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one conversion event over an exact source-record identifier set and durable positive event sequence. FHIR R4 Provenance has no native identifier, so the pair is carried by the enclosing exchange entry-identifier extension."
* uniqueId.type = #uri
* uniqueId.value = $connectedHealthConversionId
* uniqueId.preferred = true

Instance: ConnectedHealthExchangeIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Connected Health Exchange Identifier"
Description: "The identifier namespace for one acknowledged connected-provider collection Bundle."
* id = "connected-health-exchange-id"
* name = "ConnectedHealthExchangeIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one Grove Mobile collection Bundle event. The value is carried in Bundle.identifier and does not define transport, receiver, storage, or authentication policy."
* uniqueId.type = #uri
* uniqueId.value = $connectedHealthExchangeId
* uniqueId.preferred = true

Instance: ConnectedHealthProviderAccountIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Connected Health Provider Account Identifier"
Description: "The namespace used when a deployment has a stable, evidenced provider-account identifier."
* id = "connected-health-provider-account-id"
* name = "ConnectedHealthProviderAccountIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies a provider account only when the source supplies that identity. It is not required on clinical outputs, must not be synthesized from a person name, and is not an OAuth token or other authorization secret."
* uniqueId.type = #uri
* uniqueId.value = $connectedHealthProviderAccountId
* uniqueId.preferred = true
