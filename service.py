"""Bridge between the faraid engine and the MCP server.

The engine (faraid/) does all the Hanafi share calculation with exact integers.
This file only (1) prepares input, (2) adds the rupee distribution after debts,
funeral costs and the one-third bequest limit, and (3) returns plain JSON.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

from faraid.engine import FaraidError, solve_block, solve_case
from faraid.parser import parse_text
from faraid.relations import INFO, ORDER
from faraid.render_xlsx import build_xlsx
from files import new_bundle
from naqsha import sheet_to_html

DISCLAIMER = (
    "یہ حساب حنفی فقہ (کتاب الفرائض آسان سراجی کے مطابق) کا رہنما حساب ہے، فتویٰ نہیں۔ "
    "حتمی تقسیم سے پہلے کسی مستند مفتی سے تصدیق کروائیں۔"
)
NOT_COVERED = (
    "شامل نہیں: ذوی الارحام، حمل، مفقود، خنثیٰ، مولیٰ، موانعِ ارث (قتل، غلامی، اختلافِ دین)، "
    "دادا کے ساتھ بھائی بہن میں صاحبینؒ کا مقاسمہ، پڑپوتے۔"
)


def _fr(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def _money(estate: float, funeral: float, debts: float, bequest: float) -> tuple[dict, F, list[str]]:
    notes: list[str] = []
    gross = F(str(estate or 0))
    net = gross - F(str(funeral or 0)) - F(str(debts or 0))
    if net < 0:
        net = F(0)
        notes.append("تجہیز و تکفین اور قرض ترکہ سے زیادہ ہیں، وارثوں کے لیے کچھ نہیں بچتا۔")
    bq = F(str(bequest or 0))
    cap = net / 3
    if bq > cap:
        notes.append("وصیت ایک تہائی سے زیادہ تھی؛ صرف ایک تہائی تک نافذ کی گئی "
                     "(زیادہ کے لیے سب عاقل بالغ وارثوں کی رضامندی چاہیے)۔")
        bq = cap
    distributable = net - bq
    info = {
        "gross": round(float(gross), 2),
        "net_after_funeral_and_debts": round(float(net), 2),
        "bequest_applied": round(float(bq), 2),
        "distributable": round(float(distributable), 2),
    }
    return info, distributable, notes


def _clean(x: Any) -> Any:
    """Make engine output JSON-safe (Fractions -> strings)."""
    if isinstance(x, F):
        return _fr(x)
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    return x


def _block_summary(r: dict, names: dict[str, str]) -> dict:
    return {
        "asl_masala": r["asl"],
        "tashih": r["T"],
        "mudrub": r["mudrub"],
        "awl": bool(r["awl"]),
        "radd": _clean(r["radd"]) if r["radd"] else None,
        "umariyya": bool(r["umariyya"]),
        "shares": {names.get(pid, pid): s for pid, s in r["shares"].items()},
        "blocked": {names.get(pid, pid): why for pid, why in r["blocked"].items()},
        "notes": list(r["notes"]),
    }



# ------------------------------------------------------------ files (naqsha)
def _pdf_from_xlsx(xlsx: Path) -> Path | None:
    """PDF through LibreOffice, only where it is installed (not on plain Render Python)."""
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return None
    profile = tempfile.mkdtemp(prefix="lo_profile_")
    try:
        subprocess.run(
            [exe, f"-env:UserInstallation=file://{profile}", "--headless", "--convert-to", "pdf",
             "--outdir", str(xlsx.parent), str(xlsx)],
            capture_output=True, timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = xlsx.with_suffix(".pdf")
    return pdf if pdf.exists() else None


def make_files(case: dict, res: dict, lang: str, distributable: F | None) -> dict:
    """Excel + printable naqsha page (+ PDF when LibreOffice exists). Returns download links."""
    amounts = None
    if distributable and distributable > 0:
        J = res["J"]
        amounts = {
            "per": {pid: float(F(parts, J) * distributable) for pid, parts in res["final"].items()},
            "distributable": float(distributable),
        }
    folder, url = new_bundle()
    xlsx = folder / "faraid_naqsha.xlsx"
    build_xlsx(case, res, str(xlsx), lang, amounts)
    page = folder / "faraid_naqsha.html"
    page.write_text(sheet_to_html(str(xlsx), case.get("title", "")), encoding="utf-8")
    out: dict[str, Any] = {
        "excel_url": url(xlsx.name),
        "naqsha_page_url": url(page.name),
        "valid_for": "24 گھنٹے",
    }
    pdf = _pdf_from_xlsx(xlsx)
    if pdf:
        out["pdf_url"] = url(pdf.name)
    else:
        out["pdf_note"] = ("PDF کے لیے naqsha_page_url کھولیں اور اوپر «PDF محفوظ کریں» دبا کر "
                           "«Save as PDF» چنیں۔")
    return out

# ---------------------------------------------------------------- one death
SIMPLE_RELS = [r for r in ORDER]


def solve_simple(counts: dict[str, int], deceased: str = "", estate: float = 0,
                 funeral_expenses: float = 0, debts: float = 0, bequest: float = 0,
                 *, names: dict[str, list[str]] | None = None, deceased_name: str = "",
                 naqsha: bool = False, lang: str = "ur", title: str = "") -> dict:
    """One deceased person, heirs given as counts per relation code."""
    names = names or {}
    heirs: list[dict] = []
    for rel in SIMPLE_RELS:
        n = int(counts.get(rel, 0) or 0)
        if n < 0:
            raise FaraidError(f"'{rel}' منفی نہیں ہو سکتا۔")
        given = [str(x).strip() for x in (names.get(rel) or []) if str(x).strip()]
        for i in range(n):
            pid = f"{rel}:{i + 1}"
            nm = given[i] if i < len(given) else INFO[rel]["ur"] + (f" {i + 1}" if n > 1 else "")
            heirs.append({"id": pid, "name": nm, "rel": rel})
    if not heirs:
        raise FaraidError("کوئی وارث درج نہیں۔")
    if counts.get("husband") and counts.get("wife"):
        raise FaraidError("شوہر اور بیوی دونوں ایک ساتھ نہیں ہو سکتے۔")
    gender = {"male": "M", "m": "M", "مرد": "M", "female": "F", "f": "F", "عورت": "F"}.get(
        (deceased or "").strip().lower())
    if counts.get("husband"):
        gender = "F"
    elif counts.get("wife"):
        gender = "M"
    if gender is None:
        gender = "M"  # without a spouse the deceased's sex does not change any share

    r = solve_block(heirs, gender)
    T = r["T"]
    money, distributable, mnotes = _money(estate, funeral_expenses, debts, bequest)

    by_rel: dict[str, dict] = {}
    for h in heirs:
        e = by_rel.setdefault(h["rel"], {"count": 0, "parts": 0, "reason": ""})
        e["count"] += 1
        e["parts"] += r["shares"].get(h["id"], 0)
        if h["id"] in r["blocked"]:
            e["reason"] = r["blocked"][h["id"]]
    out_heirs = []
    for rel, e in by_rel.items():
        share = F(e["parts"], T)
        amount = share * distributable
        status = "وارث" if e["parts"] else ("محروم" if e["reason"] else "کچھ نہیں")
        out_heirs.append({
            "heir": rel, "label_ur": INFO[rel]["ur"], "count": e["count"], "status": status,
            "reason": e["reason"], "parts": e["parts"], "of_parts": T,
            "share_fraction": _fr(share), "share_percent": round(float(share * 100), 4),
            "amount": round(float(amount), 2), "amount_per_head": round(float(amount / e["count"]), 2),
        })
    id_names = {h["id"]: h["name"] for h in heirs}
    out = {
        "madhab": "Hanafi (حنفی)",
        "result": _block_summary(r, id_names),
        "estate": money,
        "heirs": out_heirs,
        "notes": list(r["notes"]) + mnotes,
        "disclaimer": DISCLAIMER,
        "not_covered": NOT_COVERED,
    }
    if naqsha:
        lang = "gu" if (lang or "").lower().startswith("gu") else "ur"
        case = {
            "title": title or "نقشۂ تقسیمِ سہام (علمُ الفرائض)", "lang": lang, "notes": [], "footer": [],
            "blocks": [{
                "deceased": {"id": "mayyit", "name": deceased_name or ("مرحومہ" if gender == "F" else "مرحوم"),
                             "wafat": "", "gender": gender},
                "heirs": heirs, "note": "",
            }],
        }
        out["files"] = make_files(case, solve_case(case), lang, distributable if estate else None)
    return out


# ------------------------------------------------------------ munasakha
def solve_munasakha(text: str, estate: float = 0, funeral_expenses: float = 0,
                    debts: float = 0, bequest: float = 0, *, make_naqsha: bool = True,
                    lang: str | None = None) -> dict:
    """Several deaths in a row, in the engine's text format (see cases/*.txt)."""
    case = parse_text(text)
    if lang:
        case["lang"] = "gu" if lang.lower().startswith("gu") else "ur"
    res = solve_case(case)
    J = res["J"]
    money, distributable, mnotes = _money(estate, funeral_expenses, debts, bequest)

    names = {pid: p["name"] for pid, p in res["people"].items()}
    names.update({b["deceased"]["id"]: b["deceased"]["name"] for b in case["blocks"]})
    people = []
    for pid, parts in res["final"].items():
        p = res["people"][pid]
        share = F(parts, J)
        people.append({
            "name": p["name"], "relation_ur": INFO[p["rel"]]["ur"], "heir_of": p["of"],
            "parts": parts, "of_jamia": J,
            "share_fraction": _fr(share), "share_percent": round(float(share * 100), 4),
            "amount": round(float(share * distributable), 2),
        })
    blocks = []
    for bi, r in enumerate(res["blocks"]):
        b = _block_summary(r, names)
        b["deceased"] = case["blocks"][bi]["deceased"]["name"]
        b["ma_fil_yad"] = r.get("m")
        b["ratio"] = r["ratio"]["name"] if r.get("ratio") else None
        blocks.append(b)
    out = {
        "madhab": "Hanafi (حنفی)",
        "jamia": J,
        "people": people,
        "blocks": blocks,
        "verification": [{"check": a, "ok": bool(ok), "detail": d} for a, ok, d in res["verification"]],
        "estate": money,
        "notes": mnotes,
        "disclaimer": DISCLAIMER,
        "not_covered": NOT_COVERED,
    }
    if make_naqsha:
        out["files"] = make_files(case, res, case.get("lang", "ur"), distributable if estate else None)
    return out
