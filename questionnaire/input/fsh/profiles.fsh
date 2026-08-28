//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: qg-canonical-1
Description: "Questionnaire.url is one absolute HTTP(S) canonical URL without a version separator or fragment."
Severity: #error
Expression: "url.matches('^https?://[^\\\\s/?#|]+[^\\\\s|#]*$')"

Invariant: qg-version-1
Description: "Questionnaire.version is a valid Semantic Versioning 2.0.0 version."
Severity: #error
Expression: "version.matches('^(0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)([.](0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?([+]([0-9A-Za-z-]+)([.][0-9A-Za-z-]+)*)?$')"

Invariant: qg-version-algorithm-1
Description: "The instrument declares Semantic Versioning as its one version comparison algorithm."
Severity: #error
Expression: "extension('http://hl7.org/fhir/StructureDefinition/artifact-versionAlgorithm').count() = 1 and extension('http://hl7.org/fhir/StructureDefinition/artifact-versionAlgorithm').value.ofType(Coding).where(system = 'http://hl7.org/fhir/version-algorithm' and code = 'semver').count() = 1"

Invariant: qg-item-text-1
Description: "Every question and display item has text; structural groups may use text as an optional heading."
Severity: #error
Expression: "repeat(item).where(type != 'group').all(text.exists())"

Invariant: qg-reference-1
Description: "Reference questions and reference-valued answer options are outside this exchange contract."
Severity: #error
Expression: "repeat(item).where(type = 'reference').empty() and repeat(item).answerOption.value.ofType(Reference).empty()"

Invariant: qg-repeats-1
Description: "Repeated answers are limited to choice, open-choice, and attachment questions."
Severity: #error
Expression: "repeat(item).where(repeats = true).all(type = 'choice' or type = 'open-choice' or type = 'attachment')"

Invariant: qg-enable-1
Description: "An item does not combine core enableWhen rules with an enableWhenExpression."
Severity: #error
Expression: "repeat(item).where(enableWhen.exists() and extension('http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-enableWhenExpression').exists()).empty()"

Invariant: qg-expression-1
Description: "Every retained expression is a non-empty FHIRPath expression."
Severity: #error
Expression: "extension.where(url = 'http://hl7.org/fhir/StructureDefinition/variable').value.ofType(Expression).all(language = 'text/fhirpath' and expression.exists() and expression != '') and extension.where(url = 'http://hl7.org/fhir/StructureDefinition/targetConstraint').extension.where(url = 'expression').value.ofType(Expression).all(language = 'text/fhirpath' and expression.exists() and expression != '') and repeat(item).extension.where(url = 'http://hl7.org/fhir/StructureDefinition/variable' or url = 'http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-enableWhenExpression' or url = 'http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-initialExpression' or url = 'http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-calculatedExpression').value.ofType(Expression).all(language = 'text/fhirpath' and expression.exists() and expression != '') and repeat(item).extension.where(url = 'http://hl7.org/fhir/StructureDefinition/targetConstraint').extension.where(url = 'expression').value.ofType(Expression).all(language = 'text/fhirpath' and expression.exists() and expression != '')"

Invariant: qg-variable-name-1
Description: "Every variable expression has a non-empty name."
Severity: #error
Expression: "extension('http://hl7.org/fhir/StructureDefinition/variable').value.ofType(Expression).all(name.exists() and name != '') and repeat(item).extension('http://hl7.org/fhir/StructureDefinition/variable').value.ofType(Expression).all(name.exists() and name != '')"

Invariant: qg-initial-1
Description: "An item does not combine a literal initial value with an initialExpression."
Severity: #error
Expression: "repeat(item).where(initial.exists() and extension('http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-initialExpression').exists()).empty()"

Invariant: qg-length-1
Description: "Text length constraints are used only on string, text, url, or open-choice items."
Severity: #error
Expression: "repeat(item).where(maxLength.exists() or extension('http://hl7.org/fhir/StructureDefinition/minLength').exists()).all(type = 'string' or type = 'text' or type = 'url' or type = 'open-choice')"

Invariant: qg-decimal-1
Description: "maxDecimalPlaces is used only on decimal items."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/StructureDefinition/maxDecimalPlaces').exists()).all(type = 'decimal')"

