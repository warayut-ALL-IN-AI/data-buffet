#!/bin/bash
# PreToolUse guard for Bash commands (wired in .claude/settings.json).
# Blocks destructive operations against live data/infra so they always require
# an explicit user go-ahead. Exit 2 = block (stderr is shown to Claude).
#
# Runs on Git Bash (Windows) and WSL/Linux alike — see the interpreter probe below.

INPUT=$(cat)

# --- extract tool_input.command ----------------------------------------------
# Pick the first Python that actually RUNS. On Windows `command -v python3`
# resolves to the Microsoft Store shim: it exists, prints an ad, and exits
# non-zero — which used to leave CMD empty and make this whole guard a no-op.
# If no interpreter works we scan the raw JSON payload instead: the patterns
# below still match, at the cost of the occasional false positive. Never fail open.
PY=""
for c in python3 python py; do
    if command -v "$c" >/dev/null 2>&1 && "$c" --version >/dev/null 2>&1; then
        PY="$c"; break
    fi
done

CMD=""
if [ -n "$PY" ]; then
    CMD=$("$PY" -c "
import json,sys
try:
    d = json.loads(sys.stdin.read() or '{}')
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" <<< "$INPUT")
fi

# Fallback: no interpreter, or the payload had no command field.
[ -z "$CMD" ] && CMD="$INPUT"
[ -z "$CMD" ] && exit 0

block() {
    echo "BLOCKED by .claude/hooks/guard-dangerous.sh: $1" >&2
    echo "คำสั่งนี้ทำลายข้อมูล/โครงสร้างจริง — ต้องให้ user ยืนยันหรือรันเองเท่านั้น อย่าพยายามเลี่ยง guard; อธิบายให้ user ตัดสินใจ" >&2
    exit 2
}

# 1) Dataform destructive tags/actions
echo "$CMD" | grep -qiE 're-initial'        && block "dataform re-initial drops validated/curated tables"
echo "$CMD" | grep -qiE 'drop_all_tables'   && block "drop_all_tables action"
echo "$CMD" | grep -qiE 'dataform run.*--full-refresh' && block "full-refresh rebuilds incremental tables"

# 2) bq: any write/DDL statement (SELECT-only is allowed)
if echo "$CMD" | grep -qE '(^|[[:space:];&|])bq[[:space:]]'; then
    echo "$CMD" | grep -qiE '\b(DELETE|DROP|TRUNCATE|MERGE|INSERT|UPDATE|ALTER|CREATE)\b' \
        && block "bq with DML/DDL keyword"
    echo "$CMD" | grep -qiE '\bbq[[:space:]]+(rm|cp|load|mk|update)\b' \
        && block "bq destructive subcommand"
fi

# 3) gcloud / gsutil destructive subcommands
echo "$CMD" | grep -qiE '\bgcloud\b.*\b(delete|destroy)\b' && block "gcloud delete"
echo "$CMD" | grep -qiE '\bgsutil\b.*\b(rm|rsync[^|]*-d)\b' && block "gsutil rm / rsync -d"

# 4) git history rewrites / force pushes
echo "$CMD" | grep -qiE 'git[[:space:]]+push[^|;&]*(--force|-f\b)' && block "git force push"
echo "$CMD" | grep -qiE 'git[[:space:]]+reset[[:space:]]+--hard[[:space:]]+origin' && block "git hard reset to remote"

exit 0
