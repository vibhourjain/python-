import streamlit as st
import sqlite3
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('capacity.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apps 
                 (app_name TEXT PRIMARY KEY, table_name TEXT, sql_query TEXT, db_config TEXT)''')
    conn.commit()
    return conn

# Page 1: Database Setup
def page_db_setup():
    st.header("Database Configuration")
    
    with st.form("create_table_form"):
        app_name = st.text_input("Application Name")
        table_name = st.text_input("Table Name")
        
        # Dynamic column addition
        if 'columns' not in st.session_state:
            st.session_state.columns = []
            
        cols = st.columns(3)
        with cols[0]:
            new_col_name = st.text_input("Column Name")
        with cols[1]:
            new_col_type = st.selectbox("Data Type", ["TEXT", "INTEGER", "REAL", "DATE"])
        with cols[2]:
            new_col_length = st.number_input("Length", min_value=1, value=255)
            
        if st.form_submit_button("Add Column"):
            st.session_state.columns.append((new_col_name, new_col_type, new_col_length))
            
        if st.form_submit_button("Create Table"):
            conn = init_db()
            c = conn.cursor()
            
            # Build create table query
            columns_def = ", ".join(
                [f"{col[0]} {col[1]}({col[2]})" if col[1] in ["TEXT"] else f"{col[0]} {col[1]}" 
                 for col in st.session_state.columns]
            )
            c.execute(f"CREATE TABLE {table_name} ({columns_def})")
            
            # Store app configuration
            c.execute("INSERT INTO apps VALUES (?, ?, ?, ?)", 
                     (app_name, table_name, "", ""))
            conn.commit()
            st.success(f"Table {table_name} created successfully!")

# Page 2: Data Sync
def page_data_sync():
    st.header("Data Synchronization")
    conn = init_db()
    apps = pd.read_sql("SELECT app_name, table_name FROM apps", conn)
    
    selected_app = st.selectbox("Select Application", apps['app_name'])
    end_date = st.date_input("End Date", datetime.today())
    
    if st.button("Sync Data"):
        # Get app configuration
        app_config = pd.read_sql(
            f"SELECT * FROM apps WHERE app_name = '{selected_app}'", conn
        ).iloc[0]
        
        # Get last sync date
        try:
            max_date = pd.read_sql(
                f"SELECT MAX(hire_date) FROM {app_config['table_name']}", conn
            ).iloc[0,0]
        except:
            max_date = None
            
        start_date = max_date or end_date - timedelta(days=395)  # ~13 months
        
        # Connect to Sybase
        with pyodbc.connect(app_config['db_config']) as syb_conn:
            sql = app_config['sql_query'].replace("?", "'{}'").format(start_date, end_date)
            df = pd.read_sql(sql, syb_conn)
            
        # Add derived column
        df['drv_prd'] = df['hire_date'].dt.to_period('M').astype(str)
        
        # Save to local DB
        df.to_sql(app_config['table_name'], conn, if_exists='append', index=False)
        st.success(f"Synced {len(df)} records!")

# Page 3: Reporting
def page_reporting():
    st.header("Reporting & Analysis")
    conn = init_db()
    apps = pd.read_sql("SELECT app_name, table_name FROM apps", conn)
    
    selected_app = st.selectbox("Application", apps['app_name'])
    ref_date = st.date_input("Reference Date", datetime.today())
    
    if st.button("Generate Report"):
        # Calculate date range
        start_date = ref_date - timedelta(days=395)
        
        # Get data
        table_name = apps[apps['app_name'] == selected_app]['table_name'].iloc[0]
        df = pd.read_sql(
            f"SELECT * FROM {table_name} WHERE hire_date BETWEEN ? AND ?",
            conn, 
            params=(start_date, ref_date))
        
        # Generate plot
        fig, ax = plt.subplots()
        df.plot(x='hire_date', y='num_of_employee', ax=ax)
        st.pyplot(fig)
        
        # Export to Excel
        excel_file = f"{selected_app}_report.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as f:
            st.download_button("Download Excel Report", f, file_name=excel_file)

# Main App
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Database Setup", "Data Sync", "Reporting"])
    
    if page == "Database Setup":
        page_db_setup()
    elif page == "Data Sync":
        page_data_sync()
    elif page == "Reporting":
        page_reporting()

if __name__ == "__main__":
    main()