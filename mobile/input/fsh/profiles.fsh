//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: grove-mobile-result-1
Description: "A mobile Observation has a value, one or more components or members, or a reason why the result is absent."
Expression: "value.exists() or component.where(value.exists() or dataAbsentReason.exists()).exists() or hasMember.exists() or dataAbsentReason.exists()"
Severity: #error

Invariant: grove-identifier-token-1
Description: "A resource does not repeat the same identifier system and value pair."
Expression: "identifier.select(system.length().toString() & ':' & system & value.length().toString() & ':' & value).isDistinct()"
Severity: #error

Invariant: grove-step-count-result-1
Description: "A step-count Observation has a count value or a reason why the count is absent."
Expression: "value.exists() or dataAbsentReason.exists()"
Severity: #error

Invariant: grove-step-count-period-1
Description: "A step-count Observation has a non-zero effective Period."
Expression: "effective.ofType(Period).end > effective.ofType(Period).start"
Severity: #error

Invariant: grove-step-count-value-1
Description: "A populated step count is not negative."
Expression: "value.empty() or value.ofType(Quantity).value >= 0"
Severity: #error

Invariant: grove-exchange-full-url-1
Description: "Every exchange entry has a distinct lowercase RFC 4122 UUID URN fullUrl."
Expression: "entry.all(fullUrl.matches('^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')) and entry.fullUrl.isDistinct()"
Severity: #error

Invariant: grove-exchange-entry-identity-1
Description: "Exchange entry business identifier system and value pairs are distinct."
Expression: "entry.extension('https://grovealliance.org/fhir/mobile/StructureDefinition/grove-exchange-entry-identifier').value.ofType(Identifier).select(system.length().toString() & ':' & system & value.length().toString() & ':' & value).isDistinct()"
Severity: #error

RuleSet: CompleteIdentifierPairs
* identifier.system 1..1 MS
* identifier.value 1..1 MS

RuleSet: GroveMobileObservationRules
* obeys grove-mobile-result-1 and grove-identifier-token-1
* insert CompleteIdentifierPairs
* identifier 1..* MS
* identifier ^short = "Stable business identifier used to deduplicate this exchanged record"
* status 1..1 MS
* category MS
* code 1..1 MS
* subject 1..1 MS
* subject only Reference(Patient)
* effective[x] 1..1 MS
* effective[x] only dateTime or Period
* effectiveDateTime MS
* effectiveDateTime.extension contains $timezone named timezone 0..1 MS
* effectivePeriod MS
* effectivePeriod.start 1..1 MS
* effectivePeriod.start.extension contains $timezone named startTimezone 0..1 MS
* effectivePeriod.end MS
* effectivePeriod.end.extension contains $timezone named endTimezone 0..1 MS
* issued MS
* value[x] MS
* dataAbsentReason MS
* component MS
* bodySite MS
* method MS
* device MS
* hasMember MS
* derivedFrom MS
* extension contains
    GroveRecordingMethod named recordingMethod 0..1 MS and
    $gatewayDevice named gatewayDevice 0..1 MS and
    $researchStudy named researchStudy 0..* MS
* extension[gatewayDevice].valueReference only Reference(GroveApplicationDevice)
* extension[researchStudy].valueReference only Reference(ResearchStudy)

RuleSet: GroveMobilePointObservationContextRules
* obeys grove-identifier-token-1
* insert CompleteIdentifierPairs
* identifier 1..* MS
* identifier ^short = "Stable business identifier used to deduplicate this exchanged record"
* subject 1..1 MS
* subject only Reference(Patient)
* effectiveDateTime 1..1 MS
* effectiveDateTime.extension contains $timezone named timezone 0..1 MS
* issued MS
* device MS
* derivedFrom MS
* extension contains
    GroveRecordingMethod named recordingMethod 0..1 MS and
    $gatewayDevice named gatewayDevice 0..1 MS and
    $researchStudy named researchStudy 0..* MS
* extension[gatewayDevice].valueReference only Reference(GroveApplicationDevice)
* extension[researchStudy].valueReference only Reference(ResearchStudy)

