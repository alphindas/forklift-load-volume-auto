# Automatic forklift load volume

Follow-up to my Sentics forklift challenge: [alphindas/sentics-forklift-challenge](https://github.com/alphindas/sentics-forklift-challenge). Source video: [Linde forklift on YouTube](https://www.youtube.com/watch?v=RCqa8Kojlw8).

In the challenge I estimated the load volume by clicking points by hand. This repo does the same job **automatically**: no clicking.
It uses only known sizes: the **EUR pallet (1.2 × 0.8 m)** from the task, and the **front tyre (about 0.82 m)** from the Linde E80 datasheet.

## Result

| | Automatic (this repo) | By hand (challenge) |
|---|---|---|
| Load height | **1.43 m** (1.36 – 1.48, 16 frames) | 1.41 m |
| Crates (side × front × layers) | **9 × 6 × 4** | 9 × 6 × 4 |
| Depth / length | 2.4 m / 2.4 m | 2.4 m / 2.4 m |
| Volume, load only | **7.8 m³** (7.3 – 8.2) | 7.8 m³ (7.1 – 8.5) |

How the number is built: 2.4 × 2.4 m × 1.43 m = 8.2 m³ as a solid box, then 90 – 100 % full to allow for gaps between crates → **7.8 m³**.

## How it works (4 steps)

1. **`detect.py`**: an open-vocabulary detector (YOLOE, no training) finds the load outline (crates + pallet) and the wheels in every frame.
2. **`measure_height.py`**: side view (21.6 – 22.6 s). The front wheel next to the load is the ruler (0.822 m). Height = load outline at its near end × (0.822 / wheel pixels) − 0.144 m pallet.
3. **`count_crates.py`**: view where side and front are both visible (17.9 – 19.4 s). Each crate has dark bottle openings, so peaks in a brightness profile = crate columns and layers. The corner between side and front is the tallest point of the outline.
4. **`volume.py`**: one EUR pallet layer holds 9 crates (3 × 3), so each crate is 0.4 × 0.27 m. Front: 6 × 0.4 = 2.4 m deep. Side: 9 × 0.27 = 2.4 m long. 10,000 random trials over the frame heights and a 90 – 100 % fill give the range.

## Assumptions (not verified)

- **Tyre size as the ruler** (0.822 m, from the datasheet). A 5 % error here is a 5 % error in volume.
- **Crates fill the pallets exactly**, 9 per pallet layer. The crate type is still unknown (the layer height, about 0.35 m, does not match catalogue crates of this footprint).
- **Fill 90 – 100 %** is a judgement, not a measurement.

## Where it fails (honest)

- **Crate counts are noisy.** 9 × 6 was the most common reading but only in 6 of 40 frames; others read 9 × 7, 8 × 5, 8 × 7, and a few frames put the corner in the wrong place. Layers = 4 in all 40 frames.
- **Measuring depth by geometry alone failed.** I tried vanishing points from the outline and from crate-row lines: the front face is too turned in this video, so results ranged from 0.4 to 4.4 m. Counting crates solved it.
- **Automatic length from the side view drifts** (2.2 – 2.8 m) as the forklift turns away, so length also comes from counting.
- **One load, one video, no true answer.** The automatic and hand answers share the pallet reasoning, so their agreement on volume is not fully independent. The independent check is the height (1.43 vs 1.41 m).

## Run it

```bash
pip install -r requirements.txt
# challenge video saved locally as challenge_720p.mp4 (1280×720, 25 fps); not included here
python detect.py --video challenge_720p.mp4 --start 20.9 --end 23.0 --out results/det_side.json
python detect.py --video challenge_720p.mp4 --start 17.9 --end 19.5 --out results/det_end.json
python measure_height.py --det results/det_side.json --out results/height.json
python count_crates.py --video challenge_720p.mp4 --det results/det_end.json --out results/counts.json
python volume.py --height results/height.json --counts results/counts.json --out results/volume.json
```

The `results/` folder already holds the detections and outputs from my run, so steps 2 – 4 can be checked without running the detector.
