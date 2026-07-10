# How-to: เพิ่ม Dimension (mds MERGE pattern)

ครอบคลุมกรณีหลัก: dimension ใหม่จากตาราง `mds_dataset`
(กรณี lake-sourced หรือ full-rebuild ดูไฟล์กลุ่ม b/c ใน
[project_wiki/dimension/dimension-layer.md](../project_wiki/dimension/dimension-layer.md))

## ก่อนเริ่ม

1. **สร้างตารางเป้าหมายใน BigQuery ก่อน** — `type: "operations"` Dataform ไม่สร้างให้
   คอลัมน์ต้องมี: `<Entity>SK INT64`, natural key, attributes, `CompanySK`, `MdsID STRING`
2. ตัดสินใจ **natural key** (ชุดคอลัมน์ที่ระบุ entity) และชื่อ **SK** (`<Entity>SK`)
3. ตาราง mds ต้องมี `id`, `is_active`, `updated_at` (มาตรฐาน mds ทุกตัว)

## ขั้นตอน

### 1. Copy ไฟล์ต้นแบบ

`definitions/dimension/dim_waterpac.sqlx` เป็นตัวอย่างที่สั้นและครบ pattern
(natural key 2 คอลัมน์) — copy แล้วเปลี่ยนชื่อเป็น `dim_<entity>.sqlx`

### 2. แก้ config + js

```javascript
config {
  type: "operations",
  dependencies: ["dim_company"],
  tags: [databuffet.TAG_DIM_DAILY],
}
js {
  // Dim<Entity>Table → name: name()
  // DimCompanyTable → "dim_company"
  // MdsSourceTable → name: "mds_data_<entity>_master"
}
```

### 3. แก้ SQL — จุดที่ต้องเปลี่ยนทั้งหมด

| จุด | เปลี่ยนเป็น |
|---|---|
| `MAX(WaterPacSK)` | SK ใหม่ |
| CASE t3/t2 + ROW_NUMBER `ORDER BY` | natural key columns (ผ่าน `cleanString`) |
| `t2` self-join ON | natural key ทุกคอลัมน์ |
| `t3` self-join ON | `cleanString("t1.id") = t3.MdsID` (คงเดิม) |
| SELECT columns | attributes ของ entity (ทุก string ผ่าน `cleanString`) |
| `WHEN MATCHED UPDATE` | **เฉพาะ attribute + MdsID — ห้ามใส่ key/SK** |
| `WHEN NOT MATCHED INSERT` | ครบทุกคอลัมน์รวม SK และ MdsID |

### 4. อย่าลืม DELETE ปิดท้าย (บังคับ)

```sql
  DELETE FROM `${Dim<Entity>TableRef}`
  WHERE MdsID IN (
    SELECT id FROM `${MdsSourceTableRef}` WHERE is_active = FALSE
  );
END;
```

### 5. Backfill ครั้งแรก

MERGE กรอง `updated_at >= วันนี้ - MDS_BACKFILL_DAYS` (1 วัน) — รันครั้งแรกจะได้เฉพาะ
row ที่เพิ่งอัปเดต ให้ backfill โดยรันชั่วคราวด้วยค่า var ใหญ่ (เช่น 3650) หรือรัน
MERGE แบบ manual โดยตัด window ออกหนึ่งครั้ง

## กติกาความปลอดภัยของ SK

- SK เดิมห้ามเปลี่ยน — ลำดับ CASE คือ t3 (MdsID) → t2 (natural key) → ใหม่
- ห้าม UPDATE key columns ใน WHEN MATCHED
- MERGE `ON T.<SK> = S.<SK>` เสมอ (ไม่ใช่ natural key)
- ถ้า dim มี placeholder row ที่ไม่มี MdsID ให้ปล่อย `MdsID = NULL` —
  DELETE จะไม่แตะ (ดู `dim_stk_mkt`)

## Checklist

- [ ] ตารางเป้าหมายมีอยู่ใน BigQuery แล้ว
- [ ] `dependencies: ["dim_company"]` + join `dim_com` เพื่อ `CompanySK`
- [ ] dual self-join t2/t3 ครบ
- [ ] `WHERE t1.is_active = TRUE` + `MDS_BACKFILL_DAYS` window
- [ ] UPDATE ไม่แตะ key, INSERT ครบคอลัมน์
- [ ] DELETE inactive ก่อน `END;`
- [ ] backfill ครั้งแรกแล้ว
- [ ] ถ้า fact จะใช้: เพิ่ม join + dependency ในไฟล์ fact ที่เกี่ยว
