"""
Analytics Engine for BOC Procurement Dashboard
Contains all computation logic for spend, cost, vendor, and market analytics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any


# ═══════════════════════════════════════════════════════════════
# MODULE 1: SPEND ANALYTICS
# ═══════════════════════════════════════════════════════════════

def compute_spend_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate all spend KPIs."""
    total_spend = df['total_amount'].sum()
    avg_invoice = df['total_amount'].mean()
    median_invoice = df['total_amount'].median()
    total_vendors = df['merchant_name'].nunique()
    total_categories = df['category_display'].nunique()
    total_invoices = len(df)
    
    # Monthly spend for growth calc
    monthly = df.dropna(subset=['invoice_date']).set_index('invoice_date').resample('ME')['total_amount'].sum()
    if len(monthly) >= 2:
        recent = monthly.iloc[-1]
        prev = monthly.iloc[-2]
        growth_pct = ((recent - prev) / prev * 100) if prev > 0 else 0
    else:
        growth_pct = 0
    
    return {
        'total_spend': total_spend,
        'avg_invoice': avg_invoice,
        'median_invoice': median_invoice,
        'total_vendors': total_vendors,
        'total_categories': total_categories,
        'total_invoices': total_invoices,
        'spend_growth_pct': growth_pct,
    }


def monthly_spend_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly spend trend."""
    dff = df.dropna(subset=['invoice_date', 'total_amount']).copy()
    dff['month'] = dff['invoice_date'].dt.to_period('M').astype(str)
    result = dff.groupby('month').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
        avg_invoice=('total_amount', 'mean'),
    ).reset_index()
    result = result.sort_values('month')
    return result


def vendor_spend(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top vendors by spend."""
    result = df.groupby('merchant_name').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
        avg_invoice=('total_amount', 'mean'),
    ).reset_index().sort_values('total_spend', ascending=False).head(top_n)
    return result


def category_spend(df: pd.DataFrame) -> pd.DataFrame:
    """Category-wise spend breakdown."""
    result = df.groupby('category_display').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
        avg_invoice=('total_amount', 'mean'),
        vendor_count=('merchant_name', 'nunique'),
    ).reset_index().sort_values('total_spend', ascending=False)
    result['spend_pct'] = (result['total_spend'] / result['total_spend'].sum() * 100).round(2)
    return result


def currency_spend(df: pd.DataFrame) -> pd.DataFrame:
    """Currency-wise spend breakdown."""
    result = df.groupby('currency').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
    ).reset_index().sort_values('total_spend', ascending=False)
    return result


def weekday_spend(df: pd.DataFrame) -> pd.DataFrame:
    """Spending by day of week."""
    dff = df.dropna(subset=['invoice_weekday']).copy()
    result = dff.groupby('invoice_weekday').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
    ).reset_index()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    result['day_order'] = result['invoice_weekday'].map({d: i for i, d in enumerate(day_order)})
    result = result.sort_values('day_order')
    return result


def spend_concentration(df: pd.DataFrame) -> Dict[str, float]:
    """Analyze spend concentration (Pareto/80-20)."""
    vendor_spends = df.groupby('merchant_name')['total_amount'].sum().sort_values(ascending=False)
    total = vendor_spends.sum()
    cumsum = vendor_spends.cumsum()
    
    # How many vendors make up 80% of spend
    vendors_80pct = (cumsum <= total * 0.8).sum() + 1
    pct_vendors_80 = (vendors_80pct / len(vendor_spends) * 100)
    
    # Top 5 vendor concentration
    top5_spend = vendor_spends.head(5).sum()
    top5_pct = (top5_spend / total * 100) if total > 0 else 0
    
    # HHI (Herfindahl-Hirschman Index)
    shares = (vendor_spends / total * 100)
    hhi = (shares ** 2).sum()
    
    return {
        'vendors_80pct': vendors_80pct,
        'pct_vendors_80': round(pct_vendors_80, 1),
        'top5_concentration': round(top5_pct, 1),
        'hhi': round(hhi, 2),
        'total_vendors': len(vendor_spends),
    }


# ═══════════════════════════════════════════════════════════════
# MODULE 2: COST OPTIMIZATION
# ═══════════════════════════════════════════════════════════════

