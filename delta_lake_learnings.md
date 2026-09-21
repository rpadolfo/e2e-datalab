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
