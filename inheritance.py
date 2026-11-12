"""Hanafi inheritance (ilm-ul-faraid) calculator.

Pure Python, no third-party packages. All shares are exact Fractions.

Supported heirs (one generation level each):
  spouse, father, mother, paternal grandfather, paternal grandmother,
  maternal grandmother, sons, daughters, son's sons, son's daughters,
  full / consanguine (paternal half) / uterine (maternal half) siblings,
  and a flag for "other agnatic relative" (uncle, nephew, etc.).

Not covered (a scholar must decide): dhawil-arham (distant relatives),
great-grandparents, missing person, unborn child, difference of religion,
murder, adoption, double relationships and similar special cases.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import lcm
from typing import Any

LABELS: dict[str, tuple[str, str]] = {
    "husband": ("شوہر", "Husband"),
    "wives": ("بیوی/بیویاں", "Wife/Wives"),
    "father": ("والد", "Father"),
    "mother": ("والدہ", "Mother"),
    "paternal_grandfather": ("دادا", "Paternal grandfather"),
    "paternal_grandmother": ("دادی", "Paternal grandmother"),
    "maternal_grandmother": ("نانی", "Maternal grandmother"),
    "sons": ("بیٹے", "Sons"),
    "daughters": ("بیٹیاں", "Daughters"),
    "grandsons": ("پوتے (بیٹے کے بیٹے)", "Son's sons"),
    "granddaughters": ("پوتیاں (بیٹے کی بیٹیاں)", "Son's daughters"),
    "full_brothers": ("حقیقی بھائی", "Full brothers"),
    "full_sisters": ("حقیقی بہنیں", "Full sisters"),
    "consanguine_brothers": ("علاتی بھائی (باپ شریک)", "Paternal half-brothers"),
    "consanguine_sisters": ("علاتی بہنیں (باپ شریک)", "Paternal half-sisters"),
    "uterine_brothers": ("اخیافی بھائی (ماں شریک)", "Maternal half-brothers"),
    "uterine_sisters": ("اخیافی بہنیں (ماں شریک)", "Maternal half-sisters"),
    "other_agnate": ("دیگر عصبہ رشتہ دار", "Other agnatic relative"),
}

SINGLE = (
    "husband", "father", "mother", "paternal_grandfather",
    "paternal_grandmother", "maternal_grandmother", "other_agnate",
)
SPOUSES = ("husband", "wives")

DISCLAIMER = (
    "یہ حساب حنفی فقہ کے بنیادی اصولوں پر مبنی ایک رہنما حساب ہے۔ "
    "حتمی تقسیم سے پہلے کسی مستند مفتی/عالم سے تصدیق ضرور کروائیں۔"
)
UNSUPPORTED = (
    "شامل نہیں: ذوی الارحام، پردادا/پردادی، مفقود، حمل، مذہب کا فرق، "
    "قتل، اور دیگر خاص صورتیں۔"
)


class InheritanceError(ValueError):
    """Raised for invalid input."""


def _count(heirs: dict[str, Any], key: str) -> int:
    v = heirs.get(key, 0) or 0
    if isinstance(v, bool):
        return int(v)
    try:
        n = int(v)
    except (TypeError, ValueError):
        raise InheritanceError(f"'{key}' کی قدر درست نہیں: {v!r}")
    if n < 0:
        raise InheritanceError(f"'{key}' منفی نہیں ہو سکتا")
    return n


def fr(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def calculate(
    heirs: dict[str, Any],
    estate: float = 0,
    funeral_expenses: float = 0,
    debts: float = 0,
    bequest: float = 0,
) -> dict[str, Any]:
    c = {k: _count(heirs, k) for k in LABELS}

    for k in SINGLE:
        if c[k] > 1:
            raise InheritanceError(f"'{k}' صرف 0 یا 1 ہو سکتا ہے")
    if c["husband"] and c["wives"]:
        raise InheritanceError("شوہر اور بیوی دونوں ایک ساتھ وارث نہیں ہو سکتے")
    if c["wives"] > 4:
        raise InheritanceError("بیویاں زیادہ سے زیادہ 4 ہو سکتی ہیں")
    if sum(c.values()) == 0:
        raise InheritanceError("کوئی وارث نہیں دیا گیا")

    notes: list[str] = []
    blocked: dict[str, str] = {}
    fixed: dict[str, F] = {}
    asaba: list[tuple[str, list[tuple[str, int]]]] = []  # (group, [(heir, unit)])

    sons, dau = c["sons"], c["daughters"]
    gs, gd = c["grandsons"], c["granddaughters"]
    father, mother = c["father"], c["mother"]
    pgf = c["paternal_grandfather"]
    pgm, mgm = c["paternal_grandmother"], c["maternal_grandmother"]
    fb, fs = c["full_brothers"], c["full_sisters"]
    cb, cs = c["consanguine_brothers"], c["consanguine_sisters"]
    ub, us = c["uterine_brothers"], c["uterine_sisters"]

    # ---- Hajb (exclusion) of grandchildren and ancestors ----
    if sons and (gs or gd):
        blocked["grandsons"] = blocked["granddaughters"] = "بیٹے کی موجودگی میں پوتے/پوتیاں محروم"
        gs = gd = 0
    has_desc = (sons + dau + gs + gd) > 0
    male_desc = sons > 0 or gs > 0

    if father and pgf:
        blocked["paternal_grandfather"] = "والد کی موجودگی میں دادا محروم"
        pgf = 0
    anc = "father" if father else ("paternal_grandfather" if pgf else None)

    sibs_total = fb + fs + cb + cs + ub + us  # blocked siblings still reduce mother's share

    # ---- Spouse ----
    spouse_share = F(0)
    if c["husband"]:
        spouse_share = F(1, 4) if has_desc else F(1, 2)
        fixed["husband"] = spouse_share
    if c["wives"]:
        spouse_share = F(1, 8) if has_desc else F(1, 4)
        fixed["wives"] = spouse_share

    # ---- Mother ----
    if mother:
        if has_desc or sibs_total >= 2:
            fixed["mother"] = F(1, 6)
            if has_desc:
                notes.append("والدہ کو اولاد کی موجودگی میں 1/6 ملا")
            else:
                notes.append("والدہ کو دو یا زیادہ بہن بھائیوں کی موجودگی میں 1/6 ملا")
        elif father and spouse_share:
            fixed["mother"] = (1 - spouse_share) / 3
            notes.append("عمریہ مسئلہ: زوج/زوجہ کے بعد باقی کا 1/3 والدہ کو ملا")
        else:
            fixed["mother"] = F(1, 3)

    # ---- Father / paternal grandfather ----
    anc_residuary = False
    if anc:
        if male_desc:
            fixed[anc] = F(1, 6)
        elif has_desc:
            fixed[anc] = F(1, 6)
            anc_residuary = True
            notes.append("صرف بیٹی/پوتی کی موجودگی میں باپ/دادا کو 1/6 اور باقی بھی ملے گا")
        else:
            anc_residuary = True

    # ---- Grandmothers ----
    gm_eligible: list[str] = []
    if pgm:
        if mother:
            blocked["paternal_grandmother"] = "والدہ کی موجودگی میں دادی محروم"
        elif father:
            blocked["paternal_grandmother"] = "والد کی موجودگی میں دادی محروم"
        else:
            gm_eligible.append("paternal_grandmother")
    if mgm:
        if mother:
            blocked["maternal_grandmother"] = "والدہ کی موجودگی میں نانی محروم"
        else:
            gm_eligible.append("maternal_grandmother")
    for k in gm_eligible:
        fixed[k] = F(1, 6) / len(gm_eligible)

    # ---- Children ----
    if sons:
        asaba.append(("children", [("sons", 2), ("daughters", 1)] if dau else [("sons", 2)]))
    elif dau:
        fixed["daughters"] = F(1, 2) if dau == 1 else F(2, 3)

    # ---- Son's children ----
    if not sons:
        if gs:
            asaba.append(("grandchildren", [("grandsons", 2), ("granddaughters", 1)] if gd else [("grandsons", 2)]))
        elif gd:
            if dau == 0:
                fixed["granddaughters"] = F(1, 2) if gd == 1 else F(2, 3)
            elif dau == 1:
                fixed["granddaughters"] = F(1, 6)
            else:
                blocked["granddaughters"] = "دو یا زیادہ بیٹیاں 2/3 لے چکی ہیں، پوتیاں محروم"

    # ---- Siblings ----
    sib_ok = not father and not pgf and not male_desc
    if not sib_ok:
        why = (
            "والد کی موجودگی میں بہن بھائی محروم" if father
            else "دادا کی موجودگی میں بہن بھائی محروم (امام ابوحنیفہ کا قول)" if pgf
            else "بیٹے/پوتے کی موجودگی میں بہن بھائی محروم"
        )
        for k in ("full_brothers", "full_sisters", "consanguine_brothers", "consanguine_sisters"):
            blocked[k] = why
    female_desc = dau > 0 or gd > 0
    if sib_ok:
        full_asaba_with_female_desc = fs > 0 and fb == 0 and female_desc
        if fb:
            asaba.append(("full_siblings", [("full_brothers", 2), ("full_sisters", 1)] if fs else [("full_brothers", 2)]))
        elif full_asaba_with_female_desc:
            asaba.append(("full_siblings", [("full_sisters", 1)]))
            notes.append("حقیقی بہن بیٹی/پوتی کے ساتھ عصبہ بن گئی")
        elif fs:
            fixed["full_sisters"] = F(1, 2) if fs == 1 else F(2, 3)

        if fb:
            for k in ("consanguine_brothers", "consanguine_sisters"):
                blocked[k] = "حقیقی بھائی کی موجودگی میں علاتی محروم"
        elif full_asaba_with_female_desc:
            for k in ("consanguine_brothers", "consanguine_sisters"):
                blocked[k] = "حقیقی بہن (عصبہ) کی موجودگی میں علاتی محروم"
        elif fs >= 2 and cb == 0:
            blocked["consanguine_sisters"] = "دو یا زیادہ حقیقی بہنیں 2/3 لے چکی ہیں، علاتی بہنیں محروم"
        else:
            if cb:
                asaba.append(("consanguine_siblings", [("consanguine_brothers", 2), ("consanguine_sisters", 1)] if cs else [("consanguine_brothers", 2)]))
            elif cs and female_desc and fs == 0:
                asaba.append(("consanguine_siblings", [("consanguine_sisters", 1)]))
                notes.append("علاتی بہن بیٹی/پوتی کے ساتھ عصبہ بن گئی")
            elif cs:
                if fs == 0:
                    fixed["consanguine_sisters"] = F(1, 2) if cs == 1 else F(2, 3)
                else:  # exactly one full sister
                    fixed["consanguine_sisters"] = F(1, 6)

    # ---- Uterine siblings ----
    if ub + us:
        if has_desc or father or pgf:
            why = (
                "اولاد کی موجودگی میں اخیافی بہن بھائی محروم" if has_desc
                else "والد/دادا کی موجودگی میں اخیافی بہن بھائی محروم"
            )
            blocked["uterine_brothers"] = blocked["uterine_sisters"] = why
        else:
            total = F(1, 6) if ub + us == 1 else F(1, 3)
            # equal split between male and female uterine siblings
            for k, n in (("uterine_brothers", ub), ("uterine_sisters", us)):
                if n:
                    fixed[k] = total * n / (ub + us)

    # ---- Residuary tail ----
    if anc and anc_residuary:
        asaba.insert(_anc_pos(asaba), ("ancestor", [(anc, 1)]))
    if c["other_agnate"]:
        asaba.append(("other", [("other_agnate", 1)]))

    # ---- Distribution ----
    shares: dict[str, F] = dict(fixed)
    fixed_sum = sum(fixed.values(), F(0))
    awl = radd = False
    unresolved: F | None = None
    zero_reason: dict[str, str] = {}

    if fixed_sum > 1:
        awl = True
        shares = {k: v / fixed_sum for k, v in fixed.items()}
        notes.append(f"عول: حصوں کا مجموعہ {fr(fixed_sum)} تھا، اس لیے سب حصے اسی تناسب سے کم کیے گئے")
        for _, members in asaba:
            for k, _u in members:
                zero_reason[k] = "عول کی وجہ سے عصبہ کے لیے کچھ نہیں بچا"
    else:
        remainder = 1 - fixed_sum
        if asaba:
            group, members = asaba[0]
            units = sum(c[k] * u for k, u in members)
            for k, u in members:
                shares[k] = shares.get(k, F(0)) + remainder * c[k] * u / units
            if remainder == 0:
                for k, _u in members:
                    zero_reason.setdefault(k, "مقررہ حصوں کے بعد کچھ نہیں بچا")
            for g, mem in asaba[1:]:
                for k, _u in mem:
                    blocked.setdefault(k, "قریبی عصبہ کی موجودگی میں محروم")
        elif remainder > 0:
            non_spouse = {k: v for k, v in fixed.items() if k not in SPOUSES}
            if non_spouse:
                radd = True
                s = sum(non_spouse.values(), F(0))
                factor = (1 - (fixed_sum - s)) / s
                for k, v in non_spouse.items():
                    shares[k] = v * factor
                notes.append("ردّ: بچا ہوا حصہ زوجین کے علاوہ حصے داروں میں ان کے حصوں کے تناسب سے لوٹا دیا گیا")
            else:
                unresolved = remainder
                notes.append(
                    f"باقی {fr(remainder)} حصہ تقسیم نہیں ہو سکا (کوئی عصبہ یا ردّ کا حق دار نہیں)۔ "
                    "یہ ذوی الارحام/بیت المال کا مسئلہ ہے، مفتی سے رجوع کریں"
                )

    # ---- Money ----
    gross = F(str(estate or 0))
    net = gross - F(str(funeral_expenses or 0)) - F(str(debts or 0))
    if net < 0:
        net = F(0)
        notes.append("تجہیز و تکفین اور قرض ترکہ سے زیادہ ہیں، وارثوں کے لیے کچھ نہیں بچتا")
    bq = F(str(bequest or 0))
    cap = net / 3
    if bq > cap:
        notes.append("وصیت ایک تہائی سے زیادہ تھی؛ صرف ایک تہائی تک نافذ کی گئی (زیادہ کے لیے سب وارثوں کی رضامندی چاہیے)")
        bq = cap
    distributable = net - bq

    # ---- Output ----
    denominators = [v.denominator for v in shares.values() if v != 0] or [1]
    total_parts = lcm(*denominators)
    out: list[dict[str, Any]] = []
    for key, (ur, en) in LABELS.items():
        n = c[key]
        if n == 0:
            continue
        share = shares.get(key, F(0))
        if key in blocked:
            status, reason = "محروم", blocked[key]
        elif share == 0:
            status, reason = "کچھ نہیں", zero_reason.get(key, "کوئی حصہ نہیں بنتا")
        else:
            status, reason = "وارث", ""
        amount = share * distributable
        out.append({
            "heir": key,
            "label_ur": ur,
            "label_en": en,
            "count": n,
            "status": status,
            "reason": reason,
            "share_fraction": fr(share),
            "share_percent": round(float(share * 100), 4),
            "share_parts": f"{int(share * total_parts)} / {total_parts}",
            "amount": round(float(amount), 2),
            "amount_per_head": round(float(amount / n), 2),
        })

    return {
        "madhab": "Hanafi (حنفی)",
        "estate": {
            "gross": round(float(gross), 2),
            "net_after_funeral_and_debts": round(float(net), 2),
            "bequest_applied": round(float(bq), 2),
            "distributable": round(float(distributable), 2),
        },
        "total_parts": total_parts,
        "awl": awl,
        "radd": radd,
        "unresolved_remainder": fr(unresolved) if unresolved else None,
        "heirs": out,
        "notes": notes,
        "disclaimer": DISCLAIMER,
        "not_covered": UNSUPPORTED,
    }


def _anc_pos(asaba: list) -> int:
    """Father/grandfather outrank siblings and other agnates but not descendants."""
    pos = 0
    for i, (g, _) in enumerate(asaba):
        if g in ("children", "grandchildren"):
            pos = i + 1
    return pos
