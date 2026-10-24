#!/usr/bin/env python3
"""Render a self-contained static HTML product blueprint from .raftly/ state.

The blueprint is a *view* of canonical Raftly data, never a competing source of
truth: every number and status is derived from .raftly files, and missing data is
shown as an explicit empty state rather than invented.

  render_blueprint.py [--root DIR] [--out artifacts/blueprint.html]
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import FORGE_VERSION, cli, docs, graph, mdhtml, model  # noqa: E402
from forgelib.brand import name as brand_name  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.fsutil import SKILL_ROOT, assert_not_plugin_core, atomic_write, read_text  # noqa: E402
from forgelib.project import now_iso  # noqa: E402

E = html.escape

STATUS_CLASS = {
    "COMPLETE": "ok", "PASS": "ok", "VERIFIED": "ok", "SUPPORTED": "ok", "ACCEPTED": "ok", "CLOSED": "ok", "READY": "ok",
    "IN_PROGRESS": "info", "MITIGATING": "info", "PROPOSED": "info", "READY_WITH_WARNINGS": "warn",
    "PARTIAL": "warn", "WARNING": "warn", "IMPLEMENTED_UNVERIFIED": "warn", "OPEN": "warn", "UNTESTED": "warn",
    "INSUFFICIENT_EVIDENCE": "hatch",
    "BLOCKED": "bad", "FAIL": "bad", "INVALIDATED": "bad", "NOT_READY": "bad", "critical": "bad", "high": "bad",
    "medium": "warn", "low": "muted",
    "UNVERIFIED": "hatch", "PLANNED": "muted", "NOT_STARTED": "muted", "NOT_APPLICABLE": "muted", "DROPPED": "muted",
    "SUPERSEDED": "muted", "REJECTED": "muted", "DEPRECATED": "muted",
}
LABEL = {"NOT_APPLICABLE": "N/A", "IMPLEMENTED_UNVERIFIED": "IMPLEMENTED · UNVERIFIED",
         "READY_WITH_WARNINGS": "READY WITH WARNINGS", "INSUFFICIENT_EVIDENCE": "INSUFFICIENT EVIDENCE"}


def chip(status: str) -> str:
    cls = STATUS_CLASS.get(status, "muted")
    return f'<span class="status s-{cls}">{E(LABEL.get(status, status.replace("_", " ")))}</span>'


def doc(proj, name: str) -> str:
    p = proj.forge / name
    return read_text(p) if p.exists() else ""


def empty(msg: str) -> str:
    return f'<p class="empty">{E(msg)}</p>'


def meter(parts: list[tuple[float, str]], unverified: bool = False, label: str = "") -> str:
    if unverified:
        return f'<div class="meter unverified" role="img" aria-label="{E(label or "unverified")}"></div>'
    spans = "".join(f'<span class="m-{cls}" style="width:{max(0.0, min(100.0, pct)):.1f}%"></span>' for pct, cls in parts)
    return f'<div class="meter" role="img" aria-label="{E(label)}">{spans}</div>'


def svg_graph(nodes: list[dict]) -> str:
    if not nodes:
        return empty("No build graph yet. Raftly creates it during PLANNING (build-graph.yaml).")
    try:
        layers = graph.phases(nodes)
    except ValueError:
        return empty("Build graph has a dependency cycle; run build_graph.py validate.")
    idx = graph.index(nodes)
    W, H, GX, GY, PAD = 190, 50, 70, 22, 24
    pos = {}
    for li, layer in enumerate(layers):
        for ni, nid in enumerate(layer):
            pos[nid] = (PAD + li * (W + GX), PAD + 22 + ni * (H + GY))
    width = PAD * 2 + len(layers) * W + (len(layers) - 1) * GX
    height = PAD * 2 + 22 + max(len(layer) for layer in layers) * (H + GY) - GY
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
             f'role="img" aria-labelledby="g-title"><title id="g-title">Build graph: {len(nodes)} capabilities in {len(layers)} dependency phases</title>']
    for li in range(len(layers)):
        parts.append(f'<text class="phase-label" x="{PAD + li * (W + GX)}" y="{PAD + 8}">PHASE {li}</text>')
    for n in nodes:
        x2, y2 = pos[n["id"]]
        for d in n.get("depends_on", []):
            if d not in pos:
                continue
            x1, y1 = pos[d]
            sx, sy, ex, ey = x1 + W, y1 + H / 2, x2, y2 + H / 2
            mx = (sx + ex) / 2
            parts.append(f'<path class="edge" d="M{sx},{sy} C{mx},{sy} {mx},{ey} {ex},{ey}"/>')
    for nid, (x, y) in pos.items():
        n = idx[nid]
        cls = STATUS_CLASS.get(n["status"], "muted")
        cls = "muted" if cls == "hatch" else cls
        name = n["name"] if len(n["name"]) <= 24 else n["name"][:23] + "…"
        parts.append(
            f'<g class="node n-{cls}"><title>{E(nid)} {E(n["name"])}: {E(n["status"])}'
            f'{(" — depends on " + ", ".join(n.get("depends_on", []))) if n.get("depends_on") else ""}</title>'
            f'<rect x="{x}" y="{y}" width="{W}" height="{H}"/>'
            f'<text class="nid" x="{x + 10}" y="{y + 18}">{E(nid)} · {E(n["status"].replace("_", " ").lower())}</text>'
            f'<text x="{x + 10}" y="{y + 36}">{E(name)}</text></g>')
    parts.append("</svg>")
    return '<div class="graph-wrap">' + "".join(parts) + "</div>"


def build(proj) -> str:
    st = proj.state()
    p = st["project"]
    nodes = proj.registry("build-graph.yaml")
    reqs = proj.registry("requirements.yaml")
    feats = [fm for _, fm, _ in proj.records("feature")]
    decisions = proj.records("decision")
    risks = proj.registry("risks.yaml")
    assumptions = proj.registry("assumptions.yaml")
    deps = proj.registry("dependencies.yaml")
    gate = proj.gate()
    executive, product, design, arch, launch, security = (doc(proj, n) for n in (
        "EXECUTIVE.md", "PRODUCT.md", "DESIGN.md", "ARCHITECTURE.md", "LAUNCH.md", "SECURITY.md"))
    lede = (docs.first_paragraph(docs.find_section(executive, "What", "Summary", "Overview"))
            or docs.first_paragraph(docs.find_section(product, "Vision", "Problem"))
            or p.get("summary") or "Blueprint in progress.")

    css = read_text(SKILL_ROOT / "assets" / "blueprint.css")
    brand = proj.forge / "brand" / "tokens.json"
    if brand.exists():
        try:
            tokens = json.loads(read_text(brand))
            over = []
            for key, var in (("accent", "--accent"), ("accent_ink", "--accent-ink"), ("font", "--font")):
                val = str(tokens.get(key, "")).strip()
                if val and all(c not in val for c in ";{}<>"):
                    over.append(f"{var}: {val};")
            if over:
                css += "\n:root { " + " ".join(over) + " }"
        except ValueError:
            pass

    # --- overview stats
    prog = graph.progress(nodes) if nodes else None
    sc = gatelib.score(gate["checks"]) if gate else None
    bp = st["blueprint"]
    bp_done = sum(1 for s in model.BLUEPRINT_SECTIONS if bp.get(s) in ("COMPLETE", "NOT_APPLICABLE"))
    stats = []
    stats.append(f'<div class="stat"><div class="label">Blueprint</div><div class="value">{bp_done}/{len(model.BLUEPRINT_SECTIONS)}</div>'
                 f'<div class="hint">sections resolved · {chip(bp["status"])}</div>'
                 f'{meter([(100 * bp_done / len(model.BLUEPRINT_SECTIONS), "ok")], label=f"{bp_done} of 6 blueprint sections resolved")}</div>')
    if prog and prog["total"]:
        c, v = prog["complete_pct"] or 0, prog["verified_pct"] or 0
        stats.append(f'<div class="stat"><div class="label">Build</div><div class="value">{c:.0f}%</div>'
                     f'<div class="hint">complete · {v:.0f}% verified · {prog["total"]} nodes</div>'
                     f'{meter([(c, "ok"), (max(0, v - c), "info")], label=f"{c:.0f}% complete, {v:.0f}% verified")}</div>')
    else:
        stats.append('<div class="stat"><div class="label">Build</div><div class="value">—</div><div class="hint">no build graph yet</div>'
                     f'{meter([], unverified=True, label="no build graph")}</div>')
    if sc and sc["applicable"]:
        cov = sc["coverage"] or 0
        if sc["score"] is None:
            stats.append(f'<div class="stat"><div class="label">Production readiness</div><div class="value">{chip(sc["readiness"])}</div>'
                         f'<div class="hint">evidence covers {cov * 100:.0f}% of applicable checks — no score without evidence</div>'
                         f'{meter([], unverified=True, label="insufficient evidence")}</div>')
        else:
            stats.append(f'<div class="stat"><div class="label">Production readiness</div><div class="value">{sc["score"] * 100:.0f}%</div>'
                         f'<div class="hint">{chip(sc["readiness"])} · coverage {cov * 100:.0f}%</div>'
                         f'{meter([(sc["score"] * 100, "ok" if sc["readiness"] == "READY" else "warn")], label="readiness score")}</div>')
    else:
        stats.append('<div class="stat"><div class="label">Production readiness</div><div class="value">' + chip("UNVERIFIED") +
                     '</div><div class="hint">gate not evaluated</div>' + meter([], unverified=True, label="unverified") + "</div>")
    active_reqs = [r for r in reqs if r.get("status") == "ACTIVE"]
    stats.append(f'<div class="stat"><div class="label">Scope</div><div class="value">{len(active_reqs)}</div>'
                 f'<div class="hint">active requirements · {len(feats)} features · {len(decisions)} decisions</div></div>')

    sections_html = []
    nav = []

    def add(sid: str, title: str, sub: str, body: str):
        nav.append(f'<a href="#{sid}">{E(title)}</a>')
        sections_html.append(f'<section class="card" id="{sid}" aria-labelledby="{sid}-h"><h2 id="{sid}-h">{E(title)}</h2>'
                             f'<p class="sub">{E(sub)}</p>{body}</section>')

    bp_rows = "".join(f"<tr><td>{E(s.title())}</td><td>{chip(bp.get(s, 'NOT_STARTED'))}</td></tr>" for s in model.BLUEPRINT_SECTIONS)
    ofd = bp.get("open_founder_decisions") or []
    ofd_html = ("<h3>Open founder decisions</h3><ul>" + "".join(f"<li>{mdhtml.inline(x)}</li>" for x in ofd) + "</ul>") if ofd else ""
    add("overview", "Overview", "Where the product stands, derived from state.yaml, build-graph.yaml and gate.yaml.",
        f'<div class="grid k4">{"".join(stats)}</div><div class="grid k2" style="margin-top:14px"><div>'
        f'<div class="table-wrap"><table><caption>Blueprint sections</caption><thead><tr><th scope="col">Section</th><th scope="col">Status</th></tr></thead>'
        f'<tbody>{bp_rows}</tbody></table></div></div><div class="prose">{mdhtml.render(docs.find_section(executive, "Plan", "V1") or "", 3)}{ofd_html}</div></div>')

    # product
    prod_parts = []
    for heading in ("Problem", "ICP", "Users", "Positioning", "Differentiation"):
        sec = docs.find_section(product, heading)
        if sec:
            prod_parts.append(f"<div><h3>{E(heading)}</h3><div class='prose'>{mdhtml.render(sec, 4)}</div></div>")
    req_rows = "".join(
        f"<tr><td class='mono'>{E(r['id'])}</td><td>{mdhtml.inline(r['statement'])}</td><td>{E(r['priority'])}</td>"
        f"<td class='mono'>{E(', '.join(r.get('features') or []) or '—')}</td></tr>"
        for r in sorted(active_reqs, key=lambda r: (model.REQUIREMENT_PRIORITIES.index(r["priority"]), r["id"])))
    req_table = (f'<div class="table-wrap"><table><caption>Active requirements</caption><thead><tr><th scope="col">ID</th>'
                 f'<th scope="col">Requirement</th><th scope="col">Priority</th><th scope="col">Features</th></tr></thead>'
                 f'<tbody>{req_rows}</tbody></table></div>') if req_rows else empty("No requirements recorded yet.")
    add("product", "Product", "From PRODUCT.md and requirements.yaml.",
        (f'<div class="grid k2">{"".join(prod_parts)}</div>' if prod_parts else empty("PRODUCT.md not written yet.")) + req_table)

    # build graph
    phase_rows = ""
    if nodes and not graph.problems(nodes):
        ph = graph.phase_of(nodes)
        phase_rows = "".join(
            f"<tr><td>{ph[n['id']]}</td><td class='mono'>{E(n['id'])}</td><td>{E(n['name'])}</td><td>{E(n['type'])}</td>"
            f"<td class='mono'>{E(', '.join(n.get('depends_on', [])) or '—')}</td><td>{chip(n['status'])}</td></tr>"
            for n in sorted(nodes, key=lambda n: (ph[n["id"]], n["id"])))
    legend = "".join(chip(s) for s in ("COMPLETE", "IN_PROGRESS", "IMPLEMENTED_UNVERIFIED", "BLOCKED", "PLANNED"))
    add("build", "Build graph", "Capabilities in dependency order (not a calendar). Phases are derived from dependencies.",
        svg_graph(nodes) + f'<div class="legend">{legend}</div>' +
        (f'<div class="table-wrap"><table><caption>Nodes by phase</caption><thead><tr><th scope="col">Phase</th><th scope="col">ID</th>'
         f'<th scope="col">Capability</th><th scope="col">Type</th><th scope="col">Depends on</th><th scope="col">Status</th></tr></thead>'
         f'<tbody>{phase_rows}</tbody></table></div>' if phase_rows else ""))

    # features
    cards = "".join(
        f'<article class="feature" aria-label="{E(f["id"])} {E(f["name"])}"><div class="head"><span class="name">{E(f["name"])}</span>{chip(f["status"])}</div>'
        f'<div class="meta mono">{E(f["id"])} · {E(f["priority"])} · node {E(f.get("node") or "—")} · evidence {E(f.get("evidence_status", "NONE"))}</div>'
        f'<div class="meta">Requirements: <span class="mono">{E(", ".join(f.get("requirements") or []) or "—")}</span></div></article>'
        for f in sorted(feats, key=lambda f: f["id"]))
    add("features", "Features", "Status requires evidence: VERIFIED and COMPLETE are only shown when verification passed.",
        f'<div class="grid k3">{cards}</div>' if cards else empty("No feature specifications yet."))

    # design
    dparts = []
    for heading in ("Chosen direction", "Design direction options", "Information architecture", "Key screens", "Accessibility"):
        sec = docs.find_section(design, heading)
        if sec:
            dparts.append(f"<h3>{E(heading)}</h3><div class='prose'>{mdhtml.render(sec, 4)}</div>")
    add("design", "Design", "From DESIGN.md.", "".join(dparts) if dparts else empty("DESIGN.md not written yet (or design not applicable)."))

    # architecture
    aparts = []
    for heading in ("System overview", "Overview", "Stack", "Boundaries", "Failure behavior", "Diagrams"):
        sec = docs.find_section(arch, heading)
        if sec and heading != "Overview" or (heading == "Overview" and sec and not aparts):
            aparts.append(f"<h3>{E(heading)}</h3><div class='prose'>{mdhtml.render(sec, 4)}</div>")
    dep_rows = "".join(f"<tr><td>{E(d['name'])}</td><td>{mdhtml.inline(d['purpose'])}</td><td>{E(d['license'])}</td><td>{chip(d['status'])}</td>"
                       f"<td>{E(d.get('lock_in', '—'))}</td></tr>" for d in deps)
    dep_table = (f'<div class="table-wrap"><table><caption>Dependencies (dependencies.yaml)</caption><thead><tr><th scope="col">Name</th>'
                 f'<th scope="col">Purpose</th><th scope="col">License</th><th scope="col">Status</th><th scope="col">Lock-in</th></tr></thead>'
                 f'<tbody>{dep_rows}</tbody></table></div>') if dep_rows else ""
    add("architecture", "Architecture", "From ARCHITECTURE.md and dependencies.yaml.",
        ("".join(aparts) if aparts else empty("ARCHITECTURE.md not written yet.")) + dep_table)

    # decisions timeline
    items = []
    for _path, fm, body in sorted(decisions, key=lambda r: (str(r[1].get("date")), model.id_number(r[1]["id"]))):
        cls = "override" if fm.get("override") else ("superseded" if fm["status"] == "SUPERSEDED" else "")
        why = docs.first_paragraph(docs.find_section(body, "Rationale") or docs.find_section(body, "Decision"), 220)
        t1 = '<span class="chip">Type-1</span>' if fm.get("type1") or fm.get("reversibility") == "low" or fm.get("impact") == "high" else ""
        ov = '<span class="chip">Founder override</span>' if fm.get("override") else ""
        sup = f'<span class="chip mono">→ {E(fm["superseded_by"])}</span>' if fm.get("superseded_by") else ""
        items.append(f'<li class="{cls}"><div class="t-head"><span class="mono">{E(fm["id"])}</span><span class="t-title">{E(fm["title"])}</span>'
                     f'{chip(fm["status"])}{t1}{ov}{sup}</div><div class="meta mono" style="font-size:12px;color:var(--ink-3)">{E(str(fm["date"]))} · '
                     f'{E(fm["owner_role"])} · {E(fm["decision_type"])} · confidence {fm["confidence"]} · reversibility {E(fm["reversibility"])}</div>'
                     f'<div class="t-why">{mdhtml.inline(why)}</div></li>')
    add("decisions", "Decisions", "Chronological Decision Book. Overrides and superseded decisions stay visible.",
        f'<ol class="timeline">{"".join(items)}</ol>' if items else empty("No decisions recorded yet."))

    # risks & assumptions
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    risk_rows = "".join(
        f"<tr><td class='mono'>{E(r['id'])}</td><td>{E(r['category'])}</td><td>{mdhtml.inline(r['statement'])}</td><td>{chip(r['severity'])}</td>"
        f"<td>{mdhtml.inline(r['mitigation'])}</td><td>{chip(r['status'])}</td></tr>"
        for r in sorted(risks, key=lambda r: (sev_order.get(r["severity"], 9), r["id"])))
    asm_rows = "".join(
        f"<tr><td class='mono'>{E(a['id'])}</td><td>{mdhtml.inline(a['statement'])}</td><td>{a['confidence']}</td>"
        f"<td>{mdhtml.inline(a['validation_method'])}</td><td>{chip(a['state'])}</td></tr>" for a in assumptions)
    add("risks", "Risks & assumptions", "Assumptions are not facts: low-confidence items stay labelled until validated.",
        (f'<div class="table-wrap"><table><caption>Risk register</caption><thead><tr><th scope="col">ID</th><th scope="col">Category</th>'
         f'<th scope="col">Risk</th><th scope="col">Severity</th><th scope="col">Mitigation</th><th scope="col">Status</th></tr></thead><tbody>{risk_rows}</tbody></table></div>'
         if risk_rows else empty("No risks recorded.")) +
        (f'<div class="table-wrap"><table><caption>Assumption registry</caption><thead><tr><th scope="col">ID</th><th scope="col">Assumption</th>'
         f'<th scope="col">Confidence</th><th scope="col">How we validate</th><th scope="col">State</th></tr></thead><tbody>{asm_rows}</tbody></table></div>'
         if asm_rows else empty("No assumptions recorded.")))

    # security & readiness
    sec_intro = docs.first_paragraph(docs.find_section(security, "Summary", "Threat model", "Overview"))
    if gate:
        groups: dict[str, list[dict]] = {}
        for c in gate["checks"]:
            if c["group"] == "production":
                groups.setdefault(c["category"], []).append(c)
        rows = ""
        for cat in sorted(groups):
            for c in sorted(groups[cat], key=lambda c: c["id"]):
                note = ", ".join(c.get("evidence", [])) or c.get("na_reason") or c.get("note") or ""
                rows += (f"<tr><td>{E(cat)}</td><td>{E(c['title'])}<div class='mono' style='font-size:11px;color:var(--ink-3)'>{E(c['id'])}</div></td>"
                         f"<td>{E(c['severity'])}</td><td>{chip(c['status'])}</td><td class='mono' style='font-size:12px'>{E(note)}</td></tr>")
        f20 = gatelib.score(gate["checks"], "forgotten-20")
        gate_html = (f'<div class="table-wrap"><table><caption>Production gate — {E(sc["readiness"]) if sc else ""}</caption><thead><tr>'
                     f'<th scope="col">Category</th><th scope="col">Check</th><th scope="col">Severity</th><th scope="col">Status</th>'
                     f'<th scope="col">Evidence / reason</th></tr></thead><tbody>{rows}</tbody></table></div>'
                     f'<p class="sub">Forgotten 20% audit: {", ".join(f"{k} {v}" for k, v in sorted(f20["counts"].items()))}. '
                     f'No evidence means no PASS; N/A is a valid outcome for checks that do not apply to this product.</p>')
    else:
        gate_html = empty("Production gate not initialised yet (gate.py init).")
    add("readiness", "Security & production readiness", "Evidence-gated. Raftly never marks a product “secure” or “compliant”.",
        (f"<div class='prose'><p>{mdhtml.inline(sec_intro)}</p></div>" if sec_intro else "") + gate_html)

    # launch
    lparts = []
    for heading in ("Launch plan", "Launch strategy", "Rollback", "Remaining risks"):
        sec = docs.find_section(launch, heading)
        if sec:
            lparts.append(f"<h3>{E(heading)}</h3><div class='prose'>{mdhtml.render(sec, 4)}</div>")
    add("launch", "Launch", "From LAUNCH.md.", "".join(lparts) if lparts else empty("LAUNCH.md not written yet."))

    chips = "".join([f'<span class="chip">{E(p["mode"])}</span>', f'<span class="chip">Stage: {E(p["stage"].replace("_", " "))}</span>',
                     f'<span class="chip">{E(p.get("product_type", ""))}</span>', f'<span class="chip mono">{E(brand_name())} {E(FORGE_VERSION)}</span>'])
    generated = now_iso()
    theme_js = """
