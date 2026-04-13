"""
╔══════════════════════════════════════════════════════════════════╗
║       APEX BACKTESTER v2 — Sistema Optimizado EDA-based         ║
║   Activos : XAUUSD · XAGUSD · DXY                               ║
║   Señales : A (Pairs Long Plata) · C (Long Oro puro)            ║
║             Señal B ELIMINADA (WR 25.6%, PF 0.89)               ║
║   CAMBIOS v2: SL 1.5→1.2, TP 2.5→2.0, TimeExit 10→15d         ║
║               GSR umbral A: zscore>1.0→>1.3 (más selectivo)     ║
║               Corr umbral: -0.2 → -0.35 (más exigente)          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import warnings, os
warnings.filterwarnings('ignore')

# ── 0. CONFIGURACIÓN GLOBAL ──────────────────────────────────────────────────
CAPITAL_INICIAL   = 500        # USD
RIESGO_POR_TRADE  = 0.02       # 2% del capital por operación
COMISION_RT       = 0.0005     # 0.05% ida y vuelta (spread típico)
WINDOW_ROLLING    = 252        # días para correlación rodante
ATR_WINDOW        = 14         # días para ATR (stop dinámico)
SL_MULTIPLIER     = 1.2        # v2: bajado 1.5→1.2 (stop más ajustado)
TP_MULTIPLIER     = 2.0        # v2: bajado 2.5→2.0 (más alcanzable)
TIME_EXIT_DAYS    = 15         # v2: ampliado 10→15d (C necesita tiempo)

OUTPUT_DIR = 'backtest_results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. CARGA DE DATOS ────────────────────────────────────────────────────────
print("📂 Cargando datos...")

try:
    df = pd.read_csv('data/raw_data.csv', index_col='Date', parse_dates=True)
    print(f"   ✅ Datos cargados desde CSV: {df.shape[0]} filas")
except FileNotFoundError:
    try:
        import yfinance as yf
        tickers = {"GC=F": "XAUUSD", "SI=F": "XAGUSD", "DX-Y.NYB": "DXY"}
        raw = yf.download(list(tickers.keys()), start="2016-01-01", end="2026-03-29")['Close']
        raw.rename(columns=tickers, inplace=True)
        df = raw.ffill().dropna()
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/raw_data.csv')
        print(f"   ✅ Datos descargados de Yahoo Finance: {df.shape[0]} filas")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        raise

df = df.ffill().dropna()
df.index = pd.to_datetime(df.index)
print(f"   Rango: {df.index.min().date()} → {df.index.max().date()}")

# ── 2. FEATURES DEL EDA ─────────────────────────────────────────────────────
print("\n⚙️  Calculando features...")

# Retornos diarios
returns = df.pct_change() * 100
returns.columns = ['DXY_ret', 'XAUUSD_ret', 'XAGUSD_ret']  # orden: DXY, XAUUSD, XAGUSD

# Gold/Silver Ratio + estadísticas rodantes
df['GSR']          = df['XAUUSD'] / df['XAGUSD']
gsr_mean           = df['GSR'].mean()
gsr_std            = df['GSR'].std()
df['GSR_zscore']   = (df['GSR'] - gsr_mean) / gsr_std

# Correlación rodante DXY / Oro
df['roll_corr_oro']   = (returns['XAUUSD_ret']
                         .rolling(WINDOW_ROLLING)
                         .corr(returns['DXY_ret']))
df['roll_corr_plata'] = (returns['XAGUSD_ret']
                         .rolling(WINDOW_ROLLING)
                         .corr(returns['DXY_ret']))

# DXY momentum (media 3 días para suavizar ruido)
df['DXY_mom3'] = returns['DXY_ret'].rolling(3).mean()

# ATR simplificado para XAUUSD y XAGUSD
def calc_atr(prices, window=ATR_WINDOW):
    tr = prices.diff().abs()
    return tr.rolling(window).mean()

df['ATR_oro']   = calc_atr(df['XAUUSD'])
df['ATR_plata'] = calc_atr(df['XAGUSD'])

df.dropna(inplace=True)
print(f"   ✅ Features calculadas — {df.shape[0]} filas válidas para backtest")

# ── 3. MOTOR DE SEÑALES ──────────────────────────────────────────────────────
"""
LÓGICA DE SEÑALES (derivada directamente del EDA):

