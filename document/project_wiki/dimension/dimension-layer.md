# Dimension Layer — `definitions/dimension/`

> **LLM context**: 59 files (58 `dim_*` + `update_sk_sale_rep_group`), all writing to
> dataset `dimension_table`. Tag `dimension_daily` on 58 files; only `dim_calendar`
> uses `dimension_yearly`; `dimension_monthly` is defined but unused.
> `dim_company` is the DAG root — nearly every dim depends on it and carries `CompanySK`.

## Pattern groups (regrouped 2026-07-20)

| Group | Count | Files | Detail |
|---|---|---|---|
| (a) **Full daily rebuild from `mds_dataset`** — the default | 34 | all mds dims except dim_company/dim_aging_rang; specials: `dim_sale_representative`, `dim_stk_mkt` (UNION blocks), `dim_doctype`/`dim_holiday` (no SK) | [full-rebuild-pattern.md](full-rebuild-pattern.md) — **SKs regenerate daily, not stable across days** |
| (a2) MERGE from `mds_dataset` (legacy) | 2 | `dim_company` (SK persisted everywhere), `dim_aging_rang` (SK frozen in dim_aging_history) | [merge-sk-pattern.md](merge-sk-pattern.md), [mds-delete-pattern.md](mds-delete-pattern.md) |
| (b) MERGE from lake (validated/curated) | 10 | `dim_customer, dim_invoice, dim_order, dim_delivery, dim_project, dim_quotation, dim_product_master, dim_customer_grade, dim_group_customer, dim_group_customer_grade` | Same MERGE skeleton, `ref()` sources, **no mds DELETE** |
| (c) Other full-rebuild `type: "table"` | 10 | `dim_change_district`, 7× `*_last` snapshots, `dim_target_product_group_by_sale`, `..._dayofwork` | Inline `ROW_NUMBER()` SK, self-heals daily |
| (e) Other operations | 3 | `dim_calendar` (date spine, yearly), `dim_aging` (~500-line AR aging engine), `update_sk_sale_rep_group` (UPDATE-only SK backfill) | |

No `type: "view"` files exist here — `view_dim_aging` (dimension_view) and
`view_deb_address_data` (process_dataset) are defined elsewhere.

## Group (b): lake-sourced MERGE dims

Same BEGIN/max_sk/MERGE skeleton as (a) but the USING sub-select is a `WITH` pipeline
over `ref(databuffet.VALIDATED_MAC5, ...)` / curated / cis360 / mastersku. No
`is_active` tombstone (no mds master). MERGE ON is natural-key-based for some
(`dim_product_master`: `ON T.ProductCode = S.ProductCode AND T.CompanySK = S.CompanySK`)
and SK-based for others (invoice/order/customer).

## Group (c): full-rebuild tables

```javascript
config { type: "table", schema: databuffet.DIMENSION_TABLE,
         uniqueKey: ["<X>SK"], bigquery: { clusterBy: ["<X>SK"] } }
```
Single top-level SELECT, SK = `ROW_NUMBER() OVER (ORDER BY ...)` — **SKs are NOT stable
across runs** for this group. The `*_last` tables select the current SCD row per
entity: filter `WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate`
(enabled 2026-07-22 — only versions effective today) then
`QUALIFY ... ORDER BY StartDate DESC, EndDate DESC = 1`; they pre-declare
downstream SK FK columns as NULL, which `update_sk_sale_rep_group` backfills with
UPDATE statements afterward, and carry `StartDate`/`EndDate` through as output
columns (also inserted by the `dim_sale_representative_last` MERGE). (Ledger-rep
sentinel rows 1900-01-01→2499-12-31 always pass the filter.)

`dim_target_product_group_by_sale_dayofwork` is a large daily full-rebuild joining
`dim_calendar` (working-day expansion) — it **self-heals** after upstream deletes.

## SCD-2-style dims (StartDate/EndDate in the natural key)

`dim_avg_collection_score, dim_bounce_cheque_score, dim_contact_score, dim_cost_group,
dim_cost_stk, dim_department, dim_director, dim_grade, dim_payment_receive_score,
dim_region, dim_region_manager, dim_section, dim_section_manager,
dim_sale_representative, dim_weight_score, dim_change_district`

A new validity interval ⇒ a new SK. The `*_last` family collapses to current versions.
Sentinel range for ledger-only sales reps: `1900-01-01` → `2499-12-31`.

## Conventions

- SK column: PascalCase `<Entity>SK`; not always literal from the file name
  (`dim_collection_status → CollectSK`, `dim_status_not_receive → NotReceiveSK`,
  `dim_avg_collection_score → AvgCollectSK`, `dim_product_master → ProductSK`).
- js refs: `Dim<Name>Table` + `Dim<Name>TableRef`, `MdsSourceTable(Ref)`.
- SQL aliases: `t1` = source, `t2` = self-join on natural key, `t3` = self-join on
  `MdsID`, `dim_com` = dim_company lookup, `T`/`S` = MERGE target/source.
- `schema: "mds_dataset"` is a string literal in almost every file
  (only `dim_rebate` uses `databuffet.MDS_DATASET`).
- `hasOutput: true` set on `dim_aging`, `dim_customer`, `dim_sale_representative`.
- Full inventory of all 59 files: [inventory.md](inventory.md).
