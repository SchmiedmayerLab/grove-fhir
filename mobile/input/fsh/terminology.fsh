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

CodeSystem: GroveSleepStageCS
Id: grove-sleep-stage
Title: "Grove Sleep Stage"
Description: "Source-neutral sleep-stage classes shared by mobile and connected-device adapters. Adapters retain a source-specific code separately when the source distinction is more precise."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #awake "Awake" "The person was classified as awake."
* #in-bed "In bed" "The person was classified as being in bed without asserting wake or sleep."
* #out-of-bed "Out of bed" "The person was classified as outside the sleep-session bed interval."
* #asleep-unspecified "Asleep, unspecified stage" "The person was classified as asleep without a more specific stage."
* #light "Light sleep" "The source classified the interval as light sleep without a more portable stage distinction."
* #deep "Deep sleep" "The source classified the interval as deep or slow-wave sleep."
* #rem "REM sleep" "The source classified the interval as rapid-eye-movement sleep."
* #unknown "Unknown sleep stage" "The interval was part of a sleep session but the stage was not known."

ValueSet: GroveSleepStageVS
Id: grove-sleep-stage
Title: "Grove Sleep Stage"
Description: "Source-neutral sleep stages admitted by the Grove Mobile sleep-stage profile."
* ^experimental = false
* include codes from system GroveSleepStageCS

// No ConceptMap is published for 0.2.0 because the potential HL7 PHR stepCount
// target is not a stable package dependency. Any future mapping from
// step-count-total to that target must be wider, never equal.
