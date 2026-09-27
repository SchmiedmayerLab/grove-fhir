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
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v0/test-key/1"
* identifier[physicalUnit].value = "v0:test-key:1:qhSRcij9sI7cts2PrP7Yj5iAetB4cyTf_hq2Q6b_Hbc"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[eventSnapshot].value = "v0:test-key:1:tjnY9p28ADzcMfS-ZiHs84KXwr0aHdlvpxTPTDWlV4o"
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
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:Cu-oM3Eanzl4c3ALjrGfasOLxIelhh2PR9TEN1zgm8A"
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
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier.value = "v0:test-key:1:VrMNoleVhSsWAFWBxaFRHnwoc_FWIgokpq5q8eW-M9I"
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
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:zfObGQIiHBa5vxxcAy6MJ9RJLFGFPgyip9gqUmygN4k"
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
Description: "A supported Bluetooth Low Energy source explicitly classified by the producer after the deployment supplied an authorized stable per-unit token. Only deployment-scoped HMAC identities are exchanged."
* status = #active
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v0/test-key/1"
* identifier[physicalUnit].value = "v0:test-key:1:WFvTdsYYy25kOKXkXRmN5LUpuewL402vPr8OS40oGw0"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[eventSnapshot].value = "v0:test-key:1:3exdFN2SrwgkAmjoti-lypohAfZ3DBixgUYPXNBNT84"
* deviceName.name = "Example Bluetooth Source"
* deviceName.type = #user-friendly-name

Instance: HealthKitHeartRateObservationExample
InstanceOf: HealthKitObservation
Usage: #example
Title: "HealthKit Heart Rate"
Description: "A passive HealthKit heart-rate sample with the standard clinical profile and an allowlisted motion-context value."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:KbhJV4Hy226SHr2hw6IsWmGQudFmoxM1RxJ-eflU7c0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-OEmUVWfiQ2oJ9BagEvk4GTXuo-zMmDX8BzP-GqfPEs"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierHeartRate
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:nPJeEaz45T9YDxj5eDR9tH8vd_lY1wIaPN0YB24m9ms"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:FR__fLtP23UvZ4eCVmgFh_0IDG5YOK4MmEzZVjERlAk"
* identifier[writerRecord].system = "https://study.example.org/fhir/NamingSystem/grove-writer-record-v0/test-key/1"
* identifier[writerRecord].value = "v0:test-key:1:qxujzFH9irQKon1KMxiN8jK8ahVB36Fq0JIKoBDNa2s"
* extension[writerRecordVersion].valueString = "2"
* status = #amended
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierBodyMass
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:KfCIhMCG20R_4vgFE0nC5LU7VgPxODPyne0bX2eCVg8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:c6pNXTKAqgfTMIXE6ZAfL007p21CEFiMTVBSMroyv9U"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#step-count-total "Step count total"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierStepCount
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
Description: "A heart-rate sample imported directly from a supported Bluetooth Low Energy heart-rate monitor after the deployment supplied a governed stable per-unit token."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:hLRtdm8TLwFdzySX_s3cl30mzvcJzdzSWn3N31O24d8"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:oGejclTtnAghNeHrPUbmT7N1PcggMDTYLJuYRugf_jA"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierHeartRate
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:Nyg4YzicYsoW_xkqK0vWy2kUI785S54E-rmkSDJwQlg"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:aB63HiYPjgreovjJ22CiYsd_QYqBnGTwJv4M46TNCFA"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* extension[healthKitSourceType].valueCode = #HKQuantityTypeIdentifierBodyMass
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:vJBTevn8zVrLwA7I20jrntEItf-nstECqfqzRZ_I7TI"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:1YQ0u2fneqgwHFbedvis2ggBQNpY6nxjDL3mwv-0uCM"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#85354-9 "Blood pressure panel with all children optional"
* extension[healthKitSourceType].valueCode = #HKCorrelationTypeIdentifierBloodPressure
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:vsyJXJFSZiW4mx1u7BgDdwUzgDk87H556hyBE4sUivU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:6Jd_AE_qOGOjF9Xur-1E4FjnzSUS0m183W1FGDpRmMA"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#sleep-stage "Sleep stage"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierSleepAnalysis
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
Description: "An already-obtained HealthKit ECG with a complete uniformly sampled voltage series, exact interpretation and method, and an identifier-only link to a separately exchanged symptom Observation. Sampling frequency and reported count were checked before emission rather than duplicated on the wire."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-ecg-observation"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:oN-31P0nbvC9h0LDC6b4F_cz8NSGsi_HUNQanjg2BcQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:80sl0nasACaNTanxlBQ8lRDzPB_qmC5KYJ0i8P75dRs"
* status = #final
* category = $observationCategory#procedure "Procedure"
* code = $loinc#11524-6 "EKG study"
* extension[healthKitSourceType].valueCode = #HKDataTypeIdentifierElectrocardiogram
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T10:50:00.002-07:00"
* effectivePeriod.end = "2026-08-19T10:50:00.008-07:00"
* interpretation = $healthKitECGClassification#sinusRhythm "Sinus rhythm"
* extension[healthKitECGSymptomsStatus].valueCode = #present
* method = $healthKitECGAlgorithmVersion#version2 "Version 2"
* hasMember.type = "Observation"
* hasMember.identifier.type = $groveIdentifierRole#source-output "Source output"
* hasMember.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* hasMember.identifier.value = "v0:test-key:1:4KbvOvpCwLG0ZnbRpFKS2jTFUZfpWRS0IjrT7Q_g1PY"
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

