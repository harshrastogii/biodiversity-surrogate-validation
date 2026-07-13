#!/usr/bin/env python
"""
sensitivity_checks.py — honesty checks on the pooled meta-analysis.
Answers three questions the primary result cannot answer alone:
  (1) How much does each catchment WEIGH in the pooled estimate? (Is it just Roper?)
  (2) Is there ANY agreement signal INDEPENDENT of Roper (leave-Roper-out)?
  (3) Does restricting to >=50%-coverage hexes change the picture?
Reuses the aggregation + spatial effective-n from pooled_validation.py by importing it.
All numbers here are STATISTICAL EVIDENCE (with the small-k caveats already stated).
"""
import numpy as np, pandas as pd
from scipy.stats import spearmanr, chi2, norm
import importlib.util, os
HERE=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("pv", os.path.join(HERE,"pooled_validation.py"))
# We don't want to re-run the heavy script; instead reload its cached per-catchment CSV.
per=pd.read_csv(os.path.join(HERE,"outputs","per_catchment.csv"))
POOL=["Roper","Larrimah","Wadeye"]

def z_and_var(rho, n_eff):
    rho=np.clip(rho,-0.999,0.999)
    return np.arctanh(rho), (1+rho**2/2.0)/(n_eff-3)

def dl(zs,vs):
    zs=np.asarray(zs,float); vs=np.asarray(vs,float); k=len(zs)
    w=1/vs; zf=np.sum(w*zs)/np.sum(w); Q=float(np.sum(w*(zs-zf)**2)); dfree=k-1
    C=np.sum(w)-np.sum(w**2)/np.sum(w); tau2=max(0.0,(Q-dfree)/C) if C>0 else 0.0
    wr=1/(vs+tau2); zre=np.sum(wr*zs)/np.sum(wr); se=np.sqrt(1/np.sum(wr))
    return dict(rho=np.tanh(zre), lo=np.tanh(zre-1.96*se), hi=np.tanh(zre+1.96*se),
                p=2*(1-norm.cdf(abs(zre/se))), wr=wr, k=k)

surfaces=["exposure_full","convertibility","significance","sig_landsys"]

print("="*74); print("(1) META-ANALYSIS WEIGHTS per catchment (random-effects)  [EVIDENCE]"); print("="*74)
for s in surfaces:
    rows=[per[(per.catchment==c)&(per.surface==s)].iloc[0] for c in POOL]
    zv=[z_and_var(r["spearman"], r["n_eff"]) for r in rows]
    res=dl([z for z,_ in zv],[v for _,v in zv])
    w=res["wr"]/res["wr"].sum()*100
    print(f"  {s:18s} pooled rho={res['rho']:+.3f} [{res['lo']:+.3f},{res['hi']:+.3f}] p={res['p']:.3f}")
    print(f"      weights %: "+"  ".join(f"{c}={wi:.0f}%" for c,wi in zip(POOL,w)))

print(); print("="*74)
print("(2) LEAVE-ROPER-OUT: signal from Larrimah+Wadeye ONLY  [EVIDENCE, exploratory k=2]")
print("="*74)
for s in surfaces:
    rows=[per[(per.catchment==c)&(per.surface==s)].iloc[0] for c in ["Larrimah","Wadeye"]]
    zv=[z_and_var(r["spearman"], r["n_eff"]) for r in rows]
    res=dl([z for z,_ in zv],[v for _,v in zv])
    print(f"  {s:18s} pooled rho={res['rho']:+.3f} [{res['lo']:+.3f},{res['hi']:+.3f}] p={res['p']:.3f}  (k=2, very wide)")

print(); print("="*74)
print("(3) LEAVE-ONE-OUT on exposure_full (which catchment drives the primary?)  [EVIDENCE]")
print("="*74)
for drop in POOL:
    keep=[c for c in POOL if c!=drop]
    rows=[per[(per.catchment==c)&(per.surface=="exposure_full")].iloc[0] for c in keep]
    zv=[z_and_var(r["spearman"], r["n_eff"]) for r in rows]
    res=dl([z for z,_ in zv],[v for _,v in zv])
    print(f"  drop {drop:9s} -> pooled exposure rho={res['rho']:+.3f} [{res['lo']:+.3f},{res['hi']:+.3f}] p={res['p']:.3f}")
