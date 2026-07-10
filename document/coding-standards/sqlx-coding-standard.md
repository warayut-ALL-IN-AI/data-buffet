# SQLX Coding Standard

มาตรฐานการเขียนไฟล์ `.sqlx` ของโปรเจกต์ — ยึดตามโค้ดจริงที่ใช้อยู่ (สแกน 2026-07-10)

## 1. โครงไฟล์

ทุกไฟล์เรียงเป็น 4 ส่วน:

```sqlx
config { ... }        -- metadata: type, schema, tags, dependencies, bigquery
js { ... }            -- ตัวแปร: table ref, pk_key, statement ที่ generate
<SQL body>            -- SELECT หรือ BEGIN...END
pre_operations {}     -- (validated) มักว่าง
post_operations { }   -- PK constraint / business UPDATE
```

## 2. config block

```javascript
config {
    type: "incremental",                    // "table" | "incremental" | "operations"
    schema: databuffet.VALIDATED_MAC5,      // ผ่าน databuffet.* เท่านั้น
    dependencies: ["validated_schema_mac5", "create_all_table_raw_mac5"],
    tags: [databuffet.TAG_VALIDATED, databuffet.TAG_VALIDATED_INCREMENTAL],
    uniqueKey: ["company_id", "mihtype", "mihvnos"],
    bigquery: {
        partitionBy: "asatdate",
        clusterBy: ["company_id", "mihvnos"],   // ≤ 4 คอลัมน์
    },
}
```

กติกา:
- `schema` และ `tags` ต้องอ้าง `databuffet.*` — **ห้าม string literal**
  (ยกเว้นข้อยกเว้นเดิม: `"mds_dataset"` ใน dim files)
- เลือก `type` ตาม layer:
  - validated: `incremental` (transactional) หรือ `table` (full-load reference)
  - curated: `incremental`
  - dimension MERGE: `operations` / dimension rebuild: `table`
  - fact: `table` หรือ `operations`
- `dependencies` ใช้กับ action ที่อ้างด้วย string interpolation (dim, schema bootstrap)
  ส่วนตารางที่อ่านผ่าน `${ref(...)}` Dataform จัด dependency ให้เอง — ไม่ต้องใส่ซ้ำ

## 3. js block

ตารางที่ไม่ได้อ่านผ่าน `ref()` ให้ประกาศ object + Ref string ตาม convention:

```javascript
js {
    const DimCompanyTable = {
        database: databuffet.DATABASE,
        schema: databuffet.DIMENSION_TABLE,
        name: "dim_company",
    };
    const DimCompanyTableRef = `${DimCompanyTable.database}.${DimCompanyTable.schema}.${DimCompanyTable.name}`;
}
```

- ชื่อ: `<PascalCase>Table` + `<PascalCase>TableRef`
- ตารางเป้าหมายของไฟล์ใช้ `name: name()` (ชื่อไฟล์ = ชื่อตาราง)
- validated: ประกาศ `pk_key` ใน js ให้ตรงกับ `uniqueKey` ใน config เสมอ (นิยามซ้ำ 2 ที่)

## 4. การ cast / ทำความสะอาดข้อมูล

ใช้ helper จาก `function-data.js` เท่านั้น:

```sql
${databuffet.functionData.cleanString("t1.CompanyID")} AS CompanyID,
${databuffet.functionData.castInt64("t1.StatusID")}    AS StatusID,
${databuffet.functionData.castFloat64("t1.weight")}    AS weight,
${databuffet.functionData.parseFlexibleDatetime("create_date")} AS create_date,
${databuffet.functionData.parseAsatDate()}             AS asatdate,
```

- string ทุกคอลัมน์ → `cleanString` (หรือ `cleanCode` ถ้ามี control character)
- ใน JOIN condition ก็ต้องใช้ `cleanString` ฝั่งต้นทางให้ตรงกับค่าที่เก็บ
- datetime จาก raw → `parseFlexibleDatetime` (SAFE, พังเป็น NULL)
- `castInt64/castFloat64` ไม่ SAFE — ตั้งใจให้ fail เมื่อ schema เพี้ยน

## 5. วันที่และ timezone

- `CURRENT_DATE('Asia/Bangkok')` เสมอ — ห้าม `CURRENT_DATE()` เปล่า
- Incremental window ของ validated กรองบน **string** `ASATDATE`:
  ```sql
  ${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", CURRENT_DATE('Asia/Bangkok')-1)`) }
  ```
- mds window: `DATE(t1.updated_at) >= DATE_SUB(CURRENT_DATE("Asia/Bangkok"), INTERVAL ${databuffet.MDS_BACKFILL_DAYS} DAY)`

## 6. Deduplication

```sql
QUALIFY ROW_NUMBER() OVER(
    PARTITION BY ${pk_key}
    ORDER BY asatdate DESC          -- หรือคอลัมน์ business ที่เหมาะสม
) = 1
```

## 7. Primary key (validated)

post_operations มาตรฐาน — retry loop 10 ครั้ง, รันเฉพาะ full build:

```sql
post_operations { ${ when(!incremental(), post_operations_statement) } }
-- statement = BEGIN ... WHILE retry < 10 ...
--   ALTER TABLE ${self()} DROP PRIMARY KEY IF EXISTS;
--   ALTER TABLE ${self()} ADD PRIMARY KEY (${pk_key}) NOT ENFORCED;
-- ... END
```

PK เป็น `NOT ENFORCED` — เป็น hint ให้ optimizer ไม่ใช่ constraint จริง

## 8. Dimension MERGE (สรุปย่อ)

ดูฉบับเต็ม: [project_wiki/dimension/merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md)

ลำดับใน `BEGIN...END`: `DECLARE max_sk` → `SET max_sk` → `MERGE` (CASE t3→t2→ใหม่)
→ `WHEN MATCHED UPDATE` (เฉพาะ attribute, ห้ามแตะ key) → `WHEN NOT MATCHED INSERT`
→ **DELETE row ที่ mds `is_active = FALSE`** → `END;`

## 9. คอมเมนต์

- คอมเมนต์ไทยหรืออังกฤษได้ ให้อธิบาย "ทำไม" ไม่ใช่ "ทำอะไร"
- โค้ดที่เลิกใช้: โปรเจกต์นิยม comment ไว้ (เช่น SK ใน dim_doctype) —
  ถ้าตั้งใจปิดถาวรให้เขียนเหตุผลกำกับ

## 10. สิ่งที่ห้ามทำ

| ห้าม | เพราะ |
|---|---|
| hardcode ชื่อ dataset/project | ต้องผ่าน `databuffet.*` เพื่อย้าย environment ได้ |
| แก้/regenerate SK เดิม | fact เก็บ SK แล้ว ข้อมูลจะชี้ผิด |
| `CURRENT_DATE()` ไม่ระบุ timezone | เที่ยงคืน UTC ≠ เที่ยงคืนไทย ข้อมูลคลาดวัน |
| แก้คำผิด `fact_transcation`, `CDC_DATESET`, `prdDiminsionData` | เป็น identifier จริงใน BigQuery |
| ใส่ dependency ของตารางที่อ่านผ่าน `ref()` ซ้ำ | graph ซ้ำซ้อน สับสน |
| ลืม DELETE ท้าย mds dim ใหม่ | row ที่ถูก soft-delete จะค้างตลอดไป |
