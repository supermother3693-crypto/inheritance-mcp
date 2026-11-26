# -*- coding: utf-8 -*-
"""مناسخہ کیس کی جانچ: کیا کوئی زندہ شخص کسی بطن کے ورثاء میں لکھنے سے رہ گیا؟

یہ انجن کا حساب نہیں بدلتا اور نقشے (PDF/Excel) میں کچھ نہیں چھاپتا۔
صرف AI کے لیے ایک یاددہانی بناتا ہے، تاکہ وہ ہر بطن بنانے سے پہلے پچھلے بطنوں کو دوبارہ دیکھے۔
"""
from .relations import INFO

_SPOUSE = {"wife", "husband"}
_CHILD = {"son", "daughter"}
_SIB = {"full_brother", "full_sister", "paternal_brother", "paternal_sister",
        "maternal_brother", "maternal_sister"}


def _rel_ur(code: str) -> str:
    try:
        return INFO[code]["ur"]
    except KeyError:
        return code


def _guess(x_rel: str, y_rel: str) -> str:
    """x = اس بطن کا مورث، y = پچھلے بطن کا وہ شخص جو اس بطن میں نہیں لکھا۔
    دونوں ایک ہی پچھلے مورث کے وارث تھے۔ y اب x کا کیا لگ سکتا ہے؟"""
    if x_rel in _CHILD and y_rel in _SPOUSE:
        return "ماں" if y_rel == "wife" else "باپ"
    if x_rel in _CHILD and y_rel in _CHILD:
        return "بھائی/بہن"
    if x_rel in _SIB and y_rel in _SIB:
        return "بھائی/بہن"
    return ""


def review_case(case: dict) -> dict:
    blocks = case["blocks"]
    died_at: dict[str, int] = {}      # id -> بطن (0-based) جس میں فوت ہوا
    seen: dict[str, dict] = {}        # id -> {name, batan, rel, of}
    reviews = []
    problems = []

    for bi, b in enumerate(blocks):
        d = b["deceased"]
        heirs_here = {h["id"] for h in b["heirs"]}
        # 1) جو شخص پہلے فوت ہو چکا وہ اس بطن میں وارث نہیں ہو سکتا
        for h in b["heirs"]:
            if h["id"] in died_at and died_at[h["id"]] < bi:
                problems.append({
                    "batan": bi + 1, "name": h["name"],
                    "message": f"بطن {bi + 1}: «{h['name']}» تو بطن {died_at[h['id']] + 1} میں فوت ہو چکا/چکی؛ "
                               "اسے اس بطن کے ورثاء سے ہٹائیں (وہ مردہ ہے)۔"})
        # 2) جو لوگ پچھلے بطنوں میں وارث تھے، اب تک فوت نہیں ہوئے اور یہاں نہیں لکھے
        cands = []
        if bi > 0:
            x = seen.get(d["id"], {})
            for pid, p in seen.items():
                if pid == d["id"] or pid in heirs_here or pid in died_at:
                    continue
                guess = _guess(x.get("rel", ""), p["rel"]) if x and p["of"] == x["of"] else ""
                cands.append({
                    "name": p["name"],
                    "was_heir_of": p["of"], "was_batan": p["batan"],
                    "was_relation": _rel_ur(p["rel"]),
                    "likely_now": guess,
                })
            cands.sort(key=lambda c: (c["likely_now"] == "", c["was_batan"]))
        if cands:
            likely = [c for c in cands if c["likely_now"]]
            others = [f'{c["name"]} (بطن {c["was_batan"]}: {c["was_heir_of"]} کا {c["was_relation"]})'
                      for c in cands if not c["likely_now"]]
            item = {"batan": bi + 1, "deceased": d["name"], "most_likely_missing": likely}
            if others:
                item["also_check_if_related"] = others
            reviews.append(item)
        died_at.setdefault(d["id"], bi)
        for h in b["heirs"]:
            seen.setdefault(h["id"], {"name": h["name"], "batan": bi + 1,
                                      "rel": h["rel"], "of": d["name"]})
    return {"reviews": reviews, "problems": problems}


def build_warning(case: dict) -> dict | None:
    """AI کے لیے انتباہ؛ نقشے میں شامل نہیں ہوتا۔ کچھ نہ ملے تو None۔"""
    rv = review_case(case)
    if not rv["reviews"] and not rv["problems"]:
        return None
    msg = (
        "RECHECK BEFORE FINALISING (for the AI only, not shown in the naqsha): for EACH batan from the 2nd on, "
        "look back at all earlier batans. Anyone listed there as an heir who has NOT yet died and is not written "
        "in this batan may be a living heir that was forgotten, e.g. the deceased's own mother (the wife of the "
        "earlier deceased), father, brother or sister. If such a person is alive, add them to this batan with the "
        "correct relation to THIS batan's deceased (a 'wife' above becomes 'mother' here; a son above becomes "
        "'brother' here; a daughter becomes 'sister') and call calculate_munasakha again: the shares and every "
        "ratio change. Ask the user if unsure whether the person is alive or even related. If they are truly not "
        "an heir here (already dead, or not a relative of this deceased), ignore the item."
    )
    msg_ur = (
        "ہر بطن (دوسرے سے آگے) بنانے سے پہلے پچھلے بطنوں کو دوبارہ دیکھیں: جو شخص وہاں وارث تھا، ابھی فوت نہیں ہوا "
        "اور اس بطن میں نہیں لکھا، کیا وہ زندہ ہے؟ زندہ ہو تو اسے اس بطن کے مورث کی نسبت سے لکھیں "
        "(اوپر «بیوی» تھی تو یہاں «ماں»، «بیٹا» تھا تو «بھائی»، «بیٹی» تھی تو «بہن») "
        "اور پھر calculate_munasakha دوبارہ چلائیں، کیونکہ سہام اور سب نسبتیں بدل جاتی ہیں۔ "
        "یقین نہ ہو تو صارف سے پوچھیں۔"
    )
    return {"recheck_required": True, "instruction": msg, "instruction_ur": msg_ur,
            "hard_errors": rv["problems"], "per_batan": rv["reviews"]}
