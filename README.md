[README.md](https://github.com/user-attachments/files/27749696/README.md)
<div align="center">

<img src="https://img.shields.io/badge/AUREO_SYSTEM-v1.0-FFD700?style=for-the-badge&logo=bitcoin&logoColor=black" alt="version"/>
<img src="https://img.shields.io/badge/XAUUSD-ECN-gold?style=for-the-badge&logo=tradingview&logoColor=black" alt="instrument"/>
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
<img src="https://img.shields.io/badge/MetaTrader-5-1A1A2E?style=for-the-badge&logo=metatrader&logoColor=white" alt="mt5"/>
<img src="https://img.shields.io/badge/Telegram-Alerts-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="telegram"/>

<br/><br/>

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║      ▄▀█ █ █ █▀█ █▀▀ █▀█   █▀ █▄█ █▀ ▀█▀ █▀▀ █▀▄▀█      ║
║      █▀█ █▄█ █▀▄ ██▄ █▄█   ▄█  █  ▄█  █  ██▄ █ ▀ █      ║
║                                                           ║
║        Triple Confluence Engine for XAUUSD               ║
║        Zonas  ×  Gann Estatístico  ×  Fibonacci           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

*Um sistema quantitativo de suporte à decisão para ouro (XAUUSD),*  
*construído sobre três metodologias complementares de análise técnica.*

</div>

---

## ✨ O que é o AUREO SYSTEM?

O AUREO SYSTEM é um motor de confluências para **XAUUSD** que combina três sistemas de análise técnica independentes e só gera sinal quando **todos apontam para o mesmo nível de preço**.

A lógica é simples: quanto mais sistemas confirmam um nível, maior a probabilidade de reação do mercado nesse ponto.

```
                    ┌──────────────────────────────────────┐
                    │          AUREO SYSTEM v1.0           │
                    └─────────────┬────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
      ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
      │   📦 ZONAS    │   │  🔲 GANN BOX  │   │  🌀 FIBONACCI │
      │  (Documento 1)│   │ (Documento 2) │   │ (Documento 3) │
      │               │   │               │   │               │
      │ Vela única    │   │ 2 níveis      │   │ Retrações     │
      │ 20–70 pips    │   │ estatísticos  │   │ 0.618 / 1/φ   │
      │ Contexto 3+3  │   │ M5 reactions  │   │ Extensões     │
      │ Espaço 150pip │   │ qty + volume  │   │ 1.618 / φ     │
      └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   CONFLUENCE ENGINE     │
                    │  Agrupa níveis ±$25     │
                    │                         │
                    │  ⭐ SINGLE   = 1 sistema │
                    │  ⭐⭐ DOUBLE  = 2 sistemas│
                    │  ⭐⭐⭐ TRIPLE = 3 sistemas│ ← Executa ordem
                    └─────────────┬───────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
             📟 Terminal    📱 Telegram    📈 MT5 Order
              (log live)    (alerta)      (BUY/SELL LIMIT)
```

---

## 🏗️ Arquitetura

```
aureo_system/
│
├── main.py                    ← Runner principal (loop duplo)
├── config.py                  ← Toda a configuração aqui
├── diagnose.py                ← Diagnóstico de ligação MT5
│
├── src/
│   ├── mt5_connector.py       ← Ligação MT5 + fetch OHLCV
│   ├── zone_detector.py       ← Documento 1: Zonas válidas
│   ├── gann_analyzer.py       ← Documento 2: Caixa de Gann
│   ├── fibonacci_detector.py  ← Documento 3: Fibonacci φ
│   ├── confluence_engine.py   ← Motor de confluências
│   ├── trade_executor.py      ← Ordens LIMITE no MT5
│   ├── position_manager.py    ← Trailing stop automático
│   └── signal_generator.py   ← Output terminal + Telegram
│
├── logs/
│   └── aureo.log
└── requirements.txt
```

---

## 📐 Os Três Sistemas

### 📦 Sistema 1 — Identificação de Zonas
*Baseado no Programa Formativo – Identificação das Zonas*

Uma zona é válida quando:

| Critério | Regra |
|---|---|
| Estrutura | **1 vela única** — nunca padrão composto |
| Tamanho | Corpo entre **20 e 70 pips** |
| Contexto | Mínimo **3 velas opostas** antes e depois |
| Exceção | H4/D1/W1: aceita **2 antes + 3 depois** |
| Espaçamento | Mínimo **$150** entre zonas |
| Validade | D1: 365 dias · H4: 120 dias · H1: 60 dias |

Os 3 timeframes em cascata:
```
D1 (Primário 1)  →  H4 (Primário 2)  →  H1 (Secundário)
   Visão macro         Estrutura           Refinamento
```

---

### 🔲 Sistema 2 — Caixa de Gann Estatística
*Baseado nos níveis estatísticos da metodologia Gann*

```
  swing_high ──────────────────────  1.000
                                     0.750  ← Prioritário (+ reações)
                                     0.666
                                     0.500  ← Nível central
                                     0.333
                                     0.250  ← Prioritário (+ volume)
  swing_low  ──────────────────────  0.000
```

A análise estatística em **M5** identifica:
- **Prioritário 1** → nível com **mais reações** (quantidade)
- **Prioritário 2** → nível com **maior volume** de reversão

> A estatística é baseada nos **últimos 10 dias** de dados — não no histórico completo. Atualização recomendada a cada 10–15 dias.

---

### 🌀 Sistema 3 — Fibonacci & Número de Ouro
*Baseado no AUREO (φ = 1.618034...)*

```
  Extensões  →  1.618 φ  ────────────── alvo principal
               1.500
               1.333
               1.000  ──────────────── topo do impulso

  Impulso UP ↑

               0.000  ──────────────── base do impulso
  Retrações  →  0.333  ─ terço dourado
               0.382
               0.500  ─ meio
               0.618  ────────────────  1/φ  ← nível dourado
               0.666
```

O número de ouro atravessa toda a metodologia: 0.618 = 1/φ, 1.618 = φ.

---

## ⚙️ Configuração

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/teu-username/aureo-system.git
cd aureo-system

# Instalar dependências
pip install -r requirements.txt
```

> ⚠️ O MetaTrader 5 deve estar **aberto e logado** antes de correr qualquer script.

### Configuração mínima (`config.py`)

```python
# Símbolo — verifica o nome exato no teu broker
SYMBOL = "XAUUSD-ECN"    # VTMarkets · Infinox: "XAUUSD-ECN" ou "XAUUSDm"

# Risco por trade
RISK_PCT   = 0.01    # 1% do saldo
SL_POINTS  = 250     # 250 pontos × $0.10 = $25 de SL
TP_RATIO   = 2.5     # Ratio 1:2.5

# Telegram
TELEGRAM_TOKEN   = "SEU_TOKEN"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID"
TELEGRAM_ENABLED = True

# Execução automática
AUTO_TRADE = True    # False = apenas alertas
```

### Verificar símbolo disponível

```bash
python diagnose.py
```

---

## 🚀 Uso

```bash
# Ver o mapa de confluências (não executa ordens)
python main.py --report

# Loop contínuo com execução automática
python main.py
```

---

## 🔄 Loop de Execução

```
                     python main.py
                           │
              ┌────────────┴────────────┐
              │                         │
          cada 30s                  cada 15min
              │                         │
              ▼                         ▼
    ┌──────────────────┐     ┌───────────────────────┐
    │  Trailing Stop   │     │    Scan Completo       │
    │                  │     │                        │
    │ Fase 1 @ +1R:    │     │ 1. Fetch OHLCV (4 TFs) │
    │ → SL breakeven   │     │ 2. Zonas (D1+H4+H1)   │
    │                  │     │ 3. Gann Box (M5 stats) │
    │ Fase 2 @ +2R:    │     │ 4. Fibonacci (H4)      │
    │ → Trail 1R atrás │     │ 5. Confluências        │
    │                  │     │ 6. Alerta Telegram     │
    │ Fase 3 @ +3R:    │     │ 7. Ordem LIMITE (MT5)  │
    │ → Trail apertado │     │    se TRIPLE ativa     │
    └──────────────────┘     └───────────────────────┘
```

---

## 📱 Alertas Telegram

Quando uma TRIPLE confluência é detetada, o sistema envia:

```
🏆 AUREO SYSTEM — XAUUSD
🕐 2026-05-13 17:16 UTC
💰 Preço atual: 4698.64
──────────────────────────────

#1 — TRIPLE ⭐⭐⭐
🟢 BUY @ 4668.24
📏 Distância: 30 pips
🎯 Score: 32.6
🔗 📦 Zona + 🔲 Gann + 🌀 Fib
  └ Gann 0.750 | Reações: 4
  └ 🌟 Fib 0.382

──────────────────────────────
⚠️ Não é conselho financeiro.
```

---

## 📊 Gestão de Risco

| Parâmetro | Valor | Equivalente |
|---|---|---|
| Risco por trade | 1% do saldo | $500 em conta de $50k |
| Stop Loss | 250 pontos | $25 de distância |
| Take Profit | SL × 2.5 | $62.50 de distância |
| Ratio | 1:2.5 | 40% win rate para breakeven |
| Trailing | 3 fases | Breakeven → Trail 1R → Trail 0.5R |
| Tipo de ordem | LIMIT | Só executa quando preço chega ao nível |

---

## 🧠 Exemplo Real — 13 Mai 2026

```
XAUUSD-ECN @ 4698
─────────────────────────────────────────────────────
4934 ──── DOUBLE ⭐⭐  Zona H4 BEARISH + Fib 1.618φ
─────────────────────────────────────────────────────
4826 ──── Zona H1 BEARISH
4765 ──── Ext Fib 1.0 (topo do impulso recente)
─────────────────────────────────────────────────────
4698 ════ PREÇO ATUAL
─────────────────────────────────────────────────────
4668 ──── TRIPLE ⭐⭐⭐  Zona H4 + Gann 0.75 + Fib 0.382
          └ Gann: 4 reações confirmadas em M5
          └ BUY LIMIT @ 4668 · SL: 4643 · TP: 4730
─────────────────────────────────────────────────────
4602 ──── Fib 0.618 🌟 (nível dourado)
4476 ──── Zona D1 BEARISH
```

---

## 🛠️ Stack Técnica

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Broker API | MetaTrader 5 Python API |
| Dados | OHLCV via `mt5.copy_rates_from_pos` |
| Análise | Pandas + NumPy |
| Alertas | Telegram Bot API |
| Execução | Ordens LIMIT via `mt5.order_send` |

---

## 📁 Ficheiros Principais

| Ficheiro | Função |
|---|---|
| `config.py` | Toda a configuração — começa aqui |
| `diagnose.py` | Verifica ligação MT5 e nome do símbolo |
| `main.py --report` | Scan único com relatório completo |
| `main.py` | Loop contínuo de produção |
| `logs/aureo.log` | Log completo de todas as operações |

---

## ⚠️ Disclaimer

Este sistema é uma ferramenta de **suporte à decisão**. Não garante lucros. O trading de ouro envolve risco significativo de perda de capital. Testa sempre numa conta demo antes de usar capital real.

---

<div align="center">

**Construído com Python · MetaTrader 5 · Fibonacci φ = 1.618**

*"A estatística dentro da metodologia serve como bússola objetiva,*  
*permitindo unir técnica e lógica probabilística."*

<br/>

![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python)
![MT5](https://img.shields.io/badge/MetaTrader-5-darkblue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)

</div>
