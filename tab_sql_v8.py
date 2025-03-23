import streamlit as st
import sqlalchemy
import yaml
import uuid
from datetime import date
from pathlib import Path
from io import StringIO, BytesIO
import pandas as pd
import io
import json
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

def sql_interface_main():

    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if 'user_sessions' not in st.session_state:
        st.session_state.user_sessions = {}

    # Get or create session data
    def get_session_data():
        return st.session_state.user_sessions.setdefault(st.session_state.session_id, {
            'config': None,
            'credentials': {},
            'selected_db': None,
            'db_config': None,
            'queries': {
                'tab1': {'df': None, 'total': 0},
                'tab3': {'df': None, 'total': 0},
                'tab4': {'df': None, 'total': 0}
            }
        })

    session_data = get_session_data()

    # Default configuration
    --Default config
    DEFAULT_CONFIG = {
        "databases": {
            "MySQL": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "format": "mysql://{user}:{password}@{host}:{port}/{dbname}"
            },
            "Sybase": {
                "type": "sybase",
                "server": "vibhour.asia.homework.com,57810",
                "database": "agreen",
                "driver": "SAP ASE ODBC Driver",
                "encryptedpassword": "yes",
                "charset": "sjis",
                "format": "sybase+pyodbc://{user}:{password}@{server}/{database}?driver={driver}&EncryptedPassword={encryptedpassword}&charset={charset}"
            }
        }
    }

    def load_config_json(uploaded_file=None):
        if uploaded_file:
            try:
                return json.load(uploaded_file)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {str(e)}")
                return json.loads(json.dumps(DEFAULT_CONFIG))
        else:
            return DEFAULT_CONFIG.copy()

    def load_config_yaml(uploaded_file=None):
        if uploaded_file:
            return yaml.safe_load(uploaded_file)
        return yaml.safe_load(StringIO(DEFAULT_CONFIG))

    def redact_config(config):
    redacted = config.copy()
    if 'password' in redacted:
        redacted['password'] = '*****'
    if 'databases' in redacted:
        for db_name, db_conf in redacted['databases'].items():
            if 'password' in db_conf:
                db_conf['password'] = '*****'
            if 'format' in db_conf and '{password}' in db_conf['format']:
                db_conf['format'] = db_conf['format'].replace('{password}', '*****')
    return redacted

    @st.cache_resource
    def init_engine(_session_id, db_config, username, password):
        try:
            format_str = db_config['format']
            
            # Verify critical parameters exist
            if not all(k in db_config for k in ['server', 'driver']):
                raise ValueError("Missing required connection parameters")
    
            # URL-encode special characters
            encoded_params = {
            'driver': quote_plus(db_config.get('driver', '')),
            'server': db_config.get('server', ''),
            'database': db_config.get('database', ''),
            'encryptedpassword': db_config.get('encryptedpassword', 'yes'),
            'charset': db_config.get('charset', 'sjis')
            }
    
            connection_string = format_str.format(
                user=quote_plus(username),
                password=quote_plus(password),
                **encoded_params
            )

        st.write(f"Connection String: {connection_string}")  # Debug output
        logger.info(f"Connection String: {connection_string}")  # Debug output
        return sqlalchemy.create_engine(connection_string)
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        logger.error(f"Connection String: {connection_string}")  # Debug output
        return None

    def run_query(query, params=None):
        try:
            username = session_data['credentials'].get('username')
            password = session_data['credentials'].get('password')
            db_config = session_data['db_config']

            if not username or not password:
                st.error("Missing database credentials")
                return None, None

            engine = init_engine(
                st.session_state.session_id,
                db_config,
                username,
                password
            )

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
    st.sidebar.header(f"Session ID: {st.session_state.session_id[:8]}")
    uploaded_config = st.sidebar.file_uploader("Upload JSON config", type=["json"])

    # Load config for this session
    session_data['config'] = load_config_json(uploaded_config)

    # Database Selection
    db_names = list(session_data['config']['databases'].keys())

    # Reset selected_db if not in current config
    if session_data['selected_db'] not in db_names:
        session_data['selected_db'] = None

    # Get previous selection index or default to 0
    prev_index = db_names.index(session_data['selected_db']) if session_data['selected_db'] in db_names else 0

    session_data['selected_db'] = st.sidebar.selectbox(
        "Select Database",
        db_names,
        index=prev_index,
        key=f"db_select_{st.session_state.session_id}"
    )

    # Reset credentials when database changes
    if session_data.get('prev_db') != session_data['selected_db']:
        session_data['credentials'] = {}
        current_db_conf = session_data['config']['databases'][session_data['selected_db']]
        if 'username' in current_db_conf:
            session_data['credentials']['username'] = current_db_conf['username']
        if 'password' in current_db_conf:
            session_data['credentials']['password'] = current_db_conf['password']
        session_data['prev_db'] = session_data['selected_db']

    session_data['db_config'] = session_data['config']['databases'][session_data['selected_db']]

    #Configuration Display
    with st.sidebar.expander("Current Configuration", expanded=False):
        st.write(f"**Active Database:** {session_data['selected_db']}")
        redacted = redact_config(session_data['db_config'])
        st.json(redacted)

    # Credential Handling
    with st.sidebar.expander("Database Credentials", expanded=True):
        current_db_conf = session_data['db_config']
        config_username = current_db_conf.get('username', '')
        config_password = current_db_conf.get('password', '')

        # Get current credentials or use config values
        current_uname = session_data['credentials'].get('username', config_username)
        current_pwd = session_data['credentials'].get('password', config_password)

        new_uname = st.text_input(
            "Username",
            value=current_uname,
            key=f"uname_{st.session_state.session_id}"
        )
        new_pwd = st.text_input(
            "Password",
            type="password",
            value=current_pwd,
            key=f"pwd_{st.session_state.session_id}"
        )

        # Update credentials only if user modified them
        if new_uname != current_uname:
            session_data['credentials']['username'] = new_uname
        if new_pwd != current_pwd:
            session_data['credentials']['password'] = new_pwd

        if config_username or config_password:
            st.caption("🔒 Credentials from config file")

    # Main Tabs
    tab1, tab3, tab4 = st.tabs([
        "Ad-hoc Query",
        "Upload SQL File",
        "SQL File Management"
    ])

    # Tab1: Ad-hoc Query
    with tab1:
        st.subheader("Run Ad-hoc SQL Query")
        query = st.text_area("Enter SQL query:", height=200, key=f"tab1_query_{st.session_state.session_id}")

        if st.button("Run Query", key=f"tab1_run_{st.session_state.session_id}"):
            session_data['queries']['tab1']['df'] = None
            session_data['queries']['tab1']['total'] = 0

            if query.strip():
                with st.spinner("Executing..."):
                    results, columns = run_query(query)

                    df = pd.DataFrame(results if results else [], columns=columns) if columns else pd.DataFrame()
                    session_data['queries']['tab1']['df'] = df
                    session_data['queries']['tab1']['total'] = len(df)

                    if not df.empty:
                        st.success(f"✅ Fetched {len(df)} rows")
                        st.dataframe(df.head(10))
                    else:
                        if columns:
                            st.info("No data found")
                            st.dataframe(df)
                        else:
                            st.warning("Query failed")

        if session_data['queries']['tab1']['df'] is not None:
            st.divider()
            st.write(f"**Total records:** {session_data['queries']['tab1']['total']}")
            if not session_data['queries']['tab1']['df'].empty or session_data['queries']['tab1']['df'].columns.any():
                file_name = st.text_input("Export name:", "results", key=f"tab1_file_{st.session_state.session_id}")
                excel_data = create_excel_download(session_data['queries']['tab1']['df'], file_name)
                st.download_button(
                    "⬇️ Excel", excel_data,
                    file_name=f"{file_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"tab1_download_{st.session_state.session_id}"
                )

    # Tab3: Upload SQL File
    with tab3:
        st.subheader("Upload and Execute SQL File")

        uploaded_file = st.file_uploader("Choose SQL file", type=["sql"],
                                       key=f"tab3_upload_{st.session_state.session_id}",
                                       on_change=lambda: [session_data['queries']['tab3'].update({'df': None, 'total': 0})])

        MAX_FILE_SIZE = 1024 * 1024  # 1MB

        if uploaded_file:
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error("File too large! Max 1MB allowed")
                st.stop()

            query = uploaded_file.read().decode()
            st.code(query)

            if "DROP" in query.upper() or "DELETE" in query.upper():
                st.error("Potentially dangerous SQL operations detected")
                st.stop()

            if st.button("Execute", key=f"tab3_execute_{st.session_state.session_id}"):
                session_data['queries']['tab3']['df'] = None
                session_data['queries']['tab3']['total'] = 0

                with st.spinner("Executing..."):
                    results, columns = run_query(query)

                    df = pd.DataFrame(results if results else [], columns=columns) if columns else pd.DataFrame()
                    session_data['queries']['tab3']['df'] = df
                    session_data['queries']['tab3']['total'] = len(df)

                    if not df.empty:
                        st.success(f"✅ Fetched {len(df)} rows")
                        st.dataframe(df.head(10))
                    else:
                        if columns:
                            st.info("No data found")
                            st.dataframe(df)
                        else:
                            st.warning("Query failed")

        if session_data['queries']['tab3']['df'] is not None and uploaded_file:
            st.divider()
            st.write(f"**Total records:** {session_data['queries']['tab3']['total']}")
            if not session_data['queries']['tab3']['df'].empty or session_data['queries']['tab3']['df'].columns.any():
                file_name = st.text_input("Export name:", "upload_results", key=f"tab3_file_{st.session_state.session_id}")
                excel_data = create_excel_download(session_data['queries']['tab3']['df'], file_name)
                st.download_button(
                    "⬇️ Excel", excel_data,
                    file_name=f"{file_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"tab3_download_{st.session_state.session_id}"
                )

    # Tab4: SQL File Management
    with tab4:
        # Create New File
        with st.container():
            st.subheader("Create New SQL File")
            new_name = st.text_input("New filename:", key=f"tab4_new_{st.session_state.session_id}")
            new_content = st.text_area("SQL content:", height=300, key=f"tab4_content_{st.session_state.session_id}")

            if st.button("Create", key=f"tab4_create_{st.session_state.session_id}"):
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
            selected_file = st.selectbox("Select file", files, key=f"tab4_select_{st.session_state.session_id}")

            if selected_file:
                file_path = QUERIES_DIR / selected_file
                with open(file_path, "r") as f:
                    content = st.text_area("Edit SQL:", f.read(), height=300, key=f"tab4_edit_{st.session_state.session_id}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save & Run", key=f"tab4_saverun_{st.session_state.session_id}"):
                        with open(file_path, "w") as f:
                            f.write(content)

                        with st.spinner("Executing..."):
                            results, columns = run_query(content)

                            df = pd.DataFrame(results if results else [], columns=columns) if columns else pd.DataFrame()
                            session_data['queries']['tab4']['df'] = df
                            session_data['queries']['tab4']['total'] = len(df)

                            if not df.empty:
                                st.success(f"✅ Fetched {len(df)} rows")
                                st.dataframe(df.head(10))
                            else:
                                if columns:
                                    st.info("No data found")
                                    st.dataframe(df)
                                else:
                                    st.warning("Query failed")

                if session_data['queries']['tab4']['df'] is not None:
                    st.divider()
                    st.write(f"**Total records:** {session_data['queries']['tab4']['total']}")
                    if not session_data['queries']['tab4']['df'].empty or session_data['queries']['tab4']['df'].columns.any():
                        file_name = st.text_input("Export name:", "edit_results", key=f"tab4_file_{st.session_state.session_id}")
                        excel_data = create_excel_download(session_data['queries']['tab4']['df'], file_name)
                        st.download_button(
                            "⬇️ Excel", excel_data,
                            file_name=f"{file_name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"tab4_download_{st.session_state.session_id}"
                        )
