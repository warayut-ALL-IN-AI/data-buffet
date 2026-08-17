---
name: enable-cdc
description: Enable Change Data Capture tracking for a source table by editing cdc-config.json (no SQLX changes needed). Use when the user wants change tracking or a CDC-gated downstream process.
---

CDC is config-driven: `definitions/cdc/cdc_change_log.sqlx` generates its SQL at
compile time from `includes/controller/cdc-config.json`. Enabling a table = editing
the JSON only. Reference: `document/project_wiki/cdc-process/cdc.md` and
`document/project_wiki/includes/cdc-config.md`.

Arguments: `$ARGUMENTS` = `<source> <table>`.

Steps:
1. Gather the required facts (ask or inspect the validated file):
   - `primary_keys` — row identity (from the validated file's `uniqueKey`)
   - `check_fields` — columns whose changes matter (keep minimal; each adds compare cost)
   - `raw_schema` / `validated_schema`
   - `partition_field` — `"asatdate"` for partitioned incremental tables, `null` for full-dump
2. Edit `includes/controller/cdc-config.json`: add the table under the source's
   `tables` with `"enabled": true`. Source-level `enabled` must also be true.
3. No SQLX edits. Next `cdc_incremental` run picks it up (creates/extends
   `cdc_dataset.cdc_change_log`; 7-day partition expiration).
4. If a downstream process should react to changes, gate it with the
   `WHERE EXISTS (... cdc_change_log ... asatdate = CURRENT_DATE('Asia/Bangkok'))`
   pattern from `definitions/process/deb_address_data.sqlx` — this is the cost
   control for expensive derivations (especially AI.GENERATE).

Currently enabled: `mac5.deb` only (`mih` declared but disabled).
