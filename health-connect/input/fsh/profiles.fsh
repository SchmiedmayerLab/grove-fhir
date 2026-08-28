//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: health-connect-specimen-type-1
Description: "A synthesized glucose specimen carries exactly one admitted standard SNOMED CT specimen concept."
Severity: #error
Expression: "type.coding.where(system = 'http://snomed.info/sct').count() = 1 and type.coding.where(system = 'http://snomed.info/sct' and (code = '258580003' or code = '122554006' or code = '119361006' or code = '119364003' or code = '258479004')).count() = 1"

Invariant: health-connect-glucose-specimen-1
Description: "Only a supported glucose output has a specimen, and every supported glucose output has one."
Severity: #error
Expression: "(code.coding.where(system = 'http://loinc.org' and (code = '2339-0' or code = '32016-8' or code = '2345-7' or code = '99504-3')).exists()) = specimen.exists()"

Invariant: health-connect-body-position-1
Description: "The standard body-position extension is present only on a BloodPressureRecord output and contains exactly one admitted SNOMED CT body position when present."
Severity: #error
Expression: "extension.where(url = 'http://hl7.org/fhir/StructureDefinition/observation-bodyPosition').empty() or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'BloodPressureRecord' and extension.where(url = 'http://hl7.org/fhir/StructureDefinition/observation-bodyPosition').value.ofType(CodeableConcept).coding.where(system = 'http://snomed.info/sct').count() = 1 and extension.where(url = 'http://hl7.org/fhir/StructureDefinition/observation-bodyPosition').value.ofType(CodeableConcept).coding.where(system = 'http://snomed.info/sct' and (code = '10904000' or code = '33586001' or code = '102538003' or code = '272580008')).count() = 1)"

Invariant: health-connect-body-site-applicability-1
Description: "Health Connect body-site context is present only on a source Record whose adapter mapping admits it."
Severity: #error
Expression: "bodySite.empty() or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'BloodPressureRecord' or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'BasalBodyTemperatureRecord' or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'BodyTemperatureRecord' or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'SkinTemperatureRecord'"

Invariant: health-connect-blood-pressure-site-1
Description: "A BloodPressureRecord body site contains exactly one admitted SNOMED CT measurement location when present."
Severity: #error
Expression: "extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'BloodPressureRecord' or bodySite.empty() or (bodySite.coding.where(system = 'http://snomed.info/sct').count() = 1 and bodySite.coding.where(system = 'http://snomed.info/sct' and (code = '5951000' or code = '9736006' or code = '368208006' or code = '368209003')).count() = 1)"

Invariant: health-connect-temperature-site-1
Description: "A basal or general body-temperature body site contains exactly one admitted SNOMED CT measurement location when present."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'BasalBodyTemperatureRecord' and extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'BodyTemperatureRecord') or bodySite.empty() or (bodySite.coding.where(system = 'http://snomed.info/sct').count() = 1 and bodySite.coding.where(system = 'http://snomed.info/sct' and (code = '422543003' or code = '7569003' or code = '52795006' or code = '74262004' or code = '34402009' or code = '15672000' or code = '29707007' or code = '117590005' or code = '8205005' or code = '76784001')).count() = 1)"

Invariant: health-connect-skin-temperature-site-1
Description: "A SkinTemperatureRecord body site contains exactly one of its three admitted SNOMED CT measurement locations when present."
Severity: #error
Expression: "extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'SkinTemperatureRecord' or bodySite.empty() or (bodySite.coding.where(system = 'http://snomed.info/sct').count() = 1 and bodySite.coding.where(system = 'http://snomed.info/sct' and (code = '7569003' or code = '29707007' or code = '8205005')).count() = 1)"

Invariant: health-connect-meal-context-1
Description: "Health Connect meal context is present only on a supported glucose output."
Severity: #error
Expression: "extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-glucose-meal-context').empty() or code.coding.where(system = 'http://loinc.org' and (code = '2339-0' or code = '32016-8' or code = '2345-7' or code = '99504-3')).exists()"

