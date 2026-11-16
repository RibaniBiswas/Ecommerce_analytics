
# ==========================================================
# OLIST E-COMMERCE INTELLIGENCE DASHBOARD
# Interactive HTML Dashboard
# ==========================================================

from pathlib import Path
import sys
import warnings

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

warnings.filterwarnings("ignore")

# ---------------- PROJECT PATHS ----------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "dashboard"

OUTPUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader


# ---------------- DESIGN THEME ----------------

COLORS = {
    "background": "#080E1D",
    "panel": "#111C32",
    "panel_light": "#192943",
    "cyan": "#22D3EE",
    "purple": "#A78BFA",
    "teal": "#2DD4BF",
    "green": "#34D399",
    "orange": "#FBBF24",
    "red": "#FB7185",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
    "border": "rgba(148,163,184,0.18)"
}


pio.templates["olist_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Segoe UI, sans-serif",
            color="#EAF4FF",
            size=11
        ),

        title=dict(
            font=dict(
                size=16,
                color="#F8FAFC"
            ),
            x=0.5,
            xanchor="center"
        ),

        margin=dict(l=55, r=35, t=55, b=50),

        xaxis=dict(
            gridcolor="rgba(148,163,184,0.09)",
            zerolinecolor="rgba(148,163,184,0.12)",
            linecolor="rgba(148,163,184,0.15)",
            tickfont=dict(color="#A8B8D0"),
            title_font=dict(color="#A8B8D0")
        ),

        yaxis=dict(
            gridcolor="rgba(148,163,184,0.09)",
            zerolinecolor="rgba(148,163,184,0.12)",
            linecolor="rgba(148,163,184,0.15)",
            tickfont=dict(color="#A8B8D0"),
            title_font=dict(color="#A8B8D0")
        ),

        colorway=[
            "#32E6FF",
            "#A78BFA",
            "#35E0C1",
            "#FF79C6",
            "#FBBF24",
            "#60A5FA"
        ],

        hoverlabel=dict(
            bgcolor="#17243B",
            bordercolor="#32E6FF",
            font=dict(
                color="#FFFFFF",
                size=12
            )
        )
    )
)

px.defaults.template = "olist_dark"



# ---------------- LOAD DATA ----------------

def load_data():

    loader = DataLoader(str(RAW_DIR))
    datasets = loader.load_data()

    required = [
        "orders",
        "order_items",
        "customers",
        "payments",
        "reviews",
        "products",
        "category_translation"
    ]

    missing = [name for name in required if name not in datasets]

    if missing:
        raise ValueError(f"Missing datasets: {missing}")

    print("Olist datasets loaded successfully.")

    for name, dataframe in datasets.items():
        print(f"{name}: {dataframe.shape}")

    return datasets



# ---------------- DATA PREPARATION ----------------

