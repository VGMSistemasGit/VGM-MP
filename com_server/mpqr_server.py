# com_server/mpqr_server.py
import sys, os, json, pythoncom
from pathlib import Path
from win32com.server import register
from dotenv import load_dotenv

# ─── Inserta raíz del proyecto en sys.path ────────────────────────────
_here = Path(__file__).resolve()                # …\com_server\mpqr_server.py
_root = _here.parent.parent                     # …\MercadoPagoQr
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# ─── Carga variables de entorno desde .env (si existe) ────────────────
load_dotenv(dotenv_path=_root / ".env", override=False)

# ─── Imports de tu SDK -------------------------------------------------
from mpqr.qr_client  import QRClient
from mpqr.pos_client import POSClient

# ─── Clase expuesta al COM --------------------------------------------
class MPQRServer:
    _public_methods_ = [
        "CreatePOS", "GetPOS",
        "CreateQR", "GetQRStatus", "CancelQR",
        "LastQrPng", "LastOrderId"           
    ]
    _reg_progid_ = "MPQR.Server"
    _reg_clsid_  = "{7B0625B0-F4BB-4F8A-BBA1-0DDEB7E425A1}"   # GUID fijo

    def __init__(self):
        self.qr  = QRClient()
        self.pos = POSClient()
        self._last_png  = ""      # ← buffers internos
        self._last_oid  = ""     

    # -------- POS ----------
    def CreatePOS(self, external_pos_id, name):
        return json.dumps(self.pos.create_pos(external_pos_id, name))

    def GetPOS(self, external_pos_id):
        return json.dumps(self.pos.get_pos(external_pos_id))

    # -------- QR -----------
    def CreateQR(self, external_pos_id, title, amount):
        res = self.qr.create_order(external_pos_id, title, float(amount))
        self._last_png = res.get("qr_png_b64", "")
        self._last_oid = res.get("order_id",  "")
        return json.dumps(res)   

    def GetQRStatus(self, external_pos_id, order_id):
        return json.dumps(self.qr.get_order(external_pos_id, order_id))

    def CancelQR(self, external_pos_id, order_id):
        return json.dumps(self.qr.cancel_order(external_pos_id, order_id))
    
    def LastQrPng(self):    return self._last_png
    def LastOrderId(self):  return self._last_oid

# ─── CLI para registrar / desregistrar --------------------------------
def _usage():
    print("Uso: python mpqr_server.py --register | --unregister")
    sys.exit(1)

if __name__ == "__main__":
    if "--register" in sys.argv:
        register.RegisterClasses(MPQRServer)
        print("✅ MPQR.Server registrado exitosamente.")
    elif "--unregister" in sys.argv:
        register.UnregisterClasses(MPQRServer)
        print("🗑️  MPQR.Server desregistrado exitosamente.")
    else:
        _usage()
