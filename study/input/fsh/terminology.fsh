//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: GroveStudyTaskParameterCS
Id: grove-study-task-parameter
Title: "Grove Study Task Parameter"
Description: "The type of one Task input that places an assigned occurrence in its study context. The Questionnaire input and the QuestionnaireResponse output use the Structured Data Capture codes for those roles."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #performance-window "Performance window" "The Period in which the participant is allowed to perform the occurrence. Its start opens the occurrence and its end is the last instant at which answers can be gathered for it."
* #enrollment "Enrollment" "The ResearchSubject the occurrence was assigned under. A later enrollment of the same participant is a different ResearchSubject."
* #protocol "Protocol" "The exact url|version of the PlanDefinition whose action assigned the occurrence."

ValueSet: GroveStudyTaskStatusVS
Id: grove-study-task-status
Title: "Grove Study Task Status"
Description: "The Task statuses an assigned occurrence can carry: ready while it is assigned, completed once one result has been accepted, and cancelled once the assignment was stopped."
* ^experimental = false
* $taskStatus#ready
* $taskStatus#completed
* $taskStatus#cancelled

CodeSystem: GroveStudyTaskStatusReasonCS
Id: grove-study-task-status-reason
Title: "Grove Study Task Status Reason"
Description: "Why the assignment of a cancelled occurrence was stopped, where the reason changes how the occurrence counts."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #excused "Excused" "The study released the participant from this occurrence. It counts as excused, neither as completed nor as missed."

ValueSet: GroveStudyTaskStatusReasonVS
Id: grove-study-task-status-reason
Title: "Grove Study Task Status Reason"
Description: "The status reasons a cancelled occurrence can carry."
* ^experimental = false
* include codes from system GroveStudyTaskStatusReasonCS
