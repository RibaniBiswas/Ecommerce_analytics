# 🛒 E-Commerce Sales & Customer Insights Dashboard

<p align="center">
  **An End-to-End Data Analytics Project Using Python, SQL & Machine Learning**
</p>

<p align="center">
  ![Python](https://img.shields.io/badge/Python-3.10-blue)
  ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-purple)
  ![SQL](https://img.shields.io/badge/SQL-SQLite-orange)
  ![Status](https://img.shields.io/badge/Project-In%20Progress-yellow)
</p>

---

## 📌 Project Overview

This project focuses on analyzing Brazilian e-commerce sales data from Olist to discover meaningful business insights.

The objective is to understand sales performance, customer purchasing behavior, product category performance, delivery efficiency and customer satisfaction.

The project follows an end-to-end data analytics workflow, starting from raw data loading and progressing towards data cleaning, SQL analysis, exploratory data analysis, customer segmentation and interactive dashboard development.

## 🎯 Business Objectives

- Analyze monthly revenue and sales trends.
- Identify top-performing product categories.
- Understand customer distribution across Brazilian states.
- Evaluate delivery performance.
- Analyze customer reviews and satisfaction.
- Identify valuable customer segments using RFM analysis.
- Develop actionable business recommendations.

## 📂 Dataset

**Dataset:** Brazilian E-Commerce Public Dataset by Olist

**Source:** [Kaggle – Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset contains approximately 100,000 orders from 2016–2018 and nine related CSV files.

Raw dataset files are stored locally and are not uploaded to this repository.

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data analysis |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| SQLite | SQL database and queries |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Plotly | Interactive dashboard |
| Scikit-learn | Customer segmentation |
| Git & GitHub | Version control |

## 🔄 Project Workflow

1. Data Collection and Loading
2. SQL Business Analysis
3. Data Cleaning and Feature Engineering
4. Exploratory Data Analysis (EDA)
5. RFM Customer Segmentation using KMeans
6. Interactive Dashboard Development
7. Business Insights and Recommendations

## 📁 Repository Structure

```text
Ecommerce_analytics/
│
├── data/
│   └── raw/
│
├── src/
│   ├── data_loader.py
│   └── main.py
│
├── notebooks/
├── sql/
├── images/
├── dashboard/
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/RibaniBiswas/Ecommerce_analytics.git
```

### 2. Navigate to the project directory

```bash
cd Ecommerce_analytics
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Download the dataset

Download the Olist dataset from Kaggle and extract the nine CSV files into:

```text
data/raw/
```

### 7. Run the project

```bash
python src/main.py
```

## 📊 Key Analysis Areas

- Monthly Revenue Analysis
- Top Product Categories
- State-wise Sales Analysis
- Delivery Performance
- Payment Method Analysis
- Customer Review Analysis
- Seller Performance
- Customer Segmentation

## 📈 Dashboard Preview

*Coming soon – Interactive dashboard screenshots will be added after development.*

## 💡 Business Insights

*To be added after completing the SQL analysis and exploratory data analysis.*

## 🚀 Project Status

Currently working on the data loading and preprocessing stage.

More analysis, visualizations, customer segmentation and dashboard features will be added as the project progresses.

## 👩‍💻 Author

**Ribani**

- GitHub: [RibaniBiswas](https://github.com/RibaniBiswas)
- LinkedIn: [Connect with me](https://www.linkedin.com/in/ribani-biswas-79347838b/)

---

⭐ If you find this project interesting, feel free to explore the repository!