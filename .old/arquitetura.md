# A arquitetura da solução:

## 1. **Arquivos JSON de configuração**
   - "workflow_model.json": define um modelo de workflow para a execução de funções AWS Lambda. As principais etapas do workflow são:
      - Transferência de arquivos entre as funções Lambda e o AWS S3.
      - Disparar a execução das funções Lambda.
      - Recuperar logs das funções Lambda.
      - Armazenar informações de execução no banco de dados.
   
   - "tree_operations_model.json": define um modelo de atividades para a execução de funções AWS Lambda e as estatísticas que serão coletadas. As atividades são:
      - **tree_constructor**: cria árvores filogenéticas a partir de arquivos de entrada.
      - **subtree_mining**: busca subárvores e identifica as que possuem com maior índice de similaridade.

## 2. **Funções Lambda**:
   - Utilizamos **duas funções Lambda** para processar dados provenientes de arquivos armazenados no **Amazon S3**.
   - Essas funções podem ser acionadas por eventos, como o upload de arquivos no S3 ou por resquest da "aplicação local de controle".
   - Cada função tem uma **responsabilidade específica**:
     - A função **tree_constructor** lê os arquivos de entrada e cria árvores filogenéticas usando o **ClustalW**.
     - A função **subtree_mining** lê os arquivos de árvores gerados na função **tree_constructor**, gera arquivos de subárvores e busca as que possuem com maior índice de similaridade.

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


"CloudWatch é um serviço de monitoramento e observabilidade oferecido pela Amazon Web Services (AWS). Ele permite que você colete e acompanhe métricas, registre arquivos de log e crie alarmes para monitorar o desempenho e a saúde dos recursos da AWS, como instâncias do Amazon EC2, bancos de dados do Amazon RDS, serviços do AWS Lambda, entre outros.

Com o CloudWatch, você pode coletar métricas em tempo real sobre o uso de recursos, como CPU, memória, armazenamento e tráfego de rede. Essas métricas podem ser visualizadas em gráficos e painéis personalizados, permitindo que você monitore o desempenho dos seus recursos e identifique possíveis problemas.

Além disso, o CloudWatch permite que você registre arquivos de log gerados por seus aplicativos e serviços. Esses logs podem ser armazenados e analisados para ajudar na depuração de problemas, no monitoramento de eventos e no cumprimento de requisitos de conformidade.

Você também pode criar alarmes no CloudWatch para ser notificado quando uma métrica ultrapassar um limite definido. Por exemplo, você pode configurar um alarme para ser acionado quando a utilização da CPU de uma instância do EC2 atingir um determinado valor. Isso permite que você tome medidas proativas para resolver problemas antes que eles afetem a disponibilidade ou o desempenho dos seus recursos.

Em resumo, o CloudWatch é uma ferramenta essencial para monitorar e gerenciar recursos da AWS, fornecendo insights valiosos sobre o desempenho e a saúde dos seus sistemas."



## 7. **Banco de Dados Amazon RDS**:
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