def prepare_data(datasets):

    orders = datasets["orders"].copy()
    items = datasets["order_items"].copy()
    customers = datasets["customers"].copy()
    products = datasets["products"].copy()
    reviews = datasets["reviews"].copy()
    payments = datasets["payments"].copy()
    translations = datasets["category_translation"].copy()

    # Convert date columns
    date_columns = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:
        if column in orders.columns:
            orders[column] = pd.to_datetime(
                orders[column], errors="coerce"
            )

    # Add customer state to orders
    orders = orders.merge(
        customers[["customer_id", "customer_state"]],
        on="customer_id",
        how="left"
    )

    # Add product details to order items
    sales = items.merge(
        products[["product_id", "product_category_name"]],
        on="product_id",
        how="left"
    )

    # Translate product categories
    sales = sales.merge(
        translations,
        on="product_category_name",
        how="left"
    )

    if "product_category_name_english" in sales.columns:
        sales["Category"] = (
            sales["product_category_name_english"]
            .fillna(sales["product_category_name"])
            .fillna("Unknown")
        )
    else:
        sales["Category"] = (
            sales["product_category_name"].fillna("Unknown")
        )

    # Attach order and customer information
    sales = sales.merge(
        orders[
            [
                "order_id",
                "customer_id",
                "customer_state",
                "order_purchase_timestamp",
                "order_status"
            ]
        ],
        on="order_id",
        how="left"
    )

    # Calculate revenue per order
    order_revenue = (
        items.groupby("order_id")["price"]
        .sum()
        .reset_index(name="revenue")
    )

    # Delivery analysis
    delivery = orders[
        [
            "order_id",
            "order_status",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    ].copy()

    valid_delivery = delivery[
        (delivery["order_status"] == "delivered") &
        delivery["order_delivered_customer_date"].notna() &
        delivery["order_estimated_delivery_date"].notna()
    ].copy()

    valid_delivery["Delivery_Days"] = (
        valid_delivery["order_delivered_customer_date"] -
        orders.set_index("order_id")
        .reindex(valid_delivery["order_id"])
        ["order_purchase_timestamp"].values
    ).dt.total_seconds() / 86400

    valid_delivery["is_late"] = (
        valid_delivery["order_delivered_customer_date"] >
        valid_delivery["order_estimated_delivery_date"]
    )

    # Review analysis
    review_data = reviews[
        ["order_id", "review_score"]
    ].copy()

    # Payment analysis
    payment_data = payments[
        ["order_id", "payment_type", "payment_value"]
    ].copy()

    return {
        "orders": orders,
        "customers": customers,
        "items": items,
        "sales": sales,
        "order_revenue": order_revenue,
        "delivery": valid_delivery,
        "reviews": review_data,
        "payments": payment_data
    }


# ---------------- KPI CALCULATIONS ----------------

def calculate_kpis(data):

    total_revenue = data["items"]["price"].sum()

    total_orders = data["orders"]["order_id"].nunique()

    average_order_value = (
        data["order_revenue"]["revenue"].mean()
    )

    average_review_score = (
        data["reviews"]["review_score"].mean()
    )

    delivery = data["delivery"]

    late_delivery_percentage = (
        delivery["is_late"].mean() * 100
        if not delivery.empty else 0
    )

    return {
        "Total Revenue": total_revenue,
        "Total Orders": total_orders,
        "Average Order Value": average_order_value,
        "Average Review Score": average_review_score,
        "Late Delivery Percentage": late_delivery_percentage
    }

# ---------------- 3D KPI CARD DESIGN ----------------

# ---------------- CHART 1: MONTHLY REVENUE ----------------


# ---------------- CHART 1: MONTHLY REVENUE ----------------

def create_revenue_chart(data):

    sales = data["sales"].copy()

    # Remove rows without purchase dates
    sales = sales.dropna(
        subset=["order_purchase_timestamp"]
    )

    sales["Month"] = (
        sales["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        sales.groupby("Month", as_index=False)["price"]
        .sum()
        .rename(columns={"price": "Revenue"})
        .sort_values("Month")
    )

    fig = go.Figure()

    # Soft glow layer
    fig.add_trace(go.Scatter(
        x=monthly["Month"],
        y=monthly["Revenue"],
        mode="lines",
        line=dict(
            color="rgba(34,211,238,0.20)",
            width=11,
            shape="spline"
        ),
        hoverinfo="skip",
        showlegend=False
    ))

    # Main revenue line
    fig.add_trace(go.Scatter(
        x=monthly["Month"],
        y=monthly["Revenue"],
        mode="lines+markers",
        line=dict(
            color="#32E6FF",
            width=3,
            shape="spline"
        ),
        marker=dict(
            size=7,
            color="#32E6FF",
            line=dict(color="#FFFFFF", width=1.2)
        ),
        fill="tozeroy",
        fillcolor="rgba(50,230,255,0.10)",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: R$ %{y:,.2f}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        template="olist_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="Monthly Revenue Performance",
            font=dict(size=16, color="#F8FAFC")
        ),
        height=430,
        showlegend=False,
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title="Revenue (R$)"
    )

    fig.update_xaxes(
        tickangle=-30,
        showgrid=False
    )

    return fig



# ---------------- CHART 2: CATEGORY PERFORMANCE ----------------

def create_category_chart(data):

    sales = data["sales"].copy()

    category = (
        sales.groupby("Category", as_index=False)["price"]
        .sum()
        .rename(columns={"price": "Revenue"})
        .nlargest(10, "Revenue")
        .sort_values("Revenue", ascending=True)
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=category["Revenue"],
        y=category["Category"],
        orientation="h",
        marker=dict(
            color=category["Revenue"],
            colorscale=[
                [0, "#4338CA"],
                [0.5, "#6366F1"],
                [1, "#22D3EE"]
            ],
            line=dict(width=0)
        ),
        text=category["Revenue"].apply(
            lambda value: f"R$ {value:,.0f}"
        ),
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Revenue: R$ %{x:,.2f}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        template="olist_dark",
        title=dict(
            text="Top 10 Product Categories",
            font=dict(size=15, color=COLORS["text"])
        ),
        height=430,
        showlegend=False,
        xaxis_title="Revenue (R$)",
        yaxis_title=None,
        margin=dict(l=120, r=55, t=50, b=35)
    )

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=False)

    return fig

# ---------------- CHART 3: STATE PERFORMANCE ----------------

def create_state_chart(data):

    sales = data["sales"].copy()

    state_data = (
        sales.dropna(subset=["customer_state"])
        .groupby("customer_state")
        .agg(
            Revenue=("price", "sum"),
            Orders=("order_id", "nunique")
        )
        .reset_index()
        .nlargest(10, "Revenue")
        .sort_values("Revenue", ascending=True)
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=state_data["Revenue"],
        y=state_data["customer_state"],
        orientation="h",
        marker=dict(
            color=state_data["Revenue"],
            colorscale=[
                [0, "#4338CA"],
                [0.5, "#8B5CF6"],
                [1, "#22D3EE"]
            ],
            line=dict(width=0)
        ),
        customdata=state_data["Orders"],
        hovertemplate=(
            "<b>State: %{y}</b><br>"
            "Revenue: R$ %{x:,.2f}<br>"
            "Orders: %{customdata:,}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        template="olist_dark",
        title="Top 10 Brazilian States by Revenue",
        height=430,
        showlegend=False,
        xaxis_title="Revenue (R$)",
        yaxis_title="State",
        margin=dict(l=55, r=25, t=50, b=40)
    )

    return fig


# ---------------- CHART 4: DELIVERY VS REVIEWS ----------------

def create_delivery_review_chart(data):

    delivery = data["delivery"].copy()
    reviews = data["reviews"].copy()

    comparison = delivery.merge(
        reviews,
        on="order_id",
        how="inner"
    )

    comparison = comparison.dropna(
        subset=["review_score", "is_late"]
    )

    comparison["Delivery Status"] = np.where(
        comparison["is_late"],
        "Late Delivery",
        "On-Time Delivery"
    )

    fig = go.Figure()

    colors = {
        "On-Time Delivery": "#22D3EE",
        "Late Delivery": "#FB7185"
    }

    for status in ["On-Time Delivery", "Late Delivery"]:

        scores = comparison.loc[
            comparison["Delivery Status"] == status,
            "review_score"
        ]

        fig.add_trace(go.Box(
            y=scores,
            name=status,
            marker_color=colors[status],
            line=dict(color=colors[status], width=2),
            fillcolor=(
                "rgba(34,211,238,0.18)"
                if status == "On-Time Delivery"
                else "rgba(251,113,133,0.18)"
            ),
            boxmean=True,
            hovertemplate=(
                f"<b>{status}</b><br>"
                "Review Score: %{y}<extra></extra>"
            )
        ))

    fig.update_layout(
        template="olist_dark",
        title="Delivery Status vs Customer Review",
        height=430,
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Customer Review Score",
        yaxis=dict(
            range=[0.5, 5.5],
            dtick=1
        )
    )

    return fig





# ---------------- CHART 5: PAYMENT METHODS ----------------

def create_payment_chart(data):

    payments = data["payments"].copy()

    payment_summary = (
        payments.groupby("payment_type", as_index=False)["payment_value"]
        .sum()
        .sort_values("payment_value", ascending=False)
    )

    fig = go.Figure(go.Pie(
        labels=payment_summary["payment_type"].str.replace("_", " ").str.title(),
        values=payment_summary["payment_value"],
        hole=0.62,
        sort=False,
        marker=dict(
            colors=["#22D3EE", "#A78BFA", "#2DD4BF", "#FBBF24", "#FB7185", "#60A5FA"],
            line=dict(color="#111C32", width=3)
        ),
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Payment Value: R$ %{value:,.2f}<br>"
            "Share: %{percent}<extra></extra>"
        )
    ))

    fig.update_layout(
        template="olist_dark",
        title="Payment Method Distribution",
        height=430,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#A8B8D0")
        ),
        margin=dict(l=25, r=25, t=55, b=45)
    )

    return fig


