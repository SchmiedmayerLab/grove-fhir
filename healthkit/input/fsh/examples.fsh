//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: HealthKitPatientExample
InstanceOf: Patient
Usage: #example
Title: "HealthKit Example Participant"
Description: "The Patient referenced by the HealthKit adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-hk-001"

Instance: HealthKitStudyPlanExample
InstanceOf: PlanDefinition
Usage: #example
Title: "HealthKit Study Protocol"
Description: "The versioned study protocol governing the HealthKit example collection."
* url = "https://study.example.org/fhir/PlanDefinition/healthkit-study-protocol"
* version = "2026.08"
* name = "HealthKitStudyProtocol"
* title = "HealthKit Study Protocol"
* status = #active
* experimental = false
* date = "2026-08-19"
* publisher = "Example Study"
* description = "Collect heart rate, step count, and manually entered body weight from HealthKit."

Instance: HealthKitResearchStudyExample
InstanceOf: ResearchStudy
Usage: #example
Title: "HealthKit Research Study"
Description: "A ResearchStudy whose protocol references the exact PlanDefinition revision used for collection."
* identifier.system = "https://study.example.org/fhir/identifiers/research-study"
* identifier.value = "healthkit-study"
* title = "Example HealthKit Study"
* protocol = Reference(HealthKitStudyPlanExample)
* status = #active

Instance: HealthKitResearchSubjectExample
InstanceOf: ResearchSubject
Usage: #example
Title: "HealthKit Research Subject"
Description: "The participant's enrollment in the HealthKit example study."
* identifier.system = "https://study.example.org/fhir/identifiers/research-subject"
* identifier.value = "healthkit-study-participant-hk-001"
* status = #on-study
* period.start = "2026-08-01"
* study = Reference(HealthKitResearchStudyExample)
* individual = Reference(HealthKitPatientExample)

Instance: HealthKitRecordingDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "HealthKit Recording Device"
Description: "The watch reported by HealthKit as the physical recorder for the passive examples."
* status = #active
* deviceName.name = "Study Watch"
* deviceName.type = #user-friendly-name
* manufacturer = "Apple Inc."
* modelNumber = "Watch"
* type.text = "Wrist-worn sensor"
* version.type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version.value = "11.2"

Instance: HealthKitApplicationDeviceExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "HealthKit Converting Application"
Description: "The application that read the HealthKit objects and transformed them into FHIR resources. It is a Provenance agent, not the recording device."
* status = #active
* identifier.system = $appleBundleId
* identifier.value = "org.grovealliance.example"
* deviceName[applicationName].name = "Grove Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "1.4.0"

Instance: HealthKitSourceApplicationDeviceExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "HealthKit Source Application"
Description: "The application reported by HKSourceRevision as the author of the source HealthKit object. It is distinct from the application that converted the object to FHIR."
* status = #active
* identifier.system = $appleBundleId
* identifier.value = "com.example.health-source"
* deviceName[applicationName].name = "Example Health Source"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "4.7.2"

Instance: HealthKitBluetoothSourceDeviceExample
InstanceOf: Device
Usage: #example
Title: "HealthKit Bluetooth Source Device"
Description: "A supported Bluetooth Low Energy source explicitly classified by the producer. Its opaque HealthKit source identifier is included only under an authorized exchange policy."
* status = #active
* identifier.system = $healthKitSourceDeviceId
* identifier.value = "c614cf5b-8a89-4a50-a5c8-78c1a8397f63"
* deviceName.name = "Example Bluetooth Source"
* deviceName.type = #user-friendly-name

Instance: HealthKitHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Heart Rate"
Description: "A passive HealthKit heart-rate sample with the standard clinical profile and an allowlisted motion-context value."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "1e091e2a-9f3e-49cd-b237-2ef5a3d0f213"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierHeartRate "Heart Rate"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00.251-07:00"
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 72 '/min' "beats/minute"
* device = Reference(HealthKitRecordingDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)
* component[heartRateMotionContext].code = $healthKitMetadataKey#HKMetadataKeyHeartRateMotionContext "Heart Rate Motion Context"
* component[heartRateMotionContext].valueCodeableConcept = $healthKitHeartRateMotionContext#sedentary "Sedentary"

Instance: HealthKitRevisedBodyWeightObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Revised Body Weight"
Description: "A body-weight sample a connected scale re-imported after correcting it. HealthKit replaced the earlier object, so this Observation carries a new object identifier, the unchanged sync identifier that names the measurement, and the higher sync version that supersedes the previous one."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "7c3f9b41-58d2-4e6a-9a10-4b8e2f6d05c7"
* identifier[healthKitSyncId].system = $healthKitSyncId
* identifier[healthKitSyncId].value = "scale-weighin-2026-08-19"
* extension[syncVersion].valueInteger = 2
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierBodyMass "Body Mass"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T07:12:00.000-07:00"
* issued = "2026-08-20T08:00:00.000Z"
* valueQuantity = 68.9 'kg' "kg"
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitStepCountObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Step Count"
Description: "A HealthKit interval sample preserving the recorded count of 1,042 steps over one hour."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "f1e2d3c4-4b5a-4c6d-8e9f-1234567890ab"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#step-count-total "Step count total"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierStepCount "Step Count"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T09:00:00-07:00"
* effectivePeriod.end = "2026-08-19T10:00:00-07:00"
* issued = "2026-08-19T17:30:02.000Z"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(HealthKitRecordingDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitBluetoothHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Bluetooth Heart Rate"
Description: "A heart-rate sample imported directly from a supported Bluetooth Low Energy heart-rate monitor under an exchange policy that permits the source identifier."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "d7f395c0-7e4a-4eb8-943d-5e32dc70071a"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierHeartRate "Heart Rate"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:45:00.251-07:00"
* issued = "2026-08-19T17:45:02.000Z"
* valueQuantity = 78 '/min' "beats/minute"
* device = Reference(HealthKitBluetoothSourceDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitManuallyEnteredBodyWeightExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Manually Entered Body Weight"
Description: "A body weight with an explicit HealthKit user-entered indication mapped to manual-entry."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "a4b6fbcd-a358-4b2b-bea5-eb1ed80a8a63"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierBodyMass "Body Mass"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T08:15:00-07:00"
* issued = "2026-08-19T15:15:01.000Z"
* valueQuantity = 68.4 'kg' "kg"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#manual-entry "Manual entry"
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitBloodPressureObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Blood Pressure"
Description: "A HealthKit blood-pressure correlation whose result is carried by the required systolic and diastolic components rather than Observation.value."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "b2081271-af21-4aac-9c43-921e536e0742"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#85354-9 "Blood pressure panel with all children optional"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKCorrelationTypeIdentifierBloodPressure "Blood Pressure"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T08:20:00-07:00"
* issued = "2026-08-19T15:20:01Z"
* component[+].code = $loinc#8480-6 "Systolic blood pressure"
* component[=].valueQuantity = 118 'mm[Hg]' "mmHg"
* component[+].code = $loinc#8462-4 "Diastolic blood pressure"
* component[=].valueQuantity = 76 'mm[Hg]' "mmHg"
* device = Reference(HealthKitRecordingDeviceExample)

Instance: HealthKitSleepStageObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Sleep Stage"
Description: "A HealthKit asleep-core interval retaining both the shared light-sleep meaning and the exact HealthKit source case."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-stage"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "6d4e94ef-0cdb-4930-982f-6fa4501b3e8b"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#sleep-stage "Sleep stage"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKCategoryTypeIdentifierSleepAnalysis "Sleep Analysis"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T23:10:00-07:00"
* effectivePeriod.end = "2026-08-19T23:42:00-07:00"
* issued = "2026-08-20T07:00:01Z"
* valueCodeableConcept.coding[+] = $groveSleepStage#light "Light sleep"
* valueCodeableConcept.coding[+] = $healthKitSleepAnalysis#asleepCore "Asleep, core"
* device = Reference(HealthKitRecordingDeviceExample)

Instance: HealthKitECGObservationExample
InstanceOf: HealthKitECGObservation
Usage: #example
Title: "HealthKit Lead-I-like ECG"
Description: "A caller-supplied HealthKit ECG with a complete uniformly sampled voltage series and exact classification, symptom, sampling, and count context. The adapter performs no HealthKit query."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "055f8cb3-e48f-445b-a629-388c3e38caa9"
* status = #final
* category = $observationCategory#procedure "Procedure"
* code = $loinc#11524-6 "EKG study"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKDataTypeIdentifierElectrocardiogram "ECG"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T10:50:00.002-07:00"
* effectivePeriod.end = "2026-08-19T10:50:00.008-07:00"
* issued = "2026-08-19T17:50:01Z"
* extension[healthKitECGClassification].valueCode = #sinusRhythm
* extension[healthKitECGSymptomsStatus].valueCode = #present
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceIdentifier].valueIdentifier.system = $healthKitObjectId
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceIdentifier].valueIdentifier.value = "ad32cfc5-025a-493e-bc1b-85378817ac1c"
* extension[healthKitECGCorrelatedSymptom][0].extension[effectivePeriod].valuePeriod.start = "2026-08-19T10:49:55-07:00"
* extension[healthKitECGCorrelatedSymptom][0].extension[effectivePeriod].valuePeriod.end = "2026-08-19T10:50:05-07:00"
* extension[healthKitECGCorrelatedSymptom][0].extension[symptomType].valueCode = #HKCategoryTypeIdentifierDizziness
* extension[healthKitECGCorrelatedSymptom][0].extension[severity].valueCode = #mild
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceName].valueString = "Grove Health"
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceBundleIdentifier].valueString = "org.grovealliance.health"
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceVersion].valueString = "2.0.0"
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceProductType].valueString = "Watch6,4"
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceOperatingSystemMajorVersion].valueInteger = 12
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceOperatingSystemMinorVersion].valueInteger = 0
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceOperatingSystemPatchVersion].valueInteger = 1
* extension[healthKitECGAverageHeartRate].valueQuantity = 72 '/min' "beats/minute"
* extension[healthKitECGSamplingFrequency].valueQuantity = 500 'Hz' "Hz"
* extension[healthKitECGVoltageMeasurementCount].valueInteger = 4
* extension[healthKitECGAlgorithmVersion].valueCode = #version2
* extension[healthKitECGSourcePeriod].valuePeriod.start = "2026-08-19T10:50:00.000-07:00"
* extension[healthKitECGSourcePeriod].valuePeriod.end = "2026-08-19T10:50:00.010-07:00"
* component[voltage].code = $mdc#131329 "MDC_ECG_ELEC_POTL_I"
* component[voltage].valueSampledData.origin.value = 0
* component[voltage].valueSampledData.origin.system = $ucum
* component[voltage].valueSampledData.origin.code = #mV
* component[voltage].valueSampledData.period = 2
* component[voltage].valueSampledData.dimensions = 1
* component[voltage].valueSampledData.data = "0.012 0.021 -0.004 0.016"
* device = Reference(HealthKitRecordingDeviceExample)

