//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Examples exercising every artifact: a mobile sensor observation with contained
// sensor + gateway devices, and a questionnaire using the SDC + Grove hint vocabulary.

Instance: PolarH10SensorDevice
InstanceOf: GroveSensorDevice
Usage: #inline
* deviceName[userFriendlyName].name = "Polar H10 8D2A342B"
* deviceName[userFriendlyName].type = #user-friendly-name
* manufacturer = "Polar Electro Oy"
* modelNumber = "H10"
* type = GroveDeviceType#chest-strap "Chest Strap"
* identifier[deviceLocalId].system = $sidDeviceLocalId
* identifier[deviceLocalId].value = "1F3A9C6E-2B41-4D8A-9E37-6C5D0A28B914"
* udiCarrier.deviceIdentifier = "(01)06438525002332"
* version[hardware].type = $mdc#531974 "MDC_ID_PROD_SPEC_HW"
* version[hardware].value = "39027746.01"
* version[firmware].type = $mdc#531976 "MDC_ID_PROD_SPEC_FW"
* version[firmware].value = "3.0.35"
* version[software].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[software].value = "5.1.0"

Instance: WorkoutGatewayDevice
InstanceOf: GroveGatewayDevice
Usage: #inline
* deviceName[userFriendlyName].name = "Workout"
* deviceName[userFriendlyName].type = #user-friendly-name
* modelNumber = "Watch7,1"
* identifier[appleBundleId].system = "https://grovealliance.org/fhir/sid/apple-bundle-id"
* identifier[appleBundleId].value = "com.apple.health"
* version[application].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[application].value = "17.0.3"
* version[operatingSystem].type = GroveDeviceVersionType#operating-system "Operating System Version"
* version[operatingSystem].value = "11.2.0"

Instance: GroveHeartRateObservationExample
InstanceOf: GroveMobileSensorObservation
Usage: #example
Title: "Heart Rate Observation from a Mobile Platform"
Description: """
A heart-rate Observation as Grove creates it from a platform sample: LOINC-coded,
category vital-signs, the platform record UUID as an identifier, full-precision
effective time with the named zone, the recording chest strap as a contained
sensor Device, the saving app + OS as a contained gateway Device, and the capture
modality. The residual platform metadata carries the heart-rate motion context.
The study-revision extension records which deployment definition produced the sample.
"""
* meta.source = "https://grovealliance.org/fhir/source/healthkit"
* meta.tag[deviceType] = GroveDeviceType#chest-strap "Chest Strap"
* contained[0] = PolarH10SensorDevice
* contained[1] = WorkoutGatewayDevice
* identifier[healthKitSampleId].system = "https://grovealliance.org/fhir/sid/healthkit-sample-id"
* identifier[healthKitSampleId].value = "1E091E2A-9F3E-49CD-B237-2EF5A3D0F213"
* status = #final
* category = $obsCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectiveDateTime = "2026-08-13T10:30:00.251-07:00"
* effectiveDateTime.extension[0].url = "http://hl7.org/fhir/StructureDefinition/timezone"
* effectiveDateTime.extension[0].valueCode = #"America/Los_Angeles"
* valueQuantity = 72 '/min' "beats/minute"
* device = Reference(PolarH10SensorDevice)
* extension[gatewayDevice].valueReference = Reference(WorkoutGatewayDevice)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically Recorded"
* extension[studyRevision].valueString = "protocol-2026.08"
* extension[platformMetadata][0].extension[key].valueCoding.system = "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-metadata-key"
* extension[platformMetadata][0].extension[key].valueCoding.code = #HKMetadataKeyHeartRateMotionContext
* extension[platformMetadata][0].extension[value].valueCoding.system = "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-heart-rate-motion-context"
* extension[platformMetadata][0].extension[value].valueCoding.code = #sedentary
* extension[platformMetadata][0].extension[value].valueCoding.display = "sedentary"


Instance: GrovePatientExample
InstanceOf: Patient
Usage: #example
Title: "Example Research Participant"
Description: "A minimal research participant. The consuming application is responsible for Observation.subject."
* identifier.system = "https://example.org/fhir/participants"
* identifier.value = "participant-001"


