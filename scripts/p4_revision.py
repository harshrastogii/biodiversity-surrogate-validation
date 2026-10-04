#!/usr/bin/env python
"""
p4_revision.py — pre-submission robustness analyses (RESEARCH_LOG P4). Run AFTER p3_*.py.
Nothing here replaces the P3 outputs; it adds the checks a Q1 referee will ask for, and
corrects two inferential weaknesses. Everything is reported, whatever it shows.

 R1  Small-k meta-analysis. DerSimonian–Laird (DL) Wald CIs are anti-conservative with k = 3–4
     studies; we add the Hartung–Knapp–Sidik–Jonkman (HKSJ) CI (t_{k-1}) and its conservative
     "modified" form (q floored at 1), for every pooled estimate incl. the circularity partial.
     Per-catchment z and bootstrap variances are saved so the meta can be re-done by anyone.
 R2  Incremental value of combining, done PAIRED. p3_joint.py differenced bootstrap replicates
     of the joint and single models that were drawn independently (different tiles, folds and
     complete-case sets), which is not a valid CI for a difference. Here every model is fitted
     on the SAME rows with the SAME folds (repeated R times), and Δρ is bootstrapped by
     resampling the SAME tiles for both models. The comparator (NVIS) is fixed a priori.
     Skill is reported both pooled across catchments (as P3) and within catchments (mean of
     per-catchment ρ), because pooling mixes between-catchment differences in BIORISK.
 R3  Decision-relevant screening metrics. Per catchment: AUC for separating expert high-risk
     units (BIORISK ≥ 4) from the rest (E-UNIT), and the top-20%-area capture enrichment
     (share of high-risk area inside the 20% of area a surrogate ranks highest, ÷ 0.20; 1 = no
     better than random). Tie groups are split proportionally so coarse surrogates are not
     favoured by arbitrary tie order.
 R5  NVIS class sensitivity: leave-one-rare-vegetation-group-out (see nvis_class_sensitivity).
 R6  Multiverse / specification curve over defensible analyst choices (metric & estimand incl. a
     proper area-weighted rank correlation, minimum mapping unit for sliver polygons, BIORISK-1
     exclusion) with a PAIRED NVIS - land-system difference per specification.
 R4  Modification sensitivity. BIORISK 1 = "nil / highly modified". Surrogates derived from land
     use (convertibility) can re-read modification rather than biodiversity value, so the E-UNIT
     meta is repeated excluding BIORISK-1 polygons.

Writes analysis_p4/{report.txt, per_catchment_z.csv, meta_hksj.csv, joint_paired.csv,
screening.csv, modification_sensitivity.csv, nvis_class_sensitivity.csv, verdict.json}.
Surrogates are rounded to 4 d.p. (config.load_polygons) — constant-after-rounding = non-estimable.
"""
import os, sys, json, warnings
import numpy as np, pandas as pd
from scipy.stats import rankdata, norm, kendalltau, t as tdist
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
from centroids import centroids

OUT = os.path.join(C.V2, "analysis_p4"); os.makedirs(OUT, exist_ok=True)
SURR = ["sig_landsys", "sig_nvis_mvg", "cond_dea", "convertibility", "protection"]
CORE = ["sig_landsys", "sig_nvis_mvg", "convertibility", "protection"]
TILE_M = 10000; B = 2000; R_CV = 20; K_FOLD = 10; HIGH = 4; TOP_AREA = 0.20
SEED = 42

