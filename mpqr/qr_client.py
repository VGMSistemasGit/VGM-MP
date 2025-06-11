# mpqr/qr_client.py
import os
import uuid
import datetime
import base64
import qrcode
import logging
from io import BytesIO
from .http_client import HTTPClient
from .const import URL_CREATE_ORDER, URL_GET_ORDER, URL_CANCEL_ORDER

# ─── Configurar logging ───────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("mpqr_com")

# ───────── zona horaria MLA (con fallback) ────────────
try:
    from zoneinfo import ZoneInfo
    AR_TZ = ZoneInfo("America/Argentina/Buenos_Aires")
except Exception:
    AR_TZ = datetime.timezone(datetime.timedelta(hours=-3))

# ───────── helper PNG → Base-64 ───────────────────────
def _render_qr_png_b64(qr_data: str) -> str:
    img  = qrcode.make(qr_data, box_size=8, border=1)
    buff = BytesIO()
    img.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode()

# ───────── clase principal ────────────────────────────
class QRClient(HTTPClient):
    def __init__(self, access_token: str):
        super().__init__(access_token)

    # ───── Crear orden QR MercadoPago ──────────────────
    def create_order(
        self,
        external_pos_id: str,
        title: str,
        total_amount: float,
        external_reference: str = None,
        notification_url: str = None,
        sku_number: str = None,
        category: str = "electronics",
        description: str = None
    ) -> dict:
        """
        Crea una orden QR con todos los campos customizables.
        """
        user_id = os.getenv("USER_ID")
        endpoint = URL_CREATE_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id
        )

        if not external_reference:
            external_reference = str(uuid.uuid4())
        if not description:
            description = title

        payload = {
            "external_reference": external_reference,
            "notification_url": notification_url,
            "total_amount": total_amount,
            "items": [{
                "sku_number": sku_number if sku_number else "SKU001",
                "category": category,
                "title": title,
                "description": description,
                "quantity": 1,
                "unit_measure": "unit",
                "unit_price": total_amount,
                "total_amount": total_amount
            }],
            "title": title,
            "description": description
        }

        # Limpia el payload de campos None para evitar rechazos por campos vacíos
        payload = {k: v for k, v in payload.items() if v is not None}

        log.info(f"Creando orden QR: endpoint={endpoint}, payload={payload}")
        return self._request("PUT", endpoint, json=payload)

    
    # ───── 2) estado de orden ────────────────────────────────────────
    def get_order(self, external_pos_id: str, order_id: str) -> dict:
        """
        Devuelve el dict de la orden ({} si aún no apareció) buscando
        por external_reference = order_id.
        """
        user_id  = os.getenv("USER_ID")
        endpoint = URL_GET_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id,
        )

        try:
            resp = self._request(
                "GET", endpoint,
                params={"external_reference": order_id},
            )
        except RuntimeError as e:
            # 404 sólo ocurre si la POS no existe; para una orden ausente
            # la API responde 200 con lista vacía.
            raise

        if isinstance(resp, list):
            return resp[0] if resp else {}

        if isinstance(resp, dict):
            # {"elements":[…]}  ó  {"results":[…]}
            for key in ("elements", "results"):
                if key in resp and resp[key]:
                    return resp[key][0]
        return {}

    def get_order_status(self, external_pos_id: str, external_reference: str = None):
        """
        Consulta el estado de una orden usando el flujo correcto:
        1. Primero intenta consultar como orden QR (antes del pago)
        2. Si no encuentra, busca como pago procesado (después del pago)
        
        Args:
            external_pos_id: ID del POS
            external_reference: Referencia externa de la orden
            
        Returns:
            dict: Estado de la orden/pago con información unificada
        """
        try:
            # PASO 1: Intentar consultar como orden QR (estado pre-pago)
            try:
                qr_order_result = self.get_qr_order(external_pos_id, external_reference)
                if qr_order_result:
                    log.info("Orden encontrada en estado QR: %s", external_reference)
                    return {
                        "status": "pending",
                        "source": "qr_order",
                        "data": qr_order_result,
                        "external_reference": external_reference
                    }
            except Exception as qr_error:
                log.debug("No encontrada como orden QR: %s", str(qr_error))
            
            # PASO 2: Buscar como pago procesado usando Payments API
            payment_result = self.get_processed_payment(external_reference)
            if payment_result:
                log.info("Pago procesado encontrado: %s", external_reference)
                return {
                    "status": payment_result.get("status", "unknown"),
                    "source": "payment",
                    "data": payment_result,
                    "external_reference": external_reference,
                    "payment_id": payment_result.get("id"),
                    "amount": payment_result.get("transaction_amount"),
                    "currency": payment_result.get("currency_id"),
                    "date_created": payment_result.get("date_created"),
                    "date_approved": payment_result.get("date_approved")
                }
            
            # PASO 3: No encontrado en ningún lado
            log.warning("Orden/Pago no encontrado: %s", external_reference)
            return {
                "status": "not_found",
                "source": "none",
                "external_reference": external_reference,
                "error": "Orden no encontrada en QR ni en pagos procesados"
            }
            
        except Exception as e:
            log.error("Error consultando estado de orden: %s", str(e))
            raise
    
    def get_qr_order(self, external_pos_id: str, external_reference: str = None):
        """
        Consulta el estado de una orden QR (método original)
        Solo funciona ANTES de que se procese el pago
        """
        user_id = get("USER_ID")
        url = URL_GET_ORDER.format(
            user_id=user_id,
            external_pos_id=external_pos_id
        )
        
        params = {}
        if external_reference:
            params["external_reference"] = external_reference
        
        response = self._request("GET", url, params=params)
        return response
    
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