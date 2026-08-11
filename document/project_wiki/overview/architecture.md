# Architecture Overview

> **LLM context**: Read this first. Data-Buffet is a BigQuery warehouse on Dataform 3.0.0
> (project `databuffet-nonprd`, region `us-central1`). Medallion layers
> (raw → validated → curated) feed a star schema (dimension + fact), with CDC and an
> AI-address-parsing process pipeline on the side.

## Data flow

```
GCS AVRO files  gs://file-raw-data  (Hive-partitioned by ASATDATE=YYYYMMDD)
      │
      ▼
INITIAL      definitions/initial/     External tables + CREATE SCHEMA + UDFs (15 files)
      │
      ▼
VALIDATED    definitions/validated/   Clean, cast, dedup — 1 file per source table (135 files)
      │                               mac5 87 · cis360 25 · mastersku 12 · saleout_mdt 11
      ▼
CURATED      definitions/curated/     Business joins, JSON parsing, split-sale (8 files)
      │
      ├────────────────────────────┐
      ▼                            ▼
DIMENSION    definitions/dimension/ FACT    definitions/fact/
(59 files — SK dims)         ◄──── (9 files — star-schema joins)
      │                            │
      └──────────────┬─────────────┘
                     ▼
VIEW         definitions/view/      Presentation views (type: "view") for Power BI /
(42 files)                          data marts / RLS. schema stays dimension_view,
                                    fact_view, onetime, process_dataset,
                                    bridge_dataset (folder ≠ target dataset)

Side pipelines:
  CDC      definitions/cdc/       change log driven by cdc-config.json (2 files)
  PROCESS  definitions/process/   AI Thai-address parsing, gated on CDC (1 file)
```

## Layer contracts

| Layer | Dataset(s) | Materialization | Detail page |
|---|---|---|---|
| Initial | `raw_*`, `function_dataset` | operations (external tables, UDFs) | [initial/initial-layer.md](../initial/initial-layer.md) |
| Validated | `validated_*` | incremental / table + QUALIFY dedup | [validated/validated-layer.md](../validated/validated-layer.md) |
| Curated | `curated_*` | incremental + post_operations | [curated/curated-layer.md](../curated/curated-layer.md) |
| Dimension | `dimension_table`, `dimension_view` | table rebuild (34 mds + 10 other) / operations MERGE (2 mds + 10 lake) | [dimension/dimension-layer.md](../dimension/dimension-layer.md) |
| Fact | `fact_table`, `fact_view` | table rebuild / operations upsert | [fact/fact-layer.md](../fact/fact-layer.md) |
| CDC | `cdc_dataset` | operations (config-generated) | [cdc-process/cdc.md](../cdc-process/cdc.md) |
| Process | `process_dataset` | incremental (AI.GENERATE) | [cdc-process/process.md](../cdc-process/process.md) |
| View | `dimension_view`, `fact_view`, `onetime`, `process_dataset`, `bridge_dataset` | `type: "view"` (presentation; folder ≠ target dataset) | [view/view-layer.md](../view/view-layer.md) |

## External inputs NOT managed by this repo

- **`mds_dataset`** — master-data-service tables (`mds_data_*_master`). Loaded by an
  external process. Every table has `id`, `is_active`, `updated_at`. Source of most
  dimensions.
- **`onetime`** dataset — e.g. `onetime.Transaction_Data_Mart` (grain source of
  `fact_transcation`), `cfsinvclose2024`.
- **`dim_company` exists in `dimension_table`** and has a `dim_company.sqlx`, but note
  the repo README's caveat about dependencies — most dims list `dim_company` in
  `dependencies` and it is the DAG root.
- **`onetime` also holds externally-loaded base tables** consumed by views but not
  built here: `onetime.mapping_invoice`, `onetime.Transaction_Data_Mart` is now a
  Dataform view but reads such bases. Likewise `process_dataset.mih_address_data`,
  and geo dims `dim_districts` / `dim_provinces` / `dim_geographies` /
  `dim_sub_districts`, `dim_aging_history`
  — referenced by views but **not** built by any `.sqlx`.
  > Corrected 2026-08-11: this list used to include `dim_product_rebate` (no such
  > table — it is `dim_rebate`, which **is** built here) and
  > `process_dataset.RLS_Customer360` (now built here as
  > `definitions/process/rls_customer360.sqlx`, lowercase). Both are declared in the
  > consuming files' `dependencies[]`.
- **View layer now defined** (2026-07-24): the 42 views under `definitions/view/`
  (e.g. `view_dim_aging`, `view_deb_address_data`) are Dataform-managed as of the view
  migration. See [view/view-layer.md](../view/view-layer.md).

## Critical global conventions

1. **Timezone**: always `Asia/Bangkok` (`CURRENT_DATE('Asia/Bangkok')`).
2. **NULL policy**: empty string → NULL via `cleanString` everywhere.
3. **Config through `databuffet.*`** — no hardcoded dataset names/tags
   (exception: `"mds_dataset"` is a string literal in most dim files).
4. **`type: "operations"` tables are NOT created by Dataform** — they must pre-exist
   in BigQuery (the 12 MERGE dims, `fact_transcation`). The 34 full-rebuild mds dims
   are Dataform-managed tables whose **SKs regenerate daily** (see
   [dimension/full-rebuild-pattern.md](../dimension/full-rebuild-pattern.md)).
5. **Load-bearing typos** — keep verbatim: `fact_transcation` (table + file),
   `CDC_DATESET` (variables.json key), `prdDiminsionData` (JSON field).
6. **No Dataform assertions exist** — quality is enforced via casting, QUALIFY dedup,
   and NOT ENFORCED primary keys.

## Environment

- `workflow_settings.yaml` (environment-specific): defaultProject `databuffet-nonprd`,
  vars `RAW_BUCKET`, `MDS_BACKFILL_DAYS` (currently 1).
- Branches: `dev` (working) → `nonprod` → `prod`; also `hotfix`.
- `dataform` CLI is not installed in the local WSL environment — compile/run happens
  via the Dataform service; `bq --project_id=databuffet-nonprd` works for ad-hoc queries.
