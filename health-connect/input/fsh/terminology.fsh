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

CodeSystem: HealthConnectMindfulnessSessionTypeCS
Id: health-connect-mindfulness-session-type
Title: "Health Connect Mindfulness Session Type"
Description: "The complete AndroidX Health Connect 1.1 MindfulnessSessionRecord type domain retained without reclassification."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #MINDFULNESS_SESSION_TYPE_UNKNOWN "Unknown" "A generic or otherwise unknown mindfulness session."
* #MINDFULNESS_SESSION_TYPE_MEDITATION "Meditation" "A meditation mindfulness session."
* #MINDFULNESS_SESSION_TYPE_BREATHING "Guided breathing" "A guided breathing mindfulness session."
* #MINDFULNESS_SESSION_TYPE_MUSIC "Music or soundscapes" "A music or soundscape mindfulness session."
* #MINDFULNESS_SESSION_TYPE_MOVEMENT "Movement" "A stretching or movement mindfulness session."
* #MINDFULNESS_SESSION_TYPE_UNGUIDED "Unguided" "An unguided mindfulness session."

ValueSet: HealthConnectMindfulnessSessionTypeVS
Id: health-connect-mindfulness-session-type
Title: "Health Connect Mindfulness Session Type"
Description: "Every exact AndroidX Health Connect 1.1 mindfulness-session type admitted by the adapter."
* ^experimental = false
* include codes from system HealthConnectMindfulnessSessionTypeCS

CodeSystem: HealthConnectVo2MaxMeasurementMethodCS
Id: health-connect-vo2-max-measurement-method
Title: "Health Connect VO2 Max Measurement Method"
Description: "The complete AndroidX Health Connect 1.1 Vo2MaxRecord measurement-method domain retained in Observation.method."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #MEASUREMENT_METHOD_OTHER "Other" "A method not represented by another AndroidX token."
* #MEASUREMENT_METHOD_METABOLIC_CART "Metabolic cart" "Measurement by metabolic cart."
* #MEASUREMENT_METHOD_HEART_RATE_RATIO "Heart-rate ratio" "Estimation from a heart-rate ratio."
* #MEASUREMENT_METHOD_COOPER_TEST "Cooper test" "Estimation from a Cooper test."
* #MEASUREMENT_METHOD_MULTISTAGE_FITNESS_TEST "Multistage fitness test" "Estimation from a multistage fitness test."
* #MEASUREMENT_METHOD_ROCKPORT_FITNESS_TEST "Rockport fitness test" "Estimation from a Rockport fitness test."

ValueSet: HealthConnectVo2MaxMeasurementMethodVS
Id: health-connect-vo2-max-measurement-method
Title: "Health Connect VO2 Max Measurement Method"
Description: "Every exact AndroidX Health Connect 1.1 VO2 max measurement method admitted by the adapter."
* ^experimental = false
* include codes from system HealthConnectVo2MaxMeasurementMethodCS

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

CodeSystem: HealthConnectMenstruationFlowCS
Id: health-connect-menstruation-flow
Title: "Health Connect Menstruation Flow"
Description: "Exact AndroidX MenstruationFlowRecord flow constants retained alongside the source-neutral Grove flow coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #FLOW_UNKNOWN "Unknown" "The record states no flow level."
* #FLOW_LIGHT "Light" "The flow was recorded as light."
* #FLOW_MEDIUM "Medium" "The flow was recorded as medium."
* #FLOW_HEAVY "Heavy" "The flow was recorded as heavy."

ValueSet: HealthConnectMenstruationFlowVS
Id: health-connect-menstruation-flow
Title: "Health Connect Menstruation Flow"
Description: "The complete AndroidX MenstruationFlowRecord flow domain admitted by Grove 0.6.0."
* ^experimental = false
* include codes from system HealthConnectMenstruationFlowCS

CodeSystem: HealthConnectOvulationTestResultCS
Id: health-connect-ovulation-test-result
Title: "Health Connect Ovulation Test Result"
Description: "Exact AndroidX OvulationTestRecord result constants retained alongside the source-neutral Grove result coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #RESULT_NEGATIVE "Negative" "The test did not indicate the fertile window."
* #RESULT_HIGH "High" "The test indicated the fertile window."
* #RESULT_POSITIVE "Positive" "The test detected a luteinizing-hormone surge."
* #RESULT_INCONCLUSIVE "Inconclusive" "The test produced no readable result."

ValueSet: HealthConnectOvulationTestResultVS
Id: health-connect-ovulation-test-result
Title: "Health Connect Ovulation Test Result"
Description: "The complete AndroidX OvulationTestRecord result domain admitted by Grove 0.6.0."
* ^experimental = false
* include codes from system HealthConnectOvulationTestResultCS

