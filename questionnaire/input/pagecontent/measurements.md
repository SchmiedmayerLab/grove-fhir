<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

An instrument can ask for a reading a person takes themselves.
A server that implements the SDC `$extract` operation turns those answers into Observations, and Grove requires enough of the instrument and the response that the result stands beside one an adapter produced.

Extraction is declared with SDC's own extensions rather than a Grove mechanism.
`observationExtract` on an item marks it for extraction, and `item.code` supplies the Observation code.

### One response, several Observations

`observationExtract` is answered either as `true` or as a relationship code, never as both on one item.

`true` extracts the item as its own Observation.
An instrument that asks for a weight and a symptom score marks both `true` and yields two unrelated Observations from one response.

A relationship code says how a child item relates to its parent's Observation.
`#component` puts the child on the parent as a component, so a blood pressure panel marking its systolic and diastolic children `#component` yields one Observation under LOINC 85354-9 rather than two readings.
`#member` and `#derived` extract the child separately and link it through `hasMember` or `derivedFrom`, and `#independent` extracts it with no link at all.

`observationExtractCategory` supplies `Observation.category`, which the vital-signs profiles require.
An extracted blood pressure without it does not satisfy the profile the measurement catalog names for it.

### What the response has to carry

`subject` is required and references a Patient, matching what an extracted Observation accepts.

`extension[writerContext]` states the application and host that captured the response.
A writer cannot mint a Grove device snapshot, whose identity is scoped to an exchange event that does not exist when a response is submitted.
It states plain facts instead, and a projecting system builds the snapshot from them once it holds the event and the key.

### Where a unit comes from

The instrument states the unit, not the client.

A `quantity` item offers its units through `questionnaire-unitOption`, or through `questionnaire-unitValueSet` when the choice is large.
A renderer shows those and puts the chosen one in the answer's Quantity, so `Home Vitals` offering `kg` is what makes the weight answer come back in `kg`.
An `integer` or `decimal` item instead fixes one unit with `questionnaire-unit`, which the renderer displays and the projection asserts.

An item that offers no unit leaves the renderer to invent one, and the answer is then unusable.
Neither form is bound to the unit a measurement fixes, so an instrument offering `[lb_av]` for a weight extracts into an Observation that fails the body weight profile.

### A worked instrument

[Home Vitals](Questionnaire-GroveHomeVitalsExample.html) asks for a weight and a blood pressure, and extracts three ways at once.

The weight item carries the measurement's own LOINC code and marks itself `true`, so it extracts as a standalone Observation.

```
* item[0].linkId = "body-weight"
* item[0].type = #quantity
* item[0].code = $loinc#29463-7 "Body weight"
* item[0].extension[observationExtract].valueBoolean = true
* item[0].extension[observationExtractCategory].valueCodeableConcept = $observationCategory#vital-signs
* item[0].extension[unitOption].valueCoding = $ucum#kg "kg"
```

The blood pressure group carries the panel code and marks itself `true`; its two children name themselves `#component`.
That is what puts both readings on one Observation instead of two.

```
* item[1].code = $loinc#85354-9 "Blood pressure panel with all children optional"
* item[1].extension[observationExtract].valueBoolean = true
* item[1].item[0].code = $loinc#8480-6 "Systolic blood pressure"
* item[1].item[0].extension[$observationExtract].valueCode = #component
* item[1].item[0].extension[$unitOption].valueCoding = $ucum#mm[Hg] "mm[Hg]"
* item[1].item[1].code = $loinc#8462-4 "Diastolic blood pressure"
* item[1].item[1].extension[$observationExtract].valueCode = #component
* item[1].item[1].extension[$unitOption].valueCoding = $ucum#mm[Hg] "mm[Hg]"
```

[The response](QuestionnaireResponse-GroveHomeVitalsResponseExample.html) answers each item as a Quantity in the unit its measurement fixes, names its Patient, and carries the writer context.

Extraction yields two Observations.
The weight becomes `29463-7` with `valueQuantity` 72.5 kg; the panel becomes `85354-9` with no value of its own and two components, `8480-6` at 118 mm[Hg] and `8462-4` at 76 mm[Hg].
Both take `vital-signs` from `observationExtractCategory` and `effectiveDateTime` from `authored`.

The weight arrives like this, with the identifiers, the recording method, and the device reference supplied by the projecting system.

