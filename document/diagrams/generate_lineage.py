#!/usr/bin/env python3
"""Generate the current pipeline lineage as several readable Mermaid views.

Reads every definitions/**/*.sqlx, extracts each object's layer (its directory),
whether it is paused (config block commented out), and its edges (from both the
`dependencies: [...]` array and inline `ref(...)` calls, with dataset-hint
resolution for name collisions). It then emits pipeline_lineage.md with a few
focused views instead of one giant graph:

  1. Layer overview      — the medallion + star-schema map with live counts
  2. Star schema         — every fact and what feeds it (dim/curated -> fact)
  3. Dimension backbone  — dim -> dim build order (dim_company is the root)
  4. Source -> model     — validated/curated -> dimension/fact data flow

Operational scaffolding (the `initial` layer: create_all_* / drop_all_*, and the
`*_schema_*` schema-declaration objects) is excluded from views 2-4 — it adds
hundreds of noise edges and no data-lineage value. GitHub caps Mermaid at 500
edges per diagram, so each view is kept well under that.

Usage:  python3 document/diagrams/generate_lineage.py   (run from anywhere)
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFS = REPO / "definitions"
OUT = Path(__file__).resolve().parent / "pipeline_lineage.md"

LAYER_ORDER = ["initial", "validated", "curated", "dimension", "fact", "cdc", "process"]
LAYER_STYLE = {
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
SCHEMA_NODE_RE = re.compile(r"(^|_)schema(_|$)")


def dataset_to_subdir(token):
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

    paused = CONFIG_RE.search(text) is None and "config {" in text.replace("-- ", "")

    bare_deps = set()
    m = DEP_ARRAY_RE.search(text)
    if m:
        bare_deps.update(QUOTED_RE.findall(m.group(1)))

    ref_deps = set()
    for call in REF_RE.findall(text):
        quoted = QUOTED_RE.findall(call)
        if not quoted:
            continue
        first_arg = call.split(",")[0].strip()
        hint = dataset_to_subdir(first_arg) if "." in first_arg else None
        ref_deps.add((hint, quoted[-1]))

    return name, layer, subdir, paused, bare_deps, ref_deps


def esc(label):
    return label.replace('"', "'")


def mermaid_block(nodes, node_meta, edges, direction="LR"):
    """nodes: iterable of node_id. node_meta: id -> (layer, paused, label).
    edges: iterable of (src, dst). Returns a fenced mermaid string, clustered
    by layer with per-layer styling and dashed paused nodes."""
    nodes = set(nodes)
    lines = ["```mermaid", f"flowchart {direction}"]
    by_layer = {}
    for nid in sorted(nodes):
        by_layer.setdefault(node_meta[nid][0], []).append(nid)

    for ly in LAYER_ORDER:
        members = by_layer.get(ly, [])
        if not members:
            continue
        lines.append(f'  subgraph {ly}["{ly} ({len(members)})"]')
        for nid in members:
            _, paused, label = node_meta[nid]
            text = f"{label} (paused)" if paused else label
            lines.append(f'    {nid}["{esc(text)}"]')
        lines.append("  end")

    for src, dst in sorted(edges):
        if src in nodes and dst in nodes:
            lines.append(f"  {src} --> {dst}")

    used_layers = {node_meta[n][0] for n in nodes}
    for ly in LAYER_ORDER:
        if ly in used_layers:
            fill, stroke = LAYER_STYLE[ly]
            lines.append(f"  classDef {ly} fill:{fill},stroke:{stroke},color:#111;")
    lines.append("  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;")

    for ly in LAYER_ORDER:
        members = [n for n in by_layer.get(ly, []) if not node_meta[n][1]]
        if members:
            lines.append(f"  class {','.join(members)} {ly};")
    paused = [n for n in sorted(nodes) if node_meta[n][1]]
    if paused:
        lines.append(f"  class {','.join(paused)} paused;")

    lines.append("```")
    return "\n".join(lines)


def main():
    files = [parse_file(p) for p in sorted(DEFS.rglob("*.sqlx"))]

    name_counts = {}
    for name, *_ in files:
        name_counts[name] = name_counts.get(name, 0) + 1

    node_meta = {}      # node_id -> (layer, paused, label)
    by_name = {}        # bare name -> {subdir: node_id}
    meta = {}           # node_id -> (subdir, paused, bare_deps, ref_deps)
    for name, layer, subdir, paused, bare_deps, ref_deps in files:
        node_id = name if name_counts[name] == 1 else f"{name}__{subdir}"
        node_meta[node_id] = (layer, paused, name)
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
        return None

    edges = set()
    for node_id, (subdir, paused, bare_deps, ref_deps) in meta.items():
        if paused:
            continue
        for d in bare_deps:
            src = resolve(d, None)
            if src and src != node_id:
                edges.add((src, node_id))
        for hint, d in ref_deps:
            src = resolve(d, hint)
            if src and src != node_id:
                edges.add((src, node_id))

    layer_of = {nid: m[0] for nid, m in node_meta.items()}
    counts = {ly: sum(1 for v in layer_of.values() if v == ly) for ly in LAYER_ORDER}

    def is_scaffold(nid):
        return layer_of[nid] == "initial" or SCHEMA_NODE_RE.search(node_meta[nid][2]) is not None

    data_edges = {(s, d) for s, d in edges if not is_scaffold(s) and not is_scaffold(d)}

    # ---- View 2: star schema — everything that feeds a fact ----
    fact_nodes = {n for n, ly in layer_of.items() if ly == "fact"}
    star_edges = {(s, d) for s, d in data_edges if d in fact_nodes}
    star_nodes = set(fact_nodes)
    for s, d in star_edges:
        star_nodes.add(s)
    star = mermaid_block(star_nodes, node_meta, star_edges)

    # ---- View 3: dimension backbone — dim -> dim ----
    dim_nodes = {n for n, ly in layer_of.items() if ly == "dimension"}
    dim_edges = {(s, d) for s, d in data_edges if s in dim_nodes and d in dim_nodes}
    dim_connected = {n for e in dim_edges for n in e}
    dim_backbone = mermaid_block(dim_connected, node_meta, dim_edges)

    # ---- View 4: source -> model (validated/curated -> dim/fact/curated) ----
    src_edges = {
        (s, d) for s, d in data_edges
        if layer_of[s] in ("validated", "curated")
        and layer_of[d] in ("validated", "curated", "dimension", "fact")
    }
    src_nodes = {n for e in src_edges for n in e}
    source_model = mermaid_block(src_nodes, node_meta, src_edges)

    paused_labels = sorted(node_meta[n][2] for n, m in node_meta.items() if m[1])
    total = len(node_meta)

    # ---- View 1: layer overview (architecture map with live counts) ----
    overview = f"""```mermaid
flowchart LR
  raw["Raw AVRO<br/>gs://file-raw-data"]
  I["initial ({counts['initial']})<br/>ext tables + UDFs"]
  V["validated ({counts['validated']})<br/>clean · cast · dedup"]
  C["curated ({counts['curated']})<br/>business joins"]
  D["dimension ({counts['dimension']})<br/>SK + SCD"]
  F["fact ({counts['fact']})<br/>star-schema"]
  CDC["cdc ({counts['cdc']})"]
  P["process ({counts['process']})<br/>AI address parse"]
  raw --> I --> V --> C
  C --> D
  C --> F
  V --> D
  V --> F
  D --> F
  V -.-> CDC -.-> P
  classDef raw fill:#f5f5f5,stroke:#999,color:#111;
  classDef initial fill:#e0e0e0,stroke:#9e9e9e,color:#111;
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef cdc fill:#f0d0f0,stroke:#b060b0,color:#111;
  classDef process fill:#f5c6c6,stroke:#c04040,color:#111;
  class raw raw;
  class I initial;
  class V validated;
  class C curated;
  class D dimension;
  class F fact;
  class CDC cdc;
  class P process;
```"""

    doc = f"""# Pipeline Lineage

