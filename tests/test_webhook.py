import uuid, pytest
from mpqr.webhook import WebhookProcessor

def test_webhook_updates_status():
    wh = WebhookProcessor()
    order_id = str(uuid.uuid4())

    # antes de la notificación, estado pendiente
    assert wh.get_status(order_id) == "pending"

    # simulamos JSON que envía Mercado Pago
    notif = {
        "topic": "merchant_order",
        "action": "payment.updated",
        "external_reference": order_id
    }
    assert wh.handle_notification(notif) is True

    # después, la orden debe figurar aprobada
    assert wh.get_status(order_id) == "approved"
