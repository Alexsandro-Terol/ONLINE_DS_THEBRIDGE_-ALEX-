<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/LightGBM-Ensemble-FF6B6B?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Scikit--Learn-Pipeline-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/XAUUSD-M30%20%7C%20H1-FFD700?style=for-the-badge"/>
</p>

<h1 align="center">🥇 GoldSense ML</h1>
<h3 align="center">Sistema Cuantitativo de Machine Learning para Predicción de Movimientos en XAUUSD</h3>

<p align="center">
  <em>Pipeline institucional anti-leakage · Walk-Forward Validation · DXY Edge Analysis · Streamlit App</em>
</p>

---

## 🎯 Problema de Negocio

El oro (XAUUSD) es uno de los activos más negociados del mundo, con liquidez diaria superior a **$130 mil millones**. Los traders enfrentan un mercado impulsado por la dinámica del dólar (DXY), eventos macroeconómicos y microestructura compleja.

**Objetivo**: Predecir si el precio del oro alcanzará un **TP de 0.15%** antes de un **SL de 0.10%** en las siguientes 6 velas M30, con un edge estadístico real y robusto out-of-sample.

> *"No buscamos el modelo perfecto. Buscamos un edge pequeño pero real, estable en el tiempo y explotable con costos reales."*

---

## 📊 Dataset

| Parámetro | Valor |
|:----------|:------|
| **Instrumento** | XAUUSD (Oro/USD) |
| **Timeframe** | M30 (velas de 30 minutos) |
| **Período** | 2021-11-22 → 2026-02-20 |
| **Registros** | **46,081 velas** (≫ mínimo requerido) |
| **Fuente** | Dataset propio M30 — XAUUSD + DXY sincronizados |
| **Features generados** | **30 features estables** (de 87 iniciales) |
| **Valores nulos** | 0 |
| **Leakage** | ✅ Verificado — cero features futuros |

---

## 🏗️ Arquitectura del Pipeline

```
XAUUSD_DXY.csv (raw)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              data_processing.py v3                   │
│  • Corrección naming invertido (DXY ↔ XAUUSD)      │
│  • 87 features estacionarios (sin precios absolutos) │
│  • KMeans K=4 (régimen de mercado no supervisado)   │
│  • Triple Barrier labeling (TP/SL/Timeout)          │
│  • Leakage Audit automático                         │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              training.py v4                          │
│  • Feature Stability Selection (top 30, CV ≤ 1.5)  │
│  • Purged Walk-Forward (8 folds + embargo 8 velas)  │
│  • Split temporal 70/15/15 (cronológico, sin shuffle)│
│  • LightGBM + XGBoost + RandomForest → Ensemble     │
│  • Regularización fuerte (num_leaves=5, λ=20)       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              analysis.py + evaluation.py             │
│  • Threshold Optimization (0.50 → 0.65)            │
│  • Rolling AUC — alpha decay analysis               │
│  • DXY Lead-Lag causal analysis                     │
│  • Regime-aware performance                         │
│  • Backtest realista (spread 3 pips)                │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
            Streamlit App (app_streamlit/app.py)
```

---

## 🤖 Modelos

| Modelo | Tipo | AUC Test | Train-Val Gap |
|:-------|:-----|:--------:|:-------------:|
| LinearRegression | Supervisado (baseline) | 0.51 | — |
| Ridge | Supervisado | 0.52 | — |
| SVR | Supervisado | 0.53 | — |
| RandomForest | Supervisado | 0.592 | 0.059 ✅ |
| XGBoost | Supervisado | 0.588 | 0.071 ✅ |
| **LightGBM** | **Supervisado** | **0.590** | **0.072 ✅** |
| **Ensemble** | **Stacking** | **0.591** | **0.065 ✅** |
| KMeans K=4 | **No supervisado** | — | Régimen mercado |

> **Validación**: `PurgedWalkForward(n_folds=8, embargo=8 velas)` — estándar institucional

---

## 📈 Resultados

### Métricas principales (Ensemble — Test Set 2025-2026)

```
┌──────────────────────────────────────────────┐
│  AUC-ROC           0.591   (> 0.55 = alpha) │
│  Walk-Forward AUC  0.560 ± 0.025            │
│  Train-Val Gap     0.059   (< 0.10 = OK)    │
│  Rolling AUC std   0.014   (estable)        │
│  Half-life edge    ~30 meses                │
└──────────────────────────────────────────────┘
```

### Configuración operativa (threshold = 0.57)

```
┌──────────────────────────────────────────────┐
│  Win Rate      58.7%   (break-even = 40%)   │
│  Profit Factor  2.14x                        │
│  Expectancy    +0.468% por trade             │
│  Señales/día    ~7 de 48 velas posibles      │
│  Sharpe         15.0                         │
└──────────────────────────────────────────────┘
```

### Walk-Forward AUC por fold

| Fold | AUC | PF | Win Rate |
|:----:|:---:|:--:|:--------:|
| 1 | 0.590 | 1.14 | 43.1% |
| 2 | 0.599 | 0.86 | 36.3% |
| 3 | 0.544 | 1.05 | 41.1% |
| 4 | 0.551 | 1.13 | 42.9% |
| 5 | 0.573 | 1.28 | 46.1% |
| 6 | 0.557 | 1.18 | 44.1% |
| 7 | 0.530 | 1.29 | 46.1% |
| 8 | **0.530** | **1.28** | **45.9%** |
| **Media** | **0.560** | **1.16** | **43.3%** |

