import streamlit as st
import sqlalchemy
import yaml
from datetime import date
from pathlib import Path
from io import StringIO
import pandas as pd



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


# Database Configuration Management
def load_config(uploaded_file=None):
    if uploaded_file:
        return yaml.safe_load(uploaded_file)
    else:
        return yaml.safe_load(StringIO(DEFAULT_CONFIG))


@st.cache_resource
def init_engine(db_config, username, password):
    try:
        format_str = db_config['format']
        connection_string = format_str.format(
            user=username,
            password=password,
            **{k: v for k, v in db_config.items() if k != 'format'}
        )
        return sqlalchemy.create_engine(connection_string)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def run_query(query, db_config, username, password, params=None):
    try:
        engine = init_engine(db_config, username, password)
        if not engine:
            return None, None

        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(query), params)
            if result.returns_rows:
                return result.fetchall(), result.keys()
        return None, None
    except Exception as e:
        st.error(f"Query error: {e}")
        return None, None


# Setup
QUERIES_DIR = Path("queries")
QUERIES_DIR.mkdir(parents=True, exist_ok=True)

# App Layout
st.title("SQL Query Interface")

# Configuration Section
st.sidebar.header("Database Configuration")
uploaded_config = st.sidebar.file_uploader("Upload YAML config", type=["yaml", "yml"])
config = load_config(uploaded_config)

# Database Selection
db_names = list(config['databases'].keys())
selected_db = st.sidebar.selectbox("Select Database", db_names)
db_config = config['databases'][selected_db]

# Credential Inputs
username = st.sidebar.text_input("Username", "admin")
password = st.sidebar.text_input("Password", type="password")

# Display configuration details
with st.sidebar.expander("Current Configuration"):
    st.code(yaml.dump(config['databases'][selected_db], sort_keys=False))

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Ad-hoc Query",
    "Parameterized Query",
    "Upload SQL File",
    "Edit Existing SQL"
])

# Tab 1: Ad-hoc Query
with tab1:
    st.subheader("Run Ad-hoc SQL Query")
    query = st.text_area("Enter your SQL query:", height=200)
    if st.button("Run Query"):
        if query:
            results, columns = run_query(query, db_config=db_config, username=username, password=password
                                         )
            if results:
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)
                # st.dataframe(results, columns=columns)

        else:
            st.warning("Please enter a SQL query")

# Other tabs would need similar modifications to pass db_config, username, password
# ... (remaining tab implementations follow similar pattern)



# Tab 2: Parameterized Monthly Query
with tab2:
    st.subheader("Monthly Query with Parameters")
    template = """SELECT *
FROM sales
WHERE order_date BETWEEN :start_date AND :end_date
-- Add your monthly query logic here"""

    query = st.text_area("Query Template", value=template, height=200)
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", date(2023, 1, 1))
    end_date = col2.date_input("End Date", date(2023, 12, 31))

    if st.button("Execute Monthly Query"):
        params = {"start_date": start_date, "end_date": end_date}
        results, columns = run_query(query, db_config=db_config, username=username, password=password,params=params)
        if results:
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df)

# Tab 3: Upload SQL File
with tab3:
    st.subheader("Upload and Execute SQL File")
    uploaded_file = st.file_uploader("Choose a SQL file", type=["sql"])
    if uploaded_file:
        query = uploaded_file.read().decode()
        st.code(query)
        if st.button("Execute Uploaded Query"):
            results, columns = run_query(query, db_config=db_config, username=username, password=password)
            if results:
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)

# Tab 4: Edit Existing SQL
with tab4:
    st.subheader("Edit and Execute Existing SQL Files")
    files = [f.name for f in QUERIES_DIR.glob("*.sql")]
    selected_file = st.selectbox("Choose a SQL file", files)

    if selected_file:
        file_path = QUERIES_DIR / selected_file
        with open(file_path, "r") as f:
            query = st.text_area("Edit SQL", value=f.read(), height=300)

        if st.button("Save and Execute"):
            with open(file_path, "w") as f:
                f.write(query)
            results, columns = run_query(query, db_config=db_config, username=username, password=password)
            if results:
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)

# Create new SQL files
with tab4:
    st.divider()
    new_file = st.text_input("Create new SQL file (name.sql)")
    if new_file:
        if not new_file.endswith(".sql"):
            new_file += ".sql"
        if st.button("Create"):
            (QUERIES_DIR / new_file).touch()
            st.rerun()  # Updated to st.rerun()