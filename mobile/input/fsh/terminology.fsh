//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: GroveRecordingMethodCS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "The positively established mode by which a mobile source captured a result. This vocabulary does not describe the clinical measurement technique."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #manual-entry "Manual entry" "A person manually entered the result into the source."
* #actively-recorded "Actively recorded" "A person deliberately initiated or participated in recording the result."
* #automatically-recorded "Automatically recorded" "The source recorded the result without a person initiating that individual measurement."

ValueSet: GroveRecordingMethodVS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "Capture modes permitted by the Grove recording-method extension when a source positively establishes the mode."
* ^experimental = false
* include codes from system GroveRecordingMethodCS

CodeSystem: GroveMobileMeasurementCS
Id: grove-mobile-measurement
Title: "Grove Mobile Measurement"
Description: "Measurement concepts defined by the Grove Mobile contract when an established code would not faithfully represent the exchanged result."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #step-count-total "Step count total" "The total number of steps attributed to the exact Observation effective Period."

ValueSet: GroveMobileMeasurementVS
Id: grove-mobile-measurement
Title: "Grove Mobile Measurement"
Description: "Measurement concepts defined by Grove Mobile for use in its focused domain profiles."
* ^experimental = false
* include codes from system GroveMobileMeasurementCS

// No ConceptMap is published for 0.1.0 because the potential HL7 PHR stepCount
// target is not a stable package dependency. Any future mapping from
// step-count-total to that target must be wider, never equal.
