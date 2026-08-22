//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

CodeSystem: GroveRecordingMethodCS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "The positively established mode by which a mobile source captured a result. This vocabulary does not describe the clinical measurement technique."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #manual-entry "Manual entry" "A person manually entered the result into the source."
* #actively-recorded "Actively recorded" "A person deliberately initiated or participated in recording the result."
* #automatically-recorded "Automatically recorded" "The source recorded the result without a person initiating that individual measurement."

ValueSet: GroveRecordingMethodVS
Id: grove-recording-method
Title: "Grove Recording Method"
Description: "Capture modes permitted by the Grove recording-method extension when a source positively establishes the mode."
* ^experimental = false
* include codes from system GroveRecordingMethodCS

CodeSystem: GroveSleepStageCS
Id: grove-sleep-stage
Title: "Grove Sleep Stage"
Description: "Source-neutral sleep-stage classes shared by mobile and connected-device adapters. Adapters retain a source-specific code separately when the source distinction is more precise."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #awake "Awake" "The person was classified as awake."
* #in-bed "In bed" "The person was classified as being in bed without asserting wake or sleep."
* #out-of-bed "Out of bed" "The person was classified as outside the sleep-session bed interval."
* #asleep-unspecified "Asleep, unspecified stage" "The person was classified as asleep without a more specific stage."
* #light "Light sleep" "The source classified the interval as light sleep without a more portable stage distinction."
* #deep "Deep sleep" "The source classified the interval as deep or slow-wave sleep."
* #rem "REM sleep" "The source classified the interval as rapid-eye-movement sleep."
* #unknown "Unknown sleep stage" "The interval was part of a sleep session but the stage was not known."

ValueSet: GroveSleepStageVS
Id: grove-sleep-stage
Title: "Grove Sleep Stage"
Description: "Source-neutral sleep stages admitted by the Grove Mobile sleep-stage profile."
* ^experimental = false
* include codes from system GroveSleepStageCS

// No ConceptMap is published for 0.3.0 because the potential HL7 PHR stepCount
// target is not a stable package dependency. Any future mapping from
// step-count-total to that target must be wider, never equal.

CodeSystem: GroveAggregationMethodCS
Id: grove-aggregation-method
Title: "Grove Aggregation Method"
Description: "The fixed aggregation method a windowed Grove measurement profile asserts, so an aggregate result is never mistaken for a point measurement."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #daily-total "Daily total" "The sum of the source values over one calendar day in the subject's reported time zone."
* #daily-mean "Daily mean" "The arithmetic mean of the source values over one calendar day in the subject's reported time zone."
* #daily-minimum "Daily minimum" "The minimum source value over one calendar day in the subject's reported time zone."
* #daily-maximum "Daily maximum" "The maximum source value over one calendar day in the subject's reported time zone."
* #session-mean "Session mean" "The arithmetic mean of the source values over one recorded session whose bounds are the effective Period."
* #session-total "Session total" "The sum of the source values over one recorded session whose bounds are the effective Period."
* #rolling-mean "Rolling mean" "A platform-computed rolling average whose exact window is stated by the profile description."
* #percentage-of-time "Percentage of time" "The percentage of the effective Period during which the stated condition held."
* #session-minimum "Session minimum" "The minimum source value over one recorded session whose bounds are the effective Period."
* #session-rate "Session rate" "A count of qualifying events divided by the session duration, in the unit the profile states."

ValueSet: GroveAggregationMethodVS
Id: grove-aggregation-method
Title: "Grove Aggregation Method"
Description: "Every aggregation method a windowed Grove measurement profile may assert."
* ^experimental = false
* include codes from system GroveAggregationMethodCS


