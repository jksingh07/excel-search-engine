import streamlit as st
import pandas as pd
from datetime import datetime

# Function to correct date format
def correct_date_format(date_str):
    try:
        return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return date_str

# Function to check if a string is a valid date in the YYYYMMDD format
def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False

# Title
st.title('Excel Sheet Search and Filter Application')

# File upload
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the uploaded file
    df = pd.read_excel(uploaded_file)
    
    # Specify the date columns by their names
    date_columns = ['Date']  # Replace with your actual date column names

    # Correct the date format for specified date columns
    for col in date_columns:
        if col in df.columns:
            # Convert integer dates to strings
            df[col] = df[col].astype(str)
            # Apply date format correction only to valid date strings
            df[col] = df[col].apply(lambda x: correct_date_format(x) if is_valid_date_format(x) else x)
            try:
                df[col] = pd.to_datetime(df[col]).dt.date
            except ValueError:
                pass

    st.write("Uploaded DataFrame:")
    st.dataframe(df)

    # Search
    search_query = st.text_input("Enter search query")

    # Dynamic filters
    filters = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and col not in date_columns:
            st.write(f"Filter by {col} (numeric):")
            filters[col] = {
                'operation': st.selectbox(f"Operation for {col}", ['>', '<', '>=', '<=', '==', '!='], key=col+"_operation"),
                'value': st.number_input(f"Value for {col}", value=float(df[col].min()), key=col+"_value")
            }
        elif pd.api.types.is_datetime64_any_dtype(df[col]) or col in date_columns:
            st.write(f"Filter by {col} (datetime):")
            filters[col] = {
                'operation': st.selectbox(f"Operation for {col}", ['>', '<', '>=', '<=', '==', '!='], key=col+"_operation"),
                'value': st.date_input(f"Value for {col}", value=pd.to_datetime(df[col].min()).date(), key=col+"_value")
            }
        else:
            filters[col] = st.text_input(f"Filter by {col}", key=col+"_filter")

    if st.button("Search and Filter"):
        # Perform partial search
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        # Apply filters
        for col, condition in filters.items():
            if isinstance(condition, dict):
                op = condition['operation']
                val = condition['value']
                if op == '>':
                    df = df[df[col] > val]
                elif op == '<':
                    df = df[df[col] < val]
                elif op == '>=':
                    df = df[df[col] >= val]
                elif op == '<=':
                    df = df[df[col] <= val]
                elif op == '==':
                    df = df[df[col] == val]
                elif op == '!=':
                    df = df[df[col] != val]
            else:
                if condition:
                    df = df[df[col].astype(str).str.contains(condition, case=False)]

        # Display the filtered dataframe
        st.write("Filtered DataFrame:")
        st.dataframe(df)