# mpqr/http_client.py
import logging, os, time, requests
from dotenv import load_dotenv
from pathlib import Path
from .const import BASE_URL

# Cargar .env
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

log = logging.getLogger("mpqr")

class HTTPClient:
    def __init__(self, access_token: str | None = None):
        """
        Si no se pasa token, toma ACCESS_TOKEN del .env (o envvars).
        """
        self.token = access_token or os.getenv("ACCESS_TOKEN")
        if not self.token:
            raise RuntimeError(
                "ACCESS_TOKEN no definido (añádelo al .env o pásalo al constructor)."
            )

    # ---------- helpers -------------------------------------------------
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

    def _request(self, method: str, url: str, **kw):
        t0   = time.perf_counter()
        log.debug("⮕ Payload JSON: %s", kw.get("json"))
        resp = requests.request(
            method, BASE_URL + url, headers=self._headers(), **kw
        )

        log.debug(
            "MP %s %s → %s (%.3fs)",
            method.upper(), url, resp.status_code, time.perf_counter() - t0
        )

        if resp.status_code >= 400:
            log.error("Mercado Pago %s %s → %s %s",
                      method.upper(), url, resp.status_code, resp.text)
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}") from None

        return resp.json() if resp.content else {}
