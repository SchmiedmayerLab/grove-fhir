<!--
This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT
-->

# Questionnaire resources in the prototype

The current package contains draft profiles for FHIR `Questionnaire` and
`QuestionnaireResponse`. They require an instrument canonical on responses, preserve
answered-item text, and use standard SDC extensions where possible.

The combined prototype applies three invariants:

- an item with the SDC item-media extension also has item text;
- an annotate-image item is an attachment item carrying its base image as item media;
- an answered response item should retain its question text.

The current `GroveQuestionnaire` profile also includes annotation-specific constraints
and Grove renderer hints. It therefore does not yet represent the independent,
renderer-neutral Questionnaire Exchange contract described by this preview.

See [Preview Status](publication-status.html) for the current review boundary. Image
annotation remains a Grove application feature outside the proposed FHIR contract.
