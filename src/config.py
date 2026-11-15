import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession

load_dotenv()

SPARK_HOST = os.getenv("SPARK_HOST", os.getenv("SERVER_IP", "192.168.15.13"))
PG_HOST = os.getenv("POSTGRES_HOST", os.getenv("SERVER_IP", "192.168.15.13"))

PG_CONFIG = {
    "host": PG_HOST,
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "lakehouse"),
    "user": os.getenv("POSTGRES_USER", "lakehouse"),
    "password": os.getenv("POSTGRES_PASSWORD", "lakehouse_pg_pass"),
}

def get_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .remote(f"sc://{SPARK_HOST}:15002")
        .getOrCreate()
    )