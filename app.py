"""Visão executiva — página inicial do painel Passos Mágicos."""

from __future__ import annotations

import streamlit as st

from src import charts, components, config, data_loader

st.set_page_config(page_title=config.APP_TITLE, page_icon=config.APP_ICON, layout="wide")

try:
    df = data_loader.load_streamlit_data()
    df_produto = data_loader.load_product_data()
    report = data_loader.validate_artifacts()
except data_loader.ArtifactError as exc:
    components.friendly_error(str(exc))
    st.stop()

if not report.ok:
    components.friendly_error(
        "Inconsistência encontrada entre os dados carregados e config/validacoes.json: "
        + "; ".join(report.issues)
    )
    st.stop()

components.render_page_header(
    config.APP_TITLE,
    "Qual é o cenário atual e onde a equipe deve olhar primeiro?",
)
components.render_disclaimer()

n_populacao = len(df_produto)
n_elegivel = len(df)
n_nao_elegivel = n_populacao - n_elegivel
n_muito_alta = int((df["PRIORIDADE_2025"] == "Muito alta").sum())
n_alta = int((df["PRIORIDADE_2025"] == "Alta").sum())
n_risco_oculto = int(df["RISCO_OCULTO"].sum())
n_ponto_cego = int(df["PONTO_CEGO"].sum())

st.subheader("Panorama institucional")
st.caption("🌐 KPIs abaixo sempre refletem a **população total** (1156 estudantes na base 2024, dos quais 1054 elegíveis para o modelo), independentemente dos filtros da barra lateral.")
components.render_kpi_row(
    [
        ("População 2024", f"{n_populacao:,}".replace(",", "."), "Estudantes com dados na base 2024 (elegíveis + não elegíveis)"),
        ("Elegíveis ao modelo", f"{n_elegivel:,}".replace(",", "."), "Fases 0 a 7 — escopo validado do modelo"),
        ("Não elegíveis", f"{n_nao_elegivel:,}".replace(",", "."), "Fases 8 e 9 — indicadores estruturalmente indisponíveis"),
        ("Prioridade muito alta", f"{n_muito_alta:,}".replace(",", ""), "Percentil global ou da fase ≥ 90"),
    ]
)
components.render_kpi_row(
    [
        ("Prioridade alta", f"{n_alta:,}".replace(",", ""), "Percentil global ou da fase ≥ 75"),
        ("Risco oculto", f"{n_risco_oculto:,}".replace(",", ""), "Sem defasagem atual + prioridade alta/muito alta"),
        ("Potenciais pontos cegos", f"{n_ponto_cego:,}".replace(",", ""), "Risco oculto + Pedra 2024 em Ametista ou Topázio"),
    ]
)

st.divider()

# --------------------------------------------------------------------------- #
# Filtros (afetam apenas as visualizações abaixo, não os KPIs institucionais)
# --------------------------------------------------------------------------- #
st.sidebar.header("Filtros")
st.sidebar.caption("Os filtros afetam os gráficos desta página — não os KPIs institucionais acima.")
fase_sel = st.sidebar.multiselect("Fase", sorted(df["FASE_NUM"].unique()))
prioridade_sel = st.sidebar.multiselect("Prioridade", config.PRIORITY_ORDER)
radar_sel = st.sidebar.multiselect("Perfil Radar", config.RADAR_ORDER)
pedra_sel = st.sidebar.multiselect("Pedra 2024", config.PEDRA_ORDEM)
defasagem_sel = st.sidebar.multiselect("Status defasagem atual", sorted(df["STATUS_DEFASAGEM_2024"].unique()))

filtered = df.copy()
filters_applied = any([fase_sel, prioridade_sel, radar_sel, pedra_sel, defasagem_sel])
filtered = components.apply_multiselect(filtered, "FASE_NUM", fase_sel)
filtered = components.apply_multiselect(filtered, "PRIORIDADE_2025", prioridade_sel)
filtered = components.apply_multiselect(filtered, "PERFIL_RADAR", radar_sel)
filtered = components.apply_multiselect(filtered, "PEDRA_2024", pedra_sel)
filtered = components.apply_multiselect(filtered, "STATUS_DEFASAGEM_2024", defasagem_sel)

st.subheader("Onde olhar primeiro")
components.render_scope_caption(filters_applied)

if filtered.empty:
    st.warning("Nenhum estudante corresponde aos filtros selecionados.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(charts.priority_distribution_bar(filtered), width="stretch")
    with col2:
        st.plotly_chart(charts.radar_profile_bar(filtered), width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(charts.score_distribution_histogram(filtered), width="stretch")
    with col4:
        st.plotly_chart(charts.score_by_phase_bar(filtered), width="stretch")

    st.plotly_chart(charts.risco_oculto_by_phase_bar(filtered), width="stretch")

st.divider()
st.markdown(
    "**Próximos passos sugeridos:** explore o **Radar Preventivo** para identificar risco oculto e "
    "potenciais pontos cegos, o **Ranking 2025** para priorização operacional, o **Simulador Individual** "
    "para novos casos, a **Predição em Lote** para processar arquivos externos, a **Trajetória e "
    "Efetividade** para contexto histórico, e **Modelo e Metodologia** para transparência técnica."
)