> ⚠️ **Auto-generated — do not edit by hand.** Regenerate after any change to
> `definitions/` with `python3 document/diagrams/generate_lineage.py` (the local
> pre-commit hook does this automatically). The script parses every `.sqlx`
> (`dependencies: [...]` + inline `ref(...)`), so the views always match the repo.

**Objects: {total}** — """ + " · ".join(
        f"{ly} {counts[ly]}" for ly in LAYER_ORDER if counts[ly]
    ) + f"""

**Paused (config commented out):** {', '.join(paused_labels) if paused_labels else '—'}

Edges point **source → consumer**. Operational scaffolding (the `initial` layer
and `*_schema_*` objects) is omitted from the detail views below — it only wires
the bootstrap and would add hundreds of noise edges. Paused objects are dashed.

---

## 1. Layer overview

The medallion → star-schema map. Counts are live.

{overview}

---

## 2. Star schema — what feeds each fact

Every `fact_*` table and the dimensions / curated tables it joins.

{star}

---

## 3. Dimension backbone — build order

`dim_company` is the DAG root; the `_last` snapshots feed `update_sk_sale_rep_group`
and the target-by-sale chain. Only `dimension → dimension` edges are shown.

{dim_backbone}

---

## 4. Source → model

How `validated` / `curated` tables flow into dimensions and facts (scaffolding
excluded). This is the densest view — open it on GitHub or mermaid.live to zoom.

{source_model}
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)}")
    print(f"  objects={total} data_edges={len(data_edges)}")
    print(f"  view2 star:   nodes={len(star_nodes)} edges={len(star_edges)}")
    print(f"  view3 dims:   nodes={len(dim_connected)} edges={len(dim_edges)}")
    print(f"  view4 source: nodes={len(src_nodes)} edges={len(src_edges)}")
    print(f"  paused={len(paused_labels)}")


if __name__ == "__main__":
    main()
