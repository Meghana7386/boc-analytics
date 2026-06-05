"""
╔═══════════════════════════════════════════════════════════════╗
║  BOC PROCUREMENT ANALYTICS DASHBOARD                          ║
║  Bill-on-Chain | Senior Analyst Edition                       ║
║  Global Filtering System — All modules use filtered_df        ║
╚═══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="BOC Procurement Analytics",
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp { background: linear-gradient(135deg, #0F0F1A 0%, #1A1A2E 50%, #0F0F1A 100%); }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1A2E 0%, #16213E 100%);
    border-right: 1px solid rgba(108,92,231,0.3);
  }

  .kpi-card {
    background: linear-gradient(135deg, rgba(108,92,231,0.15) 0%, rgba(0,206,201,0.08) 100%);
    border: 1px solid rgba(108,92,231,0.4);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
  }
  .kpi-card:hover { border-color: rgba(108,92,231,0.8); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(108,92,231,0.2); }
  .kpi-label  { font-size: 0.72rem; font-weight: 600; color: #a29bfe; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 4px; }
  .kpi-value  { font-size: 1.75rem; font-weight: 800; color: #ffffff; line-height: 1; }
  .kpi-delta  { font-size: 0.75rem; font-weight: 500; margin-top: 6px; }
  .kpi-delta.pos { color: #00cec9; } .kpi-delta.neg { color: #ff7675; }

  .section-title {
    font-size: 1.1rem; font-weight: 700; color: #a29bfe;
    border-left: 3px solid #6c5ce7; padding-left: 10px;
    margin: 1.5rem 0 1rem 0; text-transform: uppercase; letter-spacing: 0.8px;
  }

  /* Active filter banner */
  .filter-banner {
    background: linear-gradient(135deg, rgba(0,206,201,0.1) 0%, rgba(108,92,231,0.1) 100%);
    border: 1px solid rgba(0,206,201,0.35);
    border-radius: 12px;
    padding: 0.75rem 1.2rem;
    margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  }
  .filter-tag {
    background: rgba(108,92,231,0.25);
    border: 1px solid rgba(108,92,231,0.5);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem; font-weight: 600; color: #a29bfe;
    display: inline-block;
  }
  .filter-count {
    background: rgba(0,206,201,0.2);
    border: 1px solid rgba(0,206,201,0.5);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem; font-weight: 700; color: #00cec9;
    display: inline-block; margin-left: auto;
  }

  .alert-high   { background: rgba(255,118,117,0.12); border: 1px solid rgba(255,118,117,0.4); border-radius:10px; padding:0.8rem 1rem; margin:0.4rem 0; }
  .alert-medium { background: rgba(253,203,110,0.12); border: 1px solid rgba(253,203,110,0.4); border-radius:10px; padding:0.8rem 1rem; margin:0.4rem 0; }
  .alert-low    { background: rgba(116,185,255,0.12); border: 1px solid rgba(116,185,255,0.4); border-radius:10px; padding:0.8rem 1rem; margin:0.4rem 0; }
  .alert-text   { font-size: 0.85rem; color: #e0e0e0; }
  .alert-type   { font-size: 0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:3px; }
  .alert-type.high   { color: #ff7675; }
  .alert-type.medium { color: #fdcb6e; }
  .alert-type.low    { color: #74b9ff; }

  .badge-preferred  { background: rgba(0,206,201,0.2); color:#00cec9; border:1px solid rgba(0,206,201,0.5); border-radius:6px; padding:2px 10px; font-size:0.72rem; font-weight:600; }
  .badge-good       { background: rgba(108,92,231,0.2); color:#a29bfe; border:1px solid rgba(108,92,231,0.5); border-radius:6px; padding:2px 10px; font-size:0.72rem; font-weight:600; }
  .badge-watchlist  { background: rgba(253,203,110,0.2); color:#fdcb6e; border:1px solid rgba(253,203,110,0.5); border-radius:6px; padding:2px 10px; font-size:0.72rem; font-weight:600; }
  .badge-risk       { background: rgba(255,118,117,0.2); color:#ff7675; border:1px solid rgba(255,118,117,0.5); border-radius:6px; padding:2px 10px; font-size:0.72rem; font-weight:600; }

  .stTabs [data-baseweb="tab-list"] { background: rgba(26,26,46,0.8); border-radius: 12px; padding: 4px; gap: 4px; }
  .stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 16px; color:#a29bfe; font-weight:500; }
  .stTabs [aria-selected="true"] { background: linear-gradient(135deg,#6c5ce7,#4ecdc4) !important; color:white !important; }

  hr { border: none; border-top: 1px solid rgba(108,92,231,0.2); margin: 1.5rem 0; }
  .dataframe { background: rgba(26,26,46,0.8) !important; }

  .logo-header {
    background: linear-gradient(135deg, rgba(108,92,231,0.2) 0%, rgba(0,206,201,0.1) 100%);
    border: 1px solid rgba(108,92,231,0.3); border-radius:16px; padding:1.5rem; text-align:center; margin-bottom:1.5rem;
  }
  .logo-title { font-size:1.6rem; font-weight:800; color:#fff; }
  .logo-sub   { font-size:0.75rem; color:#a29bfe; margin-top:4px; letter-spacing:1px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly template ────────────────────────────────────────────
PALETTE = ["#6c5ce7","#00cec9","#fd79a8","#fdcb6e","#74b9ff","#a29bfe","#55efc4","#e17055","#fab1a0","#81ecec"]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,26,46,0.6)",
    font=dict(family="Inter", color="#e0e0e0", size=12),
    title_font=dict(family="Inter", color="#ffffff", size=14),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(108,92,231,0.3)", borderwidth=1),
    xaxis=dict(gridcolor="rgba(108,92,231,0.15)", linecolor="rgba(108,92,231,0.3)", title=""),
    yaxis=dict(gridcolor="rgba(108,92,231,0.15)", linecolor="rgba(108,92,231,0.3)", title=""),
    colorway=PALETTE,
)

def T(fig):
    """Apply dark theme layout WITHOUT wiping chart-specific axis settings."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,26,46,0.6)",
        font=dict(family="Inter", color="#e0e0e0", size=12),
        title_font=dict(family="Inter", color="#ffffff", size=14),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    bordercolor="rgba(108,92,231,0.3)", borderwidth=1),
        colorway=PALETTE,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    # Apply grid/line colours to existing axes without overwriting type/title
    fig.update_xaxes(gridcolor="rgba(108,92,231,0.15)",
                     linecolor="rgba(108,92,231,0.3)")
    fig.update_yaxes(gridcolor="rgba(108,92,231,0.15)",
                     linecolor="rgba(108,92,231,0.3)")
    return fig


# ════════════════════════════════════════════════════════════════
# DATA LOADING  (cached — reads file once)
# ════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_raw_data():
    # Cache busted to pick up date cleaning fixes
    from data_parser import parse_boc_dump, get_data_quality_report
    import os
    
    # Use relative path for deployment compatibility
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, "bocdata 1")
    
    # Fallback to local path if relative doesn't exist (for local testing)
    if not os.path.exists(filepath):
        local_fallback = r"C:\Users\meghanar\Downloads\bocdata 1"
        if os.path.exists(local_fallback):
            filepath = local_fallback
            
    df = parse_boc_dump(filepath)
    report = get_data_quality_report(df)

    # ── Load user & bill tables to get userId per bill ────────
    user_df = pd.DataFrame()
    try:
        import re as _re
        with open(filepath, 'r', encoding='utf-8', errors='replace') as _f:
            content = _f.read()

        # ── user table ────────────────────────────────────────
        um = _re.search(
            r'COPY public\."user" \(([^)]+)\) FROM stdin;\n(.*?)\\\.', content, _re.DOTALL)
        if um:
            ucols = [c.strip().strip('"') for c in um.group(1).split(',')]
            urows = [r for r in um.group(2).strip().split('\n') if r.strip()]
            urecs = []
            for row in urows:
                flds = row.split('\t')
                if len(flds) >= len(ucols):
                    rec = {ucols[i]: (None if flds[i] == '\\N' else flds[i])
                           for i in range(len(ucols))}
                    urecs.append(rec)
            udf = pd.DataFrame(urecs)

        # ── bill table (has userId) ────────────────────────────
        bm = _re.search(
            r'COPY public\.bill \(([^)]+)\) FROM stdin;\n(.*?)\\\.', content, _re.DOTALL)
        if bm:
            bcols = [c.strip().strip('"') for c in bm.group(1).split(',')]
            brows = [r for r in bm.group(2).strip().split('\n') if r.strip()]
            brecs = []
            for row in brows:
                flds = row.split('\t')
                if len(flds) >= 2:
                    brecs.append({'bill_id': flds[0],
                                  'user_id': flds[1] if flds[1] != '\\N' else None})
            bdf = pd.DataFrame(brecs)

        # ── join: bill_extraction → bill → user ───────────────
        if not bdf.empty and not udf.empty:
            merged = df.merge(bdf[['bill_id', 'user_id']], on='bill_id', how='left')
            user_cols = ['id', 'email', 'name', 'rewardBalance', 'lifetimeRewardPoints',
                         'createdAt', 'role', 'didStatus']
            user_cols = [c for c in user_cols if c in udf.columns]
            udf_slim = udf[user_cols].rename(columns={
                'id': 'user_id', 'email': 'user_email', 'name': 'user_name',
                'rewardBalance': 'reward_balance', 'lifetimeRewardPoints': 'lifetime_points',
                'createdAt': 'user_created_at', 'role': 'user_role',
                'didStatus': 'did_status'
            })
            for num_col in ['reward_balance', 'lifetime_points']:
                if num_col in udf_slim.columns:
                    udf_slim[num_col] = pd.to_numeric(udf_slim[num_col], errors='coerce').fillna(0)
            df = merged.merge(udf_slim, on='user_id', how='left')
            user_df = udf_slim.copy()
    except Exception:
        pass  # user enrichment is best-effort; core df still works

    return df, report, user_df


# ════════════════════════════════════════════════════════════════
# GLOBAL FILTER FUNCTION
# ════════════════════════════════════════════════════════════════
def apply_filters(df_full, date_range, sel_currency, sel_cats, sel_vendor, sel_user="All"):
    """
    Central filter function.
    Returns filtered_df based on all sidebar selections incl. user.
    Stored in st.session_state['filtered_df'].
    """
    fdf = df_full.copy()

    # 1. Date range
    if date_range and len(date_range) == 2:
        start = pd.Timestamp(date_range[0])
        end   = pd.Timestamp(date_range[1])
        fdf = fdf[fdf["invoice_date"].isna() | ((fdf["invoice_date"] >= start) & (fdf["invoice_date"] <= end))]

    # 2. Currency
    if sel_currency != "All":
        fdf = fdf[fdf["currency"] == sel_currency]

    # 3. Category (multi)
    if sel_cats:
        fdf = fdf[fdf["category_display"].isin(sel_cats)]

    # 4. Vendor
    if sel_vendor != "All":
        fdf = fdf[fdf["merchant_name"] == sel_vendor]

    # 5. User
    if sel_user != "All" and "user_id" in fdf.columns:
        fdf = fdf[fdf["user_id"] == sel_user]

    st.session_state["filtered_df"] = fdf
    return fdf


# ════════════════════════════════════════════════════════════════
# ANALYTICS ENGINE  (no caching — always runs on filtered_df)
# ════════════════════════════════════════════════════════════════
def compute_analytics(filtered_df):
    from analytics_engine import (
        compute_spend_kpis, monthly_spend_trend, vendor_spend,
        category_spend, currency_spend, weekday_spend, spend_concentration,
        price_variance_analysis, vendor_price_comparison, savings_opportunity,
        cost_optimization_score, vendor_scorecard, category_inflation,
        vendor_price_trend, generate_alerts, spend_forecast,
        vendor_clustering, anomaly_detection
    )
    return {
        "kpis":           compute_spend_kpis(filtered_df),
        "monthly_trend":  monthly_spend_trend(filtered_df),
        "vendor_spend":   vendor_spend(filtered_df, 20),
        "cat_spend":      category_spend(filtered_df),
        "currency_spend": currency_spend(filtered_df),
        "weekday_spend":  weekday_spend(filtered_df),
        "concentration":  spend_concentration(filtered_df),
        "price_variance": price_variance_analysis(filtered_df),
        "vendor_compare": vendor_price_comparison(filtered_df),
        "savings":        savings_opportunity(filtered_df),
        "opt_score":      cost_optimization_score(filtered_df),
        "scorecard":      vendor_scorecard(filtered_df),
        "cat_inflation":  category_inflation(filtered_df),
        "vendor_trend":   vendor_price_trend(filtered_df),
        "alerts":         generate_alerts(filtered_df),
        "forecast":       spend_forecast(filtered_df, 6),
        "clusters":       vendor_clustering(filtered_df),
        "anomalies":      anomaly_detection(filtered_df),
    }


# ════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════
def fmt(val):
    if pd.isna(val): return "N/A"
    if abs(val) >= 1e9: return f"{val/1e9:.2f}B"
    if abs(val) >= 1e6: return f"{val/1e6:.2f}M"
    if abs(val) >= 1e3: return f"{val/1e3:.1f}K"
    return f"{val:,.0f}"

