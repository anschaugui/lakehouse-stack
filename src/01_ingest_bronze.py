from pyspark.sql import functions as F 
from config import get_spark 


def run(): 
    spark = get_spark("01-ingest-bronze")

    raw_data = [
        ("ORD-101", "2026-11-15", "Cabo USB-C 2m", 2, 45.90, "PAGO"),
        ("ORD-102", "2026-11-15", "Hub USB 3.0 4 Portas", 1, 89.00, "PAGO"),
        ("ORD-102", "2026-11-15", "Hub USB 3.0 4 Portas", 1, 89.00, "PAGO"),  # duplicado proposital
        ("ORD-103", "2026-11-15", "Suporte Articulado Monitor", 1, 199.90, "CANCELADO"),
        ("ORD-104", "2026-11-15", "Mousepad Desk Mat XL", 3, 65.00, "PAGO"),
    ]

    df_bronze = (
        spark.createDataFrame(
            raw_data,
            ["order_id", "order_date", "product", "qtd", "unit_price", "status"],
        )
        .withColumn("_ingested_at", F.current_timestamp())
    )

    df_bronze.coalesce(1).write.format("delta").mode("overwrite").save("s3a://bronze/pedidos_raw")
    print("Ingestão concluída com sucesso! Dados salvos em s3a://bronze/pedidos_raw")
    spark.stop()

if __name__ == "__main__":
    run()