#!/usr/bin/env python3
"""Generate the current pipeline lineage graph as a Mermaid diagram.

Reads every definitions/**/*.sqlx, extracts each object's layer (from its
directory), whether it is paused (config block commented out), and its edges
(from both the `dependencies: [...]` array and inline `ref(...)` calls). Emits
a single full-lineage Mermaid flowchart into pipeline_lineage.md, clustered by
layer. It parses the real files, so re-running always reflects the live repo.

Usage:  python3 document/diagrams/generate_lineage.py
Run from the repo root (or anywhere — paths are resolved relative to this file).
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFS = REPO / "definitions"
OUT = Path(__file__).resolve().parent / "pipeline_lineage.md"

LAYER_ORDER = ["initial", "validated", "curated", "dimension", "fact", "cdc", "process"]
LAYER_STYLE = {
    # fill, stroke  (light values; text stays dark, works on GitHub light/dark)
    "initial":   ("#e0e0e0", "#9e9e9e"),
    "validated": ("#cfe8ff", "#4a90d9"),
    "curated":   ("#a8d5ff", "#2f6fb0"),
    "dimension": ("#ffe0b3", "#d98f2f"),
    "fact":      ("#c6f5c6", "#3fa63f"),
    "cdc":       ("#f0d0f0", "#b060b0"),
    "process":   ("#f5c6c6", "#c04040"),
}

DEP_ARRAY_RE = re.compile(r"dependencies\s*:\s*\[(.*?)\]", re.DOTALL)
QUOTED_RE = re.compile(r"""['"]([^'"]+)['"]""")
REF_RE = re.compile(r"ref\(([^)]*)\)")
CONFIG_RE = re.compile(r"^\s*config\s*\{", re.MULTILINE)


def dataset_to_subdir(token):
    """databuffet.VALIDATED_MASTERSKU -> 'mastersku'; CURATED_MAC5 -> 'mac5'."""
    const = token.split(".")[-1]
    parts = const.split("_")
    if parts and parts[0] in ("VALIDATED", "CURATED"):
        return "_".join(parts[1:]).lower()
    return None


def parse_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.stem
    rel = path.relative_to(DEFS).parts
    layer = rel[0]
    subdir = rel[1] if len(rel) > 2 else None

    # Paused = the config block exists only in commented-out form.
    paused = CONFIG_RE.search(text) is None and "config {" in text.replace("-- ", "")

    # deps: bare names from the dependencies array (no dataset hint)
    bare_deps = set()
    m = DEP_ARRAY_RE.search(text)
    if m:
        bare_deps.update(QUOTED_RE.findall(m.group(1)))

    # refs: (hint_subdir, name) — the dataset constant disambiguates collisions
    ref_deps = set()
    for call in REF_RE.findall(text):
        quoted = QUOTED_RE.findall(call)
        if not quoted:
            continue
        first_arg = call.split(",")[0].strip()
        hint = dataset_to_subdir(first_arg) if "." in first_arg else None
        ref_deps.add((hint, quoted[-1]))

    return name, layer, subdir, paused, bare_deps, ref_deps


def main():
    files = [parse_file(p) for p in sorted(DEFS.rglob("*.sqlx"))]

    # Assign a unique node id per object; disambiguate name collisions by subdir.
    name_counts = {}
    for name, *_ in files:
        name_counts[name] = name_counts.get(name, 0) + 1

    nodes = {}          # node_id -> (layer, paused, label)
    by_name = {}        # bare name -> {subdir: node_id}
    meta = {}           # node_id -> (subdir, paused, bare_deps, ref_deps)
    for name, layer, subdir, paused, bare_deps, ref_deps in files:
        node_id = name if name_counts[name] == 1 else f"{name}__{subdir}"
        nodes[node_id] = (layer, paused, name)
        by_name.setdefault(name, {})[subdir] = node_id
        meta[node_id] = (subdir, paused, bare_deps, ref_deps)

    def resolve(dep_name, hint):
        cands = by_name.get(dep_name)
        if not cands:
            return None
        if len(cands) == 1:
            return next(iter(cands.values()))
        if hint and hint in cands:
            return cands[hint]
        return None  # ambiguous without a matching hint — skip

    edges = set()       # (src_id, dst_id)
    for node_id, (subdir, paused, bare_deps, ref_deps) in meta.items():
        if paused:      # skip outgoing edges of paused objects
            continue
        for d in bare_deps:
            src = resolve(d, None)
            if src and src != node_id:
                edges.add((src, node_id))
        for hint, d in ref_deps:
            src = resolve(d, hint)
            if src and src != node_id:
                edges.add((src, node_id))

    # ---- emit mermaid ----
    lines = []
    lines.append("```mermaid")
    lines.append("flowchart LR")
    by_layer = {ly: [] for ly in LAYER_ORDER}
    for nid, (ly, _, _) in sorted(nodes.items()):
        by_layer.setdefault(ly, []).append(nid)

    for ly in LAYER_ORDER:
        members = by_layer.get(ly, [])
        if not members:
            continue
        lines.append(f"  subgraph {ly}[\"{ly} ({len(members)})\"]")
        for nid in members:
            _, paused, label = nodes[nid]
            text = f"{label} (paused)" if paused else label
            lines.append(f"    {nid}[\"{text}\"]")
        lines.append("  end")

    for src, dst in sorted(edges):
        lines.append(f"  {src} --> {dst}")

    # class styling per layer
    for ly, (fill, stroke) in LAYER_STYLE.items():
        lines.append(f"  classDef {ly} fill:{fill},stroke:{stroke},color:#111;")
    lines.append("  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;")

    for ly in LAYER_ORDER:
        members = [n for n in by_layer.get(ly, []) if not nodes[n][1]]
        if members:
            lines.append(f"  class {','.join(members)} {ly};")
    paused_nodes = [nid for nid, (_, p, _) in sorted(nodes.items()) if p]
    if paused_nodes:
        lines.append(f"  class {','.join(paused_nodes)} paused;")

    lines.append("```")
    mermaid = "\n".join(lines)

    counts = {ly: len(by_layer.get(ly, [])) for ly in LAYER_ORDER}
    total = len(nodes)
    paused_labels = [nodes[nid][2] for nid in paused_nodes]
    paused_list = ", ".join(paused_labels) if paused_labels else "—"

    doc = f"""# Pipeline Lineage — full dependency graph

> ⚠️ **Auto-generated — do not edit by hand.** Regenerate after any change to
> `definitions/` with:
>
> ```bash
> python3 document/diagrams/generate_lineage.py
> ```
>
> The script parses every `.sqlx` (both the `dependencies: [...]` array and
> inline `ref(...)` calls), so the graph always reflects the live repo. Edges
> point **source → consumer**. Paused objects (config commented out) are drawn
> dashed/grey and their outgoing edges are omitted.

**Objects: {total}** — """ + " · ".join(
        f"{ly} {counts[ly]}" for ly in LAYER_ORDER if counts[ly]
    ) + f"""

**Paused:** {paused_list}

{mermaid}
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)}")
    print(f"  nodes={total} edges={len(edges)} paused={len(paused_nodes)}")
    for ly in LAYER_ORDER:
        if counts[ly]:
            print(f"  {ly:10} {counts[ly]}")


if __name__ == "__main__":
    main()