Instance: GroveQuestionnaireExample
InstanceOf: GroveQuestionnaire
Usage: #example
Title: "Questionnaire with Cross-Platform Hints"
Description: """
A Questionnaire using the v2 hint vocabulary: validation via the HL7 targetConstraint
extension (FHIRPath + human message), keyboard via the SDC keyboard extension, autofill
and capitalization via the Grove WHATWG-token extensions, and an annotate-image item
whose base image travels in the SDC itemMedia extension with coded, colored regions.
"""
* status = #active
* name = "GroveExampleQuestionnaire"
* title = "Grove Example Questionnaire"
* url = "https://grovealliance.org/fhir/core/Questionnaire/GroveQuestionnaireExample"
* item[0].linkId = "email"
* item[0].type = #string
* item[0].text = "What is your email address?"
* item[0].extension[0].url = $targetConstraint
* item[0].extension[0].extension[0].url = "key"
* item[0].extension[0].extension[0].valueId = "email-format"
* item[0].extension[0].extension[1].url = "severity"
* item[0].extension[0].extension[1].valueCode = #error
* item[0].extension[0].extension[2].url = "expression"
* item[0].extension[0].extension[2].valueExpression.language = #text/fhirpath
* item[0].extension[0].extension[2].valueExpression.expression = "$this.matches('^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$')"
* item[0].extension[0].extension[3].url = "human"
* item[0].extension[0].extension[3].valueString = "Please enter a valid email address."
* item[0].extension[1].url = $sdcKeyboard
* item[0].extension[1].valueCoding.system = "http://hl7.org/fhir/uv/sdc/CodeSystem/keyboardType"
* item[0].extension[1].valueCoding.code = #email
* item[0].extension[2].url = "https://grovealliance.org/fhir/core/StructureDefinition/grove-autocomplete"
* item[0].extension[2].valueCode = #email
* item[0].extension[3].url = "https://grovealliance.org/fhir/core/StructureDefinition/grove-autocapitalize"
* item[0].extension[3].valueCode = #none
* item[1].linkId = "pain-location"
* item[1].type = #attachment
* item[1].text = "Mark where it hurts."
* item[1].extension[0].url = $itemControl
* item[1].extension[0].valueCodeableConcept.coding.system = "https://grovealliance.org/fhir/core/CodeSystem/grove-questionnaire-item-control"
* item[1].extension[0].valueCodeableConcept.coding.code = #annotate-image
* item[1].extension[1].url = $itemMedia
* item[1].extension[1].valueAttachment.contentType = #image/png
* item[1].extension[1].valueAttachment.data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
* item[1].extension[1].valueAttachment.title = "Body outline"
* item[1].extension[2].url = $mimeType
* item[1].extension[2].valueCode = #image/png
* item[1].extension[3].url = $maxSize
* item[1].extension[3].valueDecimal = 5242880
* item[1].extension[4].url = "https://grovealliance.org/fhir/core/StructureDefinition/grove-annotate-image-region"
* item[1].extension[4].extension[0].url = "label"
* item[1].extension[4].extension[0].valueString = "Left shoulder"
* item[1].extension[4].extension[1].url = "code"
* item[1].extension[4].extension[1].valueCoding = $sct#16982005 "Shoulder region structure"
* item[1].extension[4].extension[2].url = "color"
* item[1].extension[4].extension[2].valueCode = #red
* item[1].extension[5].url = "https://grovealliance.org/fhir/core/StructureDefinition/grove-annotate-image-region"
* item[1].extension[5].extension[0].url = "label"
* item[1].extension[5].extension[0].valueString = "Right shoulder"
* item[1].extension[5].extension[1].url = "color"
* item[1].extension[5].extension[1].valueCode = #blue


Instance: GrovePassthroughDocumentExample
InstanceOf: DocumentReference
Usage: #example
Title: "Clinical Record Passthrough with Source Record Identifier"
Description: """
A clinical document passed through from a platform record store. Its own `identifier`
list belongs to the originating institution, so the platform record id travels in the
source-record-id extension instead.
"""
* text.status = #generated
* text.div = "<div xmlns=\"http://www.w3.org/1999/xhtml\">Discharge summary (PDF), passed through from the platform record store; platform record id in the source-record-id extension.</div>"
* extension[0].url = "https://grovealliance.org/fhir/core/StructureDefinition/grove-source-record-id"
* extension[0].valueIdentifier.system = "https://grovealliance.org/fhir/sid/healthkit-sample-id"
* extension[0].valueIdentifier.value = "7C39C22B-4A95-4E12-8E1D-2D1A5B9C4F08"
* identifier.system = "urn:oid:2.16.840.1.113883.19.5"
* identifier.value = "doc-2026-000451"
* status = #current
* content.attachment.contentType = #application/pdf
* content.attachment.title = "Discharge summary"