CodeSystem: HealthConnectSexualActivityProtectionCS
Id: health-connect-sexual-activity-protection
Title: "Health Connect Sexual Activity Protection"
Description: "Exact AndroidX SexualActivityRecord protection constants retained alongside the source-neutral Grove coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #PROTECTION_USED_UNKNOWN "Unknown" "The record states nothing about protection."
* #PROTECTION_USED_PROTECTED "Protected" "The record states that protection was used."
* #PROTECTION_USED_UNPROTECTED "Unprotected" "The record states that protection was not used."

ValueSet: HealthConnectSexualActivityProtectionVS
Id: health-connect-sexual-activity-protection
Title: "Health Connect Sexual Activity Protection"
Description: "The complete AndroidX SexualActivityRecord protection-use domain admitted by Grove 0.6.0."
* ^experimental = false
* include codes from system HealthConnectSexualActivityProtectionCS

CodeSystem: HealthConnectCervicalMucusAppearanceCS
Id: health-connect-cervical-mucus-appearance
Title: "Health Connect Cervical Mucus Appearance"
Description: "Exact AndroidX CervicalMucusRecord appearance constants retained alongside the source-neutral Grove quality coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #APPEARANCE_UNKNOWN "Unknown" "The record states no appearance."
* #APPEARANCE_DRY "Dry" "The appearance was recorded as dry."
* #APPEARANCE_STICKY "Sticky" "The appearance was recorded as sticky."
* #APPEARANCE_CREAMY "Creamy" "The appearance was recorded as creamy."
* #APPEARANCE_WATERY "Watery" "The appearance was recorded as watery."
* #APPEARANCE_EGG_WHITE "Egg white" "The appearance was recorded as egg white."
* #APPEARANCE_UNUSUAL "Unusual" "The appearance was recorded as unusual for the person."

ValueSet: HealthConnectCervicalMucusAppearanceVS
Id: health-connect-cervical-mucus-appearance
Title: "Health Connect Cervical Mucus Appearance"
Description: "The complete AndroidX CervicalMucusRecord appearance domain admitted by Grove 0.6.0."
* ^experimental = false
* include codes from system HealthConnectCervicalMucusAppearanceCS

CodeSystem: HealthConnectCervicalMucusSensationCS
Id: health-connect-cervical-mucus-sensation
Title: "Health Connect Cervical Mucus Sensation"
Description: "Exact AndroidX CervicalMucusRecord sensation constants retained alongside the source-neutral Grove sensation coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #SENSATION_LIGHT "Light" "The sensation was recorded as light."
* #SENSATION_MEDIUM "Medium" "The sensation was recorded as medium."
* #SENSATION_HEAVY "Heavy" "The sensation was recorded as heavy."

ValueSet: HealthConnectCervicalMucusSensationVS
Id: health-connect-cervical-mucus-sensation
Title: "Health Connect Cervical Mucus Sensation"
Description: "The non-UNKNOWN AndroidX CervicalMucusRecord sensation domain retained by Grove 0.6.0; UNKNOWN is represented by omission."
* ^experimental = false
* include codes from system HealthConnectCervicalMucusSensationCS

