import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Streamlit setup
st.title("Capacity Planning Visualizer")

# Reference Date Input
reference_date = st.date_input("Select Reference Date")

# On Button Click
if st.button("Generate Graphs"):
    # Connect to DuckDB
    con = duckdb.connect("capacity_panning.duckdb")

    # Get all distinct target_table and application names
    query = """
        SELECT DISTINCT LOWER(target_table) AS table_name, application
        FROM capacity_planning.query_metadata
    """
    metadata_df = con.execute(query).fetchdf()

    # Loop through each table/application
    for _, row in metadata_df.iterrows():
        table_name = row["table_name"]
        app_name = row["application"]

        # Query last 13 months of data
        data_query = f"""
            SELECT *, 
                   strftime(Period, '%Y-%m') AS month_year
            FROM {table_name}
            WHERE Period BETWEEN DATE '{reference_date}' - INTERVAL 13 MONTHS AND DATE '{reference_date}'
        """
        try:
            df = con.execute(data_query).fetchdf()
        except Exception as e:
            st.error(f"Error fetching data from {table_name}: {e}")
            continue

        if df.empty:
            st.warning(f"No data found for {app_name} in the last 13 months.")
            continue

        # Convert Period to datetime if not already
        df['Period'] = pd.to_datetime(df['Period'])

        # Daily Multi-Line Plot
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=df, x='Period', y='Volume', hue='Application_Type', palette='colorblind', ax=ax)
        ax.set_title(f"{app_name} Daily")
        ax.set_xlabel("Date")
        ax.set_ylabel("Volume")
        ax.xaxis.set_major_locator(plt.MultipleLocator(6))  # Roughly skip every 6 days (handled better by matplotlib)
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        st.markdown("---")

        # Monthly Aggregated Bar Plot
        monthly_df = df.groupby(['month_year', 'Application_Type'], as_index=False)['Volume'].sum()

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=monthly_df, x='month_year', y='Volume', hue='Application_Type', ax=ax, palette='colorblind')

        # Annotate bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', label_type='edge', fontsize=8)

        ax.set_title(f"{app_name} Monthly")
        ax.set_xlabel("Month-Year")
        ax.set_ylabel("Total Volume")
        ax.tick_params(axis='x', rotation=45)
        ax.legend(title='Application Type')
        st.pyplot(fig)
        st.markdown("###")
