//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// The complete v2 extension set. Deliberately small: everything that has a FHIR-native
// home or a published extension uses it (Observation.device, observation-gatewayDevice,
// targetConstraint, timezone, sdc-questionnaire-keyboard, sdc-questionnaire-itemMedia,
// Resource.identifier). Only concepts with no standard counterpart anywhere are minted
// here; each definition names the standards it aligns with.

Extension: GroveInferredValue
Id: grove-inferred-value
Title: "Inferred Value"
Description: "Marks a coded value that Grove inferred from adjacent platform data rather than receiving directly from the source platform."
* ^context[+].type = #element
* ^context[=].expression = "Coding"
* value[x] only boolean
* valueBoolean 1..1

Extension: GroveRecordingMethod
Id: grove-recording-method
Title: "Recording Method"
Description: """
How the observation was captured: passively sensed, actively measured, or entered by
the user. HealthKit's `HKMetadataKeyWasUserEntered = true` maps to `manual-entry`.
"""
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] only Coding
* valueCoding 1..1
* valueCoding from GroveRecordingMethodVS (required)


Extension: GroveSourceRecordId
Id: grove-source-record-id
Title: "Source Record Identifier"
Description: """
Carries the originating platform record identifier when the resource's own `identifier`
element is reserved for identifiers assigned to the source resource. This applies, for
example, to a clinical document whose business identifier was assigned by the
originating healthcare institution.

Grove Mobile Sensor Observations carry the source record identifier directly in
`Observation.identifier`; see [Source identity](mobile.html#source-identity).
"""
* ^context[+].type = #element
* ^context[=].expression = "DomainResource"
* value[x] only Identifier
* valueIdentifier 1..1
* valueIdentifier ^short = "Platform identifier system and source record value"


Extension: GroveStudyRevision
Id: grove-study-revision
Title: "Study Definition Revision"
Description: """
Identifies the revision of the study definition in effect when the resource was
produced. Use the HL7 `workflow-researchStudy` extension to reference the study and this
extension to record a deployment-defined study revision. The revision is distinct from
the version history of a FHIR `ResearchStudy` resource.
"""
* ^context[+].type = #element
* ^context[=].expression = "DomainResource"
* value[x] only string
* valueString 1..1
* valueString ^short = "Deployment-defined study revision identifier"


Extension: GrovePlatformMetadata
Id: grove-platform-metadata
Title: "Platform Metadata Entry"
Description: """
Represents one typed entry from the source platform's metadata that is not mapped to a
standard FHIR element or published extension. Map time zones to the standard `timezone`
extension, recording method to ``GroveRecordingMethod``, and measurement-specific values
to the appropriate Observation element before using this extension. See
[Recording method and metadata](mobile.html#recording-method-and-metadata).

The key is a Coding whose system identifies the platform key space and whose code is the
raw platform key. The permitted key systems are published by the
[platform terminology guide](https://grovealliance.org/fhir/platforms).
"""
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] 0..0
* extension contains key 1..1 and value 1..1
* extension[key].value[x] only Coding
* extension[key].valueCoding from GrovePlatformMetadataKeyVS (extensible)
* extension[key] ^short = "The platform metadata key (system = platform key space, code = raw key)"
* extension[value].value[x] only string or boolean or decimal or dateTime or Coding or Quantity
* extension[value] ^short = "Metadata value represented with an appropriate FHIR datatype"


Extension: GroveAutocomplete
Id: grove-autocomplete
Title: "Autocomplete"
Description: """
Records the semantic purpose of a text answer for use by platform autofill features.
Values use the WHATWG HTML `autocomplete` detail tokens. Renderers can map supported
values to native autofill APIs.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://bdh.stanford.edu/fhir/StructureDefinition/ios-textcontenttype"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only code
* valueCode 1..1
* valueCode from GroveAutocompleteTokensVS (required)


Extension: GroveAutocapitalize
Id: grove-autocapitalize
Title: "Autocapitalize"
Description: """
Records the autocapitalization behaviour for a text answer. Values use the WHATWG HTML
`autocapitalize` attribute values and can be mapped to supported native text-input
settings.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://bdh.stanford.edu/fhir/StructureDefinition/ios-autocapitalizationType"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] only code
* valueCode 1..1
* valueCode from GroveAutocapitalizeVS (required)


Extension: GroveAnnotateImageRegion
Id: grove-annotate-image-region
Title: "Annotate Image: Region"
Description: """
Defines one selectable region for an annotate-image Questionnaire item. The label names
the region, the optional code can identify an anatomical site, and the color selects the
drawing color. The SDC `sdc-questionnaire-itemMedia` extension carries the base image,
and the answer is an Attachment constrained by the standard `mimeType` and `maxSize`
extensions.
"""
* ^identifier[+].system = "urn:ietf:rfc:3986"
* ^identifier[=].value = "http://spezi.stanford.edu/fhir/CodeSystem/questionnaire-item-control/annotate-image/region"
* ^identifier[=].use = #old
* ^context[+].type = #element
* ^context[=].expression = "Questionnaire.item"
* value[x] 0..0
* extension contains label 1..1 and code 0..1 and color 1..1
* extension[label].value[x] only string
* extension[label] ^short = "Region name shown to the user"
* extension[code].value[x] only Coding
* extension[code].valueCoding from $bodySite (preferred)
* extension[code] ^short = "Body-site code, when the region is anatomical"
* extension[color].value[x] only code
* extension[color].value[x] from GroveAnnotateImageColorsVS (required)
* extension[color] ^short = "Pen color for this region"
