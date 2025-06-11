BASE_URL = "https://api.mercadopago.com"

# --- POS ----------------------------------------------------
URL_CREATE_POS   = "/pos"
URL_GET_POS      = "/pos/{external_pos_id}"

# --- QR dinámico -------------------------------------------
URL_CREATE_ORDER = (
    "/instore/orders/qr/seller/collectors/{user_id}/"
    "pos/{external_pos_id}/qrs"
)                                  # PUT   ✔ crea orden + devuelve qr_data  :contentReference[oaicite:0]{index=0}
# URL_GET_ORDER    = (
#     "/instore/qr/seller/collectors/{user_id}/"
#     "pos/{external_pos_id}/orders"
# )                                  # GET   ✔ consulta estado               :contentReference[oaicite:1]{index=1}

# URL_GET_ORDER = (
#     "/instore/qr/seller/collectors/{user_id}/"
#     "pos/{external_pos_id}/orders"
# )

# GET una orden concreta
URL_GET_ORDER = (
    "/instore/qr/seller/collectors/{user_id}/"
    "pos/{external_pos_id}/orders"
)


URL_CANCEL_ORDER = (
    "/instore/qr/seller/collectors/{user_id}"
    "/pos/{external_pos_id}/orders"
    # "?external_reference={order_id}"
)


# # mpqr/const.py
# """
# Constantes de endpoints REST para Órdenes presenciales v2
# (ver https://www.mercadopago.com/developers/es/docs/qr-code/qr-dynamic)
# """

# BASE_URL = "https://api.mercadopago.com"

# # ─────────── 1) ÓRDENES (QR Dinámico) ──────────────────────────────────
# #   • Crear / Obtener qr_data
# URL_CREATE_ORDER = (
#     "/instore/orders/qr/seller/collectors/{user_id}/"
#     "pos/{external_pos_id}/qrs"
# )

# #   • Obtener estado  (el parámetro external_reference va en la query-string)
# #     GET …/orders?external_reference={order_id}
# URL_GET_ORDER = (
#     "/instore/qr/seller/collectors/{user_id}/"
#     "pos/{external_pos_id}/orders"
# )

# #   • Cancelar (DELETE no necesita body)
# URL_CANCEL_ORDER = (
#     "/instore/qr/seller/collectors/{user_id}/"
#     "pos/{external_pos_id}/orders/{external_order_id}"
# )

# # ─────────── 2) POS (cajas) ────────────────────────────────────────────
# URL_CREATE_POS = "/pos"
# URL_GET_POS    = "/pos/{external_pos_id}"

# # Nota:
# # - Para GET/DELETE de órdenes no incluimos los parámetros de query
# #   porque QRClient los añade dinámicamente.
# # - Si en el futuro Mercado Pago cambia la ruta, basta con tocar aquí;
# #   el resto de la librería quedará intacto.

