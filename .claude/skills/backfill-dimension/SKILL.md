---
name: backfill-dimension
description: Backfill an mds-sourced dimension beyond the 1-day MDS_BACKFILL_DAYS window. Use after adding a new dim, after missed daily runs, or when mds rows edited earlier than yesterday are missing from a dim.
---

Why needed: every mds dim MERGE filters
`DATE(t1.updated_at) >= CURRENT_DATE('Asia/Bangkok') - MDS_BACKFILL_DAYS` (var = "1"),
so anything updated earlier never enters the MERGE. Pattern:
`document/project_wiki/dimension/merge-sk-pattern.md`.

Arguments: `$ARGUMENTS` = `<dim_name or "all"> [days]`.

Two supported methods — confirm with the user which one:

**A. Temporary var override (preferred, runs the real code)**
1. In the Dataform release/workflow settings, set `MDS_BACKFILL_DAYS` to a large
   value (e.g. `"3650"`).
2. Run the target dim action(s) (tag `dimension_daily` or specific actions).
3. **Revert the var** — leaving it large makes every daily MERGE scan the whole
   mds table.

**B. Manual one-off via bq (when settings can't be touched)**
Reproduce the file's MERGE in a bq script with the `updated_at` predicate removed.
Keep everything else identical — especially the SK CASE (t3 MdsID → t2 natural key →
max_sk + ROW_NUMBER) and the `is_active = TRUE` filter. Run with
`bq --project_id=databuffet-nonprd query --use_legacy_sql=false < script.sql`.

Verification afterward:
```sql
-- rows in mds active but missing from dim (expect 0)
SELECT COUNT(*) FROM `databuffet-nonprd.mds_dataset.<mds_table>` m
WHERE m.is_active = TRUE
  AND NOT EXISTS (SELECT 1 FROM `databuffet-nonprd.dimension_table.<dim>` d
                  WHERE d.MdsID = CAST(m.id AS STRING));
```
Also check duplicate SKs: `SELECT <SK>, COUNT(*) ... GROUP BY 1 HAVING COUNT(*) > 1`.

Note: the tombstone DELETE has no date window, so inactive-row cleanup never needs
backfilling — only inserts/updates do.
