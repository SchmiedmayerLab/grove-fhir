//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: sensorkit-record-id-1
Description: "A SensorKit record identifier is a lowercase UUID in 8-4-4-4-12 form."
Expression: "matches('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')"
Severity: #error

Invariant: sensorkit-output-id-1
Description: "A SensorKit output identifier is a lowercase RFC 4122 UUIDv5 with an RFC variant."
Expression: "matches('^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')"
Severity: #error

Invariant: sensorkit-ecg-lead-standard-1
Description: "Left-arm-minus-right-arm SensorKit ECG data carries the standard MDC Lead-I coding."
Expression: "component.code.coding.where(system = 'https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-ecg-lead' and code = 'leftArmMinusRightArm').empty() or component.code.coding.where(system = 'urn:iso:std:iso:11073:10101' and code = '131329').count() = 1"
Severity: #error

Invariant: sensorkit-ecg-inverse-lead-1
Description: "Right-arm-minus-left-arm SensorKit ECG data is not mislabeled as standard Lead I."
Expression: "component.code.coding.where(system = 'https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-ecg-lead' and code = 'rightArmMinusLeftArm').empty() or component.code.coding.where(system = 'urn:iso:std:iso:11073:10101' and code = '131329').empty()"
Severity: #error

Profile: SensorKitObservation
Parent: GroveMobileObservation
Id: sensorkit-observation
Title: "SensorKit Observation"
Description: "SensorKit source and output identity for an Observation. A shared Sensor mapping directly claims this adapter plus its source-neutral profile; a SensorKit-only child directly claims only that exact child profile. The adapter does not authorize or fetch SensorKit data."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains sensorKitRecordId 1..1 MS and sensorKitOutputId 1..1 MS
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value 1..1 MS
* identifier[sensorKitRecordId].value obeys sensorkit-record-id-1
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value 1..1 MS
* identifier[sensorKitOutputId].value obeys sensorkit-output-id-1
* extension contains SensorKitSourceType named sensorKitSourceType 1..1 MS

Profile: SensorKitRecordingDocument
Parent: GroveSensorRecordingDocument
Id: sensorkit-recording-document
Title: "SensorKit Recording Document"
Description: "A native SensorKit payload supplied by the producer as an embedded or retrievable recording document."
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains sensorKitRecordId 1..1 MS and sensorKitOutputId 1..1 MS
* identifier[sensorKitRecordId].system = $sensorKitRecordId
* identifier[sensorKitRecordId].value 1..1 MS
* identifier[sensorKitRecordId].value obeys sensorkit-record-id-1
* identifier[sensorKitOutputId].system = $sensorKitOutputId
* identifier[sensorKitOutputId].value 1..1 MS
* identifier[sensorKitOutputId].value obeys sensorkit-output-id-1
* extension contains SensorKitSourceType named sensorKitSourceType 1..1 MS

Profile: SensorKitConversionProvenance
Parent: GroveSensorConversionProvenance
Id: sensorkit-conversion-provenance
Title: "SensorKit Conversion Provenance"
Description: "Provenance for transforming one SensorKit source record into structured SensorKit Observations, a native Recording Document, or both."
* target 1..* MS
* target only Reference(SensorKitObservation or SensorKitRecordingDocument)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.system = $sensorKitRecordId
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys sensorkit-record-id-1

Profile: SensorKitOnWristObservation
Parent: SensorKitObservation
Id: sensorkit-on-wrist-observation
Title: "SensorKit On-Wrist Observation"
Description: "A platform-exclusive SensorKit assertion that a watch was on or off the participant's wrist, including the reported wrist and crown placement."
* extension[sensorKitSourceType].valueCode = #on-wrist
* code = $sensorKitConcept#on-wrist-state "On-wrist state"
* effective[x] 1..1 MS
* effective[x] only dateTime or Period
* value[x] 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept from SensorKitWearStateVS (required)
* dataAbsentReason 0..0
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains wristLocation 1..1 MS and crownOrientation 1..1 MS
* component[wristLocation].code = $sensorKitConcept#wrist-location "Wrist location"
* component[wristLocation].value[x] 1..1 MS
* component[wristLocation].value[x] only CodeableConcept
* component[wristLocation].valueCodeableConcept from SensorKitSideVS (required)
* component[wristLocation].dataAbsentReason 0..0
* component[crownOrientation].code = $sensorKitConcept#crown-orientation "Crown orientation"
* component[crownOrientation].value[x] 1..1 MS
* component[crownOrientation].value[x] only CodeableConcept
* component[crownOrientation].valueCodeableConcept from SensorKitSideVS (required)
* component[crownOrientation].dataAbsentReason 0..0

