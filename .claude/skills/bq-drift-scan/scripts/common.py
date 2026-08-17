# -*- coding: utf-8 -*-
"""Shared helpers: render a .sqlx the way Dataform does, and normalise for diffing.

Rendering rules confirmed against the Dataform Compiled queries panel 2026-08-10:
  - SQL code    : backslashes pass through 1:1
  - -- comments : processed as a JS template literal (\\1 -> \1, \\n -> \n)
"""
import io, json, os, re

REPO = os.environ.get("DATABUFFET_REPO", r"D:\github\data-buffet")
DB   = "databuffet-nonprd"

VARS = json.load(io.open(os.path.join(REPO, "includes", "controller", "variables.json"),
                         encoding="utf-8"))

# dataset -> databuffet.* key, for generating js-block consts
DS_VAR = {
    "dimension_table": "DIMENSION_TABLE", "dimension_view": "DIMENSION_VIEW",
    "fact_table": "FACT_TABLE", "fact_view": "FACT_VIEW",
    "mds_dataset": "MDS_DATASET", "function_dataset": "FUNCTION_DATASET",
    "onetime": "ONETIME", "process_dataset": "PROCESS_DATASET",
    "bridge_dataset": "BRIDGE", "cdc_dataset": "CDC_DATESET",
}
# datasets that must go through ${ref()} so Dataform wires the dependency (§3.1)
REF_DS = {
    "validated_mac5": "VALIDATED_MAC5", "validated_cis360": "VALIDATED_CIS360",
    "validated_mastersku": "VALIDATED_MASTERSKU", "validated_saleout_mdt": "VALIDATED_SALEOUT_MDT",
    "curated_mac5": "CURATED_MAC5", "curated_mastersku": "CURATED_MASTERSKU",
    "curated_cis360": "CURATED_CIS360",
}
# not Dataform-managed -> never belongs in dependencies[]
NOT_DATAFORM = {"mds_dataset", "function_dataset"}

BT = chr(96)


def sqlx_files(sub="definitions"):
    for root, _, files in os.walk(os.path.join(REPO, sub)):
        for fn in sorted(files):
            if fn.endswith(".sqlx"):
                yield os.path.join(root, fn)


def name_to_dataset():
    """Every definition's object name -> its dataset."""
    out = {}
    for p in sqlx_files():
        t = io.open(p, encoding="utf-8").read()
        m = re.search(r"schema:\s*([^\s,\n]+)", t)
        if not m:
            continue
        raw = m.group(1).strip().rstrip(",")
        out[os.path.basename(p)[:-5]] = (
            VARS.get(raw.split(".", 1)[1], raw) if raw.startswith("databuffet.")
            else raw.strip("\"'"))
    return out


def grab_block(t, kw):
    """Text of the balanced {...} block introduced by kw, braces included."""
    i = t.find(kw)
    if i == -1:
        return None
    j = t.find("{", i)
    d = 0
    for k in range(j, len(t)):
        if t[k] == "{":
            d += 1
        elif t[k] == "}":
            d -= 1
            if d == 0:
                return t[i:k + 1]
    return None


def strip_block(t, kw):
    while True:
        i = t.find(kw)
        if i == -1:
            return t
        j = t.find("{", i)
        if j == -1:
            return t
        d = 0
        for k in range(j, len(t)):
            if t[k] == "{":
                d += 1
            elif t[k] == "}":
                d -= 1
                if d == 0:
                    t = t[:i] + t[k + 1:]
                    break
        else:
            return t


def _function_data(fn, args):
    col = args[0].strip().strip("\"'") if args else ""
    return {
        "cleanString": "NULLIF(CAST(TRIM(%s) AS STRING), '')" % col,
        "castInt64": "CAST(%s AS INT64)" % col,
        "castFloat64": "CAST(%s AS FLOAT64)" % col,
        "castBool": "CAST(%s AS BOOL)" % col,
        "parseAsatDate": "PARSE_DATE('%Y%m%d', ASATDATE)",
    }.get(fn, "<<FD:%s>>" % fn)


