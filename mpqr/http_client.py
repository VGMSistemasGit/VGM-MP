import logging, requests, time
from .config import get
from .const  import BASE_URL

log = logging.getLogger("mpqr")

class HTTPClient:
    def __init__(self):
        self.token = get("credentials", "access_token")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json"
        }

    def _request(self, method:str, url:str, **kw):
        t0 = time.perf_counter()
        resp = requests.request(method, BASE_URL + url, headers=self._headers(), **kw)
        log.debug("MP %@ %s → %s (%.3fs)", method.upper(), url, resp.status_code, time.perf_counter() - t0)
        if resp.status_code >= 400:
            print(">>> MP Error", resp.status_code, resp.text)
        try:
            resp.raise_for_status()          # lanza HTTPError si ≥400
        except requests.HTTPError as e:
            raise RuntimeError(
                f"HTTP {resp.status_code}: {resp.text}"
            ) from None          # ← propagamos el mensaje JSON
        return resp.json() if resp.content else {}
