//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// HealthKit identifier spaces used by the Grove Swift conversion. These systems are
// fragments because HealthKit adds identifiers and accepts third-party metadata keys.

CodeSystem: HealthKitSampleTypeCS
Id: healthkit-sample-type
Title: "HealthKit Sample Types"
Description: """
HealthKit sample-type identifiers preserved by the Grove Swift conversion. The codes
are raw HealthKit identifier strings. This Grove-published fragment is not an Apple
terminology publication.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-sample-type"
* ^valueSet = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-sample-type"
* ^copyright = "HealthKit identifiers originate in Apple SDK declarations. Apple and HealthKit are trademarks of Apple Inc. The repository's MIT license does not grant rights in Apple material."
* ^experimental = true
* ^caseSensitive = true
* ^content = #fragment
* #HKQuantityTypeIdentifierStepCount "Step Count"
* #HKQuantityTypeIdentifierHeartRate "Heart Rate"
* #HKCategoryTypeIdentifierSleepAnalysis "Sleep Analysis"
* #HKDataTypeIdentifierElectrocardiogram "Electrocardiogram"
* #HKDataTypeStateOfMind "State of Mind"

ValueSet: HealthKitSampleTypeVS
Id: healthkit-sample-type
Title: "HealthKit Sample Types"
Description: "HealthKit sample-type identifiers included in this preview. Bind extensibly: the system is a fragment."
* ^url = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-sample-type"
* ^experimental = true
* include codes from system HealthKitSampleTypeCS


CodeSystem: HealthKitMetadataKeyCS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: """
HealthKit metadata keys preserved by the Grove Swift conversion. The codes are raw
HealthKit key strings. This Grove-published fragment is not an Apple terminology
publication and does not assign clinical meaning to the keys.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-metadata-key"
* ^valueSet = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-metadata-key"
* ^copyright = "HealthKit identifiers originate in Apple SDK declarations. Apple and HealthKit are trademarks of Apple Inc. The repository's MIT license does not grant rights in Apple material."
* ^experimental = true
* ^caseSensitive = true
* ^content = #fragment
* #HKAlpineSlopeGrade "Alpine Slope Grade"
* #HKAverageMETs "Average METs"
* #HKAverageSpeed "Average Speed"
* #HKBloodGlucoseMealTime "Blood Glucose Meal Time"
* #HKBodyTemperatureSensorLocation "Body Temperature Sensor Location"
* #HKCrossTrainerDistance "Cross Trainer Distance"
* #HKCyclingCyclingFunctionalThresholdPowerTestType "Cycling Functional Threshold Power Test Type" "The doubled word is Apple's; the raw value really is spelled this way."
* #HKElevationAscended "Elevation Ascended"
* #HKElevationDescended "Elevation Descended"
* #HKExternalUUID "External UUID"
* #HKFitnessMachineDuration "Fitness Machine Duration"
* #HKHeartRateEventThreshold "Heart Rate Event Threshold"
* #HKHeartRateSensorLocation "Heart Rate Sensor Location"
* #HKIndoorBikeDistance "Indoor Bike Distance"
* #HKInsulinDeliveryReason "Insulin Delivery Reason"
* #HKLowCardioFitnessEventThreshold "Low Cardio Fitness Event Threshold"
* #HKMaximumSpeed "Maximum Speed"
* #HKMenstrualCycleStart "Menstrual Cycle Start"
* #HKMetadataKeyAppleECGAlgorithmVersion "Apple ECG Algorithm Version"
* #HKMetadataKeyAudioExposureDuration "Audio Exposure Duration"
* #HKMetadataKeyAudioExposureLevel "Audio Exposure Level"
* #HKMetadataKeyBarometricPressure "Barometric Pressure"
* #HKMetadataKeyDevicePlacementSide "Device Placement Side"
* #HKMetadataKeyHeadphoneGain "Headphone Gain"
* #HKMetadataKeyHeartRateMotionContext "Heart Rate Motion Context"
* #HKMetadataKeyHeartRateRecoveryActivityDuration "Heart Rate Recovery Activity Duration"
* #HKMetadataKeyHeartRateRecoveryMaxObservedRecoveryHeartRate "Heart Rate Recovery Max Observed Recovery Heart Rate"
* #HKMetadataKeyHeartRateRecoveryTestType "Heart Rate Recovery Test Type"
* #HKMetadataKeyMaximumLightIntensity "Maximum Light Intensity"
* #HKMetadataKeySessionEstimate "Session Estimate"
* #HKMetadataKeyUserMotionContext "User Motion Context"
* #HKMetadataKeyWaterSalinity "Water Salinity"
* #HKPhysicalEffortEstimationType "Physical Effort Estimation Type"
* #HKSexualActivityProtectionUsed "Sexual Activity: Protection Used"
* #HKSwimmingLocationType "Swimming Location Type"
* #HKSwimmingStrokeStyle "Swimming Stroke Style"
* #HKTimeZone "Time Zone"
* #HKVO2MaxTestType "VO2 Max Test Type"
* #HKVO2MaxValue "VO2 Max Value"
* #HKWasUserEntered "Was User Entered"
* #HKWeatherCondition "Weather Condition"
* #HKWeatherHumidity "Weather Humidity"
* #HKWeatherTemperature "Weather Temperature"

ValueSet: HealthKitMetadataKeyVS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "HealthKit metadata keys included in this preview. Bind extensibly: HealthKit accepts arbitrary third-party keys."
* ^url = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-metadata-key"
* ^experimental = true
* include codes from system HealthKitMetadataKeyCS
