<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A study publishes its protocol as revisions.
A protocol revision names the exact component revisions it assigns, and each component revision names the exact instrument revision it administers.
Nothing in this chain resolves to "the latest" revision.

### Protocol revision

A [Grove Study Protocol](StructureDefinition-grove-study-protocol.html) is a PlanDefinition with a canonical `url` and a `version`.
Each published `url|version` is one protocol revision and is never changed after publication; a changed protocol is a new version.

Every `action` names one component revision in `action.definitionCanonical` as an exact `url|version`.
`action.timing[x]` can describe when the action assigns occurrences, such as once per day.
The assigning application evaluates that timing into occurrences; this guide exchanges the occurrences and does not define how recurrence is evaluated.

A single-arm protocol lists its actions without arm selection.
Arm allocation is outside this guide.

The [example protocol](PlanDefinition-GroveStudyProtocolExample.html) has one action that assigns the daily check-in component once per day.

### Component revision

A [Grove Study Questionnaire Activity](StructureDefinition-grove-study-questionnaire-activity.html) is an ActivityDefinition for one study component that asks the participant to complete a Questionnaire.
Its `url` identifies the component and its `version` identifies one immutable revision of it.

| Element | Value |
|---|---|
| `kind` | `Task`: the component is assigned as a Task |
| `intent` | `order` |
| `code` | `complete-questionnaire` from the Structured Data Capture code system `http://hl7.org/fhir/uv/sdc/CodeSystem/temp` |
| `relatedArtifact[instrument]` | The one `depends-on` artifact; its `resource` is the exact `url|version` of a [Grove Questionnaire](https://grovealliance.org/fhir/questionnaire/StructureDefinition-grove-questionnaire.html) |

A component revision pins one instrument revision.
Administering a different Questionnaire version is a new component revision, and a protocol that adopts it is a new protocol revision.
Occurrences already assigned keep the component revision they were assigned with.

The [example component](ActivityDefinition-GroveStudyDailyCheckInActivityExample.html) pins the [daily check-in instrument](Questionnaire-GroveStudyDailyCheckInExample.html).

### Revision identifiers

Protocol and component versions are compared as exact strings, and this guide imposes no version syntax on them.
The instrument follows the Questionnaire Exchange, which requires a Semantic Versioning `version`.
`Resource.id` and `meta.versionId` identify a stored copy and never stand in for a canonical `url|version`.
