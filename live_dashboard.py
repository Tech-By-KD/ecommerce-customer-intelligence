"""
============================================================
  Real-Time Terminal Dashboard for E-Commerce Pipeline
  Run AFTER pipeline.py has loaded data into SQLite
  Usage: python dashboard/live_dashboard.py
============================================================
"""

import sqlite3
import os
import time
from datetime import datetime

try:
    from rich.console import Console
    from rich.table   import Table
    from rich.panel   import Panel
    from rich.layout  import Layout
    from rich.live    import Live
    from rich.text    import Text
    from rich import   box
    RICH = True
except ImportError:
    RICH = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "ecommerce.db")

console = Console()

# ── Queries ────────────────────────────────────────────

def get_kpis(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dim_users")
    customers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fact_orders")
    orders = cur.fetchone()[0]
    cur.execute("SELECT ROUND(SUM(line_total),2) FROM fact_orders")
    revenue = cur.fetchone()[0] or 0
    cur.execute("SELECT ROUND(AVG(line_total),2) FROM fact_orders")
    aov = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM fact_orders WHERE order_status='Cancelled'")
    cancelled = cur.fetchone()[0]
    return customers, orders, revenue, aov, cancelled


def get_category_revenue(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT category,
               ROUND(SUM(line_total),2) AS revenue,
               SUM(quantity)            AS units
        FROM fact_orders
        GROUP BY category
        ORDER BY revenue DESC
    """)
    return cur.fetchall()


def get_top_customers(conn, n=5):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT cs.full_name, cs.city, cs.customer_segment,
               cs.total_orders, ROUND(cs.total_spent,2) AS spent,
               cs.rfm_score
        FROM fact_customer_summary cs
        ORDER BY spent DESC
        LIMIT {n}
    """)
    return cur.fetchall()


def get_top_products(conn, n=5):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT product_name, category,
               SUM(quantity)             AS units_sold,
               ROUND(SUM(line_total),2)  AS revenue
        FROM fact_orders
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT {n}
    """)
    return cur.fetchall()


def get_order_status_dist(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT order_status, COUNT(*) AS cnt
        FROM fact_orders
        GROUP BY order_status
        ORDER BY cnt DESC
    """)
    return cur.fetchall()


