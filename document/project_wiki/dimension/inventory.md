# Dimension Inventory — all 59 files

> **LLM context**: SK = surrogate key column; NK = natural/business key (t2 self-join /
> MERGE ON). Most dims also carry `CompanySK` FK from `dim_company`.
> Groups: (a) mds MERGE, (b) lake MERGE, (c) full rebuild, (e) other.

## Group (a) — MERGE from mds_dataset (36)

| File | SK | Natural key | mds source table |
|---|---|---|---|
| dim_company | CompanySK | CompanyID, CompanyCode | mds_data_company_master |
| dim_aging_rang | AgingRangSK | companyID, AgingDayMin, AgingDayMax | mds_data_aging_rang_master |
| dim_avg_collection_score | AvgCollectSK | companyID, AvgCollectiondayMin/Max, StartDate, EndDate | mds_data_custgrade_score_master |
| dim_bounce_cheque_score | BounceChequeSK | companyID, BouncedChequeMin/Max, StartDate, EndDate | mds_data_custgrade_cheque_score_master |
| dim_channel | ChannelSK | companyID, DepCode | mds_data_channel_master |
| dim_channel_cost | ChannelCostSK | companyID, ChannelCostID | mds_data_channel_cost_master |
| dim_channel_finance | ChannelFinanceSK | companyID, ChannelIDFinance | mds_data_channel_finance_master |
| dim_channel_sales | ChannelSaleSK | companyID, ChannelID | mds_data_channel_sales_master |
| dim_collection_status | CollectSK | CompanyID, CustomerID, Month, Year | mds_data_collection_status_master |
| dim_contact_score | ContactSK | companyID, ContactYearMin/Max, StartDate, EndDate | mds_data_custgrade_contact_score_master |
| dim_cost_group | CostGroupSK | companyID, ChannelCostID, GAccID, StartDate, EndDate | mds_data_standard_cost_by_product_group_master |
| dim_cost_stk | CostStkSK | companyID, ChannelCostID, GaccID, MilStk, StartDate, EndDate | mds_data_standard_cost_by_product_id_master |
| dim_department | DepartmentSK | companyID, DepartmentID, RegionID, SectionID, StartDate, EndDate | mds_data_sales_department_master |
| dim_director | DirectorSK | companyID, DirectorID, StartDate, EndDate | mds_data_sales_director_master |
| dim_doctype | *(SK commented out)* | companyID, Code — MERGE ON natural key | mds_data_document_type_master |
| dim_grade | GradeSK | companyID, Percentmin, Percentmax, StartDate, EndDate | mds_data_custgrade_master |
| dim_guarantee | GuaranteeSK | CompanyID, CustomerCode | mds_data_guarantee_document_master |
| dim_holiday | *(SK commented out)* | HolidayDate — MERGE ON natural key | mds_data_holiday_master |
| dim_payment | PaymentSK | companyID, CodeMemo | mds_data_payment_master |
| dim_payment_receive_score | PaymentReceiveSK | companyID, PaymentReceivedMin/Max, StartDate, EndDate | mds_data_custgrade_payment_receive_score_master |
| dim_product_master_fc | ProductMasterFcSK | companyID, ProductIDOldMac5 | mds_data_product_finance_master |
| dim_product_mkt | ProductMktSK | CompanyID, MarketingGroupID, SubMarketingID, SegmentID, TypeMarketingID | mds_data_product_marketing_name_master |
| dim_product_mkt_director | ProductMktDirectorSK | CompanyID, TypeMarketingID | mds_data_product_marketing_director_master |
| dim_rate_target | RateTargetSK | companyID, TargetID, TargetDepartmentID, ProductGroupID, Month, Year | mds_data_target_rate_master |
| dim_rebate | RebateSK | companyID, rebate, status | mds_data_sales_kpi_condition_master (uses `databuffet.MDS_DATASET`) |
| dim_region | RegionSK | companyID, RegionID, SubRegionID, StartDate, EndDate | mds_data_sales_region_master |
| dim_region_manager | RegionManagerSK | companyID, RegionID, SubRegionID, StartDate, EndDate | mds_data_sales_region_manager_master |
| dim_report | ReportSK | companyID, ReportID, MarketingGroupID, RegionID | mds_data_sales_report_group_master |
| dim_sale_representative | SaleRepSK | companyID, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, StartDate, EndDate | mds_data_sales_representative_master + block 2: validated_mac5.per |
| dim_section | SectionSK | companyID, SectionID, StartDate, EndDate | mds_data_sales_section_master |
| dim_section_manager | SectionManagerSK | companyID, SectionID, StartDate, EndDate | mds_data_sales_section_manager_master |
| dim_status_not_receive | NotReceiveSK | CompanyID, StatusID | mds_data_payment_status_not_receive_master |
| dim_stk_mkt | StkMktSK | companyID, StkCode | mds_data_product_market_group_by_product_id_master + validated_mac5.stk (placeholders) |
| dim_target_product_group | TargetProductGroupSK | companyID, Year, Month, MarketingGroupID, SubMarketingID, SegmentID, ChannelTargetGroup, TargetID | mds_data_sales_target_by_product_group_master |
| dim_waterpac | WaterPacSK | CompanyID, WaterPacCode | mds_data_waterpac_master |
| dim_weight_score | WeightSK | CompanyID, Typeeng, Typethai, StartDate, EndDate | mds_data_custgrade_weight_score_master |

