<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative connected-provider status matrix

This table enumerates every provider field in the closed v0.6.0 Google Health API, Oura, and Withings source catalogs. Each field has one definitive status. This adapter maps data already obtained by its caller; it contains no provider authentication, network, pagination, or fetching implementation.

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
| `google-health-api` | `daily-resting-heart-rate` | `supported` | `dailyRestingHeartRate.beatsPerMinute` | `supported` | resting-heart-rate-daily-average | — | — |
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
| `oura` | `daily_cardiovascular_age` | `platform-exclusive` | `vascular_age` | `platform-exclusive` | oura-cardiovascular-age | provider integer years to UCUM a | Version 0.6.0 carries the Oura cardiovascular-age figure as the provider-scoped oura-cardiovascular-age profile, on an age scale in UCUM years over the civil-day Period. The profile names the vendor in its code and description, so the figure cannot be mistaken for a chronological age, for a clinical vascular assessment, or for Withings' vascular age, which stays a separate measurement because the two are undisclosed algorithms over different inputs. No comparability between vendors and no diagnosis is asserted. |
| `oura` | `daily_readiness` | `platform-exclusive` | `score` | `platform-exclusive` | oura-readiness-score | unitless provider value to the dimensionless UCUM {score} annotation | Version 0.6.0 carries the Oura readiness figure as the provider-scoped oura-readiness-score profile over the civil-day Period, on the dimensionless UCUM {score} annotation because the vendor publishes no physical unit for it. The code names the vendor and the profile description states the scale, so the figure cannot be read as an observable quantity. Nothing about the composite's inputs, weighting, or comparability across people is asserted, and Oura's daily sleep and activity scores remain outside the inventoried source surface. |
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
| `withings` | `getmeas:155` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-vascular-age | provider SI value to UCUM a | Version 0.6.0 carries the Withings vascular-age figure as the provider-scoped withings-vascular-age profile, on an age scale in UCUM years. The profile names the vendor in its code and description, so the figure cannot be mistaken for a chronological age, for a clinical vascular assessment, or for Oura's cardiovascular age, which stays a separate measurement because the two are undisclosed algorithms over different inputs. No comparability between vendors and no diagnosis is asserted. |
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
| `withings` | `getmeas:91` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-pulse-wave-velocity | provider SI value to UCUM m/s | Version 0.6.0 carries the Withings aortic pulse-wave velocity estimate as the provider-scoped withings-pulse-wave-velocity profile in UCUM metres per second. The code names the vendor rather than a shared arterial-stiffness concept, because no second inventoried source evidences it and a scale-derived estimate is not interchangeable with a tonometric measurement taken in clinic. No arterial-stiffness finding and no diagnosis is asserted. |
| `withings` | `getmeas:130` | `platform-exclusive` | `measure.value` | `platform-exclusive` | withings-atrial-fibrillation-notification-ecg | — | Version 0.6.0 carries the fact that Withings' electrocardiogram screening algorithm flagged signs of atrial fibrillation, as the provider-scoped withings-atrial-fibrillation-notification-ecg profile with a closed single-code result, on the same basis as the HealthKit irregular-heart-rhythm notification. An Observation is admitted only for the vendor's positive screening classification: Withings publishes no encoding for the numeric measure.value, so a negative or inconclusive classification produces no output. No rhythm finding, atrial-fibrillation burden, or diagnosis is asserted, and the code is taken from the providers code system so no receiver can read it as one. |
| `withings` | `getmeas:135` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | qrs-duration | provider SI value to UCUM ms | Version 0.6.0 carries the QRS duration the Withings algorithm measured from its own electrocardiogram, as the provider-scoped withings-qrs-duration profile under LOINC 8633-0. The profile is provider-scoped because Withings is the only inventoried source that reports the interval as a discrete measure. No rhythm interpretation, conduction finding, or diagnosis is asserted; the electrocardiogram recording remains the rhythm evidence. |
| `withings` | `getmeas:136` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | pr-interval | provider SI value to UCUM ms | Version 0.6.0 carries the PR interval the Withings algorithm measured from its own electrocardiogram, as the provider-scoped withings-pr-interval profile under LOINC 8625-6. The profile is provider-scoped because Withings is the only inventoried source that reports the interval as a discrete measure. No rhythm interpretation, conduction finding, or diagnosis is asserted; the electrocardiogram recording remains the rhythm evidence. |
| `withings` | `getmeas:137` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | qt-interval | provider SI value to UCUM ms | Version 0.6.0 carries the uncorrected QT interval the Withings algorithm measured from its own electrocardiogram, as the provider-scoped withings-qt-interval profile under LOINC 8634-8. The profile is provider-scoped because Withings is the only inventoried source that reports the interval as a discrete measure. No repolarization finding, rhythm interpretation, or diagnosis is asserted, and the value is never substituted for the rate-corrected interval. |
| `withings` | `getmeas:138` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | corrected-qt-interval | provider SI value to UCUM ms | Version 0.6.0 carries the rate-corrected QT interval Withings reports, as the provider-scoped withings-corrected-qt-interval profile under LOINC 8636-3. The profile is provider-scoped because Withings is the only inventoried source that reports the correction as a discrete measure and does not publish which correction formula it applied, so the value is deliberately not asserted to be interchangeable with a QTc read from a clinical twelve-lead electrocardiogram. No repolarization finding and no diagnosis is asserted. |
| `withings` | `getmeas:139` | `platform-exclusive` | `measure.value` | `platform-exclusive` | withings-atrial-fibrillation-notification-ppg | — | Version 0.6.0 carries the fact that Withings' photoplethysmography screening algorithm flagged signs of atrial fibrillation, as the provider-scoped withings-atrial-fibrillation-notification-ppg profile with a closed single-code result. It is kept separate from the electrocardiogram notification because it screens a different signal. An Observation is admitted only for the vendor's positive screening classification: Withings publishes no encoding for the numeric measure.value, so a negative or inconclusive classification produces no output. No rhythm finding, atrial-fibrillation burden, or diagnosis is asserted. |
| `withings` | `getmeas:167` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-nerve-health-score | unitless provider value to the dimensionless UCUM {score} annotation | Version 0.6.0 carries the Withings nerve-health figure as the provider-scoped withings-nerve-health-score profile, on the dimensionless UCUM {score} annotation because the vendor publishes no physical unit for it. The code names the vendor and the profile description states the scale. Withings positions the figure as small-fiber-neuropathy screening, so the profile deliberately asserts no neuropathy finding, no nerve-conduction measurement, and no diagnosis. |
| `withings` | `getmeas:168` | `supported` | `measure.value*10^unit` | `supported` | extracellular-water-mass | — | — |
| `withings` | `getmeas:169` | `supported` | `measure.value*10^unit` | `supported` | intracellular-water-mass | — | — |
| `withings` | `getmeas:170` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-visceral-fat-index | unitless provider value to the dimensionless UCUM {score} annotation | Version 0.6.0 carries the Withings visceral-fat figure as the provider-scoped withings-visceral-fat-index profile, on the dimensionless UCUM {score} annotation because the API returns the value without a unit and it is a rating rather than a mass or an area. The code names the vendor, so the figure cannot be folded into a shared body-composition measurement, and no measurand, no mass, and no comparability with another vendor's visceral-fat figure is asserted. |
| `withings` | `getmeas:174` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The consumed source shape (measure.value*10^unit) does not recover which body segment a value belongs to, and the shared model has no body-segment site; emitting a segment mass under whole-body fat-mass or muscle-mass semantics would be wrong, so conversion is refused rather than mislabeled. |
| `withings` | `getmeas:175` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The consumed source shape (measure.value*10^unit) does not recover which body segment a value belongs to, and the shared model has no body-segment site; emitting a segment mass under whole-body fat-mass or muscle-mass semantics would be wrong, so conversion is refused rather than mislabeled. |
| `withings` | `getmeas:196` | `supported` | `measure.value*10^unit` | `supported` | electrodermal-activity | — | — |

## Atomic grouped mappings

| Provider | Grouped source token | Required members | Measurement | Output discriminator | Rule |
| --- | --- | --- | --- | --- | --- |
| `withings` | `getmeas:9+10` | `getmeas:9`; `getmeas:10` | blood-pressure | blood-pressure-panel | Emit exactly one panel only when one type 9 value and one type 10 value occur in the same measure group; otherwise emit neither component as a normalized Observation. Use getmeas:9+10, not either member token, in the source-record identity preimage. |