Invariant: health-connect-user-authored-text-1
Description: "Source notes occur only on their exact SleepSessionRecord, MindfulnessSessionRecord, or ExerciseSessionRecord summary output; the shared title extension has its own applicability invariant."
Severity: #error
Expression: "note.empty() or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'SleepSessionRecord' and code.coding.where(system = 'http://loinc.org' and code = '93832-4').exists()) or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'MindfulnessSessionRecord' or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'ExerciseSessionRecord' and code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'workout').exists())"

Invariant: health-connect-source-coded-value-1
Description: "Every source-coded menstrual, ovulation, sexual-activity, and cervical-mucus value carries exactly one admitted exact Health Connect coding; those code systems occur nowhere else."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'MenstruationFlowRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-menstruation-flow' and (code = 'FLOW_UNKNOWN' or code = 'FLOW_LIGHT' or code = 'FLOW_MEDIUM' or code = 'FLOW_HEAVY')).count() = 1 or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'MenstruationFlowRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-menstruation-flow').empty()) and (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'OvulationTestRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-ovulation-test-result' and (code = 'RESULT_NEGATIVE' or code = 'RESULT_HIGH' or code = 'RESULT_POSITIVE' or code = 'RESULT_INCONCLUSIVE')).count() = 1 or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'OvulationTestRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-ovulation-test-result').empty()) and (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'SexualActivityRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sexual-activity-protection' and (code = 'PROTECTION_USED_UNKNOWN' or code = 'PROTECTION_USED_PROTECTED' or code = 'PROTECTION_USED_UNPROTECTED')).count() = 1 or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'SexualActivityRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sexual-activity-protection').empty()) and (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'CervicalMucusRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-cervical-mucus-appearance' and (code = 'APPEARANCE_UNKNOWN' or code = 'APPEARANCE_DRY' or code = 'APPEARANCE_STICKY' or code = 'APPEARANCE_CREAMY' or code = 'APPEARANCE_WATERY' or code = 'APPEARANCE_EGG_WHITE' or code = 'APPEARANCE_UNUSUAL')).count() = 1 or extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'CervicalMucusRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-cervical-mucus-appearance').empty())"

Invariant: health-connect-cervical-mucus-sensation-1
Description: "A cervical-mucus sensation component is optional for UNKNOWN and otherwise carries exactly one admitted exact Health Connect sensation coding; that code system occurs nowhere else."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'CervicalMucusRecord' and component.where(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'cervical-mucus-sensation').exists()).value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-cervical-mucus-sensation').count() <= 1 and component.where(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'cervical-mucus-sensation').exists()).value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-cervical-mucus-sensation' and (code = 'SENSATION_LIGHT' or code = 'SENSATION_MEDIUM' or code = 'SENSATION_HEAVY')).count() = component.where(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'cervical-mucus-sensation').exists()).count()) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'CervicalMucusRecord' and component.value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-cervical-mucus-sensation').empty())"

Invariant: health-connect-exercise-context-1
Description: "A workout summary carries one admitted exact ExerciseSessionRecord activity coding, while every segment or lap carries one admitted exact segment coding; neither source system leaks to any other output."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'ExerciseSessionRecord' and code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'workout').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-type').count() = 1 and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-type').memberOf('https://grovealliance.org/fhir/health-connect/ValueSet/health-connect-exercise-type') and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-segment-type').empty()) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'ExerciseSessionRecord' and code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'workout-segment').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-type').empty() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-segment-type').count() = 1 and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-segment-type').memberOf('https://grovealliance.org/fhir/health-connect/ValueSet/health-connect-exercise-segment-type')) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'ExerciseSessionRecord' and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-type' or system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-exercise-segment-type').empty())"

Invariant: health-connect-sleep-stage-1
Description: "A shared sleep-stage output carries exactly one exact Health Connect source stage coding, and no other output carries one."
Severity: #error
Expression: "(code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').exists() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sleep-stage').count() = 1) or (code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'sleep-stage').empty() and value.ofType(CodeableConcept).coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-sleep-stage').empty())"

