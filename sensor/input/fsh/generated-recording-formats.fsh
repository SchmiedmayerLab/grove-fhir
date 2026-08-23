//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// GENERATED FILE. Edit catalog/format-registry.json and run
// `python3 Scripts/render-format-registry.py`.
//

CodeSystem: GroveRecordingFormatCS
Id: grove-recording-format
Title: "Grove Recording Format"
Description: "The closed registry of payload formats a Grove recording DocumentReference may declare in content.format. Each code is fully specified in the format registry and on the formats page, so a receiver can parse any admitted payload from the guide alone."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #grove-csv-1 "Grove CSV 1" "One header row naming every column in order, then one row per source sample in source order."
* #fhir-json-1 "FHIR JSON Array 1" "A single JSON array; each element is one complete FHIR R4 resource in FHIR JSON representation, in source sample order."
* #native-json-1 "Native JSON 1" "The producer's exact native JSON serialization of one source batch, byte-preserved."
* #provider-json-1 "Provider JSON 1" "The verbatim JSON payload returned by the provider API call that produced the batch, byte-preserved apart from transport framing."
* #grove-ppg-1 "Grove PPG Binary 1" "Varint record count, then that many PPG records."
* #grove-batch-archive-1 "Grove Batch Archive 1" "A POSIX ustar tar stream, optionally compressed as one whole; every archived file is itself a registry-format payload or a documented sidecar of one."
* #fhir-resource-1 "FHIR Resource 1" "One complete provider-issued FHIR resource in FHIR JSON representation, byte-preserved exactly as the source platform delivered it."

ValueSet: GroveRecordingFormatVS
Id: grove-recording-format
Title: "Grove Recording Format"
Description: "Every payload format admitted for a Grove recording DocumentReference content entry."
* ^experimental = false
* include codes from system GroveRecordingFormatCS
