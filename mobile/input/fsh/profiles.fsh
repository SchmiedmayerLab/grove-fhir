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

Invariant: grove-patient-reference-shape-1
Description: "An Observation subject is either a literal Patient reference or one typed identifier-only logical Patient pseudonym, never both."
Expression: "(subject.reference.exists() and subject.identifier.empty()) or (subject.reference.empty() and subject.type = 'Patient' and subject.identifier.count() = 1 and subject.identifier.system.matches('^[A-Za-z][A-Za-z0-9+.-]*:') and subject.identifier.value.exists())"
Severity: #error

Invariant: grove-mobile-effective-1
Description: "A mobile Observation effective dateTime and every effective Period bound state a time of day, which FHIR requires to carry a UTC offset."
Expression: "(effective.ofType(dateTime) | effective.ofType(Period).start | effective.ofType(Period).end).all($this.toString().contains('T'))"
Severity: #error

Invariant: grove-mobile-code-system-1
Description: "A mobile Observation code is coded in LOINC, the IEEE 11073 MDC nomenclature, or a Grove code system."
Expression: "code.coding.exists() and code.coding.all(system = 'http://loinc.org' or system = 'urn:iso:std:iso:11073:10101' or (system.startsWith('https://grovealliance.org/fhir/') and system.contains('/CodeSystem/')))"
Severity: #error

Invariant: grove-mobile-body-site-1
Description: "A mobile Observation body site is coded in SNOMED CT."
Expression: "bodySite.all(coding.exists() and coding.all(system = 'http://snomed.info/sct'))"
Severity: #error

Invariant: grove-mobile-method-1
Description: "A mobile Observation method is coded in SNOMED CT or a Grove code system."
Expression: "method.all(coding.exists() and coding.all(system = 'http://snomed.info/sct' or (system.startsWith('https://grovealliance.org/fhir/') and system.contains('/CodeSystem/'))))"
Severity: #error

Invariant: grove-step-count-result-1
Description: "A step-count Observation has a count value or a reason why the count is absent."
Expression: "value.exists() or dataAbsentReason.exists()"
Severity: #error

Invariant: grove-step-count-period-1
Description: "A step or wheelchair-push count Observation has a non-zero effective Period."
Expression: "effective.ofType(Period).end > effective.ofType(Period).start"
Severity: #error

Invariant: grove-exchange-full-url-1
Description: "Every exchange entry has a distinct lowercase RFC 4122 UUID URN fullUrl."
Expression: "entry.all(fullUrl.matches('^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')) and entry.fullUrl.isDistinct()"
Severity: #error

Invariant: grove-exchange-entry-identity-1
Description: "Exchange entry-key system and value pairs are distinct."
Expression: "entry.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value).isDistinct()"
Severity: #error

Invariant: grove-opaque-identifier-value-1
Description: "A pseudonymous Grove identifier is a canonical v0 HMAC value carrying its key id and positive key epoch."
Expression: "$this.matches('^v0:[A-Za-z0-9._-]+:[1-9][0-9]*:[A-Za-z0-9_-]{43}$')"
Severity: #error

Invariant: grove-active-bundle-provenance-1
Description: "An active exchange Bundle contains at least one Provenance, one per record, and each has exactly one ISO transform lifecycle coding and no Grove retraction lifecycle coding."
Expression: "entry.resource.ofType(Provenance).exists() and entry.resource.ofType(Provenance).all(activity.coding.where(system = 'http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle').count() = 1 and activity.coding.where(system = 'http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle' and code = 'transform').count() = 1 and activity.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event').empty())"
Severity: #error

Invariant: grove-retraction-bundle-provenance-1
Description: "A retraction exchange Bundle contains at least one Provenance, one per retracted source record; each has exactly one Grove source-record-retracted lifecycle coding and no ISO lifecycle coding, and the Bundle carries no active clinical resource."
Expression: "entry.resource.ofType(Provenance).exists() and entry.resource.ofType(Provenance).all(activity.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event').count() = 1 and activity.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event' and code = 'source-record-retracted').count() = 1 and activity.coding.where(system = 'http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle').empty()) and entry.resource.all($this is Provenance or $this is Device)"
Severity: #error

Invariant: grove-exchange-target-distinct-1
Description: "No two Provenance targets in one exchange Bundle name the same entry, so every output is targeted by exactly one Provenance."
Expression: "entry.resource.ofType(Provenance).target.reference.isDistinct()"
Severity: #error