All depend on `dim_company` except `dim_company` (deps `[]`) and `dim_holiday` (no deps).

## Group (b) — MERGE from lake tables (10)

| File | SK | Sources | Deps |
|---|---|---|---|
| dim_customer | CustomerSK | validated_mac5 (match_customer, deb), validated_cis360 (customer_profile/status/type/nature_business), view_deb_address_data | dim_company |
| dim_invoice | InvoiceSK | curated_mih, ar_s/ap_s, curated_mil | dim_company, dim_order |
| dim_order | OrderSK | curated_mih, ar_s, curated_mil | dim_company |
| dim_delivery | DeliverySK | curated_mil, ttrip/ttrip_document/tdelivery, deb, curated_mih | dim_company |
| dim_project | ProjectSK | validated_mac5.tbook_profilecomp | dim_company |
| dim_quotation | QuotationSK | curated_tbook_quotation, tbook_quodetail, curated_mih/mil | dim_company, dim_project |
| dim_product_master | ProductSK (MERGE ON ProductCode + CompanySK) | validated_mac5 stk/stg, validated_mastersku product/product_detail | dim_company, dim_product_mkt, dim_rebate, dim_stk_mkt |
| dim_customer_grade | CustomerGradeSK | chq, cql, mie, mir, deb, mih, curated_mih | dim_customer, dim_aging, dim_calendar, dim_status_not_receive + 5 score dims |
| dim_group_customer | GroupCustomerSK | dim_customer | dim_customer |
| dim_group_customer_grade | GroupCustomerGradeSK | deb, chq, cql, mie, mir, mih, curated_mih | dim_calendar, dim_customer, dim_group_customer + score dims |

## Group (c) — full rebuild `type: "table"` (10)

| File | SK | Notes |
|---|---|---|
| dim_change_district | *(none; CompanySK FK)* | Plain SELECT from mds_data_change_section_master, `WHERE is_active = true` |
| dim_department_last / dim_director_last / dim_region_last / dim_region_manager_last / dim_section_last / dim_section_manager_last / dim_sale_representative_last | `<X>SK` via ROW_NUMBER | Latest SCD row per entity; NULL FK SKs backfilled by `update_sk_sale_rep_group` |
| dim_target_product_group_by_sale | TargetBySaleSK | Multi-CTE join of target/rate/report/product-mkt dims + `_last` family |
| dim_target_product_group_by_sale_dayofwork | TargetBySaleDayofworkSK | joins dim_calendar (working-day expansion); daily full rebuild, self-heals |

## Group (e) — other operations (3)

| File | What it does |
|---|---|
| dim_calendar | Date spine via `GENERATE_DATE_ARRAY` (next-year start → current+2 Dec-31), joins dim_holiday, weekend/holiday/long-weekend flags; TEMP → DELETE-by-Date → INSERT. **Tag `dimension_yearly`** |
| dim_aging | ~500-line AR aging engine over chq/cql/mir/mie/ar_s/cfs + curated mih/mil + dim_aging_history + view_dim_aging + fact_mir_vs + onetime.cfsinvclose2024 |
| update_sk_sale_rep_group | UPDATE-only: backfills FK SKs (RegionManagerSK, DirectorSK, SectionSK, ...) across the 7 `_last` tables via temp_data |
