#!/usr/bin/env python3
"""Validate Grove study task occurrences against their definitions, results, and history.

The official FHIR Validator checks each resource against its Grove profile. This companion checks
what no single resource can show: that a Task's definitions exist and agree, that the result of a
questionnaire occurrence is about the same participant and instrument, and that a delivery agrees
with the occurrences a receiver already accepted. Deliveries are applied in order; a rejected
delivery changes no state.
"""

# This source file is part of the Grove FHIR open-source project
#
# SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Sequence


ROOT = Path(__file__).resolve().parent.parent
PARAMETER_SYSTEM = "https://grovealliance.org/fhir/study/CodeSystem/grove-study-task-parameter"
SDC_SYSTEM = "http://hl7.org/fhir/uv/sdc/CodeSystem/temp"
RESULT_REFERENCE = re.compile(
    r"^(?:(?P<base>https?://[^\s|#]+)/)?QuestionnaireResponse/"
    r"(?P<id>[A-Za-z0-9.-]{1,64})/_history/(?P<version>[A-Za-z0-9.-]{1,64})$"
)
ACCEPTED_RESPONSE_STATUSES = frozenset({"completed", "amended"})
# Rules for an occurrence of any component kind.
OCCURRENCE_RULES = (
    "study-task-definition",
    "study-task-protocol",
    "study-task-enrollment",
    "study-task-duplicate-occurrence",
    "study-task-cancelled-after-window",
    "study-task-output",
    "study-task-completion-window",
    "study-task-occurrence-conflict",
    "study-task-status-transition",
    "study-task-altered-replay",
)
# Rules for the questionnaire input of any occurrence, and for an occurrence of a questionnaire
# component and the response that completes it.
QUESTIONNAIRE_RULES = (
    "study-task-instrument",
    "study-task-result-reference",
    "study-task-result-subject",
    "study-task-result-instrument",
    "study-task-result-status",
    "study-task-result-window",
    "study-task-result-part-of",
    "study-task-result-shared",
    "study-task-altered-result",
    "study-task-completion-conflict",
    "study-task-correction",
)
RULES = OCCURRENCE_RULES + QUESTIONNAIRE_RULES


def _load_pair_validator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "validate_questionnaire", ROOT / "Scripts/validate-questionnaire.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load the paired Questionnaire validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


PAIR = _load_pair_validator()


@dataclass(frozen=True, order=True)
class Issue:
    rule: str
    occurrence: str
    message: str


@dataclass(frozen=True)
class Resolved:
    """One resource with the Bundle entry fullUrl it arrived under, if any."""

    full_url: str | None
    resource: dict[str, Any]


def resources_of(document: Any) -> list[Resolved]:
    """The resources of a Bundle, or the one resource a document is."""
    if not isinstance(document, dict):
        raise ValueError("a delivery must be a JSON object")
    if document.get("resourceType") != "Bundle":
        return [Resolved(None, document)]
    resolved = []
    for entry in document.get("entry", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), dict):
            raise ValueError("every Bundle entry must carry a resource")
        full_url = entry.get("fullUrl")
        resolved.append(Resolved(full_url if isinstance(full_url, str) else None, entry["resource"]))
    return resolved


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def identifier_key(identifier: Any) -> tuple[str, str] | None:
    if not isinstance(identifier, dict):
        return None
    system, value = identifier.get("system"), identifier.get("value")
    if isinstance(system, str) and system and isinstance(value, str) and value:
        return system, value
    return None


def identifier_keys(resource: dict[str, Any]) -> set[tuple[str, str]]:
    identifiers = resource.get("identifier", [])
    if isinstance(identifiers, dict):
        identifiers = [identifiers]
    return {key for key in map(identifier_key, identifiers) if key}


def instant(value: Any) -> datetime | None:
    """A dateTime with seconds and an offset as an aware instant; anything less is no instant."""
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})", value
    ):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def member(node: Any, *path: str) -> Any:
    """The value at a path of object members, or None where any step is absent or not an object."""
    for name in path:
        if not isinstance(node, dict):
            return None
        node = node.get(name)
    return node


def members(node: Any, *path: str) -> list[Any]:
    value = member(node, *path)
    return value if isinstance(value, list) else []


def typed_input(task: dict[str, Any], system: str, code: str) -> dict[str, Any]:
    """The one input of a type, or an empty object when there is none or more than one."""
    matches = [
        entry
        for entry in members(task, "input")
        if isinstance(entry, dict)
        and any(
            isinstance(coding, dict) and coding.get("system") == system and coding.get("code") == code
            for coding in members(entry, "type", "coding")
        )
    ]
    return matches[0] if len(matches) == 1 else {}


