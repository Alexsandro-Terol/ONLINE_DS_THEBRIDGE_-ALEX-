# 🏆 CICLO ÁUREO DE 3 ONDAS — EA v1.0
### Elliott Waves + Fibonacci do 3 + Proporção Áurea + IA Fractal

---

## 📁 ESTRUTURA DE ARQUIVOS

```
ESTRATEGIA AUREA/
├── CicloAureo_EA.mq5          ← Expert Advisor principal
├── Include/
│   ├── CA_MarketStructure.mqh  ← Engine de estrutura de mercado
│   ├── CA_ElliottWave.mqh      ← Detector de ondas de Elliott
│   ├── CA_FibonacciEngine.mqh  ← Fibonacci personalizado (0.333/0.666/1.618)
│   ├── CA_LiquidityEngine.mqh  ← Sweep, order blocks, liquidez
│   ├── CA_AIProbability.mqh    ← Sistema de Score IA (0-10)
│   ├── CA_TradeExecution.mqh   ← Motor de execução de ordens
│   ├── CA_RiskManagement.mqh   ← Gestão de risco e limites diários
│   └── CA_Visualization.mqh    ← Painel visual e desenho no gráfico
└── README.md
```

---

## ⚙️ INSTALAÇÃO (MetaTrader 5)

### Passo 1 — Copiar arquivos

Abra a pasta de dados do MT5:
```
Menu: Arquivo → Abrir pasta de dados
```

Copie os arquivos:

