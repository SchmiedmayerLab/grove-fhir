//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: ProviderSourceRecordIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Provider Source Record Identifier"
Description: "The identifier namespace for a provider-scoped source record converted by the Provider adapter."
* id = "provider-source-record-id"
* name = "ProviderSourceRecordIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one provider-scoped source record without exposing its provider-native key. The provider account input is deployment-scoped and pseudonymous, and the raw source-native key is digest input only. Values use the versioned digest algorithm defined by the machine-readable adapter catalog. The complete system and value pair is business identity, never a FHIR Resource.id, access token, authorization credential, or permission to fetch provider data."
* uniqueId.type = #uri
* uniqueId.value = $providerSourceRecordId
* uniqueId.preferred = true

Instance: ProviderOutputIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Provider Output Identifier"
Description: "The identifier namespace for one source-neutral Observation emitted from a connected-provider record."
* id = "provider-output-id"
* name = "ProviderOutputIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies one logical output of a connected-provider conversion. One-to-many conversions use distinct output discriminants. Values are stable business identifiers and are not FHIR Resource.id values."
* uniqueId.type = #uri
* uniqueId.value = $providerOutputId
* uniqueId.preferred = true

Instance: ProviderProviderAccountIdentifier
InstanceOf: NamingSystem
Usage: #definition
Title: "Provider Account Identifier"
Description: "The namespace used when a deployment has a stable, evidenced provider-account identifier."
* id = "provider-account-id"
* name = "ProviderProviderAccountIdentifier"
* status = #active
* kind = #identifier
* date = "2026-08-20"
* publisher = "Schmiedmayer Lab"
* description = "Identifies a provider account only when the source supplies that identity. It is not required on clinical outputs, must not be synthesized from a person name, and is not an OAuth token or other authorization secret."
* uniqueId.type = #uri
* uniqueId.value = $providerAccountId
* uniqueId.preferred = true
