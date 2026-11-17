import requests

def extrair_municipios(uf: str) -> list[dict]: 
    url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{uf}"

    # passagem segura de query parameters 
    parametros = {
        "providers": "dados-abertos-br,gov,wikipedia"
    }

    try: 
        response = requests.get(url, params=parametros, timeout=(3.05,10))

        response.raise_for_status()

        dados = response.json()
        return dados
    except requests.exceptions.Timeout:
        print(f"[ERRO] Timout ao buscar dados para a UF: {uf}")
    except requests.exceptions.HTTPError as err:
        print(f"[ERRO HTTP] Status {response.status_code}: {err}")
    except requests.exceptions.RequestException as err: 
        print(f"[ERRO CRITICO] falha na requisicao {err}")
        raise

    # Testando extração

if __name__ == "__main__": 
    municipios_sp = extrair_municipios("RS")
    for i in municipios_sp: 
        print(i)