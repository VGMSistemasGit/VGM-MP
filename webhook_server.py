# webhook_server.py
from fastapi import FastAPI, Request, Header
from pathlib import Path
from dotenv import load_dotenv
from mpqr.webhook import WebhookProcessor

import hmac, hashlib, os, json, logging

# ──────────────────── Cargar variables de .env ────────────────────────
#   Coloca .env en la raíz del proyecto.  override=True permite que .env
#   sobrescriba cualquier variable ya definida en el sistema.
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)

# ──────────────────── Logging básico ─────────────────────────────────
log = logging.getLogger("mpqr.webhook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ──────────────────── Aplicación FastAPI ─────────────────────────────
app  = FastAPI(title="Mercado Pago Webhook Receiver")
proc = WebhookProcessor()      # lógica interna: actualiza estados en memoria

# ─────────── Firma HMAC opcional (configurable en el panel) ──────────
SECRET = os.getenv("MP_WEBHOOK_SECRET")   # vacío → no se valida firma

def valid_sig(body: bytes, header_sig: str | None) -> bool:
    """Devuelve True si la firma HMAC coincide o si no se configuró SECRET."""
    if not SECRET:
        return True
    if not header_sig:
        return False
    mac = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, header_sig)

# ──────────────────── ENDPOINT PRINCIPAL ─────────────────────────────
@app.post("/webhook")
async def mp_webhook(
    request: Request,
    x_signature: str | None = Header(default=None)
):
    raw_body = await request.body()

    if not valid_sig(raw_body, x_signature):
        log.warning("Invalid signature — request ignored")
        return {"status": "ignored"}

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        log.warning("Body is not valid JSON")
        return {"status": "ignored"}

    proc.handle_notification(data)   # actualiza estado «approved»
    log.info("Webhook OK: %s", data.get("topic"))
    return {"status": "ok"}
