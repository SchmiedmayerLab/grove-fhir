<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

This guide names two actors:

| Actor | Responsibility |
|---|---|
| **Assigning application** | Publishes protocol and component revisions, assigns occurrences, accepts results, and produces the Tasks. |
| **Receiving application** | Accepts Tasks and their results, keeps the accepted state of each occurrence, and reports outcomes. |

One application can hold both roles.
The guide defines resource content and the rules that join resources; it does not define a REST API or a transport workflow.

### Must Support obligations

A producer populates a Must Support element when it applies and the information is known; it does not invent data to satisfy the flag.
A consumer processes Must Support elements according to this guide and preserves them when it stores or forwards the resource, or rejects the resource.
Must Support does not change cardinality.

### Two validation stages

Accepting a Task and its result takes two stages.
A resource can pass the first and still form a graph the second rejects.

#### Structural validation

Run the official FHIR Validator against each resource with this package and the Questionnaire Exchange package.
It checks base R4 and the Grove profiles of each resource on its own:

- cardinalities, fixed values, and the input and output slicing, which the questionnaire profiles close;
- the required status and status-reason bindings;
- exact `url|version` syntax of the component, protocol, and instrument canonicals (`grove-study-task-pinned-1`, `grove-study-protocol-pinned-1`, `grove-study-activity-pinned-1`);
- a performance window with offsets that starts before it ends (`grove-study-task-window-1`);
- an output on a completed Task only (`grove-study-task-output-1`) and a status reason on a cancelled Task only (`grove-study-task-status-reason-1`); and
- for a questionnaire Task, a result link on every completed Task (`grove-study-questionnaire-task-completed-1`) that is a version-specific reference (`grove-study-questionnaire-task-result-1`).

A Task that claims only the base profile passes structural validation without the questionnaire rules.
Graph validation applies them to every occurrence of a questionnaire component.

#### Graph validation

Structural validation sees one resource at a time.
It cannot tell whether a Task's subject, instrument, and result agree, whether its definitions exist, or whether an occurrence identifier was used before.
Graph validation resolves the Task against the definitions and the response it links, and against the occurrences already accepted.

These rules apply to every occurrence:

| Rule | Rejects |
|---|---|
| `study-task-definition` | A component revision that resolves to no ActivityDefinition, or to more than one |
| `study-task-protocol` | A protocol revision that resolves to no PlanDefinition, or whose actions do not name the Task's component revision |
| `study-task-enrollment` | An enrollment identifier that resolves to no ResearchSubject, or to one for another participant |
| `study-task-duplicate-occurrence` | Two Tasks with one occurrence identifier in one delivery |
| `study-task-cancelled-after-window` | A cancelled Task last modified after its window ended |
| `study-task-output` | An output on an occurrence whose component defines no result in this guide |
| `study-task-completion-window` | A completed occurrence whose component defines no result, last modified outside its performance window |
| `study-task-occurrence-conflict` | A known occurrence identifier with different assignment facts |
| `study-task-status-transition` | A transition [Outcomes](outcomes.html) does not allow |
| `study-task-altered-replay` | A known occurrence repeated with its accepted status and output but different content |

An occurrence is a questionnaire occurrence when its component revision or the Task has the code `complete-questionnaire`.
These rules apply to the questionnaire input, and to every questionnaire occurrence and the response it links:

| Rule | Rejects |
|---|---|
| `study-task-instrument` | A questionnaire occurrence whose questionnaire input is missing, differs from the instrument the component revision pins, or resolves to no Questionnaire, and a questionnaire input on any other occurrence |
| `study-task-result-reference` | A completed Task without a result link, or with one that resolves to no response version in the delivery |
| `study-task-result-subject` | A linked response about another participant |
| `study-task-result-instrument` | A linked response to another instrument or another instrument version |
| `study-task-result-status` | A linked response that is not `completed` or `amended`, such as a pending response presented as a completion, or an `amended` response as the first accepted result |
| `study-task-result-window` | A linked `completed` response authored outside the performance window, or an `amended` one authored before it opened |
| `study-task-result-part-of` | A response whose `partOf` references a Task |
| `study-task-result-shared` | One response linked by two occurrences |
| `study-task-altered-result` | An accepted response version repeated with different content |
| `study-task-completion-conflict` | A completed occurrence linked to a response with another submission identifier |
| `study-task-correction` | A changed result link to a new version that does not carry the status `amended`, that names another response resource, or that is authored before the version it corrects |

Every linked response is also checked against its exact instrument with the paired Questionnaire validator, whose `pair-*` rules apply unchanged.
An exact replay of an accepted occurrence is accepted again without a change.

Graph validation needs the definitions the Tasks name.
In a checkout of the Grove FHIR Implementation Guides source corresponding to the package version, pass the protocol, component, instrument, and enrollment resources as a FHIR Bundle, followed by the deliveries in the order they arrived:

```sh
python3 Scripts/validate-study-graph.py \
  --definitions definitions.json \
  delivery-1.json delivery-2.json
```

Each delivery is a FHIR Bundle or a single Task; a completed Task travels in a Bundle with the response it links.
A delivery can carry definitions as well. A definition the receiver also holds must be identical, and two copies that differ resolve to nothing.
The command reports, for each delivery, the outcome of every occurrence it carries or the rules that rejected it, and keeps the accepted state of each occurrence for the deliveries after it.
A rejected delivery changes no state.

### Validation limits

Neither stage establishes that the sender may assign the occurrence or submit the result, that the participant consented or remains eligible, that the participant personally answered, or that the answers are scientifically valid.
The receiving application decides permission, consent, eligibility, and acceptance policy, such as how late a result may arrive, from its own records.

### Conformance fixtures

The source repository's [`study/fixtures`](https://github.com/SchmiedmayerLab/grove-fhir/tree/main/study/fixtures) directory holds the shared fixtures.
The graph fixtures are a single-arm protocol with an informational welcome component and a daily check-in questionnaire, its definitions, and a sequence of deliveries per case: an assigned and then completed occurrence, an exact replay, a conflicting reuse of an occurrence identifier, two occurrences at the same time, a re-enrollment, a corrected result, an informational occurrence completed without an output and one completed after its window, and Tasks that are structurally valid but name another participant, another instrument version, a pending response, a result reference that does not resolve, or complete a questionnaire occurrence without a result.
Every graph fixture passes structural validation, and the expected graph outcome of each case is recorded beside it.
The structural fixtures are a valid questionnaire Task and questionnaire Tasks the official FHIR Validator rejects for one named reason each, including a pending status and invalid window and status mappings.

### Dependencies and terminology notices

{% include dependency-table-nontech.xhtml %}

{% include ip-statements.xhtml %}