# ---------------- CHART 6: ORDER STATUS ----------------
def create_order_status_chart(data):

    status_data = (
        data["orders"]["order_status"]
        .fillna("unknown")
        .str.replace("_", " ")
        .str.title()
        .value_counts()
        .rename_axis("Order Status")
        .reset_index(name="Orders")
    )

    # A horizontal bar chart makes it easier to compare order volumes
    # across statuses than a second circular chart beside payment methods.
    status_data = status_data.sort_values("Orders", ascending=True)

    fig = go.Figure(go.Bar(
        x=status_data["Orders"],
        y=status_data["Order Status"],
        orientation="h",
        marker=dict(
            color=status_data["Orders"],
            colorscale=[[0, "#4338CA"], [0.55, "#8B5CF6"], [1, "#22D3EE"]],
            line=dict(width=0)
        ),
        text=status_data["Orders"].map(lambda value: f"{value:,}"),
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Orders: %{x:,}<extra></extra>"
    ))

    fig.update_layout(
        template="olist_dark",
        title="Orders by Status",
        height=430,
        showlegend=False,
        xaxis_title="Number of Orders",
        yaxis_title=None,
        yaxis=dict(automargin=True),
        margin=dict(l=35, r=55, t=55, b=45)
    )
    return fig


# ---------------- CREATE CHART HTML ----------------


