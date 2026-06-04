# 📊 BOC Analytics — Procurement Intelligence Dashboard

A powerful **Streamlit-based Procurement Analytics Dashboard** built for the **Bill-on-Chain** platform.

---

## 🚀 Features

| Module | Description |
|---|---|
| 🏠 **Executive Dashboard** | High-level KPIs, Monthly Trend, Vendor & Category overview, Live Alerts |
| 📈 **Spend Analytics** | Deep spend breakdowns by category, vendor treemap, day-of-week, Pareto analysis |
| 💰 **Cost Optimization** | Price variance, savings opportunities, cost leakage detection |
| 🏪 **Vendor Analytics** | Vendor scoring, classification (Strategic/Preferred/Review/Problematic), heatmap |
| 📉 **Market Trends** | Category price inflation, vendor price trends, inflation heatmap |
| 🔮 **Forecasting** | ML-powered 6-month spend forecast + K-Means vendor clustering |
| 🚨 **Anomaly Detection** | Isolation Forest-based fraud/error detection on invoices |
| 👤 **User Analytics** | Per-user spend profile, behavior analytics, AI insights, user-level anomaly detection |
| 🌍 **Region Analytics** | Geographic spend breakdown by region (mapped from currency codes) |

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Data Processing:** Pandas, NumPy
- **Visualizations:** Plotly Express / Plotly Graph Objects
- **Machine Learning:** Scikit-learn (Isolation Forest, K-Means, Exponential Smoothing)

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Meghana7386/boc-analytics.git
cd boc-analytics
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your data
Place your Bill-on-Chain data export folder at:
```
C:\Users\<your_username>\Downloads\bocdata 1
```
> Update the path in `app.py` → `load_raw_data()` if your path differs.

### 4. Run the dashboard
```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📁 Project Structure

```
boc-analytics/
├── app.py                  # Main Streamlit application (all 9 modules)
├── analytics_engine.py     # Analytics computation functions (KPIs, ML models)
├── data_parser.py          # Data ingestion & parsing from BOC data format
├── requirements.txt        # Python dependencies
├── .streamlit/             # Streamlit configuration
│   └── config.toml
└── BOC_Dashboard_Guide.html # Complete user guide (printable as PDF)
```

---

## 🌍 Region Mapping (Currency → Region)

Since the dataset lacks explicit region fields, regions are inferred from currency:

| Currency | Region |
|---|---|
| IDR | Southeast Asia |
| USD | North America |
| INR | South Asia |
| AED / SAR | Middle East |
| NGN | West Africa |
| EUR | Western Europe |
| VND | Southeast Asia |

---

## 📄 License

This project is proprietary to **Bill-on-Chain**. All rights reserved.
