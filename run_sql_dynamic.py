import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from io import BytesIO
from datetime import datetime
import os

# Hardcoded Database Connection (Replace with your credentials)
DB_CONFIG = {
    'drivername': 'postgresql',
    'username': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': '5432',
    'database': 'your_database'
}

def get_db_connection():
    return create_engine(
        f"{DB_CONFIG['drivername']}://{DB_CONFIG['username']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

# Initialize session state
if 'sql_queries' not in st.session_state:
    st.session_state.sql_queries = ['']
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []
if 'sequence' not in st.session_state:
    st.session_state.sequence = 1

st.title("SQL Query Runner with Excel Export")

# Request Number Input
req_number = st.text_input("Request Number (REQ format):", placeholder="REQ123456")

# SQL Input Management
st.subheader("SQL Queries")
for i, query in enumerate(st.session_state.sql_queries):
    st.session_state.sql_queries[i] = st.text_area(
        f"SQL Query {i+1}", value=query, height=150,
        key=f"sql_{i}"
    )

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add New SQL"):
        st.session_state.sql_queries.append('')
with col2:
    if st.button("➖ Remove Last SQL"):
        if len(st.session_state.sql_queries) > 1:
            st.session_state.sql_queries.pop()

# Execute Queries
if st.button("🚀 Run All SQL Queries"):
    if not req_number.startswith('REQ'):
        st.error("Request number must start with REQ")
        st.stop()
    
    engine = get_db_connection()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    for idx, query in enumerate(st.session_state.sql_queries):
        if query.strip():
            try:
                df = pd.read_sql(query, engine)
                if not df.empty:
                    # Create in-memory Excel file
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name=f'Result-{idx+1}')
                    
                    # Generate filename
                    filename = f"{req_number}-{st.session_state.sequence}-{timestamp}.xlsx"
                    st.session_state.generated_files.append({
                        'filename': filename,
                        'data': output.getvalue()
                    })
                    st.session_state.sequence += 1
                    
                    st.success(f"Query {idx+1} executed successfully!")
                else:
                    st.warning(f"Query {idx+1} returned no results")
            except Exception as e:
                st.error(f"Error in Query {idx+1}: {str(e)}")

# Download Individual Files
if st.session_state.generated_files:
    st.subheader("Download Files")
    for file in st.session_state.generated_files:
        st.download_button(
            label=f"Download {file['filename']}",
            data=file['data'],
            file_name=file['filename'],
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# Merge Files
if st.session_state.generated_files and len(st.session_state.generated_files) > 1:
    st.subheader("Merge Files")
    if st.button("🔗 Merge All Excel Files"):
        merged_output = BytesIO()
        with pd.ExcelWriter(merged_output, engine='xlsxwriter') as writer:
            for i, file in enumerate(st.session_state.generated_files):
                df = pd.read_excel(BytesIO(file['data']))
                df.to_excel(writer, index=False, sheet_name=f'Result-{i+1}')
        
        merged_filename = f"{req_number}-merged-{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        st.download_button(
            label="Download Merged File",
            data=merged_output.getvalue(),
            file_name=merged_filename,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )