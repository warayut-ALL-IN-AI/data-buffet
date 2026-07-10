# CDC Pipeline — `definitions/cdc/`

> **LLM context**: 2 files. Config-driven change tracking: the SQL is *generated at
> compile time* by looping over `includes/controller/cdc-config.json`. To track a new
> table you edit the JSON, not the SQLX. Output: `cdc_dataset.cdc_change_log`.

## Files

| File | Role |
|---|---|
| `cdc_schema.sqlx` | `CREATE SCHEMA IF NOT EXISTS cdc_dataset` (operations, tag `cdc`) |
| `cdc_change_log.sqlx` | The engine — operations, tags `cdc` + `cdc_incremental`, `hasOutput: true`, depends on `cdc_schema` |

## How `cdc_change_log` works

### 1. Compile-time generation (js block)
Iterates `databuffet.cdcConfig.cdc_enabled_sources` → sources with `enabled: true` →
tables with `enabled: true`, collecting `{sourceName, tableName, rawSchema,
validatedSchema, primaryKeys, checkFields, partitionField}`. Currently only
**`mac5.deb`** is active (PKs `company_id, debcode`; check fields
`debadd1at, debadd2at, debadd3at`; `partition_field: null` → FULL_DUMP mode).

### 2. Target table
```
cdc_dataset.cdc_change_log (
  cdc_record_id, source_system, source_schema, source_table,
  pk_fields JSON, pk_hash, change_type, asatdate, change_timestamp,
  changed_fields JSON, changed_field_names ARRAY<STRING>, num_fields_changed,
  record_raw JSON, record_validated JSON, cdc_processed_at
)
PARTITION BY asatdate
CLUSTER BY source_system, source_schema, source_table, change_type
-- partition_expiration_days = 7  (change log keeps only 7 days)
```

### 3. Daily run logic (per enabled table)
1. `DELETE ... WHERE asatdate = CURRENT_DATE('Asia/Bangkok')` — idempotent rerun.
2. `raw_data` = raw external table (partitioned tables filter `partition_field = yesterday`;
   full-dump reads all). `company_id` derived from raw schema name via regex `raw_mac5_(.+)`.
3. `validated_data` = latest validated row per PK (`ROW_NUMBER() OVER(... ORDER BY asatdate DESC) = 1`).
4. `all_records` = raw LEFT JOIN validated on normalized PKs
   (`UPPER(TRIM(CAST(... AS STRING)))`).
   - No validated match → `change_type = 'NEW'`
   - Any check-field differs → `change_type = 'CHANGED'`
   - Otherwise the row is dropped (no change).

### 4. Change detection details
- `pk_hash` = `TO_HEX(MD5(CONCAT(pk1, ',', pk2, ...)))`.
- Field comparison uses `IS DISTINCT FROM` after normalizing both sides:
  collapse whitespace `r'[\s\r\n\t]+'` → single space, strip trailing
  non-alphanumerics `r'[^\p{L}\p{N}]+$'`, `NULLIF(..., '')`.
- `changed_fields` = JSON of `field → {raw, validated}`; `changed_field_names` array;
  `num_fields_changed` count.

### 5. Error handling
Each table's INSERT is wrapped in `BEGIN ... EXCEPTION WHEN ERROR THEN ...` so one
table failing doesn't halt the rest; counters (`processed_count`, `error_count`) are
logged and a final `RAISE` fires if `error_count > 0`.

## Consumers

- [`process/deb_address_data`](process.md) reads today's `deb` changes to re-parse
  only changed addresses.

## Enabling a new table

Edit [`includes/controller/cdc-config.json`](../includes/cdc-config.md) — add the table
with `enabled: true`, `primary_keys`, `check_fields`, `raw_schema`, `validated_schema`,
`partition_field` (`asatdate` or `null`). No SQLX change required.
