"""MCP server for the Faraid (Hanafi inheritance) engine.

Tools:
  calculate_inheritance  - one deceased person, heirs as counts
  calculate_munasakha    - several deaths in a row, engine text format
"""
import os

import uvicorn
from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from faraid.engine import FaraidError
from service import solve_munasakha, solve_simple

mcp = MCPServer("inheritance-hanafi")


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


@mcp.tool()
def calculate_inheritance(
    deceased: str = "",
    husband: int = 0,
    wife: int = 0,
    father: int = 0,
    mother: int = 0,
    grandfather: int = 0,
    grandmother_paternal: int = 0,
    grandmother_maternal: int = 0,
    son: int = 0,
    daughter: int = 0,
    grandson: int = 0,
    granddaughter: int = 0,
    full_brother: int = 0,
    full_sister: int = 0,
    consanguine_brother: int = 0,
    consanguine_sister: int = 0,
    uterine_brother: int = 0,
    uterine_sister: int = 0,
    full_nephew: int = 0,
    consanguine_nephew: int = 0,
    full_uncle: int = 0,
    consanguine_uncle: int = 0,
    full_cousin: int = 0,
    consanguine_cousin: int = 0,
    estate: float = 0,
    funeral_expenses: float = 0,
    debts: float = 0,
    bequest: float = 0,
) -> dict:
    """Islamic inheritance (faraid) for ONE deceased person, Hanafi fiqh.

    Give only heirs who are alive at the time of death (counts; leave others 0).
    deceased = "male" or "female" (optional: it is worked out from husband/wife, and
    changes nothing when there is no spouse).
    Relations: grandfather/grandmothers are the father's father, father's mother
    (paternal) and mother's mother (maternal); grandson/granddaughter are children
    of a SON; consanguine = same father only; uterine = same mother only;
    nephew = brother's son, uncle = father's brother, cousin = uncle's son.
    Money is optional: estate, funeral_expenses, debts, bequest (wasiyyat, limited
    to one third of the net estate). Returns each heir's share as fraction, percent,
    parts (sihaam) and amount, plus awl/radd/exclusion notes. Not a fatwa: confirm
    with a qualified mufti.
    """
    counts = {
        "husband": husband, "wife": wife, "father": father, "mother": mother,
        "grandfather": grandfather, "grandmother_p": grandmother_paternal,
        "grandmother_m": grandmother_maternal, "son": son, "daughter": daughter,
        "grandson": grandson, "granddaughter": granddaughter,
        "full_brother": full_brother, "full_sister": full_sister,
        "cons_brother": consanguine_brother, "cons_sister": consanguine_sister,
        "ut_brother": uterine_brother, "ut_sister": uterine_sister,
        "full_nephew": full_nephew, "cons_nephew": consanguine_nephew,
        "full_uncle": full_uncle, "cons_uncle": consanguine_uncle,
        "full_cousin": full_cousin, "cons_cousin": consanguine_cousin,
    }
    try:
        return solve_simple(counts, deceased, estate, funeral_expenses, debts, bequest)
    except FaraidError as e:
        return {"error": str(e)}


@mcp.tool()
def calculate_munasakha(
    case_text: str,
    estate: float = 0,
    funeral_expenses: float = 0,
    debts: float = 0,
    bequest: float = 0,
) -> dict:
    """Inheritance with several deaths in a row (munasakha), Hanafi fiqh.

    case_text uses the engine's simple text format, one block per death:

        مورث: احمد | جنس: مرد
        بیوی: فاطمہ
        بیٹا: زید، عمر
        بیٹی: مریم

        مورث: زید
        بیوی: سارہ
        بیٹا: بکر

    Rules: each block starts with `مورث:` (or `مورثہ:` for a woman); the deceased of
    the 2nd block and later must be a heir named in an earlier block; two different
    people with the same name are written `نام#نشانی`. Relation words: بیوی، شوہر،
    باپ، ماں، دادا، دادی، نانی، بیٹا، بیٹی، پوتا، پوتی، بھائی، بہن، علاتی بھائی/بہن،
    اخیافی بھائی/بہن، بھتیجا، چچا، چچازاد. Returns the jamia (common total), every
    person's final parts, fraction and amount, and a verification list. Not a fatwa.
    """
    try:
        return solve_munasakha(case_text, estate, funeral_expenses, debts, bequest)
    except FaraidError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Streamable HTTP at /mcp; host 0.0.0.0 so Render can reach it from outside.
    app = mcp.streamable_http_app(host="0.0.0.0")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
