//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Extensions the Grove framework writes into Observations (and other resources)
// created from Apple HealthKit samples.
//
// Sub-extension URLs are ABSOLUTE (e.g. .../sourceDevice/name), matching what
// GroveHealthKitFHIR's FHIRExtensionBuilder actually emits: each field URL is the
// parent canonical with the field name appended as a path component.

Extension: GroveSourceDevice
Id: sourceDevice
Title: "Source Device"
Description: """
Encoded `HKDevice` of the HealthKit object from which a FHIR Observation was created.
Each populated field of the device is written as a sub-extension whose URL is this
extension's canonical URL with the field name appended, carrying the field's string value.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "https://bdh.stanford.edu/fhir/defs/sourceDevice"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] 0..0
* extension contains
    name 0..1 and
    manufacturer 0..1 and
    model 0..1 and
    hardwareVersion 0..1 and
    firmwareVersion 0..1 and
    softwareVersion 0..1 and
    localIdentifier 0..1 and
    udiDeviceIdentifier 0..1
* extension[name].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/name"
* extension[name].value[x] only string
* extension[name] ^short = "HKDevice.name"
* extension[manufacturer].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/manufacturer"
* extension[manufacturer].value[x] only string
* extension[manufacturer] ^short = "HKDevice.manufacturer"
* extension[model].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/model"
* extension[model].value[x] only string
* extension[model] ^short = "HKDevice.model"
* extension[hardwareVersion].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/hardwareVersion"
* extension[hardwareVersion].value[x] only string
* extension[hardwareVersion] ^short = "HKDevice.hardwareVersion"
* extension[firmwareVersion].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/firmwareVersion"
* extension[firmwareVersion].value[x] only string
* extension[firmwareVersion] ^short = "HKDevice.firmwareVersion"
* extension[softwareVersion].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/softwareVersion"
* extension[softwareVersion].value[x] only string
* extension[softwareVersion] ^short = "HKDevice.softwareVersion"
* extension[localIdentifier].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/localIdentifier"
* extension[localIdentifier].value[x] only string
* extension[localIdentifier] ^short = "HKDevice.localIdentifier"
* extension[udiDeviceIdentifier].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/udiDeviceIdentifier"
* extension[udiDeviceIdentifier].value[x] only string
* extension[udiDeviceIdentifier] ^short = "HKDevice.udiDeviceIdentifier (FDA UDI)"


Extension: GroveSourceRevision
Id: sourceRevision
Title: "Source Revision"
Description: """
Encoded `HKSourceRevision` of the HealthKit object from which a FHIR Observation was
created: the source (app or device) that saved the sample, its version, the product
type, and the operating-system version. Sub-extension URLs are this extension's
canonical URL with the field name appended.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "https://bdh.stanford.edu/fhir/defs/sourceRevision"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] 0..0
* extension contains
    source 1..1 and
    version 0..1 and
    productType 0..1 and
    OSVersion 0..1
* extension[source].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source"
* extension[source].value[x] 0..0
* extension[source] ^short = "HKSourceRevision.source"
* extension[source].extension contains sourceName 1..1 and sourceBundleIdentifier 1..1
* extension[source].extension[sourceName].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/name"
* extension[source].extension[sourceName].value[x] only string
* extension[source].extension[sourceName] ^short = "HKSource.name"
* extension[source].extension[sourceBundleIdentifier].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/bundleIdentifier"
* extension[source].extension[sourceBundleIdentifier].value[x] only string
* extension[source].extension[sourceBundleIdentifier] ^short = "HKSource.bundleIdentifier"
* extension[version].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/version"
* extension[version].value[x] only string
* extension[version] ^short = "HKSourceRevision.version"
* extension[productType].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/productType"
* extension[productType].value[x] only string
* extension[productType] ^short = "HKSourceRevision.productType"
* extension[OSVersion].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/OSVersion"
* extension[OSVersion].value[x] only string
* extension[OSVersion] ^short = "HKSourceRevision.operatingSystemVersion as major.minor.patch"


Extension: GroveHealthKitMetadata
Id: metadata
Title: "HealthKit Metadata"
Description: """
Encoded metadata dictionary of the HealthKit object from which a FHIR Observation was
created. Each metadata entry is written as a sub-extension whose URL is this extension's
canonical URL with the HealthKit metadata key appended (e.g. `.../metadata/HKMetadataKeyHeartRateSensorLocation`).
The set of keys is open: HealthKit metadata accepts arbitrary keys. Values are written as
the FHIR type matching the entry's runtime type: string, boolean, decimal, dateTime,
Coding (for HealthKit enum-valued keys), or Quantity (for HKQuantity-valued keys).
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "https://bdh.stanford.edu/fhir/defs/metadata"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] 0..0
* extension 1..*
* extension ^short = "One sub-extension per HealthKit metadata entry"
* extension.value[x] 1..1
* extension.value[x] only string or boolean or decimal or dateTime or Coding or Quantity


Extension: GroveAbsoluteTimeRangeStart
Id: absoluteTimeRangeStart
Title: "Absolute Time Range Start"
Description: """
The absolute start timestamp of the Observation's effective period, as a decimal number
of seconds since the Unix epoch (1970-01-01T00:00:00Z), including fractional seconds.
Written in addition to `Observation.effective[x]`, which loses sub-second precision and
time-zone-independent ordering when serialized as a dateTime.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "https://bdh.stanford.edu/fhir/defs/absoluteTimeRangeStart"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only decimal
* valueDecimal 1..1
* valueDecimal ^short = "Seconds since the Unix epoch"


Extension: GroveAbsoluteTimeRangeEnd
Id: absoluteTimeRangeEnd
Title: "Absolute Time Range End"
Description: """
The absolute end timestamp of the Observation's effective period, as a decimal number
of seconds since the Unix epoch (1970-01-01T00:00:00Z), including fractional seconds.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "https://bdh.stanford.edu/fhir/defs/absoluteTimeRangeEnd"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only decimal
* valueDecimal 1..1
* valueDecimal ^short = "Seconds since the Unix epoch"


Extension: GroveHealthKitSampleId
Id: healthKitSampleId
Title: "HealthKit Sample Identifier"
Description: """
The UUID of the HealthKit sample (`HKObject.uuid`) from which a FHIR resource was
created. Written on every resource Grove derives from a HealthKit sample — including
DSTU2 clinical health records, whose wire format uses this same URL — enabling
round-trip identification and deduplication against the originating HealthKit store.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "https://bdh.stanford.edu/fhir/defs/HealthKitSampleID"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "DomainResource"
* value[x] only id
* valueId 1..1
* valueId ^short = "HKObject.uuid as its canonical UUID string"
