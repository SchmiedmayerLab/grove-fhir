//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: grove-mobile-result-1
Description: "A mobile Observation has a value, one or more components or members, or a reason why the result is absent."
Expression: "value.exists() or component.where(value.exists() or dataAbsentReason.exists()).exists() or hasMember.exists() or dataAbsentReason.exists()"
Severity: #error

Invariant: grove-identifier-token-1
Description: "A resource does not repeat the same identifier system and value pair."
Expression: "identifier.select(system.length().toString() & ':' & system & value.length().toString() & ':' & value).isDistinct()"
Severity: #error

Invariant: grove-step-count-result-1
Description: "A step-count Observation has a count value or a reason why the count is absent."
Expression: "value.exists() or dataAbsentReason.exists()"
Severity: #error

Invariant: grove-step-count-period-1
Description: "A step-count Observation has a non-zero effective Period."
Expression: "effective.ofType(Period).end > effective.ofType(Period).start"
Severity: #error

Invariant: grove-step-count-value-1
Description: "A populated step count is not negative."
Expression: "value.empty() or value.ofType(Quantity).value >= 0"
Severity: #error

RuleSet: CompleteIdentifierPairs
* identifier.system 1..1 MS
* identifier.value 1..1 MS

RuleSet: GroveMobileObservationRules
* obeys grove-mobile-result-1 and grove-identifier-token-1
* insert CompleteIdentifierPairs
* identifier 1..* MS
* identifier ^short = "Stable business identifier used to deduplicate this exchanged record"
* status 1..1 MS
* category MS
* code 1..1 MS
* subject 1..1 MS
* subject only Reference(Patient)
* effective[x] 1..1 MS
* effective[x] only dateTime or Period
* effectiveDateTime MS
* effectiveDateTime.extension contains $timezone named timezone 0..1 MS
* effectivePeriod MS
* effectivePeriod.start 1..1 MS
* effectivePeriod.start.extension contains $timezone named startTimezone 0..1 MS
* effectivePeriod.end MS
* effectivePeriod.end.extension contains $timezone named endTimezone 0..1 MS
* issued MS
* value[x] MS
* dataAbsentReason MS
* component MS
* bodySite MS
* method MS
* device MS
* hasMember MS
* derivedFrom MS
* extension contains
    GroveRecordingMethod named recordingMethod 0..1 MS and
    $gatewayDevice named gatewayDevice 0..1 MS and
    $researchStudy named researchStudy 0..* MS
* extension[gatewayDevice].valueReference only Reference(GroveApplicationDevice)
* extension[researchStudy].valueReference only Reference(ResearchStudy)

Profile: GroveRecordingDevice
Parent: Device
Id: grove-recording-device
Title: "Grove Recording Device"
Description: "The physical device that acquired a measurement. Observation.device references this profile only when the recorder is known."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1
* identifier MS
* status MS
* type MS
* deviceName MS
* manufacturer MS
* modelNumber MS
* version MS
* version.type 1..1 MS
* version.value MS

Profile: GroveApplicationDevice
Parent: Device
Id: grove-application-device
Title: "Grove Application Device"
Description: "The software application that saved, routed, or converted a mobile record. The application is distinct from the physical recording device and from its host hardware."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1
* identifier 1..* MS
* deviceName 1..* MS
* deviceName ^slicing.discriminator.type = #value
* deviceName ^slicing.discriminator.path = "type"
* deviceName ^slicing.rules = #open
* deviceName contains applicationName 1..1 MS
* deviceName[applicationName].name 1..1 MS
* deviceName[applicationName].type = #user-friendly-name
* version ^slicing.discriminator.type = #pattern
* version ^slicing.discriminator.path = "type"
* version ^slicing.rules = #open
* version contains applicationVersion 0..1 MS
* version[applicationVersion].type 1..1 MS
* version[applicationVersion].type = $mdc#531975
* version[applicationVersion].value 1..1 MS
* parent MS
* parent only Reference(Device)

Profile: GroveMobileObservation
Parent: Observation
Id: grove-mobile-observation
Title: "Grove Mobile Observation"
Description: "A source-neutral FHIR R4 exchange envelope for a measurement collected through a mobile application or connected device. Combine it with an appropriate clinical or research profile."
* insert GroveMobileObservationRules

Profile: GroveMobileStepCount
Parent: GroveMobileObservation
Id: grove-mobile-step-count
Title: "Grove Mobile Step Count"
Description: "The number of steps recorded during an exact effective Period."
* obeys grove-step-count-result-1 and grove-step-count-period-1 and grove-step-count-value-1
* code = GroveMobileMeasurementCS#step-count-total
* code from GroveMobileMeasurementVS (required)
* effectiveDateTime 0..0
* effectivePeriod 1..1 MS
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.unit MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{steps} (exactly)

Profile: GroveMobileConversionProvenance
Parent: Provenance
Id: grove-mobile-conversion-provenance
Title: "Grove Mobile Conversion Provenance"
Description: "Provenance for the application that transformed one or more source records into mobile Observations."
* target 1..* MS
* target only Reference(GroveMobileObservation)
* occurred[x] MS
* recorded 1..1 MS
* activity 1..1 MS
* activity = $recordLifecycleEvent#transform
* agent 1..* MS
* agent ^slicing.discriminator.type = #pattern
* agent ^slicing.discriminator.path = "type"
* agent ^slicing.rules = #open
* agent contains assembler 1..1 MS
* agent[assembler].type 1..1 MS
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who 1..1 MS
* agent[assembler].who only Reference(GroveApplicationDevice)
* entity 1..* MS
* entity.role 1..1 MS
* entity.role = #source
* entity.what MS