Invariant: qg-value-bounds-1
Description: "Generic minimum and maximum value bounds are used only on integer, decimal, date, dateTime, or time items."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/StructureDefinition/minValue').exists() or extension('http://hl7.org/fhir/StructureDefinition/maxValue').exists()).all(type = 'integer' or type = 'decimal' or type = 'date' or type = 'dateTime' or type = 'time')"

Invariant: qg-quantity-1
Description: "Quantity bounds are used only on quantity items."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-minQuantity').exists() or extension('http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-maxQuantity').exists()).all(type = 'quantity')"

Invariant: qg-unit-1
Description: "A fixed questionnaire unit is used only for integer or decimal items; selectable units are used only for quantity items and come from either inline options or one ValueSet."
Severity: #error
Expression: "repeat(item).all((extension('http://hl7.org/fhir/StructureDefinition/questionnaire-unit').empty() or type = 'integer' or type = 'decimal') and (extension('http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption').empty() or type = 'quantity') and (extension('http://hl7.org/fhir/StructureDefinition/questionnaire-unitValueSet').empty() or type = 'quantity') and (extension('http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption').empty() or extension('http://hl7.org/fhir/StructureDefinition/questionnaire-unitValueSet').empty()))"

Invariant: qg-attachment-1
Description: "MIME type and maximum-size constraints are used only on attachment items."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/StructureDefinition/mimeType').exists() or extension('http://hl7.org/fhir/StructureDefinition/maxSize').exists()).all(type = 'attachment')"

Invariant: qg-occurrence-1
Description: "Minimum and maximum occurrence constraints are used only on repeating items."
Severity: #error
Expression: "repeat(item).where(extension('http://hl7.org/fhir/StructureDefinition/questionnaire-minOccurs').exists() or extension('http://hl7.org/fhir/StructureDefinition/questionnaire-maxOccurs').exists()).all(repeats = true)"

Invariant: qg-min-max-1
Description: "Minimum text length and occurrence counts do not exceed their corresponding maxima."
Severity: #error
Expression: "repeat(item).all((extension('http://hl7.org/fhir/StructureDefinition/minLength').empty() or maxLength.empty() or extension('http://hl7.org/fhir/StructureDefinition/minLength').value.first() <= maxLength) and (extension('http://hl7.org/fhir/StructureDefinition/questionnaire-minOccurs').empty() or extension('http://hl7.org/fhir/StructureDefinition/questionnaire-maxOccurs').empty() or extension('http://hl7.org/fhir/StructureDefinition/questionnaire-minOccurs').value.first() <= extension('http://hl7.org/fhir/StructureDefinition/questionnaire-maxOccurs').value.first()))"

Invariant: qg-style-sensitive-1
Description: "This exchange contract does not accept presentation-sensitive semantics."
Severity: #error
Expression: "extension('http://hl7.org/fhir/StructureDefinition/rendering-styleSensitive').empty() and repeat(item).extension('http://hl7.org/fhir/StructureDefinition/rendering-styleSensitive').empty()"

Invariant: gqr-canonical-1
Description: "The response names the exact instrument with an absolute url|Semantic-Version canonical; neither component contains a fragment or an extra separator."
Severity: #error
Expression: "questionnaire.matches('^https?://[^\\\\s/?#|]+[^\\\\s|#]*[|](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)[.](0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)([.](0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?([+]([0-9A-Za-z-]+)([.][0-9A-Za-z-]+)*)?$')"

Invariant: gqr-identifier-1
Description: "The response has one business identifier with a complete system and value pair."
Severity: #error
Expression: "identifier.count() = 1 and identifier.system.exists() and identifier.value.exists()"

Invariant: gqr-completion-mode-1
Description: "The response declares exactly one electronic ParticipationMode coding."
Severity: #error
Expression: "extension('http://hl7.org/fhir/StructureDefinition/questionnaireresponse-completionMode').count() = 1 and extension('http://hl7.org/fhir/StructureDefinition/questionnaireresponse-completionMode').value.ofType(CodeableConcept).coding.count() = 1 and extension('http://hl7.org/fhir/StructureDefinition/questionnaireresponse-completionMode').value.ofType(CodeableConcept).coding.all(system = 'http://terminology.hl7.org/CodeSystem/v3-ParticipationMode' and code = 'ELECTRONIC')"

