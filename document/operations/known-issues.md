# Known Issues & Gotchas

รวมจุดที่รู้แล้วว่า "เป็นแบบนี้โดยตั้งใจ" หรือ "ต้องระวัง" — อัปเดตล่าสุด 2026-07-24

## คำสะกดผิดที่เป็น identifier จริง (ห้ามแก้)

| ที่ | คำ | หมายเหตุ |
|---|---|---|
| `definitions/fact/fact_transcation.sqlx` | `fact_transcation` | ชื่อไฟล์ + ตารางจริงใน BigQuery |
| `includes/controller/variables.json` | `CDC_DATESET` | คีย์ constant (ค่า `cdc_dataset` ถูกต้อง) |
| MASTERSKU JSON | `prdDiminsionData`, `SpeciFeild`, `dimFeild` | field จริงในข้อมูล |
| `FactOrderSk` vs `FactOrderSK` | casing ไม่คงที่ในไฟล์เดียวกัน | ใช้ตามที่ไฟล์นั้นใช้ |

## พฤติกรรมที่ตั้งใจ (อย่า "แก้")

- **mds dims 34 ตัวเป็น full daily rebuild** (ตัดสินใจ 2026-07-20): แปลงจาก MERGE
  เป็น `type: "table"` ปั้นใหม่ทุกวันจาก `is_active = TRUE` — **SK ออกเลขใหม่ทุกวัน
  ห้าม persist SK พวกนี้ข้ามวัน** เหตุผล: mds มี overwrite import mode (ล้างแล้วลง
  ใหม่ id ใหม่หมด) ซึ่ง MERGE pattern รับมือไม่ครบ (zombie rows) ตรวจ consumer ครบ
  ทุกตัวแล้ว (repo + BQ + query history 90 วัน): ทุก consumer re-derive รายวัน
  ยกเว้นที่ยกเว้นไว้ ดู `project_wiki/dimension/full-rebuild-pattern.md`
  - **ยกเว้น 2 ตัวที่ยังเป็น MERGE + tombstone**: `dim_company` (CompanySK ฝังถาวรใน
    dims/facts ทั้งระบบ) และ `dim_aging_rang` (AgingRangSK freeze ใน dim_aging_history)
  - **เงื่อนไขปิดแล้ว (2026-07-20)**: `fact_mir_vs`/`fact_mir_rs` (+ `fact_chq`)
    ถูกย้ายเข้า repo เป็น `type: "table"` tag `fact_daily` (rebuild เต็มทุกคืน หลัง
    dims) — `dim_collection_status` rebuild ได้อย่างปลอดภัยแล้ว
- **Hard delete tombstone ใน mds MERGE dims** (ตัดสินใจ 2026-07-10 — ปัจจุบันเหลือ
  ใช้กับ dim_company + dim_aging_rang เท่านั้น): row ที่ mds `is_active = FALSE`
  ถูกลบจริงจาก dim โดยไม่เช็ก FK ปลายทาง; DELETE ไม่มี date filter (ตั้งใจ)
- **`dim_doctype` / `dim_holiday` ไม่มี SK** — โค้ด SK ถูก comment ไว้ MERGE ด้วย
  natural key แทน
- **`dim_stk_mkt` มี row 'Waiting Master'** (`MdsID = NULL`, MarketingGroupID='999') —
  placeholder สำหรับ stkcode ที่ยังไม่มี master ปลอดภัยจาก DELETE เพราะ
  `IN (subquery)` ไม่ match NULL
- **`curated_tbook_quotation`** — partition + incremental filter ถูก comment ไว้
  จึงทำงานเหมือน full rebuild แม้ประกาศ `type: "incremental"`
