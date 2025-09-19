#!/usr/bin/env python3
"""
GrapheneOS OLED Wallpaper Generator -- Chic Suite (Monolithic, embedded SVG)

- No external SVG file needed. This script embeds the GOS logo SVG.
- You can still pass --svg to override with a different path if you want.
- Everything else works the same (FP mode, tessellate weave, styles, custom accent control).

Dependencies:
  pip install pillow cairosvg
"""

# ---------------------------- Embedded SVG ----------------------------
EMBEDDED_SVG = r"""<svg height="253.82401" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" viewBox="0 0 2644.0798 2644" width="253.82401" xmlns="http://www.w3.org/2000/svg"><path d="m771.67168 798 381.00032-217c-7.0001-21-12.0001-43-12.0001-67 0-92 67.0001-168 155.0001-184v-330h64v330c88 16 155 92 155 184 0 24-5 46-13 67l382 217c14-16 31-30 50-42 80-46 180-26 237 42l286-165 32 56-286 165c31 84-2 180-82 226-18 10-36 17-55 21v442c19 4 37 11 55 21 80 46 113 142 82 226l286 165-32 56-286-165c-57 68-157 88-237 42-19-12-36-26-50-42-127 72-254 145-382 217 8 21 13 43 13 67 0 92-67 168-155 184v330h-64v-330c-88-16-155.0001-92-155.0001-184 0-24 5-46 12.0001-67l-381.00032-217c-14 16-31 30-50 42-80 46-180 26-237-42l-285.99999 165-32-56 285.99999-165c-31-84 2-180 82-226 18-10 36-17 55-21v-442c-19-4-37-11-55-21-80-46-113-142-82-226l-285.99999-165 32-56 285.99999 165c57-68 157-88 237-42 19 12 36 26 50 42zm1080.00032 992c-18-50-15-108 14-157 30-52 81-84 136-92v-438c-55-8-106-40-136-92-29-49-32-107-14-157l-382-218c-35 40-85 65-142 65s-107-25-142-65l-382.00032 218c18 50 15 108-14 157-30 52-81 84-136 92v438c55 8 106 40 136 92 29 49 32 107 14 157l382.00032 218c35-40 85-65 142-65s107 25 142 65z" fill="#000000" fill-rule="nonzero" transform="translate(0 .000102)"/></svg>"""

# ---------------------------- helpers ----------------------------
import argparse, os, math
from collections import deque
from PIL import Image, ImageFilter
from PIL.Image import Resampling
import cairosvg

# ---------------------------- device helper ----------------------------
def get_pixel_resolution(codename: str):
    """Return (width, height) in portrait pixels for supported Pixel devices."""
    resolutions = {
        # Pixel 9 series
        "tegu":    (1080, 2424),   # Pixel 9a
        "comet":   (2076, 2152),   # Pixel 9 Pro Fold (inner)
        "komodo":  (1344, 2992),   # Pixel 9 Pro XL
        "caiman":  (1280, 2856),   # Pixel 9 Pro
        "tokay":   (1080, 2424),   # Pixel 9

        # Pixel 8 series
        "akita":   (1080, 2400),   # Pixel 8a
        "husky":   (1344, 2992),   # Pixel 8 Pro
        "shiba":   (1080, 2400),   # Pixel 8

        # Pixel Fold + Tablet
        "felix":      (1840, 2208),   # Pixel Fold (inner)
        "tangorpro":  (1600, 2560),   # Pixel Tablet

        # Pixel 7 series
        "lynx":    (1080, 2400),   # Pixel 7a
        "cheetah": (1440, 3120),   # Pixel 7 Pro
        "panther": (1080, 2400),   # Pixel 7

        # Pixel 6 series
        "bluejay": (1080, 2400),   # Pixel 6a
        "raven":   (1440, 3120),   # Pixel 6 Pro
        "oriole":  (1080, 2400),   # Pixel 6
    }
    c = codename.lower()
    if c not in resolutions:
        raise ValueError(f"Unknown Pixel codename: {codename}")
    return resolutions[c]

