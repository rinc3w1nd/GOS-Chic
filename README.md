# GrapheneOS OLED Wallpaper — *Chic Suite*

Monolithic, no-external-assets Python tool to generate OLED-friendly GrapheneOS wallpapers with luxe vibes: gradient/gloss, tessellated weave, and a controllable “accent” logo (plus a Fingerprint—FP—mode that locks placement & center fill).

---

## Defaults

- **Resolution**: 1344 × 2992 (Pixel 9 Pro XL).  
  You can override with `--width`/`--height` or just use `--device CODENAME` to auto-set from a known Pixel model.  
- **Accent placement** (when not in FP mode): center X, **20%** from top, scale = `1.0`.  
- **FP mode**: **off by default**. You must pass `--fp_mode` to enable the fingerprint override.

---

## What you get

- **One-file script** with the GOS SVG embedded
- **FP mode** (opt-in with `--fp_mode`): accent at fingerprint target (centered horizontally, **71.8%** from top), **~225%** scale, **gray center fill**; accent outline honors your **style** and **accent color**.
- **Custom accent control**: set X/Y (screen %, not pixels) and size (relative to base tile).
- **Weave + tessellate**: logos “touch” cleanly under rotation.
- **Accent-aware anchoring**: the entire tiled grid *stems from* the accent; the tile under it is skipped; accent is pasted last (z-index above all).

---

## Requirements

- Python 3.9+  
- Packages:
  ```bash
  pip install pillow cairosvg
  ```

---

## Quick start

### 1) FP mode (opt-in)
```bash
python gos_chic.py   --out fp_default.png   --fp_mode
```

### 2) Custom placement (default)
```bash
python gos_chic.py   --out custom_topright.png   --accent_x 0.75 --accent_y 0.15 --accent_scale 1.0   --style gradient --weave
```

### 3) Auto-resolution by device codename
```bash
python gos_chic.py   --device komodo   --out fp_gold.png   --fp_mode --style gradient --accent_color gold --weave
```
This sets canvas to **1344×2992** for Pixel 9 Pro XL (`komodo`).

---

## Options (CLI)

```text
--out PATH                Output PNG (required)
--svg PATH                Optional alternate SVG; omit to use embedded

--device CODENAME         Pixel codename (e.g. komodo, caiman, tokay). Overrides --width/--height.
--width INT               Canvas width  (default 1344)
--height INT              Canvas height (default 2992)

--style {gradient,glossmix,emboss}
                          Background tile style; also tints accent outline (non-FP).
--accent_color {gold,steel,red,none or R,G,B or #RRGGBB}
                          Accent outline tint. FP mode also honors this tint/style for the outline.

--weave                   Rotate tiles ±3° in a checker (fabric vibe)
--tessellate              When weaving, make tiles “touch” (default True)

--accent_x FLOAT          0..1, default 0.50 (center X)
--accent_y FLOAT          0..1, default 0.20 (20% down)
--accent_scale FLOAT      Multiple of base logo_px, default 1.0

--fp_mode                 Opt-in. Locks placement to FP (center X, 71.8% Y) and forces center gray fill
--fp_center_rgb HEX       Center fill color for FP (default #1f1f1f)
--fp_anchor FLOAT         FP center Y ratio (default 0.718)
--fp_scale FLOAT          FP accent scale (default 2.25)
```

---

## Disallowed / Ignored combinations

- **Custom accent coords while `--fp_mode` is set** → ignored, FP overrides.  
- **Accent color = `none` in FP mode** → outline still drawn, default tint fallback.  
- **Scale variance with `--weave --tessellate`** → ignored (grid locked).  

---

## License

MIT
