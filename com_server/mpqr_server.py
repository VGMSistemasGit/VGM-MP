# com_server/mpqr_server.py
"""
Servidor COM “MPQR.Server”  (32 bit recomendado para PowerBuilder 12.6)

• Registro fiable: sale con código 1 si la clave LocalServer32 no se crea.
• Permite pasar /reg:32 para registrar explícitamente en rama WOW6432Node.
• No necesita ACCESS_TOKEN en fase de registro; se asigna luego con
  SetAccessToken().
"""
import sys, os, json, pythoncom, winreg as wr
import tempfile, base64
from pathlib import Path
from win32com.server import register
from dotenv import load_dotenv

# ─────────────────────  rutas de proyecto  ────────────────────────────
_root = Path(__file__).resolve().parent.parent        # …\MercadoPagoQr
sys.path.insert(0, str(_root))                       # importar SDK

# cargar .env (opcional; NO es obligatorio para registrar)
load_dotenv(_root / ".env", override=False)

from mpqr.qr_client  import QRClient
from mpqr.pos_client import POSClient

CLSID  = "{7B0625B0-F4BB-4F8A-BBA1-0DDEB7E425A1}"
PROGID = "MPQR.Server"

# ─────────────────────  clase expuesta  ───────────────────────────────
class MPQRServer:
    _public_methods_ = [
        "SetAccessToken",
        "CreatePOS", "GetPOS",
        "CreateQR", "GetQRStatus", "CancelQR",
        "LastQrPng", "LastOrderId",'SaveLastPngToFile'
    ]
    _reg_progid_ = PROGID
    _reg_clsid_  = CLSID

    # ------------ constructor -----------------------------------------
    def __init__(self):
        self._token = os.getenv("ACCESS_TOKEN", "")
        self.qr = self.pos = None          # se crean on-demand
        self._last_png = self._last_oid = ""
        if self._token:
            self._build_clients()

    def _build_clients(self):
        self.qr  = QRClient(self._token)
        self.pos = POSClient(self._token)

    # ------------ API expuesta a COM ----------------------------------
    def SetAccessToken(self, token: str):
        """Configura (o cambia) el access_token en tiempo de ejecución."""
        self._token = token.strip()
        self._build_clients()
        return True

    # ---------- POS ----------
    def CreatePOS(self, external_pos_id, name):
        return json.dumps(self.pos.create_pos(external_pos_id, name))

    def GetPOS(self, external_pos_id):
        return json.dumps(self.pos.get_pos(external_pos_id))

    # ---------- QR -----------
    def CreateQR(self, external_pos_id, title, amount):
        res = self.qr.create_order(external_pos_id, title, float(amount))
        self._last_png = res.get("qr_png_b64", "")
        self._last_oid = res.get("in_store_order_id", "")
        return json.dumps(res)

    def GetQRStatus(self, external_pos_id, in_store_order_id):
        return json.dumps(self.qr.get_order(external_pos_id, in_store_order_id))

    def CancelQR(self, in_store_order_id):
        return json.dumps(self.qr.cancel_order(in_store_order_id))

    # buffers para PB
    def LastQrPng(self):   return self._last_png
    def LastOrderId(self): return self._last_oid

    

    def SaveLastPngToFile(self, folder: str = ""):
        if not self._last_png:
            return ""
        folder = folder or tempfile.gettempdir()
        path   = Path(folder) / f"qr_{self._last_oid}.png"
        with open(path, "wb") as f:
            f.write(base64.b64decode(self._last_png))
        return str(path)

# ─────────────────────  utilidades CLI  ───────────────────────────────
def _reg_path(is32: bool) -> str:
    root = r"Software\Classes\CLSID\{}".format(CLSID)
    if is32:
        root = r"Software\Classes\WOW6432Node\CLSID\{}".format(CLSID)
    return root + r"\LocalServer32"

def _check_registry(is32: bool) -> bool:
    try:
        with wr.OpenKey(wr.HKEY_LOCAL_MACHINE, _reg_path(is32)):
            return True
    except FileNotFoundError:
        return False

def _usage() -> None:
    print("Uso:")
    print("  python -m com_server.mpqr_server --register [/reg:32]")
    print("  python -m com_server.mpqr_server --unregister [/reg:32]")
    sys.exit(1)

# ─────────────────────  entrada principal  ────────────────────────────
if __name__ == "__main__":
    args  = sys.argv[1:]
    is32  = any(a.lower() == "/reg:32" for a in args)
    b_reg = not is32                    # RegisterClasses: False = 32 bit

    if "--register" in args:
        try:
            register.RegisterClasses(MPQRServer, bRegister=b_reg)
        except Exception as e:
            print("❌ RegisterClasses falló:", e)
            sys.exit(1)

        if _check_registry(is32):
            print(f"✅ {PROGID} registrado ({'32' if is32 else '64'}-bit).")
            sys.exit(0)
        else:
            print("❌ Registro NO encontrado. "
                  "¿Python/bitness incorrecto o falta de permisos?")
            sys.exit(1)

    elif "--unregister" in args:
        try:
            register.UnregisterClasses(MPQRServer)
            print(f"🗑️  {PROGID} desregistrado.")
        except Exception as e:
            print("⚠️  Desregistro incompleto:", e)
        sys.exit(0)

    else:
        _usage()