Instance: PhoneSensorDevice
InstanceOf: GroveSensorDevice
Usage: #inline
Title: "iPhone as the Recording Sensor"
Description: "The phone hardware that counted the steps."
* id = "sensor-device"
* deviceName[userFriendlyName].name = "Leo's iPhone"
* deviceName[userFriendlyName].type = #user-friendly-name
* modelNumber = "iPhone17,2"
* type = GroveDeviceType#phone "Phone"
* version[hardware].type = $mdc#531974 "MDC_ID_PROD_SPEC_HW"
* version[hardware].value = "iPhone17,2"


Instance: PhoneGatewayDevice
InstanceOf: GroveGatewayDevice
Usage: #inline
Title: "Health App as the Saving Gateway"
Description: "The app-and-OS environment that saved the steps; the same physical phone as the sensor, in its gateway role."
* id = "gateway-device"
* deviceName[userFriendlyName].name = "Health"
* deviceName[userFriendlyName].type = #user-friendly-name
* identifier[appleBundleId].system = $sidAppleBundleId
* identifier[appleBundleId].value = "com.apple.Health"
* modelNumber = "iPhone17,2"
* version[operatingSystem].type = GroveDeviceVersionType#operating-system "Operating System Version"
* version[operatingSystem].value = "26.0.1"


Instance: GroveStepCountObservationExample
InstanceOf: GroveMobileSensorObservation
Usage: #example
Title: "Phone-Recorded Step Count"
Description: """
An hour of phone-counted steps. The phone appears twice — once as the recording
sensor, once (with the saving app) as the gateway — and the count carries the UCUM
`{steps}` annotation so the quantity stays coded.
"""
* meta.source = "https://grovealliance.org/fhir/source/healthkit"
* meta.tag[deviceType] = GroveDeviceType#phone "Phone"
* contained[0] = PhoneSensorDevice
* contained[1] = PhoneGatewayDevice
* identifier[healthKitSampleId].system = "https://grovealliance.org/fhir/sid/healthkit-sample-id"
* identifier[healthKitSampleId].value = "F1E2D3C4-4B5A-4C6D-8E9F-1234567890AB"
* status = #final
* category = $obsCategory#activity "Activity"
* code.coding[0] = $loinc#55423-8 "Number of steps in unspecified time Pedometer"
* code.coding[1].system = $platformHealthKitSampleType
* code.coding[1].code = #HKQuantityTypeIdentifierStepCount
* code.coding[1].display = "Step Count"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectivePeriod.start = "2026-08-12T09:00:00-07:00"
* effectivePeriod.end = "2026-08-12T10:00:00-07:00"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(PhoneSensorDevice)
* extension[gatewayDevice].valueReference = Reference(PhoneGatewayDevice)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically Recorded"


Instance: GroveSleepObservationExample
InstanceOf: GroveMobileSensorObservation
Usage: #example
Title: "Watch-Sensed REM Sleep Stage"
Description: """
A REM sleep interval: the HealthKit stage value paired with the parallel LOINC stage
code, so consumers aggregate stage durations without Apple-specific vocabulary.
"""
* identifier[healthKitSampleId].system = "https://grovealliance.org/fhir/sid/healthkit-sample-id"
* identifier[healthKitSampleId].value = "A9B8C7D6-1F2E-4D3C-8B9A-ABCDEF123456"
* status = #final
* code.coding[0].system = $platformHealthKitSampleType
* code.coding[0].code = #HKCategoryTypeIdentifierSleepAnalysis
* code.coding[0].display = "Sleep Analysis"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectivePeriod.start = "2026-08-12T02:14:00-07:00"
* effectivePeriod.end = "2026-08-12T02:41:00-07:00"
* valueCodeableConcept.coding[0].system = $platformSleepAnalysisValue
* valueCodeableConcept.coding[0].code = #asleepREM
* valueCodeableConcept.coding[0].display = "asleep REM"
* valueCodeableConcept.coding[1] = $loinc#93829-0 "REM sleep duration"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically Recorded"


Instance: GroveWearStateObservationExample
InstanceOf: GroveWearStateObservation
Usage: #example
Title: "Watch On-Wrist State"
Description: """
The watch is worn on the left wrist, crown facing right — the denominator observation
that lets consumers distinguish "no data" from "not worn".
"""
* meta.source = "https://grovealliance.org/fhir/source/sensorkit"
* meta.tag[deviceType] = GroveDeviceType#watch "Watch"
* identifier[sensorKitSampleId].system = $sidSensorKitSampleId
* identifier[sensorKitSampleId].value = "0D8E9F10-2A3B-4C5D-8E7F-99AA88BB77CC"
* status = #final
* code = GroveSensorKitSampleType#com.apple.SensorKit.onWristState "On-Wrist State"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectiveDateTime = "2026-08-12T07:02:11-07:00"
* valueCodeableConcept = GroveSensorKitValues#on-wrist "On Wrist"
* component[wristLocation].code = GroveSensorKitConcepts#wrist-location "Wrist Location"
* component[wristLocation].valueCodeableConcept = GroveSensorKitValues#left "Left"
* component[crownOrientation].code = GroveSensorKitConcepts#crown-orientation "Crown Orientation"
* component[crownOrientation].valueCodeableConcept = GroveSensorKitValues#right "Right"


