---
name: fk-integrity-scan
description: Scan live BigQuery data for dangling surrogate-key references (fact/dim SK values with no matching dimension row). Use for periodic integrity checks or after dimension deletes/rebuilds.
---

Re-runs the SK-orphan scan first performed 2026-07-09 (result then: 172 relationships,
0 orphans). Relevant because mds dims hard-delete inactive rows
(`document/project_wiki/dimension/mds-delete-pattern.md`) — orphans are expected to
appear eventually and this scan quantifies them.

Method (all via `bq --project_id=databuffet-nonprd query --use_legacy_sql=false`):

1. **Build the column inventory** per dataset (region-level INFORMATION_SCHEMA is
   denied — always dataset-level), for `fact_table`, `dimension_table`,
   `bridge_dataset`, `process_dataset`:
   ```sql
   SELECT table_name, column_name
   FROM `databuffet-nonprd.<dataset>.INFORMATION_SCHEMA.COLUMNS`
   WHERE column_name LIKE '%SK'
   ```
2. **Map each SK column to its owning dim** using
   `document/project_wiki/dimension/inventory.md` (SK → dim table). Known ambiguous —
   skip and report: `BillingSK` (no owning dim found), `DueAvgCollectSK`/
   `InvAvgCollectSK` (likely dim_avg_collection_score role-play), `DueGradeSK`/
   `InvoiceGradeSK` (likely dim_grade role-play).
3. **Generate one batched query**: per (child_table, sk_column, owner_dim) emit
   ```sql
   SELECT '<child>.<col>' AS rel, COUNT(*) AS orphans
   FROM `<child>` c
   WHERE c.<col> IS NOT NULL
     AND NOT EXISTS (SELECT 1 FROM `<owner_dim>` d WHERE d.<owner_sk> = c.<col>)
   ```
   joined with `UNION ALL`. Generate the SQL with a small Python script in the
   scratchpad if the list is long.
4. **Report**: relationships scanned, orphan counts > 0 (with child/dim names),
   skipped ambiguous columns. Compare against the 2026-07-09 baseline (0 everywhere).

Exclusions to remember: `dim_target_product_group_by_sale(_dayofwork)` and `dim_*_last`
are full daily rebuilds with unstable SKs — orphans against them are only meaningful
same-day.
