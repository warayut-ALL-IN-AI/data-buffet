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
INITIAL      definitions/initial/     External tables + CREATE SCHEMA + UDFs (13 files)
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
(59 files — MERGE + SK)      ◄──── (6 files — star-schema joins)

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
| Dimension | `dimension_table`, `dimension_view` | operations MERGE (SK) / table rebuild | [dimension/dimension-layer.md](../dimension/dimension-layer.md) |
| Fact | `fact_table`, `fact_view` | table rebuild / operations upsert | [fact/fact-layer.md](../fact/fact-layer.md) |
| CDC | `cdc_dataset` | operations (config-generated) | [cdc-process/cdc.md](../cdc-process/cdc.md) |
| Process | `process_dataset` | incremental (AI.GENERATE) | [cdc-process/process.md](../cdc-process/process.md) |

## External inputs NOT managed by this repo

- **`mds_dataset`** — master-data-service tables (`mds_data_*_master`). Loaded by an
  external process. Every table has `id`, `is_active`, `updated_at`. Source of most
  dimensions.
- **`onetime`** dataset — e.g. `onetime.Transaction_Data_Mart` (grain source of
  `fact_transcation`), `cfsinvclose2024`.
- **`dim_company` exists in `dimension_table`** and has a `dim_company.sqlx`, but note
  the repo README's caveat about dependencies — most dims list `dim_company` in
  `dependencies` and it is the DAG root.
- Views `dimension_view.view_dim_aging`, `process_dataset.view_deb_address_data`
  are referenced but not defined in `definitions/`.

## Critical global conventions

1. **Timezone**: always `Asia/Bangkok` (`CURRENT_DATE('Asia/Bangkok')`).
2. **NULL policy**: empty string → NULL via `cleanString` everywhere.
3. **Config through `databuffet.*`** — no hardcoded dataset names/tags
   (exception: `"mds_dataset"` is a string literal in most dim files).
4. **`type: "operations"` tables are NOT created by Dataform** — they must pre-exist
   in BigQuery (dimension MERGE targets, `fact_transcation`).
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
