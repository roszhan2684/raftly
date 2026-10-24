"""Canonical Raftly enums, ID formats and transition rules.

Schemas in ``schemas/`` mirror these values; ``tests/test_model_schema_sync.py``
keeps the two in sync.
"""

from __future__ import annotations

import re

MODES = [
    "GREENFIELD",
    "BUILD",
    "REVIEW",
    "RECOVERY",
    "MIGRATION",
    "SCALE",
    "LAUNCH",
    "OPERATE",
    "HANDOFF",
    "DOCTOR",
]

# Ordered lifecycle. ASSESSMENT is the entry stage for existing repositories.
STAGES = [
    "INTAKE",
    "ASSESSMENT",
    "RESEARCH",
    "PRODUCT",
    "DESIGN",
    "ARCHITECTURE",
    "PLANNING",
    "BLUEPRINT_COMPLETE",
    "BUILDING",
    "VERIFYING",
    "LAUNCH_READINESS",
    "LAUNCHED",
    "OPERATING",
]

# Stages that may only be entered when a deterministic gate passes.
GATED_STAGES = {"BLUEPRINT_COMPLETE", "LAUNCHED"}

BLUEPRINT_SECTION_STATUSES = ["NOT_STARTED", "IN_PROGRESS", "COMPLETE", "NOT_APPLICABLE"]
BLUEPRINT_SECTIONS = ["product", "design", "architecture", "data", "security", "build"]
BLUEPRINT_STATUSES = ["NOT_STARTED", "IN_PROGRESS", "COMPLETE"]

WORK_STATUSES = [
    "NOT_STARTED",
    "PLANNED",
    "IN_PROGRESS",
    "PARTIAL",
    "BLOCKED",
    "IMPLEMENTED_UNVERIFIED",
    "VERIFIED",
    "COMPLETE",
    "DROPPED",
]
DONE_STATUSES = {"VERIFIED", "COMPLETE"}
TERMINAL_STATUSES = {"COMPLETE", "DROPPED"}

GATE_STATUSES = ["PASS", "WARNING", "FAIL", "UNVERIFIED", "NOT_APPLICABLE"]
GATE_SEVERITIES = ["blocker", "major", "minor"]
READINESS_LEVELS = ["NOT_READY", "INSUFFICIENT_EVIDENCE", "READY_WITH_WARNINGS", "READY", "UNVERIFIED"]

DECISION_TYPES = ["AUTO", "RECOMMEND", "FOUNDER"]
DECISION_STATUSES = ["PROPOSED", "ACCEPTED", "SUPERSEDED", "REJECTED", "DEPRECATED"]
LEVELS = ["low", "medium", "high"]

ASSUMPTION_STATES = ["UNTESTED", "SUPPORTED", "INVALIDATED"]
RISK_CATEGORIES = [
    "product",
    "technical",
    "security",
    "privacy",
    "compliance",
    "legal",
    "vendor",
    "cost",
    "scale",
    "ux",
    "operational",
    "business",
]
RISK_STATUSES = ["OPEN", "MITIGATING", "ACCEPTED", "CLOSED"]
DEBT_TYPES = ["intentional_shortcut", "temporary_workaround", "accepted_debt", "defect", "architecture_violation"]
DEBT_STATUSES = ["OPEN", "SCHEDULED", "RESOLVED", "WONT_FIX"]
REQUIREMENT_PRIORITIES = ["MUST", "SHOULD", "COULD", "WONT"]
REQUIREMENT_STATUSES = ["ACTIVE", "SUPERSEDED", "DROPPED"]
DEPENDENCY_STATUSES = ["PROPOSED", "ADOPTED", "REJECTED", "REMOVED"]

LEARNING_OUTCOMES = ["REJECT", "PROJECT_ONLY", "CANDIDATE", "CORE_PROPOSAL"]

EVIDENCE_KINDS = ["test", "e2e", "manual", "review", "metric", "audit", "build", "lint", "research", "doc"]
VERIFICATION_KINDS = {"test", "e2e", "manual", "review", "metric", "audit"}
EVIDENCE_RESULTS = ["PASS", "FAIL", "INFO"]
LINK_RELATIONS = [
    "justifies",  # requirement/decision -> thing it motivates
    "implements",  # implementation -> requirement/feature
    "verifies",  # test -> feature/requirement/api
    "depends_on",
    "measures",  # metric -> feature/assumption
    "renders",  # screen/component -> feature
    "persists",  # table -> feature/entity
    "exposes",  # api -> feature
    "supersedes",
    "mitigates",  # feature/decision -> risk
    "validates",  # evidence/metric -> assumption
]

