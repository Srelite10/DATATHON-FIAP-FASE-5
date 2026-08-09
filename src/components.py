"""Componentes de UI reutilizáveis entre páginas (Streamlit)."""

from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd
import streamlit as st

from src import config

DISCLAIMER_GERAL = (
    "Este painel apresenta **probabilidade estimada** e **prioridade de acompanhamento** — "
    "sinais estatísticos associados a maior atenção futura. Não é um instrumento de diagnóstico "
    "e não deve ser interpretado como previsão determinística."
)


def render_page_header(title: str, subtitle: str | None = None) -> None:
    """Cabeçalho padrão de página: título curto + subtítulo gerencial opcional."""
    st.title(title)
    if subtitle:
        st.markdown(f"<p style='color:{config.COLOR_TEXT_SECONDARY};font-size:1.05rem;margin-top:-0.5rem'>{subtitle}</p>", unsafe_allow_html=True)


def render_disclaimer(text: str = DISCLAIMER_GERAL) -> None:
    """Aviso metodológico padrão (linguagem preventiva, não diagnóstica)."""
    st.info(text, icon="ℹ️")


def render_kpi_row(items: Sequence[tuple[str, str, str | None]]) -> None:
    """Renderiza uma linha de cards de KPI a partir de (rótulo, valor, ajuda)."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label, value, help_text = (item + (None,))[:3]
        with col:
            with st.container(border=True):
                st.metric(label, value, help=help_text)


def render_scope_caption(is_filtered: bool) -> None:
    """Deixa explícito se os KPIs acima refletem a população total ou a seleção filtrada."""
    if is_filtered:
        st.caption("🔎 Valores calculados sobre a **seleção filtrada**.")
    else:
        st.caption("🌐 Valores calculados sobre a **população total** (sem filtros aplicados).")


def priority_badge_html(priority: str) -> str:
    color = config.PRIORITY_COLORS.get(priority, config.COLOR_TEXT_MUTED)
    return (
        f'<span style="background:{color};color:#ffffff;padding:2px 10px;border-radius:12px;'
        f'font-size:0.82rem;font-weight:600;white-space:nowrap">{priority}</span>'
    )


def radar_badge_html(perfil: str) -> str:
    color = config.RADAR_COLORS.get(perfil, config.COLOR_TEXT_MUTED)
    return (
        f'<span style="background:{color};color:#ffffff;padding:2px 10px;border-radius:12px;'
        f'font-size:0.82rem;font-weight:600;white-space:nowrap">{perfil}</span>'
    )


def render_badge_row(label: str, badge_html: str) -> None:
    st.markdown(f"**{label}:** {badge_html}", unsafe_allow_html=True)


def render_download_button(df: pd.DataFrame, filename: str, label: str = "⬇️ Baixar CSV") -> None:
    """Botão de download padrão para tabelas filtradas."""
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(label, data=csv_bytes, file_name=filename, mime="text/csv")


def friendly_error(message: str) -> None:
    """Mensagem de erro amigável — nunca traceback bruto para o usuário final."""
    st.error(f"⚠️ {message}")


def render_not_eligible_notice() -> None:
    st.warning(
        "Estudante fora do escopo validado do modelo. As Fases 8 e 9 apresentam "
        "indisponibilidade estrutural dos indicadores necessários.",
        icon="🚫",
    )


def scale_probability_columns(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Retorna cópia do DataFrame com colunas de fração (0-1) escaladas para 0-100.

    Usado apenas para exibição em tabela — o CSV de download deve sempre usar
    o DataFrame original (probabilidade como fração, não escondida).
    """
    out = df.copy()
    for column in columns:
        if column in out.columns:
            out[column] = out[column] * 100
    return out


def percent_column_config(columns: Sequence[str], labels: dict[str, str] | None = None) -> dict:
    """Configuração de colunas percentuais para st.dataframe (uma casa decimal, símbolo %)."""
    labels = labels or {}
    return {
        column: st.column_config.NumberColumn(labels.get(column, column), format="%.1f%%")
        for column in columns
    }


def multiselect_filter(df: pd.DataFrame, column: str, label: str, options: Iterable | None = None):
    """Filtro multiselect padrão; retorna a lista de opções selecionadas."""
    opts = sorted(df[column].dropna().unique().tolist()) if options is None else list(options)
    return st.multiselect(label, options=opts, default=[])


def apply_multiselect(df: pd.DataFrame, column: str, selected: list) -> pd.DataFrame:
    """Aplica um filtro multiselect a um DataFrame (sem seleção = sem filtro)."""
    if not selected:
        return df
    return df[df[column].isin(selected)]
