#!/usr/bin/env python
"""
check_numbers.py — pre-submission checks on paper/MANUSCRIPT.md.

1. Every number in the Abstract and Results must match a value in the analysis outputs
   (analysis_p4/, analysis_p3/, paper/tables/, data/meta/P4_DATA_CHECKS.md) at the precision printed,
   or be a design constant listed in DESIGN below. Figure, table, section, class and citation-year
   numbers are ignored.
2. No unfilled {{placeholder}} anywhere in the file.
3. Word limits: Abstract <= 300 words; Introduction to the end of the Discussion <= 6,000 words.
4. Anonymity: no author name, ORCID, "Charles Darwin" or GitHub URL in the main file.
5. Citations: every in-text citation has a reference and every reference is cited.

Prints every problem and exits 1 if there is any; prints "OK" and exits 0 otherwise.
"""
import os, re, sys, glob, json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

MS = os.path.join(C.V2, "paper", "MANUSCRIPT.md")
SOURCES = (glob.glob(os.path.join(C.V2, "analysis_p4", "*.csv")) + glob.glob(os.path.join(C.V2, "analysis_p4", "*.txt"))
           + glob.glob(os.path.join(C.V2, "analysis_p3", "*.csv")) + glob.glob(os.path.join(C.V2, "analysis_p3", "*.json"))
           + glob.glob(os.path.join(C.V2, "analysis_p3", "*.txt")) + glob.glob(os.path.join(C.V2, "paper", "tables", "*.md"))
           + [os.path.join(C.V2, "data", "meta", "P4_DATA_CHECKS.md")])
SKIP_FILES = {"run_log.txt"}          # console log, not an output

# Design constants: fixed in the code or the analysis design, not results.
DESIGN = {
    "2,000": "bootstrap replicates (p4_revision.B)", "500": "multiverse replicates", "10": "block size (km) / folds",
    "20": "CV repeats; top-20% area capture", "30": "specifications (5 x 3 x 2)", "5": "metrics / catchments",
    "3": "minimum polygon sizes", "4": "decimal places / BIORISK catchments", "6": "polygon threshold for transfer",
    "0.1": "minimum polygon size (ha)", "0.01": "polygon-size step (ha)", "0.5": "polygon-size step (ha); AUC null",
    "1": "minimum polygon size (ha)", "0.25": "rarity cut-off for rare vegetation groups", "0.2": "area fraction",
    "0.4": "convertibility score threshold", "95": "interval level", "100": "percent", "23": "NVIS MVG code",
}
TOKEN = re.compile(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\d,])|-?\d+(?:\.\d+)?(?:e-?\d+)?")   # numbers in output files
NUM = re.compile(r"(?<![\w.])[−-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\w])|(?<![\w.])[−-]?\d+(?:\.\d+)?(?![\w])")

def section(text, start, end):
    i = text.index(start); j = text.index(end, i)
    return text[i:j]

def value_pool():
    pool = set()
    def add(v):
        try:
            x = float(v)
        except (TypeError, ValueError):
            return
        if x != x:
            return
        for d in range(0, 4):
            for y in (x, abs(x)):
                pool.add(f"{y:.{d}f}"); pool.add(f"{y:,.{d}f}")
        if abs(x) <= 1:                                   # shares written as percentages
            for d in range(0, 2):
                pool.add(f"{100 * abs(x):.{d}f}")
    for f in SOURCES:
        if os.path.basename(f) in SKIP_FILES or not os.path.exists(f):
            continue
        if f.endswith(".csv"):                           # parsed cells, so adjacent cells never merge
            df = pd.read_csv(f)
            for c in df.select_dtypes(exclude="number").columns:
                for cell in df[c].dropna().astype(str):
                    for tok in TOKEN.findall(cell.replace("−", "-")):
                        add(tok.replace(",", ""))
            num = df.select_dtypes("number")
            for v in num.to_numpy().ravel():
                add(v)
            for c in num.columns:                         # column sums (e.g. pooled polygon totals)
                add(num[c].sum())
            if os.path.basename(f) == "benchmarks.csv" and "catchment" in df:
                pool_rows = df[df.catchment.isin(C.BIORISK_POOL)]
                add(pool_rows.n_polygons.sum()); add(pool_rows.n_tiles_10km.sum())
        else:
            txt = open(f, encoding="utf-8", errors="ignore").read().replace("−", "-")
            for tok in TOKEN.findall(txt):
                add(tok.replace(",", ""))
    return pool