Instance: GroveQuestionnaireResponseExample
InstanceOf: GroveQuestionnaireResponse
Usage: #example
Title: "Response to the Example Questionnaire"
Description: """
A completed response to ``GroveQuestionnaireExample``: question text carried on the
items, the capture mode recorded, and the annotate-image answer returned as an
attachment.
"""
* status = #completed
* questionnaire = "https://grovealliance.org/fhir/core/Questionnaire/GroveQuestionnaireExample"
* subject = Reference(GrovePatientExample)
* authored = "2026-08-12T18:30:00-07:00"
* extension[0].url = "http://hl7.org/fhir/StructureDefinition/questionnaireresponse-completionMode"
* extension[0].valueCodeableConcept.coding.system = "http://terminology.hl7.org/CodeSystem/v3-ParticipationMode"
* extension[0].valueCodeableConcept.coding.code = #ELECTRONIC
* extension[0].valueCodeableConcept.coding.display = "electronic data"
* item[0].linkId = "email"
* item[0].text = "What is your email address?"
* item[0].answer.valueString = "participant-001@example.org"
* item[1].linkId = "pain-location"
* item[1].text = "Mark where it hurts."
* item[1].answer.valueAttachment.contentType = #image/png
* item[1].answer.valueAttachment.data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
* item[1].answer.valueAttachment.title = "Annotated body outline"



Instance: GroveVisitObservationExample
InstanceOf: GroveVisitObservation
Usage: #example
Title: "SensorKit Visit"
Description: """
A gym visit: the location category and distance from home as components, arrival and
departure as the time windows SensorKit actually reports, and `effectivePeriod`
spanning the widest possible visit.
"""
* meta.source = "https://grovealliance.org/fhir/source/sensorkit"
* meta.tag[deviceType] = GroveDeviceType#phone "Phone"
* identifier[sensorKitSampleId].system = $sidSensorKitSampleId
* identifier[sensorKitSampleId].value = "3C4D5E6F-1234-4321-9876-DDEE11223344"
* status = #final
* code = GroveSensorKitSampleType#com.apple.SensorKit.visits "Visits"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectivePeriod.start = "2026-08-11T17:20:00-07:00"
* effectivePeriod.end = "2026-08-11T19:05:00-07:00"
* component[locationCategory].code = GroveSensorKitConcepts#visit-location-category "Visit Location Category"
* component[locationCategory].valueCodeableConcept = GroveSensorKitValues#gym "Gym"
* component[distanceFromHome].code = GroveSensorKitConcepts#distance-from-home "Distance From Home"
* component[distanceFromHome].valueQuantity = 2400 'm' "m"
* component[arrivalWindow].code = GroveSensorKitConcepts#arrival-window "Arrival Window"
* component[arrivalWindow].valuePeriod.start = "2026-08-11T17:20:00-07:00"
* component[arrivalWindow].valuePeriod.end = "2026-08-11T17:35:00-07:00"
* component[departureWindow].code = GroveSensorKitConcepts#departure-window "Departure Window"
* component[departureWindow].valuePeriod.start = "2026-08-11T18:50:00-07:00"
* component[departureWindow].valuePeriod.end = "2026-08-11T19:05:00-07:00"


Instance: GroveDeviceUsageObservationExample
InstanceOf: GroveDeviceUsageObservation
Usage: #example
Title: "SensorKit Device-Usage Summary"
Description: """
A device-usage reporting period: unlock duration as the value, wake and unlock counts
as components, and the per-app detail in the raw batch this observation derives from.
"""
* meta.source = "https://grovealliance.org/fhir/source/sensorkit"
* meta.tag[deviceType] = GroveDeviceType#phone "Phone"
* identifier[sensorKitSampleId].system = $sidSensorKitSampleId
* identifier[sensorKitSampleId].value = "7A8B9C0D-4444-4555-8666-FF0011223344"
* status = #final
* code = GroveSensorKitSampleType#com.apple.SensorKit.deviceUsageReport "Device Usage"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectivePeriod.start = "2026-08-12T00:00:00-07:00"
* effectivePeriod.end = "2026-08-12T00:15:00-07:00"
* valueQuantity = 372 's' "seconds"
* component[screenWakes].code = GroveSensorKitConcepts#screen-wakes "Screen Wakes"
* component[screenWakes].valueQuantity = 6 '{count}' "wakes"
* component[unlocks].code = GroveSensorKitConcepts#unlocks "Unlocks"
* component[unlocks].valueQuantity = 4 '{count}' "unlocks"
* derivedFrom = Reference(GroveSensorBatchDocumentExample)


