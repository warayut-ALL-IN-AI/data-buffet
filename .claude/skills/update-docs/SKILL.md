---
name: update-docs
description: Sync document/ (developer docs + LLM wiki) after code changes. Use after adding/changing tables, patterns, or design decisions so the docs stay authoritative.
---

`document/` (created 2026-07-10 from a full code scan) is the authoritative doc set —
it must track the code. Index: `document/README.md`; wiki entry:
`document/project_wiki/README.md`.

Given the change in `$ARGUMENTS` (or the current git diff if empty), update:

| Change | Update |
|---|---|
| New/changed dimension | `document/project_wiki/dimension/inventory.md` (add row: file, SK, natural key, source, deps); if it deviates from the canonical MERGE pattern → `special-cases.md` |
| New validated table | `document/project_wiki/validated/source-inventory.md` |
| New curated/fact table | the layer page's inventory table |
| Pattern change (window, dedup, SK logic, tombstone) | the layer's pattern page + `document/coding-standards/sqlx-coding-standard.md` if it changes the standard |
| New tag / dataset / helper | `document/project_wiki/includes/variables.md` or `function-data.md` + tag tables in `dataform-run` skill and CLAUDE.md |
| Design decision / accepted trade-off | `document/operations/known-issues.md` (dated entry) |
| New source system | `document/project_wiki/overview/source-systems.md` + architecture pages |

Rules:
- **Lineage graph — ALWAYS regenerate** on any `definitions/` change (add/remove file,
  edit `dependencies`, add/remove a `ref()`, pause/unpause a config):
  `python3 document/diagrams/generate_lineage.py` then stage
  `document/diagrams/pipeline_lineage.md`. It is auto-generated — never hand-edit it.
- Counts matter: if file counts change (59 dims, 9 facts, 135 validated), fix them in
  `README.md` (root), `document/architecture/overview.md`, and
  `project_wiki/overview/architecture.md`.
- Keep load-bearing typos verbatim (`fact_transcation`, `CDC_DATESET`, `prdDiminsionData`).
- Do NOT resurrect `.claude/knowledge/` — it was deleted as stale; `document/` replaced it.
- After editing, verify relative links still resolve:
  `for f in $(find document -name "*.md"); do dir=$(dirname $f); grep -oP '\]\(\K[^)#]+\.md' $f | while read l; do [ -f "$dir/$l" ] || echo "BROKEN: $f -> $l"; done; done`