def price_variance_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Price variance analysis per vendor-category combination."""
    dff = df.dropna(subset=['total_amount']).copy()
    
    # Category average prices
    cat_avg = dff.groupby('category_display')['total_amount'].mean().rename('category_avg_price')
    
    # Vendor-Category analysis
    vc = dff.groupby(['merchant_name', 'category_display']).agg(
        vendor_avg_price=('total_amount', 'mean'),
        vendor_total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
    ).reset_index()
    
    vc = vc.merge(cat_avg.reset_index(), on='category_display', how='left')
    vc['price_variance_pct'] = ((vc['vendor_avg_price'] - vc['category_avg_price']) / vc['category_avg_price'] * 100).round(2)
    vc['status'] = vc['price_variance_pct'].apply(
        lambda x: 'Overpriced' if x > 20 else ('Underpriced' if x < -20 else 'Fair')
    )
    
    return vc.sort_values('price_variance_pct', ascending=False)


def vendor_price_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Compare vendor prices for same categories."""
    dff = df.dropna(subset=['total_amount']).copy()
    
    result = dff.groupby(['category_display', 'merchant_name']).agg(
        avg_price=('total_amount', 'mean'),
        min_price=('total_amount', 'min'),
        max_price=('total_amount', 'max'),
        invoice_count=('bill_id', 'count'),
        total_spend=('total_amount', 'sum'),
    ).reset_index()
    
    # Find cheapest & most expensive per category
    cat_min = result.groupby('category_display')['avg_price'].min().rename('cheapest_price')
    cat_max = result.groupby('category_display')['avg_price'].max().rename('most_expensive_price')
    
    result = result.merge(cat_min.reset_index(), on='category_display', how='left')
    result = result.merge(cat_max.reset_index(), on='category_display', how='left')
    result['is_cheapest'] = result['avg_price'] == result['cheapest_price']
    result['is_most_expensive'] = result['avg_price'] == result['most_expensive_price']
    
    return result


