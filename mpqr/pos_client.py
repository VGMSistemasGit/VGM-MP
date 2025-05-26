# mpqr/pos_client.py
import os
from .http_client import HTTPClient
from .const       import URL_CREATE_POS, URL_GET_POS

class POSClient(HTTPClient):
    def __init__(self, access_token: str):
        super().__init__(access_token)

    # ------------ crear POS --------------------------------------------
    def create_pos(self, external_pos_id: str,
                   name: str = "Caja PB",
                   fixed_amount: bool = False):
        body = {
            "name"        : name,
            "fixed_amount": fixed_amount,
            "store_id"    : os.getenv("STORE_ID"),
            "external_id" : external_pos_id,
            "category"    : 621,   # comercio minorista genérico
        }
        return self._request("POST", URL_CREATE_POS, json=body)

    # ------------ obtener POS ------------------------------------------
    def get_pos(self, external_pos_id: str):
        url = URL_GET_POS.format(external_pos_id=external_pos_id)
        return self._request("GET", url)

