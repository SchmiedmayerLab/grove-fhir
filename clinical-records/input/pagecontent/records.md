<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

### One record, one document, any number of files

A provider-issued clinical record becomes one Grove record: one conversion Provenance, one Grove Clinical Record Document, and one Grove Clinical Record Attachment for every file that accompanies the record.
The Provenance targets the document and every attachment, so the record version covers all of them, and a changed or added file is a new version of the same source record.

The document carries the provider's payload exactly as delivered and is the same whether or not the record has files.
Grove never converts, re-encodes, or asserts conformance over another issuer's record or file.

### Declaring the FHIR release

A provider-issued FHIR resource uses the `provider-issued-fhir-json` format whatever its FHIR release.
The producer takes the release from source metadata and writes it into `DocumentReference.content.attachment.contentType` as the standard `fhirVersion` media-type parameter:

| Source FHIR release | `content.attachment.contentType` |
|---|---|
| DSTU2 | `application/fhir+json; fhirVersion=1.0` |
| STU3 | `application/fhir+json; fhirVersion=3.0` |
| R4 | `application/fhir+json; fhirVersion=4.0` |
| R5 | `application/fhir+json; fhirVersion=5.0` |

Any other explicitly identified release uses the same form.
A producer must supply the parameter and must not infer the release from the JSON; a media type without it is not admitted.
The outer Grove exchange Bundle and this document remain FHIR R4.
An adapter may admit fewer releases than this guide, as the HealthKit adapter admits only the DSTU2 and R4 releases HealthKit reports.

A CDA document uses the `cda-document` format, which currently admits HL7 CDA Release 2 XML with media type `application/hl7-cda+xml`.

### Linking a file to its record

Each attachment points to its record's document, never the other way round:

- `DocumentReference.relatesTo` occurs once, with `code` = `appends` and a literal `target` reference to the record's document in the same exchange Bundle.
- The attachment carries the document's source-record identifier, so both are outputs of one record. Its own source-output identifier is distinct.
- Its type coding, subject, date, author, and study `context.related` equal the document's; where the document states no author or no study, neither does the attachment.

A receiver finds a record's files by following `relatesTo` from each attachment in the Bundle.
An attachment that points to a document of another record, or to anything but a clinical record document of its Bundle, is nonconformant.

### Carrying the file

An attachment uses the Mobile `source-file` format.
Its `contentType` is the media type the source declares, in lowercase, or `application/octet-stream` when the source declares none.
The bytes travel inline in `Attachment.data`, or by an immutable, version-specific `Attachment.url` that may be relative to the transport unit carrying the Bundle, such as `documents/<sha256>.pdf` inside the same upload archive.
`size` and `hash` cover the exact file bytes either way.
Grove never skips a file because of its size.
