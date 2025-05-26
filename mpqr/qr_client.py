# mpqr/qr_client.py
import os, uuid, datetime, base64, qrcode
from io import BytesIO
from .http_client import HTTPClient
from .const       import URL_CREATE_ORDER, URL_GET_ORDER, URL_CANCEL_ORDER

# ───────── zona horaria MLA (con fallback) ────────────────────────────
try:
    from zoneinfo import ZoneInfo                # requiere tzdata en Windows
    AR_TZ = ZoneInfo("America/Argentina/Buenos_Aires")
except Exception:                                # fallback UTC-03:00
    AR_TZ = datetime.timezone(datetime.timedelta(hours=-3))

# ───────── helper PNG → Base-64 ───────────────────────────────────────
def _render_qr_png_b64(qr_data: str) -> str:
    img  = qrcode.make(qr_data, box_size=8, border=1)
    buff = BytesIO(); img.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode()

# ───────── clase principal ────────────────────────────────────────────
class QRClient(HTTPClient):
    def __init__(self, access_token: str):
        super().__init__(access_token)

    # ───── 1) crear orden ─────────────────────────────────────────────
    def create_order(
        self,
        external_pos_id: str,
        title: str,
        total_amount: float,
        items: list | None = None,
    ) -> dict:

        user_id  = os.getenv("USER_ID")
        endpoint = URL_CREATE_ORDER.format(user_id=user_id,
                                           external_pos_id=external_pos_id)

        order_id = str(uuid.uuid4())
        total    = round(float(total_amount), 2)

        # Expiración ISO 8601 con milisegundos y offset −03:00
        exp_min = int(os.getenv("EXPIRATION_MIN", "15"))
        exp_dt  = (datetime.datetime.now(tz=AR_TZ) +
                   datetime.timedelta(minutes=exp_min))
        expiration = exp_dt.strftime("%Y-%m-%dT%H:%M:%S.000%z")
        expiration = expiration[:-2] + ":" + expiration[-2:]   # …-03:00

        # ---------- modalidad A: monto fijo ---------------------------
        if items is None:
            payload = {
                "external_reference": order_id,
                "title"            : title,
                "description"      : title,
                "total_amount"     : total,
                "cash_out"         : { "amount": total },   # ← OBLIGATORIO
                "notification_url" : os.getenv("WEBHOOK_URL"),
                "expiration_date"  : expiration,
            }
        # ---------- modalidad B: detalle de ítems ---------------------
        else:
            for it in items:
                it.setdefault("unit_measure", "unit")
            payload = {
                "external_reference": order_id,
                "title"            : title,
                "description"      : title,
                "notification_url" : os.getenv("WEBHOOK_URL"),
                "expiration_date"  : expiration,
                "items"            : items,
            }

        # PUT crea / actualiza la orden
        self._request("PUT", endpoint, json=payload)

        # POST devuelve qr_data (body con external_reference)
        qr_resp = self._request("POST", endpoint, json=payload)

        qr_resp.update({
            "order_id"  : order_id,
            "qr_png_b64": _render_qr_png_b64(qr_resp["qr_data"]),
        })
        return qr_resp

    # ───── 2) estado de orden ────────────────────────────────────────
    # ---------- 2) estado de la orden ------------------------------------
    def get_order(self, external_pos_id: str, order_id: str) -> dict:
        """
        Devuelve el dict de la orden (o {} si aún no existe).

        La API responde una *lista*; tomamos el primer elemento.
        """
        user_id  = os.getenv("USER_ID")
        endpoint = URL_GET_ORDER.format(user_id=user_id,
                                        external_pos_id=external_pos_id)

        resp = self._request(
            "GET", endpoint,
            params={"external_reference": order_id}
        )

        # ── Distintos formatos posibles ──────────────────────────────
        if isinstance(resp, list):
            return resp[0] if resp else {}

        # algunas cuentas devuelven {"elements":[{…}]}
        if isinstance(resp, dict) and "elements" in resp:
            elems = resp.get("elements", [])
            return elems[0] if elems else {}

        # {"results":[{…}]}  (caso legacy)
        if isinstance(resp, dict) and "results" in resp:
            res = resp.get("results", [])
            return res[0] if res else {}

        return {}           # si el formato es inesperado


#    # ---------- 3) cancelar orden ----------------------------------------
#     def cancel_order(self, external_pos_id: str, in_store_order_id: str):
#         """
#         Cancela la orden usando el in_store_order_id que devuelve el POST.
#         """
#         user_id  = os.getenv("USER_ID")
#         endpoint = URL_CANCEL_ORDER.format(
#             user_id=user_id,
#             external_pos_id=external_pos_id,
#             external_order_id=in_store_order_id   # ← es el in_store_order_id
#         )
#         return self._request("DELETE", endpoint)

    # def cancel_order(self, external_pos_id: str, in_store_order_id: str):
    #     """
    #     Cancela la orden (reversa) usando el in_store_order_id
    #     que devuelve create_order().
    #     """
    #     # user_id = os.getenv("USER_ID")
    #     # endpoint = URL_CANCEL_ORDER.format(
    #     #     user_id=user_id,
    #     #     external_pos_id=external_pos_id,
    #     #     in_store_order_id=in_store_order_id
    #     # )
    #     # El body puede ser {}, pero algunos SDK envían None; ambos funcionan.
    #     # return self._request("POST", endpoint, json={})
    
    #     user_id  = os.getenv("USER_ID")
    #     endpoint = URL_CANCEL_ORDER.format(
    #         user_id=user_id,
    #         in_store_order_id=in_store_order_id,
    #     )
    #     # body vacío ({}) o None – ambos aceptados
    #     return self._request("POST", endpoint, json={})

    # ---------- 3) cancelar orden ----------------------------------------
    def cancel_order(self, order_id: str) -> dict:
        """
        Revierte la orden usando el in_store_order_id que devolvió create_order().
        """
        user_id  = os.getenv("USER_ID")
        external_pos_id = os.getenv("EXTERNAL_POS_ID")
        endpoint = URL_CANCEL_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id,
            order_id= order_id
        )

        return self._request("DELETE", endpoint, json={})  