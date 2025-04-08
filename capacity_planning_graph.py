import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# DuckDB file path and schema
DUCKDB_PATH = "sybase_data.duckdb"
SCHEMA = "capacity_planning"

# List your 14 table names here (full names with schema if needed)
TABLES = [
    "application_table1",
    "application_table2",
    "application_table3",
    "application_table4",
    "application_table5",
    "application_table6",
    "application_table7",
    "application_table8",
    "application_table9",
    "application_table10",
    "application_table11",
    "application_table12",
    "application_table13",
    "application_table14"
]

# Streamlit UI
st.title("Application Metrics Dashboard")
end_date = st.date_input("Select End Date", value=datetime.today())
start_date = (end_date.replace(day=1) - timedelta(days=365)).replace(day=1)

# Connect to DuckDB
conn = duckdb.connect(DUCKDB_PATH)

for table in TABLES:
    st.subheader(f"Data from {table}")

    try:
        query = f"""
            SELECT *,
                   strftime(bv_date, '%Y-%m') AS period
            FROM {SCHEMA}.{table}
            WHERE bv_date BETWEEN '{start_date}' AND '{end_date}'
        """
        df = conn.execute(query).fetchdf()

        if df.empty:
            st.info(f"No data for {table} in the selected range.")
            continue

        # --- Line Chart: bv_date vs count_rec ---
        line_fig = px.line(
            df,
            x="bv_date",
            y="count_rec",
            color="app_type",
            title="Line Chart: Period vs Volume",
            markers=True
        )
        st.plotly_chart(line_fig, use_container_width=True)

        # --- Bar Chart: Month-Year aggregated volume ---
        df_grouped = df.groupby(["period", "app_type"], as_index=False)["count_rec"].sum()
        bar_fig = px.bar(
            df_grouped,
            x="period",
            y="count_rec",
            color="app_type",
            title="Bar Chart: Monthly Aggregated Volume",
            barmode="group"
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing {table}: {e}")