Invariant: health-connect-mindfulness-context-1
Description: "Only a MindfulnessSessionRecord output carries one exact mindfulness method coding; no other source record carries that method system."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'MindfulnessSessionRecord' and method.coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-mindfulness-session-type').count() = 1 and method.coding.count() = 1) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'MindfulnessSessionRecord' and method.coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-mindfulness-session-type').empty())"

Invariant: health-connect-session-title-1
Description: "The shared session-title extension occurs only on the primary workout, sleep-duration, or mindfulness-session summary produced by its matching Health Connect session record."
Severity: #error
Expression: "extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-session-title').empty() or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-session-title').count() = 1 and ((extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'ExerciseSessionRecord' and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-workout').exists() and code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'workout').exists()) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'SleepSessionRecord' and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-sleep-duration').exists() and code.coding.where(system = 'http://loinc.org' and code = '93832-4').exists()) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'MindfulnessSessionRecord' and meta.profile.where($this = 'https://grovealliance.org/fhir/mobile/StructureDefinition/grove-mobile-mindfulness-session').exists() and code.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-mobile-measurement' and code = 'mindfulness-session-duration').exists())))"

Invariant: health-connect-session-text-nonblank-1
Description: "Every retained source title and note contains at least one non-whitespace character. Blank source strings are omitted, not emitted."
Severity: #error
Expression: "extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-session-title').all(value.ofType(string).matches('(?s).*\\\\S.*')) and note.all(text.toString().matches('(?s).*\\\\S.*'))"

Invariant: health-connect-vo2-method-1
Description: "A Vo2MaxRecord carries exactly one exact AndroidX measurement-method Coding, and no other source record carries that method system."
Severity: #error
Expression: "(extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) = 'Vo2MaxRecord' and method.coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-vo2-max-measurement-method').count() = 1 and method.coding.count() = 1) or (extension.where(url = 'https://grovealliance.org/fhir/health-connect/StructureDefinition/health-connect-record-type').value.ofType(code) != 'Vo2MaxRecord' and method.coding.where(system = 'https://grovealliance.org/fhir/health-connect/CodeSystem/health-connect-vo2-max-measurement-method').empty())"

Invariant: health-connect-opaque-identifier-value-1
Description: "A Health Connect source or output identifier is a canonical deployment-scoped Grove v2 HMAC value."
Expression: "$this.matches('^v2:[A-Za-z0-9._-]+:[1-9][0-9]*:[A-Za-z0-9_-]{43}$')"
Severity: #error

Invariant: health-connect-writer-record-1
Description: "Health Connect always carries a clientRecordVersion for a Record that has a clientRecordId, so the two appear together or not at all. A client record version orders revisions of one writer-assigned record, so it appears only with the client record identifier it versions."
Expression: "extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-writer-record-version').exists() = identifier.where(type.coding.where(system = 'https://grovealliance.org/fhir/mobile/CodeSystem/grove-identifier-role' and code = 'writer-record').exists()).exists()"
Severity: #error


Profile: HealthConnectObservation
Parent: GroveMobileObservation
Id: health-connect-observation
Title: "Health Connect Observation"
Description: "The source and output identities plus allowlisted source context for a result converted from an AndroidX Health Connect 1.1 Record. Each output uses one exact profile-claim mode admitted by the shared profile-claims catalog: this adapter envelope with a shared Grove measurement profile, or a more specific Health Connect result profile."
* obeys health-connect-glucose-specimen-1 and health-connect-body-position-1 and health-connect-body-site-applicability-1 and health-connect-blood-pressure-site-1 and health-connect-temperature-site-1 and health-connect-skin-temperature-site-1 and health-connect-meal-context-1 and health-connect-user-authored-text-1 and health-connect-source-coded-value-1 and health-connect-cervical-mucus-sensation-1 and health-connect-exercise-context-1 and health-connect-sleep-stage-1 and health-connect-mindfulness-context-1 and health-connect-session-title-1 and health-connect-session-text-nonblank-1 and health-connect-vo2-method-1 and health-connect-writer-record-1
* issued 1..1 MS
* identifier 2..* MS
* identifier ^slicing.rules = #open
* specimen only Reference(HealthConnectSpecimen)
* extension contains
    HealthConnectRecordType named healthConnectRecordType 1..1 MS and
    $bodyPosition named bodyPosition 0..1 MS and
    HealthConnectGlucoseMealContext named glucoseMealContext 0..1 MS and
    HealthConnectSessionTitle named sessionTitle 0..1 MS