# Registered record ID formats. Prefix -> regex.
ID_PATTERNS = {
    "requirement": r"^REQ-\d{3,}$",
    "assumption": r"^A-\d{3,}$",
    "risk": r"^R-\d{3,}$",
    "decision": r"^ADR-\d{3,}$",
    "feature": r"^F\d{3,}$",
    "node": r"^N\d{3,}$",
    "debt": r"^DEBT-\d{3,}$",
    "learning": r"^L-\d{3,}$",
    "candidate": r"^LC-\d{3,}$",
    "postmortem": r"^PM-\d{3,}$",
    "evidence": r"^EV-\d{3,}$",
    "experiment": r"^EXP-\d{3,}$",
}
ID_FORMATS = {
    "requirement": ("REQ-", 3),
    "assumption": ("A-", 3),
    "risk": ("R-", 3),
    "decision": ("ADR-", 3),
    "feature": ("F", 3),
    "node": ("N", 3),
    "debt": ("DEBT-", 3),
    "learning": ("L-", 3),
    "candidate": ("LC-", 3),
    "postmortem": ("PM-", 3),
    "evidence": ("EV-", 3),
    "experiment": ("EXP-", 3),
}
# Free-form implementation entities that live in evidence.yaml ``entities``.
ENTITY_PREFIXES = {
    "SCR": "screen",
    "CMP": "component",
    "API": "api",
    "SVC": "service",
    "TBL": "table",
    "TEST": "test",
    "MET": "metric",
    "JOB": "job",
    "INT": "integration",
}
ENTITY_ID_RE = re.compile(r"^(SCR|CMP|API|SVC|TBL|TEST|MET|JOB|INT)-[A-Za-z0-9_.-]+$")


def kind_of_id(identifier: str) -> str | None:
    for kind, pat in ID_PATTERNS.items():
        if re.match(pat, identifier):
            return kind
    m = ENTITY_ID_RE.match(identifier)
    if m:
        return ENTITY_PREFIXES[m.group(1)]
    return None


def format_id(kind: str, number: int) -> str:
    prefix, width = ID_FORMATS[kind]
    return f"{prefix}{number:0{width}d}"


def id_number(identifier: str) -> int:
    m = re.search(r"(\d+)$", identifier)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Transition rules
# ---------------------------------------------------------------------------


def stage_transition_problem(current: str, target: str) -> str | None:
    """Return a reason string if moving current -> target is not allowed.

    Gate checks (blueprint completeness, launch readiness) are enforced by the
    caller because they need project data.
    """
    if target not in STAGES:
        return f"unknown stage {target!r}"
    if current not in STAGES:
        return None  # legacy/unknown state: allow re-anchoring
    if target == current:
        return None
    if target == "INTAKE":
        return "cannot return to INTAKE; record a requirement change instead"
    ci, ti = STAGES.index(current), STAGES.index(target)
    if target == "LAUNCHED" and current not in ("LAUNCH_READINESS", "OPERATING"):
        return "LAUNCHED can only be entered from LAUNCH_READINESS (run /raftly launch first)"
    if target == "OPERATING" and current not in ("LAUNCHED",) and ci < STAGES.index("LAUNCHED"):
        return "OPERATING requires a launched product"
    if ti > ci and current not in ("ASSESSMENT",) and STAGES.index("BUILDING") <= ti and ci < STAGES.index(
        "BLUEPRINT_COMPLETE"
    ):
        return "building/verification stages require BLUEPRINT_COMPLETE first"
    return None


def work_transition_problem(current: str, target: str, *, has_verification: bool, has_blockers: bool) -> str | None:
    """Rules for feature/node status changes. Returns a reason or None."""
    if target not in WORK_STATUSES:
        return f"unknown status {target!r}"
    if target == current:
        return None
    if target == "BLOCKED" and not has_blockers:
        return "BLOCKED requires at least one recorded blocker"
    if target == "VERIFIED" and not has_verification:
        return "VERIFIED requires a passing verification evidence record (test/e2e/manual/review/metric/audit)"
    if target == "COMPLETE":
        if current != "VERIFIED":
            return "COMPLETE requires the item to be VERIFIED first"
        if not has_verification:
            return "COMPLETE requires passing verification evidence"
    return None
