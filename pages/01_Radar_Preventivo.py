"""Radar Preventivo — o diferencial do produto: da reação à antecipação."""

from __future__ import annotations

import streamlit as st

from src import charts, components, config, data_loader, radar

st.set_page_config(page_title="Radar Preventivo", page_icon=config.APP_ICON, layout="wide")

try:
    df = data_loader.load_streamlit_data()
    regras_produto = data_loader.load_regras_produto()
    radar_cfg = data_loader.load_radar_preventivo()
except data_loader.ArtifactError as exc:
    components.friendly_error(str(exc))
    st.stop()

components.render_page_header(
    "Radar Preventivo",
    "Da reação à antecipação: estudantes que merecem atenção antes que uma nova defasagem seja observada.",
)
components.render_disclaimer(
    "O Radar Preventivo combina a situação educacional **atual** (defasagem observada) com a "
    "**prioridade prospectiva** (derivada da probabilidade estimada pelo modelo) em quatro perfis "
    "de acompanhamento. É um instrumento de **triagem preventiva**, não de diagnóstico."
)

# --------------------------------------------------------------------------- #
# Quatro cards de perfil
# --------------------------------------------------------------------------- #
counts = df["PERFIL_RADAR"].value_counts()
cols = st.columns(4)
descricoes = {
    radar.CRITICO_PERSISTENTE: "Já possui defasagem e mantém prioridade alta/muito alta.",
    radar.RISCO_OCULTO: "Sem defasagem hoje, mas com sinais associados a prioridade futura elevada.",
    radar.ATENCAO_ATUAL: "Possui defasagem atual, com menor prioridade prospectiva.",
    radar.ESTAVEL_MENOR_PRIORIDADE: "Sem defasagem e sem sinais de prioridade futura elevada.",
}
for col, perfil in zip(cols, config.RADAR_ORDER):
    with col:
        with st.container(border=True):
            st.markdown(components.radar_badge_html(perfil), unsafe_allow_html=True)
            st.markdown(f"<h2 style='margin:0.3rem 0 0 0'>{int(counts.get(perfil, 0))}</h2>", unsafe_allow_html=True)
            st.caption(descricoes[perfil])

st.divider()

# --------------------------------------------------------------------------- #
# Destaque: Risco oculto e Potencial ponto cego
# --------------------------------------------------------------------------- #
n_risco_oculto = int(df["RISCO_OCULTO"].sum())
n_ponto_cego = int(df["PONTO_CEGO"].sum())
highlight_col1, highlight_col2 = st.columns(2)
with highlight_col1:
    with st.container(border=True):
        st.markdown(f"### {components.radar_badge_html('Risco oculto')}", unsafe_allow_html=True)
        st.markdown(f"<h1 style='margin:0'>{n_risco_oculto}</h1>", unsafe_allow_html=True)
        st.write(
            "Estudantes **sem defasagem observada em 2024**, mas com prioridade prospectiva "
            "**alta ou muito alta** segundo o score do modelo — o principal diferencial deste painel: "
            "sinalizar atenção antes que uma nova defasagem apareça."
        )
with highlight_col2:
    with st.container(border=True):
        st.markdown("### 🔍 Potencial ponto cego")
        st.markdown(f"<h1 style='margin:0'>{n_ponto_cego}</h1>", unsafe_allow_html=True)
        st.write(
            "Subconjunto do risco oculto cuja **Pedra 2024 é Ametista ou Topázio** — portanto, fora "
            "das duas Pedras inferiores. Mesmo aparentando bom desempenho institucional, concentram "
            "prioridade prospectiva elevada. Um instrumento de triagem preventiva, não um diagnóstico."
        )

st.divider()

# --------------------------------------------------------------------------- #
# Composição em quadrantes
# --------------------------------------------------------------------------- #
st.subheader("Radar Preventivo em quadrantes")
st.plotly_chart(charts.radar_quadrant_heatmap(df), width="stretch")
st.caption(
    "Cada quadrante cruza defasagem atual (linhas) com prioridade prospectiva (colunas). "
    "A cor representa apenas a contagem de estudantes — não uma métrica contínua."
)

st.divider()

# --------------------------------------------------------------------------- #
# DNA do Risco Oculto
# --------------------------------------------------------------------------- #
st.subheader("DNA do Risco Oculto")
dna_col, tri_col = st.columns(2)
with dna_col:
    st.plotly_chart(charts.dna_diff_bar(radar_cfg["dna_diferencas_z"]), width="stretch")
    st.caption("Os valores mostram diferenças relativas aos pares da mesma fase.")
    st.caption(
        "Como essas variáveis participam do modelo, esta análise explica o score e não "
        "constitui validação independente."
    )
with tri_col:
    st.plotly_chart(charts.triangulacao_bar(radar_cfg["triangulacao"]), width="stretch")
    st.caption("Triangulação com indicadores fora do modelo (IPP e INDE 2024) — apenas contexto gerencial.")

st.plotly_chart(charts.pedra_sem_defasagem_bar(radar_cfg["pedra_sem_defasagem_pct_risco_oculto"]), width="stretch")
st.info(radar_cfg.get("storytelling", ""), icon="💡")

st.divider()

# --------------------------------------------------------------------------- #
# Tabela de estudantes
# --------------------------------------------------------------------------- #
st.subheader("Estudantes")
filtro_col1, filtro_col2, filtro_col3, filtro_col4 = st.columns(4)
with filtro_col1:
    perfil_sel = st.multiselect("Perfil Radar", config.RADAR_ORDER, default=[])
with filtro_col2:
    fase_sel = st.multiselect("Fase", sorted(df["FASE_NUM"].unique()), default=[])
with filtro_col3:
    pedra_sel = st.multiselect("Pedra 2024", config.PEDRA_ORDEM, default=[])
with filtro_col4:
    apenas_ponto_cego = st.checkbox("Apenas potenciais pontos cegos")

table = df.copy()
table = components.apply_multiselect(table, "PERFIL_RADAR", perfil_sel)
table = components.apply_multiselect(table, "FASE_NUM", fase_sel)
table = components.apply_multiselect(table, "PEDRA_2024", pedra_sel)
if apenas_ponto_cego:
    table = table[table["PONTO_CEGO"]]

table_cols = [
    "RA", "FASE_NUM", "DEFASAGEM_ANALISE", "PEDRA_2024", "INDE_2024", "IPP", "IDA", "IEG", "IPV",
    "PROB_RISCO_2025", "PERCENTIL_RISCO_2025", "PERCENTIL_RISCO_FASE_2025", "PRIORIDADE_2025",
    "PERFIL_RADAR", "PONTO_CEGO",
]
table = table[table_cols].sort_values("PROB_RISCO_2025", ascending=False)
display_table = components.scale_probability_columns(table, ["PROB_RISCO_2025"])

st.dataframe(
    display_table,
    hide_index=True,
    width="stretch",
    column_config=components.percent_column_config(
        ["PROB_RISCO_2025", "PERCENTIL_RISCO_2025", "PERCENTIL_RISCO_FASE_2025"],
        {
            "PROB_RISCO_2025": "Probabilidade estimada",
            "PERCENTIL_RISCO_2025": "Percentil global",
            "PERCENTIL_RISCO_FASE_2025": "Percentil na fase",
        },
    ),
)
st.caption(f"{len(table)} estudante(s) na seleção — ordenado por probabilidade estimada (decrescente).")
components.render_download_button(table, "radar_preventivo_estudantes.csv")
