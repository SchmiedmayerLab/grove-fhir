<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative connected-provider status matrix

This table enumerates every provider field in the closed v0.2.0 Google Health API, Oura, and Withings source catalogs. Each field has one definitive status. This adapter maps data already obtained by its caller; it contains no provider authentication, network, pagination, or fetching implementation.

| Provider | Source type | Source status | Provider field | Field status | Measurement | Representation / conversion | Binding reason / effective time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `google-health-api` | `steps` | `supported` | `steps.count` | `supported` | step-count | integer count to UCUM {steps} | steps.interval |
| `google-health-api` | `distance` | `supported` | `distance.millimeters` | `supported` | distance | millimetres divided by 1000 to UCUM m | distance.interval |
| `google-health-api` | `active-energy-burned` | `supported` | `activeEnergyBurned.kcal` | `supported` | active-energy | identity UCUM kcal | activeEnergyBurned.interval |
| `google-health-api` | `weight` | `supported` | `weight.weightGrams` | `supported` | body-weight | grams divided by 1000 to UCUM kg | weight.sampleTime.physicalTime |
| `google-health-api` | `body-fat` | `unmodeled` | `bodyFat.percentage` | `unmodeled` | — | — | No shared Mobile body-fat profile exists in version 0.2.0. |
| `google-health-api` | `height` | `supported` | `height.heightMillimeters` | `supported` | body-height | millimetres divided by 10 to UCUM cm | height.sampleTime.physicalTime |
| `google-health-api` | `vo2-max` | `unmodeled` | `vo2Max.vo2Max` | `unmodeled` | — | — | No shared Mobile VO2 max profile exists in version 0.2.0. |
| `google-health-api` | `daily-oxygen-saturation` | `deferred` | `dailyOxygenSaturation.averagePercentage` | `deferred` | — | — | A civil-date daily average is not a point-in-time pulse-oximetry result and cannot satisfy the shared oxygen-saturation effective-time semantics without invention. |
| `google-health-api` | `heart-rate-variability` | `unmodeled` | `heartRateVariability.rootMeanSquareOfSuccessiveDifferencesMilliseconds` | `unmodeled` | — | — | RMSSD is distinct from SDNN and no shared Mobile HRV profile exists in version 0.2.0. |
| `google-health-api` | `heart-rate-variability` | `unmodeled` | `heartRateVariability.standardDeviationMilliseconds` | `unmodeled` | — | — | No shared Mobile HRV profile exists in version 0.2.0. |
| `google-health-api` | `daily-resting-heart-rate` | `unmodeled` | `dailyRestingHeartRate.beatsPerMinute` | `unmodeled` | — | — | Resting heart rate is a daily aggregate with semantics distinct from the shared point heart-rate profile. |
| `google-health-api` | `daily-respiratory-rate` | `deferred` | `dailyRespiratoryRate.breathsPerMinute` | `deferred` | — | — | A civil-date daily average cannot satisfy the shared point respiratory-rate effective-time semantics without invention. |
| `google-health-api` | `blood-glucose` | `deferred` | `bloodGlucose.bloodGlucoseMilligramsPerDeciliter` | `deferred` | — | — | The consumed source shape has no specimen evidence, so none of the four Health Connect-only specimen-specific glucose profiles can be selected. |
| `google-health-api` | `core-body-temperature` | `supported` | `coreBodyTemperature.temperatureCelsius` | `supported` | body-temperature | identity UCUM Cel | coreBodyTemperature.sampleTime.physicalTime |
| `google-health-api` | `floors` | `unmodeled` | `floors.count` | `unmodeled` | — | — | No shared Mobile floors-climbed profile exists in version 0.2.0. |
| `google-health-api` | `basal-energy-burned` | `unmodeled` | `basalEnergyBurned.kcal` | `unmodeled` | — | — | Basal energy is not active energy and has no shared Mobile profile in version 0.2.0. |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.minutesAsleep` | `supported` | sleep-duration | minutes divided by 60 to UCUM h | sleep.interval |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=DEEP].minutes` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=REM].minutes` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=LIGHT].minutes` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=AWAKE].minutes` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `google-health-api` | `exercise` | `unmodeled` | `exercise.interval` | `unmodeled` | — | — | Workout duration has no shared Mobile profile in version 0.2.0. |
| `google-health-api` | `heart-rate` | `mapped-standard` | `payload` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | The source points may be irregular; retain the provider-native recording rather than resample or invent a uniform SampledData period. |
| `oura` | `daily_activity` | `supported` | `steps` | `supported` | step-count | integer count to UCUM {steps} | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `oura` | `daily_activity` | `supported` | `active_calories` | `supported` | active-energy | identity UCUM kcal | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `oura` | `daily_activity` | `supported` | `equivalent_walking_distance` | `supported` | distance | identity UCUM m | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `oura` | `sleep` | `supported` | `total_sleep_duration` | `supported` | sleep-duration | seconds divided by 3600 to UCUM h | bedtime_start through bedtime_end; output deferred when either boundary is absent |
| `oura` | `sleep` | `supported` | `deep_sleep_duration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `oura` | `sleep` | `supported` | `rem_sleep_duration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `oura` | `sleep` | `supported` | `light_sleep_duration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `oura` | `sleep` | `supported` | `awake_time` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `oura` | `sleep` | `supported` | `lowest_heart_rate` | `unmodeled` | — | — | A sleep-session minimum is not a point heart-rate measurement. |
| `oura` | `sleep` | `supported` | `average_hrv` | `unmodeled` | — | — | No shared Mobile HRV profile exists in version 0.2.0. |
| `oura` | `sleep` | `supported` | `average_breath` | `deferred` | — | — | A session average cannot satisfy the shared point respiratory-rate effective-time semantics without invention. |
| `oura` | `daily_spo2` | `deferred` | `spo2_percentage.average` | `deferred` | — | — | A daily average is not a point-in-time pulse-oximetry result. |
| `oura` | `workout` | `unmodeled` | `start_datetime/end_datetime` | `unmodeled` | — | — | Workout duration has no shared Mobile profile in version 0.2.0. |
| `oura` | `vO2_max` | `unmodeled` | `vo2_max` | `unmodeled` | — | — | No shared Mobile VO2 max profile exists in version 0.2.0. |
| `oura` | `daily_cardiovascular_age` | `unmodeled` | `vascular_age` | `unmodeled` | — | — | A provider-computed cardiovascular age is not a physiological measurement shared across sources. |
| `oura` | `daily_readiness` | `unmodeled` | `score` | `unmodeled` | — | — | A provider-computed readiness score is not a physiological measurement shared across sources. |
| `oura` | `heartrate` | `mapped-standard` | `payload` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | Timestamped points may be irregular; retain the provider-native recording rather than resample or invent a uniform SampledData period. |
| `withings` | `getmeas:1` | `supported` | `measure.value*10^unit` | `supported` | body-weight | provider SI value to UCUM kg | measure group date |
| `withings` | `getmeas:4` | `supported` | `measure.value*10^unit` | `supported` | body-height | provider SI value to UCUM cm | measure group date |
| `withings` | `getmeas:6` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | No shared Mobile body-fat profile exists in version 0.2.0. |
| `withings` | `getmeas:9` | `supported` | `measure.value*10^unit` | `supported` | blood-pressure | provider SI value to UCUM mm[Hg] | measure group date |
| `withings` | `getmeas:10` | `supported` | `measure.value*10^unit` | `supported` | blood-pressure | provider SI value to UCUM mm[Hg] | measure group date |
| `withings` | `getmeas:11` | `supported` | `measure.value*10^unit` | `supported` | heart-rate | provider value to UCUM /min | measure group date |
| `withings` | `getmeas:54` | `supported` | `measure.value*10^unit` | `supported` | oxygen-saturation | provider value to UCUM % | measure group date |
| `withings` | `getmeas:71` | `supported` | `measure.value*10^unit` | `supported` | body-temperature | provider value to UCUM Cel | measure group date |
| `withings` | `getmeas:123` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | No shared Mobile VO2 max profile exists in version 0.2.0. |
| `withings` | `getmeas:155` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | A provider-computed cardiovascular age is not a physiological measurement shared across sources. |
| `withings` | `getactivity:steps` | `supported` | `steps` | `supported` | step-count | integer count to UCUM {steps} | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `withings` | `getactivity:distance` | `supported` | `distance` | `supported` | distance | identity UCUM m | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `withings` | `getactivity:calories` | `supported` | `calories` | `supported` | active-energy | identity UCUM kcal | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `withings` | `getsummary:deepsleepduration` | `unmodeled` | `data.deepsleepduration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `withings` | `getsummary:remsleepduration` | `unmodeled` | `data.remsleepduration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `withings` | `getsummary:lightsleepduration` | `unmodeled` | `data.lightsleepduration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `withings` | `getsummary:wakeupduration` | `unmodeled` | `data.wakeupduration` | `unmodeled` | — | — | A stage-duration summary has no stage interval and is not a shared sleep-stage Observation. |
| `withings` | `getsummary:hr_average` | `unmodeled` | `data.hr_average` | `unmodeled` | — | — | A sleep-session average is not a point heart-rate measurement. |
| `withings` | `getsummary:rr_average` | `deferred` | `data.rr_average` | `deferred` | — | — | A sleep-session average cannot satisfy the shared point respiratory-rate effective-time semantics without invention. |
| `withings` | `getworkouts:interval` | `unmodeled` | `startdate/enddate` | `unmodeled` | — | — | Workout duration has no shared Mobile profile in version 0.2.0. |
| `withings` | `activityIntraday` | `mapped-standard` | `steps` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `activityIntraday` | `mapped-standard` | `calories` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `activityIntraday` | `mapped-standard` | `distance` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `activityIntraday` | `mapped-standard` | `elevation` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `activityIntraday` | `mapped-standard` | `heart_rate` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `activityIntraday` | `mapped-standard` | `spo2_auto` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `sleepIntraday` | `mapped-standard` | `hr` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `sleepIntraday` | `mapped-standard` | `rr` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `sleepIntraday` | `mapped-standard` | `snoring` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `sleepIntraday` | `mapped-standard` | `sdnn_1` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `sleepIntraday` | `mapped-standard` | `rmssd` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | — |
| `withings` | `getmeas:5` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Fat-free mass has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:8` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Fat mass has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:73` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Skin temperature is not relabeled as core or generic body temperature. |
| `withings` | `getmeas:76` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Muscle mass has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:77` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Hydration has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:88` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Bone mass has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:91` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Pulse-wave velocity has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:130` | `intentionally-unsupported` | `measure.value` | `intentionally-unsupported` | — | — | An AFib classification is diagnostic-adjacent and is not represented as an untyped scalar Observation. |
| `withings` | `getmeas:135` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A QRS interval requires an ECG-specific interpretation contract not present in version 0.2.0. |
| `withings` | `getmeas:136` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A PR interval requires an ECG-specific interpretation contract not present in version 0.2.0. |
| `withings` | `getmeas:137` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A QT interval requires an ECG-specific interpretation contract not present in version 0.2.0. |
| `withings` | `getmeas:138` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A corrected QT interval requires an ECG-specific interpretation contract not present in version 0.2.0. |
| `withings` | `getmeas:139` | `intentionally-unsupported` | `measure.value` | `intentionally-unsupported` | — | — | An AFib classification is diagnostic-adjacent and is not represented as an untyped scalar Observation. |
| `withings` | `getmeas:167` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Nerve health score has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:168` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Extracellular water has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:169` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Intracellular water has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:170` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Visceral fat has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:174` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Segmental fat mass has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:175` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Segmental muscle mass has no shared Mobile profile in version 0.2.0. |
| `withings` | `getmeas:196` | `unmodeled` | `measure.value*10^unit` | `unmodeled` | — | — | Electrodermal activity has no shared Mobile scalar profile in version 0.2.0. |

## Atomic grouped mappings

| Provider | Grouped source token | Required members | Measurement | Output discriminator | Rule |
| --- | --- | --- | --- | --- | --- |
| `withings` | `getmeas:9+10` | `getmeas:9`; `getmeas:10` | blood-pressure | blood-pressure-panel | Emit exactly one panel only when one type 9 value and one type 10 value occur in the same measure group; otherwise emit neither component as a normalized Observation. Use getmeas:9+10, not either member token, in the source-record identity preimage. |
