# Aprendizados MLOps: Databricks, Unity Catalog e Feature Store

Este documento consolida as principais decisões arquiteturais, conceitos e implementações técnicas realizadas durante o laboratório de Engenharia de Machine Learning focado em Governança e Time-Travel.

## 1. Visão Arquitetural Corporativa
- **Databricks como Orquestrador, não como Infraestrutura Básica:** O Databricks atua na camada de computação processando dados que estão armazenados no S3 (Data Lake), substituindo o EMR/EC2 tradicional para reduzir a sobrecarga de DevOps (Zero Config) e acelerar o tempo de entrega com a engine Photon.
- **Governança Unificada (Unity Catalog):** O Unity Catalog serve como a fonte da verdade para Dados, Modelos de ML e Funções. Tudo é rastreado no mesmo nível de permissão e linhagem (Lineage).
- **Terraform:** Toda a infraestrutura de dados (`schemas`) deve ser provisionada via Terraform (Infra as Code) para garantir versionamento, auditoria e evitar que Cientistas de Dados criem lixo no ambiente produtivo.

## 2. Feature Store vs Data Marts
- A **Feature Store** é a evolução dos Data Marts, construída para o consumo de Máquinas (Algoritmos) e não de Humanos (BI).
- **Centralização de Domínios:** Features não são construídas "para um modelo", elas são construídas por "Domínio de Negócio" (ex: `billing_features`, `call_center_features`).
- **Feature Reuse e Lineage:** Múltiplos modelos podem consumir a mesma feature. O Unity Catalog mapeia as relações Upstream/Downstream automaticamente, garantindo que o Engenheiro de Dados saiba exatamente quais modelos de IA dependem daquela tabela antes de fazer uma alteração estrutural.
- **Point-in-Time Correctness (Time-Travel):** Diferente do SQL clássico (SCD Tipo 2 com `start_date` e `end_date`), a Feature Store faz um "AS OF JOIN" utilizando chaves primárias e *Timestamp Keys* para buscar a "foto exata" do cliente milissegundos antes do evento, erradicando o risco de *Data Leakage* (vazar o futuro para o modelo).

## 3. Desempenho vs Governança (Monitoramento de Modelos)
- **Métrica KS (Kolmogorov-Smirnov):** Mede a capacidade do modelo de discriminar entre as duas classes (Bons x Maus). O KS foca puramente no Desempenho do Modelo e é calculado/logado durante a fase de Treinamento no MLflow.
- **Métrica PSI (Population Stability Index):** Mede o *Data Drift* (Mudança na estabilidade da população). Compara a distribuição de dados do dia do Treino contra o dia da Inferência.
- O PSI deve ser governado continuamente pela arquitetura através de recursos como o **Databricks Lakehouse Monitoring**. Se o PSI violar o limiar crítico (PSI > 0.20), isso aciona alertas e dispara o retreino automático da esteira de MLOps.

## 4. Nuances e "Gotchas" Técnicos (Trincheiras)
1. **Delta Lake e Metadata Mismatch:** Alterar o agrupamento e a estrutura das chaves primárias de uma tabela Delta gera bloqueio do motor por incompatibilidade de Metadata. Deve-se usar `.option("overwriteSchema", "true")` na escrita para forçar o recálculo do esquema.
2. **MLflow e Unity Catalog (Signatures):** O Unity Catalog é rigoroso com o registro de modelos. Você não pode jogar um modelo lá dentro sem declarar o "contrato de dados". É mandatório usar a função `infer_signature` do MLflow para mapear os tipos de entrada e saída antes de submeter via `registered_model_name`.
3. **Namespacing Universal:** Ao salvar Modelos no Unity Catalog, eles exigem nomenclatura de 3 níveis idêntica às tabelas SQL: `catalog.schema.model_name` (Ex: `workspace.bacen_mlops.BacenRiskXGBoost`). Modelos salvos sem esse prefixo caem na pasta "Models" legada do Workspace.
4. **Funções SQL Geradas Automaticamente:** Um modelo corretamente registrado no Unity Catalog com a sua Assinatura (Signature) automaticamente ganha uma User Defined Function (UDF) equivalente em SQL. Analistas de negócios podem usar o modelo chamando `SELECT modelo(colunas) FROM tabela`.
5. **Indentações PySpark no Top-Level:** Ao manipular a criação de dataframes com quebra de linhas no Jupyter Notebook (via script), códigos na raiz da célula não devem possuir nenhum espaço de indentação para evitar `IndentationError`.
