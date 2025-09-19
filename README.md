# GrapheneOS OLED Wallpaper — *Chic Suite*

Monolithic, no-external-assets Python tool to generate OLED-friendly GrapheneOS wallpapers with luxe vibes: gradient/gloss, tessellated weave, and a controllable “accent” logo (plus a Fingerprint—FP—mode that locks placement & center fill).

This README covers install, usage, options, and the combos you **shouldn’t** use unless you like disappointment.

---

## What you get

- **One-file script** with the GOS SVG embedded:
  - `gos_chic.py`
- **FP mode** (default): accent at the fingerprint target (centered horizontally, **71.8%** from top), **~225%** scale, **gray center fill**; accent outline honors your **style** and **accent color**.
- **Custom accent control**: set X/Y (screen %, not pixels) and size (relative to base tile).
- **Weave + tessellate**: logos “touch” cleanly under rotation.
- **Accent-aware anchoring**: the entire tiled grid *stems from* the accent; the tile under it is skipped; accent is pasted last (z-index above all).

Works great at Pixel 9 Pro XL native res (**1344 × 2992**) and any other dimensions you pass.

---

## Requirements

- Python 3.9+  
- Packages:
  ```bash
  pip install pillow cairosvg
  ```
- On Linux, CairoSVG might need system Cairo/PNG bits (e.g., `libcairo2`, `librsvg2-common`). If `cairosvg` complains, install those via your package manager.

---

## Quick start

### 1) FP “just works” (default)
```bash
python gos_chic.py \\
  --out fp_default.png
```
- Accent: center X, **71.8%** from top
- Size: **2.25×** tile
- Center fill: **#1f1f1f** (dark AOSP gray)
- Outline: honors `--style` + `--accent_color` if you pass them (see below)

### 2) FP, red glossmix, tessellated weave
```bash
python gos_chic.py \\
  --out fp_red_glossmix_weave.png \\
  --style glossmix --accent_color red --weave
```

### 3) Custom placement (disables FP)
```bash
python gos_chic.py \\
  --out custom_topright.png \\
  --fp_mode False \\
  --accent_x 0.75 --accent_y 0.15 --accent_scale 1.0 \\
  --style gradient --weave
```

---

## Options (CLI)

```text
--out PATH                Output PNG (required)
--svg PATH                Optional alternate SVG; omit to use embedded

--width INT               Canvas width  (default 1344)
--height INT              Canvas height (default 2992)
--logo_px INT             Base logo render size in px (default 200) – tiles use this

--style {gradient,glossmix,emboss}
                          Background tile style; also tints accent outline (non-FP).
--accent_color {gold,steel,red,none}
                          Accent outline tint (style-shaped). FP mode also honors this tint/style for the outline.

--weave                   Rotate tiles ±3° in a checker (fabric vibe)
--weave_deg FLOAT         Rotation degrees (default 3.0)
--tessellate              When weaving, make tiles “touch” (default True)

--scalevar                Periodic scale variance (non-tessellated path only)
--scale_every INT         Every N rows (default 4)
--scale_factor FLOAT      Multiplier (default 1.2)

# Accent placement (percent of screen). Grid is anchored to this.
--accent_x FLOAT          0..1, default 0.50 (center X)
--accent_y FLOAT          0..1, default 0.20 (20% down)
--accent_scale FLOAT      Multiple of base logo_px, default 1.0

# Fingerprint (FP) override (ON by default)
--fp_mode {True,False}    Locks placement to FP (center X, 71.8% Y) and forces center gray fill
--fp_center_rgb HEX       Center fill color for FP (default #1f1f1f)
--fp_anchor FLOAT         FP center Y ratio (default 0.718)
--fp_scale FLOAT          FP accent scale (default 2.25)
```

> Notes  
> • **Tessellation defaults to on** when weaving; you can explicitly set `--tessellate False` for a looser weave.  
> • In **FP mode**, the center is always flood-filled with `--fp_center_rgb`, and the outline **honors** your `--style` + `--accent_color`.

---

## Disallowed / Ignored combinations

Let’s save you some head-scratching:

- **`--accent_x/--accent_y/--accent_scale` while `--fp_mode True`**  
  FP mode **overrides** these with the locked FP placement/scale. Your custom accent coords/size are **ignored** until you set `--fp_mode False`.

- **`--accent_color none` in FP mode**  
  You’ll still get the **style-shaped** outline (using the script’s default fallback tint if “none” is too ambiguous). If you truly want “no outline,” that’s anti-FP UX; not supported.

- **`--scalevar` with `--weave --tessellate`**  
  Scale variance is **ignored** in the tessellated branch (tiles are pre-rotated, fixed footprint to keep the lattice perfect). Use scalevar in non-tessellated mode.

- **Out-of-range coordinates**  
  `--accent_x/--accent_y` must be **0..1**. Negative or >1 is invalid.  
  `--accent_scale <= 0` is invalid.

- **`--tessellate` without `--weave`**  
  It won’t hurt anything, but tessellation logic only changes behavior under **weave**. Without weave, spacing is controlled by `--spacing` (non-tessellated grid).

---

## Behavior details (so you know it’s not magic)

- **Anchoring**: The accent position defines the origin of the grid. Tiles are placed relative to it; the would-be tile under the accent is **skipped**.  
- **Z-order**: The accent pastes **last**. Nothing overlaps it.  
- **Styles**:
  - `gradient`: OLED-friendly muted top→bottom shade
  - `glossmix`: single-tile glossy gradient (background alternates glossy/matte rows)
  - `emboss`: subtle shadow/press effect  
- **Accent outline styling**:
  - **Non-FP**: outline uses the **same style algorithm** as background, tinted to `--accent_color`.  
  - **FP**: outline **also** honors `--style` + `--accent_color`. The **center** is always filled with `--fp_center_rgb`.

---

## Common recipes

**Pixel-ready FP, gold gradient outline, woven tessellation**
```bash
python gos_chic.py \\
  --out fp_gold_gradient_weave.png \\
  --style gradient --accent_color gold --weave
```

**FP, red gloss outline, no weave (clean grid)**
```bash
python gos_chic.py \\
  --out fp_red_gloss_clean.png \\
  --style glossmix --accent_color red
```

**Custom accent top-right (75%, 15%), same size as tiles, woven**
```bash
python gos_chic.py \\
  --out custom_topright_woven.png \\
  --fp_mode False \\
  --accent_x 0.75 --accent_y 0.15 --accent_scale 1.0 \\
  --style gradient --weave
```

---

## Troubleshooting

- **“`cairosvg` can’t render / missing libs”**  
  Install Cairo-related system packages (`libcairo2`, `librsvg2-common`, `libffi`, etc.).  
- **Accent color looks too bright/dull**  
  Try `glossmix` for more punch or `gradient` for restraint. You can also nudge `--weave_deg` (2–4°) for a different textile feel.  
- **Tessellated weave looks off-grid**  
  You probably rotated too far. Keep `--weave_deg` small (≤5°) to preserve the lattice.

---

## Repo layout (suggested)

```
/ (repo root)
├─ gos_chic.py   # the one-file script (SVG embedded)
├─ README.md                                 # this file
└─ samples/
   ├─ xxx.png
   ├─ yyy.png
   └─ zzz.png
```

---

## License

MIT