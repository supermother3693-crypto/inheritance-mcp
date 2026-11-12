# -*- coding: utf-8 -*-
"""اسلامی علمُ الفرائض — ریاضیاتی انجن (حنفی مسلک، «کتاب الفرائض آسان سراجی» کے مطابق)

حصہ A: تقسیمِ سہام۔ (روپے / جائیداد کی قیمت کا حساب جان بوجھ کر شامل نہیں۔)

مراحل:  شرعی حیثیت (حجب، فرض، عصبہ) → اصلِ مسئلہ → عول / رد → تصحیح (مضروب)
        → مناسخہ (ما فی الید، چار نسبتیں، وفق، مضروب، جامعہ) → آخری سہام → تصدیق
"""
from fractions import Fraction as Fr
from math import gcd
from .relations import ORDER, rel_gender, rel_label


class FaraidError(Exception):
    """ایسی غلطی جس میں انجن آگے نہیں بڑھ سکتا (معلومات ناقص / غیر معاون صورت)۔"""


def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_list(xs):
    r = 1
    for x in xs:
        r = lcm(r, x)
    return r


FRAC_LABEL = {Fr(1, 2): "نصف", Fr(1, 4): "ربع", Fr(1, 8): "ثمن", Fr(2, 3): "ثلثان",
              Fr(1, 3): "ثلث", Fr(1, 6): "سدس"}
WAFQ_NAME = {2: "بالنصف", 3: "بالثلث", 4: "بالربع", 5: "بالخمس", 6: "بالسدس",
             7: "بالسبع", 8: "بالثمن", 9: "بالتسع", 10: "بالعشر"}

SPOUSES = ("husband", "wife")


