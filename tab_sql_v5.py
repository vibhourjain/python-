import streamlit as st
import sqlalchemy
import yaml
from datetime import date
from pathlib import Path
from io import StringIO, BytesIO
import pandas as pd
import io


# Default configuration
DEFAULT_CONFIG = """
databases:
  MySQL:
    type: mysql
    host: localhost
    port: 3306
    format: "mysql://{user}:{password}@{host}:{port}/{dbname}"

  PostgreSQL:
    type: postgresql
    host: localhost
    port: 5432
    format: "postgresql://{user}:{password}@{host}:{port}/{dbname}"

  Oracle:
    type: oracle
    host: localhost
    port: 1521
    service_name: ORCL
    format: "oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service_name}"

  MSSQL:
    type: mssql
    host: localhost
    port: 1433
    driver: "ODBC Driver 17 for SQL Server"
    format: "mssql+pyodbc://{user}:{password}@{host}:{port}/{dbname}?driver={driver}"

  Sybase:
    type: sybase
    dsn: "DSN_NAME"
    format: "sybase+pyodbc://{user}:{password}@{dsn}"
"""



# Add to configuration section
CONFIG_FILE = "db_config.yaml"


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)


# Modified configuration loading
def load_config(uploaded_file=None):
    try:
        # First try to load saved config
        with open(CONFIG_FILE, "r") as f:
            saved_config = yaml.safe_load(f)
    except FileNotFoundError:
        saved_config = None

    if uploaded_file:
        # If user uploads new config, merge with saved config
        new_config = yaml.safe_load(uploaded_file)
        merged_config = {**saved_config, **new_config} if saved_config else new_config
        save_config(merged_config)
        return merged_config

    return saved_config if saved_config else yaml.safe_load(StringIO(DEFAULT_CONFIG))


# In your sidebar section
# In configuration section
st.sidebar.header("Database Configuration")
uploaded_config = st.sidebar.file_uploader("Upload YAML config", type=["yaml", "yml"])

# Load config (temporary in memory only)
config = load_config(uploaded_config)  # Use existing load_config function

# Database Selection
db_names = list(config['databases'].keys())
selected_db = st.sidebar.selectbox("Select Database", db_names)
db_config = config['databases'][selected_db]

# Credential handling from config or manual input
credentials = {}
if 'username' in db_config:
    credentials['username'] = db_config['username']
if 'password' in db_config:
    credentials['password'] = db_config['password']

# Manual credential inputs if not in config
with st.sidebar.expander("Credentials", expanded=not bool(credentials)):
    if 'username' not in credentials:
        credentials['username'] = st.text_input("Username", "admin")
    if 'password' not in credentials:
        credentials['password'] = st.text_input("Password", type="password")

# Store in session state
st.session_state.current_credentials = credentials

# Modified run_query function
def run_query(query, db_config, params=None):
    try:
        # Get credentials from session state
        username = st.session_state.current_credentials['username']
        password = st.session_state.current_credentials['password']
        
        engine = init_engine(db_config, username, password)
        # Rest of existing query execution logic...

# Main Tabs
tab1, tab2, tab3= st.tabs([
    "Ad-hoc Query",
    # "Parameterized Query",
    "Upload SQL File",
    "Edit Existing SQL"
])

# Helper function for Excel download
def create_excel_download(df, file_name):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    excel_buffer.seek(0)
    return excel_buffer


