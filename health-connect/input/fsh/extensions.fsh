//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

Extension: HealthConnectRecordType
Id: health-connect-record-type
Title: "Health Connect Record Type"
Description: "Identifies the exact AndroidX Health Connect 1.1 Record class already read by the caller. It is source lineage, not a clinical result code, fetch instruction, or authorization grant."
Context: Observation
* value[x] only code
* valueCode 1..1
* valueCode from HealthConnectRecordTypeVS (required)

Extension: HealthConnectGlucoseMealContext
Id: health-connect-glucose-meal-context
Title: "Health Connect Glucose Meal Context"
Description: "The non-unknown relation-to-meal and meal-type context supplied by a Health Connect BloodGlucoseRecord. This source context does not replace the standard clinical result or specimen coding."
Context: Observation
* extension contains
    relationToMeal 0..1 MS and
    mealType 0..1 MS
* extension[relationToMeal].value[x] 1..1 MS
* extension[relationToMeal].value[x] only Coding
* extension[relationToMeal].valueCoding from HealthConnectRelationToMealVS (required)
* extension[mealType].value[x] 1..1 MS
* extension[mealType].value[x] only Coding
* extension[mealType].valueCoding from HealthConnectMealTypeVS (required)
* value[x] 0..0

Extension: HealthConnectSleepTitle
Id: health-connect-sleep-title
Title: "Health Connect Sleep Title"
Description: "The non-blank title supplied by a Health Connect SleepSessionRecord, represented only on the source-neutral sleep-duration summary Observation."
Context: Observation
* value[x] 1..1 MS
* value[x] only string

Extension: HealthConnectExerciseTitle
Id: health-connect-exercise-title
Title: "Health Connect Exercise Title"
Description: "The caller-supplied title of a Health Connect exercise session, which the shared workout profile has no element for."
Context: Observation
* value[x] 1..1 MS
* value[x] only string

Extension: HealthConnectMindfulnessSessionType
Id: health-connect-mindfulness-session-type
Title: "Health Connect Mindfulness Session Type"
Description: "The exact closed AndroidX Health Connect 1.1 mindfulness-session type, including UNKNOWN when that is the source value."
Context: Observation
* value[x] 1..1 MS
* value[x] only Coding
* valueCoding from HealthConnectMindfulnessSessionTypeVS (required)

Extension: HealthConnectMindfulnessTitle
Id: health-connect-mindfulness-title
Title: "Health Connect Mindfulness Title"
Description: "The non-blank title supplied by a Health Connect MindfulnessSessionRecord. Blank source strings are omitted."
Context: Observation
* value[x] 1..1 MS
* value[x] only string
