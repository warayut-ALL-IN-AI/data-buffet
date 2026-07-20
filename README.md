# Data-Buffet

A BigQuery data warehouse built on **Dataform**, transforming raw enterprise data into
analytics-ready facts and dimensions. It implements a medallion architecture
(**raw → validated → curated**) feeding a **star schema** (**dimension + fact**),
with built-in Change Data Capture (CDC) and an AI address-processing pipeline.

| | |
|---|---|
| **Platform** | Google Cloud BigQuery (`databuffet-nonprd`) |
| **Framework** | Dataform `3.0.0` |
| **Location** | `us-central1` |
| **Language** | SQLX (SQL + JavaScript) |
| **Raw Data** | `gs://file-raw-data` (AVRO, Hive-partitioned by `ASATDATE`) |
| **Sources** | MAC5 (×5 companies), MASTERSKU, CIS360, SALEOUT_MDT + external `mds_dataset` |
| **Docs** | [`document/`](document/README.md) — developer guides (TH) + [LLM wiki (EN)](document/project_wiki/README.md) |

---

## Architecture

```
GCS AVRO files (gs://file-raw-data)
        │
        ▼
┌─────────────────┐   definitions/initial/      (13 files)
│ INITIAL         │   External tables over GCS + schema/UDF bootstrap
└─────────────────┘
        │
        ▼
┌─────────────────┐   definitions/validated/    (131 transformations)
│ VALIDATED       │   Type casting, NULL/empty handling, dedup, schema enforcement
└─────────────────┘
        │
        ▼
┌─────────────────┐   definitions/curated/      (5 transformations)
│ CURATED         │   Business logic, joins, JSON/text enrichment, split-sale
└─────────────────┘
        │
        ├──────────────────────────────┐
        ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│ DIMENSION       │            │ FACT            │
│ (59 files, SCD) │◄───────────│ (9 fact tables) │
└─────────────────┘            └─────────────────┘
   definitions/dimension/         definitions/fact/
        ▲
        │  mds_dataset (external master-data-service tables — not built by this repo)

Supporting pipelines:
  • CDC      definitions/cdc/        Change tracking driven by includes/controller/cdc-config.json
  • PROCESS  definitions/process/    AI Thai-address parsing (AI.GENERATE), gated on CDC changes
```

### Layers

| Layer | Path | Count | Purpose |
|-------|------|------:|---------|
| **Initial** | `definitions/initial/` | 13 | Create raw external tables over GCS AVRO; bootstrap schemas & UDFs |
| **Validated** | `definitions/validated/` | 131 | Clean, cast, dedup; one table per source object |
| **Curated** | `definitions/curated/` | 5 | Business-ready joins, enrichment, JSON parsing |
| **Dimension** | `definitions/dimension/` | 59 | Conformed dimensions with surrogate keys (MERGE + SCD intervals) |
| **Fact** | `definitions/fact/` | 9 | Star-schema fact tables joined to dimensions (4-year retention) |
| **CDC** | `definitions/cdc/` | 2 | Config-driven change log over validated tables |
| **Process** | `definitions/process/` | 1 | AI address parsing consumed by dims/facts |

**Validated breakdown:** MAC5 `86` · CIS360 `24` · MASTERSKU `11` · SALEOUT_MDT `10`
(+1 schema-bootstrap file per source)

**Dimension breakdown:** `34` full-daily-rebuild dims from `mds_dataset` (default
since 2026-07-20) · `2` legacy MERGE mds dims with stable SKs (`dim_company`,
`dim_aging_rang`) · `10` MERGE dims from validated/curated · `10` full-rebuild tables
(`*_last` snapshots, target aggregates) · `3` other (`dim_calendar`, `dim_aging`,
`update_sk_sale_rep_group`)

---

## Repository Layout

```
definitions/
├── initial/          # External tables (GCS AVRO) + create_all_schema / create_all_function
│   ├── mac5/         # raw_mac5_ag01, _aa05, _ab01, _ac02, _ak02
│   ├── cis360/
│   ├── mastersku/
│   └── saleout_mdt/
├── validated/        # Raw → clean, one file per table, per source
│   ├── mac5/  cis360/  mastersku/  saleout_mdt/{BT,GB,HP,TW}/
├── curated/          # Clean → business-ready
│   ├── mac5/         # curated_mih, curated_mil, curated_tbook_quotation
│   ├── mastersku/    # curated_product, product_for_aisearch
│   └── cis360/       # (schema only)
├── dimension/        # dim_company (DAG root), 35 more mds dims, dim_customer,
│                     # dim_invoice, dim_order, *_last snapshots, dim_calendar, ...
├── fact/             # fact_invoice, fact_order, fact_delivery, fact_quotation,
│                     # fact_transaction_delivery, fact_transcation (sic — real name),
│                     # fact_chq, fact_mir_vs, fact_mir_rs (AR billing/receive chain)
├── cdc/              # cdc_schema, cdc_change_log
└── process/          # deb_address_data (AI.GENERATE address parsing)

includes/
├── databuffet.js                 # Central config hub (imported by every SQLX file)
└── controller/
    ├── variables.json            # Dataset names & tag constants
    ├── function-data.js          # Reusable SQL-generating helpers
    └── cdc-config.json           # Which source tables participate in CDC

document/
├── getting-started/  architecture/  coding-standards/  how-to/  operations/   (Thai)
└── project_wiki/     # LLM-oriented wiki (English) — per-layer patterns & inventories
```

