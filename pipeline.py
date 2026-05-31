"""
============================================================
  Real-Time E-Commerce Customer Data Engineering Pipeline
  Source: FakeStoreAPI (https://fakestoreapi.com)
  Author: Data Engineering Project
============================================================

Pipeline Flow:
  Extract → Transform → Load (SQLite) → Export (CSV for Power BI)

Run:  python pipeline.py
Schedule: python pipeline.py --schedule   (runs every 60 seconds)
"""

import sys
import requests
import sqlite3
import pandas as pd
import json
import os
import time
import logging
import argparse
from datetime import datetime, timedelta
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Setup ────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "data", "ecommerce.db")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
LOG_DIR    = os.path.join(BASE_DIR, "logs")

for _dir in (os.path.join(BASE_DIR, "data"), EXPORT_DIR, LOG_DIR):
    os.makedirs(_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "pipeline.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

API_BASE = "https://fakestoreapi.com"

# ═══════════════════════════════════════════════════════
#  EXTRACT LAYER
# ═══════════════════════════════════════════════════════

def fetch(endpoint: str) -> list:
    """Generic REST fetcher with retry logic."""
    url = f"{API_BASE}{endpoint}"
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            log.info(f"✅ Fetched {url}  [{len(r.json())} records]")
            return r.json()
        except Exception as e:
            log.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url} after 3 attempts")


def extract() -> dict:
    """
    Pull all raw data from FakeStoreAPI (real HTTP).
    Falls back to bundled realistic dataset if network is unavailable.
    Same JSON schema as the real API in both cases.
    """
    log.info("━━━ EXTRACT phase starting ━━━")
    try:
        data = {
            "products": fetch("/products"),
            "users":    fetch("/users"),
            "carts":    fetch("/carts"),
        }
        log.info("  Source: FakeStoreAPI (live)")
        return data
    except Exception as e:
        log.warning(f"  Live API unavailable ({e}). Using bundled realistic dataset.")
        from data_source import get_products, get_users, get_carts
        data = {
            "products": get_products(),
            "users":    get_users(),
            "carts":    get_carts(),
        }
        log.info(f"  Source: Local dataset | products={len(data['products'])} users={len(data['users'])} carts={len(data['carts'])}")
        return data

# ═══════════════════════════════════════════════════════
#  TRANSFORM LAYER
# ═══════════════════════════════════════════════════════

def transform_products(raw: list) -> pd.DataFrame:
    df = pd.json_normalize(raw)
    df.rename(columns={
        "id":               "product_id",
        "title":            "product_name",
        "category":         "category",
        "price":            "price",
        "description":      "description",
        "rating.rate":      "rating",
        "rating.count":     "review_count",
    }, inplace=True)
    df = df[["product_id","product_name","category","price","rating","review_count","description"]]
    df["price"]        = df["price"].astype(float).round(2)
    df["rating"]       = df["rating"].astype(float)
    df["review_count"] = df["review_count"].astype(int)
    df["price_tier"]   = pd.cut(
        df["price"],
        bins=[0, 25, 75, 200, 9999],
        labels=["Budget", "Mid-Range", "Premium", "Luxury"]
    )
    df["ingested_at"]  = datetime.now().isoformat()
    log.info(f"  Products transformed: {len(df)} rows")
    return df


def transform_users(raw: list) -> pd.DataFrame:
    rows = []
    for u in raw:
        addr = u.get("address", {})
        geo  = addr.get("geolocation", {})
        rows.append({
            "user_id":    u["id"],
            "email":      u["email"],
            "username":   u["username"],
            "first_name": u["name"]["firstname"],
            "last_name":  u["name"]["lastname"],
            "phone":      u.get("phone", ""),
            "city":       addr.get("city", ""),
            "street":     addr.get("street", ""),
            "zipcode":    addr.get("zipcode", ""),
            "lat":        float(geo.get("lat", 0)),
            "lon":        float(geo.get("long", 0)),
        })
    df = pd.DataFrame(rows)
    df["full_name"]    = df["first_name"].str.title() + " " + df["last_name"].str.title()
    df["email_domain"] = df["email"].str.split("@").str[1]
    # Simulate customer segment
    random.seed(42)
    df["customer_segment"] = random.choices(
        ["VIP", "Regular", "New", "At-Risk"],
        weights=[15, 50, 25, 10],
        k=len(df)
    )
    df["ingested_at"] = datetime.now().isoformat()
    log.info(f"  Users transformed: {len(df)} rows")
    return df


