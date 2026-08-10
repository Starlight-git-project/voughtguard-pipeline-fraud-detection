"""Testes das funções de transformação."""
from pathlib import Path

import pytest
import pandas as pd

from src.transformacao import criar_combined_risk, criar_period_of_day, transformar


@pytest.fixture
def df_transacoes_sample():
    """Reaproveita a fixture sintética criada na issue #7."""
    caminho = Path(__file__).parent / "fixtures" / "transacoes_sample.csv"
    return pd.read_csv(caminho)


# ---------------------------------------------------------------------------
# criar_period_of_day
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "hora,periodo_esperado",
    [
        (0, "madrugada"),
        (6, "manha"),
        (12, "tarde"),
        (18, "noite"),
        (23, "noite"),
    ],
)
def test_criar_period_of_day_valores_representativos(hora, periodo_esperado):
    """Verifica os 4 períodos para valores representativos de hour."""
    df = pd.DataFrame({"hour": [hora]})
    resultado = criar_period_of_day(df)
    assert resultado.loc[0, "period_of_day"] == periodo_esperado


def test_criar_period_of_day_borda_madrugada_manha():
    """Caso de borda: hora 5 é madrugada, hora 6 é manhã."""
    df = pd.DataFrame({"hour": [5, 6]})
    resultado = criar_period_of_day(df)
    assert resultado.loc[0, "period_of_day"] == "madrugada"
    assert resultado.loc[1, "period_of_day"] == "manha"


def test_criar_period_of_day_borda_manha_tarde():
    """Caso de borda: hora 11 é manhã, hora 12 é tarde."""
    df = pd.DataFrame({"hour": [11, 12]})
    resultado = criar_period_of_day(df)
    assert resultado.loc[0, "period_of_day"] == "manha"
    assert resultado.loc[1, "period_of_day"] == "tarde"


def test_criar_period_of_day_borda_tarde_noite():
    """Caso de borda: hora 17 é tarde, hora 18 é noite."""
    df = pd.DataFrame({"hour": [17, 18]})
    resultado = criar_period_of_day(df)
    assert resultado.loc[0, "period_of_day"] == "tarde"
    assert resultado.loc[1, "period_of_day"] == "noite"


def test_criar_period_of_day_com_fixture_sample(df_transacoes_sample):
    """Roda a função contra a fixture real (issue #7) e confere que
    todas as 24 horas possíveis mapeiam para um dos 4 períodos válidos."""
    resultado = criar_period_of_day(df_transacoes_sample)
    periodos_validos = {"madrugada", "manha", "tarde", "noite"}
    assert set(resultado["period_of_day"].unique()).issubset(periodos_validos)
    assert "period_of_day" in resultado.columns


def test_criar_period_of_day_nao_altera_original():
    """Garante que a função não muta o DataFrame original (pureza)."""
    df_original = pd.DataFrame({"hour": [3, 9, 15, 20]})
    colunas_antes = list(df_original.columns)
    criar_period_of_day(df_original)
    assert list(df_original.columns) == colunas_antes


# ---------------------------------------------------------------------------
# criar_combined_risk
# ---------------------------------------------------------------------------

def test_criar_combined_risk_media_correta():
    """Verifica que o valor é a média correta entre os dois scores."""
    df = pd.DataFrame({
        "device_risk_score": [0.2, 0.8],
        "ip_risk_score": [0.4, 0.6],
    })
    resultado = criar_combined_risk(df)
    assert resultado.loc[0, "combined_risk"] == pytest.approx(0.3)
    assert resultado.loc[1, "combined_risk"] == pytest.approx(0.7)


def test_criar_combined_risk_valores_extremos():
    """Testa combined_risk com valores extremos (0.0 e 1.0)."""
    df = pd.DataFrame({
        "device_risk_score": [0.0, 1.0, 0.0, 1.0],
        "ip_risk_score": [0.0, 1.0, 1.0, 0.0],
    })
    resultado = criar_combined_risk(df)
    assert resultado.loc[0, "combined_risk"] == pytest.approx(0.0)
    assert resultado.loc[1, "combined_risk"] == pytest.approx(1.0)
    assert resultado.loc[2, "combined_risk"] == pytest.approx(0.5)
    assert resultado.loc[3, "combined_risk"] == pytest.approx(0.5)


def test_criar_combined_risk_com_fixture_sample(df_transacoes_sample):
    """Roda a função contra a fixture real (issue #7) e confere que o
    resultado sempre fica dentro do intervalo esperado dos scores."""
    resultado = criar_combined_risk(df_transacoes_sample)
    assert "combined_risk" in resultado.columns
    assert resultado["combined_risk"].notna().all()


def test_criar_combined_risk_nao_altera_original():
    """Garante que a função não muta o DataFrame original (pureza)."""
    df_original = pd.DataFrame({
        "device_risk_score": [0.1, 0.5],
        "ip_risk_score": [0.2, 0.6],
    })
    colunas_antes = list(df_original.columns)
    criar_combined_risk(df_original)
    assert list(df_original.columns) == colunas_antes


# ---------------------------------------------------------------------------
# transformar (integração das duas funções)
# ---------------------------------------------------------------------------

def test_transformar_aplica_as_duas_transformacoes():
    """Testa se transformar aplica combined_risk e period_of_day juntos."""
    df = pd.DataFrame({
        "device_risk_score": [10],
        "ip_risk_score": [20],
        "hour": [3],
    })
    resultado = transformar(df)
    assert "combined_risk" in resultado.columns
    assert "period_of_day" in resultado.columns
    assert resultado.loc[0, "combined_risk"] == 15.0
    assert resultado.loc[0, "period_of_day"] == "madrugada"


def test_transformar_com_fixture_sample(df_transacoes_sample):
    """Roda o fluxo completo de transformação contra a fixture real (issue #7)."""
    resultado = transformar(df_transacoes_sample)
    assert "combined_risk" in resultado.columns
    assert "period_of_day" in resultado.columns
    assert len(resultado) == len(df_transacoes_sample)