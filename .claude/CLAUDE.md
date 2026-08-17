# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Last full rewrite: 2026-07-10 (from a complete code scan). If this file and the code
disagree, trust the code and update this file.

## Project Overview

**Data-Buffet** is a BigQuery data warehouse built on Dataform 3.0.0. Medallion
architecture (raw → validated → curated) feeding a **star schema** (dimension + fact),
plus CDC and an AI address-parsing pipeline.

- **Platform**: Google Cloud BigQuery (`databuffet-nonprd`), region `us-central1`
- **Language**: SQLX (SQL + JavaScript)
- **Raw data**: GCS `gs://file-raw-data` (AVRO, Hive-partitioned by `ASATDATE=YYYYMMDD`)
- **Sources**: MAC5 (5 companies: ag01/aa05/ab01/ac02/ak02), MASTERSKU, CIS360,
  SALEOUT_MDT + externally-loaded `mds_dataset` (master data — not built by this repo)
- **Branches**: `dev` (working/default) → `nonprod` → `prod` (+ `hotfix`)

## Documentation — read these first

Full docs live in `document/` (created 2026-07-10, kept current):

- **LLM wiki**: `document/project_wiki/README.md` — task→page routing table.
  Per-layer patterns, full inventories, special cases.
- **Developer guides (Thai)**: `document/getting-started/`, `document/coding-standards/`,
  `document/how-to/` (step-by-step add-table guides with checklists),
  `document/operations/known-issues.md` (gotchas, load-bearing typos, tech debt).

The old `.claude/knowledge/` and root-level `.claude/*.md` scaffold guides were
**deleted 2026-07-10** (stale — referenced a nonexistent `primary-keys.json`,
`SCHEMA_*` accessors, single-fact-table design). `document/` replaced them.

## Project skills & agents (rebuilt 2026-07-10)

Skills (`.claude/skills/*/SKILL.md`): `add-initial-table`, `add-validated-table`,
`add-curated-table`, `add-dimension`, `add-fact-table`, `dataform-run`,
`enable-cdc`, `backfill-dimension`, `fk-integrity-scan`, `data-quality-check`,
`bq-drift-scan` (view/UDF ที่แก้บน BigQuery console แต่ไม่ได้เข้า git — scan, จัดกลุ่ม,
pull กลับ; มีสคริปต์ `scripts/{dump.sql,scan.py,pull.py}`),
`update-docs`, `ship` (commit → push dev → ff nonprod), `check-runs` (monitor-table
run health), `verify-setup` (day-1 machine check: CLIs, GCP auth, BigQuery/GCS
access, hooks — script `scripts/verify.sh`, read-only). Each points at its
`document/` guide — invoke the skill rather than improvising the pattern.

Safety: a PreToolUse hook (`.claude/hooks/guard-dangerous.sh`, wired in
`.claude/settings.json`) blocks destructive commands (re-initial, drop_all_tables,
full-refresh, bq DML/DDL, gcloud delete, gsutil rm, git force-push). If blocked,
explain to the user and let them decide — do not work around the guard.
git `core.hooksPath` points to `.claude/hooks` (pre-commit runs dataform
format+compile when the CLI exists, skips otherwise) — **set it manually after
cloning and dropping in `.claude/`**: `git config core.hooksPath .claude/hooks`.

Hooks must stay cross-platform (Git Bash on Windows + WSL/Linux). They probe
`python3 → python → py` and only accept an interpreter whose `--version` actually
runs; on Windows `command -v python3` resolves to the Microsoft Store shim, which
silently made `guard-dangerous.sh` a no-op until 2026-08-16. Never reintroduce a
bare `python3` dependency, and never let the guard fail open.

Agents (`.claude/agents/`): `dataform-expert` (SQLX development),
`data-architect` (design advice, read-only), `bigquery-optimizer` (perf/cost),
`data-quality-auditor` (live data checks, read-only),
`bq-drift-auditor` (repo ↔ BigQuery drift, read-only).

## Layer map

| Layer | Path | Files | Dataset | Materialization |
|---|---|---:|---|---|
| Initial | `definitions/initial/` | 15 | `raw_*`, `function_dataset` | operations (external tables, UDFs) |
| Validated | `definitions/validated/` | 135 | `validated_<source>` | incremental / table + QUALIFY dedup |
| Curated | `definitions/curated/` | 8 | `curated_<source>` | incremental (+ post_operations) |
| Dimension | `definitions/dimension/` | 59 | `dimension_table` | **table rebuild** (34 mds + 10 other) / operations MERGE (2 mds legacy + 10 lake) / other (3) |
| Fact | `definitions/fact/` | 9 | `fact_table` | table rebuild / operations upsert — **no MERGE** |
| View | `definitions/view/` | 42 | `dimension_view`, `fact_view`, `bridge_dataset`, `onetime`, `process_dataset` | `type: "view"`, tag `view` — BI/reporting over dim/fact/curated (see `document/project_wiki/view/view-layer.md`) |
| CDC | `definitions/cdc/` | 2 | `cdc_dataset` | operations, generated from `cdc-config.json` |
| Process | `definitions/process/` | 2 | `process_dataset` | `deb_address_data` (`AI.GENERATE` gated on CDC) + `rls_customer360` (RLS access map, `type: "table"`) |

