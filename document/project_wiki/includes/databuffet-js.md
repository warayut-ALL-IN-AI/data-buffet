# `includes/databuffet.js` — Central Configuration Hub

> **LLM context**: Every SQLX file in this project accesses configuration through the
> global `databuffet` object (Dataform auto-exposes `includes/*.js` by filename).
> This is the single entry point — never hardcode schema names, tags, or project IDs.

## Source

```javascript
const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")
const functionData = require("./controller/function-data")

module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,        // "databuffet-nonprd"
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,      // "gs://file-raw-data"
    REGION: dataform.projectConfig.defaultLocation,          // "us-central1"
    MDS_BACKFILL_DAYS: dataform.projectConfig.vars.MDS_BACKFILL_DAYS,  // "1"
    BACKFILL_DAYS: dataform.projectConfig.vars.BACKFILL_DAYS || "1",   // "1", fallback
    ...variables,      // all keys from variables.json (tags, schema names)
    cdcConfig,         // parsed cdc-config.json
    functionData,      // SQL-generating helpers
}
```

## What it merges

| Piece | Origin | Examples |
|---|---|---|
| Project config | `workflow_settings.yaml` | `DATABASE`, `REGION`, `RAW_BUCKET`, `MDS_BACKFILL_DAYS` |
| Schema names & tags | [`variables.json`](variables.md) | `VALIDATED_MAC5`, `DIMENSION_TABLE`, `TAG_DIM_DAILY` |
| CDC config | [`cdc-config.json`](cdc-config.md) | `cdcConfig.cdc_enabled_sources.mac5.tables.deb` |
| SQL helpers | [`function-data.js`](function-data.md) | `functionData.cleanString(col)` |

## Usage in SQLX

```javascript
config {
  type: "table",
  schema: databuffet.VALIDATED_MAC5,          // schema name from variables.json
  tags: [databuffet.TAG_VALIDATED, databuffet.TAG_VALIDATED_INCREMENTAL],
}
```

```sql
SELECT ${databuffet.functionData.cleanString("debcode")} AS debcode
```

In `type: "operations"` dimension files, fully-qualified table refs are built manually
(these tables are **not** managed by Dataform's `${ref()}`):

```javascript
js {
    const DimCompanyTable = {
        database: databuffet.DATABASE,
        schema: databuffet.DIMENSION_TABLE,
        name: "dim_company",
    };
    const DimCompanyTableRef = `${DimCompanyTable.database}.${DimCompanyTable.schema}.${DimCompanyTable.name}`;
}
```

## Key facts

- `MDS_BACKFILL_DAYS` (currently `"1"`) limits how far back mds-sourced dimension
  MERGEs scan `updated_at`. See [dimension MERGE pattern](../dimension/merge-sk-pattern.md).
- `BACKFILL_DAYS` (currently `"1"`) is the incremental look-back window for every
  validated and curated table. It is the **only** entry with a `|| "1"` fallback —
  a checkout without the var would otherwise interpolate `undefined` into 74 SQL
  statements. See [running and troubleshooting](../operations/running-and-troubleshooting.md)
  for the backfill procedure.
- `workflow_settings.yaml` appears in `.gitignore` **but is already tracked**, so
  the ignore rule does nothing and changes to it are committed normally. Do not
  assume it is local-only.
- `workflow_settings.yaml` is environment-specific (project ID differs per env).
- Adding a new tag or schema name → edit `includes/controller/variables.json`,
  never this file.
