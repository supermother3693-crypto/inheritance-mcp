"""Decorative (book-style) version of the naqsha: framed A4 page, plaque headings, Jameel Noori font.

Takes the same Excel the engine builds, so every row/number of the plain naqsha is kept.
Usage: themed_html(xlsx_path, title, theme="navy"|"green", font_url="...ttf") -> html
"""
from __future__ import annotations
import math
import re
from openpyxl import load_workbook
from naqsha import sheet_to_html

THEMES = {
    "navy":  dict(main="#0c1f4d", gold="#c29b45", gold_lt="#f0d58a", ivory="#fffaf0",
                  tint_a="#eef2fa", tint_b="#dde6f6", cream="#fbf1d3", pink="#fbdcdc", ink="#16213d"),
    "phool": dict(main="#0f4a33", gold="#b98d3a", gold_lt="#f0d58a", ivory="#fffaf0", flower=True, flat=True,
                  tint_a="#f6f1de", tint_b="#ede3c2", cream="#f6f1de", pink="#fbdcdc", ink="#1b2b22"),
    "green": dict(main="#0f4a33", gold="#c29b45", gold_lt="#f0d58a", ivory="#fffaf0",
                  tint_a="#f5f0dd", tint_b="#e6dcb8", cream="#fbf1d3", pink="#fbdcdc", ink="#1b2b22"),
}


def _star(cx, cy, r, c, points=8, inner=0.58):
    def poly(radius, ratio, rot):
        pts = []
        for i in range(points * 2):
            ang = math.pi / points * i + rot
            rad = radius if i % 2 == 0 else radius * ratio
            pts.append(f"{cx + rad * math.sin(ang):.2f},{cy - rad * math.cos(ang):.2f}")
        return " ".join(pts)
    return (f'<polygon points="{poly(r, inner, 0)}" fill="{c["gold"]}" stroke="{c["gold_lt"]}" stroke-width="0.15"/>'
            f'<polygon points="{poly(r * 0.62, inner, math.pi / points)}" fill="{c["main"]}" stroke="{c["gold_lt"]}" stroke-width="0.15"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.17:.2f}" fill="{c["gold_lt"]}"/>')


def _flower(cx, cy, r, c, points=8, inner=0):
    """آٹھ پنکھڑیوں کا پھول: کریم پنکھڑیاں، سنہری کنارہ، بیچ میں سنہری گول۔"""
    out = []
    for i in range(8):
        a = i * 45
        out.append(f'<ellipse cx="{cx:.2f}" cy="{cy - r * 0.58:.2f}" rx="{r * 0.36:.2f}" ry="{r * 0.46:.2f}" '
                   f'transform="rotate({a} {cx:.2f} {cy:.2f})" fill="#f6ecc9" stroke="{c["gold"]}" stroke-width="0.25"/>')
    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * 0.3:.2f}" fill="{c["gold"]}" stroke="#f6ecc9" stroke-width="0.25"/>')
    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * 0.12:.2f}" fill="{c["main"]}"/>')
    return "".join(out)


def frame_svg(pw, ph, c, margin=5, band=11):
    ox0, oy0, ox1, oy1 = margin, margin, pw - margin, ph - margin
    ix0, iy0, ix1, iy1 = margin + band, margin + band, pw - margin - band, ph - margin - band
    iw, ih, mid = ix1 - ix0, iy1 - iy0, band / 2
    _star_ = _flower if c.get("flower") else _star
    P = [f'<path fill-rule="evenodd" fill="{c["main"]}" d="M{ox0} {oy0}H{ox1}V{oy1}H{ox0}Z M{ix0} {iy0}V{iy1}H{ix1}V{iy0}Z"/>',
         f'<rect x="{ox0+.9}" y="{oy0+.9}" width="{ox1-ox0-1.8}" height="{oy1-oy0-1.8}" fill="none" stroke="{c["gold"]}" stroke-width="0.35"/>',
         f'<rect x="{ix0-.9}" y="{iy0-.9}" width="{iw+1.8}" height="{ih+1.8}" fill="none" stroke="{c["gold"]}" stroke-width="0.35"/>',
         f'<rect x="{ix0}" y="{iy0}" width="{iw}" height="{ih}" fill="none" stroke="{c["gold_lt"]}" stroke-width="0.6"/>']

    def strip(length, n, horiz, fixed, start):
        step, out = length / n, []
        for i in range(n):
            k = start + step * (i + .5)
            x, y = (k, fixed) if horiz else (fixed, k)
            out.append(_star_(x, y, 3.9, c))
            if i < n - 1:
                x2, y2 = (k + step / 2, fixed) if horiz else (fixed, k + step / 2)
                out.append(f'<path d="M{x2} {y2-1.1}l1.1 1.1-1.1 1.1-1.1-1.1z" fill="{c["gold"]}"/>')
        return "".join(out)
    nh, nv = round(iw / 9.4), round(ih / 9.4)
    P += [strip(iw, nh, True, oy0 + mid, ix0), strip(iw, nh, True, oy1 - mid, ix0),
          strip(ih, nv, False, ox0 + mid, iy0), strip(ih, nv, False, ox1 - mid, iy0)]
    for cx, cy in ((ox0 + mid, oy0 + mid), (ox1 - mid, oy0 + mid), (ox0 + mid, oy1 - mid), (ox1 - mid, oy1 - mid)):
        P.append(f'<circle cx="{cx}" cy="{cy}" r="4.7" fill="{c["main"]}" stroke="{c["gold_lt"]}" stroke-width="0.35"/>')
        P.append(_star_(cx, cy, 4.4, c, 12, .72))
    return (f'<svg viewBox="0 0 {pw} {ph}" xmlns="http://www.w3.org/2000/svg" '
            f'style="position:fixed;left:0;top:0;width:{pw}mm;height:{ph}mm;z-index:-1">'
            + "".join(P) + "</svg>")


