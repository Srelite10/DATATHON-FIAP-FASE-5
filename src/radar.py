"""Classificação do Radar Preventivo e identificação de potenciais pontos cegos.

Regras (config/regras_produto.json → "radar_preventivo" e "ponto_cego"):

- Crítico persistente: já possui defasagem + prioridade Alta/Muito alta.
- Risco oculto: não possui defasagem + prioridade Alta/Muito alta.
- Atenção atual: possui defasagem + prioridade Moderada/Reduzida.
- Estável / menor prioridade: não possui defasagem + prioridade Moderada/Reduzida.
- Ponto cego: Risco oculto + Pedra 2024 em Ametista ou Topázio.

Este módulo é uma ferramenta de triagem preventiva — não um instrumento de
diagnóstico. As classificações refletem sinais estatísticos associados a maior
prioridade futura de acompanhamento, não uma previsão determinística.
"""

from __future__ import annotations

import pandas as pd

from src import config

PRIORIDADE_ALTA = {"Alta", "Muito alta"}

CRITICO_PERSISTENTE = "Crítico persistente"
RISCO_OCULTO = "Risco oculto"
ATENCAO_ATUAL = "Atenção atual"
ESTAVEL_MENOR_PRIORIDADE = "Estável / menor prioridade"


def defasagem_analise_to_bool(defasagem_analise: float) -> bool:
    """DEFASAGEM_ANALISE < 0 indica presença de defasagem atual."""
    return defasagem_analise < 0


def classify_radar(tem_defasagem: bool, prioridade: str) -> str:
    """Classifica o perfil do Radar Preventivo a partir de defasagem atual e prioridade."""
    prioridade_alta = prioridade in PRIORIDADE_ALTA
    if tem_defasagem and prioridade_alta:
        return CRITICO_PERSISTENTE
    if not tem_defasagem and prioridade_alta:
        return RISCO_OCULTO
    if tem_defasagem and not prioridade_alta:
        return ATENCAO_ATUAL
    return ESTAVEL_MENOR_PRIORIDADE


def get_pedras_ponto_cego(regras_produto: dict) -> tuple[str, ...]:
    """Extrai as Pedras que caracterizam potencial ponto cego a partir do texto de config.

    Evita hardcode: procura, no vocabulário conhecido de Pedras
    (Quartzo/Ágata/Ametista/Topázio), quais nomes aparecem na regra
    ``ponto_cego`` do config/regras_produto.json.
    """
    texto = regras_produto.get("ponto_cego", "")
    pedras = tuple(p for p in config.PEDRA_ORDEM if p in texto)
    return pedras or config.PEDRAS_PONTO_CEGO_FALLBACK


def is_ponto_cego(perfil_radar: str, pedra: str | None, pedras_alvo: tuple[str, ...]) -> bool:
    """Um potencial ponto cego é um Risco oculto cuja Pedra 2024 está entre as pedras-alvo.

    Representa um estudante que não apresenta defasagem atual, não está nas
    Pedras inferiores, mas ainda assim concentra prioridade prospectiva
    elevada — um instrumento de triagem preventiva, não um diagnóstico.
    """
    if perfil_radar != RISCO_OCULTO:
        return False
    if pedra is None or (isinstance(pedra, float) and pd.isna(pedra)):
        return False
    return pedra in pedras_alvo
