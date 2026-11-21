# -*- coding: utf-8 -*-
"""روایتی نقشہ (Excel): دائیں سے بائیں، A4، چھاپنے کے قابل۔ ترتیب آپ کے نمونوں جیسی۔"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl import load_workbook
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
BLUE = InlineFont(rFont="Arial", sz=8, b=True, color="1F4E9C")          # "محفوظ n" کا عنوان
BOXB = InlineFont(rFont="Arial", sz=9, b=True, color="1F4E9C")          # تصحیح خانے کا نیلا عنوان
BOXBIG = InlineFont(rFont="Arial", sz=13, b=True, color="1F4E9C")
BOXN = InlineFont(rFont="Arial", sz=9, b=False, color="333333")
_WAFQ = {2: "بالنصف", 3: "بالثلث", 4: "بالربع", 5: "بالخمس", 6: "بالسدس", 7: "بالسبع", 8: "بالثمن", 9: "بالتسع", 10: "بالعشر"}


def tawafuq_name(g):
    """توافق کا مکمل نام: مشترک عدد 2 → بالنصف، 3 → بالثلث ... اس سے اوپر → بجزء من n۔"""
    return "توافق " + (_WAFQ[g] if g in _WAFQ else f"بجزء من {g}")



def _wpx(text, per=4.8):
    """8pt چھوٹے ٹیکسٹ کی اندازاً چوڑائی (پکسل)۔"""
    return sum(5.9 if ch.isdigit() else (2.96 if ch == " " else per) for ch in text) * 1.05



def ratio_kind(st):
    """رؤوس اور سہام کی نسبت: (نام، مضروب، بائیں کونے کا دخل/وفق)۔
    تماثل: برابر | تداخل: ایک عدد دوسرے میں پورا (سہام چھوٹے ہوں تو دخل = رؤوس÷سہام)
    توافق: مشترک عدد (وفق) | تباین: کوئی مشترک نہیں۔"""
    S, u = st["S"], st["u"]
    if st["status"] == "divisible":
        return ("تماثل" if S == u else "تداخل"), 1, ""
    if st["status"] == "tabayun":
        return "تباین", st["reduced"], ""
    if S < u and u % S == 0:
        return "تداخل", st["reduced"], f"دخل {u // S}"
    return tawafuq_name(u // st["reduced"]), st["reduced"], f"وفق {S // (u // st['reduced'])}"

_COLW = {}       # اصل کالم → چوڑائی (حرفوں میں)؛ خالی ہو تو پہلے سے طے شدہ ناپ
_CUR_W = [7]


def _colchars(cc):
    """منطقی کالم cc (1 = دائیں) کی چوڑائی۔"""
    actual = _CUR_W[0] - cc + 1
    return _COLW.get(actual, 13 if cc == 1 else 17)


def corner_val(small, big, c, span, cw=10.4, small_left="", blue=""):
    """اصول: اصل عدد خانے کے عین بیچ میں؛ چھوٹا حساب اسی خانے میں دائیں اوپر کے کونے میں،
    اور دخل/وفق (small_left) بائیں اوپر کے کونے میں۔ c = منطقی کالم (1 = دائیں، تنگ)، span = کالم۔
    خالی جگہیں دونوں طرف برابر ڈالی جاتی ہیں تاکہ ایکسل کی سمت جو بھی ہو، عدد بیچ میں رہے۔"""
    px = sum(_colchars(cc) * 7 + 5 for cc in range(c, c + span))                # خانے کی چوڑائی (پکسل)
    p = max(0, int((px - len(str(big)) * cw) / 2 / 5.2) - 1)                      # دونوں طرف خالی جگہیں
    line = small
    if small_left:
        n = max(2, int((px - 10 - _wpx(small) - _wpx(small_left)) / 2.96))
        line = small + " " * n + small_left
    first = ("\u202b" + line + "\u202c\n") if line else ""                      # RTL ترتیب: پہلا دائیں، آخری بائیں
    if blue:                                                                    # نیلی سطر: "محفوظ n"
        return CellRichText(TextBlock(SMALL, first), TextBlock(BLUE, "\u202b" + blue + "\u202c\n"),
                            TextBlock(BIGF, " " * p + str(big) + " " * p))
    return CellRichText(TextBlock(SMALL, first), TextBlock(BIGF, " " * p + str(big) + " " * p))


def _build_xlsx(case, res, path, lang=None, amounts=None):
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
    _CUR_W[0] = W
    for c in range(1, W + 1):
        ws.column_dimensions[L(c)].width = _COLW.get(c, 17 if c < W else 13)
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
    for k in range(len(vals) - 1, 0, -1):     # سب سے نچلا عدد (بطن اول کی تصحیح) بطن کے اپنے خانے میں ہے، یہاں نہیں دہرانا
        if len(blocks) == 1:
            break
        r = nxt()
        put(r, 1, vals[k], 1, F(14), FILL_B, h=22)
        put(r, W, f"{vals[k-1]} × {facs[k-1][1]} / {batan_name(facs[k-1][0])}", 1, F(10, False, "555555"), border=False, align=NOWRAP)
    if len(blocks) > 1 and len(vals) > 1:
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
        if bi:   # مضروب یہاں نہیں لکھتے؛ وہ مسئلے کے خانے کے کونے میں چھوٹا لکھا جاتا ہے
            rr = b["ratio"]
            mid = f"{rr['name']}  (↑×{b['fJ']}  ↓×{b['fh']})"
        used = 5 if mid else 2
        # سطر 1: دائیں مسئلہ (دخل/وفق)، بائیں ما في اليد (دخل/وفق)، اور مورث کے نام کے اوپر بطن کا نام
        left_big = None
        left_small = ""          # دخل/وفق: بائیں کونے میں
        right_small = []         # دخل/وفق مسئلے کی طرف
        if bi:
            parts = b.get("m_parts", [])
            left_big = f"{t['mafi']} {b['m']}" + (f"  ({' + '.join(str(v) for _, v in parts)})" if len(parts) > 1 else "")
            rr = b["ratio"]
            if rr["kind"] == "tadakhul":
                q = max(rr["a"], rr["b"]) // min(rr["a"], rr["b"])
                if rr["a"] > rr["b"]:           # ما في اليد بڑا: دخل ما في اليد کی جانب (بائیں)
                    left_small = f"دخل {q}"
                else:                           # مسئلہ بڑا: دخل مسئلے کی جانب (دائیں)
                    right_small.append(f"دخل {q}")
            elif rr["kind"] == "tawafuq":       # دونوں کا وفق: ہر ایک کے ساتھ اپنے خانے میں
                left_small = f"وفق {b['fh']}"
                right_small.append(f"وفق {b['fJ']}")
        calc = f"\u200e{b['mudrub']}×{b['asl']}" if b["mudrub"] > 1 else ""      # حساب: دائیں کونے میں
        r = nxt()
        if left_big:
            if left_small:
                put(r, 2, corner_val("", left_big, 2, used - 2, 8, small_left=left_small), used - 2, F(12), FILL_B,
                    h=34, align=CORNER)
            else:
                put(r, 2, left_big, used - 2, F(12), FILL_B, h=28)
        single = len(blocks) == 1      # ایک ہی بطن: کل عدد دوبارہ نہیں لکھنا (بطن کے خانے/تصحیح کے خانے میں موجود ہے)
        if (calc or right_small) and not single:
            put(r, 1, corner_val(calc, b["T"], 1, 1, small_left="  ".join(right_small)), 1, F(12), h=34, align=CORNER)
        if single:
            put(r, 1, batan_name(bi), W, F(12), FILL_B, h=28)
        else:
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
        r_end = r_S
        tasheeh_box = None
        for ci, h in enumerate(cols):
            put(r_rel, 1 + ci, rel_label(h["rel"], lang), 1, F(11), h=22)
            put(r_nm, 1 + ci, h["name"], 1, F(12), h=34)
        # گروہ کی ضم شدہ لکیریں؛ سہام اور رؤوس کی نسبت اسی خانے میں چھوٹے حروف میں
        tkey = {st["key"]: st for st in b["tsteps"]}
        # کسر والے وہ طائفے جن کا محفوظ عدد بنتا ہے (تماثل / رؤوس کا سہام پر پورا تقسیم ہونا: کچھ نہیں لکھتے)
        n_kasr = sum(1 for g2 in b["groups"] if tkey.get(g2["key"]) and tkey[g2["key"]]["u"] > 1
                     and ratio_kind(tkey[g2["key"]])[1] > 1)
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
                kind, m, left = ratio_kind(st)
                if m > 1:
                    note = f"{{رؤوس ⤴{st['u']}}} {kind} {{سہام ⤵{st['S']}}}"
                    if n_kasr > 1:
                        left = ""          # کئی طائفوں میں کسر: دخل/وفق نہیں، صرف محفوظ عدد
                    elif left.startswith("وفق"):
                        left = f"⤴وفق {m}  ⤵{left}"      # ایک ہی طائفہ: رؤوس اور سہام دونوں کا وفق
                    val = corner_val(note, g["S"], c, span, small_left=left, blue=(f"محفوظ {m}" if n_kasr > 1 else ""))
                    corner = True
                    any_note = True
            put(r_S, c, val, span, F(12), h=22, align=CORNER if corner else CEN)
            c += span
        if any_note:
            ws.row_dimensions[r_S].height = 48
        if b["mudrub"] > 1:
            r_fr = nxt()
            r_end = r_fr
            c = 1
            for g in b["groups"]:
                span = len(g["members"])
                put(r_fr, c, corner_val(f"\u200e{g['S']}×{b['mudrub']}", g["S"] * b["mudrub"], c, span), span, F(12), h=34, align=CORNER)
                c += span
        # --- سیڑھی ---
        lad = ladders[bi]
        nrows = max(len(v["vals"]) for v in lad["per"].values())
        r0 = None
        for k in range(nrows):
            r = nxt()
            if k == 0:
                r0 = r
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
        # --- ایک رکن والے طائفے میں اوپر نیچے کے برابر خانے ایک کر دیں (بیچ کی لکیر ہٹا کر) ---
        r_last = r_fr if b["mudrub"] > 1 else r_S
        if r0 == r_last + 1:
            c = 1
            for g in b["groups"]:
                span = len(g["members"])
                if span == 1:
                    pv = lad["per"][cols[c - 1]["id"]]
                    if pv["vals"] and not (pv["dies"] and len(pv["vals"]) == 1) and pv["vals"][0] == g["S"] * b["mudrub"]:
                        ac = W - c + 1
                        ws.merge_cells(start_row=r_last, start_column=ac, end_row=r0, end_column=ac)
                c += span
        # --- نوٹس / وضاحت ---
        lines = []
        if b["tsteps"]:
            tk_ = {t["key"]: t for t in b["tsteps"]}
            nums = [ts_["reduced"] for g in b["groups"] if (ts_ := tk_.get(g["key"])) and ts_["reduced"] > 1]
            if len(nums) > 1:
                # کئی طائفوں میں کسر: محفوظات کا باہمی مقابلہ، بائیں کالم میں (جہاں بطنوں کے مضروب لکھتے ہیں)
                from math import gcd as _g
                rows_t = []
                acc = nums[0]
                for v in nums[1:]:
                    g_ = _g(acc, v)
                    if acc == v:
                        kind, work, new = "تماثل", "", acc
                    elif acc % v == 0:
                        kind, work, new = "تداخل", "", acc
                    elif v % acc == 0:
                        kind, work, new = "تداخل", "", v
                    elif g_ == 1:
                        kind, work, new = "تباین", "", acc * v
                    else:
                        # توافق: ایک عدد کا وفق × دوسرے کا پورا عدد
                        kind, work, new = tawafuq_name(g_), f"وفق {v // g_} × {acc}", acc * (v // g_)
                    rows_t.append(f"{acc} اور {v}: {kind}" + (f"، {work}" if work else "") + f"  ←  {new}")
                    acc = new
                head = " > ".join(str(n) for n in nums)
                body = "\n" + "\n".join(rows_t) + "\n"
                tasheeh_box = CellRichText(TextBlock(BOXB, "محفوظات: "), TextBlock(BOXN, head + body),
                                           TextBlock(BOXB, "مضروب "), TextBlock(BOXBIG, str(b["mudrub"])),
                                           TextBlock(BOXN, "\n" + f"\u200e{b['asl']} × {b['mudrub']} = {b['T']}"))
            else:
                lines.append(f"تصحیح:  \u202a{b['asl']} × {b['mudrub']} = {b['T']}\u202c")
        if tasheeh_box is not None:
            ws.merge_cells(start_row=r_rel, start_column=1, end_row=r_end, end_column=1)
            bc = ws.cell(r_rel, 1)
            bc.value = tasheeh_box
            bc.alignment = Alignment(horizontal="right", vertical="center", wrap_text=True, readingOrder=2)
            for rr_ in range(r_rel, r_end + 1):
                ws.cell(rr_, 1).border = BOX
            if not _COLW:
                ws.column_dimensions[L(1)].width = 30
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
                h=(15 * (ln.count(chr(10)) + 1) + 4) if ln.count(chr(10)) else (18 if len(ln) < 110 else 34))
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


# ---------------------------------------------------------------------------
# خود کار سائز: کالم کی چوڑائی اور قطار کی اونچائی اندر کے الفاظ کے مطابق
# ---------------------------------------------------------------------------
import math
import re as _re


def _cw(ch, sz, bold):
    """ایک حرف کی اندازاً چوڑائی (پکسل)۔"""
    em = 0.28 if ch == " " else (0.58 if ch.isdigit() else 0.52)
    return em * sz * 1.333 * (1.08 if bold else 1.0)


def _tw(text, sz, bold):
    return sum(_cw(ch, sz, bold) for ch in text if ch not in "\u202a\u202b\u202c\u200e\u200f")


def _cell_lines(cell):
    """سیل کی سطریں: [(سطر کی چوڑائی پکسل، حرف کا سائز)]۔ چھوٹے حروف والی سطروں کے بیچ کی خالی جگہ گنی نہیں جاتی۔"""
    v = cell.value
    if v is None:
        return []
    out = []
    if isinstance(v, CellRichText):
        for part in v:
            if isinstance(part, TextBlock):
                sz = part.font.sz or 11
                bold = bool(part.font.b)
                txt = part.text
            else:
                sz, bold, txt = (cell.font.sz or 11), False, str(part)
            for ln in txt.split("\n"):
                if not ln.strip() and ln != txt.split("\n")[-1]:
                    continue
                pcs = [x for x in _re.split(r" {3,}", ln.strip()) if x.strip()]
                if not pcs:
                    continue
                out.append((sum(_tw(x.strip(), sz, bold) for x in pcs) + (14 if len(pcs) > 1 else 0), sz))
    else:
        sz = cell.font.sz or 11
        bold = bool(cell.font.b)
        for ln in str(v).split("\n"):
            out.append((_tw(ln, sz, bold), sz))
    return out


def autofit(wb, small_cap=125):
    """ہر کالم کی چوڑائی اس کے سب سے لمبے متن کے مطابق، اور ہر قطار کی اونچائی اس کی سطروں کے مطابق۔
    پورے نقشے پر پھیلی (ضم شدہ) سطریں چوڑائی طے نہیں کرتیں؛ وہ لپٹ کر اپنی اونچائی لیتی ہیں۔"""
    ws = wb.active
    maxc, maxr = ws.max_column, ws.max_row
    merged = {}
    covered = set()
    for mr in ws.merged_cells.ranges:
        merged[(mr.min_row, mr.min_col)] = mr
        for r in range(mr.min_row, mr.max_row + 1):
            for c in range(mr.min_col, mr.max_col + 1):
                if (r, c) != (mr.min_row, mr.min_col):
                    covered.add((r, c))
    colpx = {c: 60.0 for c in range(1, maxc + 1)}
    for (r, c), mr in merged.items():
        pass
    for r in range(1, maxr + 1):
        for c in range(1, maxc + 1):
            if (r, c) in covered:
                continue
            mr = merged.get((r, c))
            if mr is not None and mr.max_col > mr.min_col:
                continue                                    # افقی ضم شدہ: چوڑائی طے نہیں کرتا
            cell = ws.cell(r, c)
            lines = _cell_lines(cell)
            if not lines:
                continue
            need = max((min(w, small_cap) if sz < 10 else w) for w, sz in lines) + 16
            colpx[c] = max(colpx[c], need)
    for c, px in colpx.items():
        ws.column_dimensions[L(c)].width = round((px - 5) / 7, 1)
    # قطاروں کی اونچائی
    need_rows = {}
    for r in range(1, maxr + 1):
        best = 0.0
        for c in range(1, maxc + 1):
            if (r, c) in covered:
                continue
            mr = merged.get((r, c))
            if mr is not None and mr.max_row > mr.min_row:
                continue                                    # عمودی ضم شدہ: نیچے الگ دیکھتے ہیں
            cell = ws.cell(r, c)
            lines = _cell_lines(cell)
            if not lines:
                continue
            span_px = sum(colpx[cc] for cc in range(c, (mr.max_col if mr else c) + 1)) - 12
            wrap = bool(cell.alignment and cell.alignment.wrap_text)
            h = 6.0
            for w, sz in lines:
                n = max(1, math.ceil(w / span_px)) if wrap else 1
                h += n * sz * 1.5
            best = max(best, h)
        if best:
            need_rows[r] = max(best, 18.0)
            ws.row_dimensions[r].height = round(need_rows[r], 1)
    for (r, c), mr in merged.items():                           # عمودی ضم شدہ خانے
        if mr.max_row == mr.min_row:
            continue
        lines = _cell_lines(ws.cell(r, c))
        span_px = sum(colpx[cc] for cc in range(mr.min_col, mr.max_col + 1)) - 12
        h = 8.0 + sum(max(1, math.ceil(w / span_px)) * sz * 1.5 for w, sz in lines)
        have = sum((ws.row_dimensions[rr].height or 15) for rr in range(mr.min_row, mr.max_row + 1))
        if have < h:
            last = mr.max_row
            ws.row_dimensions[last].height = round((ws.row_dimensions[last].height or 15) + (h - have), 1)
    return {c: round((px - 5) / 7, 1) for c, px in colpx.items()}


def build_xlsx(case, res, path, lang=None, amounts=None, fit=True):
    """پہلی بار عام ناپ سے بنا کر کالم کی چوڑائیاں نکالتا ہے، پھر انہی چوڑائیوں پر دوبارہ بناتا ہے
    (تاکہ عدد بیچ میں رہیں)، اور آخر میں قطاروں کی اونچائی متن کے مطابق لگاتا ہے۔"""
    global _COLW
    _COLW = {}
    _build_xlsx(case, res, path, lang, amounts)
    if not fit:
        return path
    wb = load_workbook(path, rich_text=True)
    _COLW = autofit(wb)
    _build_xlsx(case, res, path, lang, amounts)
    wb = load_workbook(path, rich_text=True)
    autofit(wb)
    wb.save(path)
    _COLW = {}
    return path
