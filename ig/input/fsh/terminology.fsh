//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Grove terminology. All code systems are case-sensitive; content is complete unless
// the key space is inherently open (platform metadata keys), which are fragments.

CodeSystem: GroveDeviceVersionType
Id: grove-device-version-type
Title: "Grove Device Version Type"
Description: """
Version types for `Device.version.type` beyond the IEEE 11073 MDC production-specification
codes (hardware 531974, software 531975, firmware 531976). MDC defines no code for an
operating-system version, which mobile gateway devices need.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #operating-system "Operating System Version" "The version of the operating system running on the device."


CodeSystem: GroveRecordingMethodCS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: """
How a mobile health observation was captured, aligned with Android Health Connect's
recording-method enumeration and the IEEE 1752.1-2021 `modality` concept
(sensed vs. self-reported). HealthKit's `HKMetadataKeyWasUserEntered = true` maps to
`manual-entry`.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #automatically-recorded "Automatically Recorded" "Captured passively by a sensor without the user initiating the measurement (IEEE 1752 modality: sensed)."
* #actively-recorded "Actively Recorded" "Captured by a sensor during a measurement the user deliberately initiated (IEEE 1752 modality: sensed)."
* #manual-entry "Manual Entry" "Entered by the user rather than measured by a sensor (IEEE 1752 modality: self-reported)."
* #unknown "Unknown" "The capture method is not known."

ValueSet: GroveRecordingMethodVS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "All recording methods for mobile health observations."
* ^experimental = false
* include codes from system GroveRecordingMethodCS


CodeSystem: GroveDeviceType
Id: grove-device-type
Title: "Grove Mobile Device Type"
Description: """
Coarse device form factors for `Device.type`, mirroring Android Health Connect's
device-type enumeration so data from either mobile platform can carry it.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #watch "Watch" "A smartwatch."
* #phone "Phone" "A smartphone."
* #scale "Scale" "A body scale."
* #ring "Ring" "A smart ring."
* #head-mounted "Head-Mounted" "A head-mounted device."
* #fitness-band "Fitness Band" "A fitness band or tracker."
* #chest-strap "Chest Strap" "A chest-strap sensor."
* #smart-display "Smart Display" "A smart display."
* #unknown "Unknown" "The device type is not known."

ValueSet: GroveDeviceTypeVS
Id: grove-device-type
Title: "Grove Mobile Device Type"
Description: "All mobile device form factors."
* ^experimental = false
* include codes from system GroveDeviceType


CodeSystem: GroveSensorBatchFormatCS
Id: grove-sensor-batch-format
Title: "Grove Sensor Batch Format"
Description: """
How a raw sensor batch is serialized and compressed, for `DocumentReference.content.format`.
The media type in `contentType` describes the decompressed payload, so without this the
compression a consumer must undo is recorded nowhere. HL7's format codes cover clinical
document profiles and have no counterpart for bulk sensor payloads.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #csv "CSV" "Comma-separated values, one row per sample or per summarized entity."
* #csv-gzip "CSV, gzip-compressed" "As `csv`, stored gzip-compressed (RFC 1952)."
* #ndjson "Newline-delimited JSON" "One JSON object per line."
* #ndjson-gzip "Newline-delimited JSON, gzip-compressed" "As `ndjson`, stored gzip-compressed (RFC 1952)."

ValueSet: GroveSensorBatchFormatVS
Id: grove-sensor-batch-format
Title: "Grove Sensor Batch Format"
Description: "All serializations a raw sensor batch may use."
* ^experimental = false
* include codes from system GroveSensorBatchFormatCS


ValueSet: GrovePlatformMetadataKeyVS
Id: grove-platform-metadata-key
Title: "Platform Metadata Keys"
Description: """
The platform key spaces a ``GrovePlatformMetadata`` entry draws its key from, published
by the [platform vocabularies guide](https://grovealliance.org/fhir/platforms). Both are
fragment systems the platform vendor owns and HealthKit additionally accepts third-party
keys, so the binding that uses this set is extensible: an unlisted key is still valid,
and the resulting warning marks a key the guide has not yet published.
"""
* ^experimental = false
* include codes from system $platformHealthKitMetadataKey
* include codes from system $platformHealthConnectMetadataKey


