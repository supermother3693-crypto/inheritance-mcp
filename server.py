"""MCP server for the Faraid (Hanafi inheritance) engine.

Tools:
  calculate_inheritance  - one deceased person, heirs as counts (optional naqsha files)
  calculate_munasakha    - several deaths in a row, engine text format (naqsha files by default)
Downloads:
  /files/<token>/<name>  - Excel, printable naqsha page, PDF (temporary, private link)
"""
import os

import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import FileResponse, PlainTextResponse

from faraid.engine import FaraidError
from files import MEDIA, find
from service import solve_munasakha, solve_simple

mcp = MCPServer("inheritance-hanafi")

# Pure calculators: nothing of the user's is changed anywhere. Clients such as ChatGPT use
# these hints to treat the tools as read-only (no confirmation / allowed on read-only plans).
CALC = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)

# tool parameter name -> engine relation code
REL = {
    "husband": "husband", "wife": "wife", "father": "father", "mother": "mother",
    "grandfather": "grandfather", "grandmother_paternal": "grandmother_p",
    "grandmother_maternal": "grandmother_m", "son": "son", "daughter": "daughter",
    "grandson": "grandson", "granddaughter": "granddaughter",
    "full_brother": "full_brother", "full_sister": "full_sister",
    "consanguine_brother": "cons_brother", "consanguine_sister": "cons_sister",
    "uterine_brother": "ut_brother", "uterine_sister": "ut_sister",
    "full_nephew": "full_nephew", "consanguine_nephew": "cons_nephew",
    "full_uncle": "full_uncle", "consanguine_uncle": "cons_uncle",
    "full_cousin": "full_cousin", "consanguine_cousin": "cons_cousin",
}


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


@mcp.custom_route("/files/{token}/{name}", methods=["GET"])
async def download(request: Request):
    path = find(request.path_params["token"], request.path_params["name"])
    if path is None:
        return PlainTextResponse("فائل نہیں ملی یا لنک کی مدت (24 گھنٹے) ختم ہو گئی۔", status_code=404)
    headers = {"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex", "Referrer-Policy": "no-referrer"}
    if path.suffix.lower() != ".html":
        headers["Content-Disposition"] = f'attachment; filename="{path.name}"'
    return FileResponse(path, media_type=MEDIA.get(path.suffix.lower(), "application/octet-stream"), headers=headers)


@mcp.tool(annotations=CALC)
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
    create_naqsha: bool = False,
    language: str = "ur",
    title: str = "",
    deceased_name: str = "",
    names: dict[str, list[str]] | None = None,
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
    parts (sihaam) and amount, plus awl/radd/exclusion notes.

    create_naqsha = True also makes the traditional naqsha as an Excel file and a
    printable page (with a "Save as PDF" button); the result then has a `files`
    object with download links: show these links to the user. language = "ur" or
    "gu" (Gujarati). title, deceased_name and names (e.g. {"son": ["Zaid", "Umar"]},
    keys are the relation parameter names above) only decorate the naqsha.
    Not a fatwa: confirm with a qualified mufti.
    """
    args = locals()
    counts = {REL[k]: args[k] for k in REL}
    rel_names = {REL[k]: v for k, v in (names or {}).items() if k in REL}
    try:
        return solve_simple(
            counts, deceased, estate, funeral_expenses, debts, bequest,
            names=rel_names, deceased_name=deceased_name, naqsha=create_naqsha,
            lang=language, title=title,
        )
    except FaraidError as e:
        return {"error": str(e)}


@mcp.tool(annotations=CALC)
def calculate_munasakha(
    case_text: str,
    estate: float = 0,
    funeral_expenses: float = 0,
    debts: float = 0,
    bequest: float = 0,
    create_naqsha: bool = True,
    language: str = "",
) -> dict:
    """Inheritance with several deaths in a row (munasakha), Hanafi fiqh.

    case_text uses the engine's simple text format, one block per death:

        عنوان: نقشۂ مناسخہ          (optional title)
        زبان: ur                    (optional: ur or gu)

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
    person's final parts, fraction and amount, and a verification list.

    By default (create_naqsha = True) it also makes the traditional naqsha with
    ma fil yad, tashih, mazrub and the ladder of shares: an Excel file and a printable
    page with a "Save as PDF" button. The result has a `files` object with download
    links (valid 24 hours): show these links to the user. language = "ur" or "gu"
    overrides the case's language. Not a fatwa: confirm with a qualified mufti.
    """
    try:
        return solve_munasakha(
            case_text, estate, funeral_expenses, debts, bequest,
            make_naqsha=create_naqsha, lang=language or None,
        )
    except FaraidError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Streamable HTTP at /mcp; host 0.0.0.0 so Render can reach it from outside.
    app = mcp.streamable_http_app(host="0.0.0.0")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
