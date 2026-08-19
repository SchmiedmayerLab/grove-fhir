//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// The conformance load lives in profiles (US Core / Physical Activity IG structure):
// extensions stay small and reusable; cardinality, mustSupport, bindings, and linkage
// rules live here.

Profile: GroveSensorDevice
Parent: Device
Id: grove-sensor-device
Title: "Grove Sensor Device"
Description: """
The hardware that recorded a mobile health observation, such as a watch, chest strap,
scale, ring, or phone. `Observation.device` references this resource.

Use a contained Device when the source platform does not provide a stable, independently
resolvable device record. An external reference may be used when such a record exists.
The profile aligns device version types with the Personal Health Device IG while allowing
the partial device information commonly supplied by mobile platforms.
"""
* deviceName MS
* deviceName ^slicing.discriminator.type = #value
* deviceName ^slicing.discriminator.path = "type"
* deviceName ^slicing.rules = #open
* deviceName contains userFriendlyName 0..1 MS
* deviceName[userFriendlyName].type = #user-friendly-name
* deviceName[userFriendlyName] ^short = "The device's user-facing name"
* manufacturer MS
* modelNumber MS
* type from GroveDeviceTypeVS (extensible)
* type ^short = "Coarse form factor (watch, phone, scale, …)"
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains systemId 0..1 MS and deviceLocalId 0..1 MS
* identifier[systemId].type = http://terminology.hl7.org/CodeSystem/ContinuaDeviceIdentifiers#SYSID
* identifier[systemId].system = "urn:oid:1.2.840.10004.1.1.1.0.0.1.0.0.1.2680"
* identifier[systemId].value 1..1
* identifier[systemId] ^short = "IEEE EUI-64 system id (PHD STU2 pattern) — use whenever the hardware exposes one"
* identifier[deviceLocalId].system = $sidDeviceLocalId
* identifier[deviceLocalId].value 1..1
* identifier[deviceLocalId] ^short = "The platform's local device identifier, when no EUI-64 is exposed"
* identifier ^short = "EUI-64 system id when available; otherwise the platform-local identifier"
* udiCarrier.deviceIdentifier MS
* udiCarrier.deviceIdentifier ^short = "UDI device identifier, when the platform supplies one"
* version MS
* version ^slicing.discriminator.type = #pattern
* version ^slicing.discriminator.path = "type"
* version ^slicing.rules = #open
* version contains hardware 0..1 MS and firmware 0..1 MS and software 0..1 MS
* version[hardware].type = $mdc#531974 "MDC_ID_PROD_SPEC_HW"
* version[hardware] ^short = "Hardware version"
* version[firmware].type = $mdc#531976 "MDC_ID_PROD_SPEC_FW"
* version[firmware] ^short = "Firmware version"
* version[software].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[software] ^short = "Software version"


Profile: GroveGatewayDevice
Parent: Device
Id: grove-gateway-device
Title: "Grove Gateway Device"
Description: """
The application and operating-system environment that saved a mobile health observation.
It records the application name, platform application identifier and version, hardware
model, and operating-system version. The standard `observation-gatewayDevice` extension
links it from the Observation.

When a phone both records and saves a value, the Observation may reference the same
physical hardware in two roles: a sensor Device for acquisition and a gateway Device
for the application environment.
"""
* deviceName MS
* deviceName ^slicing.discriminator.type = #value
* deviceName ^slicing.discriminator.path = "type"
* deviceName ^slicing.rules = #open
* deviceName contains userFriendlyName 0..1 MS
* deviceName[userFriendlyName].type = #user-friendly-name
* deviceName[userFriendlyName] ^short = "The saving app's user-facing name"
* modelNumber MS
* modelNumber ^short = "Product type of the hardware the app ran on (e.g. Watch7,1)"
* identifier MS
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains appleBundleId 0..1 MS and androidApplicationId 0..1 MS
* identifier[appleBundleId].system = $sidAppleBundleId
* identifier[appleBundleId] ^short = "The app's bundle identifier"
* identifier[androidApplicationId].system = $sidAndroidApplicationId
* identifier[androidApplicationId] ^short = "The app's application id"
* version MS
* version ^slicing.discriminator.type = #pattern
* version ^slicing.discriminator.path = "type"
* version ^slicing.rules = #open
* version contains application 0..1 MS and operatingSystem 0..1 MS
* version[application].type = $mdc#531975 "MDC_ID_PROD_SPEC_SW"
* version[application] ^short = "The saving app's version"
* version[operatingSystem].type = GroveDeviceVersionType#operating-system "Operating System Version"
* version[operatingSystem] ^short = "The operating-system version (no MDC code exists for this)"


