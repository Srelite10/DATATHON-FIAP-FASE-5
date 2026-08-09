"""Ranking 2025 — tabela operacional de priorização de acompanhamento."""

from __future__ import annotations

import streamlit as st

from src import components, config, data_loader

st.set_page_config(page_title="Ranking 2025", page_icon=config.APP_ICON, layout="wide")

try:
    df = data_loader.load_streamlit_data()
except data_loader.ArtifactError as exc:
    components.friendly_error(str(exc))
    st.stop()

components.render_page_header("Ranking 2025", "Priorização operacional dos estudantes elegíveis ao modelo.")
components.render_disclaimer(
    "O ranking reflete **prioridade de acompanhamento** — uma posição relativa dentro da população "
    "de referência 2025 — e não uma medida absoluta de risco."
)

# --------------------------------------------------------------------------- #
# Filtros
# --------------------------------------------------------------------------- #
f1, f2, f3, f4 = st.columns(4)
with f1:
    busca_ra = st.text_input("Buscar por RA", placeholder="ex.: RA-672")
with f2:
    fase_sel = st.multiselect("Fase", sorted(df["FASE_NUM"].unique()))
with f3:
    prioridade_sel = st.multiselect("Prioridade", config.PRIORITY_ORDER)
with f4:
    radar_sel = st.multiselect("Perfil Radar", config.RADAR_ORDER)

f5, f6, f7 = st.columns(3)
with f5:
    pedra_sel = st.multiselect("Pedra 2024", config.PEDRA_ORDEM)
with f6:
    apenas_risco_oculto = st.checkbox("Apenas risco oculto")
with f7:
    apenas_ponto_cego = st.checkbox("Apenas potenciais pontos cegos")

filtered = df.copy()
if busca_ra:
    filtered = filtered[filtered["RA"].str.contains(busca_ra.strip(), case=False, na=False)]
filtered = components.apply_multiselect(filtered, "FASE_NUM", fase_sel)
filtered = components.apply_multiselect(filtered, "PRIORIDADE_2025", prioridade_sel)
filtered = components.apply_multiselect(filtered, "PERFIL_RADAR", radar_sel)
filtered = components.apply_multiselect(filtered, "PEDRA_2024", pedra_sel)
if apenas_risco_oculto:
    filtered = filtered[filtered["RISCO_OCULTO"]]
if apenas_ponto_cego:
    filtered = filtered[filtered["PONTO_CEGO"]]

st.caption(f"{len(filtered)} de {len(df)} estudantes na seleção.")

# --------------------------------------------------------------------------- #
# Tabela
# --------------------------------------------------------------------------- #
table_cols = [
    "RA", "FASE_NUM", "PROB_RISCO_2025", "RANK_RISCO_2025", "PERCENTIL_RISCO_2025",
    "RANK_RISCO_FASE_2025", "PERCENTIL_RISCO_FASE_2025", "PRIORIDADE_2025", "PERFIL_RADAR", "PEDRA_2024",
]
table = filtered[table_cols].sort_values("RANK_RISCO_2025", ascending=True)
display_table = components.scale_probability_columns(table, ["PROB_RISCO_2025"])

st.dataframe(
    display_table,
    hide_index=True,
    width="stretch",
    height=460,
    column_config=components.percent_column_config(
        ["PROB_RISCO_2025", "PERCENTIL_RISCO_2025", "PERCENTIL_RISCO_FASE_2025"],
        {
            "PROB_RISCO_2025": "Probabilidade estimada",
            "PERCENTIL_RISCO_2025": "Percentil global",
            "PERCENTIL_RISCO_FASE_2025": "Percentil na fase",
            "RANK_RISCO_2025": "Rank global",
            "RANK_RISCO_FASE_2025": "Rank na fase",
        },
    ),
)
components.render_download_button(table, "ranking_2025_filtrado.csv")

st.divider()

# --------------------------------------------------------------------------- #
# Painel resumido por RA
# --------------------------------------------------------------------------- #
st.subheader("Painel do estudante")
opcoes_ra = filtered["RA"].tolist()
if opcoes_ra:
    ra_selecionado = st.selectbox("Selecione um RA para ver o resumo", opcoes_ra)
    registro = filtered.loc[filtered["RA"] == ra_selecionado].iloc[0]
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Fase", int(registro["FASE_NUM"]))
        c2.metric("Probabilidade estimada", f"{registro['PROB_RISCO_2025'] * 100:.1f}%")
        c3.metric("Prioridade", registro["PRIORIDADE_2025"])
        c4, c5, c6 = st.columns(3)
        c4.metric("Rank global", f"{int(registro['RANK_RISCO_2025'])} / {len(df)}")
        c5.metric("Rank na fase", int(registro["RANK_RISCO_FASE_2025"]))
        c6.metric("Pedra 2024", registro["PEDRA_2024"])
        components.render_badge_row("Perfil Radar", components.radar_badge_html(registro["PERFIL_RADAR"]))
else:
    st.info("Nenhum estudante corresponde aos filtros selecionados.")
