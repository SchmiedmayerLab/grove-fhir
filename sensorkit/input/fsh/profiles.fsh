//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: sensorkit-ecg-lead-standard-1
Description: "Left-arm-minus-right-arm SensorKit ECG data carries the standard MDC Lead-I coding."
Expression: "component.code.coding.where(system = 'https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-ecg-lead' and code = 'leftArmMinusRightArm').empty() or component.code.coding.where(system = 'urn:iso:std:iso:11073:10101' and code = '131329').count() = 1"
Severity: #error

Invariant: sensorkit-ecg-inverse-lead-1
Description: "Right-arm-minus-left-arm SensorKit ECG data is not mislabeled as standard Lead I."
Expression: "component.code.coding.where(system = 'https://grovealliance.org/fhir/sensorkit/CodeSystem/sensorkit-ecg-lead' and code = 'rightArmMinusLeftArm').empty() or component.code.coding.where(system = 'urn:iso:std:iso:11073:10101' and code = '131329').empty()"
Severity: #error

Invariant: sensorkit-visit-focus-identifier-1
Description: "A SensorKit visit Location reference uses a complete deployment-governed native namespace and never claims a Grove graph-identity role."
Expression: "focus.empty() or (focus.identifier.system.exists() and focus.identifier.value.exists() and focus.identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role').empty())"
Severity: #error

Invariant: sensorkit-summary-quantity-nonnegative-1
Description: "Every Quantity in a SensorKit-only summary carries a present non-negative source-domain value; no clinical upper range is asserted."
Expression: "value.ofType(Quantity).all(value.exists() and value >= 0) and component.value.ofType(Quantity).all(value.exists() and value >= 0)"
Severity: #error

Invariant: sensorkit-summary-count-integer-1
Description: "Every UCUM {count} component in a SensorKit-only summary is a canonical non-negative integer."
Expression: "component.value.ofType(Quantity).where(system = 'http://unitsofmeasure.org' and code = '{count}').all(value.exists() and value.toString().matches('^(0|[1-9][0-9]*)$'))"
Severity: #error

Profile: SensorKitObservation
Parent: GroveMobileObservation
Id: sensorkit-observation
Title: "SensorKit Observation"
Description: "SensorKit source and output identity for an Observation. A shared Sensor mapping directly claims this adapter plus its source-neutral profile; a SensorKit-only child directly claims only that exact child profile. The adapter does not authorize or fetch SensorKit data."
* issued 0..0
* extension contains SensorKitSourceType named sensorKitSourceType 1..1 MS

Profile: SensorKitRecordingDocument
Parent: GroveSensorRecordingDocument
Id: sensorkit-recording-document
Title: "SensorKit Recording Document"
Description: "A SensorKit payload in one registered format, supplied by the producer as an embedded or retrievable Recording Document."
* extension contains SensorKitSourceType named sensorKitSourceType 1..1 MS

Profile: SensorKitConversionProvenance
Parent: GroveSensorConversionProvenance
Id: sensorkit-conversion-provenance
Title: "SensorKit Conversion Provenance"
Description: "Provenance for transforming one SensorKit source record into structured SensorKit Observations, a registered Recording Document, or both."
* target 1..* MS
* target only Reference(SensorKitObservation or SensorKitRecordingDocument)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.type = $groveIdentifierRole#source-record
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.value 1..1 MS

Profile: SensorKitOnWristObservation
Parent: SensorKitObservation
Id: sensorkit-on-wrist-observation
Title: "SensorKit On-Wrist Observation"
Description: "A platform-exclusive SensorKit assertion that a watch was on or off the participant's wrist, including the reported wrist and crown placement."
* extension[sensorKitSourceType].valueCode = #on-wrist
* code = $sensorKitConcept#on-wrist-state
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
* component[wristLocation].code = $sensorKitConcept#wrist-location
* component[wristLocation].value[x] 1..1 MS
* component[wristLocation].value[x] only CodeableConcept
* component[wristLocation].valueCodeableConcept from SensorKitSideVS (required)
* component[wristLocation].dataAbsentReason 0..0
* component[crownOrientation].code = $sensorKitConcept#crown-orientation
* component[crownOrientation].value[x] 1..1 MS
* component[crownOrientation].value[x] only CodeableConcept
* component[crownOrientation].valueCodeableConcept from SensorKitSideVS (required)
* component[crownOrientation].dataAbsentReason 0..0

