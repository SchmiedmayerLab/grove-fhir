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
* extension[writerContext].extension[applicationIdentifier].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/application"
* extension[writerContext].extension[applicationIdentifier].valueIdentifier.value = "org.grovealliance.example.client"
* extension[writerContext].extension[applicationName].valueString = "Grove Questionnaire Client"
* extension[writerContext].extension[applicationVersion].valueString = "1.4.0"
* extension[writerContext].extension[applicationBuild].valueString = "220"
* extension[writerContext].extension[hostModel].valueString = "iPhone15,2"
* extension[writerContext].extension[hostOperatingSystemVersion].valueString = "26.0"
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

Instance: GroveHomeVitalsExample
InstanceOf: GroveQuestionnaire
Usage: #example
Title: "Home Vitals"
Description: "An instrument whose answers extract into a body weight and a blood pressure panel."
* extension[versionAlgorithm].valueCoding = $versionAlgorithm#semver
* url = "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveHomeVitalsExample"
* version = "1.0.0"
* name = "GroveHomeVitals"
* title = "Home Vitals"
* status = #active
* subjectType = #Patient
* item[0].linkId = "body-weight"
* item[0].text = "What was your weight this morning?"
* item[0].type = #quantity
* item[0].code = $loinc#29463-7 "Body weight"
* item[0].extension[observationExtract].valueBoolean = true
* item[0].extension[observationExtractCategory].valueCodeableConcept = $observationCategory#vital-signs "Vital Signs"
* item[0].extension[unitOption].valueCoding = $ucum#kg "kg"
* item[1].linkId = "blood-pressure"
* item[1].text = "Blood pressure"
* item[1].type = #group
* item[1].code = $loinc#85354-9 "Blood pressure panel with all children optional"
* item[1].extension[observationExtract].valueBoolean = true
* item[1].extension[observationExtractCategory].valueCodeableConcept = $observationCategory#vital-signs "Vital Signs"
* item[1].item[0].linkId = "systolic"
* item[1].item[0].text = "Systolic"
* item[1].item[0].type = #quantity
* item[1].item[0].code = $loinc#8480-6 "Systolic blood pressure"
* item[1].item[0].extension[$observationExtract].valueCode = #component
* item[1].item[0].extension[$unitOption].valueCoding = $ucum#mm[Hg] "mm[Hg]"
* item[1].item[1].linkId = "diastolic"
* item[1].item[1].text = "Diastolic"
* item[1].item[1].type = #quantity
* item[1].item[1].code = $loinc#8462-4 "Diastolic blood pressure"
* item[1].item[1].extension[$observationExtract].valueCode = #component
* item[1].item[1].extension[$unitOption].valueCoding = $ucum#mm[Hg] "mm[Hg]"
* item[1].item[2].linkId = "measured-at"
* item[1].item[2].text = "When did you take this reading?"
* item[1].item[2].type = #dateTime
* item[1].item[2].extension[$definitionExtractValue].extension[definition].valueUri = "http://hl7.org/fhir/StructureDefinition/Observation#Observation.effectiveDateTime"
* item[1].item[2].extension[$definitionExtractValue].extension[expression].valueExpression.language = #text/fhirpath
* item[1].item[2].extension[$definitionExtractValue].extension[expression].valueExpression.expression = "item.where(linkId = 'measured-at').answer.value"
* item[2].linkId = "step-count"
* item[2].text = "How many steps did you take yesterday?"
* item[2].type = #integer
* item[2].code = $groveMeasurement#step-count-total "Step count total"
* item[2].extension[observationExtract].valueBoolean = true
* item[2].extension[$questionnaireUnit].valueCoding = $ucum#{steps} "{steps}"
* item[2].extension[$definitionExtractValue][0].extension[definition].valueUri = "http://hl7.org/fhir/StructureDefinition/Observation#Observation.effectivePeriod.start"
* item[2].extension[$definitionExtractValue][0].extension[expression].valueExpression.language = #text/fhirpath
* item[2].extension[$definitionExtractValue][0].extension[expression].valueExpression.expression = "(%resource.authored.toDate() - 1 day).toString() + 'T00:00:00' + %resource.authored.toString().substring(19)"
* item[2].extension[$definitionExtractValue][1].extension[definition].valueUri = "http://hl7.org/fhir/StructureDefinition/Observation#Observation.effectivePeriod.end"
* item[2].extension[$definitionExtractValue][1].extension[expression].valueExpression.language = #text/fhirpath
* item[2].extension[$definitionExtractValue][1].extension[expression].valueExpression.expression = "%resource.authored.toDate().toString() + 'T00:00:00' + %resource.authored.toString().substring(19)"

Instance: GroveHomeVitalsResponseExample
InstanceOf: GroveQuestionnaireResponse
Usage: #example
Title: "Home Vitals Response"
Description: "A conformant response to the Home Vitals instrument, carrying the context a projection needs."
* extension[completionMode].valueCodeableConcept = $participationMode#ELECTRONIC
* extension[writerContext].extension[applicationIdentifier].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/application"
* extension[writerContext].extension[applicationIdentifier].valueIdentifier.value = "org.grovealliance.example.client"
* extension[writerContext].extension[applicationName].valueString = "Grove Questionnaire Client"
* extension[writerContext].extension[applicationVersion].valueString = "1.4.0"
* extension[writerContext].extension[applicationBuild].valueString = "1402"
* extension[writerContext].extension[hostModel].valueString = "iPhone17,1"
* extension[writerContext].extension[hostOperatingSystemVersion].valueString = "26.0"
* identifier.system = "https://study.example.org/fhir/NamingSystem/questionnaire-response"
* identifier.value = "home-vitals-2026-08-28"
* questionnaire = "https://grovealliance.org/fhir/questionnaire/Questionnaire/GroveHomeVitalsExample|1.0.0"
* status = #completed
* subject = Reference(GroveQuestionnairePatientExample)
* authored = "2026-08-28T08:32:00-07:00"
* item[0].linkId = "body-weight"
* item[0].answer.valueQuantity.value = 72.5
* item[0].answer.valueQuantity.unit = "kg"
* item[0].answer.valueQuantity.system = $ucum
* item[0].answer.valueQuantity.code = #kg
* item[1].linkId = "blood-pressure"
* item[1].item[0].linkId = "systolic"
* item[1].item[0].answer.valueQuantity.value = 118
* item[1].item[0].answer.valueQuantity.unit = "mmHg"
* item[1].item[0].answer.valueQuantity.system = $ucum
* item[1].item[0].answer.valueQuantity.code = #mm[Hg]
* item[1].item[1].linkId = "diastolic"
* item[1].item[1].answer.valueQuantity.value = 76
* item[1].item[1].answer.valueQuantity.unit = "mmHg"
* item[1].item[1].answer.valueQuantity.system = $ucum
* item[1].item[1].answer.valueQuantity.code = #mm[Hg]
* item[1].item[2].linkId = "measured-at"
* item[1].item[2].answer.valueDateTime = "2026-08-28T08:10:00-07:00"
* item[2].linkId = "step-count"
* item[2].answer.valueInteger = 8432
