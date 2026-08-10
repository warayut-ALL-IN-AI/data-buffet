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

## 3. การอ้างอิงตาราง/วิว — เลือก 1 ใน 2 แบบตาม "ใครสร้างตารางนั้น"

**กฎ**: ตารางที่ Dataform สร้างในชั้น validated/curated ใช้ `${ref()}`
ที่เหลือทั้งหมดประกาศ object + Ref string ใน `js {}` — **ห้าม inline**
`` `${databuffet.DATABASE}.${databuffet.XXX}.tbl` `` ใน SQL body และห้าม hardcode
`databuffet-nonprd` หรือชื่อ dataset ตรง ๆ

| แหล่งข้อมูล | รูปแบบ | `dependencies[]` |
|---|---|---|
| `validated_*`, `curated_*` | `${ref(databuffet.VALIDATED_MAC5, "deb")}` | **ห้ามใส่** — Dataform ผูกให้เอง |
| `dimension_table`, `fact_table`, view อื่น, `process_dataset`, `mds_dataset`, `onetime` base, `function_dataset`, external | js-block `<Pascal>TableRef` | ใส่ (เฉพาะที่เป็น action ใน repo) |

### 3.1 `${ref()}` — validated / curated

```sql
FROM ${ref(databuffet.CURATED_MAC5, "curated_mih")} AS mih
LEFT JOIN ${ref(databuffet.VALIDATED_MAC5, "deb")} AS deb ON ...
```

- 2 อาร์กิวเมนต์เสมอ: `ref(<schema constant>, "<table>")`
- **ไม่ต้องครอบ backtick** — `ref()` คืน FQN ที่ quote มาให้แล้ว
- ชื่อที่อ้างผ่าน `ref()` **ห้ามใส่ซ้ำใน `dependencies[]`** (§10)

### 3.2 js block — ที่เหลือทั้งหมด

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

```sql
FROM `${DimCompanyTableRef}`
```

- ชื่อ: `<PascalCase>Table` + `<PascalCase>TableRef` — PascalCase แปลงจากชื่อตาราง
  (`dim_company` → `DimCompany`, `mds_data_keyaccount_master` → `MdsDataKeyaccountMaster`)
- ต้องครอบ backtick: `` `${XxxTableRef}` ``
- ตารางเป้าหมายของไฟล์ใช้ `name: name()` (ชื่อไฟล์ = ชื่อตาราง)
- ประกาศเรียงตามลำดับที่ถูกใช้ครั้งแรกใน SQL และ**ประกาศเฉพาะตัวที่ใช้จริง**
  (ไม่มี declared-but-unused); ถ้าไฟล์นั้นอ้างแต่ validated/curated ก็**ไม่ต้องมี js block**
- validated: ประกาศ `pk_key` ใน js ให้ตรงกับ `uniqueKey` ใน config เสมอ (นิยามซ้ำ 2 ที่)

> ทำไม dim/fact ไม่ใช้ `ref()`: MERGE dims และ `fact_transcation` เป็น
> `type: "operations"` ที่ target มีอยู่ก่อนใน BigQuery — Dataform ไม่ได้เป็นเจ้าของ
> target จึง `ref()` ไม่ได้ ส่วน dim full-rebuild ที่เป็น `type: "table"` ยังคง js-block
> ตามของเดิมเพื่อให้ทั้ง layer เขียนเหมือนกัน
>
> **tech debt**: ไฟล์เก่าบางไฟล์ยัง inline อยู่ เช่น `fact_transcation.sqlx` ใช้
> `${databuffet.DATABASE}.onetime.Transaction_Data_Mart` แบบ inline (ควรเป็น js-block Ref)
> — ของใหม่ยึดกฎข้างบน ของเก่าค่อยแปลงเมื่อแตะไฟล์นั้น
> `definitions/view/` ทั้ง 42 ไฟล์ทำตามกฎนี้ครบแล้ว (2026-07-24)

### 3.3 Backslash ใน SQL body — เขียนตรง ๆ ตัวเดียว

**Dataform ส่ง backslash ใน SQL body ของ `.sqlx` ไปยัง BigQuery ตรง ๆ ไม่ unescape**
เขียนยังไงได้อย่างนั้น — regex เขียนเหมือนที่จะเขียนใน BigQuery console เป๊ะ

```sql
-- ถูก: เขียนตัวเดียวเหมือน SQL ปกติ
REGEXP_EXTRACT(pernamet, r'\(([^)]*)\)')
STRING_AGG(item, '\n')

-- ผิด: \\ จะหลุดไปถึง BigQuery ทั้งคู่
REGEXP_EXTRACT(pernamet, r'\\(([^)]*)\\)')   -- BigQuery อ่านว่า backslash + วงเล็บเปิด
```

| เขียนใน `.sqlx` | SQL ที่ออกจริง | ผล |
|---|---|---|
| `\n` `\(` `\d` `\s` `\+` `\1` | เหมือนเดิมทุกตัว | ✅ ที่ต้องการ |
| `\\n` `\\(` `\\d` | เหมือนเดิมทุกตัว (ยังคู่) | ⛔ regex พัง / เพี้ยนเงียบ |

#### ⚠️ ข้อยกเว้น — ใน `--` comment ต้อง double

Dataform escape backslash ให้อัตโนมัติ**เฉพาะในโค้ด SQL** แต่**ไม่ทำใน `--` comment**
comment จึงถูกประมวลผลเป็น JS template literal ตรง ๆ

```sql
--   SPLIT(REGEXP_REPLACE(ProductCode, r'/([PU])', r'|\\1'), '|')   -- ✅ ใน comment ต้อง \\1
    ARRAY_REVERSE(SPLIT(REGEXP_REPLACE(ProductCode, r'/([PU])', r'|\1'), '|'))  -- ✅ ในโค้ดใช้ \1
```