Instance: HealthKitConversionProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit Conversion Provenance"
Description: "The application transformed the HealthKit object identified as the source entity into the heart-rate Observation."
* target = Reference(HealthKitHeartRateObservationExample)
* occurredDateTime = "2026-08-19T10:30:02-07:00"
* recorded = "2026-08-19T17:30:02.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value = "1e091e2a-9f3e-49cd-b237-2ef5a3d0f213"
* entity.agent.type = $provenanceParticipantType#author "Author"
* entity.agent.who = Reference(HealthKitSourceApplicationDeviceExample)

Instance: HealthKitStepCountConversionProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit Step Count Conversion Provenance"
Description: "The application transformed the exact HealthKit step-count object identified as the source entity."
* target = Reference(HealthKitStepCountObservationExample)
* occurredDateTime = "2026-08-19T10:00:02-07:00"
* recorded = "2026-08-19T17:30:02.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value = "f1e2d3c4-4b5a-4c6d-8e9f-1234567890ab"
* entity.agent.type = $provenanceParticipantType#author "Author"
* entity.agent.who = Reference(HealthKitSourceApplicationDeviceExample)

Instance: HealthKitBluetoothSourceProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit Bluetooth Source Provenance"
Description: "A producer-supplied Bluetooth heart-rate monitor authored the HealthKit object transformed into the Bluetooth heart-rate Observation."
* target = Reference(HealthKitBluetoothHeartRateObservationExample)
* occurredDateTime = "2026-08-19T10:45:02-07:00"
* recorded = "2026-08-19T17:45:02.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value = "d7f395c0-7e4a-4eb8-943d-5e32dc70071a"
* entity.agent.type = $provenanceParticipantType#author "Author"
* entity.agent.who = Reference(HealthKitBluetoothSourceDeviceExample)

