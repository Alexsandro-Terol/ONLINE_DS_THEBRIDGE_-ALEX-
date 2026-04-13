# 📊 ¿Puede el Dólar Predecir el Precio del Oro?
### Análisis Exploratorio de Datos — Oro, Plata y DXY (2016–2026)

**Autor:** Alexsandro Luiz Terol  
**Módulo:** Data Analysis Bootcamp  
**Fecha:** Abril 2025

---

## 🎯 Objetivo

Analizar la relación entre el Índice del Dólar Americano (DXY) y los metales preciosos (Oro y Plata) durante la última década, verificando si el comportamiento del dólar puede utilizarse como señal predictiva para operar en mercados de materias primas.

---

## ❓ Pregunta de investigación

> Cuando el dólar sube o baja, ¿qué le pasa al oro y a la plata?  
> ¿Es el Gold/Silver Ratio un oscilador estadístico útil para detectar oportunidades?

---

## 💡 Hipótesis

| ID | Hipótesis | Resultado |
|----|-----------|-----------|
| H1 | El Oro mantiene correlación negativa fuerte (< -0.80) con el DXY | ⚠️ Parcialmente confirmada (-0.39) |
| H2 | La Plata es más volátil que el Oro | ✅ Confirmada (2× más volátil) |
| H3 | El Gold/Silver Ratio actúa como oscilador estadístico | ✅ Confirmada (rango 44–126) |
| H4 | Una caída del DXY garantiza subida en los metales | ⚠️ Parcialmente confirmada (78.5%) |

---

## 📁 Estructura del proyecto

```
PROYECTO - EDA/
│
├── src/
│   ├── data/
│   │   └── raw_data.csv              # Datos históricos diarios 2016–2026
│   │
│   ├── notebooks/
│   │   └── memoria.ipynb             # Notebook de análisis exploratorio
│   │
│   ├── backtesting/
│   │   ├── backtester_apex.py        # Backtester v1
│   │   ├── backtester_v2.py          # Backtester v2 optimizado
│   │   └── results/
│   │       ├── backtest_report.png
│   │       └── trades.csv
│   │
│   └── reports/
│       └── figures/                  # Gráficos generados
│           ├── A_precios_normalizados.png
│           ├── B_heatmap_correlacion.png
│           ├── C_boxplot_volatilidad.png
│           ├── D_ratio_oro_plata.png
│           ├── E_correlacion_rodante.png
│           └── F_univariante_distribuciones.png
│
├── EDA_Presentacion_Alexsandro.pptx  # Presentación para público no técnico
└── README.md
```

---

## 🔍 Metodología

1. **Obtención de datos** — API de MetaTrader 5 / Yahoo Finance (`yfinance`)
2. **Limpieza** — Forward-fill para días festivos, eliminación de NaN
3. **Feature engineering** — Retornos diarios, Gold/Silver Ratio, correlación rodante 252d
4. **Análisis univariante** — Estadísticos de centralidad y dispersión por activo
5. **Análisis bivariante** — Heatmap de correlaciones sobre retornos
6. **Análisis multivariante** — Correlación rodante temporal
7. **Backtesting** — Sistema de señales cuantitativas probado sobre 10 años

---

## 📈 Resultados principales

| Métrica | Valor |
|---------|-------|
| Correlación Oro/DXY | **-0.39** |
| Correlación Plata/DXY | **-0.33** |
| Correlación Oro/Plata | **+0.77** |
| Volatilidad Plata vs Oro | **2× más volátil** |
| Días que DXY↓ y Oro↑ | **78.5%** de los casos |
| Gold/Silver Ratio medio | **80.9** (rango: 44–126) |

### Backtesting v2 (sistema optimizado)
- Capital inicial: **$500** → Capital final: **$772**
- Retorno total: **+54.4%** en 10 años
- Sharpe Ratio: **2.04** ✅
- Drawdown máximo: **-10.1%**
- Win Rate: **46.8%** | Profit Factor: **1.72**

---

## 🛠️ Tecnologías utilizadas

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?logo=pandas)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7-blue)
![Seaborn](https://img.shields.io/badge/Seaborn-0.12-blue)
![Scipy](https://img.shields.io/badge/Scipy-1.10-blue)
![yfinance](https://img.shields.io/badge/yfinance-0.2-green)

```
pandas · numpy · matplotlib · seaborn · scipy · yfinance
```

---

## 🚀 Próximos pasos

- [ ] **Fase ML** — Clasificador Random Forest / XGBoost sobre los 62 trades del backtest
- [ ] **Paper Trading** — Validación en tiempo real durante 3–6 meses
- [ ] **Live Trading** — Despliegue con gestión de riesgo estricta (2% por operación)

---

## ▶️ Cómo ejecutar

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu_usuario/proyecto-eda-forex

# 2. Instalar dependencias
pip install pandas numpy matplotlib seaborn scipy yfinance

# 3. Ejecutar el notebook
cd src/
jupyter notebook notebooks/memoria.ipynb

# 4. Ejecutar el backtester
python backtesting/backtester_v2.py
```

---

## 📬 Contacto

**Alexsandro Luiz Terol**  
Data Analysis Bootcamp · 2025
