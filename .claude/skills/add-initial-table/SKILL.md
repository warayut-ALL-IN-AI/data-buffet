---
name: add-initial-table
description: Add a raw external table (GCS AVRO) to the initial layer. Use when a new source table lands in gs://file-raw-data and needs a BigQuery external table — the prerequisite of add-validated-table.
---

Target file: `definitions/initial/<source>/create_all_table_raw_<source>[_<company>].sqlx`.
Layer reference: `document/project_wiki/initial/initial-layer.md`.

Arguments: `$ARGUMENTS` = `<source> <table_name> [incremental|full]`.

Steps:
1. Confirm the GCS path exists: `gsutil ls gs://file-raw-data/<gcs_prefix>/<table>/ | head`
   (gcs_prefix from `databuffet.GCS_*` in `includes/controller/variables.json`).
   Hive layout `ASATDATE=YYYYMMDD/` subfolders → incremental; flat `*.avro` → full.
2. Add to the correct section of the create file, following the neighbors exactly:

   **INCREMENT section** (hive-partitioned):
   ```sql
   DROP TABLE IF EXISTS `<raw_schema>.<table>`;
   CREATE OR REPLACE EXTERNAL TABLE `<raw_schema>.<table>`
   WITH PARTITION COLUMNS (ASATDATE STRING)
   OPTIONS(format='AVRO',
           uris=['${databuffet.RAW_BUCKET}/<gcs_prefix>/<table>/*'],
           hive_partition_uri_prefix='${databuffet.RAW_BUCKET}/<gcs_prefix>/<table>/');
   ```
   **FULL section**: same without partition columns, uris glob `/*.avro`.
3. MAC5 multi-company: if the table exists for all 5 companies, add it to each
   company file (`create_all_table_raw_mac5_{aa05,ab01,ac02,ak02}.sqlx` too).
4. Run tag `initial` for that source (via Dataform UI — no local CLI), then verify:
   `bq --project_id=databuffet-nonprd query --use_legacy_sql=false
   'SELECT COUNT(*) FROM \`databuffet-nonprd.<raw_schema>.<table>\` LIMIT 1'`
5. Next step is usually `/add-validated-table <source> <table>`.
