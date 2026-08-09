from __future__ import annotations

from src import radar, scoring


def test_classify_radar_all_four_combinations():
    assert radar.classify_radar(tem_defasagem=True, prioridade="Muito alta") == radar.CRITICO_PERSISTENTE
    assert radar.classify_radar(tem_defasagem=True, prioridade="Alta") == radar.CRITICO_PERSISTENTE
    assert radar.classify_radar(tem_defasagem=False, prioridade="Muito alta") == radar.RISCO_OCULTO
    assert radar.classify_radar(tem_defasagem=False, prioridade="Alta") == radar.RISCO_OCULTO
    assert radar.classify_radar(tem_defasagem=True, prioridade="Moderada") == radar.ATENCAO_ATUAL
    assert radar.classify_radar(tem_defasagem=True, prioridade="Reduzida") == radar.ATENCAO_ATUAL
    assert radar.classify_radar(tem_defasagem=False, prioridade="Moderada") == radar.ESTAVEL_MENOR_PRIORIDADE
    assert radar.classify_radar(tem_defasagem=False, prioridade="Reduzida") == radar.ESTAVEL_MENOR_PRIORIDADE


def test_defasagem_analise_to_bool():
    assert radar.defasagem_analise_to_bool(-1) is True
    assert radar.defasagem_analise_to_bool(0) is False
    assert radar.defasagem_analise_to_bool(2) is False


def test_get_pedras_ponto_cego_from_config(regras_produto):
    pedras = radar.get_pedras_ponto_cego(regras_produto)
    assert set(pedras) == {"Ametista", "Topázio"}


def test_is_ponto_cego_requires_risco_oculto_and_target_pedra():
    pedras_alvo = ("Ametista", "Topázio")
    assert radar.is_ponto_cego("Risco oculto", "Ametista", pedras_alvo) is True
    assert radar.is_ponto_cego("Risco oculto", "Topázio", pedras_alvo) is True
    assert radar.is_ponto_cego("Risco oculto", "Quartzo", pedras_alvo) is False
    assert radar.is_ponto_cego("Risco oculto", "Ágata", pedras_alvo) is False
    assert radar.is_ponto_cego("Crítico persistente", "Ametista", pedras_alvo) is False
    assert radar.is_ponto_cego("Risco oculto", None, pedras_alvo) is False


def test_classify_radar_reproduces_precomputed_perfil_column(streamlit_df):
    computed = streamlit_df.apply(
        lambda row: radar.classify_radar(
            radar.defasagem_analise_to_bool(row["DEFASAGEM_ANALISE"]), row["PRIORIDADE_2025"]
        ),
        axis=1,
    )
    assert (computed == streamlit_df["PERFIL_RADAR"]).all()


def test_is_ponto_cego_reproduces_precomputed_column(streamlit_df, regras_produto):
    pedras_alvo = radar.get_pedras_ponto_cego(regras_produto)
    computed = streamlit_df.apply(
        lambda row: radar.is_ponto_cego(row["PERFIL_RADAR"], row["PEDRA_2024"], pedras_alvo), axis=1
    )
    assert (computed == streamlit_df["PONTO_CEGO"]).all()


def test_risco_oculto_count_matches_radar_profile(streamlit_df):
    assert int((streamlit_df["PERFIL_RADAR"] == radar.RISCO_OCULTO).sum()) == int(
        streamlit_df["RISCO_OCULTO"].sum()
    )
