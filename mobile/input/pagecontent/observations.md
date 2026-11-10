<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A mobile measurement is a FHIR R4 `Observation`.
For the shared measurements below, the Grove profile imposes the authoritative FHIR R4 Vital Signs profile when one exists and adds source-neutral exchange identity and provenance context.
The generic [Grove Mobile Observation](StructureDefinition-grove-mobile-observation.html) remains available for a measurement governed by another established profile.

### Shared measurement contract

Every profile in this table has at least two independently supported source adapters in the Grove FHIR contracts.
A meaning implemented by only one source stays in that adapter guide.
Accordingly, HealthKit BMI claims the authoritative R4 BMI profile directly alongside the HealthKit adapter profile, while specimen-specific glucose profiles are defined in Health Connect, whose source record supplies the required specimen evidence.

| Measurement | Grove profile | Standard basis | Normalized result | Effective |
|---|---|---|---|---|
| Heart rate | `grove-mobile-heart-rate` | FHIR R4 Heart Rate, LOINC `8867-4` | UCUM `/min` | `dateTime` or `Period` |
| Body weight | `grove-mobile-body-weight` | FHIR R4 Body Weight, LOINC `29463-7` | UCUM `kg` | `dateTime` |
| Blood pressure | `grove-mobile-blood-pressure` | FHIR R4 Blood Pressure, LOINC `85354-9` | `8480-6` and `8462-4`, UCUM `mm[Hg]` | `dateTime` |
| Body temperature | `grove-mobile-body-temperature` | FHIR R4 Body Temperature, LOINC `8310-5` | UCUM `Cel` | `dateTime` |
| Respiratory rate | `grove-mobile-respiratory-rate` | FHIR R4 Respiratory Rate, LOINC `9279-1` | UCUM `/min` | `dateTime` |
| Oxygen saturation | `grove-mobile-oxygen-saturation` | FHIR R4 Oxygen Saturation, LOINC `2708-6` | UCUM `%` | `dateTime` |
| Body height | `grove-mobile-body-height` | FHIR R4 Body Height, LOINC `8302-2` | UCUM `cm` | `dateTime` |
| Basal body temperature | `grove-mobile-basal-body-temperature` | Grove `basal-body-temperature` | UCUM `Cel` | `dateTime` |
| Step count | `grove-mobile-step-count` | Grove `step-count-total` | UCUM `{steps}` | `Period` |
| Distance | `grove-mobile-distance` | LOINC `103208-5` | UCUM `m` | `Period` |
| Active energy | `grove-mobile-active-energy` | Grove `active-energy-burned` | UCUM `kcal` | `Period` |
| Sleep duration | `grove-mobile-sleep-duration` | LOINC `93832-4` | UCUM `h` | `Period` |
| Sleep stage | `grove-mobile-sleep-stage` | Grove `sleep-stage` and required Grove stage value set | coded stage | `Period` |