def themed_html(xlsx_path: str, title: str = "", theme: str = "navy",
                font_url: str = "static/fonts/JameelNooriNastaleeq-Regular.ttf") -> str:
    c = THEMES[theme]
    h = sheet_to_html(xlsx_path, title)
    landscape = load_workbook(xlsx_path).active.page_setup.orientation == "landscape"
    pw, ph = (297, 210) if landscape else (210, 297)
    inner_mm = pw - 2 * 16.5
    inner_px = inner_mm / 25.4 * 96
    # رنگ بدلنا
    def td_fix(m):
        s = m.group(0)
        if "background:#E8EEF7" in s:      # عنوان / مورث کی پٹیاں → گہری تختی
            s = s.replace("background:#E8EEF7", f"background:{c['main']}").replace("color:#000000", f"color:{c['gold_lt']}")
        s = (s.replace("background:#FFF4D6", f"background:{c['cream']}")
              .replace("background:#E6F4EA", f"background:{c['tint_a']}")
              .replace("background:#FFD6D6", f"background:{c['pink']}")
              .replace("border:1px solid #444", f"border:1px solid {c['main']}"))
        return s
    h = re.sub(r"<td[^>]*>", td_fix, h)
    # کتابی انداز: خانوں کی لکیریں ہٹا کر ہر لفظ/عدد کے اوپر اسی کی لمبائی کے برابر سنہری لکیر
    shadow = "" if c.get("flat") else f"box-shadow: inset 0 0 0 1.5px {c['gold']}, inset 0 0 0 4px {c['main']}, inset 0 0 0 5px {c['gold']};"
    h = h.replace(f"border:1px solid {c['main']}", "border:0")
    # رؤوس/سہام والا خانہ: اوپر پوری چوڑائی کی چمکدار نیلی لکیر اور اسی رنگ کی تفصیل
    BL = "#1a73ff"
    def rus_td(m):
        t = m.group(0)
        if "رؤوس" in t and "display:block" in t:
            t = re.sub(r'(<td[^>]*style="[^"]*)(")', r'\1;border-top:1.6px solid ' + BL + r' !important\2', t, 1)
            t = re.sub(r'(<span style="[^"]*)("[^>]*>\{[^<]*رؤوس)', r'\1;color:' + BL + r'\2', t)
        return t
    h = re.sub(r"<td[^>]*>.*?</td>", rus_td, h, flags=re.S)
    def wrap(m):
        inner = m.group(2)
        if not re.sub(r"<[^>]*>", "", inner).strip() or "display:block" in inner or "display:flex" in inner or "<br>" in inner:
            return m.group(0)
        return f'{m.group(1)}<span class="ln">{inner}</span></td>'
    h = re.sub(r"(<td[^>]*>)(.*?)</td>", wrap, h, flags=re.S)
    h = h.replace("</style>", f"""  .ln {{ display: inline-block; border-top: 1px solid {c['gold']}; padding: .1em .45em 0; line-height: 1.55; }}
  td[style*="background:{c['main']}"] {{ {shadow} }}
  td[style*="background:{c['main']}"] .ln {{ border-top-color: {c['gold_lt']}; }}
</style>""", 1)
    # فونٹ، صفحہ، فریم
    h = h.replace('<style>', f"""<style>
  @font-face {{ font-family: "JNN"; src: url("{font_url}"); }}
  :root {{ --ink: {c['ink']}; }}
  body {{ font-family: "JNN", "Noto Nastaliq Urdu", Arial, sans-serif !important; color: {c['ink']}; }}
  td {{ line-height: 1.75; }}
""", 1)
    h = re.sub(r"@page \{[^}]*\}", f"@page {{ size: A4 {'landscape' if landscape else 'portrait'}; margin: 0; }}", h)
    tw = int(re.search(r"width: (\d+)px; margin: 0 auto", h).group(1))
    h = re.sub(r"table \{ zoom: [^;]*;", f"table {{ zoom: {min(1.2, (inner_px - 4) / tw):.3f} !important;", h)
    h = h.replace("<body>", "<body>" + frame_svg(pw, ph, c), 1)
    # ہر صفحے پر فریم کے اندر جگہ: دہرائی جانے والی thead/tfoot خالی پٹیاں
    pad = "16.5mm"
    h = h.replace('<div class="wrap">', f'<table class="pg" style="width:100%;border:0"><thead><tr><td style="height:{pad};border:0;padding:0"></td></tr></thead>'
                  f'<tfoot><tr><td style="height:{pad};border:0;padding:0"></td></tr></tfoot><tbody><tr><td style="border:0;padding:0 {pad}"><div class="wrap">', 1)
    h = h.replace("</table>\n</div>\n<script>", "</table>\n</div></td></tr></tbody></table>\n<script>", 1)
    # نمائش میں بھی فریم کا پس منظر (اسکرین پر صرف ہلکا)
    h = h.replace("document.querySelector('table')", "document.querySelector('table:not(.pg)')")
    h = h.replace("</style>", "  table.pg { width: 100% !important; zoom: 1 !important; table-layout: auto; border-collapse: collapse; }\n  table.pg .wrap { overflow: visible; padding: 0; }\n</style>", 1)
    h = h.replace("</style>", "  @media screen { body > svg { display: none; } }\n</style>", 1)
    return h
