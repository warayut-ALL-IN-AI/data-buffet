# Data-Buffet — LLM Wiki

> **Purpose**: Machine-oriented knowledge base for LLM agents working on this repo.
> Every page opens with an "LLM context" block stating what the page covers and the
> non-obvious constraints. Generated from a full code scan on **2026-07-10** — when
> code and wiki disagree, trust the code and update the wiki.

## Routing — read what the task needs

| Task | Read |
|---|---|
| Any task (start here) | [overview/architecture.md](overview/architecture.md) |
| Understand a source system / raw data | [overview/source-systems.md](overview/source-systems.md), [initial/initial-layer.md](initial/initial-layer.md) |
| Add/edit a validated table | [validated/validated-layer.md](validated/validated-layer.md), [validated/source-inventory.md](validated/source-inventory.md) |
| Add/edit a curated table | [curated/curated-layer.md](curated/curated-layer.md) |
| Add/edit a dimension | [dimension/dimension-layer.md](dimension/dimension-layer.md) → [dimension/full-rebuild-pattern.md](dimension/full-rebuild-pattern.md) (default) / [dimension/merge-sk-pattern.md](dimension/merge-sk-pattern.md) (stable-SK legacy) → [dimension/special-cases.md](dimension/special-cases.md) |
| mds soft-delete / is_active / overwrite import | [dimension/full-rebuild-pattern.md](dimension/full-rebuild-pattern.md); tombstone (2 MERGE dims only): [dimension/mds-delete-pattern.md](dimension/mds-delete-pattern.md) |
| Which dim owns which SK | [dimension/inventory.md](dimension/inventory.md) |
| Add/edit a fact | [fact/fact-layer.md](fact/fact-layer.md) |
| Add/edit a view (presentation layer) | [view/view-layer.md](view/view-layer.md) |
| CDC / change tracking | [cdc-process/cdc.md](cdc-process/cdc.md) |
| AI address parsing | [cdc-process/process.md](cdc-process/process.md) |
| Config, tags, helpers | [includes/databuffet-js.md](includes/databuffet-js.md), [includes/variables.md](includes/variables.md), [includes/function-data.md](includes/function-data.md), [includes/cdc-config.md](includes/cdc-config.md) |
| Run / debug / env facts | [operations/running-and-troubleshooting.md](operations/running-and-troubleshooting.md) |

## Hard rules (apply to every change)

1. Timezone is always `Asia/Bangkok`.
2. Strings pass through `cleanString` (empty → NULL); use `functionData` helpers, not raw casts.
3. Never hardcode dataset names/tags — use `databuffet.*` constants.
4. SK stability is per-pattern: MERGE dims (`dim_company`, `dim_aging_rang`, lake dims)
   have SKs that are stable forever — never regenerate them. The 34 full-rebuild mds
   dims regenerate SKs daily — never persist those SKs across days.
5. `type: "operations"` targets (MERGE dims, `fact_transcation`) pre-exist in
   BigQuery — Dataform does not create them.
6. Preserve load-bearing typos verbatim: `fact_transcation`, `CDC_DATESET`, `prdDiminsionData`.
7. mds **MERGE** dims (dim_company, dim_aging_rang) must end with the inactive-row
   DELETE before `END;` — full-rebuild dims need no tombstone.
8. `dim_company` is the DAG root; mds dims list it in `dependencies`.

## Companion tooling

`.claude/` was rebuilt 2026-07-10 to point into this wiki: `CLAUDE.md` (session
context), skills (`add-initial-table`, `add-validated-table`, `add-curated-table`,
`add-dimension`, `add-fact-table`, `dataform-run`, `enable-cdc`,
`backfill-dimension`, `fk-integrity-scan`, `data-quality-check`, `update-docs`)
and agents (`dataform-expert`, `data-architect`, `bigquery-optimizer`,
`data-quality-auditor`). The old `.claude/knowledge/` and root scaffold guides were
deleted as stale — the historical error list is preserved in
`document/operations/known-issues.md`. Root `README.md` was rewritten the same day
and is accurate.