Invariant: grove-exchange-output-target-1
Description: "Every output entry of an active exchange Bundle is a target of a conversion Provenance in the same Bundle."
Expression: "entry.where(resource is Observation or resource is DocumentReference or resource is Specimen or resource is VisionPrescription or resource is MedicationAdministration or resource is MedicationStatement).all(fullUrl in %resource.entry.resource.ofType(Provenance).target.reference)"
Severity: #error

Invariant: grove-record-version-entry-key-1
Description: "Every conversion Provenance repeats its Bundle entry key, its record-version Identifier, in exactly one grove-record-version extension with the same system and value."
Expression: "entry.where(resource is Provenance).all(resource.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-record-version').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value) = extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value))"
Severity: #error

Invariant: grove-context-snapshot-entry-key-1
Description: "Every QuestionnaireResponse repeats its Bundle entry key, its context-snapshot Identifier, in exactly one grove-context-snapshot extension with the same system and value."
Expression: "entry.where(resource is QuestionnaireResponse).all(resource.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-context-snapshot').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value) = extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-key').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value))"
Severity: #error

Invariant: grove-retraction-no-record-version-1
Description: "A retraction Provenance carries no grove-record-version: its record-retraction key is carried only as its Bundle entry key."
Expression: "extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-record-version').empty()"
Severity: #error

Invariant: grove-active-entry-resource-type-1
Description: "Every active Bundle entry is one admitted output, lifecycle assertion, or supporting-context resource."
Expression: "entry.resource.all($this is Observation or $this is DocumentReference or $this is Specimen or $this is VisionPrescription or $this is MedicationAdministration or $this is MedicationStatement or $this is Provenance or $this is Patient or $this is Device or $this is ResearchStudy or $this is ResearchSubject or $this is PlanDefinition or $this is QuestionnaireResponse)"
Severity: #error

Invariant: grove-exchange-contained-resource-1
Description: "A Mobile exchange Bundle uses addressable Bundle entries and does not carry contained resources."
Expression: "entry.resource.ofType(DomainResource).contained.empty()"
Severity: #error

Invariant: grove-active-output-profile-1
Description: "Every active output directly declares at least one profile; the producer conformance gate applies the exact catalog mode."
Expression: "entry.resource.where($this is Observation or $this is DocumentReference or $this is Specimen or $this is VisionPrescription or $this is MedicationAdministration or $this is MedicationStatement).all(meta.profile.exists())"
Severity: #error

Invariant: grove-active-document-profile-1
Description: "Every active DocumentReference uses exactly one admitted source-neutral or adapter document profile mode."
Expression: "entry.resource.ofType(DocumentReference).all((meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document').count() = 1) or (meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-clinical-record-document').count() = 1) or (meta.profile.count() = 2 and meta.profile.where($this = 'https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document').count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-recording-document' or $this = 'https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-recording-document' or $this = 'https://grovealliance.org/fhir/providers/StructureDefinition/providers-recording-document').count() = 1))"
Severity: #error

Invariant: grove-active-device-profile-1
Description: "Every active Device directly declares exactly one admitted Grove Device profile."
Expression: "entry.resource.ofType(Device).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-recording-device' or $this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-application-device' or $this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-host-device' or $this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-application-device').count() = 1)"
Severity: #error

Invariant: grove-active-questionnaire-response-profile-1
Description: "Every active QuestionnaireResponse directly declares only the Grove QuestionnaireResponse profile."
Expression: "entry.resource.ofType(QuestionnaireResponse).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/questionnaire/StructureDefinition/grove-questionnaire-response').count() = 1)"
Severity: #error

Invariant: grove-active-provenance-profile-1
Description: "Every active lifecycle Provenance directly declares exactly one admitted Mobile or adapter conversion profile."
Expression: "entry.resource.ofType(Provenance).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-conversion-provenance' or $this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-conversion-provenance' or $this = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-conversion-provenance' or $this = 'https://grovealliance.org/fhir/providers/StructureDefinition/providers-conversion-provenance' or $this = 'https://grovealliance.org/fhir/sensorkit/StructureDefinition/sensorkit-conversion-provenance').count() = 1)"
Severity: #error