## Configuration

- `includes/databuffet.js` — the only import surface: `databuffet.DATABASE`,
  `databuffet.MDS_BACKFILL_DAYS` (currently "1"),
  `databuffet.BACKFILL_DAYS` (currently "1" — incremental look-back for
  validated/curated; bump temporarily to backfill more days), all keys from `variables.json`
  (e.g. `databuffet.VALIDATED_MAC5`, `databuffet.DIMENSION_TABLE`,
  `databuffet.TAG_DIM_DAILY` — **no `SCHEMA_` prefix**), `databuffet.functionData.*`,
  `databuffet.cdcConfig`.
- `includes/controller/variables.json` — every dataset name + tag. Add new constants
  here; never inline string literals (legacy exception: `"mds_dataset"` appears as a
  literal in most dim files).
- `includes/controller/function-data.js` — SQL helpers: `cleanString`, `cleanCode`,
  `parseFlexibleDatetime` (SAFE), `parseAsatDate`, `castInt64/castFloat64/castBool`
  (not SAFE — fail fast).
- **There is NO `primary-keys.json` / `databuffet.primaryKeys`.** Validated PKs are
  defined per file, twice: `uniqueKey` in config + `pk_key` in the js block (keep in sync).
- `workflow_settings.yaml` is **tracked** — edits are committed and shared. Holds
  `BACKFILL_DAYS` (see above). The dead `.gitignore` entry was removed 2026-08-16.

## Key patterns (summaries — full versions in the wiki)

### Validated
`config` (incremental + partitionBy asatdate) → js (`sourceTable` from `name()`,
`pk_key`) → SELECT with helpers on every column → incremental window
`${when(incremental(), \`WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY))\`)}`
(string compare, window = `BACKFILL_DAYS` วัน ปกติ 1) → `QUALIFY ROW_NUMBER() OVER(PARTITION BY pk ORDER BY asatdate DESC) = 1`
→ post_op retry-loop `ADD PRIMARY KEY ... NOT ENFORCED` guarded by `when(!incremental())`.
Full-load variant: `type: "table"` + `TAG_VALIDATED_FULL` (mac5 only, 73 files).
14 MAC5 tables UNION ALL 5 companies with literal `company_id`.
Reference: `validated/cis360/customer_profile.sqlx`, `validated/mac5/mih.sqlx`.

### Dimension (patterns split 2026-07-20)
**Default for mds dims (34 files) — full daily rebuild**
(`document/project_wiki/dimension/full-rebuild-pattern.md`): `type: "table"`,
SK = `ROW_NUMBER() OVER(ORDER BY <natural key>)`, `WHERE is_active = TRUE` only,
`MdsID` kept as trace column. **SKs regenerate every run — never persist them across
days.** No MERGE/tombstone/backfill window; handles mds overwrite imports natively.
Reference: `dim_waterpac.sqlx`. Consumer safety verified 2026-07-20 (all SK consumers
re-derive daily; `fact_transcation` covers its full 4-year window nightly, 0 orphans).
Condition on `dim_collection_status` satisfied 2026-07-20: `fact_chq`/`fact_mir_vs`/
`fact_mir_rs` now live in `definitions/fact/` as daily `type: "table"` rebuilds.

**Legacy MERGE (2 mds files: `dim_company`, `dim_aging_rang` — stable SKs)**
(`document/project_wiki/dimension/merge-sk-pattern.md`): `type: "operations"`, target
pre-exists in BigQuery; `max_sk` → MERGE with CASE t3 (MdsID) → t2 (natural key) →
`max_sk + ROW_NUMBER()`; source window `MDS_BACKFILL_DAYS`; mandatory tombstone
`DELETE ... WHERE MdsID IN (SELECT id FROM mds WHERE is_active = FALSE)` before `END;`.
Their SKs are stable forever — never regenerate. The 10 lake-sourced dims
(dim_customer, dim_invoice, ...) also use MERGE with stable SKs.

`dim_company` is the DAG root — mds dims list it in `dependencies[]` and join it for
`CompanySK`. Special cases (UNION-block dim_sale_representative / dim_stk_mkt,
SK-less dim_doctype/dim_holiday, dim_rate_target's reserved commented block,
`_last` snapshots + `update_sk_sale_rep_group`):
`document/project_wiki/dimension/special-cases.md`.

### Fact
No MERGE. Three styles: Dataform `table` (`fact_order`, `fact_invoice`, + AR chain
`fact_chq` → `fact_mir_vs` → `fact_mir_rs` added 2026-07-20 — daily full rebuilds,
`dim_aging` depends on `fact_mir_vs`); `CREATE OR REPLACE TABLE AS` (`fact_delivery`,
`fact_quotation`, `fact_transaction_delivery`); TEMP → DELETE → INSERT upsert (`fact_transcation`,
keys `milVnos, milType, CompanySK`, source `onetime.Transaction_Data_Mart`, ~20 dim
joins). Retention: rolling 4 years truncated to start-of-year. `mix_date` =
`PARSE_DATE('%Y%m%d', CONCAT(milYear, milMonth, milDay))`. Dim refs = string
interpolation + `dependencies[]`; curated/validated = `ref()`.

