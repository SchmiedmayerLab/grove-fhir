//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: HealthKitSourceDocumentTimeBasisCS
Id: healthkit-source-document-time-basis
Title: "HealthKit Source Document Time Basis"
Description: "The source API meaning of a clinical or CDA document sample's dates, independent of the dates of care in its payload."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #clinical-record-download "Download to HealthKit" "The time when HealthKit downloaded the provider-issued FHIR resource to the device."
* #cda-source-document-period "Source-assigned document dates" "The dates assigned by the creator of a HealthKit CDA document sample; no clinical service or download-time meaning is inferred."

ValueSet: HealthKitSourceDocumentTimeBasisVS
Id: healthkit-source-document-time-basis
Title: "HealthKit Source Document Time Basis"
Description: "The closed source-time bases for HealthKit clinical and CDA document envelopes."
* ^experimental = false
* include codes from system HealthKitSourceDocumentTimeBasisCS

Invariant: healthkit-source-document-time-order
Description: "Both source period endpoints are present and the end is not before the start."
Severity: #error
Expression: "extension.where(url='period').value.ofType(Period).all(start.exists() and end.exists() and start <= end)"

Invariant: healthkit-source-document-time-complete
Description: "Source document bounds include a complete time and an explicit time zone."
Severity: #error
Expression: "extension.where(url='period').value.ofType(Period).all(start.toString().matches('.*T.*(Z|[+-][0-9]{2}:[0-9]{2})$') and end.toString().matches('.*T.*(Z|[+-][0-9]{2}:[0-9]{2})$'))"

Extension: HealthKitSourceDocumentTime
Id: healthkit-source-document-time
Title: "HealthKit Source Document Time"
Description: "The source document sample dates and their exact API meaning. These describe the consumed source entity; they do not state when the care described in the original document occurred. HKClinicalRecord uses clinical-record-download; HKCDADocumentSample uses cda-source-document-period. The producer preserves the source bounds under the adapter's timestamp precision rules."
Context: Provenance.entity
* obeys healthkit-source-document-time-order and healthkit-source-document-time-complete
* extension ^slicing.rules = #closed
* extension contains basis 1..1 MS and period 1..1 MS
* extension[basis].extension 0..0
* extension[basis].value[x] 1..1
* extension[basis].value[x] only code
* extension[basis].valueCode from HealthKitSourceDocumentTimeBasisVS (required)
* extension[period].extension 0..0
* extension[period].value[x] 1..1
* extension[period].value[x] only Period
* extension[period].valuePeriod.start 1..1
* extension[period].valuePeriod.end 1..1
* value[x] 0..0
