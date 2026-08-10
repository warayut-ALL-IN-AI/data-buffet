# Running & Troubleshooting

> **LLM context**: How to execute and debug this project. Important environment facts:
> the `dataform` CLI is NOT installed in the local WSL environment (both `dataform` and
> `npx dataform` fail) — execution happens through the Dataform service in GCP.
> Ad-hoc queries: `bq --project_id=databuffet-nonprd` (default gcloud project differs!).

## Run graph by tag

| Tag | What runs |
|---|---|
| `initial` | Recreate raw external tables + schemas |
| `re-initial` | ⚠️ DROP validated/curated MAC5 tables (destructive, mac5 only) |
| `validated` / `validated_full` / `validated_incremental` | Validated layer |
| `curated` | Curated layer (no sub-tags in use) |
| `dimension_daily` | 58 of 59 dims |
| `dimension_yearly` | `dim_calendar` only |
| `fact_daily` | All 6 facts |
| `cdc` / `cdc_incremental` | CDC change log |
| `process` | AI address parsing |

Unused-but-defined: `dimension_monthly`, `fact_monthly`, `fact_yearly`,
`curated_full`, `curated_incremental`. There is **no** `assertions` tag.

```bash
dataform compile                 # syntax + graph check (on a machine that has the CLI)
dataform run --dry-run
dataform run --tags dimension_daily
dataform run --actions validated_mac5.mih
dataform compile --json | jq '.tables[] | {name: .target.name, deps: .dependencyTargets}'
```

## Ad-hoc BigQuery from local WSL

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false 'SELECT ...'
```
- Region-level `INFORMATION_SCHEMA` is permission-denied; use **dataset-level**:
  `` `databuffet-nonprd.dimension_table.INFORMATION_SCHEMA.COLUMNS` ``.
- Default gcloud project is a different one — always pass `--project_id`.

## Common failure modes

| Symptom | Likely cause / fix |
|---|---|
| Dim MERGE fails: table not found | `type: "operations"` targets pre-exist in BigQuery — a brand-new dim table must be created (DDL) before its first MERGE run |
| Duplicate SK rows | `max_sk` raced or MERGE ON mismatch; check the t2/t3 CASE and that MERGE is `ON T.<X>SK = S.<X>SK` |
| Dim missing recent mds edits | `MDS_BACKFILL_DAYS` window (currently 1 day) — a row updated earlier but missed needs a manual backfill run with a larger var value |
| Validated datetime parse fails | Raw extract switched timestamp format; `parseFlexibleDatetime` handles the two known formats — check for a third (see 2026-05-23/24 incident, self-resolved) |
| Validated incremental missed data | The window is `ASATDATE >= CURRENT_DATE - BACKFILL_DAYS` (string compare, default 1 day) — for older data raise `BACKFILL_DAYS` and rerun (see below) |
| PK post-op ALTER fails repeatedly | BigQuery metadata contention — the retry loop (10×) usually recovers; rerun otherwise |
| Fact upsert doubles rows | `fact_transcation` DELETE keys are `milVnos, milType, CompanySK` — grain drift in `onetime.Transaction_Data_Mart` breaks this |
| Orphan SK values in facts | Expected after mds hard-deletes ([mds-delete-pattern.md](../dimension/mds-delete-pattern.md)); `dim_target_product_group_by_sale*` self-heal next day |

## Backfilling more than one day (`BACKFILL_DAYS`)

Every validated and curated incremental window reads
`DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`
(74 statements across 52 files). The var lives in `workflow_settings.yaml` and
defaults to `"1"`, i.e. yesterday only.

When a source has been failing for several days — say `mih` has been broken for
three — widen the window instead of doing a full refresh:

1. Edit `workflow_settings.yaml` in the Dataform workspace:
   `BACKFILL_DAYS: "3"`
2. Compile and check **Compiled queries** — the window should read `INTERVAL 3 DAY`.
3. Run the affected actions (or the `validated` / `curated` tags).
4. **Set it back to `"1"`** and re-run nothing; the next scheduled run picks up
   the normal window.

Notes:

- The window is a look-back from today, not a date range. `"3"` means the last
  three days, so it always includes yesterday.
- Widening it costs a proportional scan of the raw partitions — the tables are
  partitioned on `asatdate`, so 3 days is roughly 3× the bytes, not a full scan.
- `QUALIFY ROW_NUMBER() ... ORDER BY asatdate DESC` still keeps one row per PK,
  so re-reading days that already landed is idempotent.
- **Left on the old hardcoded `-1` on purpose** (they mean something other than a
  look-back window, do not wire them to this var):
  `cdc_change_log.sqlx` (`=` a single partition, not a range),
  `dim_aging.sqlx` `run_date` (a snapshot date — widening it would DELETE more
  days than it re-INSERTs), and `view_fact_transcation` (the upper bound of a
  4-year range).

## Git / environments

- Branches: `dev` (default working) → merge → `nonprod` → `prod`; `hotfix` exists.
- `workflow_settings.yaml` is per-environment (project id differs).
- A Cloud-Run based Slack run-monitor lives in a separate scaffold
  (`cloud-run-monitor/`, BQ `monitor_dataset`) — deployment pending as of 2026-07.
