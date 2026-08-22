#!/usr/bin/env python3
#
# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT
#
"""Offline UCUM case-sensitive expression parser and dimension algebra.

Validates a UCUM code against the pinned atom table derived from a
version-pinned ucum-essence.xml and computes its dimension vector over the
seven UCUM base units. Special (scale/function) units are admitted only as a
whole expression, and prefixes attach only to metric atoms, so the checks a
terminology server would perform online hold offline and deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class UcumError(ValueError):
    """A UCUM code that the pinned table cannot admit."""


@dataclass
class ParsedUnit:
    """The dimension-level meaning of one UCUM expression."""

    dimension: dict[str, int] = field(default_factory=dict)
    annotations: list[str] = field(default_factory=list)
    special_atom: str | None = None
    arbitrary_atoms: list[str] = field(default_factory=list)


def _merge(target: dict[str, int], source: dict[str, int], power: int) -> None:
    for base, exponent in source.items():
        merged = target.get(base, 0) + exponent * power
        if merged:
            target[base] = merged
        else:
            target.pop(base, None)


def _split_top_level(expression: str) -> list[tuple[str, int]]:
    """Split a term into (component, sign) pairs at top-level '.' and '/'."""
    components: list[tuple[str, int]] = []
    depth = 0
    current = ""
    sign = 1
    for character in expression:
        if character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
            if depth < 0:
                raise UcumError(f"unbalanced brackets in {expression!r}")
        if depth == 0 and character in "./":
            components.append((current, sign))
            sign = 1 if character == "." else -1
            current = ""
        else:
            current += character
    if depth != 0:
        raise UcumError(f"unbalanced brackets in {expression!r}")
    components.append((current, sign))
    return components


def _trailing_exponent(component: str) -> tuple[str, int]:
    """Split a trailing top-level exponent off one component."""
    index = len(component)
    while index > 0 and component[index - 1].isdigit():
        index -= 1
    if index == len(component):
        return component, 1
    if index > 0 and component[index - 1] in "+-":
        index -= 1
    head = component[:index]
    if not head or head.endswith(("[", "{")):
        return component, 1
    return head, int(component[index:])


class UcumTable:
    """The pinned atom and prefix table plus the expression checks over it."""

    def __init__(self, pinned: dict) -> None:
        self.prefixes: dict[str, dict] = pinned["prefixes"]
        self.units: dict[str, dict] = pinned["units"]
        self._prefix_codes = sorted(self.prefixes, key=len, reverse=True)

    def _atom(self, token: str) -> tuple[str, dict, str | None]:
        unit = self.units.get(token)
        if unit is not None:
            return token, unit, None
        for prefix in self._prefix_codes:
            if token.startswith(prefix) and len(token) > len(prefix):
                candidate = self.units.get(token[len(prefix):])
                if candidate is not None:
                    if not candidate.get("isMetric"):
                        raise UcumError(
                            f"prefix {prefix!r} is not allowed on the "
                            f"non-metric atom {token[len(prefix):]!r}"
                        )
                    return token[len(prefix):], candidate, prefix
        raise UcumError(f"unknown UCUM atom {token!r}")

    def parse(self, expression: str) -> ParsedUnit:
        if not expression or expression != expression.strip():
            raise UcumError(f"malformed UCUM code {expression!r}")
        result = ParsedUnit()
        self._parse_term(expression, 1, result)
        if result.special_atom is not None:
            sole = expression == result.special_atom or (
                expression.endswith(result.special_atom)
                and expression[: -len(result.special_atom)] in self._prefix_codes
            )
            if not sole:
                raise UcumError(
                    f"special unit {result.special_atom!r} is only admitted "
                    "as a whole expression"
                )
        return result

    def _parse_term(self, term: str, power: int, result: ParsedUnit) -> None:
        for index, (component, sign) in enumerate(_split_top_level(term)):
            component = component.strip()
            if not component:
                # UCUM admits a leading solidus: "/min" is one per minute.
                if index == 0 and term.startswith("/"):
                    continue
                raise UcumError(f"empty component in {term!r}")
            self._parse_component(component, sign * power, result)

    def _parse_component(self, component: str, power: int, result: ParsedUnit) -> None:
        if component.startswith("{") and component.endswith("}"):
            result.annotations.append(component[1:-1])
            return
        if component.startswith("(") and component.endswith(")"):
            self._parse_term(component[1:-1], power, result)
            return
        head, exponent = _trailing_exponent(component)
        if head.endswith("}"):
            open_brace = head.rfind("{")
            if open_brace < 0:
                raise UcumError(f"unbalanced annotation in {component!r}")
            result.annotations.append(head[open_brace + 1 : -1])
            head = head[:open_brace]
            if not head:
                return
        if head.isdigit():
            return
        atom_code, unit, _prefix = self._atom(head)
        if unit.get("isSpecial"):
            if result.special_atom is not None or exponent != 1 or power != 1:
                raise UcumError(
                    f"special unit {atom_code!r} cannot be combined or raised"
                )
            result.special_atom = atom_code
        if unit.get("isArbitrary"):
            result.arbitrary_atoms.append(atom_code)
        _merge(result.dimension, unit.get("dimension", {}), exponent * power)


def dimension_of(pinned: dict, expression: str) -> dict[str, int]:
    """The dimension vector of a UCUM code under the pinned table."""
    return UcumTable(pinned).parse(expression).dimension
