//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: HealthConnectPatientExample
InstanceOf: Patient
Usage: #example
Title: "Health Connect Example Participant"
Description: "The Patient referenced by the Health Connect adapter examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "participant-hc-001"

Instance: HealthConnectRecordingDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "Health Connect Recording Device"
Description: "A physical watch included only because the deployment has a governed stable per-unit token. Manufacturer and model alone would not establish Device instance identity."
* identifier[physicalUnit].system = "https://study.example.org/fhir/NamingSystem/grove-recording-device-v2/test-key/1"
* identifier[physicalUnit].value = "v2:test-key:1:EJUyMyw_i_PnBqP-R7ckX6zAPrzLr3ir47Y7cl_avVw"
* identifier[eventSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[eventSnapshot].value = "v2:test-key:1:fwCxYBipSvO_JdDPe8pcHWjsVm9D1hLDuGFSVIzda7Y"
* status = #active
* type.text = "Watch"
* manufacturer = "Example Devices"
* modelNumber = "Study Watch 2"
* deviceName.name = "Participant study watch"
* deviceName.type = #user-friendly-name

Instance: HealthConnectHostDeviceExample
InstanceOf: GroveHostDevice
Usage: #example
Title: "Health Connect Host Snapshot"
Description: "An immutable event-time snapshot of the phone and operating system hosting the converter."
* identifier.system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier.value = "v2:test-key:1:FZrVNDHaRCOzkgFOQscxxt2HN_lYjz2bxtYHWf8Hzm0"
* status = #active
* manufacturer = "Example Devices"
* modelNumber = "Example Phone"
* deviceName.name = "Study phone"
* deviceName.type = #user-friendly-name
* version[operatingSystemVersion].type = $groveApplicationVersionType#os-version "Operating system version"
* version[operatingSystemVersion].value = "20.1"

Instance: HealthConnectConverterApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Health Connect Converter Snapshot"
Description: "An immutable event-time snapshot of the application that converted one source Record."
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v2/test-key/1"
* identifier[applicationSnapshot].value = "v2:test-key:1:sGzDek4hAO9SOAmIvnvd32NDtO3UMIwm9nQgw8uV6u4"
* status = #active
* deviceName[applicationName].name = "Grove Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "1.4.0"
* version[applicationBuild].type = $groveApplicationVersionType#build "Build"
* version[applicationBuild].value = "140"
* parent = Reference(HealthConnectHostDeviceExample)

Instance: HealthConnectRestingHeartRateExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Point-in-time Health Connect Resting Heart Rate"
Description: "One instantaneous AndroidX RestingHeartRateRecord. It is never converted into a daily mean or a Period."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-resting-heart-rate"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:K4qSTmnZ9b7KJz9yF4UsbHyaxvNVIa1tbRZ9TAaeaS4"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:Ta6IleWrRKQoRN9q85kJSx5-BJ0NpkHknRFnAv7ySQg"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code.coding[0] = $loinc#40443-4 "Heart rate --resting"
* code.coding[1] = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T08:15:00-07:00"
* issued = "2026-08-19T15:15:01Z"
* valueQuantity = 58 '/min' "beats/minute"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[healthConnectRecordType].valueCode = #RestingHeartRateRecord

Instance: HealthConnectMindfulnessExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Mindfulness Session"
Description: "A bounded mindfulness session preserving its exact AndroidX type, non-blank title, and source note."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-mindfulness-session"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:iIVxXFtB5SbGIRikA73tjHrpqd8ufeofEmCFSoIXg-0"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:CrOiWSVaBqUio2i_X3wERoHbRzRpUNTHwCfBGHDkh18"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#mindfulness-session-duration "Mindfulness session duration"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T07:00:00-07:00"
* effectivePeriod.end = "2026-08-19T07:12:00-07:00"
* issued = "2026-08-19T14:12:01Z"
* valueQuantity = 12 'min' "min"
* extension[healthConnectRecordType].valueCode = #MindfulnessSessionRecord
* method = $healthConnectMindfulnessSessionType#MINDFULNESS_SESSION_TYPE_MEDITATION "Meditation"
* extension[sessionTitle].valueString = "Morning practice"
* note.text = "Guided attention exercise."

Instance: HealthConnectVo2MaxExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect VO2 Max"
Description: "A point VO2 max result preserving the exact AndroidX measurement method in Observation.method."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-vo2-max"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:c4NgACTknAYRGzVz8eDS0aJElb-DTHiLL0SkSgvWI0g"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:cQW07ZS0vbYhMowJ8A0DmGXWhrtCLlkv3DO9xgonNMw"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#vo2-max "VO2 max"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T09:00:00-07:00"
* issued = "2026-08-19T16:00:01Z"
* valueQuantity = 42.5 'mL/kg/min' "mL/kg/min"
* method = $healthConnectVo2MaxMeasurementMethod#MEASUREMENT_METHOD_METABOLIC_CART "Metabolic cart"
* extension[healthConnectRecordType].valueCode = #Vo2MaxRecord

Instance: HealthConnectExerciseSessionExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Running Session"
Description: "A bounded workout summary retaining the shared activity, exact AndroidX exercise type, and explicitly retained non-blank title and note."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-workout"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:pkPzHiQ47pB7fo9kez1nwoUxruc62tEp5nLMBx-UhaM"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:rmsyU9Lm1U1Nrq7pQ9HKgpwSaMJsHdB2gLUIFJktbHw"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#workout "Workout session"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T17:30:00-07:00"
* effectivePeriod.end = "2026-08-19T18:05:00-07:00"
* issued = "2026-08-20T01:05:01Z"
* valueCodeableConcept.coding[0] = $groveWorkoutActivity#running "Running"
* valueCodeableConcept.coding[1] = $healthConnectExerciseType#EXERCISE_TYPE_RUNNING "Running"
* extension[healthConnectRecordType].valueCode = #ExerciseSessionRecord
* extension[sessionTitle].valueString = "Evening run"
* note.text = "Steady outdoor effort."

Instance: HealthConnectCapillaryGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Capillary Blood Specimen"
Description: "A synthesized Specimen with the same source-record identity as its Observation and a distinct source-output identity for the specimen node."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:S9HZl_XazTDuPI2Qw2izroj9BrmVWOhQdMPFpTLYtZA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:g_5Nfzz7OVc7wN1caeAXSmD1OKsbSlAbdpgC7B9Ms9E"
* status = #available
* type = $sct#122554006 "Capillary blood specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectCapillaryGlucoseExample
InstanceOf: HealthConnectCapillaryBloodGlucose
Usage: #example
Title: "Health Connect Capillary Blood Glucose"
Description: "A specimen-specific glucose result retaining non-unknown source meal context."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:S9HZl_XazTDuPI2Qw2izroj9BrmVWOhQdMPFpTLYtZA"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:4pEkisgic0DKgXf926qVOcX_T4oRwc2AgqbEEW4tdRo"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#32016-8 "Glucose [Mass/volume] in Capillary blood"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:15:00-07:00"
* issued = "2026-08-20T14:15:01Z"
* valueQuantity = 96 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectCapillaryGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord
* extension[glucoseMealContext].extension[relationToMeal].valueCoding = $healthConnectRelationToMeal#RELATION_TO_MEAL_FASTING "Fasting"
* extension[glucoseMealContext].extension[mealType].valueCoding = $healthConnectMealType#MEAL_TYPE_BREAKFAST "Breakfast"

Instance: HealthConnectWholeBloodGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Whole-blood Specimen"
Description: "The standard-coded Specimen synthesized for an admitted whole-blood source token."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:bRaUjs9X-R4hntsff4cSdtawFOiJ8KIcMhfGhUfLzPY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:2GLg4Fe1As8r7_V1PGJ2KiZ67ZnRsAxxFh-Py3Q91ZU"
* status = #available
* type = $sct#258580003 "Whole blood specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectWholeBloodGlucoseExample
InstanceOf: HealthConnectWholeBloodGlucose
Usage: #example
Title: "Health Connect Whole-blood Glucose"
Description: "A BloodGlucoseRecord whose exact whole-blood source token selects the whole-blood LOINC profile and paired standard-coded Specimen."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:bRaUjs9X-R4hntsff4cSdtawFOiJ8KIcMhfGhUfLzPY"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:ptU8eDukm9cI-EiAJb-H0sGSrFGQzZ6Wx6xY6v_shCw"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#2339-0 "Glucose [Mass/volume] in Blood"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:20:00-07:00"
* issued = "2026-08-20T14:20:01Z"
* valueQuantity = 91 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectWholeBloodGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord

Instance: HealthConnectPlasmaGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Plasma Specimen"
Description: "The standard-coded Specimen synthesized for an admitted plasma source token; serum uses the same Observation profile but a distinct SNOMED CT specimen code."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:71VA1gnSJo_LCwvV2REgMhPDgRVD1Qi2Jx7mN9vMgFk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:8MaAaovE633TGTTqH-MVjOTW9mIpHDDpDTPN-afojMA"
* status = #available
* type = $sct#119361006 "Plasma specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectPlasmaGlucoseExample
InstanceOf: HealthConnectSerumPlasmaGlucose
Usage: #example
Title: "Health Connect Plasma Glucose"
Description: "A BloodGlucoseRecord whose exact plasma source token is preserved by the referenced Specimen instead of being collapsed with serum."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:71VA1gnSJo_LCwvV2REgMhPDgRVD1Qi2Jx7mN9vMgFk"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:zxYhTVMKHrnLK3E7fkZXVktJ5PjghUdpR6HIhbB3WEk"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#2345-7 "Glucose [Mass/volume] in Serum or Plasma"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:25:00-07:00"
* issued = "2026-08-20T14:25:01Z"
* valueQuantity = 94 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectPlasmaGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord

Instance: HealthConnectInterstitialGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Interstitial-fluid Specimen"
Description: "The standard-coded Specimen synthesized for an admitted interstitial-fluid source token."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Z51VJVDh2iLp-g2bxOr9QZg9BXEQxruj_qk6rwPXHKw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:DFFrG6I31gqN-JyBjs3Ffxt2FK4Su44vDMOF0FQmJ5Y"
* status = #available
* type = $sct#258479004 "Interstitial fluid specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectInterstitialGlucoseExample
InstanceOf: HealthConnectInterstitialGlucose
Usage: #example
Title: "Health Connect Interstitial-fluid Glucose"
Description: "A BloodGlucoseRecord whose interstitial-fluid source token selects the specific LOINC profile and paired standard-coded Specimen."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:Z51VJVDh2iLp-g2bxOr9QZg9BXEQxruj_qk6rwPXHKw"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:0-xgJ-AL3EPAMn5LG6pm3EdSLaMMm_vVqzAzBDliiSo"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#99504-3 "Glucose [Mass/volume] in Interstitial fluid"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:30:00-07:00"
* issued = "2026-08-20T14:30:01Z"
* valueQuantity = 99 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectInterstitialGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord

Instance: HealthConnectSleepDurationExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Titled Sleep Session"
Description: "A SleepSessionRecord summary that preserves the non-blank caller title only through the shared Health Connect session-title extension."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-duration"
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* identifier[sourceRecord].value = "v2:test-key:1:HPJquAHiADGaatDS33VJedCuuWarufYLRoQ8KwUVrWE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v2/test-key/1"
* identifier[sourceOutput].value = "v2:test-key:1:wfgHT_KwgM0DSURsVN5ZRKi4oHpL_SzpfO0-6ICWRyQ"
* status = #final
* code = $loinc#93832-4 "Sleep duration"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T22:30:00-07:00"
* effectivePeriod.end = "2026-08-20T06:30:00-07:00"
* issued = "2026-08-20T13:30:01Z"
* valueQuantity = 7.5 'h' "h"
* extension[healthConnectRecordType].valueCode = #SleepSessionRecord
* extension[sessionTitle].valueString = "Overnight sleep"

Instance: HealthConnectCapillaryGlucoseProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Capillary Glucose Conversion"
Description: "One conversion Provenance targets both outputs of the admitted glucose graph: the clinical Observation and synthesized Specimen."
* target[+] = Reference(HealthConnectCapillaryGlucoseExample)
* target[+] = Reference(HealthConnectCapillaryGlucoseSpecimenExample)
* occurredDateTime = "2026-08-20T07:15:00-07:00"
* recorded = "2026-08-20T14:15:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:S9HZl_XazTDuPI2Qw2izroj9BrmVWOhQdMPFpTLYtZA"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who.type = "Device"
* entity.agent.who.identifier.system = $androidPackageName
* entity.agent.who.identifier.value = "com.example.wearable"

Instance: HealthConnectRestingHeartRateProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Resting Heart Rate Conversion"
Description: "One source Record revision transformed into every output for this event, with distinct activity and recording times."
* target = Reference(HealthConnectRestingHeartRateExample)
* occurredDateTime = "2026-08-19T08:15:00-07:00"
* recorded = "2026-08-19T15:15:02Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v2/test-key/1"
* entity.what.identifier.value = "v2:test-key:1:K4qSTmnZ9b7KJz9yF4UsbHyaxvNVIa1tbRZ9TAaeaS4"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who.type = "Device"
* entity.agent.who.identifier.system = $androidPackageName
* entity.agent.who.identifier.value = "com.example.wearable"
