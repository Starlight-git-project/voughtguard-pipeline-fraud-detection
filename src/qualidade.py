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
        Dicionário com as métricas de Data Quality.

    Raises:
        KeyError: se alguma coluna obrigatória (transaction_type,
            is_fraud, amount) não existir no DataFrame.
    """
    total_registros = len(df)
    nulos_por_coluna = df.isna().sum().to_dict()

    mascara_tipo_invalido = ~df["transaction_type"].isin(TRANSACTION_TYPE_VALIDOS)
    mascara_fraude_invalida = ~df["is_fraud"].isin(IS_FRAUD_VALIDOS)

    valores_fora_dominio = {
        "transaction_type": int(mascara_tipo_invalido.sum()),
        "is_fraud": int(mascara_fraude_invalida.sum()),
    }

    media = df["amount"].mean()
    desvio_padrao = df["amount"].std()
    limite_superior = media + n_desvios * desvio_padrao
    limite_inferior = media - n_desvios * desvio_padrao
    mascara_outlier = (df["amount"] > limite_superior) | (df["amount"] < limite_inferior)
    outliers_amount = int(mascara_outlier.sum())

    mascara_nulo_critico = df[list(COLUNAS_CRITICAS)].isna().any(axis=1)
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

    logger.info(
        "Relatorio de qualidade gerado: total=%d, com_erro=%d, conformidade=%.2f%%",
        total_registros, registros_com_erro, percentual_conformidade,
    )

    return relatorio

def salvar_relatorio(
    relatorio: dict,
    caminho: str = "data/processed/relatorio_qualidade.csv",
) -> None:
    """Salva o relatório de Data Quality em um arquivo CSV.
 
    Métricas aninhadas (ex: nulos_por_coluna) são achatadas em linhas
    no formato 'metrica.subchave'.
 
    Args:
        relatorio: dicionário retornado por gerar_relatorio().
        caminho: caminho de destino do CSV.
            Padrão: 'data/processed/relatorio_qualidade.csv'.
 
    Raises:
        OSError: se não for possível criar o diretório de destino.
    """
    caminho_path = Path(caminho)
    caminho_path.parent.mkdir(parents=True, exist_ok=True)
 
    linhas = []
    for chave, valor in relatorio.items():
        if isinstance(valor, dict):
            for subchave, subvalor in valor.items():
                linhas.append({"metrica": f"{chave}.{subchave}", "valor": subvalor})
        else:
            linhas.append({"metrica": chave, "valor": valor})
 
    df_relatorio = pd.DataFrame(linhas)
    df_relatorio.to_csv(caminho_path, index=False)
 
    logger.info("Relatorio salvo em %s", caminho_path)