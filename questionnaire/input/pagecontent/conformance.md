<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This contract uses the actor names defined by Structured Data Capture:

- a **Form Designer / Instrument Publisher** creates and distributes a Questionnaire;
- a **Form Filler / Response Producer** administers it and creates a
  QuestionnaireResponse; and
- a **Form Receiver / Response Consumer** accepts and processes the response.

The guide does not define a REST API. A CapabilityStatement belongs to a concrete server
deployment with known interactions, search parameters, authentication, and workflow.

### Must Support

For a producer, Must Support means populating the element when it applies and the source
has the information. Do not invent data to satisfy a Must Support flag.

For a consumer, Must Support means processing the element according to this guide,
preserving it when forwarding or storing the resource, or rejecting the resource before
administration or acceptance. Silently discarding a behavior-changing condition,
constraint, answer, hidden state, or identity is not conformant.

Must Support does not change cardinality. An optional `0..1 MS` element remains optional.
The inherited SDC Must Support flag on `QuestionnaireResponse.item.text` requires actors
to handle and preserve the text when supplied; it does not require a producer to copy a
Questionnaire prompt into the response. Omission is conformant even when the exact
Questionnaire is available.

### Resource validation

Run the official FHIR Validator against the declared Grove profile. It checks base R4,
SDC inheritance, cardinalities, datatypes, fixed values, extension structure, and the
named invariants in this package.

The repository wrapper uses the package built at `questionnaire/output/package.tgz`:

```sh
python3 Scripts/validate-questionnaire-fhir.py \
  --resource questionnaire.json \
  --resource questionnaire-response.json
```

The repository's static corpus also includes one-operation invalid mutations. The
wrapper submits each applicable case to the official Validator. The separate
`validator-expectations.json` manifest declares the complete error set for every case;
each observed error and each declared matcher must correspond one-to-one, so an extra
companion error cannot be hidden by the presence of the intended Grove rule.

### Paired validation

Then resolve `QuestionnaireResponse.questionnaire` and run:

```sh
python3 Scripts/validate-questionnaire.py \
  --questionnaire questionnaire.json \
  --response questionnaire-response.json \
  --value-set referenced-valueset.json
```

The paired validator checks:

1. exact canonical URL and version;
2. unique known `linkId` values in the expected hierarchy;
3. group children versus answer-context children;
4. answer datatype;
5. inline option and resolved, versioned ValueSet membership;
6. repeated-answer and selection-count limits;
7. enabled and required items according to response status; and
8. unknown, duplicate, misplaced, disabled, or entered-in-error content.

`QuestionnaireResponse.item.text` is optional presentation content and is deliberately
not compared with the Questionnaire prompt. The response `linkId`, hierarchy, and exact
versioned Questionnaire canonical provide the machine contract across locales.

These checks require both resources. The profile deliberately does not call `resolve()`
against an unspecified validation environment.

The paired validator evaluates core `enableWhen` and deterministic answer constraints.
It does not claim to be a general FHIRPath or terminology server. If a completed or
amended response depends on expression-based enablement or an error-severity
`targetConstraint`, the command reports `pair-expression-engine-required`; supply a
conforming SDC FHIRPath evaluation in the administration workflow. ValueSets with
filters or imported ValueSets likewise require a terminology service or a complete
expansion rather than guessed membership.

### Expression and failure behavior

Population and validation failures have different consequences:

- If `initialExpression` or another population expression cannot be evaluated, surface
  the failure and leave the answer blank; never substitute fabricated data. A population
  failure alone does not block completion, although ordinary rules such as `required`
  can still make the blank response invalid. Keeping the response `in-progress` permits
  later correction or completion in a more capable form filler.
- If enablement cannot be determined, a completed or amended response is blocked because
  required and disabled state is unknown.
- A failed error-severity `targetConstraint`, or an inability to evaluate it, blocks
  completion or amendment.
- A failed warning-severity constraint is shown to the user and recorded as appropriate,
  but does not block completion.
- `calculatedExpression` output is recomputed according to SDC rules and is not accepted
  as trustworthy merely because a client supplied a value.

### Test corpus

The non-published fixtures under `questionnaire/fixtures` cover valid resources and one
mutation per invalid case. The static corpus includes SemVer, version algorithm,
reference answers, repeats, condition forms, variables, expression shape, root and item
target constraints, initial values, completion mode, canonical form, response identity
and optional presentation text, extension placement, and bound relationships.

The paired corpus covers exact canonical resolution, Questionnaire `subjectType` versus
response `subject` across relative, absolute, versioned, contained, and typed logical
references (including rejection of unrecognized declared-type URIs), hierarchy, datatype, inline and versioned
ValueSet membership, locale-neutral optional text, repeats and limits, status-aware
required items, and unknown, duplicate, misplaced, and disabled items. Each invalid case declares the
stable expected rule, and the tests require that rule to be the complete local error
set. The `Conformance/corpora` live-FSH inventory references both Questionnaire-owned
manifests by corpus ID and ownership; it does not copy or redefine their cases.

### Dependencies and terminology notices

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
