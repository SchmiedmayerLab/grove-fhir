<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit catalog/format-registry.json and run
`python3 Scripts/render-format-registry.py`.
-->

Every Grove recording DocumentReference content entry declares exactly one payload format from this closed registry in `content.format`.
An unregistered payload format is nonconformant. Each entry defines the payload grammar that a conformant producer validates before emission and identifies any additional producer or receiver responsibilities. For `native-recording`, the carrying source type selects the source category and meaning; this generic format defines no per-stream field schema.
The complete machine-readable contract is published in [`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json).

### `heart-rate-samples` — Heart Rate Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Sample instant. |
| `value` | number | no | `/min` | Heart rate in beats per minute. |
| `confidence` | integer | no | — | CMHighFrequencyHeartRateDataConfidence raw value: 0 low, 1 medium, 2 high, 3 highest. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `triaxial-acceleration-samples` — Triaxial Acceleration Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Sample instant. |
| `identifier` | integer | no | — | The CoreMotion batch identifier within the row's device partition. A batch key is the exact (device, identifier) pair. |
| `x` | number | no | `[g]` | Acceleration along x in G. |
| `y` | number | no | `[g]` | Acceleration along y in G. |
| `z` | number | no | `[g]` | Acceleration along z in G. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `ambient-light-samples` — Ambient Light Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Sample instant. |
| `lux` | number | no | `lx` | Illuminance in lux. |
| `placement` | string | no | — | SRAmbientLightSample.SensorPlacement textual description. |
| `chromaticityX` | number | no | — | CIE 1931 x chromaticity coordinate. |
| `chromaticityY` | number | no | — | CIE 1931 y chromaticity coordinate. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `ambient-pressure-samples` — Ambient Pressure Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Sample instant. |
| `identifier` | integer | no | — | The CoreMotion batch identifier the sample belongs to. |
| `pressure` | number | no | `kPa` | Ambient pressure in kilopascals as provided by CoreMotion. |
| `temperature` | number | no | `Cel` | Sensor temperature in degrees Celsius as provided by CoreMotion. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `pedometer-samples` — Pedometer Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `start` | timestamp | no | — | Interval start. |
| `end` | timestamp | no | — | Interval end. |
| `steps` | integer | no | `{steps}` | Steps taken in the interval. |
| `distance` | number | yes | `m` | Estimated distance in metres; empty when unavailable. |
| `floorsUp` | integer | yes | — | Floors ascended; empty when unavailable. |
| `floorsDown` | integer | yes | — | Floors descended; empty when unavailable. |
| `currentPace` | number | yes | `s/m` | Current pace in seconds per metre; empty when unavailable. |
| `currentCadence` | number | yes | `/s` | Current cadence in steps per second; empty when unavailable. |
| `avgActivePace` | number | yes | `s/m` | Average active pace in seconds per metre; empty when unavailable. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `wrist-temperature-samples` — Wrist Temperature Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Temperature sample instant. |
| `value` | number | no | `Cel` | Wrist temperature converted to degrees Celsius. |
| `errorEstimate` | number | no | `Cel` | Estimated error converted to degrees Celsius. |
| `condition` | string | yes | — | SRWristTemperature.Condition for the sample. The source is an option set, so zero or more conditions apply: the value is the set's members joined with a comma in the declared order offWrist, onCharger, inMotion, and the field is empty when no condition applies. A value carrying a comma is quoted by the encoding rules above. |

### `triaxial-rotation-samples` — Triaxial Rotation Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Sample instant (CMRecordedRotationRateData.startDate). |
| `x` | number | no | `rad/s` | Rotation rate about x in radians per second. |
| `y` | number | no | `rad/s` | Rotation rate about y in radians per second. |
| `z` | number | no | `rad/s` | Rotation rate about z in radians per second. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `odometer-samples` — Odometer Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `start` | timestamp | no | — | Recording interval start (startDate). |
| `end` | timestamp | no | — | Recording interval end (endDate). |
| `gpsDate` | timestamp | no | — | Time of the GPS measurement associated with the location. |
| `speed` | number | no | `m/s` | Instantaneous device velocity in metres per second. |
| `speedAccuracy` | number | no | `m/s` | Accuracy of the speed value. |
| `slope` | number | yes | `deg` | Slope toward the direction of travel in degrees; empty when unavailable. |
| `maxAbsSlope` | number | yes | `deg` | Maximum absolute slope toward all directions in degrees; empty when unavailable. |
| `deltaDistance` | number | no | `m` | Distance travelled since the last location in metres. |
| `deltaDistanceAccuracy` | number | no | `m` | Accuracy of the delta distance in metres. |
| `deltaAltitude` | number | no | `m` | Change in altitude above mean sea level in metres. |
| `verticalAccuracy` | number | no | `m` | Validity and estimated uncertainty of the altitude values in metres. |
| `originDevice` | string | no | — | CMOdometerOriginDevice case name: unknown, local, or remote. |
| `device` | string | no | — | Exact SensorKit SRDevice.productType token for the source-device partition that supplied every row in the batch. It is not SRDevice.description, a user-assigned name, a system name/version, or a stable physical-unit identifier. |

### `beat-interval-series` — Beat Interval Series

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Beat instant as seconds since the Unix epoch. |
| `precededByGap` | integer | no | — | 1 when a gap in beat detection precedes this beat, else 0. |

### `location-track-samples` — Location Track Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last. CR (0x0D) is prohibited anywhere, including inside quoted fields.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or LF; embedded double quotes are doubled; all other fields are unquoted.
Finite IEEE-754 binary64 values use canonical base-10 lexemes matching the following regular expression. A plus sign, exponent, leading integer zero, negative zero, and redundant fractional trailing zero are prohibited; a lone fractional .0 remains admitted for integral values.
`^(?:0(?:\.0|\.[0-9]*[1-9])?|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?|-(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.(?:0|[0-9]*[1-9]))?))$`
Integer values use base-10 lexemes matching the following regular expression. A plus sign, -0, leading zero, decimal point, and exponent are prohibited.
`^(?:0|-?[1-9][0-9]*)$`
Seconds since the Unix epoch as a finite IEEE-754 binary64 value in the numbers form above; the column documentation states which columns are timestamps.
The table's `Nullable` column controls empty fields: `no` requires a non-empty field in every data row; `yes` permits an empty field with the meaning stated for that column. The literal strings `null` and `NULL` have no special meaning.

| Column | Type | Nullable | Unit | Meaning |
|---|---|---|---|---|
| `timestamp` | timestamp | no | — | Location fix instant. |
| `latitude` | number | no | `deg` | WGS 84 latitude in degrees. |
| `longitude` | number | no | `deg` | WGS 84 longitude in degrees. |
| `altitude` | number | no | `m` | Altitude above the WGS 84 reference ellipsoid in metres. |
| `horizontalAccuracy` | number | no | `m` | Radius of uncertainty for the horizontal position in metres. |
| `verticalAccuracy` | number | yes | `m` | Uncertainty of the altitude in metres; empty when altitude is invalid. |
| `speed` | number | yes | `m/s` | Instantaneous speed in metres per second; empty when unavailable. |
| `speedAccuracy` | number | yes | `m/s` | Uncertainty of the speed in metres per second; empty when unavailable. |
| `course` | number | yes | `deg` | Direction of travel in degrees clockwise from true north; empty when unavailable. |
| `courseAccuracy` | number | yes | `deg` | Uncertainty of the course in degrees; empty when unavailable. |

### `fhir-collection-bundle` — FHIR R4 Collection Bundle

Media type: `application/fhir+json`.
UTF-8.
One strict UTF-8 JSON resource with `resourceType` = `Bundle`, `Bundle.type` = `collection`, a required offset-bearing `Bundle.timestamp`, and one `Bundle.entry` for each source sample in source order. The Bundle has at least one entry. Every entry has a unique absolute non-fragment `fullUrl` and a resource object with `resourceType`; `request`, `response`, and `search` are absent.
Every entry resource conforms to the profile set the emitting adapter declares for its stream; one Bundle carries one stream and one source batch only.
An empty batch emits no document rather than an empty Bundle.
Grove format validation verifies strict JSON syntax and only the collection-Bundle envelope and resource shape described above. It does not execute the official FHIR Validator over embedded resources. Base FHIR R4 conformance, adapter-declared resource profiles, the one-stream/one-source-batch boundary, and preservation of source ordering and source meaning remain producer responsibilities unless a separate validation step explicitly performs them.

### `fhir-resource` — FHIR Resource

Media types: `application/fhir+json; fhirVersion=1.0`, `application/fhir+json; fhirVersion=4.0`.
UTF-8.
One complete provider-issued FHIR DSTU2 or R4 resource in FHIR JSON representation, byte-preserved exactly as the source platform delivered it.
Attachment.contentType is exactly `application/fhir+json; fhirVersion=1.0` for DSTU2 or `application/fhir+json; fhirVersion=4.0` for R4. The standard media-type parameter is the authoritative release declaration; an unversioned or other value is not admitted.
The carrying document records the issuing source, while the attachment media type records the exact FHIR release. Grove never converts, re-encodes, or asserts conformance over another issuer's resource.
One document carries exactly one clinical record's FHIR payload. Grove format validation verifies strict JSON syntax and a `resourceType`-bearing object only; it does not infer the FHIR release or execute base or profile validation over the issuer's resource.

### `clinical-document` — Clinical Document

Media type: `application/hl7-cda+xml`.
One HL7 Clinical Document Architecture Release 2 document, byte-preserved exactly as the source platform delivered it. Grove never rewrites, reserializes, or asserts conformance over another issuer's document; the carrying document records the issuer.

### `native-recording` — Native Recording

Media type: `application/json`.
UTF-8 without a byte-order mark.
The payload is strict UTF-8 JSON with an object or array root. Byte-order marks, duplicate object member names, non-finite numeric values, scalar roots, malformed UTF-8, and malformed JSON are rejected.
This format defines no per-stream field schema. The carrying document's source type supplies the source category and meaning; payload members retain their native producer-defined meaning and remain opaque to a generic receiver.
One document carries one stream and one source batch. Validation checks only this strict envelope; it does not reinterpret, sanitize, rewrite, or reserialize the bytes.

### `provider-recording` — Provider Recording

Media type: `application/json`.
UTF-8.
The payload is the exact JSON response-body bytes returned by the provider API; HTTP transport framing is not part of the payload.
The emitting adapter documents the provider, API, and endpoint per stream; the bytes are never rewritten, reordered, or reserialized.
One document carries one API response for one account and one source element batch. Grove format validation verifies strict JSON syntax and an object-or-array envelope only; provider-domain schema and meaning remain the adapter's responsibility.

### `photoplethysmogram-samples` — Photoplethysmogram Samples

Media type: `application/octet-stream`.
Varint record count, then that many PPG records.

**Primitive encodings**

| Primitive | Encoding |
|---|---|
| `varint` | Canonical unsigned LEB128: little-endian groups of 7 bits, high bit set on every byte except the last, using the shortest possible encoding. Signed integers are first converted to their 64-bit two's-complement bit pattern, so negative values occupy exactly ten bytes. Decoders reject overlong encodings and values outside 64 bits. |
| `float64` | Finite IEEE-754 binary64 bit pattern, big-endian (network byte order), eight bytes. NaN and infinities are prohibited; negative zero is canonicalized to positive zero before encoding. |
| `boolean` | One byte: 0x00 false, 0x01 true. |
| `string` | Varint UTF-8 byte count, then exact well-formed UTF-8 bytes. Unicode normalization is not performed; unpaired surrogate code points and malformed UTF-8 are rejected. |
| `array` | Varint element count, then the elements in order. |
| `set` | Canonical set: reject duplicate logical values, sort unique values in ascending numeric order, then encode the count and elements. Decoders reject duplicate or non-ascending elements. |
| `optional` | One boolean presence byte; when true, the value follows. |

**Record layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `startDate` | `float64` | — | This record's session start anchor as seconds since the Unix epoch. |
| `nanosecondsSinceStart` | `varint(int64)` | — | Offset of this record instant from startDate in nanoseconds. |
| `temperature` | `optional(float64)` | `Cel` | Device temperature in degrees Celsius when available. |
| `usage` | `array(string)` | — | SRPhotoplethysmogramSample.Usage raw values active for the record. |
| `opticalSamples` | `array(opticalSample)` | — | The optical channel samples of the record. |
| `accelerometerSamples` | `array(accelerometerSample)` | — | The accelerometer samples of the record. |

**Optical sample layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `emitter` | `varint(int64)` | — | Active emitter index as a signed 64-bit integer. |
| `activePhotodiodeIndexes` | `set(varint(uint64))` | — | Active photodiode indexes as unsigned 64-bit integers. |
| `signalIdentifier` | `varint(int64)` | — | Signal identifier as a signed 64-bit integer. |
| `nominalWavelength` | `float64` | `nm` | Nominal wavelength in nanometres. |
| `effectiveWavelength` | `float64` | `nm` | Effective wavelength in nanometres. |
| `samplingFrequency` | `float64` | `Hz` | Sampling frequency in hertz. |
| `nanosecondsSinceStart` | `varint(int64)` | — | Offset of this optical sample instant from this record's startDate session anchor in nanoseconds. |
| `conditions` | `array(string)` | — | SRPhotoplethysmogramOpticalSample.Condition raw values. |
| `noiseTerms` | `optional(noiseTerms)` | — | Noise estimates when available. |
| `normalizedReflectance` | `optional(float64)` | — | Normalized reflectance when available. |

**Noise terms layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `whiteNoise` | `float64` | `Normalized Units²/Hz` | White-noise variance estimate per hertz in normalizedReflectance; apply the noise-equivalent-bandwidth factor to estimate in-band noise. |
| `pinkNoise` | `float64` | `Normalized Units²` | Sensor estimate of total pink-noise variance in normalizedReflectance. |
| `backgroundNoise` | `float64` | `Normalized Units` | Sensor estimate of ambient-noise intrusion in normalizedReflectance. |
| `backgroundNoiseOffset` | `float64` | `Normalized Units²/Hz` | White-noise variance estimate per hertz in backgroundNoise; apply the noise-equivalent-bandwidth factor when estimating total ambient noise. |

**Accelerometer sample layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `nanosecondsSinceStart` | `varint(int64)` | — | Offset of this accelerometer sample instant from this record's startDate session anchor in nanoseconds. |
| `samplingFrequency` | `float64` | `Hz` | Sampling frequency in hertz. |
| `x` | `float64` | `[g]` | Acceleration along x in G. |
| `y` | `float64` | `[g]` | Acceleration along y in G. |
| `z` | `float64` | `[g]` | Acceleration along z in G. |
