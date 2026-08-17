---
name: data-quality-check
description: Ad-hoc data-quality audit of a layer or table via live BigQuery queries (dup keys, NULL rates, freshness, row-count drift). Use because the project has NO Dataform assertions — this is the manual substitute.
---

The project has no Dataform assertions (`document/operations/known-issues.md`), so
quality checks are run ad hoc with
`bq --project_id=databuffet-nonprd query --use_legacy_sql=false`.

Arguments: `$ARGUMENTS` = `<dataset.table>` or a layer name (`validated_mac5`,
`dimension_table`, ...). Scale checks to what was asked.

Standard checks per table type:

**Validated** (PK from the file's `uniqueKey`):
```sql
-- 1) duplicate PKs (QUALIFY should make this 0)
SELECT <pk_cols>, COUNT(*) c FROM `<t>` GROUP BY <pk_cols> HAVING c > 1 LIMIT 10;
-- 2) freshness: latest asatdate should be today/yesterday (Bangkok)
SELECT MAX(asatdate) FROM `<t>`;
-- 3) NULL rate on key business columns
SELECT COUNTIF(<col> IS NULL) / COUNT(*) FROM `<t>`;
```

**Dimension**:
```sql
-- 1) duplicate SKs (must be 0)
SELECT <SK>, COUNT(*) c FROM `<dim>` GROUP BY 1 HAVING c > 1;
-- 2) duplicate natural keys (SCD dims: include StartDate/EndDate in the key)
-- 3) mds coverage: active mds rows missing from dim / inactive rows still present
SELECT COUNT(*) FROM `mds_dataset.<mds>` m WHERE m.is_active = FALSE
  AND EXISTS (SELECT 1 FROM `<dim>` d WHERE d.MdsID = CAST(m.id AS STRING));
```

**Fact**:
```sql
-- 1) duplicate business keys (e.g. fact_transcation: milVnos, milType, CompanySK + grain cols)
-- 2) NULL-SK rate per dim FK (LEFT JOIN misses)
SELECT COUNTIF(CustomerSK IS NULL) / COUNT(*) FROM `<fact>`;
-- 3) retention bound: no rows older than the 4-year window
SELECT COUNT(*) FROM `<fact>` WHERE mix_date <
  DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR);
-- 4) day-over-day row-count drift vs monitor expectations
```

For SK referential integrity across tables, use `/fk-integrity-scan` instead.
Report findings as a table: check, target, result, verdict (OK/attention), and
suggest which file to fix when a check fails.