SEÑAL A — Long Plata / Short Oro (ratio muy alto = plata barata)
  • GSR z-score > +1.0  → ratio está 1σ por encima de su media
  • DXY_mom3 < -0.15    → dólar con momentum bajista (favorable a metales)
  • roll_corr_oro < -0.2 → correlación activa (mercado en régimen normal)

SEÑAL B — Long Oro / Short Plata (ratio muy bajo = oro barato)
  • GSR z-score < -0.8  → ratio 0.8σ por debajo (plata relativamente cara)
  • DXY_mom3 > +0.15    → dólar con momentum alcista
  • roll_corr_oro < -0.2 → correlación activa

SEÑAL C — Long Oro puro (DXY cayendo fuerte, correlación rota)
  • DXY_mom3 < -0.3     → caída significativa del dólar (H4: 78.5% acierto)
  • roll_corr_oro < -0.1 → correlación activa
  • GSR_zscore entre -0.5 y +0.5 → ratio neutral (no hay divergencia extrema)
"""

def generate_signals(df):
    sig = pd.Series(0, index=df.index, name='signal')
    trade_type = pd.Series('', index=df.index, name='trade_type')

    for i in range(1, len(df)):
        row = df.iloc[i]

        # SEÑAL A v2: Long Plata / Short Oro
        # Cambio: GSR zscore subido 1.0→1.3 (más selectivo, menos trades falsos)
        # Cambio: correlación más exigente -0.2→-0.35
        if (row['GSR_zscore'] > 1.3 and
            row['DXY_mom3'] < -0.15 and
            row['roll_corr_oro'] < -0.35):
            sig.iloc[i]        = 1
            trade_type.iloc[i] = 'A_LongPlata_ShortOro'

        # SEÑAL B: ELIMINADA — WR 25.6%, Profit Factor 0.89 (destruía capital)

        # SEÑAL C v2: Long Oro puro
        # Cambio: correlación más exigente -0.1→-0.35 (evita entrar en régimen roto)
        # Cambio: GSR neutral ampliado a ±0.8 (más oportunidades válidas)
        elif (row['DXY_mom3'] < -0.3 and
              row['roll_corr_oro'] < -0.35 and
              -0.8 < row['GSR_zscore'] < 0.8):
            sig.iloc[i]        = 3
            trade_type.iloc[i] = 'C_LongOro'

    return sig, trade_type

print("\n📡 Generando señales...")
df['signal'], df['trade_type'] = generate_signals(df)
total_signals = (df['signal'] > 0).sum()
print(f"   Total señales generadas: {total_signals}")
for t in ['A_LongPlata_ShortOro', 'C_LongOro']:
    n = (df['trade_type'] == t).sum()
    print(f"   {t}: {n} señales")

# ── 4. SIMULACIÓN DE TRADES ──────────────────────────────────────────────────
print("\n💹 Simulando trades...")

trades = []
capital   = CAPITAL_INICIAL
equity    = [CAPITAL_INICIAL]
equity_dates = [df.index[0]]

in_trade  = False
trade_open = {}

for i in range(len(df)):
    row      = df.iloc[i]
    date     = df.index[i]
    signal   = row['signal']

    if not in_trade and signal > 0:
        # Calcular tamaño de posición basado en riesgo
        if signal == 1:   # Pairs trade (solo A)
            atr_ref = (row['ATR_oro'] + row['ATR_plata']) / 2
            price_ref = row['XAUUSD']
        else:                   # Long Oro puro
            atr_ref   = row['ATR_oro']
            price_ref = row['XAUUSD']

        stop_dist   = SL_MULTIPLIER * atr_ref
        risk_amount = capital * RIESGO_POR_TRADE
        size        = risk_amount / stop_dist if stop_dist > 0 else 0

        if size > 0:
            in_trade  = True
            trade_open = {
                'entry_date'  : date,
                'entry_price' : price_ref,
                'signal_type' : row['trade_type'],
                'stop_loss'   : price_ref - stop_dist if signal != 2 else price_ref + stop_dist,
                'take_profit' : price_ref + TP_MULTIPLIER * stop_dist if signal != 2 else price_ref - TP_MULTIPLIER * stop_dist,
                'size'        : size,
                'atr'         : atr_ref,
            }

    elif in_trade:
        current_price = row['XAUUSD']
        sl = trade_open['stop_loss']
        tp = trade_open['take_profit']
        stype = trade_open['signal_type']

        hit_sl = current_price <= sl   # A y C son long → SL abajo
        hit_tp = current_price >= tp   # A y C son long → TP arriba

        # Time exit dinámico (v2: 15 días)
        days_in = (date - trade_open['entry_date']).days

        if hit_sl or hit_tp or days_in >= TIME_EXIT_DAYS:
            if hit_tp:
                pnl_pct = RIESGO_POR_TRADE * TP_MULTIPLIER
                result  = 'WIN'
            elif hit_sl:
                pnl_pct = -RIESGO_POR_TRADE
                result  = 'LOSS'
            else:  # time exit — siempre long (A y C)
                price_chg = (current_price - trade_open['entry_price']) / trade_open['entry_price']
                pnl_pct = price_chg
                result  = 'WIN' if pnl_pct > 0 else 'LOSS'

            # Aplicar comisión
            pnl_pct -= COMISION_RT
            pnl_usd  = capital * pnl_pct
            capital += pnl_usd

            trades.append({
                'entry_date'  : trade_open['entry_date'],
                'exit_date'   : date,
                'signal_type' : stype,
                'entry_price' : trade_open['entry_price'],
                'exit_price'  : current_price,
                'result'      : result,
                'pnl_pct'     : round(pnl_pct * 100, 3),
                'pnl_usd'     : round(pnl_usd, 2),
                'capital'     : round(capital, 2),
                'days'        : days_in,
            })

            in_trade   = False
            trade_open = {}

        equity.append(capital)
        equity_dates.append(date)

# ── 5. MÉTRICAS ──────────────────────────────────────────────────────────────
print("\n📊 Calculando métricas...")

trades_df = pd.DataFrame(trades)
equity_s  = pd.Series(equity, index=equity_dates)

if len(trades_df) == 0:
    print("❌ Sin trades ejecutados. Revisar umbrales de señales.")
else:
    wins      = trades_df[trades_df['result'] == 'WIN']
    losses    = trades_df[trades_df['result'] == 'LOSS']
    win_rate  = len(wins) / len(trades_df) * 100
    avg_win   = wins['pnl_pct'].mean() if len(wins) else 0
    avg_loss  = losses['pnl_pct'].mean() if len(losses) else 0
    profit_factor = abs(wins['pnl_pct'].sum() / losses['pnl_pct'].sum()) if len(losses) else np.inf

    total_return = (capital - CAPITAL_INICIAL) / CAPITAL_INICIAL * 100
    years        = (df.index[-1] - df.index[0]).days / 365.25
    cagr         = ((capital / CAPITAL_INICIAL) ** (1 / years) - 1) * 100

    # Drawdown
    eq_peak   = equity_s.cummax()
    drawdown  = (equity_s - eq_peak) / eq_peak * 100
    max_dd    = drawdown.min()

    # Sharpe anualizado (retornos diarios de equity)
    eq_ret    = equity_s.pct_change().dropna()
    sharpe    = (eq_ret.mean() / eq_ret.std()) * np.sqrt(252) if eq_ret.std() > 0 else 0

    print("\n" + "═"*55)
    print("          RESULTADOS DEL BACKTEST (2016–2026)")
    print("═"*55)
    print(f"  Capital inicial        : ${CAPITAL_INICIAL:,.0f}")
    print(f"  Capital final          : ${capital:,.2f}")
    print(f"  Retorno total          : {total_return:+.1f}%")
    print(f"  CAGR (anualizado)      : {cagr:+.1f}%")
    print(f"  Sharpe Ratio           : {sharpe:.2f}")
    print(f"  Drawdown máximo        : {max_dd:.1f}%")
    print("─"*55)
    print(f"  Total trades           : {len(trades_df)}")
    print(f"  Win Rate               : {win_rate:.1f}%")
    print(f"  Profit Factor          : {profit_factor:.2f}")
    print(f"  Ganancia media (win)   : {avg_win:+.2f}%")
    print(f"  Pérdida media (loss)   : {avg_loss:+.2f}%")
    print("─"*55)
    for t in ['A_LongPlata_ShortOro', 'C_LongOro']:
        sub = trades_df[trades_df['signal_type'] == t]
        if len(sub) > 0:
            wr = (sub['result'] == 'WIN').mean() * 100
            print(f"  {t[:22]:22s}: {len(sub):3d} trades  WR={wr:.0f}%")
    print("═"*55)

    # Guardar trades
    trades_df.to_csv(f'{OUTPUT_DIR}/trades.csv', index=False)

# ── 6. GRÁFICOS ──────────────────────────────────────────────────────────────
print("\n🎨 Generando gráficos...")

fig = plt.figure(figsize=(18, 22))
fig.patch.set_facecolor('#0d1117')
gs  = gridspec.GridSpec(5, 2, figure=fig, hspace=0.45, wspace=0.3)

GOLD   = '#FFD700'
SILVER = '#C0C0C0'
BLUE   = '#4A90D9'
GREEN  = '#51CF66'
RED    = '#FF6B6B'
WHITE  = '#E8E8E8'
GRAY   = '#555555'
BG     = '#0d1117'
PANEL  = '#161b22'

def style_ax(ax, title=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=WHITE, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRAY)
    if title:
        ax.set_title(title, color=WHITE, fontsize=10, fontweight='bold', pad=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

# ── Panel 1: Equity Curve ────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
style_ax(ax1, '📈 Equity Curve — Capital $500 inicial')
ax1.plot(equity_s.index, equity_s.values, color=GOLD, linewidth=1.8, label='Equity')
ax1.axhline(CAPITAL_INICIAL, color=GRAY, linewidth=0.8, linestyle='--', label='Capital inicial')
ax1.fill_between(equity_s.index, CAPITAL_INICIAL, equity_s.values,
                 where=(equity_s.values >= CAPITAL_INICIAL), alpha=0.15, color=GREEN)
ax1.fill_between(equity_s.index, CAPITAL_INICIAL, equity_s.values,
                 where=(equity_s.values < CAPITAL_INICIAL), alpha=0.15, color=RED)
ax1.set_ylabel('Capital (USD)', color=WHITE, fontsize=9)
ax1.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# Anotar capital final
ax1.annotate(f'${capital:,.0f}', xy=(equity_s.index[-1], equity_s.iloc[-1]),
             xytext=(-60, 12), textcoords='offset points',
             color=GOLD, fontsize=9, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=GOLD, lw=1))

# ── Panel 2: Drawdown ────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, :])
style_ax(ax2, f'📉 Drawdown — Máximo: {max_dd:.1f}%')
ax2.fill_between(drawdown.index, drawdown.values, 0, color=RED, alpha=0.6)
ax2.plot(drawdown.index, drawdown.values, color=RED, linewidth=0.8)
ax2.set_ylabel('Drawdown (%)', color=WHITE, fontsize=9)

# ── Panel 3: GSR con señales ─────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2, :])
style_ax(ax3, '🔄 Gold/Silver Ratio con Señales de Entrada')
ax3.plot(df.index, df['GSR'], color=GOLD, linewidth=1.2, label='Ratio G/S')
ax3.axhline(gsr_mean,           color=WHITE,  linewidth=0.8, linestyle='--', alpha=0.6, label=f'Media ({gsr_mean:.1f})')
ax3.axhline(gsr_mean + gsr_std, color=RED,    linewidth=0.8, linestyle=':',  alpha=0.7, label=f'+1σ ({gsr_mean+gsr_std:.1f})')
ax3.axhline(gsr_mean - gsr_std, color=GREEN,  linewidth=0.8, linestyle=':',  alpha=0.7, label=f'-1σ ({gsr_mean-gsr_std:.1f})')

# Marcar entradas
sig_a = df[df['trade_type'] == 'A_LongPlata_ShortOro']
sig_b = df[df['trade_type'] == 'B_LongOro_ShortPlata']
sig_c = df[df['trade_type'] == 'C_LongOro']
ax3.scatter(sig_a.index, sig_a['GSR'], marker='^', color=GREEN,  s=40, zorder=5, label='Señal A (Long Plata)')
ax3.scatter(sig_b.index, sig_b['GSR'], marker='v', color=RED,    s=40, zorder=5, label='Señal B (Long Oro)')
ax3.scatter(sig_c.index, sig_c['GSR'], marker='D', color=BLUE,   s=25, zorder=5, label='Señal C (Oro puro)')
ax3.set_ylabel('Ratio (oz Au / oz Ag)', color=WHITE, fontsize=9)
ax3.legend(fontsize=7, facecolor=PANEL, labelcolor=WHITE, ncol=3)

# ── Panel 4: Correlación rodante ─────────────────────────────────────────────
ax4 = fig.add_subplot(gs[3, 0])
style_ax(ax4, '🔗 Correlación Rodante 252d vs DXY')
ax4.plot(df.index, df['roll_corr_oro'],   color=GOLD,   linewidth=1.2, label='Oro/DXY')
ax4.plot(df.index, df['roll_corr_plata'], color=SILVER, linewidth=1.2, label='Plata/DXY')
ax4.axhline(0, color=WHITE, linewidth=0.6, linestyle=':')
ax4.axhline(-0.2, color=GRAY, linewidth=0.6, linestyle='--', alpha=0.5, label='Umbral señal (-0.2)')
ax4.set_ylabel('Correlación', color=WHITE, fontsize=9)
ax4.legend(fontsize=7, facecolor=PANEL, labelcolor=WHITE)
ax4.set_ylim(-1, 1)

# ── Panel 5: Distribución P&L ────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[3, 1])
ax5.set_facecolor(PANEL)
ax5.tick_params(colors=WHITE, labelsize=8)
for spine in ax5.spines.values():
    spine.set_edgecolor(GRAY)
ax5.set_title('📊 Distribución P&L por Trade (%)', color=WHITE, fontsize=10, fontweight='bold', pad=8)

if len(trades_df) > 0:
    wins_pnl   = trades_df[trades_df['result'] == 'WIN']['pnl_pct']
    losses_pnl = trades_df[trades_df['result'] == 'LOSS']['pnl_pct']
    ax5.hist(wins_pnl,   bins=20, color=GREEN, alpha=0.7, label=f'Wins ({len(wins_pnl)})')
    ax5.hist(losses_pnl, bins=20, color=RED,   alpha=0.7, label=f'Losses ({len(losses_pnl)})')
    ax5.axvline(0, color=WHITE, linewidth=0.8, linestyle='--')
    ax5.set_xlabel('P&L (%)', color=WHITE, fontsize=9)
    ax5.legend(fontsize=8, facecolor=PANEL, labelcolor=WHITE)

# ── Panel 6: Métricas resumen ────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[4, :])
ax6.set_facecolor(PANEL)
ax6.axis('off')

metrics = [
    ['Capital inicial', f'${CAPITAL_INICIAL:,.0f}',   'Capital final',    f'${capital:,.2f}'],
    ['Retorno total',   f'{total_return:+.1f}%',       'CAGR',             f'{cagr:+.1f}%'],
    ['Sharpe Ratio',    f'{sharpe:.2f}',               'Max Drawdown',     f'{max_dd:.1f}%'],
    ['Total Trades',    f'{len(trades_df)}',           'Win Rate',         f'{win_rate:.1f}%'],
    ['Profit Factor',   f'{profit_factor:.2f}',        'Comisión aplicada',f'{COMISION_RT*100:.2f}% RT'],
]

col_labels = ['Métrica', 'Valor', 'Métrica', 'Valor']
table = ax6.table(
    cellText=metrics,
    colLabels=col_labels,
    cellLoc='center',
    loc='center',
    bbox=[0, 0, 1, 1]
)
table.auto_set_font_size(False)
table.set_fontsize(9)
for (r, c), cell in table.get_celld().items():
    cell.set_facecolor('#21262d' if r % 2 == 0 else PANEL)
    cell.set_text_props(color=GOLD if c in [1, 3] else WHITE)
    cell.set_edgecolor(GRAY)
    if r == 0:
        cell.set_facecolor('#30363d')
        cell.set_text_props(color=WHITE, fontweight='bold')

fig.suptitle('APEX BACKTESTER v2 — Optimizado | XAUUSD · XAGUSD · DXY | 2016–2026 | Señal B eliminada',
             color=WHITE, fontsize=13, fontweight='bold', y=0.98)

plt.savefig(f'{OUTPUT_DIR}/backtest_report.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close()
print(f"   ✅ Gráfico guardado en {OUTPUT_DIR}/backtest_report.png")
print(f"   ✅ Trades guardados en {OUTPUT_DIR}/trades.csv")
print("\n✅ Backtest completado.")
