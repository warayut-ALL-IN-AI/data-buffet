# Onboarding — เริ่มงานกับ Data-Buffet

คู่มือสำหรับ developer ใหม่ อ่านจบแล้วควรเข้าใจว่าโปรเจกต์ทำอะไร รันยังไง และแก้โค้ดตรงไหน

## 1. โปรเจกต์นี้คืออะไร

Data warehouse บน **Google BigQuery** (project `databuffet-nonprd`, region `us-central1`)
สร้างด้วย **Dataform 3.0.0** — โค้ดทั้งหมดเป็นไฟล์ `.sqlx` (SQL + JavaScript template)

ข้อมูลไหลตามชั้น (medallion → star schema):

```
GCS AVRO (gs://file-raw-data)
  → initial   (external table + schema + UDF)
  → validated (ทำความสะอาด cast dedup — 135 ไฟล์)
  → curated   (business logic, join — 8 ไฟล์)
  → dimension (MERGE + surrogate key — 59 ไฟล์) + fact (star schema — 6 ไฟล์)
  ท่อเสริม: cdc (จับ change) + process (แกะที่อยู่ไทยด้วย AI)
```

อ่านคำศัพท์ก่อน: [glossary.md](glossary.md)

## 2. โครงสร้าง repo

```
definitions/         โค้ดหลักทุก layer (แยกโฟลเดอร์ตามชั้น/ตาม source)
includes/
  databuffet.js      config hub — ทุกไฟล์ .sqlx เรียกผ่าน databuffet.*
  controller/
    variables.json   ชื่อ dataset + tag ทั้งหมด (แก้ที่นี่ ห้าม hardcode)
    function-data.js SQL helper (cleanString, castInt64, ...)
    cdc-config.json  ตารางที่เปิด CDC
workflow_settings.yaml  ตั้งค่า project ต่อ environment
backup/              สำเนาไฟล์เวอร์ชันเก่า (อย่าแก้)
document/            เอกสาร (โฟลเดอร์นี้)
```

## 3. เครื่องมือที่ต้องมี

| เครื่องมือ | หมายเหตุ |
|---|---|
| `gcloud` + `bq` CLI | query ตรง: `bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'` — **ต้องใส่ `--project_id` เสมอ** เพราะ default project ของเครื่องไม่ใช่ตัวนี้ |
| Dataform | รันผ่าน Dataform service บน GCP (เครื่อง local WSL ปัจจุบันไม่มี CLI) ถ้าติดตั้งได้ใช้ `dataform compile` ตรวจ syntax ก่อน push |
| git | branch: `dev` (ทำงาน) → `nonprod` → `prod` |

## 4. Flow การทำงาน

1. แตกงานจาก branch `dev`  (หรือแก้บน `dev` ตามธรรมเนียมทีม)
2. แก้/เพิ่มไฟล์ `.sqlx` ตาม pattern ของ layer นั้น — ดู [how-to/](../how-to/)
3. ตรวจว่าใช้ `databuffet.*` ไม่ hardcode ชื่อ dataset
4. `dataform compile` (ถ้ามี CLI) หรือ push แล้วดู compile ใน Dataform UI
5. commit → push `dev` → merge เข้า `nonprod` เมื่อพร้อมทดสอบ

## 5. กติกาที่ห้ามพลาด

1. **Timezone Bangkok เสมอ** — `CURRENT_DATE('Asia/Bangkok')`
2. **String ทุกตัวผ่าน `cleanString`** — `''` ต้องกลายเป็น `NULL`
3. **SK มี 2 ระบบ** — dim แบบ MERGE (`dim_company`, `dim_aging_rang`, lake dims):
   SK คงที่ตลอดชีพ ห้าม regenerate / dim mds แบบ full rebuild (34 ตัว): SK ออกเลขใหม่
   ทุกวัน **ห้ามเก็บข้ามวัน**
4. **ตาราง `type: "operations"` Dataform ไม่สร้างให้** — dim แบบ MERGE และ
   `fact_transcation` ต้องมีตารางอยู่ก่อน
5. **คำผิดที่ห้ามแก้** (เป็นชื่อจริงใน BigQuery): `fact_transcation`, `CDC_DATESET`,
   `prdDiminsionData`
6. dim mds แบบ MERGE (2 ตัว) ต้องจบด้วย DELETE row ที่ `is_active = FALSE` ก่อน `END;`
   (แบบ full rebuild ไม่ต้อง)

## 6. อ่านต่อ

| เรื่อง | เอกสาร |
|---|---|
| ภาพรวมสถาปัตยกรรม | [../architecture/overview.md](../architecture/overview.md) |
| มาตรฐานการเขียนโค้ด | [../coding-standards/sqlx-coding-standard.md](../coding-standards/sqlx-coding-standard.md) |
| วิธีเพิ่มตารางแต่ละ layer | [../how-to/](../how-to/) |
| ปัญหาที่เจอบ่อย | [../operations/known-issues.md](../operations/known-issues.md) |
| Wiki ฉบับเต็ม (สำหรับคน + LLM) | [../project_wiki/README.md](../project_wiki/README.md) |
