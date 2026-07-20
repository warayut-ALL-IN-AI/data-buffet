# The MDS Full-Rebuild Pattern (canonical since 2026-07-20)

> **LLM context**: This is the default pattern for mds-sourced dimensions — **34 files**
> follow it (all mds dims except `dim_company` and `dim_aging_rang`, which keep the
> legacy [MERGE pattern](merge-sk-pattern.md)). Reference implementation:
> `definitions/dimension/dim_waterpac.sqlx`.
> Decision date 2026-07-20 — see rationale at the bottom.

## Skeleton

```sqlx
config {
  type: "table",
  schema: databuffet.DIMENSION_TABLE,
  dependencies: ["dim_company"],       // dim_company joined via string interpolation
  tags: [databuffet.TAG_DIM_DAILY],
  uniqueKey: ["WaterPacSK"],
  bigquery: { clusterBy: ["WaterPacSK"] },
}

js {
    // เหลือ 2 refs: dim_company + mds source (ไม่มี self-ref — Dataform จัดการเอง)
    const DimCompanyTableRef = `...dim_company`;
    const MdsSourceTableRef  = `...mds_data_waterpac_master`;
}

SELECT
  ROW_NUMBER() OVER(
    ORDER BY
      ${databuffet.functionData.cleanString("t1.CompanyID")},   -- natural key เดิม
      ${databuffet.functionData.cleanString("t1.WaterPacCode")}
  ) AS WaterPacSK,
  dim_com.CompanySK,
  <attributes ผ่าน cleanString/castInt64/castFloat64 ตาม column>,
  ${databuffet.functionData.cleanString("t1.id")} AS MdsID     -- เก็บไว้ trace เท่านั้น
FROM `${MdsSourceTableRef}` AS t1
LEFT JOIN `${DimCompanyTableRef}` AS dim_com
  ON ${databuffet.functionData.cleanString("t1.CompanyID")} = dim_com.companyID
WHERE t1.is_active = TRUE

pre_operations {}

post_operations {}
```

## Properties

| Aspect | Behavior |
|---|---|
| SK | `ROW_NUMBER()` over natural-key ordering — **regenerated every run, NOT stable across days** |
| mds soft delete (`is_active = FALSE`) | Row simply drops out of the rebuild — no tombstone needed |
| mds **overwrite import** (all new `id`s) | Handled automatically — rebuild reads current active rows; `MdsID` refreshes |
| Attribute changes | Always current (full re-read) |
| `MDS_BACKFILL_DAYS` | Not used — no window |
| Table ownership | **Dataform creates/replaces the table** (unlike operations dims) |

## Consumer contract — why daily SK regeneration is safe here

Verified 2026-07-20 (repo scan + live BQ + 90-day query history):

- All SK consumers re-derive daily: 9 facts (rebuild/full-window upsert — verified
  `fact_transcation` covers its whole 4-year window nightly with **0 orphan rows**),
  `dim_*_last`, `dim_target_product_group_by_sale(_dayofwork)`,
  `update_sk_sale_rep_group`; `dim_product_master` and the two grade dims refresh
  their stored FK SKs in `WHEN MATCHED UPDATE`.
- Views (`dimension_view`, `fact_view`, `Transaction_Data_Mart`) compute at query time.
- **Rules that follow**: never persist these SKs outside the daily pipeline; joins
  across days are invalid; any NEW consumer that stores these SKs must itself be
  rebuilt daily (and run after `dimension_daily`).
- **Condition attached to `dim_collection_status` — satisfied 2026-07-20**:
  `fact_mir_vs`/`fact_mir_rs` (which store `CollectSK`) plus `fact_chq` were brought
  into the repo as `type: "table"` daily full rebuilds tagged `fact_daily`
  (see [fact/fact-layer.md](../fact/fact-layer.md)).

## Special files within the 34

- `dim_sale_representative` — `UNION ALL` of the mds block and the ledger block
  (per-employees with NULL DepartmentID + sentinel dates 1900-01-01/2499-12-31, `MdsID NULL`).
- `dim_stk_mkt` — `UNION ALL` of mds block and 'Waiting Master' placeholders
  (anti-join `NOT EXISTS` against the mds CTE; `MdsID NULL`).
- `dim_doctype`, `dim_holiday` — no SK column at all (plain SELECT, no ROW_NUMBER,
  no uniqueKey) but they DO keep `bigquery.clusterBy` matching the pre-existing
  tables' clustering — `CREATE OR REPLACE TABLE` fails if the clustering spec differs
  from the live table (hit on the first night, 2026-07-21).
- `dim_status_not_receive` — dim_company join still commented out (as before).
- `dim_rate_target` — extra deps `dim_department_last`/`dim_director_last` + a real
  `post_operations` block that reallocates `Percent` for MDT departments after the
  rebuild (see [special-cases.md](special-cases.md)).

## Why this replaced the MERGE pattern (2026-07-20)

The mds source supports **overwrite imports** that wipe and re-insert all rows with
new UUID `id`s. Under the MERGE pattern that left "zombie" rows (stale `MdsID` that
the tombstone could never match) and required backfill windows. Full rebuild removes
the whole class of problems: no tombstone, no `MDS_BACKFILL_DAYS`, no dedup joins,
no zombie rows — at the cost of SK stability, which the consumer scan proved nothing
depends on (except the two excluded dims).
