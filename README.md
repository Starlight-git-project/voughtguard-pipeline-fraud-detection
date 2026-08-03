# VoughtGuard - Pipeline de Detecção de Fraude Financeira

Pipeline de dados para processar transações financeiras, aplicar limpeza e
validação de qualidade, gerar tabelas analíticas para o time de risco e
produzir um relatório automatizado de Data Quality.

## Estrutura do repositório

```
voughtguard-pipeline-fraud-detection/
├── .env.example          # variáveis de ambiente (sem valores reais)
├── .gitignore            # dados, credenciais e temporários ignorados
├── README.md             # este arquivo
├── requirements.txt      # dependências do projeto
├── Contributing.md       # guia de contribuição do time
│
├── data/
│   ├── raw/              # dataset original — não commitado
│   ├── staging/          # dados intermediários do pipeline — não commitado
│   └── processed/        # tabelas e relatórios gerados
│       ├── ranking_paises_fraude.csv
│       ├── top_merchant_risco.csv
│       └── relatorio_qualidade.csv
│
├── src/
│   ├── __init__.py
│   ├── config.py              # leitura de variáveis de ambiente
│   ├── pipeline.py            # orquestração principal
│   ├── limpeza.py             # funções de limpeza e validação
│   ├── transformacao.py       # criação de novas colunas
│   ├── qualidade.py           # relatório de data quality
│   └── tabelas_analiticas.py  # ranking de países e merchants
│
├── tests/
│   ├── __init__.py
│   ├── fixtures/               # amostras de dados para os testes
│   ├── test_limpeza.py
│   └── test_transformacao.py
│
├── notebooks/
│   ├── exploracao.ipynb           # análise exploratória genérica
│   ├── exploracao_limpeza.ipynb   # validação manual do limpeza.py
│   └── analise_fraude.ipynb       # análise de padrões de fraude
│
└── docs/
    ├── orquestracao.md        # proposta de orquestração
    └── orientacoes-desafio.md # enunciado original do desafio
```

## Como rodar o projeto

1. Clone este repositório
2. Crie um ambiente virtual: `python -m venv .venv`
3. Ative o ambiente virtual:
   - Linux/Mac: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e ajuste os valores
6. Baixe o dataset ([Kaggle — Synthetic Financial Fraud Dataset](https://www.kaggle.com/datasets/umitka/synthetic-financial-fraud-dataset/data)) e salve em `data/raw/transactions.csv`
7. Execute o pipeline: `python src/pipeline.py`
8. Rode os testes com cobertura: `pytest --cov=src tests/`