# Data-Buffet

A BigQuery data warehouse built on **Dataform**, transforming raw enterprise data into
analytics-ready facts and dimensions. It implements a medallion architecture
(**raw → validated → curated**) feeding a **star schema** (**dimension + fact**),
with built-in Change Data Capture (CDC) and address-processing pipelines.

| | |
|---|---|
| **Platform** | Google Cloud BigQuery (`databuffet-nonprd`) |
| **Framework** | Dataform `3.0.0` |
| **Location** | `us-central1` |
| **Language** | SQLX (SQL + JavaScript) |
| **Raw Data** | `gs://file-raw-data` (AVRO, Hive-partitioned by `ASATDATE`) |
| **Sources** | MAC5, MASTERSKU, CIS360, SALEOUT_MDT |

---

## Architecture

```
GCS AVRO files (gs://file-raw-data)
        │
        ▼
┌─────────────────┐   definitions/initial/
│ INITIAL         │   External tables over GCS + schema/function bootstrap
└─────────────────┘
        │
        ▼
┌─────────────────┐   definitions/validated/    (131 transformations)
│ VALIDATED       │   Type casting, NULL/empty handling, dedup, schema enforcement
└─────────────────┘
        │
        ▼
┌─────────────────┐   definitions/curated/      (5 transformations)
│ CURATED         │   Business logic, joins, JSON/text enrichment
└─────────────────┘
        │
        ├──────────────────────────────┐
        ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│ DIMENSION       │            │ FACT            │
│ (15 dims, SCD)  │◄───────────│ (6 fact tables) │
└─────────────────┘            └─────────────────┘
   definitions/dimension/         definitions/fact/

Supporting pipelines:
  • CDC      definitions/cdc/        Change tracking driven by includes/controller/cdc-config.json
  • PROCESS  definitions/process/    Derived datasets (e.g. address parsing) gated on CDC changes
```

### Layers

| Layer | Path | Count | Purpose |
|-------|------|------:|---------|
| **Initial** | `definitions/initial/` | — | Create raw external tables over GCS AVRO; bootstrap schemas & UDFs |
| **Validated** | `definitions/validated/` | 131 | Clean, cast, dedup; one table per source object |
| **Curated** | `definitions/curated/` | 5 | Business-ready joins, enrichment, JSON parsing |
| **Dimension** | `definitions/dimension/` | 15 | Conformed dimensions with surrogate keys (SCD via `MERGE`) |
| **Fact** | `definitions/fact/` | 6 | Star-schema fact tables joined to dimensions |
| **CDC** | `definitions/cdc/` | 2 | Config-driven change log over validated tables |
| **Process** | `definitions/process/` | 1 | Derived datasets consumed by dimensions |

**Validated breakdown:** MAC5 `86` · CIS360 `24` · MASTERSKU `11` · SALEOUT_MDT `10`

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
├── dimension/        # dim_customer, dim_invoice, dim_order, dim_calendar, ...
├── fact/             # fact_invoice, fact_order, fact_delivery, fact_quotation, ...
├── cdc/              # cdc_schema, cdc_change_log
└── process/          # deb_address_data

includes/
├── databuffet.js                 # Central config hub (imported by every SQLX file)
└── controller/
    ├── variables.json            # Schema names & tag constants
    ├── function-data.js          # Reusable SQL-generating helpers
    └── cdc-config.json           # Which source tables participate in CDC
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
```

### `includes/databuffet.js`
Imported by all SQLX files; merges project config, variables, CDC config and helpers:

```javascript
const databuffet = require("includes/databuffet");

databuffet.DATABASE              // defaultDatabase (databuffet-nonprd)
databuffet.RAW_BUCKET            // gs://file-raw-data
databuffet.REGION                // us-central1

databuffet.VALIDATED_MAC5        // "validated_mac5"
databuffet.CURATED_MASTERSKU     // "curated_mastersku"
databuffet.TAG_VALIDATED         // "validated"