def strip_ignored(text):
    text = re.sub(r"\((?:[^()]*?\b(?:19|20)\d{2}[a-z]?)(?:[;,][^()]*?)*\)", " ", text)   # citations
    text = re.sub(r"(Figures?|Tables?|Section|Appendix)\s+S?\d+(?:\.\d+)?[a-d]?(?:\s*[,–-]\s*S?\d+[a-d]?)*", " ", text)
    text = re.sub(r"classe?s?\s*(?:≥|≤|<|>)?\s*\d(?:\s*(?:–|-|or|and|,)\s*\d)*", " ", text)  # class labels
    text = re.sub(r"\{\{[^}]*\}\}", " ", text)
    return text

def main():
    text = open(MS, encoding="utf-8").read()
    problems = []
    # 2. placeholders
    for m in re.finditer(r"\{\{[^}]*\}\}?", text):
        problems.append(f"placeholder left: {m.group(0)[:60]}")
    # 1. numbers
    pool = value_pool()
    parts = {"Abstract": section(text, "## Abstract", "**Keywords:**"),
             "Results": section(text, "## 3. Results", "## 4. Discussion")}
    for name, body in parts.items():
        clean = strip_ignored(body)
        for m in NUM.finditer(clean):
            tok = m.group(0).replace("−", "-").lstrip("-")
            if tok in DESIGN or tok in pool or tok.replace(",", "") in pool:
                continue
            ctx = clean[max(0, m.start() - 50): m.end() + 30].replace("\n", " ")
            problems.append(f"{name}: number not found in outputs: {tok}   …{ctx}…")
    # 3. word limits
    def words(s):
        s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
        s = re.sub(r"[#*_>|`]", " ", s)
        return len(re.findall(r"\S+", s))
    abstract = section(text, "**Aim.**", "**Keywords:**")
    main_text = section(text, "## 1. Introduction", "## Tables")
    wa, wm = words(abstract), words(main_text)
    if wa > 300: problems.append(f"abstract has {wa} words (limit 300)")
    if wm > 6000: problems.append(f"Introduction to end of Discussion has {wm} words (limit 6,000)")
    # 4. anonymity
    for pat in [r"Harsh", r"Rastogi", r"orcid", r"0009-0004-9452-0206", r"Charles Darwin", r"github\.com"]:
        for m in re.finditer(pat, text, flags=re.I):
            problems.append(f"anonymity: '{m.group(0)}' found near …{text[max(0, m.start()-40):m.end()+40]}…".replace("\n", " "))
    # 5. citations <-> references
    body, refs = text.split("## References", 1)
    body = re.sub(r"\s+", " ", re.sub(r"https?://\S+", " ", body))
    keys = set()
    for e in [e.replace("\n", " ") for e in re.split(r"\n\s*\n", refs) if e.strip()]:
        m = re.match(r"\s*(.+?)\.?\s*\((\d{4}[a-z]?|n\.d\.)\)", e)
        if m:
            author = m.group(1)
            first = re.split(r",", author)[0].strip()
            if first.startswith("Department of Climate Change"): first = "DCCEEW"
            keys.add((first, m.group(2)))
    surname = (r"(?:Northern Territory Government|Geoscience Australia|"
               r"Department of Climate Change, Energy, the Environment and Water \[DCCEEW\]|DCCEEW|"
               r"[A-Z][A-Za-zÀ-ÿ'’-]+)")
    cited = set()
    for grp in re.findall(r"\(([^()]*?\d{4}[a-z]?[^()]*?)\)", body):
        for part in re.split(r";", grp):
            m = re.search(r"(" + surname + r")(?: et al\.| (?:&|and) [A-Z][A-Za-zÀ-ÿ'’-]+)?,\s*((?:\d{4}[a-z]?)(?:,\s*\d{4}[a-z]?)*)", part.strip())
            if not m: continue
            a = m.group(1).replace(" [DCCEEW]", "")
            a = "DCCEEW" if a.startswith("Department of Climate") else a
            a = "Northern Territory Government" if a.startswith("Northern") else a
            for y in re.split(r",\s*", m.group(2)):
                cited.add((a, y))
    ref_first = {(k[0].split()[0] if not k[0].startswith(("Northern", "DCCEEW", "Geoscience")) else k[0], k[1]) for k in keys}
    for c in sorted(cited - ref_first):
        problems.append(f"citation without reference: {c}")
    for r in sorted(ref_first - cited):
        problems.append(f"reference never cited: {r}")
    print(f"abstract {wa} words; Introduction–Discussion {wm} words; {len(cited)} citations, {len(ref_first)} references")
    if problems:
        print("\n".join(problems)); print(f"\n{len(problems)} problem(s)"); sys.exit(1)
    print("OK"); sys.exit(0)

if __name__ == "__main__":
    main()