Profile: SensorKitECGObservation
Parent: SensorKitObservation
Id: sensorkit-ecg-observation
Title: "SensorKit ECG Observation"
Description: "The uniformly sampled voltage projection of one SensorKit ECG source record. It is lossless only as the required hybrid graph with a linked exact native Recording Document that retains per-point signalInvalid/crownTouched flags, session identifiers/states, and any source detail not carried by the Observation."
* obeys sensorkit-ecg-lead-standard-1 and sensorkit-ecg-inverse-lead-1
* extension[sensorKitSourceType].valueCode = #ecg
* extension contains SensorKitECGSessionGuidance named sensorKitECGSessionGuidance 1..1 MS
* code = $loinc#11524-6 "EKG study"
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* derivedFrom 1..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component 1..1 MS
* component.code.coding ^slicing.discriminator.type = #value
* component.code.coding ^slicing.discriminator.path = "system"
* component.code.coding ^slicing.rules = #open
* component.code.coding contains sensorKitECGLead 1..1 MS and mdcLead 0..1 MS
* component.code.coding[sensorKitECGLead].system = $sensorKitECGLead
* component.code.coding[sensorKitECGLead].code 1..1 MS
* component.code.coding[sensorKitECGLead] from SensorKitECGLeadVS (required)
* component.code.coding[mdcLead].system = $mdc
* component.code.coding[mdcLead].code = #131329
* component.value[x] 1..1 MS
* component.value[x] only SampledData
* component.dataAbsentReason 0..0

Profile: SensorKitDeviceUsageObservation
Parent: SensorKitObservation
Id: sensorkit-device-usage-observation
Title: "SensorKit Device Usage Observation"
Description: "A platform-exclusive summary of unlock duration, screen wakes, and unlock count over one SensorKit device-usage reporting interval. Per-application, notification, and web detail remains in a related native Recording Document."
* extension[sensorKitSourceType].valueCode = #device-usage
* code = $sensorKitConcept#device-usage-summary "Device usage summary"
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #s (exactly)
* dataAbsentReason 0..0
* derivedFrom 1..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains screenWakes 1..1 MS and unlocks 1..1 MS
* component[screenWakes].code = $sensorKitConcept#screen-wakes "Screen wakes"
* component[screenWakes].value[x] 1..1 MS
* component[screenWakes].value[x] only Quantity
* component[screenWakes].valueQuantity.system = $ucum (exactly)
* component[screenWakes].valueQuantity.code = #{count} (exactly)
* component[screenWakes].dataAbsentReason 0..0
* component[unlocks].code = $sensorKitConcept#unlocks "Unlocks"
* component[unlocks].value[x] 1..1 MS
* component[unlocks].value[x] only Quantity
* component[unlocks].valueQuantity.system = $ucum (exactly)
* component[unlocks].valueQuantity.code = #{count} (exactly)
* component[unlocks].dataAbsentReason 0..0

Profile: SensorKitVisitObservation
Parent: SensorKitObservation
Id: sensorkit-visit-observation
Title: "SensorKit Visit Observation"
Description: "A platform-exclusive SensorKit visit summary preserving the category, distance from home, and uncertain arrival and departure windows without asserting a clinical Encounter."
* extension[sensorKitSourceType].valueCode = #visits
* code = $sensorKitConcept#visit-summary "Visit summary"
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains locationCategory 1..1 MS and distanceFromHome 1..1 MS and arrivalWindow 1..1 MS and departureWindow 1..1 MS
* component[locationCategory].code = $sensorKitConcept#visit-location-category "Visit location category"
* component[locationCategory].value[x] 1..1 MS
* component[locationCategory].value[x] only CodeableConcept
* component[locationCategory].valueCodeableConcept from SensorKitVisitLocationCategoryVS (required)
* component[locationCategory].dataAbsentReason 0..0
* component[distanceFromHome].code = $sensorKitConcept#distance-from-home "Distance from home"
* component[distanceFromHome].value[x] 1..1 MS
* component[distanceFromHome].value[x] only Quantity
* component[distanceFromHome].valueQuantity.system = $ucum (exactly)
* component[distanceFromHome].valueQuantity.code = #m (exactly)
* component[distanceFromHome].dataAbsentReason 0..0
* component[arrivalWindow].code = $sensorKitConcept#arrival-window "Arrival window"
* component[arrivalWindow].value[x] 1..1 MS
* component[arrivalWindow].value[x] only Period
* component[arrivalWindow].dataAbsentReason 0..0
* component[departureWindow].code = $sensorKitConcept#departure-window "Departure window"
* component[departureWindow].value[x] 1..1 MS
* component[departureWindow].value[x] only Period
* component[departureWindow].dataAbsentReason 0..0
