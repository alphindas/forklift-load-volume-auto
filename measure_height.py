"""Step 2: measure the load height in each side-view frame, using the front wheel as the ruler.

Known sizes: front tyre 315/70-15 -> about 0.822 m tall (Linde E80 datasheet); EUR pallet height 0.144 m.
Usage: python measure_height.py --det results/det_side.json --out results/height.json
"""
import argparse, json, numpy as np

TYRE_M = 0.822
PALLET_H_M = 0.144

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--det", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); D = json.load(open(a.det)); fps = D["fps"]; rows = []
    for k, dets in sorted(D["frames"].items(), key=lambda x: int(x[0])):
        crates = [x for x in dets if x["cls"] == "stack of plastic crates" and x["conf"] > 0.3 and x["box"][0] > 600 and x["poly"]]
        wheels = [x for x in dets if x["cls"] == "wheel" and x["conf"] > 0.15]
        if not crates or not wheels: continue
        c = max(crates, key=lambda x: x["conf"]); x1, y1, x2, y2 = c["box"]; w = x2 - x1
        if x2 > 1275: continue                                   # load cut off by the image edge
        fw = min(wheels, key=lambda x: abs((x["box"][0] + x["box"][2]) / 2 - x1))   # wheel next to the load
        fx = (fw["box"][0] + fw["box"][2]) / 2
        if not (x1 - 220 < fx < x1 + 80): continue
        wheel_px = fw["box"][3] - fw["box"][1]
        P = np.array(c["poly"])
        near = P[(P[:, 0] >= x1 + 0.03 * w) & (P[:, 0] <= x1 + 0.12 * w)]       # near end of the load
        if len(near) < 4: continue
        load_px = near[:, 1].max() - near[:, 1].min()
        height = load_px * TYRE_M / wheel_px - PALLET_H_M
        rows.append({"frame": int(k), "time_s": round(int(k) / fps, 2), "height_m": round(float(height), 3), "wheel_px": round(float(wheel_px), 1)})
    H = np.array([r["height_m"] for r in rows])
    summary = {"frames_used": len(rows), "median_m": float(np.median(H)), "p10_m": float(np.percentile(H, 10)), "p90_m": float(np.percentile(H, 90))}
    json.dump({"summary": summary, "rows": rows}, open(a.out, "w"), indent=1)
    print(summary)

if __name__ == "__main__":
    main()