Invariant: grove-active-adapter-output-profile-1
Description: "Every adapter-only output directly declares exactly its one admitted adapter profile."
Expression: "entry.resource.ofType(Specimen).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-specimen').count() = 1) and entry.resource.ofType(VisionPrescription).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-vision-prescription').count() = 1) and entry.resource.ofType(MedicationAdministration).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-medication-dose-event').count() = 1) and entry.resource.ofType(MedicationStatement).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-user-annotated-medication').count() = 1)"
Severity: #error

Invariant: grove-retraction-direct-profile-1
Description: "Retraction Provenance and optional Device agents directly declare only their admitted Grove profiles."
Expression: "entry.resource.ofType(Provenance).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-retraction-provenance').count() = 1) and entry.resource.ofType(Device).all(meta.profile.count() = 1 and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-recording-device' or $this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-application-device' or $this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-host-device' or $this = 'https://grovealliance.org/fhir/healthkit/StructureDefinition/healthkit-application-device').count() = 1)"
Severity: #error

Invariant: grove-identifier-role-coding-1
Description: "Each business Identifier carries at most one coding from the Grove identifier-role system."
Expression: "identifier.all(type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role').count() <= 1)"
Severity: #error

Invariant: grove-transform-lifecycle-coding-1
Description: "A conversion Provenance has exactly one ISO lifecycle coding, transform, and no Grove lifecycle coding; translations from other systems remain open."
Expression: "activity.coding.where(system = 'http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle').count() = 1 and activity.coding.where(system = 'http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle' and code = 'transform').count() = 1 and activity.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event').empty()"
Severity: #error

Invariant: grove-retraction-lifecycle-coding-1
Description: "A retraction Provenance has exactly one Grove lifecycle coding, source-record-retracted, and no ISO lifecycle coding; translations from other systems remain open."
Expression: "activity.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event').count() = 1 and activity.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-lifecycle-event' and code = 'source-record-retracted').count() = 1 and activity.coding.where(system = 'http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle').empty()"
Severity: #error

Invariant: grove-retraction-target-1
Description: "Every retraction target is a logical Reference with one complete identifier, one Grove output role, and no literal reference; every target except a source-record target states its resource type."
Expression: "target.all(reference.empty() and (type.exists() or extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').where(value = 'source-record').exists()) and identifier.system.exists() and identifier.value.exists() and extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').count() = 1)"
Severity: #error

Invariant: grove-native-record-identifier-1
Description: "A native record identifier names an absolute adapter-owned key space and never carries a Grove identifier-role coding, because it is source-native traceability rather than a Grove graph key."
Expression: "system.matches('^[A-Za-z][A-Za-z0-9+.-]*:') and value.exists() and type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role').empty()"
Severity: #error

Invariant: grove-lifecycle-source-entity-1
Description: "A lifecycle Provenance identifies exactly one source record as a logical source-role Identifier entity, never a literal Reference."
Expression: "entity.count() = 1 and entity.all(role = 'source' and what.reference.empty() and what.identifier.count() = 1 and what.identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role').count() = 1 and what.identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-record').count() = 1)"
Severity: #error

Invariant: grove-retraction-target-semantics-1
Description: "Every retraction role fixes its logical target resource type and Identifier role."
Expression: "target.all((extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').where(value = 'primary-output').exists() implies ((type = 'Observation' or type = 'VisionPrescription' or type = 'MedicationAdministration' or type = 'MedicationStatement') and identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-output').count() = 1)) and (extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').where(value = 'source-artifact').exists() implies (type = 'DocumentReference' and identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-output').count() = 1)) and (extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').where(value = 'child-output').exists() implies (type = 'Observation' and identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-output').count() = 1)) and (extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').where(value = 'specimen').exists() implies (type = 'Specimen' and identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-output').count() = 1)))"
Severity: #error

Invariant: grove-retraction-source-record-target-1
Description: "A source-record target is the retraction's only target, states no resource type, carries the source-record Identifier role, and repeats the exact source-record Identifier of the Provenance source entity."
Expression: "target.where(extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-retraction-target-role').where(value = 'source-record').exists()).exists() implies (target.count() = 1 and target.type.empty() and target.identifier.type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'source-record').count() = 1 and target.identifier.system = entity.what.identifier.system and target.identifier.value = entity.what.identifier.value)"
Severity: #error

Invariant: grove-writer-version-requires-identity-1
Description: "A writer record version never appears without the typed writer-record identity it versions; an identity may stand alone when the source supplies no revision number."
Expression: "extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-writer-record-version').exists() implies identifier.where(type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'writer-record').exists()).exists()"
Severity: #error

