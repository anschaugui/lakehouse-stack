import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

regra_retry = Retry(
    total=3,                              # Tenta até 3 vezes extras antes de desistir
    backoff_factor=2,                     # Espera exponencial: 2s, depois 4s, depois 8s
    status_forcelist=[429, 500, 502, 503, 504], # Quais códigos HTTP disparam o retry
    allowed_methods=["GET"]               # Só repete requisições de leitura (seguras)
)

# Colocamos a regra dentro do Transport Adapter
adaptador = HTTPAdapter(max_retries=regra_retry)

with requests.Session() as sessao: 
    sessao.headers.update({"User-Agent": "MeuPipelineDados/1.0"})

    sessao.mount("https://", adapter=adaptador)

    # A partir daqui, qualquer sessao.get() ja tem o keep-alive + retry automatico
    r1 = sessao.get("https://brasilapi.com.br/api/banks/v1/1", timeout=5)
    print("Banco 1:", r1.json()["name"])