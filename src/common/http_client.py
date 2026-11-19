import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def criar_sessao(headers_extras: dict | None = None) -> requests.Session: 
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "LakehouseStack-Ingestion/1.0",
        "Accept": "application/json",
    })

    if headers_extras:
        session.headers.update(headers_extras)

    session.mount("https://", adapter=adapter)
    session.mount("http://", adapter=adapter)

    return session