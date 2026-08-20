//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: healthkit-motion-context-1
Description: "Heart-rate motion context is present only on an Observation coded with LOINC 8867-4."
Expression: "component.where(code.coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-metadata-key' and code = 'HKMetadataKeyHeartRateMotionContext').exists()).empty() or code.coding.where(system = 'http://loinc.org' and code = '8867-4').exists()"
Severity: #error

Invariant: healthkit-object-id-1
Description: "A HealthKit object identifier value is lowercase UUID text in 8-4-4-4-12 hyphenated form."
Expression: "value.matches('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')"
Severity: #error

Invariant: healthkit-sleep-stage-1
Description: "A shared sleep-stage output carries exactly one exact HealthKit sleep-analysis source coding, and no other output carries one."
Expression: "(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-sleep-analysis').count() = 1) or (code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').empty() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/healthkit/CodeSystem/healthkit-sleep-analysis').empty())"
Severity: #error

Profile: HealthKitObservation
Parent: GroveMobileObservation
Id: healthkit-observation
Title: "HealthKit Observation"
Description: "The source identity and allowlisted HealthKit context for an Observation that also conforms to an appropriate clinical or research profile."
* obeys healthkit-motion-context-1 and healthkit-sleep-stage-1
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains healthKitObjectId 1..1 MS
* identifier[healthKitObjectId] obeys healthkit-object-id-1
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value 1..1 MS
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains heartRateMotionContext 0..1 MS
* component[heartRateMotionContext].code = $healthKitMetadataKey#HKMetadataKeyHeartRateMotionContext
* component[heartRateMotionContext].value[x] 1..1 MS
* component[heartRateMotionContext].value[x] only CodeableConcept
* component[heartRateMotionContext].valueCodeableConcept from HealthKitHeartRateMotionContextVS (required)
* component[heartRateMotionContext].dataAbsentReason 0..0
