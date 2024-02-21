# A arquitetura da solução:

## 1. **Arquivos JSON de configuração**
   - "workflow_model.json": define um modelo de workflow para a execução de funções AWS Lambda. As principais etapas do workflow são:
      - Transferência de arquivos entre as funções Lambda e o AWS S3.
      - Disparar a execução das funções Lambda.
      - Recuperar logs das funções Lambda.
      - Armazenar informações de execução no banco de dados.
   
   - "workflow_activities_model.json": define um modelo de atividades para a execução de funções AWS Lambda e as estatísticas que serão coletadas. As atividades são:
      - **tree_constructor**: cria árvores filogenéticas a partir de arquivos de entrada.
      - **tree_sub_find**: busca subárvores e identifica as que possuem com maior índice de similaridade.

## 2. **Funções Lambda**:
   - Utilizamos **duas funções Lambda** para processar dados provenientes de arquivos armazenados no **Amazon S3**.
   - Essas funções podem ser acionadas por eventos, como o upload de arquivos no S3 ou por resquest da "aplicação local de controle".
   - Cada função tem uma **responsabilidade específica**:
     - A função **tree_constructor** lê os arquivos de entrada e cria árvores filogenéticas usando o **ClustalW**.
     - A função **tree_sub_find** lê os arquivos de árvores gerados na função **tree_constructor**, gera arquivos de subárvores e busca as que possuem com maior índice de similaridade.

## 3. **Amazon S3**:
   - Os arquivos de entrada são carregados no S3, permitindo que a primeira função Lambda seja acionada.
   - Os arquivos intermediários e finais também são salvos no S3, em **Buckets** específicos.

## 4. **ClustalW**:
   - É uma ferramenta utilizada para alinhar sequências biológicas e criar árvores filogenéticas.
   - A função **tree_constructor** utiliza o ClustalW para gerar as árvores filogenéticas a partir dos dados de entrada.

## 5. **Logs e Estatísticas**:
   - Durante cada etapa do processo, são gerados logs de estatísticas, com as seguintes informações:
     - Tempo de início e fim de cada processo.
     - Nome, local e tamanho de cada arquivo consumido e/ou produzido.
     - Número e tamanho dos arquivos consumidos e/ou produzidos.
     - Tempo de transferência dos arquivos de/para o S3.
     - Duração real, duração "cobrada", tempo de inicialização, memória utilizada de cada execução da função Lambda.

## 6. **Amazon CloudWatch**:
   - O CloudWatch armazena e dá acesso aos logs gerados pelas funções Lambda.
   - A "aplicação local de controle" acessa esses logs via API específica.

## 7. **Banco de Dados PostgreSQL no Amazon RDS**:
   - Os logs das funções Lambda são acessados através do CloudWatch, interpretados e agregados pela "aplicação local de controle"
   - Os logs tratados são armazenados no banco de dados **PostgreSQL** hospedado no **Amazon RDS**.
   - O RDS gerencia a infraestrutura do banco de dados, incluindo escalabilidade, backups e alta disponibilidade.

## 8. **Aplicação Local de Controle**:
   - É uma aplicação local responsável por controlar a execução das funções Lambda e acessar os logs e estatísticas.


## **Possíveis pontos para melhorar**:
- Como as funções Lambda são **serverless**, a arquitetura pode ser facilmente escalada para lidar com mais dados ou mais funções.
- Especificar as **políticas de segurança**, grupos perfis, chaves de acesso necessários para que o S3, Lambda, CloudWatch, RDS e aplicação local se comuniquem
- Verificar como está **política de backup** do banco
- Versionamento das funções lambda?
- **Monitorar** as execuções das funções, acessos ao S3, RDS, etc..
- **Tratamento de erros**... A aplicação local deve tentar alguma espécie de reprocessamento dos dados?