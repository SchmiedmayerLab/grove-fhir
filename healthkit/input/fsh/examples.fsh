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
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v2/test-key/1"
* identifier[physicalUnit].value = "v2:test-key:1:Gc-nfLagscJENC57Nb98pCgbEYL9yc05MhJmZ1ZcMQs"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[eventSnapshot].value = "v2:test-key:1:a_nrcw7QmbxwDdFGGKMkaoNN2UKFgLL_kD3ccDWMQV0"
* status = #active
* deviceName.name = "Study Watch"
* deviceName.type = #user-friendly-name
* manufacturer = "Apple Inc."
* modelNumber = "Watch"
* type.text = "Wrist-worn sensor"
* version.type = $mdc#531976 "MDC_ID_PROD_SPEC_FW"
* version.value = "11.2"

Instance: HealthKitApplicationDeviceExample
InstanceOf: HealthKitApplicationDevice
Usage: #example
Title: "HealthKit Converting Application"
Description: "The application that read the HealthKit objects and transformed them into FHIR resources. It is a Provenance agent, not the recording device."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:Kuh8jiUIXu00ygR0PaXKv913Ng1pvnx1QmUT8dGIFT8"
* identifier[appleBundleId].system = $appleBundleId
* identifier[appleBundleId].value = "org.grovealliance.example"
* deviceName[applicationName].name = "Grove Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "1.4.0"
* version[applicationBuild].type = $groveApplicationVersionType#build "Build"
* version[applicationBuild].value = "140"
* parent = Reference(HealthKitHostDeviceExample)

Instance: HealthKitHostDeviceExample
InstanceOf: GroveHostDevice
Usage: #example
Title: "HealthKit Host Device Snapshot"
Description: "The immutable event-time phone hardware and operating-system snapshot hosting the converting application."
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier.value = "v2:test-key:1:yKtvFq9rJwWlXpqWr1uD3ACh3dz7qah2BH_QnQ2d_7U"
* status = #active
* manufacturer = "Apple Inc."
* modelNumber = "Example Phone"
* deviceName.name = "Study Phone"
* deviceName.type = #user-friendly-name
* type.text = "iOS host device"
* version[operatingSystemVersion].type = $groveApplicationVersionType#os-version "Operating system version"
* version[operatingSystemVersion].value = "20.1"

Instance: HealthKitSourceApplicationDeviceExample
InstanceOf: HealthKitApplicationDevice
Usage: #example
Title: "HealthKit Source Application"
Description: "The application reported by HKSourceRevision as the author of the source HealthKit object. It is distinct from the application that converted the object to FHIR."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:0jm5gNEShO3LSNkKzxMTMtht2wAfvtDuuuxf3RFE0VI"
* identifier[appleBundleId].system = $appleBundleId
* identifier[appleBundleId].value = "com.example.health-source"
* deviceName[applicationName].name = "Example Health Source"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "4.7.2"

Instance: HealthKitBluetoothSourceDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "HealthKit Bluetooth Source Device"
Description: "A supported Bluetooth Low Energy source explicitly classified by the producer after the caller supplied an authorized stable per-unit token. Only deployment-scoped HMAC identities are exchanged."
* status = #active
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v2/test-key/1"
* identifier[physicalUnit].value = "v2:test-key:1:0Fu9Y-KoyDjbxu2PwfDuZB8Erhsh8gphm6Tt5FbKnNU"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[eventSnapshot].value = "v2:test-key:1:h84aFtuFuX1HgXDVFFcaaMNNvZI8t8Oks5Spfh374lU"
* deviceName.name = "Example Bluetooth Source"
* deviceName.type = #user-friendly-name

