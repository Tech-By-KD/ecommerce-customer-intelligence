# 🛒 Real-Time E-Commerce Data Engineering Pipeline

A complete intermediate-level data engineering project that extracts live data
from a real REST API, transforms it through a multi-layer pipeline, and stores it
in a SQLite data warehouse — directly connected to Power BI via ODBC.

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
   [ LOAD ]  ──── SQLite Data Warehouse (6 tables)
        │
   ┌────┴────┐
   ▼         ▼
[Power BI]  [Live Dashboard]
(ODBC)      (Rich Terminal)
```

## 📁 Project Structure

```
ecommercecustomerintelligence/
│
├── pipeline.py              ← Main ETL orchestrator
├── data_source.py           ← Fallback local dataset
├── live_dashboard.py        ← Real-time terminal dashboard
├── POWERBI_SETUP.py         ← DAX measures + Power BI guide
├── requirements.txt
├── .gitignore
│
├── data/
│   └── ecommerce.db         ← SQLite warehouse (auto-created)
│
└── logs/
    └── pipeline.log
```

## ⚙️ Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline (one-time)
python pipeline.py

# 4. Run scheduled (every 60 seconds)
python pipeline.py --schedule --interval 60

# 5. Launch live terminal dashboard
python live_dashboard.py
```

## 🗄 Data Warehouse Schema

| Table                      | Type      | Description                        |
|----------------------------|-----------|------------------------------------|
| `dim_products`             | Dimension | Product catalog with price tiers   |
| `dim_users`                | Dimension | Customer profiles + segments       |
| `fact_orders`              | Fact      | Flattened order line items         |
| `fact_customer_summary`    | Fact      | RFM aggregation per customer       |
| `powerbi_category_revenue` | Aggregate | Revenue + orders by category       |
| `powerbi_monthly_trend`    | Aggregate | Monthly revenue + order trend      |
| `pipeline_log`             | Audit     | Run history with status + duration |

## 📊 Transformations Applied

- **Flatten nested JSON** — cart items, user address, geolocation
- **Enrich orders** — join product name, category, price onto cart items
- **Price tiers** — Budget / Mid-Range / Premium / Luxury (pd.cut)
- **Customer segmentation** — VIP / Regular / New / At-Risk
- **RFM scoring** — Recency + Frequency + Monetary weighted score
- **Aggregations** — revenue by category, customer CLV, monthly trend

## 📈 Power BI Connection (ODBC)

Power BI connects directly to `ecommerce.db` via SQLite ODBC — no CSV files needed.

### One-time setup
1. Download and install the SQLite ODBC driver:
   👉 https://www.ch-werner.de/sqliteodbc/ → `sqliteodbc_w64.exe`

### Connect in Power BI
1. Get Data → **ODBC**
2. Expand **Advanced options** → paste connection string:
   ```
   Driver={SQLite3 ODBC Driver};Database=D:\ecommercecustomerintelligence\data\ecommerce.db;
   ```
3. Credentials prompt → select **Default or Custom** → Connect
4. Select all 6 tables in the Navigator → **Load**

### Refresh data
Re-run `python pipeline.py` then click **Refresh** in Power BI.

See `POWERBI_SETUP.py` for DAX measures, table relationships, and recommended visual layout.

## 🌐 Data Source

**FakeStoreAPI** — https://fakestoreapi.com
- Free, no authentication required
- Real JSON REST endpoints: `/products`, `/users`, `/carts`
- 20 products, 10 users, 7 carts with nested product items
- Falls back to local dataset (`data_source.py`) if API is unavailable
