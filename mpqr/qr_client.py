# mpqr/qr_client.py
import uuid, datetime, json, base64, qrcode
from io import BytesIO

from .http_client import HTTPClient
from .config      import get                # ← ahora sin sección/clave doble
from .const       import (
    URL_CREATE_ORDER,
    URL_GET_ORDER,
    URL_CANCEL_ORDER,
)

class QRClient(HTTPClient):

    # ───────────────────────── util interno ──────────────────────────
    def _render_qr_png_b64(self, qr_data: str) -> str:
        """Devuelve la imagen PNG en Base64 para mostrar en PowerBuilder."""
        img  = qrcode.make(qr_data, box_size=8, border=1)
        buff = BytesIO()
        img.save(buff, format="PNG")
        return base64.b64encode(buff.getvalue()).decode()

    # ───────────────────────── 1) Crear orden ────────────────────────
    def create_order(
        self,
        external_pos_id: str,
        title: str,
        total_amount: float,
        items: list | None = None,
    ):
        user_id  = get("USER_ID")
        endpoint = URL_CREATE_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id
        )

        order_id = str(uuid.uuid4())
        exp_min  = int(get("EXPIRATION_MIN", "15"))       # ← valor por defecto
        payload  = {
            "external_reference": order_id,
            "title": title,
            "total_amount": total_amount,
            "notification_url": get("WEBHOOK_URL"),
            "expiration_date": (
                datetime.datetime.utcnow() +
                datetime.timedelta(minutes=exp_min)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "items": items
            or [
                {
                    "sku_number": "SKU-" + order_id[:8],
                    "category": "others",
                    "title": title,
                    "unit_price": total_amount,
                    "quantity": 1,
                }
            ],
        }

        # PUT devuelve 201 vacío; segundo POST devuelve qr_data
        self._request("PUT", endpoint, json=payload)
        qr_resp = self._request("POST", endpoint)

        b64_png = self._render_qr_png_b64(qr_resp["qr_data"])
        qr_resp.update({"order_id": order_id, "qr_png_b64": b64_png})
        return qr_resp

    # ───────────────────────── 2) Obtener estado ─────────────────────
    def get_order(self, external_pos_id: str, order_id: str):
        user_id  = get("USER_ID")
        endpoint = URL_GET_ORDER.format(
            user_id=user_id, external_pos_id=external_pos_id
        )
        return self._request("GET", endpoint, params={"external_reference": order_id})

    # ───────────────────────── 3) Cancelar orden ──────────────────────
    def cancel_order(self, external_pos_id: str, order_id: str):
        user_id  = get("USER_ID")
        endpoint = URL_CANCEL_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id,
            external_order_id=order_id,
        )
        return self._request("DELETE", endpoint)
