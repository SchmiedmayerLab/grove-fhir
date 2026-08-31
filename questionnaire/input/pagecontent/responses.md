<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A [Grove Questionnaire Response](StructureDefinition-grove-questionnaire-response.html) records one administration of one exact Questionnaire version.

### Response identity and instrument resolution

`QuestionnaireResponse.identifier` is the stable business identifier for the submission.
Compare the complete `(system, value)` pair.
`Resource.id` identifies a resource within its exchange or persistence context, and `meta.versionId` identifies a stored revision where versioning is used; neither replaces the business identifier.

`QuestionnaireResponse.questionnaire` contains the exact `Questionnaire.url|version`.
The value has one `|` separator and no fragment.
Resolve the instrument before processing any answer.

### Lifecycle and participation metadata

The response status determines how completeness rules and answer data are interpreted:

| Status | Interpretation |
|---|---|
| `in-progress` | Required answers may be absent, and population work may remain incomplete. |
| `completed`, `amended` | Enabled, required, and validation rules must be satisfied. |
| `stopped` | The resource may preserve a deliberately incomplete administration. |
| `entered-in-error` | The response is no longer usable answer data: it asserts that the answers were recorded in error. Preserve it when audit requirements apply, but do not treat its answers as valid for analysis or submission. |

`entered-in-error` is not the same act as a Grove [retraction event](https://grovealliance.org/fhir/mobile/observations.html#retraction-events).
Retraction says a source record is no longer exposed and deliberately asserts nothing about whether the prior statement was erroneous; `entered-in-error` asserts exactly that it was.
When a response has been projected into an exchange graph, that graph's outputs are withdrawn through the retraction path against their own source-output identifiers, independently of the response's own status.

`authored` is when the answers were gathered or authored, not necessarily when the resource was transmitted or stored.
`subject` identifies who the answers concern and is a required reference to a Patient; `author` identifies who recorded the answers; and `source` identifies who supplied them.
These roles may identify different actors and must not be inferred from one another.

The instrument declares `Patient` as its subject type, and the response subject matches it.
The paired validator checks this cross-resource rule after resolving the exact instrument and rejects a `Reference.type` that contradicts a type visible in the literal or contained target.
A declared type is either the relative R4 resource code (for example, `Patient`) or its exact core canonical (`http://hl7.org/fhir/StructureDefinition/Patient`); an arbitrary URI is not accepted merely because its last path segment resembles a resource type.
The official FHIR Validator remains authoritative for the base `author` and `source` target constraints.

The standard `questionnaireresponse-completionMode` extension contains exactly one Coding with ParticipationMode system and code `ELECTRONIC`.
Its display is descriptive and is not constrained.

### Response item structure

Every response item repeats the matching Questionnaire `linkId`.
Response item `text` is optional presentation content: a producer may omit it or carry the wording shown to the user in a different locale.
A receiver must neither require it nor compare it with the Questionnaire prompt.
Resolve the exact instrument to obtain authoritative prompts, choices, conditions, and constraints.

The Questionnaire hierarchy determines where child response items are represented:

| Questionnaire relationship | QuestionnaireResponse location |
|---|---|
| Child of a group | Directly in the group's `item` array |
| Child of a question | In `answer.item` for the particular parent answer that established its context |

Moving an answer-context child beside its parent question changes its meaning and is not conformant.

### Answer datatypes

Use the answer field dictated by the Questionnaire item type:

| Questionnaire `item.type` | QuestionnaireResponse answer |
|---|---|
| boolean | `valueBoolean` |
| decimal | `valueDecimal` |
| integer | `valueInteger` |
| date | `valueDate` |
| dateTime | `valueDateTime` |
| time | `valueTime` |
| string, text | `valueString` |
| url | `valueUri` |
| choice | `valueCoding` |
| open-choice | `valueCoding` for a listed choice or `valueString` for other text |
| quantity | `valueQuantity` |
| attachment | `valueAttachment` |
| group, display | no answer value |

Reference answers are not accepted by this contract.
Preserve the full Coding, Quantity, or Attachment instead of flattening it to display text.

### Comparison semantics

Temporal answers retain their R4 datatype and lexical precision.
Comparisons normalize a `dateTime` offset to the represented instant but do not invent a missing month, day, or fractional-second precision.
When two precision ranges overlap without denoting the same value, the comparison is indeterminate; completion fails closed when a condition depends on that comparison.
The Grove FHIR contracts admit leap-second values only at whole-second precision and reject fractional leap seconds.

For quantities with coded units, equality compares the numeric `value` and the coded unit identity (`system` and `code`).
The `unit` element is presentation text in that case, so `kg` and `kilogram` remain equal when both carry the same UCUM code.
When both quantities omit coded unit identity, equality instead compares the numeric value and `unit` text; a coded and an uncoded Quantity are not equal.
Unit-option membership is a separate Coding comparison against the Quantity's `system` and `code`; it is not equality with the complete Quantity.

### Enablement, required items, and repetition

In a completed or amended response, every enabled item marked `required=true` is present, and every enabled required question has an answer.
Disabled items are omitted.
Core `enableWhen` is evaluated against the response; expression-based enablement requires a conforming FHIRPath engine.

When `repeats` is false or absent, a question has at most one answer and a group has at most one response occurrence in its parent context.
A repeating question carries multiple answers in one response item.
A repeating group is represented by multiple group-item occurrences; each occurrence evaluates its descendants against answers in that occurrence rather than answers from another repetition.
For enabled items, `questionnaire-maxOccurs` always limits occurrences; `questionnaire-minOccurs` is enforced when the response is `completed` or `amended`.
An option marked exclusive cannot be combined with another answer.

When an item declares `answerOption`, a response value matches one inline option.
An `open-choice` item may instead contain unlisted free text in `valueString`.
For `answerValueSet`, the Coding belongs to the resolved ValueSet version.
A display string alone never proves membership.

The [completed example](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.html) shows group wrapping, a boolean answer, and a coded follow-up nested in `answer.item`.
