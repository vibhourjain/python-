import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from contextlib import contextmanager

# --------------------------
# Database Connection Setup
# --------------------------
@st.cache_resource
def init_connection():
    """Initialize and cache DuckDB connection"""
    return duckdb.connect(database='your_database.duckdb', read_only=True)

@contextmanager
def get_db_connection():
    """Context manager for handling database connections"""
    conn = init_connection()
    try:
        yield conn
    except duckdb.Error as e:
        st.error(f"Database error: {str(e)}")
    finally:
        # Connection is managed by cache_resource
        pass

# --------------------------
# Data Fetching Functions
# --------------------------
def get_table_list():
    """Fetch all distinct tables from query_metadata"""
    with get_db_connection() as conn:
        return conn.execute("""
            SELECT DISTINCT target_table 
            FROM query_metadata
            ORDER BY target_table
        """).fetchdf()['target_table'].tolist()

def fetch_table_data(table_name, reference_date):
    """Fetch only the required 13 months data using DuckDB date functions"""
    with get_db_connection() as conn:
        try:
            return conn.execute(f"""
                SELECT 
                    Application_type, 
                    Volume, 
                    Period
                FROM {table_name}
                WHERE 
                    CAST(Period AS DATE) BETWEEN 
                        DATE_SUB(CAST('{reference_date}' AS DATE), INTERVAL 13 MONTH) AND
                        CAST('{reference_date}' AS DATE)
                ORDER BY Period
            """).fetchdf()
        except Exception as e:
            st.error(f"Error fetching data from {table_name}: {str(e)}")
            return pd.DataFrame()

# --------------------------
# Visualization Functions
# --------------------------
def create_visualizations(df, table_name):
    """Create both visualizations with improved formatting and width"""
    if df.empty:
        return None, None
    
    # Convert Period to datetime
    df['Period'] = pd.to_datetime(df['Period'])
    
    # Create consistent color mapping
    app_types = sorted(df['Application_type'].unique())
    colors = px.colors.qualitative.Plotly
    color_map = {app: colors[i % len(colors)] for i, app in enumerate(app_types)}
    
    # --------------------------
    # Line Chart Configuration
    # --------------------------
    line_fig = px.line(
        df,
        x='Period',
        y='Volume',
        color='Application_type',
        title=f'{table_name} - Volume Trend',
        labels={'Period': '', 'Volume': 'Volume'},
        color_discrete_map=color_map,
        height=600,
        width=1400  # Increased width
    )
    
    line_fig.update_xaxes(
        tickformat="%b %Y",
        dtick="M1",
        tickangle=45,
        tickfont=dict(size=12),
        ticklabelmode="period",
        nticks=len(df['Period'].unique()),
        rangeslider_visible=True
    )
    
    # --------------------------
    # Bar Chart Configuration
    # --------------------------
    df['Month-Year'] = df['Period'].dt.strftime('%b %Y')
    
    bar_fig = px.bar(
        df,
        x='Month-Year',
        y='Volume',
        color='Application_type',
        title=f'{table_name} - Monthly Comparison',
        labels={'Month-Year': '', 'Volume': 'Volume'},
        color_discrete_map=color_map,
        barmode='group',
        height=600,
        width=1400  # Increased width
    )
    
    bar_fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=12),
        tickmode='array',
        tickvals=df['Month-Year'].unique()[::2],
        ticktext=df['Month-Year'].unique()[::2]
    )
    
    # --------------------------
    # Common Layout Settings
    # --------------------------
    for fig in [line_fig, bar_fig]:
        fig.update_layout(
            margin=dict(l=50, r=50, t=80, b=200),  # Extra bottom margin
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.4,  # Further down for wide charts
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            hoverlabel=dict(
                font_size=14,
                font_family="Arial"
            ),
            plot_bgcolor='rgba(240,240,240,0.8)',
            paper_bgcolor='rgba(240,240,240,0.5)',
            font=dict(size=12)
        )
    
    return line_fig, bar_fig

# --------------------------
# Streamlit UI
# --------------------------
def main():
    st.set_page_config(layout="wide", page_title="Data Analysis Dashboard")
    
    # Custom CSS for better appearance
    st.markdown("""
    <style>
        .stPlotlyChart {
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        .stExpander {
            margin-bottom: 2rem;
            border-radius: 10px;
            padding: 1rem;
            background-color: #f9f9f9;
        }
        .stExpander:hover {
            box-shadow: 0 0 0 2px #636efa;
        }
        h1 {
            color: #2c3e50;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title('📈 Automated Data Analysis Dashboard')
    
    # Date input
    reference_date = st.date_input(
        "Select Reference Date",
        datetime.today(),
        key='date_selector'
    )
    
    if not reference_date:
        return
    
    try:
        all_tables = get_table_list()
        
        if not all_tables:
            st.warning("No tables found in query_metadata")
            return
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_tables = len(all_tables)
        
        for i, table_name in enumerate(all_tables):
            status_text.text(f"Processing {i+1} of {total_tables}: {table_name}")
            
            with st.expander(f"📊 {table_name}", expanded=(i < 2)):
                df = fetch_table_data(table_name, reference_date)
                
                if df.empty:
                    st.warning(f"No data available for {table_name} in selected date range")
                    continue
                    
                line_fig, bar_fig = create_visualizations(df, table_name)
                
                # Display charts with container width but maintaining aspect
                st.plotly_chart(line_fig, use_container_width=True)
                st.plotly_chart(bar_fig, use_container_width=True)
                
                # Raw data toggle
                if st.checkbox(f"Show raw data for {table_name}", False, key=f"raw_{table_name}"):
                    st.dataframe(df.sort_values('Period').style.format({
                        'Volume': '{:,.0f}',
                        'Period': lambda x: x.strftime('%Y-%m-%d')
                    }))
            
            progress_bar.progress((i + 1) / total_tables)
        
        status_text.success(f"✅ Processed {len(all_tables)} tables successfully!")
    
    except Exception as e:
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()