CodeSystem: HealthConnectExerciseTypeCS
Id: health-connect-exercise-type
Title: "Health Connect Exercise Type"
Description: "Exact AndroidX ExerciseSessionRecord exercise-type constants retained alongside the source-neutral Grove workout activity coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #EXERCISE_TYPE_BADMINTON "Badminton" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BADMINTON constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_BASEBALL "Baseball" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BASEBALL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_BASKETBALL "Basketball" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BASKETBALL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_BIKING "Biking" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BIKING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_BIKING_STATIONARY "Biking stationary" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BIKING_STATIONARY constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_BOOT_CAMP "Boot camp" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BOOT_CAMP constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_BOXING "Boxing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_BOXING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_CALISTHENICS "Calisthenics" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_CALISTHENICS constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_CRICKET "Cricket" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_CRICKET constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_DANCING "Dancing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_DANCING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ELLIPTICAL "Elliptical" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ELLIPTICAL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_EXERCISE_CLASS "Exercise class" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_EXERCISE_CLASS constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_FENCING "Fencing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_FENCING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_FOOTBALL_AMERICAN "Football american" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_FOOTBALL_AMERICAN constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_FOOTBALL_AUSTRALIAN "Football australian" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_FOOTBALL_AUSTRALIAN constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_FRISBEE_DISC "Frisbee disc" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_FRISBEE_DISC constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_GOLF "Golf" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_GOLF constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_GUIDED_BREATHING "Guided breathing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_GUIDED_BREATHING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_GYMNASTICS "Gymnastics" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_GYMNASTICS constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_HANDBALL "Handball" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_HANDBALL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING "High intensity interval training" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_HIKING "Hiking" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_HIKING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ICE_HOCKEY "Ice hockey" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ICE_HOCKEY constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ICE_SKATING "Ice skating" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ICE_SKATING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_MARTIAL_ARTS "Martial arts" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_MARTIAL_ARTS constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_OTHER_WORKOUT "Other workout" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_OTHER_WORKOUT constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_PADDLING "Paddling" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_PADDLING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_PARAGLIDING "Paragliding" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_PARAGLIDING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_PILATES "Pilates" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_PILATES constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_RACQUETBALL "Racquetball" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_RACQUETBALL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ROCK_CLIMBING "Rock climbing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ROCK_CLIMBING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ROLLER_HOCKEY "Roller hockey" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ROLLER_HOCKEY constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ROWING "Rowing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ROWING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_ROWING_MACHINE "Rowing machine" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_ROWING_MACHINE constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_RUGBY "Rugby" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_RUGBY constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_RUNNING "Running" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_RUNNING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_RUNNING_TREADMILL "Running treadmill" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_RUNNING_TREADMILL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SAILING "Sailing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SAILING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SCUBA_DIVING "Scuba diving" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SCUBA_DIVING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SKATING "Skating" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SKATING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SKIING "Skiing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SKIING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SNOWBOARDING "Snowboarding" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SNOWBOARDING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SNOWSHOEING "Snowshoeing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SNOWSHOEING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SOCCER "Soccer" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SOCCER constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SOFTBALL "Softball" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SOFTBALL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SQUASH "Squash" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SQUASH constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_STAIR_CLIMBING "Stair climbing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_STAIR_CLIMBING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_STAIR_CLIMBING_MACHINE "Stair climbing machine" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_STAIR_CLIMBING_MACHINE constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_STRENGTH_TRAINING "Strength training" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_STRENGTH_TRAINING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_STRETCHING "Stretching" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_STRETCHING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SURFING "Surfing" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SURFING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SWIMMING_OPEN_WATER "Swimming open water" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SWIMMING_OPEN_WATER constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_SWIMMING_POOL "Swimming pool" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_SWIMMING_POOL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_TABLE_TENNIS "Table tennis" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_TABLE_TENNIS constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_TENNIS "Tennis" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_TENNIS constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_VOLLEYBALL "Volleyball" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_VOLLEYBALL constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_WALKING "Walking" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_WALKING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_WATER_POLO "Water polo" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_WATER_POLO constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_WEIGHTLIFTING "Weightlifting" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_WEIGHTLIFTING constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_WHEELCHAIR "Wheelchair" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_WHEELCHAIR constant, retained as the exact source activity behind the shared Grove workout coding."
* #EXERCISE_TYPE_YOGA "Yoga" "The AndroidX ExerciseSessionRecord EXERCISE_TYPE_YOGA constant, retained as the exact source activity behind the shared Grove workout coding."

ValueSet: HealthConnectExerciseTypeVS
Id: health-connect-exercise-type
Title: "Health Connect Exercise Type"
Description: "The complete AndroidX ExerciseSessionRecord exercise-type domain admitted by Grove 0.6.0."
* ^experimental = false
* include codes from system HealthConnectExerciseTypeCS

