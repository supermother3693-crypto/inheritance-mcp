# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from faraid.parser import load_case
from faraid.engine import solve_case

C = os.path.join(os.path.dirname(__file__), "..", "..", "cases")

def finals(res):
    return {res["people"][p]["name"] + ("" if True else ""): v for p, v in res["final"].items()}

def check(name, J, expect):
    res = solve_case(load_case(os.path.join(C, name)))
    got = {}
    for pid, v in res["final"].items():
        got.setdefault(pid, v)
    assert res["J"] == J, (name, res["J"], J)
    for k, v in expect.items():
        ids = [p for p in res["final"] if p.split("#")[0] == k.split("#")[0] and (("#" not in k) or p == k)]
        assert len(ids) == 1, (k, ids)
        assert res["final"][ids[0]] == v, (name, k, res["final"][ids[0]], v)
    assert sum(res["final"].values()) == J
    print("OK", name, "J =", J, "| people:", len(res["final"]))
    return res

check("rashida_book.txt", 128, {"خالدہ": 8, "حمیدہ": 8, "زید": 16, "محمد": 24, "احمد": 24, "فاطمہ": 12,
                                "زاہد": 18, "عبداللہ": 9, "عبدالرحمن": 9})
check("ghaffar_80.txt", 80, {"રૂકય્યા": 4, "અબ્દુલ હમીદ": 8, "ગુલામ રસૂલ": 8, "ઝહરા": 15, "સારા": 15, "અબ્દુલ વહ્હાબ": 30})
check("ishabhai_546.txt", 546, {"યાકુબ ઇસ્માઇલ મણી": 28, "સુલેમાન ઇસ્માઇલ મણી": 28, "યુસુફ મોહમદ ઇશા": 26,
                                "શીરીન ઇસ્માઇલ મણી": 14, "મોહંમદ ઇસ્માઇલ મણી": 28, "ઝુલેખા મુસા દાવજી": 13,
                                "અનવર મુસા દાવજી": 26})
check("dudha_72576.txt", 72576, {"હાશમ": 63, "હાજરા#મરિયમની": 252, "ફાતેમા": 6202, "મરિયમ#દીકરી": 2408,
                                "આયશા": 1806, "હવા#સારાની": 12096, "યુસુફ#સારાનો": 24192, "કાસીમ": 2016,
                                "હાજરા#અમીનાની": 4032, "હનીફા": 4032, "હવા#અમીનાની": 4032, "ઝૈનબ": 2408, "ઐયુબ": 2016})
check("paanch_batn_135.txt", 135, {"بکر": 54, "فاطمہ": 27, "عائشہ": 18, "زینب": 6, "ہدیٰ": 6,
                                   "عبداللہ": 8, "مریم": 4, "سعید": 8, "نائلہ": 4})
