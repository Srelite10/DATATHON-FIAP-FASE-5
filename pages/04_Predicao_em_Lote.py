"""Predição em Lote — upload de CSV externo para cálculo de score em massa."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import components, config, data_loader, model_service, radar, scoring

st.set_page_config(page_title="Predição em Lote", page_icon=config.APP_ICON, layout="wide")

MOTIVO_NAO_ELEGIVEL = "Fase fora do escopo validado do modelo e/ou ausência estrutural de indicadores"

try:
    df_ref = data_loader.load_streamlit_data()
    regras_produto = data_loader.load_regras_produto()
    bundle = model_service.load_model_bundle()
except (data_loader.ArtifactError, model_service.ModelServiceError) as exc:
    components.friendly_error(str(exc))
    st.stop()

components.render_page_header("Predição em Lote", "Envie um CSV com estudantes para calcular score, percentil e prioridade em massa.")
components.render_disclaimer()

features = model_service.get_features(bundle)
thresholds = scoring.get_priority_thresholds(regras_produto)
pedras_ponto_cego = radar.get_pedras_ponto_cego(regras_produto)

st.caption(
    "Colunas obrigatórias: " + ", ".join(features) + ". "
    "Coluna `RA` é opcional. Colunas opcionais `DEFASAGEM_ANALISE` e `PEDRA_2024` habilitam o "
    "cálculo do Radar Preventivo e do potencial ponto cego."
)
st.caption(
    "Se enviada, a coluna `PEDRA_2024` deve usar exatamente os valores "
    f"{', '.join(config.PEDRA_ORDEM)} (com acentuação) para que o potencial ponto cego seja identificado."
)

arquivo = st.file_uploader("Arquivo CSV", type=["csv"])

if arquivo is None:
    st.info("Envie um arquivo CSV para iniciar o processamento.", icon="📄")
    st.stop()

try:
    upload_df = pd.read_csv(arquivo)
except Exception:
    components.friendly_error("Não foi possível ler o arquivo enviado. Verifique se é um CSV válido (separado por vírgula, codificação UTF-8).")
    st.stop()

if upload_df.empty:
    components.friendly_error("O arquivo enviado está vazio.")
    st.stop()

missing_cols = [c for c in features if c not in upload_df.columns]
if missing_cols:
    components.friendly_error("Colunas obrigatórias ausentes no arquivo: " + ", ".join(missing_cols))
    st.stop()

# --------------------------------------------------------------------------- #
# Validação de tipos
# --------------------------------------------------------------------------- #
work_df = upload_df.copy()
invalid_type_counts = {}
for col in features:
    numeric = pd.to_numeric(work_df[col], errors="coerce")
    invalid_mask = numeric.isna() & work_df[col].notna()
    if invalid_mask.any():
        invalid_type_counts[col] = int(invalid_mask.sum())
    work_df[col] = numeric

if invalid_type_counts:
    detalhe = "; ".join(f"{col}: {n} linha(s)" for col, n in invalid_type_counts.items())
    components.friendly_error(
        "Valores não numéricos encontrados em colunas obrigatórias (tratados como ausentes): " + detalhe
    )

if "RA" not in work_df.columns:
    work_df.insert(0, "RA", [f"LINHA-{i + 1}" for i in range(len(work_df))])

# --------------------------------------------------------------------------- #
# Elegibilidade e missing pontual
# --------------------------------------------------------------------------- #
try:
    elegiveis, nao_elegiveis = model_service.split_by_eligibility(work_df, bundle)
except model_service.ModelServiceError as exc:
    components.friendly_error(str(exc))
    st.stop()

linhas_com_missing = int(elegiveis[features].isna().any(axis=1).sum())
if linhas_com_missing:
    st.warning(
        f"{linhas_com_missing} linha(s) elegível(is) chegaram com dados ausentes em pelo menos uma "
        "feature. A imputação (mediana) já embutida na pipeline do modelo será aplicada automaticamente.",
        icon="⚠️",
    )

st.caption(f"{len(elegiveis)} linha(s) elegível(is) (Fases 0-7) · {len(nao_elegiveis)} linha(s) não elegível(is) (Fases 8/9 ou fora do escopo).")

# --------------------------------------------------------------------------- #
# Predição
# --------------------------------------------------------------------------- #
resultados = []

if not elegiveis.empty:
    try:
        proba = model_service.predict_risk(bundle, elegiveis)
    except model_service.ModelServiceError as exc:
        components.friendly_error(str(exc))
        st.stop()

    elegiveis = elegiveis.copy()
    elegiveis["PROB_RISCO_2025"] = proba
    elegiveis["PERCENTIL_RISCO_2025"] = elegiveis["PROB_RISCO_2025"].apply(
        lambda s: scoring.calculate_global_percentile(s, df_ref["PROB_RISCO_2025"])
    )
    elegiveis["RANK_RISCO_2025"] = elegiveis["PROB_RISCO_2025"].apply(
        lambda s: scoring.calculate_rank(s, df_ref["PROB_RISCO_2025"])
    )
    elegiveis["PERCENTIL_RISCO_FASE_2025"] = elegiveis.apply(
        lambda r: scoring.calculate_phase_percentile(r["PROB_RISCO_2025"], r["FASE_NUM"], df_ref), axis=1
    )
    elegiveis["RANK_RISCO_FASE_2025"] = elegiveis.apply(
        lambda r: scoring.calculate_phase_rank(r["PROB_RISCO_2025"], r["FASE_NUM"], df_ref), axis=1
    )
    elegiveis["PRIORIDADE_2025"] = elegiveis.apply(
        lambda r: scoring.classify_priority(r["PERCENTIL_RISCO_2025"], r["PERCENTIL_RISCO_FASE_2025"], thresholds),
        axis=1,
    )
    elegiveis["STATUS_MODELO"] = "Elegível"
    elegiveis["MOTIVO_NAO_ELEGIBILIDADE"] = ""

    if "DEFASAGEM_ANALISE" in elegiveis.columns:
        elegiveis["PERFIL_RADAR"] = elegiveis.apply(
            lambda r: radar.classify_radar(
                radar.defasagem_analise_to_bool(r["DEFASAGEM_ANALISE"]), r["PRIORIDADE_2025"]
            ),
            axis=1,
        )
        if "PEDRA_2024" in elegiveis.columns:
            elegiveis["PONTO_CEGO"] = elegiveis.apply(
                lambda r: radar.is_ponto_cego(r["PERFIL_RADAR"], r["PEDRA_2024"], pedras_ponto_cego), axis=1
            )
    resultados.append(elegiveis)

if not nao_elegiveis.empty:
    nao_elegiveis = nao_elegiveis.copy()
    nao_elegiveis["PROB_RISCO_2025"] = float("nan")
    nao_elegiveis["STATUS_MODELO"] = "Não elegível"
    nao_elegiveis["MOTIVO_NAO_ELEGIBILIDADE"] = MOTIVO_NAO_ELEGIVEL
    components.render_not_eligible_notice()
    resultados.append(nao_elegiveis)

resultado_final = pd.concat(resultados, axis=0, ignore_index=False).sort_index() if resultados else pd.DataFrame()

st.divider()
st.subheader("Resultado")
if resultado_final.empty:
    st.warning("Nenhuma linha pôde ser processada.")
else:
    display_cols = [c for c in resultado_final.columns if c not in features or c in ("RA", "FASE_NUM")]
    ordered_cols = [c for c in ["RA", "FASE_NUM", "STATUS_MODELO", "PROB_RISCO_2025", "PERCENTIL_RISCO_2025",
                                 "RANK_RISCO_2025", "PERCENTIL_RISCO_FASE_2025", "RANK_RISCO_FASE_2025",
                                 "PRIORIDADE_2025", "PERFIL_RADAR", "PONTO_CEGO", "MOTIVO_NAO_ELEGIBILIDADE"]
                    if c in resultado_final.columns]
    view = resultado_final[ordered_cols].copy()
    display_view = components.scale_probability_columns(view, ["PROB_RISCO_2025"])
    st.dataframe(
        display_view,
        hide_index=True,
        width="stretch",
        column_config=components.percent_column_config(
            ["PROB_RISCO_2025", "PERCENTIL_RISCO_2025", "PERCENTIL_RISCO_FASE_2025"],
            {"PROB_RISCO_2025": "Probabilidade estimada"},
        ),
    )
    components.render_download_button(resultado_final, "predicao_em_lote_resultado.csv")
