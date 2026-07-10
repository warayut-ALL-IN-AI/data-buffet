# Naming Conventions

สรุปกติกาตั้งชื่อทั้งโปรเจกต์ (สแกนจากโค้ดจริง 2026-07-10)

## ไฟล์ / Action

| ประเภท | Pattern | ตัวอย่าง |
|---|---|---|
| Validated | `<ชื่อตาราง raw>.sqlx` (ชื่อไฟล์ = ชื่อตาราง ผ่าน `name()`) | `mih.sqlx`, `customer_profile.sqlx` |
| Schema bootstrap | `validated_schema_<source>.sqlx`, `curated_schema_<source>.sqlx` | |
| Initial | `create_all_table_raw_<source>[_<company>].sqlx`, `drop_all_tables_<layer>_<source>.sqlx` | |
| Curated | `curated_<ชื่อ>.sqlx` | `curated_mih.sqlx` |
| Dimension | `dim_<entity>.sqlx` snake_case; snapshot ปัจจุบันต่อท้าย `_last`; aggregate ต่อ suffix ตามเรื่อง | `dim_sale_representative_last.sqlx` |
| ตัวช่วย imperative | prefix `update_sk_` | `update_sk_sale_rep_group.sqlx` |
| Fact | `fact_<entity>.sqlx` | `fact_invoice.sqlx` (ระวัง `fact_transcation` สะกดตามนี้จริง) |

## Dataset (BigQuery schema)

`raw_<source>[_<company>]` → `validated_<source>` → `curated_<source>` +
dataset กลาง: `dimension_table`, `dimension_view`, `fact_table`, `fact_view`,
`cdc_dataset`, `process_dataset`, `function_dataset`, `mds_dataset`, `onetime`
— ทั้งหมดอ้างผ่านคีย์ใน `variables.json`

## คอลัมน์

| ที่ | Convention | ตัวอย่าง |
|---|---|---|
| validated (mac5) | ชื่อ raw ตัวพิมพ์เล็ก | `MIHvnos` → `mihvnos` |
| validated (mastersku) | prefix `prd_*` snake_case | `prd_id` |
| curated | camelCase | `mihVnos`, `prdSku` |
| dimension/fact | PascalCase | `CompanyID`, `WaterPacName` |
| Surrogate key | `<Entity>SK` PascalCase | `CompanySK`, `SaleRepSK`, `FactOrderSK` |
| mds row id ใน dim | `MdsID` | |
| คอลัมน์ก่อนปรับเครื่องหมาย | `<ชื่อ>_raw` | `mihnetsum_raw` |
| วันที่ snapshot | `asatdate` (DATE) | |
| วันที่ business ใน fact | `mix_date` | |
| multi-company | `company_id` (validated) / `CompanyID` + `CompanySK` (dim) | |

หมายเหตุ: SK ไม่จำเป็นต้องแปลตรงจากชื่อตาราง — `dim_collection_status → CollectSK`,
`dim_status_not_receive → NotReceiveSK`, `dim_avg_collection_score → AvgCollectSK`,
`dim_product_master → ProductSK`

## ตัวแปร JavaScript ใน js block

| ตัวแปร | ใช้กับ |
|---|---|
| `<Name>Table` / `<Name>TableRef` | object + FQN string ของทุกตารางที่อ้างตรง |
| `MdsSourceTable` / `MdsSourceTableRef` | ตารางต้นทาง mds |
| `sourceTable` / `sourceTableRef` | ต้นทาง raw ใน validated |
| `pk_key` | array PK ใน validated (ต้องตรงกับ `uniqueKey`) |
| `partition_statement`, `post_operations_statement` | statement ที่ generate |

## Alias ใน SQL

| Alias | ความหมาย |
|---|---|
| `t1` | ตารางต้นทาง |
| `t2` | self-join ด้วย natural key |
| `t3` | self-join ด้วย `MdsID` |
| `dim_com` | lookup `dim_company` |
| `T` / `S` | MERGE target / source |

## Tags

รูปแบบ `<layer>_<cadence|mode>`: `validated_incremental`, `validated_full`,
`dimension_daily`, `dimension_yearly`, `fact_daily`, `cdc_incremental`, `process`,
`initial`, `re-initial` — นิยามใน `variables.json` เท่านั้น

## ตาราง mds

`mds_data_<entity>_master` — มี `id`, `is_active`, `updated_at` ทุกตาราง