Instance: HealthKitECGAverageHeartRateExample
InstanceOf: HealthKitECGAverageHeartRateObservation
Usage: #example
Title: "HealthKit ECG Average Heart Rate"
Description: "The user's average heart rate during the ECG, represented as its own clinical Observation and derived from the waveform."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:oN-31P0nbvC9h0LDC6b4F_cz8NSGsi_HUNQanjg2BcQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:DPCuUXWrL7_6vuJ-tROS9PLSfIcx0lYkSSECOC3xmSg"
* status = #final
* code = $loinc#8867-4 "Heart rate"
* category = $observationCategory#vital-signs "Vital Signs"
* extension[healthKitSourceType].valueCode = #HKDataTypeIdentifierElectrocardiogram
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T10:50:00.002-07:00"
* effectivePeriod.end = "2026-08-19T10:50:00.008-07:00"
* valueQuantity = 72 '/min' "beats/minute"
* derivedFrom = Reference(HealthKitECGObservationExample)
* device = Reference(HealthKitRecordingDeviceExample)

Instance: HealthKitECGCorrelatedDizzinessExample
InstanceOf: HealthkitSymptomDizziness
Usage: #example
Title: "HealthKit ECG-associated Dizziness"
Description: "The independently identifiable HealthKit category sample associated with the ECG. It is exchanged in its own source-record event and referenced from the ECG by source-output Identifier."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:iAHwFvGOZNRZcV3Q1xU6WxW597mHysdwK_e-pfRgIkw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:4KbvOvpCwLG0ZnbRpFKS2jTFUZfpWRS0IjrT7Q_g1PY"
* status = #final
* code = HealthKitMeasurementCS#symptom-dizziness "Dizziness"
* extension[healthKitSourceType].valueCode = #HKCategoryTypeIdentifierDizziness
* subject = Reference(HealthKitPatientExample)
* performer = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-19T10:49:55-07:00"
* effectivePeriod.end = "2026-08-19T10:50:05-07:00"
* valueCodeableConcept = GroveSymptomSeverityCS#mild "Mild"

Instance: HealthKitECGConversionProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit ECG Conversion Provenance"
Description: "One conversion event targets both outputs derived from the same HealthKit ECG source record."
* target[+] = Reference(HealthKitECGObservationExample)
* target[+] = Reference(HealthKitECGAverageHeartRateExample)
* occurredDateTime = "2026-08-19T10:50:01-07:00"
* recorded = "2026-08-19T17:50:01.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:oN-31P0nbvC9h0LDC6b4F_cz8NSGsi_HUNQanjg2BcQ"

Instance: HealthKitECGSymptomProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit ECG-associated Symptom Provenance"
Description: "The separately exchanged symptom event retains its own source identity and source-revision author graph."
* target = Reference(HealthKitECGCorrelatedDizzinessExample)
* occurredDateTime = "2026-08-19T10:50:06-07:00"
* recorded = "2026-08-19T17:50:06.000Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:iAHwFvGOZNRZcV3Q1xU6WxW597mHysdwK_e-pfRgIkw"
* entity.agent.type = $provenanceParticipantType#author "Author"
* entity.agent.who = Reference(HealthKitSourceApplicationDeviceExample)

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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:KbhJV4Hy226SHr2hw6IsWmGQudFmoxM1RxJ-eflU7c0"
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:KfCIhMCG20R_4vgFE0nC5LU7VgPxODPyne0bX2eCVg8"
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
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:hLRtdm8TLwFdzySX_s3cl30mzvcJzdzSWn3N31O24d8"
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
* entry[+].fullUrl = "https://study.example.org/fhir/DocumentReference/HealthKitDSTU2ClinicalRecordDocumentExample"
* entry[=].resource = HealthKitDSTU2ClinicalRecordDocumentExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthKitDSTU2ClinicalRecordProvenanceExample"
* entry[=].resource = HealthKitDSTU2ClinicalRecordProvenanceExample

