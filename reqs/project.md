# predicao de abertura de reclamacoes
a ideia e simular toda a arquitetura onde sao prepados dados de ligacoes de clientes que passam por todo ciclo de ML, feature engineering, feature storage, analise das metricas, analise de data drift (KS e PSI), ativacao de gatilho caso o threshold nao seja satisfatorio (use qualquer valor definiremos um mais realista depois), ativacao de re-treino.

Usaremos um dataset que esteja disponivel publicamente e que condiza mais ou menos com o cenario descrito, pode ser do kaggle ou alguma outra fonte. se for o caso vamos multiplicar o dataset para termos volume de dados. vou deixar vc propor algo e se eu aprovar atualizamos esse requisito.

Vamos simular problemas de OOM, entre outros que ocorrem no dia a dia nesse tipo de projeto e resolver. Os scripts serao escritos em pyspark e vamos trabalhar otimizacoes para a linguagem vombinado com configuracoes no proprio databricks e snowflake.
