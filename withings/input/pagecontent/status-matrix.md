<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

GENERATED FILE. Edit the corresponding catalog JSON and run
`python3 Scripts/render-status-matrices.py`.
-->

### Withings Health Mate support matrix

This table lists every Withings Health Mate field in the published Grove inventory. Each field has one definitive status. This guide profiles data already obtained before FHIR conversion; it contains no authentication, network, pagination, or fetching implementation. A field named as a required group member admits no standalone output; only the corresponding grouped mapping below admits the result.

| Source type | Source status | Provider field | Field status | Measurement | Representation / conversion | Binding reason / effective time |
| --- | --- | --- | --- | --- | --- | --- |
| `getmeas:1` | `supported` | `measure.value*10^unit` | `supported` | body-weight | provider SI value to UCUM kg | measure group date |
| `getmeas:4` | `supported` | `measure.value*10^unit` | `supported` | body-height | provider SI value to UCUM cm | measure group date |
| `getmeas:6` | `supported` | `measure.value*10^unit` | `supported` | body-fat-percentage | — | — |
| `getmeas:9` | `supported` | `measure.value*10^unit` | `supported` | blood-pressure | required member of `getmeas:9+10`; no standalone output | measure group date |
| `getmeas:10` | `supported` | `measure.value*10^unit` | `supported` | blood-pressure | required member of `getmeas:9+10`; no standalone output | measure group date |
| `getmeas:11` | `supported` | `measure.value*10^unit` | `supported` | heart-rate | provider value to UCUM /min | measure group date |
| `getmeas:54` | `supported` | `measure.value*10^unit` | `supported` | oxygen-saturation | provider value to UCUM % | measure group date |
| `getmeas:71` | `supported` | `measure.value*10^unit` | `supported` | body-temperature | provider value to UCUM Cel | measure group date |
| `getmeas:123` | `supported` | `measure.value*10^unit` | `supported` | vo2-max | — | — |
| `getmeas:155` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-vascular-age | provider SI value to UCUM a | The Grove FHIR contracts carry the Withings vascular-age figure as the provider-scoped withings-vascular-age profile, on an age scale in UCUM years. The profile names the vendor in its code and description, so the figure cannot be mistaken for a chronological age, for a clinical vascular assessment, or for Oura's cardiovascular age, which stays a separate measurement because the two are undisclosed algorithms over different inputs. No comparability between vendors and no diagnosis is asserted. |
| `getactivity:steps` | `supported` | `steps` | `supported` | step-count | integer count to UCUM {steps} | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `getactivity:distance` | `supported` | `distance` | `supported` | distance | identity UCUM m | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `getactivity:calories` | `supported` | `calories` | `supported` | active-energy | identity UCUM kcal | the source civil day represented as a complete day Period; midpoint substitution is forbidden |
| `getsummary:deepsleepduration` | `supported` | `data.deepsleepduration` | `supported` | deep-sleep-duration | — | — |
| `getsummary:remsleepduration` | `supported` | `data.remsleepduration` | `supported` | rem-sleep-duration | — | — |
| `getsummary:lightsleepduration` | `supported` | `data.lightsleepduration` | `supported` | light-sleep-duration | — | — |
| `getsummary:wakeupduration` | `supported` | `data.wakeupduration` | `supported` | sleep-awake-duration | — | — |
| `getsummary:hr_average` | `supported` | `data.hr_average` | `supported` | sleep-heart-rate | — | exact sleep-session Period; method = session-mean |
| `getsummary:rr_average` | `supported` | `data.rr_average` | `supported` | respiratory-rate-average | — | method = session-mean |
| `getworkouts:interval` | `supported` | `startdate/enddate` | `supported` | workout | — | — |
| `activityIntraday` | `mapped-standard` | `steps` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `activityIntraday` | `mapped-standard` | `calories` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `activityIntraday` | `mapped-standard` | `distance` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `activityIntraday` | `mapped-standard` | `elevation` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `activityIntraday` | `mapped-standard` | `heart_rate` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `activityIntraday` | `mapped-standard` | `spo2_auto` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `sleepIntraday` | `mapped-standard` | `hr` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `sleepIntraday` | `mapped-standard` | `rr` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `sleepIntraday` | `mapped-standard` | `snoring` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `sleepIntraday` | `mapped-standard` | `sdnn_1` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `sleepIntraday` | `mapped-standard` | `rmssd` | `mapped-standard` | — | grove-sensor-recording-document; providers-recording-document | — |
| `getmeas:5` | `supported` | `measure.value*10^unit` | `supported` | lean-body-mass | — | — |
| `getmeas:8` | `supported` | `measure.value*10^unit` | `supported` | body-fat-mass | — | — |
| `getmeas:73` | `supported` | `measure.value*10^unit` | `supported` | skin-temperature | — | — |
| `getmeas:76` | `supported` | `measure.value*10^unit` | `supported` | muscle-mass | — | — |
| `getmeas:77` | `supported` | `measure.value*10^unit` | `supported` | body-water-mass | — | — |
| `getmeas:88` | `supported` | `measure.value*10^unit` | `supported` | bone-mass | — | — |
| `getmeas:91` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-pulse-wave-velocity | provider SI value to UCUM m/s | The Grove FHIR contracts carry the Withings aortic pulse-wave velocity estimate as the provider-scoped withings-pulse-wave-velocity profile in UCUM metres per second. The code names the vendor rather than a shared arterial-stiffness concept, because no second inventoried source evidences it and a scale-derived estimate is not interchangeable with a tonometric measurement taken in clinic. No arterial-stiffness finding and no diagnosis is asserted. |
| `getmeas:130` | `platform-exclusive` | `measure.value` | `platform-exclusive` | withings-atrial-fibrillation-notification-ecg | — | The Grove FHIR contracts carry the fact that Withings' electrocardiogram screening algorithm flagged signs of atrial fibrillation, as the provider-scoped withings-atrial-fibrillation-notification-ecg profile with a closed single-code result, on the same basis as the HealthKit irregular-heart-rhythm notification. An Observation is admitted only for the vendor's positive screening classification: Withings publishes no encoding for the numeric measure.value, so a negative or inconclusive classification produces no output. No rhythm finding, atrial-fibrillation burden, or diagnosis is asserted, and the code is taken from the providers code system so it cannot be interpreted as one. |
| `getmeas:135` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | qrs-duration | provider SI value to UCUM ms | The Grove FHIR contracts carry the QRS duration the Withings algorithm measured from its own electrocardiogram, as the provider-scoped withings-qrs-duration profile under LOINC 8633-0. The profile is provider-scoped because Withings is the only inventoried source that reports the interval as a discrete measure. No rhythm interpretation, conduction finding, or diagnosis is asserted; the electrocardiogram recording remains the rhythm evidence. |
| `getmeas:136` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | pr-interval | provider SI value to UCUM ms | The Grove FHIR contracts carry the PR interval the Withings algorithm measured from its own electrocardiogram, as the provider-scoped withings-pr-interval profile under LOINC 8625-6. The profile is provider-scoped because Withings is the only inventoried source that reports the interval as a discrete measure. No rhythm interpretation, conduction finding, or diagnosis is asserted; the electrocardiogram recording remains the rhythm evidence. |
| `getmeas:137` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | qt-interval | provider SI value to UCUM ms | The Grove FHIR contracts carry the uncorrected QT interval the Withings algorithm measured from its own electrocardiogram, as the provider-scoped withings-qt-interval profile under LOINC 8634-8. The profile is provider-scoped because Withings is the only inventoried source that reports the interval as a discrete measure. No repolarization finding, rhythm interpretation, or diagnosis is asserted, and the value is never substituted for the rate-corrected interval. |
| `getmeas:138` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | corrected-qt-interval | provider SI value to UCUM ms | The Grove FHIR contracts carry the rate-corrected QT interval Withings reports, as the provider-scoped withings-corrected-qt-interval profile under LOINC 8636-3. The profile is provider-scoped because Withings is the only inventoried source that reports the correction as a discrete measure and does not publish which correction formula it applied, so the value is deliberately not asserted to be interchangeable with a QTc read from a clinical twelve-lead electrocardiogram. No repolarization finding and no diagnosis is asserted. |
| `getmeas:139` | `platform-exclusive` | `measure.value` | `platform-exclusive` | withings-atrial-fibrillation-notification-ppg | — | The Grove FHIR contracts carry the fact that Withings' photoplethysmography screening algorithm flagged signs of atrial fibrillation, as the provider-scoped withings-atrial-fibrillation-notification-ppg profile with a closed single-code result. It is kept separate from the electrocardiogram notification because it screens a different signal. An Observation is admitted only for the vendor's positive screening classification: Withings publishes no encoding for the numeric measure.value, so a negative or inconclusive classification produces no output. No rhythm finding, atrial-fibrillation burden, or diagnosis is asserted. |
| `getmeas:167` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-nerve-health-score | unitless provider value to the dimensionless UCUM {score} annotation | The Grove FHIR contracts carry the Withings nerve-health figure as the provider-scoped withings-nerve-health-score profile, on the dimensionless UCUM {score} annotation because the vendor publishes no physical unit for it. The code names the vendor and the profile description states the scale. Withings positions the figure as small-fiber-neuropathy screening, so the profile deliberately asserts no neuropathy finding, no nerve-conduction measurement, and no diagnosis. |
| `getmeas:168` | `supported` | `measure.value*10^unit` | `supported` | extracellular-water-mass | — | — |
| `getmeas:169` | `supported` | `measure.value*10^unit` | `supported` | intracellular-water-mass | — | — |
| `getmeas:170` | `platform-exclusive` | `measure.value*10^unit` | `platform-exclusive` | withings-visceral-fat-index | unitless provider value to the dimensionless UCUM {score} annotation | The Grove FHIR contracts carry the Withings visceral-fat figure as the provider-scoped withings-visceral-fat-index profile, on the dimensionless UCUM {score} annotation because the API returns the value without a unit and it is a rating rather than a mass or an area. The code names the vendor, so the figure cannot be folded into a shared body-composition measurement, and no measurand, no mass, and no comparability with another vendor's visceral-fat figure is asserted. |
| `getmeas:174` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The consumed source shape (measure.value*10^unit) does not recover which body segment a value belongs to, and the shared model has no body-segment site; emitting a segment mass under whole-body fat-mass or muscle-mass semantics would be wrong, so conversion is refused rather than mislabeled. |
| `getmeas:175` | `intentionally-unsupported` | `measure.value*10^unit` | `intentionally-unsupported` | — | — | The consumed source shape (measure.value*10^unit) does not recover which body segment a value belongs to, and the shared model has no body-segment site; emitting a segment mass under whole-body fat-mass or muscle-mass semantics would be wrong, so conversion is refused rather than mislabeled. |
| `getmeas:196` | `supported` | `measure.value*10^unit` | `supported` | electrodermal-activity | — | — |

#### Mappings that require a complete source group

Some results are admitted only when every required provider field occurs in the same source group.

| Grouped source token | Required members | Measurement | Output discriminator | Rule |
| --- | --- | --- | --- | --- |
| `getmeas:9+10` | `getmeas:9`; `getmeas:10` | blood-pressure | single | Emit exactly one panel only when one type 9 value and one type 10 value occur in the same measure group; otherwise emit neither component as a normalized Observation. Use getmeas:9+10, not either member token, in the source-record identity preimage. |
