import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession

load_dotenv()

SERVER_IP = "192.168.15.13"
SPARK_REMOTE = f"sc://{SERVER_IP}:15002"
S3_ENDPOINT = f"http://{SERVER_IP}:9000"

PG_CONFIG = {
    "host": SERVER_IP,
    "port": 5432,
    "dbname": os.getenv("POSTGRES_DB", "warehouse"),
    "user": os.getenv("POSTGRES_USER", "lakehouse_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "lakehouse_pg_pass"),
}


def get_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .remote(SPARK_REMOTE)  # type: ignore[attr-defined]
        .appName(app_name)
        .getOrCreate()
    )