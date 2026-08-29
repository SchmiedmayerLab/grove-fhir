<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This guide uses the actor names defined by Structured Data Capture:

| SDC actor | Responsibility in this guide |
|---|---|
| **Form Designer / Instrument Publisher** | Creates and distributes a Questionnaire. |
| **Form Filler / Response Producer** | Administers the Questionnaire and creates a QuestionnaireResponse. |
| **Form Receiver / Response Consumer** | Accepts and processes the QuestionnaireResponse. |

The guide defines resource content and cross-resource behavior; it does not define a REST API or transport workflow.
A CapabilityStatement describes a concrete deployment with known interactions, search parameters, authentication, and workflow, and is therefore outside this exchange contract.

### Must Support obligations

Must Support obligations depend on actor role:

| Actor | Obligation |
|---|---|
| Instrument or response producer | Populate the element when it applies and the source has the information. Do not invent data solely to satisfy a Must Support flag. |
| Form filler | Process supported Questionnaire elements according to this guide and preserve them when forwarding the resource, or reject the Questionnaire before administration. |
| Response consumer | Process supported QuestionnaireResponse elements according to this guide and preserve them when storing or forwarding the resource, or reject the response before acceptance. |

Silently discarding a behavior-changing condition, constraint, answer, hidden state, or identity is not conformant.

Must Support does not change cardinality.
An optional `0..1 MS` element remains optional. The inherited SDC Must Support flag on `QuestionnaireResponse.item.text` requires actors to handle and preserve the text when supplied; it does not require a producer to copy a Questionnaire prompt into the response.
Omission is conformant even when the exact Questionnaire is available.

### Individual resource validation

Run the official FHIR Validator against the declared Grove profile.
It checks base R4, SDC inheritance, cardinalities, datatypes, fixed values, extension structure, and the named invariants in this package.
The [quick start](quick-start.html#4-validate-each-resource) provides the complete package-based commands.

### Cross-resource validation

Individual profile validation cannot determine whether a response agrees with its referenced instrument.
After resolving `QuestionnaireResponse.questionnaire` to the exact Questionnaire version, use a checkout of the Grove FHIR Implementation Guides source corresponding to the package version and run the paired validator with every ValueSet required for answer or unit membership:

```sh
python3 Scripts/validate-questionnaire.py \
  --questionnaire questionnaire.json \
  --response questionnaire-response.json \
  --value-set referenced-valueset.json
```

The paired validator checks the following cross-resource rules:

1. exact canonical URL and version;
2. unique known `linkId` values in the expected hierarchy;
3. group children versus answer-context children;
4. answer datatype;
5. inline option and resolved, versioned ValueSet membership;
6. answer and group occurrence limits, including selection counts;
7. enabled and required items according to response status;
8. required Patient subject, authored time, and electronic completion metadata; and
9. unknown, duplicate, misplaced, or disabled items, and any entered-in-error response presented as usable answer data.

`QuestionnaireResponse.item.text` is optional presentation content and is deliberately not compared with the Questionnaire prompt.
The response `linkId`, hierarchy, and exact versioned Questionnaire canonical provide the machine contract across locales.

These are pair-level obligations: validators must resolve the exact Questionnaire named by `QuestionnaireResponse.questionnaire`; neither resource can establish them alone.

### External evaluation dependencies

The paired validator evaluates core `enableWhen` and deterministic answer constraints.
It is not a general-purpose FHIRPath evaluator or terminology service.
If a completed or amended response depends on expression-based enablement or an error-severity `targetConstraint`, the command reports `pair-expression-engine-required`.
The administration and acceptance workflow must supply conforming SDC FHIRPath evaluation before treating that response as complete.
An item-level constraint applies to an enabled response-item occurrence. It is not evaluated for an optional item that was omitted or for a disabled item, because no response-item context exists.
ValueSets with filters or imported ValueSets likewise require a terminology service or a complete expansion rather than guessed membership.

### Failure handling

Population and validation failures have different consequences:

- If `initialExpression` or another population expression cannot be evaluated, surface the failure and leave the answer blank; never substitute fabricated data.
  A population failure alone does not block completion, although ordinary rules such as `required` can still make the blank response invalid.
  Keeping the response `in-progress` permits later correction or completion in a more capable form filler.
- If enablement cannot be determined, a completed or amended response is blocked because required and disabled state is unknown.
- A failed error-severity `targetConstraint`, or an inability to evaluate it, blocks completion or amendment.
- A failed warning-severity constraint is shown to the user and recorded as appropriate, but does not block completion.
- `calculatedExpression` output is recomputed according to SDC rules and is not accepted as trustworthy merely because a response producer supplied a value.

### Dependencies and terminology notices

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