def kpi_card(label, value, delta=None, pos=True, icon="📊"):
    d = ""
    if delta is not None:
        cls = "pos" if pos else "neg"
        arrow = "▲" if pos else "▼"
        d = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'
    return f"""<div class="kpi-card">
      <div class="kpi-label">{icon} {label}</div>
      <div class="kpi-value">{value}</div>{d}
    </div>"""

def alert_html(a):
    s = a["severity"]
    return f"""<div class="alert-{s}">
      <div class="alert-type {s}">{a['icon']} {a['type']}</div>
      <div class="alert-text">{a['message']}</div>
    </div>"""

def filter_banner(sel_currency, sel_cats, sel_vendor, date_range, n_records):
    """Renders active filter summary bar at top of each tab."""
    tags = []
    if date_range and len(date_range) == 2:
        tags.append(f"📅 {date_range[0]} → {date_range[1]}")
    if sel_currency != "All":
        tags.append(f"💱 {sel_currency}")
    if sel_cats:
        tags.append("🏷️ " + ", ".join(sel_cats))
    if sel_vendor != "All":
        tags.append(f"🏪 {sel_vendor}")
    if not tags:
        tags.append("🌐 All Data")
    tags_html = "".join(f'<span class="filter-tag">{t}</span>' for t in tags)
    st.markdown(
        f'<div class="filter-banner">'
        f'<span style="font-size:0.78rem;color:#e0e0e0;font-weight:600;">Active Filters:</span> '
        f'{tags_html}'
        f'<span class="filter-count">📊 {n_records:,} records</span>'
        f'</div>',
        unsafe_allow_html=True
    )


