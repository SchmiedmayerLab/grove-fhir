<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

### Definitive status meanings

The machine catalog uses exactly these meanings:

- `supported`: v0.2.0 defines an exact conversion to a listed shared profile.
- `mapped-standard`: v0.2.0 maps the provider-native payload to a listed source-neutral
  Sensor contract without asserting a scalar clinical meaning.
- `provider-specific`: the source element is known and inventoried but has no shared
  Mobile semantic profile in this release.
- `deferred`: a plausible shared mapping exists, but source evidence or time/result
  semantics are insufficient for a conformant v0.2.0 conversion.
- `intentionally-unsupported`: v0.2.0 deliberately refuses the conversion because it
  would create a misleading or diagnostic-adjacent result.

Only `supported` rows may produce a scalar normalized Observation. `mapped-standard`
rows may produce only the listed Sensor contract. The other statuses do not authorize a
FHIR output under this adapter profile.

Important fail-closed boundaries include:

- Google Health `blood-glucose` does not supply the specimen evidence needed to select
  one of the four specimen-specific shared glucose profiles.
- daily and sleep-session averages are not relabeled as point-in-time vital signs.
- sleep-stage duration summaries are not relabeled as stage intervals when the source
  does not provide their boundaries.
- Oura/Withings scores and body-composition measures remain provider-specific.
- Withings systolic and diastolic values become one blood-pressure panel only when both
  occur in the same provider measure group.

See `catalog/connected-health-adapter.json` for every exact source token, element, unit
conversion, grouping rule, shared profile, and definitive status.
