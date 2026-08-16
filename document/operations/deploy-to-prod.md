# Deploy to prod — ทำทีละ step บน Console

ทำตามลำดับ 1 → 30 ห้ามข้าม ห้ามสลับ
ทุก step บอก **ไปที่ไหน → กดอะไร → ต้องเห็นอะไร → ถ้าไม่ตรงทำยังไง**

เป้าหมาย: `databuffet-nonprd` (us-central1) → `databuffet-prd` (asia-southeast1)
ให้เหมือนกัน แล้ว prd เดินเอง

- **Step 1–12** ทำล่วงหน้าได้ ไม่กระทบใคร
- **Step 13–26** คืน cutover เริ่มประมาณ 20:00 น. (nonprd รันรอบเดียว 06:00 ข้อมูลนิ่งแล้ว)
- **Step 27–30** เช้าถัดไป

> ⚠️ ทุกหน้าของ Console มี **ตัวเลือก project มุมบนซ้าย** และบางหน้ามี **ตัวเลือก region**
> ผิด project หรือผิด region = ทำผิดที่ทั้ง step เช็กทุกครั้งก่อนกด

ลิงก์ที่ใช้บ่อย:

| บริการ | ลิงก์ |
|---|---|
| BigQuery Studio (prd) | https://console.cloud.google.com/bigquery?project=databuffet-prd |
| BigQuery Data transfers (prd) | https://console.cloud.google.com/bigquery/transfers?project=databuffet-prd |
| Dataform (prd) | https://console.cloud.google.com/bigquery/dataform?project=databuffet-prd |
| Storage Transfer (nonprd) | https://console.cloud.google.com/transfer/jobs?project=databuffet-nonprd |
| Cloud Storage buckets | https://console.cloud.google.com/storage/browser?project=databuffet-prd |
| APIs & Services (prd) | https://console.cloud.google.com/apis/library?project=databuffet-prd |
| IAM (prd) | https://console.cloud.google.com/iam-admin/iam?project=databuffet-prd |
| Cloud Run (prd) | https://console.cloud.google.com/run?project=databuffet-prd |
| Cloud Scheduler (prd) | https://console.cloud.google.com/cloudscheduler?project=databuffet-prd |
| GitHub repo | https://github.com/ALL-IN-AI-ASIA/data-buffet |

---

## Step 1 — merge `dev` → `nonprod` (GitHub)

**ไปที่**: https://github.com/ALL-IN-AI-ASIA/data-buffet

**ทำ**:
1. กด **Pull requests** → **New pull request**
2. base = `nonprod` · compare = `dev`
3. **Create pull request** → **Merge pull request**

**ต้องเห็น**: merge ผ่าน ไม่มี conflict

---

## Step 2 — merge `nonprod` → `prod` (GitHub)

**ทำ**:
1. **New pull request** → base = `prod` · compare = `nonprod`
2. จะเห็นว่า **prod ตามหลังอยู่ 197 commits** — ถูกต้องแล้ว
3. **Create pull request** → จะขึ้น conflict ที่ **`workflow_settings.yaml`**
4. กด **Resolve conflicts** แล้วแก้ไฟล์ให้เหลือ **ของฝั่ง prod** เท่านั้น:

```yaml
defaultProject: databuffet-prd
defaultLocation: asia-southeast1
defaultDataset: dataform
defaultAssertionDataset: dataform_assertions
dataformCoreVersion: 3.0.0
vars:
    RAW_BUCKET: "gs://file-raw-data-prd"
    MDS_BACKFILL_DAYS: "1"
    BACKFILL_DAYS: "1"
```

5. **Mark as resolved** → **Commit merge** → **Merge pull request**

**ต้องเห็น**: ไฟล์อื่นทั้งหมดเหมือน `dev` เหลือแค่ `workflow_settings.yaml` ที่ต่าง

**ทำไมต้อง merge**: prod ยังไม่มี `functionData` ใน `includes/databuffet.js`
ถ้าไม่ merge ทุกไฟล์ validated/curated จะ compile ไม่ผ่านเลย

---

## Step 3 — ตรวจว่า Dataform ของ prd compile ผ่าน

**ไปที่**: Dataform → https://console.cloud.google.com/bigquery/dataform?project=databuffet-prd

**ทำ**:
1. เลือก **region = `asia-southeast1`** (ด้านบนของหน้า)
2. เปิด repository **`data-buffet`**
3. แท็บ **RELEASE CONFIGURATIONS** (หรือ RELEASES AND SCHEDULING) → คลิก **`production`**
4. กด **CREATE COMPILATION RESULT** (ถ้าไม่อยากรอ cron 05:45)

**ต้องเห็น**:
- Git commitish = `prod`, สถานะ compile = **สำเร็จ ไม่มี error**
- ในรายละเอียดของ compilation result → `Variables` ต้องมี `BACKFILL_DAYS`, `MDS_BACKFILL_DAYS`,
  `RAW_BUCKET = gs://file-raw-data-prd`

**ถ้าไม่ตรง**: ถ้ายังเป็น commit เก่า = release ยังไม่หยิบ commit ใหม่ ให้กดสร้างใหม่อีกครั้ง
ถ้ามี compile error = Step 2 merge ไม่ครบ กลับไปดูว่า `includes/` มาครบไหม

---

## Step 4 — เปิด API ที่ยังขาดใน prd

**ไปที่**: https://console.cloud.google.com/apis/library?project=databuffet-prd

**ทำ**: ค้นหาแล้วกด **ENABLE** ทีละตัว

