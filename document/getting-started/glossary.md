# Glossary — คำศัพท์และแนวคิดหลักของ Data-Buffet

คำศัพท์ที่ developer ใหม่ต้องรู้ก่อนอ่านโค้ดในโปรเจกต์นี้

## แนวคิดสถาปัตยกรรม

| คำ | ความหมาย |
|---|---|
| **Medallion architecture** | การแบ่งชั้นข้อมูล raw → validated → curated → (dimension/fact) แต่ละชั้นสะอาดและพร้อมใช้ขึ้นเรื่อย ๆ |
| **Star schema** | โมเดลข้อมูลชั้นบนสุด: fact table ตรงกลาง join กับ dimension รอบ ๆ ด้วย surrogate key |
| **Layer / ชั้น** | initial → validated → curated → dimension + fact (มี cdc/process เป็นท่อเสริม) |
| **Dataform** | Framework ที่ใช้ orchestrate SQL ใน BigQuery — ไฟล์ `.sqlx` = SQL + JavaScript template |
| **SQLX** | ไฟล์ Dataform: `config {}` (metadata) + `js {}` (ตัวแปร) + ตัว SQL ที่มี `${...}` template |

## Key และ ID

| คำ | ความหมาย |
|---|---|
| **SK (Surrogate Key)** | คีย์ตัวเลขที่ระบบสร้างเอง (`CompanySK`, `SaleRepSK`, `WeightSK`, ...) ใช้ join ระหว่าง fact ↔ dimension ห้ามเอาไปมีความหมายทางธุรกิจ |
| **Natural key / Business key** | คีย์จากระบบต้นทาง เช่น `CompanyID + StkCode` ใช้จับคู่ว่า row ต้นทางตรงกับ dimension row ไหน |
| **MdsID** | คอลัมน์ในตาราง dimension เก็บค่า `id` ของ row ต้นทางจาก `mds_dataset` ใช้ทั้ง dedup (join `t3`) และลบ row ที่ต้นทาง `is_active = FALSE` |
| **max_sk + ROW_NUMBER()** | วิธีออก SK ใหม่: หา `MAX(SK)` เดิม แล้วบวก `ROW_NUMBER()` ให้ row ใหม่ที่ยังไม่มี SK |
| **Dangling FK / orphan** | ค่า SK ใน fact ที่ไม่มีอยู่ใน dimension แล้ว (เช่นหลังลบ row) — โปรเจกต์นี้สแกนแล้ว ณ 2026-07 ไม่มีค้าง |

## ข้อมูลและแหล่งข้อมูล

| คำ | ความหมาย |
|---|---|
| **MAC5** | ระบบ POS/บัญชี มี 5 บริษัท (ag01, aa05, ab01, ac02, ak02) แต่ละบริษัทมี raw dataset แยก รวมเป็น `validated_mac5` ด้วยคอลัมน์ `company_id` |
| **MASTERSKU** | Product master (สี ขนาด มิติสินค้า — มี JSON ซ้อน) |
| **CIS360** | ข้อมูลอ้างอิงลูกค้า |
| **SALEOUT_MDT** | ข้อมูล sale-out จาก dealer (BT, GB, HP, TW) |
| **mds_dataset** | ตาราง master-data-service ที่โหลดเข้ามาจากภายนอก (ไม่ได้สร้างโดย repo นี้) — เป็นต้นทางของ dimension ส่วนใหญ่ ทุกตารางมี `id`, `is_active`, `updated_at` |
| **ASATDATE / asatdate** | วันที่ของ snapshot ข้อมูล (string `YYYYMMDD` ใน raw → `DATE` ใน validated) เป็น partition column หลักของตาราง incremental |
| **AVRO / external table** | ไฟล์ raw บน GCS (`gs://file-raw-data`) อ่านผ่าน BigQuery external table — ข้อมูลจริงอยู่บน GCS |

## Pattern ที่เจอบ่อย

| คำ | ความหมาย |
|---|---|
| **Full load** | สร้างตารางใหม่ทั้งก้อนทุกรอบ — ใช้กับ reference data ขนาดเล็ก (tag `validated_full`) |
| **Incremental** | โหลดเฉพาะ partition ช่วงหลัง (`asatdate >= CURRENT_DATE('Asia/Bangkok') - N`) (tag `validated_incremental`) |
| **QUALIFY dedup** | `QUALIFY ROW_NUMBER() OVER(PARTITION BY <pk> ORDER BY file_load_datetime DESC) = 1` — เก็บ row ล่าสุดต่อคีย์ |
| **MERGE upsert** | `MERGE ... WHEN MATCHED UPDATE / WHEN NOT MATCHED INSERT` — ใช้ใน dimension เพื่อรักษา SK เดิม |
| **mds inactive DELETE** | ท้ายทุก dimension MERGE: `DELETE FROM dim WHERE MdsID IN (SELECT id FROM mds WHERE is_active = FALSE)` — ลบ row ที่ต้นทาง soft-delete |
| **MDS_BACKFILL_DAYS** | ตัวแปรโปรเจกต์ (ปัจจุบัน `1`) จำกัดหน้าต่าง `updated_at` ที่ MERGE จะสแกนจาก mds |
| **operations type** | ไฟล์ Dataform ที่รัน raw BigQuery script (`BEGIN...END`) — Dataform ไม่จัดการ schema/lineage ให้ ตารางต้องมีอยู่ก่อน |
| **cleanString** | helper แปลง `''` → `NULL` + TRIM — มาตรฐานการจัดการ string ทั้งโปรเจกต์ |
| **Bangkok timezone** | ทุกการคำนวณวันที่ใช้ `CURRENT_DATE('Asia/Bangkok')` เสมอ |
| **Waiting Master** | placeholder row ใน `dim_stk_mkt` (MdsID = NULL) สำหรับ stkcode ที่ยังไม่มี master |

## เครื่องมือ

| คำ | ความหมาย |
|---|---|
| **`dataform compile`** | ตรวจ syntax + สร้าง execution graph (ไม่รันจริง) |
| **`dataform run --tags <tag>`** | รันเฉพาะกลุ่ม เช่น `dimension_daily`, `validated_incremental` |
| **`bq` CLI** | Query BigQuery ตรง ๆ — ต้องระบุ `--project_id=databuffet-nonprd` เสมอ |