def result_link(task: dict[str, Any]) -> str | None:
    outputs = members(task, "output")
    reference = member(outputs[0], "valueReference", "reference") if len(outputs) == 1 else None
    return reference if isinstance(reference, str) else None


def is_questionnaire(resource: dict[str, Any] | None) -> bool:
    """Whether a component revision or a Task carries the SDC complete-questionnaire code."""
    return any(
        isinstance(coding, dict) and coding.get("system") == SDC_SYSTEM
        and coding.get("code") == "complete-questionnaire"
        for coding in members(resource, "code", "coding")
    )


def actions(plan: dict[str, Any]) -> Iterator[dict[str, Any]]:
    for action in plan.get("action", []):
        if isinstance(action, dict):
            yield action
            yield from actions(action)


@dataclass(frozen=True)
class Occurrence:
    """What a receiver keeps for one accepted occurrence."""

    facts: str
    status: str
    content: str
    submission: tuple[str, str] | None
    result_id: str | None
    result_version: str | None
    result_authored: datetime | None = None


@dataclass
class TaskView:
    """One Task of a delivery with the parts graph validation reads."""

    task: Resolved
    key: tuple[str, str]
    label: str
    questionnaire: bool = False
    response: dict[str, Any] | None = None

    @property
    def resource(self) -> dict[str, Any]:
        return self.task.resource

    def facts(self) -> str:
        task = self.resource
        return canonical_json({
            "for": identifier_key(member(task, "for", "identifier")),
            "enrollment": identifier_key(member(typed_input(task, PARAMETER_SYSTEM, "enrollment"), "valueReference", "identifier")),
            "component": task.get("instantiatesCanonical"),
            "protocol": typed_input(task, PARAMETER_SYSTEM, "protocol").get("valueCanonical"),
            "questionnaire": typed_input(task, SDC_SYSTEM, "questionnaire").get("valueCanonical"),
            "window": typed_input(task, PARAMETER_SYSTEM, "performance-window").get("valuePeriod"),
            "authoredOn": task.get("authoredOn"),
        })

    def content(self) -> str:
        return canonical_json({k: v for k, v in self.resource.items() if k not in {"id", "meta", "text"}})


class Definitions:
    """The canonical resources and enrollments a delivery's Tasks resolve against."""

    def __init__(self, resources: Sequence[Resolved]) -> None:
        self.canonical: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self.enrollments: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self.patients: dict[str, dict[str, Any]] = {}
        for item in resources:
            resource = item.resource
            kind = resource.get("resourceType")
            url, version = resource.get("url"), resource.get("version")
            if kind in {"PlanDefinition", "ActivityDefinition", "Questionnaire"} and url and version:
                self.canonical.setdefault((kind, f"{url}|{version}"), []).append(resource)
            if kind == "ResearchSubject":
                for key in identifier_keys(resource):
                    self.enrollments.setdefault(key, []).append(resource)
            if kind == "Patient":
                for address in self._addresses(item):
                    self.patients[address] = resource

    @staticmethod
    def _addresses(item: Resolved) -> set[str]:
        addresses = {f"{item.resource.get('resourceType')}/{item.resource.get('id')}"}
        if item.full_url:
            addresses.add(item.full_url)
        return addresses

    def one(self, kind: str, canonical: Any) -> dict[str, Any] | None:
        """The resource a canonical names, when every copy of it has the same content."""
        found = self.canonical.get((kind, canonical), []) if isinstance(canonical, str) else []
        return found[0] if found and len({canonical_json(item) for item in found}) == 1 else None

    def enrollment(self, key: tuple[str, str] | None) -> dict[str, Any] | None:
        found = self.enrollments.get(key, []) if key else []
        return found[0] if found and len({canonical_json(item) for item in found}) == 1 else None

    def subject_keys(self, reference: Any) -> set[tuple[str, str]]:
        """Every complete identifier a reference states or its resolved Patient carries."""
        if not isinstance(reference, dict):
            return set()
        keys = {key for key in [identifier_key(reference.get("identifier"))] if key}
        literal = reference.get("reference")
        if isinstance(literal, str) and literal in self.patients:
            keys |= identifier_keys(self.patients[literal])
        return keys


