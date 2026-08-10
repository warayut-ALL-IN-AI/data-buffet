# Initial Layer — `definitions/initial/`

> **LLM context**: 13 files that bootstrap everything: datasets, external tables over
> GCS AVRO, and UDFs. All `type: "operations"`. Tags: `initial` (create) and
> `re-initial` (drop for rebuild).

## Root files

### `create_all_schema.sqlx`
`CREATE SCHEMA IF NOT EXISTS` for **every** dataset: raw MAC5 ×5, validated/curated per
source, `dimension_table`, `dimension_view`, `fact_table`, `fact_view`,
`process_dataset`, `cdc_dataset`, `function_dataset`, `onetime` — all with
`OPTIONS(location="us-central1")`.

### `create_all_function.sqlx`
**6 UDFs** in `function_dataset` — re-synced from the live dataset on 2026-07-24
(`clean_company_prefix` added later; BigQuery is the source of truth for this file;
see the note below):

| UDF | Signature | Purpose |
|---|---|---|
| `fn_flag_exc` | `(mihcancel INT64, mihstatus INT64, FlagExc STRING)` | cancel/status → exclude flag |
| `fn_flag_sales_kpi` | `(mihcancel INT64, mihstatus INT64, rebate STRING)` | sales-KPI Yes/No |
| `fn_flag_scg` | `(mihvnos STRING, mihcus STRING)` | Thai "ซื้อตรง"/"ซื้อผ่านร้าน" direct-vs-store classification for CRC vnos |
| `fn_order_type` | `(mihref2 STRING)` | `QOAG` prefix → `Online-AllkonsM`, else `Offline` (used by `view_dim_order`) |
| `EXTRACT_CHQ_DATA` | `(memo_raw STRING, datec DATETIME, total FLOAT64)` | regex-heavy parser of Thai cheque/transfer memo → `STRUCT<chqmemo, extract_text, extract_value ARRAY<STRUCT<extract_date DATE, extract_amount FLOAT64>>>`; handles Thai month abbreviations + Buddhist-era (พ.ศ.) year conversion. Parsing only starts if a **trigger** matches — see below |
| `clean_company_prefix` | `(text_input STRING)` | strips Thai company prefixes (`บริษัท`, `บจก.`, `บมจ.`, `หจก.`, `ร้าน`, `ห้างหุ้นส่วนจำกัด`, leading `+`) and suffixes (`จำกัด`, `(มหาชน)`) → bare company name for matching |

> **Drift found and fixed 2026-07-24**: the file had only 4 UDFs (`fn_order_type`
> missing entirely) and `fn_flag_scg` declared its parameters as `milvnos`/`milcus`
> while BigQuery has `mihvnos`/`mihcus`. It also carried **335 unescaped backslashes**
> in the SQL body — including one `\1` that makes the whole action fail to compile
> ("octal escape"), which is likely why the file drifted from reality in the first
> place. Regenerated from `function_dataset.INFORMATION_SCHEMA.ROUTINES` with every
> backslash doubled per [coding-standard §3.3](../../coding-standards/sqlx-coding-standard.md);
> all 5 now round-trip byte-identical to BigQuery.
>
> These UDFs are **not separate Dataform actions** — they are all created by this one
> `operations` action, so consumers cannot `ref()` them (interpolate
> `${databuffet.FUNCTION_DATASET}` instead and do not list them in `dependencies[]`).

### `EXTRACT_CHQ_DATA` — the trigger list

`transfer_pos` is a `COALESCE` of trigger regexes over `memo_raw`. It returns the
position of the **first** trigger that matches; `0` means "no trigger" and the whole
parser returns NULL. Order matters — earlier entries win, so appending to the list
can never change a memo that already matched.

