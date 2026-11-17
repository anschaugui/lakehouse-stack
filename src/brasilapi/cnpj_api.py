import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def criar_sessao_resiliente() -> requests.Session:
    sessao = requests.Session()
    
    # Configura retentativa automática para Rate Limit (429) e erros de servidor (5xx)
    estrategia_retry = Retry(
        total=3,                              # Máximo de 3 tentativas extras
        backoff_factor=2,                     # Espera exponencial: 2s, 4s, 8s...
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True       # Respeita o cabeçalho 'Retry-After' se a API enviar
    )
    
    adapter = HTTPAdapter(max_retries=estrategia_retry)
    sessao.mount("https://", adapter)
    sessao.mount("http://", adapter)
    return sessao

def extrair_cnpj(cnpj: str, sessao: requests.Session) -> dict | None:
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    
    try:
        # Removemos o 'params' desnecessário desta rota
        response = sessao.get(url, timeout=5)
        
        if response.status_code == 404:
            print(f"[AVISO] CNPJ {cnpj} não encontrado na base.")
            return None
            
        response.raise_for_status()
        dados_brutos = response.json()
        
        # Filtrando apenas o schema necessário (camada Bronze/Silver)
        return {
            "cnpj": dados_brutos.get("cnpj"),
            "razao_social": dados_brutos.get("razao_social"),
            "uf": dados_brutos.get("uf"),
            "municipio": dados_brutos.get("municipio"),
        }

    except requests.exceptions.HTTPError as err:
        print(f"[ERRO HTTP] Status {response.status_code}: {err}")
        raise
    except requests.exceptions.RequestException as err:
        print(f"[ERRO CRÍTICO] Falha na requisição: {err}")
        raise

if __name__ == "__main__":
    sessao = criar_sessao_resiliente()
    dados_bb = extrair_cnpj("02420449000134", sessao)
    print(dados_bb)