Extension: GroveExchangeEntryIdentifier
Id: grove-exchange-entry-identifier
Title: "Grove Exchange Entry Identifier"
Description: "The complete business identifier from which an exchange Bundle entry fullUrl is deterministically derived. It identifies the graph node and does not replace a resource's native identifier or canonical URL."
Context: Bundle.entry
* value[x] only Identifier
* valueIdentifier 1..1
* valueIdentifier.system 1..1 MS
* valueIdentifier.value 1..1 MS

Profile: GroveMobileExchangeBundle
Parent: Bundle
Id: grove-mobile-exchange-bundle
Title: "Grove Mobile Exchange Bundle"
Description: "A source-neutral collection Bundle carrying one internally consistent mobile health resource graph. Entry UUID URNs are deterministic from complete entry business identifiers; Resource.id is not used for source identity."
* obeys grove-exchange-full-url-1 and grove-exchange-entry-identity-1
* identifier 1..1 MS
* identifier.system 1..1 MS
* identifier.value 1..1 MS
* type = #collection
* timestamp 1..1 MS
* entry 1..* MS
* entry.extension contains GroveExchangeEntryIdentifier named entryIdentifier 1..1 MS
* entry.fullUrl 1..1 MS
* entry.resource 1..1 MS
* entry.search 0..0
* entry.request 0..0
* entry.response 0..0

Profile: GroveRecordingDevice
Parent: Device
Id: grove-recording-device
Title: "Grove Recording Device"
Description: "The physical device that acquired a measurement. Observation.device references this profile only when the recorder is known."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1
* identifier MS
* status MS
* type MS
* deviceName MS
* manufacturer MS
* modelNumber MS
* version MS
* version.type 1..1 MS
* version.value MS

Profile: GroveApplicationDevice
Parent: Device
Id: grove-application-device
Title: "Grove Application Device"
Description: "The software application that saved, routed, or converted a mobile record. The application is distinct from the physical recording device and from its host hardware."
* insert CompleteIdentifierPairs
* obeys grove-identifier-token-1
* identifier 1..* MS
* deviceName 1..* MS
* deviceName ^slicing.discriminator.type = #value
* deviceName ^slicing.discriminator.path = "type"
* deviceName ^slicing.rules = #open
* deviceName contains applicationName 1..1 MS
* deviceName[applicationName].name 1..1 MS
* deviceName[applicationName].type = #user-friendly-name
* version ^slicing.discriminator.type = #pattern
* version ^slicing.discriminator.path = "type"
* version ^slicing.rules = #open
* version contains applicationVersion 0..1 MS
* version[applicationVersion].type 1..1 MS
* version[applicationVersion].type = $mdc#531975
* version[applicationVersion].value 1..1 MS
* parent MS
* parent only Reference(Device)

Profile: GroveMobileObservation
Parent: Observation
Id: grove-mobile-observation
Title: "Grove Mobile Observation"
Description: "A source-neutral FHIR R4 exchange envelope for a measurement collected through a mobile application or connected device. Combine it with an appropriate clinical or research profile."
* insert GroveMobileObservationRules

Profile: GroveMobileHeartRate
Parent: GroveMobileObservation
Id: grove-mobile-heart-rate
Title: "Grove Mobile Heart Rate"
Description: "A source-neutral mobile heart rate that is required to conform to the authoritative FHIR R4 Heart Rate profile and adds Grove exchange identity and provenance context. Values are normalized to UCUM beats per minute."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $heartRate
* code = $loinc#8867-4
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileBodyWeight
Parent: GroveMobileObservation
Id: grove-mobile-body-weight
Title: "Grove Mobile Body Weight"
Description: "A source-neutral mobile body weight that is required to conform to the authoritative FHIR R4 Body Weight profile. Values are normalized to UCUM kilograms."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyWeight
* code = $loinc#29463-7
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #kg (exactly)