def savings_opportunity(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate potential savings by switching to lowest-cost vendor per category."""
    dff = df.dropna(subset=['total_amount']).copy()
    
    # Cheapest avg price per category
    cat_cheapest = dff.groupby('category_display')['total_amount'].min().rename('lowest_price')
    
    vendor_cat = dff.groupby(['category_display', 'merchant_name']).agg(
        avg_price=('total_amount', 'mean'),
        total_quantity=('bill_id', 'count'),
        total_spend=('total_amount', 'sum'),
    ).reset_index()
    
    cat_min_avg = vendor_cat.groupby('category_display')['avg_price'].min().rename('min_vendor_avg_price')
    vendor_cat = vendor_cat.merge(cat_min_avg.reset_index(), on='category_display', how='left')
    
    vendor_cat['potential_savings'] = (vendor_cat['avg_price'] - vendor_cat['min_vendor_avg_price']) * vendor_cat['total_quantity']
    vendor_cat['savings_pct'] = ((vendor_cat['avg_price'] - vendor_cat['min_vendor_avg_price']) / vendor_cat['avg_price'] * 100).round(2)
    vendor_cat = vendor_cat[vendor_cat['potential_savings'] > 0]
    
    return vendor_cat.sort_values('potential_savings', ascending=False)


def cost_optimization_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate cost optimization score 0-100."""
    scores = {}
    
    # 1. Price Variance Score (lower variance = better, 30pts)
    pv = price_variance_analysis(df)
    if not pv.empty:
        overpriced_pct = (pv['status'] == 'Overpriced').sum() / len(pv) * 100
        scores['price_variance'] = max(0, 30 - (overpriced_pct * 0.3))
    else:
        scores['price_variance'] = 15
    
    # 2. Spend Concentration Score (moderate concentration = good, 25pts)
    conc = spend_concentration(df)
    hhi = conc['hhi']
    if hhi < 1500:
        scores['spend_concentration'] = 25
    elif hhi < 2500:
        scores['spend_concentration'] = 18
    else:
        scores['spend_concentration'] = 8
    
    # 3. Vendor Dependency (fewer single-source categories = better, 25pts)
    cat_vendors = df.groupby('category_display')['merchant_name'].nunique()
    single_source_pct = (cat_vendors == 1).sum() / len(cat_vendors) * 100 if len(cat_vendors) > 0 else 0
    scores['vendor_dependency'] = max(0, 25 - (single_source_pct * 0.25))
    
    # 4. Savings Opportunities (lower potential savings = better, 20pts)
    savings = savings_opportunity(df)
    if not savings.empty and df['total_amount'].sum() > 0:
        savings_ratio = savings['potential_savings'].sum() / df['total_amount'].sum() * 100
        scores['savings_potential'] = max(0, 20 - (savings_ratio * 0.2))
    else:
        scores['savings_potential'] = 15
    
    total_score = min(100, sum(scores.values()))
    
    return {
        'total_score': round(total_score, 1),
        'breakdown': {k: round(v, 1) for k, v in scores.items()},
        'grade': 'A' if total_score >= 85 else 'B' if total_score >= 70 else 'C' if total_score >= 55 else 'D' if total_score >= 40 else 'F',
    }


# ═══════════════════════════════════════════════════════════════
# MODULE 3: VENDOR ANALYTICS
# ═══════════════════════════════════════════════════════════════

def vendor_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """Generate vendor scorecard with composite score."""
    dff = df.dropna(subset=['total_amount']).copy()
    
    vendor_metrics = dff.groupby('merchant_name').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
        avg_invoice=('total_amount', 'mean'),
        std_invoice=('total_amount', 'std'),
        min_invoice=('total_amount', 'min'),
        max_invoice=('total_amount', 'max'),
        categories=('category_display', 'nunique'),
        first_invoice=('invoice_date', 'min'),
        last_invoice=('invoice_date', 'max'),
    ).reset_index()
    
    vendor_metrics['std_invoice'] = vendor_metrics['std_invoice'].fillna(0)
    
    # Normalize metrics to 0-100 scale
    def normalize(series):
        min_val, max_val = series.min(), series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return ((series - min_val) / (max_val - min_val) * 100).round(2)
    
    # Price Competitiveness (lower avg = better, inverted)
    if vendor_metrics['avg_invoice'].max() > vendor_metrics['avg_invoice'].min():
        vendor_metrics['price_competitiveness'] = 100 - normalize(vendor_metrics['avg_invoice'])
    else:
        vendor_metrics['price_competitiveness'] = 50
    
    # Spend Consistency (lower std = better, inverted)
    if vendor_metrics['std_invoice'].max() > vendor_metrics['std_invoice'].min():
        vendor_metrics['spend_consistency'] = 100 - normalize(vendor_metrics['std_invoice'])
    else:
        vendor_metrics['spend_consistency'] = 50
    
    # Invoice Accuracy proxy (more items = more detailed bills = better)
    vendor_items = dff.groupby('merchant_name')['line_items_count'].mean().rename('avg_items')
    vendor_metrics = vendor_metrics.merge(vendor_items.reset_index(), on='merchant_name', how='left')
    vendor_metrics['avg_items'] = vendor_metrics['avg_items'].fillna(0)
    vendor_metrics['invoice_accuracy'] = normalize(vendor_metrics['avg_items'])
    
    # Purchase Frequency
    vendor_metrics['purchase_frequency'] = normalize(vendor_metrics['invoice_count'])
    
    # Market Alignment (within category norms)
    vendor_metrics['market_alignment'] = 50  # Default mid-range
    
    # Composite Vendor Score
    vendor_metrics['vendor_score'] = (
        0.30 * vendor_metrics['price_competitiveness'] +
        0.25 * vendor_metrics['spend_consistency'] +
        0.20 * vendor_metrics['invoice_accuracy'] +
        0.15 * vendor_metrics['purchase_frequency'] +
        0.10 * vendor_metrics['market_alignment']
    ).round(1)
    
    # Classification
    vendor_metrics['classification'] = vendor_metrics['vendor_score'].apply(
        lambda x: 'Preferred Vendor' if x >= 70 else 
                  'Good Vendor' if x >= 50 else 
                  'Watchlist Vendor' if x >= 30 else 
                  'High Risk Vendor'
    )
    
    return vendor_metrics.sort_values('vendor_score', ascending=False)


# ═══════════════════════════════════════════════════════════════
# MODULE 4: MARKET TREND ANALYSIS
# ═══════════════════════════════════════════════════════════════