| Origem (esta pasta)         | Destino (MT5)                        |
|-----------------------------|--------------------------------------|
| `CicloAureo_EA.mq5`        | `MQL5\Experts\CicloAureo\`          |
| `Include\CA_*.mqh`          | `MQL5\Include\CicloAureo\`          |

### Passo 2 — Ajustar os #include no EA

Abra `CicloAureo_EA.mq5` no MetaEditor e confirme que as linhas de include estão assim:

```mql5
#include <CicloAureo\CA_MarketStructure.mqh>
#include <CicloAureo\CA_ElliottWave.mqh>
#include <CicloAureo\CA_FibonacciEngine.mqh>
#include <CicloAureo\CA_LiquidityEngine.mqh>
#include <CicloAureo\CA_AIProbability.mqh>
#include <CicloAureo\CA_TradeExecution.mqh>
#include <CicloAureo\CA_RiskManagement.mqh>
#include <CicloAureo\CA_Visualization.mqh>
```

> ⚠️ **Atenção:** Se colocar o EA diretamente em `MQL5\Experts\` (sem subpasta)
> e os includes em `MQL5\Include\CicloAureo\`, use `<CicloAureo\...>`.
> Se colocar tudo na mesma pasta do EA, use `"Include\CA_...mqh"` (caminho relativo).

### Passo 3 — Compilar

No MetaEditor:
```
Abrir CicloAureo_EA.mq5 → F7 (Compilar)
```
Deve compilar com 0 erros.

### Passo 4 — Ativar no gráfico

1. Abrir gráfico XAUUSD M15
2. Arrastar o EA da aba **Navigator → Expert Advisors**
3. Ativar **"Allow Algo Trading"** (botão na barra do MT5)
4. Configurar os parâmetros conforme abaixo

---

## 🎛️ PARÂMETROS RECOMENDADOS

### Para XAUUSD (Ouro)

| Parâmetro         | Valor recomendado | Descrição                        |
|-------------------|-------------------|----------------------------------|
| InpStructureTF    | M15               | Timeframe estrutural             |
| InpExecTF         | M5                | Timeframe de confirmação         |
| InpSwingLookback  | 5                 | Sensibilidade dos swings         |
| InpHistoryBars    | 300               | Barras analisadas                |
| InpMinScore       | **6**             | Score mínimo (conservador: 7)    |
| InpRiskPercent    | 1.0               | 1% por operação                  |
| InpDailyLossLimit | 3.0               | Para se perder 3% no dia         |
| InpDailyGainLimit | 6.0               | Para se ganhar 6% no dia         |
| InpUseBreakEven   | true              | Move SL ao custo após 1:1        |
| InpUseTrailing    | **false**         | OFF recomendado para ouro (M15)  |
| InpTrailPoints    | 200               | (caso ative trailing)            |
| InpMaxPositions   | 1                 | 1 posição por vez                |
| InpAllowBuy       | true              | Permite compras                  |
| InpAllowSell      | true              | Permite vendas                   |

> 💡 **Trailing Stop desativado por padrão** — testado empiricamente:
> o ouro em M15 tem comportamento mean-reverting que destrói trailing stops.
> Use apenas Break-Even.

### Para Forex / Índices

| Parâmetro         | Valor sugerido |
|-------------------|----------------|
| InpStructureTF    | M15 ou H1      |
| InpExecTF         | M5             |
| InpSwingLookback  | 4              |
| InpMinScore       | 6              |
| InpRiskPercent    | 0.5 – 1.0      |
| InpUseTrailing    | true           |

---

## 📊 SISTEMA DE SCORE IA

| Critério              | Pontos | Descrição                              |
|-----------------------|--------|----------------------------------------|
| ✅ Elliott válida      | +2     | Estrutura 1-2 confirmada               |
| ✅ Fibonacci 0.333     | +1     | Correção na zona primária leve         |
| ✅ Fibonacci 0.666     | +2     | Correção na zona primária forte        |
| ✅ Volume crescente    | +1     | Volume ascendente nas últimas 3 barras |
| ✅ Sweep de liquidez   | +2     | Falsa quebra + retorno ao range        |
| ✅ Candle impulsivo    | +1     | Corpo ≥ 60% do range do candle         |
| ✅ Tendência forte     | +1     | TrendStrength ≥ 0.65                   |
| **Total máximo**      | **10** |                                        |

**Score mínimo recomendado: 6/10**
- Score 8-10 → Alta probabilidade → operar com confiança
- Score 6-7  → Probabilidade moderada → operar com cautela
- Score < 6  → Ignorar o sinal

---

## 🔄 LÓGICA OPERACIONAL

### BUY (Tendência de Alta)
```
1. IA detecta Onda 1 impulsiva de alta
2. Onda 2 corrige até zona 0.333 ou 0.666
3. Score IA ≥ mínimo configurado
4. Candle impulsivo confirmador no M5
5. ENTRADA → início da Onda 3
6. STOP    → abaixo do início da Onda 1
7. TARGET  → extensão 1.618 da Onda 1
```

### SELL (Tendência de Baixa)
```
1. IA detecta Onda 1 impulsiva de baixa
2. Onda 2 corrige até zona 0.333 ou 0.666
3. Score IA ≥ mínimo configurado
4. Candle de rejeição confirmado no M5
5. ENTRADA → início da Onda 3 baixa
6. STOP    → acima do início da Onda 1
7. TARGET  → extensão 1.618 abaixo
```

---

## ❌ FILTROS — EA não opera quando:

- Mercado em lateralização (range)
- Baixa volatilidade (ATR < 0.3% do preço)
- Limite diário de perda atingido
- Limite diário de ganho atingido
- Score abaixo do mínimo configurado
- Notícias de alto impacto (se InpNewsFilter=true)
- Já existe posição aberta (InpMaxPositions=1)
- Correção maior que o impulso (invalida Elliott)

---

## 🖥️ PAINEL VISUAL

O EA desenha automaticamente no gráfico:

| Elemento                  | Cor            |
|---------------------------|----------------|
| Onda 1 (impulsiva)        | Azul           |
| Onda 2 (corretiva)        | Laranja        |
| Zona de entrada 0.333-0.666 | Verde/Vermelho transparente |
| Fibonacci 0.111           | Cinza          |
| Fibonacci 0.333           | Verde          |
| Fibonacci 0.666           | Azul           |
| Fibonacci 0.999           | Laranja        |
| Alvo 1.618                | Dourado ★      |
| Seta de entrada           | Verde (BUY) / Vermelho (SELL) |
| Painel Score              | Canto superior esquerdo |

---

## 🧠 MÓDULOS DO SISTEMA

```
┌─────────────────────────────────────────────┐
│          CicloAureo_EA.mq5 (Main)           │
├──────────────┬──────────────────────────────┤
│ Market       │ DetectSwings()               │
│ Structure    │ IsUptrend() / IsDowntrend()  │
│ Engine       │ GetTrendStrength()           │
├──────────────┼──────────────────────────────┤
│ Elliott      │ Analyze() — Onda 1/2/3       │
│ Wave         │ IsBuySignal()                │
│ Detector     │ IsSellSignal()               │
├──────────────┼──────────────────────────────┤
│ Fibonacci    │ Calculate(high, low)         │
│ Engine       │ IsIn333Zone() / IsIn666Zone()│
│              │ GetRiskReward()              │
├──────────────┼──────────────────────────────┤
│ Liquidity    │ Analyze(level, bullish)      │
│ Engine       │ IsSweep() / IsOrderBlock()   │
│              │ IsImpulsiveCandle()          │
├──────────────┼──────────────────────────────┤
│ AI           │ Calculate() → ScoreBreakdown │
│ Probability  │ IsSignalApproved(minScore)   │
│ Engine       │ ShouldSkipTrade()            │
├──────────────┼──────────────────────────────┤
│ Trade        │ OpenBuy() / OpenSell()       │
│ Execution    │ CloseAll() / ModifyPosition()│
├──────────────┼──────────────────────────────┤
│ Risk         │ CalculateLotSize()           │
│ Management   │ ManageBreakEven()            │
│              │ ManageTrailingStop()         │
│              │ IsDailyLossBreached()        │
├──────────────┼──────────────────────────────┤
│ Visualization│ DrawWaves() / DrawFibonacci()│
│ Engine       │ DrawEntryZone()              │
│              │ DrawScorePanel()             │
└──────────────┴──────────────────────────────┘
```

---

## ⚠️ AVISOS IMPORTANTES

1. **Sempre teste em conta demo primeiro** antes de conta real
2. O EA foi desenvolvido para **XAUUSD M15** como timeframe primário
3. Nunca arrisque mais de **1-2% por operação**
4. O sistema não garante resultados — mercados são imprevisíveis
5. Trailing Stop está **desativado por padrão** para ouro (comportamento mean-reverting)
6. Se o compilador mostrar erro de `#include`, verifique os caminhos (ver Passo 2)

---

## 📞 SUPORTE / CUSTOMIZAÇÃO

Desenvolvido com arquitetura modular — cada módulo pode ser ajustado
independentemente sem afetar os demais.

Para adicionar novos filtros: editar `CA_AIProbability.mqh`
Para ajustar a detecção de ondas: editar `CA_ElliottWave.mqh`
Para mudar o visual: editar `CA_Visualization.mqh`
