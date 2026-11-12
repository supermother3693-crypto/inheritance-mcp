# inheritance-mcp

MCP server for **Faraid (Hanafi inheritance)**. The calculation engine is in `faraid/`
(exact integer arithmetic, munasakha, tashih, awl, radd, Umariyyatayn). `service.py` adds
the rupee distribution (funeral costs, debts, one-third bequest limit) and `server.py`
exposes two tools:

| Tool | Use |
|------|-----|
| `calculate_inheritance` | one deceased person, heirs given as counts; `create_naqsha=true` also makes the files below |
| `calculate_munasakha` | several deaths in a row, text format (see `cases/*.txt`); makes the files below by default |

Naqsha files (temporary private links, valid 24 hours, served at `/files/<token>/<name>`):
the traditional naqsha as **Excel** (`render_xlsx.py`, optional rupee row) and as a **printable page**
(`naqsha.py`) with a "Save as PDF" button. A direct **PDF** link is added only where LibreOffice
is installed (`soffice`); plain Render Python does not have it, so use the page's button there.

> A calculation aid, not a fatwa. Confirm the final division with a qualified mufti.
> Not covered: dhawil-arham, unborn child, missing person, khuntha, mawla, impediments
> (murder, slavery, difference of religion), the Sahibayn muqasama with a grandfather,
> great-grandchildren. See `SYSTEM_ur.md` and `README_engine_ur.md` for the engine design.

## Files
- `faraid/` – engine (`engine.py`, `parser.py`, `relations.py`)
- `service.py`, `server.py`, `files.py`, `naqsha.py` – MCP layer (streamable HTTP, endpoint `/mcp`, health `/health`)
- `cases/` – sample munasakha cases; `tests/engine/` – engine tests; `test_service.py` – server-layer tests

## Run and test
```
pip install -r requirements.txt
python server.py                     # http://localhost:8000/mcp
python test_service.py
python tests/engine/test_cases.py
python tests/engine/test_book.py     # 30/33: the 3 differences are display only (see BOOK_AUDIT_NOTES.md)
```

## Deploy on Render
Web Service from this repo. Build `pip install -r requirements.txt`, start `python server.py`.
Connector URL: `https://<service-name>.onrender.com/mcp`.
