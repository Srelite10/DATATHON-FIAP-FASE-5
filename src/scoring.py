"""Percentis, ranking e classificação de prioridade de acompanhamento.

A saída principal do modelo é a probabilidade (``predict_proba``). A
prioridade é uma regra de **produto**, não do modelo: compara o score de um
estudante com a população de referência (base 2025) usando percentil global e
percentil dentro da própria fase. Os thresholds (90/75/50) são extraídos de
``config/regras_produto.json`` — nunca hardcoded soltos no meio da lógica.
"""

from __future__ import annotations

import re

import pandas as pd

REFERENCE_SCORE_COL = "PROB_RISCO_2025"
REFERENCE_PHASE_COL = "FASE_NUM"

# Usado apenas se, por algum motivo, o texto de config/regras_produto.json não
# puder ser interpretado — mantém o app operacional sem travar a UI. O valor
# efetivo em uso normal vem sempre de get_priority_thresholds().
_FALLBACK_THRESHOLDS = {"Muito alta": 90, "Alta": 75, "Moderada": 50}


def get_priority_thresholds(regras_produto: dict) -> dict[str, int]:
    """Extrai os thresholds de percentil (90/75/50) de config/regras_produto.json.

    O JSON descreve a regra em texto (ex.: "percentil global >= 90 OU
    percentil da fase >= 90"); este parser evita duplicar esses números como
    constantes soltas no código.
    """
    prioridade = regras_produto.get("prioridade", {})
    thresholds = {}
    for label in ("Muito alta", "Alta", "Moderada"):
        texto = prioridade.get(label, "")
        match = re.search(r"(\d+)", texto)
        thresholds[label] = int(match.group(1)) if match else _FALLBACK_THRESHOLDS[label]
    return thresholds


def calculate_global_percentile(score: float, reference_scores: pd.Series) -> float:
    """Percentil do ``score`` na população de referência (0-100, maior = mais prioritário).

    Definição: proporção da população de referência com score menor ou igual
    ao score avaliado. Consistente com a coluna PERCENTIL_RISCO_2025 já
    presente na base (rank percentual ascendente).
    """
    n = len(reference_scores)
    if n == 0:
        return 0.0
    count_leq = int((reference_scores <= score).sum())
    return round(100 * count_leq / n, 2)


def calculate_rank(score: float, reference_scores: pd.Series) -> int:
    """Ranking aproximado (1 = maior score/mais prioritário) na população de referência."""
    n = len(reference_scores)
    count_greater = int((reference_scores > score).sum())
    return min(count_greater + 1, n + 1)


def calculate_phase_percentile(score: float, fase_num: int, reference_df: pd.DataFrame) -> float | None:
    """Percentil do score dentro da própria fase. ``None`` se a fase não existir na referência."""
    subset = reference_df.loc[reference_df[REFERENCE_PHASE_COL] == fase_num, REFERENCE_SCORE_COL]
    if subset.empty:
        return None
    return calculate_global_percentile(score, subset)


def calculate_phase_rank(score: float, fase_num: int, reference_df: pd.DataFrame) -> int | None:
    """Ranking aproximado do score dentro da própria fase. ``None`` se a fase não existir na referência."""
    subset = reference_df.loc[reference_df[REFERENCE_PHASE_COL] == fase_num, REFERENCE_SCORE_COL]
    if subset.empty:
        return None
    return calculate_rank(score, subset)


def classify_priority(percentil_global: float, percentil_fase: float | None, thresholds: dict[str, int]) -> str:
    """Classifica a prioridade de acompanhamento (Muito alta/Alta/Moderada/Reduzida).

    Regra (config/regras_produto.json): satisfaz o threshold no percentil
    global OU no percentil da fase. Se a fase não tiver referência disponível,
    considera-se apenas o percentil global.
    """
    pf = percentil_fase if percentil_fase is not None else -1
    if percentil_global >= thresholds["Muito alta"] or pf >= thresholds["Muito alta"]:
        return "Muito alta"
    if percentil_global >= thresholds["Alta"] or pf >= thresholds["Alta"]:
        return "Alta"
    if percentil_global >= thresholds["Moderada"] or pf >= thresholds["Moderada"]:
        return "Moderada"
    return "Reduzida"


def format_probability(value: float) -> str:
    """Formata uma probabilidade (0-1) como percentual com uma casa decimal."""
    if value is None or pd.isna(value):
        return "—"
    return f"{value * 100:.1f}%"


def format_percentile(value: float | None) -> str:
    """Formata um percentil (0-100) para exibição."""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.1f}"
