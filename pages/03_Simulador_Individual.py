"""Simulador Individual — executa a pipeline real do modelo para um novo caso."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import charts, components, config, data_loader, model_service, radar, scoring

st.set_page_config(page_title="Simulador Individual", page_icon=config.APP_ICON, layout="wide")

try:
    df_ref = data_loader.load_streamlit_data()
    regras_produto = data_loader.load_regras_produto()
    bundle = model_service.load_model_bundle()
except (data_loader.ArtifactError, model_service.ModelServiceError) as exc:
    components.friendly_error(str(exc))
    st.stop()

components.render_page_header("Simulador Individual", "Calcule o score prospectivo de um estudante a partir dos indicadores da Fase.")
components.render_disclaimer()

features = model_service.get_features(bundle)
thresholds = scoring.get_priority_thresholds(regras_produto)
pedras_ponto_cego = radar.get_pedras_ponto_cego(regras_produto)

st.subheader("Indicadores usados pelo modelo")
st.caption("Somente estas sete variáveis entram no cálculo da probabilidade estimada.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    fase_num = st.selectbox("FASE_NUM", options=list(range(0, 8)), index=1)
with c2:
    tempo_programa = st.number_input("TEMPO_PROGRAMA (anos no programa)", min_value=0, max_value=10, value=1, step=1)
with c3:
    ida = st.number_input("IDA", min_value=0.0, max_value=10.0, value=6.0, step=0.1)
with c4:
    ieg = st.number_input("IEG", min_value=0.0, max_value=10.0, value=7.0, step=0.1)

c5, c6, c7 = st.columns(3)
with c5:
    iaa_modelo = st.number_input("IAA_MODELO", min_value=0.0, max_value=10.0, value=7.5, step=0.1)
with c6:
    ips = st.number_input("IPS", min_value=0.0, max_value=10.0, value=6.5, step=0.1)
with c7:
    ipv = st.number_input("IPV", min_value=0.0, max_value=10.0, value=6.5, step=0.1)

with st.expander("Contexto atual (opcional — não entra no cálculo do score)"):
    st.caption(
        "Estes campos são apenas contexto gerencial. DEFASAGEM_ANALISE, IPP, INDE e Pedra "
        "**não são usados em predict_proba**."
    )
    ctx1, ctx2, ctx3, ctx4 = st.columns(4)
    with ctx1:
        tem_defasagem_atual = st.selectbox("Defasagem atual?", options=["Sem defasagem", "Com defasagem"])
    with ctx2:
        ipp_ctx = st.number_input("IPP (contexto)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    with ctx3:
        inde_ctx = st.number_input("INDE (contexto)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    with ctx4:
        pedra_ctx = st.selectbox("Pedra (contexto)", options=config.PEDRA_ORDEM)

calcular = st.button("Calcular score prospectivo", type="primary")

if calcular:
    X = pd.DataFrame(
        [
            {
                "FASE_NUM": fase_num,
                "TEMPO_PROGRAMA": tempo_programa,
                "IDA": ida,
                "IEG": ieg,
                "IAA_MODELO": iaa_modelo,
                "IPS": ips,
                "IPV": ipv,
            }
        ]
    )[features]

    try:
        proba = model_service.predict_risk(bundle, X)[0]
    except model_service.ModelServiceError as exc:
        components.friendly_error(str(exc))
        st.stop()

    percentil_global = scoring.calculate_global_percentile(proba, df_ref["PROB_RISCO_2025"])
    rank_global = scoring.calculate_rank(proba, df_ref["PROB_RISCO_2025"])
    percentil_fase = scoring.calculate_phase_percentile(proba, fase_num, df_ref)
    rank_fase = scoring.calculate_phase_rank(proba, fase_num, df_ref)
    n_fase = int((df_ref["FASE_NUM"] == fase_num).sum())
    prioridade = scoring.classify_priority(percentil_global, percentil_fase, thresholds)

    st.divider()
    st.subheader("Resultado")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Probabilidade estimada", scoring.format_probability(proba))
    r2.metric("Percentil global", f"{percentil_global:.1f}")
    r3.metric("Rank global aproximado", f"{rank_global} / {len(df_ref)}")
    r4.metric("Prioridade gerencial", prioridade)

    r5, r6 = st.columns(2)
    r5.metric("Percentil na fase", f"{percentil_fase:.1f}" if percentil_fase is not None else "—")
    r6.metric("Rank aproximado na fase", f"{rank_fase} / {n_fase}" if rank_fase is not None else "—")

    components.render_badge_row("Prioridade de acompanhamento", components.priority_badge_html(prioridade))

    st.plotly_chart(
        charts.phase_reference_histogram(df_ref.loc[df_ref["FASE_NUM"] == fase_num, "PROB_RISCO_2025"], proba),
        width="stretch",
    )

    # Radar (se contexto informado)
    tem_defasagem_bool = tem_defasagem_atual == "Com defasagem"
    perfil_radar = radar.classify_radar(tem_defasagem_bool, prioridade)
    is_ponto_cego = radar.is_ponto_cego(perfil_radar, pedra_ctx, pedras_ponto_cego)

    st.divider()
    st.subheader("Perfil no Radar Preventivo (com base no contexto informado)")
    components.render_badge_row("Perfil", components.radar_badge_html(perfil_radar))
    if perfil_radar == radar.RISCO_OCULTO:
        st.warning(
            "Sinal de **risco oculto**: sem defasagem atual, mas prioridade prospectiva "
            "alta/muito alta segundo o modelo.",
            icon="🔍",
        )
    if is_ponto_cego:
        st.error(
            "Sinal de **potencial ponto cego**: risco oculto com Pedra em Ametista/Topázio — "
            "vale considerar para triagem preventiva.",
            icon="🎯",
        )
