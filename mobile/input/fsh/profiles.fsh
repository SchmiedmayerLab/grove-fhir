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

Invariant: grove-exchange-full-url-1
Description: "Every exchange entry has a distinct lowercase RFC 4122 UUID URN fullUrl."
Expression: "entry.all(fullUrl.matches('^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')) and entry.fullUrl.isDistinct()"
Severity: #error

Invariant: grove-exchange-entry-identity-1
Description: "Exchange entry business identifier system and value pairs are distinct."
Expression: "entry.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-identifier').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value).isDistinct()"
Severity: #error

RuleSet: CompleteIdentifierPairs
* identifier.system 1..1 MS
* identifier.value 1..1 MS

RuleSet: GroveMobileObservationRules
* obeys grove-mobile-result-1 and grove-identifier-token-1
* insert CompleteIdentifierPairs
* identifier 1..* MS
* identifier ^short = "Stable business identifier used to deduplicate this exchanged record"
* extension contains GroveWriterRecordVersion named writerRecordVersion 0..1 MS
* extension[writerRecordVersion] ^short = "Writer's version of the logical record this measurement came from"
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

RuleSet: GroveMobilePointObservationContextRules
* obeys grove-identifier-token-1
* insert CompleteIdentifierPairs
* identifier 1..* MS
* identifier ^short = "Stable business identifier used to deduplicate this exchanged record"
* subject 1..1 MS
* subject only Reference(Patient)
* effectiveDateTime 1..1 MS
* effectiveDateTime.extension contains $timezone named timezone 0..1 MS
* issued MS
* device MS
* derivedFrom MS
* extension contains
    GroveRecordingMethod named recordingMethod 0..1 MS and
    $gatewayDevice named gatewayDevice 0..1 MS and
    $researchStudy named researchStudy 0..* MS
* extension[gatewayDevice].valueReference only Reference(GroveApplicationDevice)
* extension[researchStudy].valueReference only Reference(ResearchStudy)

Extension: GroveExchangeEntryIdentifier
Id: grove-exchange-entry-identifier
Title: "Grove Exchange Entry Identifier"
Description: "The complete business identifier from which an exchange Bundle entry fullUrl is deterministically derived. It identifies the graph node and does not replace a resource's native identifier or canonical URL."
Context: Bundle.entry
* value[x] only Identifier
* valueIdentifier 1..1
* valueIdentifier.system 1..1 MS
* valueIdentifier.value 1..1 MS

Profile: GroveMobileExchangeBundle
Parent: Bundle
Id: grove-mobile-exchange-bundle
Title: "Grove Mobile Exchange Bundle"
Description: "A source-neutral collection Bundle carrying one internally consistent mobile health resource graph. Entry UUID URNs are deterministic from complete entry business identifiers; Resource.id is not used for source identity."
* obeys grove-exchange-full-url-1 and grove-exchange-entry-identity-1
* identifier 1..1 MS
* identifier.system 1..1 MS
* identifier.value 1..1 MS
* type = #collection
* timestamp 1..1 MS
* entry 1..* MS
* entry.extension contains GroveExchangeEntryIdentifier named entryIdentifier 1..1 MS
* entry.fullUrl 1..1 MS
* entry.resource 1..1 MS
* entry.search 0..0
* entry.request 0..0
* entry.response 0..0

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
* version contains applicationVersion 0..1 MS and applicationBuild 0..1 MS and operatingSystemVersion 0..1 MS
* version[applicationVersion].type 1..1 MS
* version[applicationVersion].type = $mdc#531975
* version[applicationVersion].value 1..1 MS
* version[applicationBuild].type 1..1 MS
* version[applicationBuild].type = $groveApplicationVersionType#build
* version[applicationBuild].value 1..1 MS
* version[operatingSystemVersion].type 1..1 MS
* version[operatingSystemVersion].type = $groveApplicationVersionType#os-version
* version[operatingSystemVersion].value 1..1 MS
* parent MS
* parent only Reference(Device)

Profile: GroveMobileObservation
Parent: Observation
Id: grove-mobile-observation
Title: "Grove Mobile Observation"
Description: "A source-neutral FHIR R4 exchange envelope for a measurement collected through a mobile application or connected device. Combine it with an appropriate clinical or research profile."
* insert GroveMobileObservationRules

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


Invariant: grove-writer-record-version-value-1
Description: "A writer record version is a canonical non-negative decimal integer, written without a sign, leading zeros, or separators."
Expression: "$this.matches('^(0|[1-9][0-9]*)$')"
Severity: #error


Invariant: grove-writer-record-id-value-1
Description: "A writer record identifier scopes the writer's own identifier to the writer: the scheme version, the writing application's reverse-DNS identifier, a vertical bar, then the identifier it assigned. Neither part may contain a vertical bar."
Expression: "$this.matches('^v1:[A-Za-z0-9._-]+[|].+$')"
Severity: #error
