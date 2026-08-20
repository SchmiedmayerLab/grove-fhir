//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: GroveRecordingMethod
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "The positively established capture mode for a mobile result. Observation.method remains available for the clinical measurement technique."
Context: Observation
* value[x] only Coding
* valueCoding 1..1
* valueCoding from GroveRecordingMethodVS (required)
