"""Modelo e Metodologia — transparência técnica para avaliação externa."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import components, config, data_loader, model_service

st.set_page_config(page_title="Modelo e Metodologia", page_icon=config.APP_ICON, layout="wide")

try:
    metricas = data_loader.load_metricas_modelo()
    metadados_bundle = data_loader.load_metadados_bundle()
    bundle = model_service.load_model_bundle()
except (data_loader.ArtifactError, model_service.ModelServiceError) as exc:
    components.friendly_error(str(exc))
    st.stop()

components.render_page_header("Modelo e Metodologia", "Como o score prospectivo foi construído, validado e deve ser interpretado.")

st.subheader("Alvo e protocolo temporal")
st.markdown(f"**Alvo (target):** `{metricas['target']}`")
p1, p2, p3 = st.columns(3)
p1.metric("Desenvolvimento", metricas["protocolo"]["desenvolvimento"])
p2.metric("Teste temporal independente", metricas["protocolo"]["teste_temporal"])
p3.metric("Inferência prospectiva", metricas["protocolo"]["inferencia"])
st.caption(
    "O modelo foi treinado com dados 2022→2023, validado de forma independente com 2023→2024 "
    "(dados que o modelo nunca viu no treinamento) e aplicado prospectivamente a 2024→2025."
)

st.divider()
st.subheader("Modelo e features")
st.markdown(f"**Algoritmo:** {metricas['modelo']}")
st.markdown("**Features utilizadas (nesta ordem, vindas do bundle):**")
st.code(", ".join(model_service.get_features(bundle)))
st.markdown(f"**Fases elegíveis:** {model_service.get_fases_elegiveis(bundle)}")
st.markdown(f"**Observações de treinamento:** {metricas['treinamento_final']['observacoes_aluno_ano']} pares aluno-ano · {metricas['treinamento_final']['estudantes_unicos']} estudantes únicos")

st.divider()
st.subheader("Métricas — teste temporal independente (2023 → 2024)")
st.caption("Threshold de referência para estas métricas: 0.50 (padrão de classificação binária).")
t = metricas["teste_temporal_threshold_050"]
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("ROC-AUC", f"{t['roc_auc']:.4f}")
m2.metric("PR-AUC", f"{t['pr_auc']:.4f}")
m3.metric("Accuracy", f"{t['accuracy']:.4f}")
m4.metric("Precision", f"{t['precision']:.4f}")
m5.metric("Recall", f"{t['recall']:.4f}")
m6.metric("F1", f"{t['f1']:.4f}")

st.markdown("**Calibração (Brier Score — quanto menor, melhor):**")
c1, c2 = st.columns(2)
c1.metric("Desenvolvimento (OOF)", f"{metricas['calibracao']['desenvolvimento_oof']['brier_score']:.4f}")
c2.metric("Teste temporal", f"{metricas['calibracao']['teste_temporal']['brier_score']:.4f}")
st.caption(
    f"Prevalência real no teste temporal: {metricas['calibracao']['teste_temporal']['prevalencia']:.4f} · "
    f"Probabilidade média prevista: {metricas['calibracao']['teste_temporal']['probabilidade_media']:.4f}"
)

st.divider()
st.subheader("Threshold de desenvolvimento (0.55) — por que não é regra operacional")
st.markdown(
    f"O threshold **{metricas['threshold_desenvolvimento']}** foi definido durante o desenvolvimento do modelo "
    "para maximizar uma métrica de classificação binária, mas **não se mostrou estável temporalmente** "
    "quando aplicado ao teste independente 2023→2024:"
)
t55 = metricas["teste_threshold_055"]
th1, th2, th3, th4 = st.columns(4)
th1.metric("Accuracy (0.55)", f"{t55['accuracy']:.4f}")
th2.metric("Precision (0.55)", f"{t55['precision']:.4f}")
th3.metric("Recall (0.55)", f"{t55['recall']:.4f}")
th4.metric("F1 (0.55)", f"{t55['f1']:.4f}")
st.warning(
    "Por isso, a **probabilidade estimada** é a saída principal do produto, e a priorização "
    "operacional usa **percentis** (posição relativa na população), não um corte fixo de threshold.",
    icon="⚖️",
)

st.divider()
st.subheader("Coeficientes — associações preditivas, não causalidade")
coefs = metricas["coeficientes_desenvolvimento"]
coef_df = pd.DataFrame(sorted(coefs.items(), key=lambda kv: kv[1]), columns=["Feature", "Coeficiente (log-odds)"])
st.dataframe(coef_df, hide_index=True, width="stretch")
st.caption(
    "Coeficientes de uma regressão logística indicam **associação estatística** com o alvo, na escala "
    "log-odds, controlando pelas demais variáveis do modelo — não implicam relação de causa e efeito."
)

st.divider()
st.subheader("Limitações")
st.markdown(
    "- **Fases 8 e 9 não são elegíveis**: apresentam indisponibilidade estrutural dos indicadores "
    "necessários; não há imputação que resolva uma ausência estrutural (diferente de missing pontual "
    "dentro da população elegível, que a pipeline trata via imputação por mediana).\n"
    "- **Threshold de desenvolvimento (0.55)** não é uma regra universal de risco — não se mostrou "
    "estável no teste temporal independente.\n"
    "- **Prioridade é gerencial**, baseada em ranking/percentil dentro da população de referência 2025 — "
    "não é uma probabilidade absoluta de desfecho.\n"
    "- **Sem retreinamento ou recalibração** dentro do Streamlit: a pipeline usada é exatamente a "
    "armazenada no bundle `.joblib`.\n"
)

st.error(
    "Os resultados de 2025 são **prospectivos**. Como o desfecho de 2025 ainda não está disponível, "
    "não existem métricas reais de acerto para essas previsões.",
    icon="🚨",
)

with st.expander("Metadados técnicos do bundle"):
    st.json(metadados_bundle)