(function () {
  var button = document.getElementById("theme");
  if (!button) return;
  var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    button.textContent = theme === "dark" ? "Light" : "Dark";
    try { localStorage.setItem("blueprint-theme", theme); } catch (e) { /* storage unavailable */ }
  }
  var saved = null;
  try { saved = localStorage.getItem("blueprint-theme"); } catch (e) { /* storage unavailable */ }
  if (saved) { setTheme(saved); } else { button.textContent = dark ? "Light" : "Dark"; }
  button.addEventListener("click", function () {
    var current = document.documentElement.getAttribute("data-theme") || (dark ? "dark" : "light");
    setTheme(current === "dark" ? "light" : "dark");
  });
})();
"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(p['name'])} Blueprint</title>
<meta name="description" content="{E(brand_name())} product blueprint for {E(p['name'])}, rendered from .raftly state.">
<meta name="generator" content="{E(brand_name())} {E(FORGE_VERSION)}">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="top-inner"><span class="brand">{E(p['name'])}<small>Blueprint</small></span>
<nav class="sections" aria-label="Sections">{''.join(nav)}</nav>
<button class="theme-toggle" id="theme" type="button" aria-label="Toggle colour theme">Theme</button></div></header>
<main id="main">
<div class="hero"><h1>{E(p['name'])}</h1><p class="lede">{mdhtml.inline(lede)}</p><div class="chips">{chips}</div>
<p class="notice">Rendered {E(generated)} from <code>.raftly/</code>. This page is a view, not a source of truth: edit Raftly state and re-render.</p></div>
{''.join(sections_html)}
</main>
<footer>Generated by {E(brand_name())} {E(FORGE_VERSION)} · render_blueprint.py · Statuses and scores are derived from recorded evidence only.
{E(brand_name())} provides engineering/product readiness analysis, not legal, compliance or security certification.</footer>
<script>{theme_js}</script>
</body>
</html>
"""


BLOCK_END_RE = re.compile(r"(</(?:section|div|table|thead|tbody|tr|ol|ul|li|article|g|svg|h[1-6]|p|caption|pre|nav|header|footer)>)(?!\n)")


def readable(page: str) -> str:
    """Break lines after block-level closing tags so the output is easy to review (no 'minified' blobs)."""
    page = BLOCK_END_RE.sub(r"\1\n", page)
    return re.sub(r"(<path [^>]*/>|</title>|<text class=\"phase-label\"[^>]*>[^<]*</text>)(?!\n)", r"\1\n", page)


def main(argv: list[str]) -> int:
    p = cli.parser("render_blueprint.py", "Render the static HTML blueprint")
    p.add_argument("--out", default=None, help="output path (default: <root>/artifacts/blueprint.html)")
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    out = Path(args.out) if args.out else proj.root / "artifacts" / "blueprint.html"
    if not out.is_absolute():
        out = (Path.cwd() / out).resolve()
    assert_not_plugin_core(out)
    page = readable(build(proj))
    atomic_write(out, page)
    cli.emit(args, {"written": str(out), "bytes": len(page.encode())}, lambda d: f"Blueprint written to {d['written']} ({d['bytes']:,} bytes)")
    return 0


if __name__ == "__main__":
    cli.run(main)
