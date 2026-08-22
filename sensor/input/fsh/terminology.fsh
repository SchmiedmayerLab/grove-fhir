//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

ValueSet: GroveNativeRecordingMimeTypeVS
Id: grove-native-recording-mime-type
Title: "Grove Native Recording MIME Types"
Description: "The exact media types from the external IANA BCP 13 registry admitted for a Grove native sensor recording. Grove does not publish or version the external code system."
* ^experimental = false
* urn:ietf:bcp:13#application/json "JSON"
* urn:ietf:bcp:13#application/octet-stream "Arbitrary binary data"
* urn:ietf:bcp:13#text/csv "Comma-separated values"
* urn:ietf:bcp:13#application/fhir+json "FHIR JSON"
* ^expansion.timestamp = "2026-08-20T00:00:00Z"
* ^expansion.parameter[+].name = "used-codesystem"
* ^expansion.parameter[=].valueUri = "urn:ietf:bcp:13"
* ^expansion.parameter[+].name = "includeDesignations"
* ^expansion.parameter[=].valueBoolean = false
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/json
* ^expansion.contains[=].display = "JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/octet-stream
* ^expansion.contains[=].display = "Arbitrary binary data"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #text/csv
* ^expansion.contains[=].display = "Comma-separated values"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/fhir+json
* ^expansion.contains[=].display = "FHIR JSON"
