//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

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
