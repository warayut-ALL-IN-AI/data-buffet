# MDS Inactive-Row DELETE (tombstone) Pattern

> **LLM context**: ⚠️ Scope shrank on **2026-07-20**: 34 mds dims were converted to
> [full daily rebuild](full-rebuild-pattern.md) (rebuild from `is_active = TRUE`
> makes the tombstone unnecessary), so this pattern now applies to only the **2
> remaining MERGE dims: `dim_company` and `dim_aging_rang`**.
> History: implemented 2026-07-10 across all then-MERGE mds dims (commit `e64a62d`).
> Design decision: **hard DELETE, no downstream FK checks** — chosen explicitly over
> a soft-delete `IsActive` flag.

## The problem it solves

Every mds-sourced dim MERGE filters `WHERE t1.is_active = TRUE`. Rows deactivated at
the mds source (soft-deleted) therefore stayed in the dimension forever — the dim
never saw them again.

## The pattern

Placed as the **last statement before `END;`** of the mds MERGE block:

```sql
  DELETE FROM `${Dim<Name>TableRef}`
  WHERE MdsID IN (
    SELECT id FROM `${MdsSourceTableRef}` WHERE is_active = FALSE
  );
END;
```

Properties:

- **No date filter** — intentionally scans the whole mds table so rows deactivated at
  any time are removed (mds masters are small reference tables).
- **NULL-safe by construction**: `WHERE MdsID IN (subquery)` never matches rows with
  `MdsID IS NULL` — this protects placeholder rows such as `dim_stk_mkt`'s
  'Waiting Master' rows (inserted with `MdsID = NULL`).
- **No downstream checks**: facts referencing a deleted SK keep the orphan value.
  Accepted risk per the 2026-07-10 decision; a full live scan of 172 SK relationships
  (fact_table, dimension_table, bridge_dataset, process_dataset) found **0 dangling
  SK-FKs** at implementation time.

## Where it applies (36 files)

All MERGE-based mds dims: dim_aging_rang, dim_avg_collection_score,
dim_bounce_cheque_score, dim_channel, dim_channel_cost, dim_channel_finance,
dim_channel_sales, dim_collection_status, dim_company, dim_contact_score,
dim_cost_group, dim_cost_stk, dim_department, dim_director, dim_doctype, dim_grade,
dim_guarantee, dim_holiday, dim_payment, dim_payment_receive_score,
dim_product_master_fc, dim_product_mkt, dim_product_mkt_director, dim_rate_target,
dim_rebate, dim_region, dim_region_manager, dim_report, dim_sale_representative,
dim_section, dim_section_manager, dim_status_not_receive, dim_stk_mkt,
dim_target_product_group, dim_waterpac, dim_weight_score.

Verify anytime with `grep -L "is_active = FALSE" $(grep -l "mds_data" definitions/dimension/*.sqlx)`
— only `dim_change_district` should appear.

> History: the 2026-07-10 batch initially covered 35 files; `dim_rebate` was missed
> because it references the schema via `databuffet.MDS_DATASET` instead of the literal
> `"mds_dataset"` string the scan grepped for. Added 2026-07-10 (same day, follow-up).

Exclusions:
- **`dim_change_district`** — mds-sourced but `type: "table"` full rebuild; the
  `WHERE is_active = true` filter already drops inactive rows every run.
- **`dim_sale_representative` block 2** — the fallback-reps MERGE from
  `validated_mac5.per` has no MdsID; the DELETE lives at the end of **block 1 only**.
- Lake-sourced dims (group b) — no mds master to tombstone against.

## Consequences to remember

| Scenario | Outcome |
|---|---|
| mds row set `is_active = FALSE` | Dim row hard-deleted on next daily run |
| Same row later reactivated | Re-inserted with a **new SK** (old SK is gone) |
| Fact rows holding the deleted SK | Orphaned (accepted); daily full-rebuild dims (`dim_target_product_group_by_sale*`) self-heal |
| Placeholder rows (`MdsID IS NULL`) | Never deleted (IN-subquery can't match NULL) |
