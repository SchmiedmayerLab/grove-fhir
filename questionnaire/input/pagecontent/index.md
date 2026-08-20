<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Questionnaire Exchange defines a dependable way to publish a form and return
its answers as FHIR R4. It uses two standard resources:

- a `Questionnaire` is the versioned instrument: questions, choices, conditions, and
  validation rules;
- a `QuestionnaireResponse` is one administration of that instrument: who or what the
  answers concern, when they were recorded, and the answers themselves.

The profiles build on the
[HL7 Structured Data Capture Implementation Guide](https://hl7.org/fhir/uv/sdc/).
Applications exchange ordinary FHIR JSON; the profiles make the parts that affect
interpretation explicit and testable.

### The one relationship to understand first

Every response points to one exact instrument version:

```text
Questionnaire.url | Questionnaire.version
                      ▲
                      │ QuestionnaireResponse.questionnaire
                      │
              QuestionnaireResponse
```

For example, a response for version `1.0.0` is interpreted only with version `1.0.0`.
A later Questionnaire with the same URL is not a substitute. Within the pair, `linkId`
connects each response item to its definition, and the response preserves the same
group/question hierarchy.

### Start with a complete pair

| Resource | What to look for | JSON |
|---|---|---|
| [Weekly Symptom Check-In](Questionnaire-GroveWeeklySymptomCheckInExample.html) | Versioned identity, group, boolean question, coded choices, and conditional follow-up | [Questionnaire JSON](Questionnaire-GroveWeeklySymptomCheckInExample.json) |
| [Completed response](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.html) | Stable submission identifier, exact version, electronic completion, and answer-nested follow-up | [QuestionnaireResponse JSON](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json) |

Open both JSON files side by side. Find `pain-present` in each, then follow its answer to
the nested `pain-severity` item. That small example contains the identity and nesting
rules that prevent most questionnaire exchange errors.

### Choose the page that matches your task

- [Quick start](quick-start.html) explains IG pages, profiles, packages, and the complete
  validation command sequence.
- [Define an instrument](instruments.html) covers versioning, item types, terminology,
  constraints, conditions, expressions, and hidden items.
- [Record answers](responses.html) maps each Questionnaire item type to the correct
  `QuestionnaireResponse.answer.value[x]` field and explains lifecycle and nesting.
- [Conformance](conformance.html) defines producer and consumer obligations, validation
  failure behavior, and the deterministic test corpus.
- [Artifacts](artifacts.html) lists the profiles and examples for software that already
  knows FHIR.

### Validation has two passes

First, the official FHIR Validator checks each resource against FHIR R4, SDC, and the
Grove profile. Then the Grove paired validator resolves both resources together and
checks the exact canonical, hierarchy, answer types, choices, required/enabled state,
and repeated-answer limits.

A resource can pass profile validation and still be a bad pair. For example, a
`valueCoding` is valid FHIR by itself, but only the referenced Questionnaire can say
whether that code was an allowed answer. Always run both passes before accepting a
completed or amended response.
