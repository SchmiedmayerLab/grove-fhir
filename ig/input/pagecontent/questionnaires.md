<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Grove renders FHIR Questionnaires natively on mobile devices. The complete, audited
statement of what the renderer supports is the
[Renderer Support Matrix](questionnaire-support.html); the
[example questionnaire](Questionnaire-GroveQuestionnaireExample.html) and
[its response](QuestionnaireResponse-GroveQuestionnaireResponseExample.html) show the
hint vocabulary in use, end to end. The vocabulary is SDC-first; Grove defines an
extension only where SDC and the HL7 extensions pack have nothing.

### Where these questionnaires come from

Instruments an app defines for itself are authored in the app's own source language —
in Grove's case Swift, checked at build time — and exported to FHIR R4; the encodings
below are what that export emits. Instruments published by someone else arrive as FHIR R4
`Questionnaire` resources and are read directly. Both converge on the same resource, and
an authored instrument round-trips through it: exported and read back, it renders,
branches and scores identically.

Nothing on this page is specific to how a questionnaire was written, and an authored one
carries the same obligations as any other:

- `linkId` is authored explicitly and is the item's stable identity across versions. It
  is never derived from display text or from a source-language identifier.
- Answers meant to be interpreted outside the app are coded: an `answerOption` with a
  declared `system` exports as a `valueCoding`, one without as a bare `valueString` that
  only means something within its own questionnaire.
- Scores ride `itemWeight` on the options, with the total in an SDC
  `calculatedExpression` on an item marked `readOnly` and `questionnaire-hidden`.
- `Questionnaire.url` and `version` are authored, not generated; responses pin the
  canonical `url|version`.

### Text-input hints

| Need | Encoding |
|---|---|
| Validation rule + message | HL7 `targetConstraint`: the rule as FHIRPath in `expression`, the user-facing message in `human`, `severity` = `error`. Replaces the deprecated `regex` extension and Grove's old `validationText`. |
| Pre-entry format prompt | HL7 `entryFormat` |
| Keyboard | SDC `sdc-questionnaire-keyboard` (`phone`, `email`, `number`, `url`, `chat`; extensible) |
| Autofill semantics | [autocomplete](StructureDefinition-grove-autocomplete.html) — WHATWG `autocomplete` detail tokens, mapping 1:1 to iOS `UITextContentType`, Android autofill hints, and HTML |
| Autocapitalization | [autocapitalize](StructureDefinition-grove-autocapitalize.html) — WHATWG `autocapitalize` values |

**Maturity notes.** `sdc-questionnaire-keyboard` is new in SDC STU4 with no
third-party renderer support yet — it is a pure hint, never behavior-bearing; Grove's
renderer honors it and others safely ignore it. `targetConstraint` enforcement varies by
renderer (CSIRO Smart Forms supports it; LHC-Forms does not yet): the FHIR validator is
the guaranteed enforcement baseline, and capture-time enforcement is renderer-dependent.
Items using `itemMedia` SHALL keep meaningful `item.text` so renderers without media
support degrade to text. Attachment `mimeType`/`maxSize` are enforced by Grove's client
and server, not assumed of renderers.

**Transition note.** Some third-party renderers (notably the Android FHIR SDK) still
enforce the deprecated `regex` extension but not `targetConstraint`. Questionnaires
targeting such renderers MAY mirror a `targetConstraint` pattern into `regex` during a
documented transition window; Grove's renderer treats `targetConstraint` as canonical.

### The annotate-image item control

An attachment-type item rendered as a drawing surface over a base image
("mark where it hurts"):

- `questionnaire-itemControl` carries
  [`annotate-image`](CodeSystem-grove-questionnaire-item-control.html) (the HL7
  item-control system has no image-annotation code; its binding is extensible).
- The base image travels in SDC `sdc-questionnaire-itemMedia` (a real Attachment —
  renderer-portable, snapshottable into the response).
- Answer constraints use the standard `mimeType` and `maxSize` extensions.
- Selectable regions are declared with
  [annotate-image region](StructureDefinition-grove-annotate-image-region.html):
  a label, a pen color, and — where anatomical — a SNOMED body-site code, making
  answers extractable to `Observation.bodySite`.

The answer is the annotated image as an attachment.