Instance: HealthKitHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Heart Rate"
Description: "A passive HealthKit heart-rate sample with the standard clinical profile and an allowlisted motion-context value."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:2LnL2_8DgGsZjeX6FiAKlO9JhhFmX7GYJxaMvLGay9k"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:T_TL24HHsbiJz6bM9kC7_uu59s4qFbTtxtRaOwfBFF4"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierHeartRate "Heart Rate"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:30:00.251-07:00"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:JqoK2ok7RY8ioRdSmitZxfJP5dP8QHkTisJN7Fy8C14"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ghrfu1IHSwoJoNZPFICuMdEsrvMnjQVS56vFp7DJE9Y"
* identifier[writerRecord].system = "https://study.example.org/fhir/NamingSystem/grove-writer-record-v2/test-key/1"
* identifier[writerRecord].value = "v2:test-key:1:b6CrOt2Bn8qBpBi_0IesPTPhIzN5DbRQLPz_Di3GfSQ"
* extension[writerRecordVersion].valueString = "2"
* status = #amended
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierBodyMass "Body Mass"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T07:12:00.000-07:00"
* valueQuantity = 68.9 'kg' "kg"
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitStepCountObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Step Count"
Description: "A HealthKit interval sample preserving the recorded count of 1,042 steps over one hour."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:WE2iuX55Ut-MR8aQ6B3LSsxOnf5PIY_m5G4jcj2proo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:r7g26sWzU-JpvzbKhTmtnwkdCnvgy7upa1Nn3WmGYwk"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#step-count-total "Step count total"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierStepCount "Step Count"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T09:00:00-07:00"
* effectivePeriod.end = "2026-08-19T10:00:00-07:00"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(HealthKitRecordingDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitBluetoothHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Bluetooth Heart Rate"
Description: "A heart-rate sample imported directly from a supported Bluetooth Low Energy heart-rate monitor after the caller supplied a governed stable per-unit token."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:0Z6JoM3DXxuJfA6Lmkv43yDbz34bc_OVIoF3DFZH-ec"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:BcBbbcBhR0HYMiioTjbNsfoWBrQkr8w7TIAiBn9kfw4"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierHeartRate "Heart Rate"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T10:45:00.251-07:00"
* valueQuantity = 78 '/min' "beats/minute"
* device = Reference(HealthKitBluetoothSourceDeviceExample)
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitManuallyEnteredBodyWeightExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Manually Entered Body Weight"
Description: "A body weight with an explicit HealthKit user-entered indication mapped to manual-entry."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Fue0YmKy-5yUztQhASEkI1Q9GkXoIBF4H7th7M_sDdo"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:WK3OsUNKjSl93laduHQS9JNEeoFxgG45FC07pxdtwuo"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKQuantityTypeIdentifierBodyMass "Body Mass"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T08:15:00-07:00"
* valueQuantity = 68.4 'kg' "kg"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#manual-entry "Manual entry"
* extension[researchStudy].valueReference = Reference(HealthKitResearchStudyExample)

Instance: HealthKitBloodPressureObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Blood Pressure"
Description: "A HealthKit blood-pressure correlation whose result is carried by the required systolic and diastolic components rather than Observation.value."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:ewKtQcrS1NgeoSqX76ti_buVscMJVcfExaUed-Z9fzI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ZMSrcBVUgi8r9L8x2OpHfYH2sed1FVHZLzS-C0-eI3Y"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#85354-9 "Blood pressure panel with all children optional"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKCorrelationTypeIdentifierBloodPressure "Blood Pressure"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectiveDateTime = "2026-08-19T08:20:00-07:00"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:_a7IXBkaf-Gx-b-uRjE5RNmtvMDYBnirchWWI0EQ0t0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:xJTbRQ8qlCIFYlCxR6Wm9UkxRzRm3TFYVh3avnYkLBE"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#sleep-stage "Sleep stage"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKCategoryTypeIdentifierSleepAnalysis "Sleep Analysis"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T23:10:00-07:00"
* effectivePeriod.end = "2026-08-19T23:42:00-07:00"
* valueCodeableConcept.coding[+] = $groveSleepStage#light "Light sleep"
* valueCodeableConcept.coding[+] = $healthKitSleepAnalysis#asleepCore "Asleep, core"
* device = Reference(HealthKitRecordingDeviceExample)

Instance: HealthKitECGObservationExample
InstanceOf: HealthKitECGObservation
Usage: #example
Title: "HealthKit Lead-I-like ECG"
Description: "A caller-supplied HealthKit ECG with a complete uniformly sampled voltage series and exact classification, symptom, sampling, and count context. The adapter performs no HealthKit query."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:6iXl5fm82RN3CV4qd-y8VdUKlCs9HrQLukhEL2QaobI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:D0lEAEhoiBIlIm3KBQxP1rR5HnP3LK_V4ahwSG4qImk"
* status = #final
* category = $observationCategory#procedure "Procedure"
* code = $loinc#11524-6 "EKG study"
* code.coding[healthKitSourceType] = $healthKitSourceType#HKDataTypeIdentifierElectrocardiogram "ECG"
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T10:50:00.002-07:00"
* effectivePeriod.end = "2026-08-19T10:50:00.008-07:00"
* extension[healthKitECGClassification].valueCode = #sinusRhythm
* extension[healthKitECGSymptomsStatus].valueCode = #present
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceIdentifier].valueIdentifier.type = $groveIdentifierRole#source-record "Source record"
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceIdentifier].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* extension[healthKitECGCorrelatedSymptom][0].extension[sourceIdentifier].valueIdentifier.value = "v2:test-key:1:XC0dz7P4AOySisiHBJa6uq7Zjcx7vMOa4WqW4Aui1ok"
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
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:2LnL2_8DgGsZjeX6FiAKlO9JhhFmX7GYJxaMvLGay9k"
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
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:WE2iuX55Ut-MR8aQ6B3LSsxOnf5PIY_m5G4jcj2proo"
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
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:0Z6JoM3DXxuJfA6Lmkv43yDbz34bc_OVIoF3DFZH-ec"
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
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthKitHostDeviceExample"
* entry[=].resource = HealthKitHostDeviceExample
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
* entry[+].fullUrl = "https://study.example.org/fhir/DocumentReference/HealthKitClinicalRecordDocumentExample"
* entry[=].resource = HealthKitClinicalRecordDocumentExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthKitClinicalRecordProvenanceExample"
* entry[=].resource = HealthKitClinicalRecordProvenanceExample

