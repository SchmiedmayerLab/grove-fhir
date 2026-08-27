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
Description: "The connected-provider Observation contract narrowed to Oura, for a value Oura's own algorithm produced over Oura's own inputs. A measurement two or more connected providers report stays source-neutral and is carried under the shared Provider Observation instead. The adapter does not authorize or fetch Oura data."
* extension[provider].valueCode = #oura (exactly)