RuleSet: CompleteIdentifierPairs
* identifier.system 1..1 MS
* identifier.value 1..1 MS

RuleSet: GroveOpaqueIdentifier(path, role)
* {path}.type 1..1 MS
* {path}.type = GroveIdentifierRoleCS#{role}
* {path}.system 1..1 MS
* {path}.value 1..1 MS
* {path}.value obeys grove-opaque-identifier-value-1

RuleSet: GroveOutputIdentitySlices
* obeys grove-writer-version-requires-identity-1
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #open
* identifier contains sourceRecord 1..1 MS and sourceOutput 1..1 MS and writerRecord 0..1 MS
* insert GroveOpaqueIdentifier(identifier[sourceRecord], source-record)
* insert GroveOpaqueIdentifier(identifier[sourceOutput], source-output)
* insert GroveOpaqueIdentifier(identifier[writerRecord], writer-record)

RuleSet: GroveMobileObservationRules
* obeys grove-mobile-result-1 and grove-identifier-token-1 and grove-identifier-role-coding-1 and grove-patient-reference-shape-1 and grove-mobile-effective-1 and grove-mobile-code-system-1 and grove-mobile-body-site-1 and grove-mobile-method-1
* insert CompleteIdentifierPairs
* insert GroveOutputIdentitySlices
* identifier 2..* MS
* identifier ^short = "Typed, deployment-scoped opaque source-record and exact output identifiers"
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
* dataAbsentReason from http://hl7.org/fhir/ValueSet/data-absent-reason (required)
* component MS
* component.dataAbsentReason from http://hl7.org/fhir/ValueSet/data-absent-reason (required)
* bodySite MS
* method MS
* device MS
* device only Reference(Device)
* hasMember MS
* derivedFrom MS
* extension contains
    GroveRecordingMethod named recordingMethod 0..1 MS and
    $gatewayDevice named gatewayDevice 0..1 MS and
    $researchStudy named researchStudy 0..* MS
* extension[gatewayDevice].valueReference only Reference(GroveApplicationDevice)
* extension[researchStudy].valueReference only Reference(ResearchStudy)

RuleSet: GroveMobilePointObservationContextRules
* obeys grove-identifier-token-1 and grove-identifier-role-coding-1
* insert CompleteIdentifierPairs
* insert GroveOutputIdentitySlices
* identifier 2..* MS
* identifier ^short = "Typed, deployment-scoped opaque source-record and exact output identifiers"
* subject 1..1 MS
* subject only Reference(Patient)
* effectiveDateTime 1..1 MS
* effectiveDateTime.extension contains $timezone named timezone 0..1 MS
* issued MS
* device MS
* device only Reference(Device)
* derivedFrom MS
* extension contains
    GroveRecordingMethod named recordingMethod 0..1 MS and
    $gatewayDevice named gatewayDevice 0..1 MS and
    $researchStudy named researchStudy 0..* MS
* extension[gatewayDevice].valueReference only Reference(GroveApplicationDevice)
* extension[researchStudy].valueReference only Reference(ResearchStudy)

Extension: GroveExchangeEntryKey
Id: grove-exchange-entry-key
Title: "Grove Exchange Entry Key"
Description: "The selected complete Identifier from which an exchange entry fullUrl is derived. It is one of three kinds: an output's selected business Identifier, its highest-priority typed Identifier from the exchange protocol; a shared node's content-snapshot key, which the node also carries as its typed device-snapshot or context-snapshot Resource.identifier, or a QuestionnaireResponse in its grove-context-snapshot extension; or, for a Provenance, its record-version key (active) or record-retraction key (retraction). This graph key is not a Provenance business identifier."
Context: Bundle.entry
* value[x] only Identifier
* valueIdentifier 1..1
* valueIdentifier.type 1..1 MS
* valueIdentifier.system 1..1 MS
* valueIdentifier.value 1..1 MS

