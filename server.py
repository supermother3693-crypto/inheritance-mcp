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
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

from faraid.engine import FaraidError
from pathlib import Path

import calculator
import legal
from files import MEDIA, find
from service import solve_munasakha, solve_simple

INSTRUCTIONS = (
    "Hanafi faraid (Islamic inheritance) calculator. ONE death -> calculate_inheritance. "
    "Two or more deaths in a row (munasakha / 'teen batn'): a later deceased person is an heir of an "
    "earlier one and died before the estate was divided -> call calculate_munasakha ONCE with every "
    "block in a single case_text, so everything comes out in ONE naqsha with one jamia. Never call "
    "calculate_inheritance once per death for a chain. An heir who died BEFORE the first deceased is not "
    "an heir at all. If the order of deaths is unclear, ask the user which person died first. "
    "Always show the download links from `files` to the user."
)
mcp = MCPServer("inheritance-hanafi", instructions=INSTRUCTIONS)

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


@mcp.custom_route("/", methods=["GET"])
async def home(_: Request) -> HTMLResponse:
    return HTMLResponse(legal.home())


@mcp.custom_route("/.well-known/openai-apps-challenge", methods=["GET"])
async def openai_challenge(_: Request):
    """Domain verification for the ChatGPT app directory: token comes from env OPENAI_APPS_CHALLENGE."""
    token = os.environ.get("OPENAI_APPS_CHALLENGE", "").strip()
    if not token:
        return PlainTextResponse("not set", status_code=404)
    return PlainTextResponse(token)


@mcp.custom_route("/calculator", methods=["GET"])
async def calculator_page(_: Request) -> HTMLResponse:
    return HTMLResponse(calculator.page())


async def _api(request: Request, fn) -> JSONResponse:
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "")).split(",")[0].strip()
    if not calculator.allowed(ip):
        return JSONResponse({"error": "بہت زیادہ درخواستیں، ایک منٹ بعد کوشش کریں۔"}, status_code=429)
    try:
        data = await request.json()
        if not isinstance(data, dict):
            raise ValueError
        return JSONResponse(fn(data))
    except FaraidError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception:
        return JSONResponse({"error": "ان پٹ درست نہیں، دوبارہ جانچ لیں۔"}, status_code=400)


@mcp.custom_route("/api/simple", methods=["POST"])
async def api_simple(request: Request) -> JSONResponse:
    return await _api(request, calculator.api_simple)


@mcp.custom_route("/api/munasakha", methods=["POST"])
async def api_munasakha(request: Request) -> JSONResponse:
    return await _api(request, calculator.api_munasakha)


@mcp.custom_route("/privacy", methods=["GET"])
async def privacy(_: Request) -> HTMLResponse:
    return HTMLResponse(legal.privacy())


@mcp.custom_route("/terms", methods=["GET"])
async def terms(_: Request) -> HTMLResponse:
    return HTMLResponse(legal.terms())


@mcp.custom_route("/support", methods=["GET"])
async def support(_: Request) -> HTMLResponse:
    return HTMLResponse(legal.support())


@mcp.custom_route("/logo.png", methods=["GET"])
async def logo(_: Request) -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "logo.png", media_type="image/png")


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

    Use this only when there is a single death. If an heir also died after the deceased and
    before the estate was divided (munasakha, several generations / "teen batn"), do NOT call
    this once per person: call calculate_munasakha once, which gives one combined naqsha.

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
    """Inheritance with several deaths in a row (munasakha), Hanafi fiqh: ONE call, ONE naqsha.

    Use this whenever more than one person dies in a chain, e.g. grandfather -> his son -> that
    son's son. Put ALL deaths in case_text as consecutive blocks; the engine carries each
    person's share forward, gives one jamia and makes a single combined naqsha (one Excel file and
    one page). Do not split the chain into separate calls. The order of blocks is the order of
    death: the first block is the first person to die, and each later deceased must be an heir
    named in an earlier block. A person who died before the first deceased is not an heir.

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