def resolve_result(view: TaskView, responses: Sequence[Resolved]) -> dict[str, Any] | None:
    """The one response version a version-specific result link names in this delivery."""
    match = RESULT_REFERENCE.match(result_link(view.resource) or "")
    if match is None:
        return None
    identifier, version = match.group("id"), match.group("version")
    base = match.group("base")
    task_url = view.task.full_url or ""
    if base is None and re.match(r"^https?://", task_url) and "/Task/" in task_url:
        base = task_url.rsplit("/Task/", 1)[0]

    def addressed(full_url: str | None) -> bool:
        # A RESTful base resolves the reference to one fullUrl. Without one, the reference resolves
        # by type and id to a response that has no RESTful fullUrl of its own.
        if base is not None:
            return full_url == f"{base}/QuestionnaireResponse/{identifier}"
        return full_url is None or not re.match(r"^https?://", full_url)

    candidates = [
        item.resource
        for item in responses
        if item.resource.get("id") == identifier
        and member(item.resource, "meta", "versionId") == version
        and addressed(item.full_url)
    ]
    return candidates[0] if len(candidates) == 1 else None


def references_task(reference: Any) -> bool:
    if not isinstance(reference, dict):
        return False
    literal = reference.get("reference")
    return reference.get("type") == "Task" or (
        isinstance(literal, str) and re.search(r"(^|/)Task/[^/]+", literal) is not None
    )


def check_delivery(
    definitions: Sequence[Resolved], delivery: Sequence[Resolved]
) -> tuple[list[Issue], list[TaskView]]:
    """Every graph issue of one delivery, independent of earlier deliveries."""
    index = Definitions([*definitions, *delivery])
    responses = [item for item in delivery if item.resource.get("resourceType") == "QuestionnaireResponse"]
    views = []
    for item in delivery:
        if item.resource.get("resourceType") != "Task":
            continue
        keys = identifier_keys(item.resource)
        if len(keys) != 1:
            raise ValueError(
                f"Task/{item.resource.get('id')} has no single complete occurrence identifier; "
                "validate it against its profile first"
            )
        key = next(iter(keys))
        views.append(TaskView(item, key, key[1]))
    issues: list[Issue] = []

    for item in responses:
        if any(references_task(reference) for reference in members(item.resource, "partOf")):
            issues.append(Issue(
                "study-task-result-part-of", f"QuestionnaireResponse/{item.resource.get('id')}",
                "a response never references its occurrence through partOf; the Task links the response",
            ))
    seen: dict[tuple[str, str], int] = {}
    for view in views:
        seen[view.key] = seen.get(view.key, 0) + 1
    for key, count in sorted(seen.items()):
        if count > 1:
            issues.append(Issue("study-task-duplicate-occurrence", key[1], f"{count} Tasks carry this occurrence identifier"))

    linked: dict[tuple[str, str], list[str]] = {}
    for view in views:
        issues.extend(check_task(view, index, responses))
        if view.response is not None:
            submission = identifier_key(view.response.get("identifier"))
            if submission:
                linked.setdefault(submission, []).append(view.label)
    for submission, labels in sorted(linked.items()):
        if len(labels) > 1:
            issues.append(Issue(
                "study-task-result-shared", ", ".join(sorted(labels)),
                f"response {submission[1]} is linked by more than one occurrence",
            ))
    return sorted(set(issues)), views