Instance: HealthKitStudyBundleExample
InstanceOf: Bundle
Usage: #example
Title: "HealthKit Study Documentation Bundle"
Description: "A documentation collection of the participant, versioned protocol, study enrollment, devices, converted Observations, and conversion Provenance. It is not an operational exchange bundle: a conformant exchange uses the GroveMobileExchangeBundle profile with deterministic urn:uuid full URLs, a Bundle identifier, and entry identifier extensions, as shown in the Mobile guide's exchange example."
* type = #collection
* timestamp = "2026-08-19T17:30:03.000Z"
* entry[+].fullUrl = "https://study.example.org/fhir/Patient/HealthKitPatientExample"
* entry[=].resource = HealthKitPatientExample
* entry[+].fullUrl = "https://study.example.org/fhir/PlanDefinition/HealthKitStudyPlanExample"
* entry[=].resource = HealthKitStudyPlanExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchStudy/HealthKitResearchStudyExample"
* entry[=].resource = HealthKitResearchStudyExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchSubject/HealthKitResearchSubjectExample"
* entry[=].resource = HealthKitResearchSubjectExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitRecordingDeviceExample"
* entry[=].resource = HealthKitRecordingDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitApplicationDeviceExample"
* entry[=].resource = HealthKitApplicationDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitSourceApplicationDeviceExample"
* entry[=].resource = HealthKitSourceApplicationDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthKitHeartRateObservationExample"
* entry[=].resource = HealthKitHeartRateObservationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthKitStepCountObservationExample"
* entry[=].resource = HealthKitStepCountObservationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthKitConversionProvenanceExample"
* entry[=].resource = HealthKitConversionProvenanceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthKitStepCountConversionProvenanceExample"
* entry[=].resource = HealthKitStepCountConversionProvenanceExample

Instance: HealthKitExchangeHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "Exchange Heart Rate Observation"
Description: "The converter's heart-rate output for one HealthKit sample without an HKDevice. The subject is the caller-supplied literal Patient reference; the object UUID is the sole business identifier."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[healthKitObjectId].system = $healthKitObjectId
* identifier[healthKitObjectId].value = "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierHeartRate "Heart Rate"
* subject.reference = "https://study.example.org/fhir/Patient/participant-hk-001"
* performer.reference = "https://study.example.org/fhir/Patient/participant-hk-001"
* effectiveDateTime = "2026-08-20T09:12:45.128-07:00"
* issued = "2026-08-20T16:12:47.000Z"
* valueQuantity = 76 '/min' "beats/minute"

Instance: HealthKitExchangeConversionProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "Exchange Conversion Provenance"
Description: "Conversion provenance whose target and assembler resolve through the deterministic Bundle UUID URNs and whose sole source entity is the HealthKit object identifier."
* target.reference = "urn:uuid:697f6d32-7fb0-54d3-ba0e-8d933f6e5457"
* occurredDateTime = "2026-08-20T09:12:47-07:00"
* recorded = "2026-08-20T16:12:47.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who.reference = "urn:uuid:88912f8b-fd4e-51f9-8a72-ab97fde584d9"
* entity.role = #source
* entity.what.identifier.system = $healthKitObjectId
* entity.what.identifier.value = "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f"

