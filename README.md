# VoughtGuard - Pipeline de Detecção de Fraude Financeira

Pipeline de dados para processar transações financeiras, aplicar limpeza e
validação de qualidade, gerar tabelas analíticas para o time de risco e
produzir um relatório automatizado de Data Quality.

## Estrutura do repositório

voughtguard-pipeline-fraud-detection/
├── .env.example          # variáveis de ambiente (sem valores reais)
├── .gitignore            # dados, credenciais e temporários ignorados
├── README.md             # este arquivo
├── requirements.txt      # dependências do projeto
│
├── data/
│   ├── raw/              # dataset original — não commitado
│   └── processed/        # tabelas analíticas geradas
│
├── src/
│   ├── config.py         # leitura de variáveis de ambiente
│   ├── pipeline.py       # orquestração principal
│   ├── limpeza.py        # funções de limpeza e validação
│   ├── transformacao.py  # criação de novas colunas
│   └── qualidade.py      # relatório de data quality
│
├── tests/
│   ├── fixtures/
│   │   └── transacoes_sample.csv
│   ├── test_limpeza.py
│   └── test_transformacao.py
│
├── notebooks/
│   └── exploracao.ipynb  # análise exploratória
│
└── docs/
    └── orquestracao.md   # proposta de orquestração

## Como rodar o projeto

1. Clone este repositório
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual
4. Instale as dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e ajuste os valores