Profile: SensorKitECGObservation
Parent: SensorKitObservation
Id: sensorkit-ecg-observation
Title: "SensorKit ECG Observation"
Description: "The uniformly sampled voltage projection of one SensorKit ECG source record. It is lossless only as the required hybrid graph with a linked exact Recording Document in an admitted format that retains per-point signalInvalid/crownTouched flags, session identifiers/states, and any source detail not carried by the Observation."
* obeys sensorkit-ecg-lead-standard-1 and sensorkit-ecg-inverse-lead-1
* extension[sensorKitSourceType].valueCode = #ecg
* code = $loinc#11524-6
* method 1..1 MS
* method.coding 1..1 MS
* method.coding.system = $sensorKitValue (exactly)
* method from SensorKitECGSessionGuidanceVS (required)
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
Description: "A platform-exclusive summary of unlock duration, screen wakes, and unlock count over one SensorKit device-usage reporting interval. Per-application, notification, web-usage, and text-input-session detail remains in the required related Recording Document."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #device-usage
* code = $sensorKitConcept#device-usage-summary
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
* component[screenWakes].code = $sensorKitConcept#screen-wakes
* component[screenWakes].value[x] 1..1 MS
* component[screenWakes].value[x] only Quantity
* component[screenWakes].valueQuantity.system = $ucum (exactly)
* component[screenWakes].valueQuantity.code = #{count} (exactly)
* component[screenWakes].dataAbsentReason 0..0
* component[unlocks].code = $sensorKitConcept#unlocks
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
* obeys sensorkit-visit-focus-identifier-1 and sensorkit-summary-quantity-nonnegative-1
* extension[sensorKitSourceType].valueCode = #visits
* code = $sensorKitConcept#visit-summary
* focus 0..1 MS
* focus only Reference(Location)
* focus.reference 0..0
* focus.type 1..1 MS
* focus.type = "Location" (exactly)
* focus.identifier 1..1 MS
* focus.identifier.system 1..1 MS
* focus.identifier.value 1..1 MS
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains locationCategory 1..1 MS and distanceFromHome 1..1 MS and arrivalWindow 1..1 MS and departureWindow 1..1 MS
* component[locationCategory].code = $sensorKitConcept#visit-location-category
* component[locationCategory].value[x] 1..1 MS
* component[locationCategory].value[x] only CodeableConcept
* component[locationCategory].valueCodeableConcept from SensorKitVisitLocationCategoryVS (required)
* component[locationCategory].dataAbsentReason 0..0
* component[distanceFromHome].code = $sensorKitConcept#distance-from-home
* component[distanceFromHome].value[x] 1..1 MS
* component[distanceFromHome].value[x] only Quantity
* component[distanceFromHome].valueQuantity.system = $ucum (exactly)
* component[distanceFromHome].valueQuantity.code = #m (exactly)
* component[distanceFromHome].dataAbsentReason 0..0
* component[arrivalWindow].code = $sensorKitConcept#arrival-window
* component[arrivalWindow].value[x] 1..1 MS
* component[arrivalWindow].value[x] only Period
* component[arrivalWindow].dataAbsentReason 0..0
* component[departureWindow].code = $sensorKitConcept#departure-window
* component[departureWindow].value[x] 1..1 MS
* component[departureWindow].value[x] only Period
* component[departureWindow].dataAbsentReason 0..0

