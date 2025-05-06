import streamlit as st
import duckdb
import pandas as pd
import io

st.title("DuckDB File Uploader & SQL Query Tool")

# File upload
uploaded_file = st.file_uploader("Upload Excel/CSV/TXT file", type=["csv", "txt", "xlsx"])

# Placeholder for data
df = None
table_name = "uploaded_data"

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "xlsx":
        excel_sheets = pd.ExcelFile(uploaded_file).sheet_names
        selected_sheet = st.selectbox("Select Sheet", excel_sheets)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    elif file_type in ["csv", "txt"]:
        delimiter = "," if file_type == "csv" else "\t"
        df = pd.read_csv(uploaded_file, delimiter=delimiter)

    if df is not None:
        st.success(f"File loaded with {df.shape[0]} rows and {df.shape[1]} columns")
        st.dataframe(df.head())

        # Load into DuckDB
        con = duckdb.connect(database=':memory:')
        con.register(table_name, df)

        # SQL input
        st.markdown("### Enter SQL Query")
        default_query = f"SELECT * FROM {table_name} LIMIT 10"
        user_query = st.text_area("SQL", default_query, height=150)

        if st.button("Run Query"):
            try:
                result_df = con.execute(user_query).fetchdf()
                st.dataframe(result_df)

                # CSV download
                csv_data = result_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Result as CSV", data=csv_data, file_name="query_result.csv", mime="text/csv")
            except Exception as e:
                st.error(f"Error executing query: {e}")