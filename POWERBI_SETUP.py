# Power BI Setup Guide — E-Commerce Dashboard
# ================================================
# This file contains all DAX measures and setup steps
# for the free Power BI Desktop dashboard.

# ──────────────────────────────────────────────────────
#  STEP 1: IMPORT CSV FILES INTO POWER BI
# ──────────────────────────────────────────────────────
#
#  Open Power BI Desktop (free at powerbi.microsoft.com/desktop)
#
#  Home → Get Data → Text/CSV → import all 5 files:
#   - powerbi_customers.csv       → table: Customers
#   - powerbi_orders.csv          → table: Orders
#   - powerbi_products.csv        → table: Products
#   - powerbi_category_revenue.csv → table: CategoryRevenue
#   - powerbi_monthly_trend.csv   → table: MonthlyTrend

# ──────────────────────────────────────────────────────
#  STEP 2: SET DATA TYPES (Transform Data / Power Query)
# ──────────────────────────────────────────────────────
#
#  Orders table:
#    cart_date    → Date
#    quantity     → Whole Number
#    unit_price   → Decimal Number
#    line_total   → Decimal Number
#
#  Customers table:
#    total_spent  → Decimal Number
#    rfm_score    → Decimal Number
#
#  Products table:
#    price        → Decimal Number
#    rating       → Decimal Number

# ──────────────────────────────────────────────────────
#  STEP 3: CREATE RELATIONSHIPS (Model view)
# ──────────────────────────────────────────────────────
#
#  Orders[user_id]    → Customers[user_id]     (Many-to-One)
#  Orders[product_id] → Products[product_id]   (Many-to-One)

# ──────────────────────────────────────────────────────
#  STEP 4: DAX MEASURES  (Home → New Measure)
# ──────────────────────────────────────────────────────

# Paste each block into a new measure in Power BI:

"""
Total Revenue =
    SUMX(Orders, Orders[line_total])

Total Orders =
    COUNTROWS(Orders)

Unique Customers =
    DISTINCTCOUNT(Orders[user_id])

Average Order Value =
    DIVIDE([Total Revenue], [Total Orders], 0)

Cancellation Rate % =
    DIVIDE(
        COUNTROWS(FILTER(Orders, Orders[order_status] = "Cancelled")),
        [Total Orders],
        0
    ) * 100

Top Category =
    TOPN(1,
        SUMMARIZE(Orders, Orders[category], "Rev", [Total Revenue]),
        [Rev], DESC
    )

MoM Revenue Growth % =
    VAR CurrentMonth = MAX(MonthlyTrend[month])
    VAR ThisRev = CALCULATE([Total Revenue],
        FILTER(MonthlyTrend, MonthlyTrend[month] = CurrentMonth))
    VAR PrevRev = CALCULATE([Total Revenue],
        FILTER(MonthlyTrend,
            MonthlyTrend[month] = EARLIER(MonthlyTrend[month]) - 1))
    RETURN DIVIDE(ThisRev - PrevRev, PrevRev, 0) * 100

Customer Lifetime Value =
    AVERAGE(Customers[total_spent])

VIP Customer Count =
    COUNTROWS(
        FILTER(Customers, Customers[customer_segment] = "VIP")
    )

At-Risk Customer Count =
    COUNTROWS(
        FILTER(Customers, Customers[customer_segment] = "At-Risk")
    )
"""

# ──────────────────────────────────────────────────────
#  STEP 5: BUILD VISUALS
# ──────────────────────────────────────────────────────
#
#  Recommended Dashboard Layout (1 page):
#
#  ROW 1 — KPI Cards (5 cards across):
#    • Total Revenue          (measure: Total Revenue)
#    • Total Orders           (measure: Total Orders)
#    • Unique Customers       (measure: Unique Customers)
#    • Avg Order Value        (measure: Average Order Value)
#    • Cancellation Rate      (measure: Cancellation Rate %)
#
#  ROW 2 — Charts:
#    • Bar Chart  → Category Revenue by category (CategoryRevenue table)
#    • Donut      → Order Status distribution    (Orders[order_status])
#    • Line Chart → Monthly Revenue Trend        (MonthlyTrend[month] vs revenue)
#
#  ROW 3 — Tables:
#    • Customer Segment breakdown  (Customers[customer_segment], count, avg spent)
#    • Top Products table          (Products[product_name], total revenue)
#
#  OPTIONAL — Map Visual:
#    • Bubble map using Customers[lat] and Customers[lon]
#      (requires enabling map visuals in Power BI settings)
#
# ──────────────────────────────────────────────────────
#  STEP 6: THEME & FORMATTING
# ──────────────────────────────────────────────────────
#
#  View → Themes → choose "Executive" or "Frontier"
#  Add title: "E-Commerce Customer Intelligence Dashboard"
#  Add last-refresh text box using: =NOW()  in a card
#
# ──────────────────────────────────────────────────────
#  STEP 7: REFRESH DATA (after each pipeline run)
# ──────────────────────────────────────────────────────
#
#  Each time you run:  python pipeline.py
#  New CSVs are written to exports/ folder.
#
#  In Power BI Desktop:  Home → Refresh
#  All visuals update automatically from the new CSVs.
#
#  For AUTO-REFRESH (Power BI Pro needed for web service,
#  but for local use):
#    - Run:  python pipeline.py --schedule --interval 300
#    - In Power BI: set scheduled refresh to 5-minute intervals
#      using Power BI Desktop's "Refresh" button or a macro.