Profile: SensorKitMessagesUsageObservation
Parent: SensorKitObservation
Id: sensorkit-messages-usage-observation
Title: "SensorKit Messages Usage Observation"
Description: "A platform-exclusive, content-free summary of one SensorKit messages-usage reporting interval: message and distinct-contact counts only, never content or identities."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #messages-usage
* code = $sensorKitConcept#messages-usage-summary
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* derivedFrom 0..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains incomingMessages 1..1 MS and outgoingMessages 1..1 MS and uniqueContacts 1..1 MS
* component[incomingMessages].code = $sensorKitConcept#incoming-messages
* component[incomingMessages].value[x] 1..1 MS
* component[incomingMessages].value[x] only Quantity
* component[incomingMessages].valueQuantity.system = $ucum (exactly)
* component[incomingMessages].valueQuantity.code = #{count} (exactly)
* component[incomingMessages].dataAbsentReason 0..0
* component[outgoingMessages].code = $sensorKitConcept#outgoing-messages
* component[outgoingMessages].value[x] 1..1 MS
* component[outgoingMessages].value[x] only Quantity
* component[outgoingMessages].valueQuantity.system = $ucum (exactly)
* component[outgoingMessages].valueQuantity.code = #{count} (exactly)
* component[outgoingMessages].dataAbsentReason 0..0
* component[uniqueContacts].code = $sensorKitConcept#unique-contacts
* component[uniqueContacts].value[x] 1..1 MS
* component[uniqueContacts].value[x] only Quantity
* component[uniqueContacts].valueQuantity.system = $ucum (exactly)
* component[uniqueContacts].valueQuantity.code = #{count} (exactly)
* component[uniqueContacts].dataAbsentReason 0..0

Profile: SensorKitPhoneUsageObservation
Parent: SensorKitObservation
Id: sensorkit-phone-usage-observation
Title: "SensorKit Phone Usage Observation"
Description: "A platform-exclusive, content-free summary of one SensorKit phone-usage reporting interval: the total call duration as the value plus call and distinct-contact counts, never identities."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #phone-usage
* code = $sensorKitConcept#phone-usage-summary
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #s (exactly)
* dataAbsentReason 0..0
* derivedFrom 0..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains incomingCalls 1..1 MS and outgoingCalls 1..1 MS and uniqueContacts 1..1 MS
* component[incomingCalls].code = $sensorKitConcept#incoming-calls
* component[incomingCalls].value[x] 1..1 MS
* component[incomingCalls].value[x] only Quantity
* component[incomingCalls].valueQuantity.system = $ucum (exactly)
* component[incomingCalls].valueQuantity.code = #{count} (exactly)
* component[incomingCalls].dataAbsentReason 0..0
* component[outgoingCalls].code = $sensorKitConcept#outgoing-calls
* component[outgoingCalls].value[x] 1..1 MS
* component[outgoingCalls].value[x] only Quantity
* component[outgoingCalls].valueQuantity.system = $ucum (exactly)
* component[outgoingCalls].valueQuantity.code = #{count} (exactly)
* component[outgoingCalls].dataAbsentReason 0..0
* component[uniqueContacts].code = $sensorKitConcept#unique-contacts
* component[uniqueContacts].value[x] 1..1 MS
* component[uniqueContacts].value[x] only Quantity
* component[uniqueContacts].valueQuantity.system = $ucum (exactly)
* component[uniqueContacts].valueQuantity.code = #{count} (exactly)
* component[uniqueContacts].dataAbsentReason 0..0

