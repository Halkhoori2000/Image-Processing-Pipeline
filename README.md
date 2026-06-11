# Image Processing Pipeline — RAW to sRGB in MATLAB

*CMPEN 454 — Fundamentals of Computer Vision · The Pennsylvania State University · 2022*

Takes a raw photo straight off a camera sensor — before any processing — and converts it into a normal, viewable colour image. This is the same process that happens inside every digital camera, but built from scratch in code to show how each step works.

Implemented in MATLAB with the core stages built from scratch rather than with built-in image processing routines. The pipeline covers linearization (black-level subtraction and saturation clamping), Bayer pattern identification across all four colour filter arrangements, gray-world and white-world white balancing, bilinear demosaicing by interpolating each colour channel independently, and sRGB gamma correction per the IEC 61966-2-1 transfer function.

**[Pipeline Walkthrough →](https://halkhoori2000.github.io/Image-Processing-Pipeline/)**

## Use Cases
- Digital camera firmware: every smartphone and DSLR runs an equivalent pipeline on raw sensor output before displaying or saving an image
- Computational photography research: HDR imaging, night mode, and portrait mode all build on top of linearised, white-balanced, demosaiced sensor data
- Computer vision preprocessing: machine learning models for detection and segmentation expect linearly scaled RGB input, not gamma-corrected JPEG — this pipeline produces it
- Satellite and aerial imaging: raw sensor data from remote sensing cameras undergoes the same linearisation and demosaicing steps before analysis

## Challenges
- **Bayer pattern identification**: the colour filter arrangement (RGGB, GRBG, BGGR, GBRG) is not stored in the TIFF metadata — the correct pattern must be identified by constructing all four possible quarter-resolution RGB images and selecting the one that produces the most natural colour balance
- **Demosaicing at image boundaries**: bilinear interpolation breaks down at edges where the kernel extends beyond the image — handling border pixels without introducing colour fringing or brightness discontinuities requires careful padding decisions
- **White balance channel ordering**: white balance must scale the raw Bayer channels before demosaicing — applying it after mixes unbalanced values during interpolation; both gray-world and white-world assumptions also fail on scenes that are not neutral in average or maximum luminance, making threshold selection non-trivial

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
Image-Processing-Pipeline/
├── src/
│   └── solution0.m       ← full pipeline implementation
├── data/
│   └── banana_slug.tiff  ← 16-bit Bayer RAW test image
└── index.html            ← pipeline walkthrough (GitHub Pages)
```

---

## Course

CMPEN 454 — Fundamentals of Computer Vision  
The Pennsylvania State University
