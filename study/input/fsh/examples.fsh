//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// The Publisher stamps the guide version onto every canonical resource it builds, so the example
// protocol, components, and instrument carry the guide version, and every exact canonical that joins
// them names that version.

Instance: GroveStudyDailyCheckInExample
InstanceOf: $GroveQuestionnaire
Usage: #example
Title: "Daily Check-In"
Description: "The instrument the daily check-in component asks the participant to complete."
* extension[versionAlgorithm].valueCoding = $versionAlgorithm#semver
* url = "https://grovealliance.org/fhir/study/Questionnaire/GroveStudyDailyCheckInExample"
* version = "0.8.3"
* language = #en-US
* name = "GroveStudyDailyCheckIn"
* title = "Daily Check-In"
* status = #active
* experimental = true
* subjectType = #Patient
* item[0].linkId = "slept-well"
* item[0].text = "Did you sleep well last night?"
* item[0].type = #boolean
* item[0].required = true
* item[1].linkId = "energy"
* item[1].text = "How much energy do you have today, from 0 for none to 10 for plenty?"
* item[1].type = #integer
* item[1].required = true

Instance: GroveStudyDailyCheckInComponentExample
InstanceOf: GroveStudyQuestionnaireComponent
Usage: #example
Title: "Daily Check-In Component"
Description: "One revision of the daily check-in study component. It pins the exact instrument revision every occurrence of this component administers."
* url = "https://grovealliance.org/fhir/study/ActivityDefinition/GroveStudyDailyCheckInComponentExample"
* version = "0.8.3"
* name = "GroveStudyDailyCheckInComponent"
* title = "Daily check-in"
* status = #active
* experimental = true
* kind = #Task
* intent = #order
* code = $sdcTemp#complete-questionnaire
* relatedArtifact[instrument].type = #depends-on
* relatedArtifact[instrument].resource = "https://grovealliance.org/fhir/study/Questionnaire/GroveStudyDailyCheckInExample|0.8.3"

Instance: GroveStudyWelcomeComponentExample
InstanceOf: GroveStudyComponent
Usage: #example
Title: "Welcome Component"
Description: "One revision of an informational study component that shows the participant a welcome message. It defines no result, so its occurrences complete without an output."
* url = "https://grovealliance.org/fhir/study/ActivityDefinition/GroveStudyWelcomeComponentExample"
* version = "0.8.3"
* name = "GroveStudyWelcomeComponent"
* title = "Welcome"
* status = #active
* experimental = true
* description = "Shows the participant a welcome message about the study."
* kind = #Task
* intent = #order

Instance: GroveStudyProtocolExample
InstanceOf: GroveStudyProtocol
Usage: #example
Title: "Single-Arm Daily Check-In Protocol"
Description: "One revision of a single-arm protocol with two actions: an informational welcome component and the daily check-in."
* url = "https://grovealliance.org/fhir/study/PlanDefinition/GroveStudyProtocolExample"
* version = "0.8.3"
* name = "GroveStudyDailyCheckInProtocol"
* title = "Single-arm daily check-in protocol"
* status = #active
* experimental = true
* action[0].title = "Welcome"
* action[0].definitionCanonical = "https://grovealliance.org/fhir/study/ActivityDefinition/GroveStudyWelcomeComponentExample|0.8.3"
* action[1].title = "Daily check-in"
* action[1].definitionCanonical = "https://grovealliance.org/fhir/study/ActivityDefinition/GroveStudyDailyCheckInComponentExample|0.8.3"

Instance: GroveStudyEnrollmentExample
InstanceOf: ResearchSubject
Usage: #example
Title: "Enrollment"
Description: "The participant's enrollment in the study. The occurrences assigned under it name it by its business identifier."
* identifier.system = "https://example.org/research/enrollment-id"
* identifier.value = "enrollment-001"
* status = $researchSubjectStatus#on-study
* period.start = "2026-08-18T08:00:00-07:00"
* study.type = "ResearchStudy"
* study.identifier.system = "https://example.org/research/study-id"
* study.identifier.value = "daily-check-in-study"
* individual.type = "Patient"
* individual.identifier.system = "https://example.org/research/participant-id"
* individual.identifier.value = "participant-001"

