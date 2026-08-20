<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A mobile measurement is a FHIR R4 `Observation` that conforms to the
[Grove Mobile Observation](StructureDefinition-grove-mobile-observation.html) envelope
and, when available, a separate profile for its clinical meaning. FHIR R4 explicitly
supports declaring multiple profiles when they describe independent aspects of the
same resource.

| Measurement | Profile | Clinical definition |
|---|---|---|
| Heart rate | Mobile envelope + [FHIR R4 Heart Rate](https://hl7.org/fhir/R4/heartrate.html) | LOINC `8867-4`, UCUM `/min` |
| Body weight | Mobile envelope + [FHIR R4 Body Weight](https://hl7.org/fhir/R4/bodyweight.html) | LOINC `29463-7`, a permitted UCUM body-weight unit |
| Step count | Mobile envelope + [Grove Mobile Step Count](StructureDefinition-grove-mobile-step-count.html) | Grove `step-count-total`, UCUM `{steps}`, attributed to an exact Period |
| Another measurement | Mobile envelope + an appropriate clinical or research profile | The implementation supplies an established code when no suitable profile exists |

The Mobile envelope covers exchange identity, time, device roles, study context, and
conversion. It does not copy the constraints from standard clinical profiles. A
heart-rate record declares both profile canonicals in `meta.profile` and must validate
against both contracts.

### Fields every mapping must address

| Question | FHIR element | Rule |
|---|---|---|
| Which exchanged record is this? | `identifier` | At least one stable `(system, value)` pair |
| What was measured? | `code` | Use the code fixed by the domain profile, or an established code with the generic profile |
| Who does the result describe? | `subject` | Exactly one Patient reference |
| When did it apply? | `effectiveDateTime` or `effectivePeriod` | Required; a general interval has a start and may remain open |
| What was the result? | `value[x]`, `component`, or `hasMember` | Required unless `dataAbsentReason` explains its absence |
| Which hardware or metric measured it? | `device` | Device or DeviceMetric, when known |
| How was this record captured? | `grove-recording-method` | Add only when the source positively establishes the capture mode |
| Which app mediated the measurement? | `observation-gatewayDevice` | Application Device, only when it actually routed or mediated the measurement |
| Which study is it relevant to? | `workflow-researchStudy` | ResearchStudy reference, when applicable |

The [heart-rate example](Observation-GroveMobileHeartRateExample.html) shows these
fields together. The [step-count example](Observation-GroveMobileStepCountExample.html)
shows the required interval and source count. The heart-rate example's central clinical
fields are:

```json
{
  "resourceType": "Observation",
  "meta": {
    "profile": [
      "https://schmiedmayerlab.github.io/grove-fhir/fhir/mobile/StructureDefinition/grove-mobile-observation",
      "http://hl7.org/fhir/StructureDefinition/heartrate"
    ]
  },
  "identifier": [{
    "system": "https://study.example.org/fhir/identifiers/mobile-observation",
    "value": "heart-rate-20260819-001"
  }],
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "8867-4",
      "display": "Heart rate"
    }]
  },
  "subject": { "reference": "Patient/GroveMobilePatientExample" },
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
within that namespace. Consumers compare the complete `(system, value)` pair. A bare
UUID or value is insufficient because another producer may issue the same value in a
different namespace.

An adapter may require an additional identifier for the original platform object. It
defines that identifier system in its own package. Do not put a platform object UUID
into `Observation.id`; a server may replace that logical id when it creates or copies
the resource.

### Codes and quantities

`Observation.code` states what the result means. Prefer an established domain profile
and terminology instead of recreating its constraints in Grove. Heart rate and body
weight therefore conform directly to the FHIR R4 Vital Signs profiles alongside the
Mobile envelope.

Step count uses the Grove `step-count-total` code and preserves the source interval
total in UCUM `{steps}`. The required Period defines the interval to which the count is
attributed, and its end must be later than its start. The value is the total count within
that exact Period; it is not a point sample or a normalized rate. Consumers compare
counts only with the associated Period and must not assume that equal counts represent
equal activity rates.

Quantities carry a machine-readable UCUM system and code. Preserve enough precision
to reproduce the source value.

### Time, capture mode, and clinical method

Use `effectiveDateTime` for a point measurement and `effectivePeriod` for a result over
an interval. Preserve fractional seconds and the numeric UTC offset. When the source
also supplies an IANA time-zone name, attach the standard `timezone` extension to the
date-time value; the named zone must agree with the offset at that instant.

The [Grove Recording Method extension](StructureDefinition-grove-recording-method.html)
describes a positively established capture mode:

- `manual-entry`: a person entered the result;
- `actively-recorded`: a person deliberately initiated or participated in this
  measurement; or
- `automatically-recorded`: the source recorded this measurement without individual
  initiation.

Omit the extension when the mode is unknown. A converter must not infer automatic
recording merely because a source lacks a user-entered flag. `Observation.method`
remains available for the clinical measurement technique, such as a laboratory or
device procedure; Grove does not bind it to capture mode.

### Must Support

For elements marked **Must Support**, a producer includes the element whenever the
source supplies the fact and the mapping is authorized. A consumer accepts the element
when present and preserves it or exposes its meaning to downstream processing. These
obligations do not turn an optional cardinality into a required one.

A producer always supplies the required identifier, status, code, Patient, effective
time, and either a result or `dataAbsentReason`. It supplies category, capture mode,
devices, and other Must Support context when those facts are known.
