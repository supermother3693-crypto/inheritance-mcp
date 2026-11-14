"""Turn the engine's Excel naqsha into a printable web page (same layout).

The page has a "Save as PDF" button (browser print), so a PDF can be made on any
phone or computer without LibreOffice on the server.
"""
from __future__ import annotations

from html import escape

from openpyxl import load_workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.utils import get_column_letter as L

FONT = 'Arial, "Noto Naskh Arabic", "Noto Nastaliq Urdu", "Noto Sans Gujarati", "Nirmala UI", sans-serif'


def _rgb(color) -> str | None:
    v = getattr(color, "rgb", None)
    if isinstance(v, str) and len(v) in (6, 8):
        return "#" + v[-6:]
    return None


def sheet_to_html(xlsx_path: str, title: str = "") -> str:
    wb = load_workbook(xlsx_path, rich_text=True)
    ws = wb.active
    max_r, max_c = ws.max_row, ws.max_column

    merges = {}   # (row, col) -> (rowspan, colspan) for the top-left cell
    covered = set()
    for m in ws.merged_cells.ranges:
        merges[(m.min_row, m.min_col)] = (m.max_row - m.min_row + 1, m.max_col - m.min_col + 1)
        for r in range(m.min_row, m.max_row + 1):
            for c in range(m.min_col, m.max_col + 1):
                if (r, c) != (m.min_row, m.min_col):
                    covered.add((r, c))

    widths = []
    for c in range(1, max_c + 1):
        w = ws.column_dimensions[L(c)].width or 8.43
        widths.append(w * 7 + 5)
    total_w = sum(widths)

    cols = "".join(f'<col style="width:{w / total_w * 100:.3f}%">' for w in widths)
    rows_html = []
    for r in range(1, max_r + 1):
        h = ws.row_dimensions[r].height or 15
        tds = []
        for c in range(1, max_c + 1):
            if (r, c) in covered:
                continue
            cell = ws.cell(r, c)
            rs, cs = merges.get((r, c), (1, 1))
            st = []
            if cell.fill and cell.fill.fill_type == "solid":
                bg = _rgb(cell.fill.fgColor)
                if bg:
                    st.append(f"background:{bg}")
            f = cell.font
            if f:
                st.append(f"font-size:{(f.sz or 11)}pt")
                if f.b:
                    st.append("font-weight:700")
                col = _rgb(f.color) if f.color else None
                if col:
                    st.append(f"color:{col}")
            b = cell.border
            if b and b.left and b.left.style:
                st.append("border:1px solid #444")
            al = cell.alignment
            st.append("text-align:" + ("right" if al and al.horizontal == "right" else "center"))
            v = cell.value
            if isinstance(v, CellRichText):
                text = ""
                for part in v:
                    if isinstance(part, TextBlock):
                        f2 = part.font
                        sup = getattr(f2, "vertAlign", None) == "superscript"
                        css = f"font-size:{f2.sz or 11}pt;font-weight:{700 if f2.b else 400}"
                        if f2.color is not None and getattr(f2.color, "rgb", None):
                            css += f";color:#{str(f2.color.rgb)[-6:]}"
                        tag = "sup" if sup else "span"
                        text += f'<{tag} style="{css}">{escape(part.text).replace(chr(10), "<br>")}</{tag}>'
                    else:
                        text += escape(str(part))
            else:
                text = "" if v is None else escape(str(v)).replace("\n", "<br>")
            attrs = (f' rowspan="{rs}"' if rs > 1 else "") + (f' colspan="{cs}"' if cs > 1 else "")
            tds.append(f'<td{attrs} style="{";".join(st)}">{text}</td>')
        rows_html.append(f'<tr style="height:{h:.0f}pt">{"".join(tds)}</tr>')

    landscape = ws.page_setup.orientation == "landscape"
    page_px = 1050 if landscape else 740
    zoom = min(1.0, page_px / total_w)
    page_title = escape(title or "نقشۂ تقسیمِ سہام")
    return f"""<!doctype html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=6">
<title>{page_title}</title>
<style>
  body {{ margin: 0; font-family: {FONT}; background: #fff; }}
  .bar {{ position: sticky; top: 0; z-index: 2; background: #1f3b64; color: #fff; padding: 4px 10px;
          display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
  .bar button {{ font: inherit; padding: 3px 12px; border: 0; border-radius: 6px; font-size: 15px; background: #fff; color: #1f3b64;
                 font-weight: 700; cursor: pointer; }}
  .bar span {{ font-size: 13px; opacity: .9; }}
  .wrap {{ overflow-x: auto; padding: 10px; }}
  table {{ direction: ltr; border-collapse: collapse; table-layout: fixed; width: {total_w:.0f}px; margin: 0 auto; }}
  td {{ direction: rtl; padding: 2px 3px; vertical-align: middle; overflow-wrap: anywhere; word-break: break-word; }}
  tr {{ page-break-inside: avoid; }}
  @page {{ size: A4 {"landscape" if landscape else "portrait"}; margin: 8mm; }}
  @media print {{
    .bar {{ display: none; }}
    .wrap {{ overflow: visible; padding: 0; }}
    table {{ zoom: {zoom:.3f} !important; }}
    * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  }}
</style>
</head>
<body>
<div class="bar">
  <button onclick="window.print()" title="PDF محفوظ کریں / پرنٹ (کھلنے والی ونڈو میں Save as PDF چنیں)">⤓ PDF</button>
  <button onclick="zoomBy(1.2)" aria-label="بڑا کریں">＋</button>
  <button onclick="zoomBy(1/1.2)" aria-label="چھوٹا کریں">－</button>
  <button onclick="fit()" title="پوری چوڑائی" aria-label="پوری چوڑائی">⤢</button>
</div>
<div class="wrap">
<table><colgroup>{cols}</colgroup>
{"".join(rows_html)}
</table>
</div>
<script>
const tb = document.querySelector('table');
let z = 1;
function setZ(v) {{ z = Math.max(0.15, Math.min(4, v)); tb.style.zoom = z; }}
function zoomBy(k) {{ setZ(z * k); }}
const W0 = {total_w:.0f};
function fit() {{ setZ(Math.min(1.5, (document.documentElement.clientWidth - 20) / W0)); }}
fit();
</script>
</body>
</html>
"""
