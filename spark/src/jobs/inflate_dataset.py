from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, rand, when, concat

def main():
    # Iniciando a sessão Spark local
    spark = SparkSession.builder \
        .appName("Lab: Inflate Dataset & Introduce Bad Practices") \
        .master("local[*]") \
        .getOrCreate()
        
    print("Spark Session iniciada.")

    # 1. Leitura do arquivo "semente" comprimido
    # Lembre-se: O docker mapeou './src' local para '/home/jovyan/work/src' no container
    seed_path = "/home/jovyan/work/src/telco_churn.csv.gz"
    
    print(f"Lendo dataset original de: {seed_path}")
    df_seed = spark.read.csv(seed_path, header=True, inferSchema=True)
    
    # 2. Multiplicação dos dados (Inflate)
    # Como o original tem ~7k linhas, multiplicando por 500 = ~3.5 milhões de linhas.
    # Isso já é volume suficiente para simularmos Skew e problemas de memória (já que limitamos o docker em 4GB).
    multiplier = 500
    df_multiplier = spark.range(multiplier).withColumnRenamed("id", "clone_id")
    
    # Cross Join vai multiplicar cada linha original por 500
    df_inflated = df_seed.crossJoin(df_multiplier)
    
    # Gerando um ID único temporário
    df_inflated = df_inflated.withColumn("new_customerID", concat(col("customerID"), lit("_"), col("clone_id")))
    
    # 3. Introdução de Data Skew (Desbalanceamento) Intencional
    # Vamos forçar que 80% das linhas tenham EXATAMENTE o mesmo customerID "SK-999999-SKEW".
    # Isso fará com que, ao fazermos um GroupBy ou Join nas próximas fases, 80% do processamento vá para uma única partição.
    skewed_id = "SK-999999-SKEW"
    df_skewed = df_inflated.withColumn(
        "skewed_customerID",
        when(rand() < 0.80, lit(skewed_id)).otherwise(col("new_customerID"))
    ).drop("customerID", "new_customerID", "clone_id") \
     .withColumnRenamed("skewed_customerID", "customerID")
    
    # 4. Escrevendo com a pior prática possível (Small Files Problem e formatação ruim)
    # Salvando como CSV texto puro e re-particionando agressivamente para 2000 arquivos pequenos.
    output_path = "/home/jovyan/work/data/landing/churn_data_skewed"
    
    print("Iniciando a gravação com Data Skew e Small Files Problem...")
    print("Aviso: Isso pode demorar e travar um pouco pois estamos forçando operações ineficientes intencionalmente!")
    
    # Reparticionando para 2000 garante que serão gerados 2000 arquivos CSV minúsculos na pasta de saída
    df_skewed.repartition(2000) \
             .write \
             .mode("overwrite") \
             .option("header", "true") \
             .csv(output_path)
             
    print(f"SUCESSO! Dataset caótico gerado em: {output_path}")
    spark.stop()

if __name__ == "__main__":
    main()
