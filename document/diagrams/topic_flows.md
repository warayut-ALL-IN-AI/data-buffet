# Topic Flows (subject-area views)

> ⚠️ **Auto-generated — do not edit by hand.** Regenerate with
> `python document/diagrams/generate_lineage.py`. Topic membership is defined by the
> `TOPICS` list in `generate_lineage.py`; the nodes and edges are parsed from the
> real `.sqlx` files, so each view always matches the code.

Each section is one business subject. It shows the topic's own objects (members),
the `.sqlx` that feed them (direct upstream, any layer), and any `fact_*` they feed.
Edges point **source → consumer**; paused objects render dashed. Node colours are by
layer (validated/curated/dimension/fact/…) as in
[pipeline_lineage.md](pipeline_lineage.md).

**Topics (12):**

1. Sales org hierarchy — โครงสร้างองค์กรขาย (แผนก/ภาค/ผจก./เซล)
2. Sales target / quota — เป้าการขาย
3. Customer & scoring — ลูกค้า/เกรด/สกอร์
4. Accounts receivable / aging — ลูกหนี้/อายุหนี้
5. Product master & marketing — สินค้า
6. Sales transactions — ยอดขาย/ออเดอร์/อินวอยซ์ (fact หลัก)
7. Delivery / logistics — การจัดส่ง
8. Quotation / project — ใบเสนอราคา/โปรเจกต์
9. Sales channel — ช่องทางขาย
10. Cost — ต้นทุน
11. Calendar / date spine — ปฏิทิน/วันหยุด
12. Reference / misc — ตารางอ้างอิงอื่นๆ

**Uncovered dim/fact/curated objects (not in any topic):** —

---

## Sales org hierarchy — โครงสร้างองค์กรขาย (แผนก/ภาค/ผจก./เซล)

**Objects in this topic (17):** `dim_change_district`, `dim_company`, `dim_department`, `dim_department_last`, `dim_director`, `dim_director_last`, `dim_region`, `dim_region_last`, `dim_region_manager`, `dim_region_manager_last`, `dim_sale_representative`, `dim_sale_representative_last`, `dim_section`, `dim_section_last`, `dim_section_manager`, `dim_section_manager_last`, `update_sk_sale_rep_group`

**Fed by (1):** `per`

```mermaid
flowchart LR
  subgraph validated["validated (1)"]
    per["per"]
  end
  subgraph dimension["dimension (17)"]
    dim_change_district["dim_change_district"]
    dim_company["dim_company"]
    dim_department["dim_department"]
    dim_department_last["dim_department_last"]
    dim_director["dim_director"]
    dim_director_last["dim_director_last"]
    dim_region["dim_region"]
    dim_region_last["dim_region_last"]
    dim_region_manager["dim_region_manager"]
    dim_region_manager_last["dim_region_manager_last"]
    dim_sale_representative["dim_sale_representative"]
    dim_sale_representative_last["dim_sale_representative_last"]
    dim_section["dim_section"]
    dim_section_last["dim_section_last"]
    dim_section_manager["dim_section_manager"]
    dim_section_manager_last["dim_section_manager_last"]
    update_sk_sale_rep_group["update_sk_sale_rep_group"]
  end
  subgraph fact["fact (4)"]
    fact_chq["fact_chq"]
    fact_mir_rs["fact_mir_rs"]
    fact_mir_vs["fact_mir_vs"]
    fact_transcation["fact_transcation"]
  end
  dim_change_district --> fact_transcation
  dim_company --> dim_change_district
  dim_company --> dim_department
  dim_company --> dim_department_last
  dim_company --> dim_director
  dim_company --> dim_director_last
  dim_company --> dim_region
  dim_company --> dim_region_last
  dim_company --> dim_region_manager
  dim_company --> dim_region_manager_last
  dim_company --> dim_sale_representative
  dim_company --> dim_sale_representative_last
  dim_company --> dim_section
  dim_company --> dim_section_last
  dim_company --> dim_section_manager
  dim_company --> dim_section_manager_last
  dim_company --> fact_chq
  dim_company --> fact_mir_rs
  dim_company --> fact_mir_vs
  dim_department --> dim_department_last
  dim_department --> fact_transcation
  dim_department_last --> update_sk_sale_rep_group
  dim_director --> dim_director_last
  dim_director --> fact_transcation
  dim_director_last --> update_sk_sale_rep_group
  dim_region --> dim_region_last
  dim_region --> fact_transcation
  dim_region_last --> update_sk_sale_rep_group
  dim_region_manager --> dim_region_manager_last
  dim_region_manager --> fact_transcation
  dim_region_manager_last --> update_sk_sale_rep_group
  dim_sale_representative --> dim_sale_representative_last
  dim_sale_representative --> fact_transcation
  dim_sale_representative_last --> update_sk_sale_rep_group
  dim_section --> dim_section_last
  dim_section --> fact_transcation
  dim_section_last --> update_sk_sale_rep_group
  dim_section_manager --> dim_section_manager_last
  dim_section_manager --> fact_transcation
  dim_section_manager_last --> update_sk_sale_rep_group
  fact_chq --> fact_mir_rs
  fact_mir_vs --> fact_mir_rs
  per --> dim_sale_representative
  per --> dim_sale_representative_last
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class per validated;
  class dim_change_district,dim_company,dim_department,dim_department_last,dim_director,dim_director_last,dim_region,dim_region_last,dim_region_manager,dim_region_manager_last,dim_sale_representative,dim_sale_representative_last,dim_section,dim_section_last,dim_section_manager,dim_section_manager_last,update_sk_sale_rep_group dimension;
  class fact_chq,fact_mir_rs,fact_mir_vs,fact_transcation fact;
```

