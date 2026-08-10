"""Testes das funções de limpeza."""
from pathlib import Path
import pytest
import pandas as pd
from src.limpeza import (
    remover_nulos_criticos,
    corrigir_tipos,
    validar_dominios,
    detectar_outliers_amount
)

@pytest.fixture
def df_transacoes_sample():
    caminho = Path(__file__).parent / "fixtures" / "transacoes_sample.csv"
    return pd.read_csv(caminho)

@pytest.fixture
def df_transacoes_invalidas():
    return pd.DataFrame(
        {
            "transaction_id": [1, None, 3],
            "amount": [100.0, 200.0, None],
            "hour": ["12", "13", "x"],
            "transaction_type": ["POS", "InvalidType", "Online"],
            "is_fraud": [0, 2, 1],
            "device_risk_score": [10, 20, 30],
            "ip_risk_score": [5, 15, 25],
        }
    )

def test_remover_nulos_criticos(df_transacoes_sample):
    """Remove linhas com nulos nas colunas críticas e reseta o índice."""
    resultado = remover_nulos_criticos(df_transacoes_sample)

    assert not resultado.empty

def test_remover_nulos_criticos_coluna_ausente(df_transacoes_invalidas):
    """Testa se a função levanta KeyError quando colunas críticas estão ausentes."""

    df_sem_is_fraud = df_transacoes_invalidas.drop(columns=["is_fraud"])

    with pytest.raises(KeyError, match="Colunas criticas ausentes"):
        remover_nulos_criticos(df_sem_is_fraud)
        
def test_corrigir_tipos(df_transacoes_sample):
    """Converte colunas para os tipos numéricos esperados."""
    resultado = corrigir_tipos(df_transacoes_sample)
    assert "amount" in resultado.columns
    assert "hour" in resultado.columns
    
def test_corrigir_tipos_coluna_ausente(df_transacoes_invalidas):
    """Testa se a função levanta KeyError quando colunas críticas estão ausentes."""

    df_sem_hour = df_transacoes_invalidas.drop(columns=["hour"])

    with pytest.raises(KeyError, match="Colunas ausentes para conversao de tipo:"):
        corrigir_tipos(df_sem_hour)
        

def test_validar_dominios(df_transacoes_sample):
    """Valida se os valores das colunas estão dentro dos domínios esperados."""
    resultado = validar_dominios(df_transacoes_sample, remove_invalidos=False)
    assert not resultado.empty
    
def test_validar_dominios_colunas_ausentes(df_transacoes_invalidas):
    """Testa se a função levanta KeyError quando colunas críticas está ausentes."""

    df_sem_transaction_type = df_transacoes_invalidas.drop(columns=["transaction_type"])
    
    with pytest.raises(KeyError, match="Coluna obrigatorio ausente"):
        validar_dominios(df_sem_transaction_type)
        
def test_validar_dominios_marca_invalidos_com_nan(df_transacoes_invalidas):
    """Quando remove_invalidos=False, mantém as linhas e marca inválidos como NaN."""

    resultado = validar_dominios(df_transacoes_invalidas, remove_invalidos=False)
    assert pd.isna(resultado.loc[1, "transaction_type"])
    assert pd.isna(resultado.loc[1, "is_fraud"])
    
def test_detectar_outliers_amount(df_transacoes_sample):
    """Marca outliers na coluna amount sem remover linhas."""
    resultado = detectar_outliers_amount(df_transacoes_sample, remove=False)

    assert "is_outlier" in resultado.columns
    assert resultado["is_outlier"].dtype == bool
    assert len(resultado) == len(df_transacoes_sample)
    
def test_detectar_outliers_amount_com_valor_extremo():
    """Detecta um outlier explícito em amount."""
    df = pd.DataFrame(
        {
            "transaction_id": [1, 2, 3, 4],
            "amount": [100.0, 101.0, 99.0, 1000.0],
            "hour": [10, 11, 12, 13],
            "transaction_type": ["POS", "Online", "ATM", "QR"],
            "is_fraud": [0, 0, 1, 0],
        }
    )

    resultado = detectar_outliers_amount(df, n_desvios=1, remove=False)

    assert "is_outlier" in resultado.columns
    assert bool(resultado.loc[3, "is_outlier"]) is True
    assert bool(resultado.loc[0, "is_outlier"]) is False
    
def test_detectar_outliers_amount_remove_true():
    """Remove a linha marcada como outlier quando remove=True."""
    df = pd.DataFrame(
        {
            "transaction_id": [1, 2, 3, 4],
            "amount": [100.0, 101.0, 99.0, 1000.0],
            "hour": [10, 11, 12, 13],
            "transaction_type": ["POS", "Online", "ATM", "QR"],
            "is_fraud": [0, 0, 1, 0],
        }
    )

    resultado = detectar_outliers_amount(df, n_desvios=1, remove=True)

    assert len(resultado) == 3
    assert 1000.0 not in resultado["amount"].values