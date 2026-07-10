# สถาปัตยกรรม Data-Buffet

## ภาพรวม

```
GCS AVRO files  gs://file-raw-data  (Hive partition: ASATDATE=YYYYMMDD)
      │
      ▼
┌────────────┐  definitions/initial/ (13 ไฟล์)
│  INITIAL   │  external table + CREATE SCHEMA + UDF (function_dataset)
└────────────┘
      ▼
┌────────────┐  definitions/validated/ (135 ไฟล์)
│ VALIDATED  │  cast + TRIM + NULL + dedup (QUALIFY) — 1 ไฟล์ต่อ 1 ตารางต้นทาง
└────────────┘  mac5 87 · cis360 25 · mastersku 12 · saleout_mdt 11
      ▼
┌────────────┐  definitions/curated/ (8 ไฟล์)
│  CURATED   │  business logic: status lookup, split-sale, JSON parsing
└────────────┘
      ├───────────────────────────────┐
      ▼                               ▼
┌────────────┐                 ┌────────────┐
│ DIMENSION  │ ◄──── SK ────── │    FACT    │
│ (59 ไฟล์)  │                 │  (6 ไฟล์)  │
└────────────┘                 └────────────┘
 dimension_table                 fact_table

ท่อเสริม:  CDC (cdc_dataset)  →  PROCESS (process_dataset, AI.GENERATE แกะที่อยู่ไทย)
ต้นทางภายนอก:  mds_dataset (master data service — repo นี้ไม่ได้สร้าง)
```

## หน้าที่ของแต่ละชั้น

| ชั้น | Dataset | Materialization | หน้าที่ |
|---|---|---|---|
| Initial | `raw_*`, `function_dataset` | operations | external table ชี้ GCS, สร้าง schema/UDF |
| Validated | `validated_*` | incremental / table | cast type, ลบ string ว่าง, dedup ตาม PK |
| Curated | `curated_*` | incremental | join ข้าม validated, JSON parsing, split-sale (ag01) |
| Dimension | `dimension_table` | operations (MERGE) / table | ออก surrogate key, SCD |
| Fact | `fact_table` | table / operations | join SK ทุก dimension, retention 4 ปี |
| CDC | `cdc_dataset` | operations | จับ NEW/CHANGED จาก config |
| Process | `process_dataset` | incremental | AI แกะที่อยู่ไทย เฉพาะ row ที่ CDC บอกว่าเปลี่ยน |

## จุดสำคัญเชิงออกแบบ

### Surrogate key (SK)
Fact กับ dimension join กันด้วย SK ที่ dimension เป็นคนออก (`max_sk + ROW_NUMBER()`)
SK ต้อง**คงที่ตลอดชีวิต** ของ entity — MERGE ใช้ dual self-join (natural key + MdsID)
เพื่อรักษา SK เดิมเสมอ ดูรายละเอียด:
[project_wiki/dimension/merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md)

### mds_dataset และ soft delete
ตาราง `mds_data_*_master` ทุกตัวมี `id`, `is_active`, `updated_at`
- MERGE อ่านเฉพาะ `is_active = TRUE` และ `updated_at` ภายใน `MDS_BACKFILL_DAYS` (1 วัน)
- ท้ายทุกไฟล์ MERGE มี DELETE ลบ row ใน dim ที่ต้นทาง `is_active = FALSE`
  (ตัดสินใจใช้ hard delete เมื่อ 2026-07-10)

### MAC5 multi-company
5 บริษัท (ag01/aa05/ab01/ac02/ak02) → raw dataset แยกกัน → validated รวมด้วย
UNION ALL + คอลัมน์ `company_id` (14 ตาราง) — logic พิเศษบางอย่างเฉพาะ ag01
(split-sale, sign flip)

### Retention
- Fact: rolling 4 ปี (ตัดที่ต้นปี)
- CDC change log: 7 วัน (partition expiration)

## แผนผัง dependency หลัก

```
dim_company (root)
  ├─ mds dims ทุกตัว (35 ไฟล์)
  ├─ dim_customer ─ dim_customer_grade / dim_group_customer*
  ├─ dim_order ─ dim_invoice
  └─ dim_*_last (7 ตัว) ─ update_sk_sale_rep_group
        └─ dim_target_product_group_by_sale ─ ..._dayofwork (join dim_calendar)

fact_quotation → fact_order → fact_invoice          (SK ต่อเป็นทอด)
fact_transaction_delivery → fact_delivery
fact_transcation (join ~20 dims + onetime.Transaction_Data_Mart)
```

รายละเอียดเชิงลึกทุกชั้น: [project_wiki/](../project_wiki/README.md)
