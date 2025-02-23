import streamlit as st
import pandas as pd
import re
import sqlite3  # Default for SQLite, add other DB connectors as needed

# Function to execute SQL query
def execute_query(sql_query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(result, columns=columns)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

# Function to validate SQL
def validate_sql(sql_query):
    if re.match(r"^\s*(SELECT|INSERT|UPDATE|DELETE)", sql_query, re.IGNORECASE):
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

# Initialize SQL query variable
sql_query = ""

# If user selects "Paste SQL Query"
if input_method == "Paste SQL Query":
    sql_query = st.text_area("Paste your SQL query here")

# If user selects "Upload SQL File"
elif input_method == "Upload SQL File":
    uploaded_file = st.file_uploader("Upload a SQL file", type=["sql"])
    if uploaded_file is not None:
        # Display success message for file upload
        st.success("File uploaded successfully!")
        sql_query = uploaded_file.read().decode("utf-8")

        # Toggle button to display SQL query (only for file upload)
        show_sql = st.toggle("Display SQL Query", value=False)
        if show_sql:
            st.text("SQL Query from the uploaded file:")
            st.code(sql_query, language="sql")

# Initialize session state for query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Button to execute the query
if st.button("Execute Query"):
    if host and user and password and database:
        try:
            # Connect to the database
            if db_type == "MySQL":
                import pymysql
                connection = pymysql.connect(host=host, user=user, password=password, database=database)
            elif db_type == "Oracle":
                import cx_Oracle
                connection = cx_Oracle.connect(user, password, f"{host}/{database}")
            elif db_type == "Sybase":
                import pyodbc
                connection = pyodbc.connect(f"DRIVER={{Sybase}};SERVER={host};DATABASE={database};UID={user};PWD={password}")
            elif db_type == "SQLite":
                connection = sqlite3.connect(f"{database}.db")

            st.success("Connected to the database!")

            # Validate SQL
            if sql_query and validate_sql(sql_query):
                st.success("SQL query is valid!")
                if input_method == "Upload SQL File":
                    st.info("Executing SQL from the uploaded file...")
                result_df = execute_query(sql_query, connection)
                if result_df is not None:
                    st.write("Query Result:")
                    st.dataframe(result_df)

                    # Add successful query to history
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
                st.error("Invalid SQL query. Please check your query.")

            # Close the connection
            connection.close()
        except Exception as e:
            st.error(f"Failed to connect to the database: {e}")
    else:
        st.warning("Please provide all database connection details.")

# Display Query History
if st.session_state.query_history:
    st.sidebar.subheader("Query History")
    for i, query in enumerate(st.session_state.query_history):
        st.sidebar.text_area(f"Query {i+1}", query, height=100)
