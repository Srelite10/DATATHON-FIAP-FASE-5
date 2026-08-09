from __future__ import annotations

from src import scoring


def test_get_priority_thresholds_from_config(regras_produto):
    thresholds = scoring.get_priority_thresholds(regras_produto)
    assert thresholds == {"Muito alta": 90, "Alta": 75, "Moderada": 50}


def test_calculate_global_percentile_reproduces_precomputed_values(streamlit_df):
    scores = streamlit_df["PROB_RISCO_2025"]
    sample = streamlit_df.sample(30, random_state=42)
    for _, row in sample.iterrows():
        pct = scoring.calculate_global_percentile(row["PROB_RISCO_2025"], scores)
        assert abs(pct - row["PERCENTIL_RISCO_2025"]) < 0.02


def test_calculate_rank_reproduces_precomputed_values(streamlit_df):
    scores = streamlit_df["PROB_RISCO_2025"]
    sample = streamlit_df.sample(30, random_state=42)
    for _, row in sample.iterrows():
        rank = scoring.calculate_rank(row["PROB_RISCO_2025"], scores)
        assert rank == row["RANK_RISCO_2025"]


def test_calculate_rank_top_score_is_rank_1(streamlit_df):
    scores = streamlit_df["PROB_RISCO_2025"]
    top_score = scores.max()
    assert scoring.calculate_rank(top_score, scores) == 1


def test_calculate_phase_percentile_reproduces_precomputed_values(streamlit_df):
    sample = streamlit_df.sample(30, random_state=7)
    for _, row in sample.iterrows():
        pct = scoring.calculate_phase_percentile(row["PROB_RISCO_2025"], row["FASE_NUM"], streamlit_df)
        assert abs(pct - row["PERCENTIL_RISCO_FASE_2025"]) < 0.02


def test_classify_priority_boundaries():
    thresholds = {"Muito alta": 90, "Alta": 75, "Moderada": 50}
    assert scoring.classify_priority(90, 0, thresholds) == "Muito alta"
    assert scoring.classify_priority(89.99, 0, thresholds) == "Alta"
    assert scoring.classify_priority(75, 0, thresholds) == "Alta"
    assert scoring.classify_priority(74.99, 0, thresholds) == "Moderada"
    assert scoring.classify_priority(50, 0, thresholds) == "Moderada"
    assert scoring.classify_priority(49.99, 0, thresholds) == "Reduzida"
    assert scoring.classify_priority(0, 90, thresholds) == "Muito alta"
    assert scoring.classify_priority(0, 75, thresholds) == "Alta"
    assert scoring.classify_priority(0, 50, thresholds) == "Moderada"
    assert scoring.classify_priority(0, 0, thresholds) == "Reduzida"


def test_classify_priority_reproduces_precomputed_priority_column(streamlit_df, regras_produto):
    thresholds = scoring.get_priority_thresholds(regras_produto)
    computed = streamlit_df.apply(
        lambda row: scoring.classify_priority(
            row["PERCENTIL_RISCO_2025"], row["PERCENTIL_RISCO_FASE_2025"], thresholds
        ),
        axis=1,
    )
    assert (computed == streamlit_df["PRIORIDADE_2025"]).all()


def test_format_probability():
    assert scoring.format_probability(0.5678) == "56.8%"
    assert scoring.format_probability(1.0) == "100.0%"
    assert scoring.format_probability(0.0) == "0.0%"