def check_task(view: TaskView, index: Definitions, responses: Sequence[Resolved]) -> list[Issue]:
    task, label = view.resource, view.label
    issues: list[Issue] = []

    def report(rule: str, message: str) -> None:
        issues.append(Issue(rule, label, message))

    subject = identifier_key(member(task, "for", "identifier"))
    component_canonical = task.get("instantiatesCanonical")
    component = index.one("ActivityDefinition", component_canonical)
    if component is None:
        report("study-task-definition", f"component revision {component_canonical!r} resolves to no single ActivityDefinition")

    protocol_canonical = typed_input(task, PARAMETER_SYSTEM, "protocol").get("valueCanonical")
    protocol = index.one("PlanDefinition", protocol_canonical)
    if protocol is None or not any(
        action.get("definitionCanonical") == component_canonical for action in actions(protocol)
    ):
        report("study-task-protocol", f"protocol revision {protocol_canonical!r} has no action assigning {component_canonical!r}")

    enrollment_key = identifier_key(member(typed_input(task, PARAMETER_SYSTEM, "enrollment"), "valueReference", "identifier"))
    enrollment = index.enrollment(enrollment_key)
    if enrollment is None or subject not in index.subject_keys(enrollment.get("individual")):
        report("study-task-enrollment", f"enrollment {enrollment_key!r} resolves to no single ResearchSubject of this participant")

    window = typed_input(task, PARAMETER_SYSTEM, "performance-window").get("valuePeriod")
    start, end = instant(member(window, "start")), instant(member(window, "end"))
    status = task.get("status")
    if status == "cancelled":
        stopped = instant(task.get("lastModified"))
        if end is None or stopped is None or stopped > end:
            report("study-task-cancelled-after-window", "a cancelled occurrence was last modified after its window ended")

    # A component revision or a Task with the complete-questionnaire code makes the occurrence a
    # questionnaire occurrence. Any other occurrence completes without an output.
    view.questionnaire = is_questionnaire(component) or is_questionnaire(task)
    if not view.questionnaire:
        # Without a resolved component the kind is unknown; study-task-definition already rejects it.
        if component is None:
            return issues
        if members(task, "output"):
            report("study-task-output", "the component revision defines no result, so the occurrence carries no output")
        # Without a result, lastModified is when the status became completed.
        if status == "completed":
            completed = instant(task.get("lastModified"))
            if start is None or end is None or completed is None or completed < start or completed > end:
                report("study-task-completion-window", "the occurrence was not completed within its performance window")
        if any(
            isinstance(coding, dict) and coding.get("system") == SDC_SYSTEM and coding.get("code") == "questionnaire"
            for entry in members(task, "input") for coding in members(entry, "type", "coding")
        ):
            report("study-task-instrument", "the component revision administers no instrument, so the occurrence carries no questionnaire input")
        return issues
    issues.extend(check_questionnaire(view, component, index, responses, subject, start, end))
    return issues


def check_questionnaire(
    view: TaskView,
    component: dict[str, Any] | None,
    index: Definitions,
    responses: Sequence[Resolved],
    subject: tuple[str, str] | None,
    start: datetime | None,
    end: datetime | None,
) -> list[Issue]:
    """The instrument and result issues of one questionnaire occurrence."""
    task, label = view.resource, view.label
    issues: list[Issue] = []

    def report(rule: str, message: str) -> None:
        issues.append(Issue(rule, label, message))

    questionnaire_canonical = typed_input(task, SDC_SYSTEM, "questionnaire").get("valueCanonical")
    pinned = None
    if component is not None:
        pinned = [
            artifact.get("resource")
            for artifact in members(component, "relatedArtifact")
            if isinstance(artifact, dict) and artifact.get("type") == "depends-on"
        ]
    instrument = index.one("Questionnaire", questionnaire_canonical)
    if instrument is None or (pinned is not None and pinned != [questionnaire_canonical]):
        report("study-task-instrument", f"instrument {questionnaire_canonical!r} is not the one resolvable instrument of the component revision")

    if task.get("status") != "completed":
        return issues
    response = resolve_result(view, responses)
    if response is None:
        report("study-task-result-reference", f"result link {result_link(task)!r} resolves to no single response version in the delivery")
        return issues
    view.response = response
    if subject is None or subject not in index.subject_keys(response.get("subject")):
        report("study-task-result-subject", "the linked response is about another participant")
    if response.get("questionnaire") != questionnaire_canonical:
        report("study-task-result-instrument", f"the linked response answers {response.get('questionnaire')!r}")
    if response.get("status") not in ACCEPTED_RESPONSE_STATUSES:
        report("study-task-result-status", f"a {response.get('status')!r} response is not an accepted completion")
    # authored is when the answers last changed, so an amended version records the correction time:
    # it can lie after the window, never before it opened.
    authored = instant(response.get("authored"))
    latest = end if response.get("status") != "amended" else None
    if start is None or end is None or authored is None or authored < start or (latest is not None and authored > latest):
        report("study-task-result-window", "the linked response was not authored within the performance window")
    if instrument is not None and response.get("questionnaire") == questionnaire_canonical:
        for issue in PAIR.validate_pair(instrument, response):
            if issue.severity == "error":
                report(issue.rule, f"{issue.path}: {issue.message}")
    return issues


@dataclass
class DeliveryResult:
    outcomes: dict[str, str] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)

    @property
    def rejected(self) -> bool:
        return bool(self.issues)


