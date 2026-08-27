<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A mobile measurement is a FHIR R4 `Observation`. For the shared measurements below,
the Grove profile imposes the authoritative FHIR R4 Vital Signs profile when one
exists and adds source-neutral exchange identity and provenance context. The generic
[Grove Mobile Observation](StructureDefinition-grove-mobile-observation.html) remains
available for a measurement governed by another established profile.

### Shared measurement contract

Every profile in this table has at least two independently supported source adapters
in version 0.6.0. A meaning implemented by only one source stays in that adapter guide.
Accordingly, HealthKit BMI claims the authoritative R4 BMI profile directly alongside
the HealthKit adapter profile, while specimen-specific glucose profiles are defined in
Health Connect, whose source record supplies the required specimen evidence.

| Measurement | Grove profile | Standard basis | Normalized result | Effective |
|---|---|---|---|---|
| Heart rate | `grove-mobile-heart-rate` | FHIR R4 Heart Rate, LOINC `8867-4` | UCUM `/min` | `dateTime` |
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

The machine-readable source of this table is
[`catalog/measurement-catalog.json`](https://grovealliance.org/fhir/catalog/measurement-catalog.json) in the source repository. A standard-first Grove
profile declares the standard profile through the R4 `structuredefinition-imposeProfile`
extension. An instance claiming the Grove profile therefore has to validate against
both profiles; a producer declares only the Grove canonical in `meta.profile`.

An adapter output declares exactly two canonicals: this shared measurement profile
and the one adapter profile. A source-neutral output that carries no adapter source
marker declares only the shared measurement profile, even when its producer manifest
lists adapter packages used by other resources. Package presence is a validation
capability, not proof of an individual resource's origin. An adapter source marker
without its exact adapter profile is invalid. An adapter output does not separately declare Grove Mobile Observation
or the imposed core profile; those constraints are inherited. This exact-two rule
prevents a producer from presenting ambiguous adapter or measurement semantics.

### Fields every mapping addresses

| Question | FHIR element | Rule |
|---|---|---|
| Which source and exact output is this? | `identifier` | Exactly one typed `source-record` pair and one typed `source-output` pair; optional source-supplied writer identity is separate |
| What was measured? | `code` | Fixed by the selected profile |
| Who does the result describe? | `subject` | Exactly one Patient reference |
| When did it apply? | `effectiveDateTime` or `effectivePeriod` | Fixed by the selected profile |
| What was the result? | `value[x]`, `component`, or `hasMember` | Required unless `dataAbsentReason` explains absence |
| Which hardware measured it? | `device` | Device, when known and governed |
| How was it captured? | `grove-recording-method` | Only when the source positively establishes the mode |
| Which app mediated it? | `observation-gatewayDevice` | Only when the application actually mediated the measurement |
| Which study applies? | `workflow-researchStudy` | ResearchStudy reference, when applicable |

The [heart-rate example](Observation-GroveMobileHeartRateExample.html) demonstrates a
standard-first profile:

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
      "system": "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1",
      "value": "v2:test-key:1:D2f2lnPlZ6XI5L3uOVJrhpLE55ltpgC6sNXRv8_65D4"
    },
    {
      "type": {"coding": [{"system": "https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role", "code": "source-output"}]},
      "system": "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1",
      "value": "v2:test-key:1:LmIAsdN9oEgV7BHugInyYfqBh5ZfTKlAbeSyLqMvAuA"
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

Quantity profiles fix the UCUM system/code and, where the source semantics make a
representational domain unambiguous, publish that domain from the measurement catalog. All
UCUM-percent results admit the inclusive interval 0 through 100; discrete event totals such as
steps, wheelchair pushes, flights, puffs, drinks, falls, and swimming strokes are non-negative
integers; HealthKit state-of-mind valence admits the inclusive interval -1 through 1. Zero is a
valid boundary value in each applicable contract. These are source-representation rules, not
invented physiologic plausibility ranges.

### Identity and deduplication

An Observation identifier is a business identifier, not the FHIR server's resource id.
Every Grove output carries separately typed source-record and source-output Identifiers. Their
systems are deployment-owned and immutable for one identity kind, scope, HMAC key id, and key
epoch; their values use the `v2:<key-id>:<epoch>:<digest>` form. The exact component order and
unsigned 32-bit length-framed UTF-8 preimage are normative in
[`catalog/exchange-protocol.json`](https://grovealliance.org/fhir/catalog/exchange-protocol.json).

Native HealthKit UUIDs, Health Connect record ids, provider keys, subject identifiers, and other
identity inputs are therefore not disclosed directly. HMAC reduces that disclosure but does not
de-identify clinical content, timestamps, references, or attachments. Never copy a business
identifier into `Resource.id`; a repository may assign or replace that logical id.

### Codes and quantities

Prefer an established domain profile and terminology. Grove imposes the FHIR R4 core
profiles for heart rate, body weight, blood pressure, body temperature, respiratory
rate, oxygen saturation, height, and BMI rather than recreating them.

Distance uses active LOINC `103208-5` because its measured patient path-length meaning
is compatible with an Observation whose exact event interval is carried in
`effectivePeriod`. Step count remains a Grove code: LOINC `41950-7` fixes a 24-hour
number-rate meaning and therefore cannot label arbitrary source intervals. Active
energy also remains a Grove code: LOINC `41981-2` has an energy-rate property and does
not faithfully label a total number of kilocalories accumulated over the exact source
interval. These Grove definitions are complete and intentionally narrow. Sleep
duration uses LOINC `93832-4`; it summarizes total sleep and does not represent stages.

Quantities carry the UCUM system and the catalog code. Producers convert supported
source units without inventing precision. A glucose source selects the profile that
fixes both analyte code and specimen: whole blood, capillary blood, serum/plasma, or
interstitial fluid. Unknown-specimen glucose and any unlisted specimen fail closed;
they are never relabeled as blood.

### Exchange graph

The normative producer output is a
[Grove Mobile Exchange Bundle](StructureDefinition-grove-mobile-exchange-bundle.html),
a FHIR `collection` Bundle for exactly one immutable source-record revision. The Bundle has one
typed event Identifier (`e2:<producer-instance-uuid>:<positive-sequence>`), a mandatory assembly
timestamp, and exactly one transform Provenance that records source occurrence and assertion
times and targets every output.

Lifecycle semantics are unambiguous: an active event contains exactly one coding from the ISO
21089 lifecycle system, and that code is `transform`; it contains no coding from the Grove
lifecycle system. A retraction event contains exactly one coding from the Grove lifecycle system,
and that code is `source-record-retracted`; it contains no ISO lifecycle coding. Additional
translations from unrelated coding systems remain open.

Every entry carries one `grove-exchange-entry-node-key` extension. A resource with business
identity selects the highest-priority typed Identifier defined by the protocol; a resource
without one uses an event-scoped `n2:` graph-node key. Its `fullUrl` is UUIDv5 under namespace
`43df4575-bff7-5a57-9a80-2472cd2b0623`, derived from the complete selected system/value pair using
the same length-framed UTF-8 encoding. References between entries use those UUID URNs. UUIDv5 is
deterministic formatting, not concealment.

Every literal Reference is closed over that graph and resolves to an addressable Bundle entry.
Contained resources and `#id` references are prohibited in both active and retraction events;
allowing them would create a second, owner-local identity and resolution model outside the
event-node contract. A populated `Reference.type` must equal the target's actual resource type.
The producer gate
also enforces the exact target-type table in `exchange-protocol.json` for subject, device,
specimen, member, source-document, study, parent-device, gateway, and research-study paths.
At those paths a logical Reference instead omits `reference`, carries the exact allowed `type`
and one complete absolute-system Identifier, and cannot be mixed with a literal. This permits a
deployment-scoped Patient pseudonym without fabricating or copying a Patient Bundle node.
The active entry set is closed. Outputs are Observation, DocumentReference, Specimen,
VisionPrescription, MedicationAdministration, or MedicationStatement; supporting nodes are
Patient, Device, ResearchStudy, ResearchSubject, PlanDefinition, or a Grove-profiled
QuestionnaireResponse; and the sole lifecycle node is Provenance. Every active output and each
Device, QuestionnaireResponse, and Provenance directly claims its exact admitted profile mode.
DocumentReference cannot enter as an unprofiled generic envelope. Supporting entries must be
connected to an output or the lifecycle assertion, so the Bundle cannot carry unrelated context.
DeviceMetric is not admitted in 0.6.0; adding it later requires a governed profile, identity,
reference, fixture, and SDK contract.

An exact retry reuses the event Identifier, occurrence/recording/assembly times, entry keys, and
payload. Changed content or a new source revision receives a new event sequence. Bundle entry
order does not request repository operations; `entry.request` and `entry.response` are prohibited,
and receiver upsert/atomicity policy remains separate.

### Retraction events

A source removal is represented by the dedicated Grove Mobile Retraction Bundle and exactly one
source-record-retracted Provenance. It contains typed logical `Reference.identifier` targets for
the exact previously emitted graph nodes and their closed target roles; it contains no copied
clinical resources and is not a FHIR DELETE transaction. A receiver resolves every complete
Identifier pair unambiguously and applies its separately governed idempotent, atomic lifecycle
policy. Retraction does not assert that the prior clinical statement was erroneous.

Each target role fixes both its resource type and Identifier role: primary outputs are supported
clinical result resources, child outputs are Observations, source artifacts are
DocumentReferences, specimens are Specimens, and device snapshots are Devices. Both active and
retraction Provenance carry exactly one logical `source-record` Identifier entity with role
`source`; literal source references and additional source entities are rejected.

The Bundle has no receiver byte, resource-count, paging, retry, or storage limits.
Those are transport and deployment policy outside this guide.

### Time, capture mode, and clinical method

Use the effective datatype fixed by the selected profile. For every Mobile scalar or
aggregate `effectiveDateTime` and `effectivePeriod` endpoint, round the exact instant to
the nearest millisecond with ties to even before FHIR serialization. Preserve the
caller/source numeric UTC offset when it is available; never invent one. This rule does
not apply to Sensor or ECG `SampledData`, whose exact Decimal timing contract is defined
by the Sensor guide. When the source also supplies an IANA time-zone name, attach the
standard `timezone` extension; the name must agree with the offset at that instant.

`Observation.issued` states when this version of the record became available, and it comes from the
source platform's own timestamp for that version. A producer whose platform keeps no such timestamp
omits the element rather than substituting a clock reading: an unchanged source record has to
convert to an identical Observation, or a re-read stops deduplicating against what was already
sent. Each adapter guide states which it does.

The conversion event has its own home on the conversion `Provenance`, so omitting `issued` loses
nothing.

Ordering *revisions of the same measurement* is a separate question, and `issued` does not answer
it — a replaced record can carry an earlier timestamp than the one it supersedes. Where a platform
gives the writer a logical identity and a version, the adapter carries both, and a receiver
supersedes on the version.

The [Grove Recording Method extension](StructureDefinition-grove-recording-method.html)
describes positively established `manual-entry`, `actively-recorded`, or
`automatically-recorded` capture. Omit it when unknown. `Observation.method` remains
available for the clinical measurement technique and is not a capture-mode field.

### Must Support

For elements marked **Must Support**, a producer includes the element whenever the
source supplies the fact and the mapping is authorized. A consumer accepts the element
when present and preserves it or exposes its meaning. This does not turn an optional
cardinality into a required one.