| # | Trigger | Note |
|---|---|---|
| 1 | `โอน…` / `รับโอนแทน` / `**<ธนาคาร>` / `เปลี่ยนเช็ค` | Thai bank names only fire here, i.e. when preceded by `โอน` or `**` |
| 2 | `เช็ค` | |
| 3 | `\b(?:kbank\|kbnak\|kasikorn\|kbiz\|bbl\|bualuang\|ktb\|krungthai\|krungsri\|scb\|scbt\|ttb\|tmb\|tbm\|thanachart\|gsb\|baac\|ghb\|uob\|tisco\|kkp\|cimb\|icbc\|hsbc\|citibank\|lhbank)\s*/\s*\d` | added 2026-08-10. The trailing `/<digits>` is **required** — real memos write `kbank/908`, `scb/264`. Without it `ค่า ON NET / KTB = 800611831` yields a bogus 800M amount |
| 4 | `(?:รุด\|รูด\|รับ)\s*บัตร(?:เครดิต)?(?:คืน)?[^0-9\n]{0,10}(?:\d{1,2}/\d{1,2}\|(?:ยอด\|จำนวน\|เป็นเงิน\|=)\s*\d)` | added 2026-08-10. The trailing date-or-amount is **required** — 34 of the 43 memos containing `รูดบัตร` are `ค่าเช่าเครื่องรูดบัตร` (EDC machine rent, not a payment) and must not trigger |

Measured on all 76,573 `validated_mac5.chq` rows when triggers 3–4 were added:
**+60 rows gained an amount, 0 lost, 1 changed (`189` → `189,176`, a fix), 1 noise**
(`to bbl/418` — trigger fires, no amount present). Re-run that comparison before
touching this list again.

## External-table patterns

**Incremental** (transactional tables) — Hive partition discovery on `ASATDATE=` folders:
```sql
CREATE OR REPLACE EXTERNAL TABLE `raw.<table>`
WITH PARTITION COLUMNS (ASATDATE STRING)
OPTIONS(format='AVRO',
        uris=['gs://file-raw-data/<gcs_prefix>/<table>/*'],
        hive_partition_uri_prefix='gs://file-raw-data/<gcs_prefix>/<table>/')
```

**Full** (reference tables) — direct glob, no partition:
```sql
CREATE OR REPLACE EXTERNAL TABLE `raw.<table>`
OPTIONS(format='AVRO', uris=['gs://file-raw-data/<gcs_prefix>/<table>/*.avro'])
```

Every table is preceded by `DROP TABLE IF EXISTS`.

## Per-source files

| File | Tag | Creates |
|---|---|---|
| `mac5/create_all_table_raw_mac5.sqlx` | initial | AG01 flagship: 13 incremental (`cql, rcv, cst, mih, cps, cps_dummy, mie, mie_dummy, mih2, mih_dummy, mil, mil_dummy, mir`) + ~60 full tables. `stg_report`/`stgacc` read from `mac5_report`; `tdelivery`/`ttrip*` from `mac5_gps` |
| `mac5/create_all_table_raw_mac5_{aa05,ab01,ac02,ak02}.sqlx` | initial | Per-company: incremental `cql, mih, mil, mir, mie` + full `ap_s, ar_s, chq, deb, dep, per, stg, stk, cfs` |
| `mac5/drop_all_tables_validated_mac5.sqlx` | **re-initial** | DROP ~85 validated_mac5 tables |
| `mac5/drop_all_tables_curated_mac5.sqlx` | **re-initial** | DROP 3 curated tables |
| `cis360/create_all_table_raw_cis360.sqlx` | initial | 27 hive-partitioned external tables |
| `cis360/drop_all_tables_validated_cis360.sqlx` | initial | DROP 24 validated tables |
| `mastersku/create_all_table_raw_mastersku.sqlx` | initial | 12 external tables |
| `mastersku/drop_all_tables_validated_mastersku.sqlx` | initial | DROP 11 validated tables |
| `saleout_mdt/create_all_table_raw_saleout_mdt.sqlx` | initial | 10 external tables by retailer (bt/gb/hp/tw); note renames: folder `reportsalesubscription` → table `report_sale_subscription`, `gb/*` → `saleout_gb` |
| `saleout_mdt/drop_all_tables_validated_saleout_mdt.sqlx` | initial | DROP 10 validated tables |

## Dependency wiring

`create_all_table_raw_<source>` depends on the corresponding `drop_all_tables_*`
action(s); validated schema files (`validated_schema_*`) depend on the create actions.
Running `dataform run --tags initial` therefore rebuilds raw external tables cleanly.

⚠️ `re-initial` tag DROPs validated/curated MAC5 tables — full-rebuild only, data in
incremental tables is lost until re-run.
