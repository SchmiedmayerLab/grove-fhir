//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Examples mirroring the exact wire format Grove produces — including the absolute
// sub-extension URLs the HealthKit builders write.

Instance: GroveHeartRateObservationExample
InstanceOf: Observation
Usage: #example
Title: "Heart Rate Observation from HealthKit"
Description: """
A heart-rate Observation as Grove creates it from an `HKQuantitySample`: LOINC-coded,
carrying the source device, source revision, HealthKit metadata, absolute time range,
and originating sample UUID.
"""
* status = #final
* category = http://terminology.hl7.org/CodeSystem/observation-category#vital-signs "Vital Signs"
* code = http://loinc.org#8867-4 "Heart rate"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectiveDateTime = "2026-08-13T10:30:00-07:00"
* valueQuantity = 72 '/min' "beats/minute"
* extension[0].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice"
* extension[0].extension[0].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/name"
* extension[0].extension[0].valueString = "Polar H10 8D2A342B"
* extension[0].extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/manufacturer"
* extension[0].extension[1].valueString = "Polar Electro Oy"
* extension[0].extension[2].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/model"
* extension[0].extension[2].valueString = "H10"
* extension[0].extension[3].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/hardwareVersion"
* extension[0].extension[3].valueString = "39027746.01"
* extension[0].extension[4].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/firmwareVersion"
* extension[0].extension[4].valueString = "3.0.35"
* extension[0].extension[5].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/softwareVersion"
* extension[0].extension[5].valueString = "5.1.0"
* extension[0].extension[6].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/localIdentifier"
* extension[0].extension[6].valueString = "1F3A9C6E-2B41-4D8A-9E37-6C5D0A28B914"
* extension[0].extension[7].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/udiDeviceIdentifier"
* extension[0].extension[7].valueString = "(01)06438525002332"
* extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision"
* extension[1].extension[0].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source"
* extension[1].extension[0].extension[0].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/name"
* extension[1].extension[0].extension[0].valueString = "Workout"
* extension[1].extension[0].extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/bundleIdentifier"
* extension[1].extension[0].extension[1].valueString = "com.apple.health"
* extension[1].extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/version"
* extension[1].extension[1].valueString = "17.0.3"
* extension[1].extension[2].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/productType"
* extension[1].extension[2].valueString = "Watch7,1"
* extension[1].extension[3].url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/OSVersion"
* extension[1].extension[3].valueString = "11.2.0"
* extension[2].url = "https://grovealliance.org/fhir/core/StructureDefinition/metadata"
* extension[2].extension[0].url = "https://grovealliance.org/fhir/core/StructureDefinition/metadata/HKMetadataKeyHeartRateMotionContext"
* extension[2].extension[0].valueCoding.system = "https://developer.apple.com/documentation/healthkit/hkheartratemotioncontext"
* extension[2].extension[0].valueCoding.code = #1
* extension[2].extension[0].valueCoding.display = "sedentary"
* extension[2].extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/metadata/HKWasUserEntered"
* extension[2].extension[1].valueBoolean = false
* extension[3].url = "https://grovealliance.org/fhir/core/StructureDefinition/absoluteTimeRangeStart"
* extension[3].valueDecimal = 1786988700.251
* extension[4].url = "https://grovealliance.org/fhir/core/StructureDefinition/absoluteTimeRangeEnd"
* extension[4].valueDecimal = 1786988760.251
* extension[5].url = "https://grovealliance.org/fhir/core/StructureDefinition/healthKitSampleId"
* extension[5].valueId = "1E091E2A-9F3E-49CD-B237-2EF5A3D0F213"


Instance: GrovePatientExample
InstanceOf: Patient
Usage: #example
Title: "Example Research Participant"
Description: """
A minimal research participant. Grove itself does not populate `Observation.subject` or
`Observation.category` — the consuming application is responsible for both; core FHIR
requires them on vital-signs observations.
"""
* identifier.system = "https://example.org/fhir/participants"
* identifier.value = "participant-001"


Instance: GroveQuestionnaireExample
InstanceOf: Questionnaire
Usage: #example
Title: "Questionnaire with Grove Rendering Hints"
Description: """
A Questionnaire using Grove's iOS rendering hints and the annotate-image item control,
exactly as Grove's questionnaire renderer reads them.
"""
* status = #active
* name = "GroveExampleQuestionnaire"
* title = "Grove Example Questionnaire"
* url = "https://grovealliance.org/fhir/core/Questionnaire/GroveQuestionnaireExample"
* item[0].linkId = "email"
* item[0].type = #string
* item[0].text = "What is your email address?"
* item[0].extension[0].url = "http://hl7.org/fhir/StructureDefinition/regex"
* item[0].extension[0].valueString = "^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
* item[0].extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/validationText"
* item[0].extension[1].valueString = "Please enter a valid email address."
* item[0].extension[2].url = "https://grovealliance.org/fhir/core/StructureDefinition/iosKeyboardType"
* item[0].extension[2].valueString = "emailAddress"
* item[0].extension[3].url = "https://grovealliance.org/fhir/core/StructureDefinition/iosTextContentType"
* item[0].extension[3].valueString = "emailAddress"
* item[0].extension[4].url = "https://grovealliance.org/fhir/core/StructureDefinition/iosAutocapitalizationType"
* item[0].extension[4].valueString = "none"
* item[1].linkId = "pain-location"
* item[1].type = #attachment
* item[1].text = "Mark where it hurts."
* item[1].extension[0].url = "http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl"
* item[1].extension[0].valueCodeableConcept.coding.system = "https://grovealliance.org/fhir/core/CodeSystem/questionnaire-item-control"
* item[1].extension[0].valueCodeableConcept.coding.code = #annotate-image
* item[1].extension[1].url = "https://grovealliance.org/fhir/core/StructureDefinition/annotateImageInputImage"
* item[1].extension[1].valueString = "body-outline.png"
* item[1].extension[2].url = "https://grovealliance.org/fhir/core/StructureDefinition/annotateImageRegion"
* item[1].extension[2].extension[0].url = "label"
* item[1].extension[2].extension[0].valueString = "Left shoulder"
* item[1].extension[2].extension[1].url = "color"
* item[1].extension[2].extension[1].valueString = "red"
* item[1].extension[3].url = "https://grovealliance.org/fhir/core/StructureDefinition/annotateImageRegion"
* item[1].extension[3].extension[0].url = "label"
* item[1].extension[3].extension[0].valueString = "Right shoulder"
* item[1].extension[3].extension[1].url = "color"
* item[1].extension[3].extension[1].valueString = "blue"