---

## Sales target / quota — เป้าการขาย

**Objects in this topic (5):** `dim_rate_target`, `dim_report`, `dim_target_product_group`, `dim_target_product_group_by_sale`, `dim_target_product_group_by_sale_dayofwork`

**Fed by (6):** `dim_calendar`, `dim_company`, `dim_department_last`, `dim_director_last`, `dim_product_mkt`, `update_sk_sale_rep_group`

```mermaid
flowchart LR
  subgraph dimension["dimension (11)"]
    dim_calendar["dim_calendar"]
    dim_company["dim_company"]
    dim_department_last["dim_department_last"]
    dim_director_last["dim_director_last"]
    dim_product_mkt["dim_product_mkt"]
    dim_rate_target["dim_rate_target"]
    dim_report["dim_report"]
    dim_target_product_group["dim_target_product_group"]
    dim_target_product_group_by_sale["dim_target_product_group_by_sale"]
    dim_target_product_group_by_sale_dayofwork["dim_target_product_group_by_sale_dayofwork"]
    update_sk_sale_rep_group["update_sk_sale_rep_group"]
  end
  subgraph fact["fact (1)"]
    fact_transcation["fact_transcation"]
  end
  dim_calendar --> dim_target_product_group_by_sale_dayofwork
  dim_company --> dim_department_last
  dim_company --> dim_director_last
  dim_company --> dim_product_mkt
  dim_company --> dim_rate_target
  dim_company --> dim_report
  dim_company --> dim_target_product_group
  dim_department_last --> dim_rate_target
  dim_department_last --> update_sk_sale_rep_group
  dim_director_last --> dim_rate_target
  dim_director_last --> update_sk_sale_rep_group
  dim_product_mkt --> dim_target_product_group_by_sale
  dim_product_mkt --> fact_transcation
  dim_rate_target --> dim_target_product_group_by_sale
  dim_rate_target --> dim_target_product_group_by_sale_dayofwork
  dim_report --> dim_target_product_group_by_sale
  dim_target_product_group --> dim_target_product_group_by_sale
  dim_target_product_group_by_sale --> dim_target_product_group_by_sale_dayofwork
  dim_target_product_group_by_sale_dayofwork --> fact_transcation
  update_sk_sale_rep_group --> dim_rate_target
  update_sk_sale_rep_group --> dim_target_product_group_by_sale
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class dim_calendar,dim_company,dim_department_last,dim_director_last,dim_product_mkt,dim_rate_target,dim_report,dim_target_product_group,dim_target_product_group_by_sale,dim_target_product_group_by_sale_dayofwork,update_sk_sale_rep_group dimension;
  class fact_transcation fact;
```

---

## Customer & scoring — ลูกค้า/เกรด/สกอร์

**Objects in this topic (10):** `dim_avg_collection_score`, `dim_bounce_cheque_score`, `dim_contact_score`, `dim_customer`, `dim_customer_grade`, `dim_grade`, `dim_group_customer`, `dim_group_customer_grade`, `dim_payment_receive_score`, `dim_weight_score`