def split_args(s):
    out, depth, cur, q = [], 0, "", None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in "\"'":
            q = ch
            cur += ch
            continue
        if ch in "([":
            depth += 1
        if ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def render(path, selfname, selfds, n2ds=None):
    """Resolve every ${...} in a .sqlx SQL body. Unknowns become <<UNRESOLVED:x>>."""
    n2ds = n2ds if n2ds is not None else name_to_dataset()
    src = io.open(path, encoding="utf-8").read()
    js = grab_block(src, "js {") or ""
    body = src
    for kw in ("config {", "js {", "pre_operations {", "post_operations {"):
        body = strip_block(body, kw)

    objs = {}
    for m in re.finditer(r"const\s+(\w+)\s*=\s*\{(.*?)\}", js, re.S):
        objs[m.group(1)] = {
            k.group(1): k.group(2).strip().rstrip(",").strip()
            for k in re.finditer(r"(database|schema|name)\s*:\s*([^,\n]+)", m.group(2))
        }

    def val(v):
        v = v.strip().rstrip(",").strip()
        if v.startswith("databuffet."):
            k = v.split(".", 1)[1]
            return DB if k == "DATABASE" else VARS.get(k, v)
        return selfname if v == "name()" else v.strip("\"'")

    refs = {}
    for m in re.finditer(r"const\s+(\w+)\s*=\s*`([^`]*)`", js):
        def rep(mm):
            e = mm.group(1).strip()
            om = re.match(r"(\w+)\.(database|schema|name)$", e)
            if om and om.group(1) in objs:
                return val(objs[om.group(1)].get(om.group(2), ""))
            if e.startswith("databuffet."):
                k = e.split(".", 1)[1]
                return DB if k == "DATABASE" else VARS.get(k, e)
            return "${%s}" % e
        refs[m.group(1)] = re.sub(r"\$\{([^}]*)\}", rep, m.group(2))

    def sub(m):
        e = m.group(1).strip()
        if e in refs:
            return refs[e]
        if e == "self()":
            return "%s.%s.%s" % (DB, selfds, selfname)
        if e.startswith("databuffet.functionData."):
            f = re.match(r"databuffet\.functionData\.(\w+)\((.*)\)$", e, re.S)
            if f:
                return _function_data(f.group(1), split_args(f.group(2)))
        if e.startswith("databuffet."):
            k = e.split(".", 1)[1]
            return DB if k == "DATABASE" else VARS.get(k, "${%s}" % e)
        r = re.match(r"ref\((.*)\)$", e, re.S)
        if r:
            a = [x.strip() for x in split_args(r.group(1))]
            if len(a) == 2:
                ds = (VARS.get(a[0].split(".", 1)[1], a[0]) if a[0].startswith("databuffet.")
                      else a[0].strip("\"'"))
                return "%s.%s.%s" % (DB, ds, a[1].strip("\"'"))
            t = a[0].strip("\"'")
            return "%s.%s.%s" % (DB, n2ds.get(t, "?"), t)
        om = re.match(r"(\w+)\.(database|schema|name)$", e)
        if om and om.group(1) in objs:
            return val(objs[om.group(1)].get(om.group(2), ""))
        return "<<UNRESOLVED:%s>>" % e

    prev = None
    while prev != body:
        prev = body
        body = re.sub(r"\$\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", sub, body)
    return body


def comment_pos(line):
    """Index of the -- that starts a comment, honouring quotes. -1 if none."""
    q = None
    i = 0
    while i < len(line):
        ch = line[i]
        if q:
            if ch == q:
                q = None
            i += 1
            continue
        if ch in "\"'" + BT:
            q = ch
            i += 1
            continue
        if ch == "-" and i + 1 < len(line) and line[i + 1] == "-":
            return i
        i += 1
    return -1


def unescape_comments(t):
    """Dataform runs -- comments through the template literal; code is left alone."""
    out = []
    for line in t.split("\n"):
        p = comment_pos(line)
        if p == -1:
            out.append(line)
            continue
        c = re.sub(r"\\(.)",
                   lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)),
                   line[p:])
        out.append(line[:p] + c)
    return "\n".join(out)


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    return "\n".join(
        (line[:comment_pos(line)] if comment_pos(line) != -1 else line)
        for line in t.split("\n"))


def norm(t):
    """Comparison form. NOTE: drops backticks -- see scan.py --check-backticks."""
    return re.sub(r"\s+", " ", strip_comments(t).replace(BT, "")).strip()


def norm_lines(t):
    return [re.sub(r"\s+", " ", l).strip()
            for l in strip_comments(t).replace(BT, "").split("\n") if l.strip()]


def load_dump(scratchpad):
    bq = {}
    p = os.path.join(scratchpad, "bq_dump.json")
    for r in json.load(io.open(p, encoding="utf-8")):
        bq[(r["ds"], r["nm"])] = (r["kind"], r["body"] or "")
    return bq
