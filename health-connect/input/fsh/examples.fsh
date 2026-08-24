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

Instance: HealthConnectStudyPlanExample
InstanceOf: PlanDefinition
Usage: #example
Title: "Health Connect Study Protocol"
Description: "The versioned study protocol governing the Health Connect example collection."
* url = "https://study.example.org/fhir/PlanDefinition/health-connect-study-protocol"
* version = "2026.08"
* name = "HealthConnectStudyProtocol"
* title = "Health Connect Study Protocol"
* status = #active
* experimental = false
* date = "2026-08-19"
* publisher = "Example Study"
* description = "Collect heart rate, step count, and body weight through Health Connect."

Instance: HealthConnectResearchStudyExample
InstanceOf: ResearchStudy
Usage: #example
Title: "Health Connect Research Study"
Description: "A ResearchStudy whose protocol references the exact PlanDefinition revision used for collection."
* identifier.system = "https://study.example.org/fhir/identifiers/research-study"
* identifier.value = "health-connect-study"
* title = "Example Health Connect Study"
* protocol = Reference(HealthConnectStudyPlanExample)
* status = #active

Instance: HealthConnectResearchSubjectExample
InstanceOf: ResearchSubject
Usage: #example
Title: "Health Connect Research Subject"
Description: "The participant's enrollment in the Health Connect example study."
* identifier.system = "https://study.example.org/fhir/identifiers/research-subject"
* identifier.value = "health-connect-study-participant-hc-001"
* status = #on-study
* period.start = "2026-08-01"
* study = Reference(HealthConnectResearchStudyExample)
* individual = Reference(HealthConnectPatientExample)

Instance: HealthConnectRecordingDeviceExample
InstanceOf: GroveRecordingDevice
Usage: #example
Title: "Health Connect Recording Device"
Description: "The watch supplied in Health Connect metadata as the physical device that recorded the passive examples."
* type.text = "Watch"
* manufacturer = "Example Devices"
* modelNumber = "Study Watch 2"

Instance: HealthConnectConverterApplicationExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Health Connect Converting Application"
Description: "The application that transformed Health Connect Records into FHIR resources."
* status = #active
* identifier.system = $androidPackageName
* identifier.value = "org.grovealliance.example"
* deviceName[applicationName].name = "Grove Study"
* deviceName[applicationName].type = #user-friendly-name
* version[applicationVersion].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[applicationVersion].value = "1.4.0"

Instance: HealthConnectSourceApplicationExample
InstanceOf: Device
Usage: #example
Title: "Health Connect Data Origin Application"
Description: "The application identified by Health Connect DataOrigin.packageName as the enterer of the example Records. No display name or version is asserted because DataOrigin does not supply either value."
* identifier.system = $androidPackageName
* identifier.value = "com.example.wearable"

Instance: HealthConnectHeartRateSampleOneExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Heart Rate Sample One"
Description: "The first FHIR heart-rate Observation emitted from a Health Connect HeartRateRecord containing two samples."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|HeartRateRecord|record-005"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|HeartRateRecord|record-005|sample|2026-08-19T17:30:15.000000000Z|0"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T17:30:15Z"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 72 '/min' "beats/minute"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[healthConnectRecordType].valueCode = #HeartRateRecord
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectRevisedWeightExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Revised Weight"
Description: "A weight a connected scale re-imported after correcting it. The stored Record carries a new metadata.id, so this Observation carries a new record identifier, the unchanged clientRecordId that names the measurement, and the higher clientRecordVersion that supersedes the previous one."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|WeightRecord|record-007"
* identifier[writerRecordId].system = $groveWriterRecordId
* identifier[writerRecordId].value = "v1:com.withings.wiscale2|scale-weighin-2026-08-19"
* extension[writerRecordVersion].valueString = "2"
* status = #amended
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T14:12:00Z"
* issued = "2026-08-20T08:00:00Z"
* valueQuantity = 68.9 'kg' "kg"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[healthConnectRecordType].valueCode = #WeightRecord
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectHeartRateSampleTwoExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Heart Rate Sample Two"
Description: "The second FHIR heart-rate Observation emitted from the same Health Connect HeartRateRecord."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-heart-rate"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|HeartRateRecord|record-005"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|HeartRateRecord|record-005|sample|2026-08-19T17:30:30.000000000Z|0"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8867-4 "Heart rate"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T17:30:45Z"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 75 '/min' "beats/minute"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[healthConnectRecordType].valueCode = #HeartRateRecord
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectBodyWeightExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Body Weight"
Description: "A manually entered Health Connect WeightRecord represented with the standard FHIR body-weight profile."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-weight"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|WeightRecord|record-003"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#29463-7 "Body weight"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-19T08:15:00-07:00"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 68.4 'kg' "kg"
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#manual-entry "Manual entry"
* extension[healthConnectRecordType].valueCode = #WeightRecord
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectStepCountExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Step Count"
Description: "A Health Connect StepsRecord preserving the source interval and count."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-step-count"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|StepsRecord|record-010"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#step-count-total "Step count total"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T09:00:00-07:00"
* effectivePeriod.end = "2026-08-19T10:00:00-07:00"
* issued = "2026-08-19T17:30:01Z"
* valueQuantity = 1042 '{steps}' "steps"
* device = Reference(HealthConnectRecordingDeviceExample)
* extension[recordingMethod].valueCoding = GroveRecordingMethodCS#automatically-recorded "Automatically recorded"
* extension[healthConnectRecordType].valueCode = #StepsRecord
* extension[researchStudy].valueReference = Reference(HealthConnectResearchStudyExample)

