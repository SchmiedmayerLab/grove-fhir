<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

What the native Grove questionnaire renderer does not support yet, in the order it
should be built. What *is* supported lives in the
[support matrix](questionnaire-support.html); recent additions are in the
[Change Log](changes.html).

### Remaining gaps

| Feature | Why it waits | Effort |
|---|---|---|
| Full `repeats` (repeating groups, repeated question instances) | Requires instance-indexed response paths through the whole model/UI/emission stack; planned together with the authoring-model evolution rather than bolted onto the current single-instance paths | large |
| `sdc-questionnaire-answerExpression` / `answerOptionsToggleExpression` | Dynamic option lists conflict with the static `ChoiceConfig` option model; needs the option model to become evaluation-aware | medium |
| `sdc-questionnaire-itemAnswerMedia` | Per-option media needs an option-row rendering slot; question-level `itemMedia` already renders | medium |
| `sdc-questionnaire-collapsible` | Sections-as-pages already chunk content on mobile; revisit with a disclosure grouping over `groupPath` | medium |
| `questionnaire-displayCategory` / `optionalDisplay` styling | Purely presentational; uniform instructional rendering is the documented fallback | small |
| Draft persistence for custom question kinds | `Draft` refuses custom response values rather than dropping them; needs a Codable bridge on `CustomResponseValueProtocol` | small |
| Accessibility audit of pre-existing controls | New controls shipped with labels; the legacy-era controls (slider, annotate-image, signature) still need a VoiceOver pass | medium |
| `questionnaire-signatureRequired` + QR `signature` | Attestation is typically Provenance at upload; GroveConsent covers consent signatures | medium |
| Observation-based population | Prefill-from-HealthKit is plausible study UX; expression-based population via `initialExpression` + `launchContext` already works | large |

### Out of scope (documented non-goals)

| Feature | Rationale |
|---|---|
| `item.type=reference` + `referenceResource`/`referenceProfile` | Presumes a queryable FHIR record store; failing conversion loudly is the right posture |
| `rendering-style` / `rendering-xhtml` / `sdc-questionnaire-width` | Web constructs with no clean SwiftUI mapping; styling injection is a content-trust concern (`styleSensitive` questionnaires surface a warning) |
| `candidateExpression` / StructureMap-based population | EHR-workflow oriented; no chart to draw candidates from |
| QR extraction (observation/definition/StructureMap-based) | Consumers receive the raw QR plus the source Questionnaire and extract downstream |
| `gtable`/`table` grid itemControls | Phone-width tables are an anti-pattern; SDC's stacked-layout fallback applies |
| Live terminology services (`preferredTerminologyServer`, server `$expand`) | Offline-first collection; ship contained or pre-expanded value sets (the external-ValueSet resolver covers app-bundled sets) |
| Adaptive questionnaires (`$next-question`) | Requires a live endpoint per answer, conflicting with offline-first collection |
| `text/cql` and `x-fhir-query` expressions | Fail conversion with a clear error; only `text/fhirpath` evaluates |
