//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: ConnectedHealthProvider
Id: connected-health-provider
Title: "Connected Health Provider"
Description: "Identifies the upstream provider of an already-obtained source record. It is source lineage, not a fetch instruction, authorization grant, account identifier, or clinical method."
Context: Observation, DocumentReference
* value[x] only code
* valueCode 1..1
* valueCode from ConnectedHealthProviderVS (required)

Extension: ConnectedHealthSourceType
Id: connected-health-source-type
Title: "Connected Health Source Type"
Description: "Identifies the exact provider-qualified source type of an already-obtained record. It is source lineage, not a clinical result code, fetch instruction, or authorization grant."
Context: Observation, DocumentReference
* value[x] only code
* valueCode 1..1
* valueCode from ConnectedHealthSourceTypeVS (required)
