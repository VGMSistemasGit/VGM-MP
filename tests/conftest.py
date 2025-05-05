# tests/conftest.py  ←  reemplaza TODO el contenido

# tests/conftest.py
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

import json, uuid, pytest
from types import SimpleNamespace
from urllib.parse import urlparse

class DummyResp:
    """Simula lo justo de requests.Response."""
    def __init__(self, status_code:int, data:dict|None=None):
        self.status_code = status_code
        self._data = data or {}
        self._content = json.dumps(self._data).encode() if data else b""

    # usado por nuestro HTTPClient
    @property
    def content(self):
        return self._content

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

@pytest.fixture(autouse=True)
def mock_requests(mocker):
    """Intercepta todas las llamadas HTTP."""
    def fake_request(method, url, headers=None, **kw):
        path = urlparse(url).path

        # ---- POS -----
        if path.startswith("/pos") and method == "POST":
            return DummyResp(200, {"id":"POS_ID_123","name":kw["json"]["name"]})

        if path.startswith("/pos") and method == "GET":
            external = path.split("/")[-1]
            return DummyResp(200, {"id":"POS_ID_123","external_id":external})

        # ---- QR create order ----
        if "/qrs" in path and method == "PUT":
            return DummyResp(201)                     # vacío

        if "/qrs" in path and method == "POST":
            return DummyResp(200, {
                "qr_data": "00020101021123456",
                "in_store_order_id": str(uuid.uuid4())
            })

        # ---- QR get status ----
        if "/orders" in path and method == "GET":
            return DummyResp(200, {"status":"approved"})

        # ---- QR cancel ----
        if "/orders" in path and method == "DELETE":
            return DummyResp(204)

        raise RuntimeError(f"Endpoint sin mock: {method} {path}")

    return mocker.patch("requests.request", side_effect=fake_request)
