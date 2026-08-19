//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Alias: GroveSensorKitSampleType = https://grovealliance.org/fhir/platforms/CodeSystem/sensorkit-sample-type

// SensorKit: passive sensor streams (wrist state, visits, device usage, PPG, ECG)
// that Apple's SensorKit framework exposes to approved research studies. These
// definitions generalize what study apps previously encoded ad hoc, using coded
// components and the shared device model instead of per-app extension trees.

CodeSystem: GroveSensorKitConcepts
Id: grove-sensorkit-concepts
Title: "SensorKit Observation Concepts"
Description: """
Codes used by the SensorKit profiles for device placement, visit timing, and
device-usage summary measurements.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #wrist-location "Wrist Location" "Which wrist the watch is worn on."
* #crown-orientation "Crown Orientation" "Which side the watch crown faces."
* #visit-location-category "Visit Location Category" "The kind of place visited (home, work, school, gym)."
* #distance-from-home "Distance From Home" "Distance of the visited place from the participant's home."
* #arrival-window "Arrival Window" "The time window within which the arrival occurred (SensorKit reports ranges, not instants)."
* #departure-window "Departure Window" "The time window within which the departure occurred."
* #screen-wakes "Screen Wakes" "Number of times the screen woke during the reporting period."
* #unlocks "Unlocks" "Number of device unlocks during the reporting period."
* #unlock-duration "Unlock Duration" "Total time the device was unlocked during the reporting period."


CodeSystem: GroveSensorKitValues
Id: grove-sensorkit-values
Title: "SensorKit Coded Values"
Description: """
Codes used by the SensorKit profiles for wear state, device placement, and visit
location categories.
"""
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #on-wrist "On Wrist" "The watch is currently worn."
* #off-wrist "Off Wrist" "The watch is currently not worn."
* #left "Left"
* #right "Right"
* #home "Home"
* #work "Work"
* #school "School"
* #gym "Gym"
* #unknown "Unknown"


Profile: GroveWearStateObservation
Parent: GroveMobileSensorObservation
Id: grove-wear-state-observation
Title: "Grove Wear-State Observation"
Description: """
Represents a sample from SensorKit's on-wrist state stream. The Observation value
records whether the watch is worn. Components record the wrist location and crown
orientation when available.
"""
* code = GroveSensorKitSampleType#com.apple.SensorKit.onWristState
* value[x] only CodeableConcept
* valueCodeableConcept from GroveWearStateVS (required)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains wristLocation 0..1 MS and crownOrientation 0..1 MS
* component[wristLocation].code = GroveSensorKitConcepts#wrist-location
* component[wristLocation].value[x] only CodeableConcept
* component[wristLocation].valueCodeableConcept from GroveWristSideVS (required)
* component[crownOrientation].code = GroveSensorKitConcepts#crown-orientation
* component[crownOrientation].value[x] only CodeableConcept
* component[crownOrientation].valueCodeableConcept from GroveWristSideVS (required)


ValueSet: GroveWearStateVS
Id: grove-wear-state
Title: "Wear State"
Description: "Whether a wearable is currently worn."
* ^experimental = false
* GroveSensorKitValues#on-wrist
* GroveSensorKitValues#off-wrist


ValueSet: GroveWristSideVS
Id: grove-wrist-side
Title: "Wrist Side"
Description: "Which wrist a device is worn on, and which way its crown faces."
* ^experimental = false
* GroveSensorKitValues#left
* GroveSensorKitValues#right


Profile: GroveVisitObservation
Parent: GroveMobileSensorObservation
Id: grove-visit-observation
Title: "Grove Visit Observation"
Description: """
Represents a SensorKit visit without geographic coordinates. Components record the
location category, distance from home, and the reported arrival and departure windows.
`effectivePeriod` spans from the start of the arrival window through the end of the
departure window.
"""
* code = GroveSensorKitSampleType#com.apple.SensorKit.visits
* effective[x] only Period
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains
    locationCategory 1..1 MS and
    distanceFromHome 0..1 MS and
    arrivalWindow 0..1 MS and
    departureWindow 0..1 MS
* component[locationCategory].code = GroveSensorKitConcepts#visit-location-category
* component[locationCategory].value[x] only CodeableConcept
* component[locationCategory].valueCodeableConcept from GroveVisitLocationCategoryVS (required)
* component[distanceFromHome].code = GroveSensorKitConcepts#distance-from-home
* component[distanceFromHome].value[x] only Quantity
* component[distanceFromHome].valueQuantity.system = "http://unitsofmeasure.org"
* component[distanceFromHome].valueQuantity.code = #m
* component[arrivalWindow].code = GroveSensorKitConcepts#arrival-window
* component[arrivalWindow].value[x] only Period
* component[departureWindow].code = GroveSensorKitConcepts#departure-window
* component[departureWindow].value[x] only Period


ValueSet: GroveVisitLocationCategoryVS
Id: grove-visit-location-category
Title: "Visit Location Category"
Description: "Location categories used by the Grove SensorKit visit profile."
* ^experimental = false
* GroveSensorKitValues#home
* GroveSensorKitValues#work
* GroveSensorKitValues#school
* GroveSensorKitValues#gym
* GroveSensorKitValues#unknown


Profile: GroveDeviceUsageObservation
Parent: GroveMobileSensorObservation
Id: grove-device-usage-observation
Title: "Grove Device-Usage Observation"
Description: """
Represents a SensorKit device-usage reporting period. The Observation value records
total unlock duration, and components record screen-wake and unlock counts. Detailed
per-application, notification, and web-usage data can be carried in a
``GroveSensorBatchDocument`` referenced by `derivedFrom`.
"""
* code = GroveSensorKitSampleType#com.apple.SensorKit.deviceUsageReport
* effective[x] only Period
* value[x] only Quantity
* valueQuantity.system = "http://unitsofmeasure.org"
* valueQuantity.code = #s
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains screenWakes 0..1 MS and unlocks 0..1 MS
* component[screenWakes].code = GroveSensorKitConcepts#screen-wakes
* component[screenWakes].value[x] only Quantity
* component[screenWakes].valueQuantity.system = "http://unitsofmeasure.org"
* component[screenWakes].valueQuantity.code = #{count}
* component[unlocks].code = GroveSensorKitConcepts#unlocks
* component[unlocks].value[x] only Quantity
* component[unlocks].valueQuantity.system = "http://unitsofmeasure.org"
* component[unlocks].valueQuantity.code = #{count}


Profile: GroveSensorBatchDocument
Parent: DocumentReference
Id: grove-sensor-batch-document
Title: "Grove Sensor Batch Document"
Description: """
Represents a batch of sensor data, such as a PPG waveform, accelerometer stream, or
detailed device-usage report. The attachment can contain the payload inline or reference
an external file. A summary Observation can reference the document through `derivedFrom`.

