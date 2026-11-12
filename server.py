"""MCP server exposing the `calculate_inheritance` tool (Hanafi fiqh)."""
import os

import uvicorn
from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from inheritance import InheritanceError, calculate

mcp = MCPServer("inheritance-hanafi")


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


@mcp.tool()
def calculate_inheritance(
    husband: bool = False,
    wives: int = 0,
    father: bool = False,
    mother: bool = False,
    paternal_grandfather: bool = False,
    paternal_grandmother: bool = False,
    maternal_grandmother: bool = False,
    sons: int = 0,
    daughters: int = 0,
    grandsons: int = 0,
    granddaughters: int = 0,
    full_brothers: int = 0,
    full_sisters: int = 0,
    consanguine_brothers: int = 0,
    consanguine_sisters: int = 0,
    uterine_brothers: int = 0,
    uterine_sisters: int = 0,
    other_agnate: bool = False,
    estate: float = 0,
    funeral_expenses: float = 0,
    debts: float = 0,
    bequest: float = 0,
) -> dict:
    """Calculate Islamic inheritance shares (faraid) according to Hanafi fiqh.

    Give only the heirs who are ALIVE at the time of death; leave the rest at 0/False.
    Heirs: husband OR wives (0-4), father, mother, paternal grandfather (dada),
    paternal grandmother (father's mother), maternal grandmother (mother's mother),
    sons, daughters, grandsons/granddaughters (children of a SON), full siblings,
    consanguine siblings (same father), uterine siblings (same mother).
    other_agnate = True if some other male-line relative exists (uncle, nephew...).

    Money (optional): estate = total estate, funeral_expenses, debts, and bequest
    (wasiyyat, capped at 1/3 of what remains). Returns each heir's fraction, percent,
    parts and amount, plus notes on awl (proportional reduction), radd (return of
    surplus) and heirs who are excluded. Not a fatwa: confirm with a qualified mufti.
    """
    heirs = {
        "husband": husband, "wives": wives, "father": father, "mother": mother,
        "paternal_grandfather": paternal_grandfather,
        "paternal_grandmother": paternal_grandmother,
        "maternal_grandmother": maternal_grandmother,
        "sons": sons, "daughters": daughters,
        "grandsons": grandsons, "granddaughters": granddaughters,
        "full_brothers": full_brothers, "full_sisters": full_sisters,
        "consanguine_brothers": consanguine_brothers,
        "consanguine_sisters": consanguine_sisters,
        "uterine_brothers": uterine_brothers, "uterine_sisters": uterine_sisters,
        "other_agnate": other_agnate,
    }
    try:
        return calculate(heirs, estate, funeral_expenses, debts, bequest)
    except InheritanceError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Streamable HTTP at /mcp; host 0.0.0.0 so Render can reach it from outside.
    app = mcp.streamable_http_app(host="0.0.0.0")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
