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
in version 0.3.0. A meaning implemented by only one source stays in that adapter guide.
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
and the one adapter profile. It does not separately declare Grove Mobile Observation
or the imposed core profile; those constraints are inherited. This exact-two rule
prevents a producer from presenting ambiguous adapter or measurement semantics.

### Fields every mapping addresses

| Question | FHIR element | Rule |
|---|---|---|
| Which exchanged record is this? | `identifier` | At least one stable complete `(system, value)` pair |
| What was measured? | `code` | Fixed by the selected profile |
| Who does the result describe? | `subject` | Exactly one Patient reference |
| When did it apply? | `effectiveDateTime` or `effectivePeriod` | Fixed by the selected profile |
| What was the result? | `value[x]`, `component`, or `hasMember` | Required unless `dataAbsentReason` explains absence |
| Which hardware measured it? | `device` | Device or DeviceMetric, when known |
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
  "identifier": [{
    "system": "https://study.example.org/fhir/identifiers/mobile-observation",
    "value": "heart-rate-20260819-001"
  }],
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

### Identity and deduplication

An Observation identifier is a business identifier for the exchanged record, not the
FHIR server's resource id. Producers assign a namespace they control and a stable value
within that namespace. Consumers compare the complete `(system, value)` pair.

An adapter may require an additional identifier for the original platform object. It
defines that identifier system in its own package. Never put a HealthKit UUID, Health
Connect record ID, or provider record ID into `Resource.id`; a repository may assign or
replace that logical id.

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
a FHIR `collection` Bundle. Every entry carries one complete
`grove-exchange-entry-identifier`; its `fullUrl` is the UUID version 5 value defined by
[`catalog/exchange-identity.json`](https://grovealliance.org/fhir/catalog/exchange-identity.json). References between Bundle entries use those UUID URNs.

The RFC 8785 JSON Canonicalization Scheme serialization of exactly `[system,value]` is
the UUID name under namespace `a9a39cf1-c944-5d15-a3c2-c395969ea101`. This works for
resources without a native
`identifier`, such as Provenance, without turning `Resource.id` into source identity.
The entry identifier supplements rather than replaces a resource's native identifier,
canonical URL, or Provenance source identity.

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
