<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The authoritative statement of what Grove's native questionnaire renderer reads,
enforces, and emits, audited against FHIR R4 and SDC STU4 semantics. The deprecated
ResearchKit-based path appears only where it diverges; remaining gaps are on the
[Renderer Roadmap](questionnaire-roadmap.html).

Legend: **✓** supported · **partial** (see note) · **import only** (recognised when
reading an instrument; nothing in Grove writes it yet) · **legacy only** (read solely by
the deprecated ResearchKit path) · **—** not supported (documented gap).

### Item types

| `item.type` | Support | Notes |
|---|---|---|
| `group` | ✓ | Top-level groups render as pages; nested groups are display-flattened, and the generated response restores the full group hierarchy |
| `display` | ✓ | Markdown-capable; `rendering-markdown` on `_text` preferred; nested `help` display items render as the parent question's guidance |
| `boolean` | ✓ | |
| `decimal` | ✓ | Emits `valueDecimal` (`valueQuantity` when a unit is declared) |
| `integer` | ✓ | Emits `valueInteger` |
| `quantity` | ✓ | Emits `valueQuantity` with the full coded unit; participant-selectable units via `unitOption`/contained `unitValueSet` |
| `date` / `dateTime` / `time` | ✓ | `dateTime` answers carry time of day and a zone offset |
| `string` / `text` | ✓ | SDC `keyboard` hints honored (legacy `iosKeyboardType` spellings mapped) |
| `url` | ✓ | Emits `valueUri`; validated while editing and again at response generation |
| `choice` / `open-choice` | ✓ | Coding options keyed by `system\|code`; string/integer/date/time `answerOption` values; `optionExclusive`, `optionPrefix`, weights; "Other" label via SDC `openLabel` |
| `attachment` | ✓ | Inline attachment with contentType, SHA-1 hash, size; `mimeType` restricts the picker, `maxSize` enforced at validation; memory-mapped encoding |
| `reference` | — | Conversion fails with a clear error (documented non-goal: no record store to pick references from) |
| `question` | — | Abstract in R4; rejected |

### Core behavior

| Feature | Support | Notes |
|---|---|---|
| `required` | ✓ | Defaults to `false` per R4 |
| `readOnly` / `questionnaire-hidden` | ✓ | Hidden items carry values (pre-populated or calculated) without rendering or blocking completion |
| `initial[x]` / `answerOption.initialSelected` | ✓ | Seeds editable starting values, including coded choice selections |
| `repeats` | partial | Multi-select for `choice` (with `minOccurs`/`maxOccurs` selection bounds), multi-file for `attachment`; repeating groups/questions not supported |
| `enableWhen` — all seven operators | ✓ | `!=` false while unanswered; coding comparisons honor `system`; `answerQuantity` compares in the question's (or selected) unit; unanswered/disabled sources count as absent; `answerReference` aborts conversion |
| `enableBehavior`, forward references | ✓ | Resolved questionnaire-wide; self-references and cycles evaluate as absent |
| Items nested beneath a question | ✓ | Asked once the parent is answered; answers nest beneath the parent's answer |
| `answerValueSet` | ✓ | Contained ValueSets (every `compose.include`; `expansion` preferred) and external canonicals via the app-supplied resolver; live `$expand` is out of scope — ship expansions |
| `maxLength` (+ `minLength`) | partial | Enforced for text-entry items; other item types permitted by R4 are ignored |
| Duplicate linkIds (que-2) | ✓ | Checked across the whole item tree, groups included |
| Unknown `modifierExtension` | ✓ | Conversion refuses per R4 processing rules |
| `Questionnaire.version` | ✓ | Generated responses pin the canonical (`url\|version`); drafts refuse to resume across versions |
| `Questionnaire.status` / `effectivePeriod` | ✓ | `retired` refuses to convert (opt-out for tooling); drafts and out-of-period instruments surface `administrationWarnings` |
| Localization (`translation` extension) | ✓ | `item.text`, titles, and option displays resolve per locale |

### SDC expressions (FHIRPath)

