# Source Systems

> **LLM context**: 4 raw sources land as AVRO in `gs://file-raw-data/<gcs_folder>/<table>/`
> plus one externally-loaded BigQuery dataset (`mds_dataset`).

## MAC5 — POS / ERP / Ledger (main source)

- Thai ERP system; tables use 3-letter codes (`mih` = invoice header, `mil` = invoice
  lines, `deb` = debtors/customers, `stk` = stock, `per` = personnel, `ap_s`/`ar_s` =
  AP/AR status, ...).
- **5 company instances**, each with its own raw dataset and GCS folder:
  `ag01` (flagship, ~73 tables), `aa05`, `ab01`, `ac02`, `ak02` (each ~14 tables).
- 14 validated tables UNION ALL across all five companies with a literal
  `company_id` column: `ap_s, ar_s, cfs, chq, cql, deb, dep, mie, mih, mil, mir, per, stg, stk`.
- Special GCS prefixes: `mac5_report` (stg_report, stgacc), `mac5_gps`
  (tdelivery, ttrip, ttrip_document).
- `ag01`-only quirks: split-sale percentages (`mih2`), sign flips for `mihtype='BS'`
  (`*_raw` companion columns), Thai-text memo parsing.

## MASTERSKU — Product master

- 11 tables: `product` (PK `prd_id`), `product_detail`, `brand`, `category`, `unit`,
  `vendor`, `product_group`, `product_group_cost_group`, `product_category`,
  `product_status`, `product_admin_status`.
- Nested JSON in `product_detail` (`prdDiminsionData.$.dimFeild`,
  `pd_spacific_fields.$.SpeciFeild`) holds size/color with Thai labels
  (`ขนาด`, `สี`) — parsed in `curated_product`.

## CIS360 — Customer reference data

- 24 tables, all incremental with PK `id`: core (`customer_profile`,
  `customer_address`, `juristic_profile`), lookups (province/district/sub_district/
  zipcode/country, customer_status/type, juristic_type, nature_business,
  organize_type, role_business, category, prefix), and bridges
  (`customer_profile_*`, `customer_to_*`).

## SALEOUT_MDT — Modern-trade sell-out

- Retailer sub-folders: **BT** (7 tables — sales_by_branch, stock_aging, turnover, ...),
  **GB** (`saleout_gb`), **HP** (`saleout_hp`), **TW** (`report_sale_subscription`).
- All `type: "incremental"` but tagged only `validated` (no sub-tag); mostly no
  `asatdate` partition; custom date parsing `PARSE_DATE('%Y/%m/%d', TRIM(...))`.

## mds_dataset — Master Data Service (external)

- **Not created by this repo.** Tables named `mds_data_<entity>_master`.
- Standard columns on every table: `id` (row id → stored as `MdsID` in dims),
  `is_active` (soft-delete flag), `updated_at`.
- Source of ~36 dimensions. Dims MERGE only rows with
  `is_active = TRUE AND updated_at >= today - MDS_BACKFILL_DAYS`, and delete dim rows
  whose mds source row has `is_active = FALSE`
  (see [dimension/mds-delete-pattern.md](../dimension/mds-delete-pattern.md)).
