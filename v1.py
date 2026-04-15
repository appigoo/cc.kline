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

st.set_page_config(page_title="K-Line AI Trading / K線 AI 交易", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ═════════════════════════════════════════════
# 🌐 LANGUAGE DICTIONARY  (繁中 / English)
# ═════════════════════════════════════════════
LANG = {
    # ── Page titles ──────────────────────────
    "page_title": {
        "zh": "📊 K線 AI 自動交易系統",
        "en": "📊 K-Line AI Auto Trading System"
    },
    "page_subtitle": {
        "zh": "16種核心K線形態 ｜ 三週期共振過濾 ｜ Telegram 信號推送 ｜ 實盤就緒",
        "en": "16 Core Candlestick Patterns | Multi-TF Confluence | Telegram Alerts | Live-Ready"
    },
    "lang_btn": {
        "zh": "🇺🇸 Switch to English",
        "en": "🇭🇰 切換繁體中文"
    },
    # ── Sidebar ───────────────────────────────
    "sidebar_title":        {"zh": "⚙ 系統設定",              "en": "⚙ Settings"},
    "ticker_label":         {"zh": "📌 股票代號",              "en": "📌 Ticker Symbols"},
    "ticker_hint":          {"zh": "多個股票用逗號分隔",       "en": "Separate multiple tickers with commas"},
    "general_tf_label":     {"zh": "⏱ 一般監控時框",          "en": "⏱ General Timeframes"},
    "general_tf_hint":      {"zh": "單時框信號監控",           "en": "Single-timeframe signal monitoring"},
    "mtf_section":          {"zh": "⚡ 多時框共振設定",        "en": "⚡ Multi-TF Confluence"},
    "mtf_hint":             {"zh": "設定共振組合：全部週期同向才觸發信號",
                             "en": "All selected timeframes must align to trigger a signal"},
    "mtf_enable":           {"zh": "啟用多時框共振監控",       "en": "Enable Multi-TF Confluence"},
    "mtf_group":            {"zh": "📦 共振組",               "en": "📦 Confluence Group"},
    "mtf_enable_group":     {"zh": "啟用",                    "en": "Enable"},
    "mtf_tf_hint":          {"zh": "週期（2-3個）",            "en": "Timeframes (select 2–3)"},
    "mtf_active":           {"zh": "✅ 已啟用 {} 個共振組",    "en": "✅ {} active confluence group(s)"},
    "mtf_all_align":        {"zh": "個週期需同向",             "en": "timeframes must align"},
    "tg_section":           {"zh": "📡 Telegram 設定",        "en": "📡 Telegram Settings"},
    "tg_token":             {"zh": "Bot Token",               "en": "Bot Token"},
    "tg_chat":              {"zh": "Chat ID",                 "en": "Chat ID"},
    "tg_enable":            {"zh": "啟用 Telegram 推送",      "en": "Enable Telegram Alerts"},
    "tg_single":            {"zh": "推送單時框信號",           "en": "Send Single-TF Signals"},
    "tg_conf":              {"zh": "推送共振信號（優先）",      "en": "Send Confluence Signals (Priority)"},
    "tg_test":              {"zh": "🧪 測試 Telegram",        "en": "🧪 Test Telegram"},
    "tg_ok":                {"zh": "✅ 成功",                 "en": "✅ Connected"},
    "tg_fill":              {"zh": "請填寫 Token 和 Chat ID", "en": "Please enter Token and Chat ID"},
    "auto_scan_section":    {"zh": "⏰ 自動掃描",              "en": "⏰ Auto Scan"},
    "auto_scan_toggle":     {"zh": "啟用自動掃描",             "en": "Enable Auto Scan"},
    "scan_interval":        {"zh": "掃描間隔（秒）",           "en": "Scan Interval (seconds)"},
    "filter_section":       {"zh": "🎯 信號過濾",              "en": "🎯 Signal Filter"},
    "min_strength":         {"zh": "最低形態信心度 (%)",       "en": "Min Pattern Confidence (%)"},
    "trend_confirm":        {"zh": "需要趨勢確認",             "en": "Require Trend Confirmation"},
    "disclaimer":           {"zh": "⚠ 僅供參考，後果自負",    "en": "⚠ For reference only. Trade at your own risk."},
    # ── Buttons ───────────────────────────────
    "btn_scan":             {"zh": "🔍 立即掃描",              "en": "🔍 Scan Now"},
    "btn_clear_cache":      {"zh": "🔄 清除快取",              "en": "🔄 Clear Cache"},
    "btn_load_chart":       {"zh": "📊 載入K線圖",             "en": "📊 Load Chart"},
    "btn_clear_log":        {"zh": "🗑 清除日誌",              "en": "🗑 Clear Log"},
    # ── Metrics ───────────────────────────────
    "metric_tickers":       {"zh": "監控股票",                 "en": "Watching"},
    "metric_buy":           {"zh": "看漲信號 🟢",              "en": "Bullish 🟢"},
    "metric_sell":          {"zh": "看跌信號 🔴",              "en": "Bearish 🔴"},
    "metric_conf_buy":      {"zh": "共振做多 🚀",              "en": "Confluence Long 🚀"},
    "metric_conf_sell":     {"zh": "共振做空 💥",              "en": "Confluence Short 💥"},
    "metric_last_scan":     {"zh": "最後掃描",                 "en": "Last Scan"},
    # ── Tabs ──────────────────────────────────
    "tab_confluence":       {"zh": "⚡ 多時框共振",            "en": "⚡ MTF Confluence"},
    "tab_single":           {"zh": "📈 單時框信號",            "en": "📈 Single-TF Signals"},
    "tab_chart":            {"zh": "🕯️ K線圖",               "en": "🕯️ Chart"},
    "tab_log":              {"zh": "📋 掃描日誌",              "en": "📋 Scan Log"},
    # ── Pattern reference ─────────────────────
    "pattern_ref_title":    {"zh": "📖 16種核心K線形態一覧",   "en": "📖 16 Core Candlestick Patterns"},
    "col_pattern":          {"zh": "形態",                    "en": "Pattern"},
    "col_signal":           {"zh": "信號",                    "en": "Signal"},
    "col_confidence":       {"zh": "信心度",                  "en": "Confidence"},
    "col_desc":             {"zh": "說明",                    "en": "Description"},
    # ── Signal labels ─────────────────────────
    "sig_buy":              {"zh": "🟢 看漲",                 "en": "🟢 Bullish"},
    "sig_sell":             {"zh": "🔴 看跌",                 "en": "🔴 Bearish"},
    "sig_neutral":          {"zh": "🟡 中性",                 "en": "🟡 Neutral"},
    "sig_indicator_only":   {"zh": "純技術指標信號",           "en": "Technical indicator signal only"},
    # ── Confluence tab ────────────────────────
    "conf_config_title":    {"zh": "#### 🔗 當前共振組設定",   "en": "#### 🔗 Active Confluence Groups"},
    "conf_results_title":   {"zh": "#### 🚨 共振信號結果",     "en": "#### 🚨 Confluence Signals"},
    "conf_no_signal":       {"zh": "目前無共振信號。請點擊「立即掃描」，或等待自動掃描。",
                             "en": "No confluence signals yet. Click 'Scan Now' or enable Auto Scan."},
    "conf_condition":       {"zh": "共振條件：共振組內所有週期必須同時出現相同方向信號",
                             "en": "Condition: All timeframes in a group must show the same directional signal."},
    "conf_long":            {"zh": "🚀 做多共振 (LONG)",       "en": "🚀 Confluence LONG"},
    "conf_short":           {"zh": "💥 做空共振 (SHORT)",      "en": "💥 Confluence SHORT"},
    "conf_group_lbl":       {"zh": "共振組",                  "en": "Group"},
    "conf_period_lbl":      {"zh": "週期",                    "en": "Periods"},
    "conf_time_lbl":        {"zh": "時間",                    "en": "Time"},
    "conf_strength":        {"zh": "⭐ 強度: 極強",            "en": "⭐ Strength: Extreme"},
    "conf_no_mtf":          {"zh": "請在左側側欄啟用「多時框共振監控」。",
                             "en": "Please enable 'Multi-TF Confluence' in the sidebar."},
    "conf_no_group":        {"zh": "請至少設定一個共振組（每組需選 2-3 個週期）。",
                             "en": "Please configure at least one confluence group (2–3 timeframes each)."},
    "conf_watermark":       {"zh": "⚡ 多時框共振",            "en": "⚡ MTF Confluence"},
    # ── Single TF tab ─────────────────────────
    "single_no_signal":     {"zh": "⚡ 點擊「立即掃描」開始分析。",
                             "en": "⚡ Click 'Scan Now' to start analysis."},
    "trend_label":          {"zh": "趨勢",                    "en": "Trend"},
    # ── Chart tab ─────────────────────────────
    "chart_ticker_lbl":     {"zh": "股票",                    "en": "Ticker"},
    "chart_tf_lbl":         {"zh": "時框",                    "en": "Timeframe"},
    "chart_price":          {"zh": "現價",                    "en": "Price"},
    "chart_no_data":        {"zh": "無法載入數據，請檢查股票代號",
                             "en": "Failed to load data. Please check the ticker symbol."},
    # ── Log tab ───────────────────────────────
    "log_waiting":          {"zh": "等待掃描...",              "en": "Waiting for scan..."},
    # ── Auto scan banner ──────────────────────
    "auto_scanning":        {"zh": "自動掃描中（含共振分析）... 每 {} 秒更新",
                             "en": "Auto-scanning (with confluence) every {} seconds..."},
    # ── Trade labels ──────────────────────────
    "price_lbl":            {"zh": "💰 現價",                 "en": "💰 Price"},
    "rsi_lbl":              {"zh": "📊 RSI",                  "en": "📊 RSI"},
    "sl_lbl":               {"zh": "🛑 SL",                   "en": "🛑 SL"},
    "tp_lbl":               {"zh": "🎯 TP",                   "en": "🎯 TP"},
    "rr_lbl":               {"zh": "📐 風報",                 "en": "📐 R:R"},
    # ── Data insufficient ─────────────────────
    "data_insufficient":    {"zh": "數據不足",                "en": "Insufficient data"},
    # ── Telegram messages (kept bilingual) ────
    "tg_single_title":      {"zh": "K線信號",                 "en": "Candlestick Signal"},
    "tg_conf_title":        {"zh": "⚡ 多時框共振信號 ⚡",     "en": "⚡ Multi-TF Confluence Signal ⚡"},
    "tg_action_long":       {"zh": "做多 (LONG)",             "en": "LONG"},
    "tg_action_short":      {"zh": "做空 (SHORT)",            "en": "SHORT"},
    "tg_resonance_periods": {"zh": "共振週期",                "en": "Confluence Periods"},
    "tg_each_tf":           {"zh": "各週期",                  "en": "Per Timeframe"},
    "tg_extreme_strength":  {"zh": "極強",                    "en": "Extreme"},
    "tg_disclaimer":        {"zh": "僅供參考，請自行判斷風險", "en": "For reference only. Trade at your own risk."},
    "tg_test_msg":          {"zh": "✅ K線 AI 系統連線測試成功！\n⚡ 多時框共振功能已就緒。",
                             "en": "✅ K-Line AI System connected!\n⚡ Multi-TF Confluence is ready."},
}

# Pattern reference table (bilingual rows)
PATTERN_REF = {
    "zh": [
        ["十字星 Doji",          "中性","50%","方向猶豫"],
        ["錘子線 Hammer",         "看漲","75%","下跌末端反轉"],
        ["倒錘子 Inv.Hammer",     "看漲","60%","長上影需確認"],
        ["流星線 Shooting Star",  "看跌","75%","上漲末端反轉"],
        ["上吊線 Hanging Man",    "看跌","65%","上漲末端警告"],
        ["看漲吞噬 Bull Engulf",  "看漲","80%","大陽吞噬前陰"],
        ["看跌吞噬 Bear Engulf",  "看跌","80%","大陰吞噬前陽"],
        ["晨星 Morning Star",     "看漲","85%","底部三K反轉"],
        ["黃昏星 Evening Star",   "看跌","85%","頂部三K反轉"],
        ["三白兵 3 Soldiers",     "看漲","88%","三根大陽強勢"],
        ["三黑鴉 3 Crows",        "看跌","88%","三根大陰強勢"],
        ["穿刺線 Piercing",       "看漲","72%","穿越前日中點"],
        ["烏雲蓋頂 Dark Cloud",   "看跌","72%","跌破前日中點"],
        ["陽光棍 Bull Marubozu",  "看漲","70%","無影大陽"],
        ["陰光棍 Bear Marubozu",  "看跌","70%","無影大陰"],
        ["鑷底 Tweezer Bottom",   "看漲","65%","同低支撐"],
        ["鑷頂 Tweezer Top",      "看跌","65%","同高阻力"],
    ],
    "en": [
        ["Doji",               "Neutral","50%","Indecision, await confirmation"],
        ["Hammer",             "Bullish","75%","Reversal at bottom, long lower shadow"],
        ["Inverted Hammer",    "Bullish","60%","Long upper shadow, needs confirmation"],
        ["Shooting Star",      "Bearish","75%","Reversal at top, long upper shadow"],
        ["Hanging Man",        "Bearish","65%","Warning at top, long lower shadow"],
        ["Bullish Engulfing",  "Bullish","80%","Large bullish candle engulfs prior bearish"],
        ["Bearish Engulfing",  "Bearish","80%","Large bearish candle engulfs prior bullish"],
        ["Morning Star",       "Bullish","85%","3-candle bottom reversal, strong"],
        ["Evening Star",       "Bearish","85%","3-candle top reversal, strong"],
        ["3 White Soldiers",   "Bullish","88%","3 consecutive strong bullish candles"],
        ["3 Black Crows",      "Bearish","88%","3 consecutive strong bearish candles"],
        ["Piercing Line",      "Bullish","72%","Opens low, closes above midpoint"],
        ["Dark Cloud Cover",   "Bearish","72%","Opens high, closes below midpoint"],
        ["Bull Marubozu",      "Bullish","70%","Full bullish candle, no shadows"],
        ["Bear Marubozu",      "Bearish","70%","Full bearish candle, no shadows"],
        ["Tweezer Bottom",     "Bullish","65%","Equal lows — support confirmed"],
        ["Tweezer Top",        "Bearish","65%","Equal highs — resistance confirmed"],
    ]
}

def t(key):
    """Get translated string for current language."""
    lang = st.session_state.get("lang", "zh")
    entry = LANG.get(key, {})
    return entry.get(lang, entry.get("zh", key))


# ═════════════════════════════════════════════
# CSS — LIGHT THEME (matching screenshot)
# ═════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
:root {
    --bg: #f5f5f5;
    --surface: #ffffff;
    --card: #ffffff;
    --border: #e0e0e0;
    --accent: #2e7d32;
    --green: #2e9e5a;
    --red: #d44;
    --yellow: #e6a817;
    --orange: #e67e22;
    --purple: #7b61ff;
    --text: #333333;
    --text-secondary: #666666;
    --muted: #999999;
}
html, body, [class*="css"] {
    font-family: 'Noto Sans HK', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text);
}
.stApp {
    background: var(--bg) !important;
}
h1, h2, h3 {
    font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: 0.5px;
    font-weight: 600 !important;
}

