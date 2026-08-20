<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

FHIR separates a questionnaire from the answers collected with it:

- `Questionnaire` defines the questions, answer types, choices, conditions, and a stable
  canonical URL for the instrument.
- `QuestionnaireResponse` records one set of answers and points back to that canonical URL.

Grove profiles both resources so an instrument and its answers remain understandable
across applications. Start with the
[follow-up Questionnaire](Questionnaire-GroveFollowUpQuestionnaireExample.html) and its
[QuestionnaireResponse](QuestionnaireResponse-GroveFollowUpQuestionnaireResponseExample.html).
Both are also available as [Questionnaire JSON](Questionnaire-GroveFollowUpQuestionnaireExample.json)
and [QuestionnaireResponse JSON](QuestionnaireResponse-GroveFollowUpQuestionnaireResponseExample.json).

### Defining the instrument

Assign a stable canonical URL in `Questionnaire.url` to every instrument that will be
referenced by a QuestionnaireResponse. `Questionnaire.item` then defines the form. Each
user-facing question has:

- a `linkId` that is unique within the Questionnaire;
- a FHIR item `type`, such as `boolean`, `integer`, `choice`, or `string`;
- the question shown to the user in `text`;
- optional answer choices, initial values, validation rules, or display conditions.

The example asks a boolean screening question and enables an integer follow-up when the
answer is `true`:

```json
{
  "resourceType": "Questionnaire",
  "url": "https://grovealliance.org/fhir/core/Questionnaire/GroveFollowUpQuestionnaireExample",
  "status": "active",
  "item": [{
    "linkId": "pain",
    "type": "boolean",
    "text": "Have you had any pain in the last week?",
    "item": [{
      "linkId": "pain-severity",
      "type": "integer",
      "text": "How severe was it, from 0 to 10?",
      "enableWhen": [{
        "question": "pain",
        "operator": "=",
        "answerBoolean": true
      }]
    }]
  }]
}
```

Keep `linkId` values stable when revising display text. They are the structural keys that
join the definition to each response.

### Recording the answers

`QuestionnaireResponse.questionnaire` contains the Questionnaire canonical. Append
`|version` when a deployment distinguishes multiple instrument versions. The response
also records its workflow `status`, authored time in `authored`, and the `subject`
when the answers concern a Patient or another FHIR resource.

Grove-produced response items repeat the matching `linkId` and question `text`. Keeping
the text makes the response readable on its own; the referenced Questionnaire is still
authoritative for choices, constraints, definitions, and full interpretation. The
profile reports omitted text as a validation warning when an answered response comes
from another system.

```json
{
  "resourceType": "QuestionnaireResponse",
  "questionnaire": "https://grovealliance.org/fhir/core/Questionnaire/GroveFollowUpQuestionnaireExample",
  "status": "completed",
  "subject": { "reference": "Patient/GrovePatientExample" },
  "authored": "2026-08-12T18:34:00-07:00",
  "item": [{
    "linkId": "pain",
    "text": "Have you had any pain in the last week?",
    "answer": [{
      "valueBoolean": true,
      "item": [{
        "linkId": "pain-severity",
        "text": "How severe was it, from 0 to 10?",
        "answer": [{ "valueInteger": 7 }]
      }]
    }]
  }]
}
```

For this answer-dependent follow-up, the child belongs in `answer.item`, not beside the
parent response item. This keeps the follow-up in the context of the answer that caused
it to appear.

### Validation and presentation guidance

Use standard FHIR and Structured Data Capture extensions when they express the required
behavior. The standard `targetConstraint` extension carries validation expressions;
SDC extensions carry keyboard hints and media associated with an item. Item text remains
required when media is present so a renderer that does not display the media can still
present the question.

The [Grove Questionnaire profile](StructureDefinition-grove-questionnaire.html) defines
the instrument rules. The
[Grove QuestionnaireResponse profile](StructureDefinition-grove-questionnaire-response.html)
requires the instrument canonical and checks answered-item text.

In this guide, **Must Support** means that a producer populates an element when the
information is available and a consumer accepts and preserves or interprets it when
present. It does not change the element's stated cardinality.

Continue with [Read and Validate](consuming.html) to check an instrument and response
against both profiles.
