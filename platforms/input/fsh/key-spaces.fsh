//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// Open key spaces. Apple and Google own these namespaces and extend them with every
// release, and HealthKit additionally accepts arbitrary third-party keys, so these are
// fragment systems: a code absent from the listing below is still a valid code. The
// enumerated systems are generated instead — see generated-healthkit-values.fsh.

CodeSystem: HealthKitSampleTypeCS
Id: healthkit-sample-type
Title: "HealthKit Sample Types"
Description: """
HealthKit sample-type identifiers, as their raw string values
(`HKQuantityTypeIdentifierStepCount`, `HKCategoryTypeIdentifierSleepAnalysis`,
`HKDataTypeStateOfMind`, …). This coding may be written alongside a clinical coding to
retain the source platform's data type.

A fragment: Apple adds sample types with every release.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-sample-type"
* ^valueSet = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-sample-type"
* ^experimental = false
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
Description: "All HealthKit sample-type identifiers. Bind extensibly: the system is a fragment."
* ^url = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-sample-type"
* ^experimental = false
* include codes from system HealthKitSampleTypeCS


CodeSystem: HealthKitMetadataKeyCS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: """
HealthKit metadata keys, as their raw string values. Used as the `key` coding of the
core guide's platform-metadata entry when a source key/value pair has no more specific
FHIR representation.

A fragment: HealthKit accepts arbitrary third-party keys. The codes are the raw values,
not the Swift constant names. Grove writes the raw value, and tests pin each listed code
to the value returned by HealthKit.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/healthkit-metadata-key"
* ^valueSet = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-metadata-key"
* ^experimental = false
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
* #HKTimeZone "Time Zone" "Routed to the standard timezone extension on effective[x]; never a metadata entry."
* #HKVO2MaxTestType "VO2 Max Test Type"
* #HKVO2MaxValue "VO2 Max Value"
* #HKWasUserEntered "Was User Entered" "Routed to the core guide's recording-method extension; never a metadata entry."
* #HKWeatherCondition "Weather Condition"
* #HKWeatherHumidity "Weather Humidity"
* #HKWeatherTemperature "Weather Temperature"

ValueSet: HealthKitMetadataKeyVS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "All published HealthKit metadata keys. Bind extensibly: HealthKit accepts arbitrary third-party keys."
* ^url = "https://grovealliance.org/fhir/platforms/ValueSet/healthkit-metadata-key"
* ^experimental = false
* include codes from system HealthKitMetadataKeyCS


CodeSystem: HealthConnectMetadataKeyCS
Id: health-connect-metadata-key
Title: "Health Connect Metadata Keys"
Description: """
Android Health Connect metadata fields, named as in the Health Connect API. A fragment:
the field set grows with the platform.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/health-connect-metadata-key"
* ^valueSet = "https://grovealliance.org/fhir/platforms/ValueSet/health-connect-metadata-key"
* ^experimental = false
* ^caseSensitive = true
* ^content = #fragment
* #clientRecordId "Client Record ID"
* #clientRecordVersion "Client Record Version"

ValueSet: HealthConnectMetadataKeyVS
Id: health-connect-metadata-key
Title: "Health Connect Metadata Keys"
Description: "All published Health Connect metadata fields. Bind extensibly: the field set grows with the platform."
* ^url = "https://grovealliance.org/fhir/platforms/ValueSet/health-connect-metadata-key"
* ^experimental = false
* include codes from system HealthConnectMetadataKeyCS


CodeSystem: HealthConnectRecordTypeCS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: """
Android Health Connect record classes, named as in the Health Connect API
(`StepsRecord`, `HeartRateRecord`, …) — the Android counterpart of HealthKit's
sample-type identifiers, and written into `Observation.code` for the same reason: the
platform class says which pipeline produced the number.

A fragment: the record set grows with the platform.
"""
* ^url = "https://grovealliance.org/fhir/platforms/CodeSystem/health-connect-record-type"
* ^experimental = false
* ^caseSensitive = true
* ^content = #fragment
* #StepsRecord "Steps"
* #HeartRateRecord "Heart Rate"
* #SleepSessionRecord "Sleep Session"


ValueSet: HealthConnectRecordTypeVS
Id: health-connect-record-type
Title: "Health Connect Record Types"
Description: "All Health Connect record classes."
* ^experimental = false
* include codes from system HealthConnectRecordTypeCS
