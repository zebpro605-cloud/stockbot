from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import subprocess
import sys
import re
import os
from urllib.error import URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen


app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Replace * with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ────────────────────────────────────────────────────────────────────
WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://primary-production-c9640.up.railway.app/webhook/f3604670-82e0-48cd-98f4-5cebeec36ce1"
)

# ── Static & Templates ────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_webhook_text() -> str:
    try:
        req = UrlRequest(WEBHOOK_URL, headers={"User-Agent": "fastapi-stockbot"})
        with urlopen(req, timeout=300) as response:
            payload = response.read().decode("utf-8", errors="replace").strip()
        return payload or "No suggestion returned."
    except URLError as e:
        print(f"[ERROR] URLError: {e}")
        return f"Webhook error: unable to reach suggestion service. ({e.reason})"
    except Exception as exc:
        print(f"[ERROR] Unexpected: {exc}")
        return f"Webhook error: {exc}"


def parse_suggestion(raw: str) -> list:
    # Extract inner string from [{"output":"..."}] wrapper
    match = re.search(r'"output"\s*:\s*"(.*?)"(?:\s*\}|\s*\])', raw, re.DOTALL)
    inner = match.group(1) if match else raw

    # Unescape \n
    inner = inner.replace("\\n", "\n")

    rows = []
    # Match pattern: SYMBOL - PKR PRICE: ==> ACTION
    pattern = re.compile(r'([A-Z0-9]+)\s*-\s*PKR\s*([\d.]+)\s*:?\s*==>\s*([A-Z ]+)')
    for m in pattern.finditer(inner):
        rows.append({
            "symbol": m.group(1).strip(),
            "price":  m.group(2).strip(),
            "action": m.group(3).strip()
        })
    return rows


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/suggest_stocks")
def suggest_stocks(request: Request):
    raw = fetch_webhook_text()
    stocks = parse_suggestion(raw)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "stocks": stocks,
            "raw": raw if not stocks else None
        }
    )


@app.get("/buy_stock")
def buy_stock():
    result = subprocess.run(
        [sys.executable, "helper_function_buy.py"],
        capture_output=True,
        text=True,
        timeout=300
    )
    return {
        "message": "Buy stock bot triggered",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }


@app.get("/sell_stock")
def sell_stock():
    result = subprocess.run(
        [sys.executable, "helper_function_sell.py"],
        capture_output=True,
        text=True,
        timeout=300
    )
    return {
        "message": "Sell stock bot triggered",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)