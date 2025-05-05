import uuid, datetime, json, base64, qrcode
from io import BytesIO
from .http_client import HTTPClient
from .config      import get
from .const       import URL_CREATE_ORDER, URL_GET_ORDER, URL_CANCEL_ORDER

class QRClient(HTTPClient):

    def _render_qr_png_b64(self, qr_data:str) -> str:
        """Devuelve imagen PNG en base64 para que PB la muestre en Picture control."""
        img = qrcode.make(qr_data, box_size=8, border=1)
        buff = BytesIO()
        img.save(buff, format="PNG")
        return base64.b64encode(buff.getvalue()).decode()

    # 1) Crear orden + obtener qr_data
    def create_order(self, external_pos_id:str, title:str, total_amount:float, items:list|None=None):
        user_id  = get("credentials", "user_id")
        endpoint = URL_CREATE_ORDER.format(user_id=user_id, external_pos_id=external_pos_id)

        order_id = str(uuid.uuid4())
        payload  = {
            "external_reference": order_id,
            "title": title,
            "total_amount": total_amount,
            "notification_url": get("qr", "notification_url"),
            "expiration_date": (datetime.datetime.utcnow() +
                                datetime.timedelta(minutes=int(get("qr","expiration_min")))).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "items": items or [{
                "sku_number": "SKU-"+order_id[:8],
                "category": "others",
                "title": title,
                "unit_price": total_amount,
                "quantity": 1
            }]
        }

        # PUT devuelve 201 vacío; necesitamos un segundo POST para obtener qr_data
        self._request("PUT", endpoint, json=payload)
        qr_resp = self._request("POST", endpoint)  # crea trama QR  :contentReference[oaicite:2]{index=2}

        b64_png = self._render_qr_png_b64(qr_resp["qr_data"])
        qr_resp.update({"order_id":order_id, "qr_png_b64": b64_png})
        return qr_resp

    # 2) Obtener estado de la orden
    def get_order(self, external_pos_id:str, order_id:str):
        user_id  = get("credentials", "user_id")
        endpoint = URL_GET_ORDER.format(user_id=user_id, external_pos_id=external_pos_id)
        return self._request("GET", endpoint, params={"external_reference": order_id})

    # 3) Cancelar la orden
    def cancel_order(self, external_pos_id:str, order_id:str):
        user_id  = get("credentials", "user_id")
        endpoint = URL_CANCEL_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id,
            external_order_id=order_id
        )
        return self._request("DELETE", endpoint)
