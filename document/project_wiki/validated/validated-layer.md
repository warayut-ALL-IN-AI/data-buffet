# Validated Layer — `definitions/validated/`

> **LLM context**: 135 files (mac5 87 · cis360 25 · mastersku 12 · saleout_mdt 11,
> each source has 1 `validated_schema_*` bootstrap). Pure mechanical cleaning: read raw,
> trim/cast every column with `functionData` helpers, standardize `asatdate`, dedup on PK,
> write to `validated_<source>`. No business logic (rare exceptions in mac5).
> **There is NO `primary-keys.json`** — keys are hardcoded per file (see below).

## Canonical incremental file (four parts)

```sqlx
config {
    type: "incremental",
    schema: databuffet.VALIDATED_CIS360,
    dependencies: ["validated_schema_cis360", "create_all_table_raw_cis360"],
    tags: [databuffet.TAG_VALIDATED, databuffet.TAG_VALIDATED_INCREMENTAL],
    uniqueKey: ["id"],
    bigquery: { partitionBy: "asatdate", clusterBy: ["id"] },
}

js {
    const sourceTable = { database: databuffet.DATABASE, schema: databuffet.RAW_CIS360, name: name() };
    const sourceTableRef = `${sourceTable.database}.${sourceTable.schema}.${sourceTable.name}`;
    const pk_key = ["id"]        // <-- PK defined HERE (and in uniqueKey above)
    let partition_statement, post_operations_statement;
    if (pk_key && pk_key.length > 0) {
        partition_statement = `QUALIFY ROW_NUMBER() OVER(PARTITION BY ${pk_key} ORDER BY asatdate DESC) = 1`;
        post_operations_statement = `...retry-loop ALTER TABLE ADD PRIMARY KEY NOT ENFORCED...`;
    } else { partition_statement = ""; post_operations_statement = ""; }
}

SELECT
    ${databuffet.functionData.cleanString('id')} as id,
    ${databuffet.functionData.castBool('active_status')} as active_status,
    ${databuffet.functionData.parseFlexibleDatetime('create_date')} as create_date,
    ${databuffet.functionData.parseAsatDate()} AS asatdate,
FROM `${sourceTableRef}`
${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", CURRENT_DATE('Asia/Bangkok')-1)`) }
${partition_statement}

pre_operations {}
post_operations { ${ when(!incremental(), post_operations_statement) } }
```

Key mechanics:

- **Incremental window filters on the raw STRING `ASATDATE`** compared to a formatted
  string (1-day look-back, Bangkok time) — not on the parsed DATE column.
- **PK is defined twice**: `uniqueKey` in config (drives Dataform incremental MERGE)
  and `pk_key` in js (drives QUALIFY dedup + NOT ENFORCED PK). Keep them in sync.
- **Empty `pk_key = []`** → no dedup, no PK constraint (append-style tables like `grp`).
- **PK post-op** runs only on full builds (`when(!incremental())`): a
  `WHILE retry_count < 10` loop doing `ALTER TABLE ... DROP PRIMARY KEY IF EXISTS` +
  `ADD PRIMARY KEY (...) NOT ENFORCED` inside `BEGIN...EXCEPTION` (metadata-contention guard).
- Dedup order is usually `asatdate DESC`; some tables order by business columns
  (`mir`: `mirbinvdate DESC`; `grp`: `grpname DESC`).

Reference files:
- Single-source incremental: `definitions/validated/cis360/customer_profile.sqlx`
- Multi-company incremental: `definitions/validated/mac5/mih.sqlx`
- Full-load: `definitions/validated/mac5/grp.sqlx`

## Full-load pattern (`TAG_VALIDATED_FULL`)

Differences from incremental: `type: "table"` (full rebuild each run), tag
`validated_full`, usually no `partitionBy`, no incremental WHERE. Everything else
identical. Since `incremental()` is always false for `type: "table"`, the PK post-op
runs **every** run.

- Used **only in mac5** (73 of 86 non-schema files) — all master/reference codes and
  the `tmp_*`, `tbook_*`, `tdis_*`, `match_*`, `pro_*` families.
- Exceptions to note: `mir.sqlx` is `type: "incremental"` but tagged FULL (operator
  grouping); `mih_billing`/`mil_billing` are full-rebuild snapshots.

## Per-source summary

| Aspect | mac5 | cis360 | mastersku | saleout_mdt |
|---|---|---|---|---|
| Raw datasets | `raw_mac5_ag01` + 4 companies | `raw_cis360` | `raw_mastersku` | `raw_saleout_mdt` |
| Default type | mostly `table` (full) | all incremental | all incremental | all incremental |
| Sub-tag | FULL / INCREMENTAL | INCREMENTAL | INCREMENTAL | **none** (only `validated`) |
| PK | table-specific composites | `id` | `prd_id` / `*_id` | wide business composites |
| Partition | `asatdate` when incremental | `asatdate` | `asatdate` | usually none |
| Quirks | multi-company UNION, sign flips, Thai-text cleanup | heavy `castBool` | `prd_*` prefix | vendor subfolders BT/GB/HP/TW, `PARSE_DATE('%Y/%m/%d', ...)` |

### MAC5 multi-company UNION (14 files)

`ap_s, ar_s, cfs, chq, cql, deb, dep, mie, mih, mil, mir, per, stg, stk` UNION ALL the
same table across all 5 company datasets, each block adding a literal `company_id`
as first column (hence `company_id` leads uniqueKey/clusterBy). Extra dependencies:
`create_all_table_raw_mac5_{aa05,ab01,ac02,ak02}`. Only the ag01 block has `moddate`;
others hardcode `CAST(NULL AS DATETIME) AS moddate`.

### MAC5 incremental tables (13)

`mih, mih2, mih_dummy, mil, mil_dummy, mie, mie_dummy, mir, cps, cps_dummy, cql, cst, rcv`
— the transactional invoice/cost/receiving tables.

## Data quality

No Dataform assertions exist anywhere in the project. Quality is implicit:
1. helper casting (`cleanString` → NULL for empties; `SAFE.PARSE_DATETIME` → NULL on bad dates),
2. QUALIFY dedup (one row per PK),
3. NOT ENFORCED PK constraints (optimizer hints),
4. occasional inline filters (e.g. `mih`: `WHERE IFNULL(mihvnos,'') != ''`).
