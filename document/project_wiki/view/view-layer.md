# View Layer (`definitions/view/`)

> **LLM context**: The presentation layer — BigQuery **views** that sit on top of the
> physical dim/fact/curated/validated tables (and a few external sources). Migrated
> into Dataform on **2026-07-24** from views that previously lived only in BigQuery
> (created by hand in the console). 42 views, `type: "view"`, tag `view`.
>
> **Non-obvious constraints:**
> - **A view's folder is not its dataset.** Files live under `definitions/view/<dataset>/`
>   purely for organization; the BigQuery target is set by `config.schema` and **must
>   stay the original dataset** (`dimension_view`, `fact_view`, `onetime`,
>   `process_dataset`, `bridge_dataset`) so Power BI / downstream consumers that point
>   at those datasets keep working.
> - Views are **logical** — `CREATE OR REPLACE VIEW` stores no data. Correctness at
>   query time depends on the underlying *tables* having data, not on when the view DDL
>   ran. This is why an existing table (`fact_transcation`) can read a view
>   (`dimension_view.view_dim_channel`) without a Dataform dependency and still work.
> - `dependencies[]` lists only Dataform actions that are **not** read through `${ref()}`
>   — i.e. dims, facts and upstream views (unique `.sqlx` basenames). Two exclusions:
>   1. **`validated_*` / `curated_*` are read via `${ref()}` and must NOT be listed**
>      — Dataform wires those edges itself (double-listing is banned by coding-standard §10).
>   2. Things this repo does not build are interpolated but not listed (they pre-exist):
>      `mds_dataset.*`, `onetime.mapping_invoice`, `process_dataset.RLS_Customer360`,
>      `process_dataset.mih_address_data`, UDFs (`function_dataset.fn_*` — created together
>      by `create_all_function`, not separate actions), and `dim_districts`, `dim_provinces`,
>      `dim_geographies`, `dim_sub_districts`, `dim_aging_history`, `dim_product_rebate`.

## Pattern

Blocks in fixed order: `config` → `js` (optional) → SQL body. References follow the
project-wide two-tier rule in
[coding-standards/sqlx-coding-standard.md §3](../../coding-standards/sqlx-coding-standard.md):
**`${ref()}` for validated/curated, js-block `TableRef` for everything else.**

```js
config {
  type: "view",
  schema: databuffet.DIMENSION_VIEW,          // original target dataset — DO NOT change
  dependencies: ["dim_company"],              // NON-ref() repo actions only (dims/facts/views)
  tags: [databuffet.TAG_VIEW],
}

js {
    const DimCompanyTable = {
        database: databuffet.DATABASE,
        schema: databuffet.DIMENSION_TABLE,
        name: "dim_company",
    };
    const DimCompanyTableRef = `${DimCompanyTable.database}.${DimCompanyTable.schema}.${DimCompanyTable.name}`;
}

SELECT ...
FROM `${DimCompanyTableRef}`                        -- dimension: js-block ref
LEFT JOIN ${ref(databuffet.CURATED_MAC5, "curated_mih")} AS mih   -- curated: ref()
```

Rules:
1. `validated_*` / `curated_*` → `${ref(databuffet.<CONST>, "<table>")}`, **no backticks**,
   and the table must **not** appear in `dependencies[]` (Dataform wires it).
2. Everything else → declare `<Pascal>Table` + `<Pascal>TableRef` in `js`, use
   `` `${XxxTableRef}` ``: repo dims/facts, other views, `process_dataset`,
   `mds_dataset`, `onetime` bases, `function_dataset`, `RLS_Customer360`. Repo actions
   among these go in `dependencies[]`.
3. No inline `` `${databuffet.DATABASE}.${databuffet.X}.tbl` ``, no `databuffet-nonprd`
   literal. Declarations follow first-use order; declare only what is used. A view that
   reads only validated/curated has **no `js` block** (e.g. `Dimension_Quotation`).
4. No trailing `;` (the view DDL wraps the query).
5. Dataset → constant map is the same registry as everywhere else
   (`includes/controller/variables.json`).

### Run order caveat (documented, not yet wired)

- `onetime.Transaction_Data_Mart` (view) is a **source of `fact_transcation`** (the
  fact table). `fact_transcation.sqlx` also already reads `dimension_view.view_dim_channel`.
  These fact→view edges are **not** declared as dependencies on the fact side (the fact
  files were deliberately left untouched during migration). The pipeline stays correct
  because the views pre-exist and are logical; but for a fully-connected DAG a
  follow-up should add those view dependencies to the consuming fact files.

## Inventory (42 views)

### `dimension_view` → schema `DIMENSION_VIEW` (16)