def render_svg_to_png(svg_path_or_embedded: str, png_path: str, size_px: int) -> None:
    if svg_path_or_embedded and svg_path_or_embedded != "__embedded__":
        cairosvg.svg2png(url=svg_path_or_embedded, write_to=png_path,
                         output_width=size_px, output_height=size_px)
    else:
        cairosvg.svg2png(bytestring=EMBEDDED_SVG.encode("utf-8"), write_to=png_path,
                         output_width=size_px, output_height=size_px)

def make_vertical_gradient(size, top_rgb=(30,30,30), bottom_rgb=(10,10,10)):
    w, h = size
    grad = Image.new("RGBA", (w, h))
    for y in range(h):
        t = y / (h - 1 if h > 1 else 1)
        r = int(top_rgb[0] * (1 - t) + bottom_rgb[0] * t)
        g = int(top_rgb[1] * (1 - t) + bottom_rgb[1] * t)
        b = int(top_rgb[2] * (1 - t) + bottom_rgb[2] * t)
        for x in range(w):
            grad.putpixel((x, y), (r, g, b, 255))
    return grad

def apply_fill_with_mask(fill_img: Image.Image, mask_img: Image.Image) -> Image.Image:
    out = Image.new("RGBA", fill_img.size, (0,0,0,0))
    out.paste(fill_img, (0,0), mask=mask_img)
    return out


def parse_accent_color(accent_color: str):
    """Accept preset names or custom colors:
       - "gold", "steel", "red", "none"
       - "#RRGGBB"
       - "R,G,B" (0-255 each)
    Returns (r,g,b) or None for 'none'.
    """
    presets = {"gold":(160,140,60), "steel":(70,70,70), "red":(140,40,40), "none":None}
    if accent_color in presets:
        return presets[accent_color]
    s = accent_color.strip()
    # Hex
    if s.startswith("#") and len(s) == 7:
        try:
            r = int(s[1:3], 16); g = int(s[3:5], 16); b = int(s[5:7], 16)
            return (r,g,b)
        except ValueError:
            pass
    # Comma-separated
    if "," in s:
        parts = s.split(",")
        if len(parts) == 3:
            try:
                r,g,b = [max(0, min(255, int(p.strip()))) for p in parts]
                return (r,g,b)
            except ValueError:
                pass
    # Fallback to gold
    return presets["gold"]
def recolor_flat(mask_img: Image.Image, rgb=(30,30,30)):
    fill = Image.new("RGBA", mask_img.size, (*rgb, 255))
    return apply_fill_with_mask(fill, mask_img)

def build_tile_variants(mask, style):
    if style == "gradient":
        grad = make_vertical_gradient(mask.size, (30,30,30), (10,10,10))
        base = apply_fill_with_mask(grad, mask)
        return lambda row: base

    if style == "glossmix":
        grad = make_vertical_gradient(mask.size, (35,35,35), (12,12,12))
        glossy = apply_fill_with_mask(grad, mask)
        matte  = recolor_flat(mask, (28,28,28))
        return lambda row: glossy if (row % 2 == 0) else matte

    if style == "emboss":
        # Lowlight emboss + real drop shadow (dilated alpha), baked defaults
        base_color   = (25,25,25,255)
        shadow_color = (8,8,12,255)
        dilated = mask.filter(ImageFilter.MaxFilter(3))
        shadow_rgba = apply_fill_with_mask(Image.new("RGBA", mask.size, shadow_color), dilated)
        base_rgba   = apply_fill_with_mask(Image.new("RGBA", mask.size, base_color), mask)
        def tile_for_row(row):
            canvas = Image.new("RGBA", mask.size, (0,0,0,0))
            canvas.paste(shadow_rgba, (2,2), shadow_rgba)  # 2px offset
            canvas.paste(base_rgba,   (0,0), base_rgba)
            return canvas
        return tile_for_row

    raise ValueError("Unknown style")

