<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

A day of step counts is roughly 400 HealthKit samples. A week of raw accelerometer at
50 Hz is 30 million. Writing one Observation per sample is correct FHIR and a bad idea
at both ends of that range — at the top it is unusable, and at the bottom it buries the
number the study actually analyses under provenance.

FHIR already has the answers. Which one applies depends on the shape of the data, not
on how much of it there is.

### Choosing a route

**Is the sampling regular — fixed period, one variable?**
Then it is a waveform, and one Observation carries the whole strip in
`valueSampledData`: `origin`, `period`, `dimensions`, and the values as
whitespace-separated decimals. This is how Grove writes electrocardiograms. A 30-second
lead at 512 Hz is one resource of about 80 KB, versus 15,000 resources. Per the PHD
guide's real-time sample-array rule, each channel is its own Observation or component —
never interleaved.

Regularity is necessary, not sufficient: SensorKit's PPG and accelerometer streams are
regular too, and their volume puts them on the batch route below rather than into
`SampledData` — one strip is fine, a week of 50 Hz is not. [Sensor
Streams](sensors.html) states that routing.

**Is each sample independently meaningful to a clinician?**
Then it is a measurement, and it gets its own Observation: blood pressure readings,
body weights, blood glucose. Verbosity is not a problem here, because the count is
small and every record carries a decision.

**Is the sample only meaningful in aggregate?**
Then aggregate before converting. Step counts, active energy, exercise minutes, and
stand hours are cumulative quantities whose per-sample records are an artefact of how
the phone flushed its buffer — a 2-step sample at 09:14 answers no question anyone
asked. Query them with `HKStatisticsCollectionQuery` at the interval the protocol
analyses (hourly or daily), and write one Observation per bucket with `effectivePeriod`
covering the bucket. A day of steps becomes 24 resources or 1, not 400, and the numbers
are the ones the analysis wants.

Grove does not aggregate on your behalf: the interval is a study-design decision, and a
framework that guessed it would be guessing at the analysis. Ask HealthKit for the
buckets, convert the results.

**Is it high-volume and individually meaningless?**
Then it is a payload, not a resource. It travels as a
[Grove Sensor Batch Document](StructureDefinition-grove-sensor-batch-document.html) —
a `DocumentReference` typed by the stream, whose attachment carries the media type,
hash, and size of the real file — with a summary Observation pointing back through
`derivedFrom`. Raw per-app usage detail and multi-day accelerometer belong here.

### Why not one big Bundle of everything

A transaction Bundle of 400 step Observations is still 400 Observations; it moves the
cost rather than removing it. Use the routes above to make the resource count
proportionate to the information, then use whatever transport your endpoint prefers.
For bulk upload the shape this guide specifies is newline-delimited JSON alongside the
payload files, following what [Bulk Data Access](https://hl7.org/fhir/uv/bulkdata/) uses
for export — one resource per line, no wrapping Bundle, so a consumer can stream it
without holding the whole set in memory. Grove's archive writer packages the payload
files; the NDJSON manifest beside them is specified here and not yet written by the
framework.

### Why not compress the resources instead

Compression makes a bad encoding smaller, not better. A consumer receiving 400
gzip-compressed step Observations still has to parse, deduplicate, and store 400
records to learn one daily total. Choose the encoding first; compress the transport
afterwards, which Grove's archives do anyway.
