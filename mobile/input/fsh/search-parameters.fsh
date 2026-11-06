//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: GroveProvenanceRecordVersion
InstanceOf: SearchParameter
Usage: #definition
Title: "Grove Provenance Record Version"
Description: "Finds a conversion Provenance by the record-version Identifier it repeats in its grove-record-version extension."
* id = "grove-provenance-record-version"
* url = "https://grovealliance.org/fhir/mobile/SearchParameter/grove-provenance-record-version"
* name = "GroveProvenanceRecordVersion"
* status = #active
* experimental = false
* date = "2026-11-02"
* publisher = "Schmiedmayer Lab"
* description = "Matches a conversion Provenance whose grove-record-version Identifier has exactly the given system and value. The value is opaque: a search matches the complete system and value pair only, never a part of the value, and the value is never parsed or recomputed."
* code = #grove-record-version
* base = #Provenance
* type = #token
* expression = "Provenance.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-record-version').value.ofType(Identifier)"
