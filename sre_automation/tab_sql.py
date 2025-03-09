import streamlit as st
import sqlalchemy
import yaml
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from io import StringIO, BytesIO
import time
import uuid
import os




# Configuration
CONNECTIONS_DIR = Path("connections")
QUERIES_DIR = Path("queries")
LOG_DIR = Path("logs")
for dir in [CONNECTIONS_DIR, QUERIES_DIR, LOG_DIR]:
    dir.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=LOG_DIR / "sql_app.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(user)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_connection_files():
    """Get sorted connection files with UUID-based cache busting"""
    files = [(f, f.stat().st_ctime) for f in CONNECTIONS_DIR.glob("*.yaml")]
    return sorted(files, key=lambda x: x[1], reverse=True)


def save_connection(content: bytes) -> str:
    """Save connection file with validation"""
    try:
        # Validate YAML first
        yaml.safe_load(content)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"connection_{timestamp}.yaml"
        path = CONNECTIONS_DIR / filename

        with open(path, "wb") as f:
            f.write(content)
            f.flush()  # Force write to disk
            os.fsync(f.fileno())

        return filename
    except yaml.YAMLError as e:
        st.error(f"Invalid YAML: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Save failed: {str(e)}")
        return None


def get_logger():
    logger = logging.getLogger()
    logger.user = st.session_state.get('user_id', 'system')
    return logger


# Database connection and utilities
@st.cache_resource(ttl=300, show_spinner=False)
def init_engine(db_config, username, password):
    try:
        format_str = db_config['format']
        conn_str = format_str.format(
            user=username,
            password=password,
            **{k: v for k, v in db_config.items() if k != 'format'}
        )
        return sqlalchemy.create_engine(conn_str, pool_recycle=300)
    except Exception as e:
        get_logger().error(f"Connection error: {e}", extra={'user': username})
        return None


def test_connection(engine, db_type):
    test_query = "SELECT 1 FROM DUAL" if db_type.lower() == 'oracle' else "SELECT 1"
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(test_query))
        return True
    except Exception as e:
        get_logger().error(f"Connection test failed: {e}")
        return False


# Session state management
def init_session():
    session_keys = {
        'request_number': '',
        'sheet_name': 'QueryResult',
        'user_id': str(uuid.uuid4()),
        'download_format': 'excel'
    }
    for key, val in session_keys.items():
        if key not in st.session_state:
            st.session_state[key] = val


# File handling utilities
def save_connection(file_content):
    conn_name = f"connection_{datetime.now().strftime('%Y%m%d%H%M%S')}.yaml"
    with open(CONNECTIONS_DIR / conn_name, "wb") as f:
        f.write(file_content)
    return conn_name


def generate_filename(request_number):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if request_number:
        return f"{request_number}_{timestamp}"
    return f"QueryResult_{timestamp}"


# UI Components
def connection_manager():
    st.sidebar.header("Database Connection Manager")

    # File uploader with enhanced validation
    uploaded_file = st.sidebar.file_uploader(
        "Upload YAML Config",
        type=["yaml"],
        key=f"yaml_uploader_{uuid.uuid4()}",  # Unique key
        help="Upload database connection YAML file"
    )

    if uploaded_file:
        # Show upload status
        with st.sidebar.status("Processing connection file..."):
            # Validate and save
            saved_name = save_connection(uploaded_file.getvalue())

            if saved_name:
                st.success(f"Saved as: {saved_name}")
                time.sleep(0.5)  # Allow file system sync
                st.rerun()
            else:
                st.error("Failed to save connection file")

    # 2. Get sorted connections
    conn_files = get_connection_files()
    selected_file = st.sidebar.selectbox(
        "Choose Connection File",
        [f[0].name for f in conn_files],
        key=f"conn_file_selector_{str(uuid.uuid4())}"  # Unique key
    )

    config = {}
    databases = []
    selected_db = None

    if selected_file:
        try:
            with open(CONNECTIONS_DIR / selected_file, "r") as f:
                config = yaml.safe_load(f)
                databases = list(config.get('databases', {}).keys())

                # 3. Select specific database with unique key
                selected_db = st.sidebar.selectbox(
                    "Select Database Instance",
                    databases,
                    key=f"db_instance_selector_{str(uuid.uuid4())}"  # Unique key
                )

                # Dynamic connection details
                if selected_db:
                    db_config = config['databases'].get(selected_db, {})
                    with st.sidebar.expander("Connection Details", expanded=False):
                        st.code(yaml.dump(db_config), language='yaml')

        except Exception as e:
            st.sidebar.error(f"Error loading connection: {str(e)}")

    return config, selected_db

