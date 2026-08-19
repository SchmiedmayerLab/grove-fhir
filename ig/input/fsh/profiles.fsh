//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Profile: GroveSensorDevice
Parent: Device
Id: grove-sensor-device
Title: "Grove Sensor Device"
Description: """
The device that recorded a HealthKit observation. Grove Swift usually includes this
resource as a contained `Device` referenced by `Observation.device` because HealthKit
does not always provide a stable standalone device identifier.
"""
* ^experimental = true
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
The app and operating-system environment that saved a HealthKit observation. It is
linked from the Observation with the standard `observation-gatewayDevice` extension.
"""
* ^experimental = true
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
* identifier contains appleBundleId 0..1 MS
* identifier[appleBundleId].system = $sidAppleBundleId
* identifier[appleBundleId] ^short = "The app's bundle identifier"
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
A FHIR R4 Observation produced from a HealthKit sample. It carries the HealthKit record
identifier, subject, measurement time, recording device, saving application, capture
method, and typed source metadata used by the current Grove Swift conversion.
"""
* ^experimental = true
* meta.source MS
* meta.source ^short = "Acquisition channel URI; Grove Swift uses https://grovealliance.org/fhir/source/healthkit"
* meta.tag ^slicing.discriminator.type = #value
* meta.tag ^slicing.discriminator.path = "system"
* meta.tag ^slicing.rules = #open
* meta.tag contains deviceType 0..1 MS
* meta.tag[deviceType].system = "https://grovealliance.org/fhir/core/CodeSystem/grove-device-type"
* meta.tag[deviceType].code 1..1
* meta.tag[deviceType] from GroveDeviceTypeVS (required)
* meta.tag[deviceType] ^short = "Form factor of the recording device, copied from the contained `Device.type`"
* identifier 1..* MS
* identifier ^short = "HealthKit sample identifier"
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains healthKitSampleId 0..1 MS
* identifier[healthKitSampleId].system = $sidHealthKitSampleId
* identifier[healthKitSampleId].value 1..1
* identifier[healthKitSampleId] ^short = "HKObject.uuid"
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
    GrovePlatformMetadata named platformMetadata 0..*
* extension[gatewayDevice].valueReference only Reference(GroveGatewayDevice)
* extension[gatewayDevice] ^short = "The app + OS that saved the record"
* extension[recordingMethod] ^short = "Sensed, actively measured, or manually entered"
* extension[platformMetadata] ^short = "Typed HealthKit metadata without an explicit mapping"
