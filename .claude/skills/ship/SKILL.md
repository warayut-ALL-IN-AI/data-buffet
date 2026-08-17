---
name: ship
description: Commit working-tree changes and sync branches — push dev, fast-forward nonprod, push. Use when the user says commit/push/"เอาขึ้น dev nonprod"/ship.
---

The team's standard release flow (dev → nonprod are kept identical; nonprod is
always a fast-forward of dev).

Arguments: `$ARGUMENTS` = optional commit message override.

Steps:
1. `git status --short` + `git diff --stat` — review what's changing. If the set
   mixes unrelated work, split into separate commits (user's own edits vs Claude's —
   ask if ownership is unclear; the user sometimes commits their own files separately
   without the co-author line).
2. Must be on `dev` (if not, stop and ask). Stage explicitly by path — no `git add -A`
   blind adds.
3. Commit: short imperative subject; body bullets for multi-part changes; end with
   `Co-Authored-By:` line per harness rules.
4. `git push origin dev`
5. `git checkout nonprod && git merge dev --ff-only && git push origin nonprod && git checkout dev`
   — if `--ff-only` fails, **stop** and report (nonprod has diverged; do not merge
   or rebase without the user).
6. Verify: `git status --short` clean, `git log --oneline -3`, both branches on the
   same commit. Report the commit hash and what went out.

Never: force push, rebase, or touch `prod`/`hotfix` (user handles those).
