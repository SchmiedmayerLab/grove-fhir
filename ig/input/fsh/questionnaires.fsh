//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Questionnaire conformance. The item-level hints are defined in extensions.fsh; this
// file gives them a profile to hang from and turns the two rules the Questionnaires
// page states as normative into invariants a validator can enforce.

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
An instrument a Grove renderer presents. Nothing here changes what a Questionnaire is:
the profile exists so the guide's item-level hints have a conformance home, and so the
two rules the [Questionnaires](questionnaires.html) page states as normative become
machine-checkable — an item whose content is an image keeps its text, and an
annotate-image item really carries an image to annotate.

Every hint below is optional and ignorable. A renderer that knows none of them still
presents a conformant instrument, which is why no slice is required; Must Support means
Grove's own renderer honors it, not that an authoring tool must emit it.

`autocomplete`, `autocapitalize`, and the annotate-image region legend carry no Must
Support flag: Grove recognises them on import, and nothing in Grove writes them yet. The
[Renderer Support Matrix](questionnaire-support.html) tracks that, and the flags return
when a writer does.
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
A response Grove produces for a ``GroveQuestionnaire``. The instrument is named by
canonical URL rather than by reference, so a response stays interpretable away from the
server that served the form, and how it was captured rides in the standard
completionMode extension.

Item text travels on every answered item — including a follow-up nested under the answer
it qualifies, which is where Grove puts child questions — so a reader can render the
response without resolving the instrument. That is a warning rather than an error: a
response imported from another system may legitimately omit it.
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
