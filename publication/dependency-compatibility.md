<!--

This source file is part of the Grove FHIR open-source project

SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)

SPDX-License-Identifier: MIT

-->

# HL7 dependency compatibility

The 0.7.0 release retains Extensions R4 5.3.0 and HL7 Terminology (THO) R4
7.3.0 with Publisher 2.3.3. The archive checksums and complete transitive
closure remain pinned in `Scripts/download-fhir-tools.sh`.
CI cache keys and fallback prefixes include the hash of that exact closure
file, so a restored cache cannot introduce packages from a different closure.
Deployment retains its exact-key-only cache policy.

THO 7.5.0 newly includes the `concept-property-type` CodeSystem and ValueSet
under their existing `http://hl7.org/fhir` canonicals at version 6.0.1.
The R4 core package contains the same resources at version 4.0.1, and the
R4 `CodeSystem.property.type` binding explicitly requires that ValueSet version.
Publisher 2.3.3 uses FHIR core 6.10.3. Its
[canonical-resource loader](https://github.com/hapifhir/org.hl7.fhir.core/blob/6.10.3/org.hl7.fhir.r5/src/main/java/org/hl7/fhir/r5/context/CanonicalResourceManager.java#L368-L378)
removes same-canonical resources from the base package when a THO package loads.
Consequently, loading THO 7.5.0 removes the required R4 ValueSet.

The [0.7.0 Health Connect build](https://github.com/SchmiedmayerLab/grove-fhir/actions/runs/40913649601/job/123593989608)
then reports `concept-property-type|4.0.1` as missing while validating the
valid `string` property type in `health-connect-record-type`. The exact
ValueSet and code are present in the checksum-pinned R4 core package; the
failure occurs during binding resolution before code validation. Extensions
5.4.0 requires THO 7.5.0, so retaining a coherent compatible closure requires
retaining Extensions 5.3.0 as well.

Only these exact package-age advisory alternatives are configured:

| Compatible package | Reported newer version |
| --- | --- |
| `hl7.fhir.uv.extensions.r4#5.3.0`, released 2026-05-16 | `5.3.0-ballot-tc1` or `5.4.0` |
| `hl7.terminology.r4#7.3.0`, released 2026-07-27 | `7.4.0` or `7.5.0` |

The live registry and cached package lists can report different alternatives.
An unused alternative is permitted only for Publisher 2.3.3 and a matching
generated ImplementationGuide ID, dependency index, package ID, and pinned
version. An exercised advisory must still occur exactly once. Any other
unused suppression, future version advisory, missing ValueSet, invalid code,
or other validation finding continues to fail the QA gate.

Remove this compatibility policy only after testing a corrected resolver and
dependency closure through every guide, the offline release gate, and the
producer fixture validator. Review the mobile semantic baseline when updating
the dependency versions; do not suppress the missing-ValueSet finding.
