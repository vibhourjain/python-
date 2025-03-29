import streamlit as st
import sqlite3
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Initialize SQLite database with metadata table
def init_db():
    conn = sqlite3.connect('capacity.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apps 
                 (app_name TEXT PRIMARY KEY, 
                  table_name TEXT UNIQUE, 
                  sql_query TEXT,
                  db_config TEXT)''')
    conn.commit()
    return conn

def get_existing_columns(conn, table_name):
    """Get existing columns in a table"""
    try:
        return [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")]
    except sqlite3.OperationalError:
        return []

# Page 1: Database Setup
def page_db_setup(row=None):
    st.header("Database Configuration")
    conn = init_db()
    
    # Initialize session state
    if 'columns' not in st.session_state:
        st.session_state.columns = []
    if 'selected_app' not in st.session_state:
        st.session_state.selected_app = None

    # Application selection
    existing_apps = pd.read_sql("SELECT app_name, table_name FROM apps", conn)['app_name'].tolist()
    selected_app = st.selectbox("Select Existing Application (or create new)", [""] + existing_apps)

    if selected_app:
        # Load existing application configuration
        app_config = pd.read_sql(f"SELECT * FROM apps WHERE app_name = '{selected_app}'", conn).iloc[0]
        st.session_state.selected_app = app_config

        # Get column details from existing table
        table_info = conn.execute(f"PRAGMA table_info({app_config['table_name']})").fetchall()

        # Parse column definitions
        st.session_state.columns = []
        for row in table_info:
            col_name = row[1]
            col_type = row[2].split('(')[0].upper()
            col_length = int(row[2].split('(')[1].split(')')[0]) if '(' in row[2] else None

            st.session_state.columns.append(
                (col_name, col_type, col_length)
            )

    # Application and table name inputs
    new_app_name = st.text_input("New Application Name", 
                               value=st.session_state.selected_app['app_name'] 
                               if st.session_state.selected_app else "")
    new_table_name = st.text_input("Table Name", 
                                 value=st.session_state.selected_app['table_name'] 
                                 if st.session_state.selected_app else "")
    
    # Database connection details
    db_config = st.text_area("Database Connection String",
                           value=st.session_state.selected_app['db_config'] 
                           if st.session_state.selected_app else "")
    
    # SQL query template
    sql_query = st.text_area("SQL Query Template (use ? for parameters)",
                           value=st.session_state.selected_app['sql_query'] 
                           if st.session_state.selected_app else "")

    # Column management
    st.subheader("Column Management")
    with st.form("add_column_form"):
        cols = st.columns([3, 2, 2, 1])
        new_col_name = cols[0].text_input("Column Name")
        new_col_type = cols[1].selectbox("Data Type", ["TEXT", "INTEGER", "REAL", "DATE"])
        new_col_length = cols[2].number_input("Length", min_value=1, value=255, 
                                            disabled=(new_col_type != "TEXT"))
        
        if cols[3].form_submit_button("➕ Add"):
            existing_names = [col[0] for col in st.session_state.columns]
            if not new_col_name:
                st.error("Column name cannot be empty!")
            elif new_col_name in existing_names:
                st.error(f"Column '{new_col_name}' already exists!")
            else:
                col_def = (new_col_name, new_col_type, new_col_length) if new_col_type == "TEXT" \
                          else (new_col_name, new_col_type, None)
                st.session_state.columns.append(col_def)
                st.success(f"Column '{new_col_name}' added!")

    # Display current columns with removal
    if st.session_state.columns:
        st.write("**Current Columns:**")
        for idx, col in enumerate(st.session_state.columns):
            cols = st.columns([0.7, 0.2, 0.1])
            cols[0].write(f"{col[0]} ({col[1]}{f'({col[2]})' if col[2] else ''})")
            if cols[2].button("❌", key=f"remove_{idx}"):
                del st.session_state.columns[idx]
                st.rerun()

    # Table creation/modification
    with st.form("main_form"):
        if st.form_submit_button("Save Configuration"):
            # Validation
            if not new_app_name:
                st.error("Application Name is required!")
                return
            if not new_table_name:
                st.error("Table Name is required!")
                return
            if not st.session_state.columns:
                st.error("At least one column is required!")
                return

            try:
                # Check for existing application
                existing = pd.read_sql(
                    f"SELECT * FROM apps WHERE app_name = '{new_app_name}' OR table_name = '{new_table_name}'", 
                    conn
                )
                if not existing.empty and (st.session_state.selected_app is None or 
                                         existing.iloc[0]['app_name'] != new_app_name):
                    st.error("Application or Table name already exists!")
                    return

                # Create/Alter table
                columns_def = []
                for col in st.session_state.columns:
                    if col[1] == "TEXT":
                        columns_def.append(f"{col[0]} {col[1]}({col[2]})")
                    else:
                        columns_def.append(f"{col[0]} {col[1]}")

                # Create or alter table
                c = conn.cursor()
                try:
                    c.execute(f"CREATE TABLE {new_table_name} ({', '.join(columns_def)})")
                except sqlite3.OperationalError:
                    # Table exists, alter it
                    existing_columns = get_existing_columns(conn, new_table_name)
                    for col in st.session_state.columns:
                        if col[0] not in existing_columns:
                            col_def = f"{col[0]} {col[1]}({col[2]})" if col[1] == "TEXT" \
                                      else f"{col[0]} {col[1]}"
                            c.execute(f"ALTER TABLE {new_table_name} ADD COLUMN {col_def}")

                # Update metadata
                c.execute('''REPLACE INTO apps (app_name, table_name, sql_query, db_config)
                             VALUES (?, ?, ?, ?)''',
                         (new_app_name, new_table_name, sql_query, db_config))
                
                conn.commit()
                st.success("Configuration saved successfully!")
                st.session_state.selected_app = None
                st.session_state.columns = []

            except sqlite3.Error as e:
                st.error(f"Database error: {str(e)}")
            finally:
                conn.close()


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
            ).iloc[0, 0]
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