**Fed by (16):** `chq`, `cql`, `curated_mih`, `customer_profile`, `customer_profile_nature_business`, `customer_status`, `customer_type`, `deb`, `dim_aging`, `dim_company`, `dim_status_not_receive`, `match_customer`, `mie`, `mih`, `mir`, `nature_business`

```mermaid
flowchart LR
  subgraph validated["validated (12)"]
    chq["chq"]
    cql["cql"]
    customer_profile["customer_profile"]
    customer_profile_nature_business["customer_profile_nature_business"]
    customer_status["customer_status"]
    customer_type["customer_type"]
    deb["deb"]
    match_customer["match_customer"]
    mie["mie"]
    mih["mih"]
    mir["mir"]
    nature_business["nature_business"]
  end
  subgraph curated["curated (1)"]
    curated_mih["curated_mih"]
  end
  subgraph dimension["dimension (13)"]
    dim_aging["dim_aging"]
    dim_avg_collection_score["dim_avg_collection_score"]
    dim_bounce_cheque_score["dim_bounce_cheque_score"]
    dim_company["dim_company"]
    dim_contact_score["dim_contact_score"]
    dim_customer["dim_customer"]
    dim_customer_grade["dim_customer_grade"]
    dim_grade["dim_grade"]
    dim_group_customer["dim_group_customer"]
    dim_group_customer_grade["dim_group_customer_grade"]
    dim_payment_receive_score["dim_payment_receive_score"]
    dim_status_not_receive["dim_status_not_receive"]
    dim_weight_score["dim_weight_score"]
  end
  subgraph fact["fact (7)"]
    fact_chq["fact_chq"]
    fact_invoice["fact_invoice"]
    fact_mir_rs["fact_mir_rs"]
    fact_mir_vs["fact_mir_vs"]
    fact_order["fact_order"]
    fact_quotation["fact_quotation"]
    fact_transcation["fact_transcation"]
  end
  chq --> dim_aging
  chq --> dim_customer_grade
  chq --> dim_group_customer_grade
  chq --> fact_chq
  cql --> dim_aging
  cql --> dim_customer_grade
  cql --> dim_group_customer_grade
  cql --> fact_chq
  curated_mih --> dim_aging
  curated_mih --> dim_customer_grade
  curated_mih --> dim_group_customer_grade
  curated_mih --> fact_mir_rs
  curated_mih --> fact_mir_vs
  curated_mih --> fact_transcation
  customer_profile --> dim_customer
  customer_profile_nature_business --> dim_customer
  customer_status --> dim_customer
  customer_type --> dim_customer
  deb --> dim_customer
  deb --> dim_customer_grade
  deb --> dim_group_customer_grade
  deb --> fact_transcation
  dim_aging --> dim_customer_grade
  dim_aging --> dim_group_customer_grade
  dim_avg_collection_score --> dim_customer_grade
  dim_avg_collection_score --> dim_group_customer_grade
  dim_bounce_cheque_score --> dim_customer_grade
  dim_bounce_cheque_score --> dim_group_customer_grade
  dim_company --> dim_aging
  dim_company --> dim_avg_collection_score
  dim_company --> dim_bounce_cheque_score
  dim_company --> dim_contact_score
  dim_company --> dim_customer
  dim_company --> dim_grade
  dim_company --> dim_payment_receive_score
  dim_company --> dim_status_not_receive
  dim_company --> dim_weight_score
  dim_company --> fact_chq
  dim_company --> fact_mir_rs
  dim_company --> fact_mir_vs
  dim_contact_score --> dim_customer_grade
  dim_contact_score --> dim_group_customer_grade
  dim_customer --> dim_aging
  dim_customer --> dim_customer_grade
  dim_customer --> dim_group_customer
  dim_customer --> dim_group_customer_grade
  dim_customer --> fact_chq
  dim_customer --> fact_invoice
  dim_customer --> fact_mir_rs
  dim_customer --> fact_mir_vs
  dim_customer --> fact_order
  dim_customer --> fact_quotation
  dim_customer --> fact_transcation
  dim_grade --> dim_customer_grade
  dim_grade --> dim_group_customer_grade
  dim_group_customer --> dim_group_customer_grade
  dim_payment_receive_score --> dim_customer_grade
  dim_payment_receive_score --> dim_group_customer_grade
  dim_status_not_receive --> dim_aging
  dim_status_not_receive --> dim_customer_grade
  dim_status_not_receive --> dim_group_customer_grade
  fact_chq --> fact_mir_rs
  fact_mir_vs --> dim_aging
  fact_mir_vs --> fact_mir_rs
  fact_order --> fact_invoice
  fact_quotation --> fact_order
  match_customer --> dim_customer
  mie --> dim_aging
  mie --> dim_customer_grade
  mie --> dim_group_customer_grade
  mie --> fact_mir_rs
  mie --> fact_mir_vs
  mih --> curated_mih
  mih --> dim_customer_grade
  mih --> dim_group_customer_grade
  mir --> dim_aging
  mir --> dim_customer_grade
  mir --> dim_group_customer_grade
  mir --> fact_mir_rs
  mir --> fact_mir_vs
  nature_business --> dim_customer
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class chq,cql,customer_profile,customer_profile_nature_business,customer_status,customer_type,deb,match_customer,mie,mih,mir,nature_business validated;
  class curated_mih curated;
  class dim_aging,dim_avg_collection_score,dim_bounce_cheque_score,dim_company,dim_contact_score,dim_customer,dim_customer_grade,dim_grade,dim_group_customer,dim_group_customer_grade,dim_payment_receive_score,dim_status_not_receive,dim_weight_score dimension;
  class fact_chq,fact_invoice,fact_mir_rs,fact_mir_vs,fact_order,fact_quotation,fact_transcation fact;
```

