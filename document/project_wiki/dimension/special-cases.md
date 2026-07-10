# Dimension Layer — Special Cases

> **LLM context**: Deviations from the canonical MERGE pattern. Check this page before
> editing any of these files with a bulk/mechanical change.

## `dim_sale_representative` — two BEGIN blocks

- **Block 1**: standard mds MERGE (`mds_data_sales_representative_master`, dual t2/t3
  dedup) — the mds-inactive DELETE lives at the end of **this block only**.
- **Block 2**: re-reads `max_sk`, then MERGEs in sales reps found only in the ledger:
  CTE `raw_per` reads `ref(databuffet.VALIDATED_MAC5, 'per')`, parses `pernamet` via
  `REGEXP_EXTRACT` into name/surname/nickname, sets DepartmentID/DepCode/etc. to NULL,
  `StartDate = '1900-01-01'`, `EndDate = '2499-12-31'`. Self-join matches on
  `EmployeeID + CompanySK AND t2.DepartmentID IS NULL`. These rows have **no MdsID**
  → never touched by the tombstone DELETE.

## `dim_stk_mkt` — 'Waiting Master' placeholders

After the standard MERGE: re-read `max_sk`, then `INSERT INTO ... SELECT` every distinct
`stkcode` from `ref(databuffet.VALIDATED_MAC5, "stk")` that `NOT EXISTS` in the dim,
with `MarketingGroupID='999'`, `SubMarketingID='9999'`, `SegmentID='99999'`, names
`'Waiting Master'`, and **`MdsID = NULL`**. NULL MdsID means the tombstone DELETE
(`WHERE MdsID IN (...)`) can never match them — safe by construction.

## `dim_doctype` / `dim_holiday` — commented-out SK

The full SK machinery (`DECLARE max_sk`, CASE/ROW_NUMBER, t2 join, SK in INSERT) is
present but commented out with `--`. They MERGE on the **natural key** instead:
- `dim_doctype`: `ON T.companyID = S.companyID AND T.Code = S.Code`
- `dim_holiday`: `ON T.HolidayDate = S.HolidayDate`

No populated surrogate key in the target tables. Both still have the MdsID column and
the tombstone DELETE.

## `dim_change_district` — mds-sourced but not a MERGE

`type: "table"` — plain full-rebuild SELECT from `mds_data_change_section_master`
joined to dim_company, filtered `WHERE t1.is_active = true`. No SK, no BEGIN, no
tombstone needed (inactive rows drop out on every rebuild).

## `dim_target_product_group_by_sale` / `_dayofwork` — daily full rebuilds

`type: "table"` with `uniqueKey`/`clusterBy` on their SK. `_dayofwork` joins
`dim_calendar` to expand targets over working days and joins
`dim_sale_representative` by **natural keys** (employeeid/DepartmentID/CompanySK/date
range) — so it self-heals the day after any upstream dim change/delete. SKs in these
two tables are ROW_NUMBER-based and **not stable across runs**; do not persist them
outside same-day joins.

## `update_sk_sale_rep_group` — imperative UPDATE step

Not a dim. Builds `temp_data` and runs several `UPDATE <dim>_last SET <FK>SK = ...`
statements to backfill the NULL SK FK columns the `_last` tables declare, then drops
the temp. Must run **after** all `_last` rebuilds (it depends on all 7).

## `dim_calendar` — yearly date spine

Only file tagged `dimension_yearly`. `GENERATE_DATE_ARRAY` spine + dim_holiday join +
weekend/holiday/long-weekend flags via window functions; TEMP → DELETE matching dates
→ INSERT (idempotent).

## `dim_aging` — the monster

~500 lines; AR aging engine over many validated/curated MAC5 tables, a history table
(`dim_aging_history`), a view (`view_dim_aging`), `fact_mir_vs`, and
`onetime.cfsinvclose2024`. Read it fully before touching; it is not template-shaped.
