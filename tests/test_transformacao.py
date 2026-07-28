"""Testes das funções de transformação."""

import pandas as pd
from src.transformacao import criar_combined_risk, criar_period_of_day, transformar

def test_adicionar_combined_risk():
    """Testa se combined_risk calcula a média corretamente."""
    df = pd.DataFrame({
        "device_risk_score": [10, 50],
        "ip_risk_score": [20, 60]
    })
    resultado = criar_combined_risk(df)
    assert resultado["combined_risk"][0] == 15.0
    assert resultado["combined_risk"][1] == 55.0

def test_adicionar_period_of_day():
    """Testa se period_of_day classifica as horas corretamente."""
    df = pd.DataFrame({
        "hour": [3, 9, 15, 20]
    })
    resultado = criar_period_of_day(df)
    assert resultado["period_of_day"][0] == "madrugada"
    assert resultado["period_of_day"][1] == "manha"
    assert resultado["period_of_day"][2] == "tarde"
    assert resultado["period_of_day"][3] == "noite"

def test_transformar():
    """Testa se transformar aplica as duas transformações juntas."""
    df = pd.DataFrame({
        "device_risk_score": [10],
        "ip_risk_score": [20],
        "hour": [3]
    })
    resultado = transformar(df)
    assert "combined_risk" in resultado.columns
    assert "period_of_day" in resultado.columns
    assert resultado["combined_risk"][0] == 15.0
    assert resultado["period_of_day"][0] == "madrugada"