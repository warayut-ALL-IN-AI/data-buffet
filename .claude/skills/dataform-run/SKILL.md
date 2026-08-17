---
name: dataform-run
description: Run or compile Dataform transformations by tag/action. Use when the user asks to run, compile, format, or dry-run the pipeline or a layer.
---

Arguments: `$ARGUMENTS` = tag, action, or extra flags.

**Environment caveat first**: this local machine has **no `dataform` CLI**
(`dataform` and `npx dataform` both fail). If the CLI is unavailable, do not retry —
tell the user to run via the Dataform UI on GCP, and offer the exact command to use
there. Ad-hoc data checks can use
`bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'`.

Commands (when a CLI is available):

```bash
dataform compile                          # validate syntax + dependency graph
dataform format                           # format all SQLX
dataform run --dry-run                    # show plan
dataform run --tags <tag>                 # run a layer
dataform run --actions <schema>.<table> [--include-deps]
dataform run --full-refresh --actions ... # full rebuild of an incremental table
```

Tags actually in use (there is no `fact`, `dimension`, or `assertions` tag):

| Layer | Tags |
|---|---|
| Initial | `initial`, `re-initial` (⚠️ drops validated/curated MAC5 tables) |
| Validated | `validated`, `validated_full`, `validated_incremental` |
| Curated | `curated` |
| Dimension | `dimension_daily`, `dimension_yearly` (dim_calendar only) |
| Fact | `fact_daily` |
| Support | `cdc`, `cdc_incremental`, `process` |

Troubleshooting table: `document/how-to/run-and-debug.md` and
`document/project_wiki/operations/running-and-troubleshooting.md`.
