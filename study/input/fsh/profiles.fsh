//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: grove-study-protocol-pinned-1
Description: "The protocol has an absolute canonical url without a version separator, and every action definition names one exact url|version."
Severity: #error
Expression: "url.matches('^https?://[^\\\\s|#]+$') and repeat(action).definition.ofType(canonical).all(matches('^https?://[^\\\\s|#]+[|][^\\\\s|#]+$'))"

Invariant: grove-study-activity-pinned-1
Description: "The activity has an absolute canonical url without a version separator, and its instrument names one exact Questionnaire url|version."
Severity: #error
Expression: "url.matches('^https?://[^\\\\s|#]+$') and relatedArtifact.where(type = 'depends-on').resource.all(matches('^https?://[^\\\\s|#]+[|][^\\\\s|#]+$'))"

Invariant: grove-study-task-pinned-1
Description: "instantiatesCanonical and the protocol and questionnaire inputs each name one exact url|version."
Severity: #error
Expression: "instantiatesCanonical.all(matches('^https?://[^\\\\s|#]+[|][^\\\\s|#]+$')) and input.value.ofType(canonical).all(matches('^https?://[^\\\\s|#]+[|][^\\\\s|#]+$'))"

Invariant: grove-study-task-window-1
Description: "The performance window has a start and an end, each with seconds and a time-zone offset, and it starts before it ends."
Severity: #error
Expression: "input.value.ofType(Period).all(start.exists() and end.exists() and start.toString().matches('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$') and end.toString().matches('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$') and start < end)"

Invariant: grove-study-task-status-1
Description: "A completed Task links exactly one result; a ready or cancelled Task links none."
Severity: #error
Expression: "iif(status = 'completed', output.count() = 1, output.empty())"

Invariant: grove-study-task-status-reason-1
Description: "Only a cancelled Task carries a status reason."
Severity: #error
Expression: "statusReason.empty() or status = 'cancelled'"

Invariant: grove-study-task-result-1
Description: "The result is a version-specific literal reference to a QuestionnaireResponse."
Severity: #error
Expression: "output.value.ofType(Reference).all(reference.matches('^(https?://[^\\\\s|#]+/)?QuestionnaireResponse/[A-Za-z0-9.-]{1,64}/_history/[A-Za-z0-9.-]{1,64}$'))"

Profile: GroveStudyProtocol
Parent: PlanDefinition
Id: grove-study-protocol
Title: "Grove Study Protocol"
Description: "One published revision of a study protocol. Each action names the exact revision of the study component it assigns."
* obeys grove-study-protocol-pinned-1
* url 1..1 MS
* version 1..1 MS
* version ^short = "Protocol revision; a published revision is never changed"
* status 1..1 MS
* action 1..* MS
* action.title MS
* action.definition[x] 1..1 MS
* action.definition[x] only Canonical(ActivityDefinition)
* action.definition[x] ^short = "Exact url|version of the ActivityDefinition this action assigns"
* action.timing[x] MS
* action.timing[x] ^short = "When the action assigns occurrences; recurrence is evaluated by the assigning application"

Profile: GroveStudyQuestionnaireActivity
Parent: ActivityDefinition
Id: grove-study-questionnaire-activity
Title: "Grove Study Questionnaire Activity"
Description: "One immutable revision of a study component that asks the participant to complete one exact Questionnaire version."
* obeys grove-study-activity-pinned-1
* url 1..1 MS
* url ^short = "Canonical URL of the study component"
* version 1..1 MS
* version ^short = "Component revision; a published revision is never changed"
* status 1..1 MS
* kind 1..1 MS
* kind = #Task (exactly)
* intent 1..1 MS
* intent = #order (exactly)
* code 1..1 MS
* code = $sdcTemp#complete-questionnaire
* relatedArtifact ^slicing.discriminator.type = #value
* relatedArtifact ^slicing.discriminator.path = "type"
* relatedArtifact ^slicing.rules = #open
* relatedArtifact ^slicing.description = "The instrument is the one artifact this activity depends on."
* relatedArtifact contains instrument 1..1 MS
* relatedArtifact[instrument].type = #depends-on (exactly)
* relatedArtifact[instrument].resource 1..1 MS
* relatedArtifact[instrument].resource only Canonical($GroveQuestionnaire)
* relatedArtifact[instrument].resource ^short = "Exact url|version of the Questionnaire the participant completes"