| API | สถานะปัจจุบัน |
|---|---|
| Cloud Scheduler API | ❗ **ยังไม่เปิด — ต้องเปิด** |
| Storage Transfer API (ที่ project **nonprd**) | ❗ **ยังไม่เปิด — ต้องเปิด** |
| Dataform / BigQuery / BigQuery Data Transfer / Vertex AI / Cloud Storage / Cloud Run | เปิดแล้ว |

> Storage Transfer API เปิดที่ **`databuffet-nonprd`** ไม่ใช่ prd — ดูเหตุผลใน Step 7

---

## Step 5 — สร้าง dataset ที่ยังขาดใน prd

**ไปที่**: BigQuery Studio → https://console.cloud.google.com/bigquery?project=databuffet-prd

**ทำ**: ที่ชื่อ project `databuffet-prd` ในแถบซ้าย กด **⋮ → Create dataset** ทีละตัว
ทุกตัวตั้ง **Location type = Region → `asia-southeast1`**

dataset ที่ยังไม่มี (ตรวจเมื่อ 2026-08-13):

| Dataset ID | ใช้ทำอะไร |
|---|---|
| `raw_mac5_ag01` | external table ของ ag01 |
| `raw_mac5_aa05` | external table ของ aa05 |
| `raw_mac5_ab01` | external table ของ ab01 |
| `raw_mac5_ac02` | external table ของ ac02 |
| `raw_mac5_ak02` | external table ของ ak02 |
| `raw_saleout_mdt` | external table ของ saleout |
| `validated_saleout_mdt` | validated ของ saleout |
| `bridge_dataset` | view `GroupCustomerSK_CustomerSK` |
| `monitor_dataset` | ตาราง run telemetry |

**ต้องเห็น**: ในแถบซ้ายมี dataset ครบ 25 ตัว

**ถ้าไม่ตรง**: กดที่ dataset แล้วดู **Data location** ต้องเป็น `asia-southeast1`
ถ้าเผลอสร้างเป็น `us-central1` ต้องลบแล้วสร้างใหม่ (ย้าย location ไม่ได้)

> ทำเองที่ step นี้เพราะไฟล์ `definitions/initial/create_all_schema.sqlx` ตั้ง `tags: []`
> และไม่มีใคร `dependencies` ถึง → ไม่ถูกรันโดย tag ใดเลย

---

## Step 6 — ตรวจสิทธิ์ service account ของ prd

**ไปที่**: https://console.cloud.google.com/iam-admin/iam?project=databuffet-prd

**ทำ**: ค้นหา `dbuffet-dataform-prd@databuffet-prd.iam.gserviceaccount.com`

**ต้องเห็น** อย่างน้อย 2 role นี้:
- `BigQuery Admin`
- `Storage Admin`

**ถ้าไม่ตรง**: กด **GRANT ACCESS** เพิ่มให้ก่อน — ถ้าไม่มี Storage Admin
Step 15 (`initial`) จะสร้าง external table ได้แต่ **อ่านไฟล์ใน GCS ไม่ได้** พังทั้งสาย

---

## Step 7 — สร้าง Storage Transfer job (copy ไฟล์ AVRO เข้า prd)

**ไปที่**: Storage Transfer ที่ project **`databuffet-nonprd`** →
https://console.cloud.google.com/transfer/jobs?project=databuffet-nonprd

> สร้างที่ **nonprd** เพราะ service agent ของ nonprd
> (`project-164028798508@storage-transfer-service...`) มีสิทธิ์อ่าน `file-raw-data` และ
> เขียน `file-raw-data-prd` อยู่แล้วทั้งสองฝั่ง ถ้าสร้างที่ prd ต้องไปเพิ่มสิทธิ์ใหม่

**ทำ**:
1. **CREATE TRANSFER JOB**
2. **Source type** = `Google Cloud Storage` · **Destination type** = `Google Cloud Storage`
3. **Source bucket** = `file-raw-data`
4. **Destination bucket** = `file-raw-data-prd`
5. หน้า **Choose settings**:
   - **Description**: `raw-to-prd-initial`
   - **When to overwrite**: `Overwrite if different`
   - **When to delete**: **`Never`** ← รอบนี้ยังไม่ลบอะไร
6. หน้า **Scheduling options**: `Run once` → `Starting now`
7. **CREATE**

**ต้องเห็น**: job สถานะ Running แล้วจบเป็น **Succeeded**
(ก้อนนี้ใหญ่ ปล่อยให้วิ่งข้ามคืนได้ — ทำล่วงหน้าหลายวันก่อน cutover ได้เลย)

**ถ้าไม่ตรง**: ถ้า error สิทธิ์ ให้ไปดู bucket `file-raw-data-prd` → **PERMISSIONS**
ว่ามี `project-164028798508@storage-transfer-service.iam.gserviceaccount.com`
เป็น `Storage Object Admin` อยู่ไหม

---

## Step 8 — ตรวจว่าไฟล์เข้าครบ

**ไปที่**: https://console.cloud.google.com/storage/browser?project=databuffet-prd
→ เปิด `file-raw-data-prd`

**ต้องเห็น**: โฟลเดอร์ครบ 10 ตัว — `mac5_ag01`, `mac5_aa05`, `mac5_ab01`, `mac5_ac02`,
`mac5_ak02`, `mac5_report`, `mac5_gps`, `mastersku`, `cis360`, **`saleout_mdt`**
(เดิม prd **ไม่มี** `saleout_mdt` เลย ต้องโผล่มาหลัง Step 7)

เปิด `mac5_ag01/mih/` แล้วเลื่อนลงล่างสุด

