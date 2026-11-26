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

ValueSet: GroveClinicalRecordFormatVS
Id: grove-clinical-record-format
Title: "Grove Clinical Record Format"
Description: "Every payload format the Clinical Records guide owns, drawn from the Mobile payload format CodeSystem; a Clinical Record Document content entry declares one of them. A Clinical Record Attachment fixes the Mobile source-file format instead."
* ^experimental = false
* https://grovealliance.org/fhir/mobile/CodeSystem/grove-payload-format#provider-issued-fhir-json "Provider-Issued FHIR JSON"
* https://grovealliance.org/fhir/mobile/CodeSystem/grove-payload-format#cda-document "CDA Document"
