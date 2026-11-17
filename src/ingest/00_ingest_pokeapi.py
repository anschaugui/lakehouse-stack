import json
from datetime import date
from itertools import islice
# 00_ingest_pokeapi.py
from ingest.client import make_session, fetch_all_details, s3

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon?limit=100"
BUCKET = "landing"
BATCH_SIZE = 100
MAX_POKEMON = 250  # limite para estudo; use None para buscar tudo

def batched(iterable, n):
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


def to_jsonl(records):
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)


def run():
    # Confere a conexão antes de buscar dados
    print("Buckets:", [b["Name"] for b in s3.list_buckets()["Buckets"]])
    
    session = make_session()

    pokemons = fetch_all_details(session, POKEAPI_URL)
    if MAX_POKEMON:
        pokemons = islice(pokemons, MAX_POKEMON)

    dt = date.today().isoformat()
    for n, batch in enumerate(batched(pokemons, BATCH_SIZE), start=1):
        key = f"pokeapi/dt={dt}/part-{n:04d}.jsonl"
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=to_jsonl(batch).encode("utf-8"),
        )
        print(f"Gravado s3://{BUCKET}/{key} ({len(batch)} registros)")


if __name__ == "__main__":
    run()
