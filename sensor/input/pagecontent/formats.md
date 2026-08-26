<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit catalog/format-registry.json and run
`python3 Scripts/render-format-registry.py`.
-->

Every Grove recording DocumentReference content entry declares exactly one payload format from this closed registry in `content.format`.
A receiver can parse every admitted payload from this page and the machine registry alone; an unregistered payload format is nonconformant.
The machine registry is [`catalog/format-registry.json`](https://grovealliance.org/fhir/catalog/format-registry.json); this page renders it.

### `heart-rate-samples` — Heart Rate Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Sample instant. |
| `value` | number | `/min` | Heart rate in beats per minute. |
| `confidence` | integer | — | CMHighFrequencyHeartRateDataConfidence raw value: 0 low, 1 medium, 2 high, 3 highest. |
| `device` | string | — | Source device description for the batch. |

### `triaxial-acceleration-samples` — Triaxial Acceleration Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Sample instant. |
| `identifier` | integer | — | The CoreMotion batch identifier the sample belongs to. |
| `x` | number | `[g]` | Acceleration along x in G. |
| `y` | number | `[g]` | Acceleration along y in G. |
| `z` | number | `[g]` | Acceleration along z in G. |
| `device` | string | — | Source device description for the batch. |

### `ambient-light-samples` — Ambient Light Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Sample instant. |
| `lux` | number | `lx` | Illuminance in lux. |
| `placement` | string | — | SRAmbientLightSample.SensorPlacement textual description. |
| `chromacityX` | number | — | CIE 1931 x chromaticity coordinate. |
| `chromacityY` | number | — | CIE 1931 y chromaticity coordinate. |
| `device` | string | — | Source device description for the batch. |

### `ambient-pressure-samples` — Ambient Pressure Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Sample instant. |
| `identifier` | integer | — | The CoreMotion batch identifier the sample belongs to. |
| `pressure` | number | `kPa` | Ambient pressure in kilopascals as provided by CoreMotion. |
| `temperature` | number | `Cel` | Sensor temperature in degrees Celsius as provided by CoreMotion. |
| `device` | string | — | Source device description for the batch. |

### `pedometer-samples` — Pedometer Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `start` | timestamp | — | Interval start. |
| `end` | timestamp | — | Interval end. |
| `steps` | integer | `{steps}` | Steps taken in the interval. |
| `distance` | number | `m` | Estimated distance in metres; empty when unavailable. |
| `floorsUp` | integer | — | Floors ascended; empty when unavailable. |
| `floorsDown` | integer | — | Floors descended; empty when unavailable. |
| `currentPace` | number | `s/m` | Current pace in seconds per metre; empty when unavailable. |
| `currentCadence` | number | `/s` | Current cadence in steps per second; empty when unavailable. |
| `avgActivePace` | number | `s/m` | Average active pace in seconds per metre; empty when unavailable. |
| `device` | string | — | Source device description for the batch. |

### `wrist-temperature-samples` — Wrist Temperature Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Temperature sample instant. |
| `value` | number | `Cel` | Wrist temperature converted to degrees Celsius. |
| `errorEstimate` | number | `Cel` | Estimated error converted to degrees Celsius. |
| `condition` | string | — | SRWristTemperature.Condition for the sample. The source is an option set, so zero or more conditions apply: the value is the set's members joined with a comma in the declared order offWrist, onCharger, inMotion, and the field is empty when no condition applies. A value carrying a comma is quoted by the encoding rules above. |

### `triaxial-rotation-samples` — Triaxial Rotation Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Sample instant (CMRecordedRotationRateData.startDate). |
| `x` | number | `rad/s` | Rotation rate about x in radians per second. |
| `y` | number | `rad/s` | Rotation rate about y in radians per second. |
| `z` | number | `rad/s` | Rotation rate about z in radians per second. |
| `device` | string | — | Source device description for the batch. |

### `odometer-samples` — Odometer Samples

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `start` | timestamp | — | Recording interval start (startDate). |
| `end` | timestamp | — | Recording interval end (endDate). |
| `gpsDate` | timestamp | — | Time of the GPS measurement associated with the location. |
| `speed` | number | `m/s` | Instantaneous device velocity in metres per second. |
| `speedAccuracy` | number | `m/s` | Accuracy of the speed value. |
| `slope` | number | `deg` | Slope toward the direction of travel in degrees; empty when unavailable. |
| `maxAbsSlope` | number | `deg` | Maximum absolute slope toward all directions in degrees; empty when unavailable. |
| `deltaDistance` | number | `m` | Distance travelled since the last location in metres. |
| `deltaDistanceAccuracy` | number | `m` | Accuracy of the delta distance in metres. |
| `deltaAltitude` | number | `m` | Change in altitude above mean sea level in metres. |
| `verticalAccuracy` | number | `m` | Validity and estimated uncertainty of the altitude values in metres. |
| `originDevice` | string | — | CMOdometerOriginDevice case name: unknown, local, or remote. |
| `device` | string | — | Source device description for the batch. |

### `beat-interval-series` — Beat Interval Series

Media type: `text/csv`.
UTF-8 without a byte-order mark.
One header row naming every column in order, then one row per source sample in source order.
LF (0x0A) after every row, including the last.
Comma (0x2C).
A field is enclosed in double quotes exactly when it contains a comma, a double quote, or a line break; embedded double quotes are doubled; all other fields are unquoted.
Decimal numbers use the shortest representation that round-trips an IEEE-754 binary64 value; integral values may carry a trailing .0.
Seconds since the Unix epoch as a decimal number in the numbers form above; the column documentation states which columns are timestamps.

| Column | Type | Unit | Meaning |
|---|---|---|---|
| `timestamp` | timestamp | — | Beat instant as seconds since the series start anchor stated by the document. |
| `precededByGap` | integer | — | 1 when a gap in beat detection precedes this beat, else 0. |

### `fhir-resource-array` — FHIR Resource Array

Media type: `application/vnd.grovealliance.fhir-array+json`.
UTF-8.
A single JSON array; each element is one complete FHIR R4 resource in FHIR JSON representation, in source sample order.
Every element conforms to the profile set the emitting adapter declares for its stream; the array carries resources of one stream and one batch only.
An empty batch emits no document rather than an empty array.

### `fhir-resource` — FHIR Resource

Media type: `application/fhir+json`.
UTF-8.
One complete provider-issued FHIR R4 resource in FHIR JSON representation, byte-preserved exactly as the source platform delivered it.
The carrying document records the issuing source; Grove never asserts conformance over another issuer's resource.
One document carries exactly one clinical record's FHIR payload.

### `native-recording` — Native Recording

Media type: `application/vnd.grovealliance.native+json`.
UTF-8.
The producer's exact native JSON serialization of one source batch, byte-preserved.
One document carries one stream and one batch.

### `provider-recording` — Provider Recording

Media type: `application/vnd.grovealliance.provider+json`.
UTF-8.
The verbatim JSON payload returned by the provider API call that produced the batch, byte-preserved apart from transport framing.
The emitting adapter documents the provider, API, and endpoint per stream; the payload is never rewritten, reordered, or reserialized.
One document carries one API response for one account and one source element batch.

### `photoplethysmogram-samples` — Photoplethysmogram Samples

Media type: `application/vnd.grovealliance.ppg`.
Varint record count, then that many PPG records.

**Primitive encodings**

| Primitive | Encoding |
|---|---|
| `varint` | Unsigned LEB128: little-endian groups of 7 bits, high bit set on every byte except the last; signed integers are first truncated to their 64-bit two's-complement pattern, so negative values occupy ten bytes. |
| `float64` | IEEE-754 binary64 bit pattern, big-endian (network byte order), eight bytes. |
| `boolean` | One byte: 0x00 false, 0x01 true. |
| `string` | Varint UTF-8 byte count, then the UTF-8 bytes. |
| `array` | Varint element count, then the elements in order. |
| `set` | Varint element count, then the elements; element order is not significant and receivers must not rely on it. |
| `optional` | One boolean presence byte; when true, the value follows. |

**Record layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `startDate` | `float64` | — | Record start as seconds since the Unix epoch. |
| `nanosecondsSinceStart` | `varint(int64)` | — | Offset of the record from the batch start in nanoseconds. |
| `temperature` | `optional(float64)` | `Cel` | Device temperature in degrees Celsius when available. |
| `usage` | `array(string)` | — | SRPhotoplethysmogramSample.Usage raw values active for the record. |
| `opticalSamples` | `array(opticalSample)` | — | The optical channel samples of the record. |
| `accelerometerSamples` | `array(accelerometerSample)` | — | The accelerometer samples of the record. |

**Optical sample layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `emitter` | `varint(int)` | — | Active emitter index. |
| `activePhotodiodeIndexes` | `set(varint(int))` | — | Active photodiode indexes. |
| `signalIdentifier` | `varint(int)` | — | Signal identifier. |
| `nominalWavelength` | `float64` | `nm` | Nominal wavelength in nanometres. |
| `effectiveWavelength` | `float64` | `nm` | Effective wavelength in nanometres. |
| `samplingFrequency` | `float64` | `Hz` | Sampling frequency in hertz. |
| `nanosecondsSinceStart` | `varint(int64)` | — | Offset from the record start in nanoseconds. |
| `conditions` | `array(string)` | — | SRPhotoplethysmogramOpticalSample.Condition raw values. |
| `noiseTerms` | `optional(noiseTerms)` | — | Noise estimates when available. |
| `normalizedReflectance` | `optional(float64)` | — | Normalized reflectance when available. |

**Noise terms layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `whiteNoise` | `float64` | — |  |
| `pinkNoise` | `float64` | — |  |
| `backgroundNoise` | `float64` | — |  |
| `backgroundNoiseOffset` | `float64` | — |  |

**Accelerometer sample layout**

| Field | Encoding | Unit | Meaning |
|---|---|---|---|
| `nanosecondsSinceStart` | `varint(int64)` | — | Offset from the record start in nanoseconds. |
| `samplingFrequency` | `float64` | `Hz` | Sampling frequency in hertz. |
| `x` | `float64` | `[g]` | Acceleration along x in G. |
| `y` | `float64` | `[g]` | Acceleration along y in G. |
| `z` | `float64` | `[g]` | Acceleration along z in G. |
