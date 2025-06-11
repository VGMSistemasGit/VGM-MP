
# com_server/mpqr_server.py
"""
Servidor COM 32-bit “MPQR.Server”
"""
import sys, os, json, pythoncom, winreg as wr, tempfile, base64, logging
from pathlib import Path
from win32com.server import register
from dotenv import load_dotenv

# ────────── logging ──────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("mpqr_com")

# ────────── paths / env ──────
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
load_dotenv(_root / ".env", override=False)

from mpqr.qr_client  import QRClient
from mpqr.pos_client import POSClient

CLSID  = "{7B0625B0-F4BB-4F8A-BBA1-0DDEB7E425A1}"
PROGID = "MPQR.Server"


class MPQRServer:
    # ---------- helper interno ---------------------------------------
    def _handle_error(self, where: str, exc: Exception):
        import traceback, io, json
        buf = io.StringIO()
        traceback.print_exc(file=buf)
        return json.dumps({
            "error"  : str(exc),
            "method" : where,
            "detail" : buf.getvalue()
        })
    # ───────── helpers ─────────
    # def _handle_error(self, method:str, exc:Exception):
    #     """Devuelve un dict de error para que PB/PowerShell lo lean."""
    #     log.error("%s → %s", method, exc)
    #     return json.dumps({"success": False, "error": str(exc)})
    
    _public_methods_ = [
        "SetAccessToken",
        "CreatePOS", "GetPOS",
        "CreateQR", "GetQRStatus", "CancelQR",
        "LastQrPng", "LastOrderId", "SaveLastPngToFile"
    ]
    _reg_clsid_  = CLSID
    _reg_progid_ = PROGID

    # ───────── constructor ─────────
    def __init__(self):
        self._token = os.getenv("ACCESS_TOKEN", "")
        self.qr = self.pos = None
        self._last_png = self._last_oid = ""
        if self._token:
            self._build_clients()

    def _build_clients(self):
        self.qr  = QRClient(self._token)
        self.pos = POSClient(self._token)

    
    # ───────── API COM ─────────
    def SetAccessToken(self, token:str):
        self._token = token.strip()
        self._build_clients()
        return True

    # ---- POS ---------------------------------------------------------
    def CreatePOS(self, external_pos_id, name):
        try:
            return json.dumps(self.pos.create_pos(external_pos_id, name))
        except Exception as e:
            return self._handle_error("CreatePOS", e)

    def GetPOS(self, external_pos_id):
        try:
            return json.dumps(self.pos.get_pos(external_pos_id))
        except Exception as e:
            return self._handle_error("GetPOS", e)

    # ---- QR ----------------------------------------------------------
    def CreateQR(self, external_pos_id, title, amount):
        try:
            res = self.qr.create_order(external_pos_id, title, float(str(amount).replace(",", ".")))
            self._last_png = res.get("qr_png_b64", "")
            self._last_oid = res.get("in_store_order_id", "")
            return json.dumps(res)
        except Exception as e:
            return self._handle_error("CreateQR", e)

    def GetQRStatus(self, external_pos_id, order_id):
        try:
            return json.dumps(self.qr.get_order(external_pos_id, order_id))
        except Exception as e:
            return self._handle_error("GetQRStatus", e)    

    def CancelQR(self, in_store_order_id):
        try:
            return json.dumps(self.qr.cancel_order(in_store_order_id))
        except Exception as e:
            return self._handle_error("CancelQR", e)

    # ---- buffers para PB / PowerShell --------------------------------
    def LastQrPng(self):   return self._last_png
    def LastOrderId(self): return self._last_oid

    def SaveLastPngToFile(self, folder:str=""):
        if not self._last_png:
            return ""
        folder = folder or tempfile.gettempdir()
        path   = Path(folder) / f"qr_{self._last_oid}.png"
        with open(path, "wb") as f:
            f.write(base64.b64decode(self._last_png))
        return str(path)

# ───────── utilidades CLI (registro) ─────────
def _reg_path(is32:bool) -> str:
    base = r"Software\Classes"
    if is32:
        base += r"\WOW6432Node"
    return rf"{base}\CLSID\{CLSID}\LocalServer32"

def _check_registry(is32:bool)->bool:
    try:
        with wr.OpenKey(wr.HKEY_LOCAL_MACHINE, _reg_path(is32)):
            return True
    except FileNotFoundError:
        return False

def _usage():
    print("python -m com_server.mpqr_server --register [/reg:32]")
    print("python -m com_server.mpqr_server --unregister [/reg:32]")
    sys.exit(1)

if __name__ == "__main__":
    args  = sys.argv[1:]
    is32  = any(a.lower()=="/reg:32" for a in args)
    b_reg = not is32                      # False → registrar en 32-bit

    if "--register" in args:
        register.RegisterClasses(MPQRServer, bRegister=b_reg)
        ok = _check_registry(is32)
        print("✅ Registrado." if ok else "❌ Registro NO creado.")
        sys.exit(0 if ok else 1)

    elif "--unregister" in args:
        register.UnregisterClasses(MPQRServer)
        print("🗑️  Desregistrado.")
        sys.exit(0)

    else:
        _usage()
