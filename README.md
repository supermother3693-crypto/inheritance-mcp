# inheritance-mcp

MCP server with one tool, `calculate_inheritance`, that computes Islamic
inheritance shares (faraid) according to **Hanafi fiqh**: fixed shares, residuary
heirs (asaba), exclusion (hajb), awl, radd, the Umariyyatayn cases, debts, funeral
costs and the one-third bequest limit.

> This is a calculation aid, not a fatwa. Confirm the final division with a
> qualified mufti. Not covered: dhawil-arham, great-grandparents, missing person,
> unborn child, difference of religion and other special cases.

## Files
- `inheritance.py` – the calculation (no dependencies)
- `server.py` – MCP server (streamable HTTP, endpoint `/mcp`, health check `/health`)
- `test_inheritance.py` – tests (`python test_inheritance.py`)
- `render.yaml` – deploy settings for Render

## Run locally
```
pip install -r requirements.txt
python server.py        # http://localhost:8000/mcp
```

## Deploy on Render
Create a Web Service from this repository. Build: `pip install -r requirements.txt`,
start: `python server.py`. The connector URL is `https://<service-name>.onrender.com/mcp`.
