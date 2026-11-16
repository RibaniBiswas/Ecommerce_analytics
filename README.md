# 🛒 Olist E-Commerce Analytics & Intelligence Dashboard

**An end-to-end data analytics project built with Python, Pandas,
SQLite, SQL, and Plotly using the Brazilian E-Commerce Public Dataset by
Olist.**

This project explores the Olist marketplace from raw CSV data through
data loading, database operations, SQL analysis, customer analytics, and
an interactive five-page dashboard. The goal is to turn
transaction-level data into clear business metrics and visual insights.

------------------------------------------------------------------------

## 📸 Dashboard Preview

### Overview --- Executive Performance

The Overview page brings together five KPI cards and three executive
charts: monthly revenue performance, top product categories, and order
status.

![Olist E-Commerce Intelligence Dashboard ---
Overview](images/overview.png)

> The screenshot above is the actual Overview screenshot supplied for
> this README. Add the remaining four page screenshots to the `images/`
> folder as they become available.

------------------------------------------------------------------------

## 🎯 Project Goals

The project was designed to answer practical e-commerce business
questions:

-   How much revenue and how many orders does the marketplace generate?
-   How does revenue change over time?
-   Which product categories contribute the most revenue?
-   Which Brazilian states are the strongest revenue contributors?
-   How are delivery performance and customer reviews related?
-   Which order statuses and payment methods are most common?
-   How many customers purchase more than once?
-   How do customer segments contribute to revenue?

## 🗃️ Dataset

The project uses the **Brazilian E-Commerce Public Dataset by Olist**.
The project work used nine CSV datasets:

  -----------------------------------------------------------------------------------------
  File                                      What it contains        How it supports the
                                                                    analysis
  ----------------------------------------- ----------------------- -----------------------
  `olist_customers_dataset.csv`             Customer identifiers    Customer-level analysis
                                            and location            

  `olist_geolocation_dataset.csv`           Brazilian geolocation   Geographic context
                                            information             

  `olist_order_items_dataset.csv`           Items associated with   Product and revenue
                                            orders                  analysis

  `olist_order_payments_dataset.csv`        Payment types and       Payment analysis
                                            payment values          

  `olist_order_reviews_dataset.csv`         Customer review scores  Customer satisfaction
                                                                    analysis

  `olist_orders_dataset.csv`                Order identifiers,      Order, sales, and
                                            status, and timestamps  delivery analysis

  `olist_products_dataset.csv`              Product attributes and  Product category
                                            category identifiers    analysis

  `olist_sellers_dataset.csv`               Seller identifiers and  Seller and regional
                                            location                context

  `product_category_name_translation.csv`   Portuguese-to-English   Readable category
                                            category translations   labels
  -----------------------------------------------------------------------------------------

