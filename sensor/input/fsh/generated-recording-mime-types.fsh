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

ValueSet: GroveRecordingMimeTypeVS
Id: grove-recording-mime-type
Title: "Grove Recording MIME Types"
Description: "The exact MIME content-type values admitted for a Grove sensor recording payload. Base media types use their IANA identifiers; parameters follow the standard that defines the payload. Grove does not publish or version the external code system."
* ^experimental = false
* urn:ietf:bcp:13#text/csv "Comma-separated values"
* urn:ietf:bcp:13#application/fhir+json "FHIR JSON"
* urn:ietf:bcp:13#"application/fhir+json; fhirVersion=1.0" "FHIR DSTU2 JSON"
* urn:ietf:bcp:13#"application/fhir+json; fhirVersion=4.0" "FHIR R4 JSON"
* urn:ietf:bcp:13#application/json "JSON"
* urn:ietf:bcp:13#application/octet-stream "Binary octet stream"
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
* ^expansion.contains[=].code = #"application/fhir+json; fhirVersion=1.0"
* ^expansion.contains[=].display = "FHIR DSTU2 JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #"application/fhir+json; fhirVersion=4.0"
* ^expansion.contains[=].display = "FHIR R4 JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/json
* ^expansion.contains[=].display = "JSON"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/octet-stream
* ^expansion.contains[=].display = "Binary octet stream"
* ^expansion.contains[+].system = "urn:ietf:bcp:13"
* ^expansion.contains[=].code = #application/hl7-cda+xml
* ^expansion.contains[=].display = "HL7 Clinical Document Architecture"
