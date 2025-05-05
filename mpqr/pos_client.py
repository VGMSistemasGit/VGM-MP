import json, uuid
from .http_client import HTTPClient
from .config       import get
from .const        import URL_CREATE_POS, URL_GET_POS

class POSClient(HTTPClient):
    def create_pos(self, external_pos_id:str, name:str="Caja PB", fixed_amount=False):
        body = {
            "name": name,
            "fixed_amount": fixed_amount,
            "store_id": get("pos", "external_store_id"),
            "external_id": external_pos_id,
            "category": 621  # comercio minorista genérico
        }
        return self._request("POST", URL_CREATE_POS, json=body)

    def get_pos(self, external_pos_id:str):
        url = URL_GET_POS.format(external_pos_id=external_pos_id)
        return self._request("GET", url)
