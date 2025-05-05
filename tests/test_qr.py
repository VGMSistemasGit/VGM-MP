from mpqr.qr_client import QRClient

def test_qr_full_flow():
    cli   = QRClient()
    qr    = cli.create_order("PB_CAJA1", "Artículo X", 1234.56)

    # 1) Se genera qr_data y png
    assert "qr_data" in qr and "qr_png_b64" in qr
    order_id = qr["order_id"]

    # 2) Estado aprobado (mock)
    status = cli.get_order("PB_CAJA1", order_id)
    assert status["status"] == "approved"

    # 3) Cancelación (mock)
    cancel_resp = cli.cancel_order("PB_CAJA1", order_id)
    assert cancel_resp == {}  # DELETE 204 → cuerpo vacío