---

## Accounts receivable / aging — ลูกหนี้/อายุหนี้

**Objects in this topic (8):** `dim_aging`, `dim_aging_rang`, `dim_collection_status`, `dim_guarantee`, `dim_status_not_receive`, `fact_chq`, `fact_mir_rs`, `fact_mir_vs`

**Fed by (11):** `ar_s`, `cfs`, `chq`, `cql`, `curated_mih`, `curated_mil`, `dim_company`, `dim_customer`, `dim_invoice`, `mie`, `mir`

```mermaid
flowchart LR
  subgraph validated["validated (6)"]
    ar_s["ar_s"]
    cfs["cfs"]
    chq["chq"]
    cql["cql"]
    mie["mie"]
    mir["mir"]
  end
  subgraph curated["curated (2)"]
    curated_mih["curated_mih"]
    curated_mil["curated_mil"]
  end
  subgraph dimension["dimension (8)"]
    dim_aging["dim_aging"]
    dim_aging_rang["dim_aging_rang"]
    dim_collection_status["dim_collection_status"]
    dim_company["dim_company"]
    dim_customer["dim_customer"]
    dim_guarantee["dim_guarantee"]
    dim_invoice["dim_invoice"]
    dim_status_not_receive["dim_status_not_receive"]
  end
  subgraph fact["fact (3)"]
    fact_chq["fact_chq"]
    fact_mir_rs["fact_mir_rs"]
    fact_mir_vs["fact_mir_vs"]
  end
  ar_s --> curated_mih
  ar_s --> dim_aging
  ar_s --> dim_invoice
  cfs --> dim_aging
  chq --> dim_aging
  chq --> fact_chq
  cql --> dim_aging
  cql --> fact_chq
  curated_mih --> dim_aging
  curated_mih --> dim_invoice
  curated_mih --> fact_mir_rs
  curated_mih --> fact_mir_vs
  curated_mil --> dim_aging
  curated_mil --> dim_invoice
  dim_collection_status --> fact_mir_rs
  dim_collection_status --> fact_mir_vs
  dim_company --> dim_aging
  dim_company --> dim_aging_rang
  dim_company --> dim_collection_status
  dim_company --> dim_customer
  dim_company --> dim_guarantee
  dim_company --> dim_invoice
  dim_company --> dim_status_not_receive
  dim_company --> fact_chq
  dim_company --> fact_mir_rs
  dim_company --> fact_mir_vs
  dim_customer --> dim_aging
  dim_customer --> fact_chq
  dim_customer --> fact_mir_rs
  dim_customer --> fact_mir_vs
  dim_invoice --> dim_aging
  dim_invoice --> fact_mir_rs
  dim_invoice --> fact_mir_vs
  dim_status_not_receive --> dim_aging
  fact_chq --> fact_mir_rs
  fact_mir_vs --> dim_aging
  fact_mir_vs --> fact_mir_rs
  mie --> dim_aging
  mie --> fact_mir_rs
  mie --> fact_mir_vs
  mir --> dim_aging
  mir --> fact_mir_rs
  mir --> fact_mir_vs
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class ar_s,cfs,chq,cql,mie,mir validated;
  class curated_mih,curated_mil curated;
  class dim_aging,dim_aging_rang,dim_collection_status,dim_company,dim_customer,dim_guarantee,dim_invoice,dim_status_not_receive dimension;
  class fact_chq,fact_mir_rs,fact_mir_vs fact;
```

