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

### Response language

`QuestionnaireResponse.language` is required and names the language the participant saw.
It is the instrument's base language or one of its translation languages, compared case-insensitively.
A filler that renders the `es` translation for an `es-US` participant records `es`, the language it actually showed; `es-US` would name a translation the instrument does not offer.
The paired validator reports a language the instrument does not offer as `pair-response-language`.

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
Response item `text` is optional.
When present, it equals the base `Questionnaire.item.text` of the exact instrument, character for character, which is also what the HL7 FHIR Validator requires.
The [R5 comment on the element](https://hl7.org/fhir/R5/questionnaireresponse-definitions.html#QuestionnaireResponse.item.text) says the text SHOULD be identical to the Questionnaire item's text and gives one reason it cannot be strictly enforced, a Questionnaire updated after the response; an exact `url|version` removes that reason.
A producer that rendered a translation therefore omits `text`; `language` records what the participant read, and the instrument's translation into that language recovers the wording.
Omitted text is never an issue, and text that differs from the base is reported as `pair-item-text`.
Resolve the exact instrument to obtain authoritative prompts, choices, conditions, and constraints.

Coded answers follow the same rule.
When `QuestionnaireResponse.language` differs from the instrument's base language, an answer `Coding` carries `system` and `code` and omits `display`, because those two identify the answer.
In the base language, a display that is present equals the option's base display.
The paired validator compares `system` and `code` only and never checks a display.

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
Preserve the full Coding, Quantity, or Attachment instead of flattening it to display text; a response in a translation omits the Coding's display, as [response item structure](#response-item-structure) explains.

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
Time-dependent FHIRPath functions (`now()`, `today()`, `timeOfDay()`) are evaluated at an explicit instant in an explicit zone, never at whatever the evaluating device happens to use.
While a participant answers, that is the current instant in the participant's zone; a stored response is evaluated at `authored`, in the UTC offset `authored` carries.
Calculated answers are recomputed at `authored` before a completed or amended response is exported, so re-evaluating it later on any device yields the same values and the same enablement.

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
The [Spanish example](QuestionnaireResponse-GroveWeeklySymptomCheckInSpanishResponseExample.html) answers the same instrument from its Spanish translation: it names `es` and carries neither item text nor an answer display.
