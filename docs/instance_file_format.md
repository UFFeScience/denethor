# Formato de arquivos de instância

Arquivos de instância descrevem um **problema de escalonamento de workflow** para fins de modelagem e otimização. Cada instância define um DAG de tarefas (workflow), os dados trocados entre elas, as VMs disponíveis e os custos associados.

Instâncias sintéticas usadas para modelagem e teste do escalonador estão descritas em [synthetic_instances.md](synthetic_instances.md) e são geradas em `src/instance_modeling/synthetic/generate_synthetic_instances.py`.

Instâncias reais são geradas pelos SQLs em `scripts/sql/instance_generator/` a partir de execuções registradas no banco de dados do Denethor

---

## Convenções gerais

- Colunas separadas por **tabulação** (`\t`)
- Linhas iniciadas por `#` são **cabeçalhos de seção** (não são comentários)
- Valores de lista usam a notação `[id1,id2,...]`
- `None` indica valor ausente (ex.: `write_time_avg` de arquivo estático)
- Todas as **unidades de tempo são em segundos**, tamanhos em **bytes**, custo em **USD/segundo**

---

## Nomenclatura dos arquivos

Instâncias Sintéticas seguem o padrão de nome:

```text
Synthetic_<instance_id>_T<#tasks>_D<#data>_C<#configs>.txt
```

Instâncias reais seguem o padrão:

```text
I<instance_id>_T<#tasks>_C<#configs>_D<#data>_VM<#vms>__fx_weids[<weids_fx>]__vm_weids[<weids_vm>].txt
```

| Parte | Significado |
| --- | --- |
| `<instance_id>` | Identificador numérico da instância |
| `T<n>` | Número de tarefas |
| `C<n>` | Número de configurações de FX (configs) |
| `D<n>` | Número de arquivos/dados |
| `VM<n>` | Número de tipos de VM disponíveis |
| `fx_weids[...]` | IDs de execução única de FX |
| `vm_weids[...]` | IDs de execução única de VM |

---

## Seções do arquivo

### Seção 1 — Cabeçalho (header)

```text
#<#tasks> <#config> <#data> <#vms> <#buckets> <#bucket_ranges> <max_running_time> <max_financial_cost>
```

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `#tasks` | int | Número total de tarefas distintas no workflow |
| `#config` | int | Número de configurações de funções serverless (ex.: Lambda 128MB, 256MB…) |
| `#data` | int | Número de arquivos/dados distintos referenciados |
| `#vms` | int | Número de tipos de VM disponíveis |
| `#buckets` | int | Número de buckets S3 utilizados |
| `#bucket_ranges` | int | Número de faixas de precificação do bucket |
| `max_running_time` | float (s) | Restrição de tempo máximo do workflow |
| `max_financial_cost` | float (USD) | Restrição de custo financeiro máximo |

**Como `max_running_time` é calculado:**

- Para execuções **FX** (Lambda): soma dos tempos de duração observados na configuração mais lenta (maior `task_time_duration` na matriz de configs)
- Para execuções **VM** (EC2): duração da execução na VM base + soma de `read_time` e `write_time` de todos os arquivos (transferência precisa ser contabilizada separadamente)
- O valor final é o **máximo** entre os dois grupos, representando o pior cenário possível (todas as tarefas em FX ou todas em VM)

**Como `max_financial_cost` é calculado:**

O  modelo de custo do AWS Lambda é baseado em GB-segundo, com um custo fixo por invocação. O custo total de uma tarefa é a soma do custo de computação (GB-segundos) e do custo por invocação:

```text
custo = duration(s) × memory(GB) × 0.0009765625 × 0.0000166667 + 0.0000002
```

O custo da execução em VM é calculado multiplicando o tempo total de execução (incluindo transferências) pelo custo por segundo da VM:

```text
custo = total_execution_time(s) × vm_cost_per_second
``` 

O valor final de `max_financial_cost` é o **máximo** entre o custo total estimado para todas as tarefas em FX e o custo total estimado para todas as tarefas em VM, considerando a aplicação do slowdown no tempo de CPU para as VMs mais rápidas.

Observação: `max_financial_cost` é uma estimativa conservadora, pois assume o pior cenário (todas as tarefas em FX ou todas em VM) e não leva em conta otimizações ou combinações de estratégias e nem execuções em paralelo entre VMs ou funções serverless. O objetivo é fornecer um limite superior para o custo total do workflow, para que 

---

### Seção 2 — Tasks (DAG do workflow)

**Gerado por:** `02_task.sql`

```text
#<task_id> <activity_id> <task_type__0-VM__1-VM_FX> <vm_cpu_time> <n_input> [<id_input>...] <n_output> [<id_output>...]
```

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `task_id` | int | Identificador único da tarefa |
| `activity_id` | int | Tipo de atividade (ex.: 1=tree, 2=subtree, 3=maf_db_creator, 4=maf_db_aggregator) |
| `task_type` | int | `0` = VM; `1` = FX |
| `vm_cpu_time` | float (s) | Tempo de CPU puro, medido em execuções **EC2** (VM base, slowdown=1.0) |
| `n_input` | int | Número de dados de entrada |
| `[id_input...]` | list | IDs dos dados consumidos pela tarefa |
| `n_output` | int | Número de dados de saída |
| `[id_output...]` | list | IDs dos dados produzidos pela tarefa |

**`task_type` detalhe:**

