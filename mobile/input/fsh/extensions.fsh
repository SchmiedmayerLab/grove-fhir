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
Description: "The version the writing application gave this revision of its logical record: HKMetadataKeySyncVersion on HealthKit, clientRecordVersion on Health Connect. A platform keeps the higher version when the same writer saves the same logical record again, so the lower version is superseded rather than counted as another measurement. Carried as canonical decimal text because the platforms' own values exceed a FHIR integer."
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only string
* valueString 1..1
* valueString obeys grove-writer-record-version-value-1

Extension: GroveRetractionTargetRole
Id: grove-retraction-target-role
Title: "Grove Retraction Target Role"
Description: "The role the exact prior output played in the source-derived graph. It disambiguates otherwise similar logical targets and is part of the retraction assertion, not a FHIR server delete instruction."
Context: Provenance.target
* value[x] only code
* valueCode 1..1 MS
* valueCode from GroveRetractionTargetRoleVS (required)


Extension: GroveRetractionTargetNativeIdentifier
Id: grove-retraction-target-native-identifier
Title: "Grove Retraction Target Native Identifier"
Description: "The platform-native record identifier of the retracted source record, carried beside the minted Grove identity so a consumer can delete the exact native records. Identifier.system names the adapter's own native key space, exactly as it does for a governed source identifier on the addition path, and the value is emitted only under that same explicit deployment disclosure policy. It never addresses the target: the Grove source-output or device-snapshot identity remains the retraction address."
Context: Provenance.target
* value[x] only Identifier
* valueIdentifier 1..1 MS
* valueIdentifier obeys grove-native-record-identifier-1
* valueIdentifier.system 1..1 MS
* valueIdentifier.value 1..1 MS