def flood_fill_inner_hole(alpha_img):
    w, h = alpha_img.size
    alpha = alpha_img.load()
    mask = Image.new("L", (w, h), 0)
    m = mask.load()
    cx, cy = w//2, h//2
    seeds = [(cx, cy)]
    for r in range(1, min(w, h)//6, 3):
        seeds.extend([(cx+r, cy), (cx-r, cy), (cx, cy+r), (cx, cy-r)])
        if len(seeds) > 50:
            break
    visited = set()
    q = deque()
    seed = None
    for sx, sy in seeds:
        if 0 <= sx < w and 0 <= sy < h and alpha[sx, sy] == 0:
            seed = (sx, sy); break
    if seed is None:
        return mask
    q.append(seed); visited.add(seed)
    while q:
        x, y = q.popleft()
        m[x, y] = 255
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if alpha[nx, ny] == 0:
                    visited.add((nx, ny)); q.append((nx, ny))
    return mask

def style_tinted_accent(mask_rgba, style, rgb):
    alpha = mask_rgba.split()[3] if mask_rgba.mode == "RGBA" else mask_rgba
    w, h = alpha.size
    def clamp(x): 
        y = int(x)
        return 0 if y < 0 else (255 if y > 255 else y)
    r, g, b = rgb
    if style == "gradient":
        top = (clamp(r*0.92), clamp(g*0.92), clamp(b*0.92))
        bot = (clamp(r*0.70), clamp(g*0.70), clamp(b*0.70))
        grad = make_vertical_gradient((w, h), top, bot)
        return apply_fill_with_mask(grad, alpha)
    if style == "glossmix":
        top = (clamp(r*1.05), clamp(g*1.05), clamp(b*1.05))
        bot = (clamp(r*0.75), clamp(g*0.75), clamp(b*0.75))
        grad = make_vertical_gradient((w, h), top, bot)
        return apply_fill_with_mask(grad, alpha)
    if style == "emboss":
        # Same drop shadow logic for accent outline
        base_color   = (25,25,25,255)
        shadow_color = (8,8,12,255)
        dilated = alpha.filter(ImageFilter.MaxFilter(3))
        shadow_rgba = apply_fill_with_mask(Image.new("RGBA", (w,h), shadow_color), dilated)
        base_rgba   = apply_fill_with_mask(Image.new("RGBA", (w,h), base_color), alpha)
        canvas = Image.new("RGBA", (w, h), (0,0,0,0))
        canvas.paste(shadow_rgba, (2,2), shadow_rgba)
        canvas.paste(base_rgba,   (0,0), base_rgba)
        return canvas
    return apply_fill_with_mask(Image.new("RGBA", (w,h), (r,g,b,255)), alpha)

def build_accent_with_center(svg_path_or_embedded, size_px, center_rgb=(31,31,31), outline_style=None, outline_rgb=(160,140,60)):
    tmp_png = "_accent_tmp.png"
    render_svg_to_png(svg_path_or_embedded, tmp_png, size_px)
    accent_rgba = Image.open(tmp_png).convert("RGBA")
    alpha = accent_rgba.split()[3]
    accent_outline = Image.new("RGBA", accent_rgba.size, (0,0,0,0))
    if outline_style is not None:
        styled = style_tinted_accent(accent_rgba, outline_style, outline_rgb)
        accent_outline.paste(styled, (0,0), styled)
    else:
        solid = Image.new("RGBA", accent_rgba.size, (*outline_rgb, 255))
        accent_outline.paste(solid, (0,0), mask=alpha)
    inner_mask = flood_fill_inner_hole(alpha)
    gray = (*center_rgb, 255)
    gray_layer = Image.new("RGBA", accent_rgba.size, gray)
    inner_gray = Image.new("RGBA", accent_rgba.size, (0,0,0,0))
    inner_gray.paste(gray_layer, (0,0), mask=inner_mask)
    accent_final = Image.new("RGBA", accent_rgba.size, (0,0,0,0))
    accent_final.paste(inner_gray, (0,0), inner_gray)
    accent_final.paste(accent_outline, (0,0), accent_outline)
    try:
        os.remove(tmp_png)
    except OSError:
        pass
    return accent_final
def build_wallpaper(svg_path: str,
                    out_path: str,
                    screen_w: int = 1344,
                    screen_h: int = 2992,
                    logo_px: int = 200,
                    spacing_mult: float = 1.6,
                    style: str = "gradient",
                    weave: bool = False,
                    weave_deg: float = 3.0,
                    tessellate: bool = True,
                    scalevar: bool = False,
                    scale_every: int = 4,
                    scale_factor: float = 1.2,
                    accent_color: str = "gold",
                    # explicit accent control
                    accent_x: float = 0.50,
                    accent_y: float = 0.20,
                    accent_scale: float = 1.0,
                    # FP overrides
                    fp_mode: bool = True,
                    fp_center_rgb: tuple = (31,31,31),
                    fp_anchor_ratio_y: float = 0.718,
                    fp_scale: float = 2.25):
    """Create wallpaper with grid anchored at the accent position."""
    # Render base tile (from embedded unless a path is provided)
    tmp_logo = "_logo_tmp.png"
    render_svg_to_png(svg_path, tmp_logo, size_px=logo_px)
    logo = Image.open(tmp_logo).convert("RGBA")
    mask = logo.split()[3]

    tile_for_row = build_tile_variants(mask, style)
    base_tile = tile_for_row(0)
    tile_w, tile_h = base_tile.size

    # Accent parameters (possibly overridden by FP mode)
    if fp_mode:
        accent_center_x = screen_w // 2
        accent_center_y = int(screen_h * fp_anchor_ratio_y)
        accent_size_px = int(logo_px * fp_scale)
        use_center_fill = True
        center_rgb = fp_center_rgb
    else:
        accent_center_x = int(screen_w * accent_x)
        accent_center_y = int(screen_h * accent_y)
        accent_size_px = int(logo_px * accent_scale)
        use_center_fill = False
        center_rgb = None

    bg = Image.new("RGB", (screen_w, screen_h), (0,0,0))

    if weave and tessellate:
        pad = int(math.ceil(logo_px * 0.35))
        S = tile_w + 2*pad
        tile_padded = Image.new("RGBA", (S, S), (0,0,0,0))
        tile_padded.paste(base_tile, (pad, pad), base_tile)

        tA = tile_padded.rotate( weave_deg, resample=Resampling.BICUBIC, expand=False)
        tB = tile_padded.rotate(-weave_deg, resample=Resampling.BICUBIC, expand=False)

        anchor_x = accent_center_x - S // 2
        anchor_y = accent_center_y - S // 2

        min_i = -math.ceil((anchor_x + S) / S)
        max_i =  math.ceil((screen_w - anchor_x) / S)
        min_j = -math.ceil((anchor_y + S) / S)
        max_j =  math.ceil((screen_h - anchor_y) / S)

        for j in range(min_j, max_j + 1):
            for i in range(min_i, max_i + 1):
                x = anchor_x + i * S
                y = anchor_y + j * S
                if i == 0 and j == 0:
                    continue
                tile_img = tA if ((i + j) % 2 == 0) else tB
                if j % 2 != 0:
                    x += S // 2
                if x < screen_w and y < screen_h and (x + S) > 0 and (y + S) > 0:
                    bg.paste(tile_img, (x, y), tile_img)

    else:
        x_step = int(round(tile_w * spacing_mult))
        y_step = int(round(tile_h * spacing_mult))
        anchor_x = accent_center_x - tile_w // 2
        anchor_y = accent_center_y - tile_h // 2

        pad_steps = 50
        for dy in range(-y_step * pad_steps, screen_h + y_step * pad_steps, y_step):
            for dx in range(-x_step * pad_steps, screen_w + x_step * pad_steps, x_step):
                if dx == 0 and dy == 0:
                    continue
                x = anchor_x + dx
                y = anchor_y + dy

                row_idx = (dy // y_step) if y_step != 0 else 0
                tile = tile_for_row(abs(row_idx))

                if scalevar and (abs(row_idx) % scale_every == 0):
                    new_w = max(1, int(tile.width * scale_factor))
                    new_h = max(1, int(tile.height * scale_factor))
                    tile = tile.resize((new_w, new_h), resample=Resampling.BICUBIC)

                if weave:
                    parity = ((dx // x_step) + (dy // y_step)) if (x_step and y_step) else 0
                    angle = weave_deg if (parity % 2 == 0) else -weave_deg
                    tile = tile.rotate(angle, resample=Resampling.BICUBIC, expand=True)

                if x < screen_w and y < screen_h and (x + tile.width) > 0 and (y + tile.height) > 0:
                    bg.paste(tile, (x, y), tile)

    # Accent last (z-above)
    if use_center_fill:
        # Style/color the outline in FP mode too
        orgb = parse_accent_color(accent_color) or (160,140,60)
        accent_img = build_accent_with_center(svg_path, accent_size_px, center_rgb=center_rgb, outline_style=style, outline_rgb=orgb)
    else:
        rgb = parse_accent_color(accent_color)

        accent_mask_png = "_accent_tmp.png"
        render_svg_to_png(svg_path, accent_mask_png, size_px=accent_size_px)
        accent_rgba = Image.open(accent_mask_png).convert("RGBA")

        if rgb is None:
            accent_img = style_tinted_accent(accent_rgba, style, (30,30,30))
        else:
            accent_img = style_tinted_accent(accent_rgba, style, rgb)

        try:
            os.remove(accent_mask_png)
        except OSError:
            pass

    ax = accent_center_x - accent_img.width // 2
    ay = accent_center_y - accent_img.height // 2
    bg.paste(accent_img, (ax, ay), accent_img)

    bg.save(out_path, "PNG")

    try:
        os.remove("_logo_tmp.png")
    except OSError:
        pass

# ---------------------------- CLI ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate GOS tiled wallpapers (Chic Suite, Monolithic).")
    parser.add_argument("--svg", default="__embedded__", help="Path to an alternate SVG (omit to use embedded)")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--width", type=int, default=1344, help="Screen width (default 1344)")
    parser.add_argument("--height", type=int, default=2992, help="Screen height (default 2992)")
    parser.add_argument("--device", type=str, help="Pixel codename (e.g. komodo, caiman, tokay). Overrides --width/--height.")
    parser.add_argument("--logo_px", type=int, default=200, help="Logo render size in px (default 200)")
    parser.add_argument("--spacing", type=float, default=1.6, help="Spacing multiplier (non-tessellated)")
    parser.add_argument("--style", choices=["gradient","glossmix","emboss"], default="gradient", help="Fill style")
    parser.add_argument("--weave", action="store_true", help="Enable diagonal weave rotation")
    parser.add_argument("--weave_deg", type=float, default=3.0, help="Weave rotation degrees")
    parser.add_argument("--tessellate", action="store_true", default=True, help="Touching tiles when weaving (padded, no gaps)")
    parser.add_argument("--scalevar", action="store_true", help="Enable periodic scale variance")
    parser.add_argument("--scale_every", type=int, default=4, help="Apply scale variance every N rows")
    parser.add_argument("--scale_factor", type=float, default=1.2, help="Scale factor for scale variance")
    parser.add_argument("--accent_color", type=str, default="gold", help="Accent color preset or custom RGB (#RRGGBB or R,G,B)")
    parser.add_argument("--accent_x", type=float, default=0.50, help="Accent center X as fraction of width (0..1)")
    parser.add_argument("--accent_y", type=float, default=0.20, help="Accent center Y as fraction of height (0..1)")
    parser.add_argument("--accent_scale", type=float, default=1.0, help="Accent size as multiple of base logo_px")
    parser.add_argument("--fp_mode", action="store_true", default=False,
                        help="Override accent pos/scale to FP center and fill inner cut-out with gray.")
    parser.add_argument("--fp_center_rgb", type=str, default="#1f1f1f",
                        help="FP center gray in hex (default #1f1f1f).")
    parser.add_argument("--fp_anchor", type=float, default=0.718,
                        help="Fingerprint center position from top (default 0.718).")
    parser.add_argument("--fp_scale", type=float, default=2.25,
                        help="Accent scale relative to base logo (default 2.25 ~ 225%).")
    args = parser.parse_args()

    fp_rgb = tuple(int(args.fp_center_rgb.lstrip("#")[i:i+2], 16) for i in (0,2,4))
    # Resolve device codename to resolution if provided
    if args.device:
        args.width, args.height = get_pixel_resolution(args.device)

    build_wallpaper(svg_path=args.svg, out_path=args.out,
                    screen_w=args.width, screen_h=args.height,
                    logo_px=args.logo_px, spacing_mult=args.spacing,
                    style=args.style, weave=args.weave, weave_deg=args.weave_deg, tessellate=args.tessellate,
                    scalevar=args.scalevar, scale_every=args.scale_every, scale_factor=args.scale_factor,
                    accent_color=args.accent_color,
                    accent_x=args.accent_x, accent_y=args.accent_y, accent_scale=args.accent_scale,
                    fp_mode=args.fp_mode, fp_center_rgb=fp_rgb,
                    fp_anchor_ratio_y=args.fp_anchor, fp_scale=args.fp_scale)

if __name__ == "__main__":
    main()