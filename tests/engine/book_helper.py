# -*- coding: utf-8 -*-
"""کتاب کی مثالوں کے لیے مددگار: {رشتہ: تعداد} سے ایک بلاک حل کر کے رشتے کے لحاظ سے مجموعی سہام لوٹاتا ہے۔"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from faraid.engine import solve_block, FaraidError
from faraid.relations import rel_gender


def block(heirs, dec_gender):
    hs = []
    for rel, n in heirs.items():
        for i in range(n):
            hs.append({"id": f"{rel}{i+1}", "name": f"{rel}{i+1}", "rel": rel})
    r = solve_block(hs, dec_gender)
    by = {}
    for pid, s in r["shares"].items():
        rel = next(h["rel"] for h in hs if h["id"] == pid)
        by[rel] = by.get(rel, 0) + s
    return r, by


def check(name, heirs, dec_gender, asl=None, total=None, shares=None):
    """asl: اصل مسئلہ (عول/رد سے پہلے کا مخرج نہیں، انجن کا asl)؛ total: تصحیح T؛ shares: {رشتہ: مجموعی سہام}"""
    try:
        r, by = block(heirs, dec_gender)
    except FaraidError as e:
        return (name, False, f"خطا: {e}")
    ok, msg = True, []
    if asl is not None and r["asl"] != asl:
        ok = False; msg.append(f"asl={r['asl']} (کتاب {asl})")
    if total is not None and r["T"] != total:
        ok = False; msg.append(f"T={r['T']} (کتاب {total})")
    if shares:
        for k, v in shares.items():
            if by.get(k, 0) != v:
                ok = False; msg.append(f"{k}: {by.get(k,0)} (کتاب {v})")
    return (name, ok, "; ".join(msg) or f"asl={r['asl']} T={r['T']} {by}")
