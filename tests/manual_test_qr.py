from mpqr.qr_client import QRClient
import os, json

token = os.getenv("ACCESS_TOKEN")
qr    = QRClient(token)

resp  = qr.create_order("PBTEST", "Artículo X", 1.23)
print(json.dumps(resp, indent=2))

status = qr.get_order("PBTEST", resp["order_id"])
print("Estado:", status["status"])

cancel = qr.cancel_order("PBTEST", resp["order_id"])
print("Cancelado:", cancel == {})
