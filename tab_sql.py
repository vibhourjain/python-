import streamlit as st
import sqlalchemy
import yaml
import logging
from datetime import datetime
from pathlib import Path
from io import StringIO, BytesIO
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import time
import uuid
import os

# Configure logging
LOG_FILE = "sql_app.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configuration directories
CONNECTIONS_DIR = Path("connections")
CONNECTIONS_DIR.mkdir(parents=True, exist_ok=True)
QUERIES_DIR = Path("queries")
QUERIES_DIR.mkdir(parents=True, exist_ok=True)

# Default configuration
DEFAULT_CONFIG = """\
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
"""


def load_config(uploaded_file=None):
    try:
        if uploaded_file:
            return yaml.safe_load(uploaded_file)
        else:
            return yaml.safe_load(StringIO(DEFAULT_CONFIG))
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        st.error("Failed to load database configuration.")
        return {}


@st.cache_resource
def init_engine(db_config, username, password):
    try:
        format_str = db_config['format']
        connection_string = format_str.format(
            user=username,
            password=password,
            **{k: v for k, v in db_config.items() if k != 'format'}
        )
        logging.info(f"Database engine initialized for: {db_config}")
        return sqlalchemy.create_engine(connection_string)
    except Exception as e:
        logging.error(f"Connection error: {e}")
        st.error(f"Connection error: {e}")
        return None


def run_query(query, db_config, username, password):
    try:
        engine = init_engine(db_config, username, password)
        if not engine:
            return None, None

        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(query))
            if result.returns_rows:
                data = result.fetchall()
                columns = result.keys()
                logging.info(f"Executed Query: {query} on DB: {db_config}")
                return data, columns
        return [], []
    except Exception as e:
        logging.error(f"Query error: {e}")
        st.error(f"Query error: {e}")
        return None, None


# App Layout
st.title("SQL Query Interface")

# Configuration Section
st.sidebar.header("Database Configuration")

# Initialize config with empty dict to prevent NameError
config = {}

# Connection file management
existing_connections = [f.name for f in CONNECTIONS_DIR.glob("*.yaml")] + ["New Connection"]
selected_connection = st.sidebar.selectbox(
    "Select Existing Connection",
    existing_connections,
    index=0,
    key="existing_connection_select"
)

if selected_connection != "New Connection":
    try:
        with open(CONNECTIONS_DIR / selected_connection, "r") as f:
            config = yaml.safe_load(f)
        st.sidebar.success(f"Loaded connection: {selected_connection}")
        with st.sidebar.expander("Connection Details"):
            st.code(yaml.dump(config), language="yaml")
    except Exception as e:
        st.sidebar.error(f"Error loading connection: {e}")
        config = {}
else:
    uploaded_config = st.sidebar.file_uploader(
        "Upload YAML config",
        type=["yaml", "yml"],
        key="config_uploader"
    )
    # Always load config (uses default if no upload)
    config = load_config(uploaded_config)  # FIXED LINE: Ensures config is always defined
    if uploaded_config:
        # Save uploaded connection
        conn_name = f"connection_{datetime.now().strftime('%Y%m%d%H%M%S')}.yaml"
        with open(CONNECTIONS_DIR / conn_name, "wb") as f:
            f.write(uploaded_config.getvalue())
        st.sidebar.success(f"Saved connection as: {conn_name}")

# Database Selection (NOW SAFE)
db_names = list(config.get('databases', {}).keys())  # FIXED: Added missing parenthesis
selected_db = st.sidebar.selectbox(
    "Select Database",
    db_names if db_names else ["None"],
    key="db_selection"
)
db_config = config['databases'].get(selected_db, {}) if selected_db != "None" else {}

# # Database Selection
# db_names = list(config.get('databases', {}).keys())
# selected_db = st.sidebar.selectbox(
#     "Select Database",
#     db_names if db_names else ["None"],
#     key="db_selection"
# )
# db_config = config['databases'].get(selected_db, {}) if selected_db != "None" else {}

# Credential Inputs
username = st.sidebar.text_input("Username", "admin", key="db_username")
password = st.sidebar.text_input("Password", type="password", key="db_password")

# Tabs
tab1, tab2, tab3 = st.tabs(["Run SQL Query", "Upload SQL File", "Edit Existing SQL"])

# Tab 1: Run SQL Query
with tab1:
    st.subheader("Execute SQL Query")

    # Session state management
    session_keys = ['request_number', 'sheet_name']
    for key in session_keys:
        if key not in st.session_state:
            st.session_state[key] = ""

    request_number = st.text_input(
        "Request # (Optional)",
        value=st.session_state.request_number,
        key="request_number_input"
    )
    sheet_name = st.text_input(
        "Excel Sheet Name (Optional)",
        value=st.session_state.sheet_name or "QueryResult",
        key="sheet_name_input"
    )

    query = st.text_area("Enter your SQL query:", height=200, key="query_input")

    if st.button("Run Query", key="run_query_btn"):
        if query:
            results, columns = run_query(query, db_config=db_config, username=username, password=password)
            if results is not None:
                df = pd.DataFrame(results, columns=columns)
                execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                record_count = len(df)
                st.success(f"Query Execution Completed! Total Records: {record_count}, Executed at: {execution_time}")
                st.dataframe(df)

                file_name = f"{request_number}_QueryResult.xlsx" if request_number else "QueryResult.xlsx"
                file_path = Path(file_name)

                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]

                    for i, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, max_len)

                    writer.close()

                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Download Excel",
                        data=file,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel_btn"
                    )
        else:
            st.warning("Please enter a SQL query")

# Tab 2: Upload SQL File
with tab2:
    st.subheader("Upload and Execute SQL File")
    uploaded_file = st.file_uploader("Choose a SQL file", type=["sql"], key="sql_uploader")
    if uploaded_file:
        query = uploaded_file.read().decode()
        st.code(query)
        if st.button("Execute Uploaded Query", key="execute_uploaded_btn"):
            results, columns = run_query(query, db_config=db_config, username=username, password=password)
            if results is not None:
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)

# Tab 3: Edit Existing SQL
with tab3:
    st.subheader("Edit and Execute SQL Files")
    sql_files = [f.name for f in QUERIES_DIR.glob("*.sql")]
    selected_file = st.selectbox("Select SQL File", sql_files, key="sql_file_select")
    if selected_file:
        file_path = QUERIES_DIR / selected_file
        with open(file_path, "r") as f:
            content = f.read()
        updated_content = st.text_area("Edit SQL", value=content, height=300, key="sql_editor")
        if st.button("Save & Execute", key="save_execute_btn"):
            with open(file_path, "w") as f:
                f.write(updated_content)
            results, columns = run_query(updated_content, db_config=db_config, username=username, password=password)
            if results is not None:
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)