CodeSystem: GroveWorkoutActivityCS
Id: grove-workout-activity
Title: "Grove Workout Activity"
Description: "The shared workout activity classifications present on every enumerable source platform; the long tail of platform activities maps to #other with the exact platform token retained as a secondary coding."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #running "Running" "A recorded running session."
* #walking "Walking" "A recorded walking session."
* #cycling "Cycling" "A recorded cycling session."
* #hiking "Hiking" "A recorded hiking session."
* #swimming "Swimming" "A recorded swimming session."
* #strength-training "Strength training" "A recorded strength training session."
* #high-intensity-interval-training "High-intensity interval training" "A recorded high-intensity interval training session."
* #yoga "Yoga" "A recorded yoga session."
* #pilates "Pilates" "A recorded pilates session."
* #rowing "Rowing" "A recorded rowing session."
* #elliptical "Elliptical" "A recorded elliptical session."
* #stair-climbing "Stair climbing" "A recorded stair climbing session."
* #dancing "Dancing" "A recorded dancing session."
* #tennis "Tennis" "A recorded tennis session."
* #table-tennis "Table tennis" "A recorded table tennis session."
* #badminton "Badminton" "A recorded badminton session."
* #squash "Squash" "A recorded squash session."
* #basketball "Basketball" "A recorded basketball session."
* #soccer "Soccer" "A recorded soccer session."
* #american-football "American football" "A recorded american football session."
* #baseball "Baseball" "A recorded baseball session."
* #volleyball "Volleyball" "A recorded volleyball session."
* #golf "Golf" "A recorded golf session."
* #boxing "Boxing" "A recorded boxing session."
* #martial-arts "Martial arts" "A recorded martial arts session."
* #skiing "Skiing" "A recorded skiing session."
* #snowboarding "Snowboarding" "A recorded snowboarding session."
* #other "Other activity" "A recorded other activity session."

ValueSet: GroveWorkoutActivityVS
Id: grove-workout-activity
Title: "Grove Workout Activity"
Description: "Every shared workout activity classification."
* ^experimental = false
* include codes from system GroveWorkoutActivityCS

CodeSystem: GroveWorkoutSegmentTypeCS
Id: grove-workout-segment-type
Title: "Grove Workout Segment Type"
Description: "The structural classifications of a workout segment child Observation; activity segments use the shared workout activity codes instead."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #lap "Lap" "A lap marked by the source."
* #pause "Pause" "A user or system pause event."
* #resume "Resume" "A resume event."
* #motion-paused "Motion paused" "An automatic motion-pause event."
* #motion-resumed "Motion resumed" "An automatic motion-resume event."
* #pause-or-resume-request "Pause or resume request" "A pause-or-resume request event."
* #marker "Marker" "A point marker event."
* #segment-generic "Segment" "A generic activity segment."
* #rest "Rest" "A rest segment."
* #other-workout "Other workout" "A nested other-workout segment."
* #unknown "Unknown" "A segment whose classification is unknown."

ValueSet: GroveWorkoutSegmentTypeVS
Id: grove-workout-segment-type
Title: "Grove Workout Segment Type"
Description: "Every admitted workout-segment classification: the structural codes plus the shared activity codes."
* ^experimental = false
* include codes from system GroveWorkoutSegmentTypeCS
* include codes from system GroveWorkoutActivityCS

CodeSystem: GroveWorkoutStatisticCS
Id: grove-workout-statistic
Title: "Grove Workout Statistic"
Description: "The per-interval statistic concepts a workout or workout-segment Observation may carry as components; codes derived from a catalog measurement use the {measurement}-{aggregate} form."
* ^experimental = false
* ^caseSensitive = true
* ^content = #complete
* #active-duration "Active duration" "The active duration of the session in seconds."
* #distance-sum "Total distance" "The total distance of the interval in metres."
* #active-energy-sum "Total active energy" "The total active energy of the interval in kilocalories."
* #heart-rate-avg "Average heart rate" "The mean heart rate over the interval."
* #heart-rate-max "Maximum heart rate" "The maximum heart rate over the interval."
* #heart-rate-min "Minimum heart rate" "The minimum heart rate over the interval."
* #step-count-sum "Total steps" "The total steps of the interval."
* #elevation-gain "Elevation gained" "The elevation gained over the interval in metres."
* #flights-climbed-sum "Flights climbed" "The flights climbed over the interval."
* #speed-avg "Average speed" "The mean speed over the interval in metres per second."
* #swimming-stroke-count-sum "Total swimming strokes" "The total swimming strokes of the interval."
* #pool-lap-count "Pool laps" "The pool laps completed in the interval."
* #repetitions "Repetitions" "The exercise repetitions of the segment."
* #set-weight "Set weight" "The weight lifted in the segment in kilograms."
* #set-index "Set index" "The one-based index of the segment's exercise set."
* #rating-of-perceived-exertion "Rating of perceived exertion" "The 0-10 rating of perceived exertion of the segment."
* #lap-length "Lap length" "The length of the lap in metres."
