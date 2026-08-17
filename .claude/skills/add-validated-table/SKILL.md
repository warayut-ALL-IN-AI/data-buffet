---
name: add-validated-table
description: Scaffold a new validated-layer table (clean/cast/dedup from a raw external table). Use when the user asks to add a table to validated_mac5/cis360/mastersku/saleout_mdt.
---

Follow the step-by-step guide **`document/how-to/add-validated-table.md`** exactly.
Pattern reference: `document/project_wiki/validated/validated-layer.md`.

Arguments: `$ARGUMENTS` = `<source> <table_name>` (e.g. `mac5 stk_new`).

Key rules (full checklist in the guide):
1. Confirm the raw external table exists in `definitions/initial/<source>/` first.
2. File name = raw table name (the js block uses `name()`).
3. Copy the closest reference file:
   - single-source incremental → `definitions/validated/cis360/customer_profile.sqlx`
   - multi-company mac5 → `definitions/validated/mac5/mih.sqlx`
   - full-load → `definitions/validated/mac5/grp.sqlx`
4. There is **no primary-keys.json** — define the PK twice: `uniqueKey` in config
   AND `pk_key` in the js block; they must match.
5. Every column through `databuffet.functionData.*` helpers; `asatdate` from
   `parseAsatDate()`; Bangkok timezone in the incremental window.
6. Tags: `TAG_VALIDATED` + `TAG_VALIDATED_INCREMENTAL` or `TAG_VALIDATED_FULL`.

Note: the local machine has no `dataform` CLI — after writing the file, tell the
user to compile via the Dataform UI (or a machine with the CLI) to verify.