The complete machine-readable measurement contract is published in [`catalog/measurement-catalog.json`](https://grovealliance.org/fhir/catalog/measurement-catalog.json).
A standard-first Grove profile declares the standard profile through the R4 `structuredefinition-imposeProfile` extension.
An instance claiming the Grove profile must therefore validate against both profiles; a producer declares only the Grove canonical in `meta.profile`.

An adapter output declares exactly two canonicals: this shared measurement profile and the one adapter profile.
A source-neutral output that carries no adapter source marker declares only the shared measurement profile, even when its producer manifest lists adapter packages used by other resources.
Package presence is a validation capability, not proof of an individual resource's origin.
An adapter source marker without its exact adapter profile is invalid.
An adapter output does not separately declare Grove Mobile Observation or the imposed core profile; those constraints are inherited.
This exact-two rule prevents a producer from presenting ambiguous adapter or measurement semantics.

### Required mapping decisions

| Question | FHIR element | Rule |
|---|---|---|
| Which source and exact output is this? | `identifier` | Exactly one typed `source-record` pair and one typed `source-output` pair; optional source-supplied writer identity is separate |
| What was measured? | `code` | Fixed by the selected profile; every coding is LOINC, MDC, or a Grove code system |
| Who does the result describe? | `subject` | Exactly one Patient reference |
| When did it apply? | `effectiveDateTime` or `effectivePeriod` | Fixed by the selected profile; every value states a time of day with its UTC offset |
| What was the result? | `value[x]`, `component`, or `hasMember` | Required unless `dataAbsentReason` explains absence with a FHIR data-absent-reason code |
| Where on the body? | `bodySite` | SNOMED CT, only when the source states it |
| Which measurement technique? | `method` | Fixed by aggregate and ECG profiles; otherwise SNOMED CT or a Grove code system, when the source states it |
| Which hardware measured it? | `device` | Device, when known and governed |
| How was it captured? | `grove-recording-method` | Only when the source positively establishes the mode |
| Which app mediated it? | `observation-gatewayDevice` | Only when the application actually mediated the measurement |
| Which study applies? | `workflow-researchStudy` | ResearchStudy reference, when applicable |

The [heart-rate example](Observation-GroveMobileHeartRateExample.html) demonstrates a standard-first profile.
The identifier values below are illustrative placeholders, not conformant HMAC values; the linked example contains complete valid values.

```json
{
  "resourceType": "Observation",
  "meta": {
    "profile": [
      "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
    ]
  },
  "identifier": [
    {
      "type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-record"}]},
      "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1",
      "value": "v0:<key-id>:<epoch>:…"
    },
    {
      "type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-output"}]},
      "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1",
      "value": "v0:<key-id>:<epoch>:…"
    }
  ],
  "status": "final",
  "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4"}]},
  "subject": {"reference": "Patient/GroveMobilePatientExample"},
  "effectiveDateTime": "2026-08-19T10:30:00.251-07:00",
  "valueQuantity": {
    "value": 72,
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  }
}
```

Quantity profiles fix the UCUM system and code and, when source semantics define an unambiguous allowed range or integer constraint, publish that constraint in the measurement catalog.
All UCUM-percent results admit the inclusive interval 0 through 100; discrete event totals such as steps, wheelchair pushes, flights, puffs, drinks, falls, and swimming strokes are non-negative integers; HealthKit state-of-mind valence admits the inclusive interval -1 through 1.
Zero is a valid boundary value in each applicable contract.
These are source-representation rules, not invented physiologic plausibility ranges.

### Identity and deduplication

An Observation identifier is a business identifier, not the FHIR server's resource id.
Every Grove output carries separately typed source-record and source-output Identifiers.
Their systems are deployment-owned and immutable for one identity kind, scope, HMAC key id, and key epoch; their values use the `v0:<key-id>:<epoch>:<digest>` form.
A deployment should name each system `<deployment-root>/NamingSystem/grove-<identity-kind>-v0/<key-id>/<epoch>`, including the systems that key a Provenance: `<deployment-root>/NamingSystem/grove-record-version-v0/<key-id>/<epoch>` for a record version and `<deployment-root>/NamingSystem/grove-record-retraction-v0/<key-id>/<epoch>` for a record retraction.
The form carries the identity kind, the protocol version, the key id, and the epoch, so a receiver reads them from the namespace itself and the same key material names the same namespace on every platform.
The normative test vectors use that system form under the root `https://study.example.org/fhir`; a deployment that already governs its own namespaces remains conformant.
The exact component order and unsigned 32-bit length-framed UTF-8 preimage are normative in [`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json). Each catalog-named identity component is a non-empty Unicode-scalar string; missing, empty, additional, reordered, or non-scalar components are errors.
A `part-index` component is the zero-based position of a preserved payload part as a canonical unsigned decimal: `0`, or a nonzero digit followed by digits, with no sign or leading zero.
The three identifier roles answer different questions.

| Role | Names | Derived from | When the platform revises the record in place |
|---|---|---|---|
| `source-record` | the exact source record the record was converted from | adapter id, source type, repository scope, and the native record identifier; a provider adapter uses its provider code and scope | unchanged |
| `source-output` | one exact output of that record, told apart by output role and discriminator | the source-record components plus the output role and discriminator | unchanged, so a receiver supersedes the output in place |
| `writer-record` | the logical record identity assigned by the application that wrote the source record | an opaque identity over the writer application and its record identifier, present when the platform supplies them, with the version in the writer-record-version extension | unchanged; the version orders the revisions |

Every conversion also names its own version of the source record: the conversion Provenance is keyed by a `record-version` Identifier over the source-record pair and the canonical content of the Provenance and its outputs, so a revision, a re-conversion, or any changed byte gives a new record version while these three roles stay unchanged.

The opaque Grove identifiers are mandatory even when a deployment intentionally discloses a source-native identifier for round-trip or traceability.
That optional identifier belongs only on the designated one-to-one primary output (or on the source Recording Document when no structured output exists).
Its `Identifier.system` must be an absolute, governed namespace scoped tightly enough for the exact nonempty value; `Identifier.type` is unnecessary when the namespace is known.
If a type is present, it must not claim a Grove graph role.
Child outputs, specimens, artifacts, and support resources do not repeat one source identifier that does not identify them.

The HMAC is intentionally non-reversible.
It preserves equality, deterministic retry, deduplication, and retraction addressing; it does not let a receiver recover the original native identifier.
When exact upstream round-trip matters, the optional governed Identifier on the catalog-designated primary output carries that exact value without weakening the mandatory Grove graph identities.
An output role, discriminator, or child index need not appear as a separate FHIR element when it has no independent source or clinical meaning; it remains an input to identifier derivation.
Preserve meaningful source order, time, multiplicity, or ordinal in a FHIR element or a source payload format explicitly registered by the applicable adapter contract—never only in the HMAC input.

Intentional source-identifier disclosure is separate from accidental propagation.
A source-native value is never `Resource.id`, a Bundle entry key, a retraction address, an arbitrary Observation component, or untyped metadata.
Do not incidentally copy it into Attachment titles or URLs, transport/object names, or logs.
A deployment may deliberately use the value in a separately governed non-FHIR storage contract.
HMAC reduces identifier disclosure but does not de-identify clinical content, timestamps, references, or attachments; a repository may assign or replace `Resource.id` independently.

### Codes and quantities

Prefer an established domain profile and terminology.
Grove imposes the FHIR R4 core profiles for heart rate, body weight, blood pressure, body temperature, respiratory rate, oxygen saturation, height, and BMI rather than recreating them.

Distance uses active LOINC `103208-5` because its measured patient path-length meaning is compatible with an Observation whose exact event interval is carried in `effectivePeriod`.
Step count remains a Grove code: LOINC `41950-7` fixes a 24-hour number-rate meaning and therefore cannot label arbitrary source intervals.
Active energy also remains a Grove code: LOINC `41981-2` has an energy-rate property and does not faithfully label a total number of kilocalories accumulated over the exact source interval. These Grove definitions are complete and intentionally narrow.
Sleep duration uses LOINC `93832-4`; it summarizes total sleep and does not represent stages.
Every `code` coding is LOINC, the IEEE 11073 MDC nomenclature, or a Grove code system.
[Grove Mobile Measurement Code](ValueSet-grove-mobile-measurement-code.html) lists every code a shared Mobile measurement profile fixes, and each adapter guide's measurement value set lists its own.

Quantities carry the UCUM system and the catalog code.
Producers convert supported source units without inventing precision.
A glucose source selects a specimen-specific profile when it supplies one of the admitted specimen codings.
When the source establishes blood glucose but supplies no exact specimen class, use `grove-mobile-blood-glucose-unspecified-specimen` and omit `Observation.specimen`.
Reject a source that does not establish blood glucose or supplies an unsupported specimen; never relabel it.

### Exchange graph

The normative producer output is a [Grove Mobile Exchange Bundle](StructureDefinition-grove-mobile-exchange-bundle.html), a FHIR `collection` Bundle that carries one or more records of one subject.
A record is one immutable source-record revision, every output derived from it, and exactly one transform Provenance that records source occurrence and assertion times and targets every one of those outputs.
Every output in the Bundle is targeted by exactly one Provenance, and each Provenance names exactly one source record.
Two versions of one source record never share a Bundle, because their outputs share fullUrls.
The records share their supporting nodes, such as Devices, the Patient, and study context, and each shared node appears once.
`Bundle.timestamp` is the mandatory packing time, and `Bundle.identifier` is an optional, untyped transport id with no Grove identifier role and no format; neither names a record or enters any identity, so packing records into Bundles, or repacking them, changes no record.
A receiving system accepts or rejects each record on its own: a contradictory record is rejected alone, and the other records of its Bundle remain admissible.

Lifecycle semantics are unambiguous: every Provenance in an active Bundle contains exactly one coding from the ISO 21089 lifecycle system, and that code is `transform`; it contains no coding from the Grove lifecycle system.
Every Provenance in a retraction Bundle contains exactly one coding from the Grove lifecycle system, and that code is `source-record-retracted`; it contains no ISO lifecycle coding.
The two kinds never share a Bundle.
Additional translations from unrelated coding systems remain open.

Every entry carries one `grove-exchange-entry-key` extension, which holds its entry key, the Identifier from which its fullUrl derives.

- An output selects its highest-priority typed `Resource.identifier` as the protocol orders them: its `source-output` or `source-artifact` Identifier.
- Every shared node except a QuestionnaireResponse, that is, the application, host, and recording Device, Patient, ResearchStudy, ResearchSubject, and PlanDefinition, selects its content-snapshot Identifier, `device-snapshot` or `context-snapshot`, from `Resource.identifier`. It is a v0 HMAC over the subject, the node role, and the digest of the node's complete canonical content minus `id` and minus that Identifier, so the same content gives the same key and fullUrl in every Bundle, and changed content a new one. A canonical `url|version` or an untyped business identifier never selects an entry key, even when immutable.
- A conversion Provenance, which has no identifier in R4, is keyed by its `record-version` Identifier and repeats it in the [Grove Record Version](StructureDefinition-grove-record-version.html) extension, so a consumer that stores the Provenance alone keeps it and can search for it through the `grove-provenance-record-version` SearchParameter.
- A QuestionnaireResponse, whose one identifier holds its submission's business identifier, is keyed by its `context-snapshot` Identifier with node role `questionnaire-response` and repeats it in the `grove-context-snapshot` extension, so a consumer that stores the response alone can still resolve literal references to it.
- A retraction Provenance is keyed by its `record-retraction` Identifier, which it carries on its entry alone.

Each repeated key equals its entry key in system and value.
The `fullUrl` is UUIDv5 under namespace `43df4575-bff7-5a57-9a80-2472cd2b0623`, derived from the complete entry-key system/value pair using the same length-framed UTF-8 encoding.
References between entries use those UUID URNs.
UUIDv5 is deterministic formatting, not concealment.

A record version is a keyed HMAC over the Provenance's source-record pair and the record's content digest.
That digest is taken over the `grove-canonical-json-v0` bytes of the Provenance, minus `id` and minus its own `grove-record-version` extension, followed by each output in `Provenance.target` order, minus `id`.
Canonical JSON sorts members by name, drops insignificant whitespace, and keeps every number exactly as written, so `72` and `72.0` give different record versions while a reordered or re-indented copy gives the same one.
A shared node enters the digest through the content-derived fullUrl that the record references, so a changed Device changes the record version of every record that references it.
Receivers never parse or recompute a record version; [Receiving record versions](implementation.html#receiving-record-versions) describes how they compare and order versions.

Every literal Reference is closed over the Bundle and resolves to an addressable Bundle entry: an output of the referring resource's own record, or a shared node.
A reference from one record to an output of another record is identifier-only.
Contained resources and `#id` references are prohibited in both active and retraction Bundles; allowing them would create a second, owner-local identity and resolution model outside the entry-key contract.
A populated `Reference.type` must equal the target's actual resource type.
The Grove producer validator also enforces the target-type table in `exchange-protocol.json` for Observation and QuestionnaireResponse subjects, device, specimen, member, source-document, study, parent-device, gateway, and research-study paths.
At those paths a logical Reference instead omits `reference`, carries the exact allowed `type` and one complete absolute-system Identifier, and cannot be mixed with a literal.
This permits a deployment-scoped Patient pseudonym without fabricating or copying a Patient Bundle node.
Its system/value pair is preserved exactly, and its Identifier neither claims a Grove identifier role nor uses a protocol code system as the pseudonym namespace.
The Grove producer validator checks only that the namespace is an absolute URI and does not use a reserved Grove protocol system; ownership and deployment scope remain deployment obligations.
These logical-reference shape and pseudonym-namespace rules govern Mobile exchange Bundles.
The standalone Grove QuestionnaireResponse profile independently constrains its subject target to Patient but does not impose this exchange graph's identifier-only policy outside such a Bundle.
An active Bundle may contain only the following resource types.
Outputs are Observation, DocumentReference, Specimen, VisionPrescription, MedicationAdministration, or MedicationStatement; supporting nodes are Patient, Device, ResearchStudy, ResearchSubject, PlanDefinition, or a Grove-profiled QuestionnaireResponse; and the only lifecycle resource is Provenance.
Every active output and each Device, QuestionnaireResponse, and Provenance must declare exactly the profiles required by `profile-claims.json`.
DocumentReference cannot enter as an unprofiled generic envelope.
Every supporting entry lies in at least one record unit, the record's Provenance, its targets, and every entry their literal references reach in the forward direction, so the Bundle cannot carry unrelated context; a ResearchSubject joins every record whose unit reaches the ResearchStudy it references.
`DeviceMetric` is not admitted under the Grove FHIR contracts; admitting it requires a governed profile, identity and reference rules, and validating examples.

An exact retry repeats a record's record-version Identifier and the lossless content of every resource of the record, in any Bundle and under any `Bundle.identifier` or `Bundle.timestamp`.
Any change, including a re-conversion's new `Provenance.recorded` or a changed decimal lexeme, is a new version of the source record with a new record-version Identifier.
Bundle entry order does not request repository operations; `entry.request` and `entry.response` are prohibited. How a receiving system creates or updates resources, and whether it processes the Bundle atomically, are separate deployment policies.

### Retraction Bundles

A source removal is represented by the dedicated Grove Mobile Retraction Bundle, which carries one or more source-record-retracted Provenances and no conversion Provenance.
Each Provenance asserts that the source no longer exposes the one source record its source entity names, and it is keyed by that source record's `record-retraction` Identifier, so the Provenances of one Bundle carry distinct keys.
Its targets are typed logical `Reference.identifier` targets using only the target roles the retraction profile allows; the Bundle contains no copied clinical resources and is not a FHIR DELETE transaction.
Its assembler is a literal reference to the shared application Device, with its host, in the same Bundle.
Retraction does not assert that the prior clinical statement was erroneous.

A retraction addresses the whole source record its source entity names.
A receiving system that accepts it suppresses every output of every version of that record, whether the version is accepted before or after the retraction and whatever its writer version or `recorded` instant; every version stays in history, and the record is never un-retracted.
A re-reported retraction repeats the record-retraction key and fullUrl and is a duplicate: the first accepted retraction wins, which loses nothing because every retraction addresses the whole record.
Devices are never retracted.

The targets are informative: they record what the producer emitted, or name the source record as a whole, and they neither address nor bind an output.
Each typed target role fixes both its resource type and Identifier role: primary outputs are supported clinical result resources, child outputs are Observations, source artifacts are DocumentReferences, and specimens are Specimens.

Instead of typed targets, the Provenance may name the source record as a whole through one `source-record` target, which is then its only target.
That target is an untyped logical Reference with role `source-record` whose Identifier repeats the exact `source-record` Identifier of the Provenance source entity; the role states no resource type.
The Reference identifies the source business record itself, never a graph node: a platform record such as a HealthKit sample, which has no FHIR resource, or the QuestionnaireResponse a questionnaire extraction converted, which is why the profile admits a QuestionnaireResponse target only in this form.
It names no output, so a producer needs no record of what it emitted, and it remains valid when the receiving system holds no version of the record.
Typed targets and the source-record target are alternatives with the same effect: either way, the receiving system finds the record's versions through the source entity of every conversion Provenance it has accepted or later accepts.

A target may additionally carry one [Grove Retraction Native Record Identifier](StructureDefinition-grove-retraction-target-native-identifier.html), the platform-native record identifier of the record being retracted, so a consumer can delete the exact native records rather than only the projections.
`Identifier.system` is the adapter's own absolute native key space, scoped to the governed repository, account, or store exactly as it is for the optional governed source identifier on the addition path, and the same explicit deployment disclosure policy governs both; omitting it remains conformant.
It addresses nothing: the retraction address is the Provenance's source-record entity, the targets are informative, and the native Identifier carries no Grove identifier role.
Both active and retraction Provenance carry exactly one logical `source-record` Identifier entity with role `source`; literal source references and additional source entities are rejected.

This guide sets no limits on Bundle size, resource count, paging, retry behavior, or storage.
Those are transport and deployment policy outside this guide.

### Time, capture mode, and clinical method

Use the effective datatype fixed by the selected profile.
For every Mobile scalar or aggregate `effectiveDateTime` and `effectivePeriod` endpoint, round the exact instant to the nearest millisecond with ties to even before FHIR serialization.
Every `effectiveDateTime` and `effectivePeriod` bound states a time of day and an offset: the numeric UTC offset the source supplies, otherwise UTC, never an invented one; a calendar date alone is invalid.
This rule does not apply to Sensor or ECG `SampledData`, whose exact Decimal timing contract is defined by the Sensor guide.
When the source also supplies an IANA time-zone name, attach the standard `timezone` extension; the name must agree with the offset at that instant.

`Observation.issued` states when this version of the record became available, and it comes from the source platform's own timestamp for that version.
A producer whose platform keeps no such timestamp omits the element rather than substituting a clock reading: an unchanged source record must convert to an identical Observation, or a re-read no longer deduplicates against what was already sent.
Each adapter guide states which it does.

The conversion time belongs on the conversion Provenance and must not be substituted for `Observation.issued`.

Ordering *revisions of the same measurement* is a separate question, and `issued` does not answer it — a replaced record can carry an earlier timestamp than the one it supersedes.
Where a platform gives the writer a logical identity and a version, the adapter carries both, and a receiver supersedes on the version; otherwise the later `Provenance.recorded` orders the versions of one source record, as [Receiving record versions](implementation.html#receiving-record-versions) describes.

The [Grove Recording Method extension](StructureDefinition-grove-recording-method.html) describes positively established `manual-entry`, `actively-recorded`, or `automatically-recorded` capture.
Omit it when unknown. `Observation.method` remains available for the clinical measurement technique and is not a capture-mode field.
`Observation.method` is coded in SNOMED CT or a Grove code system.

### Must Support obligations

For elements marked **Must Support**, a producer includes the element whenever the source supplies the fact and the mapping is authorized.
A consumer accepts the element when present and preserves it or exposes its meaning.
This does not turn an optional cardinality into a required one.
