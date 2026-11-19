import json 
from pathlib import Path

from src.common.http_client import criar_sessao

def extrair_nyc_311(limite: int = 1000, max_paginas: int = 3) -> None:
    url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    destino = Path("data/bronze/nyc_311")
    destino.mkdir(parents=True, exist_ok=True)

    with criar_sessao() as session: 
        for pagina in range(max_paginas): 
            offset = pagina * limite
            params = {
                "$limit": limite,
                "$offset": offset,
                "$order": "created_date DESC",
            }

            response = session.get(url=url, params=params, timeout=(5,10))
            response.raise_for_status()
            registros = response.json() 

            # Se nao tiver registros, para... 
            if not registros: 
                break

            arquivo = destino / f"part_{pagina + 1:04d}.jsonl"
            with open(arquivo, 'w', encoding="utf-8") as f: 
                for item in registros: 
                    f.writelines(json.dumps(item, ensure_ascii=False) + "\n")

            print(f"[NYC 311] Página {pagina + 1} salva ({len(registros)} linhas).")


if __name__ == "__main__":
    extrair_nyc_311()