"""
Replicates solution0.m pipeline and saves one JPEG per stage to data/stages/.
Run from the repo root: python3 src/generate_previews.py
"""

import numpy as np
import tifffile
from PIL import Image
import os

OUT_DIR = "data/stages"
os.makedirs(OUT_DIR, exist_ok=True)
MAX_W = 900  # output width for web

def save(arr, name):
    """Clip, scale to uint8, resize, save."""
    a = np.clip(arr, 0, 1)
    a = (a * 255).astype(np.uint8)
    img = Image.fromarray(a)
    w, h = img.size
    if w > MAX_W:
        img = img.resize((MAX_W, int(h * MAX_W / w)), Image.LANCZOS)
    img.save(os.path.join(OUT_DIR, name), quality=88)
    print(f"  saved {name}  {img.size}")

print("Loading banana_slug.tiff ...")
raw = tifffile.imread("data/banana_slug.tiff").astype(np.float64)
Ysize, Xsize = raw.shape
print(f"  shape: {raw.shape}, dtype: {raw.dtype}, range: {raw.min():.0f}–{raw.max():.0f}")

# ── Stage 1: Linearization ──────────────────────────────────────────────────
print("Stage 1: Linearization")
black, saturation = 2047, 15000
lin = (raw - black) / (saturation - black)
lin = np.clip(lin, 0, 1)
# visualise as grayscale (Bayer pattern will be visible)
save(np.stack([lin, lin, lin], axis=2), "stage1_linearized.jpg")

# ── Stage 2: Bayer Pattern ID ───────────────────────────────────────────────
print("Stage 2: Bayer Pattern ID — RGGB")
im1 = lin[0::2, 0::2]  # R
im2 = lin[0::2, 1::2]  # G1
im3 = lin[1::2, 0::2]  # G2
im4 = lin[1::2, 1::2]  # B

im_rggb = np.stack([im1, im2, im4], axis=2) * 4
save(np.clip(im_rggb, 0, 1), "stage2_bayer_rggb.jpg")

# ── Stage 3: White Balancing (gray world) ──────────────────────────────────
print("Stage 3: White Balance — gray world")
red   = lin[0::2, 0::2]
green = np.concatenate([lin[0::2, 1::2].ravel(), lin[1::2, 0::2].ravel()])
blue  = lin[1::2, 1::2]

red_mean   = red.mean()
green_mean = green.mean()
blue_mean  = blue.mean()

im_gw = lin.copy()
im_gw[0::2, 0::2] = red  * green_mean / red_mean
im_gw[1::2, 1::2] = blue * green_mean / blue_mean

# demosaic gray-world for visualisation
gw_r = im_gw[0::2, 0::2]
gw_g = (im_gw[0::2, 1::2] + im_gw[1::2, 0::2]) / 2
gw_b = im_gw[1::2, 1::2]
gw_rgb = np.stack([gw_r, gw_g, gw_b], axis=2) * 4
save(np.clip(gw_rgb, 0, 1), "stage3_white_balance_grayworld.jpg")

# ── Stage 4: White Balancing (white world) ─────────────────────────────────
print("Stage 4: White Balance — white world")
red_max   = red.max()
green_max = np.concatenate([lin[0::2, 1::2].ravel(), lin[1::2, 0::2].ravel()]).max()
blue_max  = blue.max()

im_ww = lin.copy()
im_ww[0::2, 0::2] = red  * green_max / red_max
im_ww[1::2, 1::2] = blue * green_max / blue_max

ww_r = im_ww[0::2, 0::2]
ww_g = (im_ww[0::2, 1::2] + im_ww[1::2, 0::2]) / 2
ww_b = im_ww[1::2, 1::2]
ww_rgb = np.stack([ww_r, ww_g, ww_b], axis=2) * 4
save(np.clip(ww_rgb, 0, 1), "stage4_white_balance_whiteworld.jpg")

# ── Stage 5: Demosaicing (bilinear, on white-world image) ──────────────────
print("Stage 5: Demosaicing")
from scipy.interpolate import RegularGridInterpolator

im = im_ww

def demosaic_channel(values, row_start, col_start):
    """Bilinear interpolation of a Bayer sub-grid to full resolution."""
    rows_known = np.arange(row_start, Ysize, 2)
    cols_known = np.arange(col_start, Xsize, 2)
    interp = RegularGridInterpolator(
        (rows_known, cols_known), values,
        method='linear', bounds_error=False, fill_value=None
    )
    all_rows = np.arange(Ysize)
    all_cols = np.arange(Xsize)
    rr, cc = np.meshgrid(all_rows, all_cols, indexing='ij')
    pts = np.stack([rr.ravel(), cc.ravel()], axis=1)
    return interp(pts).reshape(Ysize, Xsize)

red_dms   = demosaic_channel(im[0::2, 0::2], 0, 0)
blue_dms  = demosaic_channel(im[1::2, 1::2], 1, 1)
green1_dms = demosaic_channel(im[0::2, 1::2], 0, 1)
green2_dms = demosaic_channel(im[1::2, 0::2], 1, 0)
green_dms = (green1_dms + green2_dms) / 2

im_rgb = np.stack([red_dms, green_dms, blue_dms], axis=2)
save(np.clip(im_rgb * 4, 0, 1), "stage5_demosaiced.jpg")

# ── Stage 6: Brightness + Gamma (sRGB IEC 61966-2-1) ──────────────────────
print("Stage 6: Brightness + Gamma correction")
gray = 0.2126 * red_dms + 0.7152 * green_dms + 0.0722 * blue_dms
brightness = 4 * gray.max()
im_bright = np.clip(im_rgb * brightness, 0, 1)

im_final = np.where(
    im_bright <= 0.0031308,
    12.92 * im_bright,
    1.055 * np.power(np.maximum(im_bright, 1e-10), 1 / 2.4) - 0.055
)
save(np.clip(im_final, 0, 1), "stage6_final_srgb.jpg")

print("Done.")
