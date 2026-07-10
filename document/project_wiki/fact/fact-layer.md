# Fact Layer — `definitions/fact/`

> **LLM context**: 6 files, all in dataset `fact_table` (`databuffet.FACT_TABLE`),
> all tagged `fact_daily`. Three distinct materialization patterns — there is **no MERGE**
> in the fact layer. Dimension tables are referenced by raw string interpolation
> (`${...TableRef}`) + `dependencies[]`, while curated/validated sources use `${ref()}`.
> **Load-bearing typo**: the table/file is `fact_transcation` (not "transaction") — keep as-is.

## Inventory

| File | Target | Type | Pattern | Upsert keys | Partition / Cluster | Retention |
|---|---|---|---|---|---|---|
| `fact_order.sqlx` | `fact_order` | table | Dataform-managed rebuild | — (uniqueKey `FactOrderSk`) | `asatdate` / `FactOrderSk` | none active |
| `fact_invoice.sqlx` | `fact_invoice` | table | Dataform-managed rebuild | — (uniqueKey `FactInvoiceSK`) | `asatdate` / `FactInvoiceSK` | 4-year window in query |
| `fact_quotation.sqlx` | `fact_quotation` | operations | `DROP` + `CREATE OR REPLACE ... AS` | — | `asatdate` / `FactQuotationSK` | full refresh |
| `fact_transaction_delivery.sqlx` | `fact_transaction_delivery` | operations | `CREATE OR REPLACE TABLE AS` | — | `mix_date` / `FactTransDeliverySK` | 4-year window |
| `fact_delivery.sqlx` | `fact_delivery` | operations | `CREATE OR REPLACE TABLE AS` | — | (no partition) / `FactDeliverySK` | full refresh |
| `fact_transcation.sqlx` | `fact_transcation` | operations | **TEMP → DELETE → INSERT upsert** | `milVnos, milType, CompanySK` | `mix_date` / `FactTranscationSK` | DELETE < 4-year trunc-to-year |

## Dimension SK joins per fact

| Fact | Dimensions joined |
|---|---|
| `fact_order` | dim_order, dim_company, dim_product_master, dim_customer, + `fact_quotation` (QuotationSK) — source `curated_mil` |
| `fact_invoice` | dim_invoice, dim_company, dim_customer, + `fact_order` (deduped `QUALIFY ROW_NUMBER()=1`) — source `curated_mil` |
| `fact_quotation` | dim_quotation, dim_company, dim_product_master, dim_customer — source `validated_mac5.tbook_quodetail` |
| `fact_transaction_delivery` | dim_invoice, dim_product_master, dim_company — source `curated_mil` (type='IS') |
| `fact_delivery` | dim_delivery, dim_company, + `fact_transaction_delivery` — sources `ttrip_document, ttrip, tdelivery, deb, curated_mih, curated_mil`; Thai delivery-status labels |
| `fact_transcation` | ~20 dims (see below) — source `onetime.Transaction_Data_Mart` |

## `fact_transcation` walkthrough (canonical upsert fact)

Dependencies: dim_product_master, dim_payment, dim_channel, dim_cost_stk, dim_cost_group,
dim_sale_representative, dim_department, dim_region, dim_region_manager, dim_section,
dim_section_manager, dim_director, dim_channel_cost, dim_stk_mkt, dim_product_mkt,
dim_target_product_group_by_sale_dayofwork, dim_change_district, dim_customer,
dim_company, plus `process_dataset.view_deb_address_data`.

```
BEGIN
  1. CREATE OR REPLACE TEMP TABLE temp_fact_transcation AS
     ├─ raw_transction : onetime.Transaction_Data_Mart + Product/Payment/Channel SKs
     │                   + deb.debgroup; mix_date from milYear/Month/Day;
     │                   filter mix_date >= DATE_TRUNC(CURRENT_DATE - 4 YEAR, YEAR)
     ├─ final_part1    : sales-org hierarchy SKs (SaleRep→Department→Region→
     │                   RegionManager→Section→SectionManager→Director) via
     │                   seq_condition priority 1-5 matching on dim_sale_representative;
     │                   QUALIFY keeps best seq_condition per line;
     │                   excludes ChannelCostID = 'COST99999'
     ├─ final_part2    : COST99999 special case — re-derive ChannelCostID via
     │                   dim_channel_cost add-on chain, re-join CostStk/CostGroup
     ├─ mix_table      : part1 UNION ALL part2
     └─ final SELECT   : + address SKs (view_deb_address_data), dim_stk_mkt,
                         dim_product_mkt, dim_target_product_group_by_sale_dayofwork,
                         dim_customer
  2. DELETE FROM fact_transcation T WHERE EXISTS (
       SELECT 1 FROM temp WHERE T.milVnos=S.milVnos AND T.milType=S.milType
       AND T.CompanySK=S.CompanySK)
  3. INSERT INTO fact_transcation SELECT * FROM temp
END;
BEGIN  -- retention purge
  DELETE FROM fact_transcation
  WHERE mix_date < DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR);
END;
```

Because it's `operations`, the target table must already exist — Dataform does not create it.

## Conventions

- Fact PK column: `Fact<Entity>SK` (PascalCase; casing occasionally inconsistent — `FactOrderSk`).
- `mix_date` = business date derived by `PARSE_DATE('%Y%m%d', CONCAT(milYear, milMonth, milDay))`.
- `asatdate` = `CURRENT_DATE('Asia/Bangkok')` snapshot column.
- Retention = rolling 4 years, truncated to start-of-year.
- New fact checklist → see [how-to/add-fact-table.md](../../how-to/add-fact-table.md).