---

## Product master & marketing — สินค้า

**Objects in this topic (8):** `curated_product`, `dim_product_master`, `dim_product_master_fc`, `dim_product_mkt`, `dim_product_mkt_director`, `dim_rebate`, `dim_stk_mkt`, `product_for_aisearch`

**Fed by (9):** `brand`, `category`, `dim_company`, `product`, `product_detail`, `stg`, `stk`, `unit`, `vendor`

```mermaid
flowchart LR
  subgraph validated["validated (8)"]
    brand["brand"]
    category__mastersku["category"]
    product["product"]
    product_detail["product_detail"]
    stg["stg"]
    stk["stk"]
    unit["unit"]
    vendor["vendor"]
  end
  subgraph curated["curated (2)"]
    curated_product["curated_product"]
    product_for_aisearch["product_for_aisearch"]
  end
  subgraph dimension["dimension (7)"]
    dim_company["dim_company"]
    dim_product_master["dim_product_master"]
    dim_product_master_fc["dim_product_master_fc"]
    dim_product_mkt["dim_product_mkt"]
    dim_product_mkt_director["dim_product_mkt_director"]
    dim_rebate["dim_rebate"]
    dim_stk_mkt["dim_stk_mkt"]
  end
  subgraph fact["fact (4)"]
    fact_order["fact_order"]
    fact_quotation["fact_quotation"]
    fact_transaction_delivery["fact_transaction_delivery"]
    fact_transcation["fact_transcation"]
  end
  brand --> product_for_aisearch
  category__mastersku --> product_for_aisearch
  curated_product --> product_for_aisearch
  dim_company --> dim_product_master
  dim_company --> dim_product_master_fc
  dim_company --> dim_product_mkt
  dim_company --> dim_product_mkt_director
  dim_company --> dim_rebate
  dim_company --> dim_stk_mkt
  dim_product_master --> fact_order
  dim_product_master --> fact_quotation
  dim_product_master --> fact_transaction_delivery
  dim_product_master --> fact_transcation
  dim_product_mkt --> dim_product_master
  dim_product_mkt --> fact_transcation
  dim_rebate --> dim_product_master
  dim_stk_mkt --> dim_product_master
  dim_stk_mkt --> fact_transcation
  fact_quotation --> fact_order
  product --> curated_product
  product --> dim_product_master
  product_detail --> curated_product
  product_detail --> dim_product_master
  product_detail --> product_for_aisearch
  stg --> dim_product_master
  stk --> dim_product_master
  stk --> dim_stk_mkt
  unit --> product_for_aisearch
  vendor --> product_for_aisearch
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class brand,category__mastersku,product,product_detail,stg,stk,unit,vendor validated;
  class curated_product,product_for_aisearch curated;
  class dim_company,dim_product_master,dim_product_master_fc,dim_product_mkt,dim_product_mkt_director,dim_rebate,dim_stk_mkt dimension;
  class fact_order,fact_quotation,fact_transaction_delivery,fact_transcation fact;
```

---

## Sales transactions — ยอดขาย/ออเดอร์/อินวอยซ์ (fact หลัก)

**Objects in this topic (8):** `curated_mih`, `curated_mil`, `dim_invoice`, `dim_order`, `dim_payment`, `fact_invoice`, `fact_order`, `fact_transcation`

**Fed by (25):** `ap_s`, `ar_s`, `deb`, `dim_change_district`, `dim_channel`, `dim_channel_cost`, `dim_company`, `dim_cost_group`, `dim_cost_stk`, `dim_customer`, `dim_department`, `dim_director`, `dim_product_master`, `dim_product_mkt`, `dim_region`, `dim_region_manager`, `dim_sale_representative`, `dim_section`, `dim_section_manager`, `dim_stk_mkt`, `dim_target_product_group_by_sale_dayofwork`, `fact_quotation`, `mih`, `mih2`, `mil`

