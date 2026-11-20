<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Study Interaction Exchange defines how a published study protocol, the task occurrences it assigns to a participant, and the questionnaire responses that complete them are exchanged as FHIR R4.
It uses standard resources:

- a `PlanDefinition` is one published revision of the study protocol;
- an `ActivityDefinition` is one immutable revision of a study component, such as a daily check-in, and pins the exact instrument it administers;
- a `Task` is one assigned occurrence of a component for one participant in one enrollment;
- a `QuestionnaireResponse` is the result that completes an occurrence, profiled by the [Questionnaire Exchange](https://grovealliance.org/fhir/questionnaire/); and
- a `ResearchSubject` is the participant's enrollment.

Readers who are new to FHIR should begin with the [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.

### Resource graph

Every link between definitions is an exact `url|version` canonical, and the result link names one exact version of the response:

```text
PlanDefinition url|version (protocol revision)
  action.definitionCanonical ----> ActivityDefinition url|version (component revision)
                                     relatedArtifact[instrument] ----> Questionnaire url|version

Task (one occurrence)
  identifier                       occurrence identifier
  instantiatesCanonical ---------> ActivityDefinition url|version
  input[protocol] ---------------> PlanDefinition url|version
  input[questionnaire] ----------> Questionnaire url|version
  input[enrollment] -------------> ResearchSubject, by identifier
  input[performanceWindow]         Period in which the occurrence may be performed
  for ---------------------------> Patient, by identifier
  output[result] ----------------> QuestionnaireResponse/<id>/_history/<versionId>

QuestionnaireResponse
  questionnaire                    Questionnaire url|version
  subject -----------------------> Patient
```

The QuestionnaireResponse does not point back to the Task.
`QuestionnaireResponse.partOf` is never used for this link.

### Scope

The guide defines resource content and the rules that join the resources.
It does not define a REST API, how recurrence is evaluated into occurrences, synchronization cursors, quotas, arm allocation, or conversations.
The Mobile exchange Bundle and its resource whitelist are unchanged: Task and ActivityDefinition are not Mobile exchange entries.
Exchange these resources as individual resources, in a FHIR `collection` Bundle, or through any other transport.

### Adoption

Any application that assigns questionnaire tasks to study participants can adopt this exchange.
It needs this package and the Questionnaire Exchange package it depends on.
It does not need a particular study platform, conversation profiles, arm allocation, or a FHIR REST server: the resources can be produced, stored, and validated as files.
Both validation stages described on the [conformance page](conformance.html) run offline on those files.

### Examples

| Resource | What to look for |
|---|---|
| [Single-arm daily check-in protocol](PlanDefinition-GroveStudyProtocolExample.html) | One action that names the exact component revision and assigns it daily |
| [Daily check-in component](ActivityDefinition-GroveStudyDailyCheckInActivityExample.html) | The component revision and the exact instrument it pins |
| [Daily check-in instrument](Questionnaire-GroveStudyDailyCheckInExample.html) | The Grove Questionnaire the participant completes |
| [Enrollment](ResearchSubject-GroveStudyEnrollmentExample.html) | The ResearchSubject the occurrences name by identifier |
| [Assigned occurrence](Task-GroveStudyAssignedTaskExample.html) | A `ready` Task with its performance window and no result |
| [Completed occurrence](Task-GroveStudyCompletedTaskExample.html) | A `completed` Task with its version-specific result link |
| [Excused occurrence](Task-GroveStudyExcusedTaskExample.html) | A `cancelled` Task with the `excused` status reason |
| [Accepted response](QuestionnaireResponse-GroveStudyDailyCheckInResponseExample.html) | The response the completed occurrence links |

### Guide navigation

- [Publish the protocol](protocol.html) covers protocol and component revisions and how they pin the instrument.
- [Assign an occurrence](occurrences.html) defines the Task, its inputs, and occurrence identity.
- [Link the result](results.html) defines how an accepted response, and a correction of it, is linked to its occurrence.
- [Outcomes](outcomes.html) maps the assignment states to Task statuses and defines the projection to completed, missed, cancelled, and excused outcomes.
- [Conformance](conformance.html) defines structural validation and graph validation and what each one establishes.
- [Artifacts](artifacts.html) lists the profiles, terminology, and examples.
