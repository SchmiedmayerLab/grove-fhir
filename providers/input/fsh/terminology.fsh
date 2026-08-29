//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: ProviderProviderCS
Id: provider
Title: "Provider"
Description: "The upstream provider whose already-obtained source record was converted. These codes identify source systems; they do not authorize or fetch data."
* ^caseSensitive = true
* ^content = #complete
* ^experimental = false
* #google-health-api "Google Health API" "Records already obtained from the Google Health API."
* #oura "Oura" "Records already obtained from the Oura API."
* #withings "Withings" "Records already obtained from the Withings API."

ValueSet: ProviderProviderVS
Id: provider
Title: "Provider"
Description: "The closed set of connected providers admitted by the Grove FHIR contracts in this adapter package."
* include codes from system ProviderProviderCS
* ^experimental = false
