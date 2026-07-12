"""Funções de limpeza e validação de qualidade dos dados brutos."""

import logging
import numpy as np
import pandas as pd

from typing import Iterable

logger = logging.getLogger(__name__)

COLUNAS_CRITICAS = ("transaction_id", "amount", "is_fraud")

TIPOS_ESPERADOS = {
    "amount": "float64",
    "hour": "int64",
    "is_fraud": "int64"
}

TRANSACTION_TYPE_VALIDOS = ("POS", "Online", "ATM", "QR")
IS_FRAUD_VALIDOS = (0,1)

OUTLIER_DESVIOS = 3.0

def remover_nulos_criticos(
  df: pd.DataFrame,
  colunas: Iterable[str] = COLUNAS_CRITICAS,
  ) -> pd.DataFrame:
    
  """ Remove linhas com valor nulo em colunas consideradas críticas.
  
  Args: 
      df: Datafrane de entrada 
      colunas: Colunas que nao podem conter valores nulos. Por padrao usa constante
      COLUNAS_CRITICAS
      
  Returns:
      Novo Dataframe sem as linhas que tinham valores nulos em algumas das colunas criticas.

  Raises:
      KeyError: se algum coluna em 'colunas' nao existir no DataFrame
  """
  
  colunas = list(colunas)
  colunas_ausentes = [c for c in colunas if c not in df.columns]
  if colunas_ausentes:
    raise KeyError(f"Colunas criticas ausentes do DataFrame: {colunas_ausentes}")
    
    
  df_limpo = df.copy()
  df_limpo = df_limpo.dropna(subset=colunas)
  
  return df_limpo.reset_index(drop=True)
  
def corrigir_tipos(
    df: pd.DataFrame,
    tipos: dict[str,str] = TIPOS_ESPERADOS
)-> pd.DataFrame:
    
    """
    Converte colunas para os tipos numericos esperados.
    
    Valores que nao estiverem mapeados na conversao viram NaN.
    
    Args:
        df: DataFrame de entrada 
        tipos: Mapeamento coluna -> dtype alvo. Por padrao usa TIPOS_ESPERADOS.
        
    Returns:
        Novo DataFrame com as colunas convertidas
        
    Raises:
      KeyError: se algum coluna em 'tipos' nao existir no DataFrame
    """
    
    colunas_ausentes = [c for c in tipos if c not in df.columns]
    if colunas_ausentes:
        raise KeyError(f"Colunas ausentes para conversao de tipo: {colunas_ausentes}")
        
    
    df_convertido = df.copy()
    
    for coluna, dtype_alvo in tipos.items():
        valores_numericos = pd.to_numeric(df_convertido[coluna], errors = "coerce")
        
        n_invalidos = valores_numericos.isna().sum() - df_convertido[coluna].isna().sum()
        if n_invalidos > 0:
            logger.warning(
                "Corrigir tipos: %d valor(es) invalido(s) em '%s' viraram NaN",
                n_invalidos,
                coluna,
            )
            
        if dtype_alvo == "int64":
            if valores_numericos.isna().any():
                df_convertido[coluna] = valores_numericos
            else:
                df_convertido[coluna] = valores_numericos.astype("int64")
        else:
            df_convertido[coluna] = valores_numericos.astype(dtype_alvo)
    
    return df_convertido
    
def validar_dominios(
    df: pd.DataFrame,
    remove_invalidos: bool = False
) -> pd.DataFrame:
    
    """
        Valida de 'transaction_type' e 'is_fraud' estao dentro do dominio esperado.
        
        Args:
            df: DataFrame de entrada
            remove_invalidos: Se True, remove as linhas invalidas em vez de apenas marca-las como NaN. Padrao: False
            
        Returns:
            Novo DataFrame com os valores fora do dominio marcados como NaN, ou removidos se 'remove_invalidos = True'.
            
        Raises:
            KeyError: se 'transaction_type' ou 'is_fraud' nao existirem.
    """
    
    for coluna in ("transaction_type", "is_fraud"):
        if coluna not in df.columns:
            raise KeyError(f"Coluna obrigatorio ausente: '{coluna}'")
    
    df_validado = df.copy()
    
    mascara_tipo_invalido = ~df_validado["transaction_type"].isin(TRANSACTION_TYPE_VALIDOS)
    mascara_fraude_invalida = ~df_validado["is_fraud"].isin(IS_FRAUD_VALIDOS)
    
    if remove_invalidos:
        df_validado = df_validado.loc[~(mascara_tipo_invalido | mascara_fraude_invalida)]
        return df_validado.reset_index(drop=True)
        
    df_validado.loc[mascara_tipo_invalido, "transaction_type"] = np.nan
    df_validado.loc[mascara_fraude_invalida, "is_fraud"] = np.nan
    
    return df_validado
    

def detectar_outliers_amount(
    df: pd.DataFrame,
    n_desvios: float = OUTLIER_DESVIOS,
    remove: bool = False
) -> pd.DataFrame:
    
    """
    Identifica outliers em 'amount' usando o criterio de desvio padrao.
    
    Valor é considerado outlier quando sua distancia em relacao a media é maior que n_desvios desvio padrao.
    
    Por padrao os outliers nao sao removidos, sao adicionados em uma nova coluna 'is_outlier'. Usar remove = True para descarta-los.
    
    Args:
        df: DataFrame de entrada
        n_desvios: Parametro numero de desvio padrao
        remove: Se True, remove linhas que sao outliers. Padrao: False
    
    Returns:
        Novo DataFrame. Se remove = False, contem coluna 'is_outlier'.
        
    Raises:
        KeyError: se a coluna 'amount' nao existir.
    """
    
    if "amount" not in df.columns:
        raise KeyError("Coluna obrigatoria 'amount' ausente")
        
    df_resultado = df.copy()
    
    media = df_resultado["amount"].mean()
    desvio_padrao = df_resultado["amount"].std()

    limite_superior = media + n_desvios*desvio_padrao
    limite_inferior = media - n_desvios*desvio_padrao
    
    mascara_outlier = (df_resultado["amount"]> limite_superior ) |( df_resultado["amount"] < limite_inferior )
    
    if remove:
        return df_resultado.loc[~mascara_outlier].reset_index(drop=True)
        
    df_resultado["is_outlier"] = mascara_outlier
    return df_resultado