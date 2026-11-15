import psycopg2
from psycopg2.extras import execute_values
from pyspark.sql import functions as F
from common.config import PG_CONFIG, get_spark

def run(): 
    spark = get_spark("03-serve-gold")

    df_silver = spark.read.format("delta").load("s3a://silver/pedidos_refined") # Carrega os dados refinados do nível Silver

    df_gold = (
        df_silver
        .groupBy("product")
        .agg(
            F.count("order_id").alias("total_pedidos"),
            F.sum("qtd").alias("unidades_vendidas"),
            F.sum("total_amount").alias("receita_total"),
        )
        .orderBy(F.desc("receita_total"))
    )

    df_gold.coalesce(1).write.format("delta").mode("overwrite").save("s3a://gold/pedidos_aggregated")
    print("Agregação concluída com sucesso! Dados salvos em s3a://gold/pedidos_aggregated")
    df_gold.show()

    # 2. Exporta para a camada de  serving no postreSQL 
    rows = [
        (r["product"], int(r["total_pedidos"]), int(r["unidades_vendidas"]), float(r["receita_total"]))
        for r in df_gold.collect()
    ]

    spark.stop() 

    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fato_vendas_produto (
            product VARCHAR(150) PRIMARY KEY,
            total_pedidos INT,
            unidades_vendidas INT,
            receita_total DECIMAL(12, 2)    ,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    execute_values(
        cur, 
        """
        INSERT INTO fato_vendas_produto (product, total_pedidos, unidades_vendidas, receita_total)
        VALUES %s 
        ON CONFLICT (product) DO UPDATE SET
            total_pedidos = EXCLUDED.total_pedidos,
            unidades_vendidas = EXCLUDED.unidades_vendidas,
            receita_total = EXCLUDED.receita_total,
            updated_at = NOW();
        """,
        rows
    )
    conn.commit()
    cur.close()
    conn.close()
    print("Serving layer atualiza no postgreSQL (tabela fato_vendas_produto) com  sucesso!") 

if __name__ == "__main__": 
    run() 
