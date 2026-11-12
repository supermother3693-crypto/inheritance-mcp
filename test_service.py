"""Run with:  python test_service.py   (checks the server layer; engine tests: tests/engine/)"""
import os
from fractions import Fraction as F

from service import solve_munasakha, solve_simple
from faraid.engine import FaraidError


def fr(h):
    n, _, d = h["share_fraction"].partition("/")
    return F(int(n), int(d or 1))


def simple(counts, **kw):
    r = solve_simple(counts, **kw)
    return {h["heir"]: fr(h) for h in r["heirs"]}, r


def check(name, counts, expected, **kw):
    got, r = simple(counts, **kw)
    exp = {k: F(v) for k, v in expected.items()}
    assert got == exp, f"{name}: expected {exp}, got {got}"
    assert sum(got.values()) == 1, f"{name}: total != 1"
    print("OK ", name)
    return r


check("husband + son", {"husband": 1, "son": 1}, {"husband": "1/4", "son": "3/4"})
check("Umariyyatayn", {"wife": 1, "father": 1, "mother": 1}, {"wife": "1/4", "mother": "1/4", "father": "1/2"})
check("daughter + father + mother", {"daughter": 1, "father": 1, "mother": 1},
      {"daughter": "1/2", "mother": "1/6", "father": "1/3"})
check("awl", {"husband": 1, "full_sister": 2, "mother": 1}, {"husband": "3/8", "full_sister": "1/2", "mother": "1/8"})
check("Minbariyya", {"wife": 1, "daughter": 2, "father": 1, "mother": 1},
      {"wife": "1/9", "daughter": "16/27", "father": "4/27", "mother": "4/27"})
check("radd", {"daughter": 1, "mother": 1}, {"daughter": "3/4", "mother": "1/4"})
check("grandfather blocks siblings", {"grandfather": 1, "full_brother": 1}, {"grandfather": "1", "full_brother": "0"})
check("Himariyya (Hanafi)", {"husband": 1, "mother": 1, "ut_brother": 2, "full_brother": 2},
      {"husband": "1/2", "mother": "1/6", "ut_brother": "1/3", "full_brother": "0"})

# Money: debts, funeral, bequest capped at one third
r = solve_simple({"husband": 1, "son": 1}, estate=1_000_000, funeral_expenses=20_000, debts=80_000, bequest=500_000)
assert r["estate"] == {"gross": 1000000.0, "net_after_funeral_and_debts": 900000.0,
                       "bequest_applied": 300000.0, "distributable": 600000.0}
assert {h["heir"]: h["amount"] for h in r["heirs"]} == {"husband": 150000.0, "son": 450000.0}
print("OK  money")

# Munasakha from the engine's own sample file
text = open(os.path.join(os.path.dirname(__file__), "cases", "ghaffar_80.txt"), encoding="utf-8").read()
m = solve_munasakha(text, estate=800)
assert m["jamia"] == 80 and all(v["ok"] for v in m["verification"])
assert sum(p["parts"] for p in m["people"]) == 80
assert round(sum(p["amount"] for p in m["people"]), 2) == 800.0
print("OK  munasakha (ghaffar_80, jamia 80)")

# Bad input -> clear error
for bad in ({}, {"husband": 1, "wife": 1}, {"wife": 5, "mother": 1}):
    try:
        solve_simple(bad, deceased="male")
    except FaraidError:
        continue
    raise AssertionError(f"should reject {bad}")
print("OK  invalid input rejected\n\nAll service tests passed.")
