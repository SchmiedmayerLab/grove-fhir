<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit catalog/format-registry.json and run
`python3 Scripts/render-format-registry.py`.
-->

Every Grove Clinical Record Document content entry declares exactly one payload format this guide owns in `content.format`; a Clinical Record Attachment carries the Mobile `source-file` format instead. Grove byte-preserves every clinical payload and never asserts conformance over another issuer's record.
The formats are codes of the Mobile [payload format registry](https://grovealliance.org/fhir/mobile/formats.html), which also states the rules for carrying the bytes inline or by URL, their media type, size, and hash.
The complete machine-readable contract is published in [`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json).

### `provider-issued-fhir-json` — Provider-Issued FHIR JSON

Media type: `application/fhir+json` with the FHIR release the producer declares, matching `^application/fhir\+json; fhirVersion=[0-9]+\.[0-9]+$`.
UTF-8.
One complete provider-issued FHIR resource in FHIR JSON representation, of the FHIR release its producer declares, byte-preserved exactly as the source delivered it.
Attachment.contentType is `application/fhir+json` with the standard `fhirVersion` media-type parameter, which names the embedded resource's FHIR release as major.minor: `application/fhir+json; fhirVersion=1.0` for DSTU2, `application/fhir+json; fhirVersion=3.0` for STU3, `application/fhir+json; fhirVersion=4.0` for R4, and so on for any other explicitly identified release. The producer takes the release from source metadata and writes it into the parameter; it must not infer the release from the JSON. A media type without the parameter, or with a malformed one, is not admitted. The outer Grove exchange Bundle and its DocumentReference envelope remain FHIR R4 whatever release the payload declares.
The carrying document records the issuing source, while the attachment media type records the exact FHIR release. Grove never converts, re-encodes, or asserts conformance over another issuer's resource.
One document carries exactly one clinical record's FHIR payload. Grove format validation verifies strict JSON syntax and a `resourceType`-bearing object only; it does not infer the FHIR release or execute base or profile validation over the issuer's resource.

### `cda-document` — CDA Document

Media type: `application/hl7-cda+xml`.
One HL7 Clinical Document Architecture Release 2 (CDA R2) document in its XML representation, media type `application/hl7-cda+xml`, byte-preserved exactly as the source platform delivered it. CDA R2 XML is the one representation this format currently admits. Grove never rewrites, reserializes, or asserts conformance over another issuer's document; the carrying document records the issuer.