| ใน `--` comment | ผล |
|---|---|
| `\1`–`\9`, `\0` | ⛔ **compile error** *"Octal escape sequences are not allowed in template strings"* |
| `\n` `\t` `\r` | ⚠️ กลายเป็นขึ้นบรรทัดใหม่/tab จริง — **comment ขาดกลางคัน ส่วนที่เหลือกลายเป็นโค้ด** |
| `\(` `\d` `\s` | backslash หายเงียบ (ไม่อันตรายเพราะเป็น comment แต่อ่านแล้วสับสน) |
| `\\1` `\\n` | ✅ ได้ `\1` `\n` ตามต้องการ |

**สรุป: โค้ดเขียนตัวเดียว / comment เขียนสองตัว**
ที่ใช้อยู่จริง: [view_dim_product_master.sqlx:45](../../definitions/view/dimension_view/view_dim_product_master.sqlx)
เป็น comment เดียวในทั้งโปรเจกต์ที่มี backslash (สแกนยืนยัน 2026-08-10)

> ⚠️ **ข้อยกเว้น — ไฟล์ `.js` จริงใน `includes/`**
> `includes/controller/function-data.js` เป็น JavaScript จริง string ในนั้นเป็น template
> literal จริง ๆ → **ต้อง double** เช่น ``pattern = `r'[\\n\\r\\t]'` `` ซึ่ง**ถูกแล้ว**
> กฎ "เขียนตัวเดียว" ใช้กับ **SQL body ของ `.sqlx` เท่านั้น** ไม่ใช้กับ `.js`

> **ยืนยันก่อน deploy เสมอ**: เปิด panel **Compiled queries** ใน Dataform UI แล้วดูว่า
> backslash ที่ออกมาเป็นแบบที่ต้องการจริง — เร็วกว่าและชัวร์กว่าการเดาจากเอกสาร

> **ห้าม copy `.sqlx` ไปวางใน BigQuery console และห้าม copy จาก console กลับเข้า `.sqlx`
> โดยไม่ตรวจ** — deploy ผ่าน Dataform เท่านั้น

#### ประวัติ (สำคัญ — เอกสารฉบับก่อนบอกกลับด้าน)

| วันที่ | เกิดอะไร |
|---|---|
| 2026-07-27 | §3.3 ฉบับแรกสรุปว่า Dataform คอมไพล์ body เป็น JS template literal จึงต้อง double → commit `3c02e61` ไล่ double 3 view file + `67e779e` double ทั้ง `create_all_function.sqlx` (335 จุด) |
| 2026-08-07 | UDF ถูก deploy เข้า BigQuery → `EXTRACT_CHQ_DATA` พัง `Cannot parse regular expression: missing )` |
| 2026-08-10 | ตรวจ **Compiled queries panel ของจริง** → `\\` ออกมาเป็น `\\` ไม่ถูกกิน **ข้อสรุปเดิมผิด** ย้อน `create_all_function.sqlx` (351 จุด) และ 3 view file กลับเป็น backslash ตัวเดียว |

**บทเรียน**: อย่าสรุปพฤติกรรม compiler จากการอนุมาน — เปิด Compiled queries panel ดูของจริง

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
  ${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY))`) }
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

## 8. Dimension patterns (สรุปย่อ)

**Default — full rebuild** (mds dims 34 ตัว):
[project_wiki/dimension/full-rebuild-pattern.md](../project_wiki/dimension/full-rebuild-pattern.md)
`type: "table"` → SELECT เดียว: `ROW_NUMBER() OVER(ORDER BY natural key)` AS SK →
join dim_company → `WHERE is_active = TRUE` → `MdsID` ปิดท้าย — SK ใหม่ทุกวัน

**Legacy — MERGE SK เสถียร** (dim_company, dim_aging_rang + lake dims):
[project_wiki/dimension/merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md)
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
| inline `` `${databuffet.DATABASE}.${databuffet.X}.tbl` `` ใน SQL body | ต้องประกาศ object + `XxxTableRef` ใน `js {}` แล้วอ้าง `` `${XxxTableRef}` `` (§3.2) |
| ใช้ js-block Ref กับ `validated_*` / `curated_*` | ต้องใช้ `${ref(...)}` เพื่อให้ Dataform ผูก dependency ให้ (§3.1) |
| เขียน `\` เดี่ยวใน SQL body (regex, `\n`) | body เป็น JS template literal — `\1` = compile error, `\(`/`\d` โดนกลืน backslash เงียบ ต้อง `\\` (§3.3) |
| แก้/regenerate SK ของ MERGE dims | fact/dim อื่น persist SK พวกนั้นไว้ ข้อมูลจะชี้ผิด |
| persist SK ของ full-rebuild dims ข้ามวัน | SK ออกเลขใหม่ทุกคืน — consumer ใหม่ต้อง rebuild รายวันตาม |
| `CURRENT_DATE()` ไม่ระบุ timezone | เที่ยงคืน UTC ≠ เที่ยงคืนไทย ข้อมูลคลาดวัน |
| แก้คำผิด `fact_transcation`, `CDC_DATESET`, `prdDiminsionData` | เป็น identifier จริงใน BigQuery |
| ใส่ dependency ของตารางที่อ่านผ่าน `ref()` ซ้ำ | graph ซ้ำซ้อน สับสน |
| ลืม DELETE ท้าย mds dim แบบ MERGE (dim_company/dim_aging_rang) | row ที่ถูก soft-delete จะค้างตลอดไป |