Backed by a native FHIRPath evaluator (SDC subset: paths, comparisons, arithmetic,
boolean logic, collection/string/math/aggregate functions, `weight()`, `descendants()`).
`text/cql` and `x-fhir-query` expressions fail conversion with a clear error.

| Feature | Support |
|---|---|
| `enableWhenExpression` | ✓ (mutually exclusive with `enableWhen`, enforced) |
| `calculatedExpression` | ✓ live recomputation (e.g. PHQ-9 totals into hidden items) |
| `initialExpression` + `launchContext` | ✓ app supplies context resources (e.g. `%patient`); population is best-effort per SDC |
| `variable` | ✓ questionnaire-level and item-declared (evaluated in a shared scope, in document order) |
| `targetConstraint` (+ retired `questionnaire-constraint`) | ✓ cross-field validation with authored messages and severities |
| `answerExpression` / `answerOptionsToggleExpression` | — (static option model; see roadmap) |
| `weight()` scoring | ✓ `itemWeight` (+ retired `ordinalValue`) parsed from options, ValueSet concepts, and codings; emitted onto answer codings |

### Rendering & input hints

| Feature | Support |
|---|---|
| `questionnaire-itemControl` | ✓ `slider` (needs step + both bounds; degrades to a number pad), `drop-down`, `autocomplete` (client-side filtering), `help`, custom Grove controls; `radio-button`/`check-box` accepted (list rendering; multi-select from `repeats`); unrecognized codes fall back per SDC; `gtable`/`table` fall back to stacked layout |
| `item.prefix` / SDC `shortText` | ✓ numbering rendered; short titles used on watchOS |
| SDC `itemMedia` | ✓ inline image attachments with alt text (from `title`); `itemAnswerMedia` not yet |
| `rendering-markdown` | ✓ display text renders full Markdown |
| `rendering-styleSensitive` | ✓ surfaced as an administration warning (styling itself is a non-goal) |
| `questionnaire-supportLink` | ✓ rendered as a footer link |
| `questionnaire-choiceOrientation` | ✓ horizontal option layouts |
| `questionnaire-usageMode` | ✓ display-only items are skipped during capture |
| SDC `entryMode` | ✓ `sequential` disables back-navigation |
| `minValue`/`maxValue`/SDC `minQuantity`/`maxQuantity`, `maxDecimalPlaces`, `sliderStepValue` | ✓ |
| Grove `autocomplete` / `autocapitalize` | import only — parsed and honored when an authored instrument carries them; the Swift authoring API emits neither, so both are published without Must Support |
| Grove `annotate-image region` | import only — the region legend is read from an imported instrument; nothing writes it, so it too is published without Must Support |
| `entryFormat` (placeholder), Grove `validationText` | legacy only (`targetConstraint` carries authored messages natively) |

### Responses

| Aspect | Behavior |
|---|---|
| Structure | Mirrors the questionnaire: group wrappers (top-level wrappers carry the section title), child answers under `answer.item` |
| Answer types | Match the item type, including coded quantities with the participant-chosen unit |
| `item.text` | Question text carried on emitted items |
| Attribution | `subject`/`author`/`source` accepted at conversion; `questionnaireresponse-completionMode` always `electronic` |
| Lifecycle | Drafts with version pinning; `status` selectable (`in-progress` export for partial saves) |
| Skipped items | Omitted entirely; a fully empty response omits `item` |

### Native Swift authoring

Questionnaires can also be declared directly in Swift; the same model backs FHIR
import, and a Swift-declared instrument exports to a conformant FHIR R4
`Questionnaire`. The authoring API is documented with the Grove framework.

### Legacy (ResearchKit) path divergences

Deprecated; retained for existing apps. Known divergences (not being fixed): `prefix`
replaces question text, `check-box` implies multi-select regardless of `repeats`,
group-nested `enableWhen` targets do not fire, attachments are device-local file URLs,
and `reference`/`question` items render as free text (fixed output bugs are listed in
the [Change Log](changes.html)).
