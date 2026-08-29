<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This page is for readers who are new to FHIR.
It explains only the parts of the standard Grove actually uses, in the order you meet them, and every term it introduces appears in the guides that follow.
If you already write FHIR, skip to [Observations](observations.html).

### What FHIR gives you, and what Grove adds

FHIR is a standard for exchanging health data as JSON documents called **resources**.
Each resource has a `resourceType` and a set of fields the standard fixes: an `Observation` always keeps its value in `valueQuantity`, never in `value` or `measurement`.
That is the whole promise — a receiver that has never heard of your app can still read a heart rate you send it.

FHIR is deliberately loose, though.
It says an Observation *may* have a device, a time, an identifier; it rarely says it *must*.
Two applications can both emit valid FHIR and still produce records that cannot be compared.

A **profile** is how the standard is tightened.
It is a named set of extra rules over a base resource, saying which fields are required, which codes are allowed, and what they mean here.
Grove is a family of profiles.
Everything in these guides is ordinary FHIR R4 plus rules that make records from different phones, watches, and services line up.

### The five resources Grove uses

| Resource | Answers | In Grove |
|---|---|---|
| `Observation` | What was measured, of whom, when, and with what value | One measurement, one Observation |
| `Patient` | Who the measurement is about | The study participant, referenced but rarely sent by a producer |
| `Device` | What produced the record | Split in two: the recording device and the application |
| `Provenance` | Where this record came from and who assembled it | The audit trail of the conversion itself |
| `Bundle` | A set of resources travelling together | The unit an application uploads |

### Reading an Observation

A heart rate, trimmed to the fields that carry meaning:

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

Four ideas in that document are worth pausing on, because they are where newcomers most often go wrong.

**A code is a coordinate, not a word.** `code` says what was measured, and it says it as a `system` plus a `code`.
The `display` is a human courtesy; receivers match on the pair. `8867-4` in the LOINC system means heart rate to every system that reads LOINC.
Grove fixes the code for each measurement, so two producers cannot describe the same thing differently.

**A quantity carries its unit as a code too.** `unit` is for people; `code` in the UCUM system is what a receiver computes with. `/min` is UCUM for "per minute".
A number without a UCUM code is not comparable data.

**`effective` and `issued` are different times, and both matter.** `effective` is when the measurement happened — the moment the heart beat. `issued` is when this version of the record became available, taken from the source platform's own timestamp for it.
A platform that keeps no such timestamp leaves `issued` out rather than substituting a clock reading, so converting the same unchanged data twice produces the same document instead of looking like something new.
A receiver uses `effective` for the clinical timeline.
Ordering *revisions of the same measurement* is a third question again, and the adapter guides answer it with a writer-assigned version.

**`subject` is a reference, not a person.** The next section explains what that means.

### References, identifiers, and ids

This is the part of FHIR that most repays five minutes of attention.

A resource has an `id` — its address on one particular server. `Patient/abc123` means "the patient at `abc123` on this server".
Move the record elsewhere and the id changes.
It is not the participant's identity; it is a filing location.

A resource also has `identifier` — a **business identifier**, meaningful outside any one server.
It is always a pair: a `system` naming the namespace, and a `value` unique within it.

```json
"identifier": [{
  "system": "https://mystudy.example.org/fhir/identifiers/participant",
  "value": "participant-01"
}]
```

The `system` is a URL you own.
It does not have to resolve to anything — it is a name, not an address.
Its whole job is to stop your `participant-01` from colliding with someone else's.

A **reference** points from one resource to another, usually as `"reference": "Patient/abc123"`.

Three practical consequences for a producer:

- **`subject` on an Observation is a reference to a Patient**, so you need a stable participant identity before you can emit anything.
  Use whatever your study already uses as its enrolment identifier.
  Do not use an email address or a phone number: they change over a study's life, and they identify the person directly, which is what a research exchange is trying to avoid.
- **You need an identifier `system` of your own.** Pick one URL under a domain you control and keep it forever.
- **Server-assigned `id`s are not yours to invent.** A producer that has not been given one leaves `id` out and identifies its records by `identifier` instead.

### Why two devices

FHIR has one `Device` resource, and a phone measurement has two very different devices behind it.

The **recording device** is the thing that took the measurement: the watch on the wrist, the paired blood-pressure cuff.
The **application device** is the software that read the measurement out and turned it into FHIR: your application.

Keeping them apart matters.
"This heart rate came from an Apple Watch Series 9" is a statement about data quality that a researcher will filter on.
"This record was assembled by MyStudy 2.1" is a statement about the software chain, which is an audit question.
Collapsing both into one Device makes each of them unanswerable.

### Why Provenance

`Provenance` is FHIR's audit record: a separate resource saying that this resource was produced by that activity, at that time, by that actor.

For Grove it answers a question a reviewer eventually asks: where did this number come from, and what touched it on the way?
A step count read from a platform store, converted by an application, and uploaded is not the same evidence as one typed in by hand.
The Provenance carries the source record's own identifier, so a value can always be traced back to the platform row it came from.

It is a separate resource rather than a field because one conversion covers many Observations, and because audit data has a different lifetime from clinical data.

### Bundles

A `Bundle` is a container.
Grove uses `type: collection` — a plain set of resources travelling together, with no transactional meaning.

Inside a Bundle, resources refer to each other by `fullUrl`.
Grove derives those from each resource's business identifier, so the same conversion always produces the same Bundle and a re-send can be recognised as a duplicate rather than landing twice.

### Reading the rest of this guide

Profile pages are generated, and their two tables confuse people:

- The **Differential Table** shows only what this guide adds to the base resource.
  Read this one first; it is the actual content of the profile.
- The **Snapshot Table** shows every rule, including the hundreds inherited from FHIR R4.
  Useful as a reference, overwhelming as an introduction.

Fields marked **Must Support (MS)** have to be populated by a conformant producer whenever it has the data, and have to be readable by a conformant consumer.

Every profile has at least one example, with JSON, XML, and Turtle tabs.
For an application developer the JSON tab is almost always the fastest way in.

A good first path: read the [heart-rate example JSON](Observation-GroveMobileHeartRateExample.json), then the [Mobile envelope](StructureDefinition-grove-mobile-observation.html) that constrains it, then [Observations](observations.html) for the field-by-field rules.

### Where to go next

| You want to | Read |
|---|---|
| Encode a measurement | [Observations](observations.html) |
| Understand the device split and the audit trail | [Devices and provenance](devices.html) |
| Attach data to a study | [Study context](study.html) |
| Install the package and validate your JSON | [Implement and validate](implementation.html) |
| See how the ten guide packages fit together | [The Grove FHIR guides](guides.html) |
