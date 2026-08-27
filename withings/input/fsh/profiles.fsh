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
Description: "The connected-provider Observation contract narrowed to Withings, for a value Withings' own algorithm produced over Withings' own inputs. A measurement two or more connected providers report stays source-neutral and is carried under the shared Provider Observation instead. The adapter does not authorize or fetch Withings data."
* extension[provider].valueCode = #withings (exactly)
