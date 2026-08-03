# Diagrams

Visual maps of the Data-Buffet pipeline. Everything here is **auto-generated from
the code** — never hand-edit the output.

## Files

| File | What it is |
|---|---|
| [`pipeline_lineage.md`](pipeline_lineage.md) | **Structural views** (Mermaid) — the whole pipeline by layer/execution/star-schema. Open on GitHub or [mermaid.live](https://mermaid.live) to render/zoom. |
| [`topic_flows.md`](topic_flows.md) | **Subject-area views** (Mermaid) — one focused diagram per business topic (sale-org, target, customer, AR/aging, product, …) showing the topic's `.sqlx` objects, what feeds them, and the facts they feed. |
| [`generate_lineage.py`](generate_lineage.py) | The generator. Parses every `definitions/**/*.sqlx` (`dependencies: [...]`, inline `ref(...)`, and `tags: [...]`) and rewrites **both** markdown files. Topic membership is the `TOPICS` list at the top of this script. |

## The views (in `pipeline_lineage.md`)

1. **Layer overview** — the medallion → star-schema map (raw → initial → validated →
   curated → dimension → fact, plus cdc/process) with live per-layer counts.
2. **Execution / run order** — the tag-driven orchestration: what runs, in what
   order, on what cadence (bootstrap / nightly / yearly), with live object-per-tag
   counts. Start here to understand *how the system operates*.
3. **Star schema** — every `fact_*` table and the dimensions / curated tables that
   feed it.
4. **Dimension backbone** — `dimension → dimension` build order (`dim_company` is the
   DAG root; `_last` snapshots feed `update_sk_sale_rep_group`).
5. **Source → model** — how `validated` / `curated` tables flow into dimensions and
   facts (the densest view).
6. **View layer** — every `view_*` (BI/reporting layer) and the dimensions / facts /
   curated tables / other views it reads (from each view's `dependencies[]`).

Operational scaffolding (the `initial` layer and `*_schema_*` objects) is excluded
from views 3–6 — it adds hundreds of bootstrap-only edges and no data-lineage value.
Paused objects (config commented out) render dashed.

## The topic views (in `topic_flows.md`)

One section per business subject, defined by the `TOPICS` list in
`generate_lineage.py`. Each shows the topic's own objects (members), the `.sqlx`
that feed them (direct upstream, any layer), and any `fact_*` they feed — so you can
answer "what builds this subject and how does its data flow?" without reading the
whole pipeline. Current topics: sale-org, target, customer, ar-aging, product,
sales-txn, delivery, quotation, channel, cost, calendar, reference. A coverage line
at the top flags any dim/fact/curated object not yet claimed by a topic — **when you
add a new domain of tables, add a matching `TOPICS` entry** so it stays at 0.

## Regenerate

Run after **any** change to `definitions/` (add/remove a file, edit `dependencies`,
add/remove a `ref()`, change `tags`, pause/unpause a config):

```bash
python document/diagrams/generate_lineage.py
```

> On this machine use `python` (Python 3.14); `python3` is not on PATH. The local
> pre-commit hook runs this automatically when a commit stages `definitions/*.sqlx`.

The script needs only the Python standard library — no dependencies, no BigQuery
access. It always reflects the current repo state, so the views cannot drift from the
code as long as it is re-run.

### What keeps these in sync

| Mechanism | Scope | Guarantee |
|---|---|---|
| Manual `python …/generate_lineage.py` + commit | anyone | authoritative — the diagram files are tracked in git |
| Local pre-commit hook (`.claude/hooks/pre-commit.sh`) | per-machine (`.claude/` is git-ignored, **not** shared) | regenerates + stages both files when a commit touches `definitions/*.sqlx` |
| CI: [`.github/workflows/diagrams-up-to-date.yml`](../../.github/workflows/diagrams-up-to-date.yml) | repo-wide, all contributors | **fails the PR/push** if the committed diagrams don't match a fresh run |

So diagrams do **not** update on their own — but the CI check makes an out-of-date
diagram a hard failure, so a change to `definitions/` that alters the flow can't merge
without the regenerated diagrams alongside it.
