#!/usr/bin/env python3
"""Generate presentation source (Markdown slides + speaker notes) from .raftly/ state.

Fallback for hosts without native presentation tooling (see
skills/forge/references/presentation-generation.md). Output is Marp-compatible
Markdown (`---` slide separators, `<!-- notes -->` speaker notes) and also reads
fine as plain Markdown or in Slidev/reveal-md. Content is derived from Raftly
documents; anything missing is labelled, never invented.

  render_deck.py [--root DIR] [--kind blueprint|launch] [--out artifacts/deck.md]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli, docs, graph  # noqa: E402
from forgelib import gate as gatelib  # noqa: E402
from forgelib.fsutil import assert_not_plugin_core, atomic_write, read_text  # noqa: E402

MISSING = "_Not yet defined in Raftly state — Raftly will not invent this._"


def d(proj, name):
    p = proj.forge / name
    return read_text(p) if p.exists() else ""


def pick(text, *headings, limit=5):
    sec = docs.find_section(text, *headings)
    items = docs.bullets(sec, limit)
    if items:
        return "\n".join(f"- {i}" for i in items)
    para = docs.first_paragraph(sec, 320)
    return para or MISSING


def slide(title, body, notes):
    return f"# {title}\n\n{body.strip()}\n\n<!--\nSpeaker notes: {notes.strip()}\n-->"


def deck(proj, kind: str) -> str:
    st = proj.state()
    name = st["project"]["name"]
    product, design, arch, executive, security, launch, gtm = (d(proj, n) for n in (
        "PRODUCT.md", "DESIGN.md", "ARCHITECTURE.md", "EXECUTIVE.md", "SECURITY.md", "LAUNCH.md", "GTM.md"))
    nodes = proj.registry("build-graph.yaml")
    risks = sorted(proj.registry("risks.yaml"), key=lambda r: ["critical", "high", "medium", "low"].index(r["severity"]))
    untested = [a for a in proj.registry("assumptions.yaml") if a["state"] == "UNTESTED"]
    feats = [fm for _, fm, _ in proj.records("feature")]
    gate = proj.gate()
    sc = gatelib.score(gate["checks"]) if gate else None

    phases = ""
    if nodes and not graph.problems(nodes):
        idx = graph.index(nodes)
        phases = "\n".join(f"- **Phase {i}:** " + ", ".join(idx[n]["name"] for n in layer) for i, layer in enumerate(graph.phases(nodes)))
    risk_lines = "\n".join(f"- **{r['severity'].upper()}** {r['statement']} → {r['mitigation']}" for r in risks[:4]) or MISSING
    asm_lines = "\n".join(f"- {a['id']} (confidence {a['confidence']}): {a['statement']}" for a in untested[:3])
    asm_block = f"\n\n**Untested assumptions (labelled, not facts):**\n{asm_lines}" if asm_lines else ""
    readiness = (f"**{sc['readiness']}** · evidence coverage {round((sc['coverage'] or 0) * 100)}%"
                 + (f" · score {round(sc['score'] * 100)}%" if sc and sc["score"] is not None else " · no score without evidence")) if sc else "Gate not evaluated yet."
    brand = {}
    bpath = proj.forge / "brand" / "tokens.json"
    if bpath.exists():
        try:
            brand = json.loads(read_text(bpath))
        except ValueError:
            brand = {}
    accent = brand.get("accent", "#2856d8")
    header = (f"---\nmarp: true\ntheme: default\npaginate: true\nheader: \"{name}\"\n"
              f"style: |\n  section {{ font-family: {brand.get('font', 'system-ui, sans-serif')}; }}\n"
              f"  h1 {{ color: {accent}; }}\n---\n\n")

    if kind == "blueprint":
        slides = [
            slide(f"{name}", pick(executive, "What", "Summary") if executive else pick(product, "Vision"),
                  "One-sentence vision. Who it is for and why now."),
            slide("Problem", pick(product, "Problem"), "The pain in the user's words; evidence from RESEARCH.md."),
            slide("Who it's for", pick(product, "ICP", "Users"), "Primary user / ICP and the job they hire the product for."),
            slide("Today's workflow and its pain", pick(product, "Workflows", "Jobs", "Current workflow"), "What users do today and where it breaks."),
            slide("Proposed solution", pick(product, "V1", "MVP", "Solution", limit=6), "Scope of V1 and what is explicitly excluded."),
            slide("Core experience", pick(design, "Experience principles", "Flows", "Key flows"), "The main flow end to end."),
            slide("Design direction", pick(design, "Chosen direction", "Design direction"), "Options considered and why this direction won."),
            slide("Architecture", pick(arch, "System overview", "Overview", "Stack"), "Simplest architecture that satisfies the requirements; Type-1 decisions."),
            slide("Build plan", phases or MISSING, f"Dependency-ordered build graph: {len(nodes)} capabilities, {len(feats)} feature specs. No calendar promises."),
            slide("Security, privacy & compliance", pick(security, "Summary", "Threat model", "Controls"),
                  "Readiness, not certification. Items needing professional review are flagged."),
            slide("Business & go-to-market", pick(gtm, "Positioning", "Launch", "Channels") if gtm else pick(product, "Positioning", "Success metrics"),
                  "Positioning, channels, pricing inputs."),
            slide("Launch plan & risks", risk_lines + asm_block, "Top risks with mitigations; what would make us stop (kill criteria)."),
        ]
    else:
        slides = [
            slide(f"{name}", pick(executive, "What", "Summary"), "What shipped."),
            slide("Customer problem", pick(product, "Problem"), "Why it matters."),
            slide("Final solution", pick(product, "V1", "MVP", limit=6), "What V1 does and does not do."),
            slide("Demo / screens", pick(design, "Key screens", "Screens"), "Walk the primary flow live or with screenshots."),
            slide("Capabilities", "\n".join(f"- {f['name']} — {f['status']}" for f in feats[:8]) or MISSING, "Feature status straight from Raftly state."),
            slide("Architecture", pick(arch, "System overview", "Overview"), "Key boundaries and decisions."),
            slide("Reliability & security", pick(security, "Summary", "Controls"), "Evidence-backed controls; open risks."),
            slide("Metrics & evidence", pick(product, "Success metrics"), "Only metrics with recorded evidence."),
            slide("Production readiness", readiness, "Gate status from gate.yaml; UNVERIFIED is shown honestly."),
            slide("Launch strategy", pick(launch, "Launch plan", "Launch strategy"), "Sequencing, rollback, owners."),
            slide("Remaining risks", risk_lines + asm_block, "What we accept and how we watch it."),
            slide("Next phase", pick(launch, "Next phase", "After launch") if launch else MISSING, "What we learn next and what triggers it."),
        ]
    return header + "\n\n---\n\n".join(slides) + "\n"


def main(argv: list[str]) -> int:
    p = cli.parser("render_deck.py", "Generate presentation source from Raftly state")
    p.add_argument("--kind", default="blueprint", choices=["blueprint", "launch"])
    p.add_argument("--out", default=None)
    args = p.parse_args(argv)
    proj = cli.project(args).require()
    out = Path(args.out) if args.out else proj.root / "artifacts" / ("deck.md" if args.kind == "blueprint" else "launch-deck.md")
    if not out.is_absolute():
        out = (Path.cwd() / out).resolve()
    assert_not_plugin_core(out)
    text = deck(proj, args.kind)
    atomic_write(out, text)
    cli.emit(args, {"written": str(out), "slides": text.count("\n---\n\n") + 1},
             lambda r: f"Deck source written to {r['written']} ({r['slides']} slides). Missing content is labelled, not invented.")
    return 0


if __name__ == "__main__":
    cli.run(main)