**ต้องเห็น**: มีโฟลเดอร์ `ASATDATE=` ถึงวันล่าสุด (เช่น `ASATDATE=20260812`)
และยังมีของเก่ายุค `ASATDATE=20251224` ถึง `20260316` ค้างอยู่ — **ปกติ ณ ตอนนี้**
(Step 14 จะลบให้)

---

## Step 9 — สร้าง Data Transfer สำหรับ copy dataset (ยังไม่รัน)

**ไปที่**: BigQuery Data transfers ที่ **prd** →
https://console.cloud.google.com/bigquery/transfers?project=databuffet-prd
เลือก **region = `asia-southeast1`**

**ต้องเห็นก่อน**: มี transfer อยู่แล้ว 4 ตัว —
`dimension_table_from_nonprd`, `fact_table`, `process_dataset`, `mds_dataset_from_nonprd`
(ของเก่าจาก 17 มี.ค. ใช้ซ้ำได้ ไม่ต้องสร้างใหม่)

**ทำ**: กด **CREATE TRANSFER** เพิ่มอีก 9 ตัว ตามตารางนี้ ทุกตัวตั้งเหมือนกันหมด:

- **Source** = `Dataset Copy`
- **Repeat frequency** = `On-demand`  ← สำคัญ ห้ามตั้งเป็น Daily
- **Destination dataset** = ชื่อเดียวกับ Source dataset
- **Source project** = `databuffet-nonprd`
- ติ๊ก **Overwrite destination table**

| Transfer name | Source dataset |
|---|---|
| `validated_mac5_from_nonprd` | `validated_mac5` |
| `validated_cis360_from_nonprd` | `validated_cis360` |
| `validated_mastersku_from_nonprd` | `validated_mastersku` |
| `validated_saleout_mdt_from_nonprd` | `validated_saleout_mdt` |
| `curated_mac5_from_nonprd` | `curated_mac5` |
| `curated_mastersku_from_nonprd` | `curated_mastersku` |
| `onetime_from_nonprd` | `onetime` |
| `cdc_dataset_from_nonprd` | `cdc_dataset` |
| `monitor_dataset_from_nonprd` | `monitor_dataset` |

**ต้องเห็น**: หน้า Data transfers มีทั้งหมด **13 รายการ** สถานะยังไม่เคยรัน

**ที่ไม่ต้องสร้างและเหตุผล**:

| Dataset | ทำไมไม่ copy |
|---|---|
| `raw_*` | เป็น external table — Step 15 (`initial`) สร้างใหม่ให้ชี้ bucket ของ prd |
| `function_dataset` | เป็น routine/UDF — Data Transfer copy ไม่ได้ Step 15 สร้างให้ |
| `dimension_view`, `fact_view`, `bridge_dataset` | เป็น view ล้วน — Step 18 (tag `view`) สร้างให้ |
| `curated_cis360` | ว่างเปล่าใน nonprd |
| `peem_using`, `temp_dim` | ตกลงกันแล้วว่าไม่ยกไป |

---

## Step 10 — ตรวจสิทธิ์: อะไรที่ต้องตามไปทำที่ prd

**สำรวจให้แล้วเมื่อ 2026-08-13** — ผลออกมาง่ายกว่าที่คิด:

| เรื่อง | ผลสำรวจ nonprd | ต้องทำที่ prd ไหม |
|---|---|---|
| Row access policy | **ไม่มีเลยสักตาราง** ทั้งโปรเจกต์ | ❌ ไม่ต้องทำ |
| Authorized view | **ไม่มีเลย** | ❌ ไม่ต้องทำ |
| Dataset ACL | มีแค่ WRITER ให้ Dataform service agent (`curated_*`, `validated_*`) และ OWNER ให้ compute SA (`mds_dataset`) — เป็นของที่ระบบใส่เอง | ❌ prd สร้างของตัวเองอัตโนมัติ |
| **สิทธิ์ระดับ project (IAM)** | **นี่คือที่เดียวที่คุมสิทธิ์จริง** | ✅ **ต้องทำ — ดู Step 24** |

**ไปที่** (ถ้าอยากยืนยันด้วยตาเอง): BigQuery Studio (nonprd) → คลิก dataset ใดก็ได้ →
**SHARING → Permissions** จะเห็นแค่ project-level role ปกติ ไม่มี principal แปลกปลอม

**สรุป**: งานด้านสิทธิ์ทั้งหมดยุบเหลือ **step เดียวคือ Step 24** (เพิ่ม IAM ให้ผู้ใช้)

---

## Step 11 — deploy `mds-app` ไป prd

**ไปที่**: Cloud Run → https://console.cloud.google.com/run?project=databuffet-prd

**ทำ**: deploy service `mds-app` (image เดียวกับที่ nonprd ใช้) แล้วตั้ง env/secret
ให้เขียนไปที่ `databuffet-prd.mds_dataset`

**ต้องเห็น**: มี service `mds-app` ใน prd (ตอนนี้ prd **ไม่มี Cloud Run เลยสักตัว**)
ยัง**ไม่ต้อง**ต่อ Scheduler (ทำที่ Step 26)

---

## Step 12 — deploy ชุด alert ไป prd

**ไปที่**: Cloud Run + Cloud Scheduler ของ prd

**ทำ**: deploy `alert-dataform` และ `alert-ms-team` (จาก scaffold `cloud-run-monitor/`)
แล้วสร้าง Scheduler job 07:00 Asia/Bangkok แต่ **สร้างแบบ Paused ไว้ก่อน**

**ต้องเห็น**: มี 2 service + 1 scheduler job (paused)

---

# คืน cutover — เริ่มประมาณ 20:00 น.