Profile: GroveMobileExchangeBundle
Parent: Bundle
Id: grove-mobile-exchange-bundle
Title: "Grove Mobile Exchange Bundle"
Description: "One upload of one or more active records of one subject. A record is one immutable source-record revision, every output derived from it, and exactly one conversion Provenance targeting those outputs, keyed by its record version. Shared nodes, such as the Patient and the application, host, and recording Devices, are content-addressed and appear once however many records reference them. The Bundle is a container: packing records into Bundles, or repacking them, changes no record. Entry UUID URNs are deterministic formatting of typed entry keys; Resource.id is not source identity."
* obeys grove-exchange-full-url-1 and grove-exchange-entry-identity-1 and grove-active-bundle-provenance-1 and grove-exchange-target-distinct-1 and grove-exchange-output-target-1 and grove-record-version-entry-key-1 and grove-context-snapshot-entry-key-1 and grove-active-entry-resource-type-1 and grove-exchange-contained-resource-1 and grove-active-output-profile-1 and grove-active-document-profile-1 and grove-active-device-profile-1 and grove-active-questionnaire-response-profile-1 and grove-active-provenance-profile-1 and grove-active-adapter-output-profile-1
* identifier 0..1
* identifier ^short = "Optional untyped transport id; it names no record and enters no identity"
* identifier.type 0..0
* type = #collection
* timestamp 1..1 MS
* timestamp ^short = "When the Bundle was packed; enters no identity"
* entry 1..* MS
* entry.extension contains GroveExchangeEntryKey named entryKey 1..1 MS
* entry.fullUrl 1..1 MS
* entry.resource 1..1 MS
* entry.search 0..0
* entry.request 0..0
* entry.response 0..0

Profile: GroveRecordingDevice
Parent: Device
Id: grove-recording-device
Title: "Grove Recording Device"
Description: "An immutable content snapshot of the physical device that acquired a measurement. The recording-device identifier proves stable per-unit identity; the device-snapshot identifier is its content key: the same content gives the same key in every Bundle, and changed firmware, software, or other facts give a new snapshot instead of mutating one shared Device. Observation.device references this profile only when a governed stable per-unit token is available."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1 and grove-identifier-role-coding-1
* identifier 2..2 MS
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #closed
* identifier contains physicalUnit 1..1 MS and snapshot 1..1 MS
* insert GroveOpaqueIdentifier(identifier[physicalUnit], recording-device)
* insert GroveOpaqueIdentifier(identifier[snapshot], device-snapshot)
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
Description: "An immutable content snapshot of the software application that saved, routed, or converted a mobile record. The application is distinct from the physical recording device and from its host hardware. Its device-snapshot identifier is its content key, so changed release or build facts, or a changed host it names as parent, give a new snapshot rather than mutating a shared Device."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1 and grove-identifier-role-coding-1
* identifier 1..* MS
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #open
* identifier contains applicationSnapshot 1..1 MS
* insert GroveOpaqueIdentifier(identifier[applicationSnapshot], device-snapshot)
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
* version contains applicationVersion 0..1 MS and applicationBuild 0..1 MS
* version[applicationVersion].type 1..1 MS
* version[applicationVersion].type = $mdc#531975
* version[applicationVersion].value 1..1 MS
* version[applicationBuild].type 1..1 MS
* version[applicationBuild].type = $groveApplicationVersionType#build
* version[applicationBuild].value 1..1 MS
* parent MS
* parent only Reference(GroveHostDevice)

Profile: GroveHostDevice
Parent: Device
Id: grove-host-device
Title: "Grove Host Device Snapshot"
Description: "An immutable content snapshot of the host hardware and operating system on which a Grove application converted a record. Its device-snapshot identifier is its content key, so a changed operating-system version gives a new snapshot. It is not the physical recording Device unless the source explicitly establishes that identity."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1 and grove-identifier-role-coding-1
* identifier 1..1 MS
* insert GroveOpaqueIdentifier(identifier, device-snapshot)
* status MS
* manufacturer MS
* modelNumber MS
* deviceName MS
* version ^slicing.discriminator.type = #pattern
* version ^slicing.discriminator.path = "type"
* version ^slicing.rules = #open
* version contains operatingSystemVersion 1..1 MS
* version[operatingSystemVersion].type 1..1 MS
* version[operatingSystemVersion].type = $groveApplicationVersionType#os-version
* version[operatingSystemVersion].value 1..1 MS

Profile: GroveMobileObservation
Parent: Observation
Id: grove-mobile-observation
Title: "Grove Mobile Observation"
Description: "A source-neutral FHIR R4 exchange envelope for a measurement collected through a mobile application or connected device. Combine it with an appropriate clinical or research profile."
* ^abstract = true
* insert GroveMobileObservationRules

