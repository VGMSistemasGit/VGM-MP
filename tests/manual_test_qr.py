from mpqr.qr_client import QRClient
import os, time, json

token = os.getenv("ACCESS_TOKEN")
cli   = QRClient(token)

print("→ Creando QR …")
order = cli.create_order("PBTEST", "Artículo X", 150)
instore_id = order["in_store_order_id"]   # ← usar éste
print(json.dumps(order, indent=2)[:200], "...\n")

print("→ Consultando estado …")
for _ in range(5):
    st = cli.get_order("PBTEST", order["order_id"])
    if st:
        print("   status:", st["status"])
        break
    time.sleep(2)

# print("→ Cancelando …")
# print(cli.cancel_order("PBTEST", instore_id))   # debería mostrar {}

print("→ Cancelando …")
print(cli.cancel_order(order["order_id"]))    # ← sólo un argumento