Profile: GroveMobileBloodPressure
Parent: GroveMobileObservation
Id: grove-mobile-blood-pressure
Title: "Grove Mobile Blood Pressure"
Description: "A source-neutral mobile blood-pressure panel that is required to conform to the authoritative FHIR R4 Blood Pressure profile. Systolic and diastolic components are normalized to UCUM millimetres of mercury."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bloodPressure
* code = $loinc#85354-9
* effective[x] only dateTime
* value[x] 0..0
* component ^slicing.discriminator.type = #pattern
* component ^slicing.discriminator.path = "code"
* component ^slicing.rules = #open
* component contains systolic 1..1 MS and diastolic 1..1 MS
* component[systolic].code = $loinc#8480-6
* component[systolic].value[x] only Quantity
* component[systolic].valueQuantity.value 1..1 MS
* component[systolic].valueQuantity.system = $ucum (exactly)
* component[systolic].valueQuantity.code = #mm[Hg] (exactly)
* component[diastolic].code = $loinc#8462-4
* component[diastolic].value[x] only Quantity
* component[diastolic].valueQuantity.value 1..1 MS
* component[diastolic].valueQuantity.system = $ucum (exactly)
* component[diastolic].valueQuantity.code = #mm[Hg] (exactly)

Profile: GroveMobileBodyTemperature
Parent: GroveMobileObservation
Id: grove-mobile-body-temperature
Title: "Grove Mobile Body Temperature"
Description: "A source-neutral mobile body temperature that is required to conform to the authoritative FHIR R4 Body Temperature profile. Values are normalized to UCUM degrees Celsius."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyTemperature
* code = $loinc#8310-5
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #Cel (exactly)

Profile: GroveMobileRespiratoryRate
Parent: GroveMobileObservation
Id: grove-mobile-respiratory-rate
Title: "Grove Mobile Respiratory Rate"
Description: "A source-neutral mobile respiratory rate that is required to conform to the authoritative FHIR R4 Respiratory Rate profile. Values are normalized to breaths per minute."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $respiratoryRate
* code = $loinc#9279-1
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #/min (exactly)

Profile: GroveMobileOxygenSaturation
Parent: GroveMobileObservation
Id: grove-mobile-oxygen-saturation
Title: "Grove Mobile Oxygen Saturation"
Description: "A source-neutral mobile oxygen saturation that is required to conform to the authoritative FHIR R4 Oxygen Saturation profile. Values are normalized to UCUM percent."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $oxygenSaturation
* code = $loinc#2708-6
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #% (exactly)

Profile: GroveMobileBodyHeight
Parent: GroveMobileObservation
Id: grove-mobile-body-height
Title: "Grove Mobile Body Height"
Description: "A source-neutral mobile body height that is required to conform to the authoritative FHIR R4 Body Height profile. Values are normalized to UCUM centimetres."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyHeight
* code = $loinc#8302-2
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #cm (exactly)

Profile: GroveMobileBMI
Parent: GroveMobileObservation
Id: grove-mobile-bmi
Title: "Grove Mobile Body Mass Index"
Description: "A source-neutral mobile body mass index that is required to conform to the authoritative FHIR R4 BMI profile. Values are normalized to UCUM kilograms per square metre."
* ^extension[+].url = $imposeProfile
* ^extension[=].valueCanonical = $bodyMassIndex
* code = $loinc#39156-5
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code = #kg/m2 (exactly)

Profile: GroveMobileBloodGlucose
Parent: GroveMobileObservation
Id: grove-mobile-blood-glucose
Title: "Grove Mobile Whole-blood Glucose"
Description: "A point-in-time mass concentration of glucose in whole blood, normalized to UCUM milligrams per decilitre. Producers must not apply this profile to capillary blood, serum, plasma, interstitial fluid, tears, or an unknown specimen."
* code = $loinc#2339-0
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)

Profile: GroveMobileCapillaryBloodGlucose
Parent: GroveMobileObservation
Id: grove-mobile-capillary-blood-glucose
Title: "Grove Mobile Capillary-blood Glucose"
Description: "A point-in-time mass concentration of glucose in capillary blood, normalized to UCUM milligrams per decilitre."
* code = $loinc#32016-8
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)

Profile: GroveMobileSerumPlasmaGlucose
Parent: GroveMobileObservation
Id: grove-mobile-serum-plasma-glucose
Title: "Grove Mobile Serum or Plasma Glucose"
Description: "A point-in-time mass concentration of glucose in serum or plasma, normalized to UCUM milligrams per decilitre. The referenced Specimen retains whether the source was serum or plasma."
* code = $loinc#2345-7
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)