# Tab1: Ad-hoc Query
with tab1:
    st.subheader("Run Ad-hoc SQL Query")
    query = st.text_area("Enter your SQL query:", height=200, key="tab1_query")

    if st.button("Run Query", key="tab1_run"):
        # Clear previous results
        st.session_state.pop('tab1_df', None)
        st.session_state.pop('tab1_total', None)

        if query.strip():
            with st.spinner("Executing query..."):
                results, columns = run_query(query, db_config, username, password)

                # Always create DataFrame to preserve column information
                if columns:
                    df = pd.DataFrame(results if results else [], columns=columns)
                else:
                    df = pd.DataFrame()

                # Store results in session state
                st.session_state.tab1_df = df
                st.session_state.tab1_total = len(df)

                # Display appropriate message
                if not df.empty:
                    st.success(f"✅ Success! Fetched {len(df)} rows")
                    st.dataframe(df.head(10))
                else:
                    if columns:
                        st.info("Query executed successfully but returned no data")
                        # Show empty dataframe with columns
                        st.dataframe(df)
                    else:
                        st.warning("No results found")

        else:
            st.warning("Please enter a query")

    # Display results section if query was executed
    if 'tab1_df' in st.session_state:
        st.divider()
        st.write(f"**Total records:** {st.session_state.tab1_total}")

        # Always show download button with column headers
        if not st.session_state.tab1_df.empty or (st.session_state.tab1_df.columns.any()):
            file_name = st.text_input("File name for export:", "results", key="tab1_file")
            excel_data = create_excel_download(st.session_state.tab1_df, file_name)

            st.download_button(
                "⬇️ Download Excel",
                data=excel_data,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="tab1_download"
            )
# # Tab 2: Parameterized Monthly Query
# with tab2:
#     st.subheader("Monthly Query with Parameters")
#     template = """SELECT *
# FROM sales
# WHERE order_date BETWEEN :start_date AND :end_date
# -- Add your monthly query logic here"""
#
#     query = st.text_area("Query Template", value=template, height=200, key="tab2_query")
#     col1, col2 = st.columns(2)
#     start_date = col1.date_input("Start Date", date(2023, 1, 1), key="tab2_start")
#     end_date = col2.date_input("End Date", date(2023, 12, 31), key="tab2_end")
#
#     if st.button("Execute Monthly Query", key="tab2_execute"):
#         if not query.strip():
#             st.warning("Please enter a query template")
#         else:
#             with st.spinner("Executing parameterized query..."):
#                 try:
#                     params = {"start_date": start_date, "end_date": end_date}
#                     results, columns = run_query(
#                         query,
#                         db_config=db_config,
#                         username=username,
#                         password=password,
#                         params=params
#                     )
#                     if results:
#                         df = pd.DataFrame(results, columns=columns)
#                         st.session_state.tab2_df = df
#                         st.session_state.tab2_total = len(df)
#                         st.success(f"✅ Found {len(df)} records")
#                         st.dataframe(df.head(10))
#                     else:
#                         st.warning("No results found")
#                 except Exception as e:
#                     st.error(f"Query execution failed: {str(e)}")

# Tab 2: Upload SQL File
with tab2:
    st.subheader("Upload and Execute SQL File")

    # Clear results when new file is uploaded
    uploaded_file = st.file_uploader("Choose a SQL file", type=["sql"], key="tab3_upload",
                                     on_change=lambda: [st.session_state.pop('tab3_df', None),
                                                        st.session_state.pop('tab3_total', None)])

    if uploaded_file:
        query = uploaded_file.read().decode()
        st.code(query)

        if st.button("Execute Uploaded Query", key="tab3_execute"):
            # Clear previous results
            st.session_state.pop('tab3_df', None)
            st.session_state.pop('tab3_total', None)

            with st.spinner("Executing uploaded query..."):
                results, columns = run_query(query, db_config=db_config,
                                             username=username, password=password)

                # Always create DataFrame to preserve column information
                if columns:
                    df = pd.DataFrame(results if results else [], columns=columns)
                else:
                    df = pd.DataFrame()

                # Store results in session state
                st.session_state.tab3_df = df
                st.session_state.tab3_total = len(df)

                # Display appropriate message
                if not df.empty:
                    st.success(f"✅ Executed successfully! Fetched {len(df)} rows")
                    st.dataframe(df.head(10))
                else:
                    if columns:
                        st.info("Query executed successfully but returned no data")
                        st.dataframe(df)  # Show empty dataframe with columns
                    else:
                        st.warning("No results found")

    # Display results section only if there's current data
    if 'tab3_df' in st.session_state and uploaded_file:
        st.divider()
        st.write(f"**Total records:** {st.session_state.tab3_total}")

        # Always show download button with column headers
        if not st.session_state.tab3_df.empty or (st.session_state.tab3_df.columns.any()):
            file_name = st.text_input("File name for export:", "uploaded_results", key="tab3_file")
            excel_data = create_excel_download(st.session_state.tab3_df, file_name)

            st.download_button(
                "⬇️ Download Excel",
                data=excel_data,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="tab3_download"
            )