Profile: GroveMobileSensorObservation
Parent: Observation
Id: grove-mobile-sensor-observation
Title: "Grove Mobile Sensor Observation"
Description: """
An Observation captured through a mobile health platform. The profile carries the
source-record identity in `identifier`, full-precision timing in `effective[x]`, the
recording hardware in `device`, and the saving application in the standard
`observation-gatewayDevice` extension. Grove extensions record the capture method and
typed source metadata that has no standard FHIR representation.

`subject` identifies the person described by the sample and is supplied by the
converting application. `meta.source` identifies the acquisition channel. When the
recording device type is known, `meta.tag` carries a searchable copy of `Device.type`.
See [Mobile Observations](mobile.html) for the core mapping and examples.
"""
* meta.source MS
* meta.source ^short = "URI identifying the acquisition channel"
* meta.tag ^slicing.discriminator.type = #value
* meta.tag ^slicing.discriminator.path = "system"
* meta.tag ^slicing.rules = #open
* meta.tag contains deviceType 0..1 MS
* meta.tag[deviceType].system = "https://grovealliance.org/fhir/core/CodeSystem/grove-device-type"
* meta.tag[deviceType].code 1..1
* meta.tag[deviceType] from GroveDeviceTypeVS (required)
* meta.tag[deviceType] ^short = "Form factor of the recording device, copied from the contained `Device.type`"
* identifier 1..* MS
* identifier ^short = "Source-platform record identifier (see Mobile Observations)"
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    healthKitSampleId 0..1 MS and
    healthConnectRecordId 0..1 MS and
    sensorKitSampleId 0..1 MS
* identifier[healthKitSampleId].system = $sidHealthKitSampleId
* identifier[healthKitSampleId].value 1..1
* identifier[healthKitSampleId] ^short = "HKObject.uuid"
* identifier[healthConnectRecordId].system = $sidHealthConnectRecordId
* identifier[healthConnectRecordId].value 1..1
* identifier[healthConnectRecordId] ^short = "Health Connect Metadata.id"
* identifier[sensorKitSampleId].system = $sidSensorKitSampleId
* identifier[sensorKitSampleId].value 1..1
* identifier[sensorKitSampleId] ^short = "Deterministic content hash of a SensorKit sample (SensorKit assigns no record ids)"
* status MS
* code MS
* subject 1..1 MS
* category MS
* effective[x] MS
* effective[x] only dateTime or Period or instant
* effective[x] ^short = "Full platform precision: preserve fractional seconds; carry the named zone via the timezone extension when known"
* device MS
* device only Reference(GroveSensorDevice)
* device ^short = "The recording device (usually contained)"
* extension contains
    $gatewayDevice named gatewayDevice 0..1 MS and
    GroveRecordingMethod named recordingMethod 0..1 MS and
    GrovePlatformMetadata named platformMetadata 0..* and
    GroveStudyRevision named studyRevision 0..1 MS
* extension[gatewayDevice].valueReference only Reference(GroveGatewayDevice)
* extension[gatewayDevice] ^short = "The app + OS that saved the record"
* extension[recordingMethod] ^short = "Sensed, actively measured, or manually entered"
* extension[platformMetadata] ^short = "Typed source metadata with no standard FHIR representation"
* extension[studyRevision] ^short = "Deployment study-definition revision in force when this resource was produced"
