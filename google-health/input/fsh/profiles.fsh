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
Description: "The connected-provider lineage and identity envelope narrowed to the Google Health API. It is directly paired with either a shared semantic profile or a Google Health-owned semantic profile; it does not replace that clinical claim. The adapter does not authorize or fetch Google Health API data."
* extension[provider].valueCode = #google-health-api (exactly)
