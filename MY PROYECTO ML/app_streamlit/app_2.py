"""
app_streamlit/app.py
Print Money Factory — XAUUSD Decision Support System
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

st.set_page_config(
    page_title="XAUUSD · Decision Support System",
    page_icon="⚡", layout="wide",
)

st.markdown("""
<style>
.main,.stApp{background:#0D1117}
.signal-buy {background:#064E3B;border:2px solid #10B981;border-radius:12px;padding:20px;text-align:center}
.signal-sell{background:#450A0A;border:2px solid #EF4444;border-radius:12px;padding:20px;text-align:center}
.signal-hold{background:#1C1917;border:2px solid #78716C;border-radius:12px;padding:20px;text-align:center}
</style>
""", unsafe_allow_html=True)

BASE_DIR  = Path(__file__).parent.parent
DATA_DIR  = BASE_DIR / "data" / "raw"
MODEL_DIR = BASE_DIR / "models"

# ── Helpers ───────────────────────────────────────────────────────────
def _ema(s,n): return s.ewm(span=n,adjust=False).mean()

def _atr(df,n=14):
    tr=pd.concat([df.high-df.low,(df.high-df.close.shift(1)).abs(),
                  (df.low-df.close.shift(1)).abs()],axis=1).max(axis=1)
    return tr.ewm(span=n,adjust=False).mean()

def _adx(df,n=14):
    hi,lo=df.high,df.low
    up=hi.diff().clip(lower=0); dn=(-lo.diff()).clip(lower=0)
    pdm=up.where(up>dn,0.0); mdm=dn.where(dn>up,0.0)
    a=_atr(df,n)
    pdi=100*pdm.ewm(span=n,adjust=False).mean()/(a+1e-10)
    mdi=100*mdm.ewm(span=n,adjust=False).mean()/(a+1e-10)
    dx=100*(pdi-mdi).abs()/(pdi+mdi+1e-10)
    return dx.ewm(span=n,adjust=False).mean()

def _pctrank(s,w):
    v=s.values.astype(np.float64); n=len(v)
    out=np.full(n,np.nan)
    if n<w: return pd.Series(out,index=s.index)
    wins=np.lib.stride_tricks.as_strided(v,shape=(n-w+1,w),strides=(v.strides[0],v.strides[0]))
    out[w-1:]=(wins<=wins[:,-1:]).sum(axis=1)/w
    return pd.Series(out,index=s.index)

@st.cache_data(ttl=300)
def load_csv(path):
    if not path.exists(): return None
    with open(path,"r",encoding="utf-8",errors="replace") as f: first=f.readline()
    sep=";" if first.count(";")>first.count(",") else ","
    df=pd.read_csv(path,sep=sep)
    df.columns=[c.strip().lower() for c in df.columns]
    tcol=next((c for c in df.columns if c in ["date","time","datetime","timestamp"]),df.columns[0])
    s=str(df[tcol].iloc[0])
    if len(s)>=10 and s[4]=="." and s[7]==".":
        df[tcol]=df[tcol].astype(str).str.replace(r"^(\d{4})\.(\d{2})\.(\d{2})",r"\1-\2-\3",regex=True)
    df[tcol]=pd.to_datetime(df[tcol],errors="coerce")
    df=(df.dropna(subset=[tcol]).rename(columns={tcol:"datetime"}).set_index("datetime"))
    for v in ["tick_volume","real_volume"]:
        if v in df.columns and "volume" not in df.columns: df=df.rename(columns={v:"volume"})
    ohlc=["open","high","low","close"]
    if any(c not in df.columns for c in ohlc): return None
    keep=ohlc+(["volume"] if "volume" in df.columns else [])
    return (df[keep].apply(pd.to_numeric,errors="coerce").dropna(subset=ohlc).sort_index()
            .pipe(lambda x:x[~x.index.duplicated(keep="last")]).pipe(lambda x:x[x.close>0]))

@st.cache_resource
def load_model():
    p=MODEL_DIR/"final_model.pkl"
    if not p.exists():
        return None
    model_data = joblib.load(p)
    # Asegurar que el modelo tenga las features esperadas
    if isinstance(model_data, dict) and "pipeline" in model_data and "feature_cols" in model_data:
        return model_data
    return {"pipeline": model_data, "feature_cols": None}

def get_signal(xau_df, dxy_df, pipe, feat_cols, tl, ts, atr_min, adx_min, dxy_p, atr_hi):
    c=xau_df.close
    atr14=_atr(xau_df,14); atr_rel=atr14/(c+1e-10)
    atr_pct=_pctrank(atr_rel,200)
    atr_high=float(atr_pct.iloc[-1])>(atr_hi/100)
    adx_val=_adx(xau_df,14)
    ef=_ema(c,13 if atr_high else 20); es=_ema(c,45 if atr_high else 50)
    bull=ef.iloc[-1]>es.iloc[-1]
    dxy_ret=0.0
    if dxy_df is not None:
        dc=dxy_df.close.reindex(xau_df.index,method="ffill")
        dxy_ret=float(np.log(dc.iloc[-1]/(dc.iloc[-1-dxy_p]+1e-10)))

    proba=0.5
    try:
        from src.data_processing import build_features
        # Calcular features con más datos para tener suficientes ventanas
        df_fe = build_features(xau_df.tail(600), dxy_df.tail(600) if dxy_df is not None else None)
        
        if feat_cols is not None:
            # Verificar qué features están disponibles
            available_feat = [f for f in feat_cols if f in df_fe.columns]
            missing_feat = set(feat_cols) - set(available_feat)
            
            if missing_feat:
                st.warning(f"⚠️ Features faltantes: {list(missing_feat)[:5]}...")
            
            if len(available_feat) > 0:
                # Crear DataFrame con todas las features esperadas, llenando faltantes con NaN
                X_live = pd.DataFrame(index=[0])
                for f in feat_cols:
                    if f in df_fe.columns:
                        X_live[f] = df_fe[f].iloc[-1]
                    else:
                        X_live[f] = np.nan
                
                # Asegurar el orden correcto de las columnas
                X_live = X_live[feat_cols]
                
                # Intentar predicción
                proba = float(pipe.predict_proba(X_live)[0, 1])
            else:
                st.warning("No hay features disponibles para predicción")
    except Exception as e:
        st.error(f"Error en predicción: {str(e)}")
        proba = 0.5

    raw="BUY" if proba>tl else ("SELL" if proba<ts else "NO_TRADE")
    f1=float(atr_pct.iloc[-1])>(atr_min/100)
    f2=(bull if raw=="BUY" else not bull) if raw!="NO_TRADE" else None
    f3=float(adx_val.iloc[-1])>adx_min
    f4=(dxy_ret<0 if raw=="BUY" else dxy_ret>0) if raw!="NO_TRADE" else None
    f5=raw!="NO_TRADE"
    ar=float(atr_rel.iloc[-1])/(float(atr_rel.rolling(50).mean().iloc[-1])+1e-10)
    de=abs(float(ef.iloc[-1])-float(es.iloc[-1]))/(float(atr14.iloc[-1])+1e-10)
    f6=(ar>1.0)and(de>0.5)

    final=raw
    if raw!="NO_TRADE":
        if not f1 or f2 is False or not f3 or f4 is False or not f6:
            final="NO_TRADE"

    return {"signal":final,"raw":raw,"proba":proba,
            "ef":float(ef.iloc[-1]),"es":float(es.iloc[-1]),
            "ema_name":"EMA13/45" if atr_high else "EMA20/50",
            "bull":bull,"atr_pct":float(atr_pct.iloc[-1])*100,
            "adx":float(adx_val.iloc[-1]),"dxy_ret":dxy_ret,
            "filters":{"F1 ATR":f1,"F2 EMA":f2,"F3 ADX":f3,
                       "F4 DXY":f4,"F5 Threshold":f5,"F6 Régimen":f6},
            "ef_ser":ef,"es_ser":es,"bull_ser":(ef>es)}

# ── Header ────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(90deg,#0D2137,#0D1117);padding:22px 26px;
border-radius:10px;border-left:4px solid #F59E0B;margin-bottom:18px'>
<h1 style='color:#F59E0B;margin:0;font-size:1.9em'>⚡ XAUUSD · Decision Support System</h1>
<p style='color:#94A3B8;margin:5px 0 0'>Print Money Factory · Edge-Based Trading System</p>
</div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    tf=st.selectbox("Timeframe",["D1","H4","H1"],index=1)
    st.markdown("---")
    st.markdown("**Filtros del sistema**")
    tl=st.slider("Umbral BUY",0.52,0.75,0.58,0.01)
    ts=round(1-tl,2)
    atr_min=st.slider("F1 ATR percentil mín",40,80,60,5)
    adx_min=st.slider("F3 ADX mínimo",10,35,20,5)
    dxy_p  =st.slider("F4 DXY periodos",3,10,5,1)
    atr_hi =st.slider("F2 ATR alto (EMA 13/45)",50,90,70,5)
    st.markdown("---")
    art=load_model()
    if art:
        m=art.get("metrics_oos",{})
        st.markdown("**📋 Modelo**")
        st.metric("Sharpe",  m.get("sharpe","—"))
        st.metric("WinRate", m.get("winrate","—"))
        st.metric("Payoff",  m.get("payoff", "—"))
    else:
        st.warning("Ejecuta notebook 03 para generar el modelo")

# ── Datos ─────────────────────────────────────────────────────────────
tf_map={"D1":("XAU_1d.csv","DXY_1d.csv"),"H4":("XAU_4h.csv","DXY_4h.csv"),"H1":("XAU_1h.csv","DXY_1h.csv")}
xf,df_=tf_map[tf]
xau=load_csv(DATA_DIR/xf); dxy=load_csv(DATA_DIR/df_)
if xau is None:
    st.error(f"No se encontró {xf} en data/raw/"); st.stop()

# ── Señal ─────────────────────────────────────────────────────────────
if art:
    pipe=art["pipeline"] if isinstance(art, dict) else art
    fc=art["feature_cols"] if isinstance(art, dict) and "feature_cols" in art else None
    
    # Si no hay feature_cols, intentar obtener del pipeline
    if fc is None and hasattr(pipe, 'feature_names_in_'):
        fc = pipe.feature_names_in_.tolist()
    elif fc is None:
        st.error("No se pudieron determinar las características del modelo")
        st.stop()
    
    with st.spinner("Analizando..."):
        res=get_signal(xau.tail(500),dxy.tail(500) if dxy else None,pipe,fc,tl,ts,atr_min,adx_min,dxy_p,atr_hi)
else:
    res={"signal":"NO_TRADE","raw":"NO_TRADE","proba":0.5,"ef":0,"es":0,
         "ema_name":"—","bull":False,"atr_pct":50,"adx":15,"dxy_ret":0,
         "filters":{k:False for k in ["F1 ATR","F2 EMA","F3 ADX","F4 DXY","F5 Threshold","F6 Régimen"]},
         "ef_ser":xau.close,"es_ser":xau.close,"bull_ser":pd.Series(False,index=xau.index)}

# ── Señal principal ───────────────────────────────────────────────────
sig=res["signal"]; proba=res["proba"]
c1,c2,c3,c4=st.columns(4)
with c1:
    if sig=="BUY":
        st.markdown("<div class='signal-buy'><div style='font-size:2em'>🟢</div><div style='font-size:1.6em;font-weight:bold;color:#10B981'>BUY</div></div>",unsafe_allow_html=True)
    elif sig=="SELL":
        st.markdown("<div class='signal-sell'><div style='font-size:2em'>🔴</div><div style='font-size:1.6em;font-weight:bold;color:#EF4444'>SELL</div></div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='signal-hold'><div style='font-size:2em'>⚪</div><div style='font-size:1.6em;font-weight:bold;color:#78716C'>NO TRADE</div></div>",unsafe_allow_html=True)
with c2: st.metric("P(BUY)",f"{proba:.1%}",f"{proba-0.5:+.1%} vs random")
with c3: st.metric(f"Tendencia ({res['ema_name']})","🟢 Alcista" if res["bull"] else "🔴 Bajista")
with c4: st.metric("DXY","🟢 Débil" if res["dxy_ret"]<0 else "🔴 Fuerte",f"{res['dxy_ret']:+.4f}")

# ── Filtros ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔽 Desglose de filtros")
fcols=st.columns(6)
fdesc={"F1 ATR":f"ATR={res['atr_pct']:.0f}%","F2 EMA":res["ema_name"],
       "F3 ADX":f"ADX={res['adx']:.1f}","F4 DXY":f"ret={res['dxy_ret']:+.3f}",
       "F5 Threshold":f"P={proba:.3f}","F6 Régimen":"tend." if res["filters"].get("F6 Régimen") else "lateral"}
for col,(fname,fval) in zip(fcols,res["filters"].items()):
    ok=fval
    icon="✅" if ok is True else ("❌" if ok is False else "⚪")
    color="#10B981" if ok is True else ("#EF4444" if ok is False else "#78716C")
    with col:
        st.markdown(f"""<div style='background:#131D2E;border:1px solid {color};border-radius:8px;
        padding:10px;text-align:center;height:100px'>
        <div style='font-size:1.4em'>{icon}</div>
        <div style='font-size:0.8em;font-weight:bold;color:{color}'>{fname}</div>
        <div style='font-size:0.72em;color:#94A3B8'>{fdesc.get(fname,"")}</div>
        </div>""",unsafe_allow_html=True)

# ── Gráfico ───────────────────────────────────────────────────────────
st.markdown("---")
n_bars=st.slider("Velas",50,500,200)
df_p=xau.tail(n_bars); c_p=df_p.close
ef_p=res["ef_ser"].reindex(df_p.index); es_p=res["es_ser"].reindex(df_p.index)
bull_p=res["bull_ser"].reindex(df_p.index).fillna(False)

plt.style.use("dark_background")
fig,axes=plt.subplots(2,1,figsize=(12,6),gridspec_kw={"height_ratios":[3,1]},sharex=True)
fig.patch.set_facecolor("#0D1117")
ax=axes[0]; ax.set_facecolor("#0D1117")
ax.fill_between(df_p.index,c_p.min(),c_p.max(),where=bull_p,alpha=0.07,color="#10B981")
ax.fill_between(df_p.index,c_p.min(),c_p.max(),where=~bull_p,alpha=0.07,color="#EF4444")
ax.plot(df_p.index,c_p.values,color="white",lw=0.7,label="XAUUSD")
ax.plot(df_p.index,ef_p.values,color="#F59E0B",lw=1.3,label=f"EMA rápida")
ax.plot(df_p.index,es_p.values,color="#0EA5E9",lw=1.3,label=f"EMA lenta")
ax.set_title(f"XAUUSD {tf} + EMA Adaptativa ({res['ema_name']})",color="white",fontsize=11)
ax.legend(fontsize=8); ax.set_ylabel("USD",color="white")
for sp in ax.spines.values(): sp.set_color("#1E3A5A")

ax2=axes[1]; ax2.set_facecolor("#0D1117")
if dxy is not None:
    dc=dxy.close.reindex(df_p.index,method="ffill")
    sp_=(np.log(c_p/c_p.shift(1))-np.log(dc/dc.shift(1))).dropna()
    ax2.fill_between(sp_.index,sp_,0,where=sp_>0,alpha=0.6,color="#10B981",label="XAU>DXY")
    ax2.fill_between(sp_.index,sp_,0,where=sp_<0,alpha=0.6,color="#EF4444",label="XAU<DXY")
    ax2.axhline(0,color="white",lw=0.5,ls="--")
    ax2.legend(fontsize=7)
else:
    ax2.text(0.5,0.5,"DXY no disponible",transform=ax2.transAxes,ha="center",color="gray")
ax2.set_title("Spread XAU − DXY",color="white",fontsize=9)
for sp in ax2.spines.values(): sp.set_color("#1E3A5A")
plt.tight_layout()
st.pyplot(fig,use_container_width=True)

# ── Historial ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🕐 Historial señales (últimas 20 velas)")
if art:
    try:
        from src.data_processing import build_features
        df_fe=build_features(xau.tail(600),dxy.tail(600) if dxy else None)
        
        if fc:
            # Verificar qué features están disponibles
            available_feat = [f for f in fc if f in df_fe.columns]
            if len(available_feat) > 0:
                # Crear DataFrame para todas las predicciones
                X_hist = pd.DataFrame(index=df_fe.index)
                for f in fc:
                    if f in df_fe.columns:
                        X_hist[f] = df_fe[f]
                    else:
                        X_hist[f] = np.nan
                
                X_hist = X_hist[fc].dropna(how='all')
                
                if len(X_hist) > 0:
                    pr = pipe.predict_proba(X_hist.values)[:,1]
                    
                    rows=[{"Fecha":dt.strftime("%Y-%m-%d %H:%M"),
                           "P(BUY)":f"{p:.3f}",
                           "Señal ML":"🟢 BUY" if p>tl else ("🔴 SELL" if p<ts else "⚪ HOLD")}
                          for dt,p in zip(X_hist.index[-20:],pr[-20:])]
                    st.dataframe(pd.DataFrame(rows).sort_values("Fecha",ascending=False).reset_index(drop=True),
                                 use_container_width=True,height=300)
                else:
                    st.info("No hay suficientes datos para el historial")
            else:
                st.info(f"No se encontraron features compatibles")
    except Exception as e:
        st.info(f"Historial no disponible: {e}")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#4B5563;font-size:0.82em'>⚠️ Solo apoyo a decisiones · <b style='color:#F59E0B'>Print Money Factory</b> · Alexsandro · Madrid 2025</div>",unsafe_allow_html=True)