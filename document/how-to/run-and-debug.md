# How-to: รันและ Debug

## รันด้วย tag

```bash
dataform compile                      # ตรวจ syntax + graph (ไม่รันจริง)
dataform run --dry-run                # ดูแผนก่อนรัน
dataform run --tags validated_incremental
dataform run --tags dimension_daily
dataform run --tags fact_daily
dataform run --actions validated_mac5.mih          # รันตัวเดียว
dataform run --actions validated_mac5.mih --include-deps
```

Tag ที่ใช้จริง: `initial`, `re-initial` (⚠️ DROP ตาราง), `validated`,
`validated_full`, `validated_incremental`, `curated`, `dimension_daily`,
`dimension_yearly` (dim_calendar), `fact_daily`, `cdc`, `cdc_incremental`, `process`
(ไม่มี tag `assertions` — โปรเจกต์ยังไม่มี assertion)

> เครื่อง local WSL ปัจจุบัน**ไม่มี dataform CLI** — compile/run ผ่าน Dataform UI
> บน GCP หรือเครื่องที่ติดตั้งแล้ว

## Query ตรงด้วย bq

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false '
SELECT COUNT(*) FROM `databuffet-nonprd.dimension_table.dim_company`'
```

- ต้องใส่ `--project_id=databuffet-nonprd` เสมอ (default project ของเครื่องเป็นตัวอื่น)
- INFORMATION_SCHEMA ระดับ region โดน deny — ใช้ระดับ dataset:
  `` `databuffet-nonprd.<dataset>.INFORMATION_SCHEMA.COLUMNS` ``

## ลำดับการไล่ปัญหา

1. `dataform compile` ผ่านไหม (syntax / dependency ผิด)
2. `dataform compile --json | jq ...` ดู graph ว่า action ต่อกันถูกไหม
3. dry-run action ที่สงสัย
4. ดู error ใน BigQuery Cloud Console (job history)
5. เช็ก `uniqueKey`/`pk_key` ตรงกันไหม (validated)

## อาการที่เจอบ่อย

| อาการ | สาเหตุ/ทางแก้ |
|---|---|
| dim MERGE บอก table not found | ตาราง operations ต้องสร้างใน BigQuery ก่อนรันครั้งแรก |
| dim ไม่เห็นข้อมูล mds ที่แก้ไปแล้ว | เกิน window `MDS_BACKFILL_DAYS` (1 วัน) — backfill ด้วย var ใหญ่ขึ้น |
| validated ขาดข้อมูลย้อนหลัง | window incremental = 1 วัน (string compare ASATDATE) — full refresh ตารางนั้น |
| parse datetime fail | รูปแบบ timestamp จาก raw เปลี่ยน — `parseFlexibleDatetime` รองรับ 2 แบบ ถ้ามีแบบที่ 3 ต้องเพิ่ม |
| ALTER PRIMARY KEY fail ซ้ำ ๆ | BigQuery metadata ชนกัน — retry loop จัดการเอง ถ้ายัง fail ให้รันใหม่ |
| fact row ซ้ำ | grain ของ temp table ไม่ตรง DELETE key |
| SK ค้างใน fact หลัง mds ลบ | พฤติกรรมที่ยอมรับ (hard delete 2026-07-10) — dim full-rebuild จะหายเองวันถัดไป |

## Environment / Git

- Branch: `dev` → `nonprod` → `prod` (+ `hotfix`)
- `workflow_settings.yaml` ต่างกันต่อ environment — อย่า commit ค่า env อื่นทับ
- Slack run-monitor (cloud-run-monitor/) อยู่ระหว่าง deploy — ดูสถานะใน memory ทีม
