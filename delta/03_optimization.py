from pyspark.sql import SparkSession
import random

def main():
    spark = SparkSession.builder \
        .appName("Delta_Optimization_ZOrdering") \
        .getOrCreate()

    table_name = "workspace.default.delta_study_table_optimization"
    
    print("=== ESTUDO DE OTIMIZAÇÃO (OPTIMIZE & Z-ORDER) ===")
    
    print("1. Simulando Ingestão de 'Small Files' (Arquivos Pequenos)...")
    # Vamos rodar 10 appends minúsculos, cada um gerando um novo arquivo físico Parquet
    for i in range(10):
        # Gera dados fictícios: id sequencial, departamento aleatório, salário aleatório
        dept = random.choice(["Vendas", "Engenharia", "RH", "Financeiro", "Marketing"])
        data = [(i, f"Funcionario_{i}", dept, float(random.randint(3000, 15000)))]
        df = spark.createDataFrame(data, ["id", "nome", "departamento", "salario"])
        
        # Faz o append (isso intencionalmente cria fragmentação no storage)
        df.write.format("delta").mode("append").saveAsTable(table_name)
    
    print("-> Foram feitos 10 Appends! Provavelmente temos 10 arquivos minúsculos no backend.")
    print("Isso é um pesadelo para a performance de leitura do Spark (I/O e latência de rede).")

    print("\n2. Executando o OPTIMIZE e Z-ORDER...")
    # O OPTIMIZE agrupa os 10 arquivos pequenos em arquivos maiores de até 1GB (Bin-packing).
    # O ZORDER BY (departamento) cria um índice multidimensional físico.
    # Quando fizermos uma busca "WHERE departamento = 'Vendas'", o Spark pulará a leitura
    # dos arquivos que não contêm Vendas (Data Skipping), lendo o dado em milissegundos.
    
    optimize_sql = f"OPTIMIZE {table_name} ZORDER BY (departamento)"
    print(f"Executando: {optimize_sql}")
    spark.sql(optimize_sql).show(truncate=False)

    print("\n3. Verificando as Métricas do Optimize na Tabela de Histórico:")
    # Aqui veremos a transação do Optimize registrando quantos arquivos foram deletados e quantos novos foram criados
    spark.sql(f"DESCRIBE HISTORY {table_name}").select("version", "operation", "operationMetrics").show(3, truncate=False)

    print("\n[Estudo de Bastidores]:")
    print("Quando o OPTIMIZE roda, ele cria um arquivo Parquet NOVO e compacto.")
    print("Os 10 arquivos minúsculos originais NÃO são apagados imediatamente do S3/Blob,")
    print("eles são marcados como 'tombstone' (deletados logicamente). Isso garante")
    print("que o Time-Travel continue funcionando se precisarmos acessar os dados velhos.")
    print("\nPara apagar fisicamente o lixo velho e economizar dinheiro na nuvem, usamos:")
    print(f"VACUUM {table_name} RETAIN 168 HOURS") # 168 horas = 7 dias (Padrão)

    spark.stop()

if __name__ == "__main__":
    main()
