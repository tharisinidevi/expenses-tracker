# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="Student Expenses Tracker", layout="wide")
st.title("💰 Student Expenses Tracker")

# --- Initialize session state ---
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
if "categories" not in st.session_state:
    st.session_state.categories = ["Food", "Transport", "Entertainment", "Books"]
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 1000.0  # default budget as float

# --- Sidebar for budget and custom categories ---
st.sidebar.header("⚙ Settings")
st.session_state.monthly_budget = st.sidebar.number_input(
    "Set Monthly Budget (RM)",
    min_value=0.0,
    value=float(st.session_state.monthly_budget),
    step=10.0
)

new_category = st.sidebar.text_input("Add Custom Category")
if st.sidebar.button("Add Category") and new_category:
    if new_category not in st.session_state.categories:
        st.session_state.categories.append(new_category)
        st.sidebar.success(f"Added '{new_category}' category!")

# --- User Input Form ---
st.header("Add Your Expense")
with st.form("expense_form"):
    date = st.date_input("Date", value=datetime.today())
    category = st.selectbox("Category", st.session_state.categories)
    amount = st.number_input("Amount (RM)", min_value=0.0, step=0.01)
    description = st.text_input("Description")
    submitted = st.form_submit_button("Add Expense")

if submitted:
    new_expense = pd.DataFrame({
        "Date": [date],
        "Category": [category],
        "Amount": [amount],
        "Description": [description]
    })
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
    st.success("✅ Expense added!")

# --- Display Expenses ---
st.header("📊 Your Expenses")
if not st.session_state.expenses.empty:
    df = st.session_state.expenses
    st.dataframe(df)

    # --- Total & Daily Average ---
    total = df["Amount"].sum()
    days = (df["Date"].max() - df["Date"].min()).days + 1
    daily_avg = total / days if days > 0 else total

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses (RM)", f"{total:.2f}")
    col2.metric("Daily Average (RM)", f"{daily_avg:.2f}")
    col3.metric("Monthly Budget (RM)", f"{st.session_state.monthly_budget:.2f}")

    # --- Budget Alert ---
    if total > st.session_state.monthly_budget:
        st.warning("⚠️ You have exceeded your monthly budget!")
    elif total > 0.8 * st.session_state.monthly_budget:
        st.info("💡 You are close to your budget limit. Spend wisely!")

    # --- Visualization ---
    st.subheader("Expenses by Category")
    plt.figure(figsize=(6,4))
    sns.barplot(
        data=df.groupby("Category")["Amount"].sum().reset_index(),
        x="Category",
        y="Amount",
        palette="coolwarm"
    )
    plt.ylabel("Total Amount (RM)")
    st.pyplot(plt)

    st.subheader("Expenses Over Time")
    plt.figure(figsize=(8,4))
    time_data = df.groupby("Date")["Amount"].sum().reset_index()
    sns.lineplot(data=time_data, x="Date", y="Amount", marker="o")
    plt.ylabel("Amount (RM)")
    st.pyplot(plt)

    st.subheader("Category Breakdown (Pie Chart)")
    pie_data = df.groupby("Category")["Amount"].sum()
    st.pyplot(pie_data.plot.pie(autopct="%1.1f%%", figsize=(5,5)).figure)

    # --- Motivational Message ---
    top_category = df.groupby("Category")["Amount"].sum().idxmax()
    st.success(f"🎯 You spend the most on {top_category}. Keep an eye on it!")

    # --- Download CSV ---
    st.download_button(
        "📥 Download Expenses as CSV",
        data=df.to_csv(index=False),
        file_name="my_expenses.csv",
        mime="text/csv"
    )
else:
    st.info("No expenses recorded yet. Add your first expense above!")