## Step 13 — Storage Transfer รอบ delta

**ไปที่**: https://console.cloud.google.com/transfer/jobs?project=databuffet-nonprd

**ทำ**: เปิด job `raw-to-prd-initial` (จาก Step 7) → **RUN NOW**

**ต้องเห็น**: Succeeded — รอบนี้จะเร็วเพราะ copy แค่ไฟล์ที่เพิ่มมาใหม่

---

## Step 14 — ⚠️ Storage Transfer รอบ mirror (ลบของเก่าใน prd)

**ห้ามข้าม step นี้** ถ้าข้าม row count ของ prd จะไม่มีทางเท่า nonprd

**เหตุผล**: validated ของ mac5 **73 ตารางเป็น full rebuild ทุกคืน** — มัน scan external table
**ทุกพาร์ทิชัน** แล้วค่อยเลือกแถวล่าสุดต่อ PK
หน้าต่างพาร์ทิชันสองฝั่งตอนนี้**ไม่ทับกันเลยแม้แต่วันเดียว**:

| | nonprd | prd |
|---|---|---|
| `mac5_ag01/mih` | 89 พาร์ทิชัน `20260511..20260812` | 78 พาร์ทิชัน `20251224..20260316` |
| `mac5_ag01/mil` | 93 พาร์ทิชัน | **114 พาร์ทิชัน** (มากกว่า) |

ถ้าปล่อยของเก่าไว้ prd จะมี 167 พาร์ทิชัน → **แถวของลูกค้า/เอกสารที่ถูกลบไปแล้วจะฟื้นกลับมา**
และตารางแบบ full dump (`deb`, `dep`) ยิ่งหนัก เพราะ external table อ่านแบบ `deb/*.avro`
= อ่านทั้งไฟล์เก่าและใหม่พร้อมกัน

**ทำ**:
1. **CREATE TRANSFER JOB** ใหม่ (หรือแก้ job เดิมก็ได้ แต่แนะนำสร้างใหม่จะได้ย้อนดูได้)
2. Source `file-raw-data` → Destination `file-raw-data-prd`
3. หน้า **Choose settings**:
   - **Description**: `raw-to-prd-mirror`
   - **When to overwrite**: `Overwrite if different`
   - **When to delete**: **`Delete files from destination if they're not also at source`** ← จุดสำคัญ
4. **Run once → Starting now**

**ต้องเห็น**: Succeeded และในหน้า job มีตัวเลข **Objects deleted** มากกว่า 0

---

## Step 15 — ตรวจว่าพาร์ทิชันตรงกันแล้ว

**ไปที่**: Cloud Storage ทั้งสอง bucket

**ทำ**: เปิด `file-raw-data/mac5_ag01/mih/` กับ `file-raw-data-prd/mac5_ag01/mih/`
เทียบ **โฟลเดอร์แรกสุดและท้ายสุด**

**ต้องเห็น**: ช่วงวันเท่ากันทั้งสองฝั่ง และของเก่ายุค `20251224..20260316` **หายไปแล้ว**

**ถ้าไม่ตรง**: กลับไป Step 13–14 ห้ามไปต่อ

---

## Step 16 — รัน tag `initial` ใน Dataform

⚠️ **step นี้ต้องมาก่อน Step 17 เสมอ** เพราะไฟล์
`drop_all_tables_validated_cis360` / `_mastersku` / `_saleout_mdt` ติด tag `initial` เอง
= มันจะ **ลบตาราง validated 45 ตาราง** ถ้าไปรันหลัง copy ข้อมูลจะหายทันที

**ไปที่**: Dataform → repository `data-buffet` (region `asia-southeast1`)

**ทำ**:
1. แท็บ **DEVELOPMENT WORKSPACES** → **CREATE DEVELOPMENT WORKSPACE** ตั้งชื่อ `cutover`
2. เปิด workspace แล้วกด **PULL** เพื่อดึงโค้ดล่าสุดของ branch `prod`
3. กด **START EXECUTION** → เลือก **Tags**
4. ในกล่อง execute:
   - เลือก tag **`initial`**
   - **ห้ามติ๊ก** `Include dependencies`
   - **ห้ามติ๊ก** `Include dependents`
   - **ห้ามติ๊ก** `Run with full refresh`
   - **Service account** = `dbuffet-dataform-prd@databuffet-prd.iam.gserviceaccount.com`
5. **START EXECUTION**
6. ดูผลที่แท็บ **WORKFLOW EXECUTION LOGS**

**ต้องเห็น**: สถานะ **Succeeded** ทุก action

**ถ้าไม่ตรง**: คลิก action ที่ Failed อ่าน error
- ถ้าเป็นสิทธิ์อ่าน GCS → กลับ Step 6
- ถ้าเป็น dataset not found → กลับ Step 5

> **ห้ามติ๊ก `Include dependencies` เด็ดขาด** — `create_all_table_raw_mac5*` มี dependency
> เป็น `drop_all_tables_validated_mac5` + `drop_all_tables_curated_mac5` (tag `re-initial`)
> ถ้าลากมาด้วยจะลบ `validated_mac5` 86 ตาราง + `curated_mac5` ทิ้งทั้งชุด
>
> **และห้ามรัน tag `re-initial`** ตลอดทั้งกระบวนการ

### ตรวจผลของ `initial`

**ไปที่**: BigQuery Studio (prd) → `function_dataset`

