//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Profile: WithingsObservation
Parent: ProvidersObservation
Id: withings-observation
Title: "Withings Observation"
Description: "The connected-provider lineage and identity envelope narrowed to Withings. It is directly paired with either a shared semantic profile or a Withings-owned semantic profile; it does not replace that clinical claim. The adapter does not authorize or fetch Withings data."
* extension[provider].valueCode = #withings (exactly)
