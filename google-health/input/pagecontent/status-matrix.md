<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

# Authoritative Google Health API status matrix

This table enumerates every Google Health API field in the closed v0.5.0 source catalog. Each field has one definitive status. This guide profiles data already obtained by its caller; it contains no authentication, network, pagination, or fetching implementation.

| Source type | Source status | Provider field | Field status | Measurement | Representation / conversion | Binding reason / effective time |
| --- | --- | --- | --- | --- | --- | --- |
| `steps` | `supported` | `steps.count` | `supported` | step-count | integer count to UCUM {steps} | steps.interval |
| `distance` | `supported` | `distance.millimeters` | `supported` | distance | millimetres divided by 1000 to UCUM m | distance.interval |
| `active-energy-burned` | `supported` | `activeEnergyBurned.kcal` | `supported` | active-energy | identity UCUM kcal | activeEnergyBurned.interval |
| `weight` | `supported` | `weight.weightGrams` | `supported` | body-weight | grams divided by 1000 to UCUM kg | weight.sampleTime.physicalTime |
| `body-fat` | `supported` | `bodyFat.percentage` | `supported` | body-fat-percentage | — | — |
| `height` | `supported` | `height.heightMillimeters` | `supported` | body-height | millimetres divided by 10 to UCUM cm | height.sampleTime.physicalTime |
| `vo2-max` | `supported` | `vo2Max.vo2Max` | `supported` | vo2-max | — | — |
| `daily-oxygen-saturation` | `supported` | `dailyOxygenSaturation.averagePercentage` | `supported` | oxygen-saturation-daily-average | — | — |
| `heart-rate-variability` | `supported` | `heartRateVariability.rootMeanSquareOfSuccessiveDifferencesMilliseconds` | `supported` | heart-rate-variability-rmssd | — | — |
| `heart-rate-variability` | `supported` | `heartRateVariability.standardDeviationMilliseconds` | `supported` | heart-rate-variability-rmssd; heart-rate-variability-sdnn | — | — |
| `daily-resting-heart-rate` | `supported` | `dailyRestingHeartRate.beatsPerMinute` | `supported` | resting-heart-rate | — | — |
| `daily-respiratory-rate` | `supported` | `dailyRespiratoryRate.breathsPerMinute` | `supported` | respiratory-rate-average | — | — |
| `blood-glucose` | `supported` | `bloodGlucose.bloodGlucoseMilligramsPerDeciliter` | `supported` | blood-glucose-unspecified-specimen | — | — |
| `core-body-temperature` | `supported` | `coreBodyTemperature.temperatureCelsius` | `supported` | body-temperature | identity UCUM Cel | coreBodyTemperature.sampleTime.physicalTime |
| `floors` | `supported` | `floors.count` | `supported` | flights-climbed | — | — |
| `basal-energy-burned` | `supported` | `basalEnergyBurned.kcal` | `supported` | basal-energy | — | — |
| `sleep` | `supported` | `sleep.summary.minutesAsleep` | `supported` | sleep-duration | minutes divided by 60 to UCUM h | sleep.interval |
| `sleep` | `supported` | `sleep.summary.stagesSummary[type=DEEP].minutes` | `supported` | deep-sleep-duration | — | — |
| `sleep` | `supported` | `sleep.summary.stagesSummary[type=REM].minutes` | `supported` | rem-sleep-duration | — | — |
| `sleep` | `supported` | `sleep.summary.stagesSummary[type=LIGHT].minutes` | `supported` | light-sleep-duration | — | — |
| `sleep` | `supported` | `sleep.summary.stagesSummary[type=AWAKE].minutes` | `supported` | sleep-awake-duration | — | — |
| `exercise` | `supported` | `exercise.interval` | `supported` | workout | — | — |
| `heart-rate` | `mapped-standard` | `payload` | `mapped-standard` | — | https://grovealliance.org/fhir/sensor/StructureDefinition/grove-sensor-recording-document | The source points may be irregular; retain the provider-native recording rather than resample or invent a uniform SampledData period. |
