"""Carregamento e execução do modelo serializado (bundle .joblib).

O arquivo ``models/modelo_risco_defasagem_2025.joblib`` contém um dicionário
(bundle), não um estimador sklearn direto. A regra de ouro deste módulo:

    bundle = joblib.load(caminho)
    pipeline = bundle["pipeline"]
    pipeline.predict_proba(X)

Nunca chamar ``predict_proba`` no bundle, nunca retreinar, nunca recalibrar.
"""

from __future__ import annotations

import warnings

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from src import config


class ModelServiceError(Exception):
    """Erro amigável relacionado ao carregamento ou uso do modelo."""


@st.cache_resource(show_spinner="Carregando modelo de risco de defasagem...")
def load_model_bundle() -> dict:
    """Carrega o bundle (dicionário) do modelo a partir do .joblib.

    Retorna o dicionário completo — inclui a pipeline sklearn e metadados
    (features, fases elegíveis, threshold de desenvolvimento etc.).
    """
    if not config.PATH_MODELO.exists():
        raise ModelServiceError(
            f"Modelo não encontrado em `{config.PATH_MODELO.relative_to(config.BASE_DIR)}`. "
            "Verifique se o arquivo do modelo foi incluído no projeto."
        )
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            bundle = joblib.load(config.PATH_MODELO)
    except Exception as exc:  # carregar um pickle pode falhar de várias formas
        raise ModelServiceError(
            "Não foi possível carregar o modelo serializado. O ambiente pode estar "
            "com uma versão incompatível do scikit-learn (consulte docs/ambiente_modelo.txt)."
        ) from exc

    if not isinstance(bundle, dict) or "pipeline" not in bundle:
        raise ModelServiceError(
            "O arquivo de modelo não está no formato esperado (bundle/dicionário com chave 'pipeline')."
        )
    return bundle


def get_pipeline(bundle: dict):
    """Retorna a pipeline sklearn armazenada no bundle."""
    return bundle["pipeline"]


def get_features(bundle: dict) -> list[str]:
    """Lista de features exatas, na ordem esperada pela pipeline."""
    return list(bundle["features"])


def get_fases_elegiveis(bundle: dict) -> list[int]:
    """Fases (FASE_NUM) para as quais o modelo é válido."""
    return list(bundle["fases_elegiveis"])


def is_fase_elegivel(fase_num: int, bundle: dict) -> bool:
    """Indica se uma fase está dentro do escopo validado do modelo."""
    return int(fase_num) in get_fases_elegiveis(bundle)


def predict_risk(bundle: dict, df: pd.DataFrame) -> np.ndarray:
    """Executa ``pipeline.predict_proba`` sobre ``df`` e retorna P(risco futuro).

    ``df`` deve conter todas as colunas em ``bundle["features"]``. Todas as
    linhas devem pertencer a fases elegíveis — esta função não filtra, apenas
    valida e recusa executar sobre fases fora do escopo (ver
    :func:`split_by_eligibility` para separar o lote antes de chamar aqui).
    """
    features = get_features(bundle)
    missing = [f for f in features if f not in df.columns]
    if missing:
        raise ModelServiceError(
            "Faltam colunas obrigatórias para o modelo: " + ", ".join(missing)
        )

    if "FASE_NUM" in df.columns:
        fases_elegiveis = set(get_fases_elegiveis(bundle))
        fases_invalidas = sorted(set(df["FASE_NUM"].astype(int).unique()) - fases_elegiveis)
        if fases_invalidas:
            raise ModelServiceError(
                "Existem linhas com FASE_NUM fora do escopo validado do modelo "
                f"({fases_invalidas}). Separe estudantes elegíveis (Fases 0 a 7) "
                "antes de calcular o score prospectivo."
            )

    pipeline = get_pipeline(bundle)
    X = df[features]
    try:
        proba = pipeline.predict_proba(X)[:, 1]
    except Exception as exc:
        raise ModelServiceError(
            "Não foi possível calcular a probabilidade para os dados informados. "
            "Verifique se os tipos das colunas são numéricos."
        ) from exc
    return proba


def split_by_eligibility(df: pd.DataFrame, bundle: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa ``df`` em (elegíveis, não elegíveis) a partir de FASE_NUM.

    Não elegíveis (Fases 8 e 9) nunca recebem ``predict_proba`` — a ausência
    estrutural de indicadores nessas fases não é resolvida por imputação.
    """
    if "FASE_NUM" not in df.columns:
        raise ModelServiceError("Coluna obrigatória 'FASE_NUM' ausente nos dados informados.")
    fases_elegiveis = set(get_fases_elegiveis(bundle))
    elegivel_mask = df["FASE_NUM"].astype(int).isin(fases_elegiveis)
    return df.loc[elegivel_mask].copy(), df.loc[~elegivel_mask].copy()