CodeSystem: HealthConnectExerciseSegmentTypeCS
Id: health-connect-exercise-segment-type
Title: "Health Connect Exercise Segment Type"
Description: "Exact AndroidX ExerciseSegment type constants retained alongside the source-neutral Grove segment coding; EXERCISE_LAP names a lap, which Health Connect states structurally rather than as an enumeration."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #EXERCISE_SEGMENT_TYPE_ARM_CURL "Arm curl" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_ARM_CURL constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BACK_EXTENSION "Back extension" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BACK_EXTENSION constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BALL_SLAM "Ball slam" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BALL_SLAM constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BARBELL_SHOULDER_PRESS "Barbell shoulder press" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BARBELL_SHOULDER_PRESS constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BENCH_PRESS "Bench press" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BENCH_PRESS constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BENCH_SIT_UP "Bench sit up" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BENCH_SIT_UP constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BIKING "Biking" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BIKING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BIKING_STATIONARY "Biking stationary" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BIKING_STATIONARY constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_BURPEE "Burpee" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_BURPEE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_CRUNCH "Crunch" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_CRUNCH constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DEADLIFT "Deadlift" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DEADLIFT constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DOUBLE_ARM_TRICEPS_EXTENSION "Double arm triceps extension" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DOUBLE_ARM_TRICEPS_EXTENSION constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_LEFT_ARM "Dumbbell curl left arm" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_LEFT_ARM constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_RIGHT_ARM "Dumbbell curl right arm" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_RIGHT_ARM constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_FRONT_RAISE "Dumbbell front raise" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_FRONT_RAISE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_LATERAL_RAISE "Dumbbell lateral raise" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_LATERAL_RAISE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_ROW "Dumbbell row" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_ROW constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_LEFT_ARM "Dumbbell triceps extension left arm" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_LEFT_ARM constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_RIGHT_ARM "Dumbbell triceps extension right arm" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_RIGHT_ARM constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_TWO_ARM "Dumbbell triceps extension two arm" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_TWO_ARM constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_ELLIPTICAL "Elliptical" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_ELLIPTICAL constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_FORWARD_TWIST "Forward twist" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_FORWARD_TWIST constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_FRONT_RAISE "Front raise" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_FRONT_RAISE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING "High intensity interval training" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_HIP_THRUST "Hip thrust" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_HIP_THRUST constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_HULA_HOOP "Hula hoop" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_HULA_HOOP constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_JUMPING_JACK "Jumping jack" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_JUMPING_JACK constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_JUMP_ROPE "Jump rope" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_JUMP_ROPE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_KETTLEBELL_SWING "Kettlebell swing" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_KETTLEBELL_SWING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LATERAL_RAISE "Lateral raise" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LATERAL_RAISE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LAT_PULL_DOWN "Lat pull down" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LAT_PULL_DOWN constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LEG_CURL "Leg curl" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LEG_CURL constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LEG_EXTENSION "Leg extension" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LEG_EXTENSION constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LEG_PRESS "Leg press" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LEG_PRESS constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LEG_RAISE "Leg raise" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LEG_RAISE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_LUNGE "Lunge" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_LUNGE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_MOUNTAIN_CLIMBER "Mountain climber" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_MOUNTAIN_CLIMBER constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_OTHER_WORKOUT "Other workout" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_OTHER_WORKOUT constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_PAUSE "Pause" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_PAUSE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_PILATES "Pilates" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_PILATES constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_PLANK "Plank" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_PLANK constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_PULL_UP "Pull up" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_PULL_UP constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_PUNCH "Punch" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_PUNCH constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_REST "Rest" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_REST constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_ROWING_MACHINE "Rowing machine" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_ROWING_MACHINE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_RUNNING "Running" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_RUNNING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_RUNNING_TREADMILL "Running treadmill" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_RUNNING_TREADMILL constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SHOULDER_PRESS "Shoulder press" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SHOULDER_PRESS constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SINGLE_ARM_TRICEPS_EXTENSION "Single arm triceps extension" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SINGLE_ARM_TRICEPS_EXTENSION constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SIT_UP "Sit up" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SIT_UP constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SQUAT "Squat" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SQUAT constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING "Stair climbing" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING_MACHINE "Stair climbing machine" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING_MACHINE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_STRETCHING "Stretching" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_STRETCHING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_BACKSTROKE "Swimming backstroke" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_BACKSTROKE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_BREASTSTROKE "Swimming breaststroke" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_BREASTSTROKE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_BUTTERFLY "Swimming butterfly" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_BUTTERFLY constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_FREESTYLE "Swimming freestyle" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_FREESTYLE constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_MIXED "Swimming mixed" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_MIXED constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_OPEN_WATER "Swimming open water" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_OPEN_WATER constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_OTHER "Swimming other" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_OTHER constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_SWIMMING_POOL "Swimming pool" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_SWIMMING_POOL constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_UNKNOWN "Unknown" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_UNKNOWN constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_UPPER_TWIST "Upper twist" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_UPPER_TWIST constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_WALKING "Walking" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_WALKING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_WEIGHTLIFTING "Weightlifting" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_WEIGHTLIFTING constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_WHEELCHAIR "Wheelchair" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_WHEELCHAIR constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_SEGMENT_TYPE_YOGA "Yoga" "The AndroidX ExerciseSegment EXERCISE_SEGMENT_TYPE_YOGA constant, retained as the exact source segment behind the shared Grove segment coding."
* #EXERCISE_LAP "Exercise lap" "The AndroidX ExerciseSegment EXERCISE_LAP constant, retained as the exact source segment behind the shared Grove segment coding."

ValueSet: HealthConnectExerciseSegmentTypeVS
Id: health-connect-exercise-segment-type
Title: "Health Connect Exercise Segment Type"
Description: "The complete AndroidX ExerciseSegment type domain plus Grove's structural EXERCISE_LAP token admitted by Grove 0.6.0."
* ^experimental = false
* include codes from system HealthConnectExerciseSegmentTypeCS
