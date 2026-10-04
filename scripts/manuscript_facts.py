#!/usr/bin/env python
"""
manuscript_facts.py — descriptive counts quoted in the manuscript that no analysis script writes:
sub-square-metre polygons, class shares, mangrove polygons by class, and how convertibility treats
class 1 and water. No statistics, no resampling. Reads data/processed/ and the NVIS raster (to find
the mangrove rarity value); writes analysis_p4/manuscript_facts.csv. Run after harmonize.py.
"""
import os, sys
import numpy as np, pandas as pd, rasterio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

OUT = os.path.join(C.V2, "analysis_p4"); os.makedirs(OUT, exist_ok=True)
MANGROVES = 23   # NVIS v7 Major Vegetation Group 23 (value attribute table MVG_NAME = "Mangroves")

def nvis_rarity():
    """NT-wide MVG rarity, computed exactly as in harmonize.py."""
    with rasterio.open(C.NVIS_MVG_TIF) as r:
        a = r.read(1)
    codes, counts = np.unique(a[a > 0], return_counts=True)
    keep = np.array([c not in C.NVIS_EXCLUDE for c in codes])
    la = np.log(counts[keep] * 0.01)
    return dict(zip(codes[keep].tolist(), (1 - (la - la.min()) / (la.max() - la.min())).tolist()))

def main():
    poly = C.load_polygons()
    mangrove_rarity = round(nvis_rarity()[MANGROVES], 3)
    rows = []
    def add(catchment, fact, value, description):
        rows.append(dict(catchment=catchment, fact=fact, value=value, description=description))
    add("all", "mangrove_rarity", mangrove_rarity, "NT-wide rarity of NVIS MVG 23 (Mangroves), 3 d.p.")
    for name in C.BIORISK_POOL + ["Weddell"]:
        d = poly[poly.catchment == name]
        cls = d.biorisk_awm.round().astype(int)
        add(name, "n_polygons", len(d), "polygons with a valid class")
        add(name, "n_lt_1m2", int((d.unit_km2 * 1e6 < 1).sum()), "polygons smaller than 1 m2")
        for k, share in (100 * cls.value_counts(normalize=True)).sort_index().items():
            add(name, f"pct_class{k}", round(share, 1), f"% of polygons in class {k}")
        mg = d.sig_nvis_mvg.round(3) == mangrove_rarity
        add(name, "mangrove_n", int(mg.sum()), "polygons attributed to mangroves (rarity rounded to 3 d.p.)")
        add(name, "mangrove_n_class4", int((mg & (cls == 4)).sum()), "of which class 4")
        add(name, "mangrove_n_class_ge4", int((mg & (cls >= 4)).sum()), "of which class 4 or 5")
        c1 = d[(cls == 1) & d.convertibility.notna()]
        if len(c1):
            add(name, "pct_class1_conv_le_0.4", round(100 * (c1.convertibility <= 0.4).mean(), 1),
                "% of class 1 polygons with convertibility <= 0.4 (non-missing)")
        c4 = d[cls == 4]
        if len(c4):
            add(name, "pct_class4_conv_missing", round(100 * c4.convertibility.isna().mean(), 1),
                "% of class 4 polygons with convertibility missing (water)")
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "manuscript_facts.csv"), index=False)
    print(out.to_string(index=False))
    print("\nwrote", os.path.join(OUT, "manuscript_facts.csv"))

if __name__ == "__main__":
    main()