```mermaid
flowchart LR
  subgraph validated["validated (6)"]
    ap_s["ap_s"]
    ar_s["ar_s"]
    deb["deb"]
    mih["mih"]
    mih2["mih2"]
    mil["mil"]
  end
  subgraph curated["curated (2)"]
    curated_mih["curated_mih"]
    curated_mil["curated_mil"]
  end
  subgraph dimension["dimension (21)"]
    dim_change_district["dim_change_district"]
    dim_channel["dim_channel"]
    dim_channel_cost["dim_channel_cost"]
    dim_company["dim_company"]
    dim_cost_group["dim_cost_group"]
    dim_cost_stk["dim_cost_stk"]
    dim_customer["dim_customer"]
    dim_department["dim_department"]
    dim_director["dim_director"]
    dim_invoice["dim_invoice"]
    dim_order["dim_order"]
    dim_payment["dim_payment"]
    dim_product_master["dim_product_master"]
    dim_product_mkt["dim_product_mkt"]
    dim_region["dim_region"]
    dim_region_manager["dim_region_manager"]
    dim_sale_representative["dim_sale_representative"]
    dim_section["dim_section"]
    dim_section_manager["dim_section_manager"]
    dim_stk_mkt["dim_stk_mkt"]
    dim_target_product_group_by_sale_dayofwork["dim_target_product_group_by_sale_dayofwork"]
  end
  subgraph fact["fact (8)"]
    fact_delivery["fact_delivery"]
    fact_invoice["fact_invoice"]
    fact_mir_rs["fact_mir_rs"]
    fact_mir_vs["fact_mir_vs"]
    fact_order["fact_order"]
    fact_quotation["fact_quotation"]
    fact_transaction_delivery["fact_transaction_delivery"]
    fact_transcation["fact_transcation"]
  end
  ap_s --> curated_mih
  ap_s --> dim_invoice
  ar_s --> curated_mih
  ar_s --> dim_invoice
  ar_s --> dim_order
  curated_mih --> dim_invoice
  curated_mih --> dim_order
  curated_mih --> fact_delivery
  curated_mih --> fact_mir_rs
  curated_mih --> fact_mir_vs
  curated_mih --> fact_transcation
  curated_mil --> dim_invoice
  curated_mil --> dim_order
  curated_mil --> fact_delivery
  curated_mil --> fact_invoice
  curated_mil --> fact_order
  curated_mil --> fact_transaction_delivery
  curated_mil --> fact_transcation
  deb --> dim_customer
  deb --> fact_delivery
  deb --> fact_transcation
  dim_change_district --> fact_transcation
  dim_channel --> fact_transcation
  dim_channel_cost --> fact_transcation
  dim_company --> dim_change_district
  dim_company --> dim_channel
  dim_company --> dim_channel_cost
  dim_company --> dim_cost_group
  dim_company --> dim_cost_stk
  dim_company --> dim_customer
  dim_company --> dim_department
  dim_company --> dim_director
  dim_company --> dim_invoice
  dim_company --> dim_order
  dim_company --> dim_payment
  dim_company --> dim_product_master
  dim_company --> dim_product_mkt
  dim_company --> dim_region
  dim_company --> dim_region_manager
  dim_company --> dim_sale_representative
  dim_company --> dim_section
  dim_company --> dim_section_manager
  dim_company --> dim_stk_mkt
  dim_company --> fact_mir_rs
  dim_company --> fact_mir_vs
  dim_cost_group --> fact_transcation
  dim_cost_stk --> fact_transcation
  dim_customer --> fact_invoice
  dim_customer --> fact_mir_rs
  dim_customer --> fact_mir_vs
  dim_customer --> fact_order
  dim_customer --> fact_quotation
  dim_customer --> fact_transcation
  dim_department --> fact_transcation
  dim_director --> fact_transcation
  dim_invoice --> fact_invoice
  dim_invoice --> fact_mir_rs
  dim_invoice --> fact_mir_vs
  dim_invoice --> fact_transaction_delivery
  dim_order --> dim_invoice
  dim_order --> fact_order
  dim_payment --> fact_transcation
  dim_product_master --> fact_order
  dim_product_master --> fact_quotation
  dim_product_master --> fact_transaction_delivery
  dim_product_master --> fact_transcation
  dim_product_mkt --> dim_product_master
  dim_product_mkt --> fact_transcation
  dim_region --> fact_transcation
  dim_region_manager --> fact_transcation
  dim_sale_representative --> fact_transcation
  dim_section --> fact_transcation
  dim_section_manager --> fact_transcation
  dim_stk_mkt --> dim_product_master
  dim_stk_mkt --> fact_transcation
  dim_target_product_group_by_sale_dayofwork --> fact_transcation
  fact_mir_vs --> fact_mir_rs
  fact_order --> fact_invoice
  fact_quotation --> fact_order
  fact_transaction_delivery --> fact_delivery
  mih --> curated_mih
  mih --> mil
  mih2 --> curated_mih
  mih2 --> curated_mil
  mih2 --> dim_invoice
  mil --> curated_mil
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class ap_s,ar_s,deb,mih,mih2,mil validated;
  class curated_mih,curated_mil curated;
  class dim_change_district,dim_channel,dim_channel_cost,dim_company,dim_cost_group,dim_cost_stk,dim_customer,dim_department,dim_director,dim_invoice,dim_order,dim_payment,dim_product_master,dim_product_mkt,dim_region,dim_region_manager,dim_sale_representative,dim_section,dim_section_manager,dim_stk_mkt,dim_target_product_group_by_sale_dayofwork dimension;
  class fact_delivery,fact_invoice,fact_mir_rs,fact_mir_vs,fact_order,fact_quotation,fact_transaction_delivery,fact_transcation fact;
```