def download_button(df, base_name):
    file_base = generate_filename(base_name)
    format = st.radio("Download Format", ('Excel', 'CSV'), horizontal=True)

    if format == 'Excel':
        file_name = f"{file_base}.xlsx"
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            writer.close()
            data = output.getvalue()
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        file_name = f"{file_base}.csv"
        data = df.to_csv(index=False).encode()
        mime = "text/csv"

    st.download_button(
        label=f"Download {format}",
        data=data,
        file_name=file_name,
        mime=mime,
        key=f"download_{uuid.uuid4()}"
    )


# Main App
def main():
    st.title("Database Query Interface")
    init_session()

    # Single call to connection manager
    config, selected_db = connection_manager()

    # Credentials section
    if selected_db and config.get('databases'):
        db_config = config['databases'][selected_db]
        db_type = db_config.get('type', '').lower()

        with st.sidebar.expander("Authentication"):
            username = st.text_input("Username", key=f"db_user_{uuid.uuid4()}")
            password = st.text_input("Password", type="password", key=f"db_pass_{uuid.uuid4()}")

            if st.button("Test Connection", key=f"test_conn_{uuid.uuid4()}"):
                try:
                    conn_str = db_config['format'].format(
                        user=username,
                        password=password,
                        **db_config
                    )
                    engine = sqlalchemy.create_engine(conn_str)
                    test_query = "SELECT 1 FROM DUAL" if db_type == 'oracle' else "SELECT 1"
                    with engine.connect() as conn:
                        conn.execute(sqlalchemy.text(test_query))
                    st.success("Connection successful!")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")

    # Sidebar connection

    st.sidebar.text_input("Database User", key="db_user")
    st.sidebar.text_input("Password", type="password", key="db_pass")

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["Run Adhoc SQL", "Upload and Execute", "Execute Existing SQL"])

    def execute_query(query, tab_ctx):
        engine = init_engine(config, st.session_state.db_user, st.session_state.db_pass)
        if not engine:
            return

        try:
            start_time = time.time()
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text(query))

                if result.returns_rows:
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    exec_time = time.time() - start_time

                    tab_ctx.success(f"""
                        Query Execution Completed!
                        *User*: {st.session_state.db_user}
                        *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        *Records*: {len(df):,}
                        *Duration*: {exec_time:.2f}s
                    """)

                    tab_ctx.dataframe(df.head(1000))
                    download_button(df, st.session_state.request_number)

                    get_logger().info(
                        f"Query executed: {query[:50]}... | Records: {len(df)}",
                        extra={'user': st.session_state.user_id}
                    )
        except Exception as e:
            get_logger().error(f"Query failed: {e}", extra={'user': st.session_state.user_id})
            tab_ctx.error(f"Execution error: {e}")

    # Tab 1: Adhoc SQL
    with tab1:
        st.text_input("Request Number", key="request_number")
        query = st.text_area("SQL Query", height=300)
        if st.button("Execute Query"):
            execute_query(query, tab1)

    # Tab 2: Upload SQL
    with tab2:
        st.text_input("Request Number", key="request_number_t2")
        uploaded_file = st.file_uploader("Upload SQL File", type=["sql"])
        if uploaded_file and st.button("Execute Uploaded"):
            execute_query(uploaded_file.read().decode(), tab2)

    # Tab 3: Existing SQL
    with tab3:
        st.text_input("Request Number", key="request_number_t3")
        sql_files = [f.name for f in QUERIES_DIR.glob("*.sql")]
        selected_file = st.selectbox("Choose SQL File", sql_files)

        if selected_file:
            with open(QUERIES_DIR / selected_file) as f:
                query = f.read()
            st.code(query)

            if st.button("Execute Selected"):
                execute_query(query, tab3)


if __name__ == "__main__":
    main()