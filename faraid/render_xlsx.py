# -*- coding: utf-8 -*-
"""روایتی نقشہ (Excel): دائیں سے بائیں، A4، چھاپنے کے قابل۔ ترتیب آپ کے نمونوں جیسی۔"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.utils import get_column_letter as L
from .relations import rel_label

T = {
    "ur": {
        "intro": ["حامداً و مصلیاً و مسلماً: سب سے پہلے ترکہ سے تجہیز و تکفین، پھر قرض ادا کیا جائے گا؛",
                  "پھر بقیہ مال کے ایک تہائی میں سے جائز وصیت نافذ کی جائے گی؛",
                  "اس کے بعد باقی ترکہ ورثاء میں درج ذیل نقشے کے مطابق تقسیم ہوگا۔"],
        "total": "وارثوں کے کل {J} حصے بنائے جائیں گے اور نقشے کے مطابق تقسیم ہوں گے",
        "final_hdr": "آخری سہام (جامعہ {J})", "dec": "مورث", "decf": "مورثہ",
        "wafat": "وفات", "mazrub": "مضروب", "asl": "اصل مسئلہ", "tashih": "تصحیح",
        "awl": "عول", "radd": "رد", "blocked": "محروم", "chain": "سلسلۂ جامعہ",
        "ver": "تصدیق", "ok": "درست ✓", "bad": "غلط ✗", "sum": "مجموعہ",
        "mafi": "ما في اليد", "ratio": "نسبت", "new": "ضرب (نئے ورثاء)", "old": "ضرب (سابقہ ورثاء)",
        "jami": "جامعہ", "of": "از", "last": "واللہ اعلم بالصواب",
    },
}
T["gu"] = dict(T["ur"])
T["gu"].update({
    "intro": ["હામિદંવ્ વ મુસલ્લિયંવ્ વ મુસલ્લિમા સૌ પ્રથમ મય્યતની કુલ મિલકતમાંથી કફન-દફનનો ખર્ચ, ત્યારબાદ દેવું ( કરઝ ) ચૂકવવામાં આવશે",
              "પછી વારસાની બાકી સંપત્તિના એક તૃતીયાંશ ( ત્રીજા ભાગમાંથી ) જાઇઝ વસિયત ( ઇચ્છા ) પૂર્ણ કરવામાં આવશે",
              "તે પછી બાકીનો વારસો વારસદારો વચ્ચે નીચે આપેલ નકશા મુજબ વિભાજિત થશે ( વહેંચવામાં આવશે )"],
    "total": "વારસાના કુલ {J} ભાગ બનાવવામાં આવશે અને આ નકશા મુજબ વારસદારોમાં વહેંચવામાં આવશે",
    "final_hdr": "અંતિમ ભાગ (જામિઅહ {J})",
})

thin = Side(style="thin", color="444444")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
F = lambda sz=12, b=True, color="000000": Font(name="Arial", size=sz, bold=b, color=color)
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True, readingOrder=2)
NOWRAP = Alignment(horizontal="center", vertical="center", wrap_text=False, readingOrder=2)
CORNER = Alignment(horizontal="right", vertical="top", wrap_text=True)
FILL_T = PatternFill("solid", fgColor="E8EEF7")
FILL_B = PatternFill("solid", fgColor="FFF4D6")
FILL_F = PatternFill("solid", fgColor="E6F4EA")
FILL_R = PatternFill("solid", fgColor="FFD6D6")      # وفات پانے والے وارث کا پورا خانہ
RED = Side(style="medium", color="B00020")
BOX_R = Border(left=RED, right=RED, top=RED, bottom=RED)

# بطن کے نام اور مرحومین کے لیے دعائیہ کلمات (مرد / عورت)؛ بطن در بطن باری باری
BATAN = ["اول", "ثانی", "ثالث", "رابع", "خامس", "سادس", "سابع", "ثامن", "تاسع", "عاشر"]
DUA = {"M": ["رحمہ اللہ تعالیٰ", "نوّر اللہ مرقدہ"], "F": ["رحمہا اللہ تعالیٰ", "نوّر اللہ مرقدہا"]}


def batan_name(i):
    return "بطن " + (BATAN[i] if i < len(BATAN) else str(i + 1))


SMALL = InlineFont(rFont="Arial", sz=8, b=False, color="555555")
BIGF = InlineFont(rFont="Arial", sz=14, b=True)


def corner_val(small, big, c, span):
    """اصول: اصل عدد خانے کے عین بیچ میں؛ چھوٹا سا حساب اسی خانے میں دائیں اوپر کے کونے میں۔
    c = منطقی کالم (1 = دائیں، تنگ کالم)، span = خانے کے کالم۔ بیچ میں لانے کے لیے خالی جگہیں ڈالی جاتی ہیں۔"""
    px = sum((13 if cc == 1 else 17) * 7 + 5 for cc in range(c, c + span))      # خانے کی چوڑائی (پکسل)
    pad = max(0, round((px - len(str(big)) * 10.4) / 2 / 5.2))                  # Arial 14 موٹا: عدد ≈10.4px، خالی جگہ ≈5.2px
    return CellRichText(TextBlock(SMALL, small + "\n"), TextBlock(BIGF, str(big) + " " * pad))


def build_xlsx(case, res, path, lang=None, amounts=None):
    """amounts (اختیاری): {"per": {آئی ڈی: رقم}, "distributable": کل قابلِ تقسیم رقم}
    دیا جائے تو آخری سہام کے نیچے رقم کی سطر بھی چھپتی ہے؛ ورنہ نقشہ پہلے جیسا ہی رہتا ہے۔"""
    lang = lang or case.get("lang", "ur")
    t = T[lang]
    blocks, ladders = res["blocks"], res["ladders"]
    maxc = max(len(b["cols"]) for b in blocks)
    W = max(maxc + 1, 7)
    wb = Workbook()
    ws = wb.active
    ws.title = "نقشہ"
    ws.sheet_view.showGridLines = False
    for c in range(1, W + 1):
        ws.column_dimensions[L(c)].width = 17 if c < W else 13
    row = [1]

    def put(r, c, v, span=1, font=None, fill=None, border=True, h=None, align=CEN, box=None):
        c = W - (c + span - 1) + 1          # منطقی (دائیں سے) → اصل کالم
        cell = ws.cell(r, c, v)
        cell.font = font or F()
        cell.alignment = align
        if span > 1:
            ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + span - 1)
        if border:
            for cc in range(c, c + span):
                ws.cell(r, cc).border = box or BOX
                if fill:
                    ws.cell(r, cc).fill = fill
        if h:
            ws.row_dimensions[r].height = h
        return cell

    def nxt(n=1):
        r = row[0]
        row[0] += n
        return r

    # ---- عنوان اور تمہید ----
    r = nxt()
    put(r, 1, case.get("title") or "نقشۂ تقسیمِ سہام (علمُ الفرائض)", W, F(16), FILL_T, h=30)
    for line in t["intro"]:
        r = nxt()
        put(r, 1, line, W, F(11, False), border=False, h=20)
    nxt()
    # ---- مبلغ کی عمودی سیڑھی: دائیں کالم میں؛ ضارب بائیں کالم میں ----
    vals = [blocks[0]["T"]]
    facs = []
    for i, b in enumerate(blocks):
        if i and b["fJ"] > 1:
            facs.append((i, b["fJ"]))
            vals.append(vals[-1] * b["fJ"])
    for k in range(len(vals) - 1, -1, -1):
        r = nxt()
        has_f = k < len(facs) and k < len(vals) - 1
        put(r, 1, vals[k], 1, F(14), FILL_B, h=22)
        if has_f:   # ضرب کے ساتھ مختصر وجہ: کس بطن کی وجہ سے (ایک ہی لائن میں)
            put(r, W, f"× {facs[k][1]} / {batan_name(facs[k][0])}", 1, F(10, False, "555555"), border=False, align=NOWRAP)
    nxt()

    people = res["people"]
    for bi, b in enumerate(blocks):
        inp = res["inputs"][bi]
        dec = inp["deceased"]
        lab = t["decf"] if b["gender"] == "F" else t["dec"]
        wf = f" ({dec['wafat']})" if dec.get("wafat") else ""
        if b["radd"] and b["asl"] != b["asl_f"]:
            asl_txt = f"{b['asl_f']} / رد {b['asl']}"        # مسئلہ جس عدد سے چلا / پھر رد کا عدد
        elif b["awl"] and b["asl"] != b["asl_f"]:
            asl_txt = f"{b['asl_f']} / عول {b['asl']}"
        else:
            asl_txt = str(b["asl"]) + (" رد" if b["radd"] else "")
        mid = ""
        if b["mudrub"] > 1:
            mid = f"{t['mazrub']} {b['mudrub']}"
        if bi:
            rr = b["ratio"]
            mid = (mid + "   " if mid else "") + f"{rr['name']}  (↑×{b['fJ']}  ↓×{b['fh']})"
        used = 5 if mid else 2
        # سطر 1: دائیں مسئلہ (دخل/وفق)، بائیں ما في اليد (دخل/وفق)، اور مورث کے نام کے اوپر بطن کا نام
        left_t = right_t = None
        if bi:
            parts = b.get("m_parts", [])
            left_t = f"{t['mafi']} {b['m']}" + (f"  ({' + '.join(str(v) for _, v in parts)})" if len(parts) > 1 else "")
            rr = b["ratio"]
            if rr["kind"] == "tadakhul":
                q = max(rr["a"], rr["b"]) // min(rr["a"], rr["b"])
                if rr["a"] < rr["b"]:           # ما في اليد چھوٹا: اس کا دخل بائیں، ما في اليد کے ساتھ
                    left_t += f"  دخل {q}"
                else:                           # مسئلہ چھوٹا: اس کا دخل دائیں، مسئلے کے ساتھ
                    right_t = f"{b['T']}  دخل {q}"
            elif rr["kind"] == "tawafuq":       # دونوں کا وفق: ہر ایک کے ساتھ اپنی طرف
                left_t += f"  وفق {b['fh']}"
                right_t = f"{b['T']}  وفق {b['fJ']}"
        r = nxt()
        if left_t:
            put(r, 2, left_t, used - 2, F(12), FILL_B, h=28)
        if b["mudrub"] > 1 or right_t:
            put(r, 1, right_t or b["T"], 1, F(12 if right_t else 13), h=28)
        put(r, used, batan_name(bi), W - used + 1, F(12), FILL_B, h=28)
        # سطر 2: عنوان
        r = nxt()
        put(r, 1, asl_txt, 1, F(13), FILL_T, h=28)
        if mid:
            put(r, 2, mid, 3, F(12), FILL_T)
        dua = DUA["F"if b["gender"] == "F" else "M"][bi % 2]
        put(r, used, f"{lab}: {dec['name']}  {dua}{wf}", W - used + 1, F(13), FILL_T)
        cols = b["cols"]
        gi_of = {}
        for gi, g in enumerate(b["groups"]):
            for h in g["members"]:
                gi_of[h["id"]] = gi
        # --- رشتہ / نام ---
        r_rel, r_nm, r_kind, r_S = nxt(), nxt(), nxt(), nxt()
        for ci, h in enumerate(cols):
            put(r_rel, 1 + ci, rel_label(h["rel"], lang), 1, F(11), h=22)
            put(r_nm, 1 + ci, h["name"], 1, F(12), h=34)
        # گروہ کی ضم شدہ لکیریں؛ سہام اور رؤوس کی نسبت اسی خانے میں چھوٹے حروف میں
        tkey = {st["key"]: st for st in b["tsteps"]}
        any_note = False
        c = 1
        for g in b["groups"]:
            span = len(g["members"])
            lab_k = g["label"] + (f" ({g['sub']})" if g["sub"] and g["asaba"] else "")
            put(r_kind, c, lab_k, span, F(12), FILL_F, h=24)
            st = tkey.get(g["key"])
            val = g["S"]
            corner = False
            if st and st["u"] > 1:
                if st["status"] == "divisible":
                    kind, m = "برابر", 1
                else:
                    kind, m = ("تباین" if st["status"] == "tabayun" else "توافق"), st["reduced"]
                note = f"{{⤴رؤوس {st['u']}}} {kind} {{سہام⤵ {st['S']}}}  مضـ {m}"
                val = corner_val(note, g["S"], c, span)
                corner = True
                any_note = True
            put(r_S, c, val, span, F(12), h=22, align=CORNER if corner else CEN)
            c += span
        if any_note:
            ws.row_dimensions[r_S].height = 36
        if b["mudrub"] > 1:
            r_fr = nxt()
            c = 1
            for g in b["groups"]:
                span = len(g["members"])
                put(r_fr, c, corner_val(f"\u200e{g['S']}×{b['mudrub']}", g["S"] * b["mudrub"], c, span), span, F(12), h=34, align=CORNER)
                c += span
        # --- سیڑھی ---
        lad = ladders[bi]
        nrows = max(len(v["vals"]) for v in lad["per"].values())
        for k in range(nrows):
            r = nxt()
            for ci, h in enumerate(cols):
                pv = lad["per"][h["id"]]
                if k < len(pv["vals"]):
                    v = pv["vals"][k]
                    last = (k == len(pv["vals"]) - 1)
                    s = "{" + str(v) + "}" if (pv["dies"] and last) else v
                    dead = bool(pv["dies"] and last)
                    put(r, 1 + ci, s, 1, F(13, True, "B00020" if dead else "000000"),
                        FILL_R if dead else None, h=22, box=BOX_R if dead else None)
            if k >= 1:
                kk, f, kind = lad["events"][k - 1]
                put(r, W, f"× {f} / {batan_name(kk)}", 1, F(10, False, "555555"), border=False, align=NOWRAP)
        # --- نوٹس / وضاحت ---
        lines = []
        if b["tsteps"]:
            bits = []
            for s in b["tsteps"]:
                if s["status"] == "divisible":
                    bits.append(f"{s['S']}÷{s['u']} برابر")
                else:
                    bits.append(f"{s['S']}↔{s['u']} {'تباین' if s['status'] == 'tabayun' else 'توافق'} ⇒ {s['reduced']}")
            line = "تصحیح:  " + "،  ".join(bits)
            for ch in b["tchain"]:
                line += f"،  {ch['a']}↔{ch['b']} {ch['ratio']['name']} ⇒ {ch['result']}"
            line += f"  ⇒ {t['mazrub']} {b['mudrub']}  ⇒  {b['asl']}×{b['mudrub']} = {b['T']}"
            lines.append(line)
        if b["radd"] and "ratio" in b["radd"]:
            rd = b["radd"]
            lines.append(f"رد: ما بقیہ {rd['R']} اور من یرد علیہم {rd['S_r']} میں {rd['ratio']['name']} ⇒ "
                         f"اصل ×{rd['mult_asl']}، ردّ والوں کے سہام ×{rd['mult_u']}")
        if b["blocked"]:
            nm = {h["id"]: h["name"] for h in inp["heirs"]}
            lines.append("محروم: " + "،  ".join(f"{nm[p]} ({w})" for p, w in b["blocked"].items()))
        lines += b["notes"]
        if inp.get("note"):
            lines.append(inp["note"])
        for ln in lines:
            r = nxt()
            put(r, 1, ln, W, F(10, False, "333333"), border=False,
                align=Alignment(horizontal="right", vertical="center", wrap_text=True, readingOrder=2),
                h=18 if len(ln) < 110 else 34)
        nxt()

    # ---- آخری سہام ----
    r = nxt()
    put(r, 1, t["total"].format(J=res["J"]), W, F(14), FILL_T, h=28)
    final = res["final"]
    order = []
    for bi, b in enumerate(blocks):
        for h in b["cols"]:
            if h["id"] in final and h["id"] not in order:
                order.append(h["id"])
    per_row = W - 1
    for i in range(0, len(order), per_row):
        chunk = order[i:i + per_row]
        r1, r2 = nxt(), nxt()
        r3 = nxt() if amounts else None
        for ci, pid in enumerate(chunk):
            p = people[pid]
            put(r1, 1 + ci, f"{p['name']}\n{rel_label(p['rel'], lang)} · {p['of']}", 1, F(10), h=44)
            put(r2, 1 + ci, final[pid], 1, F(14), FILL_F, h=26)
            if r3:
                put(r3, 1 + ci, f"{amounts['per'].get(pid, 0):,.2f}", 1, F(11), FILL_B, h=24)
        nxt()
    r = nxt()
    put(r, 1, f"{t['sum']}: {sum(final.values())}   =   {t['jami']}: {res['J']}", W, F(13), FILL_F, h=26)
    if amounts:
        r = nxt()
        put(r, 1, f"قابلِ تقسیم رقم (تجہیز و تکفین، قرض اور وصیت کے بعد): {amounts['distributable']:,.2f}",
            W, F(12), FILL_B, h=26)
    nxt()
    r = nxt()
    put(r, 1, t["ver"], W, F(12), FILL_T)
    for name, ok, det in res["verification"]:
        r = nxt()
        put(r, 1, f"{t['ok'] if ok else t['bad']}   {name}   [{det}]", W, F(10, False), border=False,
            align=Alignment(horizontal="right", readingOrder=2))
    for n in case.get("notes", []):
        r = nxt()
        put(r, 1, "نوٹ: " + n, W, F(11), border=False, h=32,
            align=Alignment(horizontal="right", vertical="center", wrap_text=True, readingOrder=2))
    nxt()
    for ln in case.get("footer", []) or [t["last"]]:
        r = nxt()
        put(r, 1, ln, W, F(12), border=False)

    # ---- چھپائی ----
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "landscape" if W >= 11 else "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1 if row[0] <= 70 else 0
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.4
    wb.save(path)
    return path
