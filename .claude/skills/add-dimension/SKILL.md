---
name: add-dimension
description: Scaffold a new dimension with the mds MERGE + surrogate-key pattern. Use when the user asks to add a dim_* table sourced from mds_dataset.
---

Follow the step-by-step guide **`document/how-to/add-dimension.md`** exactly.
Default pattern (since 2026-07-20): **full daily rebuild** —
`document/project_wiki/dimension/full-rebuild-pattern.md`.
Deviating cases: `document/project_wiki/dimension/dimension-layer.md` + `special-cases.md`.

Arguments: `$ARGUMENTS` = `<entity_name> [mds_table_name]`.

Key rules (full checklist in the guide):
1. **Gate question first**: will any consumer persist this dim's SK across days?
   - NO (normal case) → full-rebuild pattern: copy `dim_waterpac.sqlx`,
     `type: "table"`, `ROW_NUMBER() OVER(ORDER BY <natural key>)` AS SK,
     `WHERE is_active = TRUE` only, keep `MdsID` as last column, no MERGE /
     tombstone / backfill window. Dataform creates the table itself; no backfill
     needed. **SKs regenerate daily — never persist them across days.**
   - YES → legacy MERGE pattern (`merge-sk-pattern.md`, example `dim_company.sqlx`):
     pre-create the table in BigQuery, dual t2/t3 join, tombstone DELETE before
     `END;`, first-run backfill via `MDS_BACKFILL_DAYS`. Confirm with the user first.
2. `dependencies: ["dim_company"]`, tag `TAG_DIM_DAILY`, join dim_company for CompanySK.
3. Extra source blocks (placeholders, ledger rows) = CTE + `UNION ALL` before the
   ROW_NUMBER (see `dim_stk_mkt.sqlx`, `dim_sale_representative.sqlx`).
4. If a fact will consume the SK: the fact must re-derive it daily and run after
   `dimension_daily`; add the dim to the fact's `dependencies[]`.
5. Add the new dim to `document/project_wiki/dimension/inventory.md`.
