"""Caminhos e constantes centrais da aplicação.

Nenhuma regra de negócio (thresholds, features, populações) vive aqui — apenas
localização de artefatos e parâmetros de apresentação (paleta, layout). Regras de
negócio vêm sempre de ``config/*.json`` ou do bundle do modelo, carregados via
:mod:`src.data_loader` e :mod:`src.model_service`.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Raiz do projeto e diretórios de artefatos (sempre caminhos relativos/Path)
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Dados
PATH_BASE_STREAMLIT = DATA_DIR / "base_streamlit_risco_2025.csv"
PATH_BASE_PRODUTO = DATA_DIR / "base_produto_risco_2025.csv"
PATH_TRAJETORIA = DATA_DIR / "trajetoria_pedras_2022_2024.csv"

# Modelo
PATH_MODELO = MODELS_DIR / "modelo_risco_defasagem_2025.joblib"

# Configurações de negócio (JSON)
PATH_REGRAS_PRODUTO = CONFIG_DIR / "regras_produto.json"
PATH_METRICAS_MODELO = CONFIG_DIR / "metricas_modelo.json"
PATH_EFETIVIDADE = CONFIG_DIR / "efetividade.json"
PATH_RADAR_PREVENTIVO = CONFIG_DIR / "radar_preventivo.json"
PATH_METADADOS_BUNDLE = CONFIG_DIR / "metadados_bundle.json"
PATH_VALIDACOES = CONFIG_DIR / "validacoes.json"

# --------------------------------------------------------------------------- #
# Apresentação
# --------------------------------------------------------------------------- #
APP_TITLE = "Passos Mágicos — Painel Analítico de Risco e Priorização"
APP_ICON = "🧭"

# Paleta validada (dataviz skill) — superfície clara fixa (tema único do app)
COLOR_SURFACE = "#fcfcfb"
COLOR_TEXT_PRIMARY = "#0b0b0b"
COLOR_TEXT_SECONDARY = "#52514e"
COLOR_TEXT_MUTED = "#898781"
COLOR_GRIDLINE = "#e1e0d9"
COLOR_BASELINE = "#c3c2b7"

# Sequencial (magnitude — scores, contagens)
COLOR_SEQUENTIAL = "#2a78d6"
SEQUENTIAL_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# Diverging (polaridade — z-score acima/abaixo dos pares)
COLOR_DIVERGING_POS = "#2a78d6"
COLOR_DIVERGING_NEG = "#d03b3b"
COLOR_DIVERGING_MID = "#f0efec"

# Status (prioridade de acompanhamento — estado, sempre ícone + rótulo)
PRIORITY_COLORS = {
    "Muito alta": "#d03b3b",  # critical
    "Alta": "#ec835a",  # serious
    "Moderada": "#fab219",  # warning
    "Reduzida": "#0ca30c",  # good
}
PRIORITY_ORDER = ["Muito alta", "Alta", "Moderada", "Reduzida"]

# Perfis do Radar Preventivo — Risco oculto recebe cor-assinatura (violeta) para
# se destacar como o diferencial do produto, conforme pedido no briefing.
RADAR_COLORS = {
    "Crítico persistente": "#d03b3b",
    "Risco oculto": "#4a3aa7",
    "Atenção atual": "#eda100",
    "Estável / menor prioridade": "#1baf7a",
}
RADAR_ORDER = ["Crítico persistente", "Risco oculto", "Atenção atual", "Estável / menor prioridade"]

# Trajetória das Pedras (ordinal: Quartzo < Ágata < Ametista < Topázio)
PEDRA_ORDEM = ["Quartzo", "Ágata", "Ametista", "Topázio"]
PEDRA_ORDINAL_RAMP = {
    "Quartzo": "#86b6ef",
    "Ágata": "#3987e5",
    "Ametista": "#256abf",
    "Topázio": "#104281",
}

# Movimento entre Pedras (estado: avanço / manutenção / recuo)
MOVEMENT_COLORS = {
    "Avanço": "#0ca30c",
    "Manutenção": "#898781",
    "Recuo": "#d03b3b",
}
MOVEMENT_ORDER = ["Avanço", "Manutenção", "Recuo"]

PEDRAS_PONTO_CEGO_FALLBACK = ("Ametista", "Topázio")