Instance: HealthKitClinicalRecordDocumentExample
InstanceOf: HealthKitClinicalRecordDocument
Usage: #example
Title: "HealthKit Clinical Record Pass-Through"
Description: "One provider-issued clinical resource surfaced by HealthKit and byte-preserved in its declared FHIR release. Grove asserts identity and provenance over the envelope, never conformance over the issuer's resource."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:EO21jT4OY_rLcPTZGCJUkT3hsz8ftbZgzvOI1gBtq3I"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:mTgNSwt0kt5Uf623ktK3kYsnJ53GWwh0-ffb7JSHcFw"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:luW8iF7i93xoJ8biaOBN1tQdUBfkdBF5ZloC0VUx690"
* extension[fhirRelease].valueCode = #r4
* status = #current
* type = HealthKitClinicalRecordTypeCS#allergy-record "Allergy record"
* subject = Reference(HealthKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* content.attachment.contentType = #application/fhir+json
* content.format = $recordingFormat#fhir-r4-resource "FHIR R4 Resource"
* content.format.version = "0.6.0"
* content.attachment.title = "Provider-issued AllergyIntolerance"
* content.attachment.data = "eyJyZXNvdXJjZVR5cGUiOiJBbGxlcmd5SW50b2xlcmFuY2UiLCJpZCI6InByb3ZpZGVyLWlzc3VlZC0xIiwiY2xpbmljYWxTdGF0dXMiOnsiY29kaW5nIjpbeyJzeXN0ZW0iOiJodHRwOi8vdGVybWlub2xvZ3kuaGw3Lm9yZy9Db2RlU3lzdGVtL2FsbGVyZ3lpbnRvbGVyYW5jZS1jbGluaWNhbCIsImNvZGUiOiJhY3RpdmUifV19LCJwYXRpZW50Ijp7InJlZmVyZW5jZSI6IlBhdGllbnQvcGFydGljaXBhbnQtaGstMDAxIn19"
* content.attachment.size = 240
* content.attachment.hash = "0c+dHXDzCV5zPy4cApwAoV9evYc="

Instance: HealthKitClinicalRecordProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit Clinical Record Source Provenance"
Description: "The converter byte-preserved one provider-issued R4 resource in its profiled DocumentReference envelope; it did not reinterpret or reserialize the payload."
* target = Reference(HealthKitClinicalRecordDocumentExample)
* occurredDateTime = "2026-08-20T17:05:00Z"
* recorded = "2026-08-20T17:05:01Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:EO21jT4OY_rLcPTZGCJUkT3hsz8ftbZgzvOI1gBtq3I"

Instance: HealthKitHeartbeatSeriesRecordingExample
InstanceOf: HealthKitRecordingDocument
Usage: #example
Title: "HealthKit Heartbeat Series Recording"
Description: "A beat-to-beat interval series carried as its published column schema. Reducing the series to one Observation value would keep a single beat and discard the rest."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:hKO3Ce6Zmei7W0yk4X00HsST9JhRJNg07pzAzcSIGJc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:fwNA8TGMgYVH2cw_lR-5qTsPb3rwxvweoIVtY0nozII"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v2/test-key/1"
* identifier[sourceArtifact].value = "v2:test-key:1:8vG9fzykFSfl04NwO0gG4uQR_kQIa9uNtmM6a14fn5I"
* status = #current
* type.coding[healthKitSourceType] = $healthKitSourceType#HKDataTypeIdentifierHeartbeatSeries "Heartbeat Series"
* subject = Reference(HealthKitPatientExample)
* date = "2026-08-19T10:05:00Z"
* author = Reference(HealthKitApplicationDeviceExample)
* content.attachment.contentType = #text/csv
* content.format = $recordingFormat#beat-interval-series "Beat Interval Series"
* content.format.version = "0.6.0"
* content.attachment.title = "Heartbeat series beat intervals"
* content.attachment.data = "dGltZXN0YW1wLHByZWNlZGVkQnlHYXAKMTc1NTYyNDAwMC4wLDAKMTc1NTYyNDAwMC44NCwwCjE3NTU2MjQwMDEuNzEsMQo="
* content.attachment.size = 71
* content.attachment.hash = "lpe4Lz8znQwYfaYZt3i6kWBo+JM="

Instance: HealthKitVisionPrescriptionExample
InstanceOf: HealthKitVisionPrescription
Usage: #example
Title: "HealthKit Glasses Prescription"
Description: "A glasses prescription entered in Health, with both lens specifications, the prism resolved into its vertical and horizontal components, and the fit measurements R4 has no element for."
* extension[healthKitSourceType].valueCode = #HKVisionPrescriptionTypeIdentifier
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:JkbeCK5TOY--h9bxhY-FKVuTO9b_tVndQcVFPcTiYXc"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:DRqGf6zqqSOypChdAIfkKHvj7nMqe6ZNPgwhKgy5_q8"
* extension[expiration].valueDateTime = "2028-03-14"
* status = #active
* created = "2026-03-14"
* dateWritten = "2026-03-14"
* patient = Reference(HealthKitPatientExample)
* prescriber.extension[dataAbsentReason].valueCode = #unknown
* lensSpecification[0].product = $visionProduct#lens "Lens"
* lensSpecification[0].eye = #right
* lensSpecification[0].sphere = -2.25
* lensSpecification[0].cylinder = -0.75
* lensSpecification[0].axis = 175
* lensSpecification[0].add = 1.5
* lensSpecification[0].prism[0].amount = 0.5
* lensSpecification[0].prism[0].base = #up
* lensSpecification[0].prism[1].amount = 0.25
* lensSpecification[0].prism[1].base = #in
* lensSpecification[0].extension[vertexDistance].valueQuantity = 12 'mm'
* lensSpecification[0].extension[farPupillaryDistance].valueQuantity = 32 'mm'
* lensSpecification[0].extension[nearPupillaryDistance].valueQuantity = 30 'mm'
* lensSpecification[1].product = $visionProduct#lens "Lens"
* lensSpecification[1].eye = #left
* lensSpecification[1].sphere = -2
* lensSpecification[1].cylinder = -0.5
* lensSpecification[1].axis = 5
* lensSpecification[1].add = 1.5
* lensSpecification[1].extension[vertexDistance].valueQuantity = 12 'mm'
* lensSpecification[1].extension[farPupillaryDistance].valueQuantity = 31 'mm'
* lensSpecification[1].extension[nearPupillaryDistance].valueQuantity = 29 'mm'

Instance: HealthKitUserAnnotatedMedicationExample
InstanceOf: HealthKitUserAnnotatedMedication
Usage: #example
Title: "HealthKit Tracked Medication"
Description: "A medication the person still tracks, carrying the nickname they gave it, the platform's general form, and the concept identifier a logged dose event points at."
* extension[healthKitSourceType].valueCode = #HKDataTypeUserAnnotatedMedicationConcept
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:dYPsaAi_7N_fxtxlGHQUjx_U5R3l0cRamoivN1cttpI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:jME-IMod-S7Q2Xs7qKzqZMSqALN-t3wD-Xf7j3xvLmI"
* identifier[healthConcept].system = "https://study.example.org/fhir/NamingSystem/grove-source-context-v2/test-key/1"
* identifier[healthConcept].value = "v2:test-key:1:nq3ZogmXHSznC1LC1wNMm7KTQChgapPzmjmGeB9RHcw"
* extension[nickname].valueString = "Evening statin"
* extension[hasSchedule].valueBoolean = true
* extension[generalForm].valueCode = #tablet
* status = #active
* medicationCodeableConcept.coding[0] = $rxnorm#617312 "Atorvastatin 10 MG Oral Tablet"
* medicationCodeableConcept.text = "Atorvastatin 10 MG Oral Tablet"
* subject = Reference(HealthKitPatientExample)

Instance: HealthKitMedicationDoseEventExample
InstanceOf: HealthKitMedicationDoseEvent
Usage: #example
Title: "HealthKit Medication Dose Event"
Description: "A scheduled dose logged as taken. The exact log status and the schedule it was logged against ride beside the administration status, which alone could not tell a taken dose from one the person never acted on."
* extension[healthKitSourceType].valueCode = #HKMedicationDoseEventTypeIdentifierMedicationDoseEvent
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:YZvOO4dNIgxxVYsu1OCBBnh6ape7UF-3S8sF3VVluGQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:NTPRctM8xb3nuHjM2dYovO0LzuvWJJQcv7dZnd6P8mg"
* extension[logStatus].valueCode = #taken
* extension[schedule].extension[type].valueCode = #schedule
* extension[schedule].extension[expectedDate].valueDateTime = "2026-08-20T21:00:00-07:00"
* extension[schedule].extension[expectedQuantity].valueQuantity = 10 'mg'
* status = #completed
* medicationReference.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-context-v2/test-key/1"
* medicationReference.identifier.value = "v2:test-key:1:nq3ZogmXHSznC1LC1wNMm7KTQChgapPzmjmGeB9RHcw"
* subject = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-20T21:07:12-07:00"
* effectivePeriod.end = "2026-08-20T21:07:12-07:00"
* dosage.dose = 10 'mg'
