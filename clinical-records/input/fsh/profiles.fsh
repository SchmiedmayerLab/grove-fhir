//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Invariant: clinical-record-payload-1
Description: "A clinical payload attachment carries its bytes in exactly one of embedded data or an immutable, version-specific URL, as the Mobile payload rules require."
Expression: "data.exists() xor url.exists()"
Severity: #error

Invariant: clinical-record-opaque-identifier-value-1
Description: "A clinical source, output, artifact, or writer identifier is a canonical deployment-scoped Grove v0 HMAC value."
Expression: "$this.matches('^v0:[A-Za-z0-9._-]+:[1-9][0-9]*:[A-Za-z0-9_-]{43}$')"
Severity: #error

Invariant: clinical-record-content-type-1
Description: "A provider-issued FHIR JSON payload declares its FHIR release in the media type's fhirVersion parameter, as major.minor; a CDA document is CDA R2 XML."
Expression: "content.all((format.code = 'provider-issued-fhir-json' implies attachment.contentType.matches('^application/fhir[+]json; fhirVersion=[0-9]+[.][0-9]+$')) and (format.code = 'cda-document' implies attachment.contentType = 'application/hl7-cda+xml'))"
Severity: #error

RuleSet: ClinicalRecordIdentifier(slice)
* identifier[{slice}].system 1..1 MS
* identifier[{slice}].value 1..1 MS
* identifier[{slice}].value obeys clinical-record-opaque-identifier-value-1

Profile: GroveClinicalRecordDocument
Parent: DocumentReference
Id: grove-clinical-record-document
Title: "Grove Clinical Record Document"
Description: "A pass-through envelope for one provider-issued clinical record: one FHIR resource in the FHIR release its producer declares, or one CDA R2 document. The payload is byte-preserved exactly as its source delivered it; Grove asserts identity and provenance over this R4 envelope, never conformance over the issuer's record. Files that accompany the record travel as Grove Clinical Record Attachments that append to this document; the document carries no link to them and is the same whether or not the record has attachments."
* obeys clinical-record-content-type-1
* identifier 3..* MS
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #open
* identifier contains sourceRecord 1..1 MS and sourceOutput 1..1 MS and sourceArtifact 1..1 MS and writerRecord 0..1 MS
* identifier[sourceRecord].type = $groveIdentifierRole#source-record
* insert ClinicalRecordIdentifier(sourceRecord)
* identifier[sourceOutput].type = $groveIdentifierRole#source-output
* insert ClinicalRecordIdentifier(sourceOutput)
* identifier[sourceArtifact].type = $groveIdentifierRole#source-artifact
* insert ClinicalRecordIdentifier(sourceArtifact)
* identifier[writerRecord].type = $groveIdentifierRole#writer-record
* insert ClinicalRecordIdentifier(writerRecord)
* status MS
* type 1..1 MS
* subject 1..1 MS
* subject only Reference(Patient)
* date 1..1 MS
* content 1..1 MS
* content.format 1..1 MS
* content.format from GroveClinicalRecordFormatVS (required)
// The stable CodeSystem and code identify the registered format. IG release versions do not
// travel in payload Coding values.
* content.format.version 0..0
* content.attachment obeys clinical-record-payload-1
* content.attachment.contentType 1..1 MS
* content.attachment.contentType ^short = "The payload's media type; for FHIR JSON, with the declared release as fhirVersion"
* content.attachment.size 1..1 MS
* content.attachment.hash 1..1 MS
* content.attachment.title 0..1 MS
* context.related MS

Profile: GroveClinicalRecordAttachment
Parent: DocumentReference
Id: grove-clinical-record-attachment
Title: "Grove Clinical Record Attachment"
Description: "One file that accompanies a provider-issued clinical record, such as a clinical note's PDF, carried exactly as its source stored it. It is an output of the clinical record's record beside that record's Grove Clinical Record Document, and it appends to the document through one relatesTo: code appends and one literal reference to the document in the same exchange Bundle. Its source-record identifier, type coding, subject, date, author, and study context.related equal those of that document, and where the document states no author or no study, neither does the attachment. The file's media type is whatever its source declares."
* identifier 3..3 MS
* identifier ^slicing.discriminator.type = #pattern
* identifier ^slicing.discriminator.path = "type"
* identifier ^slicing.rules = #closed
* identifier contains sourceRecord 1..1 MS and sourceOutput 1..1 MS and sourceArtifact 1..1 MS
* identifier[sourceRecord].type = $groveIdentifierRole#source-record
* insert ClinicalRecordIdentifier(sourceRecord)
* identifier[sourceOutput].type = $groveIdentifierRole#source-output
* insert ClinicalRecordIdentifier(sourceOutput)
* identifier[sourceArtifact].type = $groveIdentifierRole#source-artifact
* insert ClinicalRecordIdentifier(sourceArtifact)
* status = #current (exactly)
* type 1..1 MS
* subject 1..1 MS
* subject only Reference(Patient)
* date 1..1 MS
* relatesTo 1..1 MS
* relatesTo ^short = "The clinical record's document this file appends to"
* relatesTo.code = #appends (exactly)
* relatesTo.target only Reference(GroveClinicalRecordDocument)
* relatesTo.target.reference 1..1 MS
* relatesTo.target.identifier 0..0
* content 1..1 MS
* content.format 1..1 MS
* content.format = $payloadFormat#source-file
// The stable CodeSystem and code identify the registered format. IG release versions do not
// travel in payload Coding values.
* content.format.version 0..0
* content.attachment obeys clinical-record-payload-1
* content.attachment.contentType 1..1 MS
* content.attachment.url ^short = "Immutable, version-specific location of the file; may be relative to the transport unit that carries the Bundle"
* content.attachment.size 1..1 MS
* content.attachment.hash 1..1 MS
* content.attachment.title 0..1 MS
* content.attachment.title ^short = "The file's name as its source states it"
* content.attachment.creation 0..1 MS
* content.attachment.creation ^short = "When the source created the file"
* context.related MS
