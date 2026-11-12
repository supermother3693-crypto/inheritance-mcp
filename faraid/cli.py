# -*- coding: utf-8 -*-
"""استعمال:  python -m faraid cases/dudha_72576.txt -o output/dudha.xlsx [--pdf]"""
import argparse, os, subprocess, sys
from .parser import load_case
from .engine import solve_case, FaraidError
from .render_xlsx import build_xlsx


def main(argv=None):
    ap = argparse.ArgumentParser(prog="faraid")
    ap.add_argument("case")
    ap.add_argument("-o", "--out")
    ap.add_argument("--lang", choices=["ur", "gu"])
    ap.add_argument("--pdf", action="store_true", help="LibreOffice ہو تو PDF بھی بنائیں")
    a = ap.parse_args(argv)
    try:
        case = load_case(a.case)
        res = solve_case(case)
    except FaraidError as e:
        print("✗", e)
        return 1
    out = a.out or os.path.splitext(a.case)[0] + ".xlsx"
    build_xlsx(case, res, out, a.lang)
    print(f"✓ جامعہ = {res['J']}  →  {out}")
    if a.pdf:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(out) or ".", out],
                       capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