**ต้องเห็น**: มี routine ครบ **7 ตัว** — `EXTRACT_CHQ_DATA`, `clean_company_prefix`,
`fn_flag_exc`, `fn_flag_sales_kpi`, `fn_flag_scg`, `fn_get_scg_customer_ids`, `fn_order_type`
(ก่อนหน้านี้ prd มีแค่ 3 ตัว และ `fn_flag_scg` พังเพราะเรียก `fn_get_scg_customer_ids` ที่ไม่มี)

แล้วรัน SQL นี้ใน editor ของ prd:

```sql
SELECT MIN(ASATDATE) AS first_partition,
       MAX(ASATDATE) AS latest_partition,
       COUNT(DISTINCT ASATDATE) AS n_partitions
FROM `databuffet-prd.raw_mac5_ag01.mih`;
```

**ต้องเห็น**: อ่านได้ ไม่ error และช่วงวันตรงกับที่เห็นใน Step 15

---

## Step 17 — สั่งรัน Data Transfer ทั้ง 13 ตัว

**ไปที่**: https://console.cloud.google.com/bigquery/transfers?project=databuffet-prd
(region `asia-southeast1`)

**ทำ**: เปิดทีละ transfer → **RUN TRANSFER NOW** (หรือ **SCHEDULE BACKFILL → Run one time
transfer → now**) ทำให้ครบทั้ง 13 ตัว

**ต้องเห็น**: ทุกตัวจบเป็น **Succeeded** (ดูที่คอลัมน์ Run history)

**ถ้าไม่ตรง**: คลิกที่ run ที่ Failed → อ่าน Error message
เจอบ่อย: destination dataset ไม่มี (กลับ Step 5) หรือ region ไม่ตรง

### ตรวจจำนวนตาราง

รัน SQL นี้ที่ **nonprd** แล้วรันอีกครั้งที่ **prd** (เปลี่ยนชื่อ project) แล้วเทียบตัวเลข

```sql
SELECT 'validated_mac5' ds, COUNT(*) n FROM `databuffet-nonprd.validated_mac5.__TABLES__`
UNION ALL SELECT 'validated_cis360', COUNT(*) FROM `databuffet-nonprd.validated_cis360.__TABLES__`
UNION ALL SELECT 'validated_mastersku', COUNT(*) FROM `databuffet-nonprd.validated_mastersku.__TABLES__`
UNION ALL SELECT 'validated_saleout_mdt', COUNT(*) FROM `databuffet-nonprd.validated_saleout_mdt.__TABLES__`
UNION ALL SELECT 'curated_mac5', COUNT(*) FROM `databuffet-nonprd.curated_mac5.__TABLES__`
UNION ALL SELECT 'curated_mastersku', COUNT(*) FROM `databuffet-nonprd.curated_mastersku.__TABLES__`
UNION ALL SELECT 'dimension_table', COUNT(*) FROM `databuffet-nonprd.dimension_table.__TABLES__`
UNION ALL SELECT 'fact_table', COUNT(*) FROM `databuffet-nonprd.fact_table.__TABLES__`
UNION ALL SELECT 'onetime', COUNT(*) FROM `databuffet-nonprd.onetime.__TABLES__`
UNION ALL SELECT 'process_dataset', COUNT(*) FROM `databuffet-nonprd.process_dataset.__TABLES__`
UNION ALL SELECT 'mds_dataset', COUNT(*) FROM `databuffet-nonprd.mds_dataset.__TABLES__`
UNION ALL SELECT 'cdc_dataset', COUNT(*) FROM `databuffet-nonprd.cdc_dataset.__TABLES__`
ORDER BY ds;
```

**ต้องเห็น**: ตัวเลขเท่ากันทุกบรรทัด (prd อาจมากกว่าได้ใน `onetime` ถ้ามี view ค้าง —
Step 18 จะจัดการ)

> ทำไมต้องรัน 2 รอบ: nonprd อยู่ US, prd อยู่ asia-southeast1 — BigQuery **query ข้าม region
> ไม่ได้** จึงเทียบด้วยตาเท่านั้น

---

## Step 18 — ⚠️ ลบ view ที่ copy ติดมา

**เหตุผล**: Data Transfer พา view มาด้วย แต่ใน view definition ยังเขียนว่า
`databuffet-nonprd.…` → prd จะวิ่งกลับไปอ่านข้อมูลของ nonprd ต้องลบทิ้งให้ Step 19 สร้างใหม่

**ไปที่**: BigQuery Studio (prd) → SQL editor