def get_pipeline_log(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT run_at, status, records_loaded, duration_sec
        FROM pipeline_log
        ORDER BY run_id DESC
        LIMIT 5
    """)
    return cur.fetchall()

# ── Rich rendering ──────────────────────────────────────

def bar(value, max_val, width=20):
    filled = int((value / max_val) * width) if max_val > 0 else 0
    return "█" * filled + "░" * (width - filled)


def build_dashboard():
    conn = sqlite3.connect(DB_PATH)
    customers, orders, revenue, aov, cancelled = get_kpis(conn)

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="kpis",   size=7),
        Layout(name="middle"),
        Layout(name="bottom"),
    )
    layout["middle"].split_row(Layout(name="cat"), Layout(name="status"))
    layout["bottom"].split_row(Layout(name="top_cust"), Layout(name="top_prod"))

    # Header
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    layout["header"].update(
        Panel(Text(f"🛒  E-Commerce Real-Time Dashboard   |   {ts}", justify="center", style="bold cyan"),
              style="bold blue")
    )

    # KPIs
    kpi_table = Table(box=box.SIMPLE_HEAD, expand=True, show_header=False)
    kpi_table.add_column("", style="bold yellow", justify="center")
    kpi_table.add_column("", style="bold white",  justify="center")
    kpi_table.add_column("", style="bold yellow", justify="center")
    kpi_table.add_column("", style="bold white",  justify="center")
    kpi_table.add_column("", style="bold yellow", justify="center")
    kpi_table.add_column("", style="bold white",  justify="center")
    kpi_table.add_row(
        "👥 CUSTOMERS", str(customers),
        "🛍️  ORDERS",    str(orders),
        "💰 REVENUE",   f"${revenue:,.2f}",
    )
    kpi_table.add_row(
        "📦 AVG ORDER", f"${aov:.2f}",
        "❌ CANCELLED",  str(cancelled),
        "📈 CONV RATE",  f"{(orders/max(customers,1)*100):.1f}%",
    )
    layout["kpis"].update(Panel(kpi_table, title="[bold cyan]Key Metrics", border_style="cyan"))

    # Category Revenue
    cat_data = get_category_revenue(conn)
    cat_table = Table(box=box.SIMPLE, expand=True)
    cat_table.add_column("Category",  style="cyan",  no_wrap=True)
    cat_table.add_column("Revenue $", style="green", justify="right")
    cat_table.add_column("Units",     style="white", justify="right")
    cat_table.add_column("Bar",       style="yellow")
    max_rev = max((r[1] for r in cat_data), default=1)
    for cat, rev, units in cat_data:
        cat_table.add_row(cat, f"${rev:,.2f}", str(units), bar(rev, max_rev, 15))
    layout["cat"].update(Panel(cat_table, title="[bold green]Revenue by Category", border_style="green"))

    # Order Status
    stat_data = get_order_status_dist(conn)
    stat_table = Table(box=box.SIMPLE, expand=True)
    stat_table.add_column("Status",  style="cyan")
    stat_table.add_column("Count",   style="white", justify="right")
    stat_table.add_column("Bar",     style="magenta")
    max_cnt = max((s[1] for s in stat_data), default=1)
    colors = {"Delivered":"green","Shipped":"blue","Processing":"yellow","Cancelled":"red"}
    for status, cnt in stat_data:
        c = colors.get(status, "white")
        stat_table.add_row(f"[{c}]{status}[/{c}]", str(cnt), bar(cnt, max_cnt, 12))
    layout["status"].update(Panel(stat_table, title="[bold magenta]Order Status", border_style="magenta"))

    # Top Customers
    cust_data = get_top_customers(conn)
    cust_table = Table(box=box.SIMPLE, expand=True)
    cust_table.add_column("Name",    style="cyan",   no_wrap=True)
    cust_table.add_column("Segment", style="yellow")
    cust_table.add_column("Orders",  style="white",  justify="right")
    cust_table.add_column("Spent",   style="green",  justify="right")
    cust_table.add_column("RFM",     style="magenta",justify="right")
    for name, city, seg, ords, spent, rfm in cust_data:
        cust_table.add_row(name, seg, str(int(ords)), f"${spent:.2f}", str(rfm or ""))
    layout["top_cust"].update(Panel(cust_table, title="[bold yellow]Top Customers", border_style="yellow"))

    # Top Products
    prod_data = get_top_products(conn)
    prod_table = Table(box=box.SIMPLE, expand=True)
    prod_table.add_column("Product", style="cyan",  no_wrap=True, max_width=22)
    prod_table.add_column("Cat",     style="white", no_wrap=True, max_width=14)
    prod_table.add_column("Units",   style="white", justify="right")
    prod_table.add_column("Revenue", style="green", justify="right")
    for name, cat, units, rev in prod_data:
        prod_table.add_row(name[:22], cat[:14], str(units), f"${rev:.2f}")
    layout["top_prod"].update(Panel(prod_table, title="[bold blue]Top Products", border_style="blue"))

    conn.close()
    return layout


def run_live(refresh_sec=5):
    console.print("[bold cyan]Starting live dashboard... Press Ctrl+C to exit[/bold cyan]")
    time.sleep(1)
    with Live(build_dashboard(), refresh_per_second=1, screen=True) as live:
        while True:
            time.sleep(refresh_sec)
            live.update(build_dashboard())


def run_static():
    """Fallback plain-text dashboard (no rich installed)."""
    conn = sqlite3.connect(DB_PATH)
    customers, orders, revenue, aov, cancelled = get_kpis(conn)
    print("\n" + "="*50)
    print("  E-Commerce Dashboard")
    print("="*50)
    print(f"  Customers : {customers}")
    print(f"  Orders    : {orders}")
    print(f"  Revenue   : ${revenue:,.2f}")
    print(f"  Avg Order : ${aov:.2f}")
    print(f"  Cancelled : {cancelled}")
    print("\n  Category Revenue:")
    for row in get_category_revenue(conn):
        print(f"    {row[0]:<25} ${row[1]:>8,.2f}  ({row[2]} units)")
    print("\n  Top 5 Customers:")
    for row in get_top_customers(conn):
        print(f"    {row[0]:<20} {row[2]:<10} ${row[4]:>8,.2f}")
    print("="*50)
    conn.close()


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("❌  Database not found. Run pipeline.py first.")
        exit(1)
    if RICH:
        run_live(refresh_sec=5)
    else:
        print("⚠️  rich not installed. Showing static view.")
        run_static()
