# tests/manual_test_savepng.py
import json, os, win32com.client as wc, tempfile

TOKEN   = "TEST-6315433665621565-042910-cf49248dbba65897a7e6dd30f2f93742-63189587"
POS_ID  = "PBTEST"
TITLE   = "Artículo X"
AMOUNT  = 150

# 1) instanciar servidor COM -------------------------------------------------
srv = wc.Dispatch("MPQR.Server")          # crea proceso pythonw.exe con tu venv
srv.SetAccessToken(TOKEN)                 # o falla si token inválido

# 2) crear QR ----------------------------------------------------------------
resp = json.loads(srv.CreateQR(POS_ID, TITLE, AMOUNT))
print("In-Store Order ID:", resp["in_store_order_id"])

# 3) grabar PNG en carpeta temp ---------------------------------------------
tmpdir = tempfile.gettempdir()            # p.ej. C:\Users\<user>\AppData\Local\Temp
png    = srv.SaveLastPngToFile(tmpdir)    # ← nuevo método que añadiste
print("PNG guardado en:", png, "(", os.path.getsize(png), "bytes)")

# 4) validación simple -------------------------------------------------------
assert os.path.exists(png) and os.path.getsize(png) > 300, "PNG inválido"
print("✅ imagen OK")
