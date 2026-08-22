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

CodeSystem: HealthConnectMenstruationFlowCS
Id: health-connect-menstruation-flow
Title: "Health Connect Menstruation Flow"
Description: "Exact AndroidX MenstruationFlowRecord flow constants retained alongside the source-neutral Grove flow coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #FLOW_UNKNOWN "Unknown"
* #FLOW_LIGHT "Light"
* #FLOW_MEDIUM "Medium"
* #FLOW_HEAVY "Heavy"

CodeSystem: HealthConnectOvulationTestResultCS
Id: health-connect-ovulation-test-result
Title: "Health Connect Ovulation Test Result"
Description: "Exact AndroidX OvulationTestRecord result constants retained alongside the source-neutral Grove result coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #RESULT_NEGATIVE "Negative"
* #RESULT_HIGH "High"
* #RESULT_INCONCLUSIVE "Inconclusive"

CodeSystem: HealthConnectSexualActivityProtectionCS
Id: health-connect-sexual-activity-protection
Title: "Health Connect Sexual Activity Protection"
Description: "Exact AndroidX SexualActivityRecord protection constants retained alongside the source-neutral Grove coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #PROTECTION_USED_UNKNOWN "Unknown"
* #PROTECTION_USED_PROTECTED "Protected"

CodeSystem: HealthConnectCervicalMucusAppearanceCS
Id: health-connect-cervical-mucus-appearance
Title: "Health Connect Cervical Mucus Appearance"
Description: "Exact AndroidX CervicalMucusRecord appearance constants retained alongside the source-neutral Grove quality coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #APPEARANCE_UNKNOWN "Unknown"
* #APPEARANCE_DRY "Dry"
* #APPEARANCE_STICKY "Sticky"
* #APPEARANCE_CREAMY "Creamy"
* #APPEARANCE_WATERY "Watery"
* #APPEARANCE_EGG_WHITE "Egg white"
* #APPEARANCE_UNUSUAL "Unusual"

CodeSystem: HealthConnectCervicalMucusSensationCS
Id: health-connect-cervical-mucus-sensation
Title: "Health Connect Cervical Mucus Sensation"
Description: "Exact AndroidX CervicalMucusRecord sensation constants retained alongside the source-neutral Grove sensation coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #SENSATION_LIGHT "Light"
* #SENSATION_MEDIUM "Medium"
* #SENSATION_HEAVY "Heavy"