# ---------------- CREATE CHART HTML ----------------


def calculate_customer_insights(data):
    """Build customer-level RFM metrics from Olist orders and order items."""
    orders = data["orders"].copy()
    items = data["items"].copy()

    required_order_cols = {"order_id", "customer_id", "order_purchase_timestamp"}
    if not required_order_cols.issubset(orders.columns):
        raise ValueError("Orders data is missing columns needed for customer analysis.")

    # Map each order to the stable customer_unique_id (customer_id changes per order).
    customers = data.get("customers")
    if customers is None or "customer_unique_id" not in customers.columns:
        raise ValueError("Customer data must contain customer_unique_id for repeat-customer analysis.")

    order_customer = orders[["order_id", "customer_id", "order_purchase_timestamp"]].merge(
        customers[["customer_id", "customer_unique_id"]].drop_duplicates("customer_id"),
        on="customer_id", how="left"
    )
    order_values = items.groupby("order_id", as_index=False)["price"].sum().rename(columns={"price": "order_revenue"})
    order_customer = order_customer.merge(order_values, on="order_id", how="left")
    order_customer["order_revenue"] = order_customer["order_revenue"].fillna(0)
    order_customer["order_purchase_timestamp"] = pd.to_datetime(order_customer["order_purchase_timestamp"], errors="coerce")
    order_customer = order_customer.dropna(subset=["customer_unique_id", "order_purchase_timestamp"])

    if order_customer.empty:
        raise ValueError("No valid customer orders were found for Customer Insights.")

    snapshot = order_customer["order_purchase_timestamp"].max().normalize() + pd.Timedelta(days=1)
    rfm = order_customer.groupby("customer_unique_id").agg(
        Recency=("order_purchase_timestamp", lambda x: (snapshot - x.max().normalize()).days),
        Frequency=("order_id", "nunique"),
        Monetary=("order_revenue", "sum")
    ).reset_index()

    # Rank-based scores remain stable even when many customers have identical values.
    rfm["R"] = pd.qcut(rfm["Recency"].rank(method="first", ascending=False), 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)

    def segment(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4 and m >= 4: return "Champions"
        if r >= 3 and f >= 4: return "Loyal Customers"
        if r >= 4 and f >= 2: return "Potential Loyalists"
        if r >= 4 and f == 1: return "New Customers"
        if r <= 2 and f >= 3: return "At Risk"
        return "Lost / Hibernating"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm


def create_customer_charts(data):
    rfm = calculate_customer_insights(data)
    segment_order = ["Champions", "Loyal Customers", "Potential Loyalists", "New Customers", "At Risk", "Lost / Hibernating"]
    segment_summary = (rfm.groupby("Segment", as_index=False).agg(Customers=("customer_unique_id", "count"), Revenue=("Monetary", "sum")))
    segment_summary["Segment"] = pd.Categorical(segment_summary["Segment"], categories=segment_order, ordered=True)
    segment_summary = segment_summary.sort_values("Segment")

    segment_fig = px.bar(segment_summary, x="Customers", y="Segment", orientation="h",
        title="CUSTOMER SEGMENT DISTRIBUTION", text="Customers",
        color="Segment", color_discrete_sequence=["#22D3EE", "#2DD4BF", "#A78BFA", "#34D399", "#FBBF24", "#FB7185"])
    segment_fig.update_layout(height=360, showlegend=False, yaxis={"categoryorder":"array", "categoryarray":segment_order},
        margin=dict(l=12,r=25,t=55,b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F4F7FF")
    segment_fig.update_traces(textposition="outside", cliponaxis=False)

    revenue_fig = px.bar(segment_summary, x="Revenue", y="Segment", orientation="h",
        title="REVENUE CONTRIBUTION BY CUSTOMER SEGMENT", text="Revenue",
        color="Segment", color_discrete_sequence=["#22D3EE", "#2DD4BF", "#A78BFA", "#34D399", "#FBBF24", "#FB7185"])
    revenue_fig.update_layout(height=360, showlegend=False, yaxis={"categoryorder":"array", "categoryarray":segment_order},
        margin=dict(l=12,r=25,t=55,b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F4F7FF", xaxis_title="Revenue (R$)")
    revenue_fig.update_traces(texttemplate="R$ %{x:,.0f}", textposition="outside", cliponaxis=False)

    behaviour_fig = px.scatter(rfm, x="Frequency", y="Monetary", color="Segment",
        hover_data={"Recency":True, "customer_unique_id":False}, title="PURCHASE FREQUENCY VS CUSTOMER SPEND",
        color_discrete_sequence=["#22D3EE", "#2DD4BF", "#A78BFA", "#34D399", "#FBBF24", "#FB7185"])
    behaviour_fig.update_layout(height=360, margin=dict(l=12,r=20,t=55,b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F4F7FF",
        xaxis_title="Number of Orders", yaxis_title="Customer Spend (R$)")
    return rfm, segment_fig, revenue_fig, behaviour_fig

def create_charts_html(data):

    revenue_fig = create_revenue_chart(data)
    category_fig = create_category_chart(data)
    state_fig = create_state_chart(data)
    delivery_fig = create_delivery_review_chart(data)
    payment_fig = create_payment_chart(data)
    order_status_fig = create_order_status_chart(data)
    rfm, customer_segment_fig, customer_revenue_fig, customer_behaviour_fig = create_customer_charts(data)

    customer_counts = rfm["Segment"].value_counts()
    total_customers = len(rfm)
    repeat_customers = int((rfm["Frequency"] > 1).sum())
    avg_spend = float(rfm["Monetary"].mean())
    avg_orders = float(rfm["Frequency"].mean())
    customer_kpis = f"""<div class=\"kpi-grid customer-kpis\">
      <div class=\"kpi-card\"><div class=\"kpi-label\">UNIQUE CUSTOMERS</div><div class=\"kpi-value\">{total_customers:,.0f}</div></div>
      <div class=\"kpi-card\"><div class=\"kpi-label\">REPEAT CUSTOMERS</div><div class=\"kpi-value\">{repeat_customers:,.0f}</div></div>
      <div class=\"kpi-card\"><div class=\"kpi-label\">AVERAGE CUSTOMER SPEND</div><div class=\"kpi-value\">R$ {avg_spend:,.0f}</div></div>
      <div class=\"kpi-card\"><div class=\"kpi-label\">AVG. ORDERS / CUSTOMER</div><div class=\"kpi-value\">{avg_orders:.2f}</div></div>
    </div>"""

    chart_config = {
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
    }

    figures = [
        ("revenue", revenue_fig),
        ("category", category_fig),
        ("state", state_fig),
        ("delivery", delivery_fig),
        ("payment", payment_fig),
        ("order_status", order_status_fig)
    ]

    chart_html = {}
    for index, (name, figure) in enumerate(figures):
        chart_html[name] = figure.to_html(
            full_html=False,
            include_plotlyjs=False,
            config=chart_config,
            default_height="430px"
        )

    return f"""
    <section id="page-sales-product" class="dashboard-page">
        <div class="section-title">◈ &nbsp; SALES &amp; PRODUCT ANALYTICS</div>
        <section class="chart-grid">
            <div class="chart-card"><div class="chart-number">01 / REVENUE ANALYTICS</div>{chart_html["revenue"]}</div>
            <div class="chart-card"><div class="chart-number">02 / PRODUCT CATEGORY PERFORMANCE</div>{chart_html["category"]}</div>
        </section>
    </section>

    <section id="page-regional-delivery" class="dashboard-page">
        <div class="section-title">◈ &nbsp; REGIONAL &amp; DELIVERY ANALYTICS</div>
        <section class="chart-grid">
            <div class="chart-card"><div class="chart-number">03 / REGIONAL PERFORMANCE</div>{chart_html["state"]}</div>
            <div class="chart-card"><div class="chart-number">04 / DELIVERY &amp; CUSTOMER EXPERIENCE</div>{chart_html["delivery"]}</div>
        </section>
    </section>

    <section id="page-order-payment" class="dashboard-page">
        <div class="section-title">◈ &nbsp; ORDER &amp; PAYMENT ANALYTICS</div>
        <section class="chart-grid">
            <div class="chart-card"><div class="chart-number">05 / ORDER STATUS</div>{chart_html["order_status"]}</div>
            <div class="chart-card"><div class="chart-number">06 / PAYMENT METHODS</div>{chart_html["payment"]}</div>
        </section>
    </section>

    <section id="page-customers" class="dashboard-page">
        <div class="section-title">◈ &nbsp; CUSTOMER INSIGHTS</div>
        {customer_kpis}
        <section class="chart-grid">
            <div class="chart-card"><div class="chart-number">07 / RFM CUSTOMER SEGMENTS</div>{customer_segment_fig.to_html(full_html=False, include_plotlyjs=False, config=chart_config, default_height="360px")}</div>
            <div class="chart-card"><div class="chart-number">08 / SEGMENT REVENUE CONTRIBUTION</div>{customer_revenue_fig.to_html(full_html=False, include_plotlyjs=False, config=chart_config, default_height="360px")}</div>
            <div class="chart-card full-width"><div class="chart-number">09 / CUSTOMER PURCHASE BEHAVIOUR</div>{customer_behaviour_fig.to_html(full_html=False, include_plotlyjs=False, config=chart_config, default_height="360px")}</div>
        </section>
        <p class="customer-footnote">RFM is calculated from Olist order history using customer_unique_id. Monetary value uses item price and excludes freight.</p>
    </section>
    """


def create_kpi_cards(kpis):

    cards = [
        {
            "label": "TOTAL REVENUE",
            "value": f"R$ {kpis['Total Revenue']:,.0f}",
            "icon": "◈",
            "color": "#22D3EE",
            "change": "Overall sales value"
        },
        {
            "label": "TOTAL ORDERS",
            "value": f"{kpis['Total Orders']:,}",
            "icon": "▣",
            "color": "#A78BFA",
            "change": "Unique customer orders"
        },
        {
            "label": "AVERAGE ORDER VALUE",
            "value": f"R$ {kpis['Average Order Value']:,.2f}",
            "icon": "◇",
            "color": "#2DD4BF",
            "change": "Revenue per order"
        },
        {
            "label": "AVERAGE REVIEW SCORE",
            "value": f"{kpis['Average Review Score']:.2f} / 5",
            "icon": "✧",
            "color": "#FBBF24",
            "change": "Customer satisfaction"
        },
        {
            "label": "LATE DELIVERY",
            "value": f"{kpis['Late Delivery Percentage']:.1f}%",
            "icon": "◷",
            "color": "#FB7185",
            "change": "Of valid delivered orders"
        }
    ]

    card_html = ""

    for card in cards:
        card_html += f"""
        <div class="kpi-card" style="--accent:{card['color']}">
            <div class="kpi-top">
                <span class="kpi-icon">{card['icon']}</span>
                <span class="kpi-dot"></span>
            </div>

            <div class="kpi-label">{card['label']}</div>

            <div class="kpi-value">{card['value']}</div>

            <div class="kpi-description">{card['change']}</div>
        </div>
        """

    return card_html


# ---------------- DASHBOARD HTML EXPORT ----------------


# ---------------- DASHBOARD HTML EXPORT ----------------

def export_kpi_dashboard(kpis, prepared_data):

    cards = create_kpi_cards(kpis)
    charts_html = create_charts_html(prepared_data)
    overview_figures = [
        ("revenue", create_revenue_chart(prepared_data)),
        ("category", create_category_chart(prepared_data)),
        ("order_status", create_order_status_chart(prepared_data))
    ]
    overview_charts = ""
    for index, (name, figure) in enumerate(overview_figures):
        figure.update_layout(height=300)
        overview_charts += f'<div class="chart-card"><div class="chart-number">{index + 1:02d} / {name.replace("_", " ").upper()}</div>'
        overview_charts += figure.to_html(full_html=False, include_plotlyjs=(index == 0), config={"responsive": True, "displaylogo": False}, default_height="300px")
        overview_charts += '</div>' 

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Olist E-Commerce Intelligence</title>


<style>
* {{
    box-sizing: border-box;
}}

:root {{
    --cyan: #32E6FF;
    --violet: #A78BFA;
    --teal: #35E0C1;
    --pink: #FF79C6;
    --text: #F4F7FF;
    --muted: #8797B5;
}}

body {{
    margin: 0;
    padding: 20px;
    min-height: 100vh;
    color: var(--text);
    font-family: Inter, "Segoe UI", sans-serif;
    background:
        radial-gradient(ellipse at 8% 8%, rgba(42,91,210,.25), transparent 35%),
        radial-gradient(ellipse at 90% 15%, rgba(139,92,246,.20), transparent 32%),
        radial-gradient(ellipse at 65% 100%, rgba(34,211,238,.12), transparent 38%),
        #060A16;
    overflow-x: hidden;
}}

.app-shell {{
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    gap: 18px;
    max-width: 1900px;
    margin: 0 auto;
    align-items: start;
}}

.sidebar {{
    position: sticky;
    top: 20px;
    height: calc(100vh - 40px);
    min-height: 520px;
    padding: 18px 12px;
    border-radius: 18px;
    background: linear-gradient(160deg, rgba(27,43,72,.94), rgba(10,18,35,.97));
    border: 1px solid rgba(151,185,255,.17);
    box-shadow: 0 16px 35px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.10);
    backdrop-filter: blur(18px);
}}

.sidebar-brand {{
    color: var(--cyan);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 4px 10px 20px;
}}

.nav-label {{
    color: #8797B5;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 8px 10px;
}}

.nav-btn {{
    display: block;
    width: 100%;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 12px 10px;
    margin: 4px 0;
    color: #A6B5D0;
    background: transparent;
    text-align: left;
    font: inherit;
    font-size: 12px;
    font-weight: 650;
    cursor: pointer;
    transition: .2s ease;
}}

.nav-btn:hover, .nav-btn.active {{
    color: #FFFFFF;
    background: rgba(50,230,255,.10);
    border-color: rgba(50,230,255,.28);
    box-shadow: inset 3px 0 0 var(--cyan);
}}

.dashboard-content {{
    min-width: 0;
    width: 100%;
    max-width: none;
}}

.dashboard-page {{
    display: none;
}}

.customer-kpis {{
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin: 14px 0 18px;
}}
.full-width {{ grid-column: 1 / -1; }}
.customer-footnote {{ color: var(--muted); font-size: 11px; margin: 8px 4px 0; }}

.dashboard-page.active {{
    display: block;
}}

.single-chart {{
    grid-template-columns: minmax(0, 1fr);
}}

.customer-note {{
    padding: 24px;
    color: #A6B5D0;
    line-height: 1.7;
}}

.customer-note h2 {{
    color: #F4F7FF;
    font-size: 18px;
    margin: 14px 0 8px;
}}

.customer-note p {{
    max-width: 760px;
    font-size: 13px;
}}

.customer-note code {{
    color: var(--cyan);
}}

@media (max-width: 900px) {{
    .app-shell {{
        grid-template-columns: 1fr;
    }}
    .sidebar {{
        position: relative;
        top: auto;
        height: auto;
        min-height: 0;
    }}
    .sidebar nav {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 3px;
    }}
}}

.dashboard {{
    width: 100%;
    max-width: none;
    min-width: 0;
    margin: 0;
    position: relative;
}}

.header {{
    position: relative;
    overflow: hidden;
    padding: 21px 25px;
    border-radius: 19px;
    background: linear-gradient(
        120deg,
        rgba(30,48,83,.88),
        rgba(17,26,51,.82),
        rgba(41,31,78,.72)
    );
    border: 1px solid rgba(143,190,255,.22);
    box-shadow:
        0 18px 45px rgba(0,0,0,.38),
        inset 0 1px 1px rgba(255,255,255,.13),
        inset 0 -1px 0 rgba(255,255,255,.04);
    backdrop-filter: blur(22px);
    margin-bottom: 17px;
}}

.header::after {{
    content: "";
    position: absolute;
    width: 280px;
    height: 150px;
    right: -70px;
    top: -95px;
    background: var(--cyan);
    opacity: .17;
    filter: blur(65px);
    border-radius: 50%;
    pointer-events: none;
}}

.header h1 {{
    font-size: 26px;
    font-weight: 750;
    letter-spacing: -1px;
    margin: 0 0 8px;
}}

.header h1 span {{
    color: var(--cyan);
    text-shadow: 0 0 18px rgba(50,230,255,.7);
}}

.subtitle {{
    color: #A6B5D0;
    font-size: 10px;
    letter-spacing: 1.8px;
    font-weight: 600;
}}

.section-title {{
    color: #A5B7D4;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2.2px;
    margin: 16px 0 11px;
    text-shadow: 0 0 12px rgba(50,230,255,.15);
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 14px;
}}

.kpi-card {{
    --accent: var(--cyan);
    position: relative;
    isolation: isolate;
    overflow: hidden;
    min-width: 0;
    min-height: 139px;
    padding: 15px 16px;
    border-radius: 17px;
    background:
        linear-gradient(145deg,
            rgba(35,51,82,.92),
            rgba(12,21,41,.96)
        );
    border: 1px solid rgba(170,195,255,.17);
    box-shadow:
        0 15px 32px rgba(0,0,0,.35),
        inset 0 1px 0 rgba(255,255,255,.12),
        inset 0 -1px 0 rgba(0,0,0,.3);
    backdrop-filter: blur(18px);
    transition: transform .3s ease, box-shadow .3s ease;
}}

.kpi-card::before {{
    content: "";
    position: absolute;
    z-index: -1;
    width: 145px;
    height: 145px;
    right: -65px;
    top: -75px;
    background: var(--accent);
    opacity: .20;
    filter: blur(55px);
    border-radius: 50%;
}}

.kpi-card::after {{
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,.23),
        transparent 42%,
        var(--accent)
    );
    opacity: .35;
    pointer-events: none;
}}

.kpi-card:hover {{
    transform: translateY(-5px);
    box-shadow:
        0 22px 40px rgba(0,0,0,.45),
        0 0 22px color-mix(in srgb, var(--accent) 20%, transparent),
        inset 0 1px 0 rgba(255,255,255,.16);
}}

.kpi-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}}

