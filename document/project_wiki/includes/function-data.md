# `includes/controller/function-data.js` — SQL Helper Functions

> **LLM context**: These helpers are JavaScript functions that *return SQL strings*
> (template expansion happens at Dataform compile time). They are accessed as
> `databuffet.functionData.<name>(...)` inside `${...}` in SQLX files.
> Use them instead of hand-writing casts — they encode the project's NULL/empty-string policy.

## Helpers

| Helper | Generated SQL | Use for |
|---|---|---|
| `cleanString(col)` | `NULLIF(CAST(TRIM(col) AS STRING), '')` | Any string column — trims and converts empty string to NULL |
| `cleanCode(col, pattern?)` | `NULLIF(CAST(TRIM(REGEXP_REPLACE(col, r'[\n\r\t]', '')) AS STRING), '')` | Code fields that may contain control characters; `pattern` overrides the default regex |
| `parseFlexibleDatetime(col)` | `COALESCE(SAFE.PARSE_DATETIME('%b %d %Y %I:%M%p', SUBSTR(col,1,19)), SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', SUBSTR(col,1,19)))` | Datetime strings in either `Jan 05 2026 1:30PM` or ISO format |
| `parseAsatDate()` | `PARSE_DATE('%Y%m%d', ASATDATE)` | The hive-partition column `ASATDATE` (YYYYMMDD string) |
| `castInt64(col)` | `CAST(col AS INT64)` | Integer casts |
| `castFloat64(col)` | `CAST(col AS FLOAT64)` | Numeric casts |
| `castBool(col)` | `CAST(col AS BOOL)` | Boolean casts |

## Usage

```sql
SELECT
  ${databuffet.functionData.cleanString("t1.CompanyID")} AS CompanyID,
  ${databuffet.functionData.castInt64("t1.StatusID")}   AS StatusID,
  ${databuffet.functionData.castFloat64("t1.weight")}   AS weight,
  ${databuffet.functionData.parseAsatDate()}            AS asatdate
```

## Important behaviors

- `cleanString` is used **both** for SELECT output **and** in JOIN conditions in
  dimension files, so join keys compare on the cleaned value:
  ```sql
  LEFT JOIN `${DimCompanyTableRef}` AS dim_com
    ON ${databuffet.functionData.cleanString("t1.CompanyID")} = dim_com.companyID
  ```
- `parseFlexibleDatetime` uses `SAFE.PARSE_DATETIME` — unparseable values become
  NULL, they do not fail the job.
- `castInt64` / `castFloat64` are **not** SAFE casts — bad data fails the job.
  That is intentional at the validated layer (fail fast on schema drift).

## Adding a helper

1. Add the function with a JSDoc comment to `includes/controller/function-data.js`.
2. Export it in the `module.exports` block at the bottom.
3. It becomes available everywhere as `databuffet.functionData.<name>`.
