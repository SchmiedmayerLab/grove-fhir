<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

The Grove Study Interaction Exchange defines how a published study protocol, the occurrences of study components it assigns to a participant, and the questionnaire responses that complete questionnaire occurrences are exchanged as FHIR R4.
This package is experimental.

It uses standard resources:

- a `PlanDefinition` is one published revision of the study protocol;
- an `ActivityDefinition` is one immutable revision of a study component, such as a daily check-in questionnaire or an informational message;
- a `Task` is one assigned occurrence of a component for one participant in one enrollment;
- a `QuestionnaireResponse` is the result that completes a questionnaire occurrence, profiled by the [Questionnaire Exchange](https://grovealliance.org/fhir/questionnaire/); and
- a `ResearchSubject` is the participant's enrollment.

Readers who are new to FHIR should begin with the [FHIR basics page](https://grovealliance.org/fhir/mobile/fhir-basics.html) in the Mobile guide.

### Profiles

Two base profiles carry what every component and every occurrence share, whatever the component asks the participant to do.
Each component kind that defines more derives its own profiles from them.
This guide defines one such kind, the questionnaire.

| Base profile | Questionnaire profile derived from it |
|---|---|
| [Grove Study Activity](StructureDefinition-grove-study-activity.html): one component revision | [Grove Study Questionnaire Activity](StructureDefinition-grove-study-questionnaire-activity.html): adds the instrument the component administers |
| [Grove Study Task](StructureDefinition-grove-study-task.html): one assigned occurrence | [Grove Study Questionnaire Task](StructureDefinition-grove-study-questionnaire-task.html): adds the questionnaire input and the result link |

The [Grove Study Protocol](StructureDefinition-grove-study-protocol.html) names component revisions of any kind.
A component of a kind without a result, such as an informational message, uses the base profiles, and its completed occurrences carry no output.

### Resource graph

Every link between definitions is an exact `url|version` canonical, and the result link names one exact version of the response:

```text
PlanDefinition url|version (protocol revision)
  action.definitionCanonical ----> ActivityDefinition url|version (component revision)
                                     relatedArtifact[instrument] ----> Questionnaire url|version
                                     (questionnaire components only)

Task (one occurrence)
  identifier                       occurrence identifier
  instantiatesCanonical ---------> ActivityDefinition url|version
  input[protocol] ---------------> PlanDefinition url|version
  input[enrollment] -------------> ResearchSubject, by identifier
  input[performanceWindow]         Period in which the occurrence may be performed
  for ---------------------------> Patient, by identifier
  input[questionnaire] ----------> Questionnaire url|version (questionnaire occurrences only)
  output[result] ----------------> QuestionnaireResponse/<id>/_history/<versionId>
                                   (completed questionnaire occurrences only)

QuestionnaireResponse
  questionnaire                    Questionnaire url|version
  subject -----------------------> Patient
```

The QuestionnaireResponse does not point back to the Task.
`QuestionnaireResponse.partOf` is never used for this link.

### Scope

The guide defines resource content and the rules that join the resources.
It does not define a REST API, when or how often a protocol assigns occurrences, synchronization cursors, quotas, arm allocation, or conversations.
The Mobile exchange Bundle and its resource whitelist are unchanged: Task and ActivityDefinition are not Mobile exchange entries.
Exchange these resources as individual resources, in a FHIR `collection` Bundle, or through any other transport.

### Adoption

Any application that assigns study components to participants can adopt this exchange.
It needs this package and the Questionnaire Exchange package it depends on.
It does not need a particular study platform, conversation profiles, arm allocation, or a FHIR REST server: the resources can be produced, stored, and validated as files.
Both validation stages described on the [conformance page](conformance.html) run offline on those files.

### Examples

| Resource | What to look for |
|---|---|
| [Single-arm protocol](PlanDefinition-GroveStudyProtocolExample.html) | Two actions, each naming the exact revision of the component it assigns |
| [Welcome component](ActivityDefinition-GroveStudyWelcomeActivityExample.html) | An informational component revision that conforms to the base activity profile |
| [Daily check-in component](ActivityDefinition-GroveStudyDailyCheckInActivityExample.html) | A questionnaire component revision and the exact instrument it pins |
| [Daily check-in instrument](Questionnaire-GroveStudyDailyCheckInExample.html) | The Grove Questionnaire the participant completes |
| [Enrollment](ResearchSubject-GroveStudyEnrollmentExample.html) | The ResearchSubject the occurrences name by identifier |
| [Completed informational occurrence](Task-GroveStudyWelcomeTaskExample.html) | A `completed` base Task without an output |
| [Assigned occurrence](Task-GroveStudyAssignedTaskExample.html) | A `ready` questionnaire Task with its performance window and no result |
| [Completed occurrence](Task-GroveStudyCompletedTaskExample.html) | A `completed` questionnaire Task with its version-specific result link |
| [Excused occurrence](Task-GroveStudyExcusedTaskExample.html) | A `cancelled` questionnaire Task with the `excused` status reason |
| [Accepted response](QuestionnaireResponse-GroveStudyDailyCheckInResponseExample.html) | The response the completed occurrence links |

### Guide navigation

- [Publish the protocol](protocol.html) covers protocol and component revisions and how a questionnaire component pins its instrument.
- [Assign an occurrence](occurrences.html) defines the base Task, the questionnaire Task, their inputs, and occurrence identity.
- [Link the result](results.html) defines how an accepted response, and a correction of it, is linked to its questionnaire occurrence.
- [Outcomes](outcomes.html) maps the assignment states to Task statuses and defines the projection to completed, missed, cancelled, and excused outcomes.
- [Conformance](conformance.html) defines structural validation and graph validation and what each one establishes.
- [Artifacts](artifacts.html) lists the profiles, terminology, and examples.