Profile: GroveMobileConversionProvenance
Parent: Provenance
Id: grove-mobile-conversion-provenance
Title: "Grove Mobile Conversion Provenance"
Description: "Provenance for the application that transformed exactly one source record revision into every output of one record. It targets each output of its record exactly once, and repeats its record-version key, its Bundle entry key, in grove-record-version, so a consumer that stores the Provenance alone keeps it."
* obeys grove-transform-lifecycle-coding-1 and grove-lifecycle-source-entity-1
* extension contains GroveRecordVersion named recordVersion 1..1 MS
* extension[recordVersion] ^short = "The record-version Identifier of this record version, equal to its Bundle entry key"
* target 1..* MS
* target only Reference(Observation or DocumentReference or VisionPrescription or MedicationAdministration or MedicationStatement or Specimen)
* occurred[x] 1..1 MS
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
* entity 1..1 MS
* entity.role 1..1 MS
* entity.role = #source
* entity.what 1..1 MS
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.type 1..1 MS
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys grove-opaque-identifier-value-1

Profile: GroveMobileRetractionProvenance
Parent: Provenance
Id: grove-mobile-retraction-provenance
Title: "Grove Mobile Retraction Provenance"
Description: "An append-only assertion that the source record named by its source entity is no longer exposed. It suppresses every output of every version of that record; its targets name what the producer emitted, or the source record as a whole, and are informative. It is not a FHIR delete command and does not assert that the prior clinical result was erroneous."
* obeys grove-retraction-target-1 and grove-retraction-lifecycle-coding-1 and grove-lifecycle-source-entity-1 and grove-retraction-target-semantics-1 and grove-retraction-source-record-target-1 and grove-retraction-no-record-version-1
* target 1..* MS
* target only Reference(Observation or DocumentReference or VisionPrescription or MedicationAdministration or MedicationStatement or Specimen or QuestionnaireResponse)
* target.reference 0..0
* target.type 0..1 MS
* target.identifier 1..1 MS
* target.identifier.type 1..1 MS
* target.identifier.system 1..1 MS
* target.identifier.value 1..1 MS
* target.identifier.value obeys grove-opaque-identifier-value-1
* target.extension contains
    GroveRetractionTargetRole named targetRole 1..1 MS and
    GroveRetractionTargetNativeIdentifier named nativeIdentifier 0..1 MS
* occurred[x] 1..1 MS
* recorded 1..1 MS
* activity 1..1 MS
* activity = GroveLifecycleEventCS#source-record-retracted
* agent 1..* MS
* agent ^slicing.discriminator.type = #pattern
* agent ^slicing.discriminator.path = "type"
* agent ^slicing.rules = #open
* agent contains assembler 1..1 MS
* agent[assembler].type 1..1 MS
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who 1..1 MS
* agent[assembler].who only Reference(GroveApplicationDevice)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.type 1..1 MS
* entity.what.identifier.type = GroveIdentifierRoleCS#source-record
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys grove-opaque-identifier-value-1

Profile: GroveMobileRetractionBundle
Parent: Bundle
Id: grove-mobile-retraction-bundle
Title: "Grove Mobile Retraction Bundle"
Description: "One upload of one or more retraction records of one subject: one retraction Provenance per retracted source record, each keyed by its record-retraction key, plus the shared application Device that assembled them and its host. It never mixes with active records and never copies or mutilates the prior clinical outputs."
* obeys grove-exchange-full-url-1 and grove-exchange-entry-identity-1 and grove-retraction-bundle-provenance-1 and grove-exchange-contained-resource-1 and grove-retraction-direct-profile-1
* identifier 0..1
* identifier ^short = "Optional untyped transport id; it names no record and enters no identity"
* identifier.type 0..0
* type = #collection
* timestamp 1..1 MS
* timestamp ^short = "When the Bundle was packed; enters no identity"
* entry 1..* MS
* entry.extension contains GroveExchangeEntryKey named entryKey 1..1 MS
* entry.fullUrl 1..1 MS
* entry.resource 1..1 MS
* entry.search 0..0
* entry.request 0..0
* entry.response 0..0


Invariant: grove-writer-record-version-value-1
Description: "A writer record version is a canonical non-negative decimal integer, written without a sign, leading zeros, or separators."
Expression: "$this.matches('^(0|[1-9][0-9]*)$')"
Severity: #error