* note 0..1 MS
* note.author[x] 0..0
* note.time 0..0

Profile: HealthConnectWholeBloodGlucose
Parent: HealthConnectObservation
Id: health-connect-whole-blood-glucose
Title: "Health Connect Whole-blood Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit whole-blood specimen evidence. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#2339-0
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectCapillaryBloodGlucose
Parent: HealthConnectObservation
Id: health-connect-capillary-blood-glucose
Title: "Health Connect Capillary-blood Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit capillary-blood specimen evidence. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#32016-8
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectSerumPlasmaGlucose
Parent: HealthConnectObservation
Id: health-connect-serum-plasma-glucose
Title: "Health Connect Serum or Plasma Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit serum or plasma specimen evidence. The referenced Specimen preserves which source enum was present. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#2345-7
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectInterstitialGlucose
Parent: HealthConnectObservation
Id: health-connect-interstitial-glucose
Title: "Health Connect Interstitial-fluid Glucose"
Description: "A Health Connect BloodGlucoseRecord with explicit interstitial-fluid specimen evidence. This adapter-specific profile is not a shared Mobile profile."
* code = $loinc#99504-3
* effective[x] only dateTime
* value[x] 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)
* specimen 1..1 MS

Profile: HealthConnectSpecimen
Parent: Specimen
Id: health-connect-specimen
Title: "Health Connect Glucose Specimen"
Description: "A standard-coded specimen node synthesized only when a supported Health Connect BloodGlucoseRecord supplies an exact admitted specimen-source enum."
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier 2..2 MS
* identifier ^slicing.rules = #closed
* identifier contains sourceRecord 1..1 MS and sourceOutput 1..1 MS
* identifier[sourceRecord].type = $groveIdentifierRole#source-record
* identifier[sourceRecord].system 1..1 MS
* identifier[sourceRecord].value 1..1 MS
* identifier[sourceRecord].value obeys health-connect-opaque-identifier-value-1
* identifier[sourceOutput].type = $groveIdentifierRole#source-output
* identifier[sourceOutput].system 1..1 MS
* identifier[sourceOutput].value 1..1 MS
* identifier[sourceOutput].value obeys health-connect-opaque-identifier-value-1
* status = #available
* type 1..1 MS
* obeys health-connect-specimen-type-1
* subject 1..1 MS
* subject only Reference(Patient)

Profile: HealthConnectConversionProvenance
Parent: GroveMobileConversionProvenance
Id: health-connect-conversion-provenance
Title: "Health Connect Conversion Provenance"
Description: "Provenance for transforming one Health Connect source Record into every exact Observation and synthesized Specimen output from that Record, including the DataOrigin application that entered the Record into Health Connect."
* target 1..* MS
* target only Reference(HealthConnectObservation or HealthConnectSpecimen)
* entity 1..1 MS
* entity.role = #source
* entity.what.reference 0..0
* entity.what.identifier 1..1 MS
* entity.what.identifier.type 1..1 MS
* entity.what.identifier.type = $groveIdentifierRole#source-record
* entity.what.identifier.system 1..1 MS
* entity.what.identifier.value 1..1 MS
* entity.what.identifier.value obeys health-connect-opaque-identifier-value-1
* entity.agent 1..1 MS
* entity.agent.type 1..1 MS
* entity.agent.type = $provenanceParticipantType#enterer
* entity.agent.who 1..1 MS
* entity.agent.who only Reference(Device)
* entity.agent.who.reference 0..0
* entity.agent.who.type 1..1 MS
* entity.agent.who.type = "Device"
* entity.agent.who.identifier 1..1 MS
* entity.agent.who.identifier.system 1..1 MS
* entity.agent.who.identifier.system = $androidPackageName
* entity.agent.who.identifier.value 1..1 MS
