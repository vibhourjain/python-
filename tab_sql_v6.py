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
            **{k: v for k, v in db_config.items() if k not in ['format', 'username', 'password']}
        )
        return sqlalchemy.create_engine(connection_string)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def run_query(query, db_config, params=None):
    try:
        username = st.session_state.current_credentials['username']
        password = st.session_state.current_credentials['password']
        
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

def create_excel_download(df, file_name):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    excel_buffer.seek(0)
    return excel_buffer

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

# Credential Handling
credentials = {}
if 'username' in db_config:
    credentials['username'] = db_config['username']
if 'password' in db_config:
    credentials['password'] = db_config['password']

with st.sidebar.expander("Database Credentials", expanded=not bool(credentials)):
    if 'username' not in credentials:
        credentials['username'] = st.text_input("Username", "admin")
    if 'password' not in credentials:
        credentials['password'] = st.text_input("Password", type="password")

st.session_state.current_credentials = credentials

# Main Tabs
tab1, tab3, tab4 = st.tabs([
    "Ad-hoc Query",
    "Upload SQL File",
    "SQL File Management"
])

# Tab1: Ad-hoc Query
with tab1:
    st.subheader("Run Ad-hoc SQL Query")
    query = st.text_area("Enter SQL query:", height=200, key="tab1_query")
    
    if st.button("Run Query", key="tab1_run"):
        st.session_state.pop('tab1_df', None)
        st.session_state.pop('tab1_total', None)
        
        if query.strip():
            with st.spinner("Executing..."):
                results, columns = run_query(query, db_config)
                
                df = pd.DataFrame(results if results else [], columns=columns) if columns else pd.DataFrame()
                st.session_state.tab1_df = df
                st.session_state.tab1_total = len(df)
                
                if not df.empty:
                    st.success(f"✅ Fetched {len(df)} rows")
                    st.dataframe(df.head(10))
                else:
                    if columns:
                        st.info("No data found")
                        st.dataframe(df)
                    else:
                        st.warning("Query failed")

    if 'tab1_df' in st.session_state:
        st.divider()
        st.write(f"**Total records:** {st.session_state.tab1_total}")
        if not st.session_state.tab1_df.empty or st.session_state.tab1_df.columns.any():
            file_name = st.text_input("Export name:", "results", key="tab1_file")
            excel_data = create_excel_download(st.session_state.tab1_df, file_name)
            st.download_button(
                "⬇️ Excel", excel_data,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="tab1_download"
            )

# Tab3: Upload SQL File
with tab3:
    st.subheader("Upload and Execute SQL File")
    
    uploaded_file = st.file_uploader("Choose SQL file", type=["sql"], key="tab3_upload",
                                    on_change=lambda: [st.session_state.pop('tab3_df', None),
                                                      st.session_state.pop('tab3_total', None)])

    MAX_FILE_SIZE = 1024 * 1024  # 1MB

    if uploaded_file:
        # Validate file size
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error("File too large! Max 1MB allowed")
            st.stop()



    if uploaded_file:
        query = uploaded_file.read().decode()
        st.code(query)
        # Validate SQL content
        if "DROP" in query.upper() or "DELETE" in query.upper():
            st.error("Potentially dangerous SQL operations detected")
            st.stop()
        
        if st.button("Execute", key="tab3_execute"):
            st.session_state.pop('tab3_df', None)
            st.session_state.pop('tab3_total', None)
            
            with st.spinner("Executing..."):
                results, columns = run_query(query, db_config)
                
                df = pd.DataFrame(results if results else [], columns=columns) if columns else pd.DataFrame()
                st.session_state.tab3_df = df
                st.session_state.tab3_total = len(df)
                
                if not df.empty:
                    st.success(f"✅ Fetched {len(df)} rows")
                    st.dataframe(df.head(10))
                else:
                    if columns:
                        st.info("No data found")
                        st.dataframe(df)
                    else:
                        st.warning("Query failed")

    if 'tab3_df' in st.session_state and uploaded_file:
        st.divider()
        st.write(f"**Total records:** {st.session_state.tab3_total}")
        if not st.session_state.tab3_df.empty or st.session_state.tab3_df.columns.any():
            file_name = st.text_input("Export name:", "upload_results", key="tab3_file")
            excel_data = create_excel_download(st.session_state.tab3_df, file_name)
            st.download_button(
                "⬇️ Excel", excel_data,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="tab3_download"
            )

# Tab4: SQL File Management
with tab4:
    # Create New File
    with st.container():
        st.subheader("Create New SQL File")
        new_name = st.text_input("New filename:", key="tab4_new")
        new_content = st.text_area("SQL content:", height=300, key="tab4_content")
        
        if st.button("Create", key="tab4_create"):
            if new_name.strip():
                final_name = new_name.strip() + ("" if new_name.endswith(".sql") else ".sql")
                new_path = QUERIES_DIR / final_name
                
                if new_path.exists():
                    st.error("File exists!")
                else:
                    try:
                        with open(new_path, "w") as f:
                            f.write(new_content)
                        st.success("File created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter filename")

    st.divider()

    # Edit Existing Files
    with st.container():
        st.subheader("Edit/Execute Files")
        files = [f.name for f in QUERIES_DIR.glob("*.sql")]
        selected_file = st.selectbox("Select file", files, key="tab4_select")
        
        if selected_file:
            file_path = QUERIES_DIR / selected_file
            with open(file_path, "r") as f:
                content = st.text_area("Edit SQL:", f.read(), height=300, key="tab4_edit")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save & Run", key="tab4_saverun"):
                    with open(file_path, "w") as f:
                        f.write(content)
                    
                    with st.spinner("Executing..."):
                        results, columns = run_query(content, db_config)
                        
                        df = pd.DataFrame(results if results else [], columns=columns) if columns else pd.DataFrame()
                        st.session_state.tab4_df = df
                        st.session_state.tab4_total = len(df)
                        
                        if not df.empty:
                            st.success(f"✅ Fetched {len(df)} rows")
                            st.dataframe(df.head(10))
                        else:
                            if columns:
                                st.info("No data found")
                                st.dataframe(df)
                            else:
                                st.warning("Query failed")
            
            if 'tab4_df' in st.session_state:
                st.divider()
                st.write(f"**Total records:** {st.session_state.tab4_total}")
                if not st.session_state.tab4_df.empty or st.session_state.tab4_df.columns.any():
                    file_name = st.text_input("Export name:", "edit_results", key="tab4_file")
                    excel_data = create_excel_download(st.session_state.tab4_df, file_name)
                    st.download_button(
                        "⬇️ Excel", excel_data,
                        file_name=f"{file_name}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="tab4_download"
                    )