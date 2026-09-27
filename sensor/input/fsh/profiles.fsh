//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: sensor-inline-data-1
Description: "An inline sampled-data result contains only single-space-delimited decimal values; exceptional and missing-value tokens are not admitted."
Expression: "data.exists() and data.matches('^-?(0|[1-9][0-9]*)([.][0-9]+)?( -?(0|[1-9][0-9]*)([.][0-9]+)?)*$')"
Severity: #error

Invariant: sensor-period-positive-1
Description: "The interval between uniformly sampled frames is greater than zero milliseconds."
Expression: "period > 0"
Severity: #error

Invariant: sensor-dimensions-positive-1
Description: "A sampled-data frame contains at least one dimension."
Expression: "dimensions > 0"
Severity: #error

Invariant: sensor-complete-frames-1
Description: "SampledData contains at least two complete frames and its token count is divisible by dimensions."
Expression: "data.split(' ').count() >= dimensions.toInteger() * 2 and data.split(' ').count() mod dimensions.toInteger() = 0"
Severity: #error

Invariant: sensor-document-payload-1
Description: "A sensor recording attachment contains exactly one of embedded data or a retrievable URL."
Expression: "data.exists() xor url.exists()"
Severity: #error

Invariant: sensor-opaque-identifier-value-1
Description: "A sensor source, output, or writer identifier is a canonical deployment-scoped Grove v0 HMAC value."
Expression: "$this.matches('^v0:[A-Za-z0-9._-]+:[1-9][0-9]*:[A-Za-z0-9_-]{43}$')"
Severity: #error

Profile: GroveSensorSampledDataObservation
Parent: GroveMobileObservation
Id: grove-sensor-sampled-data-observation
Title: "Grove Sensor Sampled Data Observation"
Description: "A source-neutral uniformly sampled numeric time series represented inline with FHIR R4 SampledData. The exact end instant, effectivePeriod.end = start + (frames - 1) x period, is delegated to the producer conformance gate; a millisecond-precision FHIRPath comparison is not portable across validators."
* value[x] 1..1 MS
* value[x] only SampledData
* effective[x] 1..1 MS
* effective[x] only Period
* effectivePeriod.start 1..1 MS
* effectivePeriod.end 1..1 MS
* valueSampledData obeys sensor-inline-data-1
* valueSampledData obeys sensor-period-positive-1
* valueSampledData obeys sensor-dimensions-positive-1
* valueSampledData obeys sensor-complete-frames-1
* valueSampledData.origin.value 1..1 MS
* valueSampledData.origin.system 1..1 MS
* valueSampledData.origin.system = $ucum (exactly)
* valueSampledData.origin.code 1..1 MS
* valueSampledData.period 1..1 MS
* valueSampledData.dimensions 1..1 MS
* valueSampledData.data 1..1 MS
* valueSampledData.factor 0..0
* valueSampledData.lowerLimit 0..0
* valueSampledData.upperLimit 0..0
* dataAbsentReason 0..0

Profile: GroveSensorECGObservation
Parent: GroveMobileObservation
Id: grove-sensor-ecg-observation
Title: "Grove Sensor ECG Observation"
Description: "An ECG recording whose lead channels are uniformly sampled FHIR R4 SampledData components. The exact end instant, effectivePeriod.end = start + (frames - 1) x period, is delegated to the producer conformance gate; a millisecond-precision FHIRPath comparison is not portable across validators."
* code = $loinc#11524-6
* effective[x] 1..1 MS
* effective[x] only Period
* effectivePeriod.start 1..1 MS
* effectivePeriod.end 1..1 MS
* value[x] 0..0
* dataAbsentReason 0..0
* component 1..* MS
* component.code 1..1 MS
* component.code.coding 1..* MS
* component.code.coding.system 1..1 MS
* component.code.coding.code 1..1 MS
* component.value[x] 1..1 MS
* component.value[x] only SampledData
* component.valueSampledData obeys sensor-inline-data-1
* component.valueSampledData obeys sensor-period-positive-1
* component.valueSampledData obeys sensor-dimensions-positive-1
* component.valueSampledData obeys sensor-complete-frames-1
* component.valueSampledData.origin.value 1..1 MS
* component.valueSampledData.origin.system 1..1 MS
* component.valueSampledData.origin.system = $ucum (exactly)
* component.valueSampledData.origin.code 1..1 MS
* component.valueSampledData.origin.code = #mV (exactly)
* component.valueSampledData.period 1..1 MS
* component.valueSampledData.dimensions 1..1 MS
* component.valueSampledData.dimensions = 1 (exactly)
* component.valueSampledData.data 1..1 MS
* component.valueSampledData.factor 0..0
* component.valueSampledData.lowerLimit 0..0
* component.valueSampledData.upperLimit 0..0
* component.dataAbsentReason 0..0

Profile: GroveSensorRecordingDocument
Parent: DocumentReference
Id: grove-sensor-recording-document
Title: "Grove Sensor Recording Document"
Description: "An externally encoded or embedded sensor recording preserved in one registered wire format."
* identifier 3..* MS
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #open
* identifier contains sourceRecord 1..1 MS and sourceOutput 1..1 MS and sourceArtifact 1..1 MS and writerRecord 0..1 MS
* identifier[sourceRecord].type = $groveIdentifierRole#source-record
* identifier[sourceRecord].system 1..1 MS
* identifier[sourceRecord].value 1..1 MS
* identifier[sourceRecord].value obeys sensor-opaque-identifier-value-1
* identifier[sourceOutput].type = $groveIdentifierRole#source-output
* identifier[sourceOutput].system 1..1 MS
* identifier[sourceOutput].value 1..1 MS
* identifier[sourceOutput].value obeys sensor-opaque-identifier-value-1
* identifier[sourceArtifact].type = $groveIdentifierRole#source-artifact
* identifier[sourceArtifact].system 1..1 MS
* identifier[sourceArtifact].value 1..1 MS
* identifier[sourceArtifact].value obeys sensor-opaque-identifier-value-1
* identifier[writerRecord].type = $groveIdentifierRole#writer-record
* identifier[writerRecord].system 1..1 MS
* identifier[writerRecord].value 1..1 MS
* identifier[writerRecord].value obeys sensor-opaque-identifier-value-1
* status MS
* type 1..1 MS
* subject 1..1 MS
* subject only Reference(Patient)
* date 1..1 MS
* content 1..1 MS
* content.attachment obeys sensor-document-payload-1
* content.attachment.contentType 1..1 MS
* content.attachment.contentType from GroveRecordingMimeTypeVS (required)
* content.format 1..1 MS
* content.format from GroveRecordingFormatVS (required)
// The stable CodeSystem and code identify the registered wire format. IG release versions do
// not travel in payload Coding values.
* content.format.version 0..0
* content.attachment.title 0..1 MS
* content.attachment.size 1..1 MS
* content.attachment.hash 1..1 MS
* context.related MS

Profile: GroveSensorConversionProvenance
Parent: GroveMobileConversionProvenance
Id: grove-sensor-conversion-provenance
Title: "Grove Sensor Conversion Provenance"
Description: "Source-neutral provenance for an application transformation that produces one or more Mobile/Sensor Observations or Sensor Recording Documents."
* target 1..* MS
* target only Reference(GroveMobileObservation or GroveSensorRecordingDocument)