Profile: GroveMobileInterstitialGlucose
Parent: GroveMobileObservation
Id: grove-mobile-interstitial-glucose
Title: "Grove Mobile Interstitial-fluid Glucose"
Description: "A point-in-time mass concentration of glucose in interstitial fluid, normalized to UCUM milligrams per decilitre."
* code = $loinc#99504-3
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #mg/dL (exactly)

Profile: GroveMobileBasalBodyTemperature
Parent: GroveMobileObservation
Id: grove-mobile-basal-body-temperature
Title: "Grove Mobile Basal Body Temperature"
Description: "A source-neutral basal body temperature recorded at physiologic rest and normalized to UCUM degrees Celsius. It is not the general body-temperature vital sign."
* code = GroveMobileMeasurementCS#basal-body-temperature
* code from GroveMobileMeasurementVS (required)
* effective[x] only dateTime
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #Cel (exactly)

Profile: GroveMobileDistance
Parent: GroveMobileObservation
Id: grove-mobile-distance
Title: "Grove Mobile Distance"
Description: "Distance traveled during an exact effective Period, normalized to UCUM metres."
* code = GroveMobileMeasurementCS#distance-traveled
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #m (exactly)

Profile: GroveMobileActiveEnergy
Parent: GroveMobileObservation
Id: grove-mobile-active-energy
Title: "Grove Mobile Active Energy"
Description: "Activity-related energy expenditure, excluding basal energy, during an exact effective Period and normalized to UCUM kilocalories."
* code = GroveMobileMeasurementCS#active-energy-burned
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #kcal (exactly)

Profile: GroveMobileSleepDuration
Parent: GroveMobileObservation
Id: grove-mobile-sleep-duration
Title: "Grove Mobile Sleep Duration"
Description: "Total duration classified as sleep during an exact effective Period, using LOINC Sleep duration and normalized to UCUM hours. This summary does not encode sleep stages."
* code = $loinc#93832-4
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #h (exactly)
* hasMember only Reference(GroveMobileSleepStage)

Profile: GroveMobileSleepStage
Parent: GroveMobileObservation
Id: grove-mobile-sleep-stage
Title: "Grove Mobile Sleep Stage"
Description: "A source-neutral sleep-stage classification for one exact interval. A session summary links its ordered, non-overlapping stage Observations through hasMember."
* code = GroveMobileMeasurementCS#sleep-stage
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only CodeableConcept
* valueCodeableConcept 1..1 MS
* valueCodeableConcept from GroveSleepStageVS (required)

Profile: GroveMobileStepCount
Parent: GroveMobileObservation
Id: grove-mobile-step-count
Title: "Grove Mobile Step Count"
Description: "The number of steps recorded during an exact effective Period."
* obeys grove-step-count-result-1 and grove-step-count-period-1 and grove-step-count-value-1
* code = GroveMobileMeasurementCS#step-count-total
* code from GroveMobileMeasurementVS (required)
* effective[x] only Period
* effectivePeriod.end 1..1 MS
* value[x] only Quantity
* valueQuantity.value 1..1 MS
* valueQuantity.comparator 0..0
* valueQuantity.unit MS
* valueQuantity.system 1..1 MS
* valueQuantity.system = $ucum (exactly)
* valueQuantity.code 1..1 MS
* valueQuantity.code = #{steps} (exactly)

Profile: GroveMobileConversionProvenance
Parent: Provenance
Id: grove-mobile-conversion-provenance
Title: "Grove Mobile Conversion Provenance"
Description: "Provenance for the application that transformed one or more source records into mobile Observations."
* target 1..* MS
* target only Reference(GroveMobileObservation)
* occurred[x] MS
* recorded 1..1 MS
* activity 1..1 MS
* activity = $recordLifecycleEvent#transform
* agent 1..* MS
* agent ^slicing.discriminator.type = #pattern
* agent ^slicing.discriminator.path = "type"
* agent ^slicing.rules = #open
* agent contains assembler 1..1 MS
* agent[assembler].type 1..1 MS
* agent[assembler].type = $provenanceParticipantType#assembler
* agent[assembler].who 1..1 MS
* agent[assembler].who only Reference(GroveApplicationDevice)
* entity 1..* MS
* entity.role 1..1 MS
* entity.role = #source
* entity.what MS
