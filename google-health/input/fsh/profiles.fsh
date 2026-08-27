//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Profile: GoogleHealthObservation
Parent: ProvidersObservation
Id: google-health-observation
Title: "Google Health Observation"
Description: "The connected-provider Observation contract narrowed to the Google Health API, for a value Google's own algorithm produced over Google's own inputs. A measurement two or more connected providers report stays source-neutral and is carried under the shared Provider Observation instead. The adapter does not authorize or fetch Google Health API data."
* extension[provider].valueCode = #google-health-api (exactly)
