---
name: check-runs
description: Check Dataform run health from the monitor table — failures, durations, bytes, per layer/day. Use when the user asks "เมื่อคืนรันผ่านไหม", why a table failed, or for run-history trends.
---

Run telemetry lives in `databuffet-nonprd.monitor_dataset.dataform_run_action`
(action-grain rollup, partitioned by run_date, 90-day retention; fed from
INFORMATION_SCHEMA.JOBS_BY_PROJECT; Slack alert fires daily 07:00 BKK via Cloud Run
service `alert-dataform`).

Arguments: `$ARGUMENTS` = date / date range / table name / layer (default: yesterday
+ today, Bangkok time).

Queries (via `bq --project_id=databuffet-nonprd query --use_legacy_sql=false`):

```sql
-- Daily overview
SELECT run_date, COUNT(*) actions,
       COUNTIF(status = 'FAILED') failed,
       ROUND(SUM(total_bytes)/POW(10,9), 1) gb,
       ROUND(SUM(duration_sec)/60, 1) total_min
FROM `databuffet-nonprd.monitor_dataset.dataform_run_action`
WHERE run_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
GROUP BY run_date ORDER BY run_date DESC;

-- Failures with reasons
SELECT run_date, layer, action_name, error_message
FROM `databuffet-nonprd.monitor_dataset.dataform_run_action`
WHERE status = 'FAILED' AND run_date >= <window>
ORDER BY run_date DESC;

-- Slowest / most expensive actions
SELECT layer, action_name, ROUND(AVG(duration_sec),0) avg_sec,
       ROUND(AVG(total_bytes)/POW(10,9),1) avg_gb, COUNT(*) runs
FROM `databuffet-nonprd.monitor_dataset.dataform_run_action`
WHERE run_date >= <window>
GROUP BY layer, action_name ORDER BY avg_gb DESC LIMIT 15;

-- Per-layer health for one day
SELECT layer, COUNT(*) actions, COUNTIF(status = 'FAILED') failed,
       ROUND(SUM(total_bytes)/POW(10,9),1) gb
FROM `databuffet-nonprd.monitor_dataset.dataform_run_action`
WHERE run_date = <date>
GROUP BY layer ORDER BY gb DESC;
```

Schema (verified 2026-08-17 — use these names exactly; the table has no `state`,
`duration_seconds` or `total_bytes_processed`):

`run_id, run_date, action_schema, layer, source, action_name, action_type,
status, error_message, start_time, end_time, duration_sec, total_bytes, captured_at`

- `status` is only ever `SUCCESS` or `FAILED`.
- `action_type` is `table`, `incremental_table` or `operations`.
- The collector writes once a day at **07:00 Asia/Bangkok** (`captured_at`), i.e.
  after the ~06:00 pipeline run — today's rows do not exist before 07:00.
- Baseline for "normal": ~213 actions/night, ~117 GB, ~32 min total.

Re-check the schema only if a query still errors:
`bq --project_id=databuffet-nonprd show --schema monitor_dataset.dataform_run_action`

For diagnosing a specific failure, cross-reference the failure table in
`document/how-to/run-and-debug.md`. For cost follow-up, hand off to the
`bigquery-optimizer` agent.
