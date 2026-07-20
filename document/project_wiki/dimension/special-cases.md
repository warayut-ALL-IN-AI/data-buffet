# Dimension Layer — Special Cases

> **LLM context**: Deviations from the canonical MERGE pattern. Check this page before
> editing any of these files with a bulk/mechanical change.

## `dim_sale_representative` — UNION of two sources (rebuilt daily since 2026-07-20)

Full-rebuild file with two CTE sources UNION ALL'd, single `ROW_NUMBER()` over the union:
- **`mds_rep`**: reps from `mds_data_sales_representative_master` (full org structure,
  StartDate/EndDate intervals, MdsID populated).
- **`ledger_rep`**: per-employees from `ref(databuffet.VALIDATED_MAC5, 'per')` —
  `pernamet` parsed via `REGEXP_EXTRACT` into name/surname/nickname;
  DepartmentID/DepCode/CostChannelID/ProvinceID/flags = NULL;
  sentinel dates `1900-01-01` → `2499-12-31`; `MdsID = NULL`.
SK ordering puts mds rows first (`CASE WHEN MdsID IS NULL THEN 1 ELSE 0 END`).

## `dim_stk_mkt` — 'Waiting Master' placeholders (rebuilt daily since 2026-07-20)

Full-rebuild file: CTE `mds_mkt` (active mds rows) UNION ALL CTE `waiting_master` —
every distinct `stkcode` from `ref(databuffet.VALIDATED_MAC5, "stk")` that
`NOT EXISTS` in `mds_mkt` (matched on StkCode + companyID), with
`MarketingGroupID='999'`, `SubMarketingID='9999'`, `SegmentID='99999'`, names
`'Waiting Master'`, `MdsID = NULL`. Single `ROW_NUMBER()` over the union.

## `dim_doctype` / `dim_holiday` — no surrogate key

Full-rebuild files (since 2026-07-20) that intentionally have **no SK column**:
plain SELECT of natural columns + MdsID, `WHERE is_active = TRUE`, no ROW_NUMBER,
no uniqueKey. (Historically their SK machinery was commented out and they
MERGEd on natural keys.) `dim_holiday` has `dependencies: []`.
Both keep `bigquery.clusterBy` matching the pre-existing BigQuery tables
(`HolidayDate, LongWeekEndFlag` / `AccountCategory, Code`) — required because
`CREATE OR REPLACE TABLE` cannot change an existing table's clustering spec
(first-night failure 2026-07-21, fixed by adding the clusterBy back).

## `dim_rate_target` — MDT percent reallocation in post_operations (activated 2026-07-20)

The only full-rebuild mds dim with a real `post_operations { BEGIN ... END }` block:
after the daily rebuild it recomputes `Percent` for departments under director
'MDT' — temp `mdt_base_data` (rows joined to `dim_department_last` →
`dim_director_last`, filter `DirectorName = 'MDT'`), head-count per month
(`COUNT(DISTINCT employee-dept) / 6` + share of NULL-month rows), then two UPDATEs
on `${self()}` (per-month rows, and NULL-month rows using the max total).
This is why its `dependencies` include `dim_department_last`, `dim_director_last`
**and `update_sk_sale_rep_group`** — `dim_department_last.DirectorSK` is created as
NULL and backfilled by `update_sk_sale_rep_group`, so the post_op must run after
that backfill or the MDT join matches nothing.

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
(`dim_aging_history`), a view (`view_dim_aging`), `fact_mir_vs` (repo-managed since
2026-07-20 and declared in `dependencies[]` — see
[fact/fact-layer.md](../fact/fact-layer.md)), and `onetime.cfsinvclose2024`.
Read it fully before touching; it is not template-shaped.
