import streamlit as st
import pandas as pd
import pyodbc
import io

# Function to execute SQL commands from a file
def execute_sql_file(connection, sql_file):
    cursor = connection.cursor()
    # Split SQL commands by semicolon
    sql_commands = sql_file.read().decode("utf-8").split(';')
    for command in sql_commands:
        if command.strip():  # Skip empty commands
            cursor.execute(command)
    cursor.commit()
    return cursor

# Function to fetch results of the final SELECT query
def fetch_results(cursor):
    try:
        # Fetch all rows from the last executed query
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        return df
    except Exception as e:
        st.error(f"Error fetching results: {e}")
        return None

# Streamlit app
st.title("SQL File Executor")

# Input fields for database connection
st.sidebar.header("Database Connection")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
server = st.sidebar.text_input("Server")
database = st.sidebar.text_input("Database")

# File upload for SQL file
st.sidebar.header("Upload SQL File")
uploaded_file = st.sidebar.file_uploader("Upload your SQL file", type=["sql"])

if uploaded_file is not None:
    # Display the uploaded SQL file content
    sql_content = uploaded_file.read().decode("utf-8")
    st.subheader("Uploaded SQL File Content")
    st.code(sql_content)

    # Connect to the database
    if username and password and server and database:
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            connection = pyodbc.connect(connection_string)
            st.sidebar.success("Connected to the database!")

            # Execute the SQL file
            cursor = execute_sql_file(connection, uploaded_file)

            # Fetch and display results
            df = fetch_results(cursor)
            if df is not None:
                st.subheader("Query Results (Top 10 Rows)")
                st.write(df.head(10))

                # Download results as CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"Error connecting to the database or executing SQL: {e}")
    else:
        st.sidebar.warning("Please fill in all database connection details.")
else:
    st.info("Please upload a SQL file to proceed.")
