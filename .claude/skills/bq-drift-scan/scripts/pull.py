# -*- coding: utf-8 -*-
"""Rebuild a .sqlx view from the live BigQuery definition.

  python pull.py --scratchpad <dir> --view view_dim_invoice
  python pull.py --scratchpad <dir> --view view_dim_invoice --apply

BigQuery is the source of truth: the SQL body is taken verbatim and the only
edit is turning literal databuffet-nonprd.<ds>.<tbl> paths into the repo's
reference convention. config {} is preserved; dependencies[] only gains entries.
"""
import argparse, io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (REPO, DB, DS_VAR, REF_DS, NOT_DATAFORM, name_to_dataset,
                    grab_block, load_dump, sqlx_files)

ap = argparse.ArgumentParser()
ap.add_argument("--scratchpad", required=True)
ap.add_argument("--view", required=True, help="object name, e.g. view_dim_invoice")
ap.add_argument("--apply", action="store_true")
args = ap.parse_args()

path = next((p for p in sqlx_files(os.path.join("definitions", "view"))
             if os.path.basename(p)[:-5] == args.view), None)
if not path:
    sys.exit("no .sqlx found for %s" % args.view)

bq = load_dump(args.scratchpad)
body = next((v[1] for k, v in bq.items() if k[1] == args.view), None)
if body is None:
    sys.exit("%s is not in bq_dump.json" % args.view)

defined = {os.path.basename(p)[:-5] for p in sqlx_files()}
src = io.open(path, encoding="utf-8", newline="").read()
cfg = grab_block(src, "config {")
jsb = grab_block(src, "js {") or ""

# reuse const names already in the file so the diff stays small
existing = {m.group(2): m.group(1) for m in
            re.finditer(r"const\s+(\w+)Table\s*=\s*\{[^}]*?name:\s*\"([^\"]+)\"", jsb, re.S)}

pascal = lambda t: "".join(w[:1].upper() + w[1:] for w in t.split("_"))

used, added, refs_used = {}, [], set()
for ds, tbl in sorted(set(re.findall(
        r"%s\.([a-z_0-9]+)\.([A-Za-z_0-9]+)" % re.escape(DB), body))):
    refs_used.add((ds, tbl))
    if ds in REF_DS:
        used[(ds, tbl)] = '${ref(databuffet.%s, "%s")}' % (REF_DS[ds], tbl)
        continue
    base = existing.get(tbl) or pascal(tbl)
    used[(ds, tbl)] = "${%sTableRef}" % base
    if tbl not in existing:
        added.append((base, ds, tbl))
    existing.setdefault(tbl, base)

# BigQuery strips backticks from table paths in view_definition, and the bare
# form is not valid SQL (hyphenated project id). Always re-add them for js-block
# refs; ${ref()} is left bare because Dataform quotes it itself.
for (ds, tbl), rep in sorted(used.items(), key=lambda x: -len(x[0][1])):
    quoted = rep if rep.startswith("${ref(") else "`%s`" % rep
    body = body.replace("`%s.%s.%s`" % (DB, ds, tbl), quoted)
    body = body.replace("%s.%s.%s" % (DB, ds, tbl), quoted)

lines, seen = ["js {"], set()
for ds, tbl in sorted(refs_used):
    if ds in REF_DS or tbl in seen:
        continue
    seen.add(tbl)
    c = existing[tbl]
    lines += ["    const %sTable = {" % c,
              "        database: databuffet.DATABASE,",
              "        schema: databuffet.%s," % DS_VAR[ds],
              '        name: "%s",' % tbl,
              "    };",
              "    const %sTableRef = `${%sTable.database}.${%sTable.schema}.${%sTable.name}`;" % (c, c, c, c),
              ""]
if lines[-1] == "":
    lines.pop()
lines.append("}")

dep_m = re.search(r"dependencies:\s*\[(.*?)\]", cfg, re.S)
cur = [x.strip().strip("\"'") for x in dep_m.group(1).split(",") if x.strip()] if dep_m else []
new = [t for (ds, t) in sorted(refs_used)
       if ds not in NOT_DATAFORM and ds not in REF_DS and t in defined and t not in cur]
cfg = re.sub(r"dependencies:\s*\[.*?\]",
             "dependencies: [%s]" % ", ".join('"%s"' % d for d in cur + new), cfg, flags=re.S)

out = cfg + "\n\n" + "\n".join(lines) + "\n\n" + body.strip() + "\n"
leftover = re.findall(r"%s\.[a-z_0-9]+\.[A-Za-z_0-9]+" % re.escape(DB), out)

cbefore = len([l for l in src.split("\n") if l.strip().startswith("--")])
cafter = len([l for l in out.split("\n") if l.strip().startswith("--")])

print("%s: body=%d chars | new consts=%d | deps added=%s | leftover literal paths=%d"
      % (args.view, len(body), len(added), new or "-", len(leftover)))
for c, ds, t in added:
    print("   + const %sTableRef -> %s.%s" % (c, ds, t))
if cafter < cbefore:
    print("   ! comment lines %d -> %d (BigQuery drops commented-out blocks on save;"
          " the old text is still in git history)" % (cbefore, cafter))
if leftover:
    print("   !! LEFTOVER LITERAL PATHS:", set(leftover))

if args.apply:
    io.open(path, "w", encoding="utf-8", newline="\n").write(out)
    print("written -> %s" % os.path.relpath(path, REPO))
    print("now run: scan.py --check-backticks")
else:
    print("DRY RUN -- pass --apply to write")