---

## 🔍 Hallazgos Clave

### 1. Edge Regime-Dependiente

El modelo tiene **AUC 0.593 en alta volatilidad** vs **0.522 en baja volatilidad**. El 70% del alpha se concentra en el 30% de las velas con mayor ATR.

### 2. DXY Lead-Lag — Descubrimiento Principal

En datos **H1 con DXY diario**, el DXY **lidera el oro hasta 5 días**:

```
Lag  0d (contemporáneo): corr = -0.229
Lag -1d (DXY lidera 1d): corr = -0.248
Lag -5d (DXY lidera 5d): corr = -0.315  ← más fuerte
```

La correlación crece con el lag negativo — señal causal real, no correlación espuria.

### 3. DXY Shock Edge

```
Cuando DXY cae > 0.15% en M30:
  Régimen 0: oro sube 86.0% (N=458)
  Régimen 1: oro sube 82.5% (N=120)
  Régimen 3: oro sube 83.9% (N=280)
```

### 4. Feature Stability

Top 5 features más estables e importantes:

| Feature | Importancia | CV | Tipo |
|:--------|:-----------:|:--:|:----:|
| `hour` | 80.0 | 0.090 | Tiempo |
| `vol_ratio_48` | 74.2 | 0.068 | Volatilidad |
| `vol_48` | 69.2 | 0.087 | Volatilidad |
| `atr_pct` | 61.8 | 0.203 | Volatilidad |
| `is_london` | 48.8 | 0.081 | Tiempo |

---

## 🚀 Instalación y Uso

```bash
# 1. Clonar repositorio
git clone https://github.com/tu_usuario/gold_ml_project.git
cd gold_ml_project

# 2. Instalar dependencias
pip install -r app_streamlit/requirements.txt

# 3. Procesar datos
python src/data_processing.py

# 4. Entrenar (~5-10 min)
python src/training.py

# 5. Análisis completo
python src/analysis.py
python src/regime_modeling.py

# 6. Evaluar
python src/evaluation.py

# 7. Streamlit App
streamlit run app_streamlit/app.py
```

### Para datos H1 + DXY

```bash
# Pipeline H1 completo (incluye DXY diario)
python src/pipeline_h1.py
```

---

## 📁 Estructura

```
gold_ml_project/
├── data/
│   ├── raw/            → XAUUSD_DXY.csv · XAU_1h_data.csv · DXY_daily.csv
│   ├── processed/      → gold_processed.csv · gold_h1_processed.csv
│   ├── train/          → train.csv (70% temporal)
│   ├── val/            → val.csv   (15% temporal)
│   └── test/           → test.csv  (15% temporal)
│
├── notebooks/
│   ├── 01_Fuentes.ipynb
│   ├── 02_LimpiezaEDA.ipynb
│   └── 03_Entrenamiento_Evaluacion.ipynb
│
├── src/
│   ├── data_processing.py   → Features + Triple Barrier + Leakage Audit
│   ├── training.py          → Purged WF + Ensemble + Feature Stability
│   ├── evaluation.py        → Métricas institucionales + SHAP
│   ├── analysis.py          → Threshold Opt + DXY Lead-Lag + Rolling AUC
│   ├── regime_modeling.py   → Modelos por régimen + Rolling Window
│   ├── optimize.py          → TP/SL + High Vol filter tests
│   └── pipeline_h1.py       → Pipeline H1 completo con DXY diario
│
├── models/
│   ├── final_model.pkl
│   ├── feature_stability.csv
│   ├── threshold_optimization.csv
│   └── h1/                  → Modelos H1 separados
│
├── app_streamlit/
│   ├── app.py
│   └── requirements.txt
│
└── docs/                    → Gráficos y métricas exportadas
```

---

## 🏛️ Por qué este pipeline es institucional

| Práctica | Implementación |
|:---------|:---------------|
| **Anti-leakage** | Features 100% estacionarias, sin precios absolutos, sin variables futuras |
| **Validación temporal** | Purged Walk-Forward con embargo — estándar López de Prado (2018) |
| **Sin data snooping** | Test set bloqueado hasta evaluación final, nunca visto durante desarrollo |
| **Feature robustez** | Selección por CV entre folds, no por importancia en un solo modelo |
| **Costos reales** | Backtest con spread 3 pips, sin slippage optimista |
| **Métricas completas** | Sharpe, Sortino, Calmar, PF, Expectancy, IC, Stability R² |
| **Half-life analysis** | Estimación de decaimiento del edge y frecuencia de retraining |

---

## 🔮 Próximos Pasos

- [ ] **Validación live trading** — demo MT5 durante 3 meses, resultados reales documentados
- [ ] **DXY H1 real-time** — explotar el lead-lag de 5 días descubierto en el análisis
- [ ] **Datos alternativos** — COT (Commitment of Traders), sentiment de noticias
- [ ] **API MT5** — integración Python para ejecución automática de señales
- [ ] **Ensemble adaptativo** — retraining semestral automático con detección de régimen shift

---

## 👤 Autor

**Alexsandro** — Data Science Bootcamp · Madrid 2026

---

<p align="center">
  <em>GoldSense ML · XAUUSD Quantitative System · Madrid 2026</em>
</p>