---

## Configuration

### `workflow_settings.yaml`
Project-level Dataform settings (git-ignored — set per environment):

```yaml
defaultProject: databuffet-nonprd
defaultLocation: us-central1
defaultDataset: dataform
defaultAssertionDataset: dataform_assertions
dataformCoreVersion: 3.0.0
vars:
    RAW_BUCKET: "gs://file-raw-data"
    MDS_BACKFILL_DAYS: "1"     # updated_at look-back window for mds dimension MERGEs
```

### `includes/databuffet.js`
Imported by all SQLX files; merges project config, variables, CDC config and helpers:

```javascript
const databuffet = require("includes/databuffet");

databuffet.DATABASE              // defaultDatabase (databuffet-nonprd)
databuffet.RAW_BUCKET            // gs://file-raw-data
databuffet.REGION                // us-central1
databuffet.MDS_BACKFILL_DAYS     // "1"

databuffet.VALIDATED_MAC5        // "validated_mac5"
databuffet.DIMENSION_TABLE       // "dimension_table"
databuffet.TAG_DIM_DAILY         // "dimension_daily"

databuffet.functionData.cleanString(col)   // SQL helpers (see below)
databuffet.cdcConfig                        // CDC source/table config
```

### SQL helpers — `includes/controller/function-data.js`

| Helper | Returns |
|--------|---------|
| `cleanString(col)` | `NULLIF(CAST(TRIM(col) AS STRING), '')` |
| `cleanCode(col, pattern?)` | strips `\n\r\t` (or custom regex), trims, nullifies empty |
| `parseFlexibleDatetime(col)` | parses `%b %d %Y %I:%M%p` **or** `%Y-%m-%d %H:%M:%S` (SAFE) |
| `parseAsatDate()` | `PARSE_DATE('%Y%m%d', ASATDATE)` |
| `castInt64(col)` / `castFloat64(col)` / `castBool(col)` | type casts (not SAFE — fail fast) |

---

## BigQuery Schemas

| Source | Raw | Validated | Curated |
|--------|-----|-----------|---------|
| MAC5 | `raw_mac5_ag01`, `raw_mac5_aa05`, `raw_mac5_ab01`, `raw_mac5_ac02`, `raw_mac5_ak02` | `validated_mac5` | `curated_mac5` |
| CIS360 | `raw_cis360` | `validated_cis360` | `curated_cis360` |
| MASTERSKU | `raw_mastersku` | `validated_mastersku` | `curated_mastersku` |
| SALEOUT_MDT | `raw_saleout_mdt` | `validated_saleout_mdt` | — |

Shared datasets: `dimension_table` / `dimension_view`, `fact_table` / `fact_view`,
`process_dataset`, `cdc_dataset`, `function_dataset`, `onetime`, and the externally
loaded `mds_dataset` (master-data tables `mds_data_*_master` with `id` / `is_active` /
`updated_at` — the source of most dimensions).

---

## Tags

Run any subset of the graph by tag (`dataform run --tags <tag>`):

| Group | Tags in use |
|-------|-------------|
| Initial | `initial`, `re-initial` (⚠️ drops validated/curated MAC5 tables) |
| Validated | `validated`, `validated_full`, `validated_incremental` |
| Curated | `curated` |
| Dimension | `dimension_daily` (58 files), `dimension_yearly` (`dim_calendar` only) |
| Fact | `fact_daily` |
| Support | `process`, `cdc`, `cdc_incremental` |

Declared in `variables.json` but currently unused: `dimension_monthly`,
`fact_monthly`, `fact_yearly`, `curated_full`, `curated_incremental`, `onetime`.
There is no `assertions` tag — the project has no Dataform assertions.

---

## Common Commands

```bash
# Validate compilation (catch SQLX/JS errors)
dataform compile

# Show the execution plan without running
dataform run --dry-run

# Run a single layer
dataform run --tags validated_incremental
dataform run --tags dimension_daily
dataform run --tags fact_daily

# Run a single action (with dependencies)
dataform run --actions validated_mac5.mih --include-deps

# Inspect the dependency graph
dataform compile --json | jq '.tables[] | {name: .target.name, deps: .dependencyTargets}'
```

Ad-hoc queries: `bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'`
(always pass `--project_id`).

---

## Key Patterns

### Validated — dedup + non-enforced primary key
Each validated table casts/cleans raw columns with the `functionData` helpers,
deduplicates with `QUALIFY ROW_NUMBER()` over its primary key (defined per file as
`uniqueKey` in config **and** `pk_key` in the js block — keep them in sync), then
attaches a `NOT ENFORCED` primary key in a retry-wrapped post-operation.