.kpi-icon {{
    color: var(--accent);
    font-size: 23px;
    font-weight: 800;
    text-shadow: 0 0 15px var(--accent);
}}

.kpi-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent), 0 0 18px var(--accent);
}}

.kpi-label {{
    color: #9EADC9;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.1px;
    margin-bottom: 9px;
}}

.kpi-value {{
    color: #FFFFFF;
    font-size: clamp(18px, 1.5vw, 26px);
    font-weight: 800;
    letter-spacing: -.8px;
    white-space: nowrap;
    text-shadow: 0 2px 12px rgba(255,255,255,.10);
}}

.kpi-description {{
    color: #8293B1;
    font-size: 10px;
    margin-top: 8px;
}}

.chart-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 12px;
}}

.overview-chart-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 10px;
}}

.overview-chart-grid .chart-card {{
    padding: 10px;
}}

.overview-chart-grid .plotly-graph-div {{
    min-width: 0;
}}

/* Single-chart pages should use the entire content column. */
.chart-grid.single-chart {{
    grid-template-columns: minmax(0, 1fr);
    width: 100%;
}}

.chart-card .plotly-graph-div {{
    width: 100% !important;
}}

.chart-card {{
    position: relative;
    min-width: 0;
    overflow: hidden;
    border-radius: 18px;
    padding: 11px;
    background:
        linear-gradient(145deg,
            rgba(27,43,72,.91),
            rgba(10,18,35,.96)
        );
    border: 1px solid rgba(151,185,255,.17);
    box-shadow:
        0 16px 35px rgba(0,0,0,.35),
        inset 0 1px 0 rgba(255,255,255,.10);
    backdrop-filter: blur(18px);
    transition: border-color .3s ease, transform .3s ease;
}}

