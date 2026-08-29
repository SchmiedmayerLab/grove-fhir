<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A conforming instrument is a [Grove Questionnaire](StructureDefinition-grove-questionnaire.html), derived from the SDC Base Questionnaire.
Treat it as a durable data definition rather than a sequence of screens.

### Identity and versioning

`Questionnaire.url` identifies the instrument across systems. It is required to be one absolute HTTP(S) canonical URL without `|` or a fragment. `Questionnaire.version` identifies one immutable definition of that instrument.
This profile requires a valid Semantic Versioning 2.0.0 value and the standard `artifact-versionAlgorithm` extension fixed to `semver`.

Increment the version whenever an interpretation-relevant property changes: item meaning, datatype, answer choices, required state, condition, constraint, or hierarchy.
Never publish different content with the same `url|version`.

For `answerValueSet` and `unitValueSet`, use a versioned canonical whenever the ValueSet publisher supplies stable versions.
A response can then be checked against the same terminology content that the respondent saw.

### Item identity and hierarchy

`Questionnaire.item.linkId` is the join key between the instrument and every response.
It is not display text and should not encode the item's current position.
Use concise, durable values such as `pain-present` and `pain-severity`; do not reuse a `linkId` within one Questionnaire.

Groups organize related items. Questions nested beneath another question are answered in the context of one parent answer.
Item order is meaningful and should be preserved.
Every question and display item has text; a structural group may omit a heading.

### Answer types and choices

Use the standard R4 item types: boolean, decimal, integer, date, dateTime, time, string, text, url, choice, open-choice, quantity, and attachment.
Reference questions and reference-valued answer options are outside this exchange contract.

For a small fixed list, place allowed values in `answerOption`.
For a maintained code set, use `answerValueSet`.
A `choice` answer is a `Coding`; an `open-choice` answer is either a listed `Coding` or free `string`.
Preserve system and code, not only display.

Repeated answers are limited to choice, open-choice, and attachment items. This contract does not define repeated groups or repeated scalar questions.

### Portable constraints

Constraints are exchange semantics.
Put each extension only on the item types for which it is defined:

| Constraint | Item types and relationship |
|---|---|
| `minLength`, `maxLength` | string, text, url, open-choice; minimum cannot exceed maximum |
| `minValue`, `maxValue` | integer, decimal, date, dateTime, time; bound datatype matches item datatype |
| `maxDecimalPlaces` | decimal only; non-negative |
| SDC `minQuantity`, `maxQuantity` | quantity only; comparable UCUM units and minimum no greater than maximum |
| `questionnaire-unit` | fixed computable unit for integer or decimal |
| `questionnaire-unitOption`, `questionnaire-unitValueSet` | selectable units for quantity; use inline options or one ValueSet, not both |
| `questionnaire-minOccurs`, `questionnaire-maxOccurs` | repeating choice, open-choice, or attachment; minimum no greater than maximum |
| `mimeType`, `maxSize` | attachment only; positive maximum size |

The profile enforces relationships that are dependable in single-resource FHIRPath.
The deterministic static checker verifies datatype-specific bound comparisons, exact UCUM system-and-code comparability for quantity bounds, variable scope, and other relationships that a profile cannot evaluate reliably.
Bounds expressed in different units require a UCUM-capable validation service; the checker does not guess conversions.

### Conditions and expressions

Use core `enableWhen` for comparisons against another answer.
Set `enableBehavior` when more than one condition is present.
Use SDC `enableWhenExpression` only when core `enableWhen` cannot express the rule; an item never carries both.

The retained expression extensions use `text/fhirpath` and a non-empty expression:

- `variable` at the Questionnaire or item level; every variable has a unique, non-reserved name within that scope;
- `enableWhenExpression`;
- `initialExpression` or a literal `initial`, never both;
- `calculatedExpression`; and
- `targetConstraint` at the Questionnaire root or an item.

The important SDC expression context is:

- `%resource` is the QuestionnaireResponse being populated or evaluated;
- `%context` is the current response focus for the expression;
- `%questionnaire` is the Questionnaire resolved from the response canonical;
- `%qitem` is the Questionnaire item corresponding to the current response item;
- `answers()` collects descendant response answers beneath the focus; and
- `weight()` returns the standard ordinal weight attached to a coded answer, or an empty result when none is defined.

The standard `targetConstraint` extension also defines `%target` as the instantiated resource and `%definition` as the definition from which it was created.
In an SDC form workflow, `%resource` remains the current QuestionnaireResponse.

Earlier SDC material called the analogous scoring function `ordinal()`.
This guide targets SDC 4.0.0, where the function is `weight()`; do not copy an `ordinal()` expression without confirming that the evaluator supports the older function.
Do not replace the standard function with a private scoring function or treat `$this` as though it always refers to an answer.
The expression's documented context determines its focus.

A standard item-level `targetConstraint` looks like this:

```json
{
  "url": "http://hl7.org/fhir/StructureDefinition/targetConstraint",
  "extension": [
    {"url": "key", "valueId": "comment-not-blank"},
    {"url": "severity", "valueCode": "error"},
    {
      "url": "expression",
      "valueExpression": {
        "language": "text/fhirpath",
        "expression": "%resource.repeat(item | answer.item).where(linkId = 'comments').answer.value.ofType(string).all($this.trim().length() > 0)"
      }
    },
    {"url": "human", "valueString": "Enter a comment or leave the item unanswered."}
  ]
}
```

An expression is executable behavior.
A form filler must not silently ignore an expression that can change enablement, calculated content, or validity.

### Hidden and presentation extensions

The inherited `questionnaire-hidden` extension is Must Support. `hidden=true` means the item is not shown to the respondent; it may still carry populated or calculated data and remains part of the instrument's behavior and validation.

Keyboard hints, item controls, media placement, and similar renderer extensions may be used as optional presentation metadata.
They must not change the meaning or allowed answers. `rendering-styleSensitive` states that styling is necessary to interpret the content; that cannot be processed safely by this contract and a conforming filler rejects such an instrument before administration.
