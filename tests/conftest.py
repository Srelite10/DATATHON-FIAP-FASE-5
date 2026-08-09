from __future__ import annotations

import pytest

from src import data_loader, model_service


@pytest.fixture(scope="session")
def streamlit_df():
    return data_loader.load_streamlit_data()


@pytest.fixture(scope="session")
def product_df():
    return data_loader.load_product_data()


@pytest.fixture(scope="session")
def trajectory_df():
    return data_loader.load_trajectory_data()


@pytest.fixture(scope="session")
def regras_produto():
    return data_loader.load_regras_produto()


@pytest.fixture(scope="session")
def radar_preventivo_config():
    return data_loader.load_radar_preventivo()


@pytest.fixture(scope="session")
def validacoes():
    return data_loader.load_validacoes()


@pytest.fixture(scope="session")
def bundle():
    return model_service.load_model_bundle()
