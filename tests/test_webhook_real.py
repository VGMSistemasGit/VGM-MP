# tests/test_webhook_real.py
import os, uuid, json, hmac, hashlib, pytest, requests

pytestmark = pytest.mark.integration   # se ejecuta con -m integration

WEBHOOK_URL = os.getenv("WEBHOOK_URL")          # debe terminar en /webhook
SECRET       = os.getenv("MP_WEBHOOK_SECRET")   # clave HMAC

@pytest.mark.skipif(not WEBHOOK_URL or not SECRET,
                    reason="WEBHOOK_URL o MP_WEBHOOK_SECRET no definidas")
def test_webhook_endpoint():
    # ---------- payload de ejemplo ----------
    order_id = str(uuid.uuid4())
    payload  = {
        "topic": "merchant_order",
        "action": "payment.updated",
        "external_reference": order_id
    }
    body_bytes = json.dumps(payload).encode()

    # ---------- firma HMAC SHA-256 ----------
    signature = hmac.new(
        SECRET.encode(), body_bytes, hashlib.sha256
    ).hexdigest()

    # ---------- POST al endpoint ----------
    resp = requests.post(
        WEBHOOK_URL,
        data=body_bytes,
        headers={
            "Content-Type": "application/json",
            "x-signature":  signature
        },
        timeout=5
    )

    # ---------- asserts ----------
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