```sql
${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", CURRENT_DATE('Asia/Bangkok')-1)`) }
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY <primary key columns>
  ORDER BY asatdate DESC          -- or a business column, per table
) = 1
```

14 MAC5 tables (`mih`, `mil`, `deb`, `stk`, …) UNION ALL five company datasets with a
literal `company_id` column.

### Curated — incremental with Bangkok-time window
```javascript
config {
  type: "incremental",
  schema: databuffet.CURATED_MAC5,
  tags: [databuffet.TAG_CURATED],
  uniqueKey: ["company_id", "mihType", "mihVnos"],
  bigquery: { partitionBy: "asatdate", clusterBy: ["company_id", "mihVnos", "mihType"] }
}
```
Complex reallocation (e.g. the `ag01` split-sale expansion in `curated_mil`) lives in
`post_operations { BEGIN ... END }` as a TEMP → DELETE → INSERT on `self()`.

### Dimension — full daily rebuild (default) + legacy MERGE for stable SKs
Since 2026-07-20 the 34 mds-sourced dims are **full daily rebuilds**
(`type: "table"`): SK = `ROW_NUMBER()` over the natural key, source filtered only
`is_active = TRUE`. SKs regenerate every run — all consumers re-derive them daily
(verified), so **never persist these SKs across days**. This natively absorbs mds
soft-deletes and overwrite imports (no tombstone, no backfill window needed).
Full pattern: [document/project_wiki/dimension/full-rebuild-pattern.md](document/project_wiki/dimension/full-rebuild-pattern.md).

Two mds dims keep the legacy MERGE pattern with **stable SKs** (`dim_company`,
`dim_aging_rang` — their SKs are persisted downstream), including the mds tombstone:

```sql
DELETE FROM `<dim>` WHERE MdsID IN (
  SELECT id FROM `<mds_data_*_master>` WHERE is_active = FALSE
);
```

`dim_company` is the DAG root — every mds dim lists it in `dependencies[]` and joins
it for `CompanySK`. MERGE pattern & invariants:
[document/project_wiki/dimension/merge-sk-pattern.md](document/project_wiki/dimension/merge-sk-pattern.md).

### Fact — star-schema joins to dimensions (no MERGE)
Three materialization styles: Dataform `type: "table"` rebuilds (`fact_order`,
`fact_invoice`, and — added 2026-07-20 — the AR chain `fact_chq` → `fact_mir_vs` →
`fact_mir_rs`), `CREATE OR REPLACE TABLE AS` scripts (`fact_delivery`,
`fact_quotation`, `fact_transaction_delivery`), and TEMP → DELETE → INSERT upsert
(`fact_transcation`, keyed on `milVnos, milType, CompanySK`). Facts join dimension
surrogate keys, derive `mix_date` from `milYear/Month/Day`, and keep a rolling
**4-year** window (truncated to start-of-year). Dimension refs use string
interpolation + `dependencies[]`; curated/validated sources use `ref()`.

### CDC — config-driven change tracking
`cdc_change_log` loops over the tables flagged in
`includes/controller/cdc-config.json` (currently `mac5.deb`), compares normalized
`check_fields` between raw and validated, and records NEW/CHANGED rows as JSON
(7-day partition expiration). Downstream, `process/deb_address_data` re-parses
**only today's changed addresses** through BigQuery `AI.GENERATE`
(gemini-2.5-flash) — the CDC gate is the cost control.

---

## Adding Work

Step-by-step guides with checklists live in [`document/how-to/`](document/how-to/):

| Task | Guide |
|------|-------|
| New validated table | [add-validated-table.md](document/how-to/add-validated-table.md) |
| New curated table | [add-curated-table.md](document/how-to/add-curated-table.md) |
| New dimension (mds MERGE) | [add-dimension.md](document/how-to/add-dimension.md) |
| New fact table | [add-fact-table.md](document/how-to/add-fact-table.md) |
| Run & debug | [run-and-debug.md](document/how-to/run-and-debug.md) |

---

## Conventions

- **Timezone:** always `Asia/Bangkok` (e.g. `CURRENT_DATE('Asia/Bangkok')`).
- **NULL handling:** normalize empty strings to `NULL` via `cleanString` / `cleanCode`.
- **DDL:** initial/validated/curated objects are created by Dataform; `operations`
  targets (all MERGE dimensions, `fact_transcation`) pre-exist in BigQuery.
- **Primary keys:** declared `NOT ENFORCED` for query optimization, not constraints.
- **Surrogate keys:** MERGE dims (`dim_company`, `dim_aging_rang`, lake dims) have
  SKs that are stable forever — never regenerate them. Full-rebuild mds dims (34)
  regenerate SKs daily — never persist those SKs across days.
- **Partitioning/clustering:** partition incremental tables by `asatdate`; cluster on up to 4 frequently-filtered columns.
- **Load-bearing typos (keep verbatim):** `fact_transcation` (table/file name),
  `CDC_DATESET` (variables.json key), `prdDiminsionData` (MASTERSKU JSON field).
- **Known issues & gotchas:** [document/operations/known-issues.md](document/operations/known-issues.md).
