# mpqr/webhook.py
import json, logging

log = logging.getLogger("mpqr")

class WebhookProcessor:
    """
    Procesa el JSON que Mercado Pago envía a notification_url.
    Para el test nos basta con leer 'topic' y 'action'.
    """
    def __init__(self):
        self._store = {}   # simulamos base de datos en memoria

    def handle_notification(self, data: dict):
        topic  = data.get("topic")     # e.g. "merchant_order"
        action = data.get("action")    # e.g. "payment.updated"
        extref = data.get("external_reference")

        # --- lógica mínima ----
        if topic == "merchant_order" and action == "payment.updated":
            self._store[extref] = "approved"

        log.info("Notif %s/%s ext=%s", topic, action, extref)
        return True

    # helper para test
    def get_status(self, extref:str):
        return self._store.get(extref, "pending")
