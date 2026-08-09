"""Carregamento e validação de dados e configurações do pacote do Datathon.

Todas as funções aqui são a única porta de entrada para os arquivos em
``data/`` e ``config/``. Nenhuma página deve usar ``pd.read_csv`` ou
``json.load`` diretamente — sempre passar por este módulo, para manter cache e
tratamento de erro consistentes em toda a aplicação.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import streamlit as st

from src import config


class ArtifactError(Exception):
    """Erro amigável para artefatos (dados/config) ausentes ou inválidos."""


def _friendly_json_load(path: Path) -> dict:
    if not path.exists():
        raise ArtifactError(
            f"Arquivo de configuração não encontrado: `{path.relative_to(config.BASE_DIR)}`. "
            "Verifique se o pacote de dados do projeto está completo."
        )
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ArtifactError(
            f"Não foi possível interpretar `{path.relative_to(config.BASE_DIR)}` como JSON válido."
        ) from exc


def _friendly_csv_load(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise ArtifactError(
            f"Base de dados não encontrada: `{path.relative_to(config.BASE_DIR)}`. "
            "Verifique se o pacote de dados do projeto está completo."
        )
    try:
        return pd.read_csv(path)
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ArtifactError(
            f"Não foi possível ler `{path.relative_to(config.BASE_DIR)}` como CSV válido."
        ) from exc


# --------------------------------------------------------------------------- #
# Configurações JSON (cache_data: são dicts simples, leves e imutáveis)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def load_regras_produto() -> dict:
    """Regras de prioridade, Radar Preventivo e ponto cego."""
    return _friendly_json_load(config.PATH_REGRAS_PRODUTO)


@st.cache_data(show_spinner=False)
def load_metricas_modelo() -> dict:
    """Métricas de desenvolvimento/teste temporal do modelo."""
    return _friendly_json_load(config.PATH_METRICAS_MODELO)


@st.cache_data(show_spinner=False)
def load_efetividade() -> dict:
    """Estatísticas de trajetória/efetividade (Wilcoxon, saldos)."""
    return _friendly_json_load(config.PATH_EFETIVIDADE)


@st.cache_data(show_spinner=False)
def load_radar_preventivo() -> dict:
    """DNA do risco oculto (diferenças Z) e triangulação."""
    return _friendly_json_load(config.PATH_RADAR_PREVENTIVO)


@st.cache_data(show_spinner=False)
def load_metadados_bundle() -> dict:
    """Metadados descritivos do bundle do modelo (não o bundle em si)."""
    return _friendly_json_load(config.PATH_METADADOS_BUNDLE)


@st.cache_data(show_spinner=False)
def load_validacoes() -> dict:
    """Valores esperados de integridade dos datasets (testes de aceitação)."""
    return _friendly_json_load(config.PATH_VALIDACOES)


# --------------------------------------------------------------------------- #
# Bases de dados (cache_data: DataFrames)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Carregando base de estudantes elegíveis (2025)...")
def load_streamlit_data() -> pd.DataFrame:
    """Base principal: 1054 estudantes elegíveis, já com score e Radar calculados."""
    return _friendly_csv_load(config.PATH_BASE_STREAMLIT)


@st.cache_data(show_spinner="Carregando base completa de estudantes (2025)...")
def load_product_data() -> pd.DataFrame:
    """Base completa: 1156 estudantes (elegíveis + não elegíveis)."""
    return _friendly_csv_load(config.PATH_BASE_PRODUTO)


@st.cache_data(show_spinner="Carregando trajetória histórica de Pedras (2022-2024)...")
def load_trajectory_data() -> pd.DataFrame:
    """Trajetória de Pedra 2022 -> 2024 para 434 estudantes com histórico completo."""
    return _friendly_csv_load(config.PATH_TRAJETORIA)


# --------------------------------------------------------------------------- #
# Validação de integridade (testes de aceitação dos dados)
# --------------------------------------------------------------------------- #
@dataclass
class ValidationReport:
    """Resultado da checagem dos dados carregados contra config/validacoes.json."""

    ok: bool
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    @property
    def issues(self) -> list[str]:
        return [msg for _, passed, msg in self.checks if not passed]


def _check(checks: list, label: str, actual, expected) -> None:
    passed = actual == expected
    checks.append((label, passed, f"{label}: esperado {expected}, obtido {actual}"))


@st.cache_data(show_spinner=False)
def validate_artifacts() -> ValidationReport:
    """Roda os testes de aceitação de dados descritos no briefing do produto.

    Compara contagens vindas dos CSVs com os valores oficiais registrados em
    ``config/validacoes.json``. Não hardcoda os números esperados — eles vêm do
    próprio arquivo de configuração.
    """
    validacoes = load_validacoes()
    checks: list[tuple[str, bool, str]] = []

    df_streamlit = load_streamlit_data()
    _check(checks, "base_streamlit_linhas", len(df_streamlit), validacoes["base_streamlit_linhas"])
    _check(
        checks,
        "base_streamlit_ras_unicos",
        int(df_streamlit["RA"].nunique()),
        validacoes["base_streamlit_ras_unicos"],
    )
    _check(
        checks,
        "base_streamlit_duplicidades",
        int(df_streamlit["RA"].duplicated().sum()),
        validacoes["base_streamlit_duplicidades"],
    )
    _check(checks, "risco_oculto", int(df_streamlit["RISCO_OCULTO"].sum()), validacoes["risco_oculto"])
    _check(checks, "ponto_cego", int(df_streamlit["PONTO_CEGO"].sum()), validacoes["ponto_cego"])

    df_produto = load_product_data()
    _check(checks, "base_produto_linhas", len(df_produto), validacoes["base_produto_linhas"])
    _check(
        checks,
        "base_produto_ras_unicos",
        int(df_produto["RA"].nunique()),
        validacoes["base_produto_ras_unicos"],
    )
    _check(
        checks,
        "base_produto_duplicidades",
        int(df_produto["RA"].duplicated().sum()),
        validacoes["base_produto_duplicidades"],
    )
    status_counts = df_produto["STATUS_MODELO"].value_counts().to_dict()
    for status_label, expected_count in validacoes["status_modelo"].items():
        _check(checks, f"status_modelo[{status_label}]", int(status_counts.get(status_label, 0)), expected_count)

    df_trajetoria = load_trajectory_data()
    _check(checks, "trajetoria_linhas", len(df_trajetoria), validacoes["trajetoria_linhas"])
    _check(
        checks,
        "trajetoria_ras_unicos",
        int(df_trajetoria["RA"].nunique()),
        validacoes["trajetoria_ras_unicos"],
    )

    ok = all(passed for _, passed, _ in checks)
    return ValidationReport(ok=ok, checks=checks)
