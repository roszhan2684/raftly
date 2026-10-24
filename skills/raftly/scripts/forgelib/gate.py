"""Production gate: applicability, evidence-gated status changes, scoring.

Scoring (documented in skills/forge/references/production-gate.md):

* Only the ``production`` group counts toward readiness. ``forgotten-20`` is a
  separate audit so items are not double-counted.
* Severity weights: blocker=3, major=2, minor=1.
* Status values: PASS=1.0, WARNING=0.5, FAIL=0.0. UNVERIFIED and
  NOT_APPLICABLE are excluded from the score.
* coverage = verified weight / applicable weight (verified = PASS/WARNING/FAIL).
* score = sum(weight*value) / verified weight, only reported when coverage >= 0.6.
* readiness:
    NOT_READY             any blocker FAIL
    INSUFFICIENT_EVIDENCE coverage < 0.6, or any blocker UNVERIFIED
    READY_WITH_WARNINGS   no blocker FAIL/UNVERIFIED, but any WARNING/FAIL/UNVERIFIED remains
    READY                 every applicable check PASS
"""

from __future__ import annotations

from .fsutil import SKILL_ROOT
from . import yamlio

SEVERITY_WEIGHT = {"blocker": 3, "major": 2, "minor": 1}
STATUS_VALUE = {"PASS": 1.0, "WARNING": 0.5, "FAIL": 0.0}
COVERAGE_THRESHOLD = 0.6
UI_SURFACES = {"web", "ios", "android", "mobile", "desktop", "extension"}
FLAGS = {
    "backend",
    "accounts",
    "personal_data",
    "payments",
    "multi_tenant",
    "ai",
    "public_site",
    "email",
    "file_uploads",
    "integrations",
    "analytics",
}


class GateExpressionError(ValueError):
    pass


def catalog(group: str) -> list[dict]:
    name = "production-gate.yaml" if group == "production" else "forgotten-20.yaml"
    data = yamlio.load_file(SKILL_ROOT / "core" / name)
    return data["checks"]


def _term(term: str, profile: dict) -> bool:
    term = term.strip()
    neg = False
    if term.startswith("not "):
        neg, term = True, term[4:].strip()
    surfaces = set(profile.get("surfaces") or [])
    if term == "always":
        val = True
    elif term == "ui":
        val = bool(surfaces & UI_SURFACES)
    elif term.startswith("surface:"):
        val = term.split(":", 1)[1] in surfaces
    elif term.startswith("sensitive:"):
        cls = term.split(":", 1)[1]
        sens = set(profile.get("sensitive_data") or [])
        val = bool(sens) if cls == "any" else cls in sens
    elif term.startswith("regulated:"):
        reg = term.split(":", 1)[1]
        regs = {r.lower() for r in (profile.get("regulated") or [])}
        val = bool(regs) if reg == "any" else reg.lower() in regs
    elif term in FLAGS:
        val = bool(profile.get(term))
    else:
        raise GateExpressionError(f"unknown applies_when term: {term!r}")
    return (not val) if neg else val


def applies(expr: str, profile: dict) -> bool:
    """Evaluate an ``applies_when`` expression: OR of AND-groups."""
    return any(all(_term(t, profile) for t in group.split(" and ")) for group in expr.split(" or "))


def instantiate(profile: dict, existing: list[dict] | None = None, now: str | None = None) -> list[dict]:
    """Build the project's check list from the catalogs.

    Existing statuses/evidence are preserved for checks that still apply, so
    re-running after a profile change never discards recorded evidence.
    """
    prev = {c["id"]: c for c in (existing or [])}
    out = []
    for group in ("production", "forgotten-20"):
        for item in catalog(group):
            applicable = applies(item["applies_when"], profile)
            old = prev.get(item["id"])
            check = {
                "id": item["id"],
                "group": group,
                "category": item["category"],
                "title": item["title"],
                "severity": item["severity"],
                "status": "UNVERIFIED",
                "evidence": [],
                "updated_at": now,
            }
            if not applicable:
                check["status"] = "NOT_APPLICABLE"
                check["na_reason"] = f"profile does not match: {item['applies_when']}"
            elif old:
                auto_na = old.get("status") == "NOT_APPLICABLE" and str(old.get("na_reason", "")).startswith(
                    "profile does not match"
                )
                if not auto_na:  # keep recorded statuses, evidence and manual N/A decisions
                    for k in ("status", "evidence", "note", "na_reason", "updated_at"):
                        if k in old:
                            check[k] = old[k]
            out.append(check)
    # keep project-specific custom checks (ids not in catalog)
    known = {c["id"] for c in out}
    for cid, old in prev.items():
        if cid not in known:
            out.append(old)
    return out


def set_status_problem(check: dict, status: str, evidence: list[str], na_reason: str | None, known_evidence: set[str]) -> str | None:
    if status not in ("PASS", "WARNING", "FAIL", "UNVERIFIED", "NOT_APPLICABLE"):
        return f"unknown gate status {status!r}"
    if status in ("PASS", "WARNING"):
        if not evidence:
            return f"{status} requires at least one evidence id (EV-xxx). Constitution rule 15: no evidence, no PASS."
        missing = [e for e in evidence if e not in known_evidence]
        if missing:
            return f"unknown evidence id(s): {', '.join(missing)}"
    if status == "NOT_APPLICABLE":
        if not na_reason:
            return "NOT_APPLICABLE requires a reason (e.g. 'decision: ADR-004 no server component')"
        if check["severity"] == "blocker" and not na_reason.startswith("decision:"):
            return "a blocker check can only be marked NOT_APPLICABLE by citing a decision ('decision: ADR-xxx ...')"
    return None


def score(checks: list[dict], group: str = "production") -> dict:
    items = [c for c in checks if c.get("group", "production") == group and c["status"] != "NOT_APPLICABLE"]
    applicable_w = sum(SEVERITY_WEIGHT[c["severity"]] for c in items)
    verified = [c for c in items if c["status"] in STATUS_VALUE]
    verified_w = sum(SEVERITY_WEIGHT[c["severity"]] for c in verified)
    got = sum(SEVERITY_WEIGHT[c["severity"]] * STATUS_VALUE[c["status"]] for c in verified)
    coverage = round(verified_w / applicable_w, 3) if applicable_w else None
    blocker_fail = [c["id"] for c in items if c["severity"] == "blocker" and c["status"] == "FAIL"]
    blocker_unverified = [c["id"] for c in items if c["severity"] == "blocker" and c["status"] == "UNVERIFIED"]
    counts: dict[str, int] = {}
    for c in checks:
        if c.get("group", "production") == group:
            counts[c["status"]] = counts.get(c["status"], 0) + 1
    if not items:
        readiness = "UNVERIFIED"
    elif blocker_fail:
        readiness = "NOT_READY"
    elif coverage is not None and coverage < COVERAGE_THRESHOLD or blocker_unverified:
        readiness = "INSUFFICIENT_EVIDENCE"
    elif all(c["status"] == "PASS" for c in items):
        readiness = "READY"
    else:
        readiness = "READY_WITH_WARNINGS"
    show_score = coverage is not None and coverage >= COVERAGE_THRESHOLD and verified_w > 0
    return {
        "group": group,
        "readiness": readiness,
        "score": round(got / verified_w, 3) if show_score else None,
        "coverage": coverage,
        "counts": counts,
        "blocker_failures": blocker_fail,
        "blocker_unverified": blocker_unverified,
        "applicable": len(items),
    }
