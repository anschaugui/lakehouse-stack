from datetime import datetime, timedelta
from airflow import DAG 
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "guilherme",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="lakehouse_medalhao_pipeline",
    default_args=default_args,
    description="Orquestração ETL Medalhão: Bronze -> Silver -> Gold (PostgreSQL)",
    schedule="0 6 * * *",  # Roda todos os dias às 06:00
    start_date=datetime(2026, 11, 15),
    catchup=False,
    tags=["lakehouse", "pyspark", "medalhao"],
) as dag:

    ingest_bronze = BashOperator(
        task_id="01_ingest_bronze",
        bash_command="python /opt/airflow/src/01_ingest_bronze.py",
    )

    refine_silver = BashOperator(
        task_id="02_refine_silver",
        bash_command="python /opt/airflow/src/02_refine_silver.py",
    )

    serve_gold = BashOperator(
        task_id="03_serve_gold",
        bash_command="python /opt/airflow/src/03_serve_gold.py",
    )

    ingest_bronze >> refine_silver >> serve_gold