# ----------------------------------------------------------------------------
# چار نسبتیں
# ----------------------------------------------------------------------------
def ratio(a: int, b: int) -> dict:
    """a اور b کے درمیان تماثل / تداخل / توافق / تباین (حساب سے، اندازے سے نہیں)۔"""
    g = gcd(a, b)
    if a == b:
        kind, name = "tamathul", "تماثل"
    elif g > 1 and (a % b == 0 or b % a == 0):
        kind, name = "tadakhul", "تداخل"
    elif g > 1:
        kind = "tawafuq"
        name = "توافق " + WAFQ_NAME.get(g, f"بجزء من {g}")
    else:
        kind, name = "tabayun", "تباین"
    return {"kind": kind, "name": name, "g": g, "a": a, "b": b, "wafq_a": a // g, "wafq_b": b // g}


# ----------------------------------------------------------------------------
# ایک مسئلہ (ایک مورث) کا حل
# ----------------------------------------------------------------------------
def solve_block(heirs, dec_gender):
    """heirs: [{'id','name','rel', 'level'(اختیاری)}]   dec_gender: 'M' یا 'F'"""
    by = {r: [] for r in ORDER}
    for h in heirs:
        by[h["rel"]].append(h)
    n0 = {r: len(v) for r, v in by.items()}
    n = dict(n0)
    blocked = {}      # pid -> سبب
    notes = []

    # --- بنیادی جانچ ---
    if n0["husband"] and dec_gender == "M":
        raise FaraidError("مورث مرد ہے مگر شوہر درج ہے۔")
    if n0["wife"] and dec_gender == "F":
        raise FaraidError("مورثہ عورت ہے مگر بیوی درج ہے۔")
    if n0["husband"] > 1:
        raise FaraidError("شوہر ایک سے زیادہ نہیں ہو سکتا۔")
    for r in ("father", "mother", "grandfather"):
        if n0[r] > 1:
            raise FaraidError(f"{rel_label(r)} ایک سے زیادہ نہیں ہو سکتا (قریب ترین ایک ہی درج کریں)۔")
    if n0["wife"] > 4:
        raise FaraidError("بیویاں چار سے زیادہ درج ہیں۔")
    if not heirs:
        raise FaraidError("کوئی وارث درج نہیں۔")

    def block(rs, reason):
        for r in rs:
            for h in by[r]:
                if h["id"] not in blocked:
                    blocked[h["id"]] = reason
            n[r] = 0

    # --- حجبِ حرمان ---
    if n["father"]:
        block(["grandfather"], "باپ کی موجودگی")
    gms = by["grandmother_m"] + by["grandmother_p"]
    if n["mother"]:
        block(["grandmother_m", "grandmother_p"], "ماں کی موجودگی")
    else:
        if n["father"]:
            block(["grandmother_p"], "باپ کی موجودگی")
        rem = [h for h in gms if h["id"] not in blocked]
        if rem:
            lv = min(h.get("level", 2) for h in rem)
            for h in rem:
                if h.get("level", 2) > lv:
                    blocked[h["id"]] = "قریب کی جدہ کی موجودگی"
                    n[h["rel"]] -= 1

    if n["son"]:
        block(["grandson", "granddaughter"], "بیٹے کی موجودگی")
    elif n["daughter"] >= 2 and not n["grandson"]:
        block(["granddaughter"], "دو (یا زیادہ) بیٹیاں ثلثان پورا کر چکیں")

    desc_male = (n["son"] + n["grandson"]) > 0
    female_desc = (n0["daughter"] + n["granddaughter"]) > 0
    child = (n0["son"] + n0["daughter"] + n0["grandson"] + n0["granddaughter"]) > 0
    sib0 = sum(n0[r] for r in ("full_brother", "full_sister", "cons_brother", "cons_sister",
                               "ut_brother", "ut_sister"))
    agnates = ["full_nephew", "cons_nephew", "full_uncle", "cons_uncle", "full_cousin", "cons_cousin"]
    sibs_fc = ["full_brother", "full_sister", "cons_brother", "cons_sister"]

    if n["grandfather"] and sib0 and (n0["full_brother"] + n0["full_sister"] + n0["cons_brother"] + n0["cons_sister"]):
        notes.append("اختلاف: دادا کے ساتھ حقیقی/علاتی بھائی بہن — امام ابو حنیفہؒ (مفتی بہ، کتاب ص 225) کے قول پر "
                     "دادا کی موجودگی میں بھائی بہن محروم ہیں؛ صاحبینؒ/زید بن ثابتؓ کے قول پر مقاسمہ ہوتا ہے (اس انجن میں فعال نہیں)۔")
    root = bool(n["father"] or n["grandfather"] or desc_male)
    if root:
        why = ("بیٹے/پوتے کی موجودگی" if desc_male else ("باپ کی موجودگی" if n["father"] else "دادا کی موجودگی"))
        block(sibs_fc + agnates, why)
    if child or n["father"] or n["grandfather"]:
        why = "اولاد کی موجودگی" if child else ("باپ کی موجودگی" if n["father"] else "دادا کی موجودگی")
        block(["ut_brother", "ut_sister"], why)

    groups = []   # ہر گروہ: dict

    def G(key, rels, frac=None, asaba=False, label="", sub="", members=None):
        mem = members if members is not None else [h for r in rels for h in by[r] if h["id"] not in blocked]
        if not mem:
            return None
        g = {"key": key, "rels": list(rels), "members": mem, "frac": frac, "asaba": asaba,
             "label": label, "sub": sub, "S": 0}
        groups.append(g)
        return g

    # --- زوجین ---
    spouse_frac = None
    if n["husband"]:
        spouse_frac = Fr(1, 4) if child else Fr(1, 2)
        G("husband", ["husband"], spouse_frac, label=FRAC_LABEL[spouse_frac])
    if n["wife"]:
        spouse_frac = Fr(1, 8) if child else Fr(1, 4)
        G("wife", ["wife"], spouse_frac, label=FRAC_LABEL[spouse_frac])

    # --- ماں ---
    umariyya = False
    if n["mother"]:
        if child or sib0 >= 2:
            G("mother", ["mother"], Fr(1, 6), label="سدس")
        elif spouse_frac is not None and n["father"]:
            umariyya = True
            G("mother", ["mother"], Fr(1, 3) * (1 - spouse_frac), label="ثلث ما بقی")
            notes.append("ماں کو زوجین میں سے ایک اور باپ کے ساتھ ثلث ما بقی ملا (ص 114)۔")
        else:
            lab = "ثلث"
            if n["grandfather"] and spouse_frac is not None:
                lab = "ثلث الکل"
                notes.append("دادا کی موجودگی میں ماں کو کل مال کا ثلث (طرفین ؒ کا قول، ص 116؛ ابو یوسفؒ کے نزدیک ثلث ما بقی)۔")
            G("mother", ["mother"], Fr(1, 3), label=lab)

    # --- باپ / دادا: فرض + عصبہ ---
    asaba_group = None
    for r in ("father", "grandfather"):
        if n[r]:
            if desc_male:
                G(r, [r], Fr(1, 6), label="سدس")
            elif female_desc:
                asaba_group = G(r, [r], Fr(1, 6), asaba=True, label="سدس + عصبہ", sub="بنفسہ")
            else:
                asaba_group = G(r, [r], None, asaba=True, label="عصبہ", sub="بنفسہ")

    # --- جدات ---
    gm_eff = [h for h in gms if h["id"] not in blocked]
    if gm_eff:
        G("grandmothers", ["grandmother_m", "grandmother_p"], Fr(1, 6), label="سدس", members=gm_eff)

    # --- اولاد ---
    if n["son"]:
        asaba_group = G("children", ["son", "daughter"], asaba=True, label="عصبہ",
                        sub=("بالغیر" if n["daughter"] else "بنفسہ"))
    else:
        if n["daughter"]:
            G("daughters", ["daughter"], Fr(1, 2) if n["daughter"] == 1 else Fr(2, 3),
              label="نصف" if n["daughter"] == 1 else "ثلثان")
        if n["grandson"]:
            asaba_group = G("grandchildren", ["grandson", "granddaughter"], asaba=True, label="عصبہ",
                            sub=("بالغیر" if n["granddaughter"] else "بنفسہ"))
        elif n["granddaughter"]:
            if n["daughter"] == 0:
                G("granddaughters", ["granddaughter"], Fr(1, 2) if n["granddaughter"] == 1 else Fr(2, 3),
                  label="نصف" if n["granddaughter"] == 1 else "ثلثان")
            elif n["daughter"] == 1:
                G("granddaughters", ["granddaughter"], Fr(1, 6), label="سدس",
                  sub="تکملۂ ثلثین")

    # --- اخیافی ---
    u = n["ut_brother"] + n["ut_sister"]
    if u:
        G("uterine", ["ut_brother", "ut_sister"], Fr(1, 6) if u == 1 else Fr(1, 3),
          label="سدس" if u == 1 else "ثلث")

    # --- حقیقی / علاتی بہن بھائی ---
    fb, fs, cb, cs = n["full_brother"], n["full_sister"], n["cons_brother"], n["cons_sister"]
    if not root:
        if fb:
            asaba_group = G("full_sibs", ["full_brother", "full_sister"], asaba=True, label="عصبہ",
                            sub=("بالغیر" if fs else "بنفسہ"))
        elif fs:
            if female_desc:
                asaba_group = G("full_sibs", ["full_sister"], asaba=True, label="عصبہ", sub="مع الغیر")
            else:
                G("full_sisters", ["full_sister"], Fr(1, 2) if fs == 1 else Fr(2, 3),
                  label="نصف" if fs == 1 else "ثلثان")
        full_asaba = bool(fb or (fs and female_desc))
        if full_asaba:
            block(["cons_brother", "cons_sister"], "حقیقی بھائی / عصبہ بہن کی موجودگی")
        else:
            if cb:
                asaba_group = G("cons_sibs", ["cons_brother", "cons_sister"], asaba=True, label="عصبہ",
                                sub=("بالغیر" if cs else "بنفسہ"))
            elif cs:
                if female_desc:
                    asaba_group = G("cons_sibs", ["cons_sister"], asaba=True, label="عصبہ", sub="مع الغیر")
                elif fs == 0:
                    G("cons_sisters", ["cons_sister"], Fr(1, 2) if cs == 1 else Fr(2, 3),
                      label="نصف" if cs == 1 else "ثلثان")
                elif fs == 1:
                    G("cons_sisters", ["cons_sister"], Fr(1, 6), label="سدس", sub="تکملۂ ثلثین")
                else:
                    block(["cons_sister"], "دو حقیقی بہنوں نے ثلثان پورا کر لیا")
        # دور کے عصبات (قریب ترین نوع ہی)
        if asaba_group is None:
            found = None
            for r in agnates:
                if n[r] and not found:
                    found = r
                    asaba_group = G(r, [r], asaba=True, label="عصبہ", sub="بنفسہ")
                elif n[r]:
                    block([r], "قریب کے عصبہ کی موجودگی")
        else:
            block(agnates, "قریب کے عصبہ کی موجودگی")

    # ------------------------------------------------------------------
    # اعداد
    # ------------------------------------------------------------------
    fard_groups = [g for g in groups if g["frac"]]
    sum_f = sum((g["frac"] for g in fard_groups), Fr(0))
    asaba_g = asaba_group
    awl = False
    radd = None
    asl_f = lcm_list([g["frac"].denominator for g in fard_groups]) if fard_groups else 1

    # عصبہ کی اکائیاں (مرد 2، عورت 1 — صرف جب دونوں جنس ہوں)
    for g in groups:
        if g["asaba"]:
            genders = {rel_gender(h["rel"]) for h in g["members"]}
            mixed = len(genders) == 2
            g["units"] = {h["id"]: (2 if (mixed and rel_gender(h["rel"]) == "M") else 1) for h in g["members"]}
        else:
            g["units"] = {h["id"]: 1 for h in g["members"]}
        g["u"] = sum(g["units"].values())

    if not fard_groups and asaba_g is None:
        raise FaraidError("درج وارثوں میں سے کوئی فرض/عصبہ والا نہیں (ذوی الارحام کا حساب اس انجن میں فعال نہیں)۔")
    if not fard_groups:
        # سب عصبہ: اصل = کل اکائیاں
        asl = asaba_g["u"]
        asaba_g["S"] = asl
        asl_f = asl
    else:
        for g in fard_groups:
            g["S"] = int(g["frac"] * asl_f)
        used = sum(g["S"] for g in fard_groups)
        if used > asl_f:                         # عول
            awl = True
            asl = used
            if asaba_g is not None:
                notes.append("عول کی وجہ سے عصبہ کے لیے کچھ نہ بچا (محروم)۔")
        elif asaba_g is not None:
            rest = asl_f - used
            asaba_g["S"] += rest
            asl = asl_f
            if rest == 0:
                notes.append("فرض والوں سے مال ختم ہو گیا، عصبہ کے لیے کچھ نہ بچا۔")
        elif used == asl_f:
            asl = asl_f
        else:                                    # رد
            elig = [g for g in fard_groups if g["key"] not in SPOUSES]
            sp = [g for g in fard_groups if g["key"] in SPOUSES]
            if elig:
                if len(elig) == 1:
                    for g in elig:
                        g["runit"] = len(g["members"])
                    qism = "اول" if not sp else "سوم"
                else:
                    for g in elig:
                        g["runit"] = int(g["frac"] * 6)
                    qism = "دوم" if not sp else "چہارم"
                S_r = sum(g["runit"] for g in elig)
                if not sp:
                    asl = S_r
                    for g in elig:
                        g["S"] = g["runit"]
                    radd = {"qism": qism, "from": asl_f, "S_r": S_r}
                else:
                    sg = sp[0]
                    asl_sp = sg["frac"].denominator
                    sg["S"] = sg["frac"].numerator
                    R = asl_sp - sg["S"]
                    rr = ratio(R, S_r)
                    mult_asl, mult_u = S_r // rr["g"], R // rr["g"]
                    asl = asl_sp * mult_asl
                    asl_f = asl_sp
                    sg["S"] *= mult_asl
                    for g in elig:
                        g["S"] = g["runit"] * mult_u
                    radd = {"qism": qism, "from": asl_f, "S_r": S_r, "R": R, "ratio": rr,
                            "mult_asl": mult_asl, "mult_u": mult_u, "asl_sp": asl_sp}
            elif sp:
                sg = sp[0]
                asl = len(sg["members"])
                sg["S"] = asl
                radd = {"qism": "زوجین", "from": asl_f, "S_r": asl}
                notes.append("نسبی وارث نہیں؛ متاخرین احناف کے فتویٰ پر باقی مال زوج/زوجہ کو دیا گیا (ص 208)۔ "
                             "اگر ذوی الارحام موجود ہوں تو پہلے ان کا حق دیکھا جائے (انجن میں فعال نہیں)۔")
            else:
                raise FaraidError("کوئی مستحق وارث نہیں بچا — باقی مال بیت المال۔")

    # --- تصحیح ---
    tsteps = []
    reduced = []
    active = [g for g in groups if g["S"] > 0]
    for g in groups:
        if g["S"] == 0 and g["members"]:
            for h in g["members"]:
                blocked[h["id"]] = "عول/استغراق کی وجہ سے کچھ نہ بچا"
    for g in active:
        S, uu = g["S"], g["u"]
        if S % uu == 0:
            st, red = "divisible", 1
        else:
            d = gcd(S, uu)
            if d == 1:
                st, red = "tabayun", uu
            else:
                st, red = "tawafuq", uu // d
        tsteps.append({"key": g["key"], "S": S, "u": uu, "status": st, "reduced": red})
        g["reduced"] = red
        if red > 1:
            reduced.append(red)

    # کم ہوئے اعداد کی آپس کی نسبتیں (جیسا کتاب میں)
    chain = []
    acc = 1
    seq = []
    for v in sorted(set(reduced)):
        seq.append(v)
    if seq:
        acc = seq[0]
        for v in seq[1:]:
            rr = ratio(acc, v)
            newacc = lcm(acc, v)
            chain.append({"a": acc, "b": v, "ratio": rr, "result": newacc})
            acc = newacc
    mudrub = acc if reduced else 1
    # tamathul: برابر اعداد ایک شمار
    T = asl * mudrub

    shares = {}
    for g in active:
        for h in g["members"]:
            shares[h["id"]] = g["S"] * mudrub * g["units"][h["id"]] // g["u"]
            if (g["S"] * mudrub * g["units"][h["id"]]) % g["u"]:
                raise FaraidError("اندرونی غلطی: تصحیح کے بعد سہام صحیح عدد نہیں بنے۔")
    if sum(shares.values()) != T:
        raise FaraidError(f"اندرونی غلطی: مجموعۂ سہام {sum(shares.values())} ≠ تصحیح {T}")

    # ظاہر ہونے کی ترتیب
    order_idx = {r: i for i, r in enumerate(ORDER)}
    cols = [h for h in heirs if h["id"] in shares]
    cols.sort(key=lambda h: order_idx[h["rel"]])
    # گروہ کو ترتیب دیں: جس گروہ کا پہلا رکن پہلے آئے
    gorder = []
    for h in cols:
        for gi, g in enumerate(active):
            if any(m["id"] == h["id"] for m in g["members"]) and gi not in gorder:
                gorder.append(gi)
    active_sorted = [active[i] for i in gorder]
    # ہر گروہ کے ارکان متصل رکھیں
    cols2 = []
    for g in active_sorted:
        cols2 += sorted(g["members"], key=lambda h: order_idx[h["rel"]])
    return {
        "asl_f": asl_f, "asl": asl, "awl": awl, "radd": radd, "umariyya": umariyya,
        "groups": active_sorted, "all_groups": groups, "tsteps": tsteps, "tchain": chain,
        "mudrub": mudrub, "T": T, "shares": shares, "cols": cols2,
        "blocked": {pid: why for pid, why in blocked.items() if pid not in shares},
        "notes": notes, "sum_f": sum_f,
    }


# ----------------------------------------------------------------------------
# مناسخہ: پورا سلسلہ
# ----------------------------------------------------------------------------
def solve_case(case):
    """case = {'title','lang','blocks':[{'deceased':{...},'heirs':[...]}]}  →  نتیجہ dict"""
    blocks_in = case["blocks"]
    if not blocks_in:
        raise FaraidError("کوئی مسئلہ درج نہیں۔")
    people = {}          # pid -> {'name','rel','block'}  (جو کسی نہ کسی بطن میں وارث بنے)
    dead_at = {}         # pid -> block index جس میں وہ مورث بنا
    results = []
    steps = []           # مناسخہ کے مراحل (بلاک 2 سے)
    shares = {}          # موجودہ جامعہ میں زندہ لوگوں کے سہام
    J = None
    verification = []

    first_dead_id = None
    for bi, b in enumerate(blocks_in):
        dec = b["deceased"]
        heirs = b["heirs"]
        ids = [h["id"] for h in heirs]
        if len(set(ids)) != len(ids):
            raise FaraidError(f"بطن {bi + 1}: ایک ہی نام/آئی ڈی دو بار درج ہے — `نام#نشانی` سے فرق کریں۔")
        for h in heirs:
            if h["id"] in dead_at:
                raise FaraidError(f"بطن {bi + 1}: «{h['name']}» پہلے فوت ہو چکا/چکی ہے، وارث نہیں بن سکتا۔")
            if bi > 0 and h["id"] == dec["id"]:
                raise FaraidError(f"بطن {bi + 1}: مورث خود اپنا وارث درج ہے۔")
            if first_dead_id and h["id"] == first_dead_id:
                raise FaraidError(f"بطن {bi + 1}: پہلا مورث وارث کے طور پر درج ہے۔")

        if bi == 0:
            first_dead_id = dec["id"]
            gender = dec.get("gender") or _infer_gender(heirs)
            if gender not in ("M", "F"):
                raise FaraidError("پہلے مورث کی جنس معلوم نہیں: «جنس: مرد/عورت» لکھیں (یا مورثہ:)۔")
            r = solve_block(heirs, gender)
            m = None
            dec_shares = None
            J = r["T"]
            fJ = fh = 1
            r.update({"m": None, "ratio": None, "fJ": 1, "fh": 1, "J_after": J, "gender": gender})
            for pid, s in r["shares"].items():
                shares[pid] = shares.get(pid, 0) + s
        else:
            pid = dec["id"]
            if pid not in shares:
                if pid in dead_at:
                    raise FaraidError(f"بطن {bi + 1}: «{dec['name']}» پہلے ہی فوت شمار ہو چکا ہے۔")
                raise FaraidError(f"بطن {bi + 1}: «{dec['name']}» پچھلے بطون میں کسی کا وارث نہیں بنا یا اس کا حصہ صفر ہے۔")
            m = shares[pid]
            gender = dec.get("gender") or people[pid]["gender"]
            r = solve_block(heirs, gender)
            T = r["T"]
            rr = ratio(m, T)
            fJ, fh = T // rr["g"], m // rr["g"]
            # ما فی الید کا ذریعہ: کن بطون سے کتنا ملا
            J_before = J
            for k in list(shares):
                shares[k] *= fJ
            J *= fJ
            m_after = shares.pop(pid)            # = m * fJ
            if m_after != T * fh:
                raise FaraidError("اندرونی غلطی: مورث کا حصہ نئے مسئلے کے برابر نہیں بنا۔")
            for hid, s in r["shares"].items():
                shares[hid] = shares.get(hid, 0) + s * fh
            r.update({"m": m, "ratio": rr, "fJ": fJ, "fh": fh, "J_before": J_before, "J_after": J,
                      "gender": gender})
            dead_at[pid] = bi
        for h in heirs:
            if h["id"] not in people:
                people[h["id"]] = {"name": h["name"], "rel": h["rel"], "block": bi,
                                   "gender": rel_gender(h["rel"]), "of": dec["name"]}
        results.append(r)
        if bi == 0:
            dead_at[dec["id"]] = -1

    # ما فی الید کے ذرائع (بطن در بطن) — نقشے میں جمع دکھانے کے لیے
    _fill_sources(results, blocks_in)

    final = dict(shares)
    total = sum(final.values())
    verification.append(("آخری سہام کا مجموعہ = جامعہ", total == J, f"{total} = {J}"))
    for bi, r in enumerate(results):
        verification.append((f"بطن {bi + 1}: مجموعۂ سہام = تصحیح", sum(r["shares"].values()) == r["T"],
                             f"{sum(r['shares'].values())} = {r['T']}"))
        if bi:
            ok = r["m"] * r["fJ"] == r["T"] * r["fh"]
            verification.append((f"بطن {bi + 1}: ما فی الید × مضروب(ورثائے اولین) = تصحیح × مضروب(نئے ورثاء)", ok,
                                 f"{r['m']}×{r['fJ']} = {r['T']}×{r['fh']}"))
    if not all(v[1] for v in verification):
        raise FaraidError("تصدیق ناکام: " + "; ".join(v[0] for v in verification if not v[1]))

    ladders = _ladders(results, blocks_in, dead_at)
    return {"blocks": results, "inputs": blocks_in, "people": people, "final": final, "J": J,
            "ladders": ladders, "verification": verification, "dead_at": dead_at}


def _infer_gender(heirs):
    rels = {h["rel"] for h in heirs}
    if "husband" in rels:
        return "F"
    if "wife" in rels:
        return "M"
    return None


def _fill_sources(results, blocks_in):
    """مورث کے ما فی الید کا حساب: ہر بطن سے اس کا حصہ (وقتِ وفات کے پیمانے پر)۔"""
    K = len(results)
    for bi in range(1, K):
        pid = blocks_in[bi]["deceased"]["id"]
        parts = []
        for b in range(bi):
            if pid in results[b]["shares"]:
                v = results[b]["shares"][pid]
                if b > 0:
                    v *= results[b]["fh"]
                for k in range(b + 1, bi):
                    v *= results[k]["fJ"]
                parts.append((b, v))
        results[bi]["m_parts"] = parts


def _ladders(results, blocks_in, dead_at):
    """ہر بطن کے ہر وارث کے لیے سہام کی «سیڑھی»: تصحیح → بعد کے ہر ضرب (>1) کے بعد۔"""
    K = len(results)
    out = []
    for b in range(K):
        r = results[b]
        events = []
        if b > 0 and r["fh"] > 1:
            events.append((b, r["fh"], "new"))
        for k in range(b + 1, K):
            if results[k]["fJ"] > 1:
                events.append((k, results[k]["fJ"], "old"))
        per = {}
        for pid, t in r["shares"].items():
            d = dead_at.get(pid, None)
            vals = [t]
            cum = t
            part = 0
            for (k, f, kind) in events:
                if kind == "old" and d is not None and d >= 0 and k >= d:
                    break
                cum *= f
                vals.append(cum)
            per[pid] = {"vals": vals, "dies": (d is not None and d > b)}
        out.append({"events": events, "per": per})
    return out