Instance: HealthKitClinicalRecordDocumentExample
InstanceOf: HealthKitClinicalRecordDocument
Usage: #example
Title: "HealthKit R4 Clinical Record Pass-Through"
Description: "One provider-issued R4 resource surfaced by HealthKit and byte-preserved with its declared source release. Grove asserts identity and provenance over the R4 envelope, never conformance over the issuer's resource."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:B1KqoWjy3t3ZGjgJgs36zq44-GTIkXFvIr-2gke2dj0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:tMYriQs_qQL-BAimoowwU-d6t23x2oC5PMrv62d-WlI"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:R7qxjpolL7-0z79P7ZzKC5aM0yU898WAepzic3wPmes"
* extension[healthKitSourceType].valueCode = #HKClinicalTypeIdentifierAllergyRecord
* status = #current
* type = HealthKitClinicalRecordTypeCS#allergy-record "Allergy record"
* subject = Reference(HealthKitPatientExample)
* date = "2026-08-20T17:05:01Z"
* content.attachment.contentType = #"application/fhir+json; fhirVersion=4.0"
* content.format = $recordingFormat#fhir-resource "FHIR Resource"
* content.attachment.title = "Provider-issued AllergyIntolerance"
* content.attachment.data = "eyJyZXNvdXJjZVR5cGUiOiJBbGxlcmd5SW50b2xlcmFuY2UiLCJpZCI6InByb3ZpZGVyLWlzc3VlZC0xIiwiY2xpbmljYWxTdGF0dXMiOnsiY29kaW5nIjpbeyJzeXN0ZW0iOiJodHRwOi8vdGVybWlub2xvZ3kuaGw3Lm9yZy9Db2RlU3lzdGVtL2FsbGVyZ3lpbnRvbGVyYW5jZS1jbGluaWNhbCIsImNvZGUiOiJhY3RpdmUifV19LCJwYXRpZW50Ijp7InJlZmVyZW5jZSI6IlBhdGllbnQvcGFydGljaXBhbnQtaGstMDAxIn19"
* content.attachment.size = 240
* content.attachment.hash = "0c+dHXDzCV5zPy4cApwAoV9evYc="

Instance: HealthKitClinicalRecordProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit Clinical Record Source Provenance"
Description: "The converter byte-preserved one provider-issued R4 resource in its profiled R4 DocumentReference envelope; it did not reinterpret or reserialize the payload."
* target = Reference(HealthKitClinicalRecordDocumentExample)
* occurredDateTime = "2026-08-20T17:05:00Z"
* recorded = "2026-08-20T17:05:01Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:B1KqoWjy3t3ZGjgJgs36zq44-GTIkXFvIr-2gke2dj0"

Instance: HealthKitDSTU2ClinicalRecordDocumentExample
InstanceOf: HealthKitClinicalRecordDocument
Usage: #example
Title: "HealthKit DSTU2 Clinical Record Pass-Through"
Description: "One provider-issued DSTU2 resource surfaced by HealthKit and byte-preserved with its declared source release inside an R4 DocumentReference envelope."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:UW5bJTkRJ0UKkw7krpXqdxuXronFcrv0fcxncHrqDsQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:znQrk3qim2B70uLiwaJ0m-7sGJiBQtpu6zv2jnopM1A"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:g-a1f691jBmG-Nm40aE-LYrmGQb4AQEWGcVr-OBTRDI"
* extension[healthKitSourceType].valueCode = #HKClinicalTypeIdentifierAllergyRecord
* status = #current
* type = HealthKitClinicalRecordTypeCS#allergy-record "Allergy record"
* subject = Reference(HealthKitPatientExample)
* date = "2026-08-20T17:06:01Z"
* content.attachment.contentType = #"application/fhir+json; fhirVersion=1.0"
* content.format = $recordingFormat#fhir-resource "FHIR Resource"
* content.attachment.title = "Provider-issued DSTU2 AllergyIntolerance"
* content.attachment.data = "eyJyZXNvdXJjZVR5cGUiOiJBbGxlcmd5SW50b2xlcmFuY2UiLCJpZCI6InByb3ZpZGVyLWlzc3VlZC1kc3R1Mi0xIiwicGF0aWVudCI6eyJyZWZlcmVuY2UiOiJQYXRpZW50L3BhcnRpY2lwYW50LWhrLTAwMSJ9LCJzdWJzdGFuY2UiOnsidGV4dCI6IlBlbmljaWxsaW4ifSwic3RhdHVzIjoiY29uZmlybWVkIiwiY3JpdGljYWxpdHkiOiJDUklUTCJ9"
* content.attachment.size = 198
* content.attachment.hash = "sDYJit+YpJaTk0nwQWt0M5Xq7QA="

