#!/bin/bash
# Pre-commit hook for Data-Buffet project
# 1) Warn (never block) when code changes are committed without document/ updates.
# 2) Format + compile Dataform code when the CLI is available; skip gracefully otherwise.

echo "🔍 Running pre-commit checks..."

# --- 1. Doc-sync warning -----------------------------------------------------
STAGED=$(git diff --cached --name-only)
if echo "$STAGED" | grep -qE '^(definitions/|includes/|workflow_settings)'; then
    if ! echo "$STAGED" | grep -qE '^document/'; then
        echo ""
        echo "⚠️  DOC-SYNC: commit นี้แก้ definitions/ หรือ includes/ แต่ไม่มีการแก้ document/"
        echo "   ถ้าการแก้กระทบ pattern/inventory/การตัดสินใจ อย่าลืมอัปเดตเอกสารด้วย"
        echo "   (ตาราง mapping: .claude/skills/update-docs/SKILL.md — เตือนเฉย ๆ ไม่ block)"
        echo ""
    fi
fi

# --- 2. Regenerate diagrams when definitions/ changed -----------------------
# Regenerates BOTH pipeline_lineage.md and topic_flows.md. Picks the first Python
# that actually RUNS — on Windows `command -v python3` resolves to the Microsoft
# Store shim (exits 0 but fails to run), so we verify `--version` before using it.
if echo "$STAGED" | grep -qE '^definitions/.*\.sqlx$'; then
    PY=""
    for c in python3 python py; do
        if command -v "$c" >/dev/null 2>&1 && "$c" --version >/dev/null 2>&1; then
            PY="$c"; break
        fi
    done
    if [ -n "$PY" ] && [ -f document/diagrams/generate_lineage.py ]; then
        echo "🕸️  definitions/ changed — regenerating diagrams ($PY)..."
        if "$PY" document/diagrams/generate_lineage.py; then
            git add document/diagrams/pipeline_lineage.md document/diagrams/topic_flows.md
        else
            echo "⚠️  diagram generation failed — commit continues (fix & regenerate manually)"
        fi
    else
        echo "⚠️  no working python found — skipping diagram regeneration (run generate_lineage.py manually)"
    fi
fi

# --- 3. Dataform format + compile -------------------------------------------
if ! command -v dataform >/dev/null 2>&1; then
    echo "⚠️  dataform CLI not installed — skipping format/compile (verify in Dataform UI)"
    exit 0
fi

echo "📝 Formatting SQLX files..."
dataform format
if [ $? -ne 0 ]; then
    echo "❌ Dataform format failed"
    exit 1
fi

echo "🔨 Compiling Dataform code..."
dataform compile
if [ $? -ne 0 ]; then
    echo "❌ Dataform compilation failed"
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0
