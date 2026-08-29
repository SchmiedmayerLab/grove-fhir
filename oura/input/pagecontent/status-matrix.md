<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

### Authoritative Oura status matrix

This table lists every Oura field in the published Grove inventory. Each field has one definitive status. This guide profiles data already obtained before FHIR conversion; it contains no authentication, network, pagination, or fetching implementation.

| Source type | Source status | Provider field | Field status | Measurement | Representation / conversion | Binding reason / effective time |
| --- | --- | --- | --- | --- | --- | --- |
| `daily_activity` | `supported` | `steps` | `supported` | step-count | integer count to UCUM {steps} | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `daily_activity` | `supported` | `active_calories` | `supported` | active-energy | identity UCUM kcal | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `daily_activity` | `supported` | `equivalent_walking_distance` | `supported` | distance | identity UCUM m | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `sleep` | `supported` | `total_sleep_duration` | `supported` | sleep-duration | seconds divided by 3600 to UCUM h | bedtime_start through bedtime_end; output deferred when either boundary is absent |
| `sleep` | `supported` | `deep_sleep_duration` | `supported` | deep-sleep-duration | — | — |
| `sleep` | `supported` | `rem_sleep_duration` | `supported` | rem-sleep-duration | — | — |
| `sleep` | `supported` | `light_sleep_duration` | `supported` | light-sleep-duration | — | — |
| `sleep` | `supported` | `awake_time` | `supported` | sleep-awake-duration | — | — |
| `sleep` | `supported` | `lowest_heart_rate` | `supported` | sleep-heart-rate | — | — |
| `sleep` | `supported` | `average_hrv` | `unmodeled` | — | — | Oura reports this as an RMSSD average over the sleep session, but this contract does not define the exact session window to use as Observation.effectivePeriod. No FHIR output is admitted. |
| `sleep` | `supported` | `average_breath` | `supported` | respiratory-rate-average | — | — |
| `daily_spo2` | `supported` | `spo2_percentage.average` | `supported` | oxygen-saturation-daily-average | — | — |
| `workout` | `supported` | `start_datetime/end_datetime` | `supported` | workout | — | — |
| `vO2_max` | `supported` | `vo2_max` | `supported` | vo2-max | — | — |
| `daily_cardiovascular_age` | `platform-exclusive` | `vascular_age` | `platform-exclusive` | oura-cardiovascular-age | provider integer years to UCUM a | The Grove FHIR contracts carry the Oura cardiovascular-age figure as the provider-scoped oura-cardiovascular-age profile, on an age scale in UCUM years over the civil-day Period. The profile names the vendor in its code and description, so the figure cannot be mistaken for a chronological age, for a clinical vascular assessment, or for Withings' vascular age, which stays a separate measurement because the two are undisclosed algorithms over different inputs. No comparability between vendors and no diagnosis is asserted. |
| `daily_readiness` | `platform-exclusive` | `score` | `platform-exclusive` | oura-readiness-score | unitless provider value to the dimensionless UCUM {score} annotation | The Grove FHIR contracts carry the Oura readiness figure as the provider-scoped oura-readiness-score profile over the civil-day Period, on the dimensionless UCUM {score} annotation because the vendor publishes no physical unit for it. The code names the vendor and the profile description states the scale, so the figure cannot be read as an observable quantity. Nothing about the composite's inputs, weighting, or comparability across people is asserted, and Oura's daily sleep and activity scores remain outside the inventoried source surface. |
| `heartrate` | `mapped-standard` | `payload` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | Timestamped points may be irregular; retain the provider-native recording rather than resample or invent a uniform SampledData period. |
