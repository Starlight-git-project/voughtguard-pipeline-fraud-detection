# Proposta de Orquestração — VoughtGuard

## Ferramenta escolhida: Apache Airflow

## Justificativa

O desafio sugere três alternativas - GitHub Actions, Apache Airflow e
Prefect. Optamos pelo **Apache Airflow**, mesmo reconhecendo que, para
o tamanho atual do pipeline, ele é uma escolha mais robusta do que
estritamente necessária. A justificativa considera os quatro critérios
pedidos:

### Complexidade do pipeline

O pipeline do VoughtGuard hoje é linear e simples: leitura do CSV →
limpeza → transformação → tabelas analíticas → relatório de qualidade.
Uma ferramenta como o GitHub Actions já resolveria esse fluxo sem
dificuldade. Escolhemos o Airflow pensando no **crescimento esperado**
do projeto: o desafio já prevê mais tabelas analíticas, mais fontes de
dados e relatórios adicionais no futuro. O Airflow trata cada etapa
como uma **tarefa independente**, com dependências explícitas entre
elas, o que facilita adicionar, remover ou re-executar etapas
isoladamente conforme o pipeline crescer - algo que o GitHub Actions,
por tratar a execução como uma "caixa preta única", não oferece com a
mesma **granularidade**.

### Curva de aprendizado

Esse é o ponto onde o Airflow **perde** para as outras opções, e vale
ser transparente sobre isso: exige entender conceitos próprios (DAG,
Operator, Scheduler, Executor, Worker) e escrever as tarefas em Python
usando a API do Airflow. Comparado ao GitHub Actions (um arquivo YAML
simples) ou ao Prefect (mais próximo de Python puro), o Airflow tem a
curva mais íngreme das três opções. Assumimos esse custo de aprendizado
porque o Airflow é o **padrão de mercado** para orquestração de dados,
e dominá-lo tem valor direto para quem se especializa em Engenharia de
Dados.

### Custo

Localmente, o Airflow é gratuito (open source). Em produção, exige
infraestrutura própria para rodar o scheduler, o webserver e o banco de
metadados, seja em um servidor próprio, seja em um serviço gerenciado
(ex: Astronomer, Google Cloud Composer, MWAA da AWS), que têm custo.
Isso é mais caro e mais trabalhoso de manter do que o GitHub Actions
(gratuito, dentro do limite generoso do GitHub para repositórios
públicos) ou o Prefect Cloud (camada gratuita disponível).

### Integração com o repositório

O Airflow não tem integração nativa com o GitHub como o GitHub Actions
tem , é preciso configurar o Airflow para observar o repositório (via
webhook, ou rodando com acesso ao código clonado). Isso adiciona uma
peça de infraestrutura a mais fora do GitHub, diferente do GitHub
Actions, que já vem embutido no repositório sem nenhuma configuração
externa.

### Resumo da escolha

| Critério | GitHub Actions | Airflow (escolhido) |
|---|---|---|
| Complexidade do pipeline atual | Suficiente | Mais do que o necessário hoje |
| Curva de aprendizado | Baixa | Alta |
| Custo | Gratuito | Gratuito localmente, pago em produção |
| Integração com o repositório | Nativa | Requer configuração externa |
| Preparo para crescimento futuro | Limitado | Alto |

Escolhemos o Airflow priorizando o critério de **preparo para
crescimento** e o valor de aprendizado da ferramenta padrão de mercado,
mesmo pagando o preço de uma curva de aprendizado mais alta e de uma
integração menos direta com o GitHub.

---

## Nível de orquestração

É importante deixar claro o papel do Airflow: ele orquestra o
**disparo, a sequência e o monitoramento** de cada etapa do pipeline
como tarefas (*tasks*) independentes dentro de uma DAG (*Directed
Acyclic Graph* - grafo de tarefas com dependências definidas, sem
ciclos). Cada etapa do pipeline (limpeza, transformação, tabelas
analíticas, relatório de qualidade) se torna uma tarefa visível e
monitorável individualmente, com possibilidade de re-executar só a
etapa que falhar, sem precisar rodar o pipeline inteiro de novo.

---

## Fluxo de execução

### Gatilho (trigger)

A DAG é agendada para rodar **diariamente**, simulando uma ingestão
periódica de novas transações da VoughtGuard. Também pode ser disparada
manualmente pela interface do Airflow, para fins de teste.

### Ordem das tarefas

```
                    ┌─────────────────────┐
                    │  extrair_dados       │
                    │  (lê data/raw/*.csv) │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  limpar_dados         │
                    │  (src/limpeza.py)     │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  transformar_dados    │
                    │  (src/transformacao.py)│
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                  │
   ┌──────────▼───────────┐          ┌──────────▼───────────┐
   │ gerar_tabelas_        │          │ gerar_relatorio_      │
   │ analiticas             │          │ qualidade              │
   │ (src/tabelas_          │          │ (src/qualidade.py)     │
   │ analiticas.py)          │          │                         │
   └──────────┬───────────┘          └──────────┬───────────┘
              │                                  │
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  salvar_resultados    │
                    │  (data/processed/*)   │
                    └──────────────────────┘
```

### Descrição de cada etapa

1. **`extrair_dados`** - lê o CSV bruto de `data/raw/`.
2. **`limpar_dados`** - aplica `remover_nulos_criticos`, `corrigir_tipos`,
   `validar_dominios` e `detectar_outliers_amount` (issue #2).
3. **`transformar_dados`** - aplica `criar_combined_risk` e
   `criar_period_of_day` (issue #4). Depende da etapa de limpeza estar
   concluída.
4. **`gerar_tabelas_analiticas`** e **`gerar_relatorio_qualidade`** -
   rodam **em paralelo**, já que uma não depende do resultado da outra,
   apenas dos dados já transformados (issues #5 e #3).
5. **`salvar_resultados`** - só é disparada depois que **as duas**
   tarefas anteriores terminarem, e persiste tudo em `data/processed/`.

### Pseudocódigo da DAG (Airflow)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG(
    dag_id="voughtguard_pipeline",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    extrair = PythonOperator(task_id="extrair_dados", python_callable=extrair_dados)
    limpar = PythonOperator(task_id="limpar_dados", python_callable=limpar_dados)
    transformar = PythonOperator(task_id="transformar_dados", python_callable=transformar_dados)
    tabelas = PythonOperator(task_id="gerar_tabelas_analiticas", python_callable=gerar_tabelas)
    qualidade = PythonOperator(task_id="gerar_relatorio_qualidade", python_callable=gerar_relatorio)
    salvar = PythonOperator(task_id="salvar_resultados", python_callable=salvar_resultados)

    extrair >> limpar >> transformar >> [tabelas, qualidade] >> salvar
```

A última linha (`>>`) define visualmente as dependências: `extrair`
roda primeiro, depois `limpar`, depois `transformar`; a partir daí,
`tabelas` e `qualidade` rodam em paralelo (por isso estão entre
colchetes); e `salvar` só roda depois que **ambas** terminarem.

---

## Status

Esta é uma proposta documentada, conforme pedido pela issue #6 - a
implementação da DAG real depende da conclusão da issue #9
(`pipeline.py`), que integra todos os módulos numa função executável
única. Fica como próximo passo natural do projeto, fora do escopo desta
issue.