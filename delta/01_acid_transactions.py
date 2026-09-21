from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def main():
    # Inicializando uma sessão local do Spark configurada para usar o Delta Lake
    spark = SparkSession.builder \
        .appName("Delta_ACID_Transactions") \
        .getOrCreate()

    # Nome da tabela gerenciada no Unity Catalog (assumindo catalog 'workspace' e schema 'default')
    table_name = "workspace.default.delta_study_table"

    print("1. Criando a tabela inicial...")
    # Criamos um DataFrame simples
    data = [
        (1, "Alice", 1000.0),
        (2, "Bob", 1500.0),
        (3, "Charlie", 2000.0)
    ]
    df = spark.createDataFrame(data, ["id", "nome", "saldo"])
    
    # Gravando no formato Delta como Tabela Gerenciada
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)
    print("-> Tabela Delta criada com sucesso no Unity Catalog!")

    print("\n2. Simulando uma transação ACID (Append)...")
    # Adicionando um novo registro
    new_data = [(4, "Diana", 2500.0)]
    new_df = spark.createDataFrame(new_data, ["id", "nome", "saldo"])
    
    # Fazendo o append.
    new_df.write.format("delta").mode("append").saveAsTable(table_name)
    print("-> Novo registro adicionado!")

    print("\n3. Lendo a tabela atualizada...")
    # Lendo para provar que a transação funcionou
    read_df = spark.read.table(table_name)
    read_df.show()

    print("\n[Estudo de Bastidores]:")
    print("Como estamos em um cluster com Unity Catalog (Shared Mode), o acesso")
    print("ao sistema de arquivos bruto é bloqueado por segurança.")
    print("Para vermos o equivalente ao '_delta_log' e o histórico de transações,")
    print("podemos rodar um comando SQL no notebook logo abaixo:")
    print(f"display(spark.sql('DESCRIBE HISTORY {table_name}'))")

    spark.stop()

if __name__ == "__main__":
    main()
