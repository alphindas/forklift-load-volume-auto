"""Step 4: combine height + crate counts + EUR pallet size into a volume with an uncertainty range.

Assumption: the crates fill the EUR pallets exactly, 9 crates per pallet layer (3 x 3),
so one crate covers (1.2 x 0.8) / 9 m^2. Fill 90-100 % allows for gaps between crates.
Usage: python volume.py --height results/height.json --counts results/counts.json --out results/volume.json
"""
import argparse, json, numpy as np

EUR_PALLET_M2 = 1.2 * 0.8
CRATES_PER_PALLET_LAYER = 9

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--height", required=True); ap.add_argument("--counts", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    H = np.array([r["height_m"] for r in json.load(open(a.height))["rows"]]); C = json.load(open(a.counts))["summary"]
    crates_per_layer = C["side"] * C["front"]
    footprint = crates_per_layer * EUR_PALLET_M2 / CRATES_PER_PALLET_LAYER
    depth = C["front"] * 1.2 / 3; length = C["side"] * 0.8 / 3
    rng = np.random.default_rng(0); N = 10000
    h = rng.choice(H, N) * (1 + rng.uniform(-0.03, 0.03, N)); fill = rng.uniform(0.9, 1.0, N)
    v = footprint * h * fill
    res = {"crates": f"{C['side']} x {C['front']} x {C['layers']}", "depth_m": round(depth, 2), "length_m": round(length, 2),
           "footprint_m2": round(footprint, 2), "height_median_m": round(float(np.median(H)), 3),
           "solid_box_m3": round(float(footprint * np.median(H)), 2),
           "volume_m3": {"median": round(float(np.median(v)), 2), "p10": round(float(np.percentile(v, 10)), 2), "p90": round(float(np.percentile(v, 90)), 2)},
           "assumptions": ["front tyre about 0.822 m (datasheet) is the ruler", "crates fill the pallets: 9 per EUR pallet layer", "fill 90-100 %"]}
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main()
