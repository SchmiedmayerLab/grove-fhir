<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A [Grove Study Questionnaire Task](StructureDefinition-grove-study-questionnaire-task.html) is one assigned occurrence: one participant, in one enrollment, is asked to complete one component revision once, within one performance window.
A recurring schedule is assigned as many Tasks, one per occurrence.

### Task elements

| Element | Content |
|---|---|
| `identifier` | The occurrence identifier, with `system` and `value` |
| `instantiatesCanonical` | The exact `url|version` of the component revision |
| `status` | `ready`, `completed`, or `cancelled`, as [Outcomes](outcomes.html) defines |
| `statusReason` | Only on a cancelled Task, where the reason changes how it counts |
| `intent` | `order` |
| `code` | `complete-questionnaire` from the Structured Data Capture code system |
| `for` | The participant's Patient, by its complete identifier |
| `authoredOn` | When the occurrence was assigned |
| `lastModified` | When the status or the result link last changed |
| `executionPeriod` | When the participant actually worked on the occurrence, where known |
| `input` | Exactly the four inputs below |
| `output[result]` | The accepted result, as [Link the result](results.html) defines |

### Inputs

Each input is identified by its `type` coding.
The input slicing is closed: a Task carries exactly these four inputs, once each.

| Input | `type` | Value |
|---|---|---|
| `performanceWindow` | `performance-window` from [Grove Study Task Parameter](CodeSystem-grove-study-task-parameter.html) | `valuePeriod` with `start` and `end`, each with seconds and a time-zone offset, and `start` before `end` |
| `enrollment` | `enrollment` from Grove Study Task Parameter | `valueReference` to the ResearchSubject with its complete `identifier`; a literal reference may accompany it |
| `protocol` | `protocol` from Grove Study Task Parameter | `valueCanonical` with the exact `url|version` of the protocol revision whose action assigned the occurrence |
| `questionnaire` | `questionnaire` from `http://hl7.org/fhir/uv/sdc/CodeSystem/temp` | `valueCanonical` with the exact `url|version` of the instrument, equal to the instrument the component revision pins |

The questionnaire input repeats the instrument of the component revision so a receiver can check a response against the Task alone.

The performance window states when the participant is allowed to perform the occurrence.
Its `end` is the last instant at which answers can be gathered for this occurrence.
`executionPeriod` records actual work and never changes the window.
R4 `Task.restriction` is not used: R4 defines it for a Task that fulfills a request named in `focus`, and an occurrence has no such request.

### Occurrence identity

The occurrence identifier is a complete `(system, value)` pair.
The assigning application chooses the system, assigns the value once, and treats the value as opaque.

The identifier names exactly one occurrence, scoped to one enrollment and one component revision.
The facts it was assigned with never change under it:

- the participant in `for`;
- the enrollment identifier;
- the component revision in `instantiatesCanonical`;
- the protocol revision and the instrument;
- the performance window; and
- `authoredOn`.

Every retransmission of an occurrence preserves its identifier and these facts exactly as first sent; the same instant written with another offset is a different fact.
A Task with a known identifier and different assignment facts is a conflicting reuse of the identifier and is rejected.
Status changes and the result link are the only changes an occurrence admits; [Outcomes](outcomes.html) lists the allowed transitions.

Two occurrences with the same component revision and the same window, such as two check-ins assigned for the same time, have different identifiers and remain two occurrences.
A later enrollment of the same participant is a different ResearchSubject with its own identifier, and occurrences assigned under it have new occurrence identifiers even when their component revision and window match an earlier occurrence.
Adopting a new protocol revision affects only occurrences assigned afterwards; assigned occurrences keep their component revision.

`Resource.id` and `meta.versionId` identify a stored copy of the Task.
Neither replaces the occurrence identifier.

### Example

The [assigned occurrence](Task-GroveStudyAssignedTaskExample.html) and the [completed occurrence](Task-GroveStudyCompletedTaskExample.html) are two days of the same component revision in the same enrollment, each with its own identifier and window.
