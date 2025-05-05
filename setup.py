from mercadopago_qr.mercado_pago_com import MercadoPagoQR
import win32com.server.register

if __name__ == "__main__":
    print("Registrando COM Server...")
    win32com.server.register.UseCommandLine(MercadoPagoQR)