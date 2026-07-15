import logging
from pathlib import Path
 
import logging
from pathlib import Path
 
import pandas as pd
 
from src.limpeza import (
    TRANSACTION_TYPE_VALIDOS,
    IS_FRAUD_VALIDOS,
    OUTLIER_DESVIOS,
)
 
logger = logging.getLogger(__name__)
 
COLUNAS_CRITICAS = ("transaction_id", "amount", "is_fraud")

def gerar_relatorio(df: pd.DataFrame, n_desvios: float = OUTLIER_DESVIOS) -> dict:
    """Gera o relatório de Data Quality com as métricas do desafio.
 
    Considera "registro com erro" qualquer linha que tenha: nulo em uma
    coluna crítica, valor fora do domínio em 'transaction_type' ou
    'is_fraud', ou seja outlier em 'amount'.
 
    Args:
        df: DataFrame de entrada (pode ser o dado bruto ou já limpo).
        n_desvios: número de desvios padrão usado no critério de outlier
            em 'amount'. Padrão: OUTLIER_DESVIOS (3.0).
 
    Returns:
        Dicionário com as métricas de Data Quality:
            - total_registros
            - registros_com_erro
            - percentual_conformidade
            - nulos_por_coluna (dict coluna -> quantidade)
            - valores_fora_dominio (dict coluna -> quantidade)
            - outliers_amount
            - inconsistencias_is_fraud
    """
    total_registros = len(df)
 
    nulos_por_coluna = df.isna().sum().to_dict()
 
    if "transaction_type" in df.columns:
        mascara_tipo_invalido = ~df["transaction_type"].isin(TRANSACTION_TYPE_VALIDOS)
    else:
        mascara_tipo_invalido = pd.Series(False, index=df.index)
 
    if "is_fraud" in df.columns:
        mascara_fraude_invalida = ~df["is_fraud"].isin(IS_FRAUD_VALIDOS)
    else:
        mascara_fraude_invalida = pd.Series(False, index=df.index)
 
    valores_fora_dominio = {
        "transaction_type": int(mascara_tipo_invalido.sum()),
        "is_fraud": int(mascara_fraude_invalida.sum()),
    }
 
    if "amount" in df.columns:
        media = df["amount"].mean()
        desvio_padrao = df["amount"].std()
        limite_superior = media + n_desvios * desvio_padrao
        limite_inferior = media - n_desvios * desvio_padrao
        mascara_outlier = (df["amount"] > limite_superior) | (df["amount"] < limite_inferior)
        outliers_amount = int(mascara_outlier.sum())
    else:
        mascara_outlier = pd.Series(False, index=df.index)
        outliers_amount = 0
 
    colunas_criticas_presentes = [c for c in COLUNAS_CRITICAS if c in df.columns]
    mascara_nulo_critico = (
        df[colunas_criticas_presentes].isna().any(axis=1)
        if colunas_criticas_presentes else pd.Series(False, index=df.index)
    )
 
    mascara_erro = mascara_nulo_critico | mascara_tipo_invalido | mascara_fraude_invalida | mascara_outlier
    registros_com_erro = int(mascara_erro.sum())
 
    percentual_conformidade = (
        round((total_registros - registros_com_erro) / total_registros * 100, 2)
        if total_registros > 0
        else 0.0
    )
 
    relatorio = {
        "total_registros": total_registros,
        "registros_com_erro": registros_com_erro,
        "percentual_conformidade": percentual_conformidade,
        "nulos_por_coluna": nulos_por_coluna,
        "valores_fora_dominio": valores_fora_dominio,
        "outliers_amount": outliers_amount,
        "inconsistencias_is_fraud": valores_fora_dominio["is_fraud"],
    }
 
    logger.info("Relatorio de qualidade gerado: total=%d, com_erro=%d, conformidade=%.2f%%",
                total_registros, registros_com_erro, percentual_conformidade)
 
    return relatorio