def transform_carts(raw: list, products_df: pd.DataFrame) -> pd.DataFrame:
    """Flatten nested cart → product items and enrich with product data."""
    rows = []
    for cart in raw:
        for item in cart.get("products", []):
            rows.append({
                "cart_id":    cart["id"],
                "user_id":    cart["userId"],
                "cart_date":  cart["date"],
                "product_id": item["productId"],
                "quantity":   item["quantity"],
            })
    df = pd.DataFrame(rows)

    # Enrich with product price
    price_map = products_df.set_index("product_id")["price"].to_dict()
    name_map  = products_df.set_index("product_id")["product_name"].to_dict()
    cat_map   = products_df.set_index("product_id")["category"].to_dict()

    df["unit_price"]   = df["product_id"].map(price_map).fillna(0)
    df["product_name"] = df["product_id"].map(name_map).fillna("Unknown")
    df["category"]     = df["product_id"].map(cat_map).fillna("Unknown")
    df["line_total"]   = (df["quantity"] * df["unit_price"]).round(2)
    df["cart_date"]    = pd.to_datetime(df["cart_date"])

    # Simulate order status
    random.seed(99)
    df["order_status"] = random.choices(
        ["Delivered", "Shipped", "Processing", "Cancelled"],
        weights=[55, 20, 15, 10],
        k=len(df)
    )
    df["ingested_at"] = datetime.now().isoformat()
    log.info(f"  Cart line items transformed: {len(df)} rows")
    return df


def build_customer_summary(users_df: pd.DataFrame, carts_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate KPIs per customer — classic RFM-style analysis."""
    now = datetime.now()
    agg = carts_df.groupby("user_id").agg(
        total_orders   = ("cart_id",    "nunique"),
        total_items    = ("quantity",   "sum"),
        total_spent    = ("line_total", "sum"),
        avg_order_val  = ("line_total", "mean"),
        last_order_dt  = ("cart_date",  "max"),
    ).reset_index()

    agg["days_since_last_order"] = (now - pd.to_datetime(agg["last_order_dt"]).dt.tz_localize(None)).dt.days
    agg["total_spent"]    = agg["total_spent"].round(2)
    agg["avg_order_val"]  = agg["avg_order_val"].round(2)

    df = users_df.merge(agg, on="user_id", how="left")
    df["total_spent"]  = df["total_spent"].fillna(0)
    df["total_orders"] = df["total_orders"].fillna(0)

    # RFM Score (simplified — handles small datasets gracefully)
    def safe_qcut(series, score_labels):
        try:
            return pd.qcut(series, len(score_labels), labels=score_labels, duplicates="drop").astype(float)
        except Exception:
            # Fallback: rank-based scoring for small datasets
            ranked = series.rank(pct=True)
            buckets = (ranked * (len(score_labels) - 0.001)).astype(int).clip(1, len(score_labels))
            return buckets.astype(float)

    df["rfm_score"] = (
        safe_qcut(df["total_spent"],                         [1,2,3,4]) * 0.5 +
        safe_qcut(df["total_orders"],                        [1,2,3,4]) * 0.3 +
        safe_qcut(df["days_since_last_order"].fillna(999),   [4,3,2,1]) * 0.2
    ).round(2)

    log.info(f"  Customer summary built: {len(df)} rows")
    return df


def transform(raw: dict) -> dict:
    log.info("━━━ TRANSFORM phase starting ━━━")
    products = transform_products(raw["products"])
    users    = transform_users(raw["users"])
    carts    = transform_carts(raw["carts"], products)
    summary  = build_customer_summary(users, carts)
    return {
        "products":         products,
        "users":            users,
        "carts":            carts,
        "customer_summary": summary,
    }

# ═══════════════════════════════════════════════════════
#  LOAD LAYER  (SQLite Data Warehouse)
# ═══════════════════════════════════════════════════════

def init_db(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id   INTEGER PRIMARY KEY,
            product_name TEXT,
            category     TEXT,
            price        REAL,
            price_tier   TEXT,
            rating       REAL,
            review_count INTEGER,
            description  TEXT,
            ingested_at  TEXT
        );
        CREATE TABLE IF NOT EXISTS dim_users (
            user_id          INTEGER PRIMARY KEY,
            email            TEXT,
            username         TEXT,
            full_name        TEXT,
            city             TEXT,
            zipcode          TEXT,
            email_domain     TEXT,
            customer_segment TEXT,
            ingested_at      TEXT
        );
        CREATE TABLE IF NOT EXISTS fact_orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id      INTEGER,
            user_id      INTEGER,
            cart_date    TEXT,
            product_id   INTEGER,
            product_name TEXT,
            category     TEXT,
            quantity     INTEGER,
            unit_price   REAL,
            line_total   REAL,
            order_status TEXT,
            ingested_at  TEXT
        );
        CREATE TABLE IF NOT EXISTS fact_customer_summary (
            user_id              INTEGER PRIMARY KEY,
            full_name            TEXT,
            city                 TEXT,
            customer_segment     TEXT,
            total_orders         INTEGER,
            total_items          INTEGER,
            total_spent          REAL,
            avg_order_val        REAL,
            days_since_last_order INTEGER,
            rfm_score            REAL,
            ingested_at          TEXT
        );
        CREATE TABLE IF NOT EXISTS pipeline_log (
            run_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at       TEXT,
            status       TEXT,
            records_loaded INTEGER,
            duration_sec REAL
        );
    """)
    conn.commit()


