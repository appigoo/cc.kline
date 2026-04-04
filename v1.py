import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz

st.set_page_config(page_title="K線 AI 交易系統", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Noto+Sans+HK:wght@300;400;700&display=swap');
:root {
    --bg:#0a0e1a; --surface:#111827; --card:#1a2235; --border:#1e3a5f;
    --accent:#00d4ff; --green:#00ff88; --red:#ff4466; --yellow:#ffd700;
    --orange:#ff9500; --purple:#bf7fff; --text:#c8d8e8; --muted:#5a7a9a;
}
html,body,[class*="css"]{font-family:'Noto Sans HK',sans-serif;background-color:var(--bg);color:var(--text);}
.stApp{background:var(--bg);}
h1,h2,h3{font-family:'Share Tech Mono',monospace;color:var(--accent);letter-spacing:2px;}
.main-header{background:linear-gradient(135deg,#0a0e1a,#0d1f3a,#0a0e1a);border:1px solid var(--border);
    border-radius:12px;padding:20px 30px;margin-bottom:20px;text-align:center;position:relative;overflow:hidden;}
.main-header::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,var(--accent),transparent);}
.main-header h1{font-size:2rem;margin:0;text-shadow:0 0 20px var(--accent);}
.main-header p{color:var(--muted);margin:5px 0 0;font-size:0.85rem;}
.metric-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:15px 20px;
    text-align:center;position:relative;overflow:hidden;}
.metric-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
    background:var(--accent);opacity:0.4;}
.metric-val{font-family:'Share Tech Mono',monospace;font-size:1.5rem;color:var(--accent);}
.metric-lbl{font-size:0.75rem;color:var(--muted);margin-top:4px;}
/* ── CONFLUENCE CARD ── */
.confluence-card{border-radius:12px;padding:18px 22px;margin:10px 0;border:2px solid;position:relative;overflow:hidden;}
.confluence-card::before{content:'⚡ 多時框共振';position:absolute;top:8px;right:14px;
    font-size:0.7rem;font-family:'Share Tech Mono',monospace;opacity:0.5;letter-spacing:1px;}
.conf-buy{background:rgba(0,255,136,0.06);border-color:var(--green);box-shadow:0 0 20px rgba(0,255,136,0.15);}
.conf-sell{background:rgba(255,68,102,0.06);border-color:var(--red);box-shadow:0 0 20px rgba(255,68,102,0.15);}
/* ── TF BADGES ── */
.tf-grid{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;}
.tf-badge{display:inline-flex;flex-direction:column;align-items:center;border-radius:8px;
    padding:6px 12px;min-width:60px;font-family:'Share Tech Mono',monospace;font-size:0.75rem;}
.tf-badge-buy{background:rgba(0,255,136,0.15);border:1px solid var(--green);color:var(--green);}
.tf-badge-sell{background:rgba(255,68,102,0.15);border:1px solid var(--red);color:var(--red);}
.tf-badge-neutral{background:rgba(90,122,154,0.2);border:1px solid var(--muted);color:var(--muted);}
.tf-badge span{font-size:0.62rem;opacity:0.7;margin-top:2px;}
/* ── SINGLE SIGNAL ── */
.signal-card{border-radius:10px;padding:14px 18px;margin:8px 0;border-left:4px solid;font-size:0.88rem;}
.signal-buy{background:rgba(0,255,136,0.08);border-color:var(--green);}
.signal-sell{background:rgba(255,68,102,0.08);border-color:var(--red);}
.signal-neutral{background:rgba(255,215,0,0.08);border-color:var(--yellow);}
/* ── MTF CONFIG BOX ── */
.mtf-box{background:linear-gradient(135deg,#0d1a2e,#101e38);border:1px solid #2a4a6f;
    border-radius:10px;padding:12px 16px;margin:6px 0;}
.mtf-box-title{font-family:'Share Tech Mono',monospace;color:var(--orange);font-size:0.82rem;
    letter-spacing:1px;margin-bottom:6px;}
/* ── PATTERN TAGS ── */
.pattern-tag{display:inline-block;background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.3);
    border-radius:5px;padding:2px 8px;font-size:0.75rem;color:var(--accent);margin:2px;
    font-family:'Share Tech Mono',monospace;}
/* ── STATUS ── */
.status-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;}
.dot-live{background:var(--green);box-shadow:0 0 8px var(--green);animation:pulse 2s infinite;}
.dot-conf{background:var(--orange);box-shadow:0 0 8px var(--orange);animation:pulse 1.5s infinite;}
.dot-off{background:var(--muted);}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.3;}}
.stButton>button{background:linear-gradient(135deg,#0d2040,#1a3a5f)!important;
    color:var(--accent)!important;border:1px solid var(--border)!important;
    border-radius:8px!important;font-family:'Share Tech Mono',monospace!important;letter-spacing:1px;}
.stButton>button:hover{border-color:var(--accent)!important;box-shadow:0 0 12px rgba(0,212,255,0.3)!important;}
div[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border);}
div[data-testid="stSidebar"] label{color:var(--text)!important;}
.log-box{background:#060a12;border:1px solid var(--border);border-radius:8px;padding:12px;
    font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:#5a9a7a;
    max-height:220px;overflow-y:auto;line-height:1.6;}
