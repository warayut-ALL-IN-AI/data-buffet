# How-to: เพิ่ม Dimension จาก mds (full-rebuild pattern)

ตั้งแต่ 2026-07-20 pattern มาตรฐานของ dim ที่ source จาก `mds_dataset` คือ
**full daily rebuild** (`type: "table"`) — ปั้นใหม่ทุกวันจาก `is_active = TRUE`
ดูเหตุผลและรายละเอียด: [project_wiki/dimension/full-rebuild-pattern.md](../project_wiki/dimension/full-rebuild-pattern.md)

> ⚠️ **SK ของ pattern นี้ออกเลขใหม่ทุกวัน** — ก่อนสร้าง dim ใหม่ ตอบคำถามนี้ก่อน:
> *"จะมีตารางไหน persist SK ของ dim นี้ข้ามวันไหม?"* ถ้ามี (เช่น fact แบบ incremental
> ที่ไม่ rebuild ทั้งก้อน) ต้องใช้ [MERGE pattern](../project_wiki/dimension/merge-sk-pattern.md)
> แบบ `dim_company` แทน และปรึกษาทีมก่อน

## ขั้นตอน

### 1. Copy ไฟล์ต้นแบบ

`definitions/dimension/dim_waterpac.sqlx` — copy แล้วเปลี่ยนชื่อเป็น `dim_<entity>.sqlx`

### 2. แก้จุดเหล่านี้

| จุด | เปลี่ยนเป็น |
|---|---|
| `uniqueKey` + `clusterBy` | `<Entity>SK` ของคุณ |
| `MdsSourceTable.name` | `mds_data_<entity>_master` |
| `ROW_NUMBER() ORDER BY` | natural key ทุกคอลัมน์ (ผ่าน `cleanString`/`castInt64`) — ลำดับ deterministic |
| SELECT columns | attributes ของ entity (string ผ่าน `cleanString`) + `dim_com.CompanySK` + ปิดท้าย `MdsID` |
| `WHERE` | `t1.is_active = TRUE` เท่านั้น (ไม่มี window `updated_at`) |

- `dependencies: ["dim_company"]` เสมอ (join ผ่าน string interpolation)
- ไม่ต้องมี MERGE, max_sk, tombstone DELETE, `MDS_BACKFILL_DAYS` — pattern นี้ไม่ใช้
- Dataform สร้าง/แทนที่ตารางให้เอง — **ไม่ต้องสร้างตารางใน BigQuery ก่อน**
- ไม่ต้อง backfill — รันครั้งแรกได้ข้อมูลเต็มทันที

### 3. กรณีพิเศษ

- ต้องรวมข้อมูลจากตาราง lake (เช่น placeholder): ทำเป็น CTE + `UNION ALL` แล้วค่อยใส่
  `ROW_NUMBER()` ทับทั้งก้อน — ดู `dim_stk_mkt.sqlx` (Waiting Master) หรือ
  `dim_sale_representative.sqlx` (ledger reps)
- ไม่ต้องการ SK เลย (reference ล้วน): ตัด ROW_NUMBER + uniqueKey/clusterBy ออก —
  ดู `dim_doctype.sqlx`

### 4. ถ้า fact จะใช้ SK ของ dim ใหม่

- fact ต้องเป็นแบบ rebuild รายวัน หรือ re-derive SK ครอบทุก row ที่เก็บ (แบบ
  `fact_transcation`) และรันหลัง `dimension_daily` ใน DAG เดียวกัน
- เพิ่มชื่อ dim ใน `dependencies[]` ของไฟล์ fact (dim อ้างด้วย string interpolation)

## Checklist

- [ ] ตอบคำถาม "ใคร persist SK ข้ามวัน" แล้ว = ไม่มี
- [ ] `ROW_NUMBER ORDER BY` ครอบ natural key ครบ ลำดับ deterministic
- [ ] `WHERE t1.is_active = TRUE` เท่านั้น
- [ ] คอลัมน์ `MdsID` ปิดท้าย (ไว้ trace)
- [ ] `dependencies: ["dim_company"]` + tag `TAG_DIM_DAILY`
- [ ] เพิ่มแถวใน `project_wiki/dimension/inventory.md`

## เพิ่ม dim แบบ SK เสถียร (MERGE — เคสพิเศษเท่านั้น)

ใช้เมื่อ SK ต้องคงที่ตลอดชีพ (มี consumer persist ข้ามวัน) — ตาม
[merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md):
ตารางต้องมีใน BigQuery ก่อน, MERGE + dual join t2/t3, tombstone DELETE ก่อน `END;`,
backfill ครั้งแรกด้วย `MDS_BACKFILL_DAYS` ชั่วคราว — ตัวอย่าง: `dim_company.sqlx`