RuleSet: GroveStudyOccurrence(component, occurrence, start, end)
* identifier.system = "https://example.org/research/occurrence-id"
* identifier.value = "{occurrence}"
* instantiatesCanonical = "https://grovealliance.org/fhir/study/ActivityDefinition/{component}|0.8.3"
* intent = #order
* for.type = "Patient"
* for.identifier.system = "https://example.org/research/participant-id"
* for.identifier.value = "participant-001"
* authoredOn = "2026-08-18T08:00:00-07:00"
* input[performanceWindow].type = GroveStudyTaskInputCS#performance-window
* input[performanceWindow].valuePeriod.start = "{start}"
* input[performanceWindow].valuePeriod.end = "{end}"
* input[enrollment].type = GroveStudyTaskInputCS#enrollment
* input[enrollment].valueReference.type = "ResearchSubject"
* input[enrollment].valueReference.identifier.system = "https://example.org/research/enrollment-id"
* input[enrollment].valueReference.identifier.value = "enrollment-001"
* input[protocol].type = GroveStudyTaskInputCS#protocol
* input[protocol].valueCanonical = "https://grovealliance.org/fhir/study/PlanDefinition/GroveStudyProtocolExample|0.8.3"

RuleSet: GroveStudyDailyCheckInOccurrence(occurrence, start, end)
* insert GroveStudyOccurrence(GroveStudyDailyCheckInComponentExample, {occurrence}, {start}, {end})
* code = $sdcTemp#complete-questionnaire
* input[questionnaire].type = $sdcTemp#questionnaire
* input[questionnaire].valueCanonical = "https://grovealliance.org/fhir/study/Questionnaire/GroveStudyDailyCheckInExample|0.8.3"

Instance: GroveStudyWelcomeTaskExample
InstanceOf: GroveStudyTask
Usage: #example
Title: "Completed Informational Occurrence"
Description: "The welcome occurrence after the participant viewed the message. Its component defines no result, so the completed Task carries no output."
* insert GroveStudyOccurrence(GroveStudyWelcomeComponentExample, welcome-0001, 2026-08-18T08:00:00-07:00, 2026-08-25T08:00:00-07:00)
* status = #completed
* lastModified = "2026-08-18T08:05:12-07:00"
* executionPeriod.start = "2026-08-18T08:04:30-07:00"
* executionPeriod.end = "2026-08-18T08:05:00-07:00"

Instance: GroveStudyCompletedTaskExample
InstanceOf: GroveStudyQuestionnaireTask
Usage: #example
Title: "Completed Occurrence"
Description: "The first day's occurrence after its response was accepted. The output names the exact accepted version of the response."
* insert GroveStudyDailyCheckInOccurrence(occurrence-0001, 2026-08-19T06:00:00-07:00, 2026-08-19T23:59:59-07:00)
* status = #completed
* lastModified = "2026-08-19T09:31:02-07:00"
* executionPeriod.start = "2026-08-19T09:28:40-07:00"
* executionPeriod.end = "2026-08-19T09:30:00-07:00"
* output[result].type = $sdcTemp#questionnaire-response
* output[result].valueReference.reference = "QuestionnaireResponse/GroveStudyDailyCheckInResponseExample/_history/1"

Instance: GroveStudyAssignedTaskExample
InstanceOf: GroveStudyQuestionnaireTask
Usage: #example
Title: "Assigned Occurrence"
Description: "The second day's occurrence while it is assigned and has no accepted result."
* insert GroveStudyDailyCheckInOccurrence(occurrence-0002, 2026-08-20T06:00:00-07:00, 2026-08-20T23:59:59-07:00)
* status = #ready
* lastModified = "2026-08-18T08:00:00-07:00"

Instance: GroveStudyExcusedTaskExample
InstanceOf: GroveStudyQuestionnaireTask
Usage: #example
Title: "Excused Occurrence"
Description: "The third day's occurrence after the study released the participant from it before its window opened."
* insert GroveStudyDailyCheckInOccurrence(occurrence-0003, 2026-08-21T06:00:00-07:00, 2026-08-21T23:59:59-07:00)
* status = #cancelled
* statusReason = GroveStudyTaskStatusReasonCS#excused
* lastModified = "2026-08-20T17:12:00-07:00"

Instance: GroveStudyDailyCheckInResponseExample
InstanceOf: $GroveQuestionnaireResponse
Usage: #example
Title: "Daily Check-In Response"
Description: "The accepted response that completes the first day's occurrence. It does not point back to the Task; the Task links it."
* meta.versionId = "1"
* language = #en-US
* questionnaire = "https://grovealliance.org/fhir/study/Questionnaire/GroveStudyDailyCheckInExample|0.8.3"
* identifier.system = "https://example.org/research/questionnaire-response-id"
* identifier.value = "daily-check-in-0001"
* status = #completed
* subject.type = "Patient"
* subject.identifier.system = "https://example.org/research/participant-id"
* subject.identifier.value = "participant-001"
* authored = "2026-08-19T09:30:00-07:00"
* extension[completionMode].valueCodeableConcept = $participationMode#ELECTRONIC
* item[0].linkId = "slept-well"
* item[0].text = "Did you sleep well last night?"
* item[0].answer.valueBoolean = true
* item[1].linkId = "energy"
* item[1].text = "How much energy do you have today, from 0 for none to 10 for plenty?"
* item[1].answer.valueInteger = 7