- `task_type=1` (FX): tarefa com ambiente fixo (Lambda); o tempo real já está na seção `configs` por `conf_id`
- `task_type=0` (VM): tarefa em VM genérica; o tempo estimado para outras VMs é `vm_cpu_time × cpu_slowdown` da VM em questão

Os `input_ids` e `output_ids` definem as **arestas do DAG** — um dado de saída de uma tarefa que é entrada de outra representa uma dependência.

---

### Seção 3 — Data (arquivos do workflow)

**Gerado por:** `03_data.sql`

```text
#<data_id> <data_size_bytes> <read_time_avg> <write_time_avg> <is_static> <n_source_devices> [<device_id>...]
```

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `data_id` | int | Identificador único do dado/arquivo |
| `data_size_bytes` | int | Tamanho médio do arquivo em bytes |
| `read_time_avg` | float (s) \| None | Tempo médio de leitura (download S3). `None` se nunca lido como consumido |
| `write_time_avg` | float (s) \| None | Tempo médio de escrita (upload S3). `None` se arquivo estático |
| `is_static` | int | `1` = estático (dado de entrada pré-existente no bucket); `0` = dinâmico (gerado em execução) |
| `n_source_devices` | int | `1` se estático (origem: bucket); `0` se dinâmico |
| `[device_id...]` | list | Dispositivo onde o dado reside (sempre `[denethor_bucket]`) |

**Regra de derivação `is_static`:**

- Arquivo apenas **consumido** (não aparece como produzido por nenhuma task) → `is_static=1`
- Arquivo **produzido** por alguma task (pode também ser consumido por outra) → `is_static=0`

---

### Seção 4 — VM Info

**Gerado por:** `04_vm_info.sql`

```text
#<vm_id> <cpu_slowdown> <cost_per_second> <storage_bytes> <bandwidth_mbps>
```

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `vm_id` | int | Identificador da VM |
| `cpu_slowdown` | float | Fator de lentidão em relação à VM base (`1.0`); ex.: `0.25` = 4× mais lenta que a base |
| `cost_per_second` | float (USD/s) | Custo por segundo de uso |
| `storage_bytes` | int | Capacidade de armazenamento em bytes |
| `bandwidth_mbps` | float | Largura de banda em Mbps |

A VM com `cpu_slowdown=1.0` é a **VM de referência** — é nela que `vm_cpu_time` (seção 2) foi medido.

---

### Seção 5 — Matriz Tempo × Custo (configs)

**Gerado por:** `05_time_cost_matrix.sql`

```text
#<task_id> <activity_id> <conf_id> <task_cost> <task_time_duration> <task_time_init> <task_time_cpu> <task_time_read> <task_time_write> <task_count>
```

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `task_id` | int | Referência à tarefa |
| `activity_id` | int | Referência à atividade |
| `conf_id` | int | Configuração de provider (ex.: Lambda 128MB=1, 256MB=2…) |
| `task_cost` | float (USD) | Custo médio observado para esta task nesta config |
| `task_time_duration` | float (s) | Tempo total médio de execução |
| `task_time_init` | float (s) | Tempo de inicialização (cold start do Lambda) |
| `task_time_cpu` | float (s) | Tempo de CPU puro (`duration - consumed_transfer - produced_transfer`) |
| `task_time_read` | float (s) | Tempo médio de leitura de arquivos de entrada (S3 download) |
| `task_time_write` | float (s) | Tempo médio de escrita de arquivos de saída (S3 upload) |
| `task_count` | int | Número de amostras (execuções) que originaram as médias |

**Relação entre tempos:**

```text
task_time_duration ≈ task_time_init + task_time_cpu + task_time_read + task_time_write
```

Para cada tarefa há uma linha por `conf_id`, formando a **matriz de decisão** do problema de escalonamento.

---

### Seção 6 — Bucket Ranges (precificação de armazenamento)

**Gerado por:** `06_bucket_ranges.sql`

```text
#<bucket_range_id> <size1_bytes> <size2_bytes> <cost_per_byte>
```

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `bucket_range_id` | int | Identificador da faixa |
| `size1_bytes` | int | Limite inferior da faixa (bytes) |
| `size2_bytes` | int | Limite superior da faixa (bytes) |
| `cost_per_byte` | float (USD/byte) | Custo por byte armazenado nesta faixa |

Replica a estrutura de preços em camadas do AWS S3. No banco é armazenado em GB (`cost_per_gb`), convertido para bytes pelo SQL.

---

## Pipeline de geração

```text
Banco de dados (execuções reais)
        │
        ├── we_values_fx  (execuções Lambda / VM_FX)
        │       ├── 01_totals.sql  → cabeçalho
        │       ├── 03_data.sql    → seção data
        │       └── 05_time_cost_matrix.sql → seção configs
        │
        ├── we_values_vm  (execuções EC2 / VM_base)
        │       └── 02_task.sql (vm_cpu_time) → seção tasks
        │
        ├── vm_configurations
        │       └── 04_vm_info.sql → seção VMs
        │
        └── bucket_ranges
                └── 06_bucket_ranges.sql → seção bucket ranges
```

---

## Leitura e validação

- Parser: `src/instance_modeling/instance_io.py` — classe `InstanceParser`, retorna `ParsedInstance`
- Validação: `src/instance_modeling/validate_instance_file.py` — verifica consistência entre contadores do cabeçalho e linhas de cada seção, referências de IDs entre seções, etc.
