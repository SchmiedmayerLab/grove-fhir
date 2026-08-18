//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Standalone definitions for the sub-extensions of the HealthKit provenance extensions.
//
// Grove writes sub-extension URLs as ABSOLUTE URLs (parent canonical + field name).
// In FHIR semantics an absolutely-URL'd nested extension is an independent extension,
// so each one needs its own StructureDefinition for instances to validate. Their URLs
// deliberately do not follow the <canonical>/StructureDefinition/<id> pattern; they are
// declared as special-url parameters in sushi-config.yaml.

// ---- sourceDevice children ----------------------------------------------------------

RuleSet: SourceDeviceChild(field)
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice/{field}"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/sourceDevice"
* value[x] only string
* valueString 1..1

Extension: GroveSourceDeviceName
Id: sourceDevice-name
Title: "Source Device: Name"
Description: "`HKDevice.name` — the name of the device that recorded the sample."
* insert SourceDeviceChild(name)

Extension: GroveSourceDeviceManufacturer
Id: sourceDevice-manufacturer
Title: "Source Device: Manufacturer"
Description: "`HKDevice.manufacturer` — the manufacturer of the device."
* insert SourceDeviceChild(manufacturer)

Extension: GroveSourceDeviceModel
Id: sourceDevice-model
Title: "Source Device: Model"
Description: "`HKDevice.model` — the model of the device."
* insert SourceDeviceChild(model)

Extension: GroveSourceDeviceHardwareVersion
Id: sourceDevice-hardwareVersion
Title: "Source Device: Hardware Version"
Description: "`HKDevice.hardwareVersion` — the hardware revision of the device."
* insert SourceDeviceChild(hardwareVersion)

Extension: GroveSourceDeviceFirmwareVersion
Id: sourceDevice-firmwareVersion
Title: "Source Device: Firmware Version"
Description: "`HKDevice.firmwareVersion` — the firmware revision of the device."
* insert SourceDeviceChild(firmwareVersion)

Extension: GroveSourceDeviceSoftwareVersion
Id: sourceDevice-softwareVersion
Title: "Source Device: Software Version"
Description: "`HKDevice.softwareVersion` — the software revision of the device."
* insert SourceDeviceChild(softwareVersion)

Extension: GroveSourceDeviceLocalIdentifier
Id: sourceDevice-localIdentifier
Title: "Source Device: Local Identifier"
Description: "`HKDevice.localIdentifier` — the device's identifier local to the recording hardware."
* insert SourceDeviceChild(localIdentifier)

Extension: GroveSourceDeviceUdiDeviceIdentifier
Id: sourceDevice-udiDeviceIdentifier
Title: "Source Device: UDI Device Identifier"
Description: "`HKDevice.udiDeviceIdentifier` — the FDA Unique Device Identifier's device identifier portion."
* insert SourceDeviceChild(udiDeviceIdentifier)

// ---- sourceRevision children --------------------------------------------------------

Extension: GroveSourceRevisionSource
Id: sourceRevision-source
Title: "Source Revision: Source"
Description: "`HKSourceRevision.source` — the app or device that saved the sample, as its name and bundle identifier."
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision"
* value[x] 0..0
* extension contains sourceName 1..1 and sourceBundleIdentifier 1..1
* extension[sourceName].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/name"
* extension[sourceName].value[x] only string
* extension[sourceName] ^short = "HKSource.name"
* extension[sourceBundleIdentifier].url ^fixedUri = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/bundleIdentifier"
* extension[sourceBundleIdentifier].value[x] only string
* extension[sourceBundleIdentifier] ^short = "HKSource.bundleIdentifier"

Extension: GroveSourceRevisionSourceName
Id: sourceRevision-source-name
Title: "Source Revision: Source Name"
Description: "`HKSource.name` — the name of the app or device that saved the sample."
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/name"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source"
* value[x] only string
* valueString 1..1

Extension: GroveSourceRevisionSourceBundleIdentifier
Id: sourceRevision-source-bundleIdentifier
Title: "Source Revision: Source Bundle Identifier"
Description: "`HKSource.bundleIdentifier` — the bundle identifier of the app that saved the sample."
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source/bundleIdentifier"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/source"
* value[x] only string
* valueString 1..1

RuleSet: SourceRevisionChild(field)
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision/{field}"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/sourceRevision"
* value[x] only string
* valueString 1..1

Extension: GroveSourceRevisionVersion
Id: sourceRevision-version
Title: "Source Revision: Version"
Description: "`HKSourceRevision.version` — the version of the app that saved the sample."
* insert SourceRevisionChild(version)

Extension: GroveSourceRevisionProductType
Id: sourceRevision-productType
Title: "Source Revision: Product Type"
Description: "`HKSourceRevision.productType` — the product type of the device (e.g. `Watch7,1`)."
* insert SourceRevisionChild(productType)

Extension: GroveSourceRevisionOSVersion
Id: sourceRevision-OSVersion
Title: "Source Revision: OS Version"
Description: "`HKSourceRevision.operatingSystemVersion` rendered as `major.minor.patch`."
* insert SourceRevisionChild(OSVersion)

// ---- metadata: definitions for commonly written keys --------------------------------
//
// The metadata extension's key set is open — HealthKit accepts arbitrary metadata keys,
// and Grove appends whatever key it finds to the metadata canonical. Only commonly
// written keys are defined here; instances carrying other keys remain readable but
// their sub-extension URLs will not resolve to a definition.

Extension: GroveMetadataWasUserEntered
Id: metadata-HKWasUserEntered
Title: "HealthKit Metadata: Was User Entered"
Description: "The `HKWasUserEntered` metadata entry: whether the sample was entered manually by the user rather than recorded by a sensor."
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/metadata/HKWasUserEntered"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/metadata"
* value[x] only boolean
* valueBoolean 1..1

Extension: GroveMetadataHeartRateMotionContext
Id: metadata-HKMetadataKeyHeartRateMotionContext
Title: "HealthKit Metadata: Heart Rate Motion Context"
Description: """
The `HKMetadataKeyHeartRateMotionContext` metadata entry: the user's activity level when
the heart-rate sample was recorded, as a Coding whose system is the Apple documentation
URL of `HKHeartRateMotionContext` and whose code is the enum case's raw value.
"""
* ^url = "https://grovealliance.org/fhir/core/StructureDefinition/metadata/HKMetadataKeyHeartRateMotionContext"
* ^context[+].type = #extension
* ^context[=].expression = "https://grovealliance.org/fhir/core/StructureDefinition/metadata"
* value[x] only Coding
* valueCoding 1..1