hr{border-color:var(--border);}
.alert-box{background:rgba(255,215,0,0.1);border:1px solid var(--yellow);border-radius:8px;
    padding:10px 15px;font-size:0.83rem;color:var(--yellow);margin:8px 0;}
.conf-alert{background:rgba(255,149,0,0.1);border:1px solid var(--orange);border-radius:8px;
    padding:10px 15px;font-size:0.83rem;color:var(--orange);margin:8px 0;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CANDLESTICK PATTERN ENGINE
# ─────────────────────────────────────────────
class CandlestickPatterns:
    def __init__(self, df):
        self.o = df['Open'].values
        self.h = df['High'].values
        self.l = df['Low'].values
        self.c = df['Close'].values
        self.n = len(df)

    def _body(self, i): return abs(self.c[i] - self.o[i])
    def _upper(self, i): return self.h[i] - max(self.o[i], self.c[i])
    def _lower(self, i): return min(self.o[i], self.c[i]) - self.l[i]
    def _bull(self, i): return self.c[i] > self.o[i]
    def _bear(self, i): return self.c[i] < self.o[i]

    def doji(self, i):
        b = self._body(i); r = self.h[i] - self.l[i]
        return r > 0 and b/r < 0.1

    def hammer(self, i):
        b = self._body(i)
        return b > 0 and self._lower(i) >= 2*b and self._upper(i) <= 0.3*b

    def inverted_hammer(self, i):
        b = self._body(i)
        return b > 0 and self._upper(i) >= 2*b and self._lower(i) <= 0.3*b

    def shooting_star(self, i):
        if i < 1 or not self._bear(i): return False
        b = self._body(i)
        return b > 0 and self._bull(i-1) and self._upper(i) >= 2*b and self._lower(i) <= 0.3*b

    def hanging_man(self, i):
        if i < 1: return False
        b = self._body(i)
        return b > 0 and self._bull(i-1) and self._lower(i) >= 2*b and self._upper(i) <= 0.3*b

    def bullish_engulfing(self, i):
        if i < 1: return False
        return self._bear(i-1) and self._bull(i) and self.o[i] < self.c[i-1] and self.c[i] > self.o[i-1]

    def bearish_engulfing(self, i):
        if i < 1: return False
        return self._bull(i-1) and self._bear(i) and self.o[i] > self.c[i-1] and self.c[i] < self.o[i-1]

    def morning_star(self, i):
        if i < 2: return False
        b2 = self._body(i-2)
        return (self._bear(i-2) and max(self.o[i-1],self.c[i-1]) < self.c[i-2] and
                b2 > 0 and self._body(i-1) < 0.3*b2 and self._bull(i) and
                self.c[i] > (self.o[i-2]+self.c[i-2])/2)

    def evening_star(self, i):
        if i < 2: return False
        b2 = self._body(i-2)
        return (self._bull(i-2) and min(self.o[i-1],self.c[i-1]) > self.c[i-2] and
                b2 > 0 and self._body(i-1) < 0.3*b2 and self._bear(i) and
                self.c[i] < (self.o[i-2]+self.c[i-2])/2)

    def three_white_soldiers(self, i):
        if i < 2: return False
        for j in [i-2,i-1,i]:
            if not self._bull(j) or self._upper(j) > 0.3*self._body(j): return False
        return self.o[i-1]>self.o[i-2] and self.o[i]>self.o[i-1] and self.c[i]>self.c[i-1]>self.c[i-2]

    def three_black_crows(self, i):
        if i < 2: return False
        for j in [i-2,i-1,i]:
            if not self._bear(j) or self._lower(j) > 0.3*self._body(j): return False
        return self.o[i-1]<self.o[i-2] and self.o[i]<self.o[i-1] and self.c[i]<self.c[i-1]<self.c[i-2]

    def piercing_line(self, i):
        if i < 1: return False
        mid = (self.o[i-1]+self.c[i-1])/2
        return self._bear(i-1) and self._bull(i) and self.o[i]<self.l[i-1] and self.c[i]>mid

    def dark_cloud_cover(self, i):
        if i < 1: return False
        mid = (self.o[i-1]+self.c[i-1])/2
        return self._bull(i-1) and self._bear(i) and self.o[i]>self.h[i-1] and self.c[i]<mid

    def marubozu_bull(self, i):
        b = self._body(i); r = self.h[i]-self.l[i]
        return r > 0 and self._bull(i) and b/r > 0.92

    def marubozu_bear(self, i):
        b = self._body(i); r = self.h[i]-self.l[i]
        return r > 0 and self._bear(i) and b/r > 0.92

    def tweezer_bottom(self, i):
        if i < 1: return False
        return self._bear(i-1) and self._bull(i) and abs(self.l[i]-self.l[i-1])/max(self.l[i],0.01) < 0.002

    def tweezer_top(self, i):
        if i < 1: return False
        return self._bull(i-1) and self._bear(i) and abs(self.h[i]-self.h[i-1])/max(self.h[i],0.01) < 0.002

    def scan_latest(self):
        i = self.n - 1
        checks = [
            (self.doji(i),               "十字星 Doji",           "NEUTRAL", 50),
            (self.hammer(i),              "錘子線 Hammer",         "BUY",     75),
            (self.inverted_hammer(i),     "倒錘子 Inv.Hammer",     "BUY",     60),
            (self.shooting_star(i),       "流星線 Shooting Star",  "SELL",    75),
            (self.hanging_man(i),         "上吊線 Hanging Man",    "SELL",    65),
            (self.bullish_engulfing(i),   "看漲吞噬 Bull Engulf",  "BUY",     80),
            (self.bearish_engulfing(i),   "看跌吞噬 Bear Engulf",  "SELL",    80),
            (self.morning_star(i),        "晨星 Morning Star",     "BUY",     85),
            (self.evening_star(i),        "黃昏星 Evening Star",   "SELL",    85),
            (self.three_white_soldiers(i),"三白兵 3 Soldiers",     "BUY",     88),
            (self.three_black_crows(i),   "三黑鴉 3 Crows",        "SELL",    88),
            (self.piercing_line(i),       "穿刺線 Piercing Line",  "BUY",     72),
            (self.dark_cloud_cover(i),    "烏雲蓋頂 Dark Cloud",   "SELL",    72),
            (self.marubozu_bull(i),       "陽光棍 Bull Marubozu",  "BUY",     70),
            (self.marubozu_bear(i),       "陰光棍 Bear Marubozu",  "SELL",    70),
            (self.tweezer_bottom(i),      "鑷底 Tweezer Bottom",   "BUY",     65),
            (self.tweezer_top(i),         "鑷頂 Tweezer Top",      "SELL",    65),
        ]
        return [{"pattern":n,"signal":s,"strength":st} for det,n,s,st in checks if det]


# ─────────────────────────────────────────────
# INDICATORS
# ─────────────────────────────────────────────
def compute_indicators(df):
    c = df['Close']
    df['EMA9']  = c.ewm(span=9,  adjust=False).mean()
    df['EMA21'] = c.ewm(span=21, adjust=False).mean()
    df['EMA50'] = c.ewm(span=50, adjust=False).mean()
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['RSI'] = 100 - (100/(1+gain/loss.replace(0,np.nan)))
    e12 = c.ewm(span=12,adjust=False).mean()
    e26 = c.ewm(span=26,adjust=False).mean()
    df['MACD']        = e12-e26
    df['MACD_signal'] = df['MACD'].ewm(span=9,adjust=False).mean()
    df['MACD_hist']   = df['MACD']-df['MACD_signal']
    df['BB_mid']   = c.rolling(20).mean()
    std = c.rolling(20).std()
    df['BB_upper'] = df['BB_mid']+2*std
    df['BB_lower'] = df['BB_mid']-2*std
    hl = df['High']-df['Low']
    hc = (df['High']-df['Close'].shift()).abs()
    lc = (df['Low'] -df['Close'].shift()).abs()
    df['ATR'] = pd.concat([hl,hc,lc],axis=1).max(axis=1).rolling(14).mean()
    df['Vol_MA20']  = df['Volume'].rolling(20).mean()
    df['Vol_ratio'] = df['Volume']/df['Vol_MA20'].replace(0,np.nan)
    return df

def trend_bias(df):
    l = df.iloc[-1]; score = 0
    if l['EMA9']  > l['EMA21']: score += 1
    if l['EMA21'] > l['EMA50']: score += 1
    if l['MACD_hist'] > 0:      score += 1
    if l['RSI'] > 55:           score += 1
    if l['RSI'] < 45:           score -= 1
    if l['Close'] > l['BB_mid']:   score += 1
    if l['Close'] < l['BB_lower']: score += 2
    if l['Close'] > l['BB_upper']: score -= 2
    if score >= 3:  return "BUY",  score
    if score <= -1: return "SELL", score
    return "NEUTRAL", score


# ─────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────
TF_MAP = {"1m":("1m","1d"),"5m":("5m","5d"),"15m":("15m","60d"),
          "30m":("30m","60d"),"1h":("1h","730d"),"1d":("1d","5y"),"1w":("1wk","10y")}
ALL_TF = ["1m","5m","15m","30m","1h","1d","1w"]

@st.cache_data(ttl=60)
def fetch_data(ticker, tf):
    interval, period = TF_MAP[tf]
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    if df.empty: return None
    df.columns = [c[0] if isinstance(c,tuple) else c for c in df.columns]
    return compute_indicators(df.dropna())


# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────
def send_telegram(token, chat_id, msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id":chat_id,"text":msg,"parse_mode":"HTML"}, timeout=8)
        return r.status_code==200, r.text
    except Exception as e:
        return False, str(e)

def build_single_msg(ticker, tf, patterns, trend, price, atr, rsi):
    london = pytz.timezone("Europe/London")
    now = datetime.now(london).strftime("%Y-%m-%d %H:%M %Z")
    if not patterns and trend=="NEUTRAL": return None
    sig = trend
    if patterns:
        bn = sum(1 for p in patterns if p['signal']=='BUY')
        sn = sum(1 for p in patterns if p['signal']=='SELL')
        sig = "BUY" if bn>sn else "SELL" if sn>bn else "NEUTRAL"
    if sig=="NEUTRAL": return None
    e  = "🟢📈" if sig=="BUY" else "🔴📉"
    ac = "做多 (LONG)" if sig=="BUY" else "做空 (SHORT)"
    sl = round(price-1.5*atr,2) if sig=="BUY" else round(price+1.5*atr,2)
    tp = round(price+2.5*atr,2) if sig=="BUY" else round(price-2.5*atr,2)
    pl = "\n".join([f"  • {p['pattern']} ({p['strength']}%)" for p in patterns]) or "  • 技術指標信號"
    return (f"{e} <b>K線信號</b>\n━━━━━━━━━━━━━━━━\n"
            f"📌 {ticker} [{tf}]\n🕐 {now}\n💰 ${price:.2f}  📊 RSI:{rsi:.1f}\n"
            f"━━━━━━━━━━━━━━━━\n🕯 形態:\n{pl}\n━━━━━━━━━━━━━━━━\n"
            f"⚡ {ac}\n🛑 SL ${sl}  🎯 TP ${tp}\n📐 風報 1:2.5\n⚠️ 僅供參考")

def build_confluence_msg(ticker, sig, tf_details, price, atr, rsi):
    london = pytz.timezone("Europe/London")
    now = datetime.now(london).strftime("%Y-%m-%d %H:%M %Z")
    e   = "🚀🟢🟢🟢" if sig=="BUY" else "💥🔴🔴🔴"
    ac  = "做多 (LONG)" if sig=="BUY" else "做空 (SHORT)"
    sl  = round(price-1.5*atr,2) if sig=="BUY" else round(price+1.5*atr,2)
    tp  = round(price+2.5*atr,2) if sig=="BUY" else round(price-2.5*atr,2)
    tfs = "+".join([d['tf'] for d in tf_details])
    lines = ""
    for d in tf_details:
        em = "🟢" if d['signal']=="BUY" else "🔴"
        ps = " | ".join([p['pattern'] for p in d['patterns']]) if d['patterns'] else d['trend']
        lines += f"  {em} [{d['tf']}] {ps}\n"
    return (f"{e} <b>⚡ 多時框共振信號 ⚡</b>\n━━━━━━━━━━━━━━━━\n"
            f"📌 {ticker}\n🕐 {now}\n💰 ${price:.2f}  📊 RSI:{rsi:.1f}\n"
            f"🔗 共振週期: {tfs}\n━━━━━━━━━━━━━━━━\n🕯 各週期:\n{lines}"
            f"━━━━━━━━━━━━━━━━\n⚡ {ac}\n"
            f"🛑 SL ${sl}  🎯 TP ${tp}\n📐 風報 1:2.5\n"
            f"⭐ 強度: 極強（{len(tf_details)}週期共振）\n⚠️ 僅供參考")


# ─────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────
def build_chart(df, ticker, tf):
    dp = df.tail(120)
    fig = make_subplots(rows=3,cols=1,shared_xaxes=True,
                        row_heights=[0.6,0.2,0.2],vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=dp.index,open=dp['Open'],high=dp['High'],
        low=dp['Low'],close=dp['Close'],increasing_line_color='#00ff88',
        decreasing_line_color='#ff4466',name="K線"),row=1,col=1)
    for ema,col,w in [('EMA9','#00d4ff',1),('EMA21','#ffd700',1),('EMA50','#ff7f50',1.5)]:
        fig.add_trace(go.Scatter(x=dp.index,y=dp[ema],line=dict(color=col,width=w),name=ema),row=1,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['BB_upper'],
        line=dict(color='rgba(150,150,255,0.4)',width=1,dash='dot'),showlegend=False),row=1,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['BB_lower'],fill='tonexty',
        fillcolor='rgba(100,100,255,0.06)',line=dict(color='rgba(150,150,255,0.4)',width=1,dash='dot'),
        showlegend=False),row=1,col=1)
    colors=['#00ff88' if v>=0 else '#ff4466' for v in dp['MACD_hist']]
    fig.add_trace(go.Bar(x=dp.index,y=dp['MACD_hist'],marker_color=colors,showlegend=False),row=2,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['MACD'],line=dict(color='#00d4ff',width=1),name='MACD'),row=2,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['MACD_signal'],line=dict(color='#ffd700',width=1),name='Signal'),row=2,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['RSI'],line=dict(color='#bf7fff',width=1.5),name='RSI'),row=3,col=1)
    fig.add_hline(y=70,line_dash="dash",line_color="#ff4466",line_width=0.8,row=3,col=1)
    fig.add_hline(y=30,line_dash="dash",line_color="#00ff88",line_width=0.8,row=3,col=1)
    fig.update_layout(paper_bgcolor='#0a0e1a',plot_bgcolor='#0a0e1a',
        font=dict(color='#c8d8e8',size=11),xaxis_rangeslider_visible=False,
        title=dict(text=f"<b>{ticker}</b> [{tf}]",font=dict(color='#00d4ff',size=14),x=0.5),
        legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(size=10)),
        margin=dict(l=10,r=10,t=40,b=10),height=620)
    for ax in ['xaxis','xaxis2','xaxis3','yaxis','yaxis2','yaxis3']:
        fig.update_layout(**{ax:dict(gridcolor='#1e3a5f',showgrid=True)})
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:10px 0;
        font-family:Share Tech Mono,monospace;color:#00d4ff;font-size:1.1rem;letter-spacing:2px;'>
        ⚙ 系統設定</div>""", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📌 股票代號**")
    tickers_input = st.text_input("多個股票用逗號分隔", value="TSLA,NVDA,AAPL,SPY")
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    st.markdown("**⏱ 一般監控時框**")
    timeframes = st.multiselect("單時框信號監控", ALL_TF, default=["5m","15m","1h"])

    st.markdown("---")

    # ══════════════════════════════════════════
    # ⚡ 多時框共振設定
    # ══════════════════════════════════════════
    st.markdown("""<div style='font-family:Share Tech Mono,monospace;color:#ff9500;
        font-size:0.92rem;letter-spacing:1px;padding:4px 0 2px;'>
        ⚡ 多時框共振設定</div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size:0.76rem;color:#5a7a9a;margin-bottom:8px;'>
        設定共振組合：全部週期同向才觸發信號</div>""", unsafe_allow_html=True)

    mtf_enabled = st.toggle("啟用多時框共振監控", value=True)
    mtf_groups  = []

    if mtf_enabled:
        # ── Group 1 ──
        st.markdown("<div class='mtf-box'><div class='mtf-box-title'>📦 共振組 1</div></div>",
                    unsafe_allow_html=True)
        g1_on  = st.toggle("啟用", value=True, key="g1_on")
        g1_tfs = st.multiselect("週期（2-3個）", ALL_TF, default=["1m","5m","15m"],
                                 key="g1_tf", max_selections=3)

        # ── Group 2 ──
        st.markdown("<div class='mtf-box'><div class='mtf-box-title'>📦 共振組 2</div></div>",
                    unsafe_allow_html=True)
        g2_on  = st.toggle("啟用", value=False, key="g2_on")
        g2_tfs = st.multiselect("週期（2-3個）", ALL_TF, default=["5m","15m","1h"],
                                 key="g2_tf", max_selections=3)

        # ── Group 3 ──
        st.markdown("<div class='mtf-box'><div class='mtf-box-title'>📦 共振組 3</div></div>",
                    unsafe_allow_html=True)
        g3_on  = st.toggle("啟用", value=False, key="g3_on")
        g3_tfs = st.multiselect("週期（2-3個）", ALL_TF, default=["15m","1h","1d"],
                                 key="g3_tf", max_selections=3)

        if g1_on and len(g1_tfs) >= 2: mtf_groups.append({"label":"組1","tfs":g1_tfs})
        if g2_on and len(g2_tfs) >= 2: mtf_groups.append({"label":"組2","tfs":g2_tfs})
        if g3_on and len(g3_tfs) >= 2: mtf_groups.append({"label":"組3","tfs":g3_tfs})

        st.markdown(f"""<div style='font-size:0.78rem;color:#ff9500;padding:4px 0;'>
            ✅ 已啟用 {len(mtf_groups)} 個共振組</div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**📡 Telegram 設定**")
    tg_token   = st.text_input("Bot Token", type="password", placeholder="123456:ABC-...")
    tg_chat    = st.text_input("Chat ID",   placeholder="-1001234567890")
    tg_enabled = st.toggle("啟用 Telegram 推送", value=False)
    tg_single  = st.toggle("推送單時框信號", value=True)
    tg_conf    = st.toggle("推送共振信號（優先）", value=True)

    if st.button("🧪 測試 Telegram"):
        if tg_token and tg_chat:
            ok, resp = send_telegram(tg_token, tg_chat,
                "✅ K線 AI 系統連線測試成功！\n⚡ 多時框共振功能已就緒。")
            st.success("✅ 成功") if ok else st.error(f"❌ {resp}")
        else:
            st.warning("請填寫 Token 和 Chat ID")

    st.markdown("---")
    st.markdown("**⏰ 自動掃描**")
    auto_scan     = st.toggle("啟用自動掃描", value=False)
    scan_interval = st.slider("掃描間隔（秒）", 30, 300, 60, 10)

    st.markdown("---")
    st.markdown("**🎯 信號過濾**")
    min_strength          = st.slider("最低形態信心度 (%)", 50, 90, 65, 5)
    require_trend_confirm = st.toggle("需要趨勢確認", value=True)

    st.markdown("---")
    st.markdown("""<div style='font-size:0.72rem;color:#3a5a7a;text-align:center;line-height:1.8;'>
        📊 K線 AI 自動交易系統<br>16種K線形態 + 多時框共振<br>
        <span style='color:#1e5a4a;'>⚠ 僅供參考，後果自負</span></div>""",
        unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""<div class='main-header'>
    <h1>📊 K線 AI 自動交易系統</h1>
    <p>16種核心K線形態 ｜ 三週期共振過濾 ｜ Telegram 信號推送 ｜ 實盤就緒</p>
</div>""", unsafe_allow_html=True)

with st.expander("📖 16種核心K線形態一覧", expanded=False):
    ref = [["十字星 Doji","中性","50%","方向猶豫"],["錘子線 Hammer","看漲","75%","下跌末端反轉"],
           ["倒錘子 Inv.Hammer","看漲","60%","長上影需確認"],["流星線 Shooting Star","看跌","75%","上漲末端反轉"],
           ["上吊線 Hanging Man","看跌","65%","上漲末端警告"],["看漲吞噬 Bull Engulf","看漲","80%","大陽吞噬前陰"],
           ["看跌吞噬 Bear Engulf","看跌","80%","大陰吞噬前陽"],["晨星 Morning Star","看漲","85%","底部三K反轉"],
           ["黃昏星 Evening Star","看跌","85%","頂部三K反轉"],["三白兵 3 Soldiers","看漲","88%","三根大陽強勢"],
           ["三黑鴉 3 Crows","看跌","88%","三根大陰強勢"],["穿刺線 Piercing","看漲","72%","穿越前日中點"],
           ["烏雲蓋頂 Dark Cloud","看跌","72%","跌破前日中點"],["陽光棍 Bull Marubozu","看漲","70%","無影大陽"],
           ["陰光棍 Bear Marubozu","看跌","70%","無影大陰"],["鑷底 Tweezer Bottom","看漲","65%","同低支撐"],
           ["鑷頂 Tweezer Top","看跌","65%","同高阻力"]]
    st.dataframe(pd.DataFrame(ref, columns=["形態","信號","信心度","說明"]),
                 use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("scan_log",[]),("last_scan",None),
              ("single_results",[]),("confluence_results",[])]:
    if k not in st.session_state: st.session_state[k] = v


# ─────────────────────────────────────────────
# ANALYSE ONE TF
# ─────────────────────────────────────────────
def analyse_tf(ticker, tf):
    df = fetch_data(ticker, tf)
    if df is None or len(df) < 30: return None
    last  = df.iloc[-1]
    price = float(last['Close'])
    rsi   = float(last['RSI'])  if not np.isnan(last['RSI'])  else 50.0
    atr   = float(last['ATR'])  if not np.isnan(last['ATR'])  else price*0.01
    cp    = CandlestickPatterns(df)
    pats  = [p for p in cp.scan_latest() if p['strength'] >= min_strength]
    trend, _ = trend_bias(df)
    if require_trend_confirm and pats:
        if trend=='BUY':   pats=[p for p in pats if p['signal']=='BUY']
        elif trend=='SELL': pats=[p for p in pats if p['signal']=='SELL']
    if pats:
        bn = sum(1 for p in pats if p['signal']=='BUY')
        sn = sum(1 for p in pats if p['signal']=='SELL')
        sig = 'BUY' if bn>sn else 'SELL' if sn>bn else 'NEUTRAL'
        st_avg = float(np.mean([p['strength'] for p in pats]))
    else:
        sig    = trend if trend!='NEUTRAL' else 'NEUTRAL'
        st_avg = 0.0
    return {"ticker":ticker,"tf":tf,"price":price,"rsi":rsi,"atr":atr,
            "patterns":pats,"trend":trend,"signal":sig,"strength":st_avg}


# ─────────────────────────────────────────────
# CHECK CONFLUENCE
# ─────────────────────────────────────────────
def check_confluence(by_tf, group_tfs):
    """Returns (signal, tf_details) or (None, []) if no confluence."""
    details = []; signals = []
    for tf in group_tfs:
        r = by_tf.get(tf)
        if r is None or r['signal']=='NEUTRAL': return None, []
        signals.append(r['signal'])
        details.append({"tf":tf,"signal":r['signal'],
                         "patterns":r['patterns'],"trend":r['trend']})
    if len(set(signals))==1: return signals[0], details
    return None, []


# ─────────────────────────────────────────────
# MAIN SCAN
# ─────────────────────────────────────────────
def do_scan():
    london  = pytz.timezone("Europe/London")
    now_str = datetime.now(london).strftime("%H:%M:%S")
    log = []

    all_needed = set(timeframes)
    for g in mtf_groups: all_needed |= set(g['tfs'])

    single_out = []; conf_out = []

    for ticker in tickers:
        by_tf = {}
        for tf in all_needed:
            r = analyse_tf(ticker, tf)
            if r: by_tf[tf] = r

        # ── Single TF ──
        for tf in timeframes:
            r = by_tf.get(tf)
            if r is None:
                log.append(f"[{now_str}] ⚠ {ticker}/{tf} 數據不足"); continue
            single_out.append(r)
            if r['signal']!='NEUTRAL' or r['patterns']:
                em = "🟢" if r['signal']=='BUY' else "🔴" if r['signal']=='SELL' else "🟡"
                log.append(f"[{now_str}] {em} {ticker}/{tf} ${r['price']:.2f} → {r['signal']}")
                if tg_enabled and tg_single and tg_token and tg_chat and r['signal']!='NEUTRAL':
                    msg = build_single_msg(ticker, tf, r['patterns'], r['trend'],
                                           r['price'], r['atr'], r['rsi'])
                    if msg:
                        ok,_ = send_telegram(tg_token, tg_chat, msg)
                        log.append(f"[{now_str}]   📡 單時框 {'✅' if ok else '❌'}")

        # ── Multi-TF Confluence ──
        for group in mtf_groups:
            sig, details = check_confluence(by_tf, group['tfs'])
            if sig:
                ref = by_tf.get(group['tfs'][-1]) or list(by_tf.values())[0]
                entry = {"ticker":ticker,"signal":sig,"group_label":group['label'],
                         "group_tfs":group['tfs'],"tf_details":details,
                         "price":ref['price'],"rsi":ref['rsi'],"atr":ref['atr'],"ts":now_str}
                conf_out.append(entry)
                tfs_str = "+".join(group['tfs'])
                em = "🚀" if sig=="BUY" else "💥"
                log.append(f"[{now_str}] {em}⚡ 共振! {ticker} [{tfs_str}] → {sig}")
                if tg_enabled and tg_conf and tg_token and tg_chat:
                    msg = build_confluence_msg(ticker, sig, details,
                                               ref['price'], ref['atr'], ref['rsi'])
                    ok,_ = send_telegram(tg_token, tg_chat, msg)
                    log.append(f"[{now_str}]   📡 共振TG {'✅' if ok else '❌'}")

    st.session_state.single_results     = single_out
    st.session_state.confluence_results = conf_out
    st.session_state.last_scan          = datetime.now(london)
    for l in log: st.session_state.scan_log.insert(0, l)
    st.session_state.scan_log = st.session_state.scan_log[:150]
    return single_out, conf_out


# ─────────────────────────────────────────────
# BUTTONS
# ─────────────────────────────────────────────
cb1, cb2, _ = st.columns([1,1,3])
with cb1:
    scan_now = st.button("🔍 立即掃描", use_container_width=True)
with cb2:
    if st.button("🔄 清除快取", use_container_width=True):
        st.cache_data.clear(); st.rerun()

if scan_now:
    with st.spinner("⚡ 掃描中（含多時框共振分析）..."):
        single_results, confluence_results = do_scan()
else:
    single_results     = st.session_state.single_results
    confluence_results = st.session_state.confluence_results


# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
last_str  = st.session_state.last_scan.strftime("%H:%M %Z") if st.session_state.last_scan else "—"
buy_n     = sum(1 for r in single_results     if r['signal']=='BUY')
sell_n    = sum(1 for r in single_results     if r['signal']=='SELL')
conf_buy  = sum(1 for r in confluence_results if r['signal']=='BUY')
conf_sell = sum(1 for r in confluence_results if r['signal']=='SELL')

cols = st.columns(6)
cards = [
    (str(len(tickers)),    "監控股票",     "var(--accent)"),
    (str(buy_n),           "看漲信號 🟢",  "var(--green)"),
    (str(sell_n),          "看跌信號 🔴",  "var(--red)"),
    (str(conf_buy),        "共振做多 🚀",  "var(--orange)"),
    (str(conf_sell),       "共振做空 💥",  "#ff6080"),
    (last_str,             "最後掃描",     "var(--accent)"),
]
for col, (val, lbl, color) in zip(cols, cards):
    with col:
        fs = "1.1rem" if len(val)>5 else "1.5rem"
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-val' style='color:{color};font-size:{fs};'>{val}</div>
            <div class='metric-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_conf, tab_single, tab_chart, tab_log = st.tabs(
    ["⚡ 多時框共振", "📈 單時框信號", "🕯️ K線圖", "📋 掃描日誌"])


# ══════════════════════════════════════════════
# TAB 1 — 多時框共振（主功能）
# ══════════════════════════════════════════════
with tab_conf:

    # ── Config Summary ──
    if mtf_enabled and mtf_groups:
        st.markdown("#### 🔗 當前共振組設定")
        gcols = st.columns(max(len(mtf_groups), 1))
        for idx, g in enumerate(mtf_groups):
            with gcols[idx]:
                badges = "".join([f"<span class='pattern-tag'>{tf}</span>" for tf in g['tfs']])
                st.markdown(f"""
                <div style='background:#0d1f38;border:1px solid #2a4a6f;border-radius:10px;
                            padding:14px;text-align:center;'>
                    <div style='font-family:Share Tech Mono,monospace;color:#ff9500;
                                font-size:0.82rem;margin-bottom:8px;'>⚡ {g["label"]}</div>
                    <div>{badges}</div>
                    <div style='font-size:0.72rem;color:#5a7a9a;margin-top:8px;'>
                        全部 {len(g["tfs"])} 個週期需同向</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🚨 共振信號結果")

        if not confluence_results:
            st.markdown("""<div class='conf-alert'>
                目前無共振信號。請點擊「立即掃描」，或等待自動掃描。<br>
                <small style='opacity:0.7;'>共振條件：共振組內所有週期必須同時出現相同方向（BUY 或 SELL）信號</small>
            </div>""", unsafe_allow_html=True)
        else:
            for r in confluence_results:
                cls = "conf-buy" if r['signal']=='BUY' else "conf-sell"
                sig_lbl = "🚀 做多共振 (LONG)" if r['signal']=='BUY' else "💥 做空共振 (SHORT)"
                sl = round(r['price']-1.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']+1.5*r['atr'],2)
                tp = round(r['price']+2.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']-2.5*r['atr'],2)

                tf_badges_html = ""
                for d in r['tf_details']:
                    bc = "tf-badge-buy" if d['signal']=='BUY' else "tf-badge-sell"
                    pn = d['patterns'][0]['pattern'][:12] if d['patterns'] else d['trend']
                    tf_badges_html += f"<div class='tf-badge {bc}'>{d['tf']}<span>{pn}</span></div>"

                st.markdown(f"""
                <div class='confluence-card {cls}'>
                    <div style='display:flex;justify-content:space-between;
                                align-items:center;margin-bottom:10px;'>
                        <span style='font-size:1.25rem;font-weight:700;
                                     font-family:Share Tech Mono,monospace;'>{r['ticker']}</span>
                        <span style='font-size:1rem;font-weight:700;'>{sig_lbl}</span>
                    </div>
                    <div style='font-size:0.75rem;color:#5a7a9a;margin-bottom:8px;'>
                        共振組: {r['group_label']} &nbsp;｜&nbsp;
                        週期: {" + ".join(r['group_tfs'])} &nbsp;｜&nbsp;
                        時間: {r['ts']}
                    </div>
                    <div class='tf-grid'>{tf_badges_html}</div>
                    <div style='display:flex;gap:16px;font-size:0.82rem;color:#8aabb0;
                                margin-top:10px;padding-top:10px;
                                border-top:1px solid rgba(255,255,255,0.06);flex-wrap:wrap;'>
                        <span>💰 現價: <b style='color:#c8d8e8'>${r['price']:.2f}</b></span>
                        <span>📊 RSI: <b style='color:#c8d8e8'>{r['rsi']:.1f}</b></span>
                        <span>🛑 SL: <b style='color:#ff8888'>${sl}</b></span>
                        <span>🎯 TP: <b style='color:#88ffcc'>${tp}</b></span>
                        <span>📐 風報: <b style='color:#c8d8e8'>1:2.5</b></span>
                        <span>⭐ 強度: <b style='color:#ff9500'>極強</b></span>
                    </div>
                </div>""", unsafe_allow_html=True)

    elif not mtf_enabled:
        st.markdown("""<div class='alert-box'>
            請在左側側欄啟用「多時框共振監控」。</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='alert-box'>
            請至少設定一個共振組（每組需選 2-3 個週期）。</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2 — 單時框信號
# ══════════════════════════════════════════════
with tab_single:
    if not single_results:
        st.markdown("""<div class='alert-box'>⚡ 點擊「立即掃描」開始分析。</div>""",
                    unsafe_allow_html=True)
    else:
        for r in sorted(single_results,
                        key=lambda x:(0 if x['signal'] in ['BUY','SELL'] else 1, -x['strength'])):
            if r['signal']=='NEUTRAL' and not r['patterns']: continue
            cls = ('signal-buy' if r['signal']=='BUY' else
                   'signal-sell' if r['signal']=='SELL' else 'signal-neutral')
            se  = ("🟢 看漲" if r['signal']=='BUY' else
                   "🔴 看跌" if r['signal']=='SELL' else "🟡 中性")
            tags = "".join([f"<span class='pattern-tag'>{p['pattern']} {p['strength']}%</span>"
                             for p in r['patterns']]) or \
                   "<span style='color:#3a5a7a;font-size:0.78rem;'>純技術指標信號</span>"
            sl = round(r['price']-1.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']+1.5*r['atr'],2)
            tp = round(r['price']+2.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']-2.5*r['atr'],2)
            st.markdown(f"""
            <div class='signal-card {cls}'>
                <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                    <span style='font-size:1.05rem;font-weight:700;
                                 font-family:Share Tech Mono,monospace;'>
                        {r['ticker']} <span style='color:#5a7a9a;font-size:0.85rem;'>[{r['tf']}]</span>
                    </span>
                    <span style='font-size:0.95rem;font-weight:700;'>{se}</span>
                </div>
                <div style='margin-bottom:8px;'>{tags}</div>
                <div style='display:flex;gap:16px;font-size:0.82rem;color:#8aabb0;flex-wrap:wrap;'>
                    <span>💰 ${r['price']:.2f}</span>
                    <span>📊 RSI {r['rsi']:.1f}</span>
                    <span>🛑 SL ${sl}</span>
                    <span>🎯 TP ${tp}</span>
                    <span>趨勢 {r['trend']}</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3 — K線圖
# ══════════════════════════════════════════════
with tab_chart:
    all_chart_tfs = sorted(list(set(timeframes)|{tf for g in mtf_groups for tf in g['tfs']}),
                           key=lambda x: ALL_TF.index(x) if x in ALL_TF else 99)
    c1, c2 = st.columns(2)
    with c1: chart_ticker = st.selectbox("股票", tickers, key="ck_tk")
    with c2: chart_tf     = st.selectbox("時框", all_chart_tfs or ALL_TF, key="ck_tf")
    if st.button("📊 載入K線圖"):
        with st.spinner("載入中..."):
            df_c = fetch_data(chart_ticker, chart_tf)
            if df_c is not None:
                st.plotly_chart(build_chart(df_c, chart_ticker, chart_tf),
                                use_container_width=True)
                l = df_c.iloc[-1]
                i1,i2,i3,i4 = st.columns(4)
                i1.metric("現價",    f"${float(l['Close']):.2f}")
                i2.metric("RSI(14)", f"{float(l['RSI']):.1f}")
                i3.metric("MACD柱",  f"{float(l['MACD_hist']):.3f}")
                i4.metric("ATR(14)", f"{float(l['ATR']):.2f}")
            else:
                st.error("無法載入數據，請檢查股票代號")


# ══════════════════════════════════════════════
# TAB 4 — 掃描日誌
# ══════════════════════════════════════════════
with tab_log:
    if st.session_state.scan_log:
        st.markdown(f"<div class='log-box'>{'<br>'.join(st.session_state.scan_log[:80])}</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown("<div class='log-box'>等待掃描...</div>", unsafe_allow_html=True)
    if st.button("🗑 清除日誌"): st.session_state.scan_log=[]; st.rerun()


# ─────────────────────────────────────────────
# AUTO SCAN LOOP
# ─────────────────────────────────────────────
if auto_scan and tickers:
    st.markdown(f"""<div class='conf-alert'>
        <span class='status-dot dot-conf'></span>
        自動掃描中（含共振分析）... 每 {scan_interval} 秒更新
    </div>""", unsafe_allow_html=True)
    time.sleep(scan_interval)
    st.cache_data.clear()
    do_scan()
    st.rerun()