Profile: SensorKitKeyboardMetricsObservation
Parent: SensorKitObservation
Id: sensorkit-keyboard-metrics-observation
Title: "SensorKit Keyboard Metrics Observation"
Description: "A platform-exclusive, content-free summary of one SensorKit keyboard-metrics reporting interval: the total typing duration as the value plus typing-event counts; the summary is lossy, so the native recording is mandatory. No typed content, emoji identity, or sentiment is ever represented."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #keyboard-metrics
* code = $sensorKitConcept#keyboard-metrics-summary
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
* component contains totalWords 1..1 MS and totalAlteredWords 1..1 MS and totalTaps 1..1 MS and totalDeletes 1..1 MS and totalEmojis 1..1 MS and totalAutocorrections 1..1 MS and totalPauses 1..1 MS and totalTypingEpisodes 1..1 MS and typingSpeed 1..1 MS
* component[totalWords].code = $sensorKitConcept#total-words
* component[totalWords].value[x] 1..1 MS
* component[totalWords].value[x] only Quantity
* component[totalWords].valueQuantity.system = $ucum (exactly)
* component[totalWords].valueQuantity.code = #{count} (exactly)
* component[totalWords].dataAbsentReason 0..0
* component[totalAlteredWords].code = $sensorKitConcept#total-altered-words
* component[totalAlteredWords].value[x] 1..1 MS
* component[totalAlteredWords].value[x] only Quantity
* component[totalAlteredWords].valueQuantity.system = $ucum (exactly)
* component[totalAlteredWords].valueQuantity.code = #{count} (exactly)
* component[totalAlteredWords].dataAbsentReason 0..0
* component[totalTaps].code = $sensorKitConcept#total-taps
* component[totalTaps].value[x] 1..1 MS
* component[totalTaps].value[x] only Quantity
* component[totalTaps].valueQuantity.system = $ucum (exactly)
* component[totalTaps].valueQuantity.code = #{count} (exactly)
* component[totalTaps].dataAbsentReason 0..0
* component[totalDeletes].code = $sensorKitConcept#total-deletes
* component[totalDeletes].value[x] 1..1 MS
* component[totalDeletes].value[x] only Quantity
* component[totalDeletes].valueQuantity.system = $ucum (exactly)
* component[totalDeletes].valueQuantity.code = #{count} (exactly)
* component[totalDeletes].dataAbsentReason 0..0
* component[totalEmojis].code = $sensorKitConcept#total-emojis
* component[totalEmojis].value[x] 1..1 MS
* component[totalEmojis].value[x] only Quantity
* component[totalEmojis].valueQuantity.system = $ucum (exactly)
* component[totalEmojis].valueQuantity.code = #{count} (exactly)
* component[totalEmojis].dataAbsentReason 0..0
* component[totalAutocorrections].code = $sensorKitConcept#total-autocorrections
* component[totalAutocorrections].value[x] 1..1 MS
* component[totalAutocorrections].value[x] only Quantity
* component[totalAutocorrections].valueQuantity.system = $ucum (exactly)
* component[totalAutocorrections].valueQuantity.code = #{count} (exactly)
* component[totalAutocorrections].dataAbsentReason 0..0
* component[totalPauses].code = $sensorKitConcept#total-pauses
* component[totalPauses].value[x] 1..1 MS
* component[totalPauses].value[x] only Quantity
* component[totalPauses].valueQuantity.system = $ucum (exactly)
* component[totalPauses].valueQuantity.code = #{count} (exactly)
* component[totalPauses].dataAbsentReason 0..0
* component[totalTypingEpisodes].code = $sensorKitConcept#total-typing-episodes
* component[totalTypingEpisodes].value[x] 1..1 MS
* component[totalTypingEpisodes].value[x] only Quantity
* component[totalTypingEpisodes].valueQuantity.system = $ucum (exactly)
* component[totalTypingEpisodes].valueQuantity.code = #{count} (exactly)
* component[totalTypingEpisodes].dataAbsentReason 0..0
* component[typingSpeed].code = $sensorKitConcept#typing-speed
* component[typingSpeed].value[x] 1..1 MS
* component[typingSpeed].value[x] only Quantity
* component[typingSpeed].valueQuantity.system = $ucum (exactly)
* component[typingSpeed].valueQuantity.code = #/s (exactly)
* component[typingSpeed].dataAbsentReason 0..0

Profile: SensorKitSleepSessionObservation
Parent: SensorKitObservation
Id: sensorkit-sleep-session-observation
Title: "SensorKit Sleep Session Observation"
Description: "A platform-exclusive assertion of one SensorKit sleep session interval. The source publishes only the session bounds, so the result is the exact length of that interval and no stage, efficiency, or quality result may be invented."
* obeys sensorkit-summary-quantity-nonnegative-1
* extension[sensorKitSourceType].valueCode = #sleep-sessions
* code = $sensorKitConcept#sleep-session
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #s (exactly)
* dataAbsentReason 0..0
* derivedFrom 0..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)


