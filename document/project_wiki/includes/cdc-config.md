# `includes/controller/cdc-config.json` — CDC Table Registry

> **LLM context**: Declarative config that decides which source tables participate in
> Change Data Capture. The CDC pipeline (`definitions/cdc/`) loops over this file at
> compile time — enabling a table here is the only step needed to start tracking it.

## Current config

```json
{
  "cdc_enabled_sources": {
    "mac5": {
      "enabled": true,
      "tables": {
        "mih": {
          "enabled": false,
          "primary_keys": ["company_id", "mihtype", "mihvnos"],
          "check_fields": ["mihdesc"],
          "raw_schema": "raw_mac5_ag01",
          "validated_schema": "validated_mac5",
          "partition_field": "asatdate"
        },
        "deb": {
          "enabled": true,
          "primary_keys": ["company_id", "debcode"],
          "check_fields": ["debadd1at", "debadd2at", "debadd3at"],
          "raw_schema": "raw_mac5_ag01",
          "validated_schema": "validated_mac5",
          "partition_field": null
        }
      }
    }
  }
}
```

## Field meanings

| Field | Meaning |
|---|---|
| `enabled` (source & table level) | Both must be `true` for the table to be tracked |
| `primary_keys` | Identity of a row — used to match old vs new versions |
| `check_fields` | Columns whose changes are detected (compared between loads) |
| `raw_schema` / `validated_schema` | Where the table lives |
| `partition_field` | `asatdate` for partitioned tables, `null` for full-load tables |

## Active tracking (as of 2026-07)

- `mac5.deb` (customer master) — tracks address fields `debadd1at/2at/3at`.
  Downstream: `process_dataset.deb_address_data` re-parses only changed addresses.
- `mac5.mih` is declared but **disabled**.

## To enable CDC for a new table

1. Add an entry under the source's `tables` with `enabled: true`, primary keys and
   check fields.
2. No SQLX edit needed — `definitions/cdc/` generates actions from this config.
3. See [cdc-process/cdc.md](../cdc-process/cdc.md) for how the change log works.