Instance: GroveSensorBatchDocumentExample
InstanceOf: GroveSensorBatchDocument
Usage: #example
Title: "Raw Device-Usage Batch"
Description: """
The raw per-app, per-notification and per-web-domain detail behind the device-usage
summary, shipped as a gzip-compressed CSV sidecar file. `contentType` is the media type
once decompressed, `format` records the gzip, and `hash` and `size` are the SHA-1 and
byte length of the stored `.csv.gz` itself, so a consumer verifies the file it fetched
before decompressing it.
"""
* status = #current
* type = GroveSensorKitSampleType#com.apple.SensorKit.deviceUsageReport "Device Usage"
* subject = Reference(GrovePatientExample)
* date = "2026-08-12T06:00:00-07:00"
* content.attachment.contentType = #text/csv
* content.attachment.url = "https://uploads.example.org/grove/batches/device-usage-2026-08-12.csv.gz"
* content.attachment.hash = "gk4xc7f+FUeBNQ4mGbAL5vlQZFs="
* content.attachment.size = 688
* content.format = GroveSensorBatchFormatCS#csv-gzip "CSV, gzip-compressed"


Instance: AndroidSensorDevice
InstanceOf: GroveSensorDevice
Usage: #inline
Title: "Android Phone (Recording Sensor)"
Description: "The phone whose pedometer counted the steps, as Health Connect reports it."
* deviceName[userFriendlyName].name = "Pixel 9 Pro"
* deviceName[userFriendlyName].type = #user-friendly-name
* manufacturer = "Google"
* modelNumber = "GTA1"
* type = GroveDeviceType#phone "Phone"


Instance: AndroidGatewayDevice
InstanceOf: GroveGatewayDevice
Usage: #inline
Title: "Android App (Gateway)"
Description: "The app that read the record out of Health Connect and uploaded it."
* deviceName[userFriendlyName].name = "Study App"
* deviceName[userFriendlyName].type = #user-friendly-name
* identifier[androidApplicationId].system = "https://grovealliance.org/fhir/sid/android-application-id"
* identifier[androidApplicationId].value = "org.grovealliance.studyapp"
* version[operatingSystem].type = GroveDeviceVersionType#operating-system "Operating System Version"
* version[operatingSystem].value = "16"


Instance: GroveHealthConnectStepCountExample
InstanceOf: GroveMobileSensorObservation
Usage: #example
Title: "Health Connect Step Count"
Description: """
The same measurement as the HealthKit step-count example, recorded on Android. Only the
identifier system and the platform coding differ — which is the point of a
platform-neutral guide, and the reason the identifier slices are Must Support rather
than fixed to one vendor.
"""
* meta.source = "https://grovealliance.org/fhir/source/health-connect"
* meta.tag[deviceType] = GroveDeviceType#phone "Phone"
* contained[0] = AndroidSensorDevice
* contained[1] = AndroidGatewayDevice
* identifier[healthConnectRecordId].system = "https://grovealliance.org/fhir/sid/health-connect-record-id"
* identifier[healthConnectRecordId].value = "2b1f5f4e-9a3c-4d7e-8f10-6c5b4a3d2e1f"
* status = #final
* category = $obsCategory#activity "Activity"
* code.coding[0] = $loinc#55423-8 "Number of steps in unspecified time Pedometer"
* code.coding[1].system = "https://grovealliance.org/fhir/platforms/CodeSystem/health-connect-record-type"
* code.coding[1].code = #StepsRecord
* code.coding[1].display = "Steps"
* subject = Reference(GrovePatientExample)
* performer = Reference(GrovePatientExample)
* effectivePeriod.start = "2026-08-12T09:00:00-07:00"
* effectivePeriod.end = "2026-08-12T10:00:00-07:00"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(AndroidSensorDevice)
* extension[gatewayDevice].valueReference = Reference(AndroidGatewayDevice)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically Recorded"