---

## Delivery / logistics — การจัดส่ง

**Objects in this topic (3):** `dim_delivery`, `fact_delivery`, `fact_transaction_delivery`

**Fed by (9):** `curated_mih`, `curated_mil`, `deb`, `dim_company`, `dim_invoice`, `dim_product_master`, `tdelivery`, `ttrip`, `ttrip_document`

```mermaid
flowchart LR
  subgraph validated["validated (4)"]
    deb["deb"]
    tdelivery["tdelivery"]
    ttrip["ttrip"]
    ttrip_document["ttrip_document"]
  end
  subgraph curated["curated (2)"]
    curated_mih["curated_mih"]
    curated_mil["curated_mil"]
  end
  subgraph dimension["dimension (4)"]
    dim_company["dim_company"]
    dim_delivery["dim_delivery"]
    dim_invoice["dim_invoice"]
    dim_product_master["dim_product_master"]
  end
  subgraph fact["fact (2)"]
    fact_delivery["fact_delivery"]
    fact_transaction_delivery["fact_transaction_delivery"]
  end
  curated_mih --> dim_delivery
  curated_mih --> dim_invoice
  curated_mih --> fact_delivery
  curated_mil --> dim_delivery
  curated_mil --> dim_invoice
  curated_mil --> fact_delivery
  curated_mil --> fact_transaction_delivery
  deb --> dim_delivery
  deb --> fact_delivery
  dim_company --> dim_delivery
  dim_company --> dim_invoice
  dim_company --> dim_product_master
  dim_delivery --> fact_delivery
  dim_invoice --> fact_transaction_delivery
  dim_product_master --> fact_transaction_delivery
  fact_transaction_delivery --> fact_delivery
  tdelivery --> dim_delivery
  tdelivery --> fact_delivery
  ttrip --> dim_delivery
  ttrip --> fact_delivery
  ttrip_document --> dim_delivery
  ttrip_document --> fact_delivery
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class deb,tdelivery,ttrip,ttrip_document validated;
  class curated_mih,curated_mil curated;
  class dim_company,dim_delivery,dim_invoice,dim_product_master dimension;
  class fact_delivery,fact_transaction_delivery fact;
```

---

## Quotation / project — ใบเสนอราคา/โปรเจกต์

**Objects in this topic (4):** `curated_tbook_quotation`, `dim_project`, `dim_quotation`, `fact_quotation`

**Fed by (8):** `curated_mih`, `curated_mil`, `dim_company`, `dim_customer`, `dim_product_master`, `tbook_profilecomp`, `tbook_quodetail`, `tbook_quotation`

