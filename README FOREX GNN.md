# ForexGNN — Motor de Análisis Estructural de Mercado

> **Sistema híbrido ML + Graph Neural Networks para análisis Forex y predicción de XAUUSD**

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      FOREXGNN PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OHLCV H1 (14 activos: XAUUSD, DXY, SPX500, VIX, pares Forex) │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         ▼                                   ▼                  │
│  ┌─────────────────┐              ┌──────────────────────┐     │
│  │  FEATURE ENG.   │              │   DYNAMIC GRAPH      │     │
│  │  TEMPORAL       │              │   CONSTRUCTION       │     │
│  │                 │              │                      │     │
│  │ - Returns (5w)  │              │  - Corr matrix       │     │
│  │ - ATR norm.     │              │    (rolling 48h)     │     │
│  │ - Volatility    │              │  - Threshold 0.4     │     │
│  │ - Momentum      │              │  - Pruning (8/nodo)  │     │
│  │ - Z-score       │              │                      │     │
│  │ - Session enc.  │              │  Node features:      │     │
│  │ - Cross-asset   │              │  - Degree centrality │     │
│  │   (GS ratio,    │              │  - Eigenvector cen.  │     │
│  │    XAU-DXY corr)│              │  - Betweenness cen.  │     │
│  └────────┬────────┘              │  - Clustering coef.  │     │
│           │                       │  - Louvain community │     │
│           ▼                       │  - Node strength     │     │
│  ┌─────────────────┐              └──────────┬───────────┘     │
│  │   LightGBM      │                         │                 │
│  │   Temporal      │                         ▼                 │
│  │   Model         │              ┌──────────────────────┐     │
│  │                 │              │   GCN / GAT Model    │     │
│  │  TimeSeriesSplit│              │                      │     │
│  │  Anti-leakage   │              │  Input: node feats + │     │
│  │  Calibration    │              │         edge weights │     │
│  │                 │              │                      │     │
│  │  Output:        │              │  Output:             │     │
│  │   P(sube)       │              │   P(sube) + emb(32d) │     │
│  └────────┬────────┘              └──────────┬───────────┘     │
│           │                                   │                 │
│           └──────────────┬────────────────────┘                │
│                          ▼                                      │
│               ┌──────────────────────┐                         │
│               │    META-MODELO       │                         │
│               │  (LogisticRegression)│                         │
│               │                      │                         │
│               │  Features:           │                         │
│               │  - lgbm_prob         │                         │
│               │  - gnn_prob          │                         │
│               │  - gnn_embedding[:8] │                         │
│               │  - graph_centrality  │                         │
│               │  - graph_density     │                         │
│               │  - regime (KMeans)   │                         │
│               │                      │                         │
│               │  Salida calibrada:   │                         │
│               │  P(XAUUSD sube H1+1) │                         │
│               └──────────┬───────────┘                         │
│                          │                                      │
│                          ▼                                      │
│          P > 0.60 → BUY | P < 0.40 → SELL | else → NEUTRAL    │
│                          │                                      │
│                          ▼                                      │
│               ┌──────────────────────┐                         │
│               │    BACKTESTING       │                         │
│               │  ATR-based SL/TP     │                         │
│               │  Session filter      │                         │
│               │  Métricas completas  │                         │
│               └──────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura del Proyecto

```
forex_gnn/
├── config/
│   └── config.yaml              # Toda la configuración (YAML)
│
├── data/
│   └── loader.py                # Descarga yfinance + cache + normalización
│
├── features/
│   ├── temporal.py              # Feature engineering temporal (LGBM)
│   └── graph_features.py        # Fusión temporal+grafo + detección régimen
│
├── graphs/
│   ├── builder.py               # Grafo dinámico desde correlaciones rolling
│   └── dynamic.py               # Dataset PyTorch Geometric + splits
│
├── models/
│   ├── gnn.py                   # ForexGCN, ForexGAT, factory
│   ├── temporal.py              # LGBMTemporalModel (CV + calibración)
│   └── meta_model.py            # MetaModel de fusión (stacking)
│
├── training/
│   └── trainer.py               # GNNTrainer (GPU + early stopping)
│
├── backtesting/
│   └── backtester.py            # Backtester vectorizado
│
├── visualization/
│   └── graph_viz.py             # PyVis + Plotly (grafo, heatmap, equity)
│
├── utils/
│   ├── config.py                # Cargador YAML + Config namespace
│   └── logger.py                # Loguru centralizado
│
├── notebooks/
│   └── 01_exploracion_inicial.py  # Notebook de exploración (jupytext)
│
├── scripts/
│   └── build_graph.py           # Script standalone para construir el grafo
│
├── main.py                      # Orquestador del pipeline completo
└── requirements.txt
```

