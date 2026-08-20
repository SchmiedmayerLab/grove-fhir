//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: HealthKitMetadataKeyCS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "HealthKit metadata keys retained by Grove FHIR HealthKit 0.1.0 after standard FHIR mappings have been applied."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #HKMetadataKeyHeartRateMotionContext "Heart Rate Motion Context" "The HealthKit metadata key whose NSNumber value is mapped to a bounded motion-context code."

ValueSet: HealthKitMetadataKeyVS
Id: healthkit-metadata-key
Title: "HealthKit Metadata Keys"
Description: "The HealthKit 0.1.0 allowlist of metadata keys represented by named Observation component slices."
* ^experimental = false
* include codes from system HealthKitMetadataKeyCS

CodeSystem: HealthKitHeartRateMotionContextCS
Id: healthkit-heart-rate-motion-context
Title: "HealthKit Heart Rate Motion Context"
Description: "Adapter codes for the HKHeartRateMotionContext raw values retained by Grove FHIR HealthKit 0.1.0. The mapping to HealthKit source cases is documented separately."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "HealthKit API identifiers and type names originate from Apple Inc. and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Apple material."
* #not-set "Not Set" "The adapter code for HealthKit raw NSNumber value 0."
* #sedentary "Sedentary" "The adapter code for HealthKit raw NSNumber value 1."
* #active "Active" "The adapter code for HealthKit raw NSNumber value 2."

ValueSet: HealthKitHeartRateMotionContextVS
Id: healthkit-heart-rate-motion-context
Title: "HealthKit Heart Rate Motion Context"
Description: "Motion contexts permitted by the HealthKit 0.1.0 heart-rate metadata mapping."
* ^experimental = false
* include codes from system HealthKitHeartRateMotionContextCS