```sql
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Cheque`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Customer`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Delivery`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Invoice`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Order`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Project`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Dimension_Quotation`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Model_Invoice_Transaction`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Model_Target_DayOfWork`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.PowerBI_Data_Buffet_Transaction`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Product_Attribute`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Product_Master`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Product_Master_ALL`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Sales_Per_Non_Master`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.Transaction_Data_Mart`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.View_Product`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.TEST_Data_Transaction`;
DROP VIEW IF EXISTS `databuffet-prd.onetime.TEST_Data_Transaction_2`;
DROP VIEW IF EXISTS `databuffet-prd.process_dataset.view_deb_address_data`;
DROP VIEW IF EXISTS `databuffet-prd.process_dataset.view_mih_address_data`;
DROP VIEW IF EXISTS `databuffet-prd.process_dataset.view_rls_data`;
DROP VIEW IF EXISTS `databuffet-prd.process_dataset.view_rls_sale_data`;
DROP VIEW IF EXISTS `databuffet-prd.process_dataset.view_rls_special_data`;
```

**ต้องเห็น**: รันผ่านหมด (`DROP VIEW` ไม่แตะตาราง ถ้าชื่อนั้นเป็นตารางจะ error แล้วหยุด —
ถ้าเจอให้ข้ามบรรทัดนั้นไป)

`TEST_Data_Transaction` / `_2` ลบแล้วจะไม่ถูกสร้างกลับ — ตั้งใจ (เป็น view ทดสอบ ไม่อยู่ใน repo)

---

## Step 19 — รัน tag `view`

**ไปที่**: Dataform workspace `cutover` → **START EXECUTION → Tags**

**ทำ**: เลือก tag **`view`** · ไม่ติ๊ก dependencies/dependents/full refresh ·
Service account = `dbuffet-dataform-prd@` · **START EXECUTION**

**ต้องเห็น**: Succeeded ทุก action

### ตรวจ view

**ไปที่**: BigQuery Studio (prd) เปิดดูแต่ละ dataset

**ต้องเห็น**: `dimension_view` 16 · `fact_view` 4 · `bridge_dataset` 1 ·
`process_dataset` 5 · `onetime` 16 view
(`onetime` น้อยกว่า nonprd อยู่ 2 คือ `TEST_Data_Transaction` ×2 — ถูกต้องแล้ว)

---

## Step 20 — พิสูจน์ว่า dimension เดินได้

**ทำ**: Dataform → **START EXECUTION → Tags** → เลือก **`dimension_daily`**
(ไม่ติ๊กอะไรเลย · Service account = `dbuffet-dataform-prd@`)

**ต้องเห็น**: Succeeded

**ถ้าไม่ตรง**: ถ้า Failed เป็น `table not found` ของ dim ที่ใช้ MERGE
แปลว่า Step 17 copy `dimension_table` ไม่ครบ — กลับไปรัน transfer `dimension_table_from_nonprd` ใหม่

---

## Step 21 — พิสูจน์ว่า fact เดินได้

**ทำ**: **START EXECUTION → Tags** → เลือก **`fact_daily`**

**ต้องเห็น**: Succeeded

> Step 20–21 คือเหตุผลที่เราทำ cutover ตอนหัวค่ำ — ถ้าจะพัง ให้พังตอนที่ยังมีคนอยู่
> ไม่ใช่ตอน 06:00 เช้า

---

## Step 22 — เทียบจำนวนแถวทุกตาราง

**ไปที่**: BigQuery Studio → รัน SQL นี้ที่ **nonprd** แล้วรันซ้ำที่ **prd**
(แก้ชื่อ project ในทุกบรรทัด) แล้วเอาผลสองชุดมาวางเทียบกัน

```sql
WITH t AS (
  SELECT 'dimension_table' ds, table_id, row_count FROM `databuffet-nonprd.dimension_table.__TABLES__`
  UNION ALL SELECT 'fact_table', table_id, row_count FROM `databuffet-nonprd.fact_table.__TABLES__`
  UNION ALL SELECT 'onetime', table_id, row_count FROM `databuffet-nonprd.onetime.__TABLES__`
  UNION ALL SELECT 'process_dataset', table_id, row_count FROM `databuffet-nonprd.process_dataset.__TABLES__`
  UNION ALL SELECT 'mds_dataset', table_id, row_count FROM `databuffet-nonprd.mds_dataset.__TABLES__`
  UNION ALL SELECT 'validated_mac5', table_id, row_count FROM `databuffet-nonprd.validated_mac5.__TABLES__`
  UNION ALL SELECT 'validated_cis360', table_id, row_count FROM `databuffet-nonprd.validated_cis360.__TABLES__`
  UNION ALL SELECT 'validated_mastersku', table_id, row_count FROM `databuffet-nonprd.validated_mastersku.__TABLES__`
  UNION ALL SELECT 'curated_mac5', table_id, row_count FROM `databuffet-nonprd.curated_mac5.__TABLES__`
  UNION ALL SELECT 'curated_mastersku', table_id, row_count FROM `databuffet-nonprd.curated_mastersku.__TABLES__`
)
SELECT ds, table_id, row_count FROM t ORDER BY ds, table_id;
```

**ต้องเห็น**: จำนวนบรรทัดเท่ากัน ชื่อตารางตรงกันทุกตัว
ตัวเลข `row_count` จะต่างได้เฉพาะตารางที่ Step 20–21 เพิ่ง rebuild ใหม่ (dim/fact)

**ถ้าไม่ตรง**: ตารางที่หายไปฝั่ง prd = Data Transfer ยังไม่ครบ กลับ Step 17

> เคล็ดลับ: กด **SAVE RESULTS → Google Sheets** ทั้งสองฝั่ง แล้วใช้ VLOOKUP เทียบ
> จะเร็วกว่าไล่ดูด้วยตา

---

## Step 23 — เทียบ Surrogate Key ของ 12 dim ที่ใช้ MERGE (ต้องตรงเป๊ะ)

SK พวกนี้ต้องคงที่ตลอดไป — ถ้าไม่ตรง Power BI และตารางที่เก็บ SK ไว้จะเพี้ยนทั้งหมด

**ไปที่**: BigQuery Studio → รันที่ **nonprd** แล้วรันซ้ำที่ **prd**

```sql
SELECT 'dim_company' dim, COUNT(*) n, MIN(CompanySK) mn, MAX(CompanySK) mx FROM `databuffet-nonprd.dimension_table.dim_company`
UNION ALL SELECT 'dim_aging_rang', COUNT(*), MIN(AgingRangSK), MAX(AgingRangSK) FROM `databuffet-nonprd.dimension_table.dim_aging_rang`
UNION ALL SELECT 'dim_customer', COUNT(*), MIN(CustomerSK), MAX(CustomerSK) FROM `databuffet-nonprd.dimension_table.dim_customer`
UNION ALL SELECT 'dim_customer_grade', COUNT(*), MIN(CustomerGradeSK), MAX(CustomerGradeSK) FROM `databuffet-nonprd.dimension_table.dim_customer_grade`
UNION ALL SELECT 'dim_delivery', COUNT(*), MIN(DeliverySK), MAX(DeliverySK) FROM `databuffet-nonprd.dimension_table.dim_delivery`
UNION ALL SELECT 'dim_group_customer', COUNT(*), MIN(GroupCustomerSK), MAX(GroupCustomerSK) FROM `databuffet-nonprd.dimension_table.dim_group_customer`
UNION ALL SELECT 'dim_group_customer_grade', COUNT(*), MIN(GroupCustomerGradeSK), MAX(GroupCustomerGradeSK) FROM `databuffet-nonprd.dimension_table.dim_group_customer_grade`
UNION ALL SELECT 'dim_invoice', COUNT(*), MIN(InvoiceSK), MAX(InvoiceSK) FROM `databuffet-nonprd.dimension_table.dim_invoice`
UNION ALL SELECT 'dim_order', COUNT(*), MIN(OrderSK), MAX(OrderSK) FROM `databuffet-nonprd.dimension_table.dim_order`
UNION ALL SELECT 'dim_product_master', COUNT(*), MIN(ProductSK), MAX(ProductSK) FROM `databuffet-nonprd.dimension_table.dim_product_master`
UNION ALL SELECT 'dim_project', COUNT(*), MIN(ProjectSK), MAX(ProjectSK) FROM `databuffet-nonprd.dimension_table.dim_project`
UNION ALL SELECT 'dim_quotation', COUNT(*), MIN(QuotationSK), MAX(QuotationSK) FROM `databuffet-nonprd.dimension_table.dim_quotation`
ORDER BY dim;
```

**ต้องเห็น**: ทั้ง 3 คอลัมน์ (`n`, `mn`, `mx`) **เท่ากันเป๊ะทุกบรรทัด** ระหว่างสองฝั่ง

**ถ้าไม่ตรง**: หยุด อย่าไปต่อ — รัน Data Transfer `dimension_table_from_nonprd` ใหม่
(Step 17) แล้วรัน Step 20–21 ซ้ำ

> `dim_product_master` ใช้ชื่อคอลัมน์ **`ProductSK`** ไม่ใช่ `ProductMasterSK`
> ค่าอ้างอิงฝั่ง nonprd (2026-08-13): `dim_invoice` 1,645,664 · `dim_order` 1,362,203 ·
> `dim_customer` 97,199 · `dim_company` 5

---

## Step 24 — ให้สิทธิ์คนใช้งานใน prd

**ไปที่**: https://console.cloud.google.com/iam-admin/iam?project=databuffet-prd

**ทำ**: กด **GRANT ACCESS** เพิ่มคนที่ยังไม่มีสิทธิ์ใน prd
(diff ระหว่างสองโปรเจกต์ ณ 2026-08-13):

| ผู้ใช้ | สิทธิ์ที่มีใน nonprd | สถานะใน prd | ตัดสินใจ |
|---|---|---|---|
| `apirak@dos.co.th` | BigQuery Admin + dataViewer/jobUser/metadataViewer | **ไม่มีเลย** | ต้องเพิ่ม? |
| `atthasith@dos.co.th` | Editor + BigQuery dataViewer/jobUser/metadataViewer | **ไม่มีเลย** | ต้องเพิ่ม? |
| `prapatporn@dos.co.th` | BigQuery dataViewer/jobUser/metadataViewer | **ไม่มีเลย** | ต้องเพิ่ม? |
| `apipoj@dos.co.th` | Editor | **ไม่มีเลย** | ต้องเพิ่ม? |
| `chanpen@` / `chatchawan@` / `wisut@` | Editor | มีแค่ **Viewer** | ยกระดับหรือคงไว้? |
| `allinaiteam@dos.co.th` | BigQuery ชุด viewer | **มีครบแล้ว** | ✅ ไม่ต้องทำ |

**Service account ของฝั่ง BI** — เทียบแล้วเหมือนกันเกือบหมด ต่างจุดเดียว:

| | nonprd (`dbuffet-bquery-nonprod@`) | prd (`dbuffet-bquery-prd@`) |
|---|---|---|
| สิทธิ์อ่านข้อมูล | `bigquery.dataEditor` | `bigquery.dataViewer` |
| ที่เหลือ (jobUser, user, metadataViewer, readSessionUser, objectRefReader, connectionUser) | เหมือนกัน | เหมือนกัน |

prd ให้แค่ `dataViewer` = **เข้มกว่าและถูกต้องกว่า** สำหรับ prod
ถ้า Power BI แค่อ่านอย่างเดียว **ไม่ต้องแก้** — แก้เป็น dataEditor เฉพาะเมื่อเจอ error สิทธิ์เขียนจริง

**ต้องเห็น**: หน้า IAM ของ prd มีคนที่ต้องใช้งานครบตามที่ตัดสินใจ

> ตาราง `process_dataset.rls_customer360` และ `view_rls_*` ที่ repo สร้างให้เป็นแค่ **map
> สำหรับ BI เอาไป filter เอง** — ไม่ได้บังคับสิทธิ์ที่ระดับ BigQuery และในระบบนี้
> **ไม่มี row access policy อยู่จริงเลย** (ตรวจแล้วทั้ง nonprd)

---

## Step 25 — ตั้งเวลารันอัตโนมัติ (step ที่ทำให้ prd เดินเอง)

**นี่คือสาเหตุที่ prd ไม่เคยรันเลยตั้งแต่ 17 มี.ค.** — workflow config ของมันไม่มีทั้งเวลาและ
service account

**ไปที่**: Dataform → repository `data-buffet` → แท็บ **RELEASE CONFIGURATIONS AND
WORKFLOW CONFIGURATIONS**

**ทำ (ก)** คลิก workflow configuration **`daily_process`** → **EDIT**:

| ช่อง | ค่าที่ต้องตั้ง |
|---|---|
| Release configuration | `production` |
| Frequency / Repeats | **Custom → `0 6 * * *`** |
| Timezone | **`Asia/Bangkok`** |
| Service account | **`dbuffet-dataform-prd@databuffet-prd.iam.gserviceaccount.com`** |
| Tags | `validated`, `curated`, `dimension_daily`, `fact_daily`, `cdc_incremental`, `process` |

→ **SAVE**

**ทำ (ข)** คลิก **`yearly_process`** → **EDIT** → ใส่ **Service account** ตัวเดียวกัน → SAVE

**ต้องเห็น**: ในตาราง workflow configurations ทั้งสองแถวมี Schedule และ Service account
ครบ ไม่มีช่องว่าง

> tag `view` และ `initial` **ไม่ใส่** ใน schedule โดยตั้งใจ — รันมือตอน deploy เหมือน nonprd

---

## Step 26 — เปิดตัวช่วยรอบนอก

**ทำ**:
1. Cloud Scheduler (prd) → เปิด job ของ `alert-dataform` จาก Paused เป็น **Enabled**
2. ต่อ Scheduler ให้ `mds-app` ใน prd
3. ยืนยันกับทีมว่า **Airflow ถูกย้ายมาเขียน `gs://file-raw-data-prd` แล้ว** —
   ตั้งแต่คืนนี้ข้อมูลใหม่ต้องเข้า prd โดยตรง ไม่ผ่าน Storage Transfer อีก

