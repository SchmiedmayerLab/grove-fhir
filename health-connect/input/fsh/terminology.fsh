//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: HealthConnectSleepStageCS
Id: health-connect-sleep-stage
Title: "Health Connect Sleep Stage"
Description: "Exact AndroidX Health Connect 1.1 SleepSessionRecord stage tokens retained alongside the source-neutral Grove sleep-stage coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #STAGE_TYPE_UNKNOWN "Unknown" "Health Connect stage type unknown."
* #STAGE_TYPE_AWAKE "Awake" "Health Connect stage type awake."
* #STAGE_TYPE_SLEEPING "Sleeping" "Health Connect reports sleep without a more specific stage."
* #STAGE_TYPE_OUT_OF_BED "Out of bed" "Health Connect reports that the person was out of bed."
* #STAGE_TYPE_LIGHT "Light sleep" "Health Connect reports light sleep."
* #STAGE_TYPE_DEEP "Deep sleep" "Health Connect reports deep sleep."
* #STAGE_TYPE_REM "REM sleep" "Health Connect reports REM sleep."
* #STAGE_TYPE_AWAKE_IN_BED "Awake in bed" "Health Connect reports awake in bed."

ValueSet: HealthConnectSleepStageVS
Id: health-connect-sleep-stage
Title: "Health Connect Sleep Stage"
Description: "Exact source stage tokens admitted as the second coding of a Health Connect sleep-stage result."
* ^experimental = false
* include codes from system HealthConnectSleepStageCS

CodeSystem: HealthConnectRelationToMealCS
Id: health-connect-relation-to-meal
Title: "Health Connect Relation to Meal"
Description: "Non-unknown AndroidX Health Connect 1.1 relation-to-meal tokens retained in the glucose meal-context extension."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #RELATION_TO_MEAL_GENERAL "General" "The glucose result has a general relation to a meal."
* #RELATION_TO_MEAL_FASTING "Fasting" "The glucose result was recorded in a fasting context."
* #RELATION_TO_MEAL_BEFORE_MEAL "Before meal" "The glucose result was recorded before a meal."
* #RELATION_TO_MEAL_AFTER_MEAL "After meal" "The glucose result was recorded after a meal."

ValueSet: HealthConnectRelationToMealVS
Id: health-connect-relation-to-meal
Title: "Health Connect Relation to Meal"
Description: "Health Connect relation-to-meal values retained by the adapter. Unknown is omitted."
* ^experimental = false
* include codes from system HealthConnectRelationToMealCS

CodeSystem: HealthConnectMealTypeCS
Id: health-connect-meal-type
Title: "Health Connect Meal Type"
Description: "Non-unknown AndroidX Health Connect 1.1 meal-type tokens retained in the glucose meal-context extension."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #MEAL_TYPE_BREAKFAST "Breakfast" "The meal is breakfast."
* #MEAL_TYPE_LUNCH "Lunch" "The meal is lunch."
* #MEAL_TYPE_DINNER "Dinner" "The meal is dinner."
* #MEAL_TYPE_SNACK "Snack" "The meal is a snack."

ValueSet: HealthConnectMealTypeVS
Id: health-connect-meal-type
Title: "Health Connect Meal Type"
Description: "Health Connect meal types retained by the adapter. Unknown is omitted."
* ^experimental = false
* include codes from system HealthConnectMealTypeCS
