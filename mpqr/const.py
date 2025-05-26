BASE_URL = "https://api.mercadopago.com"

# --- POS ----------------------------------------------------
URL_CREATE_POS   = "/pos"
URL_GET_POS      = "/pos/{external_pos_id}"

# --- QR dinámico -------------------------------------------
URL_CREATE_ORDER = (
    "/instore/orders/qr/seller/collectors/{user_id}/"
    "pos/{external_pos_id}/qrs"
)                                  # PUT   ✔ crea orden + devuelve qr_data  :contentReference[oaicite:0]{index=0}
URL_GET_ORDER    = (
    "/instore/qr/seller/collectors/{user_id}/"
    "pos/{external_pos_id}/orders"
)                                  # GET   ✔ consulta estado               :contentReference[oaicite:1]{index=1}
# URL_CANCEL_ORDER = (
#     "/instore/qr/seller/collectors/{user_id}/"
#     "pos/{external_pos_id}/orders/{external_order_id}"
# )                                  # DELETE ✔ cancela orden (flujo reversa)
# URL_CANCEL_ORDER = (
#     "/instore/qr/seller/collectors/{user_id}"
#     "/pos/{external_pos_id}/orders/{in_store_order_id}/cancel"
# )

# URL_CANCEL_ORDER = (
#     "/instore/qr/seller/collectors/{user_id}"
#     "/orders/{in_store_order_id}/cancel"
# )

URL_CANCEL_ORDER = (
    "/instore/qr/seller/collectors/{user_id}"
    "/pos/{external_pos_id}/orders"
    # "?external_reference={order_id}"
)

