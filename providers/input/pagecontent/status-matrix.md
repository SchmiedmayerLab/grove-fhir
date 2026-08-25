<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative connected-provider status matrix

This table enumerates every provider field in the closed v0.4.0 Google Health API, Oura, and Withings source catalogs. Each field has one definitive status. This adapter maps data already obtained by its caller; it contains no provider authentication, network, pagination, or fetching implementation.

| Provider | Source type | Source status | Provider field | Field status | Measurement | Representation / conversion | Binding reason / effective time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `google-health-api` | `steps` | `supported` | `steps.count` | `supported` | step-count | integer count to UCUM {steps} | steps.interval |
| `google-health-api` | `distance` | `supported` | `distance.millimeters` | `supported` | distance | millimetres divided by 1000 to UCUM m | distance.interval |
| `google-health-api` | `active-energy-burned` | `supported` | `activeEnergyBurned.kcal` | `supported` | active-energy | identity UCUM kcal | activeEnergyBurned.interval |
| `google-health-api` | `weight` | `supported` | `weight.weightGrams` | `supported` | body-weight | grams divided by 1000 to UCUM kg | weight.sampleTime.physicalTime |
| `google-health-api` | `body-fat` | `supported` | `bodyFat.percentage` | `supported` | body-fat-percentage | — | — |
| `google-health-api` | `height` | `supported` | `height.heightMillimeters` | `supported` | body-height | millimetres divided by 10 to UCUM cm | height.sampleTime.physicalTime |
| `google-health-api` | `vo2-max` | `supported` | `vo2Max.vo2Max` | `supported` | vo2-max | — | — |
| `google-health-api` | `daily-oxygen-saturation` | `supported` | `dailyOxygenSaturation.averagePercentage` | `supported` | oxygen-saturation-daily-average | — | — |
| `google-health-api` | `heart-rate-variability` | `supported` | `heartRateVariability.rootMeanSquareOfSuccessiveDifferencesMilliseconds` | `supported` | heart-rate-variability-rmssd | — | — |
| `google-health-api` | `heart-rate-variability` | `supported` | `heartRateVariability.standardDeviationMilliseconds` | `supported` | heart-rate-variability-rmssd; heart-rate-variability-sdnn | — | — |
| `google-health-api` | `daily-resting-heart-rate` | `supported` | `dailyRestingHeartRate.beatsPerMinute` | `supported` | resting-heart-rate | — | — |
| `google-health-api` | `daily-respiratory-rate` | `supported` | `dailyRespiratoryRate.breathsPerMinute` | `supported` | respiratory-rate-average | — | — |
| `google-health-api` | `blood-glucose` | `supported` | `bloodGlucose.bloodGlucoseMilligramsPerDeciliter` | `supported` | blood-glucose-unspecified-specimen | — | — |
| `google-health-api` | `core-body-temperature` | `supported` | `coreBodyTemperature.temperatureCelsius` | `supported` | body-temperature | identity UCUM Cel | coreBodyTemperature.sampleTime.physicalTime |
| `google-health-api` | `floors` | `supported` | `floors.count` | `supported` | flights-climbed | — | — |
| `google-health-api` | `basal-energy-burned` | `supported` | `basalEnergyBurned.kcal` | `supported` | basal-energy | — | — |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.minutesAsleep` | `supported` | sleep-duration | minutes divided by 60 to UCUM h | sleep.interval |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=DEEP].minutes` | `supported` | deep-sleep-duration | — | — |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=REM].minutes` | `supported` | rem-sleep-duration | — | — |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=LIGHT].minutes` | `supported` | light-sleep-duration | — | — |
| `google-health-api` | `sleep` | `supported` | `sleep.summary.stagesSummary[type=AWAKE].minutes` | `supported` | sleep-awake-duration | — | — |
| `google-health-api` | `exercise` | `supported` | `exercise.interval` | `supported` | workout | — | — |
| `google-health-api` | `heart-rate` | `mapped-standard` | `payload` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | The source points may be irregular; retain the provider-native recording rather than resample or invent a uniform SampledData period. |
| `oura` | `daily_activity` | `supported` | `steps` | `supported` | step-count | integer count to UCUM {steps} | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `oura` | `daily_activity` | `supported` | `active_calories` | `supported` | active-energy | identity UCUM kcal | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `oura` | `daily_activity` | `supported` | `equivalent_walking_distance` | `supported` | distance | identity UCUM m | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `oura` | `sleep` | `supported` | `total_sleep_duration` | `supported` | sleep-duration | seconds divided by 3600 to UCUM h | bedtime_start through bedtime_end; output deferred when either boundary is absent |
| `oura` | `sleep` | `supported` | `deep_sleep_duration` | `supported` | deep-sleep-duration | — | — |
| `oura` | `sleep` | `supported` | `rem_sleep_duration` | `supported` | rem-sleep-duration | — | — |
| `oura` | `sleep` | `supported` | `light_sleep_duration` | `supported` | light-sleep-duration | — | — |
| `oura` | `sleep` | `supported` | `awake_time` | `supported` | sleep-awake-duration | — | — |
| `oura` | `sleep` | `supported` | `lowest_heart_rate` | `supported` | sleep-heart-rate | — | — |
| `oura` | `sleep` | `supported` | `average_hrv` | `unmodeled` | — | — | Oura reports this as an RMSSD average over the sleep session, which the shared heart-rate-variability-rmssd measurement represents. Unmodelled only until the session-window effective rule for it is settled. |
| `oura` | `sleep` | `supported` | `average_breath` | `supported` | respiratory-rate-average | — | — |
| `oura` | `daily_spo2` | `supported` | `spo2_percentage.average` | `supported` | oxygen-saturation-daily-average | — | — |
| `oura` | `workout` | `supported` | `start_datetime/end_datetime` | `supported` | workout | — | — |
| `oura` | `vO2_max` | `supported` | `vo2_max` | `supported` | vo2-max | — | — |
| `oura` | `daily_cardiovascular_age` | `intentionally-unsupported` | `vascular_age` | `intentionally-unsupported` | — | — | Although two providers report it, each value is the output of an undisclosed proprietary algorithm over different inputs (Withings pulse-wave velocity versus Oura PPG features), so the numbers are not comparable and no shared physiological definition exists; normalizing them under one code would fabricate clinical comparability, and the diagnostic-adjacent 'age' framing makes a shared measurement unsafe. Both provider catalog rows already record this refusal. |
| `oura` | `daily_readiness` | `intentionally-unsupported` | `score` | `intentionally-unsupported` | — | — | A proprietary vendor score with no physiologic unit is not a comparable measurement; normalizing it as a dimensionless quantity would misrepresent an undisclosed composite algorithm as an observable. The same verdict applies to Oura's daily sleep and activity scores, which are not yet inventoried in providers-adapter.json. |
| `oura` | `heartrate` | `mapped-standard` | `payload` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | Timestamped points may be irregular; retain the provider-native recording rather than resample or invent a uniform SampledData period. |
| `withings` | `getmeas:1` | `supported` | `measure.value*10^unit` | `supported` | body-weight | provider SI value to UCUM kg | measure group date |
| `withings` | `getmeas:4` | `supported` | `measure.value*10^unit` | `supported` | body-height | provider SI value to UCUM cm | measure group date |
| `withings` | `getmeas:6` | `supported` | `measure.value*10^unit` | `supported` | body-fat-percentage | — | — |
| `withings` | `getmeas:9` | `supported` | `measure.value*10^unit` | `supported` | blood-pressure | provider SI value to UCUM mm[Hg] | measure group date |
| `withings` | `getmeas:10` | `supported` | `measure.value*10^unit` | `supported` | blood-pressure | provider SI value to UCUM mm[Hg] | measure group date |
| `withings` | `getmeas:11` | `supported` | `measure.value*10^unit` | `supported` | heart-rate | provider value to UCUM /min | measure group date |
| `withings` | `getmeas:54` | `supported` | `measure.value*10^unit` | `supported` | oxygen-saturation | provider value to UCUM % | measure group date |
| `withings` | `getmeas:71` | `supported` | `measure.value*10^unit` | `supported` | body-temperature | provider value to UCUM Cel | measure group date |
| `withings` | `getmeas:123` | `supported` | `measure.value*10^unit` | `supported` | vo2-max | — | — |
| `withings` | `getmeas:155` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | Although two providers report it, each value is the output of an undisclosed proprietary algorithm over different inputs (Withings pulse-wave velocity versus Oura PPG features), so the numbers are not comparable and no shared physiological definition exists; normalizing them under one code would fabricate clinical comparability, and the diagnostic-adjacent 'age' framing makes a shared measurement unsafe. Both provider catalog rows already record this refusal. |
| `withings` | `getactivity:steps` | `supported` | `steps` | `supported` | step-count | integer count to UCUM {steps} | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `withings` | `getactivity:distance` | `supported` | `distance` | `supported` | distance | identity UCUM m | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `withings` | `getactivity:calories` | `supported` | `calories` | `supported` | active-energy | identity UCUM kcal | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `withings` | `getsummary:deepsleepduration` | `supported` | `data.deepsleepduration` | `supported` | deep-sleep-duration | — | — |
| `withings` | `getsummary:remsleepduration` | `supported` | `data.remsleepduration` | `supported` | rem-sleep-duration | — | — |
| `withings` | `getsummary:lightsleepduration` | `supported` | `data.lightsleepduration` | `supported` | light-sleep-duration | — | — |
| `withings` | `getsummary:wakeupduration` | `supported` | `data.wakeupduration` | `supported` | sleep-awake-duration | — | — |
| `withings` | `getsummary:hr_average` | `supported` | `data.hr_average` | `supported` | sleep-heart-rate; sleeping-heart-rate-average | — | — |
| `withings` | `getsummary:rr_average` | `supported` | `data.rr_average` | `supported` | respiratory-rate-average | — | — |
| `withings` | `getworkouts:interval` | `supported` | `startdate/enddate` | `supported` | workout | — | — |
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
| `withings` | `getmeas:5` | `supported` | `measure.value*10^unit` | `supported` | lean-body-mass | — | — |
| `withings` | `getmeas:8` | `supported` | `measure.value*10^unit` | `supported` | body-fat-mass | — | — |
| `withings` | `getmeas:73` | `supported` | `measure.value*10^unit` | `supported` | skin-temperature | — | — |
| `withings` | `getmeas:76` | `supported` | `measure.value*10^unit` | `supported` | muscle-mass | — | — |
| `withings` | `getmeas:77` | `supported` | `measure.value*10^unit` | `supported` | body-water-mass | — | — |
| `withings` | `getmeas:88` | `supported` | `measure.value*10^unit` | `supported` | bone-mass | — | — |
| `withings` | `getmeas:91` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | Diagnostic-adjacent cardiovascular assessment: Withings PWV is an aortic-stiffness screening value produced by a proprietary single-vendor scale algorithm (and was subject to regulatory withdrawal and reintroduction), with no second evidencing source and no safe wellness normalization, so admitting it as a normalized measurement would misrepresent a clinical vascular assessment. |
| `withings` | `getmeas:130` | `intentionally-unsupported` | `measure.value` | `intentionally-unsupported` | — | — | An AFib classification is diagnostic-adjacent and is not represented as an untyped scalar Observation. |
| `withings` | `getmeas:135` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A QRS interval requires an ECG-specific interpretation contract not present in version 0.4.0. |
| `withings` | `getmeas:136` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A PR interval requires an ECG-specific interpretation contract not present in version 0.4.0. |
| `withings` | `getmeas:137` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A QT interval requires an ECG-specific interpretation contract not present in version 0.4.0. |
| `withings` | `getmeas:138` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A corrected QT interval requires an ECG-specific interpretation contract not present in version 0.4.0. |
| `withings` | `getmeas:139` | `intentionally-unsupported` | `measure.value` | `intentionally-unsupported` | — | — | An AFib classification is diagnostic-adjacent and is not represented as an untyped scalar Observation. |
| `withings` | `getmeas:167` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | A proprietary vendor score with no physiologic unit, and additionally diagnostic-adjacent: Withings positions it as small-fiber-neuropathy screening, so an untyped scalar Observation would be misleading. |
| `withings` | `getmeas:168` | `supported` | `measure.value*10^unit` | `supported` | extracellular-water-mass | — | — |
| `withings` | `getmeas:169` | `supported` | `measure.value*10^unit` | `supported` | intracellular-water-mass | — | — |
| `withings` | `getmeas:170` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The value is a unitless proprietary rating, not a mass or area; emitting it as a dimensionless UCUM quantity would assert a measurand and comparability the vendor does not define. |
| `withings` | `getmeas:174` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The consumed source shape (measure.value*10^unit) does not recover which body segment a value belongs to, and the shared model has no body-segment site; emitting a segment mass under whole-body fat-mass or muscle-mass semantics would be wrong, so conversion is refused rather than mislabeled. |
| `withings` | `getmeas:175` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The consumed source shape (measure.value*10^unit) does not recover which body segment a value belongs to, and the shared model has no body-segment site; emitting a segment mass under whole-body fat-mass or muscle-mass semantics would be wrong, so conversion is refused rather than mislabeled. |
| `withings` | `getmeas:196` | `supported` | `measure.value*10^unit` | `supported` | electrodermal-activity | — | — |

## Atomic grouped mappings

| Provider | Grouped source token | Required members | Measurement | Output discriminator | Rule |
| --- | --- | --- | --- | --- | --- |
| `withings` | `getmeas:9+10` | `getmeas:9`; `getmeas:10` | blood-pressure | blood-pressure-panel | Emit exactly one panel only when one type 9 value and one type 10 value occur in the same measure group; otherwise emit neither component as a normalized Observation. Use getmeas:9+10, not either member token, in the source-record identity preimage. |
