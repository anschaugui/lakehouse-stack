from pyspark.sql import functions as F 
from common.config import get_spark  


def run(): 
    spark = get_spark("02-refine-silver") 

    df_bronze = spark.read.format("delta").load("s3a://bronze/pedidos_raw")

    df_silver = (
        df_bronze
        .dropDuplicates(["order_id"]) # Remove duplicatas com base na coluna order_id
        .filter(F.col("status") == "PAGO") # Filtra apenas os pedidos com status "PAGO"
        .withColumn("order_date", F.to_date("order_date", "yyyy-MM-dd")) # Converte a coluna order_date para o tipo Date
        .withColumn("qtd", F.col("qtd").cast("int")) # Converte a coluna qtd para o tipo Integer
        .withColumn("unit_price", F.col("unit_price").cast("decimal(10,2)"))
        .withColumn("total_amount", (F.col("qtd") * F.col("unit_price")).cast("decimal(10,2)"))
        .withColumn("_refined_at", F.current_timestamp())
    ) 

    df_silver.coalesce(1).write.format("delta").mode("overwrite").save("s3a://silver/pedidos_refined")
    print("Refinamento concluído com sucesso! Dados salvos em s3a://silver/pedidos_refined")
    spark.stop()


if __name__ == "__main__":
    run()