**ถึงตรงนี้จบงานของคืน cutover**

---

# เช้าถัดไป

## Step 27 — ตรวจว่ารอบ 06:00 รันผ่าน

**ไปที่**: Dataform → repository `data-buffet` → แท็บ **WORKFLOW EXECUTION LOGS**

**ต้องเห็น**: มี execution ของเช้านี้ สถานะ **Succeeded**

**ถ้าไม่ตรง**: คลิกเข้าไปดู action ที่ Failed อ่าน error message

---

## Step 28 — เทียบซ้ำ

**ทำ**: รัน SQL ของ **Step 22** และ **Step 23** อีกครั้ง

**ต้องเห็น**:
- Step 23 (SK ของ 12 MERGE dim) ต้อง **ยังตรงเป๊ะ**
- Step 22 ชื่อตารางครบ ไม่มีตัวไหนหาย

> SK ของ dim อีก 34 ตัว (ที่เป็น full rebuild ไม่ใช่ 12 ตัวใน Step 23) **จะออกเลขใหม่
> ไม่ตรงกับ nonprd** — เป็นพฤติกรรมที่ตั้งใจตั้งแต่ 2026-07-20 เพราะ fact ปั้นใหม่ในรอบเดียวกัน
> ดู [known-issues.md](known-issues.md) และ
> [full-rebuild-pattern](../project_wiki/dimension/full-rebuild-pattern.md)