```mermaid
flowchart LR
  subgraph validated["validated (3)"]
    tbook_profilecomp["tbook_profilecomp"]
    tbook_quodetail["tbook_quodetail"]
    tbook_quotation["tbook_quotation"]
  end
  subgraph curated["curated (3)"]
    curated_mih["curated_mih"]
    curated_mil["curated_mil"]
    curated_tbook_quotation["curated_tbook_quotation"]
  end
  subgraph dimension["dimension (5)"]
    dim_company["dim_company"]
    dim_customer["dim_customer"]
    dim_product_master["dim_product_master"]
    dim_project["dim_project"]
    dim_quotation["dim_quotation"]
  end
  subgraph fact["fact (2)"]
    fact_order["fact_order"]
    fact_quotation["fact_quotation"]
  end
  curated_mih --> dim_quotation
  curated_mil --> dim_quotation
  curated_mil --> fact_order
  curated_tbook_quotation --> dim_quotation
  dim_company --> dim_customer
  dim_company --> dim_product_master
  dim_company --> dim_project
  dim_company --> dim_quotation
  dim_customer --> fact_order
  dim_customer --> fact_quotation
  dim_product_master --> fact_order
  dim_product_master --> fact_quotation
  dim_project --> dim_quotation
  dim_quotation --> fact_quotation
  fact_quotation --> fact_order
  tbook_profilecomp --> dim_project
  tbook_quodetail --> dim_quotation
  tbook_quodetail --> fact_quotation
  tbook_quotation --> curated_tbook_quotation
  classDef validated fill:#cfe8ff,stroke:#4a90d9,color:#111;
  classDef curated fill:#a8d5ff,stroke:#2f6fb0,color:#111;
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class tbook_profilecomp,tbook_quodetail,tbook_quotation validated;
  class curated_mih,curated_mil,curated_tbook_quotation curated;
  class dim_company,dim_customer,dim_product_master,dim_project,dim_quotation dimension;
  class fact_order,fact_quotation fact;
```

---

## Sales channel — ช่องทางขาย

**Objects in this topic (4):** `dim_channel`, `dim_channel_cost`, `dim_channel_finance`, `dim_channel_sales`

**Fed by (1):** `dim_company`

```mermaid
flowchart LR
  subgraph dimension["dimension (5)"]
    dim_channel["dim_channel"]
    dim_channel_cost["dim_channel_cost"]
    dim_channel_finance["dim_channel_finance"]
    dim_channel_sales["dim_channel_sales"]
    dim_company["dim_company"]
  end
  subgraph fact["fact (1)"]
    fact_transcation["fact_transcation"]
  end
  dim_channel --> fact_transcation
  dim_channel_cost --> fact_transcation
  dim_company --> dim_channel
  dim_company --> dim_channel_cost
  dim_company --> dim_channel_finance
  dim_company --> dim_channel_sales
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class dim_channel,dim_channel_cost,dim_channel_finance,dim_channel_sales,dim_company dimension;
  class fact_transcation fact;
```

---

## Cost — ต้นทุน

**Objects in this topic (2):** `dim_cost_group`, `dim_cost_stk`

**Fed by (1):** `dim_company`

```mermaid
flowchart LR
  subgraph dimension["dimension (3)"]
    dim_company["dim_company"]
    dim_cost_group["dim_cost_group"]
    dim_cost_stk["dim_cost_stk"]
  end
  subgraph fact["fact (1)"]
    fact_transcation["fact_transcation"]
  end
  dim_company --> dim_cost_group
  dim_company --> dim_cost_stk
  dim_cost_group --> fact_transcation
  dim_cost_stk --> fact_transcation
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef fact fill:#c6f5c6,stroke:#3fa63f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class dim_company,dim_cost_group,dim_cost_stk dimension;
  class fact_transcation fact;
```

---

## Calendar / date spine — ปฏิทิน/วันหยุด

**Objects in this topic (2):** `dim_calendar`, `dim_holiday`

```mermaid
flowchart LR
  subgraph dimension["dimension (2)"]
    dim_calendar["dim_calendar"]
    dim_holiday["dim_holiday"]
  end
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class dim_calendar,dim_holiday dimension;
```

---

## Reference / misc — ตารางอ้างอิงอื่นๆ

**Objects in this topic (2):** `dim_doctype`, `dim_waterpac`

**Fed by (1):** `dim_company`

```mermaid
flowchart LR
  subgraph dimension["dimension (3)"]
    dim_company["dim_company"]
    dim_doctype["dim_doctype"]
    dim_waterpac["dim_waterpac"]
  end
  dim_company --> dim_doctype
  dim_company --> dim_waterpac
  classDef dimension fill:#ffe0b3,stroke:#d98f2f,color:#111;
  classDef paused fill:#f5f5f5,stroke:#bbb,color:#999,stroke-dasharray:4 3;
  class dim_company,dim_doctype,dim_waterpac dimension;
```
