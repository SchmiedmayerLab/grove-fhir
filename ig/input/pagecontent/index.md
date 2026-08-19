<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove FHIR defines how mobile health measurements and questionnaires are represented
as FHIR R4 resources. It keeps the clinical content in standard FHIR elements and adds
the source details needed to interpret, trace, and deduplicate data collected on a
mobile device.

You do not need to learn the entire guide before using it. Start with the kind of data
you want to exchange:

| I want to… | Start here |
|---|---|
| Encode a measurement from HealthKit | [Mobile Observations](mobile.html) |
| Exchange a form and its answers | [Questionnaires](questionnaires.html) |
| Check a JSON resource | [Read and Validate](consuming.html) |

### Mobile observations

A mobile measurement is a FHIR `Observation`. The measurement, subject, and time use
standard FHIR fields. Grove profiles add a stable source-record identifier and describe
the sensor that recorded the value, the app that saved it, the capture method, and
typed source metadata.

```text
mobile platform record
        |
        v
Observation ----> recording Device
        |
        +--------> gateway Device (app + operating system)
```

Begin with the [step-count example](Observation-GroveStepCountObservationExample.html),
then use the [Mobile Sensor Observation profile](StructureDefinition-grove-mobile-sensor-observation.html)
to see every rule.

### Questionnaires

A FHIR `Questionnaire` defines an instrument. A `QuestionnaireResponse` contains the
answers and names the instrument by its canonical URL. Stable `linkId` values connect
each answer to its question, including conditional follow-up questions.

```text
Questionnaire.url <---- QuestionnaireResponse.questionnaire
Questionnaire.item.linkId <---- QuestionnaireResponse.item.linkId
```

The [follow-up questionnaire](Questionnaire-GroveFollowUpQuestionnaireExample.html) and
its [completed response](QuestionnaireResponse-GroveFollowUpQuestionnaireResponseExample.html)
show the complete relationship.

### How to read this guide

FHIR implementation guides use a few recurring terms:

- A **profile** states the rules for a FHIR resource, including required fields,
  allowed types, terminology bindings, and invariants.
- An **extension** gives a defined home to information that has no suitable field in
  the base FHIR resource.
- A **terminology resource** defines the systems and values used in coded fields.
- An **example** is a complete resource that applies the profiles in a realistic case.

On a generated profile page, start with **Overview** and **Differential Table**. The
differential shows what this guide adds to base FHIR. Use **Snapshot Table** when you
need the complete inherited structure, and **JSON** when implementing or debugging a
serializer.

The quickest practical route is: inspect an example, open its profile, then
[validate your own resource](consuming.html).
