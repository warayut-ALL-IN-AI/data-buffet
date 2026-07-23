#!/usr/bin/env python3
"""Generate the current pipeline lineage as several readable Mermaid views.

Reads every definitions/**/*.sqlx, extracts each object's layer (its directory),
whether it is paused (config block commented out), and its edges (from both the
`dependencies: [...]` array and inline `ref(...)` calls, with dataset-hint
resolution for name collisions). It then emits pipeline_lineage.md with a few
focused views instead of one giant graph:

  1. Layer overview      — the medallion + star-schema map with live counts
  2. Execution / run order — the tag-driven orchestration (nightly / yearly /
                            bootstrap) with live object-per-tag counts
  3. Star schema         — every fact and what feeds it (dim/curated -> fact)
  4. Dimension backbone  — dim -> dim build order (dim_company is the root)
  5. Source -> model     — validated/curated -> dimension/fact data flow

Operational scaffolding (the `initial` layer: create_all_* / drop_all_*, and the
`*_schema_*` schema-declaration objects) is excluded from views 2-4 — it adds
hundreds of noise edges and no data-lineage value. GitHub caps Mermaid at 500
edges per diagram, so each view is kept well under that.

Usage:  python document/diagrams/generate_lineage.py   (python3 on Linux/Mac; run from anywhere)
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFS = REPO / "definitions"
OUT = Path(__file__).resolve().parent / "pipeline_lineage.md"
TOPIC_OUT = Path(__file__).resolve().parent / "topic_flows.md"

# Subject-area groupings. Each topic's members are the data objects whose bare
# name matches any pattern; the generator then draws the members plus their direct
# upstream feeders (what .sqlx builds them) and any fact they feed. Patterns match
# on the bare object name (regex). Keep this list in sync when a new domain of
# tables is added — the coverage check at the end of main() flags any dim/fact/
# curated object not claimed by a topic.
TOPICS = [
    ("sale-org", "Sales org hierarchy — โครงสร้างองค์กรขาย (แผนก/ภาค/ผจก./เซล)", [
        r"^dim_department(_last)?$",
        r"^dim_section(_manager)?(_last)?$",
        r"^dim_region(_manager)?(_last)?$",
        r"^dim_director(_last)?$",
        r"^dim_sale_representative(_last)?$",
        r"^update_sk_sale_rep_group$",
        r"^dim_change_district$",
        r"^dim_company$",
    ]),
    ("target", "Sales target / quota — เป้าการขาย", [
        r"^dim_target_product_group(_by_sale(_dayofwork)?)?$",
        r"^dim_rate_target$",
        r"^dim_report$",
    ]),
    ("customer", "Customer & scoring — ลูกค้า/เกรด/สกอร์", [
        r"^dim_customer(_grade)?$",
        r"^dim_group_customer(_grade)?$",
        r"^dim_avg_collection_score$",
        r"^dim_bounce_cheque_score$",
        r"^dim_contact_score$",
        r"^dim_payment_receive_score$",
        r"^dim_weight_score$",
        r"^dim_grade$",
    ]),
    ("ar-aging", "Accounts receivable / aging — ลูกหนี้/อายุหนี้", [
        r"^dim_aging(_rang)?$",
        r"^dim_collection_status$",
        r"^dim_status_not_receive$",
        r"^dim_guarantee$",
        r"^fact_chq$",
        r"^fact_mir_(vs|rs)$",
    ]),
    ("product", "Product master & marketing — สินค้า", [
        r"^dim_product_master(_fc)?$",
        r"^dim_product_mkt(_director)?$",
        r"^dim_stk_mkt$",
        r"^dim_rebate$",
        r"^curated_product$",
        r"^product_for_aisearch$",
    ]),
    ("sales-txn", "Sales transactions — ยอดขาย/ออเดอร์/อินวอยซ์ (fact หลัก)", [
        r"^fact_transcation$",
        r"^fact_order$",
        r"^fact_invoice$",
        r"^dim_order$",
        r"^dim_invoice$",
        r"^dim_payment$",
        r"^curated_mih$",
        r"^curated_mil$",
    ]),
    ("delivery", "Delivery / logistics — การจัดส่ง", [
        r"^fact_delivery$",
        r"^fact_transaction_delivery$",
        r"^dim_delivery$",
    ]),
    ("quotation", "Quotation / project — ใบเสนอราคา/โปรเจกต์", [
        r"^fact_quotation$",
        r"^dim_quotation$",
        r"^dim_project$",
        r"^curated_tbook_quotation$",
    ]),
    ("channel", "Sales channel — ช่องทางขาย", [
        r"^dim_channel(_cost|_finance|_sales)?$",
    ]),
    ("cost", "Cost — ต้นทุน", [
        r"^dim_cost_group$",
        r"^dim_cost_stk$",
    ]),
    ("calendar", "Calendar / date spine — ปฏิทิน/วันหยุด", [
        r"^dim_calendar$",
        r"^dim_holiday$",
    ]),
    ("reference", "Reference / misc — ตารางอ้างอิงอื่นๆ", [
        r"^dim_doctype$",
        r"^dim_waterpac$",
    ]),
]

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
TAGS_ARRAY_RE = re.compile(r"tags\s*:\s*\[(.*?)\]", re.DOTALL)
TAG_TOKEN_RE = re.compile(r"databuffet\.(TAG_[A-Z_]+)")
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

    tags = set()
    if not paused:
        tm = TAGS_ARRAY_RE.search(text)
        if tm:
            tags.update(TAG_TOKEN_RE.findall(tm.group(1)))

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

    return name, layer, subdir, paused, bare_deps, ref_deps, tags


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


def build_topic_flows(node_meta, data_edges, layer_of, is_scaffold):
    """Return (markdown, covered_set). One focused subgraph per TOPICS entry:
    members (the topic's own objects) + direct upstream feeders + facts they feed."""
    preds, succs = {}, {}
    for s, d in data_edges:
        succs.setdefault(s, set()).add(d)
        preds.setdefault(d, set()).add(s)

    parts = []
    covered = set()
    for key, title, patterns in TOPICS:
        pats = [re.compile(p) for p in patterns]
        members = sorted(
            nid for nid, (layer, paused, label) in node_meta.items()
            if any(p.search(label) for p in pats)
        )
        if not members:
            parts.append(f"## {title}\n\n_No matching objects in the repo yet._")
            continue
        covered.update(members)
        mset = set(members)
        feeders = {s for m in members for s in preds.get(m, ()) if s not in mset}
        consumers = {
            d for m in members for d in succs.get(m, ())
            if d not in mset and layer_of[d] == "fact"
        }
        nodeset = mset | feeders | consumers
        edges = {(s, d) for s, d in data_edges if s in nodeset and d in nodeset}

        block = [f"## {title}"]
        member_list = ", ".join(f"`{node_meta[m][2]}`" for m in members)
        block.append(f"**Objects in this topic ({len(members)}):** {member_list}")
        if feeders:
            feed_list = ", ".join(
                f"`{lbl}`" for lbl in sorted(node_meta[f][2] for f in feeders)
            )
            block.append(f"**Fed by ({len(feeders)}):** {feed_list}")
        block.append(mermaid_block(nodeset, node_meta, edges))
        parts.append("\n\n".join(block))

    topic_worthy = {
        nid for nid, (layer, paused, label) in node_meta.items()
        if layer in ("dimension", "fact", "curated") and not is_scaffold(nid)
    }
    uncovered = sorted(node_meta[n][2] for n in topic_worthy - covered)
    toc = "\n".join(f"{i}. {title}" for i, (_, title, _) in enumerate(TOPICS, 1))

    header = f"""# Topic Flows (subject-area views)

> ⚠️ **Auto-generated — do not edit by hand.** Regenerate with
> `python document/diagrams/generate_lineage.py`. Topic membership is defined by the
> `TOPICS` list in `generate_lineage.py`; the nodes and edges are parsed from the
> real `.sqlx` files, so each view always matches the code.

Each section is one business subject. It shows the topic's own objects (members),
the `.sqlx` that feed them (direct upstream, any layer), and any `fact_*` they feed.
Edges point **source → consumer**; paused objects render dashed. Node colours are by
layer (validated/curated/dimension/fact/…) as in
[pipeline_lineage.md](pipeline_lineage.md).

**Topics ({len(TOPICS)}):**

{toc}

**Uncovered dim/fact/curated objects (not in any topic):** {', '.join(f'`{u}`' for u in uncovered) if uncovered else '—'}

---

"""
    return header + "\n\n---\n\n".join(parts) + "\n", covered


def main():
    files = [parse_file(p) for p in sorted(DEFS.rglob("*.sqlx"))]

    name_counts = {}
    for name, *_ in files:
        name_counts[name] = name_counts.get(name, 0) + 1

    node_meta = {}      # node_id -> (layer, paused, label)
    by_name = {}        # bare name -> {subdir: node_id}
    meta = {}           # node_id -> (subdir, paused, bare_deps, ref_deps)
    tag_counts = {}     # TAG_* constant -> number of (non-paused) objects
    for name, layer, subdir, paused, bare_deps, ref_deps, tags in files:
        node_id = name if name_counts[name] == 1 else f"{name}__{subdir}"
        node_meta[node_id] = (layer, paused, name)
        by_name.setdefault(name, {})[subdir] = node_id
        meta[node_id] = (subdir, paused, bare_deps, ref_deps)
        for t in tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

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

    # ---- View 2: execution / run order (tag-driven orchestration) ----
    def tc(tag):
        return tag_counts.get(tag, 0)

    execution = f"""```mermaid
flowchart TB
  subgraph boot["Bootstrap - run once / on schema change"]
    I["initial | {tc('TAG_INITIAL')} objects<br/>external tables + UDFs<br/>tag: initial"]
  end

  subgraph nightly["Nightly run - Asia/Bangkok (top to bottom = run order)"]
    direction TB
    V["validated | {tc('TAG_VALIDATED')}<br/>clean - cast - dedup<br/>tags: validated_incremental ({tc('TAG_VALIDATED_INCREMENTAL')}) / validated_full ({tc('TAG_VALIDATED_FULL')})"]
    C["curated | {tc('TAG_CURATED')}<br/>business joins<br/>tag: curated"]
    D["dimension_daily | {tc('TAG_DIM_DAILY')}<br/>SK + SCD rebuild<br/>tag: dimension_daily"]
    Fd["fact_daily | {tc('TAG_FACT_DAILY')}<br/>star-schema load<br/>tag: fact_daily"]
    CDC["cdc | {tc('TAG_CDC')}<br/>change log<br/>tag: cdc"]
    P["process | {tc('TAG_PROCESS')}<br/>AI.GENERATE - gated on today's CDC changes<br/>tag: process"]
    V --> C --> D --> Fd
    V --> CDC --> P
  end

  subgraph yearly["Yearly"]
    Dy["dimension_yearly | {tc('TAG_DIM_YEARLY')}<br/>dim_calendar date spine<br/>tag: dimension_yearly"]
  end

  I -.->|first build| V
  Dy -.->|date spine| D

  classDef boot fill:#e0e0e0,stroke:#9e9e9e,color:#111;
  classDef val fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef cur fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dim fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fct fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef cdc fill:#f0d0f0,stroke:#b060b0,color:#111;
  classDef proc fill:#f5c6c6,stroke:#c04040,color:#111;
  class I boot;
  class V val;
  class C cur;
  class D,Dy dim;
  class Fd fct;
  class CDC cdc;
  class P proc;
```"""

    doc = f"""# Pipeline Lineage

> ⚠️ **Auto-generated — do not edit by hand.** Regenerate after any change to
> `definitions/` with `python document/diagrams/generate_lineage.py` (`python3` on
> Linux/Mac). The local pre-commit hook does this automatically when a commit stages
> `definitions/*.sqlx`. The script parses every `.sqlx` (`dependencies: [...]` +
> inline `ref(...)` + `tags: [...]`), so the views — and `topic_flows.md` — always
> match the repo.

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

## 2. Execution / run order

The tag-driven orchestration: what runs, in what order, on what cadence. Counts are
the number of (non-paused) objects carrying each tag. Solid arrows = run order;
dashed = a prerequisite from another cadence.

{execution}

---

## 3. Star schema — what feeds each fact

Every `fact_*` table and the dimensions / curated tables it joins.

{star}

---

## 4. Dimension backbone — build order

`dim_company` is the DAG root; the `_last` snapshots feed `update_sk_sale_rep_group`
and the target-by-sale chain. Only `dimension → dimension` edges are shown.

{dim_backbone}

---

## 5. Source → model

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

    topic_doc, covered = build_topic_flows(node_meta, data_edges, layer_of, is_scaffold)
    TOPIC_OUT.write_text(topic_doc, encoding="utf-8")
    topic_worthy = {
        nid for nid, (layer, paused, label) in node_meta.items()
        if layer in ("dimension", "fact", "curated") and not is_scaffold(nid)
    }
    print(f"Wrote {TOPIC_OUT.relative_to(REPO)}")
    print(f"  topics={len(TOPICS)} covered={len(covered)}/{len(topic_worthy)} "
          f"uncovered={len(topic_worthy - covered)}")


if __name__ == "__main__":
    main()
