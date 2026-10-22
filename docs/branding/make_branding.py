"""Generates the logo, app icon and banners (SVG), then renders PNGs with headless Chrome/Chromium.
Same family look as the other WikiTree tools: WikiTree brand colours, Calibri, a tilted white card.
The hero is the app's fan chart: three parent wedges (not limited to two), and a child at the centre.
Run: python3 make_branding.py   (set CHROME to a Chrome/Chromium binary if it is not found)"""
import glob
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DARK, LIME, LIME2, PALE, PALE2, YELLOW, ORANGE = "#25422D", "#8FC641", "#A5D167", "#E1F0B4", "#E5EECF", "#FCB815", "#f37c26"
CREAM, PAPER, INK, SEPIA = PALE2, "#ffffff", DARK, "#3f6347"
FONT = "Calibri, Carlito, 'Helvetica Neue', Arial, sans-serif"
WEDGES = [LIME, "#FFE270", "#f9a86a", LIME2, "#FAD158", PALE, "#c5e08a", "#f7c27c"]   # wedge colours, cycled


def find_chrome():
    cands = [os.environ.get("CHROME", ""), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             *glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), shutil.which("chromium") or "", shutil.which("google-chrome") or ""]
    return next(c for c in cands if c and os.path.exists(c))


def fan(cx, cy, R, r0, rings, stroke=None, head=True):
    """Semicircle fan chart opening upward. rings = wedges per ring, e.g. [3, 6, 12]. Centre = child silhouette."""
    sw = stroke or max(2.5, R * .022)
    w = (R - r0) / len(rings)
    pt = lambda r, a: (cx + r * math.cos(a), cy - r * math.sin(a))
    out, k = "", 0
    for gi, n in enumerate(rings):
        ri, ro = r0 + gi * w, r0 + (gi + 1) * w
        for i in range(n):
            a1, a2 = math.pi - math.pi * i / n, math.pi - math.pi * (i + 1) / n
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = pt(ro, a1), pt(ro, a2), pt(ri, a2), pt(ri, a1)
            col = WEDGES[(k + gi) % len(WEDGES)]
            k += 1
            out += (f'<path d="M{x1:.1f},{y1:.1f} A{ro:.1f},{ro:.1f} 0 0 1 {x2:.1f},{y2:.1f} L{x3:.1f},{y3:.1f} '
                    f'A{ri:.1f},{ri:.1f} 0 0 0 {x4:.1f},{y4:.1f} Z" fill="{col}" stroke="{DARK}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
    out += f'<path d="M{cx - r0:.1f},{cy:.1f} A{r0:.1f},{r0:.1f} 0 0 1 {cx + r0:.1f},{cy:.1f} Z" fill="{DARK}"/>'
    if head:
        out += f'<circle cx="{cx:.1f}" cy="{cy - r0 * .52:.1f}" r="{r0 * .30:.1f}" fill="{PALE}"/>'
    return out + f'<line x1="{cx - R - sw:.1f}" y1="{cy}" x2="{cx + R + sw:.1f}" y2="{cy}" stroke="{DARK}" stroke-width="{sw:.1f}" stroke-linecap="round"/>'


def crayon(s):
    """An orange crayon in a box of s x s, tip pointing up-right."""
    return (f'<g transform="translate({s / 2},{s / 2}) rotate(45) scale({s / 92})" stroke="{DARK}" stroke-width="4" stroke-linejoin="round">'
            f'<path d="M-10,-24 L0,-42 L10,-24 Z" fill="{PALE}"/><rect x="-10" y="-24" width="20" height="52" rx="3" fill="{ORANGE}"/>'
            f'<rect x="-10" y="-12" width="20" height="14" fill="{YELLOW}"/></g>')


def print_card(x, y, w, h, rot, inner):
    return (f'<g transform="translate({x},{y}) rotate({rot})">'
            f'<rect x="{-w / 2 + 6}" y="{-h / 2 + 8}" width="{w}" height="{h}" rx="8" fill="#000" opacity=".12"/>'
            f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="8" fill="{PAPER}" stroke="#cfe0a6"/>{inner}</g>')


def wrap(w, h, body, bg=CREAM):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg}"/><stop offset="1" stop-color="{PALE}"/></linearGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#g)"/>{body}</svg>')


def logo(s=512):
    inner = (f'<rect x="{-s * .30}" y="{-s * .33}" width="{s * .60}" height="{s * .50}" rx="6" fill="{PALE}"/>'
             + fan(0, s * .125, s * .275, s * .08, [3, 6, 12], stroke=2.2)
             + f'<text x="{-s * .06}" y="{s * .262}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="{s * .058}" fill="{INK}">Family Adventure</text>')
    card = print_card(s / 2, s / 2, s * .68, s * .80, -4, inner)
    tag = (f'<g transform="translate({s * .72},{s * .73}) rotate(8)"><rect width="{s * .21}" height="{s * .21}" rx="{s * .05}" fill="{LIME}"/>'
           f'<g transform="translate({s * .0},{s * .0})">{crayon(s * .21)}</g></g>')
    return wrap(s, s, card + tag)


def icon(s=512):
    """Square app icon / favicon: the fan on its own, no text, so it still reads at 32px."""
    return wrap(s, s, fan(s / 2, s * .74, s * .43, s * .13, [3, 6], stroke=s * .016), bg=PALE2)


def banner(w, h):
    w0, h0 = 1000, 420
    scale = min(w / w0, h / h0)
    left = (f'<text x="60" y="146" font-family="{FONT}" font-weight="700" font-size="64" fill="{INK}">WikiTree</text>'
            f'<text x="60" y="212" font-family="{FONT}" font-weight="700" font-size="64" fill="{ORANGE}">Family Adventure</text>'
            f'<text x="60" y="268" font-family="{FONT}" font-size="27" fill="{INK}">Turn your family tree into coloring pages.</text>'
            f'<text x="60" y="300" font-family="{FONT}" font-size="27" fill="{SEPIA}">Pick an age. Print it. Color it.</text>'
            f'<text x="60" y="356" font-family="{FONT}" font-weight="700" font-size="15" letter-spacing="1.5" fill="{SEPIA}">AGES 3 TO 13+ · ANY FAMILY SHAPE · COMMUNITY TOOL</text>')
    cw, ch = 340, 300
    card = print_card(w0 - 200, h0 / 2 + 4, cw, ch, 2.5, fan(0, 70, 142, 40, [3, 6, 12]) + f'<text x="0" y="{ch / 2 - 34}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="26" fill="{INK}">Family Fan</text>')
    ox, oy = (w - w0 * scale) / 2, (h - h0 * scale) / 2
    return wrap(w, h, f'<g transform="translate({ox:.1f},{oy:.1f}) scale({scale:.4f})">{left}{card}</g>')


JOBS = {  # file: (svg, width, height); extra PNG sizes for the icon are rendered below
    "logo": (logo(512), 512, 512), "icon": (icon(512), 512, 512),
    "banner-1000x420": (banner(1000, 420), 1000, 420), "social-preview-1280x640": (banner(1280, 640), 1280, 640),
}


def render(svg, w, h, out, big=None):
    """Chrome's window is taller than its viewport, so ask for extra height and crop to w x h."""
    tmp = Path(tempfile.mkdtemp())
    W, H = max(w, 520), max(h, 520)
    (tmp / "p.html").write_text(f'<html><body style="margin:0">{svg}</body></html>')
    subprocess.run([find_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={tmp / 'u'}",
                    f"--window-size={W},{H + 140}", f"--screenshot={out}", f"file://{tmp / 'p.html'}"], capture_output=True, timeout=90)
    shutil.rmtree(tmp, ignore_errors=True)
    from PIL import Image
    Image.open(out).crop((0, 0, w, h)).save(out)


for name, (svg, w, h) in JOBS.items():
    (HERE / f"{name}.svg").write_text(svg, encoding="utf-8")
    render(svg, w, h, HERE / f"{name}.png")
for px, name in [(32, "favicon-32.png"), (180, "apple-touch-icon-180.png"), (192, "icon-192.png")]:   # small sizes: icon drawn at 512, then shrunk
    render(icon(512), 512, 512, HERE / name)
    from PIL import Image
    Image.open(HERE / name).resize((px, px), Image.LANCZOS).save(HERE / name)
print("done")
