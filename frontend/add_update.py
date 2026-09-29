import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"


def add_update_tab():
    selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed")

    response = requests.get(f"{API_URL}/expenses/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

    with st.form(key="expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text("Amount")
        with col2:
            st.text("Category")
        with col3:
            st.text("Notes")

        expenses = []

        for i in range(5):
            if i < len(existing_expenses):
                amount = existing_expenses[i].get('amount', 0.0)
                category = existing_expenses[i].get("category", "Other")
                notes = existing_expenses[i].get("notes", "")
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            # 🔍 DEBUG (you can remove later)
            # st.write(f"Row {i} raw category:", category)

            # ✅ Normalize category
            if category:
                category_clean = str(category).strip().title()
            else:
                category_clean = "Other"

            # ✅ Validate category
            if category_clean in categories:
                default_index = categories.index(category_clean)
            else:
                default_index = categories.index("Other")

            col1, col2, col3 = st.columns(3)

            with col1:
                amount_input = st.number_input(
                    label="Amount",
                    min_value=0.0,
                    step=1.0,
                    value=float(amount),
                    key=f"amount_{i}",
                    label_visibility="collapsed"
                )

            with col2:
                category_input = st.selectbox(
                    label="Category",
                    options=categories,
                    index=default_index,
                    key=f"category_{i}",
                    label_visibility="collapsed"
                )

            with col3:
                notes_input = st.text_input(
                    label="Notes",
                    value=notes,
                    key=f"notes_{i}",
                    label_visibility="collapsed"
                )

            expenses.append({
                'amount': amount_input,
                'category': category_input,
                'notes': notes_input
            })

        submit_button = st.form_submit_button()

        if submit_button:
            filtered_expenses = [
                expense for expense in expenses if expense['amount'] > 0
            ]

            response = requests.post(
                f"{API_URL}/expenses/{selected_date}",
                json=filtered_expenses
            )

            if response.status_code == 200:
                st.success("Expenses updated successfully!")
            else:
                st.error("Failed to update expenses.")