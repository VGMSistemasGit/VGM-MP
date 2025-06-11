from mpqr.qr_client import QRClient
import os, time, json

token = os.getenv("ACCESS_TOKEN")
cli   = QRClient(token)

print("→ Creando QR …")
order = cli.create_order("PBTEST", "Artículo X", 1)
instore_id = order["in_store_order_id"]   # ← usar éste
print(json.dumps(order, indent=2)[:200], "...\n")

print("→ Consultando estado …")
print("\nConsultando estado …")
for _ in range(12):          # 12*5 = 60 s máx
    data = cli.get_order("PBTEST", order["order_id"])
    if data:                          # la API devolvió algo
        print(json.dumps(data, indent=2, ensure_ascii=False))
        break
    time.sleep(5)
else:
    print("Aún no existe / cliente no pagó en 60 s.")


# print("→ Cancelando …")
# print(cli.cancel_order("PBTEST", instore_id))   # debería mostrar {}

print("→ Cancelando …")
print(cli.cancel_order(order["order_id"]))    # ← sólo un argumento
