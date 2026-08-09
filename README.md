# Passos Mágicos — Painel Analítico de Risco e Priorização

Dashboard analítico desenvolvido no contexto do **Datathon FIAP Pós Tech em
Data Analytics**, em apoio à gestão pedagógica da **Associação Passos
Mágicos** — organização social que atende crianças e jovens em situação de
vulnerabilidade, acompanhando sua trajetória educacional ao longo dos anos.

O painel une situação educacional atual, score prospectivo de risco,
priorização relativa e o **Radar Preventivo** — o diferencial do produto — em
uma única ferramenta de apoio à decisão.

> **O que este painel não é:** um sistema de diagnóstico. Toda a linguagem do
> produto usa termos como *probabilidade estimada*, *score prospectivo*,
> *prioridade de acompanhamento* e *sinal preventivo* — nunca afirmações
> determinísticas ("este aluno ficará defasado") ou causais ("o programa
> causou").

# 🎓 Datathon FIAP — Passos Mágicos
## Radar Preventivo de Risco Educacional

Solução desenvolvida no **Datathon da Pós Tech FIAP em Data Analytics** para a
**Associação Passos Mágicos**, combinando análise educacional longitudinal,
Machine Learning e um produto analítico em Streamlit.

O objetivo é apoiar a transição de um acompanhamento apenas **reativo** para uma
abordagem também **preventiva**, identificando estudantes que ainda não apresentam
defasagem, mas concentram sinais associados a maior prioridade futura.

[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](COLOCAR_URL_DO_STREAMLIT)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](#)
[![Tests](https://img.shields.io/badge/tests-33%20passed-success)](#)
[![FIAP](https://img.shields.io/badge/FIAP-Datathon-E91C5D)](#)

---

## 🔗 Acesso rápido

| Entregável | Link |
|---|---|
| 🚀 Aplicação Streamlit | **[Abrir Radar Preventivo](COLOCAR_URL_DO_STREAMLIT)** |
| 📊 Apresentação executiva | [PDF](docs/Datathon_PassosMagicos_Apresentacao_Final.pdf) |
| 📓 EDA e auditoria | [Notebook 01](notebooks/01_auditoria_eda_passos_magicos.ipynb) |
| 🤖 Modelo preditivo | [Notebook 02](notebooks/02_modelo_risco_defasagem.ipynb) |

---

## 📌 Resultados em 30 segundos

| Indicador | Resultado |
|---|---:|
| Estudantes analisados em 2024 | **1.156** |
| Elegíveis ao modelo | **1.054** |
| Risco oculto identificado | **118 estudantes** |
| Potenciais pontos cegos | **37 estudantes** |
| ROC-AUC no teste temporal | **0,7649** |
| PR-AUC no teste temporal | **0,8321** |

### Principal insight

> Entre os **518 estudantes sem defasagem em 2024**, **118 (22,78%)**
> apresentaram prioridade prospectiva Alta ou Muito alta.

Esses estudantes formam o grupo de **Risco Oculto**: casos que poderiam passar
despercebidos em um acompanhamento baseado apenas na situação educacional atual.

---







## Problema de negócio

A Associação acompanha estudantes por indicadores educacionais (IDA, IEG, IAA,
IPS, IPV, IPP, INDE) e uma classificação de Pedra (Quartzo < Ágata < Ametista <
Topázio). Historicamente, o acompanhamento é **reativo**: a defasagem só é
tratada depois de observada. O objetivo deste produto é antecipar sinais de
prioridade futura **antes** que uma nova defasagem apareça — sobretudo para
estudantes que hoje parecem bem, mas concentram sinais estatísticos associados
a maior atenção prospectiva.

## Solução desenvolvida

Um dashboard Streamlit multipágina que combina um modelo preditivo já treinado
com regras de priorização gerencial:

- **Visão executiva (home):** KPIs institucionais e panorama geral 2025.
- **Radar Preventivo:** classifica cada estudante em quatro perfis (abaixo) e
  destaca risco oculto e potenciais pontos cegos.
- **Ranking 2025:** tabela operacional de priorização, com busca e filtros.
- **Simulador Individual:** calcula o score prospectivo de um caso novo
  chamando a pipeline real do modelo.
- **Predição em Lote:** aplica o modelo a um CSV externo, validando colunas,
  tipos e elegibilidade antes de prever.
- **Trajetória e Efetividade:** evolução histórica das Pedras (2022-2024).
- **Modelo e Metodologia:** transparência técnica completa para avaliação.

## Radar Preventivo

O núcleo do produto cruza a situação **atual** (defasagem observada) com a
**prioridade prospectiva** (derivada da probabilidade estimada pelo modelo) em
quatro perfis:

| Perfil | Defasagem atual | Prioridade prospectiva |
|---|---|---|
| Crítico persistente | Sim | Alta/Muito alta |
| **Risco oculto** | Não | Alta/Muito alta |
| Atenção atual | Sim | Moderada/Reduzida |
| Estável / menor prioridade | Não | Moderada/Reduzida |

**Potencial ponto cego** é um subconjunto do risco oculto: estudantes com
Pedra 2024 em Ametista ou Topázio (fora das duas Pedras inferiores) que, mesmo
assim, concentram prioridade prospectiva elevada — um instrumento de triagem
preventiva, não um diagnóstico.

> **Definição de risco oculto:** estudante **sem defasagem observada** na
> análise atual, mas cujo score prospectivo (percentil global ou da fase) o
> coloca em prioridade **Alta** ou **Muito alta** — ou seja, sinais
> estatísticos associados a maior atenção futura que passariam despercebidos
> em um acompanhamento puramente reativo.

## Arquitetura

Aplicação Streamlit **multipágina**: `app.py` é a home e cada arquivo em
`pages/` vira uma página no menu lateral automaticamente. Toda regra de
negócio e acesso a dados fica em `src/`, nunca duplicada entre páginas:

- `@st.cache_data` para CSVs e configurações JSON (`data_loader.py`);
- `@st.cache_resource` para o bundle do modelo, carregado uma única vez
  (`model_service.py`);
- páginas fazem apenas orquestração de UI, chamando funções de `src/`.

## Estrutura do projeto

```
app.py                          # Homepage — visão executiva
pages/
  01_Radar_Preventivo.py        # Diferencial do produto
  02_Ranking_2025.py            # Priorização operacional
  03_Simulador_Individual.py    # Serve a pipeline real do modelo
  04_Predicao_em_Lote.py        # Upload de CSV externo
  05_Trajetoria_Efetividade.py  # Histórico de Pedras 2022-2024
  06_Modelo_Metodologia.py      # Transparência técnica
src/
  config.py          # Caminhos (pathlib) e paleta — sem regra de negócio
  data_loader.py      # Única porta de entrada para data/ e config/ (cache)
  model_service.py   # Carrega o bundle .joblib e executa predict_proba
  scoring.py          # Percentil, rank, thresholds de prioridade
  radar.py             # Classificação do Radar Preventivo e ponto cego
  charts.py            # Construtores de gráficos Plotly (paleta validada)
  components.py       # Componentes de UI reutilizáveis (cards, badges, etc.)
data/                 # Bases fornecidas (fonte de verdade dos dados)
models/               # Bundle serializado do modelo
config/               # Regras de negócio e métricas (fonte de verdade)
docs/                  # Ambiente de treinamento do modelo
tests/                 # Suíte pytest
.streamlit/config.toml # Tema visual fixo (claro)
```

Nenhuma regra de negócio (thresholds, features, populações elegíveis) está
hardcoded fora de `config/*.json` e do bundle do modelo — `src/` apenas lê e
aplica essas regras de forma centralizada, para que nenhuma página duplique
lógica.

## Modelo

- **Algoritmo:** Regressão Logística (dentro de uma `Pipeline` sklearn com
  imputação por mediana + padronização).
- **Alvo:** `RISCO_FUTURO = 1` se `DEFASAGEM_ANALISE` do ano seguinte `< 0`.
- **Artefato:** `models/modelo_risco_defasagem_2025.joblib` é um **bundle
  (dicionário)**, não um estimador direto:

  ```python
  bundle = joblib.load(caminho)
  pipeline = bundle["pipeline"]
  proba = pipeline.predict_proba(X)[:, 1]
  ```

  O modelo nunca é retreinado, recalibrado ou ajustado dentro do Streamlit.

### Features (exatas, nesta ordem — vêm do próprio bundle)

`FASE_NUM`, `TEMPO_PROGRAMA`, `IDA`, `IEG`, `IAA_MODELO`, `IPS`, `IPV`

`RA`, `IAN`, `INDE`, `IPP`, `Pedra`, `DEFASAGEM_ANALISE`, `FASE_IDEAL` e
percentis **não** entram no modelo — aparecem apenas como contexto gerencial.

### População elegível

O modelo só é válido para `FASE_NUM` de **0 a 7**. Fases 8 e 9 apresentam
indisponibilidade estrutural dos indicadores necessários e **não recebem
`predict_proba`** — não há imputação que resolva uma ausência estrutural
(diferente de missing pontual dentro da população elegível, que a própria
pipeline trata).

### Protocolo temporal

| Etapa | Período |
|---|---|
| Desenvolvimento | 2022 → 2023 |
| Teste temporal independente | 2023 → 2024 |
| Inferência prospectiva | 2024 → 2025 |

Os resultados de 2025 são **prospectivos** — como o desfecho de 2025 ainda não
está disponível, não existem métricas reais de acerto para essas previsões
(ver página **Modelo e Metodologia**).

### Métricas (teste temporal independente, 2023 → 2024)

Avaliadas em dados que o modelo nunca viu no treinamento (fonte:
`config/metricas_modelo.json`), com threshold de referência 0.50:

| Métrica | Valor |
|---|---|
| ROC-AUC | 0.7649 |
| PR-AUC | 0.8321 |
| Accuracy | 0.6667 |
| Precision | 0.7830 |
| Recall | 0.5724 |
| F1 | 0.6614 |
| Brier Score (calibração) | 0.2060 |

Estas são as únicas métricas de acerto reais disponíveis no projeto — não
existe equivalente para 2025, pois o desfecho ainda não ocorreu. Detalhamento
completo (incluindo o comparativo no threshold 0.55 e os coeficientes do
modelo) está na página **Modelo e Metodologia** do app.

### Priorização (regra de produto, não do modelo)

A saída principal é a probabilidade (`predict_proba`). O threshold de
desenvolvimento (0.55) **não** é regra operacional de risco — a priorização
usa percentil global e percentil dentro da fase, comparando cada score com a
população de referência (`data/base_streamlit_risco_2025.csv`):

- **Muito alta:** percentil global ≥ 90 OU percentil da fase ≥ 90
- **Alta:** percentil global ≥ 75 OU percentil da fase ≥ 75
- **Moderada:** percentil global ≥ 50 OU percentil da fase ≥ 50
- **Reduzida:** demais casos

Esses thresholds são extraídos de `config/regras_produto.json` (não
hardcoded soltos no código).

## Como executar (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

O app abre em **http://localhost:8501**.

> **Erro de ExecutionPolicy ao ativar o venv?** Sem alterar a política do
> sistema, rode isto **apenas na sessão atual** do PowerShell antes de ativar:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

### Nota sobre versões (Python 3.13 local)

`docs/ambiente_modelo.txt` documenta o ambiente de treinamento (Colab):
Python 3.12.13, scikit-learn 1.6.1, pandas 2.2.2, numpy 2.0.2, joblib 1.5.3.
`requirements.txt` fixa **scikit-learn 1.6.1** e **joblib 1.5.3** de forma
idêntica (crítico para o unpickling correto do bundle) e usa **pandas 2.2.3**
/ **numpy 2.2.6** — os patches mais próximos dos documentados com wheel
disponível para Python 3.13 (não há wheel de pandas 2.2.2 / numpy 2.0.2 para
3.13). Testado localmente sem warnings de incompatibilidade. Para reprodução
exata dos números do pacote de treinamento, use Python 3.12 (ver `runtime.txt`,
usado pelo Streamlit Community Cloud).

## Testes

```powershell
pytest -q
```

33 testes cobrindo:

- existência de todos os artefatos obrigatórios;
- integridade dos dados (RAs únicos, risco oculto = 118, ponto cego = 37,
  elegíveis = 1054, não elegíveis = 102, trajetória = 434 RAs) contra
  `config/validacoes.json`;
- formato do bundle (`dict` com chave `pipeline`) e features esperadas;
- `predict_proba` no intervalo [0, 1] e reprodução exata dos scores já
  calculados na base;
- bloqueio de Fases 8 e 9 no `predict_risk`;
- percentil/rank/prioridade reproduzindo exatamente as colunas pré-calculadas
  da base (1054/1054 linhas) nos limites de 50, 75 e 90;
- classificação do Radar Preventivo e do ponto cego reproduzindo exatamente
  as colunas pré-calculadas da base.

## Limitações

- Fases 8 e 9 fora do escopo validado (ausência estrutural de indicadores).
- Threshold de desenvolvimento (0.55) não é estável temporalmente — não usado
  como regra operacional.
- Não existem métricas reais de 2025 (inferência prospectiva).
- Coeficientes do modelo são associações preditivas, não causais.
- Upload em lote: a coluna `PEDRA_2024`, se enviada, precisa usar exatamente
  os valores `Quartzo`, `Ágata`, `Ametista`, `Topázio` (com acentuação) para
  que o potencial ponto cego seja identificado corretamente.

## Deploy no Streamlit Community Cloud

O projeto já está preparado (caminhos relativos via `pathlib`, sem referências
ao Google Drive, sem segredos no código, `runtime.txt` fixando Python 3.12).
Passos:

1. Suba o projeto para um repositório no GitHub (inclua `data/`, `models/` e
   `config/` — são pequenos: maior CSV ~195 KB, modelo ~2,7 KB).
2. Em [share.streamlit.io](https://share.streamlit.io), crie um novo app
   apontando para o repositório, branch e arquivo `app.py`.
3. Streamlit Cloud instala `requirements.txt` automaticamente e usa
   `runtime.txt` para a versão do Python.
4. Nenhuma variável de ambiente/segredo é necessária — o app não usa
   `st.secrets`.

## Stack tecnológica

Streamlit · pandas · numpy · scikit-learn · joblib · Plotly · pytest
