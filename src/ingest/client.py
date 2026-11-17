import os
import boto3
import requests as req
from botocore.config import Config
from dotenv import load_dotenv
from urllib3 import Retry

load_dotenv()



# --- Sessão HTTP para a PokéAPI ---
# client.py
def make_session():
    session = req.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", req.adapters.HTTPAdapter(max_retries=retry))
    return session


# --- Cliente S3 apontando para o RustFS ---
s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{os.getenv('S3_HOST', '100.77.19.215')}:9000",
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"}),
)


def paginate(session, url):
    while url:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        yield from data["results"]
        url = data["next"]


def fetch_detail(session, url):
    response = session.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_all_details(session, list_url):
    for item in paginate(session, list_url):
        yield fetch_detail(session, item["url"])
