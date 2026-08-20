//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Questionnaire conformance. Item-level hints are defined in extensions.fsh; this file
// applies them to the Questionnaire profile and encodes reusable validation rules.

Invariant: grove-que-media-text
Description: "An item carrying the SDC itemMedia extension SHALL also carry item.text, so renderers without media support degrade to text."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-itemMedia').exists()).all(text.exists())"


Invariant: grove-que-annotate-image
Description: "An annotate-image item SHALL be of type attachment and SHALL carry the base image in the SDC itemMedia extension."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl').value.ofType(CodeableConcept).coding.exists(system = 'https://grovealliance.org/fhir/core/CodeSystem/grove-questionnaire-item-control' and code = 'annotate-image')).all(type = 'attachment' and extension('http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-itemMedia').exists())"


Invariant: grove-qr-item-text
Description: "An answered item should carry the question text, so a reader can render the response without resolving the Questionnaire."
Severity: #warning
Expression: "item.where(answer.exists()).all(text.exists()) and item.repeat(item | answer.item).where(answer.exists()).all(text.exists())"


Profile: GroveQuestionnaire
Parent: Questionnaire
Id: grove-questionnaire
Title: "Grove Questionnaire"
Description: """
A FHIR R4 Questionnaire for exchange through Grove. The profile gives item-level
validation and presentation extensions a conformance home while preserving the standard
Questionnaire structure. Optional hints do not prevent another FHIR renderer from
presenting the instrument; item text remains available as the common fallback.

See [Questionnaires](questionnaires.html) for the relationship between an instrument,
its canonical URL, stable item linkIds, and QuestionnaireResponse answers.
"""
* obeys grove-que-media-text and grove-que-annotate-image
* url MS
* status MS
* item MS
* item.text MS
* item.extension contains
    $targetConstraint named targetConstraint 0..* MS and
    $sdcKeyboard named keyboard 0..1 MS and
    $itemMedia named itemMedia 0..1 MS and
    $itemControl named itemControl 0..1 MS and
    GroveAutocomplete named autocomplete 0..1 and
    GroveAutocapitalize named autocapitalize 0..1 and
    GroveAnnotateImageRegion named annotateImageRegion 0..*
* item.extension[targetConstraint] ^short = "Validation rule: FHIRPath expression, human message, severity"
* item.extension[keyboard] ^short = "Keyboard type hint for text answers"
* item.extension[itemMedia] ^short = "Media shown with the item; the base image for an annotate-image item"
* item.extension[itemControl] ^short = "Renderer hint; `annotate-image` selects the Grove image-annotation control"
* item.extension[autocomplete] ^short = "Autofill semantics for a text answer"
* item.extension[autocapitalize] ^short = "Autocapitalization behaviour for a text answer"
* item.extension[annotateImageRegion] ^short = "Selectable regions of an annotate-image item"


Profile: GroveQuestionnaireResponse
Parent: QuestionnaireResponse
Id: grove-questionnaire-response
Title: "Grove Questionnaire Response"
Description: """
A response to a ``GroveQuestionnaire``. The `questionnaire` element names the instrument
by canonical URL, and the standard completionMode extension records how the answers were
collected.

Answered items retain their question text, including follow-up items nested under the
answer that enabled them. This keeps a response human-readable on its own; the referenced
Questionnaire remains authoritative for choices, constraints, definitions, and complete
interpretation.
"""
* obeys grove-qr-item-text
* questionnaire 1..1 MS
* questionnaire ^short = "Canonical URL of the instrument, version-pinned where the deployment pins versions"
* status MS
* subject MS
* authored MS
* extension contains $completionMode named completionMode 0..1 MS
* extension[completionMode] ^short = "How the response was captured (electronic, telephone, …)"
* item.text MS


Instance: GroveFollowUpQuestionnaireExample
InstanceOf: GroveQuestionnaire
Usage: #example
Title: "Questionnaire with a Follow-Up Question"
Description: "A screening question whose follow-up only makes sense once it is answered, nested beneath it."
* status = #active
* name = "GroveFollowUpQuestionnaire"
* title = "Grove Follow-Up Questionnaire"
* url = "https://grovealliance.org/fhir/core/Questionnaire/GroveFollowUpQuestionnaireExample"
* item[0].linkId = "pain"
* item[0].type = #boolean
* item[0].text = "Have you had any pain in the last week?"
* item[0].item[0].linkId = "pain-severity"
* item[0].item[0].type = #integer
* item[0].item[0].text = "How severe was it, from 0 to 10?"
* item[0].item[0].enableWhen[0].question = "pain"
* item[0].item[0].enableWhen[0].operator = #=
* item[0].item[0].enableWhen[0].answerBoolean = true


Instance: GroveFollowUpQuestionnaireResponseExample
InstanceOf: GroveQuestionnaireResponse
Usage: #example
Title: "Response with a Follow-Up Under Its Answer"
Description: """
The response to ``GroveFollowUpQuestionnaireExample``. The follow-up rides in
`answer.item`, in the context of the answer that enabled it, and carries its own question
text there — which is what `grove-qr-item-text` checks below the top level.
"""
* status = #completed
* questionnaire = "https://grovealliance.org/fhir/core/Questionnaire/GroveFollowUpQuestionnaireExample"
* subject = Reference(GrovePatientExample)
* authored = "2026-08-12T18:34:00-07:00"
* item[0].linkId = "pain"
* item[0].text = "Have you had any pain in the last week?"
* item[0].answer.valueBoolean = true
* item[0].answer.item[0].linkId = "pain-severity"
* item[0].answer.item[0].text = "How severe was it, from 0 to 10?"
* item[0].answer.item[0].answer.valueInteger = 7