# ---------------------------------------------------------------------------- data
def load_pool():
    poly = C.load_polygons()
    frames = []
    for n in C.BIORISK_POOL + ["Weddell"]:
        d = poly[poly.catchment == n].merge(centroids(n), on="unit_id")
        frames.append(d)
    D = pd.concat(frames, ignore_index=True)
    D["pool"] = D.catchment.isin(C.BIORISK_POOL)       # Weddell kept for separate reporting only
    D["tile"] = (D["catchment"] + "_" + (D.cx // TILE_M).astype(int).astype(str) + "_"
                 + (D.cy // TILE_M).astype(int).astype(str))
    return D

# ---------------------------------------------------------------------------- stats helpers
def wspear(x, y, w=None):
    """Spearman; with w, area-weighted Pearson of ranks (as in P3, for comparability)."""
    rx, ry = rankdata(x), rankdata(y)
    if w is None:
        if np.ptp(rx) == 0 or np.ptp(ry) == 0: return np.nan
        return np.corrcoef(rx, ry)[0, 1]
    w = np.asarray(w, float); w = w / w.sum()
    mx, my = np.sum(w * rx), np.sum(w * ry)
    vx, vy = np.sum(w * (rx - mx) ** 2), np.sum(w * (ry - my) ** 2)
    return np.sum(w * (rx - mx) * (ry - my)) / np.sqrt(vx * vy) if vx > 0 and vy > 0 else np.nan

def auc(score, high):
    """P(score_high > score_low) with ties counted 1/2 (Mann–Whitney)."""
    high = np.asarray(high, bool); n1, n0 = high.sum(), (~high).sum()
    if n1 == 0 or n0 == 0: return np.nan
    r = rankdata(score)
    return (r[high].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

def capture_enrichment(score, area, high, frac=TOP_AREA):
    """share of high-risk area inside the top `frac` of total area ranked by score, / frac.
    Tie groups at the cut are included proportionally (no arbitrary tie order)."""
    df = pd.DataFrame({"s": score, "a": area, "h": np.where(high, area, 0.0)})
    g = df.groupby("s", sort=True)[["a", "h"]].sum().iloc[::-1]   # descending score
    tot_a, tot_h = g.a.sum(), g.h.sum()
    if tot_h <= 0 or tot_a <= 0: return np.nan
    budget, got = frac * tot_a, 0.0
    for a, h in zip(g.a.values, g.h.values):
        take = min(1.0, budget / a) if a > 0 else 0.0
        got += take * h; budget -= take * a
        if budget <= 1e-12: break
    return (got / tot_h) / frac

def tile_index(tiles):
    u = np.unique(tiles); return u, {t: np.where(tiles == t)[0] for t in u}

def block_boot(stat, tiles, rng, b=B):
    """block bootstrap of stat(idx) resampling tiles with replacement."""
    u, by = tile_index(tiles)
    if len(u) < 3: return np.array([])
    out = np.empty(b)
    for i in range(b):
        idx = np.concatenate([by[t] for t in rng.choice(u, len(u), replace=True)])
        try: out[i] = stat(idx)
        except Exception: out[i] = np.nan
    return out[np.isfinite(out)]

def meta(ys, vs):
    """random-effects meta on an additive scale: DL, HKSJ, modified HKSJ (q>=1)."""
    ys, vs = np.asarray(ys, float), np.asarray(vs, float)
    ok = np.isfinite(ys) & np.isfinite(vs) & (vs > 0); ys, vs = ys[ok], vs[ok]; k = len(ys)
    nan = dict(est=np.nan, dl_lo=np.nan, dl_hi=np.nan, dl_p=np.nan, hk_lo=np.nan, hk_hi=np.nan,
               hk_p=np.nan, mhk_lo=np.nan, mhk_hi=np.nan, mhk_p=np.nan, tau2=np.nan, I2=np.nan, k=k)
    if k == 0: return nan
    w = 1 / vs; yf = np.sum(w * ys) / np.sum(w); Q = float(np.sum(w * (ys - yf) ** 2))
    Cc = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / Cc) if (Cc > 0 and k > 1) else 0.0
    wr = 1 / (vs + tau2); mu = np.sum(wr * ys) / np.sum(wr); se = np.sqrt(1 / np.sum(wr))
    I2 = max(0.0, (Q - (k - 1)) / Q) * 100 if Q > 0 else 0.0
    r = dict(nan, est=mu, dl_lo=mu - 1.96 * se, dl_hi=mu + 1.96 * se,
             dl_p=2 * (1 - norm.cdf(abs(mu / se))), tau2=tau2, I2=I2, k=k)
    if k >= 2:
        q = np.sum(wr * (ys - mu) ** 2) / (k - 1); tc = tdist.ppf(0.975, k - 1)
        for tag, qq in [("hk", q), ("mhk", max(q, 1.0))]:
            s = np.sqrt(qq / np.sum(wr))
            r[f"{tag}_lo"], r[f"{tag}_hi"] = mu - tc * s, mu + tc * s
            r[f"{tag}_p"] = 2 * (1 - tdist.cdf(abs(mu / s), k - 1))
    return r

def z(r): return np.arctanh(np.clip(r, -0.999, 0.999))

def meta_auc(aucs, variances):
    """pool AUCs on the logit scale (delta-method variances) so intervals stay inside (0, 1)."""
    a = np.clip(np.asarray(aucs, float), 1e-3, 1 - 1e-3); v = np.asarray(variances, float)
    m = meta(np.log(a / (1 - a)), v / (a * (1 - a)) ** 2)
    return back(m, lambda x: 1 / (1 + np.exp(-x)))

def back(m, f):
    """back-transform a meta dict's estimate/limits with f (tanh for Fisher z)."""
    o = dict(m)
    for key in ["est", "dl_lo", "dl_hi", "hk_lo", "hk_hi", "mhk_lo", "mhk_hi"]:
        o[key] = float(f(m[key])) if np.isfinite(m[key]) else np.nan
    return o

def partial_rank(sub, idx):
    R = {c: rankdata(sub[c].values[idx]) for c in ["sig_nvis_mvg", "biorisk_awm", "sig_landsys", "convertibility"]}
    Z = np.c_[np.ones(len(idx)), R["sig_landsys"], R["convertibility"]]
    rx = R["sig_nvis_mvg"] - Z @ np.linalg.lstsq(Z, R["sig_nvis_mvg"], rcond=None)[0]
    ry = R["biorisk_awm"] - Z @ np.linalg.lstsq(Z, R["biorisk_awm"], rcond=None)[0]
    return np.corrcoef(rx, ry)[0, 1]

# ---------------------------------------------------------------------------- R1 + R4
def per_catchment_z(D, rng, exclude_class1=False, catchments=None):
    """per-catchment rho + block-bootstrap Fisher-z variance. E-AREA uses area-weighted mid-ranks
    (weighted ECDF; wspear_ecdf), which replaces P3's unweighted-rank weighted Pearson."""
    rows = []
    for name in (catchments or C.BIORISK_POOL):
        d = D[D.catchment == name]
        if exclude_class1: d = d[d.biorisk_awm > 1]
        for s in SURR:
            for est, wtd in [("E-UNIT", False), ("E-AREA", True)]:
                if exclude_class1 and wtd: continue
                sub = d[[s, "biorisk_awm", "unit_km2", "tile"]].dropna()
                if len(sub) < 6 or sub[s].nunique() < 2 or sub.biorisk_awm.nunique() < 2: continue
                x, y = sub[s].values, sub.biorisk_awm.values
                w = sub.unit_km2.values
                fn = (lambda i: wspear_ecdf(x[i], y[i], w[i])) if wtd else (lambda i: wspear(x[i], y[i]))
                obs = fn(np.arange(len(sub)))
                bs = block_boot(fn, sub.tile.values, rng)
                rows.append(dict(catchment=name, quantity=s, estimand=est, rho=obs, z=z(obs),
                                 z_var=float(np.var(z(bs))) if len(bs) > 10 else np.nan,
                                 n=len(sub), n_tiles=sub.tile.nunique()))
        if not exclude_class1:  # NVIS circularity partial
            sub = d[["sig_nvis_mvg", "biorisk_awm", "sig_landsys", "convertibility", "tile"]].dropna()
            if len(sub) >= 12:
                obs = partial_rank(sub, np.arange(len(sub)))
                bs = block_boot(lambda i: partial_rank(sub, i), sub.tile.values, rng)
                rows.append(dict(catchment=name, quantity="nvis_partial", estimand="E-UNIT", rho=obs,
                                 z=z(obs), z_var=float(np.var(z(bs))) if len(bs) > 10 else np.nan,
                                 n=len(sub), n_tiles=sub.tile.nunique(), n_boot_ok=len(bs)))
    return pd.DataFrame(rows)

def pool_z(per):
    out = []
    for (q, est), g in per.groupby(["quantity", "estimand"], sort=False):
        m = back(meta(g.z.values, g.z_var.values), np.tanh)
        ok = g[np.isfinite(g.z_var) & (g.z_var > 0)]
        loo = [float(np.tanh(meta(ok.z.drop(i).values, ok.z_var.drop(i).values)["est"]))
               for i in ok.index] if len(ok) >= 3 else []
        out.append(dict(quantity=q, estimand=est, **m, catchments=";".join(ok.catchment),
                        loo_min=min(loo) if loo else np.nan, loo_max=max(loo) if loo else np.nan))
    return pd.DataFrame(out)

# ---------------------------------------------------------------------------- R2
def fit_predict(tr, te, preds):
    X = tr[preds].values; y = tr["biorisk_awm"].values
    mu = X.mean(0); sd = X.std(0); sd[sd == 0] = 1
    beta = np.linalg.lstsq(np.c_[np.ones(len(X)), (X - mu) / sd], y, rcond=None)[0]
    return np.c_[np.ones(len(te)), (te[preds].values - mu) / sd] @ beta

def oof_predictions(d, models, rng):
    """repeated spatial-block CV; identical folds for every model; oof preds averaged over repeats."""
    tiles = d.tile.unique(); P = {m: np.zeros(len(d)) for m in models}
    pos = {t: np.where(d.tile.values == t)[0] for t in tiles}
    for _ in range(R_CV):
        folds = np.array_split(rng.permutation(tiles), K_FOLD)
        for f in folds:
            te = np.concatenate([pos[t] for t in f]); trm = np.ones(len(d), bool); trm[te] = False
            for m, preds in models.items():
                P[m][te] += fit_predict(d.iloc[trm], d.iloc[te], preds) / R_CV
    return P

def skill(pred, d, idx, mode):
    if mode == "pooled":
        return wspear(pred[idx], d.biorisk_awm.values[idx])
    vals = []
    cat = d.catchment.values[idx]
    for c in np.unique(cat):
        j = idx[cat == c]
        if len(j) >= 6: vals.append(wspear(pred[j], d.biorisk_awm.values[j]))
    vals = [v for v in vals if np.isfinite(v)]
    return np.mean(vals) if vals else np.nan

def paired_joint(D, rng):
    d = D.dropna(subset=CORE + ["biorisk_awm"]).reset_index(drop=True)
    models = {"CORE_joint": CORE, "sig_nvis_mvg": ["sig_nvis_mvg"], "convertibility": ["convertibility"],
              "sig_landsys": ["sig_landsys"]}
    P = oof_predictions(d, models, rng)
    u, by = tile_index(d.tile.values)
    cats = d.catchment.values
    rows = []
    for mode in ["pooled", "within"]:
        allidx = np.arange(len(d))
        obs = {m: skill(P[m], d, allidx, mode) for m in models}
        bs = {m: [] for m in models}; bd = []
        for _ in range(B):
            # stratified by catchment: resample tiles within each catchment
            pick = []
            for c in C.BIORISK_POOL:
                tc = [t for t in u if t.startswith(c + "_")]
                if tc: pick += list(rng.choice(tc, len(tc), replace=True))
            idx = np.concatenate([by[t] for t in pick])
            vals = {m: skill(P[m], d, idx, mode) for m in models}
            for m in models: bs[m].append(vals[m])
            bd.append(vals["CORE_joint"] - vals["sig_nvis_mvg"])
        for m in models:
            lo, hi = np.nanpercentile(bs[m], [2.5, 97.5])
            rows.append(dict(mode=mode, model=m, n=len(d), test_rho=obs[m], ci_lo=lo, ci_hi=hi))
        lo, hi = np.nanpercentile(bd, [2.5, 97.5])
        rows.append(dict(mode=mode, model="DELTA joint-NVIS (paired)", n=len(d),
                         test_rho=obs["CORE_joint"] - obs["sig_nvis_mvg"], ci_lo=lo, ci_hi=hi,
                         p_le0=float(np.mean(np.array(bd) <= 0))))
    # leave-one-catchment-out for the joint model (single-surrogate LOCO is, by construction,
    # ± the raw within-catchment correlation, so only the joint model's weight transfer is tested)
    loco = {}
    for c in C.BIORISK_POOL:
        te = d[d.catchment == c]; tr = d[d.catchment != c]
        if len(te) >= 6:
            loco[c] = dict(joint=wspear(fit_predict(tr, te, CORE), te.biorisk_awm.values),
                           nvis_raw=wspear(te.sig_nvis_mvg.values, te.biorisk_awm.values), n=len(te))
    return pd.DataFrame(rows), loco

# ---------------------------------------------------------------------------- R3
def screening(DA, rng):
    """threshold-specific discrimination: AUC for BIORISK>=4 and for BIORISK==5, plus area capture."""
    rows = []
    for name in C.BIORISK_POOL + ["Weddell"]:
        d = DA[DA.catchment == name]
        for s in SURR:
            sub = d[[s, "biorisk_awm", "unit_km2", "tile"]].dropna()
            if len(sub) < 6 or sub[s].nunique() < 2: continue
            x, a = sub[s].values, sub.unit_km2.values
            for thr_name, hi_ in [(">=4", (sub.biorisk_awm >= HIGH).values), ("==5", (sub.biorisk_awm == 5).values)]:
                if hi_.all() or not hi_.any(): continue
                bs = block_boot(lambda i: auc(x[i], hi_[i]), sub.tile.values, rng)
                rows.append(dict(catchment=name, surrogate=s, threshold=thr_name, n=len(sub),
                                 n_high=int(hi_.sum()), auc=auc(x, hi_),
                                 auc_var=float(np.var(bs)) if len(bs) > 10 else np.nan,
                                 capture_enrichment_top20=capture_enrichment(x, a, hi_)))
    per = pd.DataFrame(rows)
    pooled = []
    for (s, thr), g in per[per.catchment != "Weddell"].groupby(["surrogate", "threshold"], sort=False):
        m = meta_auc(g.auc.values, g.auc_var.values)
        pooled.append(dict(surrogate=s, threshold=thr, **m, mean_enrichment=g.capture_enrichment_top20.mean()))
    return per, pd.DataFrame(pooled)

def nvis_class_sensitivity(DA):
    """R5: is the NVIS signal carried by a few rare vegetation groups? E-UNIT Spearman per catchment
    (i) all polygons, (ii) dropping each common rare-MVG rarity value in turn, (iii) dropping all
    polygons with NVIS rarity >= 0.25. Polygons are attributed to an MVG value by rounding the
    area-weighted rarity to 3 d.p. (mixed polygons fall between class values and are kept)."""
    rows = []
    for name in C.BIORISK_POOL + ["Weddell"]:
        d = DA[DA.catchment == name][["sig_nvis_mvg", "biorisk_awm"]].dropna()
        if len(d) < 6 or d.sig_nvis_mvg.nunique() < 2: continue
        v = d.sig_nvis_mvg.round(3)
        rho = lambda m: wspear(d.sig_nvis_mvg.values[m], d.biorisk_awm.values[m]) if m.sum() >= 6 else np.nan
        rows.append(dict(catchment=name, drop="none", n_dropped=0, rho=rho(np.ones(len(d), bool))))
        common = v.value_counts(); common = common[(common.index >= 0.25) & (common >= max(5, 0.01 * len(d)))]
        for val, cnt in common.items():
            m = (v != val).values
            share4 = float((d.biorisk_awm[v == val] >= HIGH).mean())
            rows.append(dict(catchment=name, drop=f"rarity={val:.3f} (share BIORISK>=4: {share4:.2f})",
                             n_dropped=int(cnt), rho=rho(m)))
        m = (d.sig_nvis_mvg < 0.25).values
        rows.append(dict(catchment=name, drop="all rarity>=0.25", n_dropped=int((~m).sum()), rho=rho(m)))
    return pd.DataFrame(rows)

# ---------------------------------------------------------------------------- R6 multiverse
def wrank(x, w):
    """area-weighted mid-ranks (weighted ECDF): rank of a value = cumulative weight below + half its own."""
    o = pd.Series(w, index=x).groupby(level=0).sum().sort_index()
    cw = o.cumsum() - o / 2
    return pd.Series(x).map(cw).values

def wspear_ecdf(x, y, w):
    rx, ry = wrank(x, w), wrank(y, w); w = np.asarray(w, float) / np.sum(w)
    mx, my = np.sum(w * rx), np.sum(w * ry)
    vx, vy = np.sum(w * (rx - mx) ** 2), np.sum(w * (ry - my) ** 2)
    return np.sum(w * (rx - mx) * (ry - my)) / np.sqrt(vx * vy) if vx > 0 and vy > 0 else np.nan

METRICS = {  # name -> f(x, y, w) ; every metric is "higher = surrogate agrees more with experts"
    "spearman_unit": lambda x, y, w: wspear(x, y),
    "spearman_area": lambda x, y, w: wspear_ecdf(x, y, w),
    "auc_ge4":       lambda x, y, w: auc(x, y >= HIGH),
    "auc_eq5":       lambda x, y, w: auc(x, y == 5),
    "kendall_tau_b": lambda x, y, w: kendalltau(x, y).statistic,
}
MMU_HA = [0, 0.1, 1.0]   # minimum polygon size (ha): none; 0.1 ha; one 100 m NVIS pixel
B_MV = 500

def multiverse(D, rng):
    """R6: every combination of defensible analyst choices (metric/estimand x minimum mapping unit x
    exclusion of BIORISK-1). For each specification: per-catchment estimate for every surrogate and
    the PAIRED difference NVIS - land-system (same bootstrap tiles), pooled by RE meta (DL point,
    modified-HKSJ CI). Answers: does the verdict 'which surrogate is best' survive the choices?"""
    rows, drows = [], []
    for metric, fn in METRICS.items():
        for mmu in MMU_HA:
            for ex1 in [False, True]:
                per, dper = [], []
                for name in C.BIORISK_POOL:
                    d = D[(D.catchment == name) & (D.unit_km2 * 100 >= mmu)]
                    if ex1: d = d[d.biorisk_awm > 1]
                    for s in SURR:
                        sub = d[[s, "biorisk_awm", "unit_km2", "tile"]].dropna()
                        if len(sub) < 6 or sub[s].nunique() < 2 or sub.biorisk_awm.nunique() < 2: continue
                        x, y, w = sub[s].values, sub.biorisk_awm.values, sub.unit_km2.values
                        obs = fn(x, y, w)
                        if not np.isfinite(obs): continue
                        bs = block_boot(lambda i: fn(x[i], y[i], w[i]), sub.tile.values, rng, B_MV)
                        per.append((s, name, obs, np.var(bs) if len(bs) > 10 else np.nan))
                    sub = d[["sig_nvis_mvg", "sig_landsys", "biorisk_awm", "unit_km2", "tile"]].dropna()
                    if len(sub) >= 6 and sub.sig_nvis_mvg.nunique() > 1 and sub.sig_landsys.nunique() > 1 \
                            and sub.biorisk_awm.nunique() > 1:
                        a, b_, y, w = sub.sig_nvis_mvg.values, sub.sig_landsys.values, sub.biorisk_awm.values, sub.unit_km2.values
                        diff = lambda i: fn(a[i], y[i], w[i]) - fn(b_[i], y[i], w[i])
                        obs = diff(np.arange(len(sub)))
                        if np.isfinite(obs):
                            bs = block_boot(diff, sub.tile.values, rng, B_MV)
                            dper.append((name, obs, np.var(bs) if len(bs) > 10 else np.nan))
                spec = dict(metric=metric, mmu_ha=mmu, exclude_class1=ex1)
                P = pd.DataFrame(per, columns=["s", "c", "e", "v"])
                for s, g in P.groupby("s"):
                    m = (meta_auc(g.e.values, g.v.values) if metric.startswith("auc")
                         else back(meta(z(g.e.values), g.v.values / (1 - np.clip(g.e.values, -0.999, 0.999) ** 2) ** 2), np.tanh))
                    rows.append(dict(spec, surrogate=s, est=m["est"], lo=m["mhk_lo"], hi=m["mhk_hi"], k=m["k"]))
                Dd = pd.DataFrame(dper, columns=["c", "e", "v"])
                m = meta(Dd.e.values, Dd.v.values)
                drows.append(dict(spec, diff_nvis_minus_landsys=m["est"], lo=m["mhk_lo"], hi=m["mhk_hi"],
                                  dl_lo=m["dl_lo"], dl_hi=m["dl_hi"], k=m["k"]))
    mv, dv = pd.DataFrame(rows), pd.DataFrame(drows)
    best = (mv[mv.surrogate.isin(["sig_landsys", "sig_nvis_mvg", "cond_dea", "convertibility"])]
            .sort_values("est").groupby(["metric", "mmu_ha", "exclude_class1"]).tail(1)
            .rename(columns={"surrogate": "best_surrogate", "est": "best_est"})
            [["metric", "mmu_ha", "exclude_class1", "best_surrogate", "best_est"]])
    dv = dv.merge(best, on=["metric", "mmu_ha", "exclude_class1"], how="left")
    return mv, dv

def mmu_table(DA):
    """per-catchment E-UNIT Spearman of each surrogate as small polygons are removed (no bootstrap)."""
    rows = []
    for name in C.BIORISK_POOL + ["Weddell"]:
        for mmu in [0, 0.01, 0.1, 0.5, 1.0, 5.0]:
            d = DA[(DA.catchment == name) & (DA.unit_km2 * 100 >= mmu)]
            for s in SURR:
                sub = d[[s, "biorisk_awm"]].dropna()
                ok = len(sub) >= 6 and sub[s].nunique() > 1 and sub.biorisk_awm.nunique() > 1
                rows.append(dict(catchment=name, mmu_ha=mmu, surrogate=s, n=len(sub),
                                 rho=wspear(sub[s].values, sub.biorisk_awm.values) if ok else np.nan))
    return pd.DataFrame(rows)

def benchmark_table(DA):
    """Table 1 inputs: polygons, area, class counts, polygon-size distribution, 10 km tiles."""
    rows = []
    for name in C.BIORISK_POOL + ["Weddell"]:
        d = DA[DA.catchment == name]; a_ha = d.unit_km2 * 100
        cls = d.biorisk_awm.value_counts().sort_index()
        rows.append(dict(catchment=name, n_polygons=len(d), area_km2=d.unit_km2.sum(),
                         classes=", ".join(f"{int(k)}:{v}" for k, v in cls.items()),
                         median_polygon_ha=a_ha.median(), pct_lt_1ha=100 * (a_ha < 1).mean(),
                         n_tiles_10km=d.tile.nunique()))
    return pd.DataFrame(rows)

def spec_curve(dv, path):
    """specification curve: paired NVIS - land-system difference across all specifications."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    d = dv.sort_values("diff_nvis_minus_landsys").reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1.6]))
    col = np.where(d.lo > 0, "#009E73", np.where(d.hi < 0, "#D55E00", "#7F7F7F"))
    a1.errorbar(d.index, d.diff_nvis_minus_landsys, yerr=[d.diff_nvis_minus_landsys - d.lo, d.hi - d.diff_nvis_minus_landsys],
                fmt="none", ecolor=col, lw=0.8)
    a1.scatter(d.index, d.diff_nvis_minus_landsys, c=col, s=14, zorder=3); a1.axhline(0, color="k", lw=0.6)
    a1.set_ylabel("NVIS − land-system\n(paired, pooled; mHKSJ 95% CI)")
    labels = [("metric", m) for m in METRICS] + [("mmu_ha", v) for v in MMU_HA] + [("exclude_class1", True)]
    for j, (k, v) in enumerate(labels):
        on = (d[k] == v).values
        a2.scatter(np.where(on)[0], np.full(on.sum(), j), s=8, color="k")
    a2.set_yticks(range(len(labels))); a2.set_yticklabels([f"{k}={v}" for k, v in labels], fontsize=7)
    a2.set_xlabel("specification (sorted by estimate)")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)

# ---------------------------------------------------------------------------- main
def main():
    DA = load_pool(); D = DA[DA.pool].reset_index(drop=True)
    rng = np.random.default_rng(SEED)
    per = per_catchment_z(D, rng); pooled = pool_z(per)
    per_wed = per_catchment_z(DA, rng, catchments=["Weddell"])   # separate scheme: never pooled
    per_wed.to_csv(os.path.join(OUT, "weddell.csv"), index=False)
    mmu_table(DA).to_csv(os.path.join(OUT, "mmu_per_catchment.csv"), index=False)
    benchmark_table(DA).to_csv(os.path.join(OUT, "benchmarks.csv"), index=False)
    per_nc1 = per_catchment_z(D, rng, exclude_class1=True); pooled_nc1 = pool_z(per_nc1)
    joint, loco = paired_joint(D, rng)
    scr_per, scr_pool = screening(DA, rng)
    mvg = nvis_class_sensitivity(DA)
    mv, dv = multiverse(D, rng)
    mv.to_csv(os.path.join(OUT, "multiverse_surrogates.csv"), index=False)
    dv.to_csv(os.path.join(OUT, "multiverse_nvis_vs_landsys.csv"), index=False)
    spec_curve(dv, os.path.join(OUT, "specification_curve.png"))

    per.to_csv(os.path.join(OUT, "per_catchment_z.csv"), index=False)
    pooled.to_csv(os.path.join(OUT, "meta_hksj.csv"), index=False)
    pooled_nc1.to_csv(os.path.join(OUT, "modification_sensitivity.csv"), index=False)
    per_nc1.to_csv(os.path.join(OUT, "modification_per_catchment.csv"), index=False)
    pd.DataFrame([dict(catchment=c, **v) for c, v in loco.items()]).to_csv(os.path.join(OUT, "loco.csv"), index=False)
    joint.to_csv(os.path.join(OUT, "joint_paired.csv"), index=False)
    scr_per.to_csv(os.path.join(OUT, "screening.csv"), index=False)
    mvg.to_csv(os.path.join(OUT, "nvis_class_sensitivity.csv"), index=False)

    f = lambda v: f"{v:+.3f}" if np.isfinite(v) else "  n/a "
    L = ["P4 REVISION ANALYSES (pre-submission audit)",
         f"tiles={TILE_M//1000} km, B={B}, CV repeats={R_CV}x{K_FOLD}-fold, seed={SEED}", "",
         "R1  POOLED rho: DL (as P3) vs HKSJ vs modified-HKSJ 95% CI, k = estimable catchments",
         f"  {'quantity':16s} {'est':6s} {'rho':>7s} {'DL CI':>17s} {'HKSJ CI':>17s} {'mHKSJ CI':>17s} {'p_mHK':>6s} {'I2':>4s} k  LOO range"]
    for _, r in pooled.iterrows():
        L.append(f"  {r.quantity:16s} {r.estimand:6s} {f(r.est)} [{f(r.dl_lo)},{f(r.dl_hi)}] "
                 f"[{f(r.hk_lo)},{f(r.hk_hi)}] [{f(r.mhk_lo)},{f(r.mhk_hi)}] {r.mhk_p:6.3f} {r.I2:4.0f} {r.k}  "
                 f"[{f(r.loo_min)},{f(r.loo_max)}]  ({r.catchments})")
    L += ["  Weddell (BioValues scheme, separate): " + "  ".join(
          f"{r.quantity}/{r.estimand}={f(r.rho)}" for _, r in per_wed.iterrows())]
    L += ["", "R4  MODIFICATION SENSITIVITY: E-UNIT excluding BIORISK class 1 (nil/highly modified)"]
    for _, r in pooled_nc1.iterrows():
        L.append(f"  {r.quantity:16s} {f(r.est)} DL[{f(r.dl_lo)},{f(r.dl_hi)}] mHKSJ[{f(r.mhk_lo)},{f(r.mhk_hi)}] k={r.k}")
    L += ["", "R2  JOINT vs NVIS — same rows, same folds, paired tile bootstrap (stratified by catchment)"]
    for _, r in joint.iterrows():
        extra = f"  P(Δ<=0)={r.p_le0:.3f}" if "DELTA" in r.model else ""
        L.append(f"  {r['mode']:7s} {r.model:26s} {f(r.test_rho)} [{f(r.ci_lo)},{f(r.ci_hi)}] n={r.n}{extra}")
    L += ["  LOCO (joint weights transferred to a held-out catchment) vs NVIS raw within-catchment rho:"]
    for c, v in loco.items():
        L.append(f"    {c:10s} joint={f(v['joint'])}  nvis_raw={f(v['nvis_raw'])}  n={v['n']}")
    L += ["", f"R3  SCREENING: threshold-specific AUC (E-UNIT; RE meta over BIORISK pool) and top-{int(TOP_AREA*100)}%-area capture enrichment (1 = random)"]
    for _, r in scr_pool.iterrows():
        L.append(f"  {r.surrogate:16s} {r.threshold:3s} AUC={r.est:.3f} DL[{r.dl_lo:.3f},{r.dl_hi:.3f}] mHKSJ[{r.mhk_lo:.3f},{r.mhk_hi:.3f}] "
                 f"k={r.k}  mean enrichment={r.mean_enrichment:.2f}")
    L.append("  per catchment, AUC>=4 / AUC==5 / enrichment(>=4)   [Weddell = separate scheme, not pooled]:")
    for name in C.BIORISK_POOL + ["Weddell"]:
        g = scr_per[scr_per.catchment == name]; parts = []
        for s_ in SURR:
            a4 = g[(g.surrogate == s_) & (g.threshold == ">=4")]; a5 = g[(g.surrogate == s_) & (g.threshold == "==5")]
            if len(a4) or len(a5):
                parts.append(f"{s_.split('_')[-1][:4]}:" + (f"{a4.auc.iloc[0]:.2f}" if len(a4) else "n/a") + "/"
                             + (f"{a5.auc.iloc[0]:.2f}" if len(a5) else "n/a") + "/"
                             + (f"{a4.capture_enrichment_top20.iloc[0]:.2f}" if len(a4) else "n/a"))
        L.append(f"    {name:10s} " + "  ".join(parts))
    L += ["", "R5  NVIS CLASS SENSITIVITY (E-UNIT Spearman; is the signal carried by a few rare MVGs?)"]
    for _, r in mvg.iterrows():
        L.append(f"  {r.catchment:10s} drop {r['drop']:45s} n_dropped={r.n_dropped:6d}  rho={f(r.rho)}")
    L += ["", "R6  MULTIVERSE / SPECIFICATION CURVE: metric x minimum mapping unit x exclude BIORISK-1",
          f"  {len(dv)} specifications. Paired NVIS - land-system difference (pooled, mHKSJ CI) and best surrogate:"]
    for _, r in dv.iterrows():
        L.append(f"  {r.metric:14s} mmu={r.mmu_ha:<4} ex1={str(r.exclude_class1):5s} diff={f(r.diff_nvis_minus_landsys)} "
                 f"[{f(r.lo)},{f(r.hi)}] k={r.k}  best={r.best_surrogate} ({f(r.best_est)})")
    n = len(dv)
    L += [f"  SUMMARY: NVIS significantly better in {int((dv.lo > 0).sum())}/{n}; land-system significantly better in "
          f"{int((dv.hi < 0).sum())}/{n}; inconclusive in {int(((dv.lo <= 0) & (dv.hi >= 0)).sum())}/{n}.",
          "  best surrogate by specification: " + ", ".join(f"{k}={v}" for k, v in dv.best_surrogate.value_counts().items())]
    report = "\n".join(L); print(report)
    open(os.path.join(OUT, "report.txt"), "w").write(report + "\n")
    json.dump(dict(meta=pooled.to_dict("records"), modification=pooled_nc1.to_dict("records"),
                   joint=joint.to_dict("records"), loco=loco, screening=scr_pool.to_dict("records"),
                   nvis_class_sensitivity=mvg.to_dict("records"),
                   multiverse=dv.to_dict("records")),
              open(os.path.join(OUT, "verdict.json"), "w"), indent=2, default=float)
    # R4 for Greater Weddell (separate scheme, never pooled). Own generator, so every result above
    # is unchanged by this addition.
    per_catchment_z(DA, np.random.default_rng(SEED + 1), exclude_class1=True, catchments=["Weddell"]) \
        .to_csv(os.path.join(OUT, "modification_weddell.csv"), index=False)
    print("\nwrote", OUT)

if __name__ == "__main__":
    main()