```json
{
  "resourceType": "Observation",
  "meta": { "profile": ["…/StructureDefinition/grove-mobile-body-weight"] },
  "identifier": [
    { "type": { "coding": [{ "code": "source-record" }] }, "value": "v2:test-key:1:…" },
    { "type": { "coding": [{ "code": "source-output" }] }, "value": "v2:test-key:1:…" }
  ],
  "status": "final",
  "category": [{ "coding": [{ "code": "vital-signs" }] }],
  "code": { "coding": [{ "system": "http://loinc.org", "code": "29463-7" }] },
  "subject": { "reference": "Patient/GroveQuestionnairePatientExample" },
  "effectiveDateTime": "2026-08-28T08:32:00-07:00",
  "valueQuantity": { "value": 72.5, "unit": "kg", "system": "http://unitsofmeasure.org", "code": "kg" },
  "extension": [
    { "url": "…/grove-recording-method", "valueCodeableConcept": { "coding": [{ "code": "manual-entry" }] } },
    { "url": "…/observation-gatewayDevice", "valueReference": { "reference": "Device/home-vitals-writer-snapshot" } }
  ],
  "derivedFrom": [{ "reference": "QuestionnaireResponse/GroveHomeVitalsResponseExample" }]
}
```

### Where the writer context lands

The response states the capturing application as plain facts; the projection turns them into the Device snapshot the Observation points at.

```json
{
  "resourceType": "Device",
  "id": "home-vitals-writer-snapshot",
  "meta": { "profile": ["…/StructureDefinition/grove-application-device"] },
  "deviceName": [{ "name": "Grove Questionnaire Client", "type": "user-friendly-name" }],
  "version": [
    { "type": { "coding": [{ "system": "urn:iso:std:iso:11073:10101", "code": "531975" }] }, "value": "1.4.0" },
    { "type": { "coding": [{ "code": "build" }] }, "value": "1402" }
  ],
  "parent": { "reference": "Device/home-vitals-host-snapshot" }
}
```

Its parent carries the host, `iPhone17,1` running `26.0`, so an Observation reached from either end names the application build and the hardware it ran on.

### What a projection does not recover

An adapter reading the same weight from a phone's health store carries three things this route cannot.

It carries a writer record identifier and its version, so a later correction supersedes the earlier reading rather than arriving beside it.
A response has no writer revision to build either from.

It carries the exact instant of the reading, at the precision the store recorded it.
A projection carries `authored`, which is when the answers were gathered.

It carries a source-type marker naming the native type the reading came from, and the recording device when the store names one.
A projection names manual entry and the capturing application, which is the honest equivalent and not the same fact.

### Measurement time

`authored` records when the answers were gathered, which need not be when the reading was taken.
Observation-based extraction has nowhere to put the second time, so it uses `authored`.

That is exact for a reading taken while answering and wrong for one entered later.

It also gives every Observation from one response the same time, so a weight and a blood pressure taken twenty minutes apart both claim the instant the answers were gathered.

That limit belongs to observation-based extraction rather than to the approach.
An instrument that asks when a reading was taken can bind that answer straight to `Observation.effective[x]` through SDC's definition-based extraction, and each Observation then carries its own time.
The same mechanism supplies a period, from two answered boundaries or from an expression over the response.
An instrument asking how many steps a person took yesterday knows the period from its own wording, and can state it rather than leave a reader to infer it.

`Home Vitals` shows both.
The blood pressure group asks when the reading was taken and binds that answer to the panel's own instant, so the panel does not inherit the moment the form was submitted.

```
* item[1].item[2].linkId = "measured-at"
* item[1].item[2].type = #dateTime
* item[1].item[2].extension[$definitionExtractValue].extension[definition].valueUri = "http://hl7.org/fhir/StructureDefinition/Observation#Observation.effectiveDateTime"
```

The step count asks for yesterday's total and states the day it means, computing both boundaries from the response rather than asking a person to type them.

```
* item[2].extension[$definitionExtractValue][0].extension[definition].valueUri = "http://hl7.org/fhir/StructureDefinition/Observation#Observation.effectivePeriod.start"
* item[2].extension[$definitionExtractValue][0].extension[expression].valueExpression.expression = "(%resource.authored.toDate() - 1 day).toString() + 'T00:00:00' + %resource.authored.toString().substring(19)"
```

Both forms are declared on the instrument, which is what keeps them safe.
An extractor that has not been told which item carries the time falls back to `authored` and is quietly wrong, so an instrument whose measurement time is not the moment of answering states the binding or does not project.
