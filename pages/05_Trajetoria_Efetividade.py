"""Trajetória e Efetividade — evolução das Pedras 2022-2024 e sinais de efetividade."""

from __future__ import annotations

import streamlit as st

from src import charts, components, config, data_loader

st.set_page_config(page_title="Trajetória e Efetividade", page_icon=config.APP_ICON, layout="wide")

try:
    trajetoria = data_loader.load_trajectory_data()
    efetividade = data_loader.load_efetividade()
except data_loader.ArtifactError as exc:
    components.friendly_error(str(exc))
    st.stop()

components.render_page_header("Trajetória e Efetividade", "O que a evolução histórica das Pedras (2022-2024) mostra sobre o programa.")
st.info("Análise observacional — não permite atribuição causal.", icon="ℹ️")

st.caption(f"Painel com histórico completo de Pedra em 2022, 2023 e 2024: {efetividade['painel_completo_2022_2024']} estudantes.")

st.subheader("Saldo geral 2022 → 2024")
saldo = efetividade["saldo_2022_2024"]
k1, k2, k3 = st.columns(3)
k1.metric("Avanço", f"{saldo['avanco_pct']:.1f}%")
k2.metric("Manutenção", f"{saldo['manutencao_pct']:.1f}%")
k3.metric("Recuo", f"{saldo['recuo_pct']:.1f}%")
st.plotly_chart(charts.movement_distribution_bar(saldo, "Movimento de Pedra — população completa (2022 → 2024)"), width="stretch")

st.divider()
st.subheader("Matriz de transição de Pedra (2022 → 2024)")
st.plotly_chart(charts.transition_matrix_heatmap(trajetoria), width="stretch")
st.caption("Ordem das Pedras: Quartzo < Ágata < Ametista < Topázio.")

st.divider()
st.subheader("Subgrupo inicial: Ágata + Ametista")
ag = efetividade["agata_ametista"]
sg1, sg2, sg3, sg4 = st.columns(4)
sg1.metric("Estudantes", ag["n"])
sg2.metric("Avanço", f"{ag['avanco_pct']:.1f}%")
sg3.metric("Manutenção", f"{ag['manutencao_pct']:.1f}%")
sg4.metric("Recuo", f"{ag['recuo_pct']:.1f}%")
st.plotly_chart(
    charts.movement_distribution_bar(ag, "Movimento de Pedra — subgrupo Ágata + Ametista (2022 → 2024)"),
    width="stretch",
)

st.markdown(
    f"**Teste de Wilcoxon (delta ordinal de Pedra, subgrupo Ágata + Ametista):** "
    f"estatística = {ag['wilcoxon_estatistica']:.1f} · p-valor = {ag['wilcoxon_p_valor']:.4f} "
    f"· delta médio = {ag['delta_medio']:.4f} · delta mediano = {ag['delta_mediano']:.1f}"
)

st.divider()
st.subheader("Conclusão")
st.warning(
    "Os dados sugerem efetividade heterogênea. Há sinais positivos para alguns grupos, "
    "mas não há evidência estatística suficiente para afirmar melhora ordinal sistemática "
    "de toda a população.",
    icon="⚖️",
)
st.caption(f"Conclusão registrada em config/efetividade.json: \"{efetividade['conclusao']}\"")