/* ── LANG TOGGLE ── */
.lang-bar { display:flex; justify-content:flex-end; align-items:center; margin-bottom:12px; gap:10px; }
.lang-badge { font-size:0.72rem; color:var(--muted); letter-spacing:1px; }
.lang-toggle-btn {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 16px;
    color: var(--text);
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.lang-toggle-btn:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-color: var(--accent); }

/* ── HEADER ── */
.main-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 30px;
    margin-bottom: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.main-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--green), var(--orange), var(--green));
}
.main-header h1 { font-size: 1.9rem; margin: 0; color: var(--text) !important; }
.main-header p { color: var(--muted); margin: 5px 0 0; font-size: 0.83rem; }

/* ── METRICS ── */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 15px 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.metric-val { font-weight: 700; font-size: 1.5rem; }
.metric-lbl { font-size: 0.75rem; color: var(--muted); margin-top: 4px; }

/* ── CONFLUENCE CARD ── */
.confluence-card {
    border-radius: 12px;
    padding: 18px 22px;
    margin: 10px 0;
    border: 1px solid;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.conf-watermark {
    position: absolute;
    top: 8px; right: 14px;
    font-size: 0.7rem;
    opacity: 0.35;
    letter-spacing: 1px;
    color: var(--muted);
}
.conf-buy {
    background: #f0faf3;
    border-color: var(--green);
}
.conf-sell {
    background: #fdf2f2;
    border-color: var(--red);
}

/* ── TF BADGES ── */
.tf-grid { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
.tf-badge {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    border-radius: 8px;
    padding: 6px 12px;
    min-width: 60px;
    font-weight: 600;
    font-size: 0.75rem;
}
.tf-badge-buy { background: #e8f5e9; border: 1px solid var(--green); color: var(--green); }
.tf-badge-sell { background: #ffebee; border: 1px solid var(--red); color: var(--red); }
.tf-badge-neutral { background: #f5f5f5; border: 1px solid var(--muted); color: var(--muted); }
.tf-badge span { font-size: 0.62rem; opacity: 0.7; margin-top: 2px; }

/* ── SIGNAL CARDS ── */
.signal-card {
    background: var(--surface);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    border-left: 4px solid;
    font-size: 0.88rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.signal-buy { border-color: var(--green); }
.signal-sell { border-color: var(--red); }
.signal-neutral { border-color: var(--yellow); }

/* ── MTF CONFIG BOX ── */
.mtf-box {
    background: #fafafa;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
}
.mtf-box-title {
    color: var(--orange);
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

/* ── PATTERN TAGS ── */
.pattern-tag {
    display: inline-block;
    background: #e8f5e9;
    border: 1px solid #c8e6c9;
    border-radius: 5px;
    padding: 2px 8px;
    font-size: 0.75rem;
    color: var(--green);
    margin: 2px;
    font-weight: 500;
}

/* ── STATUS DOTS ── */
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.dot-live { background: var(--green); box-shadow: 0 0 6px var(--green); animation: pulse 2s infinite; }
.dot-conf { background: var(--orange); box-shadow: 0 0 6px var(--orange); animation: pulse 1.5s infinite; }
.dot-off { background: var(--muted); }
@keyframes pulse { 0%,100%{ opacity:1; } 50%{ opacity:0.3; } }

/* ── BUTTONS ── */
.stButton > button {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    color: var(--accent) !important;
}

/* ── SIDEBAR ── */
div[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
div[data-testid="stSidebar"] label { color: var(--text) !important; }

/* ── LOG BOX ── */
.log-box {
    background: #fafafa;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    font-family: 'SF Mono', 'Menlo', 'Consolas', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
    max-height: 220px;
    overflow-y: auto;
    line-height: 1.6;
}
hr { border-color: var(--border); }
.alert-box {
    background: #fffde7;
    border: 1px solid var(--yellow);
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 0.83rem;
    color: #7a6600;
    margin: 8px 0;
}
.conf-alert {
    background: #fff3e0;
    border: 1px solid var(--orange);
    border-radius: 8px;
    padding: 10px 15px;
    font-size: 0.83rem;
    color: #a85600;
    margin: 8px 0;
}

/* ── Streamlit overrides for light theme ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px 8px 0 0;
    color: var(--text-secondary);
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    border-bottom-color: var(--surface) !important;
    color: var(--accent) !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# SESSION STATE — language default
# ═════════════════════════════════════════════
if "lang" not in st.session_state:
    st.session_state.lang = "zh"
for k, v in [("scan_log",[]),("last_scan",None),
              ("single_results",[]),("confluence_results",[])]:
    if k not in st.session_state:
        st.session_state[k] = v


# ═════════════════════════════════════════════
# 🌐 LANGUAGE TOGGLE BAR  (top-right)
# ═════════════════════════════════════════════
lang_col_space, lang_col_btn = st.columns([5, 1])
with lang_col_btn:
    if st.button(t("lang_btn"), key="lang_toggle_top", use_container_width=True):
        st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
        st.rerun()


# ═════════════════════════════════════════════
# CANDLESTICK PATTERN ENGINE
# ═════════════════════════════════════════════
class CandlestickPatterns:
    def __init__(self, df):
        self.o = df['Open'].values; self.h = df['High'].values
        self.l = df['Low'].values;  self.c = df['Close'].values
        self.n = len(df)

    def _body(self, i): return abs(self.c[i] - self.o[i])
    def _upper(self, i): return self.h[i] - max(self.o[i], self.c[i])
    def _lower(self, i): return min(self.o[i], self.c[i]) - self.l[i]
    def _bull(self, i): return self.c[i] > self.o[i]
    def _bear(self, i): return self.c[i] < self.o[i]

    def doji(self, i):
        b=self._body(i); r=self.h[i]-self.l[i]
        return r>0 and b/r<0.1
    def hammer(self, i):
        b=self._body(i)
        return b>0 and self._lower(i)>=2*b and self._upper(i)<=0.3*b
    def inverted_hammer(self, i):
        b=self._body(i)
        return b>0 and self._upper(i)>=2*b and self._lower(i)<=0.3*b
    def shooting_star(self, i):
        if i<1 or not self._bear(i): return False
        b=self._body(i)
        return b>0 and self._bull(i-1) and self._upper(i)>=2*b and self._lower(i)<=0.3*b
    def hanging_man(self, i):
        if i<1: return False
        b=self._body(i)
        return b>0 and self._bull(i-1) and self._lower(i)>=2*b and self._upper(i)<=0.3*b
    def bullish_engulfing(self, i):
        if i<1: return False
        return self._bear(i-1) and self._bull(i) and self.o[i]<self.c[i-1] and self.c[i]>self.o[i-1]
    def bearish_engulfing(self, i):
        if i<1: return False
        return self._bull(i-1) and self._bear(i) and self.o[i]>self.c[i-1] and self.c[i]<self.o[i-1]
    def morning_star(self, i):
        if i<2: return False
        b2=self._body(i-2)
        return (self._bear(i-2) and max(self.o[i-1],self.c[i-1])<self.c[i-2] and
                b2>0 and self._body(i-1)<0.3*b2 and self._bull(i) and
                self.c[i]>(self.o[i-2]+self.c[i-2])/2)
    def evening_star(self, i):
        if i<2: return False
        b2=self._body(i-2)
        return (self._bull(i-2) and min(self.o[i-1],self.c[i-1])>self.c[i-2] and
                b2>0 and self._body(i-1)<0.3*b2 and self._bear(i) and
                self.c[i]<(self.o[i-2]+self.c[i-2])/2)
    def three_white_soldiers(self, i):
        if i<2: return False
        for j in [i-2,i-1,i]:
            if not self._bull(j) or self._upper(j)>0.3*self._body(j): return False
        return self.o[i-1]>self.o[i-2] and self.o[i]>self.o[i-1] and self.c[i]>self.c[i-1]>self.c[i-2]
    def three_black_crows(self, i):
        if i<2: return False
        for j in [i-2,i-1,i]:
            if not self._bear(j) or self._lower(j)>0.3*self._body(j): return False
        return self.o[i-1]<self.o[i-2] and self.o[i]<self.o[i-1] and self.c[i]<self.c[i-1]<self.c[i-2]
    def piercing_line(self, i):
        if i<1: return False
        mid=(self.o[i-1]+self.c[i-1])/2
        return self._bear(i-1) and self._bull(i) and self.o[i]<self.l[i-1] and self.c[i]>mid
    def dark_cloud_cover(self, i):
        if i<1: return False
        mid=(self.o[i-1]+self.c[i-1])/2
        return self._bull(i-1) and self._bear(i) and self.o[i]>self.h[i-1] and self.c[i]<mid
    def marubozu_bull(self, i):
        b=self._body(i); r=self.h[i]-self.l[i]
        return r>0 and self._bull(i) and b/r>0.92
    def marubozu_bear(self, i):
        b=self._body(i); r=self.h[i]-self.l[i]
        return r>0 and self._bear(i) and b/r>0.92
    def tweezer_bottom(self, i):
        if i<1: return False
        return self._bear(i-1) and self._bull(i) and abs(self.l[i]-self.l[i-1])/max(self.l[i],0.01)<0.002
    def tweezer_top(self, i):
        if i<1: return False
        return self._bull(i-1) and self._bear(i) and abs(self.h[i]-self.h[i-1])/max(self.h[i],0.01)<0.002

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


# ═════════════════════════════════════════════
# INDICATORS
# ═════════════════════════════════════════════
def compute_indicators(df):
    c=df['Close']
    df['EMA9'] =c.ewm(span=9, adjust=False).mean()
    df['EMA21']=c.ewm(span=21,adjust=False).mean()
    df['EMA50']=c.ewm(span=50,adjust=False).mean()
    delta=c.diff(); gain=delta.clip(lower=0).rolling(14).mean()
    loss=(-delta.clip(upper=0)).rolling(14).mean()
    df['RSI']=100-(100/(1+gain/loss.replace(0,np.nan)))
    e12=c.ewm(span=12,adjust=False).mean(); e26=c.ewm(span=26,adjust=False).mean()
    df['MACD']=e12-e26; df['MACD_signal']=df['MACD'].ewm(span=9,adjust=False).mean()
    df['MACD_hist']=df['MACD']-df['MACD_signal']
    df['BB_mid']=c.rolling(20).mean(); std=c.rolling(20).std()
    df['BB_upper']=df['BB_mid']+2*std; df['BB_lower']=df['BB_mid']-2*std
    hl=df['High']-df['Low']; hc=(df['High']-df['Close'].shift()).abs()
    lc=(df['Low']-df['Close'].shift()).abs()
    df['ATR']=pd.concat([hl,hc,lc],axis=1).max(axis=1).rolling(14).mean()
    df['Vol_MA20']=df['Volume'].rolling(20).mean()
    df['Vol_ratio']=df['Volume']/df['Vol_MA20'].replace(0,np.nan)
    return df

def trend_bias(df):
    l=df.iloc[-1]; score=0
    if l['EMA9'] >l['EMA21']: score+=1
    if l['EMA21']>l['EMA50']: score+=1
    if l['MACD_hist']>0:      score+=1
    if l['RSI']>55:           score+=1
    if l['RSI']<45:           score-=1
    if l['Close']>l['BB_mid']:   score+=1
    if l['Close']<l['BB_lower']: score+=2
    if l['Close']>l['BB_upper']: score-=2
    if score>=3:  return "BUY",  score
    if score<=-1: return "SELL", score
    return "NEUTRAL", score


# ═════════════════════════════════════════════
# DATA FETCH
# ═════════════════════════════════════════════
TF_MAP={"1m":("1m","1d"),"5m":("5m","5d"),"15m":("15m","60d"),
        "30m":("30m","60d"),"1h":("1h","730d"),"1d":("1d","5y"),"1w":("1wk","10y")}
ALL_TF=["1m","5m","15m","30m","1h","1d","1w"]

@st.cache_data(ttl=60)
def fetch_data(ticker, tf):
    interval,period=TF_MAP[tf]
    df=yf.download(ticker,period=period,interval=interval,auto_adjust=True,progress=False)
    if df.empty: return None
    df.columns=[c[0] if isinstance(c,tuple) else c for c in df.columns]
    return compute_indicators(df.dropna())


# ═════════════════════════════════════════════
# TELEGRAM
# ═════════════════════════════════════════════
def send_telegram(token, chat_id, msg):
    try:
        r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id":chat_id,"text":msg,"parse_mode":"HTML"},timeout=8)
        return r.status_code==200, r.text
    except Exception as e:
        return False, str(e)

def build_single_msg(ticker, tf, patterns, trend, price, atr, rsi, lang):
    london=pytz.timezone("Europe/London")
    now=datetime.now(london).strftime("%Y-%m-%d %H:%M %Z")
    if not patterns and trend=="NEUTRAL": return None
    sig=trend
    if patterns:
        bn=sum(1 for p in patterns if p['signal']=='BUY')
        sn=sum(1 for p in patterns if p['signal']=='SELL')
        sig="BUY" if bn>sn else "SELL" if sn>bn else "NEUTRAL"
    if sig=="NEUTRAL": return None
    e="🟢📈" if sig=="BUY" else "🔴📉"
    ac=LANG["tg_action_long"][lang] if sig=="BUY" else LANG["tg_action_short"][lang]
    sl=round(price-1.5*atr,2) if sig=="BUY" else round(price+1.5*atr,2)
    tp=round(price+2.5*atr,2) if sig=="BUY" else round(price-2.5*atr,2)
    pl="\n".join([f"  • {p['pattern']} ({p['strength']}%)" for p in patterns]) or \
       f"  • {LANG['sig_indicator_only'][lang]}"
    title=LANG["tg_single_title"][lang]
    disc=LANG["tg_disclaimer"][lang]
    return (f"{e} <b>{title}</b>\n━━━━━━━━━━━━━━━━\n"
            f"📌 {ticker} [{tf}]\n🕐 {now}\n💰 ${price:.2f}  📊 RSI:{rsi:.1f}\n"
            f"━━━━━━━━━━━━━━━━\n🕯 Patterns:\n{pl}\n━━━━━━━━━━━━━━━━\n"
            f"⚡ {ac}\n🛑 SL ${sl}  🎯 TP ${tp}\n📐 R:R 1:2.5\n⚠️ {disc}")

def build_confluence_msg(ticker, sig, tf_details, price, atr, rsi, lang):
    london=pytz.timezone("Europe/London")
    now=datetime.now(london).strftime("%Y-%m-%d %H:%M %Z")
    e="🚀🟢🟢🟢" if sig=="BUY" else "💥🔴🔴🔴"
    ac=LANG["tg_action_long"][lang] if sig=="BUY" else LANG["tg_action_short"][lang]
    sl=round(price-1.5*atr,2) if sig=="BUY" else round(price+1.5*atr,2)
    tp=round(price+2.5*atr,2) if sig=="BUY" else round(price-2.5*atr,2)
    tfs="+".join([d['tf'] for d in tf_details])
    lines=""
    for d in tf_details:
        em="🟢" if d['signal']=="BUY" else "🔴"
        ps=" | ".join([p['pattern'] for p in d['patterns']]) if d['patterns'] else d['trend']
        lines+=f"  {em} [{d['tf']}] {ps}\n"
    title=LANG["tg_conf_title"][lang]
    rp_lbl=LANG["tg_resonance_periods"][lang]
    each_lbl=LANG["tg_each_tf"][lang]
    str_lbl=LANG["tg_extreme_strength"][lang]
    disc=LANG["tg_disclaimer"][lang]
    return (f"{e} <b>{title}</b>\n━━━━━━━━━━━━━━━━\n"
            f"📌 {ticker}\n🕐 {now}\n💰 ${price:.2f}  📊 RSI:{rsi:.1f}\n"
            f"🔗 {rp_lbl}: {tfs}\n━━━━━━━━━━━━━━━━\n🕯 {each_lbl}:\n{lines}"
            f"━━━━━━━━━━━━━━━━\n⚡ {ac}\n🛑 SL ${sl}  🎯 TP ${tp}\n📐 R:R 1:2.5\n"
            f"⭐ {str_lbl} ({len(tf_details)} TF)\n⚠️ {disc}")


# ═════════════════════════════════════════════
# CHART (light theme)
# ═════════════════════════════════════════════
def build_chart(df, ticker, tf):
    dp=df.tail(120)
    fig=make_subplots(rows=3,cols=1,shared_xaxes=True,
                      row_heights=[0.6,0.2,0.2],vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=dp.index,open=dp['Open'],high=dp['High'],
        low=dp['Low'],close=dp['Close'],increasing_line_color='#2e9e5a',
        decreasing_line_color='#dd4444',name="Candles"),row=1,col=1)
    for ema,col,w in [('EMA9','#5b9bd5',1),('EMA21','#e6a817',1),('EMA50','#e67e22',1.5)]:
        fig.add_trace(go.Scatter(x=dp.index,y=dp[ema],line=dict(color=col,width=w),name=ema),row=1,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['BB_upper'],
        line=dict(color='rgba(180,180,200,0.5)',width=1,dash='dot'),showlegend=False),row=1,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['BB_lower'],fill='tonexty',
        fillcolor='rgba(180,180,220,0.08)',
        line=dict(color='rgba(180,180,200,0.5)',width=1,dash='dot'),showlegend=False),row=1,col=1)
    colors=['#2e9e5a' if v>=0 else '#dd4444' for v in dp['MACD_hist']]
    fig.add_trace(go.Bar(x=dp.index,y=dp['MACD_hist'],marker_color=colors,showlegend=False),row=2,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['MACD'],line=dict(color='#5b9bd5',width=1),name='MACD'),row=2,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['MACD_signal'],line=dict(color='#e6a817',width=1),name='Signal'),row=2,col=1)
    fig.add_trace(go.Scatter(x=dp.index,y=dp['RSI'],line=dict(color='#7b61ff',width=1.5),name='RSI'),row=3,col=1)
    fig.add_hline(y=70,line_dash="dash",line_color="#dd4444",line_width=0.8,row=3,col=1)
    fig.add_hline(y=30,line_dash="dash",line_color="#2e9e5a",line_width=0.8,row=3,col=1)
    fig.update_layout(paper_bgcolor='#ffffff',plot_bgcolor='#ffffff',
        font=dict(color='#333333',size=11),xaxis_rangeslider_visible=False,
        title=dict(text=f"<b>{ticker}</b> [{tf}]",font=dict(color='#333333',size=14),x=0.5),
        legend=dict(bgcolor='rgba(255,255,255,0.9)',font=dict(size=10)),
        margin=dict(l=10,r=10,t=40,b=10),height=620)
    for ax in ['xaxis','xaxis2','xaxis3','yaxis','yaxis2','yaxis3']:
        fig.update_layout(**{ax:dict(gridcolor='#e8e8e8',showgrid=True)})
    return fig


# ═════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""<div style='text-align:center;padding:10px 0;
        color:#333;font-size:1.05rem;font-weight:600;
        letter-spacing:1px;'>{t('sidebar_title')}</div>""",
        unsafe_allow_html=True)

    if st.button(t("lang_btn"), key="lang_toggle_sidebar", use_container_width=True):
        st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
        st.rerun()

    st.markdown("---")

    st.markdown(f"**{t('ticker_label')}**")
    tickers_input = st.text_input(t("ticker_hint"), value="TSLA,NVDA,AAPL,SPY")
    tickers = [x.strip().upper() for x in tickers_input.split(",") if x.strip()]

    st.markdown(f"**{t('general_tf_label')}**")
    timeframes = st.multiselect(t("general_tf_hint"), ALL_TF, default=["5m","15m","1h"])

    st.markdown("---")

    # ── MTF Confluence ──
    st.markdown(f"""<div style='color:#e67e22;
        font-size:0.92rem;font-weight:600;letter-spacing:0.5px;padding:4px 0 2px;'>{t('mtf_section')}</div>""",
        unsafe_allow_html=True)
    st.markdown(f"""<div style='font-size:0.76rem;color:#999;margin-bottom:8px;'>
        {t('mtf_hint')}</div>""", unsafe_allow_html=True)

    mtf_enabled = st.toggle(t("mtf_enable"), value=True)
    mtf_groups  = []

    if mtf_enabled:
        for gnum, gdefault in [(1,["1m","5m","15m"]),(2,["5m","15m","1h"]),(3,["15m","1h","1d"])]:
            st.markdown(f"<div class='mtf-box'><div class='mtf-box-title'>"
                        f"{t('mtf_group')} {gnum}</div></div>", unsafe_allow_html=True)
            g_on  = st.toggle(t("mtf_enable_group"), value=(gnum==1), key=f"g{gnum}_on")
            g_tfs = st.multiselect(t("mtf_tf_hint"), ALL_TF, default=gdefault,
                                    key=f"g{gnum}_tf", max_selections=3)
            if g_on and len(g_tfs)>=2:
                lbl = f"G{gnum}" if st.session_state.lang=="en" else f"組{gnum}"
                mtf_groups.append({"label": lbl, "tfs": g_tfs})

        active_str = t("mtf_active").format(len(mtf_groups))
        st.markdown(f"<div style='font-size:0.78rem;color:#e67e22;padding:4px 0;'>"
                    f"{active_str}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Telegram ──
    st.markdown(f"**{t('tg_section')}**")
    tg_token   = st.text_input(t("tg_token"),  type="password", placeholder="123456:ABC-...")
    tg_chat    = st.text_input(t("tg_chat"),   placeholder="-1001234567890")
    tg_enabled = st.toggle(t("tg_enable"),  value=False)
    tg_single  = st.toggle(t("tg_single"),  value=True)
    tg_conf    = st.toggle(t("tg_conf"),    value=True)

    if st.button(t("tg_test")):
        if tg_token and tg_chat:
            ok, resp = send_telegram(tg_token, tg_chat, t("tg_test_msg"))
            st.success(t("tg_ok")) if ok else st.error(f"❌ {resp}")
        else:
            st.warning(t("tg_fill"))

    st.markdown("---")
    st.markdown(f"**{t('auto_scan_section')}**")
    auto_scan     = st.toggle(t("auto_scan_toggle"), value=False)
    scan_interval = st.slider(t("scan_interval"), 30, 300, 60, 10)

    st.markdown("---")
    st.markdown(f"**{t('filter_section')}**")
    min_strength          = st.slider(t("min_strength"), 50, 90, 65, 5)
    require_trend_confirm = st.toggle(t("trend_confirm"), value=True)

    st.markdown("---")
    st.markdown(f"""<div style='font-size:0.72rem;color:#999;text-align:center;line-height:1.8;'>
        📊 K-Line AI / K線 AI<br>
        <span style='color:#bbb;'>{t('disclaimer')}</span></div>""",
        unsafe_allow_html=True)


# ═════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════
st.markdown(f"""<div class='main-header'>
    <h1>{t('page_title')}</h1>
    <p>{t('page_subtitle')}</p>
</div>""", unsafe_allow_html=True)

# Pattern reference expander
with st.expander(t("pattern_ref_title"), expanded=False):
    lang = st.session_state.get("lang","zh")
    col_names = [t("col_pattern"), t("col_signal"), t("col_confidence"), t("col_desc")]
    ref_df = pd.DataFrame(PATTERN_REF[lang], columns=col_names)
    st.dataframe(ref_df, use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════
# ANALYSE HELPERS
# ═════════════════════════════════════════════
def analyse_tf(ticker, tf):
    df=fetch_data(ticker,tf)
    if df is None or len(df)<30: return None
    last=df.iloc[-1]
    price=float(last['Close'])
    rsi=float(last['RSI']) if not np.isnan(last['RSI']) else 50.0
    atr=float(last['ATR']) if not np.isnan(last['ATR']) else price*0.01
    cp=CandlestickPatterns(df)
    pats=[p for p in cp.scan_latest() if p['strength']>=min_strength]
    trend,_=trend_bias(df)
    if require_trend_confirm and pats:
        if trend=='BUY':   pats=[p for p in pats if p['signal']=='BUY']
        elif trend=='SELL': pats=[p for p in pats if p['signal']=='SELL']
    if pats:
        bn=sum(1 for p in pats if p['signal']=='BUY')
        sn=sum(1 for p in pats if p['signal']=='SELL')
        sig='BUY' if bn>sn else 'SELL' if sn>bn else 'NEUTRAL'; sa=float(np.mean([p['strength'] for p in pats]))
    else:
        sig=trend if trend!='NEUTRAL' else 'NEUTRAL'; sa=0.0
    return {"ticker":ticker,"tf":tf,"price":price,"rsi":rsi,"atr":atr,
            "patterns":pats,"trend":trend,"signal":sig,"strength":sa}

def check_confluence(by_tf, group_tfs):
    details=[]; signals=[]
    for tf in group_tfs:
        r=by_tf.get(tf)
        if r is None or r['signal']=='NEUTRAL': return None,[]
        signals.append(r['signal'])
        details.append({"tf":tf,"signal":r['signal'],
                         "patterns":r['patterns'],"trend":r['trend']})
    if len(set(signals))==1: return signals[0],details
    return None,[]


# ═════════════════════════════════════════════
# MAIN SCAN
# ═════════════════════════════════════════════
def do_scan():
    lang=st.session_state.get("lang","zh")
    london=pytz.timezone("Europe/London")
    now_str=datetime.now(london).strftime("%H:%M:%S")
    log=[]; single_out=[]; conf_out=[]
    all_needed=set(timeframes)
    for g in mtf_groups: all_needed|=set(g['tfs'])

    for ticker in tickers:
        by_tf={}
        for tf in all_needed:
            r=analyse_tf(ticker,tf)
            if r: by_tf[tf]=r

        for tf in timeframes:
            r=by_tf.get(tf)
            if r is None:
                log.append(f"[{now_str}] ⚠ {ticker}/{tf} {t('data_insufficient')}"); continue
            single_out.append(r)
            if r['signal']!='NEUTRAL' or r['patterns']:
                em="🟢" if r['signal']=='BUY' else "🔴" if r['signal']=='SELL' else "🟡"
                log.append(f"[{now_str}] {em} {ticker}/{tf} ${r['price']:.2f} → {r['signal']}")
                if tg_enabled and tg_single and tg_token and tg_chat and r['signal']!='NEUTRAL':
                    msg=build_single_msg(ticker,tf,r['patterns'],r['trend'],
                                         r['price'],r['atr'],r['rsi'],lang)
                    if msg:
                        ok,_=send_telegram(tg_token,tg_chat,msg)
                        log.append(f"[{now_str}]   📡 {'✅' if ok else '❌'}")

        for group in mtf_groups:
            sig,details=check_confluence(by_tf,group['tfs'])
            if sig:
                ref=by_tf.get(group['tfs'][-1]) or list(by_tf.values())[0]
                entry={"ticker":ticker,"signal":sig,"group_label":group['label'],
                       "group_tfs":group['tfs'],"tf_details":details,
                       "price":ref['price'],"rsi":ref['rsi'],"atr":ref['atr'],"ts":now_str}
                conf_out.append(entry)
                tfs_str="+".join(group['tfs'])
                em="🚀" if sig=="BUY" else "💥"
                log.append(f"[{now_str}] {em}⚡ CONFLUENCE {ticker} [{tfs_str}] → {sig}")
                if tg_enabled and tg_conf and tg_token and tg_chat:
                    msg=build_confluence_msg(ticker,sig,details,
                                              ref['price'],ref['atr'],ref['rsi'],lang)
                    ok,_=send_telegram(tg_token,tg_chat,msg)
                    log.append(f"[{now_str}]   📡 Confluence TG {'✅' if ok else '❌'}")

    st.session_state.single_results=single_out
    st.session_state.confluence_results=conf_out
    st.session_state.last_scan=datetime.now(london)
    for l in log: st.session_state.scan_log.insert(0,l)
    st.session_state.scan_log=st.session_state.scan_log[:150]
    return single_out, conf_out


# ═════════════════════════════════════════════
# SCAN BUTTONS
# ═════════════════════════════════════════════
cb1,cb2,_=st.columns([1,1,3])
with cb1:
    scan_now=st.button(t("btn_scan"), use_container_width=True)
with cb2:
    if st.button(t("btn_clear_cache"), use_container_width=True):
        st.cache_data.clear(); st.rerun()

if scan_now:
    with st.spinner("⚡ ..."):
        single_results, confluence_results = do_scan()
else:
    single_results     = st.session_state.single_results
    confluence_results = st.session_state.confluence_results


# ═════════════════════════════════════════════
# METRICS BAR
# ═════════════════════════════════════════════
last_str = st.session_state.last_scan.strftime("%H:%M %Z") if st.session_state.last_scan else "—"
buy_n    = sum(1 for r in single_results     if r['signal']=='BUY')
sell_n   = sum(1 for r in single_results     if r['signal']=='SELL')
conf_buy = sum(1 for r in confluence_results if r['signal']=='BUY')
conf_sel = sum(1 for r in confluence_results if r['signal']=='SELL')

metric_data=[
    (str(len(tickers)), t("metric_tickers"),   "#333"),
    (str(buy_n),        t("metric_buy"),        "#2e9e5a"),
    (str(sell_n),       t("metric_sell"),       "#dd4444"),
    (str(conf_buy),     t("metric_conf_buy"),   "#e67e22"),
    (str(conf_sel),     t("metric_conf_sell"),  "#dd4444"),
    (last_str,          t("metric_last_scan"),  "#333"),
]
for col,(val,lbl,color) in zip(st.columns(6), metric_data):
    with col:
        fs="1.05rem" if len(val)>5 else "1.5rem"
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-val' style='color:{color};font-size:{fs};'>{val}</div>
            <div class='metric-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════
tab_conf, tab_single, tab_chart, tab_log = st.tabs([
    t("tab_confluence"), t("tab_single"), t("tab_chart"), t("tab_log")
])


# ─── TAB 1: CONFLUENCE ───────────────────────
with tab_conf:
    if mtf_enabled and mtf_groups:
        st.markdown(t("conf_config_title"))
        gcols=st.columns(max(len(mtf_groups),1))
        for idx,g in enumerate(mtf_groups):
            with gcols[idx]:
                badges="".join([f"<span class='pattern-tag'>{tf}</span>" for tf in g['tfs']])
                align_txt=f"{len(g['tfs'])} {t('mtf_all_align')}"
                st.markdown(f"""
                <div style='background:#fafafa;border:1px solid #e0e0e0;border-radius:10px;
                            padding:14px;text-align:center;'>
                    <div style='color:#e67e22;font-weight:600;
                                font-size:0.82rem;margin-bottom:8px;'>⚡ {g["label"]}</div>
                    <div>{badges}</div>
                    <div style='font-size:0.72rem;color:#2e9e5a;margin-top:8px;'>{align_txt}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(t("conf_results_title"))

        if not confluence_results:
            st.markdown(f"""<div class='conf-alert'>
                {t('conf_no_signal')}<br>
                <small style='opacity:0.7;'>{t('conf_condition')}</small>
            </div>""", unsafe_allow_html=True)
        else:
            for r in confluence_results:
                cls  = "conf-buy" if r['signal']=='BUY' else "conf-sell"
                s_lbl= t("conf_long") if r['signal']=='BUY' else t("conf_short")
                sl   = round(r['price']-1.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']+1.5*r['atr'],2)
                tp   = round(r['price']+2.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']-2.5*r['atr'],2)
                tf_badges=""
                for d in r['tf_details']:
                    bc="tf-badge-buy" if d['signal']=='BUY' else "tf-badge-sell"
                    pn=d['patterns'][0]['pattern'][:14] if d['patterns'] else d['trend']
                    tf_badges+=f"<div class='tf-badge {bc}'>{d['tf']}<span>{pn}</span></div>"
                wm=t("conf_watermark")
                grp_lbl=t("conf_group_lbl"); per_lbl=t("conf_period_lbl"); tm_lbl=t("conf_time_lbl")
                st.markdown(f"""
                <div class='confluence-card {cls}'>
                    <div class='conf-watermark'>{wm}</div>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>
                        <span style='font-size:1.25rem;font-weight:700;color:#333;'>{r['ticker']}</span>
                        <span style='font-size:1rem;font-weight:700;'>{s_lbl}</span>
                    </div>
                    <div style='font-size:0.75rem;color:#999;margin-bottom:8px;'>
                        {grp_lbl}: {r['group_label']} &nbsp;｜&nbsp;
                        {per_lbl}: {" + ".join(r['group_tfs'])} &nbsp;｜&nbsp;
                        {tm_lbl}: {r['ts']}
                    </div>
                    <div class='tf-grid'>{tf_badges}</div>
                    <div style='display:flex;gap:16px;font-size:0.82rem;color:#888;
                                margin-top:10px;padding-top:10px;
                                border-top:1px solid #eee;flex-wrap:wrap;'>
                        <span>{t('price_lbl')}: <b style='color:#333'>${r['price']:.2f}</b></span>
                        <span>{t('rsi_lbl')}: <b style='color:#333'>{r['rsi']:.1f}</b></span>
                        <span>{t('sl_lbl')}: <b style='color:#dd4444'>${sl}</b></span>
                        <span>{t('tp_lbl')}: <b style='color:#2e9e5a'>${tp}</b></span>
                        <span>{t('rr_lbl')}: <b style='color:#333'>1:2.5</b></span>
                        <span>{t('conf_strength')}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    elif not mtf_enabled:
        st.markdown(f"<div class='alert-box'>{t('conf_no_mtf')}</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alert-box'>{t('conf_no_group')}</div>",
                    unsafe_allow_html=True)


# ─── TAB 2: SINGLE TF ────────────────────────
with tab_single:
    if not single_results:
        st.markdown(f"<div class='alert-box'>{t('single_no_signal')}</div>",
                    unsafe_allow_html=True)
    else:
        for r in sorted(single_results,
                        key=lambda x:(0 if x['signal'] in ['BUY','SELL'] else 1,-x['strength'])):
            if r['signal']=='NEUTRAL' and not r['patterns']: continue
            cls=('signal-buy' if r['signal']=='BUY' else
                 'signal-sell' if r['signal']=='SELL' else 'signal-neutral')
            se=(t("sig_buy") if r['signal']=='BUY' else
                t("sig_sell") if r['signal']=='SELL' else t("sig_neutral"))
            tags="".join([f"<span class='pattern-tag'>{p['pattern']} {p['strength']}%</span>"
                           for p in r['patterns']]) or \
                 f"<span style='color:#999;font-size:0.78rem;'>{t('sig_indicator_only')}</span>"
            sl=round(r['price']-1.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']+1.5*r['atr'],2)
            tp=round(r['price']+2.5*r['atr'],2) if r['signal']=='BUY' else round(r['price']-2.5*r['atr'],2)
            st.markdown(f"""
            <div class='signal-card {cls}'>
                <div style='display:flex;justify-content:space-between;margin-bottom:8px;'>
                    <span style='font-size:1.05rem;font-weight:700;color:#333;'>
                        {r['ticker']} <span style='color:#999;font-size:0.85rem;'>[{r['tf']}]</span>
                    </span>
                    <span style='font-size:0.95rem;font-weight:700;'>{se}</span>
                </div>
                <div style='margin-bottom:8px;'>{tags}</div>
                <div style='display:flex;gap:16px;font-size:0.82rem;color:#888;flex-wrap:wrap;'>
                    <span>{t('price_lbl')}: <b style='color:#333'>${r['price']:.2f}</b></span>
                    <span>{t('rsi_lbl')}: <b style='color:#333'>{r['rsi']:.1f}</b></span>
                    <span>{t('sl_lbl')}: <b style='color:#dd4444'>${sl}</b></span>
                    <span>{t('tp_lbl')}: <b style='color:#2e9e5a'>${tp}</b></span>
                    <span>{t('trend_label')}: <b style='color:#333'>{r['trend']}</b></span>
                </div>
            </div>""", unsafe_allow_html=True)


# ─── TAB 3: CHART ────────────────────────────
with tab_chart:
    all_chart_tfs=sorted(list(set(timeframes)|{tf for g in mtf_groups for tf in g['tfs']}),
                          key=lambda x:ALL_TF.index(x) if x in ALL_TF else 99)
    c1,c2=st.columns(2)
    with c1: chart_ticker=st.selectbox(t("chart_ticker_lbl"), tickers, key="ck_tk")
    with c2: chart_tf    =st.selectbox(t("chart_tf_lbl"), all_chart_tfs or ALL_TF, key="ck_tf")
    if st.button(t("btn_load_chart")):
        with st.spinner("..."):
            df_c=fetch_data(chart_ticker,chart_tf)
            if df_c is not None:
                st.plotly_chart(build_chart(df_c,chart_ticker,chart_tf),use_container_width=True)
                l=df_c.iloc[-1]
                i1,i2,i3,i4=st.columns(4)
                i1.metric(t("chart_price"),  f"${float(l['Close']):.2f}")
                i2.metric("RSI(14)",         f"{float(l['RSI']):.1f}")
                i3.metric("MACD Hist",       f"{float(l['MACD_hist']):.3f}")
                i4.metric("ATR(14)",         f"{float(l['ATR']):.2f}")
            else:
                st.error(t("chart_no_data"))


# ─── TAB 4: LOG ──────────────────────────────
with tab_log:
    if st.session_state.scan_log:
        st.markdown(f"<div class='log-box'>{'<br>'.join(st.session_state.scan_log[:80])}</div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='log-box'>{t('log_waiting')}</div>", unsafe_allow_html=True)
    if st.button(t("btn_clear_log")):
        st.session_state.scan_log=[]; st.rerun()


# ═════════════════════════════════════════════
# AUTO SCAN LOOP
# ═════════════════════════════════════════════
if auto_scan and tickers:
    banner=t("auto_scanning").format(scan_interval)
    st.markdown(f"""<div class='conf-alert'>
        <span class='status-dot dot-conf'></span>{banner}</div>""",
        unsafe_allow_html=True)
    time.sleep(scan_interval)
    st.cache_data.clear()
    do_scan()
    st.rerun()