def category_inflation(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate category-level price inflation over time."""
    dff = df.dropna(subset=['invoice_date', 'total_amount']).copy()
    dff['month'] = dff['invoice_date'].dt.to_period('M').astype(str)
    
    result = dff.groupby(['month', 'category_display']).agg(
        avg_price=('total_amount', 'mean'),
        invoice_count=('bill_id', 'count'),
    ).reset_index()
    
    # Calculate MoM inflation per category
    result = result.sort_values(['category_display', 'month'])
    result['prev_avg_price'] = result.groupby('category_display')['avg_price'].shift(1)
    result['inflation_pct'] = ((result['avg_price'] - result['prev_avg_price']) / result['prev_avg_price'] * 100).round(2)
    
    return result


def vendor_price_trend(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Track vendor price increases over time."""
    dff = df.dropna(subset=['invoice_date', 'total_amount']).copy()
    
    # Top vendors by spend
    top_vendors = dff.groupby('merchant_name')['total_amount'].sum().nlargest(top_n).index.tolist()
    dff = dff[dff['merchant_name'].isin(top_vendors)]
    
    dff['month'] = dff['invoice_date'].dt.to_period('M').astype(str)
    result = dff.groupby(['month', 'merchant_name']).agg(
        avg_price=('total_amount', 'mean'),
        invoice_count=('bill_id', 'count'),
    ).reset_index().sort_values(['merchant_name', 'month'])
    
    result['prev_price'] = result.groupby('merchant_name')['avg_price'].shift(1)
    result['price_change_pct'] = ((result['avg_price'] - result['prev_price']) / result['prev_price'] * 100).round(2)
    
    return result


def generate_alerts(df: pd.DataFrame) -> List[Dict]:
    """Generate procurement alerts."""
    alerts = []
    dff = df.dropna(subset=['total_amount']).copy()
    
    # 1. Price Spike Alerts
    pv = price_variance_analysis(dff)
    overpriced = pv[pv['price_variance_pct'] > 50].head(5)
    for _, row in overpriced.iterrows():
        alerts.append({
            'type': 'Price Increase Alert',
            'severity': 'high',
            'icon': '🔴',
            'message': f"{row['merchant_name']} charges {row['price_variance_pct']:.0f}% above category average in {row['category_display']}",
        })
    
    # 2. Vendor Concentration Risk
    conc = spend_concentration(dff)
    if conc['top5_concentration'] > 60:
        alerts.append({
            'type': 'Vendor Risk Alert',
            'severity': 'medium',
            'icon': '🟡',
            'message': f"Top 5 vendors account for {conc['top5_concentration']}% of total spend — high concentration risk",
        })
    
    # 3. High-value outlier invoices
    q99 = dff['total_amount'].quantile(0.99)
    outliers = dff[dff['total_amount'] > q99]
    if len(outliers) > 0:
        alerts.append({
            'type': 'Budget Overrun Alert',
            'severity': 'high',
            'icon': '🔴',
            'message': f"{len(outliers)} invoices exceed the 99th percentile value ({q99:,.0f}) — review for anomalies",
        })
    
    # 4. Category with single vendor
    cat_vendors = dff.groupby('category_display')['merchant_name'].nunique()
    single_source = cat_vendors[cat_vendors == 1]
    if len(single_source) > 0:
        for cat in single_source.index[:3]:
            alerts.append({
                'type': 'Vendor Risk Alert',
                'severity': 'medium',
                'icon': '🟡',
                'message': f"Category '{cat}' has only 1 vendor — single-source dependency risk",
            })
    
    # 5. Missing data alerts
    missing_dates = df['invoice_date'].isna().sum()
    if missing_dates > 0:
        alerts.append({
            'type': 'Data Quality Alert',
            'severity': 'low',
            'icon': '🔵',
            'message': f"{missing_dates} invoices ({missing_dates/len(df)*100:.1f}%) have missing dates",
        })
    
    return alerts


# ═══════════════════════════════════════════════════════════════
# ADVANCED ML ANALYTICS
# ═══════════════════════════════════════════════════════════════

def spend_forecast(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """Simple spend forecasting using exponential smoothing and linear regression."""
    dff = df.dropna(subset=['invoice_date', 'total_amount']).copy()
    monthly = dff.set_index('invoice_date').resample('ME')['total_amount'].sum().reset_index()
    monthly.columns = ['date', 'spend']
    monthly = monthly[monthly['spend'] > 0].sort_values('date')
    
    if len(monthly) < 3:
        return pd.DataFrame()
    
    # Simple linear trend
    monthly['t'] = range(len(monthly))
    
    from numpy.polynomial import polynomial as P
    coeffs = np.polyfit(monthly['t'].values, monthly['spend'].values, 1)
    
    # Exponential smoothing
    alpha = 0.3
    monthly['ema'] = monthly['spend'].ewm(alpha=alpha, adjust=False).mean()
    
    # Forecast future periods
    last_date = monthly['date'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=periods, freq='ME')
    future_t = range(len(monthly), len(monthly) + periods)
    
    linear_forecast = np.polyval(coeffs, list(future_t))
    last_ema = monthly['ema'].iloc[-1]
    ema_forecast = [last_ema * (1 + 0.02 * i) for i in range(1, periods + 1)]  # Simple growth assumption
    
    # Ensemble average
    ensemble = [(l + e) / 2 for l, e in zip(linear_forecast, ema_forecast)]
    
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'linear_forecast': linear_forecast,
        'ema_forecast': ema_forecast,
        'ensemble_forecast': ensemble,
        'is_forecast': True,
    })
    
    historical = monthly[['date', 'spend']].copy()
    historical['is_forecast'] = False
    historical['linear_forecast'] = np.polyval(coeffs, monthly['t'].values)
    historical['ema_forecast'] = monthly['ema'].values
    historical['ensemble_forecast'] = historical['spend']
    
    result = pd.concat([historical, forecast_df], ignore_index=True)
    return result