Profile: GroveQuestionnaire
Parent: http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire
Id: grove-questionnaire
Title: "Grove Questionnaire"
Description: "A versioned SDC Questionnaire that can be administered and answered without relying on renderer-specific semantics."
* obeys qg-canonical-1 and qg-version-1 and qg-version-algorithm-1 and qg-item-text-1 and qg-reference-1 and qg-repeats-1 and qg-enable-1 and qg-expression-1 and qg-variable-name-1 and qg-initial-1 and qg-length-1 and qg-decimal-1 and qg-value-bounds-1 and qg-quantity-1 and qg-unit-1 and qg-attachment-1 and qg-occurrence-1 and qg-min-max-1 and qg-style-sensitive-1
* extension contains
    $variable named variable 0..* MS and
    $targetConstraint named targetConstraint 0..* MS
* extension[versionAlgorithm] 1..1 MS
* extension[versionAlgorithm].value[x] only Coding
* extension[versionAlgorithm].valueCoding.system 1..1
* extension[versionAlgorithm].valueCoding.system = $versionAlgorithm (exactly)
* extension[versionAlgorithm].valueCoding.code 1..1
* extension[versionAlgorithm].valueCoding.code = #semver (exactly)
* extension[variable].valueExpression.name 1..1 MS
* url 1..1 MS
* version 1..1 MS
* status 1..1 MS
* subjectType MS
* item 1..* MS
* item.linkId 1..1 MS
* item.definition MS
* item.code MS
* item.text MS
* item.type 1..1 MS
* item.required MS
* item.repeats MS
* item.readOnly MS
* item.enableWhen MS
* item.enableBehavior MS
* item.answerOption MS
* item.answerValueSet MS
* item.initial MS
* item.maxLength MS
* item.extension[hidden] MS
* item.extension contains
    $variable named variable 0..* MS and
    $enableWhenExpression named enableWhenExpression 0..1 MS and
    $initialExpression named initialExpression 0..1 MS and
    $calculatedExpression named calculatedExpression 0..1 MS and
    $targetConstraint named targetConstraint 0..* MS and
    $minLength named minLength 0..1 MS and
    $minValue named minValue 0..1 MS and
    $maxValue named maxValue 0..1 MS and
    $minQuantity named minQuantity 0..1 MS and
    $maxQuantity named maxQuantity 0..1 MS and
    $maxDecimalPlaces named maxDecimalPlaces 0..1 MS and
    $questionnaireUnit named unit 0..1 MS and
    $unitOption named unitOption 0..* MS and
    $unitValueSet named unitValueSet 0..1 MS and
    $minOccurs named minOccurs 0..1 MS and
    $maxOccurs named maxOccurs 0..1 MS and
    $mimeType named mimeType 0..* MS and
    $maxSize named maxSize 0..1 MS
* item.extension[variable].valueExpression.name 1..1 MS
* item.answerOption.extension contains
    $optionExclusive named optionExclusive 0..1 MS and
    $itemWeight named itemWeight 0..1 MS
* item.answerOption.valueCoding.extension contains
    $itemWeight named itemWeight 0..1 MS

Profile: GroveQuestionnaireResponse
Parent: http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaireresponse
Id: grove-questionnaire-response
Title: "Grove Questionnaire Response"
Description: "A response to one exact version of a Grove Questionnaire, with a stable submission identifier and electronic completion mode."
* obeys gqr-canonical-1 and gqr-identifier-1 and gqr-completion-mode-1
* questionnaire 1..1 MS
* questionnaire only Canonical(GroveQuestionnaire)
* identifier 1..1 MS
* identifier.system 1..1 MS
* identifier.value 1..1 MS
* status 1..1 MS
* subject MS
* authored 1..1 MS
* author MS
* source MS
* extension[completionMode] 1..1 MS
* extension[completionMode].value[x] only CodeableConcept
* extension[completionMode].valueCodeableConcept.coding 1..1 MS
* extension[completionMode].valueCodeableConcept.coding.system 1..1 MS
* extension[completionMode].valueCodeableConcept.coding.system = $participationMode (exactly)
* extension[completionMode].valueCodeableConcept.coding.code 1..1 MS
* extension[completionMode].valueCodeableConcept.coding.code = #ELECTRONIC (exactly)
* extension[completionMode].valueCodeableConcept from $questionnaireResponseModeVS (required)
* item MS
* item.linkId 1..1 MS
* item.text MS
* item.answer MS
* item.answer.valueCoding.extension contains
    $itemWeight named itemWeight 0..1 MS
