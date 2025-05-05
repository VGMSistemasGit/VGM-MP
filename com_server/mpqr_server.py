# pip install pywin32
import json, pythoncom
from win32com.server import register
from mpqr.qr_client import QRClient
from mpqr.pos_client import POSClient

class MPQRServer:
    _public_methods_ = [
        "CreatePOS", "GetPOS",
        "CreateQR", "GetQRStatus", "CancelQR"
    ]
    _reg_progid_ = "MPQR.Server"
    _reg_clsid_  = "{7B0625B0-F4BB-4F8A-BBA1-0DDEB7E425A1}"   # genera tu propio GUID

    def __init__(self):
        self.qr  = QRClient()
        self.pos = POSClient()

    # -------- POS ----------
    def CreatePOS(self, external_pos_id, name):
        return json.dumps(self.pos.create_pos(external_pos_id, name))

    def GetPOS(self, external_pos_id):
        return json.dumps(self.pos.get_pos(external_pos_id))

    # -------- QR -----------
    def CreateQR(self, external_pos_id, title, amount):
        res = self.qr.create_order(external_pos_id, title, float(amount))
        return json.dumps(res)

    def GetQRStatus(self, external_pos_id, order_id):
        return json.dumps(self.qr.get_order(external_pos_id, order_id))

    def CancelQR(self, external_pos_id, order_id):
        return json.dumps(self.qr.cancel_order(external_pos_id, order_id))

if __name__ == "__main__":
    register.UseCommandLine(MPQRServer)