Instance: HealthConnectCapillaryGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Capillary Blood Specimen"
Description: "The standard-coded specimen node synthesized from an exact Health Connect capillary-blood specimen source."
* identifier[specimenId].system = $healthConnectSpecimenId
* identifier[specimenId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|StepsRecord|record-010|specimen|SPECIMEN_SOURCE_CAPILLARY_BLOOD"
* status = #available
* type = $sct#122554006 "Capillary blood specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectCapillaryGlucoseExample
InstanceOf: HealthConnectCapillaryBloodGlucose
Usage: #example
Title: "Health Connect Capillary Blood Glucose"
Description: "A Health Connect glucose result whose exact source specimen selects the capillary-blood profile and whose non-unknown meal context is retained."
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-004"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#32016-8 "Glucose [Mass/volume] in Capillary blood"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:15:00-07:00"
* issued = "2026-08-20T14:15:01Z"
* valueQuantity = 96 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectCapillaryGlucoseSpecimenExample)
* extension[glucoseMealContext].extension[relationToMeal].valueCoding = $healthConnectRelationToMeal#RELATION_TO_MEAL_FASTING "Fasting"
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord
* extension[glucoseMealContext].extension[mealType].valueCoding = $healthConnectMealType#MEAL_TYPE_BREAKFAST "Breakfast"

Instance: HealthConnectWholeBloodGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Whole Blood Specimen"
Description: "The standard-coded specimen node synthesized from an exact Health Connect whole-blood specimen source."
* identifier[specimenId].system = $healthConnectSpecimenId
* identifier[specimenId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-004|specimen|SPECIMEN_SOURCE_CAPILLARY_BLOOD"
* status = #available
* type = $sct#258580003 "Whole blood specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectWholeBloodGlucoseExample
InstanceOf: HealthConnectWholeBloodGlucose
Usage: #example
Title: "Health Connect Whole Blood Glucose"
Description: "A Health Connect glucose result whose exact source specimen selects the whole-blood profile."
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-011"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#2339-0 "Glucose [Mass/volume] in Blood"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:16:00-07:00"
* issued = "2026-08-20T14:16:01Z"
* valueQuantity = 95 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectWholeBloodGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord

Instance: HealthConnectSerumGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Serum Specimen"
Description: "The standard-coded specimen node synthesized from an exact Health Connect serum specimen source."
* identifier[specimenId].system = $healthConnectSpecimenId
* identifier[specimenId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-011|specimen|SPECIMEN_SOURCE_CAPILLARY_BLOOD"
* status = #available
* type = $sct#119364003 "Serum specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectSerumGlucoseExample
InstanceOf: HealthConnectSerumPlasmaGlucose
Usage: #example
Title: "Health Connect Serum Glucose"
Description: "A Health Connect glucose result whose exact source specimen selects the serum-or-plasma profile while preserving serum specifically."
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-008"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#2345-7 "Glucose [Mass/volume] in Serum or Plasma"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:17:00-07:00"
* issued = "2026-08-20T14:17:01Z"
* valueQuantity = 94 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectSerumGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord

Instance: HealthConnectInterstitialGlucoseSpecimenExample
InstanceOf: HealthConnectSpecimen
Usage: #example
Title: "Health Connect Interstitial Fluid Specimen"
Description: "The standard-coded specimen node synthesized from an exact Health Connect interstitial-fluid specimen source."
* identifier[specimenId].system = $healthConnectSpecimenId
* identifier[specimenId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-008|specimen|SPECIMEN_SOURCE_CAPILLARY_BLOOD"
* status = #available
* type = $sct#258479004 "Interstitial fluid specimen"
* subject = Reference(HealthConnectPatientExample)

Instance: HealthConnectInterstitialGlucoseExample
InstanceOf: HealthConnectInterstitialGlucose
Usage: #example
Title: "Health Connect Interstitial Fluid Glucose"
Description: "A Health Connect glucose result whose exact source specimen selects the interstitial-fluid profile."
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodGlucoseRecord|record-006"
* status = #final
* category = $observationCategory#laboratory "Laboratory"
* code = $loinc#99504-3 "Glucose [Mass/volume] in Interstitial fluid"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:18:00-07:00"
* issued = "2026-08-20T14:18:01Z"
* valueQuantity = 93 'mg/dL' "mg/dL"
* specimen = Reference(HealthConnectInterstitialGlucoseSpecimenExample)
* extension[healthConnectRecordType].valueCode = #BloodGlucoseRecord

Instance: HealthConnectBloodPressureExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Blood Pressure"
Description: "A Health Connect blood-pressure panel retaining standard body-position and measurement-site concepts."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-blood-pressure"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BloodPressureRecord|record-001"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#85354-9 "Blood pressure panel with all children optional"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:20:00-07:00"
* issued = "2026-08-20T14:20:01Z"
* component[+].code = $loinc#8480-6 "Systolic blood pressure"
* component[=].valueQuantity = 118 'mm[Hg]' "mmHg"
* component[+].code = $loinc#8462-4 "Diastolic blood pressure"
* component[=].valueQuantity = 76 'mm[Hg]' "mmHg"
* extension[bodyPosition].valueCodeableConcept = $sct#33586001 "Sitting position"
* extension[healthConnectRecordType].valueCode = #BloodPressureRecord
* bodySite = $sct#368208006 "Left upper arm structure"

Instance: HealthConnectBodyTemperatureExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Body Temperature"
Description: "A Health Connect body-temperature result retaining its standard oral-cavity measurement site."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-body-temperature"
* extension[healthConnectRecordType].valueCode = #BodyTemperatureRecord
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|BodyTemperatureRecord|record-002"
* status = #final
* category = $observationCategory#vital-signs "Vital Signs"
* code = $loinc#8310-5 "Body temperature"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectiveDateTime = "2026-08-20T07:25:00-07:00"
* issued = "2026-08-20T14:25:01Z"
* valueQuantity = 36.8 'Cel' "Cel"
* bodySite = $sct#74262004 "Oral cavity structure"

Instance: HealthConnectSleepDurationExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Sleep Duration Summary"
Description: "A source-neutral duration summary retaining a non-blank Health Connect title and note."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-duration"
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|SleepSessionRecord|record-009"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|SleepSessionRecord|record-009|sleep-stage|2026-08-19T02:10:00.000000000Z|2026-08-19T02:55:00.000000000Z|STAGE_TYPE_DEEP|0"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $loinc#93832-4 "Sleep duration"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T23:00:00-07:00"
* effectivePeriod.end = "2026-08-20T07:00:00-07:00"
* issued = "2026-08-20T14:00:01Z"
* valueQuantity = 7.5 'h' "h"
* extension[sleepTitle].valueString = "Night sleep"
* extension[healthConnectRecordType].valueCode = #SleepSessionRecord
* note.text = "Brief awakening recorded by the participant."

Instance: HealthConnectSleepStageExample
InstanceOf: HealthConnectObservation
Usage: #example
Title: "Health Connect Light Sleep Stage"
Description: "One sleep-session stage retaining both the shared light-sleep class and exact Health Connect source token."
* meta.profile[+] = "https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-stage"
* extension[healthConnectRecordType].valueCode = #SleepSessionRecord
* identifier[recordId].system = $healthConnectRecordId
* identifier[recordId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|SleepSessionRecord|record-009"
* identifier[outputId].system = $healthConnectOutputId
* identifier[outputId].value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|SleepSessionRecord|record-009|sleep-stage|2026-08-19T02:55:00.000000000Z|2026-08-19T03:20:00.000000000Z|STAGE_TYPE_REM|0"
* status = #final
* category = $observationCategory#activity "Activity"
* code = $groveMobileMeasurement#sleep-stage "Sleep stage"
* subject = Reference(HealthConnectPatientExample)
* performer = Reference(HealthConnectPatientExample)
* effectivePeriod.start = "2026-08-19T23:10:00-07:00"
* effectivePeriod.end = "2026-08-19T23:42:00-07:00"
* issued = "2026-08-20T14:00:01Z"
* valueCodeableConcept.coding[+] = $groveSleepStage#light "Light sleep"
* valueCodeableConcept.coding[+] = $healthConnectSleepStage#STAGE_TYPE_LIGHT "Light sleep"

Instance: HealthConnectHeartRateProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Heart Rate Conversion Provenance"
Description: "One source HeartRateRecord was transformed into two FHIR heart-rate Observations."
* target[+] = Reference(HealthConnectHeartRateSampleOneExample)
* target[+] = Reference(HealthConnectHeartRateSampleTwoExample)
* occurredDateTime = "2026-08-19T18:00:00Z"
* recorded = "2026-08-19T18:00:00Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|HeartRateRecord|record-005"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who = Reference(HealthConnectSourceApplicationExample)

Instance: HealthConnectBodyWeightProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Body Weight Conversion Provenance"
Description: "The source WeightRecord and DataOrigin application for the converted body-weight Observation."
* target = Reference(HealthConnectBodyWeightExample)
* occurredDateTime = "2026-08-19T18:00:00Z"
* recorded = "2026-08-19T18:00:00Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|WeightRecord|record-003"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who = Reference(HealthConnectSourceApplicationExample)

Instance: HealthConnectStepCountProvenanceExample
InstanceOf: HealthConnectConversionProvenance
Usage: #example
Title: "Health Connect Step Count Conversion Provenance"
Description: "The source StepsRecord and DataOrigin application for the converted step-count Observation."
* target = Reference(HealthConnectStepCountExample)
* occurredDateTime = "2026-08-19T18:00:00Z"
* recorded = "2026-08-19T18:00:00Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(HealthConnectConverterApplicationExample)
* entity.role = #source
* entity.what.identifier.system = $healthConnectRecordId
* entity.what.identifier.value = "v1:1f5c58aa-6ec6-4e79-a682-829a9debd3f5|StepsRecord|record-010"
* entity.agent.type = $provenanceParticipantType#enterer "Enterer"
* entity.agent.who = Reference(HealthConnectSourceApplicationExample)

Instance: HealthConnectStudyBundleExample
InstanceOf: Bundle
Usage: #example
Title: "Health Connect Documentation Bundle"
Description: "An aggregate profile-validation fixture containing the participant, study context, devices, converted Observations, and source-linked conversion Provenance from several source records. It is not an operational synchronization event."
* type = #collection
* timestamp = "2026-08-19T18:00:00Z"
* entry[+].fullUrl = "https://study.example.org/fhir/Patient/HealthConnectPatientExample"
* entry[=].resource = HealthConnectPatientExample
* entry[+].fullUrl = "https://study.example.org/fhir/PlanDefinition/HealthConnectStudyPlanExample"
* entry[=].resource = HealthConnectStudyPlanExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchStudy/HealthConnectResearchStudyExample"
* entry[=].resource = HealthConnectResearchStudyExample
* entry[+].fullUrl = "https://study.example.org/fhir/ResearchSubject/HealthConnectResearchSubjectExample"
* entry[=].resource = HealthConnectResearchSubjectExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthConnectRecordingDeviceExample"
* entry[=].resource = HealthConnectRecordingDeviceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthConnectConverterApplicationExample"
* entry[=].resource = HealthConnectConverterApplicationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Device/HealthConnectSourceApplicationExample"
* entry[=].resource = HealthConnectSourceApplicationExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectHeartRateSampleOneExample"
* entry[=].resource = HealthConnectHeartRateSampleOneExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectHeartRateSampleTwoExample"
* entry[=].resource = HealthConnectHeartRateSampleTwoExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectBodyWeightExample"
* entry[=].resource = HealthConnectBodyWeightExample
* entry[+].fullUrl = "https://study.example.org/fhir/Observation/HealthConnectStepCountExample"
* entry[=].resource = HealthConnectStepCountExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthConnectHeartRateProvenanceExample"
* entry[=].resource = HealthConnectHeartRateProvenanceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthConnectBodyWeightProvenanceExample"
* entry[=].resource = HealthConnectBodyWeightProvenanceExample
* entry[+].fullUrl = "https://study.example.org/fhir/Provenance/HealthConnectStepCountProvenanceExample"
* entry[=].resource = HealthConnectStepCountProvenanceExample
