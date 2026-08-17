---
name: add-curated-table
description: Scaffold a new curated-layer table (business logic over validated tables). Use when the user asks to add a curated_mac5/mastersku/cis360 table.
---

Follow the step-by-step guide **`document/how-to/add-curated-table.md`** exactly.
Pattern reference: `document/project_wiki/curated/curated-layer.md`.

Arguments: `$ARGUMENTS` = `<source> <table_name>`.

Key rules (full checklist in the guide):
1. `type: "incremental"`, schema via `databuffet.CURATED_<SOURCE>`,
   `dependencies: ["curated_schema_<source>"]` only — validated sources come in
   through `${ref(...)}` (Dataform wires those deps automatically).
2. The real incremental window in this layer is **1 day**, inline:
   `${when(incremental(), \`AND asatdate >= CURRENT_DATE('Asia/Bangkok')-1\`)}`
   (not updatePartitionFilter — only `curated_product` uses that, with 7 days).
3. Output columns are camelCase; MAC5 uniqueKey starts with `company_id`.
4. Group reallocation logic (like the ag01 split-sale in `curated_mil`) goes in
   `post_operations { BEGIN ... END }` as TEMP → DELETE → INSERT on `self()`.

Reference implementations: `curated_mih.sqlx` (status lookup), `curated_mil.sqlx`
(post_operations split-sale), `curated_product.sqlx` (JSON + Thai/EN color parsing).
