# 🛒 Real-Time E-Commerce Data Engineering Pipeline

A complete intermediate-level data engineering project that extracts live data
from a real REST API, transforms it through a multi-layer pipeline, stores it
in a SQLite data warehouse, and exports Power BI-ready CSVs with a live terminal dashboard.

---

## 🏗 Architecture

```
FakeStoreAPI (Real REST API)
        │
        ▼
   [ EXTRACT ]  ── HTTP GET → products, users, carts
        │
        ▼
   [ TRANSFORM ] ── Flatten · Enrich · RFM Scoring · Aggregations
        │
        ▼
   [ LOAD ]  ──── SQLite Data Warehouse (4 tables)
        │
   ┌────┴────┐
   ▼         ▼
[CSV Export]  [Live Dashboard]
(Power BI)   (Rich Terminal)
```

## 📁 Project Structure

```
ecommerce_pipeline/
│
├── pipeline.py              ← Main ETL orchestrator
├── requirements.txt
├── POWERBI_SETUP.py         ← DAX measures + Power BI guide
│
├── dashboard/
│   └── live_dashboard.py    ← Real-time terminal dashboard
│
├── data/
│   └── ecommerce.db         ← SQLite warehouse (auto-created)
│
├── exports/                 ← Power BI CSVs (auto-generated)
│   ├── powerbi_customers.csv
│   ├── powerbi_orders.csv
│   ├── powerbi_products.csv
│   ├── powerbi_category_revenue.csv
│   └── powerbi_monthly_trend.csv
│
└── logs/
    └── pipeline.log
```

## ⚙️ Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the pipeline (one-time)
python pipeline.py

# 3. Run scheduled (every 60 seconds)
python pipeline.py --schedule --interval 60

# 4. Launch live terminal dashboard
python dashboard/live_dashboard.py
```

## 🗄 Data Warehouse Schema

| Table                   | Type      | Description                        |
|-------------------------|-----------|------------------------------------|
| `dim_products`          | Dimension | Product catalog with price tiers   |
| `dim_users`             | Dimension | Customer profiles + segments       |
| `fact_orders`           | Fact      | Flattened order line items         |
| `fact_customer_summary` | Fact      | RFM aggregation per customer       |
| `pipeline_log`          | Audit     | Run history with status + duration |

## 📊 Transformations Applied

- **Flatten nested JSON** — cart items, user address, geolocation
- **Enrich orders** — join product name, category, price onto cart items
- **Price tiers** — Budget / Mid-Range / Premium / Luxury (pd.cut)
- **Customer segmentation** — VIP / Regular / New / At-Risk
- **RFM scoring** — Recency + Frequency + Monetary weighted score
- **Aggregations** — revenue by category, customer CLV, monthly trend

## 📈 Power BI Dashboard

Import the 5 CSV files from `exports/` into Power BI Desktop (free).
See `POWERBI_SETUP.py` for full step-by-step instructions including:
- Data type configuration
- Table relationships
- 10 DAX measures (Revenue, AOV, Cancellation Rate, MoM Growth…)
- Recommended visual layout

## 🌐 Data Source

**FakeStoreAPI** — https://fakestoreapi.com
- Free, no authentication required
- Real JSON REST endpoints: `/products`, `/users`, `/carts`
- 20 products, 10 users, 7 carts with nested product items
