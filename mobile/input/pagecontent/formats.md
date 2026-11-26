<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit catalog/format-registry.json and run
`python3 Scripts/render-format-registry.py`.
-->

Every Grove payload DocumentReference content entry declares exactly one payload format from this closed registry in `content.format`, with system `https://grovealliance.org/fhir/mobile/CodeSystem/grove-payload-format` and no `Coding.version`. An unregistered payload format is nonconformant.
Mobile publishes the one format CodeSystem and its ValueSet. Each format belongs to the guide that owns its definition; a document profile admits only the formats its guide owns, or fixes the one format it carries.
The complete machine-readable contract is published in [`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json).

### Carrying the bytes

These rules apply to every payload content entry, whatever its format and whichever guide's profile carries it.

- **Inline or by URL.** `Attachment` carries the exact payload bytes in exactly one of `data` (base64) or `url`. A URL names an immutable, version-specific location; it may be relative to the transport unit that carries the Bundle, such as an entry of the same upload archive. A receiver resolves a URL through its deployment, never through Grove.
- **Media type.** `Attachment.contentType` is always present and is the media type the format defines: one of its enumerated values, or a value matching its pattern.
- **Size and hash.** `Attachment.size` is the exact byte count and `Attachment.hash` the base64 SHA-1 digest of the exact payload bytes, inline or by URL alike. A validator checks both against embedded bytes.
- **No release coupling.** `content.format.version` is absent: the stable CodeSystem and code identify the wire contract, not an IG release.

### Registered formats

| Code | Title | Owner | Media type |
|---|---|---|---|
| `heart-rate-samples` | Heart Rate Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `triaxial-acceleration-samples` | Triaxial Acceleration Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `ambient-light-samples` | Ambient Light Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `ambient-pressure-samples` | Ambient Pressure Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `pedometer-samples` | Pedometer Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `wrist-temperature-samples` | Wrist Temperature Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `triaxial-rotation-samples` | Triaxial Rotation Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `odometer-samples` | Odometer Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `beat-interval-series` | Beat Interval Series | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `location-track-samples` | Location Track Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `text/csv` |
| `sensor-sample-collection-bundle` | Sensor Sample Collection Bundle | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `application/fhir+json` |
| `provider-issued-fhir-json` | Provider-Issued FHIR JSON | [Grove FHIR Clinical Records](https://grovealliance.org/fhir/clinical-records/formats.html) | `application/fhir+json` with the FHIR release the producer declares, matching `^application/fhir\+json; fhirVersion=[0-9]+\.[0-9]+$` |
| `cda-document` | CDA Document | [Grove FHIR Clinical Records](https://grovealliance.org/fhir/clinical-records/formats.html) | `application/hl7-cda+xml` |
| `source-file` | Source File | Grove FHIR Mobile (below) | the one the source declares, matching `^[a-z0-9][a-z0-9!#$&^_.+-]{0,126}/[a-z0-9][a-z0-9!#$&^_.+-]{0,126}(; [a-z0-9][a-z0-9!#$&^_.+-]{0,126}=([^\s";]+|"[^"]*"))*$`; `application/octet-stream` when it declares none |
| `native-recording-json` | Native Recording JSON | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `application/json` |
| `provider-response-json` | Provider Response JSON | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `application/json` |
| `photoplethysmogram-samples` | Photoplethysmogram Samples | [Grove FHIR Sensor and Waveform](https://grovealliance.org/fhir/sensor/formats.html) | `application/octet-stream` |

The formats Mobile owns are defined below; every other format is defined on its owner's formats page.

### `source-file` — Source File

Media type: the one the source declares, matching `^[a-z0-9][a-z0-9!#$&^_.+-]{0,126}/[a-z0-9][a-z0-9!#$&^_.+-]{0,126}(; [a-z0-9][a-z0-9!#$&^_.+-]{0,126}=([^\s";]+|"[^"]*"))*$`; `application/octet-stream` when it declares none.
Attachment.contentType is the file's IANA media type as the source platform declares it, with the type, subtype, and parameter names in lowercase, or `application/octet-stream` when the source declares none. The registry enumerates no media type for this format: any value that matches its contentTypePattern is admitted, and a receiver must not reject a file for an unfamiliar media type.
Grove format validation checks only the size and SHA-1 hash of embedded bytes, as for every recording attachment; it never opens or interprets the file. A URL payload is resolved by the deployment, not by Grove.
One document carries exactly one file. Only a profile that fixes this format carries it, such as the Clinical Records attachment; no document profile admits it through a value-set binding.
One file exactly as the source platform stored it, in any format. Grove never opens, rewrites, reserializes, or interprets the file.

### Reading Bundles that use the retired format codes

Bundles written before the payload formats moved to Mobile declare DocumentReference.content.format from the retired Sensor CodeSystem named below. A receiver that keeps or reads such a Bundle maps each coding through the code map to the Mobile coding of the same meaning: the system always changes, and five codes also change their spelling. The mapped coding means exactly what the old one meant, including its media types. No producer of a later release writes the old system or the old codes, and a validator of a later release rejects them. A receiver never recomputes a record version or a source-artifact identity from a mapped coding: a stored Bundle keeps the identities it was written with, and a producer that converts the same source record again under a later release emits a new record version of the same source record, not a retry, whose outputs carry new source-artifact identities where the format code changed spelling.

Retired system: `https://grovealliance.org/fhir/sensor/CodeSystem/grove-recording-format`. Current system: `https://grovealliance.org/fhir/mobile/CodeSystem/grove-payload-format`.

| Retired code | Current code |
|---|---|
| `heart-rate-samples` | `heart-rate-samples` |
| `triaxial-acceleration-samples` | `triaxial-acceleration-samples` |
| `ambient-light-samples` | `ambient-light-samples` |
| `ambient-pressure-samples` | `ambient-pressure-samples` |
| `pedometer-samples` | `pedometer-samples` |
| `wrist-temperature-samples` | `wrist-temperature-samples` |
| `triaxial-rotation-samples` | `triaxial-rotation-samples` |
| `odometer-samples` | `odometer-samples` |
| `beat-interval-series` | `beat-interval-series` |
| `location-track-samples` | `location-track-samples` |
| `fhir-collection-bundle` | `sensor-sample-collection-bundle` |
| `fhir-resource` | `provider-issued-fhir-json` |
| `clinical-document` | `cda-document` |
| `source-file` | `source-file` |
| `native-recording` | `native-recording-json` |
| `provider-recording` | `provider-response-json` |
| `photoplethysmogram-samples` | `photoplethysmogram-samples` |
