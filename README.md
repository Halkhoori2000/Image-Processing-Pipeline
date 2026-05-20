# Image Processing Pipeline — RAW to sRGB in MATLAB

An end-to-end RAW image processing pipeline implemented from scratch in MATLAB, converting a 16-bit Bayer sensor image to a display-ready sRGB output. Each stage is implemented manually without using MATLAB's built-in image processing functions.

**[Pipeline Walkthrough →](https://halkhoori2000.github.io/The-Image-Processing-Pipeline/)**

---

## Pipeline Stages

```
RAW (.tiff)
    │
    ▼
① Linearization          — black-level subtraction, saturation clamp → [0, 1]
    │
    ▼
② Bayer Pattern ID       — test all 4 patterns (GRBG/RGGB/BGGR/GBRG), pick natural-looking one
    │
    ▼
③ White Balancing        — gray-world assumption (mean-normalise per channel)
                         — white-world assumption (max-normalise per channel)
    │
    ▼
④ Demosaicing            — bilinear interpolation per channel (R, G, B independently)
    │
    ▼
⑤ Brightness + Gamma     — brightness scaling, sRGB gamma curve (IEC 61966-2-1)
    │
    ▼
sRGB output image
```

---

## Tech Stack

| Item | Detail |
|---|---|
| Language | MATLAB |
| Input | 16-bit Bayer RAW TIFF (banana slug, 2856 × 4290) |
| Libraries | None — all stages implemented from scratch |

---

## Key Implementation Details

**Linearization**
Applies the affine transform `(raw - black) / (saturation - black)` then clips to [0, 1]. Black level = 2047, saturation = 15000.

**Bayer Pattern Identification**
Constructs four quarter-resolution RGB images (one per Bayer arrangement) and visually selects the pattern that produces the most natural colour balance. Selected: RGGB.

**White Balancing — Gray World**
Assumes the scene average should be neutral gray. Scales each channel by `green_mean / channel_mean`.

**White Balancing — White World**
Assumes the brightest pixel should be white. Scales each channel by `green_max / channel_max`.

**Demosaicing**
Each colour channel (red at odd rows/cols, blue at even rows/cols, two green sub-grids) is interpolated separately using `interp2` (bilinear) to produce a full-resolution channel before compositing into an RGB image.

**Gamma Correction**
Applies the IEC 61966-2-1 sRGB transfer function:
- If `v ≤ 0.0031308`: output = `12.92 × v`
- Otherwise: output = `1.055 × v^(1/2.4) − 0.055`

---

## Run It

**Requirements:** MATLAB (any recent version)

```matlab
% From the repo root in MATLAB
cd src
run('solution0.m')
```

The script displays intermediate figures at each stage and the final sRGB image.

---

## Project Structure

```
The-Image-Processing-Pipeline/
├── src/
│   └── solution0.m       ← full pipeline implementation
├── data/
│   └── banana_slug.tiff  ← 16-bit Bayer RAW test image
└── index.html            ← pipeline walkthrough (GitHub Pages)
```

---

## Course

CMPEN 454 — Computer Vision I  
The Pennsylvania State University
