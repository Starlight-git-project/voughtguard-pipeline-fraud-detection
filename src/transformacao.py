"""Criação de novas colunas e features (period_of_day, combined_risk)."""

import pandas as pd

def adicionar_combined_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna combined_risk como média entre device_risk_score e ip_risk_score."""
    df["combined_risk"] = (df["device_risk_score"] + df["ip_risk_score"]) / 2
    return df

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
    
def adicionar_period_of_day(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna period_of_day a partir da coluna hour."""
    df["period_of_day"] = df["hour"].apply(classificar_periodo)
    return df

def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas as transformações: combined_risk e period_of_day."""
    df = adicionar_combined_risk(df)
    df = adicionar_period_of_day(df)
    return df
    