def load(tables: dict):
    log.info("━━━ LOAD phase starting ━━━")
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    mapping = {
        "dim_products":         ("products",         "replace"),
        "dim_users":            ("users",            "replace"),
        "fact_orders":          ("carts",            "replace"),
        "fact_customer_summary":("customer_summary", "replace"),
    }

    total = 0
    for table, (key, if_exists) in mapping.items():
        df = tables[key]
        df.to_sql(table, conn, if_exists=if_exists, index=False)
        log.info(f"  Loaded {len(df):>4} rows → {table}")
        total += len(df)

    conn.close()
    log.info(f"  Total rows loaded: {total}")
    return total

# ═══════════════════════════════════════════════════════
#  EXPORT LAYER  (DB tables for Power BI)
# ═══════════════════════════════════════════════════════

def export_for_powerbi(tables: dict):
    log.info("━━━ EXPORT phase (Power BI DB tables) ━━━")
    carts = tables["carts"]

    cat_rev = carts.groupby("category").agg(
        total_revenue=("line_total", "sum"),
        total_orders =("cart_id",    "nunique"),
        total_qty    =("quantity",   "sum"),
    ).reset_index()

    carts = carts.copy()
    carts["month"] = pd.to_datetime(carts["cart_date"]).dt.to_period("M").astype(str)
    monthly = carts.groupby("month").agg(
        revenue=("line_total", "sum"),
        orders =("cart_id",    "nunique"),
    ).reset_index()

    conn = sqlite3.connect(DB_PATH)
    cat_rev.to_sql("powerbi_category_revenue", conn, if_exists="replace", index=False)
    monthly.to_sql("powerbi_monthly_trend",    conn, if_exists="replace", index=False)
    conn.close()
    log.info("  Saved powerbi_category_revenue + powerbi_monthly_trend → ecommerce.db")

# ═══════════════════════════════════════════════════════
#  ORCHESTRATOR
# ═══════════════════════════════════════════════════════

def run_pipeline():
    start = time.time()
    log.info("╔══════════════════════════════════════════╗")
    log.info("║  E-Commerce Pipeline Run Started         ║")
    log.info(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                      ║")
    log.info("╚══════════════════════════════════════════╝")

    try:
        raw    = extract()
        tables = transform(raw)
        total  = load(tables)
        export_for_powerbi(tables)

        duration = round(time.time() - start, 2)
        # Log to DB
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO pipeline_log (run_at, status, records_loaded, duration_sec) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), "SUCCESS", total, duration)
        )
        conn.commit(); conn.close()

        log.info(f"✅ Pipeline completed in {duration}s | {total} records loaded")
        return True

    except Exception as e:
        log.error(f"❌ Pipeline failed: {e}", exc_info=True)
        return False


def run_scheduled(interval_sec=60):
    log.info(f"📅 Scheduled mode: running every {interval_sec}s. Ctrl+C to stop.")
    run_count = 0
    while True:
        run_count += 1
        log.info(f"\n🔄 Scheduled run #{run_count}")
        run_pipeline()
        log.info(f"💤 Sleeping {interval_sec}s until next run...")
        time.sleep(interval_sec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E-Commerce Data Pipeline")
    parser.add_argument("--schedule", action="store_true", help="Run on a schedule")
    parser.add_argument("--interval", type=int, default=60, help="Schedule interval in seconds")
    args = parser.parse_args()

    if args.schedule:
        run_scheduled(args.interval)
    else:
        run_pipeline()
