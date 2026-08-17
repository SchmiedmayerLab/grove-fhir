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

Extension: GroveRecordingMethod
Id: grove-recording-method
Title: "Recording Method"
Description: """
How the observation was captured: passively sensed, actively measured, or entered by
the user. Aligned with Android Health Connect's recording methods and IEEE 1752.1-2021's
`modality` (sensed vs. self-reported); HealthKit's `HKMetadataKeyWasUserEntered = true`
maps to `manual-entry`. No HL7 code system covers this concept.
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
The identifier of the record in the originating mobile platform's store, for resources
where writing it into the resource's own `identifier` list would misrepresent
source-assigned business identity — chiefly clinical-record payloads passed through
from a platform store (e.g. HealthKit clinical records), whose `identifier` content
belongs to the originating healthcare institution.

Grove-authored Observations do NOT use this extension: they carry the platform record
identifier in `Observation.identifier` with the Grove identifier systems
(see the Identifiers page), per ``GroveMobileSensorObservation``.
"""
* ^context[+].type = #element
* ^context[=].expression = "DomainResource"
* value[x] only Identifier
* valueIdentifier 1..1
* valueIdentifier ^short = "system = a Grove identifier system; value = the platform record id"


Extension: GroveStudyRevision
Id: grove-study-revision
Title: "Study Definition Revision"
Description: """
The revision of the study definition in force when the resource was produced.

The study itself is referenced by the HL7 `workflow-researchStudy` extension. That
extension's value is a `Reference`, whose `display` is plain-text narrative for a reader
— not a machine-readable version — so the revision needs a home of its own. It is not a
FHIR version of the `ResearchStudy` resource either: study bundles are revised
independently of whatever server stores them, so a versioned reference
(`ResearchStudy/x/_history/y`) would assert something untrue.

A deployment that revises its protocol mid-study needs this to tell which definition a
participant was answering.
"""
* ^context[+].type = #element
* ^context[=].expression = "DomainResource"
* value[x] only string
* valueString 1..1
* valueString ^short = "The study-definition revision, as the deployment numbers it"


Extension: GrovePlatformMetadata
Id: grove-platform-metadata
Title: "Platform Metadata Entry"
Description: """
One entry of the originating platform's metadata dictionary that has no better FHIR
home. This is the LAST layer of the metadata policy (see the Metadata Policy page):
time zones go to the standard `timezone` extension, recording modality to
``GroveRecordingMethod``, body/sensor location to `Observation.bodySite`,
device-adjacent values to `Device.property`, measurement-adjacent values to
`Observation.component` — only the residue lands here.

The key is a Coding whose system identifies the platform key space
(`https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-metadata-key` or
`…/health-connect-metadata-key`, both fragment code systems published by the
[platform vocabularies guide](https://grovealliance.org/fhir/platforms) — arbitrary
platform keys are valid codes) and whose code is the raw platform key.
"""
* ^context[+].type = #element
* ^context[=].expression = "Observation"
* value[x] 0..0
* extension contains key 1..1 and value 1..1
* extension[key].value[x] only Coding
* extension[key].valueCoding from GrovePlatformMetadataKeyVS (extensible)
* extension[key] ^short = "The platform metadata key (system = platform key space, code = raw key)"
* extension[value].value[x] only string or boolean or decimal or dateTime or Coding or Quantity
* extension[value] ^short = "The entry's value, typed by its platform runtime type"


Extension: GroveAutocomplete
Id: grove-autocomplete
Title: "Autocomplete"
Description: """
The semantic content type of a text answer, enabling platform autofill. Values are the
WHATWG HTML `autocomplete` detail tokens — the cross-platform vocabulary that maps 1:1
to iOS `UITextContentType`, Android autofill hints, and HTML `autocomplete`. No SDC or
HL7 extension covers autofill semantics (verified against SDC STU4 and the extensions
pack 5.3.0).
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
The autocapitalization behaviour for a text answer. Values are the WHATWG HTML
`autocapitalize` attribute values, 1:1 with iOS `UITextAutocapitalizationType` and
mappable to Android input types. The SDC keyboard extension deliberately excludes
input capabilities; no standard counterpart exists.
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
One selectable region of an annotate-image item: the label the user sees, the pen color
used when annotating that region, and — where the region is anatomical — a body-site
code that makes answers extractable to `Observation.bodySite`. The base image itself is
carried by the SDC `sdc-questionnaire-itemMedia` extension; the answer is an attachment
(the annotated image), constrained via the standard `mimeType`/`maxSize` extensions.
No standard region-legend or body-map questionnaire extension exists.
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