CodeSystem: HealthConnectExerciseTypeCS
Id: health-connect-exercise-type
Title: "Health Connect Exercise Type"
Description: "Exact AndroidX ExerciseSessionRecord exercise-type constants retained alongside the source-neutral Grove workout activity coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #EXERCISE_TYPE_BADMINTON "Badminton"
* #EXERCISE_TYPE_BASEBALL "Baseball"
* #EXERCISE_TYPE_BASKETBALL "Basketball"
* #EXERCISE_TYPE_BIKING "Biking"
* #EXERCISE_TYPE_BIKING_STATIONARY "Biking stationary"
* #EXERCISE_TYPE_BOOT_CAMP "Boot camp"
* #EXERCISE_TYPE_BOXING "Boxing"
* #EXERCISE_TYPE_CALISTHENICS "Calisthenics"
* #EXERCISE_TYPE_CRICKET "Cricket"
* #EXERCISE_TYPE_DANCING "Dancing"
* #EXERCISE_TYPE_ELLIPTICAL "Elliptical"
* #EXERCISE_TYPE_EXERCISE_CLASS "Exercise class"
* #EXERCISE_TYPE_FENCING "Fencing"
* #EXERCISE_TYPE_FOOTBALL_AMERICAN "Football american"
* #EXERCISE_TYPE_FOOTBALL_AUSTRALIAN "Football australian"
* #EXERCISE_TYPE_FRISBEE_DISC "Frisbee disc"
* #EXERCISE_TYPE_GOLF "Golf"
* #EXERCISE_TYPE_GUIDED_BREATHING "Guided breathing"
* #EXERCISE_TYPE_GYMNASTICS "Gymnastics"
* #EXERCISE_TYPE_HANDBALL "Handball"
* #EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING "High intensity interval training"
* #EXERCISE_TYPE_HIKING "Hiking"
* #EXERCISE_TYPE_ICE_HOCKEY "Ice hockey"
* #EXERCISE_TYPE_ICE_SKATING "Ice skating"
* #EXERCISE_TYPE_MARTIAL_ARTS "Martial arts"
* #EXERCISE_TYPE_OTHER_WORKOUT "Other workout"
* #EXERCISE_TYPE_PADDLING "Paddling"
* #EXERCISE_TYPE_PARAGLIDING "Paragliding"
* #EXERCISE_TYPE_PILATES "Pilates"
* #EXERCISE_TYPE_RACQUETBALL "Racquetball"
* #EXERCISE_TYPE_ROCK_CLIMBING "Rock climbing"
* #EXERCISE_TYPE_ROLLER_HOCKEY "Roller hockey"
* #EXERCISE_TYPE_ROWING "Rowing"
* #EXERCISE_TYPE_ROWING_MACHINE "Rowing machine"
* #EXERCISE_TYPE_RUGBY "Rugby"
* #EXERCISE_TYPE_RUNNING "Running"
* #EXERCISE_TYPE_RUNNING_TREADMILL "Running treadmill"
* #EXERCISE_TYPE_SAILING "Sailing"
* #EXERCISE_TYPE_SCUBA_DIVING "Scuba diving"
* #EXERCISE_TYPE_SKATING "Skating"
* #EXERCISE_TYPE_SKIING "Skiing"
* #EXERCISE_TYPE_SNOWBOARDING "Snowboarding"
* #EXERCISE_TYPE_SNOWSHOEING "Snowshoeing"
* #EXERCISE_TYPE_SOCCER "Soccer"
* #EXERCISE_TYPE_SOFTBALL "Softball"
* #EXERCISE_TYPE_SQUASH "Squash"
* #EXERCISE_TYPE_STAIR_CLIMBING "Stair climbing"
* #EXERCISE_TYPE_STAIR_CLIMBING_MACHINE "Stair climbing machine"
* #EXERCISE_TYPE_STRENGTH_TRAINING "Strength training"
* #EXERCISE_TYPE_STRETCHING "Stretching"
* #EXERCISE_TYPE_SURFING "Surfing"
* #EXERCISE_TYPE_SWIMMING_OPEN_WATER "Swimming open water"
* #EXERCISE_TYPE_SWIMMING_POOL "Swimming pool"
* #EXERCISE_TYPE_TABLE_TENNIS "Table tennis"
* #EXERCISE_TYPE_TENNIS "Tennis"
* #EXERCISE_TYPE_VOLLEYBALL "Volleyball"
* #EXERCISE_TYPE_WALKING "Walking"
* #EXERCISE_TYPE_WATER_POLO "Water polo"
* #EXERCISE_TYPE_WEIGHTLIFTING "Weightlifting"
* #EXERCISE_TYPE_WHEELCHAIR "Wheelchair"
* #EXERCISE_TYPE_YOGA "Yoga"