### CDC / Process
`cdc_change_log` is compile-time generated from `includes/controller/cdc-config.json`
(currently only `mac5.deb` enabled) — to track a new table, edit the JSON only.
`process/deb_address_data` calls `AI.GENERATE` (gemini-2.5-flash) to parse Thai
addresses, gated on today's CDC changes (cost control — don't remove the gate).

## Hard rules

1. Timezone: always `Asia/Bangkok`.
2. Every string column through `cleanString`/`cleanCode`; empty string → NULL.
3. No hardcoded dataset names/tags — use `databuffet.*`.
4. SK stability is per-pattern: MERGE dims (`dim_company`, `dim_aging_rang`, 10 lake
   dims) have SKs that are stable forever — never regenerate or update them. The 34
   full-rebuild mds dims regenerate SKs daily — never persist those SKs across days,
   and any new consumer that stores them must itself rebuild daily after `dimension_daily`.
5. MERGE-pattern mds dims must end with the tombstone DELETE before `END;`
   (full-rebuild dims need no tombstone).
6. **Load-bearing typos — keep verbatim**: `fact_transcation` (file + table),
   `CDC_DATESET` (variables.json key), `prdDiminsionData` (MASTERSKU JSON field).
7. `dataform format` before committing when available.
8. **Doc-sync (user mandate 2026-07-10)**: every change to `definitions/`,
   `includes/`, or `workflow_settings.yaml` must be assessed for documentation
   impact before the turn ends, using the mapping table in
   `.claude/skills/update-docs/SKILL.md`. If impacted, update `document/` and
   commit code + docs together. If not impacted (e.g. a bug fix that changes no
   pattern/inventory), state that assessment briefly to the user. A Stop hook
   enforces this; a pre-commit warning backs it up.

## Tags (in use)

`initial`, `re-initial` (⚠️ drops validated/curated MAC5 tables), `validated`,
`validated_full`, `validated_incremental`, `curated`, `dimension_daily`,
`dimension_yearly` (dim_calendar only), `fact_daily`, `view`, `cdc`, `cdc_incremental`,
`process`. Declared but unused: `dimension_monthly`, `fact_monthly`, `fact_yearly`,
`curated_full`, `curated_incremental`. **No `assertions` tag — no Dataform assertions
exist.**

## Environment facts

- **`.claude/` is git-ignored on purpose** (decision 2026-08-16): the working set
  (CLAUDE.md, skills, agents, hooks, `settings.json`) is handed to new developers
  **by copy**, not by clone. Packaging + post-copy steps (hooksPath, chmod, CRLF):
  `document/getting-started/onboarding.md` §4. When sharing, always exclude
  `settings.local.json` (personal permissions).
- `FromAI/` (repo root, git-ignored) holds non-pipeline material: hiring documents
  (candidate CVs, evaluations — **PII**) and ad-hoc HTML decks. Moved out of
  `.claude/` on 2026-08-17. Reads are denied in `settings.json`; never commit,
  never include in a handover bundle.
- `.mcp.json` (repo root) declares the shared MCP servers — currently `context7`.
  Also git-ignored; it travels with the same hand-delivered bundle as `.claude/`.
- Dev machine is **Windows + WSL Ubuntu**: `gcloud`/`bq`/`gsutil` exist **only inside
  WSL** (reach the repo there via `/mnt/<drive>/...`); the Windows PATH has none of them.
  Run BigQuery/GCS commands through WSL, e.g.
  `wsl -e bash -lc "bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'"`.
  Windows has `python` (3.14) and `node`; WSL has `python3` (3.12).
- **No `dataform` CLI** on either side (`dataform` and `npx dataform` both fail) —
  compile/run via the Dataform service; treat compile verification as unavailable
  locally.
- Ad-hoc queries: `bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'`
  — **always pass `--project_id`** (default gcloud project is a different one).
- Region-level `INFORMATION_SCHEMA` is permission-denied; dataset-level works.
- `backup/` holds old file copies — never edit.
- Commit style: short imperative subject; push `dev`, then fast-forward `nonprod`.

## Common tasks

| Task | Guide |
|---|---|
| Onboard a new developer / check a machine | `document/getting-started/onboarding.md`, skill `verify-setup` |
| Add validated table | `document/how-to/add-validated-table.md` |
| Add curated table | `document/how-to/add-curated-table.md` |
| Add dimension (mds MERGE) | `document/how-to/add-dimension.md` |
| Add fact table | `document/how-to/add-fact-table.md` |
| Run / debug / failure table | `document/how-to/run-and-debug.md`, `document/project_wiki/operations/running-and-troubleshooting.md` |
| Which dim owns which SK | `document/project_wiki/dimension/inventory.md` |

# Current Year : 2026