Instance: HealthKitDSTU2ClinicalRecordProvenanceExample
InstanceOf: HealthKitConversionProvenance
Usage: #example
Title: "HealthKit DSTU2 Clinical Record Source Provenance"
Description: "The converter byte-preserved one provider-issued DSTU2 resource in its profiled R4 DocumentReference envelope; it did not reinterpret or reserialize the payload."
* target = Reference(HealthKitDSTU2ClinicalRecordDocumentExample)
* occurredDateTime = "2026-08-20T17:06:00Z"
* recorded = "2026-08-20T17:06:01Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthKitApplicationDeviceExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:UW5bJTkRJ0UKkw7krpXqdxuXronFcrv0fcxncHrqDsQ"

Instance: HealthKitHeartbeatSeriesRecordingExample
InstanceOf: HealthKitRecordingDocument
Usage: #example
Title: "HealthKit Heartbeat Series Recording"
Description: "A beat-to-beat interval series carried as its published column schema. Reducing the series to one Observation value would keep a single beat and discard the rest."
* meta.profile[+] = "https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:WcJEb3IdnPKltbqMjxoeo-kDcGnvOz7f6gW7_Nr55z4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:-hvxbZhBlqPixknyrvDdW7Fkl8zbcl_FHAUmVQk_UFg"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:7tVsCFC3DOk-0eneckGKzPj6qx7T1kvnwnpEwTtw3Q4"
* status = #current
* type.text = "Heartbeat series recording"
* extension[healthKitSourceType].valueCode = #HKDataTypeIdentifierHeartbeatSeries
* subject = Reference(HealthKitPatientExample)
* date = "2026-08-19T10:05:00Z"
* author = Reference(HealthKitApplicationDeviceExample)
* content.attachment.contentType = #text/csv
* content.format = $recordingFormat#beat-interval-series "Beat Interval Series"
* content.attachment.title = "Heartbeat series beat intervals"
* content.attachment.data = "dGltZXN0YW1wLHByZWNlZGVkQnlHYXAKMTc4NzEzMzYwMC4wLDAKMTc4NzEzMzYwMC44NCwwCjE3ODcxMzM2MDEuNzEsMQo="
* content.attachment.size = 71
* content.attachment.hash = "hRPUfJrDsoGXIPige7C51EtpY9E="

Instance: HealthKitVisionPrescriptionExample
InstanceOf: HealthKitVisionPrescription
Usage: #example
Title: "HealthKit Glasses Prescription"
Description: "A glasses prescription entered in Health, with both lens specifications, the prism resolved into its vertical and horizontal components, and the fit measurements R4 has no element for."
* extension[healthKitSourceType].valueCode = #HKVisionPrescriptionTypeIdentifier
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:8eNut_ub5HXjZeiFRlZpi4oU36tC2wR9BHCwDzPU44o"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:367nUVbJALaI4f0eZmHTgMznKYNIX4VCmT221lL9ucQ"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:CHSikTaDEwAmroypuSSj9OXHXwC2-4cclkUTm_1gFzU"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:Fh49hSp7fu5MT3-DGXDWSdXJs1Tq7eP2OMc4PxvRKbo"
* identifier[healthConcept].system = "https://study.example.org/fhir/NamingSystem/grove-source-context-v0/test-key/1"
* identifier[healthConcept].value = "v0:test-key:1:yGgoW6BXR_wT7vPwUpVQz6UsHq7NLUDE70Ocog4kKtw"
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
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:tCNGYuv426SwROmmIgcvHUPOLyHEyaSOQDaVRGXwvgQ"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:BJvX5mWndAwPoVfnXB64w4MgcWNDVWHas0NRuLrV6ug"
* extension[logStatus].valueCode = #taken
* extension[schedule].extension[type].valueCode = #schedule
* extension[schedule].extension[expectedDate].valueDateTime = "2026-08-20T21:00:00-07:00"
* extension[schedule].extension[expectedQuantity].valueQuantity = 10 'mg'
* status = #completed
* medicationReference.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-context-v0/test-key/1"
* medicationReference.identifier.value = "v0:test-key:1:yGgoW6BXR_wT7vPwUpVQz6UsHq7NLUDE70Ocog4kKtw"
* subject = Reference(HealthKitPatientExample)
* effectivePeriod.start = "2026-08-20T21:07:12-07:00"
* effectivePeriod.end = "2026-08-20T21:07:12-07:00"
* dosage.dose = 10 'mg'
