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

ValueSet: GroveNativeRecordingMimeTypeVS
Id: grove-native-recording-mime-type
Title: "Grove Native Recording MIME Types"
Description: "The exact media types admitted for a Grove native sensor recording. Standard types are identified by their IANA registration; the vendor-tree types are Grove's own and are not IANA-registered. Grove does not publish or version the external code system."
* ^experimental = false
* urn:ietf:bcp:13#text/csv "Comma-separated values"
* urn:ietf:bcp:13#application/fhir+json "FHIR JSON"
* urn:ietf:bcp:13#application/vnd.grovealliance.native+json "Grove native recording JSON"
* urn:ietf:bcp:13#application/vnd.grovealliance.provider+json "Grove provider recording JSON"
* urn:ietf:bcp:13#application/vnd.grovealliance.ppg "Grove photoplethysmogram binary"
* urn:ietf:bcp:13#application/hl7-cda+xml "HL7 Clinical Document Architecture"
* ^expansion.timestamp = "2026-08-20T00:00:00Z"
* ^expansion.parameter[+].name = "used-codesystem"
* ^expansion.parameter[=].valueUri = "urn:ietf:bcp:13"
* ^expansion.parameter[+].name = "includeDesignations"
* ^expansion.parameter[=].valueBoolean = false
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #text/csv
* ^expansion.contains[=].display = "Comma-separated values"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/fhir+json
* ^expansion.contains[=].display = "FHIR JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/vnd.grovealliance.native+json
* ^expansion.contains[=].display = "Grove native recording JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/vnd.grovealliance.provider+json
* ^expansion.contains[=].display = "Grove provider recording JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/vnd.grovealliance.ppg
* ^expansion.contains[=].display = "Grove photoplethysmogram binary"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/hl7-cda+xml
* ^expansion.contains[=].display = "HL7 Clinical Document Architecture"
