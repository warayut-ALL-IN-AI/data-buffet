---
name: add-fact-table
description: Scaffold a new fact table (star-schema joins to dimension SKs). Use when the user asks to add a fact_* table.
---

Follow the step-by-step guide **`document/how-to/add-fact-table.md`** exactly.
Pattern reference: `document/project_wiki/fact/fact-layer.md`.

Arguments: `$ARGUMENTS` = `<entity_name>`.

Key rules (full checklist in the guide):
1. The fact layer has **no MERGE**. Pick one of the three real patterns:
   - Dataform `type: "table"` full rebuild (fact_order, fact_invoice)
   - `CREATE OR REPLACE TABLE AS` operations (fact_delivery, fact_quotation)
   - TEMP → DELETE → INSERT upsert (fact_transcation) — for large tables
2. Upsert targets must pre-exist in BigQuery (operations type).
3. Retention is a rolling **4 years** truncated to start-of-year (not 3):
   `mix_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR)`
   plus a separate purge `BEGIN ... DELETE ... END;` block.
4. Dimension refs = string interpolation + names in `dependencies[]`;
   curated/validated sources = `${ref(...)}`.
5. SKs from full-rebuild dims (`dim_target_product_group_by_sale*`, `dim_*_last`)
   are not stable across runs — join same-day only.
6. Tag `TAG_FACT_DAILY`; fact PK column `Fact<Entity>SK`.

Reference implementation: `definitions/fact/fact_transcation.sqlx` (note: that
spelling is the real table name — do not "fix" it).
