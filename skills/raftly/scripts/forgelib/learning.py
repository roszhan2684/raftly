"""Learning Firewall: classify observations and sanitize proposals.

Outcomes (Constitution 18-21):
  REJECT         noisy, incorrect or unsupported
  PROJECT_ONLY   preference or local fact; stays in this project
  CANDIDATE      potentially generalizable; collect more evidence
  CORE_PROPOSAL  strong enough to propose to Raftly maintainers (never auto-applied)

Classification is deterministic so the same inputs always yield the same
outcome and the reasoning can be shown to the user.
"""

from __future__ import annotations

import re

QUALITY = {"none": 0, "anecdotal": 1, "observed": 2, "reproduced": 3, "tested": 4}
AUTHORITY = {"none": 0, "user": 1, "project": 1, "community": 2, "official_docs": 3, "standard": 4}


def classify(obs: dict) -> dict:
    """Return {"outcome", "credibility", "reasons"} for an observation.

    Expected keys (all optional except kind): kind, evidence_quality,
    source_authority, repeat_count, cross_project, objective, contradicted,
    contains_private.
    """
    kind = obs.get("kind", "implementation_finding")
    q = QUALITY.get(obs.get("evidence_quality", "none"), 0)
    a = AUTHORITY.get(obs.get("source_authority", "none"), 0)
    repeats = int(obs.get("repeat_count", 0) or 0)
    cross = bool(obs.get("cross_project"))
    objective = bool(obs.get("objective"))
    contradicted = bool(obs.get("contradicted"))
    private = bool(obs.get("contains_private"))
    reasons: list[str] = []

    credibility = q * 10 + a * 8 + min(repeats, 5) * 4 + (10 if cross else 0) + (10 if objective else 0)
    if contradicted:
        credibility -= 25
    credibility = max(0, min(100, credibility))

    if kind in ("preference", "override"):
        reasons.append("user preferences and overrides are not universal best practice (rule 18)")
        return {"outcome": "PROJECT_ONLY", "credibility": credibility, "reasons": reasons}
    if kind == "local_fact":
        reasons.append("local fact about this project")
        return {"outcome": "PROJECT_ONLY", "credibility": credibility, "reasons": reasons}
    if q == 0 and a == 0:
        reasons.append("no evidence and no authoritative source")
        return {"outcome": "REJECT", "credibility": credibility, "reasons": reasons}
    if contradicted and q < QUALITY["tested"]:
        reasons.append("contradicted by other evidence and not verified by tests")
        return {"outcome": "PROJECT_ONLY" if q >= 2 else "REJECT", "credibility": credibility, "reasons": reasons}
    if not objective:
        reasons.append("not objectively verifiable; kept as project knowledge")
        return {"outcome": "PROJECT_ONLY", "credibility": credibility, "reasons": reasons}
    if not cross:
        reasons.append("no evidence of relevance beyond this project")
        return {"outcome": "PROJECT_ONLY", "credibility": credibility, "reasons": reasons}

    strong_source = a >= AUTHORITY["official_docs"]
    if q >= QUALITY["tested"] and (repeats >= 2 or strong_source) and not contradicted:
        if private:
            reasons.append("would qualify for a core proposal, but contains private project detail: sanitize first")
            return {"outcome": "CANDIDATE", "credibility": credibility, "reasons": reasons}
        reasons.append("tested, repeatable or authoritatively sourced, cross-project, uncontradicted")
        return {"outcome": "CORE_PROPOSAL", "credibility": credibility, "reasons": reasons}
    if q >= QUALITY["observed"] or strong_source:
        reasons.append("objective and cross-project but needs more evidence before a core proposal")
        return {"outcome": "CANDIDATE", "credibility": credibility, "reasons": reasons}
    reasons.append("evidence too weak to generalize")
    return {"outcome": "PROJECT_ONLY", "credibility": credibility, "reasons": reasons}


_PATTERNS = {
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "absolute user path": re.compile(r"(/Users/|/home/|[A-Z]:\\Users\\)[^\s]+"),
    "secret-like token": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S{6,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}"),
    "private URL": re.compile(r"https?://(localhost|127\.0\.0\.1|10\.|192\.168\.|[^\s/]*\.(internal|local|corp))[^\s]*"),
    "IP address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}


def leak_scan(text: str, project_terms: list[str]) -> list[str]:
    """Find content that must not leave the project (rule 20)."""
    hits = []
    for label, pat in _PATTERNS.items():
        for m in pat.finditer(text):
            hits.append(f"{label}: {m.group(0)[:60]}")
    lowered = text.lower()
    for term in project_terms:
        t = term.strip().lower()
        if len(t) >= 4 and t in lowered:
            hits.append(f"project identifier: {term}")
    return hits
