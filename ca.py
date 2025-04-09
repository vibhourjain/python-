import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Persistent connection handler
@st.cache_resource
def get_db_connection():
    return duckdb.connect(database='your_database.duckdb', read_only=True)

def get_table_list(conn):
    """Fetch all distinct tables from query_metadata"""
    return conn.execute("""
        SELECT DISTINCT target_table 
        FROM query_metadata
        ORDER BY target_table
    """).fetchdf()['target_table'].tolist()

def fetch_table_data(conn, table_name):
    """Fetch data from specified table with error handling"""
    try:
        return conn.execute(f"""
            SELECT Application_type, Volume, Period
            FROM {table_name}
        """).fetchdf()
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {str(e)}")
        return None

def create_visualizations(df, reference_date, table_name):
    """Create both visualizations with improved multi-bar formatting"""
    # Filter data for last 13 months
    df['Period'] = pd.to_datetime(df['Period'])
    start_date = reference_date - timedelta(days=395)  # 13 months buffer
    filtered_df = df[(df['Period'] >= start_date) & (df['Period'] <= reference_date)]
    
    if filtered_df.empty:
        return None, None
    
    # Create consistent color mapping per table
    app_types = sorted(filtered_df['Application_type'].unique())
    colors = px.colors.qualitative.Plotly
    color_map = {app: colors[i % len(colors)] for i, app in enumerate(app_types)}
    
    # LINE CHART (bigger and clearer)
    line_fig = px.line(
        filtered_df,
        x='Period',
        y='Volume',
        color='Application_type',
        title=f'{table_name} - Volume Trend',
        labels={'Period': '', 'Volume': 'Volume'},
        color_discrete_map=color_map,
        height=500
    )
    line_fig.update_xaxes(
        tickformat="%b-%Y",
        dtick="M1",
        tickvals=filtered_df['Period'].unique()[::6],
        tickangle=45
    )
    line_fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode='x unified',
        legend_title_text='Application Type'
    )
    
    # MULTI-BAR CHART (properly grouped bars)
    filtered_df['Month-Year'] = filtered_df['Period'].dt.strftime('%b-%Y')
    
    # Create a sorted month-year order
    month_order = sorted(filtered_df['Period'].dt.strftime('%Y-%m').unique())
    filtered_df['Year-Month'] = filtered_df['Period'].dt.strftime('%Y-%m')
    filtered_df = filtered_df.sort_values('Year-Month')
    
    bar_fig = px.bar(
        filtered_df,
        x='Month-Year',
        y='Volume',
        color='Application_type',
        title=f'{table_name} - Monthly Comparison',
        labels={'Month-Year': '', 'Volume': 'Volume'},
        color_discrete_map=color_map,
        barmode='group',  # This creates the multi-bar effect
        category_orders={'Month-Year': [pd.to_datetime(m + '-01').strftime('%b-%Y') for m in month_order]},
        height=500
    )
    
    # Improve bar chart layout
    bar_fig.update_layout(
        xaxis={'tickangle': 45},
        margin=dict(l=20, r=20, t=60, b=100),
        legend_title_text='Application Type',
        bargap=0.15,  # Space between bars of different categories
        bargroupgap=0.1  # Space between bars of same category
    )
    
    # Only show every 6th x-axis label to prevent crowding
    bar_fig.update_xaxes(
        tickvals=filtered_df['Month-Year'].unique()[::6]
    )
    
    return line_fig, bar_fig

# Streamlit UI
st.set_page_config(layout="wide")
st.title('Automated Table Analysis Dashboard')

# Date input
reference_date = st.date_input(
    "Select Reference Date",
    datetime.today(),
    key='date_selector'
)

if reference_date:
    conn = None
    try:
        conn = get_db_connection()
        all_tables = get_table_list(conn)
        
        if not all_tables:
            st.warning("No tables found in query_metadata")
            st.stop()
            
        progress_bar = st.progress(0)
        total_tables = len(all_tables)
        
        for i, table_name in enumerate(all_tables):
            with st.expander(f"Table: {table_name}", expanded=True):
                df = fetch_table_data(conn, table_name)
                if df is None or df.empty:
                    st.warning(f"No data available for {table_name}")
                    continue
                    
                line_fig, bar_fig = create_visualizations(df, reference_date, table_name)
                
                # Display graphs vertically with more space
                st.plotly_chart(line_fig, use_container_width=True)
                st.plotly_chart(bar_fig, use_container_width=True)
                
            progress_bar.progress((i + 1) / total_tables)
    
    except Exception as e:
        st.error(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

# CSS improvements
st.markdown("""
<style>
    .stPlotlyChart {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 30px;
        background-color: white;
    }
    .stPlotlyChart:hover {
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
    }
    .stExpander {
        margin-bottom: 30px;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)