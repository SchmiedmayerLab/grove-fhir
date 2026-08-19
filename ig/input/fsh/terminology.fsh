//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: GroveDeviceVersionType
Id: grove-device-version-type
Title: "Grove Device Version Type"
Description: "Version types used by the Grove gateway-device profile when IEEE 11073 MDC has no corresponding code."
* ^experimental = true
* ^caseSensitive = true
* ^content = #complete
* #operating-system "Operating System Version"


CodeSystem: GroveRecordingMethodCS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "How a mobile health observation was captured."
* ^experimental = true
* ^caseSensitive = true
* ^content = #complete
* #automatically-recorded "Automatically Recorded" "Captured passively by a sensor."
* #actively-recorded "Actively Recorded" "Captured during a measurement initiated by the user."
* #manual-entry "Manual Entry" "Entered by the user rather than measured by a sensor."

ValueSet: GroveRecordingMethodVS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "Recording methods used by Grove mobile observations."
* ^experimental = true
* include codes from system GroveRecordingMethodCS


CodeSystem: GroveDeviceType
Id: grove-device-type
Title: "Grove Mobile Device Type"
Description: "Coarse form factors used for devices represented by Grove."
* ^experimental = true
* ^caseSensitive = true
* ^content = #complete
* #watch "Watch" "A smartwatch."
* #phone "Phone" "A smartphone."
* #scale "Scale" "A body scale."
* #ring "Ring" "A smart ring."
* #head-mounted "Head-Mounted" "A head-mounted device."
* #fitness-band "Fitness Band" "A fitness band or tracker."
* #chest-strap "Chest Strap" "A chest-strap sensor."

ValueSet: GroveDeviceTypeVS
Id: grove-device-type
Title: "Grove Mobile Device Type"
Description: "Device form factors represented by Grove."
* ^experimental = true
* include codes from system GroveDeviceType


ValueSet: GrovePlatformMetadataKeyVS
Id: grove-platform-metadata-key
Title: "HealthKit Metadata Keys"
Description: "HealthKit metadata keys preserved by the Grove platform-metadata extension."
* ^experimental = true
* include codes from system $platformHealthKitMetadataKey