databuffet.functionData.cleanString(col)   // SQL helpers (see below)
databuffet.cdcConfig                        // CDC source/table config
```

### SQL helpers — `includes/controller/function-data.js`

| Helper | Returns |
|--------|---------|
| `cleanString(col)` | `NULLIF(CAST(TRIM(col) AS STRING), '')` |
| `cleanCode(col, pattern?)` | strips `\n\r\t` (or custom regex), trims, nullifies empty |
| `parseFlexibleDatetime(col)` | parses `%b %d %Y %I:%M%p` **or** `%Y-%m-%d %H:%M:%S` |
| `parseAsatDate()` | `PARSE_DATE('%Y%m%d', ASATDATE)` |
| `castInt64(col)` / `castFloat64(col)` / `castBool(col)` | type casts |

---

## BigQuery Schemas

| Source | Raw | Validated | Curated |
|--------|-----|-----------|---------|
| MAC5 | `raw_mac5_ag01`, `raw_mac5_aa05`, `raw_mac5_ab01`, `raw_mac5_ac02`, `raw_mac5_ak02` | `validated_mac5` | `curated_mac5` |
| CIS360 | `raw_cis360` | `validated_cis360` | `curated_cis360` |
| MASTERSKU | `raw_mastersku` | `validated_mastersku` | `curated_mastersku` |
| SALEOUT_MDT | `raw_saleout_mdt` | `validated_saleout_mdt` | — |

Shared datasets: `dimension_table` / `dimension_view`, `fact_table` / `fact_view`,
`process_dataset`, `cdc_dataset`, `function_dataset`, `onetime`.

---

## Tags

Run any subset of the graph by tag (`dataform run --tags <tag>`):

| Group | Tags |
|-------|------|
| Initial | `initial`, `re-initial` |
| Validated | `validated`, `validated_full`, `validated_incremental` |
| Curated | `curated`, `curated_full`, `curated_incremental` |
| Dimension | `dimension_daily`, `dimension_monthly`, `dimension_yearly` |
| Fact | `fact_daily`, `fact_monthly`, `fact_yearly` |
| Support | `process`, `cdc`, `cdc_incremental` |

---

## Common Commands

```bash
# Validate compilation (catch SQLX/JS errors)
dataform compile

# Show the execution plan without running
dataform run --dry-run

# Run the whole project
dataform run

# Run a single layer
dataform run --tags validated
dataform run --tags curated
dataform run --tags dimension_daily
dataform run --tags fact_daily

# Run one source's validated tables, with dependencies
dataform run --tags validated --include-deps --actions "validated_mac5.*"

# Run a single action
dataform run --actions validated_mac5.mih

# Format every SQLX file
dataform format

# Inspect the dependency graph
dataform compile --json | jq '.tables[] | {name: .target.name, deps: .dependencyTargets}'
```

---

## Key Patterns

### Validated — dedup + non-enforced primary key
Each validated table casts/cleans raw columns, deduplicates with
`QUALIFY ROW_NUMBER()` over its primary key, then attaches a `NOT ENFORCED`
primary key in a retry-wrapped post-operation.

```sql
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY <primary key columns>
  ORDER BY file_load_datetime DESC      -- or completedat, per table
) = 1
```

### Curated — incremental with Bangkok-time window
```javascript
config {
  type: "incremental",
  schema: databuffet.CURATED_MAC5,
  tags: [databuffet.TAG_CURATED],
  uniqueKey: ["company_id", "mihType", "mihVnos"],
  bigquery: {
    partitionBy: "asatdate",
    clusterBy: ["company_id", "mihVnos", "mihType"]
  }
}
```

### Dimension — surrogate keys via `MERGE`
Dimensions are `operations` that compute the next surrogate key
(`MAX(...SK)+1`) and `MERGE` new/changed rows, preserving existing keys.

### Fact — star-schema joins to dimensions
Facts join curated data to dimension surrogate keys (`CustomerSK`,
`InvoiceSK`, …) and are partitioned by `asatdate`.

> **Note:** `dim_company` is *referenced* by several dimensions but is **not**
> created by Dataform — it has no `.sqlx` file. Do not add it to a
> `dependencies[]` array.

### CDC — config-driven change tracking
`cdc_change_log` loops over the tables flagged in
`includes/controller/cdc-config.json`, compares `check_fields` against the
prior load (by `ASATDATE`), and records inserts/updates. Downstream
`process/` datasets (e.g. `deb_address_data`) only recompute rows that changed.

---

## Adding Work

**New validated table**
1. Add/confirm the raw external table in `definitions/initial/<source>/`.
2. Create `definitions/validated/<source>/<table>.sqlx`.
3. Clean & cast with the helpers in `function-data.js`; dedup via `QUALIFY`.
4. Tag with `validated` plus `validated_full` or `validated_incremental`.

**New curated table**
1. Identify validated dependencies.
2. Create `definitions/curated/<source>/<table>.sqlx` (`type: "incremental"`).
3. Partition by `asatdate`; cluster on common filter columns.

**New dimension / fact**
1. Dimension: `operations` MERGE that assigns a surrogate key.
2. Fact: join curated data to the relevant dimension surrogate keys; partition by `asatdate`.

---

## Conventions

- **Timezone:** always `Asia/Bangkok` (e.g. `CURRENT_DATE('Asia/Bangkok')`).
- **NULL handling:** normalize empty strings to `NULL` via `cleanString` / `cleanCode`.
- **No manual DDL:** all schemas, tables and UDFs are created by Dataform.
- **Primary keys:** declared `NOT ENFORCED` for query optimization, not constraints.
- **Partitioning/clustering:** partition incremental tables by `asatdate`; cluster on up to 4 frequently-filtered columns.
