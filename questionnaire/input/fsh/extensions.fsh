// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT

Extension: GroveQuestionnaireWriterContext
Id: grove-questionnaire-writer-context
Title: "Grove Questionnaire Writer Context"
Description: "The application and host that captured one response, stated as plain facts. A writer cannot mint a Grove device snapshot, whose identity is scoped to an exchange event that does not exist at submission, so it states what it is and the projecting system builds the snapshot."
* ^context[+].type = #element
* ^context[=].expression = "QuestionnaireResponse"
* extension contains
    applicationIdentifier 1..1 MS and
    applicationName 1..1 MS and
    applicationVersion 1..1 MS and
    applicationBuild 0..1 MS and
    hostModel 0..1 MS and
    hostOperatingSystemVersion 0..1 MS
* extension[applicationIdentifier].value[x] only Identifier
* extension[applicationIdentifier].valueIdentifier.system 1..1 MS
* extension[applicationIdentifier].valueIdentifier.value 1..1 MS
* extension[applicationIdentifier] ^short = "Typed identifier of the capturing application in a deployment-owned namespace"
* extension[applicationName].value[x] only string
* extension[applicationName] ^short = "User-friendly application name the device snapshot carries"
* extension[applicationVersion].value[x] only string
* extension[applicationVersion] ^short = "Exact version the capturing application reports for itself"
* extension[applicationBuild].value[x] only string
* extension[applicationBuild] ^short = "Exact build the capturing application reports for itself"
* extension[hostModel].value[x] only string
* extension[hostModel] ^short = "Hardware model the application ran on"
* extension[hostOperatingSystemVersion].value[x] only string
* extension[hostOperatingSystemVersion] ^short = "Operating system version the host snapshot requires"
