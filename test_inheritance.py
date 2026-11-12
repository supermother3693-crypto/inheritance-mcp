"""Run with:  python test_inheritance.py"""
from fractions import Fraction as F

from inheritance import InheritanceError, calculate


def shares(heirs, **kw):
    r = calculate(heirs, **kw)
    out = {}
    for h in r["heirs"]:
        n, d = (h["share_fraction"].split("/") + ["1"])[:2]
        out[h["heir"]] = F(int(n), int(d))
    return out, r


def check(name, heirs, expected, **kw):
    got, r = shares(heirs, **kw)
    exp = {k: F(v) for k, v in expected.items()}
    assert got == exp, f"{name}: expected {exp}, got {got}"
    assert sum(got.values()) == 1 or r["unresolved_remainder"], f"{name}: total != 1"
    print("OK ", name)
    return r


check("husband + son", {"husband": 1, "sons": 1}, {"husband": "1/4", "sons": "3/4"})
check("wife + father + mother (Umariyyatayn)", {"wives": 1, "father": 1, "mother": 1},
      {"wives": "1/4", "mother": "1/4", "father": "1/2"})
check("husband + father + mother", {"husband": 1, "father": 1, "mother": 1},
      {"husband": "1/2", "mother": "1/6", "father": "1/3"})
check("daughter + father + mother", {"daughters": 1, "father": 1, "mother": 1},
      {"daughters": "1/2", "mother": "1/6", "father": "1/3"})
check("two daughters + father + mother", {"daughters": 2, "father": 1, "mother": 1},
      {"daughters": "2/3", "mother": "1/6", "father": "1/6"})
check("son + daughter (2:1)", {"sons": 1, "daughters": 1}, {"sons": "2/3", "daughters": "1/3"})
check("awl: husband + 2 full sisters + mother", {"husband": 1, "full_sisters": 2, "mother": 1},
      {"husband": "3/8", "full_sisters": "1/2", "mother": "1/8"})
check("awl Minbariyya", {"wives": 1, "daughters": 2, "father": 1, "mother": 1},
      {"wives": "1/9", "daughters": "16/27", "father": "4/27", "mother": "4/27"})
check("radd: daughter + mother", {"daughters": 1, "mother": 1}, {"daughters": "3/4", "mother": "1/4"})
check("radd keeps spouse: wife + daughter", {"wives": 1, "daughters": 1},
      {"wives": "1/8", "daughters": "7/8"})
check("daughter + son's daughter (1/2 + 1/6, then radd)", {"daughters": 1, "granddaughters": 1},
      {"daughters": "3/4", "granddaughters": "1/4"})
check("two daughters block son's daughter", {"daughters": 2, "granddaughters": 1, "father": 1},
      {"daughters": "2/3", "granddaughters": "0", "father": "1/3"})
check("son blocks grandchildren", {"sons": 1, "grandsons": 2}, {"sons": "1", "grandsons": "0"})
check("father blocks siblings", {"father": 1, "full_brothers": 2}, {"father": "1", "full_brothers": "0"})
check("grandfather blocks siblings (Hanafi)", {"paternal_grandfather": 1, "full_brothers": 1},
      {"paternal_grandfather": "1", "full_brothers": "0"})
check("full sister + daughter -> sister asaba", {"daughters": 1, "full_sisters": 1},
      {"daughters": "1/2", "full_sisters": "1/2"})
check("uterine siblings share equally", {"mother": 1, "uterine_brothers": 1, "uterine_sisters": 1, "full_brothers": 1},
      {"mother": "1/6", "uterine_brothers": "1/6", "uterine_sisters": "1/6", "full_brothers": "1/2"})
check("full sister + consanguine sister (radd)", {"full_sisters": 1, "consanguine_sisters": 1},
          {"full_sisters": "3/4", "consanguine_sisters": "1/4"})
check("grandmothers share 1/6", {"paternal_grandmother": 1, "maternal_grandmother": 1, "sons": 1},
      {"paternal_grandmother": "1/12", "maternal_grandmother": "1/12", "sons": "5/6"})
check("mother blocks grandmothers", {"mother": 1, "paternal_grandmother": 1, "daughters": 1},
      {"mother": "1/4", "paternal_grandmother": "0", "daughters": "3/4"})
check("Himariyya (Hanafi): brothers get nothing",
      {"husband": 1, "mother": 1, "uterine_brothers": 2, "full_brothers": 2},
      {"husband": "1/2", "mother": "1/6", "uterine_brothers": "1/3", "full_brothers": "0"})

# Money
r = calculate({"husband": 1, "sons": 1}, estate=1_000_000, funeral_expenses=20_000, debts=80_000, bequest=500_000)
assert r["estate"]["net_after_funeral_and_debts"] == 900000
assert r["estate"]["bequest_applied"] == 300000           # capped at 1/3
assert r["estate"]["distributable"] == 600000
assert {h["heir"]: h["amount"] for h in r["heirs"]} == {"husband": 150000.0, "sons": 450000.0}
print("OK  money (debts, funeral, 1/3 bequest cap)")

# Invalid input
for bad in ({}, {"husband": 1, "wives": 1}, {"wives": 5}, {"father": 2}, {"sons": -1}):
    try:
        calculate(bad)
    except InheritanceError:
        continue
    raise AssertionError(f"should reject {bad}")
print("OK  invalid input rejected")

# Only a spouse -> remainder not auto-distributed
r = calculate({"husband": 1})
assert r["unresolved_remainder"] == "1/2"
print("OK  spouse-only remainder flagged")
print("\nAll tests passed.")
