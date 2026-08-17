---
name: verify-setup
description: Verify a developer machine is correctly set up for Data-Buffet — CLIs, GCP auth, BigQuery/GCS access, git remote and branches, Claude Code hooks. Use on day 1 after onboarding, or when bq/gcloud/hooks behave unexpectedly.
---

Run the check script and report only what FAILS, with the exact fix. Everything
that passes gets one summary line.

```bash
bash .claude/skills/verify-setup/scripts/verify.sh
```

The script probes each item and prints `PASS` / `FAIL` / `SKIP`. It never writes
anything — no BigQuery DML, no GCS mutation, no git push.

## What is checked, and the fix when it fails

| # | Check | Fix when it fails |
|---|---|---|
| 1 | `git` + repo remote is `ALL-IN-AI-ASIA/data-buffet` | ขอสิทธิ์ repo จาก admin แล้ว `git clone` ใหม่ |
| 2 | Branch `dev` exists and tracks `origin/dev` | `git fetch origin && git checkout dev` |
| 3 | `core.hooksPath` = `.claude/hooks` | `git config core.hooksPath .claude/hooks` (ต้องตั้งเองหลัง clone — git ไม่ copy ค่านี้มาให้) |
| 4 | A working Python (`python3` / `python` / `py`) | ติดตั้ง Python 3.x — hooks และ `document/diagrams/generate_lineage.py` ใช้ |
| 5 | `gcloud` on PATH | ติดตั้ง Google Cloud SDK; บน Windows ให้รันจาก WSL (ดู onboarding §3) |
| 6 | `gcloud auth list` has an active account | `gcloud auth login` + `gcloud auth application-default login` |
| 7 | `bq` on PATH | มากับ Cloud SDK — `gcloud components install bq` |
| 8 | `bq ls --project_id=databuffet-nonprd` works | ยังไม่มีสิทธิ์ → ขอ role ตาม onboarding §3.2 |
| 9 | Read query on `dimension_table.dim_company` returns a row | ขาด `roles/bigquery.jobUser` หรือ dataset-level read |
| 10 | `gsutil ls gs://file-raw-data` works | ขอ `roles/storage.objectViewer` บน bucket |
| 11 | Guard hook blocks a destructive payload (`exit 2`) | hook พัง — ดู `.claude/hooks/guard-dangerous.sh`; ห้ามปล่อยผ่าน เพราะ guard ที่เป็นหมันอันตรายกว่าไม่มี guard |
| 12 | Doc-sync Stop hook returns `exit 0` on a clean tree | ดู `.claude/hooks/doc-sync-check.sh` |
| 13 | `dataform` CLI (optional) | ไม่มีก็ทำงานได้ — compile ผ่าน Dataform UI บน GCP แทน |

Checks 5–10 are skipped with `SKIP` (not `FAIL`) when the CLI is missing, so a
Windows-side run still gives useful output; run it again inside WSL for the full
picture.

After a clean run, point the developer at `document/getting-started/onboarding.md`
§4 (flow การทำงาน) and the `how-to/` guides.
