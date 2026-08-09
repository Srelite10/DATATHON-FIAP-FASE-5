"""Construtores de gráficos Plotly reutilizáveis.

Centraliza estilo (superfície clara, grade recessiva, marcas finas, rótulos
diretos) e a paleta validada em ``src/config.py`` para que nenhuma página
escolha cores ou layout "no olho". Cada função recebe dados já no formato de
negócio (DataFrame/Series/dict) e devolve uma ``go.Figure`` pronta para
``st.plotly_chart``.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src import config

_FONT_FAMILY = "system-ui, -apple-system, Segoe UI, sans-serif"


def _apply_layout(fig: go.Figure, height: int = 360, show_legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        plot_bgcolor=config.COLOR_SURFACE,
        paper_bgcolor=config.COLOR_SURFACE,
        font=dict(family=_FONT_FAMILY, color=config.COLOR_TEXT_PRIMARY, size=13),
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family=_FONT_FAMILY),
    )
    fig.update_xaxes(gridcolor=config.COLOR_GRIDLINE, zerolinecolor=config.COLOR_BASELINE, linecolor=config.COLOR_BASELINE)
    fig.update_yaxes(gridcolor=config.COLOR_GRIDLINE, zerolinecolor=config.COLOR_BASELINE, linecolor=config.COLOR_BASELINE)
    return fig


def priority_distribution_bar(df: pd.DataFrame, priority_col: str = "PRIORIDADE_2025") -> go.Figure:
    """Distribuição de estudantes por prioridade de acompanhamento."""
    counts = df[priority_col].value_counts().reindex(config.PRIORITY_ORDER).fillna(0).astype(int)
    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=[config.PRIORITY_COLORS[p] for p in counts.index],
            text=counts.values,
            textposition="outside",
        )
    )
    fig.update_layout(title="Distribuição por prioridade de acompanhamento")
    fig.update_yaxes(title="Estudantes")
    return _apply_layout(fig, show_legend=False)


def radar_profile_bar(df: pd.DataFrame, profile_col: str = "PERFIL_RADAR") -> go.Figure:
    """Distribuição de estudantes pelos quatro perfis do Radar Preventivo."""
    counts = df[profile_col].value_counts().reindex(config.RADAR_ORDER).fillna(0).astype(int)
    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=[config.RADAR_COLORS[p] for p in counts.index],
            text=counts.values,
            textposition="outside",
        )
    )
    fig.update_layout(title="Distribuição pelos perfis do Radar Preventivo")
    fig.update_yaxes(title="Estudantes")
    return _apply_layout(fig, show_legend=False)


def score_distribution_histogram(df: pd.DataFrame, score_col: str = "PROB_RISCO_2025") -> go.Figure:
    """Histograma da probabilidade estimada (score prospectivo)."""
    fig = go.Figure(
        go.Histogram(
            x=df[score_col],
            marker_color=config.COLOR_SEQUENTIAL,
            nbinsx=30,
            xbins=dict(start=0, end=1),
        )
    )
    fig.update_layout(title="Distribuição dos scores prospectivos (probabilidade estimada)")
    fig.update_xaxes(title="Probabilidade estimada", tickformat=".0%")
    fig.update_yaxes(title="Estudantes")
    return _apply_layout(fig, show_legend=False)


def score_by_phase_bar(df: pd.DataFrame, score_col: str = "PROB_RISCO_2025", phase_col: str = "FASE_NUM") -> go.Figure:
    """Score médio e mediano por fase."""
    agg = df.groupby(phase_col)[score_col].agg(["mean", "median"]).reset_index().sort_values(phase_col)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=agg[phase_col], y=agg["mean"], name="Média", marker_color=config.COLOR_SEQUENTIAL)
    )
    fig.add_trace(
        go.Scatter(
            x=agg[phase_col],
            y=agg["median"],
            name="Mediana",
            mode="markers",
            marker=dict(color=config.COLOR_TEXT_PRIMARY, size=9, symbol="diamond"),
        )
    )
    fig.update_layout(title="Score prospectivo médio e mediano por fase")
    fig.update_xaxes(title="Fase", dtick=1)
    fig.update_yaxes(title="Probabilidade estimada", tickformat=".0%")
    return _apply_layout(fig)


def risco_oculto_by_phase_bar(df: pd.DataFrame, phase_col: str = "FASE_NUM") -> go.Figure:
    """Contagem de risco oculto por fase."""
    agg = df.loc[df["PERFIL_RADAR"] == "Risco oculto"].groupby(phase_col).size().reindex(
        sorted(df[phase_col].unique()), fill_value=0
    )
    fig = go.Figure(
        go.Bar(
            x=agg.index,
            y=agg.values,
            marker_color=config.RADAR_COLORS["Risco oculto"],
            text=agg.values,
            textposition="outside",
        )
    )
    fig.update_layout(title="Risco oculto por fase")
    fig.update_xaxes(title="Fase", dtick=1)
    fig.update_yaxes(title="Estudantes em risco oculto")
    return _apply_layout(fig, show_legend=False)


def radar_quadrant_heatmap(df: pd.DataFrame) -> go.Figure:
    """Composição 2x2 do Radar Preventivo: defasagem atual x prioridade prospectiva.

    Usa uma grade de calor (cor sequencial = contagem) em vez de um dispersão
    por estudante, para não sugerir que defasagem e prioridade são eixos
    contínuos e comparáveis ponto a ponto.
    """
    prioridade_alta = df["PRIORIDADE_2025"].isin(["Alta", "Muito alta"])
    tem_defasagem = df["DEFASAGEM_ANALISE"] < 0

    z = [
        [int((tem_defasagem & prioridade_alta).sum()), int((tem_defasagem & ~prioridade_alta).sum())],
        [int((~tem_defasagem & prioridade_alta).sum()), int((~tem_defasagem & ~prioridade_alta).sum())],
    ]
    labels = [
        ["Crítico persistente", "Atenção atual"],
        ["Risco oculto", "Estável / menor prioridade"],
    ]
    text = [[f"<b>{labels[r][c]}</b><br>{z[r][c]} estudantes" for c in range(2)] for r in range(2)]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=["Prioridade alta/muito alta", "Prioridade moderada/reduzida"],
            y=["Com defasagem atual", "Sem defasagem atual"],
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=13, color=config.COLOR_TEXT_PRIMARY),
            colorscale=[[0, config.SEQUENTIAL_RAMP[0]], [1, config.SEQUENTIAL_RAMP[-2]]],
            showscale=False,
            xgap=3,
            ygap=3,
        )
    )
    fig.update_layout(title="Radar Preventivo — composição por quadrante")
    fig.update_yaxes(autorange="reversed")
    return _apply_layout(fig, height=320, show_legend=False)


def dna_diff_bar(dna: dict[str, float]) -> go.Figure:
    """Diferenças Z do risco oculto em relação aos pares da mesma fase (barra horizontal divergente)."""
    ordered = sorted(dna.items(), key=lambda kv: kv[1])
    labels = [k for k, _ in ordered]
    values = [v for _, v in ordered]
    colors = [config.COLOR_DIVERGING_NEG if v < 0 else config.COLOR_DIVERGING_POS for v in values]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.2f}" for v in values],
            textposition="outside",
        )
    )
    fig.add_vline(x=0, line_color=config.COLOR_BASELINE, line_width=1)
    fig.update_layout(title="DNA do Risco Oculto — diferença Z frente aos pares da fase")
    fig.update_xaxes(title="Diferença Z (pares da mesma fase)")
    return _apply_layout(fig, height=320, show_legend=False)


def triangulacao_bar(triangulacao: dict[str, dict[str, float]]) -> go.Figure:
    """Compara IPP e INDE 2024 entre risco oculto e estudantes estáveis."""
    indicadores = list(triangulacao.keys())
    risco_oculto_vals = [triangulacao[k]["media_risco_oculto"] for k in indicadores]
    estavel_vals = [triangulacao[k]["media_estavel"] for k in indicadores]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=indicadores,
            y=risco_oculto_vals,
            name="Risco oculto",
            marker_color=config.RADAR_COLORS["Risco oculto"],
            text=[f"{v:.2f}" for v in risco_oculto_vals],
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Bar(
            x=indicadores,
            y=estavel_vals,
            name="Estável / menor prioridade",
            marker_color=config.RADAR_COLORS["Estável / menor prioridade"],
            text=[f"{v:.2f}" for v in estavel_vals],
            textposition="outside",
        )
    )
    fig.update_layout(title="Triangulação — IPP e INDE 2024 (risco oculto x estável)", barmode="group")
    return _apply_layout(fig, height=340)


def pedra_sem_defasagem_bar(pct_por_pedra: dict[str, float]) -> go.Figure:
    """% de estudantes sem defasagem, por Pedra 2024, classificados como risco oculto."""
    pedras = [p for p in config.PEDRA_ORDEM if p in pct_por_pedra]
    values = [pct_por_pedra[p] for p in pedras]
    fig = go.Figure(
        go.Bar(
            x=pedras,
            y=values,
            marker_color=[config.PEDRA_ORDINAL_RAMP[p] for p in pedras],
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(title="Concentração de risco oculto por Pedra 2024 (entre os sem defasagem)")
    fig.update_yaxes(title="% classificados como risco oculto")
    return _apply_layout(fig, height=320, show_legend=False)


def movement_distribution_bar(saldo: dict[str, float], title: str = "Movimento de Pedra 2022 → 2024") -> go.Figure:
    """Distribuição percentual de avanço/manutenção/recuo."""
    labels = [f"{m}" for m in config.MOVEMENT_ORDER]
    keys = {"Avanço": "avanco_pct", "Manutenção": "manutencao_pct", "Recuo": "recuo_pct"}
    values = [saldo[keys[m]] for m in config.MOVEMENT_ORDER]
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=[config.MOVEMENT_COLORS[m] for m in config.MOVEMENT_ORDER],
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(title=title)
    fig.update_yaxes(title="% dos estudantes")
    return _apply_layout(fig, height=320, show_legend=False)


def transition_matrix_heatmap(df: pd.DataFrame, col_from: str = "PEDRA_2022", col_to: str = "PEDRA_2024") -> go.Figure:
    """Matriz de transição de Pedra (2022 -> 2024)."""
    ordem = [p for p in config.PEDRA_ORDEM]
    matrix = pd.crosstab(df[col_from], df[col_to]).reindex(index=ordem, columns=ordem, fill_value=0)
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            text=matrix.values,
            texttemplate="%{text}",
            textfont=dict(size=12),
            colorscale=[[0, config.SEQUENTIAL_RAMP[0]], [1, config.SEQUENTIAL_RAMP[-1]]],
            xgap=2,
            ygap=2,
            colorbar=dict(title="Estudantes"),
        )
    )
    fig.update_layout(title="Matriz de transição de Pedra (2022 → 2024)")
    fig.update_xaxes(title="Pedra 2024")
    fig.update_yaxes(title="Pedra 2022")
    return _apply_layout(fig, height=380, show_legend=False)


def phase_reference_histogram(reference_scores: pd.Series, student_score: float | None = None) -> go.Figure:
    """Histograma de referência da fase, com marcador opcional do estudante simulado."""
    fig = go.Figure(
        go.Histogram(
            x=reference_scores,
            marker_color=config.COLOR_SEQUENTIAL,
            nbinsx=20,
            xbins=dict(start=0, end=1),
            name="Estudantes da fase",
        )
    )
    if student_score is not None:
        fig.add_vline(
            x=student_score,
            line_color=config.RADAR_COLORS["Risco oculto"],
            line_width=3,
            annotation_text="Score simulado",
            annotation_position="top",
        )
    fig.update_layout(title="Comparação com a distribuição de referência da fase")
    fig.update_xaxes(title="Probabilidade estimada", tickformat=".0%")
    fig.update_yaxes(title="Estudantes")
    return _apply_layout(fig, show_legend=False)