---

## Instalación

```bash
# 1. Entorno virtual
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Dependencias base
pip install -r requirements.txt

# 3. PyTorch Geometric (ajustar según tu versión de CUDA)
# CPU:
pip install torch-geometric

# CUDA 12.1:
pip install torch-geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster \
    torch_spline_conv -f https://data.pyg.org/whl/torch-2.2.0+cu121.html
```

---

## Uso Rápido

### Pipeline completo
```bash
python main.py
```

### Stages individuales
```bash
python main.py --stages data features          # Solo datos + features
python main.py --stages graphs                 # Solo grafo
python main.py --stages gnn lgbm meta         # Solo modelos
python main.py --stages backtest viz           # Solo backtesting + viz
```

### Construir el grafo standalone
```bash
python scripts/build_graph.py
python scripts/build_graph.py --start 2022-01-01 --threshold 0.5
```

### Notebook de exploración
```bash
# Instalar jupytext una sola vez
pip install jupytext

# Convertir a .ipynb
jupytext --to notebook notebooks/01_exploracion_inicial.py

# Ejecutar
jupyter lab notebooks/01_exploracion_inicial.ipynb
```

---

## Roadmap

### Fase 1 — Fundamentos ✅
- [x] Arquitectura modular completa
- [x] Descarga y caché de OHLCV (14 activos, H1)
- [x] Feature engineering temporal (retornos, ATR, volatilidad, sesión)
- [x] Construcción de grafo dinámico (correlaciones rolling)
- [x] Extracción de features de teoría de grafos
- [x] Detección de comunidades (Louvain)
- [x] Visualización interactiva (PyVis + Plotly)
- [x] Dataset PyTorch Geometric con splits temporales

### Fase 2 — Modelos ✅
- [x] GCN con residual + BatchNorm
- [x] GAT con multi-head attention
- [x] LightGBM con TimeSeriesSplit anti-leakage
- [x] Meta-modelo de stacking (fusión GNN + LGBM)
- [x] Calibración de probabilidades

### Fase 3 — Evaluación ✅
- [x] Backtesting vectorizado con ATR-based SL/TP
- [x] Filtro de sesión de mercado
- [x] Métricas: Sharpe, Sortino, Calmar, Max DD, Win Rate
- [x] Curva de equity interactiva

### Fase 4 — Mejoras Futuras
- [ ] EvolveGCN / DySAT para modelado temporal explícito del grafo
- [ ] Attention temporal sobre secuencia de snapshots
- [ ] Integración MT5 para datos en tiempo real
- [ ] Streamlit dashboard
- [ ] Walk-forward optimization
- [ ] Análisis SHAP de features del grafo

---

## Diseño del Grafo Dinámico

| Parámetro | Valor por defecto | Descripción |
|-----------|-------------------|-------------|
| `correlation_window` | 48 barras H1 | 2 días de historia para cada correlación |
| `correlation_step` | 6 barras H1 | Nuevo snapshot cada 6h |
| `edge_threshold` | 0.4 | Mínimo \|corr\| para crear arista |
| `edge_method` | pearson | Tipo de correlación |
| `max_edges_per_node` | 8 | Pruning de aristas débiles |

### Features de Grafos Extraídas

| Feature | Descripción |
|---------|-------------|
| `degree_centrality` | Número de conexiones normalizadas |
| `eigenvector_centrality` | Influencia propagada (PageRank-like) |
| `betweenness_centrality` | Nodos que actúan como "puentes" |
| `clustering_coefficient` | Qué tan denso es el vecindario |
| `community_label` | Grupo Louvain (risk-on/off/neutral) |
| `node_strength` | Suma de pesos de aristas |
| `graph_density` | Densidad global del grafo |
| `avg_neighbor_corr` | Correlación media con vecinos |

---

## Diseño de Señales

| Condición | Señal |
|-----------|-------|
| P(sube) ≥ 0.60 | **BUY** |
| P(sube) ≤ 0.40 | **SELL** |
| 0.40 < P < 0.60 | **NEUTRAL** |

La zona neutral reduce el overtrading en períodos de incertidumbre.

---

## Configuración

Todos los parámetros son editables en `config/config.yaml` sin tocar código:

```yaml
graph:
  correlation_window: 48
  edge_threshold: 0.4

gnn:
  architecture: "GAT"    # GCN → GAT para más precisión

meta_model:
  threshold_buy:  0.60
  threshold_sell: 0.40

backtesting:
  sl_atr_multiplier: 1.5
  tp_atr_multiplier: 2.5
```
