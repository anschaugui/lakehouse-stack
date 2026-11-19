import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def criar_sessao() -> requests.Session: 
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "LakehouseStack-Ingestion/1.0",
        "Accept": "application/vnd.github+json"
    })
    session.mount("https://", adapter=adapter)
    return session

def extrair_todos_repositorios(org: str) -> list[dict]: 
    url = f"https://api.github.com/orgs/{org}/repos"
    params = {"per_page": 10, "page": 1}
    todos_dados = []
    pagina_atual = 1

    with criar_sessao() as session: 
        while url: 
            print(f"Extraindo página {pagina_atual}...")
            # Na 1 volta usa 'params'; nas seguintes, a URL do 'next' já vem com os parâmetros embutidos
            response = session.get(url=url, params=params if pagina_atual == 1 else None, timeout=(5,10))
            response.raise_for_status()

            dados_pagina = response.json()
            todos_dados.extend(dados_pagina)

            proxima_pagina = response.links.get("next")
            url = proxima_pagina["url"] if proxima_pagina else None
            pagina_atual +=1

    return todos_dados

if __name__ == "__main__": 
    repos = extrair_todos_repositorios("BrasilAPI")
    print(f"\nTotal de repositórios extraídos em todas as páginas: {len(repos)}")
    print("Exemplo:", repos[0]["name"])