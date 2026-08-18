<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

Mobile platforms name their own data: HealthKit calls a step count
`HKQuantityTypeIdentifierStepCount`, reports sleep stages as an enumeration, and
attaches metadata under keys of its own. Resources produced by the
[Grove core guide](https://grovealliance.org/fhir/core) carry those platform names
alongside their clinical codings, because a platform identifier says something LOINC
cannot: exactly which sensor pipeline produced the number.

This guide publishes those vocabularies as proper FHIR code systems, with value sets over
them where a profile needs to bind one, so the platform codings validate like any other.

### Why not Apple's documentation URLs

Earlier Grove versions used `https://developer.apple.com/documentation/healthkit/…`
as the coding system. Documentation URLs are not terminology: they resolve to prose,
they change with Apple's site structure, and nothing defines which codes are valid.
The systems here are Grove-owned, versioned with the guide, and enumerate their codes.

### How the vocabulary stays honest

Every HealthKit value system in this guide is **generated from the Grove framework's
own source** — the same macro invocations that generate the Swift `code` and `display`
members, read by `tools/generate-platform-vocabulary.py`. Regenerating and diffing the
result against the committed FSH is a release step: a difference means the framework
writes codes this guide does not publish, and the guide is what has to move.

Codes are Swift case names (`asleepREM`, `eggWhite`), not the platform's raw integers:
Apple may renumber an enumeration, and `3` tells a consumer nothing.

### Contents

- **HealthKit sample types** — the identifier strings for quantity, category, and
  workout types.
- **HealthKit value enumerations** — one system per enumeration, generated.
- **HealthKit metadata keys** — the runtime key strings, as a fragment system.
- **Health Connect metadata fields** — the Android equivalents, also a fragment system.
- **SensorKit sensor streams** — `SRSensor` raw values, pinned to the framework by a
  test (the raw values are not derivable from the Swift names: `onWrist` is
  `com.apple.SensorKit.onWristState`, ambient light is `…als`).

### Dependencies

{% include dependency-table.xhtml %}

{% include globals-table.xhtml %}

{% include cross-version-analysis.xhtml %}

{% include ip-statements.xhtml %}
