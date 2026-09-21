from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def main():
    # Inicializando uma sessão local do Spark configurada para usar o Delta Lake
    spark = SparkSession.builder \
        .appName("Delta_ACID_Transactions") \
        .getOrCreate()

    # Caminho no disco local do cluster (já que o DBFS público está desabilitado por segurança)
    delta_path = "file:/tmp/delta_study_table"

    print("1. Criando a tabela inicial...")
    # Criamos um DataFrame simples
    data = [
        (1, "Alice", 1000.0),
        (2, "Bob", 1500.0),
        (3, "Charlie", 2000.0)
    ]
    df = spark.createDataFrame(data, ["id", "nome", "saldo"])
    
    # Gravando no formato Delta
    # Repare que no fundo isso cria arquivos Parquet + um diretório _delta_log
    df.write.format("delta").mode("overwrite").save(delta_path)
    print("-> Tabela Delta criada com sucesso!")

    print("\n2. Simulando uma transação ACID (Append)...")
    # Adicionando um novo registro
    new_data = [(4, "Diana", 2500.0)]
    new_df = spark.createDataFrame(new_data, ["id", "nome", "saldo"])
    
    # Fazendo o append. Se a gravação falhasse no meio, o _delta_log 
    # não receberia o commit e para quem lê, a tabela estaria intacta.
    new_df.write.format("delta").mode("append").save(delta_path)
    print("-> Novo registro adicionado!")

    print("\n3. Lendo a tabela atualizada...")
    # Lendo para provar que a transação funcionou
    read_df = spark.read.format("delta").load(delta_path)
    read_df.show()

    print("\n[Estudo de Bastidores]:")
    print("Se você olhar a pasta '{}' no seu sistema de arquivos,".format(delta_path))
    print("verá os arquivos Parquet com os dados e a pasta '_delta_log'.")
    print("Dentro do '_delta_log' haverá arquivos JSON (00000.json, 00001.json).")
    print("Eles são o coração das transações ACID, mapeando quais arquivos Parquet")
    print("pertencem a qual versão da tabela.")

    spark.stop()

if __name__ == "__main__":
    main()
