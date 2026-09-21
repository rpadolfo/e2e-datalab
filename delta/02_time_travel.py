from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("Delta_Time_Travel") \
        .getOrCreate()

    # Vamos usar a mesma tabela gerenciada que criamos no script 01
    table_name = "workspace.default.delta_study_table"
    
    print("=== ESTUDO DE TIME-TRAVEL ===")
    print(f"Lendo a tabela '{table_name}'\n")

    print("1. Lendo a versão ATUAL da tabela (Versão 1 - com a Diana):")
    df_atual = spark.read.table(table_name)
    df_atual.show()

    print("\n2. Lendo a tabela como ela era na VERSÃO 0 (Antes do Append):")
    print("Repare que a Diana NÃO estará aqui.")
    # Usando a API nativa do PySpark passando a opção 'versionAsOf'
    df_v0 = spark.read.option("versionAsOf", 0).table(table_name)
    df_v0.show()

    print("\n3. Fazendo a mesma viagem no tempo usando SQL puro:")
    # No SQL, o comando é 'VERSION AS OF' ou 'TIMESTAMP AS OF'
    spark.sql(f"SELECT * FROM {table_name} VERSION AS OF 0").show()

    print("\n[Cenário Real do Dia a Dia]:")
    print("Se a sua pipeline (ex: Airflow) precisa reprocessar os dados de ontem")
    print("porque houve um bug, e a tabela atual já recebeu os dados de hoje,")
    print("você pode rodar a pipeline passando a Data de Execução do Airflow")
    print("direto na leitura do Spark:")
    print("Exemplo: spark.read.option('timestampAsOf', '2026-09-20 23:59:59').table(...)")

    spark.stop()

if __name__ == "__main__":
    main()
