"""Stable producer-rule diagnostics shared by every validation domain."""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from .context import EXCHANGE_PROTOCOL


PRODUCER_RULE_REASONS = {
    row["code"]: row["reason"] for row in EXCHANGE_PROTOCOL["producerDiagnostics"]
}
if len(PRODUCER_RULE_REASONS) != len(EXCHANGE_PROTOCOL["producerDiagnostics"]):
    raise RuntimeError("exchange-protocol producer diagnostic codes must be unique")


class ProducerValidationError(ValueError):
    """A deterministic producer-contract failure with an optional rule diagnostic."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        reason: str | None = None,
        location: str | None = None,
        severity: str = "error",
    ) -> None:
        super().__init__(message)
        self.diagnostic = None if code is None else {
            "code": code,
            "reason": reason if reason is not None else PRODUCER_RULE_REASONS[code],
            "location": location,
            "severity": severity,
        }


def contract_failure(
    code: str,
    location: str,
    message: str,
    *,
    reason: str | None = None,
) -> ProducerValidationError:
    """Construct one machine-comparable producer diagnostic without losing detail."""
    if code not in PRODUCER_RULE_REASONS:
        raise ValueError(
            f"producer diagnostic code {code!r} is not registered by the exchange protocol"
        )
    return ProducerValidationError(
        message,
        code=code,
        reason=reason,
        location=location,
    )