Profile: SensorKitWristTemperatureObservation
Parent: SensorKitObservation
Id: sensorkit-wrist-temperature-observation
Title: "SensorKit Wrist Temperature Observation"
Description: "A platform-exclusive coverage summary of one SensorKit wrist-temperature session; the wrist-temperature-samples recording document carries the samples and is mandatory. This is a wrist skin measurement: it deliberately binds to no body-temperature or basal-body-temperature meaning, because a sleep-interval wrist reading is neither."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #wrist-temperature
* code = $sensorKitConcept#wrist-temperature-recording-summary
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* derivedFrom 1..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains sampleCount 1..1 MS
* component[sampleCount].code = $sensorKitConcept#sample-count
* component[sampleCount].value[x] 1..1 MS
* component[sampleCount].value[x] only Quantity
* component[sampleCount].valueQuantity.system = $ucum (exactly)
* component[sampleCount].valueQuantity.code = #{count} (exactly)
* component[sampleCount].dataAbsentReason 0..0
// A version string alone is not a self-describing method concept, and Coding.version is the
// version of a code system. Preserve this opaque source fact without inventing either meaning.
* extension contains SensorKitWristTemperatureAlgorithmVersion named algorithmVersion 1..1 MS


Profile: SensorKitAccelerometerObservation
Parent: SensorKitObservation
Id: sensorkit-accelerometer-observation
Title: "SensorKit Accelerometer Observation"
Description: "A platform-exclusive coverage summary of one SensorKit accelerometer recording spanning one or more CoreMotion delivery batches; the triaxial-acceleration-samples recording document carries the signal and is mandatory."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #accelerometer
* code = $sensorKitConcept#accelerometer-recording-summary
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* derivedFrom 1..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains sampleCount 1..1 MS and batchCount 1..1 MS
* component[sampleCount].code = $sensorKitConcept#sample-count
* component[sampleCount].value[x] 1..1 MS
* component[sampleCount].value[x] only Quantity
* component[sampleCount].valueQuantity.system = $ucum (exactly)
* component[sampleCount].valueQuantity.code = #{count} (exactly)
* component[sampleCount].dataAbsentReason 0..0
* component[batchCount].code = $sensorKitConcept#batch-count
* component[batchCount].value[x] 1..1 MS
* component[batchCount].value[x] only Quantity
* component[batchCount].valueQuantity.system = $ucum (exactly)
* component[batchCount].valueQuantity.code = #{count} (exactly)
* component[batchCount].dataAbsentReason 0..0

Profile: SensorKitPpgObservation
Parent: SensorKitObservation
Id: sensorkit-ppg-observation
Title: "SensorKit PPG Observation"
Description: "A platform-exclusive coverage summary of one SensorKit photoplethysmogram batch; the photoplethysmogram-samples recording document carries the signal and is mandatory."
* obeys sensorkit-summary-quantity-nonnegative-1 and sensorkit-summary-count-integer-1
* extension[sensorKitSourceType].valueCode = #ppg
* code = $sensorKitConcept#ppg-recording-summary
* effective[x] 1..1 MS
* effective[x] only Period
* value[x] 0..0
* dataAbsentReason 0..0
* derivedFrom 1..1 MS
* derivedFrom only Reference(SensorKitRecordingDocument)
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #closed
* component contains recordCount 1..1 MS and opticalSampleCount 1..1 MS and accelerometerSampleCount 1..1 MS
* component[recordCount].code = $sensorKitConcept#record-count
* component[recordCount].value[x] 1..1 MS
* component[recordCount].value[x] only Quantity
* component[recordCount].valueQuantity.system = $ucum (exactly)
* component[recordCount].valueQuantity.code = #{count} (exactly)
* component[recordCount].dataAbsentReason 0..0
* component[opticalSampleCount].code = $sensorKitConcept#optical-sample-count
* component[opticalSampleCount].value[x] 1..1 MS
* component[opticalSampleCount].value[x] only Quantity
* component[opticalSampleCount].valueQuantity.system = $ucum (exactly)
* component[opticalSampleCount].valueQuantity.code = #{count} (exactly)
* component[opticalSampleCount].dataAbsentReason 0..0
* component[accelerometerSampleCount].code = $sensorKitConcept#accelerometer-sample-count
* component[accelerometerSampleCount].value[x] 1..1 MS
* component[accelerometerSampleCount].value[x] only Quantity
* component[accelerometerSampleCount].valueQuantity.system = $ucum (exactly)
* component[accelerometerSampleCount].valueQuantity.code = #{count} (exactly)
* component[accelerometerSampleCount].dataAbsentReason 0..0
