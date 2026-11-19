import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def criar_sessao() -> requests.Session: 
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429,500,502,503,504], 
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.headers.update({"User-Agent": "LakehouseStack-Ingestion/1.0",
                            "Accept": "application/json",
                            "Content-Type": "application/json"}
                        )
    session.mount("https://", adapter=adapter)
    return session


def download_streaming(url: str, destino: str, session: requests.Session) -> None:
    caminho_arquivo = Path(destino)
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=(5,30)) as response: 
        response.raise_for_status()

        # Abrindo o arquivo no disco em modo de escrita binária ('wb') 
        with open(destino, "wb") as arquivo: 

            for chunk in response.iter_content(chunk_size=1025*1014):
                if chunk: # Ignora pacotes vazios
                    arquivo.write(chunk)
    print(f"Download concluido em {destino} usando quase zero RAM")


if __name__ == "__main__": 

    ufs = ["RS", "SP", "TO"]
    
    with criar_sessao() as sessao:
        for uf in ufs:
            url_origem = f"https://brasilapi.com.br/api/ibge/municipios/v1/{uf}"
            arquivo_destino = f"data/bronze/municipios_{uf}.json"
            
            download_streaming(
                    url=url_origem,
                    destino=arquivo_destino,
                    session=sessao
                )