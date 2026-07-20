# Pipeline Lineage — full dependency graph

> ⚠️ **Auto-generated — do not edit by hand.** Regenerate after any change to
> `definitions/` with:
>
> ```bash
> python3 document/diagrams/generate_lineage.py
> ```
>
> The script parses every `.sqlx` (both the `dependencies: [...]` array and
> inline `ref(...)` calls), so the graph always reflects the live repo. Edges
> point **source → consumer**. Paused objects (config commented out) are drawn
> dashed/grey and their outgoing edges are omitted.

**Objects: 229** — initial 15 · validated 135 · curated 8 · dimension 59 · fact 9 · cdc 2 · process 1

**Paused:** fact_chq, fact_mir_rs, fact_mir_vs

```mermaid
flowchart LR
  subgraph initial["initial (15)"]
    create_all_function["create_all_function"]
    create_all_schema["create_all_schema"]
    create_all_table_raw_cis360["create_all_table_raw_cis360"]
    create_all_table_raw_mac5["create_all_table_raw_mac5"]
    create_all_table_raw_mac5_aa05["create_all_table_raw_mac5_aa05"]
    create_all_table_raw_mac5_ab01["create_all_table_raw_mac5_ab01"]
    create_all_table_raw_mac5_ac02["create_all_table_raw_mac5_ac02"]
    create_all_table_raw_mac5_ak02["create_all_table_raw_mac5_ak02"]
    create_all_table_raw_mastersku["create_all_table_raw_mastersku"]
    create_all_table_raw_saleout_mdt["create_all_table_raw_saleout_mdt"]
    drop_all_tables_curated_mac5["drop_all_tables_curated_mac5"]
    drop_all_tables_validated_cis360["drop_all_tables_validated_cis360"]
    drop_all_tables_validated_mac5["drop_all_tables_validated_mac5"]
    drop_all_tables_validated_mastersku["drop_all_tables_validated_mastersku"]
    drop_all_tables_validated_saleout_mdt["drop_all_tables_validated_saleout_mdt"]
  end
  subgraph validated["validated (135)"]
    address_type["address_type"]
    ap_s["ap_s"]
    apilog["apilog"]
    ar_s["ar_s"]
    brand["brand"]
    category__cis360["category"]
    category__mastersku["category"]
    cfs["cfs"]
    check_po["check_po"]
    chq["chq"]
    comboset["comboset"]
    combostk["combostk"]
    country["country"]
    cpp["cpp"]
    cps["cps"]
    cps_dummy["cps_dummy"]
    cpx["cpx"]
    cql["cql"]
    cre["cre"]
    cst["cst"]
    customer_address["customer_address"]
    customer_profile["customer_profile"]
    customer_profile_category["customer_profile_category"]
    customer_profile_nature_business["customer_profile_nature_business"]
    customer_profile_role_business["customer_profile_role_business"]
    customer_profile_tag["customer_profile_tag"]
    customer_profile_type["customer_profile_type"]
    customer_status["customer_status"]
    customer_to_customer["customer_to_customer"]
    customer_to_platform["customer_to_platform"]
    customer_to_transaction["customer_to_transaction"]
    customer_type["customer_type"]
    deb["deb"]
    dep["dep"]
    detail_qtspread["detail_qtspread"]
    district["district"]
    doc["doc"]
    grp["grp"]
    juristic_profile["juristic_profile"]
    juristic_type["juristic_type"]
    log_print_billing["log_print_billing"]
    main_qtspread["main_qtspread"]
    maincontract["maincontract"]
    match_customer["match_customer"]
    match_deb_bot_re["match_deb_bot_re"]
    match_product["match_product"]
    mec["mec"]
    mie["mie"]
    mie_dummy["mie_dummy"]
    mih["mih"]
    mih2["mih2"]
    mih_billing["mih_billing"]
    mih_dummy["mih_dummy"]
    mil["mil"]
    mil_billing["mil_billing"]
    mil_dummy["mil_dummy"]
    mip["mip"]
    mir["mir"]
    mkt_per["mkt_per"]
    nature_business["nature_business"]
    order_from_allkon_m["order_from_allkon_m"]
    organize_type["organize_type"]
    pathfilestamper["pathfilestamper"]
    per["per"]
    pro_ag["pro_ag"]
    pro_crc["pro_crc"]
    pro_re["pro_re"]
    product["product"]
    product_admin_status["product_admin_status"]
    product_bot_re["product_bot_re"]
    product_category["product_category"]
    product_detail["product_detail"]
    product_detail_bot_re["product_detail_bot_re"]
    product_group["product_group"]
    product_group_cost_group["product_group_cost_group"]
    product_promotion["product_promotion"]
    product_status["product_status"]
    province["province"]
    qt_spread_to_mih["qt_spread_to_mih"]
    rcv["rcv"]
    report_sale_subscription["report_sale_subscription"]
    rno["rno"]
    role_business["role_business"]
    sale_by_branch_detail["sale_by_branch_detail"]
    sale_by_branch_mch3["sale_by_branch_mch3"]
    saleout_gb["saleout_gb"]
    saleout_hp["saleout_hp"]
    sales_by_branch["sales_by_branch"]
    sbl["sbl"]
    std["std"]
    stf["stf"]
    stg["stg"]
    stg_report["stg_report"]
    stgacc["stgacc"]
    stk["stk"]
    stk_mkt["stk_mkt"]
    sto["sto"]
    stock_aging["stock_aging"]
    stock_by_branch["stock_by_branch"]
    sub_district["sub_district"]
    supcontract["supcontract"]
    tab["tab"]
    tbcontact["tbcontact"]
    tbook_apptype["tbook_apptype"]
    tbook_givestk["tbook_givestk"]
    tbook_payin["tbook_payin"]
    tbook_profilecomp["tbook_profilecomp"]
    tbook_quodetail["tbook_quodetail"]
    tbook_quotation["tbook_quotation"]
    tbpjaddacc["tbpjaddacc"]
    tdelivery["tdelivery"]
    tdis_approveorder["tdis_approveorder"]
    tdis_approveqt["tdis_approveqt"]
    tdis_mail["tdis_mail"]
    tempgpsweb["tempgpsweb"]
    tmp_mihstatus["tmp_mihstatus"]
    tmp_pdf_ap["tmp_pdf_ap"]
    tmp_pdf_frasers["tmp_pdf_frasers"]
    tmp_pdf_pruksa["tmp_pdf_pruksa"]
    tmp_pdf_qh["tmp_pdf_qh"]
    tmp_pdf_sansiri["tmp_pdf_sansiri"]
    tmp_pdf_supalai["tmp_pdf_supalai"]
    ttrip["ttrip"]
    ttrip_document["ttrip_document"]
    turnover["turnover"]
    turnover_brand["turnover_brand"]
    unit["unit"]
    userloginanyprogram["userloginanyprogram"]
    validated_schema_cis360["validated_schema_cis360"]
    validated_schema_mac5["validated_schema_mac5"]
    validated_schema_mastersku["validated_schema_mastersku"]
    validated_schema_saleout["validated_schema_saleout"]
    vendor["vendor"]
    vmp["vmp"]
    zipcode["zipcode"]
  end
  subgraph curated["curated (8)"]
    curated_mih["curated_mih"]
    curated_mil["curated_mil"]
    curated_product["curated_product"]
    curated_schema_cis360["curated_schema_cis360"]
    curated_schema_mac5["curated_schema_mac5"]
    curated_schema_mastersku["curated_schema_mastersku"]
    curated_tbook_quotation["curated_tbook_quotation"]
    product_for_aisearch["product_for_aisearch"]
  end
  subgraph dimension["dimension (59)"]
    dim_aging["dim_aging"]
    dim_aging_rang["dim_aging_rang"]
    dim_avg_collection_score["dim_avg_collection_score"]
    dim_bounce_cheque_score["dim_bounce_cheque_score"]
    dim_calendar["dim_calendar"]
    dim_change_district["dim_change_district"]
    dim_channel["dim_channel"]
    dim_channel_cost["dim_channel_cost"]
    dim_channel_finance["dim_channel_finance"]
    dim_channel_sales["dim_channel_sales"]
    dim_collection_status["dim_collection_status"]
    dim_company["dim_company"]
    dim_contact_score["dim_contact_score"]
    dim_cost_group["dim_cost_group"]
    dim_cost_stk["dim_cost_stk"]
    dim_customer["dim_customer"]
    dim_customer_grade["dim_customer_grade"]
    dim_delivery["dim_delivery"]
    dim_department["dim_department"]
    dim_department_last["dim_department_last"]
    dim_director["dim_director"]
    dim_director_last["dim_director_last"]
    dim_doctype["dim_doctype"]
    dim_grade["dim_grade"]
    dim_group_customer["dim_group_customer"]
    dim_group_customer_grade["dim_group_customer_grade"]
    dim_guarantee["dim_guarantee"]
    dim_holiday["dim_holiday"]
    dim_invoice["dim_invoice"]
    dim_order["dim_order"]
    dim_payment["dim_payment"]
    dim_payment_receive_score["dim_payment_receive_score"]
    dim_product_master["dim_product_master"]
    dim_product_master_fc["dim_product_master_fc"]
    dim_product_mkt["dim_product_mkt"]
    dim_product_mkt_director["dim_product_mkt_director"]
    dim_project["dim_project"]
    dim_quotation["dim_quotation"]
    dim_rate_target["dim_rate_target"]
    dim_rebate["dim_rebate"]
    dim_region["dim_region"]
    dim_region_last["dim_region_last"]
    dim_region_manager["dim_region_manager"]
    dim_region_manager_last["dim_region_manager_last"]
    dim_report["dim_report"]
    dim_sale_representative["dim_sale_representative"]
    dim_sale_representative_last["dim_sale_representative_last"]
    dim_section["dim_section"]
    dim_section_last["dim_section_last"]
    dim_section_manager["dim_section_manager"]
    dim_section_manager_last["dim_section_manager_last"]
    dim_status_not_receive["dim_status_not_receive"]
    dim_stk_mkt["dim_stk_mkt"]
    dim_target_product_group["dim_target_product_group"]
    dim_target_product_group_by_sale["dim_target_product_group_by_sale"]
    dim_target_product_group_by_sale_dayofwork["dim_target_product_group_by_sale_dayofwork"]
    dim_waterpac["dim_waterpac"]
    dim_weight_score["dim_weight_score"]
    update_sk_sale_rep_group["update_sk_sale_rep_group"]
  end
  subgraph fact["fact (9)"]
    fact_chq["fact_chq (paused)"]
    fact_delivery["fact_delivery"]
    fact_invoice["fact_invoice"]
    fact_mir_rs["fact_mir_rs (paused)"]
    fact_mir_vs["fact_mir_vs (paused)"]
    fact_order["fact_order"]
    fact_quotation["fact_quotation"]
    fact_transaction_delivery["fact_transaction_delivery"]
    fact_transcation["fact_transcation"]
  end
  subgraph cdc["cdc (2)"]
    cdc_change_log["cdc_change_log"]
    cdc_schema["cdc_schema"]
  end
  subgraph process["process (1)"]
    deb_address_data["deb_address_data"]
  end
  ap_s --> curated_mih
  ap_s --> dim_invoice
  ar_s --> curated_mih
  ar_s --> dim_aging
  ar_s --> dim_invoice
  ar_s --> dim_order
  brand --> product_for_aisearch
  category__mastersku --> product_for_aisearch
  cdc_change_log --> deb_address_data
  cdc_change_log --> validated_schema_cis360
  cdc_change_log --> validated_schema_mac5
  cdc_change_log --> validated_schema_mastersku
  cdc_change_log --> validated_schema_saleout
  cdc_schema --> cdc_change_log
  cfs --> dim_aging
  chq --> dim_aging
  chq --> dim_customer_grade
  chq --> dim_group_customer_grade
  cql --> dim_aging
  cql --> dim_customer_grade
  cql --> dim_group_customer_grade
  create_all_function --> chq
  create_all_table_raw_cis360 --> address_type
  create_all_table_raw_cis360 --> category__cis360
  create_all_table_raw_cis360 --> country
  create_all_table_raw_cis360 --> customer_address
  create_all_table_raw_cis360 --> customer_profile
  create_all_table_raw_cis360 --> customer_profile_category
  create_all_table_raw_cis360 --> customer_profile_nature_business
  create_all_table_raw_cis360 --> customer_profile_role_business
  create_all_table_raw_cis360 --> customer_profile_tag
  create_all_table_raw_cis360 --> customer_profile_type
  create_all_table_raw_cis360 --> customer_status
  create_all_table_raw_cis360 --> customer_to_customer
  create_all_table_raw_cis360 --> customer_to_platform
  create_all_table_raw_cis360 --> customer_to_transaction
  create_all_table_raw_cis360 --> customer_type
  create_all_table_raw_cis360 --> district
  create_all_table_raw_cis360 --> juristic_profile
  create_all_table_raw_cis360 --> juristic_type
  create_all_table_raw_cis360 --> nature_business
  create_all_table_raw_cis360 --> organize_type
  create_all_table_raw_cis360 --> province
  create_all_table_raw_cis360 --> role_business
  create_all_table_raw_cis360 --> sub_district
  create_all_table_raw_cis360 --> validated_schema_cis360
  create_all_table_raw_cis360 --> zipcode
  create_all_table_raw_mac5 --> ap_s
  create_all_table_raw_mac5 --> apilog
  create_all_table_raw_mac5 --> ar_s
  create_all_table_raw_mac5 --> cdc_schema
  create_all_table_raw_mac5 --> cfs
  create_all_table_raw_mac5 --> check_po
  create_all_table_raw_mac5 --> chq
  create_all_table_raw_mac5 --> comboset
  create_all_table_raw_mac5 --> combostk
  create_all_table_raw_mac5 --> cpp
  create_all_table_raw_mac5 --> cps
  create_all_table_raw_mac5 --> cps_dummy
  create_all_table_raw_mac5 --> cpx
  create_all_table_raw_mac5 --> cql
  create_all_table_raw_mac5 --> cre
  create_all_table_raw_mac5 --> cst
  create_all_table_raw_mac5 --> deb
  create_all_table_raw_mac5 --> dep
  create_all_table_raw_mac5 --> detail_qtspread
  create_all_table_raw_mac5 --> doc
  create_all_table_raw_mac5 --> grp
  create_all_table_raw_mac5 --> log_print_billing
  create_all_table_raw_mac5 --> main_qtspread
  create_all_table_raw_mac5 --> maincontract
  create_all_table_raw_mac5 --> match_customer
  create_all_table_raw_mac5 --> match_deb_bot_re
  create_all_table_raw_mac5 --> match_product
  create_all_table_raw_mac5 --> mec
  create_all_table_raw_mac5 --> mie
  create_all_table_raw_mac5 --> mie_dummy
  create_all_table_raw_mac5 --> mih
  create_all_table_raw_mac5 --> mih2
  create_all_table_raw_mac5 --> mih_billing
  create_all_table_raw_mac5 --> mih_dummy
  create_all_table_raw_mac5 --> mil
  create_all_table_raw_mac5 --> mil_billing
  create_all_table_raw_mac5 --> mil_dummy
  create_all_table_raw_mac5 --> mip
  create_all_table_raw_mac5 --> mir
  create_all_table_raw_mac5 --> mkt_per
  create_all_table_raw_mac5 --> order_from_allkon_m
  create_all_table_raw_mac5 --> pathfilestamper
  create_all_table_raw_mac5 --> per
  create_all_table_raw_mac5 --> pro_ag
  create_all_table_raw_mac5 --> pro_crc
  create_all_table_raw_mac5 --> pro_re
  create_all_table_raw_mac5 --> product_bot_re
  create_all_table_raw_mac5 --> product_detail_bot_re
  create_all_table_raw_mac5 --> product_promotion
  create_all_table_raw_mac5 --> qt_spread_to_mih
  create_all_table_raw_mac5 --> rcv
  create_all_table_raw_mac5 --> rno
  create_all_table_raw_mac5 --> sbl
  create_all_table_raw_mac5 --> std
  create_all_table_raw_mac5 --> stf
  create_all_table_raw_mac5 --> stg
  create_all_table_raw_mac5 --> stg_report
  create_all_table_raw_mac5 --> stgacc
  create_all_table_raw_mac5 --> stk
  create_all_table_raw_mac5 --> stk_mkt
  create_all_table_raw_mac5 --> sto
  create_all_table_raw_mac5 --> supcontract
  create_all_table_raw_mac5 --> tab
  create_all_table_raw_mac5 --> tbcontact
  create_all_table_raw_mac5 --> tbook_apptype
  create_all_table_raw_mac5 --> tbook_givestk
  create_all_table_raw_mac5 --> tbook_payin
  create_all_table_raw_mac5 --> tbook_profilecomp
  create_all_table_raw_mac5 --> tbook_quodetail
  create_all_table_raw_mac5 --> tbook_quotation
  create_all_table_raw_mac5 --> tbpjaddacc
  create_all_table_raw_mac5 --> tdelivery
  create_all_table_raw_mac5 --> tdis_approveorder
  create_all_table_raw_mac5 --> tdis_approveqt
  create_all_table_raw_mac5 --> tdis_mail
  create_all_table_raw_mac5 --> tempgpsweb
  create_all_table_raw_mac5 --> tmp_mihstatus
  create_all_table_raw_mac5 --> tmp_pdf_ap
  create_all_table_raw_mac5 --> tmp_pdf_frasers
  create_all_table_raw_mac5 --> tmp_pdf_pruksa
  create_all_table_raw_mac5 --> tmp_pdf_qh
  create_all_table_raw_mac5 --> tmp_pdf_sansiri
  create_all_table_raw_mac5 --> tmp_pdf_supalai
  create_all_table_raw_mac5 --> ttrip
  create_all_table_raw_mac5 --> ttrip_document
  create_all_table_raw_mac5 --> userloginanyprogram
  create_all_table_raw_mac5 --> validated_schema_mac5
  create_all_table_raw_mac5 --> vmp
  create_all_table_raw_mac5_aa05 --> ap_s
  create_all_table_raw_mac5_aa05 --> ar_s
  create_all_table_raw_mac5_aa05 --> chq
  create_all_table_raw_mac5_aa05 --> cql
  create_all_table_raw_mac5_aa05 --> deb
  create_all_table_raw_mac5_aa05 --> dep
  create_all_table_raw_mac5_aa05 --> mih
  create_all_table_raw_mac5_aa05 --> mil
  create_all_table_raw_mac5_aa05 --> per
  create_all_table_raw_mac5_aa05 --> stg
  create_all_table_raw_mac5_aa05 --> stk
  create_all_table_raw_mac5_ab01 --> ap_s
  create_all_table_raw_mac5_ab01 --> ar_s
  create_all_table_raw_mac5_ab01 --> chq
  create_all_table_raw_mac5_ab01 --> cql
  create_all_table_raw_mac5_ab01 --> deb
  create_all_table_raw_mac5_ab01 --> dep
  create_all_table_raw_mac5_ab01 --> mih
  create_all_table_raw_mac5_ab01 --> mil
  create_all_table_raw_mac5_ab01 --> per
  create_all_table_raw_mac5_ab01 --> stg
  create_all_table_raw_mac5_ab01 --> stk
  create_all_table_raw_mac5_ac02 --> ap_s
  create_all_table_raw_mac5_ac02 --> ar_s
  create_all_table_raw_mac5_ac02 --> chq
  create_all_table_raw_mac5_ac02 --> cql
  create_all_table_raw_mac5_ac02 --> deb
  create_all_table_raw_mac5_ac02 --> dep
  create_all_table_raw_mac5_ac02 --> mih
  create_all_table_raw_mac5_ac02 --> mil
  create_all_table_raw_mac5_ac02 --> per
  create_all_table_raw_mac5_ac02 --> stg
  create_all_table_raw_mac5_ac02 --> stk
  create_all_table_raw_mac5_ak02 --> ap_s
  create_all_table_raw_mac5_ak02 --> ar_s
  create_all_table_raw_mac5_ak02 --> chq
  create_all_table_raw_mac5_ak02 --> cql
  create_all_table_raw_mac5_ak02 --> deb
  create_all_table_raw_mac5_ak02 --> dep
  create_all_table_raw_mac5_ak02 --> mih
  create_all_table_raw_mac5_ak02 --> mil
  create_all_table_raw_mac5_ak02 --> per
  create_all_table_raw_mac5_ak02 --> stg
  create_all_table_raw_mac5_ak02 --> stk
  create_all_table_raw_mastersku --> brand
  create_all_table_raw_mastersku --> category__mastersku
  create_all_table_raw_mastersku --> product
  create_all_table_raw_mastersku --> product_admin_status
  create_all_table_raw_mastersku --> product_category
  create_all_table_raw_mastersku --> product_detail
  create_all_table_raw_mastersku --> product_group
  create_all_table_raw_mastersku --> product_group_cost_group
  create_all_table_raw_mastersku --> product_status
  create_all_table_raw_mastersku --> unit
  create_all_table_raw_mastersku --> validated_schema_mastersku
  create_all_table_raw_mastersku --> vendor
  create_all_table_raw_saleout_mdt --> report_sale_subscription
  create_all_table_raw_saleout_mdt --> sale_by_branch_detail
  create_all_table_raw_saleout_mdt --> sale_by_branch_mch3
  create_all_table_raw_saleout_mdt --> saleout_gb
  create_all_table_raw_saleout_mdt --> saleout_hp
  create_all_table_raw_saleout_mdt --> sales_by_branch
  create_all_table_raw_saleout_mdt --> stock_aging
  create_all_table_raw_saleout_mdt --> stock_by_branch
  create_all_table_raw_saleout_mdt --> turnover
  create_all_table_raw_saleout_mdt --> turnover_brand
  create_all_table_raw_saleout_mdt --> validated_schema_saleout
  curated_mih --> dim_aging
  curated_mih --> dim_customer_grade
  curated_mih --> dim_delivery
  curated_mih --> dim_group_customer_grade
  curated_mih --> dim_invoice
  curated_mih --> dim_order
  curated_mih --> dim_quotation
  curated_mih --> fact_delivery
  curated_mih --> fact_transcation
  curated_mil --> dim_aging
  curated_mil --> dim_delivery
  curated_mil --> dim_invoice
  curated_mil --> dim_order
  curated_mil --> dim_quotation
  curated_mil --> fact_delivery
  curated_mil --> fact_invoice
  curated_mil --> fact_order
  curated_mil --> fact_transaction_delivery
  curated_mil --> fact_transcation
  curated_product --> product_for_aisearch
  curated_schema_mac5 --> curated_mih
  curated_schema_mac5 --> curated_mil
  curated_schema_mac5 --> curated_tbook_quotation
  curated_tbook_quotation --> dim_quotation
  customer_profile --> dim_customer
  customer_profile_nature_business --> dim_customer
  customer_status --> dim_customer
  customer_type --> dim_customer
  deb --> deb_address_data
  deb --> dim_customer
  deb --> dim_customer_grade
  deb --> dim_delivery
  deb --> dim_group_customer_grade
  deb --> fact_delivery
  deb --> fact_transcation
  dim_aging --> dim_customer_grade
  dim_aging --> dim_group_customer_grade
  dim_avg_collection_score --> dim_customer_grade
  dim_avg_collection_score --> dim_group_customer_grade
  dim_bounce_cheque_score --> dim_customer_grade
  dim_bounce_cheque_score --> dim_group_customer_grade
  dim_calendar --> dim_target_product_group_by_sale_dayofwork
  dim_change_district --> fact_transcation
  dim_channel --> fact_transcation
  dim_channel_cost --> fact_transcation
  dim_company --> dim_aging
  dim_company --> dim_aging_rang
  dim_company --> dim_avg_collection_score
  dim_company --> dim_bounce_cheque_score
  dim_company --> dim_change_district
  dim_company --> dim_channel
  dim_company --> dim_channel_cost
  dim_company --> dim_channel_finance
  dim_company --> dim_channel_sales
  dim_company --> dim_collection_status
  dim_company --> dim_contact_score
  dim_company --> dim_cost_group
  dim_company --> dim_cost_stk
  dim_company --> dim_customer
  dim_company --> dim_delivery
  dim_company --> dim_department
  dim_company --> dim_department_last
  dim_company --> dim_director
  dim_company --> dim_director_last
  dim_company --> dim_doctype
  dim_company --> dim_grade
  dim_company --> dim_guarantee
  dim_company --> dim_invoice
  dim_company --> dim_order
  dim_company --> dim_payment
  dim_company --> dim_payment_receive_score
  dim_company --> dim_product_master
  dim_company --> dim_product_master_fc
  dim_company --> dim_product_mkt
  dim_company --> dim_product_mkt_director
  dim_company --> dim_project
  dim_company --> dim_quotation
  dim_company --> dim_rate_target
  dim_company --> dim_rebate
  dim_company --> dim_region
  dim_company --> dim_region_last
  dim_company --> dim_region_manager
  dim_company --> dim_region_manager_last
  dim_company --> dim_report
  dim_company --> dim_sale_representative
  dim_company --> dim_sale_representative_last
  dim_company --> dim_section
  dim_company --> dim_section_last
  dim_company --> dim_section_manager
  dim_company --> dim_section_manager_last
  dim_company --> dim_status_not_receive
  dim_company --> dim_stk_mkt
  dim_company --> dim_target_product_group
  dim_company --> dim_waterpac
  dim_company --> dim_weight_score
  dim_contact_score --> dim_customer_grade
  dim_contact_score --> dim_group_customer_grade
  dim_cost_group --> fact_transcation
  dim_cost_stk --> fact_transcation
  dim_customer --> dim_aging
  dim_customer --> dim_customer_grade
  dim_customer --> dim_group_customer
  dim_customer --> dim_group_customer_grade
  dim_customer --> fact_invoice
  dim_customer --> fact_order
  dim_customer --> fact_quotation
  dim_customer --> fact_transcation
  dim_delivery --> fact_delivery
  dim_department --> dim_department_last
  dim_department --> fact_transcation
  dim_department_last --> dim_rate_target
  dim_department_last --> update_sk_sale_rep_group
  dim_director --> dim_director_last
  dim_director --> fact_transcation
  dim_director_last --> dim_rate_target
  dim_director_last --> update_sk_sale_rep_group
  dim_grade --> dim_customer_grade
  dim_grade --> dim_group_customer_grade
  dim_group_customer --> dim_group_customer_grade
  dim_invoice --> dim_aging
  dim_invoice --> fact_invoice
  dim_invoice --> fact_transaction_delivery
  dim_order --> dim_invoice
  dim_order --> fact_order
  dim_payment --> fact_transcation
  dim_payment_receive_score --> dim_customer_grade
  dim_payment_receive_score --> dim_group_customer_grade
  dim_product_master --> fact_order
  dim_product_master --> fact_quotation
  dim_product_master --> fact_transaction_delivery
  dim_product_master --> fact_transcation
  dim_product_mkt --> dim_product_master
  dim_product_mkt --> dim_target_product_group_by_sale
  dim_product_mkt --> fact_transcation
  dim_project --> dim_quotation
  dim_quotation --> fact_quotation
  dim_rate_target --> dim_target_product_group_by_sale
  dim_rate_target --> dim_target_product_group_by_sale_dayofwork
  dim_rebate --> dim_product_master
  dim_region --> dim_region_last
  dim_region --> fact_transcation
  dim_region_last --> update_sk_sale_rep_group
  dim_region_manager --> dim_region_manager_last
  dim_region_manager --> fact_transcation
  dim_region_manager_last --> update_sk_sale_rep_group
  dim_report --> dim_target_product_group_by_sale
  dim_sale_representative --> dim_sale_representative_last
  dim_sale_representative --> fact_transcation
  dim_sale_representative_last --> update_sk_sale_rep_group
  dim_section --> dim_section_last
  dim_section --> fact_transcation
  dim_section_last --> update_sk_sale_rep_group
  dim_section_manager --> dim_section_manager_last
  dim_section_manager --> fact_transcation
  dim_section_manager_last --> update_sk_sale_rep_group
  dim_status_not_receive --> dim_aging
  dim_status_not_receive --> dim_customer_grade
  dim_status_not_receive --> dim_group_customer_grade
  dim_stk_mkt --> dim_product_master
  dim_stk_mkt --> fact_transcation
  dim_target_product_group --> dim_target_product_group_by_sale
  dim_target_product_group_by_sale --> dim_target_product_group_by_sale_dayofwork
  dim_target_product_group_by_sale_dayofwork --> fact_transcation
  drop_all_tables_curated_mac5 --> create_all_table_raw_mac5
  drop_all_tables_curated_mac5 --> create_all_table_raw_mac5_aa05
  drop_all_tables_curated_mac5 --> create_all_table_raw_mac5_ab01
  drop_all_tables_curated_mac5 --> create_all_table_raw_mac5_ac02
  drop_all_tables_curated_mac5 --> create_all_table_raw_mac5_ak02
  drop_all_tables_validated_cis360 --> create_all_table_raw_cis360
  drop_all_tables_validated_cis360 --> validated_schema_cis360
  drop_all_tables_validated_mac5 --> create_all_table_raw_mac5
  drop_all_tables_validated_mac5 --> create_all_table_raw_mac5_aa05
  drop_all_tables_validated_mac5 --> create_all_table_raw_mac5_ab01
  drop_all_tables_validated_mac5 --> create_all_table_raw_mac5_ac02
  drop_all_tables_validated_mac5 --> create_all_table_raw_mac5_ak02
  drop_all_tables_validated_mac5 --> validated_schema_mac5
  drop_all_tables_validated_mastersku --> create_all_table_raw_mastersku
  drop_all_tables_validated_mastersku --> validated_schema_mastersku
  drop_all_tables_validated_saleout_mdt --> create_all_table_raw_saleout_mdt
  drop_all_tables_validated_saleout_mdt --> validated_schema_saleout
  fact_mir_vs --> dim_aging
  fact_order --> fact_invoice
  fact_quotation --> fact_order
  fact_transaction_delivery --> fact_delivery
  match_customer --> dim_customer
  mie --> dim_aging
  mie --> dim_customer_grade
  mie --> dim_group_customer_grade
  mih --> curated_mih
  mih --> dim_customer_grade
  mih --> dim_group_customer_grade
  mih --> mil
  mih2 --> curated_mih
  mih2 --> curated_mil
  mih2 --> dim_invoice
  mil --> curated_mil
  mir --> dim_aging
  mir --> dim_customer_grade
  mir --> dim_group_customer_grade
  nature_business --> dim_customer
  per --> dim_sale_representative
  per --> dim_sale_representative_last
  product --> curated_product
  product --> dim_product_master
  product_detail --> curated_product
  product_detail --> dim_product_master
  product_detail --> product_for_aisearch
  stg --> dim_product_master
  stg_report --> stg
  stgacc --> stg
  stk --> dim_product_master
  stk --> dim_stk_mkt
  tbook_profilecomp --> dim_project
  tbook_quodetail --> dim_quotation
  tbook_quodetail --> fact_quotation
  tbook_quotation --> curated_tbook_quotation
  tdelivery --> dim_delivery
  tdelivery --> fact_delivery
  ttrip --> dim_delivery
  ttrip --> fact_delivery
  ttrip_document --> dim_delivery
  ttrip_document --> fact_delivery
  unit --> product_for_aisearch
  update_sk_sale_rep_group --> dim_rate_target
  update_sk_sale_rep_group --> dim_target_product_group_by_sale
  validated_schema_cis360 --> address_type
  validated_schema_cis360 --> category__cis360
  validated_schema_cis360 --> country
  validated_schema_cis360 --> curated_schema_cis360
  validated_schema_cis360 --> customer_address
  validated_schema_cis360 --> customer_profile
  validated_schema_cis360 --> customer_profile_category
  validated_schema_cis360 --> customer_profile_nature_business
  validated_schema_cis360 --> customer_profile_role_business
  validated_schema_cis360 --> customer_profile_tag
  validated_schema_cis360 --> customer_profile_type
  validated_schema_cis360 --> customer_status
  validated_schema_cis360 --> customer_to_customer
  validated_schema_cis360 --> customer_to_platform
  validated_schema_cis360 --> customer_to_transaction
  validated_schema_cis360 --> customer_type
  validated_schema_cis360 --> district
  validated_schema_cis360 --> juristic_profile
  validated_schema_cis360 --> juristic_type
  validated_schema_cis360 --> nature_business
  validated_schema_cis360 --> organize_type
  validated_schema_cis360 --> province
  validated_schema_cis360 --> role_business
  validated_schema_cis360 --> sub_district
  validated_schema_cis360 --> zipcode
  validated_schema_mac5 --> ap_s
  validated_schema_mac5 --> apilog
  validated_schema_mac5 --> ar_s
  validated_schema_mac5 --> cfs
  validated_schema_mac5 --> check_po
  validated_schema_mac5 --> chq
  validated_schema_mac5 --> comboset
  validated_schema_mac5 --> combostk
  validated_schema_mac5 --> cpp
  validated_schema_mac5 --> cps
  validated_schema_mac5 --> cps_dummy
  validated_schema_mac5 --> cpx
  validated_schema_mac5 --> cql
  validated_schema_mac5 --> cre
  validated_schema_mac5 --> cst
  validated_schema_mac5 --> curated_schema_mac5
  validated_schema_mac5 --> deb
  validated_schema_mac5 --> dep
  validated_schema_mac5 --> detail_qtspread
  validated_schema_mac5 --> doc
  validated_schema_mac5 --> grp
  validated_schema_mac5 --> log_print_billing
  validated_schema_mac5 --> main_qtspread
  validated_schema_mac5 --> maincontract
  validated_schema_mac5 --> match_customer
  validated_schema_mac5 --> match_deb_bot_re
  validated_schema_mac5 --> match_product
  validated_schema_mac5 --> mec
  validated_schema_mac5 --> mie
  validated_schema_mac5 --> mie_dummy
  validated_schema_mac5 --> mih
  validated_schema_mac5 --> mih2
  validated_schema_mac5 --> mih_billing
  validated_schema_mac5 --> mih_dummy
  validated_schema_mac5 --> mil
  validated_schema_mac5 --> mil_billing
  validated_schema_mac5 --> mil_dummy
  validated_schema_mac5 --> mip
  validated_schema_mac5 --> mir
  validated_schema_mac5 --> mkt_per
  validated_schema_mac5 --> order_from_allkon_m
  validated_schema_mac5 --> pathfilestamper
  validated_schema_mac5 --> per
  validated_schema_mac5 --> pro_ag
  validated_schema_mac5 --> pro_crc
  validated_schema_mac5 --> pro_re
  validated_schema_mac5 --> product_bot_re
  validated_schema_mac5 --> product_detail_bot_re
  validated_schema_mac5 --> product_promotion
  validated_schema_mac5 --> qt_spread_to_mih
  validated_schema_mac5 --> rcv
  validated_schema_mac5 --> rno
  validated_schema_mac5 --> sbl
  validated_schema_mac5 --> std
  validated_schema_mac5 --> stf
  validated_schema_mac5 --> stg
  validated_schema_mac5 --> stg_report
  validated_schema_mac5 --> stgacc
  validated_schema_mac5 --> stk
  validated_schema_mac5 --> stk_mkt
  validated_schema_mac5 --> sto
  validated_schema_mac5 --> supcontract
  validated_schema_mac5 --> tab
  validated_schema_mac5 --> tbcontact
  validated_schema_mac5 --> tbook_apptype
  validated_schema_mac5 --> tbook_givestk
  validated_schema_mac5 --> tbook_payin
  validated_schema_mac5 --> tbook_profilecomp
  validated_schema_mac5 --> tbook_quodetail
  validated_schema_mac5 --> tbook_quotation
  validated_schema_mac5 --> tbpjaddacc
  validated_schema_mac5 --> tdelivery
  validated_schema_mac5 --> tdis_approveorder
  validated_schema_mac5 --> tdis_approveqt
  validated_schema_mac5 --> tdis_mail
  validated_schema_mac5 --> tempgpsweb
  validated_schema_mac5 --> tmp_mihstatus
  validated_schema_mac5 --> tmp_pdf_ap
  validated_schema_mac5 --> tmp_pdf_frasers
  validated_schema_mac5 --> tmp_pdf_pruksa
  validated_schema_mac5 --> tmp_pdf_qh
  validated_schema_mac5 --> tmp_pdf_sansiri
  validated_schema_mac5 --> tmp_pdf_supalai
  validated_schema_mac5 --> ttrip
  validated_schema_mac5 --> ttrip_document
  validated_schema_mac5 --> userloginanyprogram
  validated_schema_mac5 --> vmp
  validated_schema_mastersku --> brand
  validated_schema_mastersku --> category__mastersku
  validated_schema_mastersku --> curated_schema_mastersku
  validated_schema_mastersku --> product
  validated_schema_mastersku --> product_admin_status
  validated_schema_mastersku --> product_category
  validated_schema_mastersku --> product_detail
  validated_schema_mastersku --> product_group
  validated_schema_mastersku --> product_group_cost_group
  validated_schema_mastersku --> product_status
  validated_schema_mastersku --> unit
  validated_schema_mastersku --> vendor
  validated_schema_saleout --> report_sale_subscription
  validated_schema_saleout --> sale_by_branch_detail
  validated_schema_saleout --> sale_by_branch_mch3
  validated_schema_saleout --> saleout_gb
  validated_schema_saleout --> saleout_hp
  validated_schema_saleout --> sales_by_branch
  validated_schema_saleout --> stock_aging
  validated_schema_saleout --> stock_by_branch
  validated_schema_saleout --> turnover
  validated_schema_saleout --> turnover_brand
  vendor --> product_for_aisearch
  classDef initial fill:#e0e0e0,stroke:#9e9e9e,color:#111;
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef cdc fill:#f0d0f0,stroke:#b060b0,color:#111;
  classDef process fill:#f5c6c6,stroke:#c04040,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class create_all_function,create_all_schema,create_all_table_raw_cis360,create_all_table_raw_mac5,create_all_table_raw_mac5_aa05,create_all_table_raw_mac5_ab01,create_all_table_raw_mac5_ac02,create_all_table_raw_mac5_ak02,create_all_table_raw_mastersku,create_all_table_raw_saleout_mdt,drop_all_tables_curated_mac5,drop_all_tables_validated_cis360,drop_all_tables_validated_mac5,drop_all_tables_validated_mastersku,drop_all_tables_validated_saleout_mdt initial;
  class address_type,ap_s,apilog,ar_s,brand,category__cis360,category__mastersku,cfs,check_po,chq,comboset,combostk,country,cpp,cps,cps_dummy,cpx,cql,cre,cst,customer_address,customer_profile,customer_profile_category,customer_profile_nature_business,customer_profile_role_business,customer_profile_tag,customer_profile_type,customer_status,customer_to_customer,customer_to_platform,customer_to_transaction,customer_type,deb,dep,detail_qtspread,district,doc,grp,juristic_profile,juristic_type,log_print_billing,main_qtspread,maincontract,match_customer,match_deb_bot_re,match_product,mec,mie,mie_dummy,mih,mih2,mih_billing,mih_dummy,mil,mil_billing,mil_dummy,mip,mir,mkt_per,nature_business,order_from_allkon_m,organize_type,pathfilestamper,per,pro_ag,pro_crc,pro_re,product,product_admin_status,product_bot_re,product_category,product_detail,product_detail_bot_re,product_group,product_group_cost_group,product_promotion,product_status,province,qt_spread_to_mih,rcv,report_sale_subscription,rno,role_business,sale_by_branch_detail,sale_by_branch_mch3,saleout_gb,saleout_hp,sales_by_branch,sbl,std,stf,stg,stg_report,stgacc,stk,stk_mkt,sto,stock_aging,stock_by_branch,sub_district,supcontract,tab,tbcontact,tbook_apptype,tbook_givestk,tbook_payin,tbook_profilecomp,tbook_quodetail,tbook_quotation,tbpjaddacc,tdelivery,tdis_approveorder,tdis_approveqt,tdis_mail,tempgpsweb,tmp_mihstatus,tmp_pdf_ap,tmp_pdf_frasers,tmp_pdf_pruksa,tmp_pdf_qh,tmp_pdf_sansiri,tmp_pdf_supalai,ttrip,ttrip_document,turnover,turnover_brand,unit,userloginanyprogram,validated_schema_cis360,validated_schema_mac5,validated_schema_mastersku,validated_schema_saleout,vendor,vmp,zipcode validated;
  class curated_mih,curated_mil,curated_product,curated_schema_cis360,curated_schema_mac5,curated_schema_mastersku,curated_tbook_quotation,product_for_aisearch curated;
  class dim_aging,dim_aging_rang,dim_avg_collection_score,dim_bounce_cheque_score,dim_calendar,dim_change_district,dim_channel,dim_channel_cost,dim_channel_finance,dim_channel_sales,dim_collection_status,dim_company,dim_contact_score,dim_cost_group,dim_cost_stk,dim_customer,dim_customer_grade,dim_delivery,dim_department,dim_department_last,dim_director,dim_director_last,dim_doctype,dim_grade,dim_group_customer,dim_group_customer_grade,dim_guarantee,dim_holiday,dim_invoice,dim_order,dim_payment,dim_payment_receive_score,dim_product_master,dim_product_master_fc,dim_product_mkt,dim_product_mkt_director,dim_project,dim_quotation,dim_rate_target,dim_rebate,dim_region,dim_region_last,dim_region_manager,dim_region_manager_last,dim_report,dim_sale_representative,dim_sale_representative_last,dim_section,dim_section_last,dim_section_manager,dim_section_manager_last,dim_status_not_receive,dim_stk_mkt,dim_target_product_group,dim_target_product_group_by_sale,dim_target_product_group_by_sale_dayofwork,dim_waterpac,dim_weight_score,update_sk_sale_rep_group dimension;
  class fact_delivery,fact_invoice,fact_order,fact_quotation,fact_transaction_delivery,fact_transcation fact;
  class cdc_change_log,cdc_schema cdc;
  class deb_address_data process;
  class fact_chq,fact_mir_rs,fact_mir_vs paused;
```