---

## Step 29 — ย้าย Power BI มาชี้ prd

ทำหลังจาก Step 27–28 ผ่านแล้วเท่านั้น

---

## Step 30 — เก็บกวาด (ไม่ต้องรีบ)

**ไปที่**: BigQuery Studio (prd)

dataset **`raw_mac5`** เก่า (85 external table ของโครงเดิม) ค้างอยู่เฉย ๆ ไม่กระทบอะไร
ลบได้เมื่อ prd รันนิ่งต่อเนื่องหลายวันแล้ว

---

# ถ้าต้อง rollback

`nonprd` ไม่ถูกแตะเลยตลอดกระบวนการ (Data Transfer อ่านทางเดียว) ดังนั้น:

1. Dataform (prd) → `daily_process` → **EDIT** → ลบ schedule ออก / **PAUSE**
2. ชี้ Power BI กลับ `databuffet-nonprd`

จุดที่ย้อนยากคือ **Step 16** — tag `initial` ลบ validated ของ cis360/mastersku/saleout ไปแล้ว
ถ้าหยุดกลางทางระหว่าง Step 16–17 ต้องรัน Data Transfer ให้จบ หรือรัน tag `validated`
เพื่อปั้นใหม่จาก raw

---

# หมายเหตุที่เจอตอนสำรวจ (ไม่ต้องทำอะไร)

- `monitoring_dataset.dataform_all_logs` ที่ `validated/mac5/chq.sqlx:43` เขียน `INSERT INTO` ถึง
  **ไม่มีอยู่ใน nonprd ด้วย** — เป็น bug ที่ซ่อนอยู่เท่ากันทั้งสองฝั่ง (โค้ดเส้นนั้นทำงานเฉพาะตอน
  PK retry loop ล้มเหลว)
- `AI.GENERATE` ใน `process/deb_address_data.sqlx` **ไม่ต้องสร้าง BigQuery connection** —
  ทดสอบด้วย dry-run แล้วว่าใช้ได้ทั้งสอง project โดยไม่มี connection
- `dim_product_rebate` ที่ `view/onetime/Transaction_Data_Mart.sqlx` อ้างถึง อยู่ใน `LEFT JOIN`
  ที่ถูก comment ไว้ — ไม่ต้องไปหาตารางนี้
