# สถาปัตยกรรม Data-Buffet

## ภาพรวม

```
GCS AVRO files  gs://file-raw-data  (Hive partition: ASATDATE=YYYYMMDD)
      │
      ▼
┌────────────┐  definitions/initial/ (15 ไฟล์)
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
      └───────────────┬───────────────┘
                      ▼
              ┌────────────┐  definitions/view/ (42 ไฟล์)
              │    VIEW    │  BI/reporting views (type: "view")
              └────────────┘  dimension_view · fact_view · bridge_dataset ·
               view schemas    onetime · process_dataset

ท่อเสริม:  CDC (cdc_dataset)  →  PROCESS (process_dataset, AI.GENERATE แกะที่อยู่ไทย + RLS)
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
| View | `dimension_view`, `fact_view`, `bridge_dataset`, `onetime`, `process_dataset` | view | BI/reporting views อ่านจาก dim/fact/curated (`type: "view"`, tag `view`) |
| CDC | `cdc_dataset` | operations | จับ NEW/CHANGED จาก config |
| Process | `process_dataset` | incremental / operations | AI แกะที่อยู่ไทย (row ที่ CDC เปลี่ยน) + RLS (`rls_customer360`) |

## จุดสำคัญเชิงออกแบบ

### Surrogate key (SK) — 2 ระบบ (ตั้งแต่ 2026-07-20)
- **SK เสถียร** (MERGE dims: `dim_company`, `dim_aging_rang` + lake dims 10 ตัว):
  ออกด้วย `max_sk + ROW_NUMBER()` + dual self-join รักษา SK เดิมตลอดชีพ —
  ห้าม regenerate เด็ดขาด ดู
  [project_wiki/dimension/merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md)
- **SK รายวัน** (mds dims 34 ตัว — ปั้น full ใหม่ทุกวัน): `ROW_NUMBER()` ออกเลขใหม่
  ทุกคืน — consumer ทุกตัว re-derive รายวัน (ตรวจครบแล้ว) **ห้าม persist SK
  พวกนี้ข้ามวัน** ดู
  [project_wiki/dimension/full-rebuild-pattern.md](../project_wiki/dimension/full-rebuild-pattern.md)

### mds_dataset และการจัดการ delete/overwrite
ตาราง `mds_data_*_master` ทุกตัวมี `id` (UUID), `is_active`, `updated_at`
และรองรับ **overwrite import** (ล้างแล้วลงใหม่ = id ใหม่หมด)
- **dims 34 ตัว (full rebuild)**: อ่านเฉพาะ `is_active = TRUE` ทั้งตารางทุกคืน —
  soft delete และ overwrite import หายเองอัตโนมัติ (ตัดสินใจ 2026-07-20)
- **dims 2 ตัว (MERGE)**: window `MDS_BACKFILL_DAYS` (1 วัน) + tombstone DELETE
  ลบ row ที่ต้นทาง `is_active = FALSE` (hard delete, ตัดสินใจ 2026-07-10)

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