| View | Key upstream (repo tables) | External refs (not deps) |
|---|---|---|
| `view_dim_aging` | dim_aging, dim_aging_rang, dim_sale_representative_last, view_dim_channel | — |
| `view_dim_aging_history` | view_dim_channel | dim_aging_history |
| `view_dim_channel` | dim_channel, dim_channel_cost, dim_channel_finance, dim_channel_sales | — |
| `view_dim_company` | dim_company | — |
| `view_dim_customer` | dim_customer, dim_group_customer | mds ×3, dim_districts/provinces/geographies/sub_districts |
| `view_dim_customer_credit_management` | dim_customer, dim_customer_grade | — |
| `view_dim_guarantee` | dim_customer, dim_guarantee | — |
| `view_dim_invoice` | dim_aging, dim_invoice | fn_flag_scg |
| `view_dim_order` | dim_order, mih2 | fn_order_type |
| `view_dim_product_master` | dim_product_master, dim_product_mkt, dim_rebate, dim_waterpac | — |
| `view_dim_product_mkt` | dim_product_mkt, dim_product_mkt_director | — |
| `view_dim_sale_representative` | dim_department, dim_sale_representative | — |
| `view_dim_sale_representative_last` | dim_department_last, dim_sale_representative_last | — |
| `view_dim_target_by_agent` | dim_rate_target + 9 dims | — |
| `view_dim_target_by_agent_dayofwork` | dim_calendar + 8 dims | — |
| `view_sales_representative_last` | dim_department_last, dim_region_last, dim_section_last, view_dim_sale_representative_last | — |

### `fact_view` → schema `FACT_VIEW` (4)

| View | Key upstream | External refs |
|---|---|---|
| `view_fact_transcation` | fact_invoice, fact_order, fact_transcation, curated_mih, deb, ~20 dims, view_dim_aging, view_dim_invoice | mds, onetime.mapping_invoice, fn_flag_scg/exc |
| `view_aging_ri` | fact_mir_vs, dim_aging_rang, dim_invoice, dim_status_not_receive, curated_mih, ar_s/chq/cql/mir, view_dim_aging | — |
| `view_fact_mir_rs` | fact_mir_rs, dim_aging, curated_mih, ar_s | — |
| `view_fact_mir_vs` | fact_mir_vs, dim_aging | — |

### `onetime` → schema `ONETIME` (16 — data marts / Power BI / models)

| View | Key upstream | External refs |
|---|---|---|
| `Transaction_Data_Mart` | curated_mih/mil/tbook_quotation, dim_company, view_deb_address_data, stk | fn_flag_sales_kpi, dim_product_rebate |
| `Model_Invoice_Transaction` | 15 dims, view_fact_transcation, view_dim_customer | — |
| `Model_Target_DayOfWork` | 11 dims | — |
| `PowerBI_Data_Buffet_Transaction` | curated_mih/mil, stk | — |
| `Dimension_Customer` | validated_cis360 ×5, deb, match_customer, view_deb_address_data | dim_provinces/geographies |
| `Dimension_Cheque` | chq, cql, mir | — |
| `Dimension_Delivery` | curated_mih/mil, deb, tdelivery, ttrip, ttrip_document | — |
| `Dimension_Invoice` | ap_s, ar_s, mih, mih2 | — |
| `Dimension_Order` | curated_mih, ar_s | — |
| `Dimension_Project` | tbook_profilecomp | — |
| `Dimension_Quotation` | curated_tbook_quotation | — |
| `Product_Attribute` | dim_company, dim_product_master, stg, stk, mastersku ×4 | — |
| `Product_Master` | stg, stk, mastersku ×4 | dim_product_rebate |
| `Product_Master_ALL` | dim_product_master, dim_product_mkt_director, view_dim_product_mkt, Product_Attribute | — |
| `Sales_Per_Non_Master` | per, dim_sale_representative | — |
| `View_Product` | stg, stk, stk_mkt, mastersku ×5 | validated_mastersku.category |

**Excluded (test — not migrated):** `TEST_Data_Transaction`, `TEST_Data_Transaction_2`.

### `process_dataset` → schema `PROCESS_DATASET` (5)

| View | Key upstream | External refs |
|---|---|---|
| `view_deb_address_data` | deb_address_data | dim_districts/provinces/sub_districts |
| `view_mih_address_data` | — | mih_address_data (no .sqlx), dim geo ×3 |
| `view_rls_data` | dim_*_last ×6 | — |
| `view_rls_sale_data` | view_rls_data | mds, RLS_Customer360 |
| `view_rls_special_data` | — | mds ×2, RLS_Customer360 |

### `bridge_dataset` → schema `BRIDGE` (1)

| View | Key upstream |
|---|---|
| `GroupCustomerSK_CustomerSK` | dim_customer, dim_group_customer |

## Not migrated (12 total)

- **Test (5):** `onetime.TEST_Data_Transaction`, `onetime.TEST_Data_Transaction_2`,
  `temp_dim.fact_transcation`, `temp_dim.view_dim_aging`, `temp_dim.view_fact_transcation`.
- **`peem_using` dataset — excluded entirely (7):** the four
  `view_1..4_Product_DOS_CAT1*` (wrap externally-loaded `peem_using.Product_*` tables),
  plus `view_rls_data` / `view_rls_sale_data` / `view_rls_special_data` — the RLS trio
  in `peem_using` is a **personal test copy** of the `process_dataset` RLS views and is
  intentionally not managed by Dataform. (The canonical RLS views live in
  `process_dataset`.) No `PEEM_USING` dataset constant exists.

## Compile-verification checklist (local `dataform` CLI unavailable)

1. All 42 views compile and the `view` tag runs after the table-building tags.
2. Views referencing other views (chains — e.g. `view_dim_aging` → `view_dim_channel`,
   `Model_Invoice_Transaction` → `view_fact_transcation`) resolve in the right order.
