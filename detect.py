"""Step 1: detect the load (crates + pallet) and the wheels in every frame of a time window.

Usage: python detect.py --video challenge_720p.mp4 --start 20.9 --end 23.0 --out results/det_side.json
"""
import argparse, json, cv2
from ultralytics import YOLOE

CLASSES = ["red forklift truck", "forklift mast", "wheel", "stack of plastic crates", "wooden pallet"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True); ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--weights", default="yoloe-11l-seg.pt")
    a = ap.parse_args()
    model = YOLOE(a.weights)                      # open-vocabulary detector, no training needed
    model.set_classes(CLASSES, model.get_text_pe(CLASSES))
    cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS)
    k0, k1 = int(a.start * fps), int(a.end * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, k0); out = {"fps": fps, "frames": {}}
    for k in range(k0, k1):
        ok, frame = cap.read()
        if not ok: break
        r = model.predict(frame, conf=0.1, verbose=False, imgsz=1280)[0]
        dets = []
        for i, b in enumerate(r.boxes):
            poly = r.masks.xy[i].tolist() if r.masks is not None else []
            dets.append({"cls": CLASSES[int(b.cls)], "conf": round(float(b.conf), 3),
                         "box": [float(v) for v in b.xyxy[0]], "poly": poly[::2]})
        out["frames"][k] = dets
    json.dump(out, open(a.out, "w"))
    print(f"saved {len(out['frames'])} frames to {a.out}")

if __name__ == "__main__":
    main()