Profile: GroveStudyQuestionnaireTask
Parent: Task
Id: grove-study-questionnaire-task
Title: "Grove Study Questionnaire Task"
Description: "One assigned occurrence of a study component that the participant completes with one exact Questionnaire version. A recurring schedule is assigned as one Task per occurrence."
* obeys grove-study-task-pinned-1 and grove-study-task-window-1 and grove-study-task-status-1 and grove-study-task-status-reason-1 and grove-study-task-result-1
* identifier 1..1 MS
* identifier ^short = "Occurrence identifier; assigned once and preserved on every retransmission"
* identifier.system 1..1 MS
* identifier.value 1..1 MS
* instantiatesCanonical 1..1 MS
* instantiatesCanonical only Canonical(GroveStudyQuestionnaireActivity)
* instantiatesCanonical ^short = "Exact url|version of the component revision this occurrence belongs to"
* status 1..1 MS
* status from GroveStudyTaskStatusVS (required)
* status ^short = "ready | completed | cancelled"
* statusReason MS
* statusReason from GroveStudyTaskStatusReasonVS (required)
* statusReason.coding 1..1 MS
* statusReason ^short = "Why a cancelled occurrence was stopped, where that changes how it counts"
* intent 1..1 MS
* intent = #order (exactly)
* code 1..1 MS
* code = $sdcTemp#complete-questionnaire
* for 1..1 MS
* for only Reference(Patient)
* for ^short = "The participant"
* for.identifier 1..1 MS
* for.identifier.system 1..1 MS
* for.identifier.value 1..1 MS
* authoredOn 1..1 MS
* authoredOn ^short = "When the occurrence was assigned"
* lastModified 1..1 MS
* lastModified ^short = "When the status or result link last changed"
* executionPeriod MS
* executionPeriod ^short = "When the participant actually worked on the occurrence"
* input 4..4 MS
* input ^slicing.discriminator.type = #value
* input ^slicing.discriminator.path = "type"
* input ^slicing.rules = #closed
* input ^slicing.description = "Each input places the occurrence in its study context."
* input contains
    performanceWindow 1..1 MS and
    enrollment 1..1 MS and
    protocol 1..1 MS and
    questionnaire 1..1 MS
* input[performanceWindow].type = GroveStudyTaskParameterCS#performance-window
* input[performanceWindow].value[x] only Period
* input[performanceWindow].value[x] ^short = "When the participant is allowed to perform the occurrence"
* input[enrollment].type = GroveStudyTaskParameterCS#enrollment
* input[enrollment].value[x] only Reference(ResearchSubject)
* input[enrollment].valueReference.identifier 1..1 MS
* input[enrollment].valueReference.identifier.system 1..1 MS
* input[enrollment].valueReference.identifier.value 1..1 MS
* input[enrollment].value[x] ^short = "The ResearchSubject, by its complete business identifier"
* input[protocol].type = GroveStudyTaskParameterCS#protocol
* input[protocol].value[x] only Canonical(GroveStudyProtocol)
* input[protocol].value[x] ^short = "Exact url|version of the protocol whose action assigned the occurrence"
* input[questionnaire].type = $sdcTemp#questionnaire
* input[questionnaire].value[x] only Canonical($GroveQuestionnaire)
* input[questionnaire].value[x] ^short = "Exact url|version of the Questionnaire the participant completes"
* output 0..1 MS
* output ^slicing.discriminator.type = #value
* output ^slicing.discriminator.path = "type"
* output ^slicing.rules = #closed
* output ^slicing.description = "The accepted result of a completed occurrence."
* output contains result 0..1 MS
* output[result].type = $sdcTemp#questionnaire-response
* output[result].value[x] only Reference($GroveQuestionnaireResponse)
* output[result].valueReference.reference 1..1 MS
* output[result].value[x] ^short = "Version-specific reference to the accepted QuestionnaireResponse"
