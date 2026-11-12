# -*- coding: utf-8 -*-
"""سادہ متنی فارمیٹ → case dict

مثال:

    عنوان: نقشۂ مناسخہ
    زبان: ur

    مورث: یوسف ابراہیم | وفات: 1998 | جنس: مرد
    بیوی: امینہ
    بہن: سارا#بین، مریم#بین
    چچازاد: اعظم، یوسف، اسماعیل

    مورث: یوسف                 ← پچھلے بطن کا وارث جو فوت ہوا
    بیوی: مریم#بیوی
    بہن: فاطمہ، سارا، خدیجہ
    بھائی: اعظم، اسماعیل

• ایک ہی نام کے دو مختلف افراد ہوں تو `نام#نشانی` لکھیں (نشانی نقشے میں نہیں چھپتی)۔
• ایک ہی شخص جہاں بھی آئے، وہاں وہی نام/نشانی لکھیں — انجن اسے ایک شخص سمجھ کر سہام جمع کرے گا۔
"""
import re
from .relations import rel_code, rel_gender, norm, ALIASES
from .engine import FaraidError

_SEP = re.compile(r"[،,؛;]+")
_KEYS = {
    "عنوان": "title", "title": "title",
    "زبان": "lang", "lang": "lang",
    "نوٹ": "note", "note": "note",
    "دستخط": "footer", "footer": "footer",
    "مورث": "dec_m", "مورثہ": "dec_f", "deceased": "dec_m",
}


def _split_names(s):
    return [x.strip() for x in _SEP.split(s) if x.strip()]


def _person(token):
    token = token.strip()
    name = token.split("#", 1)[0].strip()
    return {"id": token, "name": name}


def parse_text(text: str) -> dict:
    case = {"title": "", "lang": "ur", "notes": [], "footer": [], "blocks": []}
    cur = None
    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        if line.strip("-—= ") == "":
            continue
        if ":" not in line and "：" not in line:
            raise FaraidError(f"سطر {ln}: «:» نہیں ملا — {line}")
        key, val = re.split(r"[:：]", line, maxsplit=1)
        key = key.strip()
        k = _KEYS.get(norm(key)) or _KEYS.get(key)
        if k == "title":
            case["title"] = val.strip()
        elif k == "lang":
            case["lang"] = "gu" if val.strip().lower().startswith(("gu", "گج")) else "ur"
        elif k == "note":
            case["notes"].append(val.strip())
        elif k == "footer":
            case["footer"] = [x.strip() for x in val.split("|") if x.strip()]
        elif k in ("dec_m", "dec_f"):
            parts = [p.strip() for p in val.split("|")]
            who = _person(parts[0])
            dec = {"id": who["id"], "name": who["name"], "wafat": "", "gender": "F" if k == "dec_f" else None}
            for p in parts[1:]:
                if ":" in p:
                    a, _, b = p.partition(":")
                    a = a.strip()
                    if a in ("وفات", "وفات کی تاریخ", "wafat", "died"):
                        dec["wafat"] = b.strip()
                    elif a in ("جنس", "gender"):
                        dec["gender"] = "F" if b.strip() in ("عورت", "مؤنث", "F", "f", "female") else "M"
            cur = {"deceased": dec, "heirs": [], "note": ""}
            case["blocks"].append(cur)
        else:
            if cur is None:
                raise FaraidError(f"سطر {ln}: پہلے «مورث:» لکھیں۔")
            if norm(key) in ("نوٹ", "note"):
                cur["note"] = val.strip()
                continue
            try:
                rel = rel_code(key)
            except KeyError:
                raise FaraidError(f"سطر {ln}: نامعلوم رشتہ «{key}»۔ معاون رشتے: "
                                  + "، ".join(sorted({a for a in ALIASES if len(a) < 14 and not a.isascii()})[:40]))
            for nm in _split_names(val):
                p = _person(nm)
                cur["heirs"].append({"id": p["id"], "name": p["name"], "rel": rel})
    _resolve_deceased(case)
    return case


def _resolve_deceased(case):
    """دوسرے بطن سے آگے مورث کو پچھلے وارثوں میں سے ڈھونڈیں (آئی ڈی یا نام سے)۔"""
    known = {}   # id -> person
    for bi, b in enumerate(case["blocks"]):
        if bi > 0:
            d = b["deceased"]
            if d["id"] not in known:
                cands = [p for p in known.values() if p["name"] == d["name"]]
                if len(cands) == 1:
                    d["id"] = cands[0]["id"]
                elif len(cands) > 1:
                    raise FaraidError(f"بطن {bi + 1}: «{d['name']}» نام کے ایک سے زیادہ افراد ہیں — "
                                      "`نام#نشانی` لکھ کر واضح کریں: " + "، ".join(p["id"] for p in cands))
                else:
                    raise FaraidError(f"بطن {bi + 1}: مورث «{d['name']}» پچھلے بطون میں وارث کے طور پر نہیں ملا۔")
            else:
                d["name"] = known[d["id"]]["name"]
        for h in b["heirs"]:
            known.setdefault(h["id"], {"id": h["id"], "name": h["name"], "rel": h["rel"]})


def load_case(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return parse_text(f.read())
