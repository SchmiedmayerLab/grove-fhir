//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Profile: OuraObservation
Parent: ProvidersObservation
Id: oura-observation
Title: "Oura Observation"
Description: "The connected-provider lineage and identity envelope narrowed to Oura. It is directly paired with either a shared semantic profile or an Oura-owned semantic profile; it does not replace that clinical claim. The adapter does not authorize or fetch Oura data."
* extension[provider].valueCode = #oura (exactly)
