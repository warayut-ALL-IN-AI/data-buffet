# `includes/controller/variables.json` — Tags & Dataset Names

> **LLM context**: The single registry of every BigQuery dataset name and Dataform tag.
> All keys are spread into the `databuffet` object, so `databuffet.TAG_DIM_DAILY`,
> `databuffet.DIMENSION_TABLE`, etc. work in any SQLX file.
> **Add new tags/datasets here — never inline string literals in SQLX.**

## Tags

| Constant | Value | Runs |
|---|---|---|
| `TAG_INITIAL` | `initial` | External-table / bootstrap actions |
| `TAG_REINITIAL` | `re-initial` | Re-create external tables |
| `TAG_VALIDATED` | `validated` | All validated tables |
| `TAG_VALIDATED_FULL` | `validated_full` | Full-load reference tables |
| `TAG_VALIDATED_INCREMENTAL` | `validated_incremental` | Partitioned transactional tables |
| `TAG_CURATED` / `TAG_CURATED_FULL` / `TAG_CURATED_INCREMENTAL` | `curated`, `curated_full`, `curated_incremental` | Curated layer |
| `TAG_DIM_DAILY` / `TAG_DIM_MONTHLY` / `TAG_DIM_YEARLY` | `dimension_daily`, `dimension_monthly`, `dimension_yearly` | Dimension refresh cadence |
| `TAG_FACT_DAILY` / `TAG_FACT_MONTHLY` / `TAG_FACT_YEARLY` | `fact_daily`, `fact_monthly`, `fact_yearly` | Fact refresh cadence |
| `TAG_PROCESS` | `process` | Process layer (address parsing) |
| `TAG_CDC` / `TAG_CDC_INCREMENTAL` | `cdc`, `cdc_incremental` | CDC pipeline |
| `ONETIME` | `onetime` | One-off actions |

## Dataset (BigQuery schema) names

### Per-source raw → validated → curated

| Source | Raw | Validated | Curated |
|---|---|---|---|
| MAC5 | `raw_mac5_ag01`, `raw_mac5_aa05`, `raw_mac5_ab01`, `raw_mac5_ac02`, `raw_mac5_ak02` (one per company) | `validated_mac5` | `curated_mac5` |
| CIS360 | `raw_cis360` | `validated_cis360` | `curated_cis360` |
| MASTERSKU | `raw_mastersku` | `validated_mastersku` | `curated_mastersku` |
| SALEOUT_MDT | `raw_saleout_mdt` | `validated_saleout_mdt` | — |

### Shared datasets

| Constant | Value | Holds |
|---|---|---|
| `DIMENSION_TABLE` | `dimension_table` | Physical dimension tables |
| `DIMENSION_VIEW` | `dimension_view` | Dimension views |
| `FACT_TABLE` | `fact_table` | Physical fact tables |
| `FACT_VIEW` | `fact_view` | Fact views |
| `CDC_DATESET` (sic) | `cdc_dataset` | CDC change log |
| `PROCESS_DATASET` | `process_dataset` | Derived datasets (address parsing) |
| `FUNCTION_DATASET` | `function_dataset` | BigQuery UDFs |
| `MDS_DATASET` | `mds_dataset` | Master-data-service tables (externally loaded, **not** created by this repo) |

> Note the historical typo: the constant is `CDC_DATESET`, not `CDC_DATASET`. Keep using
> it as-is; renaming would touch every consumer.

### GCS folder names (`GCS_*`)

Map source system → folder under `gs://file-raw-data`:
`mac5_ag01`, `mac5_aa05`, `mac5_ab01`, `mac5_ac02`, `mac5_ak02`, `mac5_report`,
`mac5_gps`, `mastersku`, `cis360`, `saleout_mdt`.

## MAC5 multi-company note

MAC5 has **5 company instances** (ag01, aa05, ab01, ac02, ak02), each with its own raw
dataset and GCS folder. The validated layer consolidates them into the single
`validated_mac5` dataset with a `company_id` column.
