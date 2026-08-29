<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Questionnaire Exchange defines an interoperable way to publish an instrument and exchange its answers as FHIR R4.
The exchange uses two standard resources:

- a `Questionnaire` is the versioned instrument, including its questions, choices, conditions, and validation rules; and
- a `QuestionnaireResponse` records one administration of that instrument, including who the answers concern, when they were recorded, and the answers themselves.

Readers who are new to FHIR should begin with the [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.
It introduces the resources used across the Grove FHIR Implementation Guides, identifiers and references, and the structure of a profile page.

The profiles build on the [HL7 Structured Data Capture Implementation Guide](https://hl7.org/fhir/uv/sdc/). Applications exchange ordinary FHIR JSON; the profiles make the parts that affect interpretation explicit and testable.

### Versioned resource pairing

Every response references one exact instrument version:

```text
Questionnaire.url | Questionnaire.version
                      ▲
                      │ QuestionnaireResponse.questionnaire
                      │
              QuestionnaireResponse
```

For example, a response for version `1.0.0` is interpreted only with version `1.0.0` of the referenced Questionnaire.
A later Questionnaire with the same canonical URL is not a substitute.
Within the pair, `linkId` connects each response item to its definition, and the response preserves the same group/question hierarchy.

### Canonical example pair

| Resource | What to look for | JSON |
|---|---|---|
| [Weekly Symptom Check-In](Questionnaire-GroveWeeklySymptomCheckInExample.html) | Versioned identity, group, boolean question, coded choices, and conditional follow-up | [Questionnaire JSON](Questionnaire-GroveWeeklySymptomCheckInExample.json) |
| [Completed response](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.html) | Stable submission identifier, exact version, electronic completion, and answer-nested follow-up | [QuestionnaireResponse JSON](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.json) |

Review both JSON files together.
The `pain-present` item demonstrates how `linkId` joins the resources and how its `pain-severity` follow-up remains nested under the answer that established its context.
This example illustrates the identity and nesting rules that prevent most questionnaire exchange errors.

### Guide navigation

- [Quick start](quick-start.html) explains IG pages, profiles, packages, and the complete validation command sequence.
- [Define an instrument](instruments.html) covers versioning, item types, terminology, constraints, conditions, expressions, and hidden items.
- [Record answers](responses.html) maps each Questionnaire item type to the correct `QuestionnaireResponse.answer.value[x]` field and explains lifecycle and nesting.
- [Measurement extraction](measurements.html) explains how standard SDC extraction converts responses into profiled Observations and which source context is required.
- [Conformance](conformance.html) defines producer and consumer obligations, cross-resource validation, and failure behavior.
- [Artifacts](artifacts.html) lists the profiles and examples for FHIR-experienced implementers.

### Two-stage validation

First, the official FHIR Validator checks each resource against FHIR R4, SDC, and the applicable Grove profile.
The Grove paired validator then resolves both resources together and checks the exact canonical reference, hierarchy, answer types, choices, required and enabled state, and repetition limits.

A resource can pass profile validation and still form a nonconformant pair.
For example, a `valueCoding` may be valid FHIR by itself, but the referenced Questionnaire determines whether that code was an allowed answer.
Always run both passes before accepting a completed or amended response.
