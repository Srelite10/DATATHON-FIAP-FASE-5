from __future__ import annotations

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from src import model_service


def test_bundle_is_dict(bundle):
    assert isinstance(bundle, dict)


def test_bundle_has_pipeline_key(bundle):
    assert "pipeline" in bundle
    assert isinstance(bundle["pipeline"], Pipeline)


def test_bundle_features_match_expected(bundle):
    expected = ["FASE_NUM", "TEMPO_PROGRAMA", "IDA", "IEG", "IAA_MODELO", "IPS", "IPV"]
    assert model_service.get_features(bundle) == expected


def test_bundle_fases_elegiveis_are_0_to_7(bundle):
    assert model_service.get_fases_elegiveis(bundle) == [0, 1, 2, 3, 4, 5, 6, 7]


def test_predict_risk_returns_probability_between_0_and_1(bundle, streamlit_df):
    features = model_service.get_features(bundle)
    sample = streamlit_df[features].head(20)
    proba = model_service.predict_risk(bundle, sample)
    assert len(proba) == 20
    assert (proba >= 0).all() and (proba <= 1).all()


def test_predict_risk_matches_precomputed_scores(bundle, streamlit_df):
    """A pipeline do bundle deve reproduzir PROB_RISCO_2025 já calculado na base."""
    features = model_service.get_features(bundle)
    sample = streamlit_df.head(50)
    proba = model_service.predict_risk(bundle, sample[features])
    diffs = (pd.Series(proba, index=sample.index) - sample["PROB_RISCO_2025"]).abs()
    assert diffs.max() < 1e-6


def test_predict_risk_raises_for_fase_8(bundle):
    df = pd.DataFrame(
        [{"FASE_NUM": 8, "TEMPO_PROGRAMA": 3, "IDA": 5.0, "IEG": 5.0, "IAA_MODELO": 5.0, "IPS": 5.0, "IPV": 5.0}]
    )
    with pytest.raises(model_service.ModelServiceError):
        model_service.predict_risk(bundle, df)


def test_predict_risk_raises_for_fase_9(bundle):
    df = pd.DataFrame(
        [{"FASE_NUM": 9, "TEMPO_PROGRAMA": 3, "IDA": 5.0, "IEG": 5.0, "IAA_MODELO": 5.0, "IPS": 5.0, "IPV": 5.0}]
    )
    with pytest.raises(model_service.ModelServiceError):
        model_service.predict_risk(bundle, df)


def test_is_fase_elegivel(bundle):
    assert model_service.is_fase_elegivel(0, bundle) is True
    assert model_service.is_fase_elegivel(7, bundle) is True
    assert model_service.is_fase_elegivel(8, bundle) is False
    assert model_service.is_fase_elegivel(9, bundle) is False


def test_split_by_eligibility(bundle, product_df):
    elegivel, nao_elegivel = model_service.split_by_eligibility(product_df, bundle)
    assert set(elegivel["FASE_NUM"].unique()).issubset(set(model_service.get_fases_elegiveis(bundle)))
    assert set(nao_elegivel["FASE_NUM"].unique()).isdisjoint(set(model_service.get_fases_elegiveis(bundle)))
    assert len(elegivel) + len(nao_elegivel) == len(product_df)
