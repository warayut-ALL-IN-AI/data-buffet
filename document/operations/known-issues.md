# Known Issues & Gotchas

รวมจุดที่รู้แล้วว่า "เป็นแบบนี้โดยตั้งใจ" หรือ "ต้องระวัง" — อัปเดตล่าสุด 2026-07-10

## คำสะกดผิดที่เป็น identifier จริง (ห้ามแก้)

| ที่ | คำ | หมายเหตุ |
|---|---|---|
| `definitions/fact/fact_transcation.sqlx` | `fact_transcation` | ชื่อไฟล์ + ตารางจริงใน BigQuery |
| `includes/controller/variables.json` | `CDC_DATESET` | คีย์ constant (ค่า `cdc_dataset` ถูกต้อง) |
| MASTERSKU JSON | `prdDiminsionData`, `SpeciFeild`, `dimFeild` | field จริงในข้อมูล |
| `FactOrderSk` vs `FactOrderSK` | casing ไม่คงที่ในไฟล์เดียวกัน | ใช้ตามที่ไฟล์นั้นใช้ |

## เอกสารเก่าที่ล้าสมัย (อย่าเชื่อ)

`.claude/CLAUDE.md`, `.claude/knowledge/*.md`, `.claude/skills/add-*.md` เขียนจาก
design เก่า มีข้อผิดพลาดสำคัญ:

- อ้าง `includes/controller/primary-keys.json` และ `databuffet.primaryKeys` — **ไม่มีไฟล์นี้**
  (PK นิยามในแต่ละไฟล์: `uniqueKey` + `pk_key`)
- ใช้ accessor `databuffet.SCHEMA_VALIDATED_MAC5` — ของจริงคือ `databuffet.VALIDATED_MAC5`
- บอกว่า fact มีตารางเดียว (`fact_transaction`) — ของจริงมี 6 ไฟล์
- ไม่พูดถึง dimension/CDC/process layer และ source SALEOUT_MDT
- อ้าง tag `fact`, `assertions` — ไม่มีจริง
- ตัวเลขจำนวนไฟล์ผิดหมด

**แหล่งที่ถูกต้อง**: `README.md` (root) + `document/project_wiki/`
ส่วน root README มีจุดเดียวที่เพี้ยน: บอก "15 dims" (ของจริง 59 ไฟล์)

## พฤติกรรมที่ตั้งใจ (อย่า "แก้")

- **Hard delete ใน mds dims** (ตัดสินใจ 2026-07-10): row ที่ mds `is_active = FALSE`
  ถูกลบจริงจาก dim โดยไม่เช็ก FK ปลายทาง — สแกน ณ วันตัดสินใจพบ SK ค้าง 0 แถว
  ผลข้างเคียงที่ยอมรับ: fact อาจถือ SK กำพร้า / entity ที่ reactivate ได้ SK ใหม่
- **DELETE ไม่มี date filter** — ตั้งใจสแกน mds ทั้งตาราง (ตารางเล็ก)
- **`dim_doctype` / `dim_holiday` ไม่มี SK** — โค้ด SK ถูก comment ไว้ MERGE ด้วย
  natural key แทน
- **`dim_stk_mkt` มี row 'Waiting Master'** (`MdsID = NULL`, MarketingGroupID='999') —
  placeholder สำหรับ stkcode ที่ยังไม่มี master ปลอดภัยจาก DELETE เพราะ
  `IN (subquery)` ไม่ match NULL
- **`curated_tbook_quotation`** — partition + incremental filter ถูก comment ไว้
  จึงทำงานเหมือน full rebuild แม้ประกาศ `type: "incremental"`
- **`mir.sqlx`** — `type: "incremental"` แต่ tag `validated_full` (จัดกลุ่ม operator)
- **saleout_mdt** — ไม่มี sub-tag และส่วนใหญ่ไม่ partition

## ข้อจำกัด environment

- เครื่อง local WSL ไม่มี `dataform` CLI (`dataform` และ `npx dataform` fail ทั้งคู่)
- `bq` ต้องระบุ `--project_id=databuffet-nonprd` (default gcloud project เป็นตัวอื่น)
- INFORMATION_SCHEMA ระดับ region ถูก deny — ใช้ระดับ dataset
- `workflow_settings.yaml` เป็นค่าเฉพาะ environment

## เหตุการณ์ที่เคยเกิด

- **2026-05-23/24**: validated_mac5 datetime parse fail 2 วัน (รูปแบบ timestamp
  จาก raw เปลี่ยนชั่วคราว) — หายเองตั้งแต่ 05-25 ถ้าเกิดซ้ำให้ดู
  `parseFlexibleDatetime` ว่ารองรับ format ใหม่หรือยัง

## หนี้ทางเทคนิค / งานค้าง

- SK ที่ยังไม่รู้เจ้าของ (จาก FK scan 2026-07-09): `BillingSK` (หา dim ต้นทางไม่พบ),
  `DueAvgCollectSK`/`InvAvgCollectSK` (น่าจะ role-play ของ dim_avg_collection_score),
  `DueGradeSK`/`InvoiceGradeSK` (น่าจะ role-play ของ dim_grade)
- ไม่มี Dataform assertions เลย — ถ้าจะเพิ่ม data-quality checks ต้องเริ่มจากศูนย์
- Slack run-monitor (cloud-run-monitor/ + BQ `monitor_dataset`) — ยังไม่ deploy ขึ้น GCP
- Tag ที่ประกาศแต่ไม่ใช้: `dimension_monthly`, `fact_monthly`, `fact_yearly`,
  `curated_full`, `curated_incremental`, `onetime`
