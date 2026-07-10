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
| Add/edit a dimension | [dimension/dimension-layer.md](dimension/dimension-layer.md) → [dimension/merge-sk-pattern.md](dimension/merge-sk-pattern.md) → [dimension/special-cases.md](dimension/special-cases.md) |
| mds soft-delete / is_active handling | [dimension/mds-delete-pattern.md](dimension/mds-delete-pattern.md) |
| Which dim owns which SK | [dimension/inventory.md](dimension/inventory.md) |
| Add/edit a fact | [fact/fact-layer.md](fact/fact-layer.md) |
| CDC / change tracking | [cdc-process/cdc.md](cdc-process/cdc.md) |
| AI address parsing | [cdc-process/process.md](cdc-process/process.md) |
| Config, tags, helpers | [includes/databuffet-js.md](includes/databuffet-js.md), [includes/variables.md](includes/variables.md), [includes/function-data.md](includes/function-data.md), [includes/cdc-config.md](includes/cdc-config.md) |
| Run / debug / env facts | [operations/running-and-troubleshooting.md](operations/running-and-troubleshooting.md) |

## Hard rules (apply to every change)

1. Timezone is always `Asia/Bangkok`.
2. Strings pass through `cleanString` (empty → NULL); use `functionData` helpers, not raw casts.
3. Never hardcode dataset names/tags — use `databuffet.*` constants.
4. Surrogate keys are stable forever; never regenerate an existing SK.
5. `type: "operations"` targets (all MERGE dims, `fact_transcation`) pre-exist in
   BigQuery — Dataform does not create them.
6. Preserve load-bearing typos verbatim: `fact_transcation`, `CDC_DATESET`, `prdDiminsionData`.
7. mds MERGE dims must end with the inactive-row DELETE before `END;`.
8. `dim_company` is the DAG root; mds dims list it in `dependencies`.

## Known stale docs elsewhere in the repo

`.claude/CLAUDE.md`, `.claude/knowledge/*.md`, and `.claude/skills/add-*.md` predate the
current code and contain errors: they reference a nonexistent
`includes/controller/primary-keys.json` and `databuffet.primaryKeys`, use wrong
`SCHEMA_*`-prefixed accessors, describe a single `fact_transaction` table, omit the
dimension/CDC/process layers and the SALEOUT_MDT source, and cite tags (`fact`,
`assertions`) that don't exist. The root `README.md` is accurate except it says
"15 dims" (actual: 59 files). **This wiki supersedes them.**
