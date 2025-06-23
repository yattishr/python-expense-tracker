"""
Expense Pilot Simulator
This script provides a mock-up of the Expense Pilot dashboard using Streamlit.

Usage:
    1. Ensure Streamlit is installed: pip install streamlit
    2. Run with: streamlit run expense_pilot_streamlit.py

If Streamlit is unavailable, the script will exit with an explanatory message.
"""

# --- Environment Check ---
import sys
try:
    import streamlit as st
except ModuleNotFoundError:
    print("Error: Module 'streamlit' not found. Please install it with 'pip install streamlit' and run this script in a Streamlit-supported environment.")
    sys.exit(1)

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# --- Helper functions ---
def generate_dummy_data():
    """Generate 30 days of dummy expense data."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=30)
    categories = ['Travel', 'Meals', 'Supplies', 'Software', 'Other']
    data = []
    for date in dates:
        data.append({
            'date': date,
            'category': np.random.choice(categories),
            'amount': round(np.random.uniform(10, 200), 2),
            'description': f"Dummy expense {np.random.randint(1000,9999)}"
        })
    return pd.DataFrame(data)


def load_data(uploaded_file):
    """Load user-uploaded CSV/XLSX or fallback to dummy data."""
    if uploaded_file:
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file, parse_dates=['date'])
        else:
            df = pd.read_excel(uploaded_file, parse_dates=['date'])
    else:
        df = generate_dummy_data()
    return df


def plot_monthly_trends(df):
    monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly['date'] = monthly['date'].dt.to_timestamp()
    fig, ax = plt.subplots()
    ax.plot(monthly['date'], monthly['amount'])
    ax.set_title("Monthly Spend Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Spend")
    st.pyplot(fig)


def plot_category_breakdown(df):
    category_totals = df.groupby('category')['amount'].sum()
    fig, ax = plt.subplots()
    ax.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=140)
    ax.set_title("Spend by Category")
    st.pyplot(fig)

# --- Main App ---
def main():
    st.set_page_config(page_title="Expense Pilot Simulator", layout="wide")
    st.title("💼 Expense Pilot Simulator")

    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload your expense file (CSV/Excel)", type=['csv','xlsx'])

    df = load_data(uploaded_file)

    st.header("Summary Metrics")
    total = df['amount'].sum()
    st.metric("Total Spend", f"${total:,.2f}")

    st.subheader("Monthly Trend")
    plot_monthly_trends(df)

    st.subheader("Category Breakdown")
    plot_category_breakdown(df)

    with st.expander("Raw Data"):
        st.dataframe(df)

if __name__ == "__main__":
    main()