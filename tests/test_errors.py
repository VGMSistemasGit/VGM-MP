import pytest
from mpqr.http_client import HTTPClient
from tests.conftest import DummyResp   # ya lo tienes

# parametrizamos varios códigos
@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 500, 502])
def test_http_error_handling(mocker, status):
    # simulamos que todas las peticiones devuelven ese status
    mocker.patch(
        "requests.request",
        return_value=DummyResp(status)  # cuerpo vacío
    )
    cli = HTTPClient()
    with pytest.raises(RuntimeError):  # tu wrapper debe alzar
        cli._request("GET", "/pos/xyz")
