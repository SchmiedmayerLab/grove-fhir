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


Extension: GroveWriterRecordVersion
Id: grove-writer-record-version
Title: "Grove Writer Record Version"
Description: "The version the writing application gave this revision of its logical record: HKMetadataKeySyncVersion on HealthKit, clientRecordVersion on Health Connect. A platform keeps the higher version when the same writer saves the same logical record again, so a receiver supersedes the lower version rather than counting the measurement twice. Carried as canonical decimal text because the platforms' own values exceed a FHIR integer."
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only string
* valueString 1..1
* valueString obeys grove-writer-record-version-value-1