`type` names the sensor stream; `content.attachment.contentType` is the media type of
the payload once decompressed; `content.format` names its serialization and any
compression applied to the stored bytes. `hash` and `size` describe the stored bytes,
including compression when present.

FHIR R4 resolves a relative `attachment.url` against the service base. A writer using
sidecar files SHALL provide an absolute URL or document the base used to resolve a
relative URL.
"""
* type 1..1 MS
* type from GroveSensorBatchTypeVS (extensible)
* content 1..* MS
* content.attachment.contentType 1..1 MS
* content.attachment.url MS
* content.attachment.url ^short = "Absolute URL of the sidecar payload, or a relative URL against a documented base"
* content.attachment.hash MS
* content.attachment.hash ^short = "SHA-1 of the stored bytes, base64-encoded (compressed bytes when content.format says so)"
* content.attachment.size MS
* content.attachment.size ^short = "Length in bytes of the stored payload"
* content.format MS
* content.format from GroveSensorBatchFormatVS (extensible)
* content.format ^short = "Serialization and compression of the stored payload"


ValueSet: GroveSensorBatchTypeVS
Id: grove-sensor-batch-type
Title: "Sensor Batch Types"
Description: "SensorKit stream identifiers permitted for a Grove Sensor Batch Document."
* ^experimental = false
* include codes from system GroveSensorKitSampleType
