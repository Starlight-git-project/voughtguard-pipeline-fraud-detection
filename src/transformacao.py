"""Criação de novas colunas e features (period_of_day, combined_risk)."""

import pandas as pd

def criar_combined_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna combined_risk como média entre device_risk_score e ip_risk_score."""
    df_resultado = df.copy()
    df_resultado["combined_risk"] = (df_resultado["device_risk_score"] + df_resultado["ip_risk_score"]) / 2
    return df_resultado

def classificar_periodo(hora: int) -> str:
    """Classifica uma hora (0-23) em um período do dia."""
    if 0 <= hora <= 5:
        return "madrugada"
    elif 6 <= hora <= 11:
        return "manha"
    elif 12 <= hora <= 17:
        return "tarde"
    else:
        return "noite"
    
def criar_period_of_day(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna period_of_day a partir da coluna hour."""
    df_resultado = df.copy()
    df_resultado["period_of_day"] = df_resultado["hour"].apply(classificar_periodo)
    return df_resultado

def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas as transformações: combined_risk e period_of_day."""
    df = criar_combined_risk(df)
    df = criar_period_of_day(df)
    return df
    