CodeSystem: HealthConnectExerciseSegmentTypeCS
Id: health-connect-exercise-segment-type
Title: "Health Connect Exercise Segment Type"
Description: "Exact AndroidX ExerciseSegment type constants retained alongside the source-neutral Grove segment coding; EXERCISE_LAP names a lap, which Health Connect states structurally rather than as an enumeration."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* ^copyright = "AndroidX Health Connect API identifiers and type names originate from Google LLC and are used here only to identify source API concepts for interoperability. The MIT license applies to Grove-authored definitions; it does not grant rights in Google material."
* #EXERCISE_SEGMENT_TYPE_ARM_CURL "Arm curl"
* #EXERCISE_SEGMENT_TYPE_BACK_EXTENSION "Back extension"
* #EXERCISE_SEGMENT_TYPE_BALL_SLAM "Ball slam"
* #EXERCISE_SEGMENT_TYPE_BARBELL_SHOULDER_PRESS "Barbell shoulder press"
* #EXERCISE_SEGMENT_TYPE_BENCH_PRESS "Bench press"
* #EXERCISE_SEGMENT_TYPE_BENCH_SIT_UP "Bench sit up"
* #EXERCISE_SEGMENT_TYPE_BIKING "Biking"
* #EXERCISE_SEGMENT_TYPE_BIKING_STATIONARY "Biking stationary"
* #EXERCISE_SEGMENT_TYPE_BURPEE "Burpee"
* #EXERCISE_SEGMENT_TYPE_CRUNCH "Crunch"
* #EXERCISE_SEGMENT_TYPE_DEADLIFT "Deadlift"
* #EXERCISE_SEGMENT_TYPE_DOUBLE_ARM_TRICEPS_EXTENSION "Double arm triceps extension"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_LEFT_ARM "Dumbbell curl left arm"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_RIGHT_ARM "Dumbbell curl right arm"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_FRONT_RAISE "Dumbbell front raise"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_LATERAL_RAISE "Dumbbell lateral raise"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_ROW "Dumbbell row"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_LEFT_ARM "Dumbbell triceps extension left arm"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_RIGHT_ARM "Dumbbell triceps extension right arm"
* #EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_TWO_ARM "Dumbbell triceps extension two arm"
* #EXERCISE_SEGMENT_TYPE_ELLIPTICAL "Elliptical"
* #EXERCISE_SEGMENT_TYPE_FORWARD_TWIST "Forward twist"
* #EXERCISE_SEGMENT_TYPE_FRONT_RAISE "Front raise"
* #EXERCISE_SEGMENT_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING "High intensity interval training"
* #EXERCISE_SEGMENT_TYPE_HIP_THRUST "Hip thrust"
* #EXERCISE_SEGMENT_TYPE_HULA_HOOP "Hula hoop"
* #EXERCISE_SEGMENT_TYPE_JUMPING_JACK "Jumping jack"
* #EXERCISE_SEGMENT_TYPE_JUMP_ROPE "Jump rope"
* #EXERCISE_SEGMENT_TYPE_KETTLEBELL_SWING "Kettlebell swing"
* #EXERCISE_SEGMENT_TYPE_LATERAL_RAISE "Lateral raise"
* #EXERCISE_SEGMENT_TYPE_LAT_PULL_DOWN "Lat pull down"
* #EXERCISE_SEGMENT_TYPE_LEG_CURL "Leg curl"
* #EXERCISE_SEGMENT_TYPE_LEG_EXTENSION "Leg extension"
* #EXERCISE_SEGMENT_TYPE_LEG_PRESS "Leg press"
* #EXERCISE_SEGMENT_TYPE_LEG_RAISE "Leg raise"
* #EXERCISE_SEGMENT_TYPE_LUNGE "Lunge"
* #EXERCISE_SEGMENT_TYPE_MOUNTAIN_CLIMBER "Mountain climber"
* #EXERCISE_SEGMENT_TYPE_OTHER_WORKOUT "Other workout"
* #EXERCISE_SEGMENT_TYPE_PAUSE "Pause"
* #EXERCISE_SEGMENT_TYPE_PILATES "Pilates"
* #EXERCISE_SEGMENT_TYPE_PLANK "Plank"
* #EXERCISE_SEGMENT_TYPE_PULL_UP "Pull up"
* #EXERCISE_SEGMENT_TYPE_PUNCH "Punch"
* #EXERCISE_SEGMENT_TYPE_REST "Rest"
* #EXERCISE_SEGMENT_TYPE_ROWING_MACHINE "Rowing machine"
* #EXERCISE_SEGMENT_TYPE_RUNNING "Running"
* #EXERCISE_SEGMENT_TYPE_RUNNING_TREADMILL "Running treadmill"
* #EXERCISE_SEGMENT_TYPE_SHOULDER_PRESS "Shoulder press"
* #EXERCISE_SEGMENT_TYPE_SINGLE_ARM_TRICEPS_EXTENSION "Single arm triceps extension"
* #EXERCISE_SEGMENT_TYPE_SIT_UP "Sit up"
* #EXERCISE_SEGMENT_TYPE_SQUAT "Squat"
* #EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING "Stair climbing"
* #EXERCISE_SEGMENT_TYPE_STAIR_CLIMBING_MACHINE "Stair climbing machine"
* #EXERCISE_SEGMENT_TYPE_STRETCHING "Stretching"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_BACKSTROKE "Swimming backstroke"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_BREASTSTROKE "Swimming breaststroke"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_BUTTERFLY "Swimming butterfly"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_FREESTYLE "Swimming freestyle"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_MIXED "Swimming mixed"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_OPEN_WATER "Swimming open water"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_OTHER "Swimming other"
* #EXERCISE_SEGMENT_TYPE_SWIMMING_POOL "Swimming pool"
* #EXERCISE_SEGMENT_TYPE_UNKNOWN "Unknown"
* #EXERCISE_SEGMENT_TYPE_UPPER_TWIST "Upper twist"
* #EXERCISE_SEGMENT_TYPE_WALKING "Walking"
* #EXERCISE_SEGMENT_TYPE_WEIGHTLIFTING "Weightlifting"
* #EXERCISE_SEGMENT_TYPE_WHEELCHAIR "Wheelchair"
* #EXERCISE_SEGMENT_TYPE_YOGA "Yoga"
* #EXERCISE_LAP "Exercise lap"
