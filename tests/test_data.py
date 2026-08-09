from __future__ import annotations

from src import config, data_loader


def test_all_required_artifacts_exist():
    required = [
        config.PATH_BASE_STREAMLIT,
        config.PATH_BASE_PRODUTO,
        config.PATH_TRAJETORIA,
        config.PATH_MODELO,
        config.PATH_REGRAS_PRODUTO,
        config.PATH_METRICAS_MODELO,
        config.PATH_EFETIVIDADE,
        config.PATH_RADAR_PREVENTIVO,
        config.PATH_METADADOS_BUNDLE,
        config.PATH_VALIDACOES,
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing, f"Artefatos ausentes: {missing}"


def test_base_streamlit_has_1054_unique_ras(streamlit_df, validacoes):
    assert len(streamlit_df) == validacoes["base_streamlit_linhas"]
    assert streamlit_df["RA"].nunique() == validacoes["base_streamlit_ras_unicos"]
    assert streamlit_df["RA"].duplicated().sum() == validacoes["base_streamlit_duplicidades"]


def test_risco_oculto_totals_118(streamlit_df, validacoes):
    assert int(streamlit_df["RISCO_OCULTO"].sum()) == validacoes["risco_oculto"]


def test_ponto_cego_totals_37(streamlit_df, validacoes):
    assert int(streamlit_df["PONTO_CEGO"].sum()) == validacoes["ponto_cego"]


def test_base_produto_has_1156_unique_ras(product_df, validacoes):
    assert len(product_df) == validacoes["base_produto_linhas"]
    assert product_df["RA"].nunique() == validacoes["base_produto_ras_unicos"]


def test_base_produto_elegibilidade_counts(product_df, validacoes):
    counts = product_df["STATUS_MODELO"].value_counts().to_dict()
    for status_label, expected in validacoes["status_modelo"].items():
        assert counts.get(status_label, 0) == expected


def test_trajetoria_has_434_unique_ras(trajectory_df, validacoes):
    assert len(trajectory_df) == validacoes["trajetoria_linhas"]
    assert trajectory_df["RA"].nunique() == validacoes["trajetoria_ras_unicos"]


def test_validate_artifacts_report_is_ok():
    report = data_loader.validate_artifacts()
    assert report.ok, f"Validações de integridade falharam: {report.issues}"
