# Initial Layer — `definitions/initial/`

> **LLM context**: 13 files that bootstrap everything: datasets, external tables over
> GCS AVRO, and UDFs. All `type: "operations"`. Tags: `initial` (create) and
> `re-initial` (drop for rebuild).

## Root files

### `create_all_schema.sqlx`
`CREATE SCHEMA IF NOT EXISTS` for **every** dataset: raw MAC5 ×5, validated/curated per
source, `dimension_table`, `dimension_view`, `fact_table`, `fact_view`,
`process_dataset`, `cdc_dataset`, `function_dataset`, `onetime` — all with
`OPTIONS(location="us-central1")`.

### `create_all_function.sqlx`
4 UDFs in `function_dataset`:

| UDF | Purpose |
|---|---|
| `fn_flag_exc` | cancel/status → exclude flag |
| `fn_flag_sales_kpi` | sales-KPI Yes/No |
| `fn_flag_scg` | Thai "ซื้อตรง"/"ซื้อผ่านร้าน" direct-vs-store classification for CRC vnos |
| `EXTRACT_CHQ_DATA` | regex-heavy parser of Thai cheque/transfer memo → `STRUCT<chqmemo, extract_text, extract_value ARRAY<STRUCT<extract_date DATE, extract_amount FLOAT64>>>`; handles Thai month abbreviations + Buddhist-era (พ.ศ.) year conversion |

## External-table patterns

**Incremental** (transactional tables) — Hive partition discovery on `ASATDATE=` folders:
```sql
CREATE OR REPLACE EXTERNAL TABLE `raw.<table>`
WITH PARTITION COLUMNS (ASATDATE STRING)
OPTIONS(format='AVRO',
        uris=['gs://file-raw-data/<gcs_prefix>/<table>/*'],
        hive_partition_uri_prefix='gs://file-raw-data/<gcs_prefix>/<table>/')
```

**Full** (reference tables) — direct glob, no partition:
```sql
CREATE OR REPLACE EXTERNAL TABLE `raw.<table>`
OPTIONS(format='AVRO', uris=['gs://file-raw-data/<gcs_prefix>/<table>/*.avro'])
```

Every table is preceded by `DROP TABLE IF EXISTS`.

## Per-source files

| File | Tag | Creates |
|---|---|---|
| `mac5/create_all_table_raw_mac5.sqlx` | initial | AG01 flagship: 13 incremental (`cql, rcv, cst, mih, cps, cps_dummy, mie, mie_dummy, mih2, mih_dummy, mil, mil_dummy, mir`) + ~60 full tables. `stg_report`/`stgacc` read from `mac5_report`; `tdelivery`/`ttrip*` from `mac5_gps` |
| `mac5/create_all_table_raw_mac5_{aa05,ab01,ac02,ak02}.sqlx` | initial | Per-company: incremental `cql, mih, mil, mir, mie` + full `ap_s, ar_s, chq, deb, dep, per, stg, stk, cfs` |
| `mac5/drop_all_tables_validated_mac5.sqlx` | **re-initial** | DROP ~85 validated_mac5 tables |
| `mac5/drop_all_tables_curated_mac5.sqlx` | **re-initial** | DROP 3 curated tables |
| `cis360/create_all_table_raw_cis360.sqlx` | initial | 27 hive-partitioned external tables |
| `cis360/drop_all_tables_validated_cis360.sqlx` | initial | DROP 24 validated tables |
| `mastersku/create_all_table_raw_mastersku.sqlx` | initial | 12 external tables |
| `mastersku/drop_all_tables_validated_mastersku.sqlx` | initial | DROP 11 validated tables |
| `saleout_mdt/create_all_table_raw_saleout_mdt.sqlx` | initial | 10 external tables by retailer (bt/gb/hp/tw); note renames: folder `reportsalesubscription` → table `report_sale_subscription`, `gb/*` → `saleout_gb` |
| `saleout_mdt/drop_all_tables_validated_saleout_mdt.sqlx` | initial | DROP 10 validated tables |

## Dependency wiring

`create_all_table_raw_<source>` depends on the corresponding `drop_all_tables_*`
action(s); validated schema files (`validated_schema_*`) depend on the create actions.
Running `dataform run --tags initial` therefore rebuilds raw external tables cleanly.

⚠️ `re-initial` tag DROPs validated/curated MAC5 tables — full-rebuild only, data in
incremental tables is lost until re-run.
