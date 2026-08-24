//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: GroveQuestionnairePatientExample
InstanceOf: Patient
Usage: #example
Title: "Questionnaire Example Participant"
Description: "The participant referenced by the example response."
* identifier.system = "https://example.org/research/participant-id"
* identifier.value = "participant-001"

Instance: GroveWeeklySymptomCheckInExample
InstanceOf: GroveQuestionnaire
Usage: #example
Title: "Weekly Symptom Check-In"
Description: "A versioned instrument with a conditional follow-up question."
* extension[versionAlgorithm].valueCoding = $versionAlgorithm#semver
* url = "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveWeeklySymptomCheckInExample"
* version = "1.0.0"
* name = "GroveWeeklySymptomCheckIn"
* title = "Weekly Symptom Check-In"
* status = #active
* subjectType = #Patient
* item[0].linkId = "symptoms"
* item[0].text = "Symptoms"
* item[0].type = #group
* item[0].item[0].linkId = "pain-present"
* item[0].item[0].text = "Have you had pain during the last week?"
* item[0].item[0].type = #boolean
* item[0].item[0].item[0].linkId = "pain-severity"
* item[0].item[0].item[0].text = "How severe was the pain?"
* item[0].item[0].item[0].type = #choice
* item[0].item[0].item[0].enableWhen.question = "pain-present"
* item[0].item[0].item[0].enableWhen.operator = #=
* item[0].item[0].item[0].enableWhen.answerBoolean = true
* item[0].item[0].item[0].answerOption[0].valueCoding = $sct#255604002 "Mild"
* item[0].item[0].item[0].answerOption[1].valueCoding = $sct#6736007 "Moderate severity"
* item[0].item[0].item[0].answerOption[2].valueCoding = $sct#24484000 "Severe"
* item[0].item[1].linkId = "notes"
* item[0].item[1].text = "Is there anything else you would like to tell us?"
* item[0].item[1].type = #string

Instance: GroveWeeklySymptomCheckInResponseExample
InstanceOf: GroveQuestionnaireResponse
Usage: #example
Title: "Weekly Symptom Check-In Response"
Description: "A completed response whose follow-up answer is nested beneath the answer that enabled it."
* questionnaire = "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveWeeklySymptomCheckInExample|1.0.0"
* identifier.system = "https://example.org/research/questionnaire-response-id"
* identifier.value = "weekly-check-in-0001"
* status = #completed
* subject = Reference(GroveQuestionnairePatientExample)
* authored = "2026-08-19T09:30:00-07:00"
* extension[completionMode].valueCodeableConcept = $participationMode#ELECTRONIC
* item[0].linkId = "symptoms"
* item[0].text = "Symptoms"
* item[0].item[0].linkId = "pain-present"
* item[0].item[0].text = "Have you had pain during the last week?"
* item[0].item[0].answer.valueBoolean = true
* item[0].item[0].answer.item[0].linkId = "pain-severity"
* item[0].item[0].answer.item[0].text = "How severe was the pain?"
* item[0].item[0].answer.item[0].answer.valueCoding = $sct#6736007 "Moderate severity"
* item[0].item[1].linkId = "notes"
* item[0].item[1].text = "Is there anything else you would like to tell us?"
* item[0].item[1].answer.valueString = "The pain was limited to the first two days."
