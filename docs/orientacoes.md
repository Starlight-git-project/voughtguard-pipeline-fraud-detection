# VoughtGuard - Pipeline de Detecção de Fraude Financeira

> Desafio técnico da trilha **[Starlight Git Project](https://github.com/orgs/Starlight-git-project/repositories)** aplicando as três camadas de boas práticas de Git e GitHub em um projeto de engenharia e Análise de dados.

---

## Contexto

A **VoughtGuard** é uma fintech de meios de pagamento digital (cartões, PIX e carteiras digitais) com mais de 2 milhões de transações processadas por mês.

O time de risco precisa de indicadores confiáveis para detectar movimentações suspeitas. Você foi contratada para o time de Engenharia e Análise de Dados e esta é sua primeira missão.

---

## Sua missão

Construir um pipeline de dados que:

- Processe transações financeiras brutas a partir de um arquivo CSV
- Aplique limpeza e validação de qualidade nos dados
- Gere tabelas analíticas para o time de risco
- Produza um relatório automatizado de Data Quality

---

## Dataset

Arquivo CSV com **10.000 transações financeiras sintéticas** simulando comportamento real de fraude.

Fonte: [Synthetic Financial Fraud Dataset - Kaggle](https://www.kaggle.com/datasets/umitka/synthetic-financial-fraud-dataset/data)

| Coluna | Descrição |
|--------|-----------|
| `transaction_id` | Identificador único da transação |
| `user_id` | Identificador do usuário |
| `amount` | Valor da transação (moeda local) |
| `transaction_type` | Tipo: `POS` · `Online` · `ATM` · `QR` |
| `merchant_category` | Categoria do estabelecimento |
| `country` | País onde ocorreu a transação |
| `hour` | Hora da transação (0–23) |
| `device_risk_score` | Score de risco do dispositivo |
| `ip_risk_score` | Score de risco do IP |
| `is_fraud` | `0` = legítima · `1` = fraude |

---

## Requisitos do pipeline

| Área | O que implementar |
|------|------------------|
| **Limpeza** | Tratar nulos, corrigir tipos, validar domínios categóricos, detectar outliers em `amount` |
| **Transformação** | Criar `period_of_day` a partir de `hour` e `combined_risk` como média entre os dois scores de risco |
| **Tabelas analíticas** | Ranking de países por taxa de fraude e top categorias de merchant por risco médio |
| **Data Quality** | Relatório com total de registros, registros com erro, percentual de conformidade e anomalias |

### Métricas mínimas do relatório de Data Quality

- Total de registros
- Registros com erro
- Percentual de conformidade
- Valores nulos por coluna
- Valores fora do domínio esperado
- Outliers em `amount`
- Inconsistências em `is_fraud`

---

## Entregáveis

| # | Entregável |
|---|-----------|
| 01 | Repositório público no GitHub com README claro |
| 02 | Pipeline funcional em Python - scripts organizados, tipados e com docstrings |
| 03 | Tabelas analíticas salvas em `data/processed/` (CSV ou Parquet) |
| 04 | Relatório de Data Quality gerado automaticamente |
| 05 | Testes automatizados com `pytest` - cobertura mínima das funções de limpeza e transformação |
| 06 | Proposta de orquestração documentada no README ou em `docs/orquestracao.md` |

---

## Estrutura esperada do repositório

```
voughtguard-pipeline-fraud-detection/
│
├── .env.example               # variáveis de ambiente (sem valores reais)
├── .gitignore                 # dados, credenciais e temporários ignorados
├── README.md                  # este arquivo
├── requirements.txt           # dependências do projeto
│
├── data/
│   ├── raw/                   # dataset original — não commitado
│   │   └── .gitkeep
│   └── processed/             # tabelas analíticas geradas
│       └── .gitkeep
│
├── src/
│   ├── config.py              # leitura de variáveis de ambiente
│   ├── pipeline.py            # orquestração principal
│   ├── limpeza.py             # funções de limpeza e validação
│   ├── transformacao.py       # criação de novas colunas
│   └── qualidade.py           # relatório de data quality
│
├── tests/
│   ├── fixtures/
│   │   └── transacoes_sample.csv
│   ├── test_limpeza.py
│   └── test_transformacao.py
│
├── notebooks/
│   └── exploracao.ipynb       # análise exploratória
│
└── docs/
    └── orquestracao.md        # proposta de orquestração
```

---

## Como começar

### 1. Faça fork deste repositório

```bash
# No GitHub: clique em Fork (canto superior direito)
```

### 2. Clone o seu fork

```bash
git clone https://github.com/SEU-USUARIO/voughtguard-pipeline-fraud-detection.git
cd voughtguard-pipeline-fraud-detection
```

### 3. Crie sua branch

```bash
git checkout -b feature/seu-nome
```

### 4. Configure o ambiente

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

pip install -r requirements.txt
cp .env.example .env
```

### 5. Baixe o dataset

Faça o download em: [Kaggle — Synthetic Financial Fraud Dataset](https://www.kaggle.com/datasets/umitka/synthetic-financial-fraud-dataset/data)  
Salve o arquivo em `data/raw/transactions.csv`

### 6. Execute o pipeline

```bash
python src/pipeline.py
```

### 7. Rode os testes

```bash
pytest tests/
```

---

## Critérios de avaliação

| Critério | O que será observado |
|----------|---------------------|
| **Organização do repositório** | Estrutura clara, arquivos no lugar certo, sem código solto na raiz |
| **Qualidade do código** | Funções tipadas, docstrings, sem duplicação desnecessária |
| **Clareza da documentação** | README que qualquer pessoa consegue seguir |
| **Cobertura de testes** | Funções principais cobertas com pytest |
| **Raciocínio sobre orquestração** | Justificativa clara da escolha da ferramenta |
| **Histórico de commits e branches** | Commits descritivos, uso correto de branches e PRs |

> O critério de commits e branches é parte da avaliação. Commits como `fix`, `wip` ou `arrumei` serão descontados.  
> Consulte a [trilha-01-fundamentos](https://github.com/Starlight-git-project/trilha-01-fundamentos) antes de começar.

---

## Entrega

Abra um **Pull Request** deste repositório com:

- Branch: `feature/seu-nome`
- Título: `[VoughtGuard] Seu Nome - Pipeline de Fraude`
- Descrição: o que você implementou, decisões tomadas e proposta de orquestração

---

## Sugestões de orquestração

Documente sua proposta em `docs/orquestracao.md`. Não é obrigatório implementar - mas a justificativa será avaliada.

- **GitHub Actions** - já presente no repositório, boa escolha para pipelines simples
- **Apache Airflow** - padrão de mercado para orquestração complexa -  Recomendado
- **Prefect** - mais simples que o Airflow, bom para quem está começando
- Alternativas em nuvem são bem-vindas

---

## Antes de começar

Se você ainda não tem familiaridade com Git e GitHub, comece por aqui:

→ **[Trilha 01 - Fundamentos](https://github.com/Starlight-git-project/trilha-01-fundamentos)**  
Commits semânticos, `.gitignore`, variáveis de ambiente e estrutura de projeto.

---

<div align="center">

⭐ [Starlight Git Project](https://github.com/Starlight-git-project) · open source · feito para profissionais de dados

</div>
