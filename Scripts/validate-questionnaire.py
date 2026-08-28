#!/usr/bin/env python3
"""Validate Grove Questionnaire resources and Questionnaire/Response pairs.

The official FHIR Validator remains authoritative for base FHIR, SDC, and profile
validation.  This deterministic companion performs the static and cross-resource
checks that require the Questionnaire, QuestionnaireResponse, and referenced
ValueSets to be available together.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


VERSION_ALGORITHM = "http://hl7.org/fhir/StructureDefinition/artifact-versionAlgorithm"
VERSION_ALGORITHM_SYSTEM = "http://hl7.org/fhir/version-algorithm"
VARIABLE = "http://hl7.org/fhir/StructureDefinition/variable"
TARGET_CONSTRAINT = "http://hl7.org/fhir/StructureDefinition/targetConstraint"
ENABLE_EXPRESSION = (
    "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
    "sdc-questionnaire-enableWhenExpression"
)
INITIAL_EXPRESSION = (
    "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
    "sdc-questionnaire-initialExpression"
)
CALCULATED_EXPRESSION = (
    "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
    "sdc-questionnaire-calculatedExpression"
)
MIN_LENGTH = "http://hl7.org/fhir/StructureDefinition/minLength"
MIN_VALUE = "http://hl7.org/fhir/StructureDefinition/minValue"
MAX_VALUE = "http://hl7.org/fhir/StructureDefinition/maxValue"
MIN_QUANTITY = (
    "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
    "sdc-questionnaire-minQuantity"
)
MAX_QUANTITY = (
    "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
    "sdc-questionnaire-maxQuantity"
)
MAX_DECIMAL_PLACES = "http://hl7.org/fhir/StructureDefinition/maxDecimalPlaces"
QUESTIONNAIRE_UNIT = "http://hl7.org/fhir/StructureDefinition/questionnaire-unit"
UNIT_OPTION = "http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption"
UNIT_VALUE_SET = "http://hl7.org/fhir/StructureDefinition/questionnaire-unitValueSet"
MIN_OCCURS = "http://hl7.org/fhir/StructureDefinition/questionnaire-minOccurs"
MAX_OCCURS = "http://hl7.org/fhir/StructureDefinition/questionnaire-maxOccurs"
MIME_TYPE = "http://hl7.org/fhir/StructureDefinition/mimeType"
MAX_SIZE = "http://hl7.org/fhir/StructureDefinition/maxSize"
OPTION_EXCLUSIVE = (
    "http://hl7.org/fhir/StructureDefinition/questionnaire-optionExclusive"
)
STYLE_SENSITIVE = (
    "http://hl7.org/fhir/StructureDefinition/rendering-styleSensitive"
)
COMPLETION_MODE = (
    "http://hl7.org/fhir/StructureDefinition/questionnaireresponse-completionMode"
)
PARTICIPATION_MODE = "http://terminology.hl7.org/CodeSystem/v3-ParticipationMode"

SEMVER_PATTERN = (
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)
SEMVER = re.compile(rf"^{SEMVER_PATTERN}$")
QUESTIONNAIRE_CANONICAL_URL_PATTERN = r"https?://[^\s/?#|]+[^\s|#]*"
QUESTIONNAIRE_CANONICAL_URL = re.compile(
    rf"^{QUESTIONNAIRE_CANONICAL_URL_PATTERN}$"
)
CANONICAL_WITH_VERSION = re.compile(
    rf"^{QUESTIONNAIRE_CANONICAL_URL_PATTERN}\|{SEMVER_PATTERN}$"
)
EXPRESSION_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
RESERVED_VARIABLES = {
    "context",
    "definition",
    "loinc",
    "qitem",
    "questionnaire",
    "resource",
    "rootResource",
    "sct",
    "target",
    "ucum",
}
EXPRESSION_URLS = {VARIABLE, ENABLE_EXPRESSION, INITIAL_EXPRESSION, CALCULATED_EXPRESSION}
COMPLETED_STATUSES = {"amended", "completed"}

ANSWER_TYPES: dict[str, frozenset[str]] = {
    "boolean": frozenset({"valueBoolean"}),
    "decimal": frozenset({"valueDecimal"}),
    "integer": frozenset({"valueInteger"}),
    "date": frozenset({"valueDate"}),
    "dateTime": frozenset({"valueDateTime"}),
    "time": frozenset({"valueTime"}),
    "string": frozenset({"valueString"}),
    "text": frozenset({"valueString"}),
    "url": frozenset({"valueUri"}),
    "choice": frozenset({"valueCoding"}),
    "open-choice": frozenset({"valueCoding", "valueString"}),
    "attachment": frozenset({"valueAttachment"}),
    "quantity": frozenset({"valueQuantity"}),
}
ANSWER_VALUE_KEYS = frozenset().union(*ANSWER_TYPES.values(), {"valueReference"})


@dataclass(frozen=True, order=True)
class Issue:
    rule: str
    path: str
    message: str
    severity: str = "error"


def extensions(element: dict[str, Any], url: str) -> list[dict[str, Any]]:
    return [
        extension
        for extension in element.get("extension", [])
        if isinstance(extension, dict) and extension.get("url") == url
    ]


def extension_value(extension: dict[str, Any]) -> tuple[str | None, Any]:
    values = [
        (key, value)
        for key, value in extension.items()
        if key.startswith("value") and key != "valueSet"
    ]
    if len(values) != 1:
        return None, None
    return values[0]


def first_extension_value(
    element: dict[str, Any], url: str
) -> tuple[str | None, Any]:
    matches = extensions(element, url)
    return extension_value(matches[0]) if matches else (None, None)


def iter_items(
    items: Iterable[dict[str, Any]], path: str = "Questionnaire.item"
) -> Iterator[tuple[dict[str, Any], str]]:
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        yield item, item_path
        yield from iter_items(item.get("item", []), f"{item_path}.item")


def expression_is_valid(value: Any, *, require_name: bool = False) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("language") != "text/fhirpath":
        return False
    if not isinstance(value.get("expression"), str) or not value["expression"].strip():
        return False
    if require_name and (
        not isinstance(value.get("name"), str) or not value["name"].strip()
    ):
        return False
    return True


def validate_expression_scope(
    element: dict[str, Any], path: str, issues: list[Issue], keys: set[str]
) -> None:
    names: set[str] = set()
    for index, extension in enumerate(element.get("extension", [])):
        if not isinstance(extension, dict):
            continue
        url = extension.get("url")
        extension_path = f"{path}.extension[{index}]"
        if url in EXPRESSION_URLS:
            _, value = extension_value(extension)
            if not expression_is_valid(value, require_name=url == VARIABLE):
                rule = "qg-variable-name-1" if url == VARIABLE and isinstance(value, dict) and not value.get("name") else "qg-expression-1"
                issues.append(
                    Issue(rule, extension_path, "Expression must contain the required FHIRPath fields")
                )
            if url == VARIABLE and isinstance(value, dict):
                name = value.get("name")
                if isinstance(name, str) and name:
                    if not EXPRESSION_NAME.fullmatch(name) or name in RESERVED_VARIABLES:
                        issues.append(
                            Issue(
                                "qg-variable-name-reserved",
                                f"{extension_path}.valueExpression.name",
                                f"Variable name {name!r} is invalid or reserved",
                            )
                        )
                    if name in names:
                        issues.append(
                            Issue(
                                "qg-variable-name-duplicate",
                                f"{extension_path}.valueExpression.name",
                                f"Variable name {name!r} is duplicated in this scope",
                            )
                        )
                    names.add(name)
        if url == TARGET_CONSTRAINT:
            parts = {
                part.get("url"): part
                for part in extension.get("extension", [])
                if isinstance(part, dict) and isinstance(part.get("url"), str)
            }
            key = parts.get("key", {}).get("valueId")
            severity = parts.get("severity", {}).get("valueCode")
            human = parts.get("human", {}).get("valueString")
            expression = parts.get("expression", {}).get("valueExpression")
            if not isinstance(key, str) or not key:
                issues.append(
                    Issue("qg-target-constraint-shape", extension_path, "targetConstraint requires a non-empty key")
                )
            elif key in keys:
                issues.append(
                    Issue("qg-target-constraint-key", extension_path, f"targetConstraint key {key!r} is not unique")
                )
            else:
                keys.add(key)
            if severity not in {"error", "warning"}:
                issues.append(
                    Issue("qg-target-constraint-shape", extension_path, "targetConstraint severity must be error or warning")
                )
            if not isinstance(human, str) or not human.strip():
                issues.append(
                    Issue("qg-target-constraint-shape", extension_path, "targetConstraint requires human guidance")
                )
            if not expression_is_valid(expression):
                issues.append(
                    Issue("qg-expression-1", extension_path, "targetConstraint requires a non-empty FHIRPath expression")
                )


def decimal_value(value: Any) -> Decimal | None:
    try:
        if isinstance(value, bool) or value is None:
            return None
        return Decimal(str(value))
    except InvalidOperation:
        return None


def comparable_quantity(value: Any) -> tuple[Decimal, str, str] | None:
    if not isinstance(value, dict):
        return None
    number = decimal_value(value.get("value"))
    system = value.get("system")
    code = value.get("code")
    if number is None or not isinstance(system, str) or not isinstance(code, str):
        return None
    return number, system, code


def compare_bound_values(left: Any, right: Any) -> bool | None:
    left_decimal = decimal_value(left)
    right_decimal = decimal_value(right)
    if left_decimal is not None and right_decimal is not None:
        return left_decimal <= right_decimal
    if isinstance(left, str) and isinstance(right, str):
        return left <= right
    left_quantity = comparable_quantity(left)
    right_quantity = comparable_quantity(right)
    if left_quantity and right_quantity:
        if left_quantity[1:] != right_quantity[1:]:
            return None
        return left_quantity[0] <= right_quantity[0]
    return None


def validate_bound_pair(
    item: dict[str, Any],
    path: str,
    minimum_url: str,
    maximum_url: str,
    rule: str,
    issues: list[Issue],
) -> None:
    minimum_key, minimum = first_extension_value(item, minimum_url)
    maximum_key, maximum = first_extension_value(item, maximum_url)
    if minimum_key is None or maximum_key is None:
        return
    if minimum_key != maximum_key or compare_bound_values(minimum, maximum) is not True:
        issues.append(
            Issue(rule, path, "Minimum and maximum must use comparable values and minimum must not exceed maximum")
        )


def validate_questionnaire(questionnaire: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    if questionnaire.get("resourceType") != "Questionnaire":
        return [Issue("qg-resource-type", "Questionnaire", "Expected a Questionnaire resource")]

    canonical_url = questionnaire.get("url")
    if (
        not isinstance(canonical_url, str)
        or QUESTIONNAIRE_CANONICAL_URL.fullmatch(canonical_url) is None
    ):
        issues.append(
            Issue(
                "qg-canonical-1",
                "Questionnaire.url",
                "Use one absolute HTTP(S) canonical URL without a version separator or fragment",
            )
        )

    version = questionnaire.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        issues.append(Issue("qg-version-1", "Questionnaire.version", "Version is not valid SemVer 2.0.0"))

    algorithm = extensions(questionnaire, VERSION_ALGORITHM)
    algorithm_value = extension_value(algorithm[0]) if len(algorithm) == 1 else (None, None)
    algorithm_coding = algorithm_value[1]
    if (
        algorithm_value[0] != "valueCoding"
        or not isinstance(algorithm_coding, dict)
        or algorithm_coding.get("system") != VERSION_ALGORITHM_SYSTEM
        or algorithm_coding.get("code") != "semver"
    ):
        issues.append(
            Issue(
                "qg-version-algorithm-1",
                "Questionnaire.extension",
                "Exactly one Coding must declare the semver version algorithm",
            )
        )

    if extensions(questionnaire, STYLE_SENSITIVE):
        issues.append(Issue("qg-style-sensitive-1", "Questionnaire.extension", "styleSensitive is not supported"))

    target_keys: set[str] = set()
    validate_expression_scope(questionnaire, "Questionnaire", issues, target_keys)
    seen_link_ids: set[str] = set()
    all_items = list(iter_items(questionnaire.get("item", [])))
    for item, path in all_items:
        link_id = item.get("linkId")
        if not isinstance(link_id, str) or not link_id:
            issues.append(Issue("qg-linkid", f"{path}.linkId", "Item linkId is required"))
        elif link_id in seen_link_ids:
            issues.append(Issue("qg-linkid-duplicate", f"{path}.linkId", f"Duplicate Questionnaire linkId {link_id!r}"))
        else:
            seen_link_ids.add(link_id)

        item_type = item.get("type")
        if item_type != "group" and not item.get("text"):
            issues.append(Issue("qg-item-text-1", f"{path}.text", "Question and display items require text"))
        if item_type == "reference" or any("valueReference" in option for option in item.get("answerOption", [])):
            issues.append(Issue("qg-reference-1", path, "Reference answers are outside this contract"))
        if item.get("repeats") is True and item_type not in {"choice", "open-choice", "attachment"}:
            issues.append(Issue("qg-repeats-1", f"{path}.repeats", "This item type cannot repeat"))
        if item.get("enableWhen") and extensions(item, ENABLE_EXPRESSION):
            issues.append(Issue("qg-enable-1", path, "Use either enableWhen or enableWhenExpression"))
        if item.get("initial") and extensions(item, INITIAL_EXPRESSION):
            issues.append(Issue("qg-initial-1", path, "Use either initial or initialExpression"))
        if extensions(item, STYLE_SENSITIVE):
            issues.append(Issue("qg-style-sensitive-1", f"{path}.extension", "styleSensitive is not supported"))

        validate_expression_scope(item, path, issues, target_keys)

        has_length = item.get("maxLength") is not None or bool(extensions(item, MIN_LENGTH))
        if has_length and item_type not in {"string", "text", "url", "open-choice"}:
            issues.append(Issue("qg-length-1", path, "Length constraints require a textual item"))
        _, minimum_length = first_extension_value(item, MIN_LENGTH)
        maximum_length = item.get("maxLength")
        if minimum_length is not None and (
            not isinstance(minimum_length, int)
            or minimum_length < 0
            or (isinstance(maximum_length, int) and minimum_length > maximum_length)
        ):
            issues.append(Issue("qg-min-max-1", path, "Text length bounds are invalid or reversed"))

        _, decimal_places = first_extension_value(item, MAX_DECIMAL_PLACES)
        if decimal_places is not None and item_type != "decimal":
            issues.append(Issue("qg-decimal-1", path, "maxDecimalPlaces requires a decimal item"))
        if decimal_places is not None and (
            not isinstance(decimal_places, int) or decimal_places < 0
        ):
            issues.append(Issue("qg-decimal-precision", path, "maxDecimalPlaces must be non-negative"))

        lower_key, _ = first_extension_value(item, MIN_VALUE)
        upper_key, _ = first_extension_value(item, MAX_VALUE)
        if (lower_key or upper_key) and item_type not in {"integer", "decimal", "date", "dateTime", "time"}:
            issues.append(Issue("qg-value-bounds-1", path, "Generic value bounds do not match the item type"))
        expected_bound_type = {
            "integer": "valueInteger",
            "decimal": "valueDecimal",
            "date": "valueDate",
            "dateTime": "valueDateTime",
            "time": "valueTime",
        }.get(item_type)
        bound_type_mismatch = bool(
            expected_bound_type
            and any(
                key and key != expected_bound_type
                for key in (lower_key, upper_key)
            )
        )
        if bound_type_mismatch:
            issues.append(Issue("qg-value-bound-type", path, "Bound datatype must match the Questionnaire item type"))
        else:
            validate_bound_pair(
                item,
                path,
                MIN_VALUE,
                MAX_VALUE,
                "qg-value-bounds-order",
                issues,
            )

        has_quantity_bounds = bool(extensions(item, MIN_QUANTITY) or extensions(item, MAX_QUANTITY))
        if has_quantity_bounds and item_type != "quantity":
            issues.append(Issue("qg-quantity-1", path, "Quantity bounds require a quantity item"))
        validate_bound_pair(item, path, MIN_QUANTITY, MAX_QUANTITY, "qg-quantity-bounds-order", issues)

        fixed_units = extensions(item, QUESTIONNAIRE_UNIT)
        unit_options = extensions(item, UNIT_OPTION)
        unit_value_sets = extensions(item, UNIT_VALUE_SET)
        if fixed_units and item_type not in {"integer", "decimal"}:
            issues.append(Issue("qg-unit-1", path, "A fixed unit requires an integer or decimal item"))
        if (unit_options or unit_value_sets) and item_type != "quantity":
            issues.append(Issue("qg-unit-1", path, "Selectable units require a quantity item"))
        if unit_options and unit_value_sets:
            issues.append(Issue("qg-unit-1", path, "Use unitOption or unitValueSet, not both"))

        if (extensions(item, MIME_TYPE) or extensions(item, MAX_SIZE)) and item_type != "attachment":
            issues.append(Issue("qg-attachment-1", path, "Attachment constraints require an attachment item"))
        _, maximum_size = first_extension_value(item, MAX_SIZE)
        if maximum_size is not None and (
            decimal_value(maximum_size) is None or decimal_value(maximum_size) <= 0
        ):
            issues.append(Issue("qg-attachment-size", path, "Maximum attachment size must be positive"))

        _, minimum_occurs = first_extension_value(item, MIN_OCCURS)
        _, maximum_occurs = first_extension_value(item, MAX_OCCURS)
        if (minimum_occurs is not None or maximum_occurs is not None) and item.get("repeats") is not True:
            issues.append(Issue("qg-occurrence-1", path, "Occurrence constraints require repeats=true"))
        invalid_occurrence = (
            minimum_occurs is not None
            and (not isinstance(minimum_occurs, int) or minimum_occurs < 0)
        ) or (
            maximum_occurs is not None
            and (not isinstance(maximum_occurs, int) or maximum_occurs < 1)
        ) or (
            isinstance(minimum_occurs, int)
            and isinstance(maximum_occurs, int)
            and minimum_occurs > maximum_occurs
        )
        if invalid_occurrence:
            issues.append(Issue("qg-min-max-1", path, "Occurrence bounds are invalid or reversed"))

    enable_targets = seen_link_ids
    for item, path in all_items:
        for index, condition in enumerate(item.get("enableWhen", [])):
            if condition.get("question") not in enable_targets:
                issues.append(
                    Issue(
                        "qg-enable-question",
                        f"{path}.enableWhen[{index}].question",
                        "enableWhen references an unknown Questionnaire linkId",
                    )
                )
    return sorted(set(issues))


def response_items(items: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for item in items:
        yield item
        yield from response_items(item.get("item", []))
        for answer in item.get("answer", []):
            yield from response_items(answer.get("item", []))


def validate_response(response: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    if response.get("resourceType") != "QuestionnaireResponse":
        return [Issue("gqr-resource-type", "QuestionnaireResponse", "Expected a QuestionnaireResponse resource")]
    canonical = response.get("questionnaire")
    if not isinstance(canonical, str) or not CANONICAL_WITH_VERSION.fullmatch(canonical):
        issues.append(
            Issue(
                "gqr-canonical-1",
                "QuestionnaireResponse.questionnaire",
                "Use one absolute HTTP(S) canonical URL with a non-blank authority, "
                "followed by one separator and an exact SemVer version",
            )
        )
    identifier = response.get("identifier")
    if not isinstance(identifier, dict) or not identifier.get("system") or not identifier.get("value"):
        issues.append(Issue("gqr-identifier-1", "QuestionnaireResponse.identifier", "A complete business identifier is required"))
    completion = extensions(response, COMPLETION_MODE)
    completion_value = extension_value(completion[0]) if len(completion) == 1 else (None, None)
    expected_coding = {"system": PARTICIPATION_MODE, "code": "ELECTRONIC"}
    completion_valid = False
    if completion_value[0] == "valueCodeableConcept" and isinstance(completion_value[1], dict):
        codings = completion_value[1].get("coding")
        completion_valid = (
            isinstance(codings, list)
            and len(codings) == 1
            and isinstance(codings[0], dict)
            and codings[0].get("system") == expected_coding["system"]
            and codings[0].get("code") == expected_coding["code"]
        )
    if not completion_valid:
        issues.append(Issue("gqr-completion-mode-1", "QuestionnaireResponse.extension", "Completion mode must contain exactly one ELECTRONIC ParticipationMode coding"))
    return sorted(set(issues))


def coding_key(coding: Any) -> tuple[Any, Any, Any] | None:
    if not isinstance(coding, dict) or not coding.get("code"):
        return None
    return coding.get("system"), coding.get("version"), coding.get("code")


def values_equal(left: Any, right: Any) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        if "code" in left or "code" in right:
            left_key = coding_key(left)
            right_key = coding_key(right)
            if left_key is None or right_key is None:
                return False
            return left_key[0] == right_key[0] and left_key[2] == right_key[2]
        left_quantity = comparable_quantity(left)
        right_quantity = comparable_quantity(right)
        return left_quantity is not None and left_quantity == right_quantity
    return left == right


def answer_value(answer: dict[str, Any]) -> tuple[str | None, Any]:
    values = [(key, answer[key]) for key in ANSWER_VALUE_KEYS if key in answer]
    if len(values) != 1:
        return None, None
    return values[0]


def questionnaire_answer_values(response: dict[str, Any]) -> dict[str, list[Any]]:
    values: dict[str, list[Any]] = {}
    for item in response_items(response.get("item", [])):
        bucket = values.setdefault(str(item.get("linkId", "")), [])
        for answer in item.get("answer", []):
            _, value = answer_value(answer)
            if value is not None:
                bucket.append(value)
    return values


def evaluate_enable_when(
    item: dict[str, Any], all_answers: dict[str, list[Any]]
) -> bool | None:
    conditions = item.get("enableWhen", [])
    if not conditions:
        return True
    outcomes: list[bool] = []
    for condition in conditions:
        values = all_answers.get(str(condition.get("question", "")), [])
        operator = condition.get("operator")
        expected_pairs = [
            (key.replace("answer", "value", 1), value)
            for key, value in condition.items()
            if key.startswith("answer")
        ]
        if len(expected_pairs) != 1:
            return None
        _, expected = expected_pairs[0]
        if operator == "exists":
            if not isinstance(expected, bool):
                return None
            outcomes.append(bool(values) is expected)
        elif operator == "=":
            outcomes.append(any(values_equal(value, expected) for value in values))
        elif operator == "!=":
            # R4 enableWhen is satisfied when any answer satisfies the operator.
            # An unanswered question therefore satisfies neither equality operator;
            # `!=` must not be implemented as the negation of `=`.
            outcomes.append(any(not values_equal(value, expected) for value in values))
        elif operator in {">", "<", ">=", "<="}:
            comparisons: list[bool] = []
            for value in values:
                left = decimal_value(value)
                right = decimal_value(expected)
                if left is None or right is None:
                    if isinstance(value, str) and isinstance(expected, str):
                        left, right = value, expected
                    else:
                        return None
                comparisons.append(
                    {
                        ">": left > right,
                        "<": left < right,
                        ">=": left >= right,
                        "<=": left <= right,
                    }[operator]
                )
            outcomes.append(any(comparisons))
        else:
            return None
    behavior = item.get("enableBehavior", "all")
    return any(outcomes) if behavior == "any" else all(outcomes)


class ValueSetResolver:
    def __init__(self, value_sets: Sequence[dict[str, Any]]) -> None:
        self._resources: dict[str, dict[str, Any]] = {}
        for value_set in value_sets:
            if value_set.get("resourceType") != "ValueSet" or not value_set.get("url"):
                continue
            url = value_set["url"]
            self._resources[url] = value_set
            if value_set.get("version"):
                self._resources[f"{url}|{value_set['version']}"] = value_set

    def contains(self, canonical: str, coding: Any) -> bool | None:
        value_set = self._resources.get(canonical)
        key = coding_key(coding)
        if value_set is None or key is None:
            return None
        for include in value_set.get("compose", {}).get("include", []):
            if include.get("filter") or include.get("valueSet"):
                return None
            if include.get("system") != key[0]:
                continue
            concepts = include.get("concept")
            if concepts is None:
                return None
            if any(concept.get("code") == key[2] for concept in concepts):
                return True
        for contains in value_set.get("expansion", {}).get("contains", []):
            if contains.get("system") == key[0] and contains.get("code") == key[2]:
                return True
        return False


def selected_inline_option(item: dict[str, Any], value: Any) -> dict[str, Any] | None:
    for option in item.get("answerOption", []):
        _, candidate = next(
            ((key, option[key]) for key in option if key.startswith("value")),
            (None, None),
        )
        if values_equal(value, candidate):
            return option
    return None


def validate_answer_constraints(
    definition: dict[str, Any],
    answers: list[dict[str, Any]],
    path: str,
    resolver: ValueSetResolver,
    issues: list[Issue],
) -> None:
    expected_types = ANSWER_TYPES.get(definition.get("type"), frozenset())
    selected_options: list[dict[str, Any]] = []
    for index, answer in enumerate(answers):
        answer_path = f"{path}.answer[{index}]"
        value_key, value = answer_value(answer)
        if value_key not in expected_types:
            issues.append(Issue("pair-answer-type", answer_path, f"Expected one of {sorted(expected_types)}, found {value_key!r}"))
            continue
        options = definition.get("answerOption", [])
        if options and value_key in {"valueCoding", "valueString", "valueInteger", "valueDate", "valueTime"}:
            option = selected_inline_option(definition, value)
            if option is None and not (definition.get("type") == "open-choice" and value_key == "valueString"):
                issues.append(Issue("pair-inline-option", answer_path, "Answer is not one of the inline options"))
            elif option is not None:
                selected_options.append(option)
        answer_value_set = definition.get("answerValueSet")
        if answer_value_set and value_key == "valueCoding":
            membership = resolver.contains(answer_value_set, value)
            if membership is None:
                issues.append(Issue("pair-valueset-unresolved", answer_path, f"Cannot resolve and deterministically expand {answer_value_set!r}"))
            elif not membership:
                issues.append(Issue("pair-valueset-membership", answer_path, "Coded answer is not in the referenced ValueSet"))

        if value_key in {"valueString", "valueUri"}:
            _, minimum_length = first_extension_value(definition, MIN_LENGTH)
            maximum_length = definition.get("maxLength")
            if isinstance(minimum_length, int) and len(value) < minimum_length:
                issues.append(Issue("pair-answer-length", answer_path, "Answer is shorter than minLength"))
            if isinstance(maximum_length, int) and len(value) > maximum_length:
                issues.append(Issue("pair-answer-length", answer_path, "Answer exceeds maxLength"))

        if value_key == "valueDecimal":
            _, places = first_extension_value(definition, MAX_DECIMAL_PLACES)
            if isinstance(places, int):
                decimal = Decimal(str(value))
                actual_places = max(0, -decimal.as_tuple().exponent)
                if actual_places > places:
                    issues.append(Issue("pair-answer-decimal-places", answer_path, "Answer exceeds maxDecimalPlaces"))

        for url, operator, rule in (
            (MIN_VALUE, "minimum", "pair-answer-value-bound"),
            (MAX_VALUE, "maximum", "pair-answer-value-bound"),
            (MIN_QUANTITY, "minimum", "pair-answer-quantity-bound"),
            (MAX_QUANTITY, "maximum", "pair-answer-quantity-bound"),
        ):
            _, bound = first_extension_value(definition, url)
            if bound is None:
                continue
            comparison = compare_bound_values(bound, value)
            valid = comparison if operator == "minimum" else compare_bound_values(value, bound)
            if valid is not True:
                issues.append(Issue(rule, answer_path, f"Answer violates the {operator} bound or uses an incomparable unit"))

        if value_key == "valueQuantity" and isinstance(value, dict):
            options = [extension_value(extension)[1] for extension in extensions(definition, UNIT_OPTION)]
            if options and not any(values_equal(value, option) for option in options):
                issues.append(Issue("pair-answer-unit", answer_path, "Quantity unit is not one of unitOption"))
            _, unit_value_set = first_extension_value(definition, UNIT_VALUE_SET)
            if isinstance(unit_value_set, str):
                unit_coding = {"system": value.get("system"), "code": value.get("code")}
                membership = resolver.contains(unit_value_set, unit_coding)
                if membership is not True:
                    rule = "pair-valueset-unresolved" if membership is None else "pair-answer-unit"
                    issues.append(Issue(rule, answer_path, "Quantity unit is not certified by unitValueSet"))

        if value_key == "valueAttachment" and isinstance(value, dict):
            allowed_types = {extension_value(extension)[1] for extension in extensions(definition, MIME_TYPE)}
            if allowed_types and value.get("contentType") not in allowed_types:
                issues.append(Issue("pair-answer-attachment", answer_path, "Attachment contentType is not allowed"))
            _, maximum_size = first_extension_value(definition, MAX_SIZE)
            size = value.get("size")
            if maximum_size is not None and (not isinstance(size, int) or Decimal(size) > Decimal(str(maximum_size))):
                issues.append(Issue("pair-answer-attachment", answer_path, "Attachment exceeds maxSize or does not declare size"))

    exclusive = [
        option
        for option in selected_options
        if any(extension_value(extension) == ("valueBoolean", True) for extension in extensions(option, OPTION_EXCLUSIVE))
    ]
    if exclusive and len(answers) > 1:
        issues.append(Issue("pair-option-exclusive", path, "An exclusive option cannot be combined with another answer"))

    if definition.get("repeats") is not True and len(answers) > 1:
        issues.append(Issue("pair-repeats", path, "Non-repeating item has multiple answers"))
    _, minimum_occurs = first_extension_value(definition, MIN_OCCURS)
    _, maximum_occurs = first_extension_value(definition, MAX_OCCURS)
    if isinstance(minimum_occurs, int) and len(answers) < minimum_occurs:
        issues.append(Issue("pair-answer-occurrence", path, "Answer count is below minOccurs"))
    if isinstance(maximum_occurs, int) and len(answers) > maximum_occurs:
        issues.append(Issue("pair-answer-occurrence", path, "Answer count exceeds maxOccurs"))


def reference_resource_type(
    reference: Any, containing_resource: dict[str, Any]
) -> str | None:
    """Return a Reference target type when it is explicit or locally resolvable."""
    if not isinstance(reference, dict):
        return None
    declared_type = reference.get("type")
    declared_resource_type: str | None = None
    if isinstance(declared_type, str):
        if re.fullmatch(r"[A-Z][A-Za-z0-9]*", declared_type):
            declared_resource_type = declared_type
        else:
            canonical_prefix = "http://hl7.org/fhir/StructureDefinition/"
            if declared_type.startswith(canonical_prefix):
                candidate = declared_type[len(canonical_prefix) :]
                if re.fullmatch(r"[A-Z][A-Za-z0-9]*", candidate):
                    declared_resource_type = candidate
    if "type" in reference and declared_resource_type is None:
        # R4 Reference.type names a resource by its relative resource code or by
        # the canonical core StructureDefinition URL. An arbitrary URI whose
        # final path segment happens to look like a resource type proves nothing.
        return None

    literal = reference.get("reference")
    if not isinstance(literal, str) or not literal:
        return declared_resource_type
    literal_resource_type: str | None = None
    if literal.startswith("#"):
        contained_id = literal[1:]
        matches = [
            resource
            for resource in containing_resource.get("contained", [])
            if isinstance(resource, dict) and resource.get("id") == contained_id
        ]
        if len(matches) == 1 and isinstance(matches[0].get("resourceType"), str):
            literal_resource_type = matches[0]["resourceType"]
    else:
        match = re.search(
            r"(?:^|/)([A-Z][A-Za-z0-9]*)/[^/?#]+(?:/_history/[^/?#]+)?$",
            literal,
        )
        literal_resource_type = match.group(1) if match else None

    if (
        declared_resource_type is not None
        and literal_resource_type is not None
        and declared_resource_type != literal_resource_type
    ):
        return None
    return declared_resource_type or literal_resource_type


def validate_pair(
    questionnaire: dict[str, Any],
    response: dict[str, Any],
    value_sets: Sequence[dict[str, Any]] = (),
) -> list[Issue]:
    issues = validate_questionnaire(questionnaire) + validate_response(response)
    expected_canonical = f"{questionnaire.get('url', '')}|{questionnaire.get('version', '')}"
    if response.get("questionnaire") != expected_canonical:
        issues.append(Issue("pair-questionnaire-canonical", "QuestionnaireResponse.questionnaire", f"Expected exact canonical {expected_canonical!r}"))
    subject = response.get("subject")
    admitted_subject_types = questionnaire.get("subjectType", [])
    if subject is not None and admitted_subject_types:
        actual_subject_type = reference_resource_type(subject, response)
        if actual_subject_type not in admitted_subject_types:
            issues.append(
                Issue(
                    "pair-subject-type",
                    "QuestionnaireResponse.subject",
                    "QuestionnaireResponse.subject must target one of "
                    f"Questionnaire.subjectType {sorted(admitted_subject_types)!r}; "
                    f"found {actual_subject_type!r}",
                )
            )
    if response.get("status") == "entered-in-error":
        issues.append(Issue("pair-response-entered-in-error", "QuestionnaireResponse.status", "An entered-in-error response must not be accepted as answer data"))

    definitions = {item.get("linkId"): item for item, _ in iter_items(questionnaire.get("item", [])) if item.get("linkId")}
    all_answers = questionnaire_answer_values(response)
    resolver = ValueSetResolver(value_sets)
    completed = response.get("status") in COMPLETED_STATUSES

    def check_container(
        expected_items: list[dict[str, Any]],
        actual_items: list[dict[str, Any]],
        path: str,
    ) -> None:
        expected = {item.get("linkId"): item for item in expected_items}
        actual_by_link: dict[str, list[tuple[dict[str, Any], str]]] = {}
        for index, actual in enumerate(actual_items):
            actual_path = f"{path}[{index}]"
            link_id = actual.get("linkId")
            if link_id not in expected:
                rule = "pair-item-misplaced" if link_id in definitions else "pair-item-unknown"
                issues.append(Issue(rule, f"{actual_path}.linkId", f"Item {link_id!r} is not valid at this location"))
                continue
            actual_by_link.setdefault(link_id, []).append((actual, actual_path))

        for link_id, occurrences in actual_by_link.items():
            if len(occurrences) > 1:
                issues.append(Issue("pair-item-duplicate", path, f"Item {link_id!r} appears more than once in one response context"))

        for link_id, definition in expected.items():
            enabled = evaluate_enable_when(definition, all_answers)
            has_expression_enablement = bool(extensions(definition, ENABLE_EXPRESSION))
            if has_expression_enablement and completed:
                issues.append(Issue("pair-expression-engine-required", path, f"Completed response requires FHIRPath enablement evaluation for {link_id!r}"))
            if enabled is None and completed:
                issues.append(Issue("pair-enable-evaluation", path, f"Cannot evaluate enableWhen for {link_id!r}"))
            present = actual_by_link.get(link_id, [])
            if enabled is False and present:
                issues.append(Issue("pair-item-disabled", present[0][1], f"Disabled item {link_id!r} must not be present"))
            if completed and definition.get("required") is True and enabled is True and not present:
                issues.append(Issue("pair-required-item", path, f"Required enabled item {link_id!r} is missing"))

            for actual, actual_path in present:
                item_type = definition.get("type")
                answers = actual.get("answer", [])
                if item_type in {"group", "display"} and answers:
                    issues.append(Issue("pair-answer-type", f"{actual_path}.answer", f"{item_type} items cannot have answers"))
                elif item_type in ANSWER_TYPES:
                    validate_answer_constraints(definition, answers, actual_path, resolver, issues)
                    if completed and definition.get("required") is True and enabled is True and not answers:
                        issues.append(Issue("pair-required-item", actual_path, f"Required enabled item {link_id!r} has no answer"))
                if actual.get("item") and item_type != "group":
                    issues.append(Issue("pair-item-nesting", f"{actual_path}.item", "Children of a question belong beneath the answer that supplies their context"))
                if item_type == "group":
                    check_container(definition.get("item", []), actual.get("item", []), f"{actual_path}.item")
                else:
                    for answer_index, answer in enumerate(answers):
                        check_container(definition.get("item", []), answer.get("item", []), f"{actual_path}.answer[{answer_index}].item")

                for constraint in extensions(definition, TARGET_CONSTRAINT):
                    if not completed:
                        continue
                    parts = {part.get("url"): part for part in constraint.get("extension", []) if isinstance(part, dict)}
                    severity = parts.get("severity", {}).get("valueCode", "error")
                    key = parts.get("key", {}).get("valueId", "targetConstraint")
                    issues.append(
                        Issue(
                            "pair-expression-engine-required",
                            actual_path,
                            f"FHIRPath engine must evaluate target constraint {key!r}",
                            "warning" if severity == "warning" else "error",
                        )
                    )

            # A group is structural, so omitting the group does not make enabled,
            # required descendants optional in a completed response.  Question
            # children are different: they exist in an answer context and cannot be
            # required until that answer context exists.
            if completed and enabled is True and definition.get("type") == "group" and not present:
                check_container(definition.get("item", []), [], f"{path}.{link_id}.item")

    check_container(questionnaire.get("item", []), response.get("item", []), "QuestionnaireResponse.item")
    for constraint in extensions(questionnaire, TARGET_CONSTRAINT):
        if not completed:
            continue
        parts = {part.get("url"): part for part in constraint.get("extension", []) if isinstance(part, dict)}
        severity = parts.get("severity", {}).get("valueCode", "error")
        key = parts.get("key", {}).get("valueId", "targetConstraint")
        issues.append(
            Issue(
                "pair-expression-engine-required",
                "QuestionnaireResponse",
                f"FHIRPath engine must evaluate root target constraint {key!r}",
                "warning" if severity == "warning" else "error",
            )
        )
    return sorted(set(issues))


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} does not contain one FHIR resource object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questionnaire", required=True, type=Path)
    parser.add_argument("--response", type=Path)
    parser.add_argument("--value-set", action="append", default=[], type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit a JSON report")
    arguments = parser.parse_args(argv)
    try:
        questionnaire = load_json(arguments.questionnaire)
        response = load_json(arguments.response) if arguments.response else None
        value_sets = [load_json(path) for path in arguments.value_set]
    except ValueError as error:
        parser.error(str(error))

    issues = (
        validate_pair(questionnaire, response, value_sets)
        if response is not None
        else validate_questionnaire(questionnaire)
    )
    if arguments.json_output:
        print(json.dumps({"valid": not any(issue.severity == "error" for issue in issues), "issues": [asdict(issue) for issue in issues]}, indent=2, sort_keys=True))
    elif issues:
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.rule} {issue.path}: {issue.message}")
    else:
        print("Questionnaire validation passed")
    return int(any(issue.severity == "error" for issue in issues))


if __name__ == "__main__":
    raise SystemExit(main())