Instance: HealthKitExchangeBundleExample
InstanceOf: GroveMobileExchangeBundle
Usage: #example
Title: "HealthKit Exchange Bundle"
Description: "The complete graph one heart-rate conversion uploads: the Observation, the converting application, and the conversion Provenance under deterministic UUIDv5 full URLs and graph-namespace identifiers."
* identifier.system = "https://study.example.org/fhir/identifiers/mobile-graph"
* identifier.value = "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f|exchange-bundle"
* type = #collection
* timestamp = "2026-08-20T16:12:47.000Z"
* entry[0].extension[entryIdentifier].valueIdentifier.system = $healthKitObjectId
* entry[0].extension[entryIdentifier].valueIdentifier.value = "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f"
* entry[0].fullUrl = "urn:uuid:697f6d32-7fb0-54d3-ba0e-8d933f6e5457"
* entry[0].resource = HealthKitExchangeHeartRateObservationExample
* entry[1].extension[entryIdentifier].valueIdentifier.system = $appleBundleId
* entry[1].extension[entryIdentifier].valueIdentifier.value = "org.grovealliance.example"
* entry[1].fullUrl = "urn:uuid:88912f8b-fd4e-51f9-8a72-ab97fde584d9"
* entry[1].resource = HealthKitApplicationDeviceExample
* entry[2].extension[entryIdentifier].valueIdentifier.system = "https://study.example.org/fhir/identifiers/mobile-graph"
* entry[2].extension[entryIdentifier].valueIdentifier.value = "9a2f4d6e-1c3b-4f8a-b7d0-5e6a8c9b0d1f|conversion-provenance"
* entry[2].fullUrl = "urn:uuid:16d49bf9-a6dc-58da-bc29-7146da34831c"
* entry[2].resource = HealthKitExchangeConversionProvenanceExample

Instance: HealthKitClinicalRecordDocumentExample
InstanceOf: HealthKitClinicalRecordDocument
Usage: #example
Title: "HealthKit Clinical Record Pass-Through"
Description: "One provider-issued clinical resource surfaced by HealthKit and byte-preserved in its declared FHIR release. Grove asserts identity and provenance over the envelope, never conformance over the issuer's resource."
* identifier[+].system = $healthKitObjectId
* identifier[=].value = "3c7f1a90-24f6-4a2c-9d55-6f1c0a1de4b7"
* extension[fhirRelease].valueCode = #r4
* status = #current
* type = HealthKitClinicalRecordTypeCS#allergy-record "Allergy record"
* subject = Reference(HealthKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* content.attachment.contentType = #application/fhir+json
* content.format = $recordingFormat#fhir-resource-1 "FHIR Resource 1"
* content.attachment.title = "Provider-issued AllergyIntolerance"
* content.attachment.data = "eyJyZXNvdXJjZVR5cGUiOiJBbGxlcmd5SW50b2xlcmFuY2UiLCJpZCI6InByb3ZpZGVyLWlzc3VlZC0xIiwiY2xpbmljYWxTdGF0dXMiOnsiY29kaW5nIjpbeyJzeXN0ZW0iOiJodHRwOi8vdGVybWlub2xvZ3kuaGw3Lm9yZy9Db2RlU3lzdGVtL2FsbGVyZ3lpbnRvbGVyYW5jZS1jbGluaWNhbCIsImNvZGUiOiJhY3RpdmUifV19LCJwYXRpZW50Ijp7InJlZmVyZW5jZSI6IlBhdGllbnQvcGFydGljaXBhbnQtaGstMDAxIn19"
* content.attachment.size = 240
* content.attachment.hash = "0c+dHXDzCV5zPy4cApwAoV9evYc="
