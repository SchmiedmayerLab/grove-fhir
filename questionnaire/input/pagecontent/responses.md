<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A [Grove Questionnaire Response](StructureDefinition-grove-questionnaire-response.html)
records one administration of one exact Questionnaire version.

### Identity and lifecycle

`QuestionnaireResponse.identifier` is the stable business identifier for the submission.
Compare the complete `(system, value)` pair. `Resource.id` and `meta.versionId` are
server-managed identifiers and do not replace it.

`QuestionnaireResponse.questionnaire` contains the exact `Questionnaire.url|version`.
The value has one `|` separator and no fragment. Resolve the instrument before
processing any answer.

The status describes the response lifecycle:

- `in-progress` may omit required answers and may contain population work still in
  progress;
- `completed` and `amended` must satisfy enabled, required, and validation rules;
- `stopped` may preserve a deliberately incomplete administration; and
- `entered-in-error` retracts the response as usable answer data. Preserve it for audit
  when required, but do not analyze or submit its answers as a valid response.

`authored` is when answers were gathered or authored, not necessarily upload time.
`subject` is who or what the answers concern, `author` is who recorded them, and `source`
is who supplied them. These roles may identify different actors and must not be inferred
from one another.

The standard `questionnaireresponse-completionMode` extension contains exactly one
Coding with ParticipationMode system and code `ELECTRONIC`. Its display is descriptive
and is not constrained.

### Item and answer structure

Every response item repeats the matching Questionnaire `linkId`. Response item `text`
is optional presentation content: a producer may omit it or carry the wording shown to
the user in a different locale. A receiver must neither require it nor compare it with
the Questionnaire prompt. Resolve the exact instrument to obtain authoritative prompts,
choices, conditions, and constraints.

Groups place child response items directly in `item`. A child defined beneath a question
belongs beneath the particular `answer.item` that created its context. Do not move that
child beside the parent question.

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

Reference answers are not accepted by this contract. Preserve the full Coding,
Quantity, or Attachment instead of flattening it to display text.

### Required, enabled, and repeated answers

For completed and amended responses, every enabled item marked `required=true` has an
answer. Disabled items are omitted. Core `enableWhen` is evaluated against the response;
expression-based enablement requires a conforming FHIRPath engine.

When `repeats` is false or absent, an item has at most one answer. Repeating choice,
open-choice, and attachment items may carry multiple answers, subject to
`questionnaire-minOccurs` and `questionnaire-maxOccurs`. An option marked exclusive
cannot be combined with another answer.

For `answerOption`, the response value matches one inline option. For `answerValueSet`,
the Coding belongs to the resolved ValueSet version. A display string alone never proves
membership.

The [completed example](QuestionnaireResponse-GroveWeeklySymptomCheckInResponseExample.html)
shows group wrapping, a boolean answer, and a coded follow-up nested in `answer.item`.