- **`mir.sqlx`** — `type: "incremental"` แต่ tag `validated_full` (จัดกลุ่ม operator)
- **saleout_mdt** — ไม่มี sub-tag และส่วนใหญ่ไม่ partition
- **View layer เข้า Dataform** (ตัดสินใจ + ทำ 2026-07-24): เดิม BigQuery views ถูก
  สร้าง/แก้ **นอก Dataform** ตรงใน console จึงไม่อยู่ใน repo และไม่มี lineage — ย้ายมา
  เป็น `type: "view"` ใต้ `definitions/view/` (แยก subfolder ตาม dataset ปลายทาง)
  แล้ว **42 ไฟล์** โดย **`config.schema` คงชี้ dataset เดิม** (`dimension_view`,
  `fact_view`, `onetime`, `process_dataset`, `bridge_dataset`) เพื่อไม่ให้
  Power BI/consumer พัง และแทน project literal `databuffet-nonprd` ด้วย
  `${databuffet.DATABASE}` (portable ข้าม env) — inventory เต็ม: `project_wiki/view/view-layer.md`
  - ขอบเขต: 42 ตัว **ตัด 12** (test 5: `TEST_Data_Transaction`×2 + `temp_dim.*`×3;
    `peem_using` ทั้ง dataset 7 ตัว: `view_1..4_Product_DOS_CAT1*` + RLS trio
    `view_rls_data`/`sale`/`special` — เป็น **test copy ส่วนตัวของเจ้าของ** ของ RLS views
    ใน `process_dataset` จงใจไม่เอาเข้า Dataform)
  - เพิ่ม constant: `TAG_VIEW`=`view`, `BRIDGE`=`bridge_dataset` (ไม่มี `PEEM_USING`)
  - `dependencies[]` ใส่เฉพาะ action จริง (basename ที่ unique) — external/UDF/ตารางที่
    ไม่มี .sqlx (`dim_districts/provinces/geographies/sub_districts`, `dim_aging_history`,
    `dim_product_rebate`, `mih_address_data`, `RLS_Customer360`, `mds_*`) อ้างด้วย
    interpolation แต่ไม่ list เป็น dep (ตารางมีอยู่แล้ว)
  - ⚠️ ยังไม่ได้ compile-verify (เครื่องนี้ไม่มี dataform CLI) — ต้องเช็คตอนขึ้น service:
    (1) view ที่อ้าง view อื่น (chain เช่น `view_dim_aging`→`view_dim_channel`,
    `Model_Invoice_Transaction`→`view_fact_transcation`) resolve เรียงลำดับถูก
    (2) `fact_transcation.sqlx` อ่าน `onetime.Transaction_Data_Mart` และ
    `dimension_view.view_dim_channel` แต่ไม่ได้ประกาศ dep ฝั่ง fact (จงใจไม่แตะไฟล์
    pipeline เดิม) — pipeline ยังถูกเพราะ view เป็น logical + มีอยู่ก่อน; follow-up ควรเติม
    dep ฝั่ง fact ให้ DAG ครบ (3) ownership เปลี่ยนมือ — Dataform จะ `CREATE OR REPLACE`
    ทับทุกครั้งที่รัน ใครแก้ใน console จะโดนเขียนทับ
  - **Format การอ้างอิงตาราง = กฎ 2 ชั้น** (แก้ 2026-07-24 ตาม feedback 2 รอบ):
    (ก) `validated_*`/`curated_*` → `${ref(databuffet.<CONST>, "tbl")}` ไม่ครอบ backtick
    และ **ห้ามใส่ใน `dependencies[]`** (Dataform ผูกให้เอง — §10)
    (ข) ที่เหลือ (dim/fact, view อื่น, process, mds, onetime base, UDF, external) →
    js-block `<Pascal>Table`/`<Pascal>TableRef` อ้างด้วย `` `${XxxTableRef}` ``
    ห้าม inline `${databuffet.DATABASE}...` ใน body; view ที่อ่านแต่ validated/curated
    จะ**ไม่มี js block** เลย (เช่น `Dimension_Quotation`)
    ประวัติ: รอบแรก generate เป็น inline (ผิด §3) → รอบสองแก้เป็น js-block ทั้งหมด
    (ยัง**ผิด** เพราะ validated/curated ต้องเป็น `ref()`) → รอบสามได้ตามนี้
    ยืนยันทุกรอบ: เนื้อ SQL ไม่เปลี่ยน 42/42 เทียบกับ BigQuery
- **ไฟล์เก่ายังมี inline reference (tech debt)**: `fact_transcation.sqlx` ใช้ js-block Ref
  กับ dims และ `${ref(...)}` กับ validated ถูกแล้ว แต่ยัง inline
  `${databuffet.DATABASE}.onetime.Transaction_Data_Mart` (ควรเป็น js-block Ref ตาม §3.2)
  — ของใหม่ยึดกฎ 2 ชั้น ของเก่าค่อยแปลงเมื่อแตะไฟล์นั้น

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
