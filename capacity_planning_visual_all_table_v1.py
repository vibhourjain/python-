import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Initialize DuckDB connection
conn = duckdb.connect(database='your_database.duckdb')

def get_table_list():
    """Fetch all distinct tables from query_metadata"""
    return conn.execute("""
        SELECT DISTINCT target_table 
        FROM query_metadata
        ORDER BY target_table
    """).fetchdf()['target_table'].tolist()

def fetch_table_data(table_name):
    """Fetch data from specified table with error handling"""
    try:
        return conn.execute(f"""
            SELECT Application_type, Volume, Period
            FROM {table_name}
        """).fetchdf()
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {str(e)}")
        return None

def create_visualizations(df, reference_date):
    """Create both visualizations with consistent formatting"""
    # Filter data for last 13 months
    df['Period'] = pd.to_datetime(df['Period'])
    start_date = reference_date - timedelta(days=395)  # 13 months buffer
    filtered_df = df[(df['Period'] >= start_date) & (df['Period'] <= reference_date)]
    
    if filtered_df.empty:
        return None, None
    
    # Create consistent color mapping per table
    app_types = filtered_df['Application_type'].unique()
    colors = px.colors.qualitative.Plotly
    color_map = {app: colors[i % len(colors)] for i, app in enumerate(app_types)}
    
    # Line Chart
    line_fig = px.line(
        filtered_df,
        x='Period',
        y='Volume',
        color='Application_type',
        title='Volume Trend',
        labels={'Period': '', 'Volume': 'Volume'},
        color_discrete_map=color_map
    )
    line_fig.update_xaxes(
        tickformat="%b-%Y",
        dtick="M1",
        tickvals=filtered_df['Period'].unique()[::6],
        tickangle=45
    )
    
    # Bar Chart
    filtered_df['Month-Year'] = filtered_df['Period'].dt.strftime('%b-%Y')
    bar_fig = px.bar(
        filtered_df,
        x='Month-Year',
        y='Volume',
        color='Application_type',
        title='Monthly Comparison',
        labels={'Month-Year': '', 'Volume': 'Volume'},
        color_discrete_map=color_map
    )
    bar_fig.update_xaxes(
        tickvals=filtered_df['Month-Year'].unique()[::6],
        tickangle=45
    )
    
    return line_fig, bar_fig

# Streamlit UI
st.title('Automated Table Analysis')

# Date input
reference_date = st.date_input(
    "Select Reference Date",
    datetime.today()
)

if reference_date:
    try:
        all_tables = get_table_list()
        st.write(f"Found {len(all_tables)} tables to process")
        
        for table_name in all_tables:
            st.header(f"Analyzing: {table_name}")
            
            df = fetch_table_data(table_name)
            if df is None:
                continue
                
            line_fig, bar_fig = create_visualizations(df, reference_date)
            
            if line_fig and bar_fig:
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(line_fig, use_container_width=True)
                with col2:
                    st.plotly_chart(bar_fig, use_container_width=True)
            else:
                st.warning(f"No data available for {table_name} in selected date range")
            
            st.markdown("---")  # Add separator between tables
    
    except Exception as e:
        st.error(f"Critical error: {str(e)}")
    finally:
        conn.close()
        
        
        
Approach2

import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# Establish DuckDB connection
conn = duckdb.connect(database='your_database.duckdb')

# List of tables to iterate over
tables = ['table1', 'table2', 'table3', 'table4', 'table5', 'table6', 'table7', 'table8']

# Streamlit Date Picker for selecting the reference date
end_date = st.date_input("Select reference date", pd.to_datetime("2023-03-01"))

# Calculate the start date as the last 13 months from the selected end date
start_date = end_date - pd.DateOffset(months=12)

# Color mapping for Application_type
color_map = {'App1': 'blue', 'App2': 'orange'}  # Adjust this if more application types are there

# Loop over each table
for table in tables:
    # Fetch data from DuckDB table
    query = f"SELECT Application_type, Volume, Period FROM {table} WHERE Period >= '{start_date.strftime('%Y-%m-%d')}'"
    df = conn.execute(query).fetchdf()

    # Convert 'Period' to datetime format
    df['Period'] = pd.to_datetime(df['Period'], format='%Y-%m-%d')

    # Graph 1 (Line Graph): Period (yyyy-mm-dd) vs Volume, color by Application_type
    fig1 = px.line(df, x='Period', y='Volume', color='Application_type',
                   labels={'Period': 'Date', 'Volume': 'Volume'},
                   title=f'Line Graph: Volume Over Time by Application Type - {table}')
    
    # Customize xticks to skip 6 data points
    fig1.update_xaxes(tickmode='array', tickvals=df['Period'][::6])

    # Graph 2 (Bar Graph): Period (yyyy-mm) vs Volume, color by Application_type
    df['Month-Year'] = df['Period'].dt.to_period('M').astype(str)  # Extract month-year

    fig2 = px.bar(df, x='Month-Year', y='Volume', color='Application_type',
                  color_discrete_map=color_map,
                  labels={'Month-Year': 'Month-Year', 'Volume': 'Volume'},
                  title=f'Bar Graph: Volume by Application Type - {table}')

    # Show graphs for each table in Streamlit
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

# Close the DuckDB connection
conn.close()
