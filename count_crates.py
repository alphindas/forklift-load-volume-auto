"""Step 3: count crates along the side, across the front, and the layers, in frames where both faces are visible.

How: inside the detected load outline, the dark bottle openings repeat once per crate.
Peaks in a horizontal profile = crate columns; peaks in a vertical profile = layers.
The corner between side and front is the tallest point of the outline (closest to the camera).
Usage: python count_crates.py --video challenge_720p.mp4 --det results/det_end.json --out results/counts.json
"""
import argparse, json, cv2, numpy as np
from collections import Counter
from scipy.signal import find_peaks

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--det", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); D = json.load(open(a.det)); fps = D["fps"]; cap = cv2.VideoCapture(a.video); rows = []
    for k, dets in sorted(D["frames"].items(), key=lambda x: int(x[0])):
        cs = [x for x in dets if x["cls"].startswith("stack") and 500 < x["box"][0] < 700 and x["conf"] > 0.5 and x["poly"]]
        if not cs: continue
        c = max(cs, key=lambda x: x["conf"])
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(k)); ok, frame = cap.read()
        if not ok: continue
        mask = np.zeros(frame.shape[:2], np.uint8); cv2.fillPoly(mask, [np.int32(c["poly"])], 255)
        xs = np.where(mask.any(0))[0]; x1, x2 = xs.min(), xs.max(); ys = np.where(mask.any(1))[0]; y1, y2 = ys.min(), ys.max()
        if x2 > frame.shape[1] - 10: continue
        # corner = tallest column of the outline
        X = np.arange(x1 + int(0.10 * (x2 - x1)), x2 - int(0.04 * (x2 - x1)))
        hgt = np.array([np.ptp(np.where(mask[:, x])[0]) for x in X])
        sm = np.convolve(hgt, np.ones(15) / 15, "same"); corner = X[np.argmax(sm[10:-10]) + 10]
        dark = ((cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[..., 2] < 90) & (mask > 0)).astype(np.uint8)
        prof = np.convolve(dark[int(y1 + .35 * (y2 - y1)):int(y1 + .75 * (y2 - y1)), x1:x2].sum(0).astype(float), np.ones(5) / 5, "same")
        cols, _ = find_peaks(prof, distance=12, prominence=prof.max() * 0.25); cols = cols + x1
        vprof = np.convolve(dark[y1:y2, int(x1 + .3 * (x2 - x1)):int(x1 + .6 * (x2 - x1))].sum(1).astype(float), np.ones(7) / 7, "same")
        layers, _ = find_peaks(vprof, distance=25, prominence=vprof.max() * 0.3)
        rows.append({"frame": int(k), "time_s": round(int(k) / fps, 2), "side": int((cols < corner).sum()),
                     "front": int((cols > corner).sum()), "layers": int(len(layers))})
    pairs = Counter((r["side"], r["front"]) for r in rows); lay = Counter(r["layers"] for r in rows)
    (side, front), n_pair = pairs.most_common(1)[0]; layers, n_lay = lay.most_common(1)[0]
    summary = {"frames": len(rows), "side": side, "front": front, "layers": layers,
               "frames_agreeing_side_front": n_pair, "frames_agreeing_layers": n_lay,
               "other_readings": [[list(p), n] for p, n in pairs.most_common(5)[1:]]}
    json.dump({"summary": summary, "rows": rows}, open(a.out, "w"), indent=1)
    print(summary)

if __name__ == "__main__":
    main()
