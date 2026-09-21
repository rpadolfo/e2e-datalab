# Aprendizados: Delta Lake & Delta Tables

> **Nota de Contexto do Profissional:**
> Este documento centraliza o aprendizado e as melhores práticas focadas especificamente na camada de armazenamento utilizando o Delta Lake. Ele complementa os conceitos de processamento distribuído (Spark) e de governança (MLOps/Unity Catalog), mergulhando nas características de transações ACID e otimização de arquivos na nuvem.

## 1. Transações ACID no Data Lake
- **O Problema:** Em um Data Lake tradicional (arquivos Parquet no S3), se um job falhar no meio da gravação, você fica com arquivos corrompidos ou parciais. Múltiplos leitores podem ler dados pela metade.
- **A Solução (Delta):** O Delta Lake adiciona um Transaction Log (`_delta_log`). Ele garante que as operações de gravação e leitura sigam propriedades ACID (Atomicidade, Consistência, Isolamento e Durabilidade). Ou os dados são totalmente gravados com sucesso, ou a transação falha sem afetar o estado anterior.

## 2. Time-Travel e Versionamento
- **O Cenário:** É necessário auditar alterações passadas, reverter uma exclusão acidental ou garantir *Point-in-Time Correctness* para modelos de Machine Learning.
- **A Prática:** O Delta mantém o histórico das versões dos arquivos. Podemos consultar os dados exatamente como estavam ontem utilizando: `SELECT * FROM tabela TIMESTAMP AS OF '2026-09-20'`.

## 3. Otimização de Layout de Arquivos (OPTIMIZE e Z-Ordering)
- **O Desafio:** Com o tempo, a ingestão contínua gera muitos arquivos pequenos. Além disso, as consultas podem estar lendo o disco inteiro (Full Scan).
- **A Solução:** O comando `OPTIMIZE` resolve o problema dos arquivos pequenos agrupando-os de forma inteligente (Bin-packing). Já o `ZORDER BY (coluna)` organiza fisicamente os dados dentro dos arquivos para criar índices multidimensionais (Data Skipping), fazendo com que as consultas ignorem os arquivos irrelevantes em frações de segundos.

## 4. Retenção de Histórico e Limpeza (VACUUM)
- **O Risco:** Manter todas as versões antigas de dados para Time-Travel custa caro no S3, pois os arquivos de dados antigos (marcados como deletados/atualizados) não são removidos fisicamente por padrão.
- **A Prática:** Utilizamos o comando `VACUUM` periodicamente para limpar fisicamente arquivos que não são mais necessários (por padrão, arquivos com mais de 7 dias e que não estão na versão mais recente da tabela), equilibrando a janela de Time-Travel com o custo de Storage.

## 5. A Relação entre Parquet e Delta
- O Delta Lake não substitui o Parquet, ele o **abraça**. No PySpark, trocar `.format("parquet")` por `.format("delta")` faz com que o Spark continue salvando os dados brutos no formato colunar (Parquet), mas passe a orquestrar uma pasta oculta `_delta_log` com arquivos JSON, que conferem os "superpoderes" transacionais (ACID) aos arquivos físicos.

## 6. Leitura e Localização de Tabelas (Unity Catalog)
- **A Abordagem Moderna:** Se a tabela foi registrada no Unity Catalog, a leitura não requer mapeamento de caminhos físicos: `spark.read.table("catalog.schema.tabela")`.
- **A Rastreabilidade:** Para descobrir o caminho físico no S3/Storage associado à tabela, basta checar a aba "Details" no Catalog Explorer da interface gráfica ou rodar o comando SQL `DESCRIBE EXTENDED tabela`, que informará a `Location` (URL física) exata onde os Parquets estão.

## 7. Migração Legada: Transformando Parquet em Delta
- **Read/Write Tradicional:** Carregar os arquivos velhos (`spark.read.parquet`) e reescrevê-los formatados como Delta. Útil quando é necessário mover a pasta, higienizar dados ou mudar nomes de colunas.
- **In-Place Conversion (O Jeito Ninja):** O comando `CONVERT TO DELTA parquet.caminho` apenas insere o `_delta_log` na pasta existente de arquivos Parquet antigos, habilitando Time-Travel e ACID instantaneamente sem custo de computação para reescrita dos dados físicos.

## 8. Boas Práticas Operacionais: A Faxina (Vacuum & Optimize)
- A manutenção de tabelas (agrupamento de arquivos pequenos e limpeza de lixo histórico) não deve ser colocada no final dos scripts individuais de ETL para não comprometer a latência da esteira principal.
- **Predictive Optimization:** Em workspaces modernos com Unity Catalog, essa opção delega a manutenção 100% para a Inteligência Artificial do Databricks via computação Serverless.
- **Abordagem Centralizada:** Em arquiteturas tradicionais, a melhor prática é possuir um único Script de Manutenção agendado (ex: aos fins de semana de madrugada) que itera por todas as tabelas do catálogo executando `OPTIMIZE` e `VACUUM`.