def vendor_clustering(df: pd.DataFrame) -> pd.DataFrame:
    """Cluster vendors using K-Means based on spend patterns."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    
    dff = df.dropna(subset=['total_amount']).copy()
    
    vendor_features = dff.groupby('merchant_name').agg(
        total_spend=('total_amount', 'sum'),
        invoice_count=('bill_id', 'count'),
        avg_invoice=('total_amount', 'mean'),
        std_invoice=('total_amount', 'std'),
        categories=('category_display', 'nunique'),
    ).reset_index()
    
    vendor_features['std_invoice'] = vendor_features['std_invoice'].fillna(0)
    
    if len(vendor_features) < 4:
        vendor_features['cluster'] = 0
        vendor_features['cluster_name'] = 'Uncategorized'
        return vendor_features
    
    features = ['total_spend', 'invoice_count', 'avg_invoice']
    X = vendor_features[features].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    n_clusters = min(4, len(vendor_features))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    vendor_features['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Name clusters based on characteristics
    cluster_stats = vendor_features.groupby('cluster').agg(
        avg_spend=('total_spend', 'mean'),
        avg_freq=('invoice_count', 'mean'),
    )
    
    cluster_ranking = cluster_stats.sort_values('avg_spend', ascending=False).index.tolist()
    cluster_names = ['Strategic Vendor', 'Preferred Vendor', 'Occasional Vendor', 'Risk Vendor']
    
    name_map = {}
    for i, cluster_id in enumerate(cluster_ranking):
        if i < len(cluster_names):
            name_map[cluster_id] = cluster_names[i]
        else:
            name_map[cluster_id] = 'Other'
    
    vendor_features['cluster_name'] = vendor_features['cluster'].map(name_map)
    
    return vendor_features


def anomaly_detection(df: pd.DataFrame) -> pd.DataFrame:
    """Detect anomalous invoices using Isolation Forest."""
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    
    dff = df.dropna(subset=['total_amount']).copy()
    
    if len(dff) < 10:
        dff['anomaly'] = 0
        dff['anomaly_score'] = 0
        return dff
    
    features = dff[['total_amount', 'line_items_count']].copy()
    features['tax_ratio'] = (dff['tax_amount'].fillna(0) / dff['total_amount'].clip(lower=0.01))
    features = features.fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features.values)
    
    iso_forest = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100,
    )
    
    dff['anomaly'] = iso_forest.fit_predict(X_scaled)
    dff['anomaly_score'] = iso_forest.decision_function(X_scaled)
    dff['is_anomaly'] = dff['anomaly'] == -1
    
    return dff
