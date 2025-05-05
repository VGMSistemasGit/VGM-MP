import os, time, pytest, uuid
from mpqr.qr_client import QRClient

pytestmark = pytest.mark.integration   # todo el archivo marcado

SKIP_REASON = "Variables de entorno MP_SANDBOX=1 no definidas"

def sandbox_enabled():
    return os.getenv("MP_SANDBOX") == "1"

# --- debug temporal: muestra la variable al ejecutar el test ---
print("DEBUG MP_SANDBOX =", os.getenv("MP_SANDBOX"))

@pytest.mark.skipif(not sandbox_enabled(), reason=SKIP_REASON)
def test_qr_sandbox_flow():
    """
    Crea un QR real, espera la respuesta OPENED de la API y
    luego lo cancela.  No requiere que el pago se complete.
    """
    cli = QRClient()
    external_pos_id = "PBTEST"        # <--  tu POS real (sin guion bajo)
    amount = 1.23

    qr = cli.create_order(external_pos_id, "Prueba integración", amount)
    order_id = qr["order_id"]

    # --- Poll de estado hasta que aparezca la orden --------------
    for _ in range(5):
        status = cli.get_order(external_pos_id, order_id)
        if status["status"] in ("opened", "approved", "rejected"):
            break
        time.sleep(2)

    assert status["status"] in ("opened", "approved")

    # --- Cancelamos la orden (flujo de reversa) -------------------
    cancel = cli.cancel_order(external_pos_id, order_id)
    assert cancel == {}
