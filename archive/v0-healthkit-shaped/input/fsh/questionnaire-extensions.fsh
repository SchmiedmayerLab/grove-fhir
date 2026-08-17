//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Questionnaire rendering hints Grove's iOS questionnaire renderer reads from
// Questionnaire items, and the annotate-image custom item control.
//
// Unlike the Observation extensions, annotate-image region sub-extensions use
// conventional RELATIVE URLs ("label", "color"), matching the reader in
// GroveQuestionnaireFHIR.

Extension: GroveValidationText
Id: validationText
Title: "Validation Text"
Description: """
The message shown to the user when their answer fails the item's validation
(typically the `regex` extension). Read by Grove's questionnaire renderer.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://bdh.stanford.edu/fhir/StructureDefinition/validationtext"
* ^identifier[=].use = #old
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://biodesign.stanford.edu/fhir/StructureDefinition/validationtext"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only string
* valueString 1..1


Extension: GroveIosKeyboardType
Id: iosKeyboardType
Title: "iOS Keyboard Type"
Description: """
The preferred iOS keyboard for a text answer, as the case-insensitive name of a
`UIKeyboardType` case (e.g. `emailAddress`, `numberPad`, `URL`). A hint for iOS
renderers; other clients ignore it.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://bdh.stanford.edu/fhir/StructureDefinition/ios-keyboardtype"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only string
* valueString 1..1


Extension: GroveIosTextContentType
Id: iosTextContentType
Title: "iOS Text Content Type"
Description: """
The semantic content type of a text answer, as the name of a `UITextContentType`
constant (e.g. `emailAddress`, `telephoneNumber`), enabling iOS autofill.
A hint for iOS renderers; other clients ignore it.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://bdh.stanford.edu/fhir/StructureDefinition/ios-textcontenttype"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only string
* valueString 1..1


Extension: GroveIosAutocapitalizationType
Id: iosAutocapitalizationType
Title: "iOS Autocapitalization Type"
Description: """
The autocapitalization behaviour for a text answer, as the name of a
`UITextAutocapitalizationType` case (e.g. `none`, `words`, `sentences`).
A hint for iOS renderers; other clients ignore it.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://bdh.stanford.edu/fhir/StructureDefinition/ios-autocapitalizationType"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only string
* valueString 1..1


Extension: GroveAnnotateImageInputImage
Id: annotateImageInputImage
Title: "Annotate Image: Input Image"
Description: """
The base image of an annotate-image item, as the filename of an image in the app's
main bundle. Exactly one is required on an item whose `itemControl` is
`annotate-image` from the Grove questionnaire item control code system.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control/annotate-image/input-image"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only string
* valueString 1..1
* valueString ^short = "Image filename in the app's main bundle"


Extension: GroveAnnotateImageRegion
Id: annotateImageRegion
Title: "Annotate Image: Region"
Description: """
One selectable region of an annotate-image item: a label the user sees and the pen
color used when annotating that region. An item may declare any number of regions.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control/annotate-image/region"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] 0..0
* extension contains label 1..1 and color 1..1
* extension[label].value[x] only string
* extension[label] ^short = "Region name shown to the user"
* extension[color].value[x] only string
* extension[color].value[x] from GroveAnnotateImageColorsVS (required)
* extension[color] ^short = "Pen color for this region"


CodeSystem: GroveQuestionnaireItemControlCS
Id: questionnaire-item-control
Title: "Grove Questionnaire Item Control"
Description: """
Item control codes for Grove-specific questionnaire item renderers, used as codings
in the standard `questionnaire-itemControl` extension.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control"
* ^identifier[=].use = #old
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #annotate-image "Annotate Image" "The user annotates a base image with a drawing; the answer is the annotated image as a PNG attachment."


CodeSystem: GroveAnnotateImageColorsCS
Id: annotate-image-colors
Title: "Annotate Image Region Colors"
Description: "Pen colors available to annotate-image regions, mirroring SwiftUI's standard colors."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #red "Red"
* #orange "Orange"
* #yellow "Yellow"
* #green "Green"
* #mint "Mint"
* #teal "Teal"
* #cyan "Cyan"
* #blue "Blue"
* #indigo "Indigo"
* #purple "Purple"
* #pink "Pink"
* #brown "Brown"
* #white "White"
* #gray "Gray"
* #black "Black"
* #clear "Clear"
* #primary "Primary"
* #secondary "Secondary"


ValueSet: GroveAnnotateImageColorsVS
Id: annotate-image-colors
Title: "Annotate Image Region Colors"
Description: "All pen colors an annotate-image region may use."
* ^experimental = false
* include codes from system GroveAnnotateImageColorsCS
