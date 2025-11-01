# profit_analysis_starter.py
# Project 2: Production Cost & Profitability Analysis
# Run with: python profit_analysis_starter.py

import pandas as pd
import matplotlib.pyplot as plt

# 1) Load data
prod = pd.read_csv("prod_costs_6mo.csv", parse_dates=["date"])
sales = pd.read_csv("sales_6mo.csv", parse_dates=["date"])

# 2) Aggregate production to daily totals per product
prod_daily = prod.groupby(["date","product"]).agg(
    units_produced=("units_produced","sum"),
    scrap_units=("scrap_units","sum"),
    unit_mfg_cost=("unit_mfg_cost","mean"),  # assume stable
).reset_index()

# 3) Merge with sales
df = pd.merge(sales, prod_daily, on=["date","product"], how="left")

# 4) Compute KPIs
df["net_price"] = df["unit_price"] * (1 - df["discount_rate"])
df["revenue"] = df["units_sold"] * df["net_price"]
df["scrap_cost"] = df["scrap_units"] * df["unit_mfg_cost"]
df["cogs"] = df["units_sold"] * df["unit_mfg_cost"]
df["gross_profit"] = df["revenue"] - (df["cogs"] + df["scrap_cost"])
df["gross_margin_pct"] = (df["gross_profit"] / df["revenue"]).replace([pd.NA, pd.NaT], 0) * 100

# 5) Daily summary (all products)
daily = df.groupby("date").agg(
    revenue=("revenue","sum"),
    cogs=("cogs","sum"),
    scrap_cost=("scrap_cost","sum"),
    gross_profit=("gross_profit","sum")
).reset_index()
daily["gross_margin_pct"] = (daily["gross_profit"] / daily["revenue"]) * 100

# 6) Monthly by product
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
monthly_prod = df.groupby(["month","product"]).agg(
    revenue=("revenue","sum"),
    cogs=("cogs","sum"),
    scrap_cost=("scrap_cost","sum"),
    gross_profit=("gross_profit","sum"),
    units_sold=("units_sold","sum")
).reset_index()
monthly_prod["gross_margin_pct"] = (monthly_prod["gross_profit"] / monthly_prod["revenue"]) * 100

# 7) Save outputs for Excel/Power BI
daily.to_csv("p2_daily_summary.csv", index=False)
monthly_prod.to_csv("p2_monthly_product_summary.csv", index=False)
df.to_csv("p2_detailed_joined.csv", index=False)

print("Saved: p2_daily_summary.csv, p2_monthly_product_summary.csv, p2_detailed_joined.csv")

# 8) Quick visuals
# Note: Running these plots will open windows. Comment out if running in headless mode.
daily.plot(x="date", y="gross_profit", title="Daily Gross Profit")
plt.tight_layout()
plt.show()

monthly_pivot = monthly_prod.pivot_table(index="month", columns="product", values="gross_profit", aggfunc="sum").fillna(0)
monthly_pivot.plot(title="Monthly Gross Profit by Product")
plt.tight_layout()
plt.show()
