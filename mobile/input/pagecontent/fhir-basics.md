<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page introduces the parts of FHIR used throughout the Grove FHIR Implementation Guides.
It presents resources, profiles, terminology, identifiers, references, and exchange Bundles in the order required to interpret the remaining pages.
It is explanatory; the linked profiles and machine-readable catalogs define the normative requirements.
Readers already familiar with FHIR can continue directly to [Observations](observations.html).

### FHIR and Grove

FHIR is a standard for exchanging healthcare information as structured data objects called **resources**.
FHIR supports several serializations; these guides primarily use JSON, in which each resource has a `resourceType` and a standardized set of elements.
For example, a quantitative Observation represents its result in `valueQuantity` rather than an application-defined `value` or `measurement` field.
This common structure allows a receiver with no knowledge of the source application to interpret a standardized heart-rate result.

FHIR is deliberately flexible.
The base Observation permits many optional elements and alternative representations.
Two applications can both emit valid FHIR and still produce records that cannot be compared.

A **profile** constrains the base standard for a defined use case.
It is a named set of additional rules that identifies required elements, admitted codes, and their meaning in that context.
Grove is a family of profiles.
The guides use FHIR R4 with additional rules that align records from different applications, devices, and services.

### Five resources in the core measurement exchange

The core mobile measurement exchange centers on five resource types.
Specialized Grove guides add resources for their own use cases, including questionnaires, research participation, specimens, and document attachments.

| Resource | Answers | In Grove |
|---|---|---|
| `Observation` | What was measured, of whom, when, and with what value | One measurement, one Observation |
| `Patient` | Who the measurement is about | The study participant; referenced by every Observation and included as a Bundle entry when the exchange supplies the Patient resource |
| `Device` | What produced the record | Split in two: the recording device and the application |
| `Provenance` | Where this record came from and who assembled it | The audit trail of the conversion itself |
| `Bundle` | A set of resources traveling together | One immutable exchange event graph |

### Observation example

The following heart-rate Observation is limited to the elements needed for this introduction:

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{ "system": "http://loinc.org", "code": "8867-4", "display": "Heart rate" }]
  },
  "subject": { "reference": "Patient/participant-01" },
  "effectiveDateTime": "2026-08-19T10:30:00-07:00",
  "valueQuantity": {
    "value": 72,
    "unit": "beats/minute",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  }
}
```

Four concepts in this example are fundamental to interoperable FHIR exchange.

**A code is a coordinate, not a word.** `code` says what was measured, and it says it as a `system` plus a `code`.
The `display` is presentation text; receivers match on the `(system, code)` pair. `8867-4` in the LOINC system represents heart rate consistently across systems that understand LOINC.
Grove fixes the code for each measurement so producers cannot assign conflicting codes to the same measurement concept.

**A quantity also carries a coded unit.** `unit` is presentation text; the `code` in the UCUM system supports machine interpretation. `/min` is the UCUM representation for "per minute".
Grove quantity profiles require the applicable UCUM code so results remain comparable.

**`effective` and `issued` represent different times.** `effective` identifies when the measurement applied. `issued` identifies when this version of the record became available, using the source platform's own timestamp.
A platform that does not retain such a timestamp omits `issued` rather than substituting the conversion time. This ensures that converting unchanged source data twice does not create an apparent revision.
A receiver uses `effective` for the clinical timeline.
Ordering *revisions of the same measurement* is a separate concern addressed by writer-assigned versions in the adapter guides.

**`subject` is a reference to another resource.** The next section distinguishes references from identities.

### References, identifiers, and resource IDs

A resource `id` is its address within a particular repository. `Patient/abc123` identifies the Patient resource stored as `abc123` in that repository.
The ID can change when the resource moves to another repository.
It is not the participant's business identity.

A resource can also carry an `identifier`: a **business identifier** that remains meaningful outside a single repository.
The Grove exchange contracts require each business identifier to be a complete pair: a `system` naming the namespace and a `value` unique within it.

```json
"identifier": [{
  "system": "https://mystudy.example.org/fhir/identifiers/participant",
  "value": "participant-01"
}]
```

The `system` is an absolute URL governed by the deployment.
It serves as a namespace and does not need to resolve as a network address.
The namespace prevents a local value such as `participant-01` from colliding with the same value assigned by another deployment.

A **reference** points from one resource to another, usually as `"reference": "Patient/abc123"`.

These distinctions have three consequences for a producer:

- **`Observation.subject` references a Patient.** A stable participant identity must therefore exist before a producer emits an Observation. A study enrollment identifier is appropriate; an email address or phone number is not stable and directly identifies the person.
- **Every business identifier requires a governed `system`.** The deployment selects an absolute URL under a namespace it controls and keeps that namespace stable.
- **Repository-assigned resource IDs are separate from business identity.** A producer that does not control the repository-assigned `id` omits it and uses `identifier` for the record's business identity.

### Device roles

FHIR uses one `Device` resource type, while a mobile measurement can involve two distinct device roles.

The **recording device** is the hardware that acquired the measurement, such as a wearable sensor or paired blood-pressure cuff.
The **application device** is software that mediated the measurement and/or converted the source record; gateway and assembler are asserted as separate roles.

Keeping these roles separate preserves two different claims.
The recording-device statement supports interpretation of measurement provenance and quality, while the application-device statement documents the software transformation chain.
Collapsing both roles into one Device makes neither claim precise.

### Conversion provenance

`Provenance` is FHIR's audit resource. It records that a target resource was produced by a defined activity, at a defined time, by a defined actor.

In Grove, Provenance records the origin and transformation path of a result.
A step count obtained from a platform store and converted by an application has different provenance from a manually entered value.
The Provenance carries the source-record identifier so the result remains traceable to the source record consumed by the conversion.

Provenance is a separate resource because one conversion can cover multiple outputs and because audit information has a lifecycle distinct from clinical data.

### Bundle exchange

A `Bundle` is a resource container.
Grove uses `type: collection`, which groups resources without assigning transactional meaning.

Inside a Bundle, resources refer to each other by `fullUrl`.
Grove derives each `fullUrl` deterministically from the entry identity selected by the [exchange protocol](https://grovealliance.org/fhir/catalog/exchange-protocol.json).
An entry without a business identifier instead uses the protocol's event-scoped `n0:` graph key.
An exact retry therefore preserves graph identity and can be recognized as a duplicate.

### Reading profile pages

Each profile page contains two complementary tables:

- The **Differential Table** shows only what this guide adds to the base resource.
  It is the most direct view of the profile's own constraints.
- The **Snapshot Table** shows every rule, including the hundreds inherited from FHIR R4.
  It is a complete reference that includes all inherited constraints.

For Grove profiles, a conformant producer populates fields marked **Must Support (MS)** whenever the data is available, and a conformant consumer must be able to read them.

Every profile has at least one example with JSON, XML, and Turtle representations.
The JSON representation is generally the most direct starting point for application development.

A useful reading sequence is the [heart-rate example JSON](Observation-GroveMobileHeartRateExample.json), the constraining [Mobile envelope](StructureDefinition-grove-mobile-observation.html), and then [Observations](observations.html) for the field-by-field rules.

### Next steps

| Goal | Read |
|---|---|
| Encode a measurement | [Observations](observations.html) |
| Understand the device split and the audit trail | [Devices and provenance](devices.html) |
| Attach data to a study | [Study context](study.html) |
| Install the package and validate JSON | [Implement and validate](implementation.html) |
| See how the ten guide packages fit together | [The Grove FHIR guides](guides.html) |
