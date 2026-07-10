# How-to: เพิ่มตาราง Curated

## ขั้นตอน

### 1. ระบุ dependency

ต้นทางคือตาราง validated (อ่านผ่าน `${ref(databuffet.VALIDATED_MAC5, "mih")}` —
Dataform จัด dependency ให้เอง) ส่วน `dependencies` ใน config ใส่แค่
`curated_schema_<source>`

### 2. สร้าง `definitions/curated/<source>/curated_<name>.sqlx`

```javascript
config {
    type: "incremental",
    schema: databuffet.CURATED_MAC5,
    dependencies: ["curated_schema_mac5"],
    tags: [databuffet.TAG_CURATED],
    uniqueKey: ["company_id", "mihType", "mihVnos"],
    bigquery: {
        partitionBy: "asatdate",
        clusterBy: ["company_id", "mihVnos", "mihType"],
    },
}
```

### 3. เขียน logic

- Rename คอลัมน์ validated (snake/lower) → **camelCase**
- Business logic ที่ทำในชั้นนี้: status lookup (join ar_s/ap_s), แปลง percent string,
  JSON parsing, dedup revision ล่าสุด
- Incremental window แบบ inline (มาตรฐานจริงของชั้นนี้คือ **1 วัน**):
  ```sql
  ${when(incremental(), `AND asatdate >= CURRENT_DATE('Asia/Bangkok')-1`)}
  ```

### 4. Logic ซับซ้อนหลัง load → post_operations

ถ้าต้อง reallocate/แก้ค่าเป็นกลุ่ม (เช่น split-sale ของ ag01 ใน `curated_mil`)
ใช้ block รูปแบบนี้:

```sql
post_operations {
  BEGIN
    CREATE TEMP TABLE new_data AS ( ...CTE คำนวณ... );
    DELETE FROM ${self()} WHERE <PK> IN (SELECT <PK> FROM new_data);
    INSERT INTO ${self()} SELECT * FROM new_data;
  END
}
```

ตัวอย่างจริงที่ควรอ่านก่อนเขียน:
- `curated/mac5/curated_mih.sqlx` — status lookup + UNION แยกบริษัท
- `curated/mac5/curated_mil.sqlx` — post_operations split-sale (ซับซ้อนสุด)
- `curated/mastersku/curated_product.sqlx` — JSON parsing + Thai/English color split
  (ตารางเดียวที่ใช้ `updatePartitionFilter` 7 วัน)

## Checklist

- [ ] `type: "incremental"` + `uniqueKey` มี `company_id` (mac5)
- [ ] partition `asatdate`, cluster ≤ 4 คอลัมน์
- [ ] อ่านต้นทางผ่าน `ref()` — ไม่ hardcode
- [ ] window `when(incremental(), ...)` Bangkok time
- [ ] คอลัมน์ output เป็น camelCase
- [ ] logic กลุ่ม/ซับซ้อนอยู่ใน post_operations ไม่ปนกับ SELECT หลัก