.chart-card:hover {{
    border-color: rgba(50,230,255,.40);
    transform: translateY(-2px);
}}

.chart-number {{
    color: var(--cyan);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.7px;
    padding: 5px 9px 2px;
    text-shadow: 0 0 12px rgba(50,230,255,.35);
}}

@media (max-width: 1100px) {{
    .kpi-grid {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
}}

@media (max-width: 1200px) {{
    .overview-chart-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
}}

@media (max-width: 850px) {{
    .chart-grid, .overview-chart-grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 650px) {{
    .nav-btn {{
        font-size: 11px;
        padding: 10px 8px;
    }}
    body {{
        padding: 10px;
    }}

    .kpi-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
}}
</style>

</head>

<body>

<div class="app-shell">

    <aside class="sidebar">
        <div class="sidebar-brand">◈ OLIST INTELLIGENCE</div>
        <div class="nav-label">DASHBOARD MENU</div>
        <nav>
            <button class="nav-btn active" data-page="page-overview">▦ &nbsp; Overview</button>
            <button class="nav-btn" data-page="page-sales-product">↗ &nbsp; Sales &amp; Product Analytics</button>
            <button class="nav-btn" data-page="page-regional-delivery">⌖ &nbsp; Regional &amp; Delivery Analytics</button>
            <button class="nav-btn" data-page="page-order-payment">◇ &nbsp; Order &amp; Payment Analytics</button>
            <button class="nav-btn" data-page="page-customers">✧ &nbsp; Customer Insights</button>
        </nav>
    </aside>

    <main class="dashboard dashboard-content">

        <header class="header">
            <h1><span>◈</span> OLIST E-Commerce Intelligence</h1>
            <div class="subtitle">
                SALES PERFORMANCE &nbsp; • &nbsp;
                CUSTOMER INSIGHTS &nbsp; • &nbsp;
                BUSINESS ANALYTICS
            </div>
        </header>

        <section id="page-overview" class="dashboard-page active">
            <div class="section-title">
                ◈ &nbsp; EXECUTIVE PERFORMANCE OVERVIEW
            </div>
            <section class="kpi-grid">
                {cards}
            </section>
            <section class="overview-chart-grid">
                {overview_charts}
            </section>
        </section>

        {charts_html}

    </main>

</div>

<script>
document.querySelectorAll(".nav-btn").forEach(function(button) {{
    button.addEventListener("click", function() {{
        document.querySelectorAll(".nav-btn").forEach(function(item) {{
            item.classList.remove("active");
        }});
        document.querySelectorAll(".dashboard-page").forEach(function(page) {{
            page.classList.remove("active");
        }});

        button.classList.add("active");
        var targetPage = document.getElementById(button.dataset.page);
        if (targetPage) {{
            targetPage.classList.add("active");
            window.dispatchEvent(new Event("resize"));
        }}
    }});
}});
</script>

</body>
</html>
"""

    output_file = OUTPUT_DIR / "dashboard.html"

    output_file.write_text(html, encoding="utf-8")

    print(f"\nDashboard exported successfully: {output_file}")




# ---------------- MAIN EXECUTION ----------------


# ---------------- MAIN EXECUTION ----------------

if __name__ == "__main__":

    datasets = load_data()

    prepared_data = prepare_data(datasets)

    kpis = calculate_kpis(prepared_data)

    print("\nOLIST KPI SUMMARY")

    for name, value in kpis.items():
        print(f"{name}: {value}")

    export_kpi_dashboard(kpis, prepared_data)

    print("\nDASHBOARD EXPORTED SUCCESSFULLY!")