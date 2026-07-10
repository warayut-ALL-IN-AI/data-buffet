# The MDS MERGE + Surrogate-Key Pattern (canonical)

> **LLM context**: This is the most important pattern in the project — 36 dimension
> files follow it. Target tables pre-exist in BigQuery (`type: "operations"`; Dataform
> does not create them). Reference implementation: `definitions/dimension/dim_company.sqlx`
> (root) or `dim_waterpac.sqlx` (typical child).

## Skeleton

```sqlx
config {
  type: "operations",
  dependencies: ["dim_company"],          // dim_company itself has []
  tags: [databuffet.TAG_DIM_DAILY],
}

js {
    const DimWaterPacTable = {
        database: databuffet.DATABASE,
        schema: databuffet.DIMENSION_TABLE,
        name: name(),
    };
    const DimWaterPacTableRef = `${DimWaterPacTable.database}.${DimWaterPacTable.schema}.${DimWaterPacTable.name}`;

    const DimCompanyTable = { database: databuffet.DATABASE, schema: databuffet.DIMENSION_TABLE, name: "dim_company" };
    const DimCompanyTableRef = `${DimCompanyTable.database}.${DimCompanyTable.schema}.${DimCompanyTable.name}`;

    const MdsSourceTable = { database: databuffet.DATABASE, schema: "mds_dataset", name: "mds_data_waterpac_master" };
    const MdsSourceTableRef = `${MdsSourceTable.database}.${MdsSourceTable.schema}.${MdsSourceTable.name}`;
}

BEGIN
  DECLARE max_sk INT64 DEFAULT 0;
  SET max_sk = (SELECT IFNULL(MAX(WaterPacSK), 0) FROM `${DimWaterPacTableRef}`);

  MERGE `${DimWaterPacTableRef}` AS T
  USING (
    SELECT
      (CASE
        WHEN t3.WaterPacSK IS NOT NULL THEN t3.WaterPacSK   -- 1) matched by MdsID
        WHEN t2.WaterPacSK IS NOT NULL THEN t2.WaterPacSK   -- 2) matched by natural key
        ELSE max_sk + ROW_NUMBER() OVER(                    -- 3) truly new → new SK
          PARTITION BY (CASE WHEN t2.WaterPacSK IS NULL AND t3.WaterPacSK IS NULL THEN 1 ELSE 0 END)
          ORDER BY
            ${databuffet.functionData.cleanString("t1.CompanyID")},
            ${databuffet.functionData.cleanString("t1.WaterPacCode")}
        )
      END) AS WaterPacSK,
      dim_com.CompanySK,
      ${databuffet.functionData.cleanString("t1.CompanyID")} AS CompanyID,
      ${databuffet.functionData.cleanString("t1.WaterPacCode")} AS WaterPacCode,
      ${databuffet.functionData.cleanString("t1.WaterPacName")} AS WaterPacName,
      ${databuffet.functionData.cleanString("t1.id")} as MdsID
    FROM `${MdsSourceTableRef}` AS t1
    LEFT JOIN `${DimCompanyTableRef}` AS dim_com
      ON ${databuffet.functionData.cleanString("t1.CompanyID")} = dim_com.companyID
    LEFT JOIN `${DimWaterPacTableRef}` AS t2                -- natural-key self-join
      ON ... CompanyID = t2.CompanyID AND ... WaterPacCode = t2.WaterPacCode
    LEFT JOIN `${DimWaterPacTableRef}` AS t3                -- MdsID self-join
      ON ${databuffet.functionData.cleanString("t1.id")} = t3.MdsID
    WHERE t1.is_active = TRUE
      AND DATE(t1.updated_at) >= DATE_SUB(
            CURRENT_DATE("Asia/Bangkok"),
            INTERVAL ${databuffet.MDS_BACKFILL_DAYS} DAY)   -- incremental window
  ) AS S
  ON T.WaterPacSK = S.WaterPacSK

  WHEN MATCHED THEN
    UPDATE SET T.WaterPacName = S.WaterPacName, ..., T.MdsID = S.MdsID
    -- descriptive attributes + MdsID only; NEVER the key columns

  WHEN NOT MATCHED THEN
    INSERT (WaterPacSK, CompanySK, CompanyID, WaterPacCode, ..., MdsID)
    VALUES (S.WaterPacSK, ...);

  DELETE FROM `${DimWaterPacTableRef}`                      -- tombstone (see mds-delete-pattern.md)
  WHERE MdsID IN (
    SELECT id FROM `${MdsSourceTableRef}` WHERE is_active = FALSE
  );
END;
```

## Why the dual self-join (t2 + t3)

| Join | Matches on | Handles |
|---|---|---|
| `t3` (checked first) | `MdsID` = mds `id` | Same mds row whose natural key was *edited* — SK survives the change |
| `t2` | natural/business key | Row loaded before `MdsID` existed, or re-created mds row with the same business key — SK is reused |
| neither | — | Truly new row → `max_sk + ROW_NUMBER()` |

The `PARTITION BY (CASE WHEN both NULL THEN 1 ELSE 0 END)` makes ROW_NUMBER count only
over genuinely-new rows, so existing SK holders don't inflate the sequence.

## Invariants — do not break

1. **SK stability**: a business entity keeps its SK forever (facts store SKs).
   Never UPDATE key columns; never regenerate SKs for matched rows.
2. **MERGE ON the SK** (computed in the sub-select), not the natural key —
   this is what makes the CASE logic the single source of truth.
3. **`WHERE t1.is_active = TRUE`** + `MDS_BACKFILL_DAYS` window on the source.
4. **Trailing DELETE has no date filter** (scans the whole mds table) — intentional;
   mds masters are small and inactive rows must be removed regardless of when they
   were deactivated.
5. New file = copy an existing one and rename the SK/keys — the structure is
   deliberately uniform.

## Known caveats

- If a MERGE run fails midway, `max_sk` is re-read next run, so SK gaps can appear —
  harmless.
- Deleting dim rows can orphan SKs already copied into facts (hard-delete decision of
  2026-07-10; live scan found 0 orphans at implementation time). The daily full-rebuild
  tables (`dim_target_product_group_by_sale*`) self-heal automatically.
- SK reactivation: if an mds row flips back to `is_active = TRUE` after deletion, the
  t2 natural-key join (or t3 if a row still exists) reassigns — but after a hard delete
  the entity gets a **new** SK.
