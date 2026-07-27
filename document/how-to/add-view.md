# How-to: เพิ่ม View (presentation layer)

View คือชั้นนำเสนอสำหรับ Power BI / data mart / RLS — `type: "view"` ไม่เก็บข้อมูลจริง
รายละเอียด pattern เต็ม: [project_wiki/view/view-layer.md](../project_wiki/view/view-layer.md)

## ขั้นตอน

### 1. เลือก dataset ปลายทาง (สำคัญที่สุด)

**โฟลเดอร์ ≠ dataset ปลายทาง** — ไฟล์อยู่ที่ `definitions/view/<dataset>/` เพื่อจัดกลุ่ม
แต่ปลายทางจริงกำหนดด้วย `config.schema`

| ใช้เมื่อ | โฟลเดอร์ | `schema` |
|---|---|---|
| ห่อ dimension | `definitions/view/dimension_view/` | `databuffet.DIMENSION_VIEW` |
| ห่อ fact | `definitions/view/fact_view/` | `databuffet.FACT_VIEW` |
| data mart / Power BI / model | `definitions/view/onetime/` | `databuffet.ONETIME` |
| address / RLS | `definitions/view/process_dataset/` | `databuffet.PROCESS_DATASET` |
| bridge (many-to-many SK) | `definitions/view/bridge_dataset/` | `databuffet.BRIDGE` |

> ถ้าเป็นการย้าย view เดิมจาก BigQuery console เข้ามา — **ห้ามเปลี่ยน dataset ปลายทาง**
> เพราะ Power BI ชี้อยู่ที่เดิม จะพังทันที

### 2. สร้าง `definitions/view/<dataset>/<view_name>.sqlx`

```javascript
config {
  type: "view",
  schema: databuffet.DIMENSION_VIEW,
  dependencies: ["dim_company"],        // เฉพาะ action ที่ไม่ได้อ่านผ่าน ref()
  tags: [databuffet.TAG_VIEW],
}
```

### 3. อ้างอิงต้นทาง — กฎ 2 ชั้น ([coding-standard §3](../coding-standards/sqlx-coding-standard.md))

**(ก) `validated_*` / `curated_*` → `${ref()}`** ไม่ครอบ backtick และ
**ห้ามใส่ใน `dependencies[]`** (Dataform ผูกให้เอง)

```sql
FROM ${ref(databuffet.CURATED_MAC5, "curated_mih")} AS mih
```

**(ข) ที่เหลือ → js-block `TableRef`** (dim/fact, view อื่น, `process_dataset`,
`mds_dataset`, `onetime` base, UDF, external) แล้วใส่ใน `dependencies[]` ถ้าเป็น action ใน repo

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
LEFT JOIN `${DimCompanyTableRef}` AS com ON ...
```

ถ้า view อ่านแต่ validated/curated → **ไม่ต้องมี js block เลย**
(ตัวอย่าง: `view/onetime/Dimension_Quotation.sqlx`)

### 4. ข้อควรระวัง

- **backslash ต้อง double** — SQL body เป็น JS template literal
  ([§3.3](../coding-standards/sqlx-coding-standard.md)) เวลา copy SQL จาก BigQuery
  console เข้ามาต้องแปลงก่อน: `r'|\1'` → `r'|\\1'`, `r'\('` → `r'\\('`, `'\n'` → `'\\n'`
  (`\1` = compile error; `\(` / `\n` **ไม่ error แต่ผลลัพธ์เพี้ยนเงียบ**)
- **ห้ามมี `;` ปิดท้าย** — DDL ของ view ครอบ query อยู่แล้ว
- ห้าม hardcode `databuffet-nonprd` หรือชื่อ dataset; ห้าม inline
  `` `${databuffet.DATABASE}.${databuffet.X}.tbl` `` ใน SQL body
- ประกาศ js เฉพาะตัวที่ใช้จริง เรียงตามลำดับที่ถูกใช้ครั้งแรก
- ชื่อไฟล์ = ชื่อ view ใน BigQuery และต้องไม่ซ้ำกับ `.sqlx` อื่นทั้ง repo
  (ชื่อซ้ำทำให้ `dependencies[]` กำกวม)
- ถ้ามีคนแก้ view เดิมใน console อยู่ ต้องคุยก่อน — พอเข้า Dataform แล้วจะ
  `CREATE OR REPLACE` ทับทุกครั้งที่รัน

### 5. รัน

```bash
dataform run --tags view
```

view รันหลัง table layer (`dimension_daily` / `fact_daily`) เสมอ

## Checklist

- [ ] `type: "view"` + `schema` ชี้ dataset เดิม (ไม่เปลี่ยนปลายทาง)
- [ ] `tags: [databuffet.TAG_VIEW]`
- [ ] โฟลเดอร์ตรงกับ dataset ปลายทาง
- [ ] validated/curated ใช้ `${ref(...)}` และ **ไม่อยู่ใน** `dependencies[]`
- [ ] ที่เหลือใช้ js-block `` `${XxxTableRef}` `` และ repo action อยู่ใน `dependencies[]` ครบ
- [ ] ไม่มี `databuffet-nonprd` / inline `${databuffet.DATABASE}` / `;` ท้ายไฟล์
- [ ] backslash ใน regex/สตริง double เป็น `\\` แล้ว (รวมใน comment)
- [ ] ไม่มี declaration ที่ประกาศแล้วไม่ได้ใช้
- [ ] อัปเดต inventory ใน [project_wiki/view/view-layer.md](../project_wiki/view/view-layer.md)
