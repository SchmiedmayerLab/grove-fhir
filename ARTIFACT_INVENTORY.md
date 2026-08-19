<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Artifact inventory

This inventory records the contents of the combined Grove FHIR prototype at repository
commit [`6674807`](https://github.com/SchmiedmayerLab/grove-fhir/commit/66748077806a86cc85d20d437b7bda2147acae4d).
It is the starting point for the pre-1.0 package redesign, not a compatibility promise.

### Dispositions

| Disposition | Meaning |
|---|---|
| Candidate Mobile | Implemented by Grove Swift and under review for Mobile Data Exchange |
| Candidate Questionnaire | Implemented generic questionnaire exchange under review |
| Generated Platform Terminology | Source-platform vocabulary emitted by current Swift mappings |
| Experimental | Implementation or conformance evidence is incomplete |
| Excluded Image Annotation | Grove demonstration that will not enter the FHIR contract now |
| Evidence Pending | No implemented producer, consumer, or symmetric conversion establishes a contract |
| Illustrative Example | Hand-authored example; validation alone is not implementation evidence |
| Legacy Archive | Historical material excluded from the active contract |

Candidate means eligible for focused FHIR and implementation review. It does not mean
stable, clinically validated, or accepted into a released package.

### Contract direction

- Mobile Data Exchange is the first package boundary.
- Questionnaire Exchange follows as an independent package.
- Platform Terminology supports both without defining clinical meaning.
- SensorKit and raw batches remain experimental.
- Image annotation remains a Grove-local extensibility demonstration.
- Writers will emit only the redesigned contract. Legacy reads will be retained only
  where real stored data or downstream consumers establish a need.

### Canonical namespaces under review

| Namespace | Current use | Direction |
|---|---|---|
| `https://grovealliance.org/fhir/core` | Combined prototype package | Replace with functional package identities if the usage inventory permits |
| `https://grovealliance.org/fhir/platforms` | Platform terminology prototype | Retain or replace after terminology provenance review |
| `https://grovealliance.org/fhir/sid` | Source-record and device identifier systems | Review with the Mobile contract |
| Stanford and Spezi historical URLs | Reader compatibility | Preserve only evidence-backed migration paths |

Standard HL7, terminology, and vendor URLs referenced by these sources are not owned by
Grove. Before a stable release, the canonical host must serve every retained definition,
package, version history, and redirect over HTTPS.

### FHIR Shorthand inventory

The table below is checked against every top-level declaration in the active guides and
legacy archive. A source change must update its disposition in the same pull request.

<!-- fsh-inventory:start -->
| Source | Disposition | Kind | FSH name |
|---|---|---|---|
| `ig/input/fsh/profiles.fsh` | `candidate-mobile` | `Profile` | `GroveSensorDevice` |
| `ig/input/fsh/profiles.fsh` | `candidate-mobile` | `Profile` | `GroveGatewayDevice` |
| `ig/input/fsh/profiles.fsh` | `candidate-mobile` | `Profile` | `GroveMobileSensorObservation` |
| `ig/input/fsh/extensions.fsh` | `candidate-mobile` | `Extension` | `GroveInferredValue` |
| `ig/input/fsh/extensions.fsh` | `candidate-mobile` | `Extension` | `GroveRecordingMethod` |
| `ig/input/fsh/extensions.fsh` | `candidate-mobile` | `Extension` | `GroveSourceRecordId` |
| `ig/input/fsh/extensions.fsh` | `evidence-pending` | `Extension` | `GroveStudyRevision` |
| `ig/input/fsh/extensions.fsh` | `candidate-mobile` | `Extension` | `GrovePlatformMetadata` |
| `ig/input/fsh/extensions.fsh` | `experimental-questionnaire` | `Extension` | `GroveAutocomplete` |
| `ig/input/fsh/extensions.fsh` | `experimental-questionnaire` | `Extension` | `GroveAutocapitalize` |
| `ig/input/fsh/extensions.fsh` | `excluded-image-annotation` | `Extension` | `GroveAnnotateImageRegion` |
| `ig/input/fsh/questionnaires.fsh` | `candidate-questionnaire` | `Invariant` | `grove-que-media-text` |
| `ig/input/fsh/questionnaires.fsh` | `excluded-image-annotation` | `Invariant` | `grove-que-annotate-image` |
| `ig/input/fsh/questionnaires.fsh` | `candidate-questionnaire` | `Invariant` | `grove-qr-item-text` |
| `ig/input/fsh/questionnaires.fsh` | `experimental-questionnaire` | `Profile` | `GroveQuestionnaire` |
| `ig/input/fsh/questionnaires.fsh` | `candidate-questionnaire` | `Profile` | `GroveQuestionnaireResponse` |
| `ig/input/fsh/questionnaires.fsh` | `illustrative-questionnaire-example` | `Instance` | `GroveFollowUpQuestionnaireExample` |
| `ig/input/fsh/questionnaires.fsh` | `illustrative-questionnaire-example` | `Instance` | `GroveFollowUpQuestionnaireResponseExample` |
| `ig/input/fsh/terminology.fsh` | `candidate-mobile` | `CodeSystem` | `GroveDeviceVersionType` |
| `ig/input/fsh/terminology.fsh` | `candidate-mobile` | `CodeSystem` | `GroveRecordingMethodCS` |
| `ig/input/fsh/terminology.fsh` | `candidate-mobile` | `ValueSet` | `GroveRecordingMethodVS` |
| `ig/input/fsh/terminology.fsh` | `candidate-mobile` | `CodeSystem` | `GroveDeviceType` |
| `ig/input/fsh/terminology.fsh` | `candidate-mobile` | `ValueSet` | `GroveDeviceTypeVS` |
| `ig/input/fsh/terminology.fsh` | `experimental-sensorkit` | `CodeSystem` | `GroveSensorBatchFormatCS` |
| `ig/input/fsh/terminology.fsh` | `experimental-sensorkit` | `ValueSet` | `GroveSensorBatchFormatVS` |
| `ig/input/fsh/terminology.fsh` | `evidence-pending` | `ValueSet` | `GrovePlatformMetadataKeyVS` |
| `ig/input/fsh/terminology.fsh` | `excluded-image-annotation` | `CodeSystem` | `GroveQuestionnaireItemControl` |
| `ig/input/fsh/terminology.fsh` | `excluded-image-annotation` | `CodeSystem` | `GroveAnnotateImageColors` |
| `ig/input/fsh/terminology.fsh` | `excluded-image-annotation` | `ValueSet` | `GroveAnnotateImageColorsVS` |
| `ig/input/fsh/terminology.fsh` | `experimental-questionnaire` | `CodeSystem` | `GroveAutocompleteTokens` |
| `ig/input/fsh/terminology.fsh` | `experimental-questionnaire` | `ValueSet` | `GroveAutocompleteTokensVS` |
| `ig/input/fsh/terminology.fsh` | `experimental-questionnaire` | `CodeSystem` | `GroveAutocapitalizeCS` |
| `ig/input/fsh/terminology.fsh` | `experimental-questionnaire` | `ValueSet` | `GroveAutocapitalizeVS` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `CodeSystem` | `GroveSensorKitConcepts` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `CodeSystem` | `GroveSensorKitValues` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `Profile` | `GroveWearStateObservation` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `ValueSet` | `GroveWearStateVS` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `ValueSet` | `GroveWristSideVS` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `Profile` | `GroveVisitObservation` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `ValueSet` | `GroveVisitLocationCategoryVS` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `Profile` | `GroveDeviceUsageObservation` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `Profile` | `GroveSensorBatchDocument` |
| `ig/input/fsh/sensorkit.fsh` | `experimental-sensorkit` | `ValueSet` | `GroveSensorBatchTypeVS` |
| `ig/input/fsh/capabilities.fsh` | `evidence-pending` | `Instance` | `GroveDataReceiver` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `PolarH10SensorDevice` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `WorkoutGatewayDevice` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `GroveHeartRateObservationExample` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `GrovePatientExample` |
| `ig/input/fsh/examples.fsh` | `excluded-image-annotation` | `Instance` | `GroveQuestionnaireExample` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `GrovePassthroughDocumentExample` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `PhoneSensorDevice` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `PhoneGatewayDevice` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `GroveStepCountObservationExample` |
| `ig/input/fsh/examples.fsh` | `illustrative-mobile-example` | `Instance` | `GroveSleepObservationExample` |
| `ig/input/fsh/examples.fsh` | `experimental-sensorkit` | `Instance` | `GroveWearStateObservationExample` |
| `ig/input/fsh/examples.fsh` | `excluded-image-annotation` | `Instance` | `GroveQuestionnaireResponseExample` |
| `ig/input/fsh/examples.fsh` | `experimental-sensorkit` | `Instance` | `GroveVisitObservationExample` |
| `ig/input/fsh/examples.fsh` | `experimental-sensorkit` | `Instance` | `GroveDeviceUsageObservationExample` |
| `ig/input/fsh/examples.fsh` | `experimental-sensorkit` | `Instance` | `GroveSensorBatchDocumentExample` |
| `ig/input/fsh/examples.fsh` | `evidence-pending` | `Instance` | `AndroidSensorDevice` |
| `ig/input/fsh/examples.fsh` | `evidence-pending` | `Instance` | `AndroidGatewayDevice` |
| `ig/input/fsh/examples.fsh` | `evidence-pending` | `Instance` | `GroveHealthConnectStepCountExample` |
| `platforms/input/fsh/key-spaces.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthKitSampleTypeCS` |
| `platforms/input/fsh/key-spaces.fsh` | `generated-platform-terminology` | `ValueSet` | `HealthKitSampleTypeVS` |
| `platforms/input/fsh/key-spaces.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthKitMetadataKeyCS` |
| `platforms/input/fsh/key-spaces.fsh` | `generated-platform-terminology` | `ValueSet` | `HealthKitMetadataKeyVS` |
| `platforms/input/fsh/key-spaces.fsh` | `evidence-pending` | `CodeSystem` | `HealthConnectMetadataKeyCS` |
| `platforms/input/fsh/key-spaces.fsh` | `evidence-pending` | `ValueSet` | `HealthConnectMetadataKeyVS` |
| `platforms/input/fsh/key-spaces.fsh` | `evidence-pending` | `CodeSystem` | `HealthConnectRecordTypeCS` |
| `platforms/input/fsh/key-spaces.fsh` | `evidence-pending` | `ValueSet` | `HealthConnectRecordTypeVS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitAppleEcgAlgorithmVersionCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitAppleWalkingSteadinessClassificationCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitBloodGlucoseMealTimeCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitBodyTemperatureSensorLocationCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueAppetiteChangesCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueAppleStandHourCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueAppleWalkingSteadinessEventCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueCervicalMucusQualityCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueContraceptiveCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueEnvironmentalAudioExposureEventCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueHeadphoneAudioExposureEventCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueLowCardioFitnessEventCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueMenstrualFlowCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueOvulationTestResultCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValuePregnancyTestResultCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValuePresenceCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueProgesteroneTestResultCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueSeverityCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueSleepAnalysisCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCategoryValueVaginalBleedingCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitCyclingFunctionalThresholdPowerTestTypeCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitDevicePlacementSideCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitElectrocardiogramClassificationCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitElectrocardiogramSymptomsStatusCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitHeartRateMotionContextCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitHeartRateRecoveryTestTypeCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitHeartRateSensorLocationCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitInsulinDeliveryReasonCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitPhysicalEffortEstimationTypeCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitStateOfMindAssociationCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitStateOfMindKindCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitStateOfMindLabelCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitStateOfMindValenceClassificationCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitSwimmingStrokeStyleCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitUserMotionContextCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitVo2MaxTestTypeCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitWaterSalinityCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitWeatherConditionCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitWorkoutSwimmingLocationTypeCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitElectrocardiogramPropertyCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitStateOfMindPropertyCS` |
| `platforms/input/fsh/generated-healthkit-values.fsh` | `generated-platform-terminology` | `CodeSystem` | `HealthkitWorkoutActivityTypeCS` |
| `platforms/input/fsh/sensorkit-sample-type.fsh` | `experimental-sensorkit` | `CodeSystem` | `GroveSensorKitSampleType` |
| `platforms/input/fsh/sensorkit-sample-type.fsh` | `experimental-sensorkit` | `ValueSet` | `GroveSensorKitSampleTypeVS` |
| `archive/v0-healthkit-shaped/input/fsh/examples.fsh` | `legacy-archive` | `Instance` | `GroveHeartRateObservationExample` |
| `archive/v0-healthkit-shaped/input/fsh/examples.fsh` | `legacy-archive` | `Instance` | `GrovePatientExample` |
| `archive/v0-healthkit-shaped/input/fsh/examples.fsh` | `legacy-archive` | `Instance` | `GroveQuestionnaireExample` |
| `archive/v0-healthkit-shaped/input/fsh/observation-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDevice` |
| `archive/v0-healthkit-shaped/input/fsh/observation-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevision` |
| `archive/v0-healthkit-shaped/input/fsh/observation-extensions.fsh` | `legacy-archive` | `Extension` | `GroveHealthKitMetadata` |
| `archive/v0-healthkit-shaped/input/fsh/observation-extensions.fsh` | `legacy-archive` | `Extension` | `GroveAbsoluteTimeRangeStart` |
| `archive/v0-healthkit-shaped/input/fsh/observation-extensions.fsh` | `legacy-archive` | `Extension` | `GroveAbsoluteTimeRangeEnd` |
| `archive/v0-healthkit-shaped/input/fsh/observation-extensions.fsh` | `legacy-archive` | `Extension` | `GroveHealthKitSampleId` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `Extension` | `GroveValidationText` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `Extension` | `GroveIosKeyboardType` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `Extension` | `GroveIosTextContentType` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `Extension` | `GroveIosAutocapitalizationType` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `Extension` | `GroveAnnotateImageInputImage` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `Extension` | `GroveAnnotateImageRegion` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `CodeSystem` | `GroveQuestionnaireItemControlCS` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `CodeSystem` | `GroveAnnotateImageColorsCS` |
| `archive/v0-healthkit-shaped/input/fsh/questionnaire-extensions.fsh` | `legacy-archive` | `ValueSet` | `GroveAnnotateImageColorsVS` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceName` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceManufacturer` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceModel` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceHardwareVersion` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceFirmwareVersion` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceSoftwareVersion` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceLocalIdentifier` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceDeviceUdiDeviceIdentifier` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevisionSource` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevisionSourceName` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevisionSourceBundleIdentifier` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevisionVersion` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevisionProductType` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveSourceRevisionOSVersion` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveMetadataWasUserEntered` |
| `archive/v0-healthkit-shaped/input/fsh/sub-extensions.fsh` | `legacy-archive` | `Extension` | `GroveMetadataHeartRateMotionContext` |
<!-- fsh-inventory:end -->

### Implementation evidence

Candidate implementation evidence is under review in Grove Swift and will be pinned to a
public commit before a package is released. The review found Swift producers and focused
tests for the Mobile Observation envelope,
recording and gateway devices, source identity, recording method, and typed HealthKit
metadata. Questionnaire import and export and QuestionnaireResponse export also exist;
FHIR QuestionnaireResponse import has not been established.

That branch does not yet establish the full prototype package as a reusable contract.
There is no Grove receiver implementation for the CapabilityStatement, no Grove Swift
Health Connect implementation, no production FHIR `Provenance` producer, and incomplete
conformance coverage for SensorKit. Hand-authored examples are illustrative only.