# ════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ════════════════════════════════════════════════════════════════
def main():

    # ── Load raw data (cached) ────────────────────────────────
    with st.spinner("Loading dataset..."):
        df_full, dq_report, user_df = load_raw_data()

    # ── SIDEBAR ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="logo-header">
          <div class="logo-title">⛓️ BOC Analytics</div>
          <div class="logo-sub">BILL-ON-CHAIN | PROCUREMENT INTELLIGENCE</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 🔧 Filters")

        # 1. Date Range
        valid = df_full.dropna(subset=["invoice_date"])
        if not valid.empty:
            min_d = valid["invoice_date"].min().date()
            max_d = valid["invoice_date"].max().date()
            st.markdown("**📅 Date Range**")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From", value=min_d, min_value=min_d, max_value=max_d)
            with col2:
                end_date = st.date_input("To", value=max_d, min_value=min_d, max_value=max_d)
            
            date_range = (start_date, end_date)
        else:
            date_range = None

        # 2. Currency
        currencies = ["All"] + sorted(df_full["currency"].dropna().unique().tolist())
        sel_currency = st.selectbox("💱 Currency", currencies)

        # 3. Category (multi-select)
        all_cats = sorted(df_full["category_display"].dropna().unique().tolist())
        sel_cats = st.multiselect("🏷️ Categories", all_cats, default=[], placeholder="All categories")

        # 4. Vendor
        all_vendors = ["All"] + sorted(df_full["merchant_name"].dropna().unique().tolist())
        sel_vendor = st.selectbox("🏪 Vendor", all_vendors)

        # ── User Analytics Filter ─────────────────────────────
        st.markdown("---")
        st.markdown("### 👤 User Analytics")

        has_users = "user_id" in df_full.columns and "user_email" in df_full.columns
        sel_user = "All"
        sel_user_row = None

        if has_users:
            # Email text search
            email_query = st.text_input("🔍 Enter User Email", value="",
                                        placeholder="e.g. user@example.com")

            # Build user list for dropdown
            user_opts_df = df_full[["user_id", "user_email", "user_name"]].dropna(
                subset=["user_id", "user_email"]).drop_duplicates("user_id")

            # Filter by email search if entered
            if email_query.strip():
                mask = user_opts_df["user_email"].str.contains(
                    email_query.strip(), case=False, na=False)
                user_opts_df = user_opts_df[mask]

            user_labels = ["All"] + [
                f"{row['user_name'] or 'Unknown'} ({row['user_email']})"
                for _, row in user_opts_df.iterrows()
            ]
            user_ids    = ["All"] + user_opts_df["user_id"].tolist()

            chosen_label = st.selectbox("👤 Select User", user_labels)
            chosen_idx   = user_labels.index(chosen_label)
            sel_user     = user_ids[chosen_idx]

            if sel_user != "All":
                # Grab this user's full profile row
                sel_user_row = user_opts_df[user_opts_df["user_id"] == sel_user].iloc[0]
        else:
            st.caption("⚠️ User data not available in this dataset.")

        st.markdown("---")

        # ── APPLY GLOBAL FILTERS (incl. user) ─────────────────
        filtered_df = apply_filters(df_full, date_range, sel_currency, sel_cats,
                                    sel_vendor, sel_user)

        # Sidebar summary (reflects filtered data)
        st.markdown("### 📊 Filtered Summary")
        st.metric("Records",        f"{len(filtered_df):,}")
        st.metric("Unique Vendors",  f"{filtered_df['merchant_name'].nunique():,}")
        st.metric("Currencies",      f"{filtered_df['currency'].nunique()}")
        if not filtered_df.dropna(subset=["invoice_date"]).empty:
            d0 = filtered_df["invoice_date"].min().strftime("%Y-%m-%d")
            d1 = filtered_df["invoice_date"].max().strftime("%Y-%m-%d")
            st.metric("Date Range", f"{d0} → {d1}")

        st.markdown("---")
        st.caption("🤖 Powered by Antigravity IDE · BOC Analytics v2.0")

    # ── GUARD — empty filter result ───────────────────────────
    if filtered_df.empty:
        st.warning("⚠️ No records match the selected filters. Please broaden your selection.")
        return

    # ── COMPUTE ALL ANALYTICS on filtered_df ─────────────────
    with st.spinner("🔄 Computing analytics on filtered data..."):
        ana = compute_analytics(filtered_df)

    # ════════════════════════════════════════════════════════════
    # TABS
    # ════════════════════════════════════════════════════════════
    tabs = st.tabs([
        "🏠 Executive Dashboard",
        "📈 Spend Analytics",
        "💰 Cost Optimization",
        "🏪 Vendor Analytics",
        "📉 Market Trends",
        "🔮 Forecasting",
        "🚨 Anomaly Detection",
        "👤 User Analytics",
        "🌍 Region Analytics",
    ])

    # ──────────────────────────────────────────────────────────
    # TAB 1 — EXECUTIVE DASHBOARD
    # ──────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("## 🏠 Executive Dashboard")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        # ── KPIs directly from filtered_df ─────────────────
        fdf = filtered_df   # alias for brevity
        ts   = fdf["total_amount"].sum()
        ai   = fdf["total_amount"].mean()
        med  = fdf["total_amount"].median()
        ni   = len(fdf)
        nv   = fdf["merchant_name"].nunique()
        nc   = fdf["category_display"].nunique()
        ncur = fdf["currency"].nunique()

        mth  = fdf.dropna(subset=["invoice_date"]).set_index("invoice_date").resample("ME")["total_amount"].sum()
        mom  = ((mth.iloc[-1] - mth.iloc[-2]) / mth.iloc[-2] * 100) if len(mth) >= 2 and mth.iloc[-2] > 0 else 0.0

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        with c1: st.markdown(kpi_card("Total Spend",    fmt(ts),        icon="💸"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("Avg Invoice",    fmt(ai),        icon="🧾"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("Total Invoices", f"{ni:,}",      icon="📋"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_card("Unique Vendors", f"{nv:,}",      icon="🏪"), unsafe_allow_html=True)
        with c5: st.markdown(kpi_card("Categories",     f"{nc}",        icon="🏷️"), unsafe_allow_html=True)
        with c6: st.markdown(kpi_card("MoM Growth",     f"{mom:+.1f}%",
                                       delta=f"{abs(mom):.1f}% vs prev month", pos=mom>=0, icon="📊"), unsafe_allow_html=True)

        st.markdown("---")

        # ── Monthly Spend Trend ───────────────────────────────
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown('<div class="section-title">📈 Monthly Spend Trend</div>', unsafe_allow_html=True)
            _mt = fdf.dropna(subset=["invoice_date","total_amount"]).copy()

            # Filter out date outliers (keep 98th-percentile window ± 3 yrs)
            if not _mt.empty:
                _max_d = _mt["invoice_date"].quantile(0.98)
                _min_d = _max_d - pd.DateOffset(years=3)
                _mt = _mt[(_mt["invoice_date"] >= _min_d) & (_mt["invoice_date"] <= _max_d)]

            _mt["month"]      = _mt["invoice_date"].dt.strftime("%b %Y")
            _mt["month_sort"] = _mt["invoice_date"].dt.to_period("M").astype(str)
            _mtg = _mt.groupby(["month","month_sort"]).agg(
                total_spend=("total_amount","sum"),
                invoice_count=("bill_id","count"),
            ).reset_index().sort_values("month_sort")

            if not _mtg.empty:
                # Max 12 evenly-spaced tick labels
                _all_months = _mtg["month"].tolist()
                _step       = max(1, len(_all_months) // 12)
                _tick_vals  = _all_months[::_step]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=_mtg["month"], y=_mtg["total_spend"], mode="lines+markers",
                    name="Total Spend", line=dict(color="#6c5ce7", width=3),
                    marker=dict(size=7, color="#6c5ce7"),
                    fill="tozeroy", fillcolor="rgba(108,92,231,0.15)"
                ))
                fig.add_trace(go.Bar(
                    x=_mtg["month"], y=_mtg["invoice_count"],
                    name="Invoice Count", yaxis="y2",
                    marker_color="rgba(0,206,201,0.4)"
                ))
                T(fig)
                fig.update_layout(
                    xaxis=dict(
                        type="category",
                        title="",
                        tickmode="array",
                        tickvals=_tick_vals,
                        tickangle=-60,
                        tickfont=dict(size=10),
                        categoryorder="array",
                        categoryarray=_all_months,
                    ),
                    yaxis=dict(title="Total Spend"),
                    yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Invoice Count"),
                    height=340, showlegend=True,
                    margin=dict(b=80, l=20, r=20, t=40),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No date data available for trend chart.")

        with col_right:
            st.markdown('<div class="section-title">🏷️ Spend by Category</div>', unsafe_allow_html=True)
            _cat = fdf.groupby("category_display")["total_amount"].sum().reset_index()
            _cat.columns = ["category_display","total_spend"]
            _cat = _cat.sort_values("total_spend", ascending=False)
            if not _cat.empty:
                fig = px.pie(_cat, values="total_spend", names="category_display",
                             color_discrete_sequence=PALETTE, hole=0.55)
                fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
                fig.update_layout(height=320, showlegend=False)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        # ── Bottom Row ────────────────────────────────────────
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown('<div class="section-title">🏆 Top 10 Vendors</div>', unsafe_allow_html=True)
            _vs = fdf.groupby("merchant_name").agg(
                total_spend=("total_amount","sum"),
                invoice_count=("bill_id","count"),
            ).reset_index().sort_values("total_spend", ascending=False).head(10)
            if not _vs.empty:
                fig = px.bar(_vs, x="total_spend", y="merchant_name", orientation="h",
                             color="total_spend", color_continuous_scale=["#6c5ce7","#00cec9"],
                             text="invoice_count")
                fig.update_traces(texttemplate="%{text} inv", textposition="inside")
                fig.update_layout(height=320, yaxis=dict(title="", autorange="reversed"),
                                  showlegend=False, coloraxis_showscale=False)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-title">💱 Currency Distribution</div>', unsafe_allow_html=True)
            _cur = fdf.groupby("currency").agg(
                total_spend=("total_amount","sum"),
                invoice_count=("bill_id","count"),
            ).reset_index().sort_values("total_spend", ascending=False).head(12)
            if not _cur.empty:
                fig = px.bar(_cur, x="currency", y="total_spend",
                             color="total_spend", color_continuous_scale=["#a29bfe","#6c5ce7"],
                             text="invoice_count")
                fig.update_traces(texttemplate="%{text}", textposition="outside")
                fig.update_layout(height=320, showlegend=False, coloraxis_showscale=False)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        with col_c:
            st.markdown('<div class="section-title">🎯 Optimization Score</div>', unsafe_allow_html=True)
            score = ana["opt_score"]["total_score"]
            grade = ana["opt_score"]["grade"]
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                domain={"x":[0,1],"y":[0,1]},
                number={"suffix":"/100","font":{"color":"#fff","size":28}},
                gauge={
                    "axis":{"range":[0,100],"tickcolor":"#a29bfe"},
                    "bar":{"color":"#6c5ce7"},
                    "steps":[
                        {"range":[0,40],"color":"rgba(255,118,117,0.3)"},
                        {"range":[40,70],"color":"rgba(253,203,110,0.3)"},
                        {"range":[70,100],"color":"rgba(0,206,201,0.3)"},
                    ],
                    "threshold":{"line":{"color":"#00cec9","width":3},"value":70}
                },
                title={"text":f"Grade: <b>{grade}</b>","font":{"color":"#a29bfe","size":14}}
            ))
            fig.update_layout(height=320)
            T(fig); st.plotly_chart(fig, use_container_width=True)

        # ── Alerts ───────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="section-title">🚨 Live Procurement Alerts</div>', unsafe_allow_html=True)
        _alerts = ana["alerts"]
        if _alerts:
            cols = st.columns(min(3, len(_alerts)))
            for i, a in enumerate(_alerts[:6]):
                with cols[i % len(cols)]:
                    st.markdown(alert_html(a), unsafe_allow_html=True)
        else:
            st.success("✅ No critical alerts detected.")

    # ──────────────────────────────────────────────────────────
    # TAB 2 — SPEND ANALYTICS
    # ──────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("## 📈 Spend Analytics")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        fdf = filtered_df
        ts   = fdf["total_amount"].sum()
        ai   = fdf["total_amount"].mean()
        med  = fdf["total_amount"].median()
        mth  = fdf.dropna(subset=["invoice_date"]).set_index("invoice_date").resample("ME")["total_amount"].sum()
        mom  = ((mth.iloc[-1]-mth.iloc[-2])/mth.iloc[-2]*100) if len(mth)>=2 and mth.iloc[-2]>0 else 0.0

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(kpi_card("Total Spend",    fmt(ts),        icon="💸"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("Avg Invoice",    fmt(ai),        icon="🧾"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("Median Invoice", fmt(med),       icon="📊"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_card("Spend Growth",   f"{mom:+.1f}%", pos=mom>=0, icon="📈"), unsafe_allow_html=True)

        st.markdown("---")

        # Monthly Trend (dual-axis) — in Spend Analytics tab
        st.markdown('<div class="section-title">📅 Monthly Spend Trend</div>', unsafe_allow_html=True)
        mt = ana["monthly_trend"].copy()
        if not mt.empty:
            # Re-format month label from "2026-05" → "May 2026"
            try:
                mt["month_label"] = pd.to_datetime(mt["month"]).dt.strftime("%b %Y")
                mt["month_sort"]  = mt["month"]  # original YYYY-MM for sorting
            except Exception:
                mt["month_label"] = mt["month"]
                mt["month_sort"]  = mt["month"]

            # Filter out date outliers (keep 98th-percentile window ± 3 yrs)
            try:
                mt["_dt"] = pd.to_datetime(mt["month"], errors="coerce")
                _max_d = mt["_dt"].quantile(0.98)
                _min_d = _max_d - pd.DateOffset(years=3)
                mt = mt[(mt["_dt"] >= _min_d) & (mt["_dt"] <= _max_d)]
                mt = mt.drop(columns=["_dt"])
            except Exception:
                pass

            mt = mt.sort_values("month_sort")

            if not mt.empty:
                _all_months = mt["month_label"].tolist()
                _step       = max(1, len(_all_months) // 12)
                _tick_vals  = _all_months[::_step]

                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Scatter(
                    x=mt["month_label"], y=mt["total_spend"], name="Total Spend",
                    line=dict(color="#6c5ce7", width=2.5),
                    fill="tozeroy", fillcolor="rgba(108,92,231,0.1)",
                    mode="lines+markers", marker=dict(size=6)),
                    secondary_y=False)
                fig.add_trace(go.Scatter(
                    x=mt["month_label"], y=mt["avg_invoice"], name="Avg Invoice",
                    line=dict(color="#00cec9", width=2, dash="dot"), mode="lines"),
                    secondary_y=True)
                T(fig)
                fig.update_layout(
                    xaxis=dict(
                        type="category",
                        title="",
                        tickmode="array",
                        tickvals=_tick_vals,
                        tickangle=-60,
                        tickfont=dict(size=10),
                        categoryorder="array",
                        categoryarray=_all_months,
                    ),
                    yaxis=dict(title="Total Spend"),
                    height=350, hovermode="x unified",
                    margin=dict(b=80, l=20, r=20, t=40),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date data available.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">🏷️ Category-wise Spend</div>', unsafe_allow_html=True)
            cat_df = ana["cat_spend"]
            if not cat_df.empty:
                fig = px.bar(cat_df, x="category_display", y="total_spend",
                             color="category_display", color_discrete_sequence=PALETTE,
                             text="spend_pct")
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig.update_layout(height=350, showlegend=False, xaxis_tickangle=-30,
                                  xaxis_title="", yaxis_title="Total Spend")
                T(fig); st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">🗺️ Vendor Spend Treemap</div>', unsafe_allow_html=True)
            vs = ana["vendor_spend"].head(30)
            if not vs.empty:
                fig = px.treemap(vs, path=["merchant_name"], values="total_spend",
                                 color="total_spend",
                                 color_continuous_scale=["#1a1a2e","#6c5ce7","#00cec9"])
                fig.update_layout(height=350)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="section-title">📆 Spend by Day of Week</div>', unsafe_allow_html=True)
            wd = ana["weekday_spend"]
            if not wd.empty:
                fig = px.bar_polar(wd, r="total_spend", theta="invoice_weekday",
                                   color="total_spend", color_discrete_sequence=PALETTE,
                                   template="plotly_dark")
                fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)",
                                  polar=dict(bgcolor="rgba(26,26,46,0.6)"))
                st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.markdown('<div class="section-title">🎯 Spend Concentration (Pareto)</div>', unsafe_allow_html=True)
            conc = ana["concentration"]
            vs_full = fdf.groupby("merchant_name")["total_amount"].sum().sort_values(ascending=False)
            vs_cum  = (vs_full.cumsum() / vs_full.sum() * 100).reset_index()
            vs_cum.columns = ["vendor","cumulative_pct"]
            vs_cum["vendor_rank"] = range(1, len(vs_cum)+1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=vs_cum["vendor_rank"], y=vs_cum["cumulative_pct"],
                fill="tozeroy", mode="lines", line=dict(color="#6c5ce7",width=2.5),
                fillcolor="rgba(108,92,231,0.15)", name="Cumulative %"))
            fig.add_hline(y=80, line_dash="dash", line_color="#fdcb6e",
                          annotation_text="80% threshold", annotation_font_color="#fdcb6e")
            fig.update_layout(height=350, xaxis_title="Vendor Rank", yaxis_title="Cumulative Spend %")
            T(fig); st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            > **Concentration:** {conc['pct_vendors_80']:.1f}% of vendors drive 80% of spend
            > · Top 5 = **{conc['top5_concentration']}%**
            > · HHI = **{conc['hhi']:,.0f}** ({"High" if conc['hhi']>2500 else "Moderate" if conc['hhi']>1500 else "Low"})
            """)

        st.markdown("---")
        st.markdown('<div class="section-title">📊 Category Performance Table</div>', unsafe_allow_html=True)
        if not cat_df.empty:
            disp = cat_df[["category_display","total_spend","invoice_count","avg_invoice","vendor_count","spend_pct"]].copy()
            disp.columns = ["Category","Total Spend","Invoices","Avg Invoice","Vendors","Spend %"]
            disp["Total Spend"] = disp["Total Spend"].apply(fmt)
            disp["Avg Invoice"] = disp["Avg Invoice"].apply(fmt)
            disp["Spend %"]     = disp["Spend %"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(disp, use_container_width=True, hide_index=True)

    # ──────────────────────────────────────────────────────────
    # TAB 3 — COST OPTIMIZATION
    # ──────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("## 💰 Cost Optimization")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        opt        = ana["opt_score"]
        savings_df = ana["savings"]
        pv_df      = ana["price_variance"]
        vc_df      = ana["vendor_compare"]

        overpriced_n  = (pv_df["status"] == "Overpriced").sum()  if not pv_df.empty else 0
        total_savings = savings_df["potential_savings"].sum()     if not savings_df.empty else 0

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(kpi_card("Optimization Score", f"{opt['total_score']}/100", icon="🎯"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("Grade",              opt["grade"],                icon="🏆"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("Potential Savings",  fmt(total_savings),          icon="💰"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_card("Overpriced Vendors", f"{overpriced_n}",           icon="⚠️"), unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns([3,2])

        with col1:
            st.markdown('<div class="section-title">📊 Price Variance Analysis</div>', unsafe_allow_html=True)
            if not pv_df.empty:
                fig = px.scatter(pv_df.head(20),
                    x="price_variance_pct", y="vendor_total_spend",
                    color="status", size="invoice_count",
                    color_discrete_map={"Overpriced":"#ff7675","Underpriced":"#00cec9","Fair":"#6c5ce7"},
                    hover_data=["merchant_name","category_display","vendor_avg_price","category_avg_price"],
                    labels={"price_variance_pct":"Variance %","vendor_total_spend":"Total Spend"})
                fig.add_vline(x=20,  line_dash="dash", line_color="#ff7675", annotation_text="Overpriced")
                fig.add_vline(x=-20, line_dash="dash", line_color="#00cec9", annotation_text="Underpriced")
                fig.update_layout(height=350)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">🎯 Score Breakdown</div>', unsafe_allow_html=True)
            breakdown = opt["breakdown"]
            lbl = {"price_variance":"Price Variance","spend_concentration":"Concentration",
                   "vendor_dependency":"Vendor Diversity","savings_potential":"Savings Potential"}
            sdf = pd.DataFrame({
                "factor": [lbl.get(k,k) for k in breakdown],
                "score":  list(breakdown.values()),
                "max":    [30,25,25,20],
            })
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sdf["factor"], y=sdf["max"],   name="Max",      marker_color="rgba(108,92,231,0.2)"))
            fig.add_trace(go.Bar(x=sdf["factor"], y=sdf["score"], name="Achieved", marker_color="#6c5ce7"))
            fig.update_layout(barmode="overlay", height=350, xaxis_tickangle=-20)
            T(fig); st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="section-title">💡 Top Savings Opportunities</div>', unsafe_allow_html=True)
            if not savings_df.empty:
                fig = px.bar(savings_df.head(15), x="potential_savings", y="merchant_name",
                             orientation="h", color="savings_pct",
                             color_continuous_scale=["#6c5ce7","#fdcb6e","#ff7675"],
                             hover_data=["category_display","avg_price","min_vendor_avg_price"])
                fig.update_layout(height=380, yaxis=dict(title="", autorange="reversed"),
                                  coloraxis_colorbar=dict(title="Savings %"))
                T(fig); st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.markdown('<div class="section-title">🔀 Vendor Price Comparison by Category</div>', unsafe_allow_html=True)
            if not vc_df.empty:
                top_cats = vc_df.groupby("category_display")["invoice_count"].sum().nlargest(6).index
                vc_top = vc_df[vc_df["category_display"].isin(top_cats)]
                fig = px.box(vc_top, x="category_display", y="avg_price",
                             color="category_display", color_discrete_sequence=PALETTE,
                             points="all", hover_data=["merchant_name"])
                fig.update_layout(height=380, showlegend=False,
                                  xaxis_tickangle=-25, xaxis_title="", yaxis_title="Avg Price")
                T(fig); st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-title">🕳️ Cost Leakage — Overpriced Vendors</div>', unsafe_allow_html=True)
        if not pv_df.empty:
            overpriced = pv_df[pv_df["status"]=="Overpriced"].head(20).copy()
            if not overpriced.empty:
                overpriced["Potential Leakage"] = (
                    overpriced["price_variance_pct"] / 100 * overpriced["vendor_total_spend"]
                ).apply(fmt)
                disp = overpriced[["merchant_name","category_display","vendor_avg_price",
                                   "category_avg_price","price_variance_pct","invoice_count","Potential Leakage"]].copy()
                disp.columns = ["Vendor","Category","Vendor Avg","Category Avg","Variance %","Invoices","Leakage"]
                disp["Vendor Avg"]   = disp["Vendor Avg"].apply(lambda x: f"{x:,.0f}")
                disp["Category Avg"] = disp["Category Avg"].apply(lambda x: f"{x:,.0f}")
                disp["Variance %"]   = disp["Variance %"].apply(lambda x: f"🔴 +{x:.1f}%")
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No significantly overpriced vendors detected.")

    # ──────────────────────────────────────────────────────────
    # TAB 4 — VENDOR ANALYTICS
    # ──────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("## 🏪 Vendor Analytics")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        scorecard = ana["scorecard"]
        class_counts = scorecard["classification"].value_counts()

        c1,c2,c3,c4 = st.columns(4)
        for col, (cls, icon) in zip([c1,c2,c3,c4], [
            ("Preferred Vendor","🥇"),("Good Vendor","✅"),
            ("Watchlist Vendor","⚠️"),("High Risk Vendor","🚨")
        ]):
            with col:
                st.markdown(kpi_card(cls, str(class_counts.get(cls,0)), icon=icon), unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns([2,1])

        with col1:
            st.markdown('<div class="section-title">📊 Vendor Score Distribution</div>', unsafe_allow_html=True)
            fig = px.histogram(scorecard, x="vendor_score", nbins=20, color="classification",
                               color_discrete_map={
                                   "Preferred Vendor":"#00cec9","Good Vendor":"#a29bfe",
                                   "Watchlist Vendor":"#fdcb6e","High Risk Vendor":"#ff7675"},
                               barmode="overlay")
            fig.add_vline(x=70, line_dash="dash", line_color="#00cec9", annotation_text="Preferred")
            fig.add_vline(x=50, line_dash="dash", line_color="#a29bfe", annotation_text="Good")
            fig.add_vline(x=30, line_dash="dash", line_color="#fdcb6e", annotation_text="Watchlist")
            fig.update_layout(height=340)
            T(fig); st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">🍩 Classification Mix</div>', unsafe_allow_html=True)
            cls_df = pd.DataFrame(class_counts).reset_index()
            cls_df.columns = ["Class","Count"]
            fig = px.pie(cls_df, values="Count", names="Class", hole=0.6,
                         color_discrete_map={
                             "Preferred Vendor":"#00cec9","Good Vendor":"#a29bfe",
                             "Watchlist Vendor":"#fdcb6e","High Risk Vendor":"#ff7675"})
            fig.update_traces(textinfo="percent+label", textfont_size=11)
            fig.update_layout(height=340, showlegend=False)
            T(fig); st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-title">🔥 Vendor Performance Heatmap (Top 30)</div>', unsafe_allow_html=True)
        top30 = scorecard.head(30)[["merchant_name","price_competitiveness",
                                     "spend_consistency","invoice_accuracy","purchase_frequency"]].copy()
        top30 = top30.set_index("merchant_name")
        hd = top30.values
        fig = go.Figure(go.Heatmap(
            z=hd,
            x=["Price Competitiveness","Spend Consistency","Invoice Accuracy","Purchase Frequency"],
            y=top30.index.tolist(),
            colorscale=[[0,"#1a1a2e"],[0.5,"#6c5ce7"],[1,"#00cec9"]],
            text=hd.round(1), texttemplate="%{text}", textfont={"size":10},
        ))
        fig.update_layout(height=max(400, len(top30)*18), xaxis=dict(side="top"),
                          yaxis=dict(autorange="reversed"))
        T(fig); st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-title">📋 Full Vendor Scorecard</div>', unsafe_allow_html=True)
        sd = scorecard[["merchant_name","vendor_score","classification","total_spend",
                         "invoice_count","avg_invoice","categories",
                         "price_competitiveness","spend_consistency"]].head(50).copy()
        sd["total_spend"] = sd["total_spend"].apply(fmt)
        sd["avg_invoice"] = sd["avg_invoice"].apply(fmt)
        sd["classification"] = sd["classification"].apply(
            lambda x: f"{'🥇' if x=='Preferred Vendor' else '✅' if x=='Good Vendor' else '⚠️' if x=='Watchlist Vendor' else '🚨'} {x}")
        sd.columns = ["Vendor","Score","Classification","Total Spend",
                      "Invoices","Avg Invoice","Categories","Price Score","Consistency"]
        st.dataframe(sd, use_container_width=True, hide_index=True)

    # ──────────────────────────────────────────────────────────
    # TAB 5 — MARKET TRENDS
    # ──────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("## 📉 Market Trend Analysis")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        cat_inf = ana["cat_inflation"]
        vt      = ana["vendor_trend"]
        alerts  = ana["alerts"]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">📈 Category Price Inflation</div>', unsafe_allow_html=True)
            if not cat_inf.empty:
                top_cats = cat_inf.groupby("category_display")["invoice_count"].sum().nlargest(6).index
                ci_top   = cat_inf[cat_inf["category_display"].isin(top_cats)].dropna(subset=["inflation_pct"]).copy()

                if not ci_top.empty:
                    # Sort months chronologically (YYYY-MM strings sort correctly)
                    _months = sorted(ci_top["month"].unique())
                    # Show max 12 evenly-spaced tick labels to avoid overlap
                    _step   = max(1, len(_months) // 12)
                    _ticks  = _months[::_step]

                    fig = px.line(ci_top, x="month", y="inflation_pct",
                                  color="category_display", color_discrete_sequence=PALETTE,
                                  markers=True, line_shape="spline",
                                  category_orders={"month": _months},
                                  labels={"inflation_pct":"MoM Inflation %","month":"",
                                          "category_display":"Category"})
                    fig.add_hline(y=0, line_color="rgba(255,255,255,0.3)", line_dash="dash")
                    T(fig)
                    fig.update_layout(
                        xaxis=dict(
                            type="category",
                            title="",
                            tickmode="array",
                            tickvals=_ticks,
                            tickangle=-60,
                            tickfont=dict(size=10),
                            categoryorder="array",
                            categoryarray=_months,
                        ),
                        yaxis=dict(title="MoM Inflation %"),
                        height=370, hovermode="x unified",
                        margin=dict(b=85, l=20, r=20, t=40),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Insufficient data for inflation chart.")
            else:
                st.info("Insufficient data for inflation chart.")

        with col2:
            st.markdown('<div class="section-title">🏪 Vendor Price Trends</div>', unsafe_allow_html=True)
            if not vt.empty:
                top_v  = vt["merchant_name"].unique()[:6]
                vt_top = vt[vt["merchant_name"].isin(top_v)].dropna(subset=["avg_price"])
                fig = px.line(vt_top, x="month", y="avg_price",
                              color="merchant_name", color_discrete_sequence=PALETTE,
                              markers=True, line_shape="spline")
                fig.update_layout(height=370, hovermode="x unified")
                T(fig); st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for vendor trend chart.")

        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="section-title">🌡️ Category Inflation Heatmap</div>', unsafe_allow_html=True)
            if not cat_inf.empty:
                pivot = cat_inf.pivot_table(index="category_display", columns="month",
                                            values="inflation_pct", aggfunc="mean").fillna(0).round(1)
                pivot = pivot.iloc[:, -12:]
                fig = go.Figure(go.Heatmap(
                    z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                    colorscale=[[0,"#ff7675"],[0.5,"#1a1a2e"],[1,"#00cec9"]],
                    text=pivot.values.round(1), texttemplate="%{text}%",
                    textfont={"size":10}, zmid=0,
                ))
                fig.update_layout(height=300, xaxis_tickangle=-40)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.markdown('<div class="section-title">🔝 Highest Inflation Categories</div>', unsafe_allow_html=True)
            if not cat_inf.empty:
                avg_inf = cat_inf.dropna(subset=["inflation_pct"]).groupby(
                    "category_display")["inflation_pct"].mean().sort_values(ascending=False)
                fig = px.bar(avg_inf.reset_index(), x="category_display", y="inflation_pct",
                             color="inflation_pct",
                             color_continuous_scale=["#00cec9","#fdcb6e","#ff7675"])
                fig.update_layout(height=300, xaxis_tickangle=-30, xaxis_title="",
                                  coloraxis_showscale=False)
                T(fig); st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-title">🚨 All Market Alerts</div>', unsafe_allow_html=True)
        if alerts:
            for a in alerts:
                st.markdown(alert_html(a), unsafe_allow_html=True)
        else:
            st.success("✅ No active market alerts.")

    # ──────────────────────────────────────────────────────────
    # TAB 6 — FORECASTING
    # ──────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("## 🔮 Spend Forecasting & Vendor Clustering")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        forecast_df = ana["forecast"]
        clusters_df = ana["clusters"]

        if not forecast_df.empty:
            st.markdown('<div class="section-title">📊 Spend Forecast — Next 6 Months</div>', unsafe_allow_html=True)
            hist  = forecast_df[~forecast_df["is_forecast"]].copy()
            fcast = forecast_df[ forecast_df["is_forecast"]].copy()

            c1,c2,c3 = st.columns(3)
            if len(fcast) >= 3:
                with c1: st.markdown(kpi_card("Next Month",      fmt(fcast["ensemble_forecast"].iloc[0]),       icon="📅"), unsafe_allow_html=True)
                with c2: st.markdown(kpi_card("3-Month Forecast", fmt(fcast["ensemble_forecast"].iloc[:3].sum()), icon="📆"), unsafe_allow_html=True)
                with c3: st.markdown(kpi_card("6-Month Forecast", fmt(fcast["ensemble_forecast"].sum()),          icon="🗓️"), unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist["date"],  y=hist["spend"],
                name="Historical", mode="lines+markers",
                line=dict(color="#6c5ce7",width=2.5), marker=dict(size=6)))
            fig.add_trace(go.Scatter(x=fcast["date"], y=fcast["linear_forecast"],
                name="Linear Trend", mode="lines+markers",
                line=dict(color="#fdcb6e",width=1.5,dash="dot"),
                marker=dict(size=5,symbol="diamond")))
            fig.add_trace(go.Scatter(x=fcast["date"], y=fcast["ema_forecast"],
                name="EMA Smoothed", mode="lines+markers",
                line=dict(color="#74b9ff",width=1.5,dash="dash"),
                marker=dict(size=5,symbol="triangle-up")))
            fig.add_trace(go.Scatter(x=fcast["date"], y=fcast["ensemble_forecast"],
                name="Ensemble ✓", mode="lines+markers",
                line=dict(color="#00cec9",width=3), marker=dict(size=8),
                fill="tozeroy", fillcolor="rgba(0,206,201,0.08)"))
            fig.add_trace(go.Scatter(
                x=list(fcast["date"])+list(fcast["date"])[::-1],
                y=list(fcast["ensemble_forecast"]*1.15)+list(fcast["ensemble_forecast"]*0.85)[::-1],
                fill="toself", fillcolor="rgba(0,206,201,0.08)",
                line=dict(color="rgba(255,255,255,0)"), name="±15% Band"))
            if not hist.empty and not fcast.empty:
                fig.add_vline(x=hist["date"].max(), line_dash="dash",
                              line_color="rgba(255,255,255,0.3)",
                              annotation_text="Forecast begins",
                              annotation_font_color="#a29bfe")
            fig.update_layout(height=420, hovermode="x unified")
            T(fig); st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Insufficient data for forecasting (need ≥ 3 months).")

        st.markdown("---")
        st.markdown('<div class="section-title">🔮 Vendor Clustering (K-Means)</div>', unsafe_allow_html=True)
        if not clusters_df.empty:
            cluster_counts = clusters_df["cluster_name"].value_counts()
            icons = {"Strategic Vendor":"🏆","Preferred Vendor":"⭐","Occasional Vendor":"🔵","Risk Vendor":"🚨","Other":"⚪"}
            c1,c2,c3,c4 = st.columns(4)
            for i,(name,count) in enumerate(cluster_counts.items()):
                if i < 4:
                    with [c1,c2,c3,c4][i]:
                        st.markdown(kpi_card(name, str(count), icon=icons.get(name,"📊")), unsafe_allow_html=True)

            col1, col2 = st.columns([3,2])
            with col1:
                fig = px.scatter(clusters_df, x="total_spend", y="invoice_count",
                    color="cluster_name", size="avg_invoice",
                    hover_data=["merchant_name","avg_invoice","categories"],
                    color_discrete_map={
                        "Strategic Vendor":"#fdcb6e","Preferred Vendor":"#00cec9",
                        "Occasional Vendor":"#6c5ce7","Risk Vendor":"#ff7675","Other":"#a29bfe"},
                    log_x=True, log_y=True,
                    labels={"total_spend":"Total Spend (log)","invoice_count":"Invoice Count (log)"})
                fig.update_layout(height=400)
                T(fig); st.plotly_chart(fig, use_container_width=True)

            with col2:
                cs = clusters_df.groupby("cluster_name").agg(
                    vendors=("merchant_name","count"),
                    total_spend=("total_spend","sum"),
                    avg_spend=("total_spend","mean"),
                    avg_invoices=("invoice_count","mean"),
                ).reset_index().sort_values("total_spend",ascending=False)
                cs["total_spend"]  = cs["total_spend"].apply(fmt)
                cs["avg_spend"]    = cs["avg_spend"].apply(fmt)
                cs["avg_invoices"] = cs["avg_invoices"].apply(lambda x: f"{x:.1f}")
                cs.columns = ["Cluster","Vendors","Total Spend","Avg Spend","Avg Invoices"]
                st.dataframe(cs, use_container_width=True, hide_index=True)

    # ──────────────────────────────────────────────────────────
    # TAB 7 — ANOMALY DETECTION
    # ──────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown("## 🚨 Anomaly Detection")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))
        st.markdown("*Using **Isolation Forest** on filtered data — anomalies are detected only within the selected scope.*")

        adf = ana["anomalies"]

        if not adf.empty and "is_anomaly" in adf.columns:
            n_anom     = int(adf["is_anomaly"].sum())
            anom_pct   = n_anom / len(adf) * 100
            anom_spend = adf[adf["is_anomaly"]]["total_amount"].sum()
            n_normal   = len(adf) - n_anom

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(kpi_card("Anomalous Invoices", f"{n_anom:,}",       icon="🚨"), unsafe_allow_html=True)
            with c2: st.markdown(kpi_card("Anomaly Rate",        f"{anom_pct:.1f}%", icon="📊"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("Anomalous Spend",     fmt(anom_spend),    icon="💸"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_card("Normal Invoices",     f"{n_normal:,}",    icon="✅"), unsafe_allow_html=True)

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="section-title">🔍 Anomaly Score Distribution</div>', unsafe_allow_html=True)
                fig = px.histogram(adf, x="anomaly_score", color="is_anomaly",
                                   color_discrete_map={True:"#ff7675",False:"#6c5ce7"},
                                   nbins=40, barmode="overlay",
                                   labels={"anomaly_score":"Isolation Forest Score","is_anomaly":"Is Anomaly"})
                fig.add_vline(x=0, line_dash="dash", line_color="#fdcb6e",
                              annotation_text="Anomaly Threshold")
                fig.update_layout(height=360)
                T(fig); st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown('<div class="section-title">💥 Anomalous vs Normal Spend</div>', unsafe_allow_html=True)
                plot_df = adf.dropna(subset=["total_amount","line_items_count"]).copy()
                plot_df["invoice_type"] = plot_df["is_anomaly"].map({True:"🚨 Anomaly",False:"✅ Normal"})
                fig = px.scatter(plot_df, x="line_items_count", y="total_amount",
                                 color="invoice_type",
                                 color_discrete_map={"🚨 Anomaly":"#ff7675","✅ Normal":"rgba(108,92,231,0.4)"},
                                 hover_data=["merchant_name","category_display","invoice_number","currency"],
                                 opacity=0.75,
                                 labels={"line_items_count":"Line Items","total_amount":"Amount"})
                fig.update_layout(height=360)
                T(fig); st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            col3, col4 = st.columns(2)
            with col3:
                st.markdown('<div class="section-title">📊 Anomalies by Category</div>', unsafe_allow_html=True)
                ac = adf[adf["is_anomaly"]].groupby("category_display").size().reset_index(name="count")
                if not ac.empty:
                    fig = px.bar(ac, x="category_display", y="count",
                                 color="count", color_continuous_scale=["#6c5ce7","#ff7675"])
                    fig.update_layout(height=300, xaxis_tickangle=-30, coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            with col4:
                st.markdown('<div class="section-title">🏪 Top Vendors with Anomalies</div>', unsafe_allow_html=True)
                av = adf[adf["is_anomaly"]].groupby("merchant_name").size().reset_index(name="count")
                av = av.sort_values("count",ascending=False).head(10)
                if not av.empty:
                    fig = px.bar(av, x="count", y="merchant_name", orientation="h",
                                 color="count", color_continuous_scale=["#fdcb6e","#ff7675"])
                    fig.update_layout(height=300, yaxis=dict(autorange="reversed"),
                                      coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown('<div class="section-title">📋 Anomalous Invoice Details</div>', unsafe_allow_html=True)
            anom_detail = adf[adf["is_anomaly"]].sort_values("total_amount",ascending=False).head(50).copy()
            cols_show = ["merchant_name","invoice_number","invoice_date","currency",
                         "total_amount","category_display","line_items_count","anomaly_score"]
            disp = anom_detail[cols_show].copy()
            disp["total_amount"]   = disp["total_amount"].apply(lambda x: f"{x:,.2f}")
            disp["anomaly_score"]  = disp["anomaly_score"].apply(lambda x: f"{x:.4f}")
            disp["invoice_date"]   = disp["invoice_date"].dt.strftime("%Y-%m-%d")
            disp.columns = ["Vendor","Invoice #","Date","Currency","Amount",
                            "Category","Line Items","Anomaly Score"]
            st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("📊 Run the analysis with sufficient filtered data to detect anomalies.")


    # ──────────────────────────────────────────────────────────
    # TAB 8 — USER ANALYTICS
    # ──────────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown("## 👤 User Analytics")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        if not has_users:
            st.warning("⚠️ User data is not available in the current dataset.")
        elif sel_user == "All":
            # ── Show all-users overview when no user selected ─
            st.info("👆 Select a specific user from the sidebar to see their detailed profile and analytics.")

            st.markdown("### 🌐 Platform-Wide User Overview")
            if "user_id" in filtered_df.columns:
                ovu = filtered_df.dropna(subset=["user_id"])
                active_users  = ovu["user_id"].nunique()
                total_bills   = len(ovu)
                total_spend   = ovu["total_amount"].sum()
                avg_per_user  = total_spend / active_users if active_users else 0

                c1,c2,c3,c4 = st.columns(4)
                with c1: st.markdown(kpi_card("Active Users",     f"{active_users:,}",  icon="👥"), unsafe_allow_html=True)
                with c2: st.markdown(kpi_card("Total Bills",      f"{total_bills:,}",   icon="📋"), unsafe_allow_html=True)
                with c3: st.markdown(kpi_card("Total Spend",      fmt(total_spend),     icon="💸"), unsafe_allow_html=True)
                with c4: st.markdown(kpi_card("Avg Spend/User",   fmt(avg_per_user),    icon="🧾"), unsafe_allow_html=True)

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="section-title">🏆 Top Users by Spend</div>', unsafe_allow_html=True)
                    top_u = ovu.groupby(["user_id","user_name","user_email"]).agg(
                        total_spend=("total_amount","sum"),
                        bill_count=("bill_id","count"),
                    ).reset_index().sort_values("total_spend",ascending=False).head(15)
                    top_u["label"] = top_u["user_name"].fillna("?") + " (" + top_u["user_email"].fillna("") + ")"
                    fig = px.bar(top_u, x="total_spend", y="label", orientation="h",
                                 color="total_spend", color_continuous_scale=["#6c5ce7","#00cec9"],
                                 text="bill_count",
                                 labels={"total_spend":"Total Spend","label":"User"})
                    fig.update_traces(texttemplate="%{text} bills", textposition="inside")
                    fig.update_layout(height=420, yaxis=dict(title="", autorange="reversed"),
                                      showlegend=False, coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown('<div class="section-title">📊 Bills per User Distribution</div>', unsafe_allow_html=True)
                    bills_per_user = ovu.groupby("user_id")["bill_id"].count().reset_index()
                    bills_per_user.columns = ["user_id","bill_count"]
                    fig = px.histogram(bills_per_user, x="bill_count", nbins=30,
                                       color_discrete_sequence=["#6c5ce7"],
                                       labels={"bill_count":"Bills Uploaded","count":"# Users"})
                    fig.update_layout(height=420)
                    T(fig); st.plotly_chart(fig, use_container_width=True)
        else:
            # ══════════════════════════════════════════════════
            # SINGLE USER DETAILED VIEW
            # ══════════════════════════════════════════════════
            udf_user  = filtered_df  # already filtered to this user by apply_filters
            user_name  = sel_user_row["user_name"] if sel_user_row is not None else "Unknown"
            user_email = sel_user_row["user_email"] if sel_user_row is not None else "—"

            # Enrich with full user record from user_df
            user_profile = {}
            if not user_df.empty and sel_user in user_df["user_id"].values:
                user_profile = user_df[user_df["user_id"]==sel_user].iloc[0].to_dict()

            # ── Compute user KPIs ─────────────────────────────
            total_bills   = len(udf_user)
            total_spend   = udf_user["total_amount"].sum()
            avg_bill      = udf_user["total_amount"].mean() if total_bills else 0
            vendors_used  = udf_user["merchant_name"].nunique()
            cats_used     = udf_user["category_display"].nunique()
            last_active   = udf_user["invoice_date"].max()
            reward_bal    = int(user_profile.get("reward_balance", 0))
            lifetime_pts  = int(user_profile.get("lifetime_points", 0))

            # Monthly stats for MoM growth
            umth = udf_user.dropna(subset=["invoice_date"]).set_index("invoice_date").resample("ME")["total_amount"].sum()
            umom = ((umth.iloc[-1]-umth.iloc[-2])/umth.iloc[-2]*100) if len(umth)>=2 and umth.iloc[-2]>0 else 0.0
            avg_monthly   = umth.mean() if len(umth) else 0

            # Purchase frequency (avg days between bills)
            sorted_dates = udf_user["invoice_date"].dropna().sort_values()
            if len(sorted_dates) >= 2:
                diffs = sorted_dates.diff().dropna().dt.days
                avg_days_between = diffs.mean()
            else:
                avg_days_between = None

            # Risk level based on anomaly detection
            try:
                from sklearn.ensemble import IsolationForest
                if len(udf_user) >= 3:
                    _X = udf_user[["total_amount","line_items_count"]].fillna(0)
                    _iso = IsolationForest(contamination=0.15, random_state=42)
                    _preds = _iso.fit_predict(_X)
                    anom_rate = (_preds == -1).mean() * 100
                    risk_level = "🔴 High" if anom_rate > 30 else "🟡 Medium" if anom_rate > 10 else "🟢 Low"
                else:
                    anom_rate = 0
                    risk_level = "🟢 Low"
            except Exception:
                anom_rate = 0
                risk_level = "🟢 Low"

            # ── USER PROFILE CARD ─────────────────────────────
            did_badge = ""
            if user_profile.get("did_status") == "ready":
                did_badge = '<span style="background:#00cec9;color:#000;border-radius:4px;padding:2px 8px;font-size:0.7rem;font-weight:700;">✅ DID Verified</span>'

            last_active_str = last_active.strftime("%Y-%m-%d") if pd.notna(last_active) else "N/A"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(108,92,231,0.2),rgba(0,206,201,0.1));
                        border:1px solid rgba(108,92,231,0.4);border-radius:16px;padding:1.5rem;margin-bottom:1rem;">
              <div style="display:flex;align-items:center;gap:1rem;">
                <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#6c5ce7,#00cec9);
                            display:flex;align-items:center;justify-content:center;font-size:1.8rem;">👤</div>
                <div>
                  <div style="font-size:1.4rem;font-weight:800;color:#fff;">{user_name}</div>
                  <div style="color:#a29bfe;font-size:0.9rem;">{user_email}</div>
                  <div style="margin-top:6px;">{did_badge}</div>
                </div>
                <div style="margin-left:auto;text-align:right;">
                  <div style="font-size:0.8rem;color:#a29bfe;">Risk Level</div>
                  <div style="font-size:1.1rem;font-weight:700;">{risk_level}</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:1.2rem;">
                <div style="text-align:center;"><div style="color:#a29bfe;font-size:0.75rem;">💎 Reward Balance</div>
                  <div style="color:#fdcb6e;font-size:1.1rem;font-weight:700;">{reward_bal:,} pts</div></div>
                <div style="text-align:center;"><div style="color:#a29bfe;font-size:0.75rem;">🌟 Lifetime Points</div>
                  <div style="color:#fdcb6e;font-size:1.1rem;font-weight:700;">{lifetime_pts:,} pts</div></div>
                <div style="text-align:center;"><div style="color:#a29bfe;font-size:0.75rem;">📅 Last Active</div>
                  <div style="color:#fff;font-size:1.0rem;font-weight:600;">{last_active_str}</div></div>
                <div style="text-align:center;"><div style="color:#a29bfe;font-size:0.75rem;">📊 Anomaly Rate</div>
                  <div style="color:#ff7675;font-size:1.0rem;font-weight:600;">{anom_rate:.1f}%</div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── USER KPI CARDS ────────────────────────────────
            c1,c2,c3,c4,c5,c6 = st.columns(6)
            with c1: st.markdown(kpi_card("Bills Uploaded", f"{total_bills:,}",    icon="📋"), unsafe_allow_html=True)
            with c2: st.markdown(kpi_card("Total Spend",    fmt(total_spend),       icon="💸"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("Avg Bill",       fmt(avg_bill),          icon="🧾"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_card("Vendors Used",   f"{vendors_used:,}",   icon="🏪"), unsafe_allow_html=True)
            with c5: st.markdown(kpi_card("Categories",     f"{cats_used}",         icon="🏷️"), unsafe_allow_html=True)
            with c6: st.markdown(kpi_card("MoM Growth",     f"{umom:+.1f}%",       pos=umom>=0, icon="📈"), unsafe_allow_html=True)

            st.markdown("---")

            # ── CHARTS ROW 1 ──────────────────────────────────
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown('<div class="section-title">📈 Monthly Spending Trend</div>', unsafe_allow_html=True)
                if not udf_user.empty:
                    _u = udf_user.dropna(subset=["invoice_date","total_amount"]).copy()
                    _u["month"]      = _u["invoice_date"].dt.strftime("%b %Y")
                    _u["month_sort"] = _u["invoice_date"].dt.to_period("M").astype(str)
                    _ug = _u.groupby(["month","month_sort"]).agg(
                        total_spend=("total_amount","sum"),
                        bill_count=("bill_id","count"),
                        avg_bill=("total_amount","mean"),
                    ).reset_index().sort_values("month_sort")
                    if not _ug.empty:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=_ug["month"], y=_ug["total_spend"], name="Total Spend",
                            mode="lines+markers", fill="tozeroy",
                            line=dict(color="#6c5ce7",width=3), marker=dict(size=8),
                            fillcolor="rgba(108,92,231,0.15)"))
                        fig.add_trace(go.Scatter(
                            x=_ug["month"], y=_ug["avg_bill"], name="Avg Bill",
                            mode="lines+markers", yaxis="y2",
                            line=dict(color="#00cec9",width=2,dash="dot"), marker=dict(size=6)))
                        fig.update_layout(
                            xaxis=dict(type="category",title="",tickangle=-30),
                            yaxis=dict(title="Total Spend"),
                            yaxis2=dict(overlaying="y",side="right",showgrid=False,title="Avg Bill"),
                            height=340, showlegend=True)
                        T(fig); st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No date data for this user.")

            with col2:
                st.markdown('<div class="section-title">🏷️ Category Usage Distribution</div>', unsafe_allow_html=True)
                _cat = udf_user.groupby("category_display")["total_amount"].sum().reset_index()
                _cat.columns = ["category","spend"]
                _cat = _cat.sort_values("spend",ascending=False)
                if not _cat.empty:
                    fig = px.pie(_cat, values="spend", names="category",
                                 color_discrete_sequence=PALETTE, hole=0.55)
                    fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10)
                    fig.update_layout(height=340, showlegend=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            # ── CHARTS ROW 2 ──────────────────────────────────
            col3, col4 = st.columns(2)

            with col3:
                st.markdown('<div class="section-title">🏪 Vendor Usage Analysis</div>', unsafe_allow_html=True)
                _ven = udf_user.groupby("merchant_name").agg(
                    total_spend=("total_amount","sum"),
                    bill_count=("bill_id","count"),
                ).reset_index().sort_values("total_spend",ascending=False).head(10)
                if not _ven.empty:
                    fig = px.bar(_ven, x="total_spend", y="merchant_name", orientation="h",
                                 color="total_spend", color_continuous_scale=["#6c5ce7","#00cec9"],
                                 text="bill_count",
                                 labels={"total_spend":"Spend","merchant_name":"Vendor"})
                    fig.update_traces(texttemplate="%{text} bills", textposition="inside")
                    fig.update_layout(height=340, yaxis=dict(title="",autorange="reversed"),
                                      showlegend=False, coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            with col4:
                st.markdown('<div class="section-title">📅 Bill Upload Activity (Monthly)</div>', unsafe_allow_html=True)
                if not udf_user.empty:
                    _act = udf_user.dropna(subset=["invoice_date"]).copy()
                    _act["month"]      = _act["invoice_date"].dt.strftime("%b %Y")
                    _act["month_sort"] = _act["invoice_date"].dt.to_period("M").astype(str)
                    _actg = _act.groupby(["month","month_sort"]).size().reset_index(name="uploads")
                    _actg = _actg.sort_values("month_sort")
                    if not _actg.empty:
                        fig = px.bar(_actg, x="month", y="uploads",
                                     color="uploads", color_continuous_scale=["#a29bfe","#6c5ce7"],
                                     labels={"month":"","uploads":"Bills Uploaded"})
                        fig.update_layout(
                            xaxis=dict(type="category",title="",tickangle=-30),
                            yaxis=dict(title="Bills Uploaded"),
                            height=340, coloraxis_showscale=False)
                        T(fig); st.plotly_chart(fig, use_container_width=True)

            # ── CHARTS ROW 3 ──────────────────────────────────
            col5, col6 = st.columns(2)

            with col5:
                st.markdown('<div class="section-title">🏷️ Top Spending Categories</div>', unsafe_allow_html=True)
                _topcat = udf_user.groupby("category_display")["total_amount"].sum().sort_values(
                    ascending=False).reset_index()
                _topcat.columns = ["category","spend"]
                if not _topcat.empty:
                    _topcat["pct"] = (_topcat["spend"] / _topcat["spend"].sum() * 100).round(1)
                    fig = px.bar(_topcat, x="category", y="spend",
                                 color="category", color_discrete_sequence=PALETTE,
                                 text="pct",
                                 labels={"category":"","spend":"Total Spend"})
                    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig.update_layout(height=320, showlegend=False, xaxis_tickangle=-30)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            with col6:
                st.markdown('<div class="section-title">🏆 Top Vendors Used</div>', unsafe_allow_html=True)
                _topv = udf_user.groupby("merchant_name")["total_amount"].sum().sort_values(
                    ascending=False).head(10).reset_index()
                _topv.columns = ["vendor","spend"]
                if not _topv.empty:
                    fig = px.bar(_topv, x="spend", y="vendor", orientation="h",
                                 color="spend", color_continuous_scale=["#fd79a8","#6c5ce7"],
                                 labels={"spend":"Total Spend","vendor":"Vendor"})
                    fig.update_layout(height=320, yaxis=dict(title="",autorange="reversed"),
                                      showlegend=False, coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            # ── SPEND HEATMAP ─────────────────────────────────
            st.markdown("---")
            st.markdown('<div class="section-title">🌡️ Spend Heatmap — Month × Category</div>', unsafe_allow_html=True)
            _hm = udf_user.dropna(subset=["invoice_date","category_display","total_amount"]).copy()
            _hm["month"] = _hm["invoice_date"].dt.strftime("%b %Y")
            _hm["month_sort"] = _hm["invoice_date"].dt.to_period("M").astype(str)
            if not _hm.empty:
                pivot = _hm.groupby(["category_display","month","month_sort"])["total_amount"].sum().reset_index()
                # Sort months
                month_order = pivot[["month","month_sort"]].drop_duplicates().sort_values("month_sort")["month"].tolist()
                pivot_wide = pivot.pivot_table(index="category_display", columns="month",
                                               values="total_amount", aggfunc="sum").fillna(0)
                # Reorder columns by month_sort
                pivot_wide = pivot_wide.reindex(columns=[m for m in month_order if m in pivot_wide.columns])
                fig = go.Figure(go.Heatmap(
                    z=pivot_wide.values,
                    x=pivot_wide.columns.tolist(),
                    y=pivot_wide.index.tolist(),
                    colorscale=[[0,"#1a1a2e"],[0.5,"#6c5ce7"],[1,"#00cec9"]],
                    text=pivot_wide.values.round(0),
                    texttemplate="%{text:,.0f}", textfont={"size":9},
                ))
                fig.update_layout(
                    height=max(280, len(pivot_wide)*32),
                    xaxis=dict(type="category",title=""),
                    yaxis=dict(title="")
                )
                T(fig); st.plotly_chart(fig, use_container_width=True)

            # ── BEHAVIORAL INSIGHTS ───────────────────────────
            st.markdown("---")
            st.markdown("### 🧠 User Behavior Analytics")

            most_used_cat = udf_user.groupby("category_display")["total_amount"].sum().idxmax() \
                if not udf_user.empty else "N/A"
            most_used_ven = udf_user.groupby("merchant_name")["total_amount"].sum().idxmax() \
                if not udf_user.empty else "N/A"
            cat_pct = udf_user.groupby("category_display")["total_amount"].sum()
            cat_pct_top = (cat_pct.max()/cat_pct.sum()*100) if len(cat_pct) else 0
            spend_growth_str = f"{umom:+.1f}% MoM" if len(umth)>=2 else "Insufficient data"
            avg_days_str = f"{avg_days_between:.1f} days" if avg_days_between else "N/A"

            bi_col1, bi_col2, bi_col3, bi_col4 = st.columns(4)
            with bi_col1:
                st.markdown(kpi_card("Most Used Category", most_used_cat,    icon="🏷️"), unsafe_allow_html=True)
            with bi_col2:
                st.markdown(kpi_card("Most Used Vendor",   most_used_ven,    icon="🏪"), unsafe_allow_html=True)
            with bi_col3:
                st.markdown(kpi_card("Avg Monthly Spend",  fmt(avg_monthly),  icon="📅"), unsafe_allow_html=True)
            with bi_col4:
                st.markdown(kpi_card("Avg Days Between",   avg_days_str,      icon="⏱️"), unsafe_allow_html=True)

            # ── AI INSIGHTS ───────────────────────────────────
            st.markdown("---")
            st.markdown("### 💡 AI-Generated Insights")

            insights = []
            if cat_pct_top > 0:
                insights.append({"icon":"📊","color":"#6c5ce7",
                    "text":f"User spends **{cat_pct_top:.1f}%** on **{most_used_cat}** — their dominant category."})
            if vendors_used > 0:
                insights.append({"icon":"🏪","color":"#00cec9",
                    "text":f"**{most_used_ven}** is the most frequently used vendor."})
            if total_bills > 0:
                insights.append({"icon":"📋","color":"#a29bfe",
                    "text":f"User has uploaded **{total_bills}** invoice(s) with an average bill of **{fmt(avg_bill)}**."})
            if len(umth) >= 2:
                trend_word = "increasing" if umom > 0 else "decreasing"
                insights.append({"icon":"📈" if umom>0 else "📉","color":"#fdcb6e" if umom>0 else "#ff7675",
                    "text":f"Spend is **{trend_word}** — MoM change: **{umom:+.1f}%**."})
            if reward_bal > 0:
                insights.append({"icon":"💎","color":"#fdcb6e",
                    "text":f"User has **{reward_bal}** reward points and **{lifetime_pts}** lifetime points. May qualify for premium loyalty rewards."})
            if avg_days_between and avg_days_between < 7:
                insights.append({"icon":"⚡","color":"#00cec9",
                    "text":f"Very high purchase frequency — average **{avg_days_str}** between bills."})
            if anom_rate > 15:
                insights.append({"icon":"⚠️","color":"#ff7675",
                    "text":f"Anomaly rate of **{anom_rate:.1f}%** detected. Review suspicious transactions."})
            # Forecast next month
            if len(umth) >= 2:
                next_month_est = umth.mean() * (1 + umom/100)
                insights.append({"icon":"🔮","color":"#74b9ff",
                    "text":f"Estimated next-month spend: **{fmt(next_month_est)}** based on current trend."})

            if insights:
                for ins in insights:
                    st.markdown(f"""
                    <div style="background:rgba({','.join(str(int(ins['color'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.12);
                                border-left:3px solid {ins['color']};border-radius:8px;
                                padding:0.8rem 1rem;margin-bottom:0.6rem;">
                      <span style="font-size:1.1rem;margin-right:8px;">{ins['icon']}</span>
                      <span style="color:#e0e0e0;font-size:0.9rem;">{ins['text']}</span>
                    </div>""", unsafe_allow_html=True)

            # ── USER FORECASTING ──────────────────────────────
            st.markdown("---")
            st.markdown("### 🔮 User Spend Forecast")

            if len(umth) >= 3:
                import numpy as np
                months_hist = list(range(len(umth)))
                spend_vals  = umth.values

                # Linear trend
                z = np.polyfit(months_hist, spend_vals, 1)
                p = np.poly1d(z)
                forecast_months = [len(umth)+i for i in range(6)]
                linear_fc = [max(0, p(m)) for m in forecast_months]

                # EMA
                ema_fc = []
                alpha = 0.3
                ema_val = float(spend_vals[-1])
                for _ in range(6):
                    ema_val = alpha * float(spend_vals[-1]) + (1-alpha)*ema_val
                    ema_fc.append(max(0, ema_val))

                # Ensemble
                ensemble_fc = [(l+e)/2 for l,e in zip(linear_fc,ema_fc)]

                # Build date axis
                # umth.index is already a DatetimeIndex (resample returns DatetimeIndex)
                hist_dates   = umth.index
                last_date    = hist_dates[-1]
                future_dates = pd.date_range(last_date, periods=7, freq="ME")[1:]

                # KPI forecast cards
                f1,f2,f3 = st.columns(3)
                with f1: st.markdown(kpi_card("Next Month",      fmt(ensemble_fc[0]),        icon="📅"), unsafe_allow_html=True)
                with f2: st.markdown(kpi_card("3-Month Total",   fmt(sum(ensemble_fc[:3])),  icon="📆"), unsafe_allow_html=True)
                with f3: st.markdown(kpi_card("6-Month Total",   fmt(sum(ensemble_fc)),      icon="🗓️"), unsafe_allow_html=True)

                # Forecast chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist_dates, y=spend_vals, name="Historical",
                    mode="lines+markers", line=dict(color="#6c5ce7",width=2.5),
                    marker=dict(size=6)))
                fig.add_trace(go.Scatter(
                    x=future_dates, y=ensemble_fc, name="Ensemble Forecast",
                    mode="lines+markers", line=dict(color="#00cec9",width=3),
                    marker=dict(size=8,symbol="diamond"),
                    fill="tozeroy", fillcolor="rgba(0,206,201,0.08)"))
                fig.add_trace(go.Scatter(
                    x=future_dates, y=linear_fc, name="Linear Trend",
                    mode="lines", line=dict(color="#fdcb6e",width=1.5,dash="dot")))
                fig.add_trace(go.Scatter(
                    x=future_dates, y=ema_fc, name="EMA Smoothed",
                    mode="lines", line=dict(color="#74b9ff",width=1.5,dash="dash")))
                if len(hist_dates):
                    fig.add_vline(x=hist_dates[-1], line_dash="dash",
                                  line_color="rgba(255,255,255,0.3)",
                                  annotation_text="Forecast begins",
                                  annotation_font_color="#a29bfe")
                fig.update_layout(height=380, hovermode="x unified")
                T(fig); st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Need at least 3 months of data to generate a forecast for this user.")

            # ── USER ANOMALY DETECTION ────────────────────────
            st.markdown("---")
            st.markdown("### 🚨 User Anomaly Detection")

            if len(udf_user) >= 3:
                try:
                    from sklearn.ensemble import IsolationForest
                    _X2 = udf_user[["total_amount","line_items_count"]].fillna(0)
                    _iso2 = IsolationForest(contamination=0.15, random_state=42)
                    _scores2 = _iso2.fit_predict(_X2)
                    _anom_scores2 = _iso2.score_samples(_X2)

                    udf_anom = udf_user.copy()
                    udf_anom["is_anomaly"]    = (_scores2 == -1)
                    udf_anom["anomaly_score"] = _anom_scores2

                    n_anom2    = udf_anom["is_anomaly"].sum()
                    anom_pct2  = n_anom2 / len(udf_anom) * 100
                    anom_sp2   = udf_anom[udf_anom["is_anomaly"]]["total_amount"].sum()

                    ac1,ac2,ac3 = st.columns(3)
                    with ac1: st.markdown(kpi_card("Anomalies Found", f"{n_anom2}",          icon="🚨"), unsafe_allow_html=True)
                    with ac2: st.markdown(kpi_card("Anomaly Rate",    f"{anom_pct2:.1f}%",   icon="📊"), unsafe_allow_html=True)
                    with ac3: st.markdown(kpi_card("Anomalous Spend", fmt(anom_sp2),          icon="💸"), unsafe_allow_html=True)

                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown('<div class="section-title">🔍 Score Distribution</div>', unsafe_allow_html=True)
                        fig = px.histogram(udf_anom, x="anomaly_score",
                                           color="is_anomaly",
                                           color_discrete_map={True:"#ff7675",False:"#6c5ce7"},
                                           nbins=20, barmode="overlay",
                                           labels={"anomaly_score":"Isolation Forest Score",
                                                   "is_anomaly":"Is Anomaly"})
                        fig.add_vline(x=0, line_dash="dash", line_color="#fdcb6e")
                        fig.update_layout(height=300)
                        T(fig); st.plotly_chart(fig, use_container_width=True)

                    with col_b:
                        st.markdown('<div class="section-title">💥 Amount vs Line Items</div>', unsafe_allow_html=True)
                        fig = px.scatter(udf_anom, x="line_items_count", y="total_amount",
                                         color=udf_anom["is_anomaly"].map({True:"🚨 Anomaly",False:"✅ Normal"}),
                                         color_discrete_map={"🚨 Anomaly":"#ff7675","✅ Normal":"rgba(108,92,231,0.5)"},
                                         hover_data=["merchant_name","invoice_number","invoice_date"],
                                         labels={"line_items_count":"Line Items","total_amount":"Amount",
                                                 "color":"Type"})
                        fig.update_layout(height=300)
                        T(fig); st.plotly_chart(fig, use_container_width=True)

                    # Suspicious transactions table
                    if n_anom2 > 0:
                        st.markdown('<div class="section-title">📋 Suspicious Transactions</div>', unsafe_allow_html=True)
                        show_cols = ["merchant_name","invoice_number","invoice_date",
                                     "currency","total_amount","category_display",
                                     "line_items_count","anomaly_score"]
                        show_cols = [c for c in show_cols if c in udf_anom.columns]
                        anom_tbl = udf_anom[udf_anom["is_anomaly"]].sort_values(
                            "total_amount",ascending=False)[show_cols].copy()
                        anom_tbl["total_amount"]  = anom_tbl["total_amount"].apply(lambda x: f"{x:,.2f}")
                        anom_tbl["anomaly_score"] = anom_tbl["anomaly_score"].apply(lambda x: f"{x:.4f}")
                        if "invoice_date" in anom_tbl.columns:
                            anom_tbl["invoice_date"] = anom_tbl["invoice_date"].dt.strftime("%Y-%m-%d")
                        anom_tbl.columns = ["Vendor","Invoice #","Date","Currency",
                                            "Amount","Category","Line Items","Score"][:len(show_cols)]
                        st.dataframe(anom_tbl, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ No anomalous transactions detected for this user.")

                except Exception as ex:
                    st.warning(f"⚠️ Anomaly detection could not run: {ex}")
            else:
                st.info("📊 Need at least 3 transactions to run anomaly detection.")


    # ──────────────────────────────────────────────────────────
    # TAB 9 — REGION ANALYTICS
    # ──────────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown("## 🌍 Region Analytics")
        filter_banner(sel_currency, sel_cats, sel_vendor, date_range, len(filtered_df))

        # ──────────────────────────────────────────────────────────
        # DERIVE REGION + COUNTRY FROM CURRENCY
        # (dataset has no explicit region/city/state column—
        #  currency is the only reliable geography signal across
        #  all 9 723 rows; GSTIN prefix used for India sub-state)
        # ──────────────────────────────────────────────────────────
        CURRENCY_COUNTRY = {
            "IDR": ("Indonesia",      "Southeast Asia"),
            "USD": ("United States",   "North America"),
            "INR": ("India",           "South Asia"),
            "NGN": ("Nigeria",         "West Africa"),
            "VND": ("Vietnam",         "Southeast Asia"),
            "PHP": ("Philippines",     "Southeast Asia"),
            "DZD": ("Algeria",         "North Africa"),
            "PKR": ("Pakistan",        "South Asia"),
            "TRY": ("Turkey",          "Middle East"),
            "UAH": ("Ukraine",         "Eastern Europe"),
            "IRR": ("Iran",            "Middle East"),
            "BDT": ("Bangladesh",      "South Asia"),
            "GBP": ("United Kingdom",  "Western Europe"),
            "MYR": ("Malaysia",        "Southeast Asia"),
            "EUR": ("Europe",          "Western Europe"),
            "HKD": ("Hong Kong",       "East Asia"),
            "MMK": ("Myanmar",         "Southeast Asia"),
            "BRL": ("Brazil",          "South America"),
            "AED": ("UAE",             "Middle East"),
            "CHF": ("Switzerland",     "Western Europe"),
            "ETB": ("Ethiopia",        "East Africa"),
            "TWD": ("Taiwan",          "East Asia"),
            "ZAR": ("South Africa",    "Southern Africa"),
            "EGP": ("Egypt",           "North Africa"),
            "KES": ("Kenya",           "East Africa"),
            "THB": ("Thailand",        "Southeast Asia"),
            "JPY": ("Japan",           "East Asia"),
            "XOF": ("West Africa",     "West Africa"),
            "UZS": ("Uzbekistan",      "Central Asia"),
            "MXN": ("Mexico",          "North America"),
            "NPR": ("Nepal",           "South Asia"),
            "CAD": ("Canada",          "North America"),
            "SGD": ("Singapore",       "Southeast Asia"),
            "RUB": ("Russia",          "Eastern Europe"),
            "KHR": ("Cambodia",        "Southeast Asia"),
            "PEN": ("Peru",            "South America"),
            "MAD": ("Morocco",         "North Africa"),
            "NZD": ("New Zealand",     "Oceania"),
            "BTC": ("Global/Crypto",   "Global"),
            "AZN": ("Azerbaijan",      "Central Asia"),
            "PLN": ("Poland",          "Eastern Europe"),
            "LYD": ("Libya",           "North Africa"),
            "ZMW": ("Zambia",          "Southern Africa"),
            "CRC": ("Costa Rica",      "Central America"),
            "LKR": ("Sri Lanka",       "South Asia"),
            "AUD": ("Australia",       "Oceania"),
        }

        GSTIN_STATE = {
            "01":"Jammu & Kashmir","02":"Himachal Pradesh","03":"Punjab",
            "04":"Chandigarh",     "05":"Uttarakhand",     "06":"Haryana",
            "07":"Delhi",          "08":"Rajasthan",       "09":"Uttar Pradesh",
            "10":"Bihar",          "11":"Sikkim",          "12":"Arunachal Pradesh",
            "13":"Nagaland",       "14":"Manipur",         "15":"Mizoram",
            "16":"Tripura",        "17":"Meghalaya",       "18":"Assam",
            "19":"West Bengal",    "20":"Jharkhand",       "21":"Odisha",
            "22":"Chhattisgarh",   "23":"Madhya Pradesh",  "24":"Gujarat",
            "25":"Daman & Diu",    "26":"Dadra & NH",      "27":"Maharashtra",
            "28":"Andhra Pradesh", "29":"Karnataka",       "30":"Goa",
            "31":"Lakshadweep",    "32":"Kerala",          "33":"Tamil Nadu",
            "34":"Puducherry",     "35":"Andaman & Nicobar","36":"Telangana",
            "37":"Andhra Pradesh (New)",
        }

        rdf = filtered_df.copy()

        # Map country and macro-region from currency
        rdf["country"] = rdf["currency"].map(
            lambda c: CURRENCY_COUNTRY.get(c, ("Unknown","Other"))[0])
        rdf["region"]  = rdf["currency"].map(
            lambda c: CURRENCY_COUNTRY.get(c, ("Unknown","Other"))[1])

        # For India: enrich with state from GSTIN
        def _get_state(row):
            if row.get("currency") == "INR" and isinstance(row.get("tax_reg_number"), str):
                code = row["tax_reg_number"][:2]
                return GSTIN_STATE.get(code, "India-Other")
            return row.get("country", "Unknown")

        rdf["state"] = rdf.apply(_get_state, axis=1)

        # Drop unknown
        rdf = rdf[rdf["region"] != "Other"]

        if rdf.empty:
            st.warning("⚠️ No data available after filters.")
        else:
            # ──── PRE-COMPUTE REGION AGGREGATIONS ────────────────
            rgby = rdf.groupby("region").agg(
                total_spend=("total_amount","sum"),
                invoice_count=("bill_id","count"),
                avg_bill=("total_amount","mean"),
                unique_vendors=("merchant_name","nunique"),
                unique_users=("user_id" if "user_id" in rdf.columns else "extraction_id","nunique"),
                unique_cats=("category_display","nunique"),
            ).reset_index().sort_values("total_spend", ascending=False)

            # Top category per region
            top_cat_per_region = (
                rdf.groupby(["region","category_display"])["total_amount"].sum()
                .reset_index()
                .sort_values("total_amount",ascending=False)
                .drop_duplicates("region")
                .set_index("region")["category_display"].to_dict()
            )
            # Top vendor per region
            top_ven_per_region = (
                rdf.groupby(["region","merchant_name"])["total_amount"].sum()
                .reset_index()
                .sort_values("total_amount",ascending=False)
                .drop_duplicates("region")
                .set_index("region")["merchant_name"].to_dict()
            )
            # Top user per region
            if "user_name" in rdf.columns:
                top_user_per_region = (
                    rdf.dropna(subset=["user_name"]).groupby(["region","user_name"])["total_amount"].sum()
                    .reset_index().sort_values("total_amount",ascending=False)
                    .drop_duplicates("region").set_index("region")["user_name"].to_dict()
                )
            else:
                top_user_per_region = {}

            total_all_spend = rdf["total_amount"].sum()
            n_regions        = rgby["region"].nunique()
            top_region       = rgby.iloc[0]["region"]   if not rgby.empty else "N/A"
            top_spend        = rgby.iloc[0]["total_spend"] if not rgby.empty else 0
            avg_spend_region = rgby["total_spend"].mean()

            # Most active region (by invoice count)
            most_active_region = rgby.sort_values("invoice_count",ascending=False).iloc[0]["region"] \
                if not rgby.empty else "N/A"

            # Fastest growing region (MoM change)
            fastest_growing = "N/A"
            fastest_pct = 0.0
            if "invoice_date" in rdf.columns:
                _trend = rdf.dropna(subset=["invoice_date"]).copy()
                _trend["month_str"] = _trend["invoice_date"].dt.to_period("M").astype(str)
                _rgm = _trend.groupby(["region","month_str"])["total_amount"].sum().unstack(fill_value=0)
                if _rgm.shape[1] >= 2:
                    last  = _rgm.iloc[:,-1]
                    prev  = _rgm.iloc[:,-2].replace(0, float("nan"))
                    growth = ((last - prev) / prev * 100).dropna()
                    if not growth.empty:
                        fastest_growing = growth.idxmax()
                        fastest_pct     = growth.max()

            # ──── KPI CARDS ──────────────────────────────────
            k1,k2,k3,k4,k5,k6 = st.columns(6)
            with k1: st.markdown(kpi_card("Total Regions",      f"{n_regions}",                    icon="🌍"), unsafe_allow_html=True)
            with k2: st.markdown(kpi_card("Top Spending Region", top_region,                         icon="🏆"), unsafe_allow_html=True)
            with k3: st.markdown(kpi_card("Total Regional Spend",fmt(total_all_spend),               icon="💸"), unsafe_allow_html=True)
            with k4: st.markdown(kpi_card("Avg Spend/Region",   fmt(avg_spend_region),              icon="🧾"), unsafe_allow_html=True)
            with k5: st.markdown(kpi_card("Most Active Region",  most_active_region,                 icon="⚡"), unsafe_allow_html=True)
            with k6: st.markdown(kpi_card("Fastest Growing",    f"{fastest_growing} ({fastest_pct:+.1f}%)", icon="📈"), unsafe_allow_html=True)

            st.markdown("---")

            # ──── ROW 1: Region Spend + Contribution Donut ─────
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown('<div class="section-title">📊 Region-Wise Total Spend</div>', unsafe_allow_html=True)
                fig = px.bar(rgby, x="region", y="total_spend",
                             color="region", color_discrete_sequence=PALETTE,
                             text="invoice_count",
                             labels={"region":"Region","total_spend":"Total Spend","invoice_count":"# Invoices"})
                fig.update_traces(texttemplate="%{text:,} invoices", textposition="outside")
                fig.update_layout(height=380, showlegend=False, xaxis_tickangle=-30)
                T(fig); st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown('<div class="section-title">🍥 Region Spend Contribution</div>', unsafe_allow_html=True)
                fig = px.pie(rgby, values="total_spend", names="region",
                             color_discrete_sequence=PALETTE, hole=0.55)
                fig.update_traces(textposition="outside", textinfo="label+percent",
                                  textfont_size=10, pull=[0.03]*len(rgby))
                fig.update_layout(height=380, showlegend=False)
                T(fig); st.plotly_chart(fig, use_container_width=True)

            # ──── ROW 2: Category Stacked Bar + Spend Trend ───
            col3, col4 = st.columns(2)

            with col3:
                st.markdown('<div class="section-title">🏷️ Category Distribution by Region</div>', unsafe_allow_html=True)
                _rcat = rdf.groupby(["region","category_display"])["total_amount"].sum().reset_index()
                _rcat.columns = ["region","category","spend"]
                # Sort regions by total spend so highest is at top
                _region_order = rgby["region"].tolist()[::-1]  # reversed for horizontal (bottom=highest)
                _rcat["region"] = pd.Categorical(_rcat["region"], categories=_region_order, ordered=True)
                _rcat = _rcat.sort_values("region")
                # Horizontal bar — regions on Y-axis (no overlap)
                fig = px.bar(_rcat, y="region", x="spend", color="category",
                             color_discrete_sequence=PALETTE, barmode="stack",
                             orientation="h",
                             labels={"region":"","spend":"Total Spend","category":"Category"})
                fig.update_layout(
                    height=max(380, len(_region_order) * 34),
                    yaxis=dict(title="", autorange="reversed"),
                    xaxis=dict(title="Total Spend"),
                    margin=dict(l=130, r=20, t=10, b=40),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.28, x=0,
                                font=dict(size=10)))
                T(fig); st.plotly_chart(fig, use_container_width=True)

            with col4:
                st.markdown('<div class="section-title">📈 Region Spend Trend (Monthly)</div>', unsafe_allow_html=True)
                if "invoice_date" in rdf.columns:
                    _rt = rdf.dropna(subset=["invoice_date"]).copy()

                    # Filter out extreme date outliers (keep last 5 years of real data)
                    _max_date = _rt["invoice_date"].quantile(0.98)  # ignore top 2% outliers
                    _min_date = _max_date - pd.DateOffset(years=3)
                    _rt = _rt[(_rt["invoice_date"] >= _min_date) & (_rt["invoice_date"] <= _max_date)]

                    _rt["month"]      = _rt["invoice_date"].dt.strftime("%b %Y")
                    _rt["month_sort"] = _rt["invoice_date"].dt.to_period("M").astype(str)
                    _rtg = _rt.groupby(["region","month","month_sort"])["total_amount"].sum().reset_index()
                    _rtg = _rtg.sort_values("month_sort")
                    # Limit to top 5 regions for readability
                    top5 = rgby.head(5)["region"].tolist()
                    _rtg5 = _rtg[_rtg["region"].isin(top5)]
                    if not _rtg5.empty:
                        # Keep only unique sorted months for the x-axis
                        _sorted_months = (
                            _rtg5[["month","month_sort"]]
                            .drop_duplicates()
                            .sort_values("month_sort")["month"]
                            .tolist()
                        )
                        fig = px.line(
                            _rtg5, x="month", y="total_amount", color="region",
                            color_discrete_sequence=PALETTE,
                            markers=True,
                            category_orders={"month": _sorted_months},
                            labels={"total_amount":"Spend", "region":"Region", "month":""},
                        )
                        T(fig)
                        fig.update_layout(
                            height=420,
                            xaxis_title="",
                            xaxis_type="category",
                            xaxis_tickangle=-60,
                            xaxis_tickfont=dict(size=10),
                            xaxis_nticks=10,
                            yaxis_title="Spend",
                            legend=dict(orientation="h", yanchor="bottom", y=-0.35, x=0,
                                        font=dict(size=10)),
                            margin=dict(b=110, l=20, r=20, t=40),
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No trend data after filtering date outliers.")

            # ──── ROW 3: Top Category Heatmap + Vendor Horizontal ────
            col5, col6 = st.columns(2)

            with col5:
                st.markdown('<div class="section-title">🌡️ Region × Category Spend Heatmap</div>', unsafe_allow_html=True)
                _hm = rdf.groupby(["region","category_display"])["total_amount"].sum().unstack(fill_value=0)
                if not _hm.empty:
                    fig = go.Figure(go.Heatmap(
                        z=_hm.values,
                        x=_hm.columns.tolist(),
                        y=_hm.index.tolist(),
                        colorscale=[[0,"#1a1a2e"],[0.5,"#6c5ce7"],[1,"#00cec9"]],
                        text=_hm.values.round(0),
                        texttemplate="%{text:,.0f}", textfont={"size":8},
                    ))
                    fig.update_layout(
                        height=max(300, len(_hm)*30),
                        xaxis=dict(title="",tickangle=-40),
                        yaxis=dict(title="")
                    )
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            with col6:
                st.markdown('<div class="section-title">🏪 Top Vendors by Region</div>', unsafe_allow_html=True)
                _rv = rdf.groupby(["region","merchant_name"])["total_amount"].sum().reset_index()
                _rv.columns = ["region","vendor","spend"]
                # Top 3 vendors per region, then take overall top 15 rows
                _rv_top = _rv.sort_values("spend",ascending=False).groupby("region").head(2)
                _rv_top = _rv_top.sort_values("spend",ascending=False).head(20)
                _rv_top["label"] = _rv_top["region"] + " | " + _rv_top["vendor"]
                fig = px.bar(_rv_top, x="spend", y="label", orientation="h",
                             color="region", color_discrete_sequence=PALETTE,
                             labels={"spend":"Total Spend","label":"Region | Vendor"})
                fig.update_layout(height=max(340, len(_rv_top)*22),
                                  yaxis=dict(title="",autorange="reversed"),
                                  showlegend=False)
                T(fig); st.plotly_chart(fig, use_container_width=True)

            # ──── ROW 4: User Activity by Region ─────────────
            st.markdown("---")
            st.markdown('<div class="section-title">👥 User Activity by Region</div>', unsafe_allow_html=True)
            if "user_id" in rdf.columns:
                _ua = rdf.groupby("region").agg(
                    invoices=("bill_id","count"),
                    users=("user_id","nunique"),
                    avg_monthly_spend=("total_amount","mean"),
                ).reset_index().sort_values("invoices",ascending=False)
                _ua["invoices_per_user"] = (_ua["invoices"] / _ua["users"].replace(0,1)).round(1)

                ua_col1, ua_col2 = st.columns(2)
                with ua_col1:
                    fig = px.bar(_ua, x="region", y="invoices",
                                 color="users", color_continuous_scale=["#a29bfe","#6c5ce7"],
                                 text="users",
                                 labels={"region":"Region","invoices":"# Invoices","users":"# Users"})
                    fig.update_traces(texttemplate="%{text} users", textposition="outside")
                    fig.update_layout(height=320, xaxis_tickangle=-30, coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

                with ua_col2:
                    fig = px.bar(_ua, x="region", y="invoices_per_user",
                                 color="invoices_per_user",
                                 color_continuous_scale=["#74b9ff","#00cec9"],
                                 labels={"region":"Region","invoices_per_user":"Invoices per User"})
                    fig.update_layout(height=320, xaxis_tickangle=-30, coloraxis_showscale=False)
                    T(fig); st.plotly_chart(fig, use_container_width=True)

            # ──── REGION SUMMARY TABLE ─────────────────────
            st.markdown("---")
            st.markdown("### 📊 Region Summary Table")

            summary_rows = []
            for _, row in rgby.iterrows():
                reg = row["region"]
                summary_rows.append({
                    "Region":         reg,
                    "Total Spend":    f"{row['total_spend']:,.2f}",
                    "Invoices":       f"{int(row['invoice_count']):,}",
                    "Avg Bill":       f"{row['avg_bill']:,.2f}",
                    "Vendors":        f"{int(row['unique_vendors'])}",
                    "Users":          f"{int(row['unique_users'])}",
                    "Top Category":   top_cat_per_region.get(reg,"N/A"),
                    "Top Vendor":     top_ven_per_region.get(reg,"N/A"),
                    "Top User":       top_user_per_region.get(reg,"N/A"),
                })
            summary_df = pd.DataFrame(summary_rows)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            # ──── REGION × CATEGORY MATRIX ───────────────────
            st.markdown("---")
            st.markdown("### 🗳️ Region × Category Spend Matrix")

            _matrix = rdf.groupby(["region","category_display"])["total_amount"].sum().unstack(fill_value=0)
            if not _matrix.empty:
                # Highlight max/min per row
                def _style_row(row):
                    styles = ["" for _ in row]
                    if row.max() > 0:
                        styles[row.values.argmax()] = "background-color:rgba(0,206,201,0.25);font-weight:700;"
                    if row.min() < row.max():
                        styles[row.values.argmin()] = "background-color:rgba(255,118,117,0.18);font-style:italic;"
                    return styles

                # Format numbers
                _fmt_matrix = _matrix.map(lambda x: f"{x:,.0f}" if x > 0 else "—")

                # Show as styled dataframe
                styled = _matrix.style.apply(_style_row, axis=1).format("{:,.0f}")
                st.dataframe(styled, use_container_width=True)
                st.caption("✅ Teal = Highest spend in that region  |  🔴 Red-tinted = Lowest spend in that region")

            # ──── AI INSIGHTS ─────────────────────────────
            st.markdown("---")
            st.markdown("### 💡 AI-Generated Region Insights")

            r_insights = []

            # 1. Top region contribution %
            if not rgby.empty:
                top_pct = (rgby.iloc[0]["total_spend"] / total_all_spend * 100)
                r_insights.append({
                    "icon":"🏆","color":"#6c5ce7",
                    "text":f"**{top_region}** is the highest-spending region, contributing "
                           f"**{top_pct:.1f}%** of total spend."
                })

            # 2. Most active region
            if most_active_region != "N/A":
                ma_invoices = rgby[rgby["region"]==most_active_region]["invoice_count"].values[0]
                r_insights.append({
                    "icon":"⚡","color":"#00cec9",
                    "text":f"**{most_active_region}** has the highest user activity with "
                           f"**{int(ma_invoices):,}** invoices uploaded."
                })

            # 3. Top category per top region
            tc = top_cat_per_region.get(top_region)
            if tc:
                r_insights.append({
                    "icon":"🏷️","color":"#a29bfe",
                    "text":f"**{tc}** is the most purchased category in the **{top_region}** region."
                })

            # 4. Highest avg bill region
            best_avg = rgby.loc[rgby["avg_bill"].idxmax()]
            r_insights.append({
                "icon":"🧾","color":"#fdcb6e",
                "text":f"**{best_avg['region']}** has the highest average bill value of "
                       f"**{fmt(best_avg['avg_bill'])}** per invoice."
            })

            # 5. Fastest growing
            if fastest_growing != "N/A":
                r_insights.append({
                    "icon":"📈" if fastest_pct > 0 else "📉",
                    "color":"#74b9ff",
                    "text":f"**{fastest_growing}** is the fastest-growing region with a "
                           f"month-on-month change of **{fastest_pct:+.1f}%**."
                })

            # 6. Top vendor per top region
            tv = top_ven_per_region.get(top_region)
            if tv:
                r_insights.append({
                    "icon":"🏪","color":"#00cec9",
                    "text":f"**{tv}** is the most preferred vendor in **{top_region}**."
                })

            # 7. Bottom region
            if len(rgby) > 1:
                bot = rgby.iloc[-1]
                bot_pct = (bot["total_spend"] / total_all_spend * 100)
                r_insights.append({
                    "icon":"🟡","color":"#ff7675",
                    "text":f"**{bot['region']}** has the lowest regional spend at "
                           f"**{fmt(bot['total_spend'])}** ({bot_pct:.1f}% of total)."
                })

            for ins in r_insights:
                r, g, b = tuple(int(ins["color"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
                st.markdown(f"""
                <div style="background:rgba({r},{g},{b},0.12);
                            border-left:3px solid {ins['color']};border-radius:8px;
                            padding:0.8rem 1rem;margin-bottom:0.6rem;">
                  <span style="font-size:1.1rem;margin-right:8px;">{ins['icon']}</span>
                  <span style="color:#e0e0e0;font-size:0.9rem;">{ins['text']}</span>
                </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
