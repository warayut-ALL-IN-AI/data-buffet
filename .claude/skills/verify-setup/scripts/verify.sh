#!/bin/bash
# Data-Buffet setup verification — read-only.
# Runs on Git Bash (Windows) and WSL/Linux. Prints PASS / FAIL / SKIP per check.
# Usage: bash .claude/skills/verify-setup/scripts/verify.sh

PROJECT="databuffet-nonprd"
BUCKET="gs://file-raw-data"
REPO_MATCH="ALL-IN-AI-ASIA/data-buffet"

PASS=0; FAIL=0; SKIP=0
pass() { printf '  PASS  %s\n' "$1"; PASS=$((PASS+1)); }
fail() { printf '  FAIL  %s\n        → %s\n' "$1" "$2"; FAIL=$((FAIL+1)); }
skip() { printf '  SKIP  %s\n        → %s\n' "$1" "$2"; SKIP=$((SKIP+1)); }

cd "$(dirname "$0")/../../../.." 2>/dev/null || { echo "cannot locate repo root"; exit 1; }
echo "Data-Buffet setup check — repo: $(pwd)"
echo

# --- 1-3 git ------------------------------------------------------------------
echo "[git]"
if command -v git >/dev/null 2>&1; then
    if git remote -v 2>/dev/null | grep -q "$REPO_MATCH"; then
        pass "git remote points at $REPO_MATCH"
    else
        fail "git remote does not point at $REPO_MATCH" "ขอสิทธิ์ repo จาก admin แล้ว clone ใหม่"
    fi
    if git rev-parse --verify dev >/dev/null 2>&1; then
        pass "branch dev exists"
    else
        fail "branch dev missing" "git fetch origin && git checkout dev"
    fi
    HP=$(git config --get core.hooksPath)
    if [ "$HP" = ".claude/hooks" ]; then
        pass "core.hooksPath = .claude/hooks"
    else
        fail "core.hooksPath = '${HP:-<unset>}'" "git config core.hooksPath .claude/hooks"
    fi
else
    fail "git not on PATH" "ติดตั้ง git ก่อน"
fi

# --- 4 python -----------------------------------------------------------------
echo
echo "[python]"
PY=""
for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 && "$c" --version >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -n "$PY" ]; then
    pass "working python: $PY ($($PY --version 2>&1))"
else
    fail "no working python (python3/python/py)" "ติดตั้ง Python 3.x — hooks + generate_lineage.py ต้องใช้"
fi

# --- 5-9 gcloud / bq ----------------------------------------------------------
echo
echo "[gcp]"
if command -v gcloud >/dev/null 2>&1; then
    pass "gcloud on PATH"
    ACC=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
    if [ -n "$ACC" ]; then
        pass "active gcloud account: $ACC"
    else
        fail "no active gcloud account" "gcloud auth login && gcloud auth application-default login"
    fi
else
    skip "gcloud not on PATH" "บน Windows ให้รันสคริปต์นี้ใน WSL (Cloud SDK ติดตั้งฝั่ง WSL)"
fi

if command -v bq >/dev/null 2>&1; then
    pass "bq on PATH"
    if bq ls --project_id="$PROJECT" >/dev/null 2>&1; then
        pass "bq ls on $PROJECT"
    else
        fail "bq ls on $PROJECT denied" "ขอ role ตาม document/getting-started/onboarding.md §3.2"
    fi
    if bq --project_id="$PROJECT" query --use_legacy_sql=false --format=none \
         "SELECT 1 FROM \`$PROJECT.dimension_table.dim_company\` LIMIT 1" >/dev/null 2>&1; then
        pass "read query on dimension_table.dim_company"
    else
        fail "cannot query dimension_table.dim_company" "ขาด roles/bigquery.jobUser หรือสิทธิ์อ่าน dataset"
    fi
else
    skip "bq not on PATH" "มากับ Cloud SDK — gcloud components install bq (หรือรันใน WSL)"
fi

if command -v gsutil >/dev/null 2>&1; then
    if gsutil ls "$BUCKET" >/dev/null 2>&1; then
        pass "gsutil ls $BUCKET"
    else
        fail "cannot list $BUCKET" "ขอ roles/storage.objectViewer บน bucket"
    fi
else
    skip "gsutil not on PATH" "มากับ Cloud SDK (หรือรันใน WSL)"
fi

# --- 11-12 claude code hooks --------------------------------------------------
echo
echo "[claude code hooks]"
G=".claude/hooks/guard-dangerous.sh"
if [ -f "$G" ]; then
    # Build the payload indirectly so this script's own text is not what gets matched.
    A="bq"; B="rm"
    printf '{"tool_input":{"command":"%s %s -t some_table"}}' "$A" "$B" | bash "$G" >/dev/null 2>&1
    if [ $? -eq 2 ]; then
        pass "guard-dangerous.sh blocks destructive commands"
    else
        fail "guard-dangerous.sh did NOT block a destructive payload" "hook เป็นหมัน — ตรวจ .claude/hooks/guard-dangerous.sh (เคยพังเพราะหา python3 ไม่เจอ)"
    fi
else
    fail "$G missing" "clone ใหม่ หรือ checkout ไฟล์กลับมา"
fi

D=".claude/hooks/doc-sync-check.sh"
if [ -f "$D" ]; then
    printf '{"stop_hook_active":true}' | CLAUDE_PROJECT_DIR="$(pwd)" bash "$D" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        pass "doc-sync-check.sh loop guard works"
    else
        fail "doc-sync-check.sh loop guard broken" "ตรวจ .claude/hooks/doc-sync-check.sh"
    fi
else
    fail "$D missing" "clone ใหม่ หรือ checkout ไฟล์กลับมา"
fi

# --- 13 dataform (optional) ---------------------------------------------------
echo
echo "[dataform]"
if command -v dataform >/dev/null 2>&1; then
    pass "dataform CLI: $(dataform --version 2>&1 | head -1)"
else
    skip "dataform CLI not installed" "ไม่บังคับ — compile/run ผ่าน Dataform UI บน GCP"
fi

echo
echo "----------------------------------------"
printf 'PASS %d   FAIL %d   SKIP %d\n' "$PASS" "$FAIL" "$SKIP"
[ "$FAIL" -gt 0 ] && exit 1
exit 0