# Tab 3: Edit Existing SQL
with tab3:
    # Container 1: Create New File
    with st.container():
        st.subheader("Create New SQL File")

        # Initialize session state for success message
        if 'create_success' not in st.session_state:
            st.session_state.create_success = None

        new_file_name = st.text_input("New file name (e.g., new_query.sql):", key="new_file_name")
        new_file_content = st.text_area("SQL Content:", height=300, key="new_file_content")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Create New", key="create_new"):
                if not new_file_name.strip():
                    st.warning("Please enter a file name")
                else:
                    try:
                        # Ensure .sql extension
                        final_name = new_file_name.strip()
                        if not final_name.endswith(".sql"):
                            final_name += ".sql"

                        new_path = QUERIES_DIR / final_name

                        if new_path.exists():
                            st.error("File already exists!")
                        else:
                            with open(new_path, "w") as f:
                                f.write(new_file_content)
                            st.session_state.create_success = final_name
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error creating file: {str(e)}")

        # Show success message after rerun
        if st.session_state.create_success:
            st.success(f"File '{st.session_state.create_success}' created successfully!")
            # Clear the success message after display
            st.session_state.create_success = None

    st.divider()

    if 'create_success' in st.session_state:
        del st.session_state.create_success
    # Container 2: Edit & Execute Existing Files
    with st.container():
        st.subheader("Edit & Execute Existing Files")

        # Refresh file list
        files = [f.name for f in QUERIES_DIR.glob("*.sql")]
        selected_file = st.selectbox("Select SQL File", files, key="file_selector")

        if selected_file:
            file_path = QUERIES_DIR / selected_file

            # Load file content
            with open(file_path, "r") as f:
                file_content = f.read()

            # Editable text area
            updated_content = st.text_area("Edit SQL Content:", value=file_content, height=300, key="editor")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save & Run", key="save_run"):
                    try:
                        # Save changes
                        with open(file_path, "w") as f:
                            f.write(updated_content)

                        # Execute query
                        with st.spinner("Executing query..."):
                            results, columns = run_query(updated_content, db_config, username, password)
                            if results:
                                df = pd.DataFrame(results, columns=columns)
                                st.session_state.tab4_df = df
                                st.session_state.tab4_total = len(df)
                                st.success(f"✅ Saved and executed! Found {len(df)} rows")
                                st.dataframe(df.head(10))
                            else:
                                if columns:
                                    st.info("Query executed successfully but returned no data")
                                    st.dataframe(pd.DataFrame(columns=columns))
                                else:
                                    st.warning("No results found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            with col2:
                if st.button("Save Only", key="save_only"):
                    try:
                        with open(file_path, "w") as f:
                            f.write(updated_content)
                        st.success("File saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving file: {str(e)}")

        # Download functionality
        if "tab4_df" in st.session_state:
            st.divider()
            st.write(f"**Total records:** {st.session_state.tab4_total}")
            file_name = st.text_input("Export filename:", "query_results", key="tab4_export")
            excel_data = create_excel_download(st.session_state.tab4_df, file_name)

            st.download_button(
                "⬇️ Download Excel",
                data=excel_data,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="tab4_download"
            )