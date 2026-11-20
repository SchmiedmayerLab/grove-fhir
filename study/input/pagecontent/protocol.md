<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A study publishes its protocol as revisions.
A protocol revision names the exact component revisions it assigns, and a questionnaire component revision names the exact instrument revision it administers.
Nothing in this chain resolves to "the latest" revision.

### Protocol revision

A [Grove Study Protocol](StructureDefinition-grove-study-protocol.html) is a PlanDefinition with a canonical `url` and a `version`.
Each published `url|version` is one protocol revision and is never changed after publication; a changed protocol is a new version.

Every `action` names one component revision of any kind in `action.definitionCanonical` as an exact `url|version` of a [Grove Study Activity](StructureDefinition-grove-study-activity.html) or a profile derived from it.
This guide does not define when or how often an action assigns occurrences; it exchanges the occurrences the assigning application assigns.

A single-arm protocol lists its actions without arm selection.
Arm allocation is outside this guide.

The [example protocol](PlanDefinition-GroveStudyProtocolExample.html) has two actions: an informational welcome component and the daily check-in questionnaire component.

### Component revision

A [Grove Study Activity](StructureDefinition-grove-study-activity.html) is an ActivityDefinition for one study component of any kind, such as a questionnaire or an informational message.
Its `url` identifies the component and its `version` identifies one immutable revision of it.

| Element | Value |
|---|---|
| `url` | The canonical URL of the component, without a version separator |
| `version` | The component revision |
| `kind` | `Task`: each occurrence of the component is assigned as a Task |
| `intent` | `order` |

Every artifact a component revision names with the `relatedArtifact` type `depends-on` is an exact `url|version`.
A component of a kind that defines no result, such as an informational message, conforms to this profile and needs nothing more; the [welcome component](ActivityDefinition-GroveStudyWelcomeActivityExample.html) is an example.

### Questionnaire component revision

A [Grove Study Questionnaire Activity](StructureDefinition-grove-study-questionnaire-activity.html) derives from Grove Study Activity for a component that asks the participant to complete a Questionnaire.
It adds:

| Element | Value |
|---|---|
| `code` | `complete-questionnaire` from the Structured Data Capture code system `http://hl7.org/fhir/uv/sdc/CodeSystem/temp` |
| `relatedArtifact[instrument]` | The one `depends-on` artifact; its `resource` is the exact `url|version` of a [Grove Questionnaire](https://grovealliance.org/fhir/questionnaire/StructureDefinition-grove-questionnaire.html) |

The `complete-questionnaire` code identifies a questionnaire component: [graph validation](conformance.html#graph-validation) applies the questionnaire rules to every occurrence of a component revision with this code, and to every Task with this code.
A component revision pins one instrument revision.
Administering a different Questionnaire version is a new component revision, and a protocol that adopts it is a new protocol revision.
Occurrences already assigned keep the component revision they were assigned with.

The [daily check-in component](ActivityDefinition-GroveStudyDailyCheckInActivityExample.html) pins the [daily check-in instrument](Questionnaire-GroveStudyDailyCheckInExample.html).

### Revision identifiers

Protocol and component versions are compared as exact strings, and this guide imposes no version syntax on them.
The instrument follows the Questionnaire Exchange, which requires a Semantic Versioning `version`.
`Resource.id` and `meta.versionId` identify a stored copy and never stand in for a canonical `url|version`.