**Dataset source:** [Brazilian E-Commerce Public Dataset by Olist ---
Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset files are expected in `data/raw/` when running the project
locally.

------------------------------------------------------------------------

## 🧰 Technologies Used

  -----------------------------------------------------------------------
  Technology                          Role in the project
  ----------------------------------- -----------------------------------
  Python                              Main programming language

  Pandas                              Loading and manipulating CSV
                                      datasets

  NumPy                               Numerical operations

  SQLite                              Local relational database

  SQL                                 Aggregation and business analysis
                                      queries

  Plotly                              Interactive dashboard charts

  Matplotlib                          Data visualization and exploration

  Seaborn                             Statistical visualization

  Scikit-learn                        Included in the project environment
                                      for analytical workflows

  Jupyter Notebook                    Exploratory analysis

  HTML and CSS                        Dashboard layout and visual styling

  Git and GitHub                      Version control and project hosting

  VS Code                             Development environment
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🏗️ How I Built the Project

The project was developed in stages, moving from data organization to
analysis and then dashboard presentation.

### Phase 1 --- Project Setup

I created the project workspace and organized the work into separate
folders for the raw data, source code, SQL queries, notebooks,
dashboard, and images. I also prepared the Python environment and a
`requirements.txt` file for the project dependencies.

### Phase 2 --- Dataset Organization

I collected the nine Olist CSV files and organized them under
`data/raw/`. Keeping the source files together made it easier to load
and work with the related datasets consistently.

### Phase 3 --- Reusable Data Loading

I created a `DataLoader` class in `src/data_loader.py`.

The purpose of this class is to centralize the loading of the Olist CSV
files with Pandas rather than repeating separate file-loading code
throughout the project.

### Phase 4 --- SQLite Database Management

I created a `DatabaseManager` class in `src/database.py` and used
Python's SQLite support to manage the database connection and database
operations.

This separated database-related work from the data-loading and analysis
code.

### Phase 5 --- SQL Business Analysis

I created and ran SQL queries in `sql/queries.sql`. The queries explored
business measures such as:

-   Monthly revenue
-   Top product categories
-   Revenue by Brazilian state
-   Order and transaction patterns

The SQL work helped turn the raw transactional tables into grouped and
aggregated results that could be used for analysis.

### Phase 6 --- Python Analysis

I organized analytical logic in the `src/` source-code area, including
`analyzer.py`, and used Pandas and NumPy to work with the datasets.

The project also includes the `notebooks/Olist_Analysis.ipynb` notebook
for exploratory work.

### Phase 7 --- Customer Analytics and RFM

I added customer-level analysis using customer and order information.
The dashboard includes repeat-customer metrics and an RFM-style
segmentation view.

RFM stands for:

-   **Recency:** How recently a customer placed an order.
-   **Frequency:** How often a customer ordered.
-   **Monetary:** How much a customer spent.

For repeat-customer analysis, the customer-level identity is based on
Olist's `customer_unique_id`, which allows purchases associated with the
same customer to be grouped even when order-level customer IDs differ.

### Phase 8 --- Interactive Dashboard

I developed the dashboard in `dashboard/app.py` using Python and Plotly,
with HTML/CSS styling. The dashboard uses a dark visual theme, KPI
cards, chart panels, and a left-hand navigation menu.

Running the Python dashboard script exports a standalone HTML dashboard
to `dashboard/dashboard.html`, which can be opened in a web browser.

------------------------------------------------------------------------

## 📊 Dashboard Pages

The final dashboard is organized into five navigation sections.

### 1. Overview

A high-level executive summary of marketplace performance.

**KPI cards** - Total Revenue - Total Orders - Average Order Value -
Average Review Score - Late Delivery Percentage

**Executive charts** - Monthly Revenue Performance - Top 10 Product
Categories - Orders by Status

### 2. Sales & Product Analytics

This page brings sales trends and product category performance together.

**Charts** - Monthly Revenue Performance - Top 10 Product Categories

### 3. Regional & Delivery Analytics

This page explores regional revenue and delivery experience.

**Charts** - Top 10 Brazilian States by Revenue - Delivery Status vs
Customer Review

### 4. Order & Payment Analytics

This page combines order status and payment behaviour.

**Charts** - Order Status Distribution --- horizontal bar chart -
Payment Method Distribution --- donut chart

### 5. Customer Insights

This page focuses on customer purchasing behaviour and segmentation.

**KPI cards** - Unique Customers - Repeat Customers - Average Customer
Spend - Average Orders per Customer

**Charts** - RFM Customer Segment Distribution - Revenue Contribution by
Customer Segment - Purchase Frequency vs Customer Spend

------------------------------------------------------------------------

## 📌 Current Dashboard Metrics

The current Overview screenshot displays the following values:

  Metric                   Displayed value
  ---------------------- -----------------
  Total Revenue             R\$ 13,591,644
  Total Orders                      99,441
  Average Order Value           R\$ 137.75
  Average Review Score            4.09 / 5
  Late Delivery                       8.1%

These values are transcribed from the supplied dashboard screenshot.
They describe that dashboard output and may change if the source data or
calculation logic changes.

------------------------------------------------------------------------

## 📁 Project Structure

The main project structure is:

``` text
ecommerce_prj/
│
├── data/
│   └── raw/
│       ├── olist_customers_dataset.csv
│       ├── olist_geolocation_dataset.csv
│       ├── olist_order_items_dataset.csv
│       ├── olist_order_payments_dataset.csv
│       ├── olist_order_reviews_dataset.csv
│       ├── olist_orders_dataset.csv
│       ├── olist_products_dataset.csv
│       ├── olist_sellers_dataset.csv
│       └── product_category_name_translation.csv
│
├── dashboard/
│   ├── app.py
│   └── dashboard.html
│
├── images/
│   └── overview.png
│
├── notebooks/
│   └── Olist_Analysis.ipynb
│
├── sql/
│   └── queries.sql
│
├── src/
│   ├── analyzer.py
│   ├── data_loader.py
│   └── database.py
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

*This tree shows the main project files. Local backup files, virtual
environments, generated caches, and other machine-specific files are
intentionally not listed.*

------------------------------------------------------------------------

## ▶️ How to Run the Project

### 1. Clone the repository

Replace the placeholder with the URL of your GitHub repository:

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ecommerce_prj
```

### 2. Create a virtual environment

``` bash
python -m venv venv
```

### 3. Activate the environment

**Windows PowerShell:**

``` powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install the dependencies

``` bash
pip install -r requirements.txt
```

### 5. Add the dataset files

Place the nine Olist CSV files inside:

``` text
data/raw/
```

### 6. Generate the dashboard

Run the command from the project root:

``` bash
python dashboard/app.py
```

### 7. Open the dashboard

Open the generated HTML file in your browser:

``` text
dashboard/dashboard.html
```

------------------------------------------------------------------------

## 💡 Skills Demonstrated

By completing this project, I practised and applied:

-   Python programming and object-oriented code organization
-   CSV data loading and manipulation with Pandas
-   Numerical analysis with NumPy
-   SQLite database connection and management
-   SQL queries, joins, grouping, and aggregations
-   Exploratory data analysis
-   E-commerce sales and product analysis
-   Regional and delivery performance analysis
-   Customer metrics and RFM-style segmentation
-   Interactive Plotly chart development
-   HTML/CSS dashboard presentation
-   Organizing a multi-file analytics project
-   Version control with Git and GitHub

## 🔭 Possible Future Improvements

-   Add more dashboard filters and drill-down interactions.
-   Extend customer lifetime value analysis.
-   Add sales forecasting.
-   Explore seller performance in more detail.
-   Deploy the dashboard for public online access.
-   Add screenshots for all five dashboard pages.

------------------------------------------------------------------------

## 👩‍💻 Author

**Ribani**

Data Analytics \| Python \| SQL \| Business Intelligence \| Data
Visualization

------------------------------------------------------------------------

**Project:** Olist E-Commerce Analytics & Intelligence Dashboard\
**Dataset:** Brazilian E-Commerce Public Dataset by Olist
