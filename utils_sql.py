import streamlit as st
import pandas as pd
import re
import sqlite3  # Default for SQLite, add other DB connectors as needed
from sqlalchemy import create_engine

# Function to execute SQL query with parameterized approach
def execute_query(sql_query, connection):
    try:
        result_df = pd.read_sql(sql_query, connection)
        return result_df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

# Function to validate SQL to prevent destructive queries
def validate_sql(sql_query):
    forbidden_keywords = ["DROP", "ALTER", "TRUNCATE", "DELETE"]
    if re.match(r"^\s*(SELECT|INSERT|UPDATE)", sql_query, re.IGNORECASE):
        if any(keyword in sql_query.upper() for keyword in forbidden_keywords):
            return False
        return True
    return False

# Streamlit app
st.title("SQL Query Executor")

# Dropdown for database type
db_type = st.selectbox(
    "Select Database Type",
    options=["MySQL", "Oracle", "Sybase", "SQLite"]
)

# Input for database connection details
host = st.text_input("Host")
user = st.text_input("User")
password = st.text_input("Password", type="password")
database = st.text_input("Database")

# Toggle button to choose between pasting SQL or uploading a file
input_method = st.radio(
    "Choose how to provide the SQL query:",
    options=["Paste SQL Query", "Upload SQL File"]
)

sql_query = ""
if input_method == "Paste SQL Query":
    sql_query = st.text_area("Paste your SQL query here")
elif input_method == "Upload SQL File":
    uploaded_file = st.file_uploader("Upload a SQL file", type=["sql", "txt"])
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        sql_query = uploaded_file.read().decode("utf-8")
        show_sql = st.toggle("Display SQL Query", value=False)
        if show_sql:
            st.code(sql_query, language="sql")

# Initialize session state for query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Button to execute the query
if st.button("Execute Query"):
    if host and user and password and database:
        try:
            # Establish connection
            if db_type == "MySQL":
                engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
            elif db_type == "Oracle":
                engine = create_engine(f"oracle+cx_oracle://{user}:{password}@{host}/{database}")
            elif db_type == "Sybase":
                engine = create_engine(f"sybase+pyodbc://{user}:{password}@{host}/{database}")
            elif db_type == "SQLite":
                engine = create_engine(f"sqlite:///{database}.db")
            
            st.success("Connected to the database!")

            if sql_query and validate_sql(sql_query):
                st.success("SQL query is valid!")
                if input_method == "Upload SQL File":
                    st.info("Executing SQL from the uploaded file...")
                result_df = execute_query(sql_query, engine)
                if result_df is not None:
                    st.write("Query Result:")
                    st.dataframe(result_df)
                    st.session_state.query_history.append(sql_query)

                    # Download results as CSV or Excel
                    csv = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv",
                    )
            else:
                st.error("Invalid SQL query or contains restricted keywords.")

        except Exception as e:
            st.error(f"Failed to connect to the database: {e}")
    else:
        st.warning("Please provide all database connection details.")

# Display Query History with an option to clear
st.sidebar.subheader("Query History")
if st.session_state.query_history:
    for i, query in enumerate(st.session_state.query_history):
        st.sidebar.text_area(f"Query {i+1}", query, height=100)
    if st.sidebar.button("Clear History"):
        st.session_state.query_history.clear()
        st.sidebar.success("Query history cleared!")

import oracledb

# Oracle connection details
username = "hr"
password = "hr"
host = "localhost"
port = "1521"
service_name = "xepdb1"

# Create DSN (Data Source Name)
dsn = oracledb.makedsn(host, port, service_name=service_name)

# Establish connection
try:
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connected to Oracle database!")

    # Execute a test query
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dual")
    print(cursor.fetchall())

    # Close the cursor and connection
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Error: {e}")


import oracledb

# Oracle connection details
username = "hr"
password = "hr"
host = "localhost"
port = "1521"
service_name = "xepdb1"

# Create DSN (Data Source Name)
dsn = oracledb.makedsn(host, port, service_name=service_name)

# Establish connection
try:
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connected to Oracle database!")

    # Execute a test query
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dual")
    print(cursor.fetchall())

    # Close the cursor and connection
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Error: {e}")
