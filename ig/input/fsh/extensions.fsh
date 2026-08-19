//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: GroveInferredValue
Id: grove-inferred-value
Title: "Inferred Value"
Description: "Indicates that Grove inferred a coded value rather than receiving it directly from HealthKit."
* ^experimental = true
* ^context[+].type = #element
* ^context[=].expression = "Coding"
* value[x] only boolean
* valueBoolean 1..1


Extension: GroveRecordingMethod
Id: grove-recording-method
Title: "Recording Method"
Description: "How an observation was captured. HealthKit samples marked as user-entered use `manual-entry`."
* ^experimental = true
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only Coding
* valueCoding 1..1
* valueCoding from GroveRecordingMethodVS (required)


Extension: GrovePlatformMetadata
Id: grove-platform-metadata
Title: "HealthKit Metadata Entry"
Description: "One typed HealthKit metadata entry preserved by Grove when the current conversion has no explicit FHIR mapping for the key."
* ^experimental = true
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] 0..0
* extension contains key 1..1 and value 1..1
* extension[key].value[x] only Coding
* extension[key].valueCoding from GrovePlatformMetadataKeyVS (extensible)
* extension[key] ^short = "HealthKit metadata key"
* extension[value].value[x] only string or boolean or decimal or dateTime or Coding or Quantity
* extension[value] ^short = "Metadata value represented with its FHIR datatype"
