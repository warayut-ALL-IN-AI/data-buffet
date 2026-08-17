#!/bin/bash
# Stop hook: before Claude ends its turn, if code changed but document/ didn't,
# force one re-check of doc impact. Exit 2 = block stop (stderr shown to Claude).
#
# No Python dependency on purpose — this hook must behave identically on Git Bash
# (Windows) and WSL/Linux. A missing interpreter used to break the loop guard.

INPUT=$(cat)

# Prevent infinite loop: if we already blocked once this stop sequence, allow.
echo "$INPUT" | grep -qE '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Status codes are columns 1-2; the path starts at column 4 (keeps spaces intact).
CHANGED=$(git status --porcelain 2>/dev/null | cut -c4-)
[ -z "$CHANGED" ] && exit 0

CODE_TOUCHED=$(echo "$CHANGED" | grep -cE '^(definitions/|includes/|workflow_settings)')
DOC_TOUCHED=$(echo "$CHANGED"  | grep -cE '^document/')

if [ "$CODE_TOUCHED" -gt 0 ] && [ "$DOC_TOUCHED" -eq 0 ]; then
    cat >&2 <<'MSG'
DOC-SYNC CHECK: มีการแก้ definitions/ หรือ includes/ แต่ document/ ยังไม่ถูกแตะ
ก่อนจบ turn ให้ประเมินตามตารางใน .claude/skills/update-docs/SKILL.md:
- เพิ่ม/ลบตาราง → inventory ของ layer + จำนวนไฟล์ใน README/architecture
- เปลี่ยน pattern → หน้า pattern + coding-standards
- tag/dataset/helper ใหม่ → project_wiki/includes/* + CLAUDE.md
- ตัดสินใจเชิงออกแบบ → operations/known-issues.md (ลงวันที่)
ถ้ากระทบ: อัปเดต document/ ให้เสร็จก่อนจบ (ใช้ skill update-docs ได้)
ถ้าไม่กระทบ (เช่น bug fix ที่ pattern ไม่เปลี่ยน): แจ้งผู้ใช้สั้น ๆ ว่าประเมินแล้วไม่กระทบเอกสาร แล้วจบ turn ได้เลย
MSG
    exit 2
fi

exit 0
