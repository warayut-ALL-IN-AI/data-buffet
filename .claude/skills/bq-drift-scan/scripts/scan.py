# -*- coding: utf-8 -*-
"""Diff every .sqlx view and UDF against the live BigQuery definition.

  python scan.py --scratchpad <dir>                    full drift report
  python scan.py --scratchpad <dir> --check-backticks  post-pull safety check

Needs <dir>/bq_dump.json (see SKILL.md step 1).
"""
import argparse, difflib, io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (REPO, DB, BT, name_to_dataset, render, unescape_comments,
                    norm, norm_lines, load_dump, grab_block, sqlx_files)

ap = argparse.ArgumentParser()
ap.add_argument("--scratchpad", required=True)
ap.add_argument("--check-backticks", action="store_true")
args = ap.parse_args()

n2ds = name_to_dataset()

# ---------------------------------------------------------------- backtick check
if args.check_backticks:
    bad = ok = lit = 0
    for p in sqlx_files():
        t = io.open(p, encoding="utf-8").read()
        js = grab_block(t, "js {")
        body = t[t.find(js) + len(js):] if js else t
        rel = os.path.relpath(p, REPO)
        for m in re.finditer(r"(.?)\$\{(\w+TableRef)\}(.?)", body):
            if m.group(1) == BT and m.group(3) == BT:
                ok += 1
            else:
                bad += 1
                print("  NO BACKTICK   %s  ...%s..." % (rel, m.group(0)))
        for m in re.finditer(r"%s\.[a-z_0-9]+\.[A-Za-z_0-9]+" % re.escape(DB), body):
            lit += 1
            print("  LITERAL PATH  %s  %s" % (rel, m.group(0)))
    print("\nbackticked refs=%d  unbackticked=%d  literal paths=%d" % (ok, bad, lit))
    sys.exit(1 if (bad or lit) else 0)

# ---------------------------------------------------------------- drift report
bq = load_dump(args.scratchpad)

repo = {}
for p in sqlx_files(os.path.join("definitions", "view")):
    nm = os.path.basename(p)[:-5]
    ds = n2ds.get(nm, "?")
    repo[(ds, nm)] = unescape_comments(render(p, nm, ds, n2ds))

# UDFs: one file holds them all, split on CREATE OR REPLACE FUNCTION
fnfile = os.path.join(REPO, "definitions", "initial", "create_all_function.sqlx")
if os.path.exists(fnfile):
    src = render(fnfile, "create_all_function", "function_dataset", n2ds)
    for part in re.split(r"(?=CREATE\s+OR\s+REPLACE\s+FUNCTION)", src, flags=re.I):
        m = re.search(r"FUNCTION\s+`[^`]*\.([A-Za-z0-9_]+)`", part, re.I)
        if m:
            repo[("function_dataset", m.group(1))] = part.strip().rstrip(";").strip()

def fn_norm(t):
    return re.sub(r"CREATE\s+OR\s+REPLACE\s+FUNCTION", "CREATE FUNCTION",
                  norm(t), flags=re.I).rstrip(";").strip()

same, diff = [], []
for k in sorted(repo):
    if k not in bq:
        continue
    f = fn_norm if k[0] == "function_dataset" else norm
    a, b = f(repo[k]), f(bq[k][1])
    if a == b:
        same.append(k)
    else:
        diff.append((k, difflib.SequenceMatcher(None, a, b).ratio()))

missing = [k for k in repo if k not in bq]
extra = [k for k in bq if k not in repo]

print("repo objects %d | identical %d | DIFFERENT %d | missing in BQ %d | extra in BQ %d"
      % (len(repo), len(same), len(diff), len(missing), len(extra)))

print("\n-- DIFFERENT (worst first) --")
for (ds, nm), r in sorted(diff, key=lambda x: x[1]):
    print("   %-16s %-40s sim=%.3f" % (ds, nm, r))
print("\n-- MISSING IN BIGQUERY (in repo, never deployed) --")
for ds, nm in sorted(missing):
    print("   %s.%s" % (ds, nm))
print("\n-- EXTRA IN BIGQUERY (not in repo) --")
for ds, nm in sorted(extra):
    print("   %s.%s" % (ds, nm))

warn = [(k, set(re.findall(r"<<UNRESOLVED:[^>]*>>|<<FD:[^>]*>>", repo[k]))) for k in sorted(repo)]
warn = [w for w in warn if w[1]]
if warn:
    print("\n-- RENDER WARNINGS (renderer bug, not drift) --")
    for k, u in warn:
        print("   %s.%s -> %s" % (k[0], k[1], u))

dd = os.path.join(args.scratchpad, "diffs")
os.makedirs(dd, exist_ok=True)
for (ds, nm), _ in diff:
    io.open(os.path.join(dd, "%s__%s.diff" % (ds, nm)), "w", encoding="utf-8").write(
        "\n".join(difflib.unified_diff(norm_lines(repo[(ds, nm)]), norm_lines(bq[(ds, nm)][1]),
                                       "REPO/" + nm, "BQ/%s.%s" % (ds, nm), lineterm="", n=2)))
print("\ndiffs -> %s" % dd)
