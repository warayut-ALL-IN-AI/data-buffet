# Validated Layer — Source Inventory

> **LLM context**: Table-level inventory per source. Descriptions of MAC5 3-letter
> codes are inferred from column prefixes — verify in-file when it matters.
> Authoritative full-load list: `grep -l 'TAG_VALIDATED_FULL' definitions/validated/mac5/`.

## MAC5 (87 files = 13 incremental + 73 full + 1 schema)

### Incremental (transactional)

| Table | Meaning (inferred) |
|---|---|
| `mih` / `mih2` / `mih_dummy` | invoice/document header (multi-company) / header revision / staging variant |
| `mil` / `mil_dummy` | invoice line items (multi-company) / variant |
| `mie` / `mie_dummy` | invoice extra/expense lines (multi-company) / variant |
| `mir` | invoice receipt/return lines (multi-company; tagged FULL) |
| `cps` / `cps_dummy` | cost-per-stock movement / variant |
| `cql` | quotation lines (multi-company) |
| `cst` | cost/stock transactions |
| `rcv` | receiving / goods receipt |

### Full-load families (73 tables, grouped)

- **Multi-company masters**: `ap_s, ar_s` (AP/AR status), `cfs` (cashflow), `chq`
  (cheques), `deb` (debtors/customers), `dep` (departments), `per` (personnel),
  `stg` (stock group), `stk` (stock master)
- **Billing**: `mih_billing, mil_billing, log_print_billing`
- **Docs/reference codes**: `doc, cpp, cpx, cre, rno, sbl, std, stf, sto, stgacc,
  stk_mkt, tab, vmp, mec, mip, check_po, grp`
- **Contract/quote-spread**: `maincontract, supcontract, main_qtspread,
  detail_qtspread, qt_spread_to_mih`
- **Booking (`tbook_*`)**: `tbook_apptype, tbook_givestk, tbook_payin,
  tbook_profilecomp, tbook_quodetail, tbook_quotation`; also `tbpjaddacc, tbcontact`
- **Distribution/approval (`tdis_*`) + logistics**: `tdis_approveorder, tdis_approveqt,
  tdis_mail, tdelivery, ttrip, ttrip_document`
- **Matching/BOT-RE**: `match_customer, match_product, match_deb_bot_re,
  product_bot_re, product_detail_bot_re`
- **Promotions/marketing**: `pro_ag, pro_crc, pro_re, product_promotion, mkt_per`
- **Combos**: `comboset, combostk`
- **PDF extracts per property developer**: `tmp_pdf_ap, tmp_pdf_frasers, tmp_pdf_pruksa,
  tmp_pdf_qh, tmp_pdf_sansiri, tmp_pdf_supalai`
- **Misc/ops**: `tmp_mihstatus, stg_report, pathfilestamper, tempgpsweb, apilog,
  userloginanyprogram, order_from_allkon_m`

## CIS360 (25 = 24 incremental + 1 schema) — PK `id`

- **Core**: `customer_profile`, `customer_address`, `juristic_profile`
- **Lookups**: `address_type, category, country, customer_status, customer_type,
  customer_profile_type, district, province, sub_district, zipcode, juristic_type,
  nature_business, organize_type, role_business, prefix`
- **Bridges**: `customer_profile_category, customer_profile_nature_business,
  customer_profile_role_business, customer_profile_tag, customer_to_customer,
  customer_to_platform, customer_to_transaction`

## MASTERSKU (12 = 11 incremental + 1 schema) — PK `prd_id` / `*_id`

`product` (SKU master), `product_detail` (JSON dims/specs), `product_category`,
`product_group`, `product_group_cost_group`, `product_status`, `product_admin_status`,
`brand`, `category`, `unit`, `vendor`

## SALEOUT_MDT (11 = 10 incremental + 1 schema) — by retailer subfolder

| Folder | Tables |
|---|---|
| `BT/` | `sales_by_branch`, `sale_by_branch_detail`, `sale_by_branch_mch3`, `stock_by_branch`, `stock_aging`, `turnover`, `turnover_brand` |
| `GB/` | `saleout_gb` |
| `HP/` | `saleout_hp` |
| `TW/` | `report_sale_subscription` |

All `type: "incremental"` but tagged only `validated`; PKs are wide business
composites (e.g. `["sale_no","sale_date","branch_code","product_code"]`).
