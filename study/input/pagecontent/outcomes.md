<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

`Task.status` records the state of the assignment.
Study outcomes such as missed and excused are derived from the status, the status reason, and the performance window by the projection below, without additional R4 status codes or extensions.

### Status mapping

| Assignment state | `Task.status` | Result link |
|---|---|---|
| Assigned | `ready` | none |
| Accepted completion | `completed` | exactly one |
| Stopped assignment | `cancelled` | none |

The [Grove Study Task Status](ValueSet-grove-study-task-status.html) value set binds these three codes; every other R4 Task status is rejected.
A local pending completion is not an accepted transition: an occurrence whose response is in progress, or whose completion awaits acceptance, stays `ready`.

The allowed transitions are:

| From | To | Meaning |
|---|---|---|
| `ready` | `completed` | One result was accepted |
| `ready` | `cancelled` | The assignment was stopped |
| `completed` | `completed` | A correction changed the result link to a new version of the same response |

A `completed` or `cancelled` occurrence never returns to `ready`, and a `cancelled` occurrence is final.
A first transmission may already carry `completed` or `cancelled`.

### Status reason

Only a cancelled Task carries `statusReason`.
Its coding comes from the [Grove Study Task Status Reason](ValueSet-grove-study-task-status-reason.html) value set, which has one code:

| Code | Meaning |
|---|---|
| `excused` | The study released the participant from this occurrence |

A cancelled Task without a status reason is a cancelled occurrence.

Stop an occurrence before its window ends.
A cancelled Task's `lastModified` is at or before the end of its performance window, so cancelling an occurrence that already lapsed cannot remove it from the missed count.

### Outcome projection

A consumer that reports outcomes evaluates each Task at one stated projection instant `T`:

| Outcome | Task |
|---|---|
| completed | `status` is `completed` |
| excused | `status` is `cancelled` and `statusReason` is `excused` |
| cancelled | `status` is `cancelled` without a status reason |
| missed | `status` is `ready` and the performance window ended at or before `T` |
| open | `status` is `ready` and the performance window ends after `T` |

Each occurrence has exactly one outcome at `T`.
Comparisons use the instants the window's time-zone offsets denote.
A report states `T` beside its outcomes, because a `ready` occurrence moves from open to missed as `T` passes its window end.

The [excused occurrence](Task-GroveStudyExcusedTaskExample.html) was cancelled with the `excused` reason before its window opened.