class Receiver:
    """The accepted state of each occurrence across ordered deliveries."""

    def __init__(self, definitions: Sequence[Resolved]) -> None:
        self.definitions = list(definitions)
        self.occurrences: dict[tuple[str, str], Occurrence] = {}
        self.responses: dict[tuple[tuple[str, str], str], str] = {}
        self.linked_by: dict[tuple[str, str], tuple[str, str]] = {}

    def apply(self, delivery: Sequence[Resolved]) -> DeliveryResult:
        issues, views = check_delivery(self.definitions, delivery)
        result = DeliveryResult(issues=list(issues))
        if issues:
            return result
        occurrences: dict[tuple[str, str], Occurrence] = {}
        responses: dict[tuple[tuple[str, str], str], str] = {}
        linked_by: dict[tuple[str, str], tuple[str, str]] = {}
        for view in views:
            submission = identifier_key(view.response.get("identifier")) if view.response else None
            version = member(view.response, "meta", "versionId")
            result_id = member(view.response, "id")
            current = Occurrence(
                view.facts(), str(view.resource.get("status", "")), view.content(), submission, result_id, version,
                instant(member(view.response, "authored")),
            )
            outcome, rule = self.transition(
                self.occurrences.get(view.key), current, view.response, view.questionnaire
            )
            if submission and version and not rule:
                stored = self.responses.get((submission, version))
                content = canonical_json(view.response)
                owner = self.linked_by.get(submission)
                if stored is not None and stored != content:
                    outcome, rule = "an accepted response version repeats with different content", "study-task-altered-result"
                elif owner is not None and owner != view.key:
                    outcome, rule = "the response already completes another occurrence", "study-task-result-shared"
                responses[(submission, version)] = content
                linked_by[submission] = view.key
            if rule:
                result.issues.append(Issue(rule, view.label, outcome))
            else:
                result.outcomes[view.label] = outcome
                occurrences[view.key] = current
        if result.issues:
            result.outcomes = {}
            result.issues.sort()
            return result
        self.occurrences.update(occurrences)
        self.responses.update(responses)
        self.linked_by.update(linked_by)
        return result

    @staticmethod
    def transition(
        prior: Occurrence | None,
        current: Occurrence,
        response: dict[str, Any] | None,
        questionnaire: bool,
    ) -> tuple[str, str | None]:
        """The outcome for one occurrence, or the message and rule that reject it."""
        completing = current.status == "completed" and (prior is None or prior.status == "ready")
        if questionnaire and completing and (response or {}).get("status") != "completed":
            return "the first accepted result of an occurrence is a completed response", "study-task-result-status"
        if prior is None:
            return "accepted", None
        if prior.facts != current.facts:
            return "the occurrence identifier is already assigned with other facts", "study-task-occurrence-conflict"
        if prior.content == current.content:
            return "replayed", None
        if prior.status == "ready" and current.status in {"completed", "cancelled"}:
            return "accepted", None
        if prior.status == "completed" and current.status == "completed":
            if current.submission != prior.submission:
                return "the occurrence is already completed by another response", "study-task-completion-conflict"
            if current.result_id != prior.result_id:
                return "a correction is a new version of the same response resource", "study-task-correction"
            if current.result_version == prior.result_version:
                return "the accepted occurrence repeats with different content", "study-task-altered-replay"
            if (response or {}).get("status") != "amended":
                return "a corrected response must carry the status amended", "study-task-correction"
            if (
                current.result_authored is None
                or prior.result_authored is None
                or current.result_authored < prior.result_authored
            ):
                return "a correction is authored at or after the version it corrects", "study-task-correction"
            return "corrected", None
        if prior.status == current.status:
            return "the accepted occurrence repeats with different content", "study-task-altered-replay"
        return f"{prior.status} cannot become {current.status}", "study-task-status-transition"


def load(path: Path) -> list[Resolved]:
    try:
        return resources_of(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {path}: {error}") from error


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--definitions", required=True, type=Path, action="append",
                        help="a Bundle or resource with protocol, component, instrument, and enrollment resources")
    parser.add_argument("deliveries", nargs="+", type=Path, help="deliveries in the order they arrived")
    arguments = parser.parse_args(argv)
    try:
        definitions = [item for path in arguments.definitions for item in load(path)]
        deliveries = [(path, load(path)) for path in arguments.deliveries]
    except ValueError as error:
        parser.error(str(error))
    receiver = Receiver(definitions)
    rejected = False
    for path, delivery in deliveries:
        try:
            result = receiver.apply(delivery)
        except ValueError as error:
            parser.error(f"{path}: {error}")
        if result.rejected:
            rejected = True
            for issue in result.issues:
                print(f"{path}: REJECTED {issue.rule} {issue.occurrence}: {issue.message}")
        else:
            for occurrence, outcome in sorted(result.outcomes.items()):
                print(f"{path}: {outcome} {occurrence}")
    return int(rejected)


if __name__ == "__main__":
    raise SystemExit(main())