CodeSystem: GroveQuestionnaireItemControl
Id: grove-questionnaire-item-control
Title: "Grove Questionnaire Item Control"
Description: """
Item control codes for Grove-specific questionnaire item renderers, used as codings in
the standard `questionnaire-itemControl` extension (whose binding is extensible; no
image-annotation control exists in the HL7 item-control code system).
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control"
* ^identifier[=].use = #old
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #annotate-image "Annotate Image" "The user annotates a base image (provided via the SDC itemMedia extension) with a drawing; the answer is the annotated image as an attachment."


CodeSystem: GroveAnnotateImageColors
Id: grove-annotate-image-colors
Title: "Annotate Image Region Colors"
Description: "Pen colors available to annotate-image regions."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #red "Red"
* #orange "Orange"
* #yellow "Yellow"
* #green "Green"
* #mint "Mint"
* #teal "Teal"
* #cyan "Cyan"
* #blue "Blue"
* #indigo "Indigo"
* #purple "Purple"
* #pink "Pink"
* #brown "Brown"
* #white "White"
* #gray "Gray"
* #black "Black"
* #clear "Clear"
* #primary "Primary"
* #secondary "Secondary"

ValueSet: GroveAnnotateImageColorsVS
Id: grove-annotate-image-colors
Title: "Annotate Image Region Colors"
Description: "All pen colors an annotate-image region may use."
* ^experimental = false
* include codes from system GroveAnnotateImageColors


CodeSystem: GroveAutocompleteTokens
Id: grove-autocomplete-tokens
Title: "Grove Autocomplete Tokens"
Description: """
Semantic content types for text answers, taken verbatim from the WHATWG HTML living
standard's `autocomplete` detail tokens — the de-facto cross-platform vocabulary.
Renderers map them to platform autofill facilities (iOS `UITextContentType`,
Android autofill hints, HTML `autocomplete`).
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #name "Full name"
* #given-name "Given name"
* #additional-name "Additional name"
* #family-name "Family name"
* #honorific-prefix "Honorific prefix"
* #honorific-suffix "Honorific suffix"
* #nickname "Nickname"
* #username "Username"
* #new-password "New password"
* #current-password "Current password"
* #one-time-code "One-time code"
* #organization-title "Organization title"
* #organization "Organization"
* #street-address "Street address"
* #address-line1 "Address line 1"
* #address-line2 "Address line 2"
* #address-level1 "Address level 1 (state/province)"
* #address-level2 "Address level 2 (city)"
* #country "Country code"
* #country-name "Country name"
* #postal-code "Postal code"
* #bday "Birthday"
* #sex "Sex"
* #tel "Telephone number"
* #email "Email address"
* #url "URL"
* #photo "Photo URL"

ValueSet: GroveAutocompleteTokensVS
Id: grove-autocomplete-tokens
Title: "Grove Autocomplete Tokens"
Description: "All semantic content types for text answers."
* ^experimental = false
* include codes from system GroveAutocompleteTokens


CodeSystem: GroveAutocapitalizeCS
Id: grove-autocapitalize
Title: "Grove Autocapitalize"
Description: """
Autocapitalization behaviours for text answers, taken verbatim from the WHATWG HTML
living standard's `autocapitalize` attribute values; 1:1 with iOS
`UITextAutocapitalizationType` and mappable to Android input types.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #none "None" "No autocapitalization."
* #sentences "Sentences" "Capitalize the first letter of each sentence."
* #words "Words" "Capitalize the first letter of each word."
* #characters "Characters" "Capitalize every character."

ValueSet: GroveAutocapitalizeVS
Id: grove-autocapitalize
Title: "Grove Autocapitalize"
Description: "All autocapitalization behaviours."
* ^experimental = false
* include codes from system GroveAutocapitalizeCS
