//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Instance: GroveClinicalRecordsPatientExample
InstanceOf: Patient
Usage: #example
Title: "Grove Clinical Records Example Participant"
Description: "The participant referenced by the clinical record examples."
* identifier.system = "https://study.example.org/fhir/identifiers/participant"
* identifier.value = "portal-participant-001"

Instance: GroveClinicalRecordsImporterExample
InstanceOf: GroveApplicationDevice
Usage: #example
Title: "Grove Clinical Records Example Importer"
Description: "A web importer that received a provider-issued clinical note and its PDF from a patient portal and byte-preserved both. No platform adapter is involved."
* status = #active
* identifier[applicationSnapshot].system = "https://study.example.org/fhir/NamingSystem/grove-device-snapshot-v0/test-key/1"
* identifier[applicationSnapshot].value = "v0:test-key:1:9X0eMtS2ovcmoGrgbDCdSO1PvAoDtLIQ9YeRa-lZVx4"
* deviceName[applicationName].name = "Portal Importer"
* deviceName[applicationName].type = #user-friendly-name

Instance: GroveClinicalNoteRecordDocumentExample
InstanceOf: GroveClinicalRecordDocument
Usage: #example
Title: "Grove Clinical Note Record Pass-Through"
Description: "One provider-issued R4 clinical note, byte-preserved with its declared FHIR release. Its PDF travels beside it as a Grove Clinical Record Attachment; this document and its payload are the same whether or not the record has attachments."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:_hcEGJV15Q_pOgnQva_qLn7onjsqM3_YBbCpOE52eaE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:pKADUrrKywzVTkUyBjqXFclrM4YWez6lSFCQMZqYRHM"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:fT0CaSwLECwfII6cX_LgG2FA8gGU9X2BNRFkw3ZFh9k"
* status = #current
* type = $loinc#34109-9 "Note"
* subject = Reference(GroveClinicalRecordsPatientExample)
* date = "2026-08-20T17:09:01Z"
* content.format = $payloadFormat#provider-issued-fhir-json "Provider-Issued FHIR JSON"
* content.attachment.contentType = #"application/fhir+json; fhirVersion=4.0"
* content.attachment.title = "Provider-issued DocumentReference"
* content.attachment.data = "eyJyZXNvdXJjZVR5cGUiOiJEb2N1bWVudFJlZmVyZW5jZSIsImlkIjoicHJvdmlkZXItbm90ZS03Iiwic3RhdHVzIjoiY3VycmVudCIsInR5cGUiOnsidGV4dCI6IlByb2dyZXNzIG5vdGUifSwic3ViamVjdCI6eyJyZWZlcmVuY2UiOiJQYXRpZW50L3BvcnRhbC1wYXRpZW50LTcifSwiY29udGVudCI6W3siYXR0YWNobWVudCI6eyJjb250ZW50VHlwZSI6ImFwcGxpY2F0aW9uL3BkZiIsInVybCI6IkJpbmFyeS9wcm92aWRlci1ub3RlLTctcGRmIiwidGl0bGUiOiJWaXNpdCBub3RlIn19XX0="
* content.attachment.size = 278
* content.attachment.hash = "9hYGF2CskU4fd9vhihIP8PNaDSk="

Instance: GroveClinicalRecordAttachmentExample
InstanceOf: GroveClinicalRecordAttachment
Usage: #example
Title: "Grove Clinical Record Attachment"
Description: "The PDF that accompanies the clinical note, carried exactly as the portal delivered it and named by its path in the upload archive that also carries the record's Bundle. The directory name is illustrative. It appends to the record's clinical record document, which does not point back to it."
* identifier[sourceRecord].system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* identifier[sourceRecord].value = "v0:test-key:1:_hcEGJV15Q_pOgnQva_qLn7onjsqM3_YBbCpOE52eaE"
* identifier[sourceOutput].system = "https://study.example.org/fhir/NamingSystem/grove-source-output-v0/test-key/1"
* identifier[sourceOutput].value = "v0:test-key:1:UKNWwUuarzRHBX-I70n__ghFxUwE8fKIEHOAPFTTOVU"
* identifier[sourceArtifact].system = "https://study.example.org/fhir/NamingSystem/grove-source-artifact-v0/test-key/1"
* identifier[sourceArtifact].value = "v0:test-key:1:747212hmvziVtxAX5r1M_rx-mHwpfkU_TUtStpsau4U"
* type = $loinc#34109-9 "Note"
* subject = Reference(GroveClinicalRecordsPatientExample)
* date = "2026-08-20T17:09:01Z"
* relatesTo.code = #appends
* relatesTo.target = Reference(GroveClinicalNoteRecordDocumentExample)
* content.format = $payloadFormat#source-file "Source File"
* content.attachment.contentType = #application/pdf
* content.attachment.url = "documents/c4071ece7b3d0e2501f5278299ff8be67aa48f40b4657cd898a99afa57de295e.pdf"
* content.attachment.size = 125
* content.attachment.hash = "TF2ofvSD2nMLKkzbb/w6aZ8CoFY="
* content.attachment.title = "Visit note.pdf"
* content.attachment.creation = "2026-08-20T09:30:00-07:00"

Instance: GroveClinicalNoteRecordProvenanceExample
InstanceOf: GroveMobileConversionProvenance
Usage: #example
Title: "Grove Clinical Note Record Provenance"
Description: "One conversion of a clinical note record with one attachment: the record's single Provenance targets both its clinical record document and its attachment document."
* extension[recordVersion].valueIdentifier.type = $groveIdentifierRole#record-version "Record version"
* extension[recordVersion].valueIdentifier.system = "https://study.example.org/fhir/NamingSystem/grove-record-version-v0/test-key/1"
* extension[recordVersion].valueIdentifier.value = "v0:test-key:1:Hnoh7ZO_ACeibF5mdr0M0p4gPlT8oCL9Py9bSGwaD4Y"
* target[+] = Reference(GroveClinicalNoteRecordDocumentExample)
* target[+] = Reference(GroveClinicalRecordAttachmentExample)
* occurredDateTime = "2026-08-20T17:09:00Z"
* recorded = "2026-08-20T17:09:01Z"
* activity = $recordLifecycleEvent#transform "Transform/Translate Record Lifecycle Event"
* agent[assembler].type = $provenanceParticipantType#assembler "Assembler"
* agent[assembler].who = Reference(GroveClinicalRecordsImporterExample)
* entity.role = #source
* entity.what.identifier.type = $groveIdentifierRole#source-record "Source record"
* entity.what.identifier.system = "https://study.example.org/fhir/NamingSystem/grove-source-record-v0/test-key/1"
* entity.what.identifier.value = "v0:test-key:1:_hcEGJV15Q_pOgnQva_qLn7onjsqM3_YBbCpOE52eaE"
