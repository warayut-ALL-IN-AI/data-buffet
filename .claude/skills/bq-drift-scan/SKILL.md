---
name: bq-drift-scan
description: Compare live BigQuery views and UDFs against the .sqlx files and report drift. Use when views/functions were edited in the BigQuery console and may never have made it back into git, before running the `view` tag, or to pull a console edit back into the repo.
---

Views and UDFs get edited in the BigQuery console and the change never reaches
`definitions/`. Two failure modes follow: the next Dataform run silently
overwrites the console work, or the repo carries SQL that no longer compiles.
This skill finds both, and pulls the console version back when BigQuery is right.

**BigQuery is the source of truth for view SQL.** Never rewrite a live view from
the repo without being asked — pull the other direction.

Scripts live in `scripts/` next to this file. Run them from the scratchpad so
nothing lands in the repo.

## 1. Dump the live definitions

`bq` is not on PATH on Windows — go through WSL:

```bash
wsl -e bash -lc "bq --project_id=databuffet-nonprd query --use_legacy_sql=false \
  --format=prettyjson --max_rows=500 < <scratchpad>/dump.sql > <scratchpad>/bq_dump.json"
```

`scripts/dump.sql` unions `INFORMATION_SCHEMA.VIEWS` over `dimension_view`,
`fact_view`, `bridge_dataset`, `onetime`, `process_dataset` plus
`INFORMATION_SCHEMA.ROUTINES` over `function_dataset`. Region-level
INFORMATION_SCHEMA is permission-denied — it must stay per-dataset.

Write SQL files as **UTF-8 without BOM** (`[System.IO.File]::WriteAllText` with
`UTF8Encoding($false)`); `Out-File -Encoding utf8` adds a BOM and BigQuery
rejects it with `Illegal input character "\357"`.

## 2. Who edited what, and when

`scripts/dump.sql` has a second query (commented at the bottom) that joins
`__TABLES__.last_modified_time` per view and `ROUTINES.last_altered`, ordered
newest first. Anything modified after the last commit touching that file is a
console edit. Cross-check with:

```bash
git log -1 --format="%ad %s" --date=format:"%Y-%m-%d %H:%M" -- <path>
```

## 3. Compare

```bash
python <skill>/scripts/scan.py --scratchpad <scratchpad>
```

Reports: identical / different (with a similarity score) / missing in BigQuery /
extra in BigQuery, and writes a unified diff per differing object into
`<scratchpad>/diffs/`.

The script renders each `.sqlx` the way Dataform does before diffing —
`${XxxTableRef}` from the `js {}` block, `${ref(ds, "t")}`, `${databuffet.*}`
from `variables.json`, `${databuffet.functionData.*}` from `function-data.js`.
Anything it cannot resolve is reported as `<<UNRESOLVED:...>>`; that is a bug in
the renderer, not drift.

## 4. Classify before acting

Sort every difference into one of these. Only the first two are real drift:

| Class | Tell | Action |
|---|---|---|
| BigQuery ahead | New columns/joins in BQ, `last_modified` after the last commit | Pull into repo (step 5) |
| Repo broken | References an object that does not exist | Fix the repo |
| Cosmetic | Trailing `;`, whitespace | Leave it |
| Renderer artifact | `<<UNRESOLVED>>`, or a `--` comment differing only in backslash count | Fix the renderer, not the file |

Case matters: BigQuery table ids are case sensitive. `RLS_Customer360` vs
`rls_customer360` compiles fine and fails at run time. Confirm real names with
`bq ls <dataset>` rather than trusting either side.

## 5. Pull a view back from BigQuery

```bash
python <skill>/scripts/pull.py --scratchpad <scratchpad> --view <name>   # dry run
python <skill>/scripts/pull.py --scratchpad <scratchpad> --view <name> --apply
```

Keeps the existing `config {}`, takes the SQL body from BigQuery verbatim, and
rewrites only the table paths:

- `validated_*` / `curated_*` → `${ref(databuffet.<KEY>, "table")}` (§3.1)
- everything else → js-block `` `${XxxTableRef}` `` (§3.2), reusing const names
  already in the file and generating PascalCase ones for new tables
- newly referenced Dataform-managed objects are appended to `dependencies[]`;
  existing entries are never removed (that would change the DAG as a side effect)

### Two things BigQuery does to the text — both bite

1. **Backticks are stripped from table paths** in `view_definition`.
   `from databuffet-nonprd.dimension_table.dim_invoice` comes back bare. This
   still *runs* — GoogleSQL accepts a hyphenated project id unquoted in a table
   path (verified with `bq query --dry_run` 2026-08-10) — but it breaks the repo
   convention, and one file (`fact_transcation.sqlx:768`) already has a bare ref
   that reads like a bug every time someone reviews it. `pull.py` re-adds them.
   UDF calls keep their backticks, so a raw pull comes back inconsistent.
2. **Commented-out blocks are dropped** when a view is saved in the console.
   `view_rls_data` lost 88 lines that way. Count `--` lines before and after and
   say so in the report; the old text is still in git history.

After `--apply`, always run:

```bash
python <skill>/scripts/scan.py --scratchpad <scratchpad> --check-backticks
```

`--check-backticks` verifies every `${XxxTableRef}` in a SQL body is wrapped in
backticks and no literal `databuffet-nonprd.` path survived. **The normal diff
cannot see this** — it strips backticks before comparing, which is exactly how a
broken pull passed review once already.

## 6. Backslashes when hand-editing after a pull

Confirmed 2026-08-10 against the Compiled queries panel:

- **SQL code** — backslashes pass through untouched. Write `\d`, `\s`, `\1` as
  they should reach BigQuery.
- **`--` comments** — processed as a JS template literal. Write `\\1`, `\\n`.
  A bare `\1` in a comment fails the whole action with *"Octal escape sequences
  are not allowed in template strings"*, and a bare `\n` becomes a real newline
  that ends the comment early.

Full rule and history: `document/coding-standards/sqlx-coding-standard.md` §3.3.

## 7. Report

State counts, then per object: what changed, which side is ahead, and what you
did. Name what you deliberately left alone and why. Do not commit without being
asked; when you do, keep the pull and any hand fix in separate commits.
